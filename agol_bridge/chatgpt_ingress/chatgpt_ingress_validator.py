"""Fail-closed validation for ChatGPT ingress artifacts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .chatgpt_ingress_artifact import (
    ARTIFACT_TYPE,
    BOUNDARY_STATEMENT,
    SCHEMA_VERSION,
    SOURCE,
    artifact_hash_for,
    hash_text,
    replay_identity_for,
)

ACCEPTED_AS_SEMANTIC_INPUT = "ACCEPTED_AS_SEMANTIC_INPUT"
REJECTED = "REJECTED"
ALLOWED_VALIDATION_STATUSES = (ACCEPTED_AS_SEMANTIC_INPUT, REJECTED)

REQUIRED_FIELDS = (
    "artifact_type",
    "schema_version",
    "source",
    "created_at",
    "session_id",
    "human_request",
    "chatgpt_semantic_output",
    "normalized_intent",
    "expected_artifacts",
    "constraints",
    "forbidden_operations",
    "authority_boundary",
    "provenance",
    "replay_identity",
    "hashes",
    "validation_status",
)

AUTHORITY_FLAGS = (
    "chatgpt_authority",
    "execution_authority",
    "governance_authority",
    "approval_authority",
    "provider_dispatch_authority",
    "autonomous_continuation_authority",
)

FORBIDDEN_FIELD_NAMES = (
    "provider_dispatch",
    "provider_dispatch_id",
    "provider_id",
    "selected_provider",
    "execution_authorization",
    "execution_authorized",
    "authorization_token",
    "approval_token",
    "approved_for_execution",
    "governance_approval",
    "governance_approved",
    "autonomous_continuation",
    "continue_autonomously",
    "follow_up_tasks",
)

HIDDEN_AUTHORITY_PHRASES = (
    "approved for execution",
    "approval granted",
    "governance approved",
    "governance approval granted",
    "authorize execution",
    "execution authorized",
    "dispatch to codex",
    "provider dispatch",
    "codex is authorized",
    "continue autonomously",
    "autonomous continuation",
)

SEMANTIC_CORRECTNESS_PHRASES = (
    "semantic correctness verified",
    "semantically correct",
    "guaranteed correct",
    "correctness guaranteed",
    "verified as correct",
)

BYPASS_GOVERNANCE_PHRASES = (
    "bypass aigol",
    "bypass governance",
    "skip aigol",
    "skip governance",
    "without aigol validation",
    "without governance validation",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _reject(errors: list[dict[str, str]]) -> dict:
    return {"valid": False, "status": REJECTED, "errors": errors}


def _add(errors: list[dict[str, str]], field: str, error: str) -> None:
    errors.append({"field": field, "error": error})


def _walk_forbidden_fields(value: Any, *, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if str(key) in FORBIDDEN_FIELD_NAMES:
                findings.append(child_path)
            findings.extend(_walk_forbidden_fields(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            findings.extend(_walk_forbidden_fields(child, path=child_path))
    return findings


def _canonical_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {_canonical_text(child)}" for key, child in value.items())
    if isinstance(value, list):
        return " ".join(_canonical_text(child) for child in value)
    return str(value or "")


def _contains_phrase(value: Any, phrases: tuple[str, ...]) -> str | None:
    text = _canonical_text(value).lower()
    for phrase in phrases:
        if phrase in text:
            return phrase
    return None


def _claim_payload(artifact: dict) -> dict:
    """Return fields where authority/correctness claims are meaningful.

    Boundary statements and forbidden operation lists intentionally contain
    authority terms as negations, so they are validated structurally instead
    of scanned as positive claims.
    """

    return {
        "human_request": artifact.get("human_request", ""),
        "chatgpt_semantic_output": artifact.get("chatgpt_semantic_output", ""),
        "normalized_intent": artifact.get("normalized_intent", ""),
        "expected_artifacts": artifact.get("expected_artifacts", []),
        "constraints": artifact.get("constraints", []),
        "provenance": artifact.get("provenance", {}),
    }


def _validate_string_fields(artifact: dict, errors: list[dict[str, str]]) -> None:
    for field in (
        "artifact_type",
        "schema_version",
        "source",
        "created_at",
        "session_id",
        "human_request",
        "chatgpt_semantic_output",
        "normalized_intent",
        "replay_identity",
        "validation_status",
    ):
        if not isinstance(artifact.get(field), str) or not artifact[field].strip():
            _add(errors, field, "expected non-empty str")


def _validate_list_fields(artifact: dict, errors: list[dict[str, str]]) -> None:
    for field in ("expected_artifacts", "constraints", "forbidden_operations"):
        if not isinstance(artifact.get(field), list):
            _add(errors, field, "expected list")


def _validate_authority_boundary(artifact: dict, errors: list[dict[str, str]]) -> None:
    boundary = artifact.get("authority_boundary")
    if not isinstance(boundary, dict):
        _add(errors, "authority_boundary", "expected dict")
        return
    for flag in AUTHORITY_FLAGS:
        if boundary.get(flag) is not False:
            _add(errors, f"authority_boundary.{flag}", "authority flag must be false")
    if boundary.get("boundary_statement") != BOUNDARY_STATEMENT:
        _add(errors, "authority_boundary.boundary_statement", "required boundary statement missing")


def _validate_provenance(artifact: dict, errors: list[dict[str, str]]) -> None:
    provenance = artifact.get("provenance")
    if not isinstance(provenance, dict) or not provenance:
        _add(errors, "provenance", "provenance is required")
        return
    for field in ("aigol_governance_required",):
        if provenance.get(field) is not True:
            _add(errors, f"provenance.{field}", "AiGOL governance requirement must be true")
    for field in ("execution_authority", "provider_dispatch_authority"):
        if provenance.get(field) is not False:
            _add(errors, f"provenance.{field}", "authority must be false")


def _validate_hashes(artifact: dict, errors: list[dict[str, str]]) -> None:
    hashes = artifact.get("hashes")
    if not isinstance(hashes, dict):
        _add(errors, "hashes", "expected dict")
        return
    for field in ("human_request_hash", "semantic_output_hash", "artifact_hash"):
        value = hashes.get(field)
        if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
            _add(errors, f"hashes.{field}", "hash is missing or malformed")
    if errors:
        return
    expected_human_hash = hash_text(artifact.get("human_request", ""))
    expected_semantic_hash = hash_text(artifact.get("chatgpt_semantic_output", ""))
    if hashes.get("human_request_hash") != expected_human_hash:
        _add(errors, "hashes.human_request_hash", "human_request_hash mismatch")
    if hashes.get("semantic_output_hash") != expected_semantic_hash:
        _add(errors, "hashes.semantic_output_hash", "semantic_output_hash mismatch")
    expected_replay_identity = replay_identity_for(
        session_id=artifact.get("session_id", ""),
        human_request_hash=hashes.get("human_request_hash", ""),
        semantic_output_hash=hashes.get("semantic_output_hash", ""),
        schema_version=artifact.get("schema_version", ""),
    )
    if artifact.get("replay_identity") != expected_replay_identity:
        _add(errors, "replay_identity", "replay identity mismatch")
    expected_artifact_hash = artifact_hash_for(artifact)
    if hashes.get("artifact_hash") != expected_artifact_hash:
        _add(errors, "hashes.artifact_hash", "artifact_hash mismatch")


def validate_chatgpt_ingress_artifact(artifact: Any) -> dict:
    """Validate a ChatGPT ingress artifact as untrusted semantic input."""

    if not isinstance(artifact, dict) or isinstance(artifact, list):
        return _reject([{"field": "artifact", "error": "artifact must be a JSON object"}])

    artifact_copy = _canonical_copy(artifact)
    errors: list[dict[str, str]] = []

    for field in REQUIRED_FIELDS:
        if field not in artifact_copy:
            _add(errors, field, "required field missing")
    if errors:
        return _reject(errors)

    _validate_string_fields(artifact_copy, errors)
    _validate_list_fields(artifact_copy, errors)

    if artifact_copy.get("artifact_type") != ARTIFACT_TYPE:
        _add(errors, "artifact_type", "unsupported artifact_type")
    if artifact_copy.get("schema_version") != SCHEMA_VERSION:
        _add(errors, "schema_version", "unsupported schema_version")
    if artifact_copy.get("source") != SOURCE:
        _add(errors, "source", "source must be chatgpt")
    if artifact_copy.get("validation_status") not in ALLOWED_VALIDATION_STATUSES:
        _add(errors, "validation_status", "unsupported validation status")
    if artifact_copy.get("validation_status") == REJECTED:
        _add(errors, "validation_status", "rejected artifact cannot be accepted as semantic input")

    _validate_authority_boundary(artifact_copy, errors)
    _validate_provenance(artifact_copy, errors)

    forbidden_fields = _walk_forbidden_fields(artifact_copy)
    for field in forbidden_fields:
        _add(errors, field, "forbidden provider dispatch, execution authorization, approval, or continuation field present")

    claim_payload = _claim_payload(artifact_copy)
    hidden_authority = _contains_phrase(claim_payload, HIDDEN_AUTHORITY_PHRASES)
    if hidden_authority is not None:
        _add(errors, "artifact", f"hidden authority language detected: {hidden_authority}")
    semantic_correctness = _contains_phrase(claim_payload, SEMANTIC_CORRECTNESS_PHRASES)
    if semantic_correctness is not None:
        _add(errors, "artifact", f"semantic correctness claim detected: {semantic_correctness}")
    bypass_governance = _contains_phrase(claim_payload, BYPASS_GOVERNANCE_PHRASES)
    if bypass_governance is not None:
        _add(errors, "artifact", f"AiGOL governance bypass claim detected: {bypass_governance}")

    _validate_hashes(artifact_copy, errors)

    if errors:
        return _reject(errors)
    return {
        "valid": True,
        "status": ACCEPTED_AS_SEMANTIC_INPUT,
        "errors": [],
        "replay_identity": artifact_copy["replay_identity"],
        "artifact_hash": artifact_copy["hashes"]["artifact_hash"],
    }


__all__ = [
    "ACCEPTED_AS_SEMANTIC_INPUT",
    "ALLOWED_VALIDATION_STATUSES",
    "REJECTED",
    "validate_chatgpt_ingress_artifact",
]
