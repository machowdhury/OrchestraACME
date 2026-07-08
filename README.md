# OrchestraACME
End-to-end agentic AI security lab: multi-agent banking app, adversarial attack range, Cisco AI Defense runtime controls, OpenTelemetry GenAI telemetry, and Splunk compliance dashboard.

What It Does (for your GitHub profile / README)
OrchestraACME is a Docker-based security lab that lets you build, attack, defend, and monitor multi-agent AI systems in one stack:

Layer	What It Does
Build
4-agent banking pipeline with live Ollama LLM reasoning
Attack
10-week adversarial lifecycle console (prompt injection → kill chain)
Defend
Cisco AI Defense middleware with POLICY_HARD_DENY runtime blocking
Monitor
OpenTelemetry GenAI metrics, traces, and threat alerts
Comply
Splunk app with OWASP LLM / MITRE ATLAS crosswalk and compliance dashboard
How It Helps Agent Security, Monitoring & Compliance
Agent Security
Tests real multi-agent chains (not mocks)
Fires real adversarial payloads at live endpoints
Enforces runtime policy at the model layer (prompt + response inspection)
Covers prompt injection, privilege escalation, tool boundary escapes, and chain poisoning
Security Monitoring
Emits OpenTelemetry GenAI semantic conventions (gen_ai.system, gen_ai.prompt, token usage)
Streams Cisco AI Defense findings as cisco:aidefense:json
Provides distributed tracing across the full agent chain
Forecasts token usage anomalies via Splunk CTSM
Compliance
Maps runtime events to OWASP LLM, MITRE ATLAS, and Cisco AI Defense taxonomy
10-phase compliance crosswalk from compile-time BOM audits to runtime containment
Audit ledger with event ID, transaction ID, severity, and matched indicators
Configuration variance detection for governance gaps
