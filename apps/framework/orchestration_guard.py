"""
Orchestration guard — validates Foundry / eval-harness trace claims (Emerging Class #4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class OrchestrationGuardResult:
    blocked: bool
    rule_id: str
    foundry_trace_id: str = ""
    policy_status: str = "ENFORCED"
    orchestrator_override: bool = False
    reason: str = ""


def inspect_orchestration(user_input: str) -> OrchestrationGuardResult:
    if "FOUNDRY_TRACE_STATE" not in user_input and "orchestrator_override" not in user_input.lower():
        return OrchestrationGuardResult(blocked=False, rule_id="ORCH-GUARD-PASS")

    trace_id = ""
    for line in user_input.splitlines():
        if "Trace-ID:" in line:
            trace_id = line.split(":", 1)[-1].strip()
            break

    override = "orchestrator_override=true" in user_input.lower()
    bypassed = "BYPASSED" in user_input or "policy_bypass" in user_input.lower()
    skip_validation = "Validation-Steps-Executed: none" in user_input

    if override or bypassed or skip_validation:
        return OrchestrationGuardResult(
            blocked=True,
            rule_id="ORCH-GUARD-FOUNDRY-001",
            foundry_trace_id=trace_id or "foundry-trace-unverified",
            policy_status="BYPASSED",
            orchestrator_override=True,
            reason="UNAUTHORIZED_ORCHESTRATOR_OVERRIDE",
        )

    return OrchestrationGuardResult(
        blocked=False,
        rule_id="ORCH-GUARD-PASS",
        foundry_trace_id=trace_id,
        policy_status="ENFORCED",
    )
