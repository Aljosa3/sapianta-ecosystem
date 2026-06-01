"""Replay-visible Dispatch Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ready_for_dispatch_runtime import READY_FOR_DISPATCH, READY_FOR_DISPATCH_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_runtime import (
    ASSIGNED,
    AVAILABLE,
    WORKER_ASSIGNMENT_ARTIFACT_V1,
    WORKER_ASSIGNMENT_RETURNED,
)


DISPATCH_RUNTIME_VERSION = "DISPATCH_RUNTIME_V1"
DISPATCH_ARTIFACT_V1 = "DISPATCH_ARTIFACT_V1"
DISPATCHED = "DISPATCHED"
DISPATCH_VALIDATED = "DISPATCH_VALIDATED"
DISPATCH_RETURNED = "DISPATCH_RETURNED"

REPLAY_STEPS = ("dispatch_validated", "dispatch_returned")


def dispatch_worker(
    *,
    dispatch_id: str,
    worker_assignment_artifact: dict[str, Any],
    worker_assignment_replay: dict[str, Any],
    readiness_artifact: dict[str, Any],
    canonical_chain_id: str,
    dispatched_by: str,
    dispatched_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record deterministic dispatch from a valid worker assignment without invocation."""

    replay_path = Path(replay_dir)
    _ensure_dispatch_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    assignment = _validate_worker_assignment_artifact(worker_assignment_artifact, chain_id)
    assignment_replay = _validate_worker_assignment_replay(worker_assignment_replay, assignment)
    readiness = _validate_readiness_artifact(readiness_artifact, assignment, chain_id)
    dispatch = _dispatch_artifact(
        dispatch_id=dispatch_id,
        assignment=assignment,
        assignment_replay=assignment_replay,
        readiness=readiness,
        canonical_chain_id=chain_id,
        dispatched_by=dispatched_by,
        dispatched_at=dispatched_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], dispatch)
    returned = _dispatch_returned(dispatch)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(dispatch, returned)


