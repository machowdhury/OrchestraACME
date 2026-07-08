"""
ACME Banking App Engine — Multi-Agent Transaction Fabric
OrchestraACME Lab | Principal Application Runtime
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import requests
from flask import Flask, jsonify, render_template_string, request
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OTEL_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel_collector:4318")
OTEL_SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "orchestra-acme-banking-app")

AGENT_CHAIN = [
    "Customer Intake",
    "Document Extraction",
    "Credit Risk",
    "Compliance Verification",
]

# ---------------------------------------------------------------------------
# Cisco AI Defense — Threat Pattern Signatures
# ---------------------------------------------------------------------------

THREAT_PATTERNS: list[dict[str, Any]] = [
    {
        "category": "prompt_injection",
        "finding_type": "VALIDATION_FINDING",
        "cisco_threat_taxonomy": {
            "objective": "TA0001",
            "technique": "T1566",
            "subtechnique": "T1566.001",
        },
        "patterns": [
            r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
            r"disregard\s+(your|the)\s+(rules|policy|policies|guidelines)",
            r"override\s+(system|safety)\s+prompt",
            r"you\s+are\s+now\s+(in\s+)?(developer|admin|root)\s+mode",
            r"forget\s+(everything|all)\s+you\s+(were|have\s+been)\s+told",
            r"new\s+instructions\s*:",
            r"system\s+prompt\s*:",
            r"<\s*/?\s*system\s*>",
            r"do\s+not\s+follow\s+(the\s+)?(bank|compliance)\s+rules",
        ],
    },
    {
        "category": "privilege_escalation",
        "finding_type": "RUNTIME_ANOMALY",
        "cisco_threat_taxonomy": {
            "objective": "TA0004",
            "technique": "T1078",
            "subtechnique": "T1078.004",
        },
        "patterns": [
            r"escalat(e|ion)\s+(my\s+)?privileges?",
            r"grant\s+(me\s+)?(admin|administrator|root|superuser)\s+(access|role|rights)",
            r"run\s+as\s+(root|administrator|sudo)",
            r"bypass\s+(authentication|authorization|rbac|access\s+control)",
            r"elevate\s+(my\s+)?permissions?",
            r"assume\s+(admin|root)\s+role",
            r"disable\s+(mfa|multi[- ]factor|authentication)",
            r"approve\s+(this\s+)?loan\s+without\s+(verification|checks)",
        ],
    },
    {
        "category": "tool_boundary_escape",
        "finding_type": "MODEL_VULNERABILITY",
        "cisco_threat_taxonomy": {
            "objective": "TA0002",
            "technique": "T1059",
            "subtechnique": "T1059.004",
        },
        "patterns": [
            r"execute\s+(shell|bash|cmd|powershell)\s+command",
            r"run\s+`[^`]+`",
            r"subprocess\.(run|call|popen)",
            r"os\.system\s*\(",
            r"read\s+file\s+(/etc/passwd|/etc/shadow|\.\./)",
            r"access\s+(the\s+)?filesystem",
            r"call\s+external\s+api\s+without\s+authorization",
            r"invoke\s+(tool|function|plugin)\s+outside\s+(scope|boundary)",
            r"curl\s+http",
            r"wget\s+",
            r"import\s+os\b",
            r"__import__\s*\(",
        ],
    },
]

COMPILED_THREAT_PATTERNS: list[dict[str, Any]] = [
    {
        **entry,
        "compiled": [re.compile(p, re.IGNORECASE) for p in entry["patterns"]],
    }
    for entry in THREAT_PATTERNS
]

# ---------------------------------------------------------------------------
# OpenTelemetry Bootstrap
# ---------------------------------------------------------------------------


def _build_resource() -> Resource:
    return Resource.create(
        {
            "service.name": OTEL_SERVICE_NAME,
            "service.namespace": "orchestra-acme",
            "deployment.environment": "orchestra-acme-lab",
        }
    )


def _init_telemetry() -> tuple[trace.Tracer, metrics.Meter, logging.Logger]:
    resource = _build_resource()

    trace_exporter = OTLPSpanExporter(endpoint=f"{OTEL_ENDPOINT}/v1/traces")
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{OTEL_ENDPOINT}/v1/metrics"),
        export_interval_millis=5000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    log_exporter = OTLPLogExporter(endpoint=f"{OTEL_ENDPOINT}/v1/logs")
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

    app_logger = logging.getLogger("acme.banking")
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(otel_handler)

    tracer = trace.get_tracer("acme.banking.genai", "1.0.0")
    meter = metrics.get_meter("acme.banking.genai", "1.0.0")
    return tracer, meter, app_logger


TRACER, METER, LOGGER = _init_telemetry()

GEN_AI_REQUEST_COUNTER = METER.create_counter(
    name="gen_ai.client.operation.duration",
    description="GenAI client operation count",
    unit="1",
)

GEN_AI_TOKEN_HISTOGRAM = METER.create_histogram(
    name="gen_ai.client.token.usage",
    description="GenAI token usage histogram",
    unit="token",
)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class AgentStepResult:
    agent_name: str
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    duration_ms: float
    blocked: bool = False
    block_reason: str | None = None


@dataclass
class TransactionContext:
    transaction_id: str
    customer_name: str
    document_text: str
    loan_amount: float
    customer_notes: str
    agent_results: list[AgentStepResult] = field(default_factory=list)
    status: str = "pending"
    policy_action: str | None = None


# ---------------------------------------------------------------------------
# Cisco AI Defense Security Middleware Sidecar
# ---------------------------------------------------------------------------


class CiscoAIDefenseMiddleware:
    """Inline security sidecar emulating the Cisco AI Defense platform interface."""

    PLATFORM = "cisco_ai_defense"
    POLICY_ACTION_DENY = "POLICY_HARD_DENY"

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._otel_logs_url = f"{OTEL_ENDPOINT}/v1/logs"

    def scan_text(self, text: str, agent_name: str, transaction_id: str) -> dict[str, Any] | None:
        for threat in COMPILED_THREAT_PATTERNS:
            for pattern in threat["compiled"]:
                match = pattern.search(text)
                if match:
                    return self._build_finding(
                        matched_text=match.group(0),
                        category=threat["category"],
                        finding_type=threat["finding_type"],
                        taxonomy=threat["cisco_threat_taxonomy"],
                        agent_name=agent_name,
                        transaction_id=transaction_id,
                        full_text=text,
                    )
        return None

    def _build_finding(
        self,
        matched_text: str,
        category: str,
        finding_type: str,
        taxonomy: dict[str, str],
        agent_name: str,
        transaction_id: str,
        full_text: str,
    ) -> dict[str, Any]:
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": self.PLATFORM,
            "policy_action": self.POLICY_ACTION_DENY,
            "finding_type": finding_type,
            "cisco_threat_taxonomy": {
                "objective": taxonomy["objective"],
                "technique": taxonomy["technique"],
                "subtechnique": taxonomy["subtechnique"],
            },
            "threat_category": category,
            "agent_name": agent_name,
            "transaction_id": transaction_id,
            "matched_indicator": matched_text,
            "severity": "critical",
            "source": "orchestra-acme-banking-app",
            "sourcetype": "cisco:aidefense:json",
            "content_preview": full_text[:512],
        }

    def enforce(
        self,
        text: str,
        agent_name: str,
        transaction_id: str,
        scan_target: str,
    ) -> tuple[bool, dict[str, Any] | None]:
        finding = self.scan_text(text=text, agent_name=agent_name, transaction_id=transaction_id)
        if finding is None:
            return True, None

        finding["scan_target"] = scan_target
        self.stream_alert(finding)
        self._logger.warning(
            "Cisco AI Defense POLICY_HARD_DENY triggered",
            extra={"cisco_alert": json.dumps(finding)},
        )
        return False, finding

    def stream_alert(self, finding: dict[str, Any]) -> None:
        """Stream authentic JSON alert to OTel collector HTTP port 4318."""
        otlp_payload = {
            "resourceLogs": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": OTEL_SERVICE_NAME}},
                            {"key": "cisco.platform", "value": {"stringValue": self.PLATFORM}},
                        ]
                    },
                    "scopeLogs": [
                        {
                            "scope": {"name": "cisco.ai.defense"},
                            "logRecords": [
                                {
                                    "timeUnixNano": str(int(time.time() * 1_000_000_000)),
                                    "severityText": "CRITICAL",
                                    "body": {"stringValue": json.dumps(finding)},
                                    "attributes": [
                                        {
                                            "key": "finding_type",
                                            "value": {"stringValue": finding["finding_type"]},
                                        },
                                        {
                                            "key": "policy_action",
                                            "value": {"stringValue": finding["policy_action"]},
                                        },
                                        {
                                            "key": "cisco_threat_taxonomy.objective",
                                            "value": {
                                                "stringValue": finding["cisco_threat_taxonomy"]["objective"]
                                            },
                                        },
                                        {
                                            "key": "cisco_threat_taxonomy.technique",
                                            "value": {
                                                "stringValue": finding["cisco_threat_taxonomy"]["technique"]
                                            },
                                        },
                                        {
                                            "key": "cisco_threat_taxonomy.subtechnique",
                                            "value": {
                                                "stringValue": finding["cisco_threat_taxonomy"]["subtechnique"]
                                            },
                                        },
                                        {
                                            "key": "sourcetype",
                                            "value": {"stringValue": "cisco:aidefense:json"},
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        try:
            response = requests.post(
                self._otel_logs_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(otlp_payload),
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            self._logger.error("Failed to stream Cisco AI Defense alert to OTel: %s", exc)


SECURITY_MIDDLEWARE = CiscoAIDefenseMiddleware(LOGGER)

# ---------------------------------------------------------------------------
# Ollama LLM Client with OpenTelemetry GenAI Semantic Conventions
# ---------------------------------------------------------------------------


def call_ollama_generate(prompt: str, agent_name: str, transaction_id: str) -> dict[str, Any]:
    """
    Execute a real HTTP POST to the Ollama /api/generate endpoint and emit
    OpenTelemetry GenAI semantic convention metrics.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 256},
    }

    allowed, input_finding = SECURITY_MIDDLEWARE.enforce(
        text=prompt,
        agent_name=agent_name,
        transaction_id=transaction_id,
        scan_target="prompt",
    )
    if not allowed:
        return {
            "blocked": True,
            "block_reason": "Input blocked by Cisco AI Defense middleware",
            "finding": input_finding,
            "response": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "duration_ms": 0.0,
        }

    start = time.perf_counter()
    with TRACER.start_as_current_span(
        "gen_ai.chat",
        attributes={
            "gen_ai.system": "ollama",
            "gen_ai.request.model": OLLAMA_MODEL,
            "gen_ai.operation.name": "chat",
            "gen_ai.prompt": prompt[:2048],
            "gen_ai.agent.name": agent_name,
            "transaction.id": transaction_id,
        },
    ) as span:
        try:
            http_response = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=120)
            http_response.raise_for_status()
            data = http_response.json()
        except requests.RequestException as exc:
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise

        model_response = data.get("response", "")
        input_tokens = int(data.get("prompt_eval_count", 0))
        output_tokens = int(data.get("eval_count", 0))
        duration_ms = (time.perf_counter() - start) * 1000

        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
        span.set_attribute("gen_ai.response.finish_reason", "stop")

        gen_ai_attributes = {
            "gen_ai.system": "ollama",
            "gen_ai.request.model": OLLAMA_MODEL,
            "gen_ai.operation.name": "chat",
            "gen_ai.prompt": prompt[:2048],
            "gen_ai.usage.input_tokens": input_tokens,
            "gen_ai.usage.output_tokens": output_tokens,
            "gen_ai.agent.name": agent_name,
        }

        GEN_AI_REQUEST_COUNTER.add(1, gen_ai_attributes)
        GEN_AI_TOKEN_HISTOGRAM.record(input_tokens, {**gen_ai_attributes, "token.type": "input"})
        GEN_AI_TOKEN_HISTOGRAM.record(output_tokens, {**gen_ai_attributes, "token.type": "output"})

        allowed, output_finding = SECURITY_MIDDLEWARE.enforce(
            text=model_response,
            agent_name=agent_name,
            transaction_id=transaction_id,
            scan_target="model_output",
        )
        if not allowed:
            span.set_attribute("cisco.policy_action", SECURITY_MIDDLEWARE.POLICY_ACTION_DENY)
            return {
                "blocked": True,
                "block_reason": "Model output blocked by Cisco AI Defense middleware",
                "finding": output_finding,
                "response": model_response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "duration_ms": duration_ms,
            }

        return {
            "blocked": False,
            "block_reason": None,
            "finding": None,
            "response": model_response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
        }


