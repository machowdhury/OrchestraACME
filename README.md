# OrchestraACME

**A Docker-based agentic AI security range for red-teaming, runtime defense, and compliance monitoring.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](docker-compose.yml)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-GenAI-000000?logo=opentelemetry&logoColor=white)](apps/app_runtime.py)
[![Splunk](https://img.shields.io/badge/Splunk-Compliance_App-65A637?logo=splunk&logoColor=white)](splunk_app/App-Agentic-Compliance/)

> **Repository:** [github.com/machowdhury/OrchestraACME](https://github.com/machowdhury/OrchestraACME)  
> **Author:** Mahamudul Alam Chowdhury ([@machowdhury](https://github.com/machowdhury))

---

## What Is This?

**OrchestraACME** is an end-to-end **agentic AI security lab** that simulates a real multi-agent banking application, attacks it with adversarial prompts, defends it with runtime AI security controls, and streams everything into Splunk for detection engineering and compliance reporting.

Unlike static slide decks or mocked demos, this project runs **live LLM inference** (Ollama), **real HTTP attack traffic**, **actual policy enforcement**, and **production-grade telemetry pipelines** — all in a single `docker compose up`.

### Suggested GitHub Repository Description

```
End-to-end agentic AI security lab: multi-agent banking app, adversarial attack range, Cisco AI Defense runtime controls, OpenTelemetry GenAI telemetry, and Splunk compliance dashboard.
```

### Suggested GitHub Topics

```
agentic-ai, ai-security, llm-security, prompt-injection, opentelemetry, splunk, devsecops, red-team, compliance, cisco-ai-defense, ollama, genai, mitre-atlas, owasp-llm
```

---

## Why It Exists — The Agent Security Problem

Enterprises are deploying **multi-agent AI systems** that chain LLMs across intake, extraction, risk scoring, and compliance gates. These systems introduce attack surfaces that traditional AppSec tools were not built for:

| Gap | What Goes Wrong |
|-----|-----------------|
| **No runtime visibility** | Prompt injections and jailbreaks happen inside agent reasoning loops — invisible to WAFs and API gateways |
| **No policy enforcement at the model layer** | A compromised agent can escalate privileges, escape tool boundaries, or exfiltrate data across chain hops |
| **No compliance mapping** | Security teams cannot tie runtime AI events to OWASP LLM, MITRE ATLAS, or internal control frameworks |
| **No detection validation** | SIEM rules for AI threats are written blind — without a range to fire real attacks and confirm alerts fire |

**OrchestraACME closes this gap** by giving security engineers a repeatable lab to **build, break, detect, and report** on agentic AI risk.

---

## How It Helps — Security, Monitoring & Compliance

### 1. Agent Security (Offense + Defense)

| Capability | How OrchestraACME Delivers It |
|------------|-------------------------------|
| **Red-team testing** | 10-week adversarial lifecycle matrix fires real prompt injection, privilege escalation, tool escape, and kill-chain payloads |
| **Runtime defense** | Cisco AI Defense middleware inspects every prompt and model response; executes `POLICY_HARD_DENY` on threat match |
| **Multi-agent chain testing** | 4-agent loan pipeline (Intake → Extraction → Risk → Compliance) mirrors real enterprise agent orchestration |
| **Non-deterministic reasoning** | Live Ollama `llama3.2:1b` calls — attacks test actual model behavior, not canned responses |

### 2. Security Monitoring (Observability)

| Capability | How OrchestraACME Delivers It |
|------------|-------------------------------|
| **GenAI semantic conventions** | OpenTelemetry emits `gen_ai.system`, `gen_ai.request.model`, `gen_ai.prompt`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| **Distributed tracing** | Full agent chain traced end-to-end through OTel Collector |
| **Threat alerting** | Cisco AI Defense findings streamed as `cisco:aidefense:json` with `finding_type`, `cisco_threat_taxonomy`, and `policy_action` |
| **Token anomaly detection** | Splunk CTSM forecasting panel detects abnormal GenAI token consumption patterns |

### 3. Compliance (Framework Alignment)

| Capability | How OrchestraACME Delivers It |
|------------|-------------------------------|
| **10-phase compliance crosswalk** | CSV lookup maps agents to Cisco AI Defense objectives, OWASP LLM classifications, and MITRE ATLAS IDs |
| **Compliance dashboard** | Splunk Simple XML dashboard with denial gauges, threat pie charts, enrichment ledger, and forecast panels |
| **Audit trail** | Every blocked transaction logged with event ID, transaction ID, matched indicator, agent name, and severity |
| **Configuration variance detection** | Dashboard identifies events that fail crosswalk enrichment — surfacing governance gaps |

### 4. Who Should Use This

- **Detection engineers** — validate Splunk ES correlation searches against real `cisco:aidefense:json` telemetry
- **AI security architects** — prototype runtime guardrails before production agent deployment
- **Compliance officers** — demonstrate OWASP LLM / MITRE ATLAS control coverage with live evidence
- **Red teamers** — exercise agentic attack chains in an isolated, instrumented environment
- **DevSecOps engineers** — integrate OTel GenAI instrumentation patterns into CI/CD pipelines

---

## Quick Start

```bash
git clone https://github.com/machowdhury/OrchestraACME.git
cd OrchestraACME
docker compose up -d --build
```

| Dashboard | URL |
|-----------|-----|
| Banking App (defend) | http://localhost:5000 |
| Attack Panel (offense) | http://localhost:5001 |
| Splunk (monitor) | http://localhost:8000 (`admin` / `ACMEPassword2026!`) |

Use this lab to:

- Execute a **4-agent loan processing chain** with live LLM reasoning
- Launch **10 adversarial attack scenarios** mapped to a threat lifecycle matrix
- Enforce **Cisco AI Defense** policy controls (`POLICY_HARD_DENY`)
- Validate **Splunk ES detection rules** against `cisco:aidefense:json` telemetry

---

## Table of Contents

1. [Architecture](#architecture)
2. [Requirements](#requirements)
3. [Project Structure](#project-structure)
4. [Implementation Overview](#implementation-overview)
5. [Installation](#installation)
6. [Usage Guide](#usage-guide)
7. [Splunk App Deployment](#splunk-app-deployment)
8. [Configuration Reference](#configuration-reference)
9. [Verification &amp; Troubleshooting](#verification--troubleshooting)
10. [Security Notes](#security-notes)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Host Machine                                        │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────────────────┐  │
│  │ Attack Panel │───▶│ Banking App  │───▶│ Ollama (llama3.2:1b)        │  │
│  │  :5001       │    │  :5000       │    │  :11434 (internal)          │  │
│  └──────────────┘    └──────┬───────┘    └─────────────────────────────┘  │
│                             │                                               │
│                             │ OTLP (traces, metrics, logs)                  │
│                             ▼                                               │
│                    ┌─────────────────┐                                      │
│                    │ OTel Collector  │                                      │
│                    │ :4317 / :4318   │                                      │
│                    └────────┬────────┘                                      │
│                             │ HEC                                           │
│                             ▼                                               │
│                    ┌─────────────────┐     ┌──────────────────────────┐   │
│                    │ Splunk          │────▶│ App-Agentic-Compliance   │   │
│                    │ :8000 / :8088   │     │ (dashboard + lookups)    │   │
│                    └─────────────────┘     └──────────────────────────┘   │
│                                                                             │
│  Network: acme-sec-net (Docker bridge)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Banking App** (`app_runtime.py`) runs a 4-agent transaction chain. Each agent calls Ollama for real LLM inference.
2. **Cisco AI Defense middleware** scans every prompt and model response. On threat detection it executes `POLICY_HARD_DENY` and blocks the transaction.
3. **OpenTelemetry** exports GenAI metrics, traces, and Cisco alert logs to the OTel Collector on port `4318`.
4. **OTel Collector** forwards everything to Splunk HEC as `sourcetype=cisco:aidefense:json` in the `security` index.
5. **Attack Panel** (`exploit_ui.py`) fires real adversarial payloads at the banking app to test detection coverage.
6. **Splunk Compliance App** joins live telemetry against the framework crosswalk and visualizes denials, threats, and token anomalies.

---

## Requirements

### Hardware

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB (Splunk alone needs ~4 GB) |
| Disk | 20 GB free | 40 GB free |
| GPU | Optional | NVIDIA GPU for faster Ollama inference |

> **Note:** Ollama runs on CPU by default. Remove the NVIDIA `deploy` block in `docker-compose.yml` on CPU-only hosts.

### Software

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | v2.20+ | Stack orchestration |
| Git | Any recent | Clone the repository |
| Web browser | Modern | Access dashboards |
| Splunk (optional) | 9.2+ with MLTK | External Splunk instead of container |

### Network Ports

| Port | Service | Access |
|------|---------|--------|
| 5000 | Banking App | http://localhost:5000 |
| 5001 | Attack Panel | http://localhost:5001 |
| 8000 | Splunk Web UI | http://localhost:8000 |
| 8088 | Splunk HEC | Internal / localhost |

### Splunk App Prerequisites (for full dashboard)

- Splunk Enterprise 9.2+ (included in Docker stack, or external instance)
- **Machine Learning Toolkit (MLTK)** — required for Panel 4 (CTSM token anomaly forecasting)
- `security` index created (auto-created on first HEC ingest in most setups)

---

## Project Structure

```
AgenticProject/
├── docker-compose.yml              # Full container stack definition
├── config/
│   └── otel-collector-config.yaml  # OTLP pipelines → Splunk HEC exporter
├── apps/
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Shared image for both Flask apps
│   ├── app_runtime.py              # ACME Banking App (port 5000)
│   └── exploit_ui.py               # Attack Panel Console (port 5001)
└── splunk_app/
    └── App-Agentic-Compliance/
        ├── local/
        │   ├── inputs.conf         # HEC receiver → index=security
        │   └── props.conf          # JSON parsing + field extraction
        ├── lookups/
        │   └── framework_compliance_crosswalk.csv
        └── default/
            ├── app.conf
            ├── transforms.conf
            └── data/ui/views/
                └── compliance_matrix.xml
```

---

## Implementation Overview

### 1. Container Stack (`docker-compose.yml`)

Five services on the shared `acme-sec-net` bridge network:

| Service | Image / Build | Role |
|---------|---------------|------|
| `ollama` | `ollama/ollama:latest` | Local LLM; auto-pulls `llama3.2:1b` on first start |
| `banking_app` | `./apps` → `app_runtime.py` | 4-agent banking fabric on port 5000 |
| `attack_panel` | `./apps` → `exploit_ui.py` | 10-week attack console on port 5001 |
| `otel_collector` | `otel/opentelemetry-collector-contrib` | Aggregates OTLP → Splunk HEC |
| `splunk` | `splunk/splunk:9.2.1` | Local telemetry sink (toggleable) |

### 2. Banking App (`apps/app_runtime.py`)

**4-agent execution chain** (sequential, each calling Ollama):

1. **Customer Intake** — Profile and intent analysis
2. **Document Extraction** — Structured field extraction from documents
3. **Credit Risk** — Risk scoring and decision rationale
4. **Compliance Verification** — KYC/AML/BSA gate (APPROVED / DENIED)

**OpenTelemetry GenAI instrumentation** on every LLM call:

- `gen_ai.system="ollama"`
- `gen_ai.request.model="llama3.2:1b"`
- `gen_ai.prompt`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`
- `gen_ai.operation.name="chat"`

**Cisco AI Defense middleware** detects:

- Prompt injection
- Privilege escalation
- Tool boundary escapes

On match → `POLICY_HARD_DENY` → transaction blocked → JSON alert streamed to OTel Collector.

### 3. Attack Panel (`apps/exploit_ui.py`)

10 interactive buttons mapped to the **Agentic Threat Lifecycle Matrix**:

| Week | Phase | Expected Detection |
|------|-------|--------------------|
| 1 | Reconnaissance & Agent Discovery | May pass (informational) |
| 2 | Initial Access via Prompt Injection | `VALIDATION_FINDING` → DENY |
| 3 | Context Poisoning | Model-dependent |
| 4 | Instruction Hijacking | `VALIDATION_FINDING` → DENY |
| 5 | Sensitive Data Exfiltration | Model-dependent |
| 6 | Privilege Escalation | `RUNTIME_ANOMALY` → DENY |
| 7 | Tool Boundary Escape | `MODEL_VULNERABILITY` → DENY |
| 8 | Multi-Agent Chain Poisoning | `VALIDATION_FINDING` → DENY |
| 9 | Compliance Bypass | `RUNTIME_ANOMALY` → DENY |
| 10 | Full Kill Chain | Multiple findings → DENY |

Each button sends a **real HTTP POST** to `http://banking_app:5000/api/transaction` with raw adversarial text.

### 4. Splunk Compliance App

- **inputs.conf** — HEC token routes to `index=security`, `sourcetype=cisco:aidefense:json`
- **props.conf** — Strict JSON parsing, OTLP timestamp extraction, Cisco field aliases
- **framework_compliance_crosswalk.csv** — 10-phase mapping to OWASP LLM, MITRE ATLAS, Cisco taxonomy
- **compliance_matrix.xml** — Dark-theme dashboard with gauges, pie chart, ledger table, CTSM forecast

---

## Installation

### Step 1 — Clone and enter the project

```bash
cd /path/to/AgenticProject
```

### Step 2 — (Optional) Adjust for CPU-only hosts

If you do not have an NVIDIA GPU, remove or comment out the `deploy` block under the `ollama` service in `docker-compose.yml` (lines 84–91).

### Step 3 — Start the full stack

```bash
docker compose up -d --build
```

First startup takes **5–15 minutes** because:

- Ollama pulls the `llama3.2:1b` model (~1.3 GB)
- Splunk initializes and accepts the license

### Step 4 — Monitor startup progress

```bash
# Watch all service health
docker compose ps

# Follow Ollama model pull
docker compose logs -f ollama

# Follow Splunk initialization (wait for "Splunk is running")
docker compose logs -f splunk
```

### Step 5 — Confirm all services are healthy

```bash
docker compose ps
```

Expected state: all services `running` / `healthy`.

| Check | Command |
|-------|---------|
| Banking App | `curl -s http://localhost:5000/health` |
| Attack Panel | `curl -s http://localhost:5001/health` |
| Splunk Web | Open http://localhost:8000 |
| Ollama (internal) | `docker compose exec ollama ollama list` |

### Step 6 — Install the Splunk compliance app

```bash
# Copy app into the running Splunk container
docker cp splunk_app/App-Agentic-Compliance orchestra-acme-splunk:/opt/splunk/etc/apps/

# Set correct ownership and restart Splunk
docker compose exec splunk bash -c \
  "chown -R splunk:splunk /opt/splunk/etc/apps/App-Agentic-Compliance && /opt/splunk/bin/splunk restart"
```

Alternatively, for a standalone Splunk instance:

```bash
cp -r splunk_app/App-Agentic-Compliance $SPLUNK_HOME/etc/apps/
chown -R splunk:splunk $SPLUNK_HOME/etc/apps/App-Agentic-Compliance
$SPLUNK_HOME/bin/splunk restart
```

### Step 7 — Install MLTK (for token anomaly forecasting panel)

In Splunk Web → **Apps** → **Find More Apps** → search **Machine Learning Toolkit** → Install.

Or via CLI inside the Splunk container:

```bash
docker compose exec splunk /opt/splunk/bin/splunk install app Splunk_ML_Toolkit -update 1 -auth admin:ACMEPassword2026!
```

---

## Usage Guide

### A. Run a Legitimate Banking Transaction

1. Open the banking dashboard: **http://localhost:5000**
2. Fill in the loan application form (defaults are pre-populated).
3. Click **Execute 4-Agent Transaction Chain**.
4. Watch each agent light up as Ollama processes the request.
5. Review the final status: `APPROVED`, `DENIED`, or `BLOCKED`.

**API alternative:**

```bash
curl -s -X POST http://localhost:5000/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jane Doe",
    "loan_amount": 25000,
    "document_text": "Annual income: $72,000. Employer: ACME Corp.",
    "customer_notes": "Home improvement loan application."
  }' | python3 -m json.tool
```

### B. Launch Adversarial Attacks

1. Open the attack console: **http://localhost:5001**
2. Click any **Week 1–10** button in the sidebar.
3. Watch the terminal panel for:
   - HTTP status and transaction ID
   - `POLICY_HARD_DENY` events
   - Per-agent token usage and block status
4. Recommended test sequence for detection validation:

```text
Week 2  → Prompt Injection        (should BLOCK)
Week 6  → Privilege Escalation    (should BLOCK)
Week 7  → Tool Boundary Escape    (should BLOCK)
Week 10 → Full Kill Chain         (should BLOCK)
```

**API alternative — launch a single week:**

```bash
curl -s -X POST http://localhost:5001/api/launch/6 | python3 -m json.tool
```

**API alternative — run the full 10-week matrix:**

```bash
curl -s -X POST http://localhost:5001/api/launch-all | python3 -m json.tool
```

> Running the full matrix takes several minutes because each attack triggers 4 sequential Ollama inference calls.

### C. Verify Telemetry in Splunk

1. Log in to Splunk: **http://localhost:8000**
   - Username: `admin`
   - Password: `ACMEPassword2026!`
2. Run this search in **Search & Reporting**:

```spl
index=security sourcetype=cisco:aidefense:json
| table _time finding_type policy_action threat_category cisco_agent_name transaction_id
| sort - _time
```

3. Confirm `POLICY_HARD_DENY` events appear after running attack weeks 2, 6, 7, or 10.

**GenAI token metrics search:**

```spl
index=security sourcetype=cisco:aidefense:json
| stats sum(gen_ai_input_tokens) AS input_tokens sum(gen_ai_output_tokens) AS output_tokens by cisco_agent_name
```

### D. Use the Compliance Dashboard

1. In Splunk Web, navigate to: **Agentic Compliance → Agentic Compliance Matrix**
2. Review the four panels:

| Panel | What It Shows |
|-------|---------------|
| **POLICY_HARD_DENY Interventions** | Radial gauge — count of blocked transactions (24h) |
| **Configuration Variances** | Radial gauge — events not matching the compliance crosswalk |
| **Runtime Threats by Objective** | Pie chart — threat distribution by Cisco AI Defense objective |
| **Compliance Tracking Ledger** | Table — live events joined to OWASP / MITRE ATLAS / severity |
| **Token Anomaly Forecast** | CTSM line chart — predicted vs. actual GenAI token usage |

3. Click any table row to drill down into the full transaction event in Splunk.

### E. End-to-End Detection Validation Workflow

```text
1. docker compose up -d --build
2. Wait for all services healthy
3. Install Splunk app + MLTK
4. Open Attack Panel → fire Week 2, 6, 7, 10
5. Open Splunk → confirm cisco:aidefense:json events in index=security
6. Open Compliance Matrix dashboard → verify gauges increment
7. Review ledger table → confirm OWASP / ATLAS enrichment from crosswalk
8. Check CTSM panel → token anomaly lines after sustained attacks
```

---

## Splunk App Deployment

### HEC Token Alignment

These three values **must match** across the stack:

| Location | Token |
|----------|-------|
| `docker-compose.yml` → `SPLUNK_HEC_TOKEN` | `00000000-0000-4000-8000-ACMEHECLOCAL01` |
| `config/otel-collector-config.yaml` → `splunk_hec.token` | `00000000-0000-4000-8000-ACMEHECLOCAL01` |
| `splunk_app/.../local/inputs.conf` → `token` | `00000000-0000-4000-8000-ACMEHECLOCAL01` |

### Lookup Enrichment

The dashboard joins live events to `framework_compliance_crosswalk.csv` on:

- `cisco_aidefense_objective`
- `cisco_aidefense_technique`
- `cisco_aidefense_subtechnique`
- `cisco_agent_name`

This adds `owasp_classification`, `mitre_atlas_id`, and `severity` to each event.

---

## Configuration Reference

### Switch to External Splunk Cloud

**1. Comment out the `splunk` service** in `docker-compose.yml`.

**2. Remove the Splunk dependency** from `otel_collector`:

```yaml
# Comment out:
# depends_on:
#   splunk:
#     condition: service_healthy
```

**3. Switch OTel exporter to Option B** in `config/otel-collector-config.yaml`:

- Comment out the `splunk_hec` block (Option A)
- Uncomment `splunk_hec_external` and set your HEC URL and token
- Update pipeline `exporters` references to `[splunk_hec_external]`

**4. Update the Splunk app** `inputs.conf` token to match your cloud HEC token.

### Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `OLLAMA_BASE_URL` | banking_app, attack_panel | `http://ollama:11434` | Ollama API endpoint |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | banking_app | `http://otel_collector:4318` | OTel HTTP exporter |
| `OTEL_SERVICE_NAME` | banking_app | `orchestra-acme-banking-app` | Service name in telemetry |
| `BANKING_APP_URL` | attack_panel | `http://banking_app:5000` | Attack target URL |
| `SPLUNK_PASSWORD` | splunk | `ACMEPassword2026!` | Splunk admin password |

### Credentials (Lab Defaults)

| System | Username | Password |
|--------|----------|----------|
| Splunk Web | `admin` | `ACMEPassword2026!` |

> Change all default passwords before exposing this lab beyond localhost.

---

## Verification & Troubleshooting

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Banking app returns 502 / timeout | Ollama not ready | `docker compose logs ollama` — wait for model pull |
| No Splunk events | HEC token mismatch | Verify token alignment across 3 config files |
| `POLICY_HARD_DENY` never fires | Attack too mild | Use Week 6, 7, or 10 |
| Compliance dashboard empty | App not installed | Re-run Step 6 in Installation |
| CTSM panel shows error | MLTK not installed | Install Machine Learning Toolkit |
| Ollama GPU error | No NVIDIA driver | Remove `deploy` GPU block in compose |
| Splunk slow to start | Normal on first boot | Wait 3–5 min; check `docker compose logs splunk` |

### Useful Diagnostic Commands

```bash
# Service status
docker compose ps

# Banking app logs
docker compose logs -f banking_app

# OTel Collector logs
docker compose logs -f otel_collector

# Test Ollama directly
docker compose exec ollama ollama run llama3.2:1b "Hello"

# Test HEC ingest manually
curl -k https://localhost:8088/services/collector/event \
  -H "Authorization: Splunk 00000000-0000-4000-8000-ACMEHECLOCAL01" \
  -d '{"event": {"test": true, "sourcetype": "cisco:aidefense:json"}}'

# Restart a single service
docker compose restart banking_app

# Full teardown (preserves volumes)
docker compose down

# Full teardown including model data
docker compose down -v
```

### Health Check Endpoints

```bash
curl http://localhost:5000/health    # {"status": "healthy", ...}
curl http://localhost:5001/health    # {"status": "healthy", ...}
```

---

## Security Notes

This is a **deliberately vulnerable lab environment** designed for security research and detection engineering. Do not deploy to production or expose to untrusted networks.

- Default passwords and HEC tokens are for local lab use only
- The attack panel contains real adversarial payloads
- Splunk is configured with `--accept-license` for rapid lab setup
- All services communicate on an isolated Docker bridge (`acme-sec-net`)
- Only ports 5000, 5001, 8000, and 8088 are published to the host

**Recommended lab practices:**

- Run only on localhost or an isolated VLAN
- Rotate `SPLUNK_PASSWORD` and HEC tokens if sharing the environment
- Do not commit real cloud credentials to `otel-collector-config.yaml`
- Tear down with `docker compose down -v` when finished

---

## Quick Reference Card

```bash
# Start everything
docker compose up -d --build

# Open dashboards
open http://localhost:5000    # Banking App
open http://localhost:5001    # Attack Panel
open http://localhost:8000    # Splunk (admin / ACMEPassword2026!)

# Stop everything
docker compose down
```

| URL | Purpose |
|-----|---------|
| http://localhost:5000 | ACME Banking Multi-Agent Fabric |
| http://localhost:5001 | ACME Agentic Threat Range Console |
| http://localhost:8000 | Splunk Web + Compliance Dashboard |

---

## License & Attribution

OrchestraACME Lab — Principal DevSecOps Systems Engineering range for agentic AI security validation. Built for Cisco AI Defense telemetry integration, OpenTelemetry GenAI semantic conventions, and Splunk Enterprise Security detection rule development.
