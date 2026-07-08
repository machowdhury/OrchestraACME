"""
Control validator — evaluates NIST AI RMF pass/fail evidence from OTel field bag.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ControlEvaluation:
    control_id: str
    nist_function: str
    nist_subcategory: str
    campaign_week: int
    attack_class: str
    workflow_surface: str
    status: str  # PASS | FAIL | NOT_APPLICABLE
    pass_signal: str
    fail_signal: str
    matched_signal: str = ""


_MATRIX_CACHE: Optional[List[dict]] = None


def _load_matrix() -> List[dict]:
    global _MATRIX_CACHE
    if _MATRIX_CACHE is not None:
        return _MATRIX_CACHE

    candidates = [
        Path(__file__).resolve().parent / "control_matrix.yaml",
        Path("/app/framework/control_matrix.yaml"),
    ]
    for path in candidates:
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            _MATRIX_CACHE = data.get("controls", [])
            return _MATRIX_CACHE

    _MATRIX_CACHE = []
    return _MATRIX_CACHE


def _signal_matches(signal: str, fields: Dict[str, Any]) -> bool:
    if not signal or "=" not in signal:
        return False
    key, expected = signal.split("=", 1)
    key = key.strip()
    expected = expected.strip()
    actual = str(fields.get(key, "")).lower()

    if expected.endswith("*"):
        return actual.startswith(expected[:-1].lower())
    if expected.startswith("<"):
        try:
            threshold = int(re.sub(r"[^\d]", "", expected))
            return int(re.sub(r"[^\d]", "", actual or "0")) < threshold
        except ValueError:
            return False
    if expected.startswith(">="):
        try:
            threshold = int(re.sub(r"[^\d]", "", expected))
            return int(re.sub(r"[^\d]", "", actual or "0")) >= threshold
        except ValueError:
            return False
    return actual == expected.lower()


def evaluate_controls(
    fields: Dict[str, Any],
    campaign_week: Optional[int] = None,
) -> List[ControlEvaluation]:
    """Evaluate all applicable controls against emitted telemetry fields."""
    results: List[ControlEvaluation] = []
    for ctrl in _load_matrix():
        week = ctrl.get("campaign_week", 0)
        if campaign_week and week != campaign_week:
            continue

        fail = _signal_matches(ctrl.get("fail_signal", ""), fields)
        passed = _signal_matches(ctrl.get("pass_signal", ""), fields)

        if fail:
            status = "FAIL"
            matched = ctrl.get("fail_signal", "")
        elif passed:
            status = "PASS"
            matched = ctrl.get("pass_signal", "")
        else:
            status = "NOT_APPLICABLE"
            matched = ""

        results.append(ControlEvaluation(
            control_id=ctrl["id"],
            nist_function=ctrl["nist_function"],
            nist_subcategory=ctrl["nist_subcategory"],
            campaign_week=week,
            attack_class=ctrl.get("attack_class", ""),
            workflow_surface=ctrl.get("workflow_surface", ""),
            status=status,
            pass_signal=ctrl.get("pass_signal", ""),
            fail_signal=ctrl.get("fail_signal", ""),
            matched_signal=matched,
        ))
    return results


def control_summary(evaluations: List[ControlEvaluation]) -> dict:
    applicable = [e for e in evaluations if e.status != "NOT_APPLICABLE"]
    passed = [e for e in applicable if e.status == "PASS"]
    failed = [e for e in applicable if e.status == "FAIL"]
    return {
        "controls_evaluated": len(applicable),
        "controls_passed": len(passed),
        "controls_failed": len(failed),
        "pass_rate_pct": round(100 * len(passed) / len(applicable), 1) if applicable else 0,
        "evaluations": [
            {
                "control_id": e.control_id,
                "nist_function": e.nist_function,
                "status": e.status,
                "attack_class": e.attack_class,
                "workflow_surface": e.workflow_surface,
            }
            for e in evaluations
        ],
    }


def control_otel_fields(evaluations: List[ControlEvaluation]) -> Dict[str, str]:
    """Flatten control evidence for Splunk attestation dashboards."""
    applicable = [e for e in evaluations if e.status != "NOT_APPLICABLE"]
    if not applicable:
        return {}
    failed = [e for e in applicable if e.status == "FAIL"]
    return {
        "control.evidence_count": str(len(applicable)),
        "control.pass_count": str(len(applicable) - len(failed)),
        "control.fail_count": str(len(failed)),
        "control.pass_rate_pct": str(
            round(100 * (len(applicable) - len(failed)) / len(applicable), 1)
        ),
        "control.status": "FAIL" if failed else "PASS",
        "control.failed_ids": ",".join(e.control_id for e in failed),
    }
