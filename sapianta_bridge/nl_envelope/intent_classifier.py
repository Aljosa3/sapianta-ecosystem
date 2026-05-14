"""Deterministic natural language intent classification."""

from __future__ import annotations

from typing import Any


INTENT_TYPES = (
    "GOVERNED_REFINEMENT",
    "CREATIVE_GENERATION",
    "GOVERNED_EXECUTION_PROPOSAL",
    "GOVERNANCE_INSPECTION",
    "UNKNOWN",
)

_RULES = {
    "GOVERNED_EXECUTION_PROPOSAL": (
        "execute",
        "run test",
        "run pytest",
        "apply patch",
        "transport",
        "execution envelope",
    ),
    "GOVERNANCE_INSPECTION": (
        "inspect",
        "audit",
        "review governance",
        "validate",
        "show evidence",
    ),
    "GOVERNED_REFINEMENT": (
        "refine",
        "improve",
        "fix",
        "stabilize",
        "update",
    ),
    "CREATIVE_GENERATION": (
        "generate",
        "create",
        "write",
        "draft",
        "design",
    ),
}

_FORBIDDEN_AUTHORITY_PHRASES = (
    "without approval",
    "bypass governance",
    "ignore validation",
    "unrestricted",
    "self authorize",
    "auto execute",
)


def classify_intent(request: dict[str, Any]) -> dict[str, Any]:
    text = str(request.get("raw_text", "")).lower()
    matched = [
        intent
        for intent, phrases in _RULES.items()
        if any(phrase in text for phrase in phrases)
    ]
    forbidden = [phrase for phrase in _FORBIDDEN_AUTHORITY_PHRASES if phrase in text]
    if forbidden or len(matched) != 1:
        intent_type = "UNKNOWN"
        unknown_detected = True
        requires_review = True
    else:
        intent_type = matched[0]
        unknown_detected = False
        requires_review = intent_type in {"GOVERNED_EXECUTION_PROPOSAL", "GOVERNED_REFINEMENT"}
    return {
        "semantic_request_id": request.get("semantic_request_id"),
        "intent_type": intent_type,
        "confidence": "DETERMINISTIC",
        "requires_review": requires_review,
        "unknown_detected": unknown_detected,
        "matched_intents": matched,
        "forbidden_authority_phrases": forbidden,
        "replay_safe": True,
    }
