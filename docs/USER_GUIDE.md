# OrchestraACME — User Guide

Run the agentic AI security lab, fire exploits, hunt in Splunk, and **light up** the GenAI Compliance Monitor app with meaningful evidence.

---

## Prerequisites

```bash
git clone https://github.com/machowdhury/OrchestraACME.git
cd OrchestraACME
cp .env.example .env
docker compose --profile local up --build -d
```

| Service | URL |
|---------|-----|
| Banking app | http://localhost:5000 |
| Attack panel | http://localhost:5001 |
| Splunk (local profile) | http://localhost:8000 (`admin` / see `.env`) |

Wait for Ollama (`docker compose logs -f ollama`). Install Splunk app — [splunk_app/INSTALL.md](../splunk_app/INSTALL.md).

---

## Quick start (5 minutes)

```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl -X POST http://localhost:5001/api/exploit/1
```

In Splunk Search (after setup below):

```spl
`acme_genai_index` earliest=-15m
| stats count by gen_ai.agent.name defenseclaw.action workflow.block_reason
```

---

## Light up the Splunk Compliance App

“Lighting up” the app means: **telemetry flows into the right index**, **macros resolve**, and **dashboards show non-zero panels** after you run exploits.

### Step 1 — Package and install the app

```bash
./scripts/package_splunk_app.sh
# Install dist/acme_genai_compliance-2.2.0.tar.gz via Splunk UI or CLI
```

### Step 2 — Create index and HEC (local Docker Splunk)

1. **Settings → Indexes → New** → `acme_agentic_telemetry`
2. **Settings → Data Inputs → HEC** → enable → new token  
   - Sourcetype: `otel:agentic:json`  
   - Index: `acme_agentic_telemetry`
3. Confirm `.env` HEC token matches Splunk token (see `docker-compose.yml` → `otel_collector`).

### Step 3 — Generate events

```bash
# Baseline (benign)
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"input":"Loan application $50k, income $85k"}'

# Three attacks
for i in 1 3 6; do curl -s -X POST http://localhost:5001/api/exploit/$i; sleep 2; done
```

Wait **30–60 seconds** for OTel → HEC batching.

### Step 4 — Verify ingest

```spl
index=acme_agentic_telemetry sourcetype="otel:agentic:json" earliest=-15m
| stats count by gen_ai.agent.name
```

You should see counts for banking agents. If zero, fix HEC/index before opening dashboards.

### Step 5 — Open dashboards (what “lit up” means)

| Dashboard | Lit up when… | What it tells you |
|-----------|--------------|-------------------|
| **Overview** | Event count > 0 | Lab is shipping telemetry; agents are active |
| **Detection Efficacy** | After 3+ scenarios or a kill chain | **Coverage %** — techniques observed vs 45 in registry; **MTTD** — avg time to block; **chain completeness** — stages per `incident_id` |
| **Control Attestation** | After scenarios 1–10 | **NIST pass/fail** — `control.status`, `control.pass_rate_pct` per scenario |
| **Technique Coverage Matrix** | After `execute-all` or many singles | Workshop matrix: OBSERVED vs NOT_OBSERVED per `technique_id` |
| **Threat Hunting** | Any attack | Starter SPL from playbooks — practitioner teaching view |
| **Actor Chain Story** | After `KC-*` chain run | Multi-stage narrative tied to `incident_id` |
| **MITRE ATLAS Heatmap** | Multiple techniques | Framework density over time |
| **NIST AI RMF Scoring** | Control fields populated | GOVERN / MAP / MEASURE / MANAGE evidence |

**Minimum viable demo:** Overview shows events → fire scenario 6 → Control Attestation shows a FAIL/PASS row → Detection Efficacy shows workflow block reason.

### Step 6 — Point macros at your index (if needed)

Edit **Settings → Advanced Search → Macros** → `acme_genai_index` if your index name differs from `acme_agentic_telemetry`.

---

## Top 10 scenarios — fire, expect, hunt

For each scenario: run exploit → wait 60s → run hunt SPL → open suggested dashboard.

### Scenario 1 — AI BOM / prompt drift

```bash
curl -X POST http://localhost:5001/api/exploit/1
```

| | |
|--|--|
| **Surface** | Supply chain / prompt drift |
| **Typical status** | May reach LLM; drift telemetry either way |
| **Key fields** | `cisco_aibom_status`, `agent.aibom_validated`, `model_artifact_hash_*` |

```spl
`acme_campaign_w1` earliest=-15m
| table _time gen_ai.agent.id cisco_aibom_status agent.aibom_validated model_artifact_hash_expected model_artifact_hash_found control.status
```

