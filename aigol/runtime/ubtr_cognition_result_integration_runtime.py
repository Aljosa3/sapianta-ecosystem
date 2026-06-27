"""Integrate governed OCS cognition results back into UBTR semantic artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_semantic_artifact_runtime import (
    CANONICAL_SEMANTIC_ARTIFACT_TYPE,
    CANONICAL_SEMANTIC_SCHEMA_VERSION,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_COMPLETED, reconstruct_ocs_cognition_replay
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_ocs_cognition_handoff_runtime import (
    HANDOFF_COMPLETED,
    RUNTIME_VERSION as UBTR_OCS_COGNITION_HANDOFF_RUNTIME_VERSION,
)


RUNTIME_VERSION = "UBTR_COGNITION_RESULT_INTEGRATION_RUNTIME_V1"
REPLAY_STEP = "ubtr_cognition_result_integrated"

INTEGRATION_COMPLETED = "UBTR_COGNITION_RESULT_INTEGRATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def integrate_ocs_cognition_result_into_canonical_semantic_artifact(
    *,
    integration_id: str,
    prior_canonical_semantic_artifact: dict[str, Any],
    ubtr_ocs_cognition_handoff_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Produce a replay-visible CSA revision that includes governed OCS cognition lineage."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        prior = _validate_canonical_semantic_artifact(prior_canonical_semantic_artifact)
        handoff = _validate_handoff_artifact(ubtr_ocs_cognition_handoff_artifact)
        cognition = _validate_ocs_cognition_replay(handoff)
        integrated = _integrated_semantic_artifact(
            integration_id=integration_id,
            prior=prior,
            handoff=handoff,
            cognition=cognition,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        integration_status = INTEGRATION_COMPLETED
        failure_reason = None
    except Exception as exc:
        prior = prior_canonical_semantic_artifact if isinstance(prior_canonical_semantic_artifact, dict) else {}
        handoff = ubtr_ocs_cognition_handoff_artifact if isinstance(ubtr_ocs_cognition_handoff_artifact, dict) else {}
        cognition = {}
        integrated = None
        integration_status = FAILED_CLOSED
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "UBTR cognition result integration failed closed"
    artifact = _integration_artifact(
        integration_id=integration_id,
        integration_status=integration_status,
        prior=prior,
        handoff=handoff,
        cognition=cognition,
        integrated=integrated,
        created_at=created_at,
        replay_reference=str(replay_path),
        failure_reason=failure_reason,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return _capture(artifact, replay_path)


def reconstruct_ubtr_cognition_result_integration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct UBTR cognition result integration replay."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("UBTR cognition result integration replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "integration_artifact")
    _verify_artifact_hash(artifact, "UBTR cognition result integration artifact")
    if artifact.get("artifact_type") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("UBTR cognition result integration artifact type mismatch")
    _validate_no_authority(artifact)
    integrated = artifact.get("integrated_canonical_semantic_artifact")
    if isinstance(integrated, dict):
        _validate_canonical_semantic_artifact(integrated)
    return {
        **_capture(artifact, replay_path),
        "replay_hash": wrapper["replay_hash"],
    }


def _integrated_semantic_artifact(
    *,
    integration_id: str,
    prior: dict[str, Any],
    handoff: dict[str, Any],
    cognition: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = deepcopy(prior)
    artifact["semantic_artifact_id"] = _require_string(integration_id, "integration_id")
    artifact["replay_identity"] = {
        **deepcopy(prior["replay_identity"]),
        "semantic_replay_reference": _require_string(replay_reference, "replay_reference"),
        "prior_semantic_artifact_hash": prior["artifact_hash"],
        "ocs_cognition_handoff_replay_reference": handoff["replay_reference"],
        "ocs_cognition_replay_reference": handoff["ocs_cognition_replay_reference"],
    }
    artifact["translation_lineage"] = {
        **deepcopy(prior["translation_lineage"]),
        "cognition_result_integration_runtime": RUNTIME_VERSION,
        "prior_semantic_artifact_hash": prior["artifact_hash"],
    }
    artifact["cognition_result_lineage"] = {
        "ubtr_ocs_cognition_handoff_hash": handoff["artifact_hash"],
        "ubtr_ocs_cognition_request_hash": handoff["ubtr_ocs_cognition_request_hash"],
        "ocs_context_hash": handoff["ocs_context_hash"],
        "ocs_cognition_hash": handoff["ocs_cognition_hash"],
        "ocs_cognition_status": cognition["cognition_status"],
        "ocs_provider_necessity": deepcopy(cognition["provider_necessity"]),
        "ocs_task_intent": deepcopy(cognition["task_intent"]),
        "ocs_ambiguity": deepcopy(cognition["ambiguity"]),
        "ocs_clarification_requirements": deepcopy(cognition["clarification_requirements"]),
    }
    artifact["confidence"] = {
        **deepcopy(prior["confidence"]),
        "cognition_result_confidence": cognition["task_intent"]["confidence"],
        "cognition_result_status": cognition["cognition_status"],
    }
    artifact["ambiguity"] = {
        **deepcopy(prior["ambiguity"]),
        "ocs_ambiguity": deepcopy(cognition["ambiguity"]),
        "ocs_clarification_requirements": deepcopy(cognition["clarification_requirements"]),
    }
    artifact["provider_projection"] = {
        **deepcopy(prior["provider_projection"]),
        "provider_necessity": deepcopy(cognition["provider_necessity"]),
        "provider_selection_owner": "OCS",
        "provider_invoked": False,
    }
    artifact["human_readable_projection"] = {
        **deepcopy(prior["human_readable_projection"]),
        "cognition_result_summary": _cognition_summary(cognition),
    }
    artifact["technical_projection"] = {
        **deepcopy(prior["technical_projection"]),
        "ocs_cognition_result": {
            "task_intent": deepcopy(cognition["task_intent"]),
            "ambiguity": deepcopy(cognition["ambiguity"]),
            "provider_necessity": deepcopy(cognition["provider_necessity"]),
        },
    }
    artifact["created_at"] = _require_string(created_at, "created_at")
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_canonical_semantic_artifact(artifact)
    return artifact


def _integration_artifact(
    *,
    integration_id: str,
    integration_status: str,
    prior: dict[str, Any],
    handoff: dict[str, Any],
    cognition: dict[str, Any],
    integrated: dict[str, Any] | None,
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RUNTIME_VERSION,
        "integration_id": integration_id if isinstance(integration_id, str) and integration_id.strip() else "INVALID",
        "integration_status": integration_status,
        "prior_canonical_semantic_artifact_hash": prior.get("artifact_hash"),
        "ubtr_ocs_cognition_handoff_hash": handoff.get("artifact_hash"),
        "ocs_cognition_hash": cognition.get("cognition_hash"),
        "integrated_canonical_semantic_artifact": deepcopy(integrated),
        "integrated_canonical_semantic_artifact_hash": integrated.get("artifact_hash")
        if isinstance(integrated, dict)
        else None,
        "provider_selection_owner": "OCS",
        "ubtr_semantic_artifact_owner": "UBTR",
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_authorized": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
        "failure_reason": failure_reason,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "integration_status": artifact["integration_status"],
        "integration_artifact": deepcopy(artifact),
        "integration_replay_reference": str(replay_path),
        "prior_canonical_semantic_artifact_hash": artifact["prior_canonical_semantic_artifact_hash"],
        "ubtr_ocs_cognition_handoff_hash": artifact["ubtr_ocs_cognition_handoff_hash"],
        "ocs_cognition_hash": artifact["ocs_cognition_hash"],
        "integrated_canonical_semantic_artifact": deepcopy(artifact["integrated_canonical_semantic_artifact"]),
        "integrated_canonical_semantic_artifact_hash": artifact["integrated_canonical_semantic_artifact_hash"],
        "fail_closed": artifact["integration_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "execution_requested": False,
        "authority_granted": False,
        "replay_visible": True,
    }


def _validate_canonical_semantic_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(artifact, "canonical_semantic_artifact")
    if candidate.get("artifact_type") != CANONICAL_SEMANTIC_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("UBTR cognition integration canonical semantic artifact type mismatch")
    if candidate.get("schema_version") != CANONICAL_SEMANTIC_SCHEMA_VERSION:
        raise FailClosedRuntimeError("UBTR cognition integration canonical semantic schema mismatch")
    flags = _require_mapping(candidate.get("authority_flags"), "authority_flags")
    if flags.get("semantic_authority") is not True:
        raise FailClosedRuntimeError("UBTR cognition integration semantic authority missing")
    for key, value in flags.items():
        if key != "semantic_authority" and value is not False:
            raise FailClosedRuntimeError("UBTR cognition integration canonical artifact grants non-semantic authority")
    _verify_artifact_hash(candidate, "canonical semantic artifact")
    return deepcopy(candidate)


def _validate_handoff_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(artifact, "ubtr_ocs_cognition_handoff_artifact")
    if candidate.get("artifact_type") != UBTR_OCS_COGNITION_HANDOFF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("UBTR cognition integration handoff artifact type mismatch")
    if candidate.get("handoff_status") != HANDOFF_COMPLETED:
        raise FailClosedRuntimeError("UBTR cognition integration requires completed OCS handoff")
    _verify_artifact_hash(candidate, "UBTR OCS cognition handoff artifact")
    _validate_no_authority(candidate)
    return deepcopy(candidate)


def _validate_ocs_cognition_replay(handoff: dict[str, Any]) -> dict[str, Any]:
    replay_reference = _require_string(handoff.get("ocs_cognition_replay_reference"), "ocs_cognition_replay_reference")
    cognition = reconstruct_ocs_cognition_replay(replay_reference)
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("UBTR cognition integration requires completed OCS cognition")
    if cognition.get("cognition_hash") != handoff.get("ocs_cognition_hash"):
        raise FailClosedRuntimeError("UBTR cognition integration OCS cognition hash mismatch")
    return deepcopy(cognition)


def _cognition_summary(cognition: dict[str, Any]) -> str:
    provider = cognition["provider_necessity"]["necessity_classification"]
    intent = cognition["task_intent"]["intent"]
    confidence = cognition["task_intent"]["confidence"]
    return f"Governed OCS cognition reviewed intent {intent} with {confidence} confidence; provider necessity: {provider}."


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "worker_invoked",
        "approval_granted",
        "execution_authorized",
        "execution_requested",
        "dispatch_requested",
        "governance_mutated",
        "replay_mutated",
        "authority_granted",
    ):
        if artifact.get(field) is not False and artifact.get(field) is not None:
            raise FailClosedRuntimeError("UBTR cognition result integration authority drift")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError("UBTR cognition result integration replay hash mismatch")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError("UBTR cognition result integration replay path already contains artifacts")
    path.mkdir(parents=True, exist_ok=True)
