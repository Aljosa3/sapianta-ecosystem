"""Canonical Semantic Artifact builder for Generation 2 UBTR migration."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    HUMAN_TO_GOVERNANCE,
    validate_universal_translation_artifact,
)


CANONICAL_SEMANTIC_ARTIFACT_TYPE = "CANONICAL_SEMANTIC_ARTIFACT_V1"
CANONICAL_SEMANTIC_SCHEMA_VERSION = "CANONICAL_SEMANTIC_ARTIFACT_SPECIFICATION_V1"
RUNTIME_VERSION = "CANONICAL_SEMANTIC_ARTIFACT_RUNTIME_V1"
REPLAY_STEP = "canonical_semantic_artifact_recorded"


def create_canonical_semantic_artifact_from_translation(
    *,
    semantic_artifact_id: str,
    translation_artifact: dict[str, Any],
    conversation_id: str,
    workflow_id: str | None,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a replay-visible canonical semantic artifact from UBTR translation."""

    replay_path = Path(replay_dir)
    translation = validate_universal_translation_artifact(translation_artifact)
    if translation["source_direction"] != HUMAN_TO_GOVERNANCE:
        raise FailClosedRuntimeError("canonical semantic artifact requires human-to-governance translation")
    governance_payload = _require_mapping(
        translation["translated_governance_payload"],
        "translated_governance_payload",
    )
    normalized_intent = _require_mapping(translation["normalized_intent"], "normalized_intent")
    selected_workflow = _optional_string(workflow_id) or _optional_string(governance_payload.get("workflow_candidate"))
    artifact = {
        "artifact_type": CANONICAL_SEMANTIC_ARTIFACT_TYPE,
        "schema_version": CANONICAL_SEMANTIC_SCHEMA_VERSION,
        "semantic_artifact_id": _require_string(semantic_artifact_id, "semantic_artifact_id"),
        "semantic_identity": {
            "semantic_id": f"{semantic_artifact_id}:SEMANTIC",
            "intent_family": _optional_string(normalized_intent.get("intent_family"))
            or _optional_string(governance_payload.get("intent_family"))
            or "UNKNOWN_INTENT",
            "domain": _optional_string(governance_payload.get("domain_candidate")) or "UNKNOWN_DOMAIN",
            "requested_actions": _string_list(governance_payload.get("requested_actions")),
            "entities": deepcopy(governance_payload.get("entities") or {}),
        },
        "conversation_identity": {
            "conversation_id": _require_string(conversation_id, "conversation_id"),
            "source_payload_hash": translation["source_payload"].get("human_request_hash"),
        },
        "workflow_identity": {
            "workflow_id": selected_workflow,
            "workflow_candidate": _optional_string(governance_payload.get("workflow_candidate")),
            "workflow_selected_by": "UBTR_CANONICAL_SEMANTIC_ARTIFACT"
            if selected_workflow
            else "COMPATIBILITY_FALLBACK_REQUIRED",
        },
        "replay_identity": {
            "semantic_replay_reference": str(replay_path),
            "translation_replay_reference": translation["replay_reference"],
        },
        "translation_lineage": {
            "translation_artifact_hash": translation["artifact_hash"],
            "translation_id": translation["translation_id"],
            "translation_runtime": normalized_intent.get("translation_runtime"),
            "source_direction": translation["source_direction"],
        },
        "confidence": {
            "semantic_confidence": translation["confidence"],
            "source_confidence": translation["confidence"],
        },
        "ambiguity": deepcopy(translation["ambiguity_flags"]),
        "clarification_state": {
            "clarification_required": translation["ambiguity_flags"].get("clarification_required") is True,
            "clarification_questions": list(translation["ambiguity_flags"].get("clarification_questions") or []),
        },
        "approval_state": {
            "approval_required": governance_payload.get("approval_required") is True,
            "approval_granted": False,
        },
        "execution_intent": {
            "execution_requested": governance_payload.get("execution_requested") is True,
            "worker_relevance": governance_payload.get("worker_relevance") or "UNKNOWN",
        },
        "provider_projection": {
            "provider_relevance": governance_payload.get("provider_relevance") or "UNKNOWN",
            "provider_invoked": False,
        },
        "worker_projection": {
            "worker_relevance": governance_payload.get("worker_relevance") or "UNKNOWN",
            "worker_invoked": False,
        },
        "human_readable_projection": {
            "summary": _human_summary(governance_payload, selected_workflow),
        },
        "technical_projection": {
            "normalized_intent": deepcopy(normalized_intent),
            "translated_governance_payload": deepcopy(governance_payload),
        },
        "authority_flags": _authority_flags(),
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_canonical_semantic_artifact(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "runtime_version": RUNTIME_VERSION,
        "semantic_artifact": deepcopy(artifact),
        "semantic_replay_reference": str(replay_path),
        "semantic_artifact_hash": artifact["artifact_hash"],
        "workflow_candidate": selected_workflow,
        "semantic_confidence": translation["confidence"],
        "authority_granted": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "replay_visible": True,
    }


def reconstruct_canonical_semantic_artifact_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct canonical semantic artifact replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("canonical semantic artifact replay ordering mismatch")
    expected_wrapper = deepcopy(wrapper)
    actual_hash = expected_wrapper.pop("replay_hash", None)
    if not isinstance(actual_hash, str) or replay_hash(expected_wrapper) != actual_hash:
        raise FailClosedRuntimeError("canonical semantic artifact replay hash mismatch")
    artifact = _require_mapping(wrapper.get("artifact"), "canonical_semantic_artifact")
    _validate_canonical_semantic_artifact(artifact)
    return {
        "runtime_version": RUNTIME_VERSION,
        "semantic_artifact": deepcopy(artifact),
        "semantic_replay_reference": str(replay_path),
        "semantic_artifact_hash": artifact["artifact_hash"],
        "workflow_candidate": artifact["workflow_identity"]["workflow_id"],
        "replay_hash": wrapper["replay_hash"],
        "authority_granted": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "replay_visible": True,
    }


def _validate_canonical_semantic_artifact(artifact: dict[str, Any]) -> None:
    candidate = _require_mapping(artifact, "canonical_semantic_artifact")
    if candidate.get("artifact_type") != CANONICAL_SEMANTIC_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("canonical semantic artifact type mismatch")
    if candidate.get("schema_version") != CANONICAL_SEMANTIC_SCHEMA_VERSION:
        raise FailClosedRuntimeError("canonical semantic schema version mismatch")
    _require_string(candidate.get("semantic_artifact_id"), "semantic_artifact_id")
    for field in (
        "semantic_identity",
        "conversation_identity",
        "workflow_identity",
        "replay_identity",
        "translation_lineage",
        "confidence",
        "ambiguity",
        "clarification_state",
        "approval_state",
        "execution_intent",
        "provider_projection",
        "worker_projection",
        "human_readable_projection",
        "technical_projection",
        "authority_flags",
    ):
        _require_mapping(candidate.get(field), field)
    flags = candidate["authority_flags"]
    if flags.get("semantic_authority") is not True:
        raise FailClosedRuntimeError("canonical semantic artifact must assert semantic authority")
    for key, value in flags.items():
        if key != "semantic_authority" and value is not False:
            raise FailClosedRuntimeError("canonical semantic artifact cannot grant non-semantic authority")
    actual = candidate.get("artifact_hash")
    expected = deepcopy(candidate)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("canonical semantic artifact hash mismatch")


def _authority_flags() -> dict[str, bool]:
    return {
        "semantic_authority": True,
        "governance_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "mutation_authority": False,
        "provider_authority": False,
        "worker_authority": False,
        "replay_mutation_authority": False,
    }


def _human_summary(governance_payload: dict[str, Any], workflow_id: str | None) -> str:
    action = ", ".join(_string_list(governance_payload.get("requested_actions"))) or "UNKNOWN_ACTION"
    domain = _optional_string(governance_payload.get("domain_candidate")) or "UNKNOWN_DOMAIN"
    workflow = workflow_id or "COMPATIBILITY_FALLBACK_REQUIRED"
    return f"UBTR understood a {domain} request with action {action}; workflow candidate: {workflow}."


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]
