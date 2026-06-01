"""Replay-visible Worker Invocation Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.dispatch_runtime import DISPATCH_ARTIFACT_V1, DISPATCH_RETURNED, DISPATCHED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_runtime import ASSIGNED, AVAILABLE, WORKER_ASSIGNMENT_ARTIFACT_V1


WORKER_INVOCATION_RUNTIME_VERSION = "WORKER_INVOCATION_RUNTIME_V1"
WORKER_INVOCATION_ARTIFACT_V1 = "WORKER_INVOCATION_ARTIFACT_V1"
INVOKED = "INVOKED"
WORKER_INVOCATION_VALIDATED = "WORKER_INVOCATION_VALIDATED"
WORKER_INVOCATION_RETURNED = "WORKER_INVOCATION_RETURNED"

REPLAY_STEPS = ("worker_invocation_validated", "worker_invocation_returned")
FORBIDDEN_INVOCATION_PARAMETER_FIELDS = frozenset(
    {
        "approval_decision",
        "authorization_decision",
        "provider_command",
        "worker_command",
        "execute_now",
        "completion_status",
        "result_payload",
        "credentials",
        "api_key",
        "secret",
    }
)


def invoke_worker(
    *,
    worker_invocation_id: str,
    dispatch_artifact: dict[str, Any],
    dispatch_replay: dict[str, Any],
    worker_assignment_artifact: dict[str, Any],
    canonical_chain_id: str,
    invocation_parameters: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record deterministic worker invocation without execution or completion."""

    replay_path = Path(replay_dir)
    _ensure_invocation_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    dispatch = _validate_dispatch_artifact(dispatch_artifact, chain_id)
    returned = _validate_dispatch_replay(dispatch_replay, dispatch)
    assignment = _validate_worker_assignment_artifact(worker_assignment_artifact, dispatch, chain_id)
    parameters = _validate_invocation_parameters(invocation_parameters, dispatch)
    invocation = _invocation_artifact(
        worker_invocation_id=worker_invocation_id,
        dispatch=dispatch,
        dispatch_replay=returned,
        assignment=assignment,
        canonical_chain_id=chain_id,
        invocation_parameters=parameters,
        invoked_by=invoked_by,
        invoked_at=invoked_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], invocation)
    invocation_returned = _invocation_returned(invocation)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], invocation_returned)
    return _capture(invocation, invocation_returned)


