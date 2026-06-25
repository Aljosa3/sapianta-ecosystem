"""Canonical schema for Universal Bidirectional Translation artifacts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_VERSION = "UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_V1"
UNIVERSAL_TRANSLATION_ARTIFACT_TYPE = "UNIVERSAL_TRANSLATION_ARTIFACT_V1"

HUMAN_TO_GOVERNANCE = "HUMAN_TO_GOVERNANCE"
GOVERNANCE_TO_HUMAN = "GOVERNANCE_TO_HUMAN"
ALLOWED_SOURCE_DIRECTIONS = frozenset({HUMAN_TO_GOVERNANCE, GOVERNANCE_TO_HUMAN})

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
GOVERNANCE_ONLY = "GOVERNANCE_ONLY"
UNKNOWN = "UNKNOWN"
ALLOWED_CONFIDENCE = frozenset({HIGH, MEDIUM, LOW, GOVERNANCE_ONLY, UNKNOWN})

NO_AMBIGUITY = "NO_AMBIGUITY"
MINOR_AMBIGUITY = "MINOR_AMBIGUITY"
MATERIAL_AMBIGUITY = "MATERIAL_AMBIGUITY"
UNRESOLVED_AMBIGUITY = "UNRESOLVED_AMBIGUITY"
UNSAFE_AMBIGUITY = "UNSAFE_AMBIGUITY"
ALLOWED_AMBIGUITY_STATUS = frozenset(
    {
        NO_AMBIGUITY,
        MINOR_AMBIGUITY,
        MATERIAL_AMBIGUITY,
        UNRESOLVED_AMBIGUITY,
        UNSAFE_AMBIGUITY,
    }
)

AUTHORITY_FLAG_FIELDS = (
    "authority_granted",
    "translation_authority",
    "governance_authority",
    "approval_authority",
    "execution_authority",
    "mutation_authority",
    "replay_mutation_authority",
    "provider_authority",
    "worker_authority",
)

SCHEMA_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "translation_id",
        "translation_request",
        "source_direction",
        "source_payload",
        "normalized_intent",
        "translated_governance_payload",
        "human_readable_payload",
        "ambiguity_flags",
        "confidence",
        "provider_metadata",
        "deterministic_fallback_status",
        "replay_reference",
        "authority_flags",
        "created_at",
        "artifact_hash",
    }
)


def create_universal_translation_artifact(
    *,
    translation_id: str,
    translation_request: dict[str, Any],
    source_direction: str,
    source_payload: dict[str, Any],
    normalized_intent: dict[str, Any],
    translated_governance_payload: dict[str, Any] | None = None,
    human_readable_payload: dict[str, Any] | None = None,
    ambiguity_flags: dict[str, Any] | None = None,
    confidence: str,
    provider_metadata: dict[str, Any] | None = None,
    deterministic_fallback_status: dict[str, Any] | None = None,
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a canonical, hash-bound translation artifact."""

    artifact = {
        "artifact_type": UNIVERSAL_TRANSLATION_ARTIFACT_TYPE,
        "schema_version": UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_VERSION,
        "translation_id": _require_string(translation_id, "translation_id"),
        "translation_request": _require_mapping(translation_request, "translation_request"),
        "source_direction": _require_direction(source_direction),
        "source_payload": _require_mapping(source_payload, "source_payload"),
        "normalized_intent": _require_mapping(normalized_intent, "normalized_intent"),
        "translated_governance_payload": _mapping_or_empty(
            translated_governance_payload,
            "translated_governance_payload",
        ),
        "human_readable_payload": _mapping_or_empty(human_readable_payload, "human_readable_payload"),
        "ambiguity_flags": _normalized_ambiguity_flags(ambiguity_flags),
        "confidence": _require_confidence(confidence),
        "provider_metadata": _normalized_provider_metadata(provider_metadata),
        "deterministic_fallback_status": _normalized_fallback_status(deterministic_fallback_status),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "authority_flags": _default_authority_flags(),
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = _artifact_hash(artifact)
    return validate_universal_translation_artifact(artifact)


def validate_universal_translation_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a canonical copy of a Universal Translation artifact."""

    candidate = _require_mapping(artifact, "translation_artifact")
    if set(candidate) != SCHEMA_FIELDS:
        raise FailClosedRuntimeError("universal translation artifact has malformed structure")
    if candidate.get("artifact_type") != UNIVERSAL_TRANSLATION_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("universal translation artifact type mismatch")
    if candidate.get("schema_version") != UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_VERSION:
        raise FailClosedRuntimeError("universal translation schema version mismatch")
    _require_string(candidate.get("translation_id"), "translation_id")
    _validate_translation_request(candidate.get("translation_request"))
    direction = _require_direction(candidate.get("source_direction"))
    _require_mapping(candidate.get("source_payload"), "source_payload")
    _require_mapping(candidate.get("normalized_intent"), "normalized_intent")
    governance_payload = _require_mapping(
        candidate.get("translated_governance_payload"),
        "translated_governance_payload",
    )
    human_payload = _require_mapping(candidate.get("human_readable_payload"), "human_readable_payload")
    if direction == HUMAN_TO_GOVERNANCE and not governance_payload:
        raise FailClosedRuntimeError("human-to-governance translation requires governance payload")
    if direction == GOVERNANCE_TO_HUMAN and not human_payload:
        raise FailClosedRuntimeError("governance-to-human translation requires human-readable payload")
    _validate_ambiguity_flags(candidate.get("ambiguity_flags"))
    _require_confidence(candidate.get("confidence"))
    _validate_provider_metadata(candidate.get("provider_metadata"))
    _validate_fallback_status(candidate.get("deterministic_fallback_status"))
    _require_string(candidate.get("replay_reference"), "replay_reference")
    _validate_authority_flags(candidate.get("authority_flags"))
    _require_string(candidate.get("created_at"), "created_at")
    canonical_serialize(candidate)
    if candidate.get("artifact_hash") != _artifact_hash(candidate):
        raise FailClosedRuntimeError("universal translation artifact hash mismatch")
    return deepcopy(candidate)


def translation_artifact_hash(artifact: dict[str, Any]) -> str:
    """Return the stable artifact hash after validation."""

    return validate_universal_translation_artifact(artifact)["artifact_hash"]


def authority_flags_for_translation() -> dict[str, bool]:
    """Return canonical authority-denial flags for translation artifacts."""

    return _default_authority_flags()


def _artifact_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    return replay_hash(value)


def _default_authority_flags() -> dict[str, bool]:
    return {field: False for field in AUTHORITY_FLAG_FIELDS}


def _validate_translation_request(value: Any) -> None:
    request = _require_mapping(value, "translation_request")
    _require_string(request.get("translation_request_id"), "translation_request.translation_request_id")
    if "created_at" in request:
        _require_string(request.get("created_at"), "translation_request.created_at")
    canonical_serialize(request)


def _normalized_ambiguity_flags(value: dict[str, Any] | None) -> dict[str, Any]:
    flags = _mapping_or_empty(value, "ambiguity_flags")
    if "ambiguity_status" not in flags:
        flags["ambiguity_status"] = NO_AMBIGUITY
    if "clarification_required" not in flags:
        flags["clarification_required"] = flags["ambiguity_status"] in {
            MATERIAL_AMBIGUITY,
            UNRESOLVED_AMBIGUITY,
            UNSAFE_AMBIGUITY,
        }
    if "clarification_questions" not in flags:
        flags["clarification_questions"] = []
    _validate_ambiguity_flags(flags)
    return flags


def _validate_ambiguity_flags(value: Any) -> None:
    flags = _require_mapping(value, "ambiguity_flags")
    status = flags.get("ambiguity_status")
    if status not in ALLOWED_AMBIGUITY_STATUS:
        raise FailClosedRuntimeError("universal translation ambiguity status invalid")
    if not isinstance(flags.get("clarification_required"), bool):
        raise FailClosedRuntimeError("universal translation clarification_required must be boolean")
    questions = flags.get("clarification_questions")
    if not isinstance(questions, list) or not all(isinstance(item, str) for item in questions):
        raise FailClosedRuntimeError("universal translation clarification_questions must be strings")
    canonical_serialize(flags)


def _normalized_provider_metadata(value: dict[str, Any] | None) -> dict[str, Any]:
    metadata = _mapping_or_empty(value, "provider_metadata")
    metadata.setdefault("provider_used", False)
    metadata.setdefault("provider_count", 0)
    metadata.setdefault("providers", [])
    metadata.setdefault("comparison_used", False)
    _validate_provider_metadata(metadata)
    return metadata


def _validate_provider_metadata(value: Any) -> None:
    metadata = _require_mapping(value, "provider_metadata")
    if not isinstance(metadata.get("provider_used"), bool):
        raise FailClosedRuntimeError("universal translation provider_used must be boolean")
    if not isinstance(metadata.get("provider_count"), int) or metadata["provider_count"] < 0:
        raise FailClosedRuntimeError("universal translation provider_count must be non-negative integer")
    providers = metadata.get("providers")
    if not isinstance(providers, list):
        raise FailClosedRuntimeError("universal translation providers must be a list")
    if metadata["provider_count"] != len(providers):
        raise FailClosedRuntimeError("universal translation provider_count mismatch")
    if metadata["provider_used"] is not bool(providers):
        raise FailClosedRuntimeError("universal translation provider_used mismatch")
    if not isinstance(metadata.get("comparison_used"), bool):
        raise FailClosedRuntimeError("universal translation comparison_used must be boolean")
    canonical_serialize(metadata)


def _normalized_fallback_status(value: dict[str, Any] | None) -> dict[str, Any]:
    status = _mapping_or_empty(value, "deterministic_fallback_status")
    status.setdefault("fallback_used", False)
    status.setdefault("fallback_reason", None)
    status.setdefault("deterministic_rule_ids", [])
    _validate_fallback_status(status)
    return status


def _validate_fallback_status(value: Any) -> None:
    status = _require_mapping(value, "deterministic_fallback_status")
    if not isinstance(status.get("fallback_used"), bool):
        raise FailClosedRuntimeError("universal translation fallback_used must be boolean")
    reason = status.get("fallback_reason")
    if reason is not None and not isinstance(reason, str):
        raise FailClosedRuntimeError("universal translation fallback_reason must be string or null")
    rule_ids = status.get("deterministic_rule_ids")
    if not isinstance(rule_ids, list) or not all(isinstance(item, str) for item in rule_ids):
        raise FailClosedRuntimeError("universal translation deterministic_rule_ids must be strings")
    canonical_serialize(status)


def _validate_authority_flags(value: Any) -> None:
    flags = _require_mapping(value, "authority_flags")
    if set(flags) != set(AUTHORITY_FLAG_FIELDS):
        raise FailClosedRuntimeError("universal translation authority flags malformed")
    for field in AUTHORITY_FLAG_FIELDS:
        if flags[field] is not False:
            raise FailClosedRuntimeError("universal translation cannot grant authority")


def _require_direction(value: Any) -> str:
    if value not in ALLOWED_SOURCE_DIRECTIONS:
        raise FailClosedRuntimeError("universal translation source direction invalid")
    return str(value)


def _require_confidence(value: Any) -> str:
    if value not in ALLOWED_CONFIDENCE:
        raise FailClosedRuntimeError("universal translation confidence invalid")
    return str(value)


def _mapping_or_empty(value: dict[str, Any] | None, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    return _require_mapping(value, field_name)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    canonical_serialize(value)
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
