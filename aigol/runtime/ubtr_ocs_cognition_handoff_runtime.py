"""Replay-safe UBTR request to OCS cognition handoff runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import (
    OCS_COGNITION_COMPLETED,
    PROVIDER_REQUIRED,
    run_ocs_cognition,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import (
    OCS_COGNITION_REQUESTED,
    RUNTIME_VERSION as UBTR_SEMANTIC_COGNITION_RUNTIME_VERSION,
)


RUNTIME_VERSION = "UBTR_OCS_COGNITION_HANDOFF_RUNTIME_V1"
REPLAY_STEP = "ubtr_ocs_cognition_handoff_recorded"

HANDOFF_COMPLETED = "UBTR_OCS_COGNITION_HANDOFF_COMPLETED"
HANDOFF_NOT_REQUIRED = "UBTR_OCS_COGNITION_HANDOFF_NOT_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

UBTR_GOVERNED_OCS_COGNITION_REQUEST_V1 = "UBTR_GOVERNED_OCS_COGNITION_REQUEST_V1"
UBTR_TO_OCS_COGNITION_HANDOFF_SOURCE_V1 = "UBTR_TO_OCS_COGNITION_HANDOFF_SOURCE_V1"


def run_ubtr_ocs_cognition_handoff(
    *,
    handoff_id: str,
    ubtr_orchestration_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Hand a governed UBTR cognition request to the existing OCS cognition pipeline."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        orchestration = _validate_ubtr_orchestration_artifact(ubtr_orchestration_artifact)
        request = _validate_ocs_request(orchestration)
        source_artifact = _handoff_source_artifact(
            handoff_id=handoff_id,
            orchestration=orchestration,
            request=request,
            created_at=created_at,
        )
        context_capture = assemble_ocs_context(
            context_assembly_id=f"{_require_string(handoff_id, 'handoff_id')}:OCS-CONTEXT",
            created_at=created_at,
            replay_dir=replay_path / "ocs_context",
            source_context={"conversation_context": [source_artifact]},
            source_chain_id=orchestration.get("orchestration_id"),
            source_request_reference=request.get("request_id"),
        )
        _require_context_success(context_capture)
        cognition_capture = run_ocs_cognition(
            cognition_id=f"{_require_string(handoff_id, 'handoff_id')}:OCS-COGNITION",
            ocs_context_assembly_artifact=context_capture["ocs_context_assembly_artifact"],
            created_at=created_at,
            replay_dir=replay_path / "ocs_cognition",
        )
        _require_cognition_success(cognition_capture)
        artifact = _handoff_artifact(
            handoff_id=handoff_id,
            handoff_status=HANDOFF_COMPLETED,
            orchestration=orchestration,
            request=request,
            source_artifact=source_artifact,
            context_capture=context_capture,
            cognition_capture=cognition_capture,
            failure_reason=None,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "UBTR to OCS cognition handoff failed closed"
        artifact = _failed_handoff_artifact(
            handoff_id=handoff_id,
            ubtr_orchestration_artifact=ubtr_orchestration_artifact,
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
    _persist_failure_if_possible(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return _capture(artifact, replay_path)


def reconstruct_ubtr_ocs_cognition_handoff_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct UBTR to OCS cognition handoff replay."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("UBTR OCS cognition handoff replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "handoff_artifact")
    _verify_artifact_hash(artifact, "UBTR OCS cognition handoff artifact")
    if artifact.get("artifact_type") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("UBTR OCS cognition handoff artifact type mismatch")
    _validate_no_authority(artifact)
    return {
        **_capture(artifact, replay_path),
        "replay_hash": wrapper["replay_hash"],
    }


def _handoff_source_artifact(
    *,
    handoff_id: str,
    orchestration: dict[str, Any],
    request: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": UBTR_TO_OCS_COGNITION_HANDOFF_SOURCE_V1,
        "artifact_id": f"{_require_string(handoff_id, 'handoff_id')}:HANDOFF-SOURCE",
        "status": "UBTR_GOVERNED_OCS_COGNITION_REQUEST_READY",
        "ubtr_orchestration_id": orchestration["orchestration_id"],
        "ubtr_orchestration_hash": orchestration["artifact_hash"],
        "ubtr_ocs_cognition_request_id": request["request_id"],
        "ubtr_ocs_cognition_request_hash": request["artifact_hash"],
        "canonical_semantic_artifact_hash": request["canonical_semantic_artifact_hash"],
        "provider_necessity_classification": PROVIDER_REQUIRED,
        "provider_selection_owner": "OCS",
        "capability_escalation_owner": "OCS",
        "multi_provider_comparison_owner": "OCS",
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _handoff_artifact(
    *,
    handoff_id: str,
    handoff_status: str,
    orchestration: dict[str, Any],
    request: dict[str, Any],
    source_artifact: dict[str, Any],
    context_capture: dict[str, Any],
    cognition_capture: dict[str, Any],
    failure_reason: str | None,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RUNTIME_VERSION,
        "handoff_id": _require_string(handoff_id, "handoff_id"),
        "handoff_status": handoff_status,
        "ubtr_orchestration_reference": orchestration["orchestration_id"],
        "ubtr_orchestration_hash": orchestration["artifact_hash"],
        "ubtr_ocs_cognition_request_reference": request["request_id"],
        "ubtr_ocs_cognition_request_hash": request["artifact_hash"],
        "handoff_source_hash": source_artifact["artifact_hash"],
        "ocs_context_replay_reference": context_capture["ocs_context_assembly_replay_reference"],
        "ocs_context_hash": context_capture["context_hash"],
        "ocs_cognition_replay_reference": cognition_capture["ocs_cognition_replay_reference"],
        "ocs_cognition_hash": cognition_capture["cognition_hash"],
        "ocs_cognition_status": cognition_capture["cognition_status"],
        "ocs_provider_necessity": deepcopy(cognition_capture["provider_necessity"]),
        "provider_selection_owner": "OCS",
        "capability_escalation_owner": "OCS",
        "multi_provider_comparison_owner": "OCS",
        "ubtr_provider_selection": False,
        "ubtr_provider_invocation": False,
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
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_handoff_artifact(
    *,
    handoff_id: str,
    ubtr_orchestration_artifact: Any,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    orchestration_hash = (
        ubtr_orchestration_artifact.get("artifact_hash") if isinstance(ubtr_orchestration_artifact, dict) else None
    )
    artifact = {
        "artifact_type": RUNTIME_VERSION,
        "handoff_id": handoff_id if isinstance(handoff_id, str) and handoff_id.strip() else "INVALID_HANDOFF_ID",
        "handoff_status": FAILED_CLOSED,
        "ubtr_orchestration_reference": (
            ubtr_orchestration_artifact.get("orchestration_id")
            if isinstance(ubtr_orchestration_artifact, dict)
            else None
        ),
        "ubtr_orchestration_hash": orchestration_hash,
        "ubtr_ocs_cognition_request_reference": None,
        "ubtr_ocs_cognition_request_hash": None,
        "handoff_source_hash": None,
        "ocs_context_replay_reference": None,
        "ocs_context_hash": None,
        "ocs_cognition_replay_reference": None,
        "ocs_cognition_hash": None,
        "ocs_cognition_status": None,
        "ocs_provider_necessity": None,
        "provider_selection_owner": "OCS",
        "capability_escalation_owner": "OCS",
        "multi_provider_comparison_owner": "OCS",
        "ubtr_provider_selection": False,
        "ubtr_provider_invocation": False,
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
        "handoff_status": artifact["handoff_status"],
        "handoff_artifact": deepcopy(artifact),
        "handoff_replay_reference": str(replay_path),
        "ubtr_orchestration_hash": artifact["ubtr_orchestration_hash"],
        "ubtr_ocs_cognition_request_hash": artifact["ubtr_ocs_cognition_request_hash"],
        "ocs_context_hash": artifact["ocs_context_hash"],
        "ocs_cognition_hash": artifact["ocs_cognition_hash"],
        "ocs_cognition_status": artifact["ocs_cognition_status"],
        "ocs_provider_necessity": deepcopy(artifact["ocs_provider_necessity"]),
        "fail_closed": artifact["handoff_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "provider_selection_owner": artifact["provider_selection_owner"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "execution_requested": False,
        "authority_granted": False,
        "replay_visible": True,
    }


def _validate_ubtr_orchestration_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(artifact, "ubtr_orchestration_artifact")
    if candidate.get("artifact_type") != UBTR_SEMANTIC_COGNITION_RUNTIME_VERSION:
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: invalid UBTR orchestration artifact")
    _verify_artifact_hash(candidate, "UBTR orchestration artifact")
    _validate_no_authority(candidate)
    if candidate.get("semantic_decision") != OCS_COGNITION_REQUESTED:
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: OCS cognition was not requested")
    if candidate.get("ocs_cognition_request_hash") is None:
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: OCS cognition request hash missing")
    return deepcopy(candidate)


def _validate_ocs_request(orchestration: dict[str, Any]) -> dict[str, Any]:
    request = _require_mapping(orchestration.get("ocs_cognition_request"), "ocs_cognition_request")
    if request.get("artifact_type") != UBTR_GOVERNED_OCS_COGNITION_REQUEST_V1:
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: invalid OCS cognition request type")
    _verify_artifact_hash(request, "UBTR governed OCS cognition request")
    if request["artifact_hash"] != orchestration["ocs_cognition_request_hash"]:
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: request hash mismatch")
    if request.get("provider_selection_owner") != "OCS":
        raise FailClosedRuntimeError("UBTR OCS handoff failed closed: provider selection owner must be OCS")
    for field in (
        "provider_invoked",
        "provider_selected",
        "worker_invoked",
        "approval_granted",
        "execution_authorized",
        "governance_mutated",
        "replay_mutated",
        "authority_granted",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError("UBTR OCS handoff failed closed: request carries prohibited authority")
    return deepcopy(request)


def _require_context_success(capture: dict[str, Any]) -> None:
    if capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(f"UBTR OCS handoff context assembly failed: {capture.get('failure_reason')}")


def _require_cognition_success(capture: dict[str, Any]) -> None:
    if capture.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError(f"UBTR OCS handoff cognition failed: {capture.get('failure_reason')}")


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
            raise FailClosedRuntimeError("UBTR OCS cognition handoff authority drift")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError("UBTR OCS cognition handoff replay hash mismatch")


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
        raise FailClosedRuntimeError("UBTR OCS cognition handoff replay path already contains artifacts")
    path.mkdir(parents=True, exist_ok=True)


def _persist_failure_if_possible(path: Path, wrapper: dict[str, Any]) -> None:
    try:
        write_json_immutable(path, wrapper)
    except Exception:
        pass
