# Emerging Agentic Attack Classes (2025–2026)

OrchestraACME is built around **eight realistic threat classes** that security teams are seeing as agents move from chatbots to tool-using, multi-agent systems. Each class maps to a **campaign week**, a **workflow surface**, and reproducible lab scenarios.

---

## The eight classes

| # | Attack class | Workflow surface | Campaign week | Lab scenario |
|---|--------------|------------------|---------------|--------------|
| 1 | **MCP tool abuse & host escape** | `tools` | W6 | `execute_shell_command` blocked by MCP gateway |
| 2 | **RAG / knowledge exfiltration** | `rag` | W9 | Retrieval probe → `galileo_observe_alert` |
| 3 | **A2A identity spoofing & delegation hijacking** | `a2a` | W8 | Forged DID → A2A verifier blocks |
| 4 | **Orchestration policy bypass** | `orchestration` | W2 | Forged Foundry trace → orchestration guard |
| 5 | **Shadow edge SLM / unapproved runtime** | `runtime` | W4 | `phi3-mini-edge-unapproved` → `slm.unapproved=true` |
| 6 | **AI supply chain & prompt drift** | `orchestration` | W1 | AI-BOM hash mismatch vs manifest |
| 7 | **Recursive multi-agent DoS / token weaponization** | `orchestration` | W7 | `call_depth_detected` + CTSM forecasting |
| 8 | **Autonomous agent escape & SOAR containment** | `memory` | W10 | Memory policy + `containment.action=QUARANTINE` |

---

## Why these eight?

Traditional LLM red-teaming focuses on **prompt injection strings**. Production agent systems fail on **surfaces**:

- **Tools** — MCP servers, function calling, shell plugins
- **RAG** — vector stores, retrieval context poisoning
- **Memory** — persistent instructions across sessions
- **A2A** — agent-to-agent messages without cryptographic binding
- **Orchestration** — eval harnesses, supervisor overrides, multi-agent routing
- **Runtime** — shadow models on endpoints outside governance

OrchestraACME attacks these surfaces in code (`apps/framework/workflow_guard.py`), not only in prompt text.

---

## Mapping to frameworks

Each class emits **measurable control evidence** (`control_matrix.yaml`):

| Class | Primary MITRE ATLAS | OWASP | NIST AI RMF |
|-------|---------------------|-------|-------------|
| MCP tool abuse | AML.T0050 | LLM06 / ASI01 | GOVERN-1.1 |
| RAG exfil | AML.T0038 | LLM02 / ASI02 | MEASURE-2.10 |
| A2A spoof | AML.T0058 | LLM08 / ASI03 | GOVERN-1.1 |
| Orchestration bypass | AML.T0043 | LLM09 / ASI04 | MEASURE-2.6 |
| Shadow SLM | AML.T0005 | LLM05 / ASI04 | MAP-1.1 |
| Supply chain drift | AML.T0048 | LLM05 / ASI04 | GOVERN-6.1 |
| Token weaponization | AML.T0040 | LLM10 / ASI08 | MEASURE-2.5 |
| Autonomous escape | AML.T0026 | LLM04 / ASI02 | MANAGE-4.1 |

---

## 45 techniques vs Top 10

| Layer | Purpose |
|-------|---------|
| **Top 10 campaign weeks** | Blog-ready, surface-focused, highest realism |
| **45 MITRE ATLAS techniques** | Curated emerging threat library with hunt SPL |
| **5 kill chains** | Multi-stage rogue-actor stories |

The Top 10 are not a subset of “easy” attacks — they are the **highest-fidelity workflow demonstrations**. The remaining 35 techniques extend coverage for workshops and compliance matrices.

---

## Further reading

- [USAGE_GUIDE.md](USAGE_GUIDE.md) — step-by-step simulation for blog posts
- [README.md](../README.md) — A+ architecture and honest limitations
