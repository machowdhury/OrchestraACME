# OrchestraACME Workshop Curriculum

**Ordered learning path** for security analysts, detection engineers, architects, and compliance teams.

| Resource | URL |
|----------|-----|
| Attack Panel (run paths) | http://localhost:5001 → **// Workshop** |
| Splunk (run hunts) | http://localhost:8000 → **Search** or app dashboards |
| Banking app | http://localhost:5000 |

**Companion docs:** [USER_GUIDE.md](USER_GUIDE.md) (dashboards) · [THREAT_SURFACES.md](THREAT_SURFACES.md) · [MAESTRO_WORKSHOP.md](MAESTRO_WORKSHOP.md) · [CISCO_INTEGRATION.md](CISCO_INTEGRATION.md)

---

## How to use this guide

Read top to bottom **once**, then jump to your role track. Every level assumes the previous level is complete.

```text
Level 0  Environment          (everyone, ~20 min)
Level 1  Pipeline proof        (everyone, ~15 min)
Level 2  SOC hunts            (analysts, ~45 min)     ← BOTS-style questions in Splunk Search
Level 3  Correlation          (senior analyst, ~30 min)
Level 4  Detection engineering (detection engineer, ~60 min)
Level 5  Architecture & GRC    (architect + compliance, ~90 min)
```

**Where to run queries:** Always in **Splunk Search** (or copy from **Threat Hunting** / **MLTK Anomaly Hunting** dashboards). Do not skip Splunk — the workshop is designed to build SIEM muscle memory.

**Where to fire attacks:** Attack Panel → **// Workshop** (or individual scenario buttons).

**Timing rule:** Wait **60 seconds** after each Attack Panel path before running SPL.

---

## Level 0 — Environment (everyone)

**Goal:** Prove Docker, LLM, and Splunk ingest work before teaching anything else.

| Step | Action | Pass criteria |
|------|--------|---------------|
| 0.1 | `docker compose --profile local up -d` | `docker compose ps` shows healthy containers |
| 0.2 | Open Attack Panel http://localhost:5001 | Header: **TARGET ONLINE**, **LLM ONLINE** |
| 0.3 | Install Splunk compliance app — [splunk_app/INSTALL.md](../splunk_app/INSTALL.md) | App visible in Splunk |
| 0.4 | Configure HEC → index `acme_agentic_telemetry`, sourcetype `otel:agentic:json` | See Setup Guide dashboard |
| 0.5 | Run benign loan on http://localhost:5000 | Splunk Overview shows events > 0 |

**Verification SPL:**

```spl
`acme_genai_index` earliest=-15m
| stats count by gen_ai.agent.name
```

---

## Level 1 — Pipeline proof (everyone)

**Goal:** See three different control philosophies in one sitting.

**Attack Panel:** **▶ RUN FIRST WIN PATH** (Scenarios 6 → 5 → 9)

| Scenario | Surface | What you teach |
|----------|---------|----------------|
| 6 | MCP tools | Block **before** LLM (`workflow.block_reason`) |
| 5 | Output gateway | Block or flag **after** LLM (`defenseclaw.action`) |
| 9 | RAG | **Detect-only** — alert without always blocking |

**Splunk dashboards:** Overview · Detection Efficacy · Control Attestation

**Level 1 check — answer in Splunk Search:**

<details>
<summary><strong>Q101</strong> — Which scenario produced a workflow block before the model ran?</summary>

```spl
`acme_genai_index` earliest=-30m campaign_week=6
| stats count by workflow.block_reason workflow.blocked
```

Look for `workflow.blocked=true` and a tool-scope `workflow.block_reason` on Scenario 6 events.

</details>

<details>
<summary><strong>Q102</strong> — Which field tells you DefenseClaw acted on output?</summary>

```spl
`acme_genai_index` earliest=-30m campaign_week=5
| table defenseclaw.action defenseclaw_blocked codeguard_blocked workflow.blocked
```

**Answer field:** `defenseclaw.action` (e.g. `HARD_DENY`, `ALLOW`).

</details>

<details>
<summary><strong>Q103</strong> — Scenario 9: was the attack blocked or only observed?</summary>

```spl
`acme_campaign_w9` earliest=-30m
| table workflow.blocked galileo_observe_alert vector_retrieval_count control.status
```

Discuss why detect-only may be correct for retrieval exfiltration.

</details>

---

## Level 2 — SOC hunts (junior → senior analyst)