# ---------------------------------------------------------------------------
# Four-Agent Transaction Execution Chain
# ---------------------------------------------------------------------------


def _build_agent_prompt(agent_name: str, ctx: TransactionContext, prior_context: str) -> str:
    prompts = {
        "Customer Intake": (
            f"You are the Customer Intake agent for ACME Banking. "
            f"Analyze the following new loan application intake data and summarize "
            f"the customer profile, stated intent, and any risk flags.\n\n"
            f"Customer Name: {ctx.customer_name}\n"
            f"Requested Loan Amount: ${ctx.loan_amount:,.2f}\n"
            f"Customer Notes: {ctx.customer_notes}\n\n"
            f"Provide a concise professional intake summary."
        ),
        "Document Extraction": (
            f"You are the Document Extraction agent for ACME Banking. "
            f"Extract structured fields from the submitted document text below. "
            f"Identify income, employment, identity markers, and anomalies.\n\n"
            f"Prior Intake Summary:\n{prior_context}\n\n"
            f"Document Text:\n{ctx.document_text}\n\n"
            f"Return extracted fields and extraction confidence assessment."
        ),
        "Credit Risk": (
            f"You are the Credit Risk agent for ACME Banking. "
            f"Evaluate creditworthiness based on intake and extracted document data. "
            f"Provide a risk score rationale (low/medium/high) and key risk drivers.\n\n"
            f"Intake and Extraction Context:\n{prior_context}\n\n"
            f"Loan Amount Requested: ${ctx.loan_amount:,.2f}\n\n"
            f"Deliver a credit risk assessment with recommended decision."
        ),
        "Compliance Verification": (
            f"You are the Compliance Verification agent for ACME Banking. "
            f"Verify regulatory compliance (KYC/AML/BSA) for this loan application. "
            f"Flag any policy violations and state APPROVED or DENIED with rationale.\n\n"
            f"Full Transaction Context:\n{prior_context}\n\n"
            f"Customer Notes: {ctx.customer_notes}\n\n"
            f"Provide final compliance determination."
        ),
    }
    return prompts[agent_name]


