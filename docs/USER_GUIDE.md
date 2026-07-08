# OrchestraACME — User Guide

Run the lab from the **Attack Panel**, generate telemetry, hunt in Splunk, and **light up** the GenAI Compliance Monitor app.

**Attack Panel:** http://localhost:5001  
**Banking app:** http://localhost:5000  
**Splunk:** http://localhost:8000 (local Docker profile)

> **Terminology:** The lab uses **Scenario 1–10** (one per agentic threat surface). Splunk macros still use `acme_campaign_w1` … `w10` and events carry `campaign_week=1..10` — same numbers, different label.

---

## 15-minute first win (start here)

If Splunk is already configured (index + HEC), this is the fastest path to a teaching moment.

| Step | Where | Action | Splunk (after 60s) | Why it matters |
|------|-------|--------|-------------------|----------------|
| 1 | Attack Panel → **// Workshop** | **▶ RUN FIRST WIN PATH** | — | Runs scenarios 6 → 5 → 9 automatically |
| 2 | Splunk Search | `` `acme_campaign_w6` `` earliest=-15m | Control Attestation | Proves **pre-LLM** MCP tool block |
| 3 | Splunk | Open **Detection Efficacy** | Workflow Surface Blocks | Shows `workflow.block_reason` before the model runs |
| 4 | Splunk | Open **Overview** | Event count > 0 | Confirms OTel → HEC → index pipeline |

**Or click manually:** Tab **Top 10 Scenarios** → **▶ FIRE SCENARIO 6**, then **5**, then **9** (~5s between each).

**Reflect after each step:**
- Scenario 6: *Why block tool abuse before the LLM runs?*
- Scenario 5: *When is post-LLM output inspection the right layer?*
- Scenario 9: *Why might detect-only be correct for retrieval exfil?*

---

## Prerequisites

```bash
git clone https://github.com/machowdhury/OrchestraACME.git
cd OrchestraACME
cp .env.example .env
docker compose --profile local up --build -d
```

Wait for Ollama (`docker compose logs -f ollama`). Install the Splunk app — [splunk_app/INSTALL.md](../splunk_app/INSTALL.md).

Confirm the panel header shows **TARGET ONLINE** and **LLM ONLINE** before firing attacks.

**Splunk quick checklist** (do once):

1. `./scripts/package_splunk_app.sh` → install `dist/acme_genai_compliance-2.2.0.tar.gz`
2. Index `acme_agentic_telemetry` + HEC token → sourcetype `otel:agentic:json`
3. Verify: `` index=acme_agentic_telemetry earliest=-15m | stats count ``

---

## Attack Panel — all options

Everything at **http://localhost:5001**. Five tabs on the left; **Real-Time Attack Feed** on the right.

```
Click (Workshop / Scenario / Chain) → Banking app → Ollama → OTel → Splunk → Dashboard
```

### Tab 0 — `// Workshop` (guided learning paths)

| Button | Duration | What runs | Splunk dashboards to open | Learning goal |
|--------|----------|-----------|---------------------------|---------------|
| **▶ RUN FIRST WIN PATH** | ~15 min | Scenarios 6 → 5 → 9 | Control Attestation, Detection Efficacy, Overview | Three control philosophies: pre-LLM block, output deny, detect-only |
| **▶ RUN STANDARD WORKSHOP** | ~25 min | First Win + chain **KC-C001** | + Actor Chain Story | Single surface vs multi-stage `incident_id` correlation |
| **▶ RUN DEEP WORKSHOP** | ~45+ min | Standard + **RUN ALL 45** | + Technique Coverage Matrix | Measurable MITRE coverage (OBSERVED vs NOT_OBSERVED) |
| **▶ FIRE ALL 10 SCENARIOS** | ~5 min | Scenarios 1–10 sequential | Control Attestation, NIST AI RMF, Heatmap | All eight agentic surfaces in one pass |

Progress and a Splunk checklist appear in the panel after each path completes.

---

### Tab 1 — `// Top 10 Scenarios`

| Button | What it does |
|--------|----------------|
| **▶ FIRE SCENARIO n → … AGENT** | One adversarial payload to one agent (fastest demo). |
| **⚡ Full Pipeline** | Same payload through all **4 agents** in sequence. |
| **👁 Preview Payload** | Raw attack string (does not fire). |

Cards are labeled **SCENARIO n — SURFACE** (e.g. Scenario 6 — TOOLS SURFACE). See [THREAT_SURFACES.md](THREAT_SURFACES.md) for the conceptual map.

---

### Tab 2 — `// All 45 Techniques`

| Button | What it does |
|--------|----------------|
| **↻ Reload Catalog** | Refresh 45 technique cards. |
| **⚡ RUN ALL 45 TECHNIQUES** | Full registry (LIVE + SIMULATED + HYBRID). ~10–20 min. |
| **▶ EXECUTE** (per card) | One technique (e.g. `AML.T0050`). |