def reconstruct_worker_invocation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker Invocation Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker invocation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker invocation artifact")
        wrappers.append(wrapper)

    invocation = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker invocation replay reference mismatch")
    if returned.get("worker_invocation_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation replay hash mismatch")
    if returned.get("dispatch_reference") != invocation["dispatch_reference"]:
        raise FailClosedRuntimeError("worker invocation replay dispatch reference mismatch")
    if returned.get("canonical_chain_id") != invocation["canonical_chain_id"]:
        raise FailClosedRuntimeError("worker invocation replay chain mismatch")
    _validate_invocation_artifact(invocation)
    return {
        "worker_invocation_id": invocation["worker_invocation_id"],
        "canonical_chain_id": invocation["canonical_chain_id"],
        "dispatch_reference": invocation["dispatch_reference"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_reference": invocation["worker_reference"],
        "readiness_reference": invocation["readiness_reference"],
        "execution_request_reference": invocation["execution_request_reference"],
        "invoked_by": invocation["invoked_by"],
        "invoked_at": invocation["invoked_at"],
        "invocation_status": invocation["invocation_status"],
        "request_type": invocation["request_type"],
        "capability_id": invocation["capability_id"],
        "invocation_parameters": deepcopy(invocation["invocation_parameters"]),
        "replay_reference": invocation["replay_reference"],
        "provider_authority": False,
        "worker_self_invoked": False,
        "execution_started": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "scope_expansion": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _invocation_artifact(
    *,
    worker_invocation_id: str,
    dispatch: dict[str, Any],
    dispatch_replay: dict[str, Any],
    assignment: dict[str, Any],
    canonical_chain_id: str,
    invocation_parameters: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_ARTIFACT_V1,
        "worker_invocation_runtime_version": WORKER_INVOCATION_RUNTIME_VERSION,
        "worker_invocation_id": _require_string(worker_invocation_id, "worker_invocation_id"),
        "canonical_chain_id": canonical_chain_id,
        "dispatch_reference": dispatch["dispatch_id"],
        "dispatch_hash": dispatch["artifact_hash"],
        "dispatch_replay_hash": dispatch_replay["artifact_hash"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_reference": dispatch["worker_reference"],
        "worker_hash": dispatch["worker_hash"],
        "readiness_reference": dispatch["readiness_reference"],
        "execution_request_reference": dispatch["execution_request_reference"],
        "execution_request_hash": dispatch["execution_request_hash"],
        "invoked_by": _normalize_token(invoked_by, "invoked_by"),
        "invoked_at": _require_string(invoked_at, "invoked_at"),
        "invocation_status": INVOKED,
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_before_invocation": assignment["worker_state_after"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "invocation_parameters": deepcopy(invocation_parameters),
        "invocation_parameters_hash": replay_hash(invocation_parameters),
        "validation_results": (
            "dispatch_valid",
            "dispatch_replay_continuous",
            "worker_identity_verified",
            "worker_assignment_valid",
            "canonical_chain_continuous",
            "invocation_parameters_valid",
            "provider_authority_absent",
            "execution_absent",
            "completion_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_invoked": False,
        "execution_started": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "scope_expansion": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_invocation_artifact(artifact)
    return artifact


def _invocation_returned(invocation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(invocation, "worker invocation artifact")
    returned = {
        "event_type": WORKER_INVOCATION_RETURNED,
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "canonical_chain_id": invocation["canonical_chain_id"],
        "dispatch_reference": invocation["dispatch_reference"],
        "dispatch_hash": invocation["dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_reference": invocation["worker_reference"],
        "worker_hash": invocation["worker_hash"],
        "execution_request_reference": invocation["execution_request_reference"],
        "invocation_status": invocation["invocation_status"],
        "replay_reference": invocation["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_invoked": False,
        "execution_started": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "scope_expansion": False,
        "reconstruction_metadata": {
            "worker_invocation_reconstructable": True,
            "dispatch_reconstructable": True,
            "worker_assignment_reconstructable": True,
            "canonical_chain_continuous": True,
            "execution_started": False,
            "execution_performed": False,
            "completion_recorded": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(invocation: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "worker_invocation_artifact": deepcopy(invocation),
        "worker_invocation_replay": deepcopy(returned),
    }
    capture["worker_invocation_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_invocation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker invocation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "worker invocation artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": WORKER_INVOCATION_VALIDATED if index == 0 else WORKER_INVOCATION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_dispatch_artifact(dispatch: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(dispatch, dict):
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch is required")
    _verify_artifact_hash(dispatch, "dispatch artifact")
    if dispatch.get("artifact_type") != DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch artifact")
    if dispatch.get("dispatch_status") != DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch status")
    if dispatch.get("dispatched_by") != "AIGOL":
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch must be AiGOL-created")
    if dispatch.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("worker invocation failed closed: chain mismatch")
    if dispatch.get("worker_state_before_dispatch") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if dispatch.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay visibility missing")
    if dispatch.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: provider authority introduced")
    if dispatch.get("worker_self_dispatched") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: worker self dispatch introduced")
    if dispatch.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: duplicate invocation marker")
    if dispatch.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: execution performed")
    if dispatch.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: completion recorded")
    if dispatch.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: automatic authorization introduced")
    _require_string(dispatch.get("dispatch_id"), "dispatch_id")
    _require_string(dispatch.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(dispatch.get("worker_assignment_hash"), "worker_assignment_hash")
    _require_string(dispatch.get("worker_reference"), "worker_reference")
    _require_string(dispatch.get("worker_hash"), "worker_hash")
    _require_string(dispatch.get("readiness_reference"), "readiness_reference")
    _require_string(dispatch.get("execution_request_reference"), "execution_request_reference")
    _require_string(dispatch.get("execution_request_hash"), "execution_request_hash")
    _require_string(dispatch.get("request_type"), "request_type")
    _require_string(dispatch.get("capability_id"), "capability_id")
    return deepcopy(dispatch)


def _validate_dispatch_replay(replay: dict[str, Any], dispatch: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay is required")
    _verify_artifact_hash(replay, "dispatch replay artifact")
    if replay.get("event_type") != DISPATCH_RETURNED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch replay event")
    if replay.get("dispatch_reference") != dispatch["dispatch_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay reference mismatch")
    if replay.get("dispatch_hash") != dispatch["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay hash mismatch")
    if replay.get("canonical_chain_id") != dispatch["canonical_chain_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: chain mismatch")
    if replay.get("worker_assignment_reference") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment reference mismatch")
    if replay.get("worker_reference") != dispatch["worker_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if replay.get("worker_hash") != dispatch["worker_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if replay.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: duplicate invocation marker")
    if replay.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: execution performed")
    if replay.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: completion recorded")
    return deepcopy(replay)


def _validate_worker_assignment_artifact(
    assignment: dict[str, Any],
    dispatch: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(assignment, dict):
        raise FailClosedRuntimeError("worker invocation failed closed: worker assignment is required")
    _verify_artifact_hash(assignment, "worker assignment artifact")
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid worker assignment artifact")
    if assignment.get("assignment_status") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid assignment status")
    if assignment.get("worker_state_before") != AVAILABLE:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if assignment.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("worker invocation failed closed: chain mismatch")
    if assignment.get("worker_assignment_id") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment reference mismatch")
    if assignment.get("artifact_hash") != dispatch["worker_assignment_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment hash mismatch")
    if assignment.get("worker_id") != dispatch["worker_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if assignment.get("worker_hash") != dispatch["worker_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if assignment.get("capability_id") != dispatch["capability_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: capability mismatch")
    if assignment.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: provider authority introduced")
    if assignment.get("worker_self_assigned") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: worker self assignment introduced")
    if assignment.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: duplicate dispatch marker")
    if assignment.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: duplicate invocation marker")
    if assignment.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: execution performed")
    if assignment.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: completion recorded")
    return deepcopy(assignment)


def _validate_invocation_parameters(parameters: dict[str, Any], dispatch: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(parameters, dict) or not parameters:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation_parameters are required")
    if FORBIDDEN_INVOCATION_PARAMETER_FIELDS.intersection(parameters):
        raise FailClosedRuntimeError("worker invocation failed closed: authority-bearing invocation parameters")
    required = {
        "execution_request_reference",
        "request_type",
        "capability_id",
        "payload_reference",
        "payload_hash",
        "allowed_effects",
        "forbidden_effects",
    }
    missing = [field for field in required if field not in parameters]
    if missing:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if parameters["execution_request_reference"] != dispatch["execution_request_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if parameters["request_type"] != dispatch["request_type"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if parameters["capability_id"] != dispatch["capability_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    _require_string(parameters.get("payload_reference"), "payload_reference")
    _require_string(parameters.get("payload_hash"), "payload_hash")
    if not isinstance(parameters.get("allowed_effects"), list):
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if not isinstance(parameters.get("forbidden_effects"), list):
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    return deepcopy(parameters)


def _validate_invocation_artifact(invocation: dict[str, Any]) -> None:
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid invocation artifact")
    if invocation.get("invoked_by") != "AIGOL":
        raise FailClosedRuntimeError("worker invocation failed closed: invoked_by must be AIGOL")
    if invocation.get("invocation_status") != INVOKED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid invocation status")
    if invocation.get("dispatch_status_before") != DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch status")
    if invocation.get("worker_state_before_invocation") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if invocation.get("invocation_parameters_hash") != replay_hash(invocation.get("invocation_parameters")):
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameters hash mismatch")
    if invocation.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker invocation failed closed: replay visibility missing")
    if invocation.get("provider_authority") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: provider authority introduced")
    if invocation.get("worker_self_invoked") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: worker self invocation introduced")
    if invocation.get("execution_started") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: execution started")
    if invocation.get("execution_performed") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: execution performed")
    if invocation.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: completion recorded")
    if invocation.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: automatic authorization introduced")
    if invocation.get("scope_expansion") is not False:
        raise FailClosedRuntimeError("worker invocation failed closed: scope expansion introduced")
    _require_string(invocation.get("worker_invocation_id"), "worker_invocation_id")
    _require_string(invocation.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(invocation.get("dispatch_reference"), "dispatch_reference")
    _require_string(invocation.get("dispatch_hash"), "dispatch_hash")
    _require_string(invocation.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(invocation.get("worker_assignment_hash"), "worker_assignment_hash")
    _require_string(invocation.get("worker_reference"), "worker_reference")
    _require_string(invocation.get("worker_hash"), "worker_hash")
    _require_string(invocation.get("readiness_reference"), "readiness_reference")
    _require_string(invocation.get("execution_request_reference"), "execution_request_reference")
    _require_string(invocation.get("invoked_at"), "invoked_at")
    _require_string(invocation.get("request_type"), "request_type")
    _require_string(invocation.get("capability_id"), "capability_id")
    _require_string(invocation.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("worker invocation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("worker invocation replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
