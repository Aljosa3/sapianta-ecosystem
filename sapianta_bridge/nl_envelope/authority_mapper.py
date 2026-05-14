"""Deterministic authority mapping from semantic intent."""

from __future__ import annotations

from typing import Any


AUTHORITY_BY_INTENT = {
    "GOVERNANCE_INSPECTION": ("READ_ONLY", "NO_NETWORK", "NO_RUNTIME_EXECUTION", "NO_PRIVILEGE_ESCALATION"),
    "CREATIVE_GENERATION": ("CREATE_NEW_FILES", "NO_NETWORK", "NO_RUNTIME_EXECUTION", "NO_PRIVILEGE_ESCALATION"),
    "GOVERNED_REFINEMENT": ("PATCH_EXISTING_FILES", "NO_NETWORK", "NO_RUNTIME_EXECUTION", "NO_PRIVILEGE_ESCALATION"),
    "GOVERNED_EXECUTION_PROPOSAL": ("RUN_TESTS", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"),
}


def map_authority_scope(classification: dict[str, Any], admissibility: dict[str, Any]) -> dict[str, Any]:
    intent = classification.get("intent_type")
    if admissibility.get("admissibility") == "REJECTED" or intent not in AUTHORITY_BY_INTENT:
        return {
            "authority_scope": [],
            "authority_mapping_valid": False,
            "reason": "authority mapping blocked by inadmissible or unknown intent",
            "least_privilege_preserved": True,
            "execution_authority_granted": False,
        }
    return {
        "authority_scope": list(AUTHORITY_BY_INTENT[intent]),
        "authority_mapping_valid": True,
        "reason": "least-privilege authority scope mapped from deterministic intent",
        "least_privilege_preserved": True,
        "execution_authority_granted": False,
    }