| Mode | Meaning |
|------|---------|
| **LIVE** | Real Ollama call |
| **SIMULATED** | Enriched OTel only |
| **HYBRID** | Both |

---

### Tab 3 — `// Threat Chains`

| Button | What it does |
|--------|----------------|
| **▶ EXECUTE THREAT CHAIN** | All stages with shared `incident_id`. |

| Chain | Name |
|-------|------|
| KC-A001 | Silent Data Harvest |
| KC-B001 | Trojan Model Operation |
| KC-C001 | Fraudulent Loan Pipeline |
| KC-D001 | Agent Impersonation Cascade |
| KC-E001 | Denial-of-Wallet |

---

### Tab 4 — `// Custom Payload`

Custom string, agent picker, optional **Full Pipeline**, **▶ EXECUTE**.

---

## Light up the Splunk Compliance App

**“Lit up”** = events in `index=acme_agentic_telemetry`, macros resolve, dashboards show **non-zero** panels.

### What to click → dashboard → why

After each action: wait **30–60 seconds**.

| Your goal | What to click | Dashboard | Why it populates |
|-----------|---------------|-----------|------------------|
| Prove telemetry | Workshop **First Win** or any **▶ FIRE SCENARIO n** | **Overview** | `gen_ai.agent.*` on `otel:agentic:json` events |
| Input/output blocking | **Scenario 3** or **5** | **Control Attestation** | `codeguard_blocked`, `defenseclaw.action`, `control.status` |
| Workflow-surface blocks | **Scenario 2**, **6**, or **8** | **Detection Efficacy** | `workflow.block_reason` (orchestration, MCP, A2A) |
| All 10 surfaces | **FIRE ALL 10 SCENARIOS** (Workshop) | **Control Attestation** | `campaign_week=1..10` + NIST fields |
| Technique breadth | **RUN ALL 45** or Deep Workshop | **Technique Coverage Matrix** | `technique_id` → OBSERVED / NOT_OBSERVED |
| Multi-stage story | **KC-C001** or Standard Workshop | **Actor Chain Story** | Shared `incident_id` across stages |
| Detect-only RAG | **Scenario 9** | Threat Hunting / Overview | `galileo_observe_alert` without always blocking |
| Token / cost abuse | **Scenario 7** or **KC-E001** | **Detection Efficacy** | `gen_ai.usage.*_tokens`, `call_depth_detected` |

### Minimum viable check (2 minutes)

1. Workshop → **▶ RUN FIRST WIN PATH** (or **▶ FIRE SCENARIO 6**)
2. Splunk:

```spl
`acme_campaign_w6` earliest=-15m
| table _time tool.scope_violation workflow.block_reason control.status
```

3. **Control Attestation** — scenario 6 row has data  
4. **Overview** — event count > 0  

### Macro tweak

If Search has data but dashboards are empty, edit macro **`acme_genai_index`** to match your index name.

---

## Top 10 scenarios — surface, hunt, learning question

For each: **Top 10 Scenarios** tab → **▶ FIRE SCENARIO n** → wait 60s → SPL → dashboard.

| Scenario | Surface | Click | Typical status | Key fields | Learning question | Dashboard |
|----------|---------|-------|----------------|------------|-------------------|-----------|
| 1 | Supply chain / drift | **▶ FIRE SCENARIO 1** | Drift telemetry | `cisco_aibom_status`, `agent.aibom_validated` | *How would you detect prompt drift without blocking every request?* | Control Attestation |
| 2 | Orchestration | **▶ FIRE SCENARIO 2** | BLOCKED | `foundry.orchestrator_override`, `workflow.block_reason` | *Why enforce policy at the orchestrator, not only in prompts?* | Detection Efficacy |
| 3 | Input validation | **▶ FIRE SCENARIO 3** | BLOCKED | `codeguard.rule_id`, `codeguard_blocked` | *What attacks does input validation miss if you skip output inspection?* | Control Attestation |
| 4 | Shadow runtime | **▶ FIRE SCENARIO 4** | INJECTED + discovery | `slm.unapproved`, `deployment.tier` | *How do you govern models IT never approved?* | Overview |
| 5 | Output gateway | **▶ FIRE SCENARIO 5** | BLOCKED or INJECTED | `defenseclaw.action`, `defenseclaw_blocked` | *When is post-LLM output inspection the right layer?* | Control Attestation |
| 6 | Tools (MCP) | **▶ FIRE SCENARIO 6** | BLOCKED | `tool.scope_violation`, `mcp.gateway.rule_id` | *Why block tool abuse before the LLM runs?* | Detection Efficacy |
| 7 | Cost / DoS | **▶ FIRE SCENARIO 7** | Often INJECTED | `gen_ai.usage.*_tokens`, `call_depth_detected` | *What is your token budget alert threshold per agent?* | Detection Efficacy |
| 8 | Agent identity (A2A) | **▶ FIRE SCENARIO 8** | BLOCKED | `cryptographic_passport_valid=false` | *Who is allowed to delegate authority between agents?* | Control Attestation |
| 9 | Retrieval (RAG) | **▶ FIRE SCENARIO 9** | Alert, not always block | `galileo_observe_alert`, `galileo_anomaly_score` | *Why might detect-only be correct for retrieval exfil?* | Threat Hunting |
| 10 | Memory / SOC | **▶ FIRE SCENARIO 10** | BLOCKED + SOAR | `containment.action`, `soar.playbook_id` | *How fast must containment run once memory policy fires?* | Control Attestation |