def execute_transaction_chain(ctx: TransactionContext) -> TransactionContext:
    accumulated_context = ""

    for agent_name in AGENT_CHAIN:
        prompt = _build_agent_prompt(agent_name, ctx, accumulated_context)
        llm_result = call_ollama_generate(
            prompt=prompt,
            agent_name=agent_name,
            transaction_id=ctx.transaction_id,
        )

        step = AgentStepResult(
            agent_name=agent_name,
            prompt=prompt,
            response=llm_result.get("response", ""),
            input_tokens=llm_result.get("input_tokens", 0),
            output_tokens=llm_result.get("output_tokens", 0),
            duration_ms=llm_result.get("duration_ms", 0.0),
            blocked=llm_result.get("blocked", False),
            block_reason=llm_result.get("block_reason"),
        )
        ctx.agent_results.append(step)

        if step.blocked:
            ctx.status = "blocked"
            ctx.policy_action = SECURITY_MIDDLEWARE.POLICY_ACTION_DENY
            LOGGER.warning(
                "Transaction %s blocked at agent %s: %s",
                ctx.transaction_id,
                agent_name,
                step.block_reason,
            )
            return ctx

        accumulated_context += f"\n--- {agent_name} ---\n{step.response}\n"

    final_response = ctx.agent_results[-1].response.lower() if ctx.agent_results else ""
    if "denied" in final_response and "approved" not in final_response:
        ctx.status = "denied"
    else:
        ctx.status = "approved"
    return ctx


