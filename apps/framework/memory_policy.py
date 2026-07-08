"""
Agent memory policy — blocks persistence / poisoned memory writes (Emerging Class #6).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MEMORY_WRITE_PATTERNS = [
    re.compile(r"persistent\s+memory", re.I),
    re.compile(r"store\s+these\s+instructions", re.I),
    re.compile(r"remember\s+(?:this|these)\s+(?:for\s+)?(?:all\s+)?future\s+sessions", re.I),
    re.compile(r"do\s+not\s+(?:forget|clear)\s+this", re.I),
    re.compile(r"memory\.write\s*\(", re.I),
    re.compile(r"vector_store\.upsert", re.I),
]


@dataclass
class MemoryPolicyResult:
    blocked: bool
    rule_id: str
    matched_pattern: str = ""


def inspect_memory_policy(user_input: str) -> MemoryPolicyResult:
    for i, pattern in enumerate(MEMORY_WRITE_PATTERNS):
        match = pattern.search(user_input)
        if match:
            return MemoryPolicyResult(
                blocked=True,
                rule_id=f"MEM-POL-{100 + i:03d}",
                matched_pattern=pattern.pattern,
            )
    return MemoryPolicyResult(blocked=False, rule_id="MEM-POL-PASS")
