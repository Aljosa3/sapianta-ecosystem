"""Deterministic forbidden capability detection."""

from __future__ import annotations

import json
from typing import Any


FORBIDDEN_PATTERNS = {
    "automatic_approval": ("automatic approval", "auto approval", "auto-approval"),
    "automatic_rejection": ("automatic rejection", "auto rejection", "auto-rejection"),
    "codex_invocation": ("codex invocation", "invoke codex", "trigger codex", "codex exec"),
    "transport_invocation": ("transport invocation", "trigger transport", "invoke transport"),
    "task_generation": ("task generation", "generate task", "create task", "enqueue task"),
    "recursive_execution": ("recursive execution", "recursive task", "recursive orchestration"),
    "self_approval": ("self approval", "self-approval"),
    "self_modifying_governance": ("self-modifying governance", "self modifying governance"),
    "policy_bypass": ("policy bypass", "bypass policy"),
    "protocol_enforcement_bypass": ("protocol enforcement bypass", "bypass protocol enforcement"),
    "auto_merge": ("auto-merge", "auto merge"),
    "auto_push": ("auto-push", "auto push"),
}

BOUNDARY_PATTERNS = (
    "runtime",
    "transport",
    "approval",
    "policy",
    "protocol",
    "reflection",
    "enforcement",
)
GOVERNANCE_PATTERNS = ("governance boundary", "authority semantics", "approval semantics")
SECURITY_PATTERNS = ("subprocess", "network", "secret", "external system", "credential")


def _semantic_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        strings: list[str] = []
        for key, item in value.items():
            if key == "lineage" or key.endswith("_id") or key == "input_type":
                continue
            strings.extend(_semantic_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_semantic_strings(item))
        return strings
    if isinstance(value, str):
        return [value]
    return []


def _text(value: Any) -> str:
    return json.dumps(_semantic_strings(value), sort_keys=True).lower()


def detect_forbidden_capabilities(value: dict[str, Any]) -> list[str]:
    blocked = []
    if value.get("allowed_to_execute_automatically") is True:
        blocked.append("automatic_execution")
    if value.get("execution_authority_granted") is True:
        blocked.append("execution_authority_granted")
    text = _text(value)
    for capability, patterns in FORBIDDEN_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            blocked.append(capability)
    return sorted(set(blocked))


def matched_boundary_rules(value: dict[str, Any]) -> list[str]:
    text = _text(value)
    matches = [f"boundary:{pattern}" for pattern in BOUNDARY_PATTERNS if pattern in text]
    matches.extend(f"governance:{pattern}" for pattern in GOVERNANCE_PATTERNS if pattern in text)
    matches.extend(f"security:{pattern}" for pattern in SECURITY_PATTERNS if pattern in text)
    return sorted(set(matches))
