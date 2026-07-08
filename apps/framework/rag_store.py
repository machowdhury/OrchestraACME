"""
In-memory RAG store with Galileo-style retrieval anomaly scoring (Campaign W9).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

CONFIDENTIAL_DOCS = [
    {"id": "doc-001", "title": "ACME Loan Policy v4.2", "classification": "INTERNAL"},
    {"id": "doc-002", "title": "Customer Application Template", "classification": "CONFIDENTIAL"},
    {"id": "doc-003", "title": "Risk Model Weights", "classification": "RESTRICTED"},
]

EXFIL_PROBE_PATTERNS = [
    re.compile(r"knowledge\s+base\s+index", re.I),
    re.compile(r"embedding\s+vectors?", re.I),
    re.compile(r"vector\s+store", re.I),
    re.compile(r"last\s+\d+\s+customer", re.I),
    re.compile(r"CONFIDENTIAL", re.I),
    re.compile(r"retrieve\s+and\s+display", re.I),
    re.compile(r"without\s+redaction", re.I),
]


@dataclass
class RagRetrievalResult:
    vector_retrieval_count: int
    galileo_anomaly_score: float
    galileo_observe_alert: bool
    retrieved_doc_ids: List[str]
    injection_vector: str = ""


def probe_rag_exfiltration(user_input: str) -> RagRetrievalResult:
    """Score retrieval probes — high scores indicate exfiltration-style RAG abuse."""
    probe_hits = sum(1 for p in EXFIL_PROBE_PATTERNS if p.search(user_input))
    retrieval_count = min(probe_hits * 3, 15)

    anomaly = min(0.15 + (probe_hits * 0.18), 0.99)
    alert = probe_hits >= 3 or anomaly >= 0.7

    doc_ids = [d["id"] for d in CONFIDENTIAL_DOCS[:probe_hits]] if probe_hits else []

    injection = "retrieved_content" if probe_hits >= 2 else ""

    return RagRetrievalResult(
        vector_retrieval_count=retrieval_count,
        galileo_anomaly_score=round(anomaly, 3),
        galileo_observe_alert=alert,
        retrieved_doc_ids=doc_ids,
        injection_vector=injection,
    )


def rag_otel_fields(result: RagRetrievalResult) -> dict:
    return {
        "vector_retrieval_count": str(result.vector_retrieval_count),
        "galileo_anomaly_score": str(result.galileo_anomaly_score),
        "galileo_observe_alert": str(result.galileo_observe_alert).lower(),
        "rag.retrieved_doc_ids": ",".join(result.retrieved_doc_ids),
        "injection_vector": result.injection_vector,
    }