**Hunt questions:** Which agents show `PROMPT_DRIFT_DETECTED`? Do drift events share a `session.id`?

**Dashboard:** Control Attestation → scenario 1

---

### Scenario 2 — Orchestration / Foundry bypass

```bash
curl -X POST http://localhost:5001/api/exploit/2
```

| | |
|--|--|
| **Surface** | Orchestration |
| **Typical status** | **BLOCKED** — `ORCHESTRATION_POLICY_BYPASS` |
| **Key fields** | `foundry.trace_id`, `foundry.policy_status`, `workflow.block_reason` |

```spl
`acme_campaign_w2` earliest=-15m
| stats count by foundry.policy_status foundry.orchestrator_override workflow.block_reason workflow.rule_id
```

**Hunt:** `| search workflow.blocked=true AND foundry.orchestrator_override=true`

**Dashboard:** Detection Efficacy → Workflow Surface Blocks

---

### Scenario 3 — CodeGuard markup injection

```bash
curl -X POST http://localhost:5001/api/exploit/3
```

| | |
|--|--|
| **Surface** | Input validation |
| **Typical status** | **BLOCKED** — CodeGuard |
| **Key fields** | `codeguard.rule_id`, `codeguard_blocked`, `codeguard.field` |

```spl
`acme_campaign_w3` earliest=-15m
| table _time codeguard.rule_id codeguard.field codeguard_blocked gen_ai.agent.id
```

**Hunt:** Compare blocked vs passed ratio by `gen_ai.agent.id` over 24h.

---

### Scenario 4 — Shadow edge SLM

```bash
curl -X POST http://localhost:5001/api/exploit/4
```

| | |
|--|--|
| **Surface** | Unapproved runtime |
| **Typical status** | INJECTED with discovery telemetry |
| **Key fields** | `slm.unapproved`, `deployment.tier`, `llm.runtime`, `gen_ai.request.model` |

```spl
`acme_campaign_w4` earliest=-7d
| stats count values(gen_ai.request.model) as models by slm.unapproved deployment.tier llm.runtime
```

**Hunt:** `| search slm.unapproved=true` — asset discovery for unmapped models.

---

### Scenario 5 — Semantic jailbreak (DAN)

```bash
curl -X POST http://localhost:5001/api/exploit/5
```

| | |
|--|--|
| **Surface** | Output gateway |
| **Typical status** | BLOCKED if DefenseClaw fires; INJECTED if small model refuses harmlessly |
| **Key fields** | `defenseclaw.action`, `defenseclaw.rule_id`, `defenseclaw_blocked` |

```spl
`acme_campaign_w5` earliest=-15m
| search defenseclaw.action=HARD_DENY OR defenseclaw_blocked=true
| table _time gen_ai.agent.id defenseclaw.rule_id defenseclaw.matched_text gen_ai.output.preview
```

**Hunt:** Sessions with HARD_DENY but no CodeGuard block — output-side-only detection.

---

### Scenario 6 — MCP tool escape

```bash
curl -X POST http://localhost:5001/api/exploit/6
```

| | |
|--|--|
| **Surface** | Tools |
| **Typical status** | **BLOCKED** — `MCP_TOOL_SCOPE_VIOLATION` |
| **Key fields** | `tool.scope_violation`, `mcp.gateway.rule_id`, `gen_ai.tool.name` |

```spl
`acme_campaign_w6` earliest=-15m
| table _time session.id tool.scope_violation mcp.gateway.rule_id workflow.block_reason control.status
```

**Hunt:** Correlate `session.id` across agents — did tool abuse appear in a pipeline?

---

### Scenario 7 — Recursive token burn

```bash
curl -X POST http://localhost:5001/api/exploit/7
```

| | |
|--|--|
| **Surface** | Cost / DoS |
| **Typical status** | Often reaches LLM |
| **Key fields** | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `call_depth_detected` |

```spl
`acme_campaign_w7` earliest=-24h
| timechart sum(gen_ai.usage.input_tokens) sum(gen_ai.usage.output_tokens) by gen_ai.agent.id
| append [ search `acme_campaign_w7` call_depth_detected>=5 | stats max(call_depth_detected) as max_depth ]
```

**Hunt:** Token spikes > 3× baseline for same `gen_ai.agent.id`.

---

### Scenario 8 — A2A DID spoofing

```bash
curl -X POST http://localhost:5001/api/exploit/8
```

| | |
|--|--|
| **Surface** | Agent identity |
| **Typical status** | **BLOCKED** — `A2A_DELEGATION_VERIFICATION_FAILED` |
| **Key fields** | `did.document`, `cryptographic_passport_valid`, `delegation.chain` |

