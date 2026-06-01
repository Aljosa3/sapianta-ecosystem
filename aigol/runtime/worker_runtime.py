"""Replay-visible Worker Registration and Assignment Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ready_for_dispatch_runtime import (
    READY_FOR_DISPATCH,
    READY_FOR_DISPATCH_ARTIFACT_V1,
    READY_FOR_DISPATCH_RETURNED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


WORKER_RUNTIME_VERSION = "WORKER_RUNTIME_V1"
WORKER_ARTIFACT_V1 = "WORKER_ARTIFACT_V1"
WORKER_ASSIGNMENT_ARTIFACT_V1 = "WORKER_ASSIGNMENT_ARTIFACT_V1"

AVAILABLE = "AVAILABLE"
ASSIGNED = "ASSIGNED"
UNAVAILABLE = "UNAVAILABLE"

WORKER_REGISTERED = "WORKER_REGISTERED"
WORKER_REGISTRATION_RETURNED = "WORKER_REGISTRATION_RETURNED"
WORKER_ASSIGNED = "WORKER_ASSIGNED"
WORKER_ASSIGNMENT_RETURNED = "WORKER_ASSIGNMENT_RETURNED"

REGISTRATION_REPLAY_STEPS = ("worker_registered", "worker_registration_returned")
ASSIGNMENT_REPLAY_STEPS = ("worker_assigned", "worker_assignment_returned")
VALID_WORKER_STATES = frozenset({AVAILABLE, ASSIGNED, UNAVAILABLE})
VALID_TRUST_BOUNDARIES = frozenset({"LOCAL_BOUNDED_WORKER", "SANDBOXED_WORKER"})


def register_worker(
    *,
    worker_id: str,
    worker_type: str,
    worker_version: str,
    declared_capabilities: list[str],
    supported_request_types: list[str],
    trust_boundary: str,
    created_at: str,
    replay_reference: str,
    replay_dir: str | Path,
    state: str = AVAILABLE,
) -> dict[str, Any]:
    """Register a replay-visible non-authoritative worker identity."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path, REGISTRATION_REPLAY_STEPS)
    worker = _worker_artifact(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_version=worker_version,
        declared_capabilities=declared_capabilities,
        supported_request_types=supported_request_types,
        trust_boundary=trust_boundary,
        created_at=created_at,
        replay_reference=replay_reference,
        state=state,
    )
    _persist_step(replay_path, 0, REGISTRATION_REPLAY_STEPS, WORKER_REGISTERED, worker)
    returned = _worker_registration_returned(worker)
    _persist_step(replay_path, 1, REGISTRATION_REPLAY_STEPS, WORKER_REGISTRATION_RETURNED, returned)
    return _registration_capture(worker, returned)