def reconstruct_dispatch_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Dispatch Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("dispatch replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("dispatch replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "dispatch artifact")
        wrappers.append(wrapper)

    dispatch = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("dispatch_reference") != dispatch["dispatch_id"]:
        raise FailClosedRuntimeError("dispatch replay reference mismatch")
    if returned.get("dispatch_hash") != dispatch["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch replay hash mismatch")
    if returned.get("worker_assignment_reference") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("dispatch replay worker assignment reference mismatch")
    if returned.get("canonical_chain_id") != dispatch["canonical_chain_id"]:
        raise FailClosedRuntimeError("dispatch replay chain mismatch")
    _validate_dispatch_artifact(dispatch)
    return {
        "dispatch_id": dispatch["dispatch_id"],
        "canonical_chain_id": dispatch["canonical_chain_id"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_reference": dispatch["worker_reference"],
        "readiness_reference": dispatch["readiness_reference"],
        "execution_request_reference": dispatch["execution_request_reference"],
        "dispatched_by": dispatch["dispatched_by"],
        "dispatched_at": dispatch["dispatched_at"],
        "dispatch_status": dispatch["dispatch_status"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "replay_reference": dispatch["replay_reference"],
        "provider_authority": False,
        "worker_self_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _dispatch_artifact(
    *,
    dispatch_id: str,
    assignment: dict[str, Any],
    assignment_replay: dict[str, Any],
    readiness: dict[str, Any],
    canonical_chain_id: str,
    dispatched_by: str,
    dispatched_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DISPATCH_ARTIFACT_V1,
        "dispatch_runtime_version": DISPATCH_RUNTIME_VERSION,
        "dispatch_id": _require_string(dispatch_id, "dispatch_id"),
        "canonical_chain_id": canonical_chain_id,
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_assignment_replay_hash": assignment_replay["artifact_hash"],
        "worker_reference": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "readiness_reference": assignment["readiness_reference"],
        "readiness_hash": assignment["readiness_hash"],
        "execution_request_reference": assignment["execution_request_reference"],
        "execution_request_hash": assignment["execution_request_hash"],
        "dispatched_by": _normalize_token(dispatched_by, "dispatched_by"),
        "dispatched_at": _require_string(dispatched_at, "dispatched_at"),
        "dispatch_status": DISPATCHED,
        "assignment_status_before": assignment["assignment_status"],
        "worker_state_before_dispatch": assignment["worker_state_after"],
        "request_type": readiness["request_type"],
        "capability_id": assignment["capability_id"],
        "validation_results": (
            "worker_assignment_valid",
            "worker_assignment_replay_continuous",
            "readiness_evidence_valid",
            "canonical_chain_continuous",
            "provider_authority_absent",
            "worker_invocation_absent",
            "execution_absent",
            "completion_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_dispatch_artifact(artifact)
    return artifact


def _dispatch_returned(dispatch: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(dispatch, "dispatch artifact")
    returned = {
        "event_type": DISPATCH_RETURNED,
        "dispatch_reference": dispatch["dispatch_id"],
        "dispatch_hash": dispatch["artifact_hash"],
        "canonical_chain_id": dispatch["canonical_chain_id"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_reference": dispatch["worker_reference"],
        "worker_hash": dispatch["worker_hash"],
        "readiness_reference": dispatch["readiness_reference"],
        "readiness_hash": dispatch["readiness_hash"],
        "execution_request_reference": dispatch["execution_request_reference"],
        "dispatch_status": dispatch["dispatch_status"],
        "replay_reference": dispatch["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "reconstruction_metadata": {
            "dispatch_reconstructable": True,
            "worker_assignment_reconstructable": True,
            "readiness_reconstructable": True,
            "canonical_chain_continuous": True,
            "worker_invoked": False,
            "execution_performed": False,
            "completion_recorded": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(dispatch: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "dispatch_artifact": deepcopy(dispatch),
        "dispatch_replay": deepcopy(returned),
    }
    capture["dispatch_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_dispatch_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("dispatch replay step ordering mismatch")
    _verify_artifact_hash(artifact, "dispatch artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": DISPATCH_VALIDATED if index == 0 else DISPATCH_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_worker_assignment_artifact(assignment: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(assignment, dict):
        raise FailClosedRuntimeError("dispatch failed closed: worker assignment is required")
    _verify_artifact_hash(assignment, "worker assignment artifact")
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch failed closed: invalid assignment artifact")
    if assignment.get("assignment_status") != ASSIGNED:
        raise FailClosedRuntimeError("dispatch failed closed: invalid assignment status")
    if assignment.get("assigned_by") != "AIGOL":
        raise FailClosedRuntimeError("dispatch failed closed: assignment must be AiGOL-created")
    if assignment.get("worker_state_before") != AVAILABLE:
        raise FailClosedRuntimeError("dispatch failed closed: worker unavailable")
    if assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("dispatch failed closed: worker unavailable")
    if assignment.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("dispatch failed closed: chain mismatch")
    if assignment.get("replay_visible") is not True:
        raise FailClosedRuntimeError("dispatch failed closed: assignment replay visibility missing")
    if assignment.get("provider_authority") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: provider authority introduced")
    if assignment.get("worker_self_assigned") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker self assignment introduced")
    if assignment.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: duplicate dispatch marker")
    if assignment.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker invocation detected")
    if assignment.get("execution_performed") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: execution performed")
    if assignment.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: completion recorded")
    if assignment.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: automatic authorization introduced")
    _require_string(assignment.get("worker_assignment_id"), "worker_assignment_id")
    _require_string(assignment.get("worker_id"), "worker_id")
    _require_string(assignment.get("worker_hash"), "worker_hash")
    _require_string(assignment.get("readiness_reference"), "readiness_reference")
    _require_string(assignment.get("readiness_hash"), "readiness_hash")
    _require_string(assignment.get("execution_request_reference"), "execution_request_reference")
    _require_string(assignment.get("execution_request_hash"), "execution_request_hash")
    _require_string(assignment.get("capability_id"), "capability_id")
    return deepcopy(assignment)


def _validate_worker_assignment_replay(replay: dict[str, Any], assignment: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("dispatch failed closed: worker assignment replay is required")
    _verify_artifact_hash(replay, "worker assignment replay artifact")
    if replay.get("event_type") != WORKER_ASSIGNMENT_RETURNED:
        raise FailClosedRuntimeError("dispatch failed closed: invalid assignment replay event")
    if replay.get("worker_assignment_reference") != assignment["worker_assignment_id"]:
        raise FailClosedRuntimeError("dispatch failed closed: assignment replay reference mismatch")
    if replay.get("worker_assignment_hash") != assignment["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch failed closed: assignment replay hash mismatch")
    if replay.get("worker_reference") != assignment["worker_id"]:
        raise FailClosedRuntimeError("dispatch failed closed: worker reference mismatch")
    if replay.get("readiness_reference") != assignment["readiness_reference"]:
        raise FailClosedRuntimeError("dispatch failed closed: readiness reference mismatch")
    if replay.get("canonical_chain_id") != assignment["canonical_chain_id"]:
        raise FailClosedRuntimeError("dispatch failed closed: chain mismatch")
    if replay.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: duplicate dispatch marker")
    if replay.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker invocation detected")
    if replay.get("execution_performed") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: execution performed")
    if replay.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: completion recorded")
    return deepcopy(replay)


def _validate_readiness_artifact(
    readiness: dict[str, Any],
    assignment: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(readiness, dict):
        raise FailClosedRuntimeError("dispatch failed closed: readiness evidence is required")
    _verify_artifact_hash(readiness, "ready for dispatch artifact")
    if readiness.get("artifact_type") != READY_FOR_DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch failed closed: invalid readiness artifact")
    if readiness.get("readiness_status") != READY_FOR_DISPATCH:
        raise FailClosedRuntimeError("dispatch failed closed: invalid readiness status")
    if readiness.get("readiness_id") != assignment["readiness_reference"]:
        raise FailClosedRuntimeError("dispatch failed closed: readiness reference mismatch")
    if readiness.get("artifact_hash") != assignment["readiness_hash"]:
        raise FailClosedRuntimeError("dispatch failed closed: readiness hash mismatch")
    if readiness.get("execution_request_reference") != assignment["execution_request_reference"]:
        raise FailClosedRuntimeError("dispatch failed closed: execution request reference mismatch")
    if "canonical_chain_id" in readiness and readiness.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("dispatch failed closed: chain mismatch")
    if readiness.get("worker_assigned") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: duplicate assignment marker")
    if readiness.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: duplicate dispatch marker")
    if readiness.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker invocation detected")
    if readiness.get("execution_performed") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: execution performed")
    if readiness.get("provider_authority") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: provider authority introduced")
    _require_string(readiness.get("request_type"), "request_type")
    return deepcopy(readiness)


def _validate_dispatch_artifact(dispatch: dict[str, Any]) -> None:
    if dispatch.get("artifact_type") != DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch failed closed: invalid dispatch artifact")
    if dispatch.get("dispatched_by") != "AIGOL":
        raise FailClosedRuntimeError("dispatch failed closed: dispatched_by must be AIGOL")
    if dispatch.get("dispatch_status") != DISPATCHED:
        raise FailClosedRuntimeError("dispatch failed closed: invalid dispatch status")
    if dispatch.get("assignment_status_before") != ASSIGNED:
        raise FailClosedRuntimeError("dispatch failed closed: invalid assignment status")
    if dispatch.get("worker_state_before_dispatch") != ASSIGNED:
        raise FailClosedRuntimeError("dispatch failed closed: worker unavailable")
    if dispatch.get("replay_visible") is not True:
        raise FailClosedRuntimeError("dispatch failed closed: replay visibility missing")
    if dispatch.get("provider_authority") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: provider authority introduced")
    if dispatch.get("worker_self_dispatched") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker self dispatch introduced")
    if dispatch.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: worker invocation detected")
    if dispatch.get("execution_performed") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: execution performed")
    if dispatch.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: completion recorded")
    if dispatch.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("dispatch failed closed: automatic authorization introduced")
    _require_string(dispatch.get("dispatch_id"), "dispatch_id")
    _require_string(dispatch.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(dispatch.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(dispatch.get("worker_assignment_hash"), "worker_assignment_hash")
    _require_string(dispatch.get("worker_reference"), "worker_reference")
    _require_string(dispatch.get("worker_hash"), "worker_hash")
    _require_string(dispatch.get("readiness_reference"), "readiness_reference")
    _require_string(dispatch.get("readiness_hash"), "readiness_hash")
    _require_string(dispatch.get("execution_request_reference"), "execution_request_reference")
    _require_string(dispatch.get("execution_request_hash"), "execution_request_hash")
    _require_string(dispatch.get("dispatched_at"), "dispatched_at")
    _require_string(dispatch.get("request_type"), "request_type")
    _require_string(dispatch.get("capability_id"), "capability_id")
    _require_string(dispatch.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("dispatch replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("dispatch replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
