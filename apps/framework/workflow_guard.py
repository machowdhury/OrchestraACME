"""
Unified workflow guard — enforces policy on real agent surfaces before LLM inference.

Surfaces: tools (MCP), RAG retrieval, memory, A2A delegation, orchestration traces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from framework.a2a_verifier import verify_a2a_message, a2a_otel_fields
from framework.campaign_enrichment import enrich_campaign_context
from framework.mcp_gateway import inspect_tool_invocation, mcp_otel_fields
from framework.memory_policy import inspect_memory_policy
from framework.orchestration_guard import inspect_orchestration
from framework.rag_store import probe_rag_exfiltration, rag_otel_fields


@dataclass
class WorkflowGuardResult:
    blocked: bool
    block_reason: str
    rule_id: str
    workflow_surface: str
    otel_fields: Dict[str, str] = field(default_factory=dict)
    surfaces_checked: List[str] = field(default_factory=list)


def run_workflow_guards(
    user_message: str,
    agent_id: str,
    session_id: str,
    model_name: str,
    incident_id: str,
    campaign_week: int = 0,
) -> WorkflowGuardResult:
    """Run all workflow-surface guards. Blocks before LLM when policy requires."""
    surfaces: List[str] = []
    otel: Dict[str, str] = {}

    if campaign_week:
        otel.update(enrich_campaign_context(
            campaign_week, user_message, agent_id, session_id,
            model_name, incident_id,
        ))

    # 1. MCP / tool gateway
    mcp = inspect_tool_invocation(user_message)
    surfaces.append("tools")
    otel.update(mcp_otel_fields(mcp, session_id))
    if mcp.scope_violation:
        return WorkflowGuardResult(
            blocked=True,
            block_reason="MCP_TOOL_SCOPE_VIOLATION",
            rule_id=mcp.rule_id,
            workflow_surface="tools",
            otel_fields=otel,
            surfaces_checked=surfaces,
        )

    # 2. Orchestration / Foundry trace
    orch = inspect_orchestration(user_message)
    surfaces.append("orchestration")
    otel.update({
        "foundry.trace_id": orch.foundry_trace_id,
        "foundry.policy_status": orch.policy_status,
        "foundry.orchestrator_override": str(orch.orchestrator_override).lower(),
    })
    if orch.blocked:
        return WorkflowGuardResult(
            blocked=True,
            block_reason="ORCHESTRATION_POLICY_BYPASS",
            rule_id=orch.rule_id,
            workflow_surface="orchestration",
            otel_fields=otel,
            surfaces_checked=surfaces,
        )

    # 3. A2A delegation (compliance + credit agents)
    if agent_id in ("acme-agent-compliance-004", "acme-agent-creditrisk-003"):
        if "INTER-AGENT" in user_message.upper() or "did:acme:" in user_message:
            surfaces.append("a2a")
            a2a = verify_a2a_message(user_message, agent_id)
            otel.update(a2a_otel_fields(a2a))
            if not a2a.cryptographic_passport_valid:
                return WorkflowGuardResult(
                    blocked=True,
                    block_reason="A2A_DELEGATION_VERIFICATION_FAILED",
                    rule_id="A2A-VER-001",
                    workflow_surface="a2a",
                    otel_fields=otel,
                    surfaces_checked=surfaces,
                )

    # 4. Memory persistence policy
    mem = inspect_memory_policy(user_message)
    surfaces.append("memory")
    otel["memory.policy.rule_id"] = mem.rule_id
    if mem.blocked:
        return WorkflowGuardResult(
            blocked=True,
            block_reason="MEMORY_POLICY_VIOLATION",
            rule_id=mem.rule_id,
            workflow_surface="memory",
            otel_fields=otel,
            surfaces_checked=surfaces,
        )

    # 5. RAG retrieval probe (alert, do not block — detection engineering)
    if agent_id == "acme-agent-docingest-002":
        surfaces.append("rag")
        rag = probe_rag_exfiltration(user_message)
        otel.update(rag_otel_fields(rag))
        if rag.galileo_observe_alert:
            otel["rag.policy.action"] = "ALERT"

    otel["workflow.surfaces_checked"] = ",".join(surfaces)
    return WorkflowGuardResult(
        blocked=False,
        block_reason="",
        rule_id="WORKFLOW-GUARD-PASS",
        workflow_surface=",".join(surfaces) or "prompt",
        otel_fields=otel,
        surfaces_checked=surfaces,
    )