def assign_worker(
    *,
    worker_assignment_id: str,
    worker_artifact: dict[str, Any],
    readiness_artifact: dict[str, Any],
    readiness_replay: dict[str, Any],
    assigned_by: str,
    assigned_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Assign an AVAILABLE worker to a READY_FOR_DISPATCH request without dispatching work."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path, ASSIGNMENT_REPLAY_STEPS)
    worker = _validate_worker_artifact(worker_artifact)
    readiness = _validate_readiness_artifact(readiness_artifact)
    readiness_returned = _validate_readiness_replay(readiness_replay, readiness)
    assignment = _worker_assignment_artifact(
        worker_assignment_id=worker_assignment_id,
        worker=worker,
        readiness=readiness,
        readiness_replay=readiness_returned,
        assigned_by=assigned_by,
        assigned_at=assigned_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, ASSIGNMENT_REPLAY_STEPS, WORKER_ASSIGNED, assignment)
    returned = _worker_assignment_returned(assignment)
    _persist_step(replay_path, 1, ASSIGNMENT_REPLAY_STEPS, WORKER_ASSIGNMENT_RETURNED, returned)
    return _assignment_capture(assignment, returned)


def reconstruct_worker_registration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker Runtime registration replay deterministically."""

    wrappers = _load_ordered_wrappers(Path(replay_dir), REGISTRATION_REPLAY_STEPS, "worker registration")
    worker = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("worker_reference") != worker["worker_id"]:
        raise FailClosedRuntimeError("worker registration replay reference mismatch")
    if returned.get("worker_hash") != worker["artifact_hash"]:
        raise FailClosedRuntimeError("worker registration replay hash mismatch")
    _validate_worker_artifact(worker, require_available=False)
    return {
        "worker_id": worker["worker_id"],
        "worker_type": worker["worker_type"],
        "worker_version": worker["worker_version"],
        "declared_capabilities": tuple(worker["declared_capabilities"]),
        "supported_request_types": tuple(worker["supported_request_types"]),
        "trust_boundary": worker["trust_boundary"],
        "state": worker["state"],
        "created_at": worker["created_at"],
        "replay_reference": worker["replay_reference"],
        "governance_authority": False,
        "provider_authority": False,
        "self_authorization": False,
        "worker_dispatched": False,
        "execution_performed": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def reconstruct_worker_assignment_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker Runtime assignment replay deterministically."""

    wrappers = _load_ordered_wrappers(Path(replay_dir), ASSIGNMENT_REPLAY_STEPS, "worker assignment")
    assignment = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("worker_assignment_reference") != assignment["worker_assignment_id"]:
        raise FailClosedRuntimeError("worker assignment replay reference mismatch")
    if returned.get("worker_assignment_hash") != assignment["artifact_hash"]:
        raise FailClosedRuntimeError("worker assignment replay hash mismatch")
    if returned.get("worker_reference") != assignment["worker_id"]:
        raise FailClosedRuntimeError("worker assignment replay worker reference mismatch")
    if returned.get("readiness_reference") != assignment["readiness_reference"]:
        raise FailClosedRuntimeError("worker assignment replay readiness reference mismatch")
    _validate_worker_assignment_artifact(assignment)
    return {
        "worker_assignment_id": assignment["worker_assignment_id"],
        "worker_id": assignment["worker_id"],
        "worker_type": assignment["worker_type"],
        "capability_id": assignment["capability_id"],
        "readiness_reference": assignment["readiness_reference"],
        "execution_request_reference": assignment["execution_request_reference"],
        "assigned_by": assignment["assigned_by"],
        "assigned_at": assignment["assigned_at"],
        "assignment_status": assignment["assignment_status"],
        "worker_state_after": assignment["worker_state_after"],
        "replay_reference": assignment["replay_reference"],
        "provider_authority": False,
        "worker_self_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _worker_artifact(
    *,
    worker_id: str,
    worker_type: str,
    worker_version: str,
    declared_capabilities: list[str],
    supported_request_types: list[str],
    trust_boundary: str,
    created_at: str,
    replay_reference: str,
    state: str,
) -> dict[str, Any]:
    normalized_capabilities = _normalize_string_list(declared_capabilities, "declared_capabilities")
    normalized_request_types = _normalize_string_list(supported_request_types, "supported_request_types")
    artifact = {
        "artifact_type": WORKER_ARTIFACT_V1,
        "worker_runtime_version": WORKER_RUNTIME_VERSION,
        "worker_id": _require_string(worker_id, "worker_id"),
        "worker_type": _normalize_token(worker_type, "worker_type"),
        "worker_version": _require_string(worker_version, "worker_version"),
        "declared_capabilities": normalized_capabilities,
        "supported_request_types": normalized_request_types,
        "capability_id": normalized_capabilities[0],
        "trust_boundary": _normalize_token(trust_boundary, "trust_boundary"),
        "state": _normalize_token(state, "state"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "governance_authority": False,
        "approval_authority": False,
        "proposal_authority": False,
        "provider_authority": False,
        "self_authorization": False,
        "replay_mutation_authority": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_worker_artifact(artifact, require_available=False)
    return artifact


def _worker_registration_returned(worker: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(worker, "worker artifact")
    returned = {
        "event_type": WORKER_REGISTRATION_RETURNED,
        "worker_reference": worker["worker_id"],
        "worker_hash": worker["artifact_hash"],
        "worker_type": worker["worker_type"],
        "state": worker["state"],
        "replay_reference": worker["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "self_authorization": False,
        "worker_dispatched": False,
        "execution_performed": False,
        "reconstruction_metadata": {
            "worker_reconstructable": True,
            "assignment_created": False,
            "worker_dispatched": False,
            "execution_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _worker_assignment_artifact(
    *,
    worker_assignment_id: str,
    worker: dict[str, Any],
    readiness: dict[str, Any],
    readiness_replay: dict[str, Any],
    assigned_by: str,
    assigned_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    if readiness["request_type"] not in worker["supported_request_types"]:
        raise FailClosedRuntimeError("worker runtime failed closed: unsupported request type")
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_ARTIFACT_V1,
        "worker_runtime_version": WORKER_RUNTIME_VERSION,
        "worker_assignment_id": _require_string(worker_assignment_id, "worker_assignment_id"),
        "worker_id": worker["worker_id"],
        "worker_hash": worker["artifact_hash"],
        "worker_type": worker["worker_type"],
        "capability_id": worker["capability_id"],
        "readiness_reference": readiness["readiness_id"],
        "readiness_hash": readiness["artifact_hash"],
        "readiness_replay_hash": readiness_replay["artifact_hash"],
        "execution_request_reference": readiness["execution_request_reference"],
        "execution_request_hash": readiness["execution_request_hash"],
        "assigned_by": _normalize_token(assigned_by, "assigned_by"),
        "assigned_at": _require_string(assigned_at, "assigned_at"),
        "assignment_status": ASSIGNED,
        "worker_state_before": worker["state"],
        "worker_state_after": ASSIGNED,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_worker_assignment_artifact(artifact)
    return artifact


def _worker_assignment_returned(assignment: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(assignment, "worker assignment artifact")
    returned = {
        "event_type": WORKER_ASSIGNMENT_RETURNED,
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_reference": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "readiness_reference": assignment["readiness_reference"],
        "readiness_hash": assignment["readiness_hash"],
        "execution_request_reference": assignment["execution_request_reference"],
        "assignment_status": assignment["assignment_status"],
        "replay_reference": assignment["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
        "reconstruction_metadata": {
            "worker_reconstructable": True,
            "assignment_reconstructable": True,
            "readiness_reconstructable": True,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "completion_recorded": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _registration_capture(worker: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "worker_artifact": deepcopy(worker),
        "worker_registration_replay": deepcopy(returned),
    }
    capture["worker_registration_capture_hash"] = replay_hash(capture)
    return capture


def _assignment_capture(assignment: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "worker_assignment_artifact": deepcopy(assignment),
        "worker_assignment_replay": deepcopy(returned),
    }
    capture["worker_assignment_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path, steps: tuple[str, str]) -> None:
    for index, step in enumerate(steps):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(
    replay_dir: Path,
    index: int,
    steps: tuple[str, str],
    event_type: str,
    artifact: dict[str, Any],
) -> None:
    if index < 0 or index >= len(steps):
        raise FailClosedRuntimeError("worker runtime replay step ordering mismatch")
    _verify_artifact_hash(artifact, "worker runtime artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": steps[index],
        "artifact": deepcopy(artifact),
        "event_type": event_type,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{steps[index]}.json", wrapper)


def _load_ordered_wrappers(replay_path: Path, steps: tuple[str, str], label: str) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError(f"{label} replay ordering mismatch")
        _verify_wrapper_hash(wrapper, label)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(f"{label} replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"{label} artifact")
        wrappers.append(wrapper)
    return wrappers


def _validate_worker_artifact(worker: dict[str, Any], *, require_available: bool = True) -> dict[str, Any]:
    if not isinstance(worker, dict):
        raise FailClosedRuntimeError("worker runtime failed closed: worker is required")
    _verify_artifact_hash(worker, "worker artifact")
    if worker.get("artifact_type") != WORKER_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid worker artifact")
    if worker.get("state") not in VALID_WORKER_STATES:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid worker state")
    if require_available and worker.get("state") != AVAILABLE:
        raise FailClosedRuntimeError("worker runtime failed closed: worker unavailable")
    if worker.get("trust_boundary") not in VALID_TRUST_BOUNDARIES:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid trust boundary")
    if worker.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker runtime failed closed: replay visibility missing")
    if worker.get("governance_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: governance authority introduced")
    if worker.get("approval_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: approval authority introduced")
    if worker.get("proposal_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: proposal authority introduced")
    if worker.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: provider authority introduced")
    if worker.get("self_authorization") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: self authorization introduced")
    if worker.get("replay_mutation_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: replay mutation authority introduced")
    if worker.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker dispatch detected")
    if worker.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker invocation detected")
    if worker.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: execution performed")
    if worker.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: completion recorded")
    _require_string(worker.get("worker_id"), "worker_id")
    _require_string(worker.get("worker_type"), "worker_type")
    _require_string(worker.get("worker_version"), "worker_version")
    _require_string(worker.get("capability_id"), "capability_id")
    _require_string(worker.get("created_at"), "created_at")
    _require_string(worker.get("replay_reference"), "replay_reference")
    if not isinstance(worker.get("declared_capabilities"), list) or not worker["declared_capabilities"]:
        raise FailClosedRuntimeError("worker runtime failed closed: declared_capabilities are required")
    if not isinstance(worker.get("supported_request_types"), list) or not worker["supported_request_types"]:
        raise FailClosedRuntimeError("worker runtime failed closed: supported_request_types are required")
    return deepcopy(worker)


def _validate_readiness_artifact(readiness: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(readiness, dict):
        raise FailClosedRuntimeError("worker runtime failed closed: readiness is required")
    _verify_artifact_hash(readiness, "ready for dispatch artifact")
    if readiness.get("artifact_type") != READY_FOR_DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid readiness artifact")
    if readiness.get("readiness_status") != READY_FOR_DISPATCH:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid readiness status")
    if readiness.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker runtime failed closed: readiness replay visibility missing")
    if readiness.get("worker_assigned") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: duplicate assignment marker")
    if readiness.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker dispatch detected")
    if readiness.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker invocation detected")
    if readiness.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: execution performed")
    if readiness.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: provider authority introduced")
    _require_string(readiness.get("readiness_id"), "readiness_id")
    _require_string(readiness.get("execution_request_reference"), "execution_request_reference")
    _require_string(readiness.get("execution_request_hash"), "execution_request_hash")
    _require_string(readiness.get("request_type"), "request_type")
    return deepcopy(readiness)


def _validate_readiness_replay(replay: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("worker runtime failed closed: readiness replay is required")
    _verify_artifact_hash(replay, "ready for dispatch replay artifact")
    if replay.get("event_type") != READY_FOR_DISPATCH_RETURNED:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid readiness replay event")
    if replay.get("readiness_reference") != readiness["readiness_id"]:
        raise FailClosedRuntimeError("worker runtime failed closed: readiness replay reference mismatch")
    if replay.get("readiness_hash") != readiness["artifact_hash"]:
        raise FailClosedRuntimeError("worker runtime failed closed: readiness replay hash mismatch")
    if replay.get("execution_request_reference") != readiness["execution_request_reference"]:
        raise FailClosedRuntimeError("worker runtime failed closed: execution request reference mismatch")
    if replay.get("worker_assigned") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: duplicate assignment marker")
    if replay.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker dispatch detected")
    if replay.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker invocation detected")
    if replay.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: execution performed")
    return deepcopy(replay)


def _validate_worker_assignment_artifact(assignment: dict[str, Any]) -> None:
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid worker assignment artifact")
    if assignment.get("assigned_by") != "AIGOL":
        raise FailClosedRuntimeError("worker runtime failed closed: assigned_by must be AIGOL")
    if assignment.get("assignment_status") != ASSIGNED:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid assignment status")
    if assignment.get("worker_state_before") != AVAILABLE:
        raise FailClosedRuntimeError("worker runtime failed closed: worker unavailable")
    if assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("worker runtime failed closed: invalid worker assignment state")
    if assignment.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker runtime failed closed: replay visibility missing")
    if assignment.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: provider authority introduced")
    if assignment.get("worker_self_assigned") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker self assignment introduced")
    if assignment.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker dispatch detected")
    if assignment.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: worker invocation detected")
    if assignment.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: execution performed")
    if assignment.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: completion recorded")
    if assignment.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("worker runtime failed closed: automatic authorization introduced")
    _require_string(assignment.get("worker_assignment_id"), "worker_assignment_id")
    _require_string(assignment.get("worker_id"), "worker_id")
    _require_string(assignment.get("worker_hash"), "worker_hash")
    _require_string(assignment.get("worker_type"), "worker_type")
    _require_string(assignment.get("capability_id"), "capability_id")
    _require_string(assignment.get("readiness_reference"), "readiness_reference")
    _require_string(assignment.get("readiness_hash"), "readiness_hash")
    _require_string(assignment.get("readiness_replay_hash"), "readiness_replay_hash")
    _require_string(assignment.get("execution_request_reference"), "execution_request_reference")
    _require_string(assignment.get("execution_request_hash"), "execution_request_hash")
    _require_string(assignment.get("assigned_at"), "assigned_at")
    _require_string(assignment.get("replay_reference"), "replay_reference")


def _normalize_string_list(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise FailClosedRuntimeError(f"{field_name} are required")
    normalized = [_normalize_token(value, field_name) for value in values]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(f"{field_name} must be unique")
    return normalized


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any], label: str) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError(f"{label} replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