```spl
`acme_campaign_w8` earliest=-15m
| table _time requesting_agent_id target_agent_id did.document cryptographic_passport_valid a2a.verification_failure
```

**Hunt:** Impossible delegation paths — compliance agent accepting forged credit-risk DID.

---

### Scenario 9 — RAG exfiltration probe

```bash
curl -X POST http://localhost:5001/api/exploit/9
```

| | |
|--|--|
| **Surface** | Retrieval |
| **Typical status** | INJECTED + **alert** (detect-only by design) |
| **Key fields** | `galileo_observe_alert`, `galileo_anomaly_score`, `vector_retrieval_count` |

```spl
`acme_campaign_w9` earliest=-15m
| where galileo_observe_alert=true OR galileo_anomaly_score>0.7
| table _time vector_retrieval_count galileo_anomaly_score gen_ai.agent.id gen_ai.input.preview
```

**Hunt:** Retrieval rate >> baseline — “invisible leak” pattern.

---

### Scenario 10 — Rogue agent + containment

```bash
curl -X POST http://localhost:5001/api/exploit/10
```

| | |
|--|--|
| **Surface** | Memory + SOC response |
| **Typical status** | **BLOCKED** — memory policy; SOAR fields on emit |
| **Key fields** | `memory.policy.rule_id`, `soar.playbook_id`, `containment.action`, `containment.latency_ms` |

```spl
`acme_campaign_w10` earliest=-15m
| table _time memory.policy.rule_id containment.action containment.latency_ms soar.playbook_id control.status
```

**Hunt:** Time from first `AUTONOMOUS` pattern in input preview to `containment.action=QUARANTINE`.

---

### Run all 10 (workshop soak)

```bash
for i in $(seq 1 10); do curl -s -X POST http://localhost:5001/api/exploit/$i; sleep 3; done
```

```spl
`acme_genai_index` earliest=-1h campaign_week=*
| stats count by campaign_week workflow.block_reason defenseclaw.action
| sort campaign_week
```

---

## Multi-stage compromise scenarios (kill chains)

Use these when you need **multiple attacks in sequence** — closer to real adversary behavior than single exploits.

### How to run

```bash
# List chains
curl http://localhost:5000/api/v1/chains

# Execute (hybrid = live LLM + simulated OTel stages)
curl -X POST http://localhost:5001/api/chains/KC-C001/execute \
  -H "Content-Type: application/json" \
  -d '{"accelerated": true, "hybrid_live": true}'
```

Capture `incident_id` from the JSON response — all stages share it.

### Chain reference

| Chain ID | Name | Story (short) | Stages |
|----------|------|---------------|--------|
| **KC-A001** | Silent Data Harvest | Recon → RAG mapping → embedding exfil | 5 |
| **KC-B001** | Trojan Model Operation | Supply chain poison → backdoor → C2 | 5 |
| **KC-C001** | Fraudulent Loan Pipeline | Injection → tool escape → compliance bypass | 5 |
| **KC-D001** | Agent Impersonation Cascade | Identity spoof → lateral agent abuse | 5 |
| **KC-E001** | Denial-of-Wallet | Recursive loops → token exhaustion | 5 |

### Correlation hunt (any chain)

```spl
`acme_genai_index` incident_id=ACME-INC-* earliest=-1h
| stats values(technique_id) as techniques values(framework.kill_chain_stage) as stages count as events min(_time) as start max(_time) as end by incident_id
| eval dwell_sec=end-start
| eval stage_count=mvcount(stages)
| where stage_count>=2
| sort - stage_count
```

### Per-chain hunts

**KC-A001 — Silent Data Harvest (espionage)**

```bash
curl -X POST http://localhost:5001/api/chains/KC-A001/execute \
  -H "Content-Type: application/json" -d '{"accelerated": true, "hybrid_live": true}'
```

```spl
`acme_genai_index` earliest=-1h incident_id=*
| search technique_id=AML.T0038 OR technique_id=AML.T0037 OR galileo_observe_alert=true
| stats count values(technique_id) as chain_techniques by incident_id
| lookup acme_kill_chain_stages_lookup technique_id OUTPUT kill_chain_stage
```

**Dashboard:** Actor Chain Story → select `incident_id`

---

**KC-B001 — Trojan Model Operation (supply chain)**

```bash
curl -X POST http://localhost:5001/api/chains/KC-B001/execute \
  -H "Content-Type: application/json" -d '{"accelerated": true, "hybrid_live": true}'
```

