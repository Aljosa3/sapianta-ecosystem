"""Replay-visible READY_FOR_DISPATCH Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.execution_request_runtime import (
    CREATED_STATUS,
    EXECUTION_REQUEST_ARTIFACT_V1,
    EXECUTION_REQUEST_RETURNED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import APPROVED, PROPOSAL_APPROVAL_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


READY_FOR_DISPATCH_RUNTIME_VERSION = "READY_FOR_DISPATCH_RUNTIME_V1"
READY_FOR_DISPATCH_ARTIFACT_V1 = "READY_FOR_DISPATCH_ARTIFACT_V1"
READY_FOR_DISPATCH = "READY_FOR_DISPATCH"
READY_FOR_DISPATCH_VALIDATED = "READY_FOR_DISPATCH_VALIDATED"
READY_FOR_DISPATCH_RETURNED = "READY_FOR_DISPATCH_RETURNED"

REPLAY_STEPS = ("ready_for_dispatch_validated", "ready_for_dispatch_returned")


def mark_ready_for_dispatch(
    *,
    readiness_id: str,
    execution_request_artifact: dict[str, Any],
    execution_request_replay: dict[str, Any],
    approval_artifact: dict[str, Any],
    validated_at: str,
    replay_reference: str,
    replay_dir: str | Path,
    validated_by: str = "AIGOL",
) -> dict[str, Any]:
    """Record deterministic readiness validation for a CREATED execution request."""

    replay_path = Path(replay_dir)
    _ensure_readiness_replay_available(replay_path)
    request = _validate_execution_request_artifact(execution_request_artifact)
    request_replay = _validate_execution_request_replay(execution_request_replay, request)
    approval = _validate_approval_artifact(approval_artifact, request)
    readiness = _readiness_artifact(
        readiness_id=readiness_id,
        request=request,
        request_replay=request_replay,
        approval=approval,
        validated_by=validated_by,
        validated_at=validated_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], readiness)
    returned = _readiness_returned(readiness)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(readiness, returned)


def reconstruct_ready_for_dispatch_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct READY_FOR_DISPATCH Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("ready for dispatch replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("ready for dispatch replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "ready for dispatch artifact")
        wrappers.append(wrapper)

    readiness = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("readiness_reference") != readiness["readiness_id"]:
        raise FailClosedRuntimeError("ready for dispatch replay reference mismatch")
    if returned.get("readiness_hash") != readiness["artifact_hash"]:
        raise FailClosedRuntimeError("ready for dispatch replay hash mismatch")
    if returned.get("execution_request_reference") != readiness["execution_request_reference"]:
        raise FailClosedRuntimeError("ready for dispatch replay execution request reference mismatch")
    if returned.get("approval_reference") != readiness["approval_reference"]:
        raise FailClosedRuntimeError("ready for dispatch replay approval reference mismatch")
    _validate_readiness_artifact(readiness)
    return {
        "readiness_id": readiness["readiness_id"],
        "execution_request_reference": readiness["execution_request_reference"],
        "execution_request_hash": readiness["execution_request_hash"],
        "proposal_reference": readiness["proposal_reference"],
        "approval_reference": readiness["approval_reference"],
        "validated_by": readiness["validated_by"],
        "validated_at": readiness["validated_at"],
        "status": readiness["readiness_status"],
        "request_type": readiness["request_type"],
        "payload_hash": readiness["payload_hash"],
        "replay_reference": readiness["replay_reference"],
        "provider_authority": False,
        "provider_invoked": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _readiness_artifact(
    *,
    readiness_id: str,
    request: dict[str, Any],
    request_replay: dict[str, Any],
    approval: dict[str, Any],
    validated_by: str,
    validated_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": READY_FOR_DISPATCH_ARTIFACT_V1,
        "readiness_runtime_version": READY_FOR_DISPATCH_RUNTIME_VERSION,
        "readiness_id": _require_string(readiness_id, "readiness_id"),
        "execution_request_reference": request["execution_request_id"],
        "execution_request_hash": request["artifact_hash"],
        "execution_request_replay_hash": request_replay["artifact_hash"],
        "execution_request_status_before": request["status"],
        "proposal_reference": request["proposal_reference"],
        "proposal_hash": request["proposal_hash"],
        "approval_reference": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "validated_by": _normalize_token(validated_by, "validated_by"),
        "validated_at": _require_string(validated_at, "validated_at"),
        "readiness_status": READY_FOR_DISPATCH,
        "request_type": request["request_type"],
        "payload_hash": request["request_payload_hash"],
        "validation_results": (
            "execution_request_valid",
            "execution_request_replay_continuous",
            "approval_matches_execution_request",
            "provider_authority_absent",
            "worker_dispatch_absent",
            "execution_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_readiness_artifact(artifact)
    return artifact


def _readiness_returned(readiness: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(readiness, "ready for dispatch artifact")
    returned = {
        "event_type": READY_FOR_DISPATCH_RETURNED,
        "readiness_reference": readiness["readiness_id"],
        "readiness_hash": readiness["artifact_hash"],
        "execution_request_reference": readiness["execution_request_reference"],
        "execution_request_hash": readiness["execution_request_hash"],
        "proposal_reference": readiness["proposal_reference"],
        "approval_reference": readiness["approval_reference"],
        "readiness_status": readiness["readiness_status"],
        "replay_reference": readiness["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
        "reconstruction_metadata": {
            "readiness_reconstructable": True,
            "execution_request_reconstructable": True,
            "approval_reconstructable": True,
            "worker_assigned": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(readiness: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "ready_for_dispatch_artifact": deepcopy(readiness),
        "ready_for_dispatch_replay": deepcopy(returned),
    }
    capture["ready_for_dispatch_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_readiness_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("ready for dispatch replay step ordering mismatch")
    _verify_artifact_hash(artifact, "ready for dispatch artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": READY_FOR_DISPATCH_VALIDATED if index == 0 else READY_FOR_DISPATCH_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_execution_request_artifact(request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution request is required")
    _verify_artifact_hash(request, "execution request artifact")
    if request.get("artifact_type") != EXECUTION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid execution request artifact")
    if request.get("status") != CREATED_STATUS:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid execution request status")
    if request.get("request_payload_hash") != replay_hash(request.get("request_payload")):
        raise FailClosedRuntimeError("ready for dispatch failed closed: request payload hash mismatch")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution request replay visibility missing")
    if request.get("provider_authority") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider authority introduced")
    if request.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider invocation detected")
    if request.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker dispatch detected")
    if request.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker invocation detected")
    if request.get("execution_performed") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution performed")
    if request.get("approval_created") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval introduced")
    if request.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: automatic authorization introduced")
    _require_string(request.get("execution_request_id"), "execution_request_id")
    _require_string(request.get("proposal_reference"), "proposal_reference")
    _require_string(request.get("proposal_hash"), "proposal_hash")
    _require_string(request.get("approval_reference"), "approval_reference")
    _require_string(request.get("approval_hash"), "approval_hash")
    _require_string(request.get("request_type"), "request_type")
    _require_string(request.get("request_payload_hash"), "request_payload_hash")
    _require_string(request.get("replay_reference"), "replay_reference")
    return deepcopy(request)


def _validate_execution_request_replay(replay: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution request replay is required")
    _verify_artifact_hash(replay, "execution request replay artifact")
    if replay.get("event_type") != EXECUTION_REQUEST_RETURNED:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid execution request replay event")
    if replay.get("execution_request_reference") != request["execution_request_id"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution request replay reference mismatch")
    if replay.get("execution_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution request replay hash mismatch")
    if replay.get("proposal_reference") != request["proposal_reference"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: proposal replay reference mismatch")
    if replay.get("proposal_hash") != request["proposal_hash"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: proposal replay hash mismatch")
    if replay.get("approval_reference") != request["approval_reference"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval replay reference mismatch")
    if replay.get("approval_hash") != request["approval_hash"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval replay hash mismatch")
    if replay.get("status") != CREATED_STATUS:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid execution request replay status")
    if replay.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker dispatch detected")
    if replay.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker invocation detected")
    if replay.get("execution_performed") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution performed")
    if replay.get("provider_authority") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider authority introduced")
    return deepcopy(replay)


def _validate_approval_artifact(approval: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval is required")
    _verify_artifact_hash(approval, "proposal approval artifact")
    if approval.get("artifact_type") != PROPOSAL_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid approval artifact")
    if approval.get("approval_status") != APPROVED:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval mismatch")
    if approval.get("approval_id") != request["approval_reference"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval reference mismatch")
    if approval.get("artifact_hash") != request["approval_hash"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval hash mismatch")
    if approval.get("proposal_id") != request["proposal_reference"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: proposal reference mismatch")
    if approval.get("proposal_hash") != request["proposal_hash"]:
        raise FailClosedRuntimeError("ready for dispatch failed closed: proposal hash mismatch")
    if approval.get("provider_approval") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider approval introduced")
    if approval.get("worker_approval") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker approval introduced")
    if approval.get("automatic_approval") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: automatic approval introduced")
    if approval.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider invocation detected")
    if approval.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker invocation detected")
    return deepcopy(approval)


def _validate_readiness_artifact(readiness: dict[str, Any]) -> None:
    if readiness.get("artifact_type") != READY_FOR_DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid readiness artifact")
    if readiness.get("validated_by") != "AIGOL":
        raise FailClosedRuntimeError("ready for dispatch failed closed: validated_by must be AIGOL")
    if readiness.get("execution_request_status_before") != CREATED_STATUS:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid execution request status")
    if readiness.get("readiness_status") != READY_FOR_DISPATCH:
        raise FailClosedRuntimeError("ready for dispatch failed closed: invalid readiness status")
    if readiness.get("replay_visible") is not True:
        raise FailClosedRuntimeError("ready for dispatch failed closed: replay visibility missing")
    if readiness.get("provider_authority") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider authority introduced")
    if readiness.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: provider invocation detected")
    if readiness.get("worker_assigned") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker assignment detected")
    if readiness.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker dispatch detected")
    if readiness.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: worker invocation detected")
    if readiness.get("execution_performed") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: execution performed")
    if readiness.get("approval_created") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: approval introduced")
    if readiness.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("ready for dispatch failed closed: automatic authorization introduced")
    _require_string(readiness.get("readiness_id"), "readiness_id")
    _require_string(readiness.get("execution_request_reference"), "execution_request_reference")
    _require_string(readiness.get("execution_request_hash"), "execution_request_hash")
    _require_string(readiness.get("execution_request_replay_hash"), "execution_request_replay_hash")
    _require_string(readiness.get("proposal_reference"), "proposal_reference")
    _require_string(readiness.get("approval_reference"), "approval_reference")
    _require_string(readiness.get("validated_at"), "validated_at")
    _require_string(readiness.get("request_type"), "request_type")
    _require_string(readiness.get("payload_hash"), "payload_hash")
    _require_string(readiness.get("replay_reference"), "replay_reference")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("ready for dispatch replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("ready for dispatch replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