### Example hunt — Scenario 6

```spl
`acme_campaign_w6` earliest=-15m
| table _time session.id tool.scope_violation mcp.gateway.rule_id workflow.block_reason control.status control.pass_rate_pct
```

### All 10 scenarios

Workshop → **▶ FIRE ALL 10 SCENARIOS**, then:

```spl
`acme_genai_index` earliest=-1h campaign_week=*
| stats count by campaign_week workflow.block_reason defenseclaw.action
| sort campaign_week
```

---

## Kill chains

**Tab 3** → **▶ EXECUTE THREAT CHAIN**, or use **Standard Workshop**.

| Chain | Best dashboard | Learning question |
|-------|----------------|-------------------|
| KC-A001 | Actor Chain Story | *How would you spot slow RAG exfil without a single HARD_DENY?* |
| KC-B001 | Control Attestation | *What supply-chain signal precedes model backdoor behavior?* |
| KC-C001 | Actor Chain Story | *Which stage would you block first in a fraud pipeline?* |
| KC-D001 | Control Attestation | *How do you bind agent identity cryptographically in production?* |
| KC-E001 | Detection Efficacy | *What cost anomaly would trigger finance + security jointly?* |

**Correlation hunt:**

```spl
`acme_genai_index` incident_id=ACME-INC-* earliest=-1h
| stats values(technique_id) as techniques values(framework.kill_chain_stage) as stages count as events by incident_id
| eval stage_count=mvcount(stages)
| where stage_count>=2
| sort - stage_count
```

---

## 45 techniques

**Tab 2** → **⚡ RUN ALL 45** or **Deep Workshop**.

```spl
| inputlookup acme_framework_lookup
| join type=left technique_id [
    search `acme_genai_index` earliest=-24h
    | stats count as events by technique_id
  ]
| eval status=if(isnull(events),"NOT_OBSERVED","OBSERVED")
| table technique_id technique_name tactic_name status events severity
```

Aim for **coverage % > 50%** on **Technique Coverage Matrix** after a full run.

---

## Layered defenses

| Layer | When | Terminal signal |
|-------|------|-------------------|
| Workflow guard | Before LLM | `workflow.block_reason` |
| CodeGuard | Before LLM | `codeguard_blocked=true` |
| DefenseClaw | After LLM | `defenseclaw.action=HARD_DENY` |

| Status | Meaning |
|--------|---------|
| **BLOCKED** | Guard fired — still valuable Splunk evidence |
| **INJECTED** | Model reached — detection-gap exercise |

---

## Optional: curl equivalents

```bash
curl -X POST http://localhost:5001/api/exploit/6
curl -X POST http://localhost:5001/api/exploit/pipeline/6
curl -X POST http://localhost:5001/api/techniques/AML.T0050/execute
curl -X POST http://localhost:5001/api/techniques/execute-all -H "Content-Type: application/json" -d '{"delay_seconds":0.2}'
curl -X POST http://localhost:5001/api/chains/KC-C001/execute -H "Content-Type: application/json" -d '{"accelerated":true,"hybrid_live":true}'
```

---

## Banking app (benign baseline)

http://localhost:5000 — normal loan through **Run Through All Agents** before workshops (establishes “good” telemetry contrast).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **TARGET OFFLINE** | `docker compose ps` — banking_app healthy |
| **LLM OFFLINE** | Wait for Ollama; check `/api/v1/ollama/health` |
| Workshop stuck | Keep tab open; Deep Workshop includes 10–20 min RUN ALL 45 |
| Tab 2 / 3 empty | **↻ Reload Catalog** or refresh |
| Dashboards empty, Search has data | Fix `acme_genai_index` macro |
| Scenarios 2, 6, 8 always BLOCKED | Expected — pre-LLM guards |
| Scenario 9 not blocked | Expected — detect-only |

---

## Learn more

- [THREAT_SURFACES.md](THREAT_SURFACES.md) — surfaces vs prompts; framework crosswalk
- [README.md](../README.md) — architecture
- [splunk_app/INSTALL.md](../splunk_app/INSTALL.md) — Splunk install
