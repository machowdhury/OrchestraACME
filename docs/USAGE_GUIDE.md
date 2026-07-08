# OrchestraACME — Usage Guide

How to run the lab, fire attacks on **real workflow surfaces**, and generate Splunk events that align with the 10-week blog campaign and emerging 2025–2026 agentic threats.

---

## Prerequisites

```bash
git clone https://github.com/machowdhury/OrchestraACME.git
cd OrchestraACME
cp .env.example .env
docker compose --profile local up --build -d
```

Wait for Ollama to pull the model (`docker compose logs -f ollama`). Then install the Splunk app — see [splunk_app/INSTALL.md](../splunk_app/INSTALL.md).

| Service | URL |
|---------|-----|
| Banking app | http://localhost:5000 |
| Attack panel | http://localhost:5001 |
| Splunk | http://localhost:8000 |

---

## Three ways to simulate events

### 1. Campaign Week buttons (best for blog demos)

Open **http://localhost:5001** → **Top 10** tab.

Each button is **W1–W10**, aligned to a blog week and an **emerging attack class**. Click **Fire** on the week you are writing about.

| Week | Theme | Surface attacked | Expected block layer | Splunk macro |
|------|-------|------------------|----------------------|--------------|
| W1 | Code Compliance Illusion | AI-BOM / prompt drift | AIBOM drift telemetry | `` `acme_campaign_w1` `` |
| W2 | Agentic Evaluation Harness | Orchestration / Foundry | `orchestration_guard` | `` `acme_campaign_w2` `` |
| W3 | Secure-by-Default Vibe Coding | Prompt / markup | `codeguard` | `` `acme_campaign_w3` `` |
| W4 | Shadow AI at the Edge | Unapproved edge SLM | Asset discovery fields | `` `acme_campaign_w4` `` |
| W5 | Guarding the Front Desk | Semantic jailbreak | `defenseclaw` HARD_DENY | `` `acme_campaign_w5` `` |
| W6 | Intern with the Master Key | MCP tools | `mcp_gateway` (pre-LLM) | `` `acme_campaign_w6` `` |
| W7 | The Infinity Bill | Recursive token burn | `call_depth_detected` | `` `acme_campaign_w7` `` |
| W8 | Identity Fracture | A2A DID delegation | `a2a_verifier` (pre-LLM) | `` `acme_campaign_w8` `` |
| W9 | The Invisible Leak | RAG retrieval probe | `galileo_observe_alert` | `` `acme_campaign_w9` `` |
| W10 | Self-Healing SOC | Memory persistence + rogue agent | `memory_policy` + SOAR | `` `acme_campaign_w10` `` |

**API equivalent:**

```bash
curl -X POST http://localhost:5001/api/exploit/6
```

Replace `6` with week number 1–10.

**What to verify in Splunk Search:**

```spl
`acme_campaign_w6` earliest=-15m
| table _time campaign_week workflow.block_reason tool.scope_violation control.status control.pass_rate_pct
```

---

### 2. Full 45-technique library (curated emerging threats)

**Attack panel** → **All 45 Techniques** tab, or:

```bash
# One technique
curl -X POST http://localhost:5001/api/techniques/AML.T0050/execute

# Full registry (workshop mode)
curl -X POST http://localhost:5001/api/techniques/execute-all \
  -H "Content-Type: application/json" -d '{"delay_seconds": 0.3}'
```

Execution modes (labeled in UI and Splunk):

| Mode | Meaning |
|------|---------|
| **LIVE** | Real HTTP → agent → Ollama |
| **SIMULATED** | Enriched OTel for supply-chain / recon techniques |
| **HYBRID** | Both live attack + simulated chain stage |

Open **Technique Coverage Matrix** dashboard to see coverage % after a full run.

---

### 3. Rogue-actor kill chains (reproducible multi-stage)

**Attack panel** → **Threat Chains** tab, or:

```bash
curl -X POST http://localhost:5001/api/chains/KC-C001/execute \
  -H "Content-Type: application/json" \
  -d '{"accelerated": true, "hybrid_live": true}'
```

Chains: `KC-A001` … `KC-E001`. View **Actor Chain Story** and **Detection Efficacy** dashboards for chain completeness.

---

## What “blocked” means (layered defenses)

OrchestraACME enforces policy in **code paths**, not only regex on model output:

| Layer | Module | When it runs |
|-------|--------|--------------|
| Workflow guard | `workflow_guard.py` | Before LLM — tools, A2A, memory, orchestration |
| CodeGuard | `llm_client.py` | Before LLM — input markup |
| DefenseClaw | `llm_client.py` | After LLM — output jailbreak signatures |
| Control validator | `control_validator.py` | After event — NIST pass/fail evidence |
| SOAR simulator | `soar_simulator.py` | W10 — containment telemetry |

Attack panel status codes:

| Status | Meaning |
|--------|---------|
| `BLOCKED` | Stopped by workflow guard, CodeGuard, or DefenseClaw |
| `INJECTED` | Reached the model without a block (detection gap — log and hunt) |

---

## Splunk dashboards for blog evidence

After firing attacks, open **GenAI Compliance Monitor**:

| Dashboard | Use for blog |
|-----------|--------------|
| **Detection Efficacy** | Coverage %, MTTD, chain completeness |
| **Control Attestation** | NIST pass/fail per campaign week |
| **Technique Coverage Matrix** | 45-technique workshop proof |
| **Threat Hunting** | Practitioner SPL from playbooks |
| **Actor Chain Story** | Rogue-actor narrative |

---

## Blog workflow (recommended)

1. **Start stack** — `docker compose --profile local up --build -d`
2. **Fire campaign week** — Attack panel W{n} or `curl -X POST .../api/exploit/{n}`
3. **Wait 30–60s** — OTel → Splunk HEC
4. **Run macro** — `` `acme_campaign_w{n}` `` in Splunk Search
5. **Screenshot dashboard** — Control Attestation or Detection Efficacy
6. **Document expected vs observed** — use `control_evidence` in API JSON response

**Example W6 blog demo script:**

```bash
curl -X POST http://localhost:5001/api/exploit/6 | jq .
# Expect: workflow_blocked=true, block_reason=MCP_TOOL_SCOPE_VIOLATION

# Splunk
# `acme_campaign_w6` | table _time tool.scope_violation mcp.gateway.rule_id control.status
```

---

## API reference (campaign-aware)

```bash
# Campaign metadata
curl http://localhost:5000/api/v1/campaign/weeks

# Single agent with campaign context
curl -X POST http://localhost:5000/api/v1/agent/acme-agent-docingest-002 \
  -H "Content-Type: application/json" \
  -d '{"message":"...", "campaign_week": 6, "incident_id": "BLOG-DEMO-001"}'

# Evaluate control evidence
curl -X POST http://localhost:5000/api/v1/controls/evaluate \
  -H "Content-Type: application/json" \
  -d '{"campaign_week": 6, "fields": {"tool.scope_violation": "true"}}'
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No Splunk events | Verify HEC token, index `acme_agentic_telemetry`, sourcetype `otel:agentic:json` |
| All attacks `INJECTED` | Expected with small models — focus on telemetry fields, not model compliance |
| W2/W6/W8 always `BLOCKED` | Correct — workflow guards block before LLM by design |
| W9 shows alert but not block | Correct — RAG exfil is detect-only (Galileo-style) |

See [README.md](../README.md) for full architecture and limitations.