**Goal:** Field discovery and hunt writing — same pedagogy as [Splunk BOTS](https://github.com/splunk/botsv3) 200-series, but on agentic telemetry.

**Prerequisite:** Level 1 complete.

**Attack Panel:** **▶ RUN FIRST WIN PATH** again if events aged out, then fire **Scenario 8** manually (Top 10 tab).

### Hunt progression (do in order)

| # | Question | Skill |
|---|----------|-------|
| Q201 | What sourcetype/index holds agentic events? | Index discovery |
| Q202 | Which agents appear in telemetry? | Field inventory |
| Q203 | How many events per `campaign_week`? | Aggregation |
| Q204 | What blocked Scenario 6? | Workflow forensics |
| Q205 | Which MITRE technique IDs fired? | Framework fields |
| Q206 | Token usage for Scenario 7 | Cost / DoS hunting |
| Q207 | A2A identity failure on Scenario 8 | Multi-agent trust |
| Q208 | RAG indicators on Scenario 9 | Retrieval hunting |
| Q209 | Memory / containment on Scenario 10 | Autonomous escape |
| Q210 | Events sharing one `incident_id` | Correlation prep |

<details>
<summary><strong>Q201</strong> — What index and sourcetype should you search?</summary>

```spl
index=acme_agentic_telemetry earliest=-1h
| stats count by sourcetype
```

**Expected sourcetype:** `otel:agentic:json` · Shortcut macro: `` `acme_genai_index` ``

</details>

<details>
<summary><strong>Q202</strong> — List the four banking agents seen in telemetry.</summary>

```spl
`acme_genai_index` earliest=-1h
| stats count by gen_ai.agent.name
| sort -count
```

**Expected:** `acme-agent-intake-001`, `acme-agent-docingest-002`, `acme-agent-creditrisk-003`, `acme-agent-compliance-004`

</details>

<details>
<summary><strong>Q203</strong> — Event count per campaign week after First Win.</summary>

```spl
`acme_genai_index` earliest=-30m
| stats count by campaign_week
| sort campaign_week
```

</details>

<details>
<summary><strong>Q204</strong> — What workflow block reason appears for MCP tool abuse?</summary>

```spl
`acme_campaign_w6` earliest=-30m
| stats count by workflow.block_reason tool.scope_violation workflow.blocked
```

</details>

<details>
<summary><strong>Q205</strong> — Which `technique_id` values appear?</summary>

```spl
`acme_genai_index` earliest=-30m
| stats count by technique_id framework.severity
| sort -count
```

</details>

<details>
<summary><strong>Q206</strong> — Fire Scenario 7, then find token surge fields.</summary>

Attack Panel → **▶ FIRE SCENARIO 7**, wait 60s.

```spl
`acme_campaign_w7` earliest=-15m
| table gen_ai.usage.input_tokens gen_ai.usage.output_tokens call_depth_detected campaign_week
| sort - gen_ai.usage.input_tokens
```

</details>

<details>
<summary><strong>Q207</strong> — A2A spoof indicators (Scenario 8).</summary>

```spl
`acme_campaign_w8` earliest=-15m
| table cryptographic_passport_valid a2a.sender_agent workflow.block_reason
```

</details>

<details>
<summary><strong>Q208</strong> — RAG exfil indicators (Scenario 9).</summary>

```spl
`acme_campaign_w9` earliest=-15m
| table galileo_observe_alert vector_retrieval_count workflow.blocked
```

</details>

<details>
<summary><strong>Q209</strong> — Memory / SOC bypass (Scenario 10).</summary>

```spl
`acme_campaign_w10` earliest=-15m
| table memory.policy.rule_id containment.action workflow.blocked
```

</details>

<details>
<summary><strong>Q210</strong> — Preview: events that share an incident_id (Level 3).</summary>

```spl
`acme_genai_index` earliest=-1h incident_id=*
| stats count by incident_id
| where count > 1
```

If empty, complete Level 3 first.

</details>

**Splunk dashboards:** Threat Hunting · Overview · Detection Efficacy

---

## Level 3 — Correlation (senior analyst)

**Goal:** Multi-stage adversary behavior tied by `incident_id`.

**Attack Panel:** **▶ RUN STANDARD WORKSHOP** (First Win + kill chain **KC-C001**)

| Concept | Field | Dashboard |
|---------|-------|-----------|
| Single-surface attack | `campaign_week`, `trace_id` | Control Attestation |
| Multi-stage story | `incident_id` | Actor Chain Story |
| Timeline | `_time`, `kill_chain.stage` | Kill-Chain Timeline |

<details>
<summary><strong>Q301</strong> — How many stages fired for KC-C001?</summary>

```spl
`acme_genai_index` earliest=-1h
| search incident_id=*
| stats dc(kill_chain.stage) AS stages values(kill_chain.stage) BY incident_id
```

</details>

<details>
<summary><strong>Q302</strong> — Which agents participated in one incident?</summary>

```spl
`acme_genai_index` earliest=-1h incident_id=*
| stats values(gen_ai.agent.name) AS agents BY incident_id
```

</details>

<details>
<summary><strong>Q303</strong> — Were any chain stages blocked?</summary>

```spl
`acme_genai_index` earliest=-1h incident_id=*
| stats count by incident_id workflow.blocked defenseclaw_blocked codeguard_blocked
```

</details>

**Splunk dashboards:** Actor Chain Story · Kill-Chain Timeline · Detection Efficacy (chain completeness)

---

## Level 4 — Detection engineering

**Goal:** Measurable coverage, playbooks, and optional Cisco/MLTK overlay.

**Audience:** Detection engineers, security engineers building rules.

### Track 4A — Coverage breadth (~45 min)

**Attack Panel:** **▶ RUN DEEP WORKSHOP** (Standard + RUN ALL 45 TECHNIQUES)

Keep the browser tab open 10–20 minutes during RUN ALL 45.

<details>
<summary><strong>Q401</strong> — What percentage of techniques are OBSERVED?</summary>

Open **Technique Coverage Matrix** dashboard, or:

```spl
| inputlookup acme_framework_lookup
| eval observed=if([| `acme_genai_index` earliest=-24h | stats count BY technique_id | rename technique_id AS tid | eval observed=1 | table tid observed], 1, 0)
```

Prefer the dashboard for workshop delivery.

</details>

<details>
<summary><strong>Q402</strong> — List NOT_OBSERVED techniques (purple-team backlog).</summary>

Use **Technique Coverage Matrix** → filter NOT_OBSERVED, or Threat Hunting playbook list.

</details>

<details>
<summary><strong>Q403</strong> — Mean time to detect proxy: events with `defenseclaw_blocked` or `workflow.blocked`.</summary>

```spl
`acme_genai_index` earliest=-24h (workflow.blocked=true OR defenseclaw_blocked=true OR codeguard_blocked=true)
| timechart span=1h count
```

</details>

### Track 4B — Cisco + MLTK overlay (~30 min, optional)

**Prerequisite:** `docker compose -f docker-compose.yml -f docker-compose.cisco.yml --profile local up -d`

**Attack Panel:** **▶ RUN CISCO + MLTK PATH**

See [CISCO_INTEGRATION.md](CISCO_INTEGRATION.md) and Splunk **MLTK Anomaly Hunting** dashboard.

<details>
<summary><strong>Q404</strong> — AIBOM scan telemetry after Scenario 1.</summary>

```spl
`acme_campaign_w1` earliest=-30m
| table cisco_aibom_status agent.aibom_validated model_artifact_hash_expected model_artifact_hash_found
```

</details>

**Splunk dashboards:** Technique Coverage Matrix · Detection Efficacy · MLTK Anomaly Hunting

---

## Level 5 — Architecture & compliance

**Goal:** Design-time modeling + governance evidence for architects and GRC.

### Track 5A — MAESTRO threat modeling (architects)

**Attack Panel:** **▶ RUN MAESTRO VALIDATE PATH**

Full procedure: [MAESTRO_WORKSHOP.md](MAESTRO_WORKSHOP.md)

<details>
<summary><strong>Q501</strong> — MAESTRO layer coverage after validation path.</summary>

```spl
`acme_genai_index` earliest=-30m
| mvexpand framework.maestro_layers
| search framework.maestro_layers=L*
| stats dc(framework.maestro_layers) AS layers_at_risk
| eval maestro_coverage_pct=round(layers_at_risk/7*100,1)
```

Target: **>50%** after Scenarios 6, 8, 9, 10.

</details>

### Track 5B — Compliance attestation (GRC)

**Attack Panel:** **▶ FIRE ALL 10 SCENARIOS**

<details>
<summary><strong>Q502</strong> — NIST control pass/fail per scenario.</summary>

Open **Control Attestation** dashboard, or:

```spl
`acme_genai_index` earliest=-1h
| stats latest(control.status) AS control_status BY campaign_week control.control_id
| sort campaign_week
```

</details>

<details>
<summary><strong>Q503</strong> — OWASP LLM risk categories observed.</summary>

Open **NIST AI RMF Scoring** dashboard (OWASP panels), or:

```spl
`acme_genai_index` earliest=-1h
| mvexpand framework.owasp_llm
| stats count by framework.owasp_llm
```

</details>

**Splunk dashboards:** NIST AI RMF Scoring · Control Attestation · MITRE ATLAS Heatmap

---

## Role quick-start (pick one row)

| Role | Start here | Through level | Attack Panel path | Primary Splunk views |
|------|------------|---------------|-------------------|----------------------|
| **Junior SOC analyst** | Level 0 → 1 | Level 2 (Q201–Q210) | First Win | Overview, Threat Hunting |
| **Senior SOC analyst** | Level 1 | Level 3 (Q301–Q303) | Standard Workshop | Actor Chain Story, Kill-Chain Timeline |
| **Detection engineer** | Level 2 | Level 4 (Q401–Q404) | Deep Workshop + optional Cisco | Technique Coverage, Detection Efficacy |
| **Security engineer** | Level 1 | Level 2 + Top 10 **Full Pipeline** | First Win + manual scenarios | Detection Efficacy, workflow fields |
| **Security architect** | Level 3 | Level 5A (MAESTRO) | MAESTRO Validate | NIST AI RMF, MAESTRO coverage % |
| **Compliance / GRC** | Level 1 | Level 5B (Q502–Q503) | Fire All 10 | Control Attestation, NIST AI RMF |
| **Facilitator (half-day)** | Level 0 | Levels 1 → 3 | First Win → Standard | All dashboards in order |
| **Facilitator (full day)** | Level 0 | Levels 1 → 5 | Deep + Fire All 10 | Full app nav |

---

## Attack Panel path reference

| Button | Scenarios / steps | Maps to level |
|--------|-------------------|---------------|
| **15-Minute First Win** | 6 → 5 → 9 | Level 1 |
| **Standard Workshop** | First Win + KC-C001 | Level 3 |
| **Deep Workshop** | Standard + RUN ALL 45 | Level 4A |
| **Fire All 10 Scenarios** | 1–10 | Level 5B |
| **MAESTRO Validate** | MAESTRO briefing + 6,8,9,10 | Level 5A |
| **Cisco + MLTK** | Preflight + 1,6,7,9 | Level 4B |

---

## Facilitator runbook (90-minute session)

| Min | Activity | Materials |
|-----|----------|-----------|
| 0–15 | Level 0 + Level 1 live demo | Attack Panel First Win, Splunk Overview |
| 15–40 | Learners Level 2 hunts Q201–Q207 | This doc, Splunk Search |
| 40–55 | Instructor Level 3 KC-C001 story | Actor Chain Story dashboard |
| 55–70 | Q208–Q210 + discussion | THREAT_SURFACES.md |
| 70–90 | Optional: Control Attestation or MAESTRO overview | Level 5 dashboards |

---

## Splunk vs Jupyter — recommendation

### Stay Splunk-native (recommended)

| Reason | Detail |
|--------|--------|
| **Audience expectation** | Analysts and detection engineers live in Splunk Search and ES — not notebooks |
| **Already built in** | Threat Hunting, MLTK Anomaly Hunting, and playbook lookups ship hunt SPL in the app |
| **One less dependency** | No Python kernel, `splunk-sdk`, or notebook server to debug in class |
| **BOTS precedent** | [Splunk BOTS](https://github.com/splunk/botsv3) teaches via **questions + SPL in Splunk** — this curriculum follows that pattern (Q201–Q503 above) |

This guide **is** your notebook: ordered questions, collapsible SPL, Attack Panel buttons for reproducible data generation.

### When Jupyter might make sense (optional, not default)

Consider a **separate optional appendix** only if:

- Audience is **ML/data science** leaning and already lives in Jupyter
- You run a **multi-day** course with homework outside Splunk
- You want `splunk-sdk` programmatic exports for research (Dataset Export dashboard already covers HF export)

**Risk of Jupyter as primary UI:** splits attention, feels like “extra tooling,” and duplicates what Splunk Search already does. For Splunk/Cisco workshops, it often **pulls people away** from the SIEM they need to operate in production.

### If you add Jupyter later (lightweight pattern)

Do **not** replace Splunk. Use Jupyter as a **facilitator-only** or **homework** artifact:

```text
Cell 1: Markdown — Q204 question text (copy from this doc)
Cell 2: splunk-sdk query — same SPL as Search
Cell 3: Markdown — discussion / expected fields
```

Keep Attack Panel for attacks; keep Splunk as the student-facing hunt surface.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Zero events in Q201 | Complete Level 0; run First Win; check HEC token and index |
| Q210 empty | Run Standard Workshop (KC-C001) |
| Q401 all NOT_OBSERVED | Run Deep Workshop; widen time range to 24h |
| MAESTRO step cancelled | Install CSA MAESTRO on :9002 — [MAESTRO_WORKSHOP.md](MAESTRO_WORKSHOP.md) |
| Cisco preflight skipped | Start `docker-compose.cisco.yml` overlay |

---

## Document map

| Doc | Use when |
|-----|----------|
| **WORKSHOP.md** (this file) | Ordered curriculum + hunt questions |
| [USER_GUIDE.md](USER_GUIDE.md) | Splunk dashboard field-by-field reference |
| [THREAT_SURFACES.md](THREAT_SURFACES.md) | What each scenario teaches |
| [MAESTRO_WORKSHOP.md](MAESTRO_WORKSHOP.md) | CSA MAESTRO install + validate |
| [CISCO_INTEGRATION.md](CISCO_INTEGRATION.md) | Cisco overlay + MLTK |
