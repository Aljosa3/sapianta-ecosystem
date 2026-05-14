"""Fail-closed admissibility evaluation for semantic ingress."""

from __future__ import annotations

from typing import Any


ADMISSIBILITY = ("ADMISSIBLE", "REVIEW_REQUIRED", "REJECTED")

_REJECT_PHRASES = (
    "bypass governance",
    "ignore validation",
    "unrestricted shell",
    "full filesystem",
    "auto execute",
    "without approval",
    "self modifying governance",
)


def evaluate_admissibility(request: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    text = str(request.get("raw_text", "")).lower()
    violations = [phrase for phrase in _REJECT_PHRASES if phrase in text]
    if classification.get("intent_type") == "UNKNOWN" or classification.get("unknown_detected") is True:
        status = "REJECTED"
        reason = "unknown or ambiguous intent fails closed"
    elif violations:
        status = "REJECTED"
        reason = "implicit or explicit authority escalation rejected"
    elif classification.get("requires_review") is True:
        status = "REVIEW_REQUIRED"
        reason = "governed intent requires downstream review"
    else:
        status = "ADMISSIBLE"
        reason = "intent is admissible as bounded proposal"
    return {
        "semantic_request_id": request.get("semantic_request_id"),
        "admissibility": status,
        "reason": reason,
        "violations": violations,
        "execution_authority_granted": False,
        "replay_safe": True,
    }
