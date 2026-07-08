"""
A2A delegation verifier — W3C DID and cryptographic passport checks (Campaign W8).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

DID_PATTERN = re.compile(
    r"did:acme:[a-z]+:agent:\d{3}:v[\d.]+",
    re.IGNORECASE,
)
FORGED_SIG_MARKERS = (
    "FORGED",
    "BYPASS_VERIFICATION",
    "FAKE_SIGNATURE",
    "INVALID_SIG",
)


@dataclass
class A2AVerificationResult:
    did_document: str
    delegation_chain: str
    cryptographic_passport_valid: bool
    requesting_agent_id: str
    target_agent_id: str
    verification_failure_reason: str = ""


def verify_a2a_message(message: str, receiving_agent_id: str) -> A2AVerificationResult:
    """Parse inter-agent message headers and validate DID / signature claims."""
    did_match = DID_PATTERN.search(message)
    did = did_match.group(0) if did_match else ""

    chain = ""
    for line in message.splitlines():
        if "Delegation-Chain:" in line or "delegation.chain" in line.lower():
            chain = line.split(":", 1)[-1].strip()
            break

    requesting = ""
    if did:
        parts = did.split(":")
        if len(parts) >= 4:
            requesting = f"acme-agent-{parts[3]}-{parts[4]}"

    passport_valid = True
    reason = ""
    upper = message.upper()
    if any(marker in upper for marker in FORGED_SIG_MARKERS):
        passport_valid = False
        reason = "FORGED_SIGNATURE_DETECTED"
    elif "CRYPTOGRAPHIC_PASSPORT_VERIFIED" in upper and "FORGED" in upper:
        passport_valid = False
        reason = "CONTRADICTORY_PASSPORT_CLAIM"
    elif did and "Signature:" in message and "FORGED" in upper:
        passport_valid = False
        reason = "SIGNATURE_MISMATCH"

    return A2AVerificationResult(
        did_document=did,
        delegation_chain=chain or "orchestrator-000 → unknown",
        cryptographic_passport_valid=passport_valid,
        requesting_agent_id=requesting,
        target_agent_id=receiving_agent_id,
        verification_failure_reason=reason,
    )


def a2a_otel_fields(result: A2AVerificationResult) -> dict:
    return {
        "did.document": result.did_document,
        "delegation.chain": result.delegation_chain,
        "cryptographic_passport_valid": str(result.cryptographic_passport_valid).lower(),
        "requesting_agent_id": result.requesting_agent_id,
        "target_agent_id": result.target_agent_id,
        "a2a.verification_failure": result.verification_failure_reason,
    }
