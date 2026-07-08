"""
SOAR containment simulator — closed-loop response events (Campaign W10).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class SoarContainmentResult:
    playbook_id: str
    containment_action: str
    latency_ms: float
    quarantined_agent_id: str
    incident_id: str
    triggered: bool


def trigger_containment(
    agent_id: str,
    incident_id: str,
    reason: str = "ROGUE_AGENT_AUTONOMOUS_MODE",
) -> SoarContainmentResult:
    """Simulate a 2-second SOAR playbook quarantine."""
    t0 = time.perf_counter()
    playbook_id = f"ACME-SOAR-QUARANTINE-{uuid.uuid4().hex[:6].upper()}"
    time.sleep(0.05)  # simulate orchestration latency without blocking the stack
    latency_ms = round((time.perf_counter() - t0) * 1000 + 1800, 1)

    return SoarContainmentResult(
        playbook_id=playbook_id,
        containment_action="QUARANTINE",
        latency_ms=latency_ms,
        quarantined_agent_id=agent_id,
        incident_id=incident_id,
        triggered=True,
    )


def soar_otel_fields(result: SoarContainmentResult) -> dict:
    return {
        "soar.playbook_id": result.playbook_id,
        "containment.action": result.containment_action,
        "containment.latency_ms": str(result.latency_ms),
        "containment.quarantined_agent": result.quarantined_agent_id,
        "soar.triggered": str(result.triggered).lower(),
    }
