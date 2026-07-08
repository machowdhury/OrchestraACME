# OrchestraACME — User Guide

Run the lab from the **Attack Panel**, generate telemetry, hunt in Splunk, and **light up** the GenAI Compliance Monitor app.

**Attack Panel:** http://localhost:5001  
**Banking app:** http://localhost:5000  
**Splunk:** http://localhost:8000 (local Docker profile)

> **Terminology:** The lab uses **Scenario 1–10** (one per agentic threat surface). Splunk macros still use `acme_campaign_w1` … `w10` and events carry `campaign_week=1..10` — same numbers, different label.

**New here?** Complete [Prerequisites](#prerequisites), then read [The Workshop (full guide)](#the-workshop-full-guide) and run **15-Minute First Win**.

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

## The Workshop (full guide)

The **Workshop** is the default tab on the Attack Panel. It is a set of **guided learning paths** — ordered sequences of real attacks that produce Splunk evidence you can teach from. You do not need to know which scenario to fire first or which dashboard to open; the path and the panel tell you.

### Why run the Workshop?

Most agentic-AI security training fails in one of two ways:

1. **Theory without telemetry** — slides about MCP and RAG, but no observable `workflow.block_reason` in a SIEM.
2. **Telemetry without narrative** — random prompt injections with no story about *which surface* failed and *why that control exists*.

The Workshop fixes both. Every path:

- Fires **real** HTTP traffic through the banking app and **real** Ollama inference (not mocked responses).
- Exercises **workflow-surface defenses** (tools, output gateway, retrieval) — not prompt strings alone.
- Emits **OpenTelemetry** security fields your Splunk app already knows how to chart.
- Ends with a **Splunk checklist** so you know what “success” looks like in the compliance app.

**Run the Workshop if you are:**

| Audience | Start with |
|----------|------------|
| First-time lab user | **15-Minute First Win** |
| Workshop facilitator (classroom / brown-bag) | **Standard Workshop** |
| Detection engineer proving coverage | **Deep Workshop** |
| Someone validating all NIST / surface mappings | **Fire All 10 Scenarios** |

**Skip the Workshop** only if you already know exactly which `technique_id` or `incident_id` hunt you need — then use **Top 10**, **45 Techniques**, or **Threat Chains** directly.

### How to run it (step by step)

1. **Complete prerequisites** above — Docker stack healthy, Splunk index + HEC working, compliance app installed.
2. Open **http://localhost:5001** and confirm **TARGET ONLINE** and **LLM ONLINE** in the header.
3. Stay on the **// Workshop** tab (default).
4. Pick a path and click the green **▶ RUN …** button.
5. **Confirm** the dialog — paths run multiple steps; keep the browser tab open.
6. Watch the **Real-Time Attack Feed** on the right: `BLOCKED` and `INJECTED` are both valid teaching outcomes.
7. Read the **progress box** at the bottom of the Workshop tab — it shows the current step and reflection prompts (First Win path).
8. When the path completes, wait **60 seconds** for OTel batching → HEC → index.
9. Open the **Splunk dashboards** listed in the completion checklist.
10. Run the suggested SPL (in this guide or in **Threat Hunting** inside the app) to connect clicks to fields.

**Facilitator tip:** Run one benign loan on http://localhost:5000 *before* the Workshop so **Overview** shows normal traffic next to attack traffic.

### What you get out of it (benefits)

| Benefit | Where you see it | Why it matters for education |
|---------|------------------|------------------------------|
| **Proof the pipeline works** | Splunk **Overview** — event count > 0 | Students trust the lab before you teach detections |
| **Three control philosophies in one sitting** | First Win → scenarios 6, 5, 9 | Pre-LLM block vs post-LLM deny vs detect-only alert |
| **Correlated multi-stage attacks** | Standard Workshop → **Actor Chain Story** | Real incidents span stages; `incident_id` ties them together |
| **Measurable MITRE coverage** | Deep Workshop → **Technique Coverage Matrix** | Coverage % is defensible in audits and roadmaps |
| **NIST control evidence** | Fire All 10 → **Control Attestation** | Pass/fail per scenario, not hand-wavy “we use AI responsibly” |
| **Hunt-ready SPL** | Macros `` `acme_campaign_w6` `` etc. | Practitioners leave with queries, not just screenshots |
| **Honest limit cases** | Terminal shows INJECTED on some runs | Teaches detection gaps when models behave unpredictably |

### Workshop paths explained

#### 15-Minute First Win (~15 min)

**Runs:** Scenario 6 (MCP tools) → Scenario 5 (output gateway) → Scenario 9 (RAG detect-only).

**Why this order:** Each step teaches a *different layer* of defense:

```text
Scenario 6 — workflow guard blocks BEFORE the LLM (tool scope)
Scenario 5 — DefenseClaw may block AFTER the LLM (output)
Scenario 9 — alert fires without always blocking (retrieval monitoring)
```

**Splunk after:** Control Attestation, Detection Efficacy (Workflow Surface Blocks), Overview.

**Reflection prompts** (built into the panel):

- *Why block tool abuse before the LLM runs?*
- *When is post-LLM output inspection the right layer?*
- *Why might detect-only be correct for retrieval exfil?*

#### Standard Workshop (~25 min)

**Runs:** First Win path + kill chain **KC-C001** (Fraudulent Loan Pipeline).

**Why add a chain:** Single scenarios teach **surfaces**. Kill chains teach **adversary behavior over time** — the same `incident_id` appears across stages, mimicking how SOC analysts correlate alerts.

**Splunk after:** + **Actor Chain Story** (filter by `incident_id`).

#### Deep Workshop (~45+ min)

**Runs:** Standard Workshop + **RUN ALL 45 TECHNIQUES** (10–20 min automated).

**Why add 45 techniques:** Top 10 scenarios are **high-fidelity demos**. The full registry proves **breadth** — which MITRE ATLAS techniques your telemetry can observe vs gaps (NOT_OBSERVED).

**Splunk after:** + **Technique Coverage Matrix**, **Detection Efficacy** (coverage %, MTTD).

**Note:** Keep the Attack Panel tab open during RUN ALL 45; do not close the browser mid-run.

#### Fire All 10 Scenarios (~5 min active clicking, ~10 min with Splunk)

**Runs:** Scenarios 1–10 in order with pauses for ingest.

**Why:** Maps every **agentic threat surface** in [THREAT_SURFACES.md](THREAT_SURFACES.md) to `campaign_week=1..10` and NIST control fields — ideal before a compliance or risk audience.

**Splunk after:** Control Attestation (all rows), NIST AI RMF Scoring, MITRE ATLAS Heatmap.

### Quick start — 15-minute first win

| Step | Where | Action | Splunk (after 60s) | Why it matters |
|------|-------|--------|-------------------|----------------|
| 1 | Attack Panel → **// Workshop** | **▶ RUN FIRST WIN PATH** | — | Runs scenarios 6 → 5 → 9 automatically |
| 2 | Splunk Search | `` `acme_campaign_w6` `` earliest=-15m | Control Attestation | Proves **pre-LLM** MCP tool block |
| 3 | Splunk | Open **Detection Efficacy** | Workflow Surface Blocks | Shows `workflow.block_reason` before the model runs |
| 4 | Splunk | Open **Overview** | Event count > 0 | Confirms OTel → HEC → index pipeline |

**Manual equivalent:** Tab **Top 10 Scenarios** → **▶ FIRE SCENARIO 6**, then **5**, then **9** (~5s between each).

---

## Beyond the Workshop — expand your knowledge

The Workshop is the **on-ramp**. The other Attack Panel tabs and Splunk dashboards are how you go deeper. Use this map to decide what to explore next and **why** each capability exists.

### Learning progression

```text
Workshop (guided paths)
    ↓
Top 10 Scenarios (one surface at a time, Full Pipeline variant)
    ↓
Threat Chains (multi-stage stories, incident_id correlation)
    ↓
All 45 Techniques (MITRE breadth, LIVE / SIMULATED / HYBRID modes)
    ↓
Custom Payload (your own strings, agent targeting)
    ↓
Splunk Threat Hunting + SPL macros (practitioner hunts)
```

### Additional capabilities — what, why, when

| Capability | Where | What it adds beyond Workshop | Why we built it |
|------------|-------|------------------------------|-----------------|
| **Individual scenarios** | Top 10 tab | Pause on one surface; use **Preview Payload** | Deep-dive a single OWASP / NIST mapping in class |
| **Full Pipeline** | Top 10 → ⚡ on any card | Same attack through **all 4 agents** | Shows how one payload propagates across an agent chain |
| **Threat Chains (KC-*)** | Threat Chains tab | 5-stage rogue-actor narratives | Teaches kill-chain thinking and `incident_id` hunts |
| **45-technique registry** | All 45 tab | Full MITRE ATLAS library; per-technique **EXECUTE** | Proves detection **coverage %**, not just 10 demos |
| **LIVE vs SIMULATED vs HYBRID** | Technique cards | Some threats cannot be ethically live-fired | Supply-chain / recon style events still appear in Splunk for hunts |
| **Custom Payload** | Custom tab | Your own injection strings | Red-team exercises and variant testing |
| **Control Attestation dashboard** | Splunk app | NIST pass/fail per scenario | Bridges security engineering and governance audiences |
| **Detection Efficacy dashboard** | Splunk app | Coverage %, MTTD, chain completeness | Answers “are we measuring agentic risk?” with numbers |
| **Technique Coverage Matrix** | Splunk app | OBSERVED vs NOT_OBSERVED grid | Prioritize purple-team backlog from evidence |
| **Actor Chain Story** | Splunk app | Timeline per `incident_id` | SOC-style narrative for leadership |
| **Threat Hunting playbooks** | Splunk app | Starter SPL per technique | Graduates learners from buttons to queries |

### Suggested expansion paths by goal

| Your goal | After Workshop, do this |
|-----------|------------------------|
| Teach **one** surface deeply (e.g. MCP tools) | Top 10 → Scenario 6 only → run hunt SPL → discuss BLOCKED vs INJECTED |
| Teach **pipeline** risk | Same scenario with **⚡ Full Pipeline** → compare single-agent vs 4-agent events |
| Teach **SOC correlation** | Threat Chains → KC-A001 and KC-D001 → Actor Chain Story + correlation SPL |
| Build a **coverage report** | All 45 → RUN ALL 45 → Technique Coverage Matrix screenshot + NOT_OBSERVED list |
| Teach **governance** | Fire All 10 → Control Attestation + NIST AI RMF Scoring walkthrough |
| Run a **mini red team** | Custom tab + mix of chains; learners write hunts in Splunk |

---

## What we built the Workshop with (lab stack)

The Workshop is not a separate product — it orchestrates components already in OrchestraACME. Understanding the stack helps you explain the lab credibly and troubleshoot when something does not light up.

### End-to-end flow

```text
Workshop button (Attack Panel :5001)
    → REST API (/api/exploit, /api/chains, /api/techniques/execute-all)
    → Banking app (:5000) — 4 agents, workflow guards, CodeGuard, DefenseClaw
    → Ollama (:11434) — live LLM inference (llama3.2:1b by default)
    → OpenTelemetry spans + security attributes
    → OTel Collector (:4318) — batch, enrich
    → Splunk HEC (:8088) — index acme_agentic_telemetry
    → GenAI Compliance Monitor app — dashboards, macros, hunts
```

### Components called by Workshop paths

| Component | Role in Workshop | Path / artifact |
|-----------|------------------|-----------------|
| **Attack Panel** (`apps/exploit_ui.py`) | UI, Workshop sequencer, terminal feed | http://localhost:5001 |
| **Workshop definitions** | Step lists, delays, Splunk checklist (client-side `WORKSHOPS` object) | Attack Panel `// Workshop` tab |
| **Banking app** (`apps/app_runtime.py`, `agents/agent_router.py`) | Agent APIs, pipeline, OTel export | http://localhost:5000 |
| **Attack payloads** (`apps/framework/attack_payloads.py`) | Scenarios 1–10 adversarial strings + metadata | Used by `/api/exploit/<n>` |
| **Workflow guard** (`apps/framework/workflow_guard.py`) | Pre-LLM policy — orchestration, MCP, A2A, memory | Scenarios 2, 6, 8, 10 |
| **MCP gateway** (`apps/framework/mcp_gateway.py`) | Tool scope enforcement | Scenario 6, KC-C001 stages |
| **A2A verifier** (`apps/framework/a2a_verifier.py`) | Delegation / DID checks | Scenario 8, KC-D001 |
| **Memory policy** (`apps/framework/memory_policy.py`) | Persistent instruction abuse | Scenario 10 |
| **RAG store / probe** (`apps/framework/rag_store.py`) | Retrieval anomaly telemetry | Scenario 9, KC-A001 |
| **Orchestration guard** (`apps/framework/orchestration_guard.py`) | Supervisor bypass detection | Scenario 2 |
| **CodeGuard** (in `llm_client.py`) | Input pattern block | Scenario 3 |
| **DefenseClaw** (in `llm_client.py`) | Output HARD_DENY | Scenario 5 |
| **Control validator** (`control_validator.py` + `control_matrix.yaml`) | NIST pass/fail on emit | Control Attestation dashboard |
| **Technique executor** (`apps/framework/technique_executor.py`) | 45 MITRE playbooks (LIVE/SIM/HYBRID) | Deep Workshop, All 45 tab |
| **Kill chain engine** (`apps/framework/chain_engine.py`) | KC-A001…E001 staged execution + `incident_id` | Standard Workshop |
| **Ollama** | Local LLM — non-deterministic BLOCKED vs INJECTED | Docker service `ollama` |
| **OTel Collector** | OTLP → Splunk HEC + optional JSONL | `otel_collector` in compose |
| **Splunk compliance app** | Dashboards, lookups, macros `` `acme_campaign_w1` `` … | `splunk_app/splunk_compliance_app/` |

### Splunk artifacts the Workshop expects

| Artifact | Purpose |
|----------|---------|
| Index `acme_agentic_telemetry` | Stores all workshop-generated events |
| Sourcetype `otel:agentic:json` | HEC routing |
| Macro `` `acme_genai_index` `` | Base search for all dashboards |
| Macros `` `acme_campaign_w1` `` … `` `w10` `` | Per-scenario hunts (match Scenario 1–10) |
| Lookups `acme_framework_lookup`, `acme_control_matrix_lookup` | Technique matrix + NIST attestation |
| Dashboards Overview, Detection Efficacy, Control Attestation, Technique Coverage Matrix, Actor Chain Story | Workshop completion checklists |

### What is real vs simulated (teach this honestly)

| Real | Simulated / enriched (still valid for hunts) |
|------|---------------------------------------------|
| HTTP attack traffic, Ollama inference | Some 45-technique **SIMULATED** events (supply chain, recon) |
| CodeGuard / DefenseClaw / workflow guard decisions | SOAR containment fields (lab stub, not a live SOAR) |
| OTel → Splunk pipeline (when HEC configured) | “Cisco” product names on fields — lab middleware, not commercial products |
| Kill chain **HYBRID** stages where live LLM applies | Accelerated chain timing (`accelerated: true`) |

Saying this out loud in a workshop builds trust and mirrors how production ranges mix live execution with safe simulation.

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
- [README.md](../README.md) — architecture, A+ lab modules, honest limits
- [splunk_app/INSTALL.md](../splunk_app/INSTALL.md) — Splunk install