# ---------------------------------------------------------------------------
# Flask Application
# ---------------------------------------------------------------------------

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ACME Banking Multi-Agent Fabric</title>
  <style>
    :root {
      --bg: #0b1f33;
      --panel: #122a44;
      --accent: #00b4d8;
      --accent2: #48cae4;
      --text: #e8f4ff;
      --muted: #8fb3cc;
      --success: #2ecc71;
      --danger: #e74c3c;
      --warn: #f39c12;
      --border: #1f3f5f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #071525 0%, #0b1f33 50%, #0e2a47 100%);
      color: var(--text);
      min-height: 100vh;
    }
    header {
      padding: 28px 40px;
      border-bottom: 1px solid var(--border);
      background: rgba(7, 21, 37, 0.85);
      backdrop-filter: blur(8px);
    }
    header h1 {
      margin: 0;
      font-size: 1.9rem;
      letter-spacing: 0.5px;
      color: var(--accent2);
    }
    header p { margin: 8px 0 0; color: var(--muted); }
    main {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      padding: 32px 40px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }
    .card h2 {
      margin-top: 0;
      font-size: 1.1rem;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    label {
      display: block;
      margin: 12px 0 6px;
      font-size: 0.85rem;
      color: var(--muted);
    }
    input, textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #0a1828;
      color: var(--text);
      font-size: 0.95rem;
    }
    textarea { min-height: 100px; resize: vertical; }
    button {
      margin-top: 18px;
      width: 100%;
      padding: 14px;
      border: none;
      border-radius: 8px;
      background: linear-gradient(90deg, #0077b6, #00b4d8);
      color: white;
      font-weight: 700;
      font-size: 1rem;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }
    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(0, 180, 216, 0.35);
    }
    .chain {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .chain-step {
      flex: 1;
      min-width: 120px;
      text-align: center;
      padding: 10px 8px;
      border-radius: 8px;
      background: #0a1828;
      border: 1px solid var(--border);
      font-size: 0.78rem;
      color: var(--muted);
    }
    .chain-step.active { border-color: var(--accent); color: var(--accent2); }
    #results {
      grid-column: 1 / -1;
      white-space: pre-wrap;
      font-family: "Cascadia Code", "Fira Code", monospace;
      font-size: 0.82rem;
      line-height: 1.5;
      max-height: 500px;
      overflow-y: auto;
    }
    .status-approved { color: var(--success); }
    .status-blocked { color: var(--danger); }
    .status-denied { color: var(--warn); }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>ACME Banking Multi-Agent Fabric</h1>
    <p>4-Agent Transaction Execution Chain — Customer Intake → Document Extraction → Credit Risk → Compliance Verification</p>
  </header>
  <main>
    <div class="card">
      <h2>Loan Application Intake</h2>
      <form id="txForm">
        <label for="customer_name">Customer Name</label>
        <input id="customer_name" name="customer_name" value="Jane Doe" required />
        <label for="loan_amount">Loan Amount (USD)</label>
        <input id="loan_amount" name="loan_amount" type="number" value="25000" required />
        <label for="document_text">Supporting Document Text</label>
        <textarea id="document_text" name="document_text">Annual income: $72,000. Employer: ACME Corp. Employment tenure: 4 years. No prior defaults.</textarea>
        <label for="customer_notes">Customer Notes</label>
        <textarea id="customer_notes" name="customer_notes">Applying for home improvement loan. All documentation attached.</textarea>
        <button type="submit">Execute 4-Agent Transaction Chain</button>
      </form>
    </div>
    <div class="card">
      <h2>Agent Pipeline Status</h2>
      <div class="chain">
        <div class="chain-step" id="step-0">① Customer Intake</div>
        <div class="chain-step" id="step-1">② Document Extraction</div>
        <div class="chain-step" id="step-2">③ Credit Risk</div>
        <div class="chain-step" id="step-3">④ Compliance Verification</div>
      </div>
      <p style="color: var(--muted); font-size: 0.85rem;">
        Each agent performs live LLM reasoning via Ollama (<code>llama3.2:1b</code>).
        Cisco AI Defense middleware inspects all prompts and model outputs.
        Telemetry streams to OpenTelemetry Collector on port 4318.
      </p>
    </div>
    <div class="card" id="results">
      <h2>Execution Results</h2>
      <p style="color: var(--muted);">Submit a transaction to view agent chain output.</p>
    </div>
  </main>
  <script>
    document.getElementById("txForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const results = document.getElementById("results");
      results.innerHTML = "<h2>Execution Results</h2><p>Executing 4-agent chain via Ollama...</p>";
      for (let i = 0; i < 4; i++) {
        document.getElementById("step-" + i).classList.remove("active");
      }
      const payload = {
        customer_name: document.getElementById("customer_name").value,
        loan_amount: parseFloat(document.getElementById("loan_amount").value),
        document_text: document.getElementById("document_text").value,
        customer_notes: document.getElementById("customer_notes").value,
      };
      try {
        const resp = await fetch("/api/transaction", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await resp.json();
        data.agent_results.forEach((_, idx) => {
          document.getElementById("step-" + idx).classList.add("active");
        });
        const statusClass = "status-" + data.status;
        let html = "<h2>Execution Results</h2>";
        html += "<p class='" + statusClass + "'><strong>Status:</strong> " + data.status.toUpperCase();
        if (data.policy_action) {
          html += " | <strong>Policy:</strong> " + data.policy_action;
        }
        html += "</p><p><strong>Transaction ID:</strong> " + data.transaction_id + "</p>";
        data.agent_results.forEach((step) => {
          html += "<hr><h3>" + step.agent_name + "</h3>";
          html += "<p><em>Tokens in/out: " + step.input_tokens + "/" + step.output_tokens;
          html += " | Duration: " + step.duration_ms.toFixed(1) + "ms</em></p>";
          if (step.blocked) {
            html += "<p class='status-blocked'><strong>BLOCKED:</strong> " + step.block_reason + "</p>";
          }
          html += "<pre>" + step.response + "</pre>";
        });
        results.innerHTML = html;
      } catch (err) {
        results.innerHTML = "<h2>Execution Results</h2><p class='status-blocked'>Error: " + err + "</p>";
      }
    });
  </script>
