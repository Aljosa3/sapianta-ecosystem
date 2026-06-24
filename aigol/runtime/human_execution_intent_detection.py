"""Deterministic human execution-intent detection helpers."""

from __future__ import annotations

import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError


GENERIC_GOVERNED_DOMAIN_CREATION = "GENERIC_GOVERNED_DOMAIN_CREATION"
GENERIC_GOVERNED_ARTIFACT_CREATION = "GENERIC_GOVERNED_ARTIFACT_CREATION"
GENERIC_GOVERNED_EXECUTION_REQUEST = "GENERIC_GOVERNED_EXECUTION_REQUEST"
NO_EXECUTION_INTENT = "NO_EXECUTION_INTENT"

_CREATION_TERMS = ("create", "new", "add", "build", "make", "define", "draft", "prepare", "write", "generate")
_NAMING_MARKERS = ("called", "named")
_EXECUTION_TERMS = ("execute", "run", "trigger", "start", "invoke", "apply")
_GOVERNANCE_ARTIFACT_TERMS = ("governed", "governance", "certification")
_ARTIFACT_KIND_TERMS = ("artifact", "doc", "document", "markdown", "specification")


def detect_human_execution_intent(human_prompt: str) -> dict[str, Any]:
    """Detect generic governed execution intent without granting execution authority."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    matched_terms: list[str] = []

    if _is_generic_governed_domain_creation(normalized):
        matched_terms = _matched_terms(normalized, (*_CREATION_TERMS, "governed", "domain", *_NAMING_MARKERS))
        return {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_DOMAIN_CREATION,
            "confidence": "HIGH",
            "target_kind": "DOMAIN",
            "target_name": _extract_named_target(prompt),
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "GOVERNED_UNKNOWN_DOMAIN_CLARIFICATION",
        }

    if _is_generic_governed_artifact_creation(normalized):
        matched_terms = _matched_terms(
            normalized,
            (*_CREATION_TERMS, *_GOVERNANCE_ARTIFACT_TERMS, *_ARTIFACT_KIND_TERMS, *_NAMING_MARKERS),
        )
        return {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_ARTIFACT_CREATION,
            "confidence": "MEDIUM",
            "target_kind": "ARTIFACT",
            "target_name": _extract_named_target(prompt),
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "ROUTE_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
        }

    if _is_generic_governed_execution_request(normalized):
        matched_terms = _matched_terms(
            normalized,
            (*_EXECUTION_TERMS, "governed", "execution", "workflow", "chain"),
        )
        return {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_EXECUTION_REQUEST,
            "confidence": "MEDIUM",
            "target_kind": "EXECUTION",
            "target_name": None,
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "FAIL_CLOSED_NO_CERTIFIED_GENERIC_EXECUTION_ENTRYPOINT",
        }

    return {
        "intent_detected": False,
        "intent_class": NO_EXECUTION_INTENT,
        "confidence": "LOW",
        "target_kind": None,
        "target_name": None,
        "matched_terms": [],
        "requires_clarification": False,
        "execution_authority_granted": False,
        "routing_action": None,
    }


def _is_generic_governed_domain_creation(normalized: str) -> bool:
    return (
        "domain" in normalized
        and any(term in normalized for term in _CREATION_TERMS)
        and ("governed" in normalized or any(marker in normalized for marker in _NAMING_MARKERS))
    )


def _is_generic_governed_artifact_creation(normalized: str) -> bool:
    return (
        any(subject in normalized for subject in _GOVERNANCE_ARTIFACT_TERMS)
        and any(kind in normalized for kind in _ARTIFACT_KIND_TERMS)
        and any(term in normalized for term in _CREATION_TERMS)
    )


def _is_generic_governed_execution_request(normalized: str) -> bool:
    has_execution_subject = (
        "governed execution" in normalized
        or "execution workflow" in normalized
        or "execution chain" in normalized
        or "governed workflow" in normalized
    )
    return has_execution_subject and any(term in normalized for term in _EXECUTION_TERMS)


def _extract_named_target(prompt: str) -> str | None:
    patterns = (
        r"\b(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
        r"\bdomain\s+(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
        r"\bartifact\s+(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1)
    return None


def _matched_terms(normalized: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term in normalized]


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
