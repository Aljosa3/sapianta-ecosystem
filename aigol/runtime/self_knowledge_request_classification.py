"""Deterministic pre-objective classification for Self Knowledge requests.

The classifier recognizes only the eight closed G65-05 query subjects through
the exact G65-07 Conversation request forms.  It creates no Objective, invokes
no runtime owner, and performs no semantic or natural-language inference.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_VERSION = (
    "G65_07_SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1"
)
SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1 = (
    "SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1"
)

SELF_KNOWLEDGE_QUERY = "SELF_KNOWLEDGE_QUERY"
DEVELOPMENT_OBJECTIVE = "DEVELOPMENT_OBJECTIVE"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"

REQUEST_CLASSIFICATION_BOUNDARY_FLAGS = {
    "classification_before_objective_inference": True,
    "deterministic_matching_only": True,
    "natural_language_inference_performed": False,
    "objective_created": False,
    "development_work_executed": False,
    "repository_search_performed": False,
    "conversation_invoked": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "replay_modified": False,
    "governance_modified": False,
}

_NATURAL_SUBJECT_BY_REQUEST = {
    "show architecture": "ARCHITECTURE",
    "show runtime inventory": "RUNTIME_INVENTORY",
    "show certified capabilities": "CERTIFIED_CAPABILITIES",
    "show governance state": "GOVERNANCE_STATE",
    "show execution boundaries": "EXECUTION_BOUNDARIES",
    "show certified history": "CERTIFIED_HISTORY",
    "show known limitations": "KNOWN_LIMITATIONS",
    "show ownership": "OWNERSHIP",
}
_EXPLICIT_SUBJECT_BY_REQUEST = {
    form: subject
    for subject in _NATURAL_SUBJECT_BY_REQUEST.values()
    for form in (
        f"/self-knowledge {subject.casefold()}",
        f"self_knowledge:{subject.casefold()}",
    )
}
_SUBJECT_BY_REQUEST = {
    **_NATURAL_SUBJECT_BY_REQUEST,
    **_EXPLICIT_SUBJECT_BY_REQUEST,
}
_SELF_KNOWLEDGE_TERMS = tuple(
    sorted(
        {
            request.removeprefix("show ")
            for request in _NATURAL_SUBJECT_BY_REQUEST
        },
        key=lambda value: (-len(value), value),
    )
)
_CLASSIFICATION_FIELDS = frozenset(
    {
        "artifact_type",
        "runtime_version",
        "request_text",
        "normalized_request",
        "request_classification",
        "query_subject",
        "canonical_self_knowledge_request",
        "classification_reason",
        "objective_inference_allowed",
        "deterministic_exact_match",
        "ambiguous_self_knowledge_request",
        "boundary_flags",
        "artifact_hash",
    }
)


def classify_self_knowledge_request(request_text: str) -> dict[str, Any]:
    """Classify one request before any Project Objective inference."""

    request = _require_string(request_text, "request_text")
    normalized = _normalize_request(request)
    subject = _SUBJECT_BY_REQUEST.get(normalized)
    if subject is not None:
        classification = SELF_KNOWLEDGE_QUERY
        reason = "EXACT_CLOSED_SELF_KNOWLEDGE_REQUEST_MATCH"
        canonical_request = f"/self-knowledge {subject}"
        objective_inference_allowed = False
        exact_match = True
        ambiguous = False
    elif _is_ambiguous_self_knowledge_request(normalized):
        classification = CLARIFICATION_REQUIRED
        reason = "SELF_KNOWLEDGE_REQUEST_NOT_EXACTLY_ONE_CLOSED_SUBJECT"
        subject = None
        canonical_request = None
        objective_inference_allowed = False
        exact_match = False
        ambiguous = True
    else:
        classification = DEVELOPMENT_OBJECTIVE
        reason = "NO_CLOSED_SELF_KNOWLEDGE_REQUEST_MATCH"
        subject = None
        canonical_request = None
        objective_inference_allowed = True
        exact_match = False
        ambiguous = False
    artifact = {
        "artifact_type": SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1,
        "runtime_version": SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_VERSION,
        "request_text": request,
        "normalized_request": normalized,
        "request_classification": classification,
        "query_subject": subject,
        "canonical_self_knowledge_request": canonical_request,
        "classification_reason": reason,
        "objective_inference_allowed": objective_inference_allowed,
        "deterministic_exact_match": exact_match,
        "ambiguous_self_knowledge_request": ambiguous,
        "boundary_flags": deepcopy(REQUEST_CLASSIFICATION_BOUNDARY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_self_knowledge_request_classification(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a classification by deterministic reconstruction."""

    if not isinstance(artifact, dict) or set(artifact) != _CLASSIFICATION_FIELDS:
        _fail("request classification schema is invalid")
    if artifact.get("artifact_type") != SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1:
        _fail("request classification artifact type is invalid")
    if artifact.get("runtime_version") != SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_VERSION:
        _fail("request classification version is invalid")
    if artifact.get("boundary_flags") != REQUEST_CLASSIFICATION_BOUNDARY_FLAGS:
        _fail("request classification boundary flags are invalid")
    expected = classify_self_knowledge_request(artifact.get("request_text"))
    if artifact != expected:
        _fail("request classification deterministic reconstruction mismatch")
    return deepcopy(artifact)


def _normalize_request(request: str) -> str:
    normalized = " ".join(request.split()).casefold()
    if normalized.startswith("show ") and normalized.endswith("."):
        normalized = normalized[:-1].rstrip()
    return normalized


def _is_ambiguous_self_knowledge_request(normalized: str) -> bool:
    if normalized.startswith("/self-knowledge") or normalized.startswith(
        "self_knowledge:"
    ):
        return True
    if not normalized.startswith("show "):
        return False
    remainder = normalized.removeprefix("show ")
    return any(
        remainder == term
        or remainder.startswith(f"{term} ")
        or remainder.endswith(f" {term}")
        or f" {term} " in remainder
        for term in _SELF_KNOWLEDGE_TERMS
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field_name} is required")
    return value.strip()


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(
        f"SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_INVALID: {message}"
    )


__all__ = [
    "CLARIFICATION_REQUIRED",
    "DEVELOPMENT_OBJECTIVE",
    "REQUEST_CLASSIFICATION_BOUNDARY_FLAGS",
    "SELF_KNOWLEDGE_QUERY",
    "SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1",
    "SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_VERSION",
    "classify_self_knowledge_request",
    "validate_self_knowledge_request_classification",
]