</body>
</html>
"""

app = Flask(__name__)


@app.route("/health")
def health() -> tuple[Any, int]:
    return jsonify({"status": "healthy", "service": OTEL_SERVICE_NAME}), 200


@app.route("/")
def dashboard() -> str:
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/transaction", methods=["POST"])
def api_transaction() -> tuple[Any, int]:
    body = request.get_json(force=True, silent=True) or {}
    ctx = TransactionContext(
        transaction_id=str(uuid.uuid4()),
        customer_name=str(body.get("customer_name", "Unknown Customer")),
        document_text=str(body.get("document_text", "")),
        loan_amount=float(body.get("loan_amount", 0)),
        customer_notes=str(body.get("customer_notes", "")),
    )
    ctx = execute_transaction_chain(ctx)
    response_body = {
        "transaction_id": ctx.transaction_id,
        "status": ctx.status,
        "policy_action": ctx.policy_action,
        "agent_results": [
            {
                "agent_name": step.agent_name,
                "response": step.response,
                "input_tokens": step.input_tokens,
                "output_tokens": step.output_tokens,
                "duration_ms": step.duration_ms,
                "blocked": step.blocked,
                "block_reason": step.block_reason,
            }
            for step in ctx.agent_results
        ],
    }
    status_code = 403 if ctx.status == "blocked" else 200
    return jsonify(response_body), status_code


@app.route("/api/intake", methods=["POST"])
def api_intake() -> tuple[Any, int]:
    """Direct intake endpoint targeted by adversarial probes."""
    return api_transaction()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