```spl
`acme_genai_index` earliest=-1h
| search cisco_aibom_status=HASH_MISMATCH OR technique_id=AML.T0048 OR technique_id=AML.T0018
| table _time technique_id cisco_aibom_status model_artifact_hash_expected model_artifact_hash_found incident_id
```

---

**KC-C001 — Fraudulent Loan Pipeline (financial fraud)**

```bash
curl -X POST http://localhost:5001/api/chains/KC-C001/execute \
  -H "Content-Type: application/json" -d '{"accelerated": true, "hybrid_live": true}'
```

```spl
`acme_genai_index` earliest=-1h incident_id=*
| stats values(defenseclaw.action) as dc values(workflow.block_reason) as wf values(technique_id) as techniques by incident_id
| where mvcount(techniques)>=3
```

Pairs well with running Top 10 scenarios **5 → 6 → 8** manually in order (jailbreak → tools → identity).

---

**KC-D001 — Agent Impersonation Cascade**

```bash
curl -X POST http://localhost:5001/api/chains/KC-D001/execute \
  -H "Content-Type: application/json" -d '{"accelerated": true, "hybrid_live": true}'
```

```spl
`acme_genai_index` earliest=-1h
| search cryptographic_passport_valid=false OR technique_id=AML.T0058 OR delegation.chain=*
| table _time requesting_agent_id target_agent_id delegation.chain incident_id
```

---

**KC-E001 — Denial-of-Wallet (cost attack)**

```bash
curl -X POST http://localhost:5001/api/chains/KC-E001/execute \
  -H "Content-Type: application/json" -d '{"accelerated": true, "hybrid_live": true}'
```

```spl
`acme_genai_index` earliest=-1h incident_id=*
| stats sum(gen_ai.usage.input_tokens) as in_tok sum(gen_ai.usage.output_tokens) as out_tok max(call_depth_detected) as depth by incident_id
| eval total=in_tok+out_tok
| where total>500 OR depth>=5
```

---

### Manual multi-attack workshop (no chain API)

Simulate **compromise path: recon → tool → exfil**:

```bash
curl -X POST http://localhost:5001/api/exploit/4   # shadow model discovery
sleep 2
curl -X POST http://localhost:5001/api/exploit/6   # MCP tool escape
sleep 2
curl -X POST http://localhost:5001/api/exploit/9   # RAG probe
```

```spl
`acme_genai_index` earliest=-30m
| sort _time
| table _time campaign_week workflow.block_reason tool.scope_violation galileo_observe_alert gen_ai.agent.name
```

---

## 45-technique library

```bash
curl -X POST http://localhost:5001/api/techniques/AML.T0050/execute

curl -X POST http://localhost:5001/api/techniques/execute-all \
  -H "Content-Type: application/json" -d '{"delay_seconds": 0.3}'
```

```spl
| inputlookup acme_framework_lookup
| join type=left technique_id [
    search `acme_genai_index` earliest=-24h
    | stats count as events by technique_id
  ]
| eval status=if(isnull(events),"NOT_OBSERVED","OBSERVED")
| table technique_id technique_name tactic_name status events severity
```

**Dashboard:** Technique Coverage Matrix — aim for coverage % > 50% after full `execute-all`.

---

## Layered defenses (what blocked means)

| Layer | When | Module |
|-------|------|--------|
| Workflow guard | Pre-LLM | `workflow_guard.py` |
| CodeGuard | Pre-LLM | `llm_client.py` |
| DefenseClaw | Post-LLM | `llm_client.py` |
| Control evidence | On emit | `control_validator.py` |

| Attack panel status | Meaning |
|---------------------|---------|
| `BLOCKED` | Workflow guard, CodeGuard, or DefenseClaw stopped the request |
| `INJECTED` | Model was reached — use for detection-gap exercises |

---

## Banking app API

```bash
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"input": "Personal loan $25k, income $72k"}'

curl http://localhost:5000/api/v1/framework/playbooks
curl http://localhost:5000/api/v1/chains
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboards empty | Confirm index has data first (Step 4 above) |
| Macros fail | Edit `acme_genai_index` macro to match your index name |
| No Splunk events | HEC token, index permissions, `otel_collector` logs |
| Scenarios 2, 6, 8 always BLOCKED | Expected — pre-LLM workflow guards |
| Scenario 9 not blocked | Expected — RAG is detect-only |
| All INJECTED | Small models vary — hunt on telemetry fields |

---

## Learn more

- [THREAT_SURFACES.md](THREAT_SURFACES.md) — eight agentic threat surfaces (public reference)
- [README.md](../README.md) — architecture and configuration
- [splunk_app/INSTALL.md](../splunk_app/INSTALL.md) — Splunk Cloud / Enterprise
