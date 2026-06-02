"""Replay-visible Completion Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.dispatch_runtime import DISPATCH_ARTIFACT_V1, DISPATCHED
from aigol.runtime.execution_runtime import EXECUTING, EXECUTION_ARTIFACT_V1, EXECUTION_RETURNED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_runtime import INVOKED, WORKER_INVOCATION_ARTIFACT_V1
from aigol.runtime.worker_runtime import ASSIGNED, WORKER_ASSIGNMENT_ARTIFACT_V1


COMPLETION_RUNTIME_VERSION = "COMPLETION_RUNTIME_V1"
COMPLETION_ARTIFACT_V1 = "COMPLETION_ARTIFACT_V1"
COMPLETED = "COMPLETED"
COMPLETION_RECORDED = "COMPLETION_RECORDED"
COMPLETION_RETURNED = "COMPLETION_RETURNED"

REPLAY_STEPS = ("completion_recorded", "completion_returned")
FORBIDDEN_COMPLETION_FIELDS = frozenset(
    {
        "result_quality",
        "result_certification",
        "result_payload",
        "failure_analysis",
        "self_improvement",
        "worker_proposal",
        "governance_mutation",
        "replay_mutation",
        "execution_history_mutation",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
    }
)


def complete_execution(
    *,
    completion_id: str,
    execution_artifact: dict[str, Any],
    execution_replay: dict[str, Any],
    invocation_artifact: dict[str, Any],
    dispatch_artifact: dict[str, Any],
    worker_assignment_artifact: dict[str, Any],
    canonical_chain_id: str,
    completion_metadata: dict[str, Any],
    completed_by: str,
    completed_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record deterministic execution completion without result evaluation or certification."""

    replay_path = Path(replay_dir)
    _ensure_completion_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    execution = _validate_execution_artifact(execution_artifact, chain_id)
    execution_returned = _validate_execution_replay(execution_replay, execution)
    invocation = _validate_invocation_artifact(invocation_artifact, execution, chain_id)
    dispatch = _validate_dispatch_artifact(dispatch_artifact, execution, invocation, chain_id)
    assignment = _validate_worker_assignment_artifact(worker_assignment_artifact, execution, invocation, dispatch, chain_id)
    metadata = _validate_completion_metadata(completion_metadata)
    completion = _completion_artifact(
        completion_id=completion_id,
        execution=execution,
        execution_replay=execution_returned,
        invocation=invocation,
        dispatch=dispatch,
        assignment=assignment,
        canonical_chain_id=chain_id,
        completion_metadata=metadata,
        completed_by=completed_by,
        completed_at=completed_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], completion)
    returned = _completion_returned(completion)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(completion, returned)


def reconstruct_completion_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Completion Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("completion replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("completion replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "completion artifact")
        wrappers.append(wrapper)

    completion = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("completion_reference") != completion["completion_id"]:
        raise FailClosedRuntimeError("completion replay reference mismatch")
    if returned.get("completion_hash") != completion["artifact_hash"]:
        raise FailClosedRuntimeError("completion replay hash mismatch")
    if returned.get("execution_reference") != completion["execution_reference"]:
        raise FailClosedRuntimeError("completion replay execution reference mismatch")
    if returned.get("worker_invocation_reference") != completion["worker_invocation_reference"]:
        raise FailClosedRuntimeError("completion replay invocation reference mismatch")
    if returned.get("dispatch_reference") != completion["dispatch_reference"]:
        raise FailClosedRuntimeError("completion replay dispatch reference mismatch")
    if returned.get("canonical_chain_id") != completion["canonical_chain_id"]:
        raise FailClosedRuntimeError("completion replay chain mismatch")
    _validate_completion_artifact(completion)
    return {
        "completion_id": completion["completion_id"],
        "canonical_chain_id": completion["canonical_chain_id"],
        "execution_reference": completion["execution_reference"],
        "worker_invocation_reference": completion["worker_invocation_reference"],
        "dispatch_reference": completion["dispatch_reference"],
        "worker_assignment_reference": completion["worker_assignment_reference"],
        "worker_reference": completion["worker_reference"],
        "execution_request_reference": completion["execution_request_reference"],
        "completion_status": completion["completion_status"],
        "completed_by": completion["completed_by"],
        "completed_at": completion["completed_at"],
        "completion_metadata": deepcopy(completion["completion_metadata"]),
        "completion_timestamps": deepcopy(completion["completion_timestamps"]),
        "replay_reference": completion["replay_reference"],
        "result_quality_evaluated": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _completion_artifact(
    *,
    completion_id: str,
    execution: dict[str, Any],
    execution_replay: dict[str, Any],
    invocation: dict[str, Any],
    dispatch: dict[str, Any],
    assignment: dict[str, Any],
    canonical_chain_id: str,
    completion_metadata: dict[str, Any],
    completed_by: str,
    completed_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COMPLETION_ARTIFACT_V1,
        "completion_runtime_version": COMPLETION_RUNTIME_VERSION,
        "completion_id": _require_string(completion_id, "completion_id"),
        "canonical_chain_id": canonical_chain_id,
        "execution_reference": execution["execution_id"],
        "execution_hash": execution["artifact_hash"],
        "execution_replay_hash": execution_replay["artifact_hash"],
        "worker_invocation_reference": execution["worker_invocation_reference"],
        "worker_invocation_hash": execution["worker_invocation_hash"],
        "dispatch_reference": execution["dispatch_reference"],
        "dispatch_hash": execution["dispatch_hash"],
        "worker_assignment_reference": execution["worker_assignment_reference"],
        "worker_assignment_hash": execution["worker_assignment_hash"],
        "worker_reference": execution["worker_reference"],
        "worker_hash": execution["worker_hash"],
        "execution_request_reference": execution["execution_request_reference"],
        "request_type": execution["request_type"],
        "capability_id": execution["capability_id"],
        "completed_by": _normalize_token(completed_by, "completed_by"),
        "completed_at": _require_string(completed_at, "completed_at"),
        "completion_status": COMPLETED,
        "execution_status_before": execution["execution_status"],
        "invocation_status_before": invocation["invocation_status"],
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_at_completion_boundary": assignment["worker_state_after"],
        "completion_metadata": deepcopy(completion_metadata),
        "completion_metadata_hash": replay_hash(completion_metadata),
        "completion_timestamps": {
            "started_at": execution["started_at"],
            "completed_at": _require_string(completed_at, "completed_at"),
        },
        "validation_results": (
            "execution_valid",
            "execution_replay_continuous",
            "worker_identity_verified",
            "invocation_continuous",
            "dispatch_continuous",
            "assignment_continuous",
            "canonical_chain_continuous",
            "completion_metadata_valid",
            "result_quality_evaluation_absent",
            "result_certification_absent",
            "failure_analysis_absent",
            "self_improvement_absent",
            "governance_mutation_absent",
            "replay_mutation_absent",
            "execution_history_mutation_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_completed": False,
        "completion_recorded": True,
        "result_quality_evaluated": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
        "scope_expansion": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_completion_artifact(artifact)
    return artifact


def _completion_returned(completion: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(completion, "completion artifact")
    returned = {
        "event_type": COMPLETION_RETURNED,
        "completion_reference": completion["completion_id"],
        "completion_hash": completion["artifact_hash"],
        "canonical_chain_id": completion["canonical_chain_id"],
        "execution_reference": completion["execution_reference"],
        "execution_hash": completion["execution_hash"],
        "worker_invocation_reference": completion["worker_invocation_reference"],
        "worker_invocation_hash": completion["worker_invocation_hash"],
        "dispatch_reference": completion["dispatch_reference"],
        "dispatch_hash": completion["dispatch_hash"],
        "worker_assignment_reference": completion["worker_assignment_reference"],
        "worker_reference": completion["worker_reference"],
        "worker_hash": completion["worker_hash"],
        "completion_status": completion["completion_status"],
        "completed_at": completion["completed_at"],
        "replay_reference": completion["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_completed": False,
        "completion_recorded": True,
        "result_quality_evaluated": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
        "scope_expansion": False,
        "reconstruction_metadata": {
            "completion_reconstructable": True,
            "execution_reconstructable": True,
            "worker_invocation_reconstructable": True,
            "dispatch_reconstructable": True,
            "worker_assignment_reconstructable": True,
            "canonical_chain_continuous": True,
            "result_quality_evaluated": False,
            "result_certified": False,
            "failure_analysis_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(completion: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "completion_artifact": deepcopy(completion),
        "completion_replay": deepcopy(returned),
    }
    capture["completion_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_completion_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("completion replay step ordering mismatch")
    _verify_artifact_hash(artifact, "completion artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": COMPLETION_RECORDED if index == 0 else COMPLETION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_execution_artifact(execution: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(execution, dict):
        raise FailClosedRuntimeError("completion failed closed: execution artifact is required")
    _verify_artifact_hash(execution, "execution artifact")
    if execution.get("artifact_type") != EXECUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("completion failed closed: invalid execution artifact")
    if execution.get("execution_status") != EXECUTING:
        raise FailClosedRuntimeError("completion failed closed: invalid execution state")
    if execution.get("started_by") != "AIGOL":
        raise FailClosedRuntimeError("completion failed closed: execution must be AiGOL-created")
    if execution.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("completion failed closed: chain mismatch")
    if execution.get("execution_started") is not True:
        raise FailClosedRuntimeError("completion failed closed: execution start missing")
    if execution.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("completion failed closed: duplicate completion")
    if execution.get("result_certified") is not False:
        raise FailClosedRuntimeError("completion failed closed: result certification introduced")
    if execution.get("self_improvement_performed") is not False:
        raise FailClosedRuntimeError("completion failed closed: self improvement introduced")
    if execution.get("governance_mutated") is not False:
        raise FailClosedRuntimeError("completion failed closed: governance mutation introduced")
    if execution.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("completion failed closed: replay mutation introduced")
    _require_string(execution.get("execution_id"), "execution_id")
    _require_string(execution.get("worker_invocation_reference"), "worker_invocation_reference")
    _require_string(execution.get("worker_invocation_hash"), "worker_invocation_hash")
    _require_string(execution.get("dispatch_reference"), "dispatch_reference")
    _require_string(execution.get("dispatch_hash"), "dispatch_hash")
    _require_string(execution.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(execution.get("worker_assignment_hash"), "worker_assignment_hash")
    _require_string(execution.get("worker_reference"), "worker_reference")
    _require_string(execution.get("worker_hash"), "worker_hash")
    _require_string(execution.get("execution_request_reference"), "execution_request_reference")
    _require_string(execution.get("request_type"), "request_type")
    _require_string(execution.get("capability_id"), "capability_id")
    _require_string(execution.get("started_at"), "started_at")
    return deepcopy(execution)


def _validate_execution_replay(replay: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("completion failed closed: execution replay is required")
    _verify_artifact_hash(replay, "execution replay artifact")
    if replay.get("event_type") != EXECUTION_RETURNED:
        raise FailClosedRuntimeError("completion failed closed: invalid execution replay event")
    if replay.get("execution_reference") != execution["execution_id"]:
        raise FailClosedRuntimeError("completion failed closed: execution replay reference mismatch")
    if replay.get("execution_hash") != execution["artifact_hash"]:
        raise FailClosedRuntimeError("completion failed closed: execution replay hash mismatch")
    if replay.get("canonical_chain_id") != execution["canonical_chain_id"]:
        raise FailClosedRuntimeError("completion failed closed: chain mismatch")
    if replay.get("worker_invocation_reference") != execution["worker_invocation_reference"]:
        raise FailClosedRuntimeError("completion failed closed: invocation continuity mismatch")
    if replay.get("dispatch_reference") != execution["dispatch_reference"]:
        raise FailClosedRuntimeError("completion failed closed: dispatch continuity mismatch")
    if replay.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("completion failed closed: duplicate completion")
    if replay.get("result_certified") is not False:
        raise FailClosedRuntimeError("completion failed closed: result certification introduced")
    return deepcopy(replay)


def _validate_invocation_artifact(
    invocation: dict[str, Any],
    execution: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(invocation, dict):
        raise FailClosedRuntimeError("completion failed closed: invocation artifact is required")
    _verify_artifact_hash(invocation, "worker invocation artifact")
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("completion failed closed: invalid invocation artifact")
    if invocation.get("invocation_status") != INVOKED:
        raise FailClosedRuntimeError("completion failed closed: invalid invocation state")
    if invocation.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("completion failed closed: chain mismatch")
    if invocation.get("worker_invocation_id") != execution["worker_invocation_reference"]:
        raise FailClosedRuntimeError("completion failed closed: invocation continuity mismatch")
    if invocation.get("artifact_hash") != execution["worker_invocation_hash"]:
        raise FailClosedRuntimeError("completion failed closed: invocation hash mismatch")
    if invocation.get("dispatch_reference") != execution["dispatch_reference"]:
        raise FailClosedRuntimeError("completion failed closed: dispatch continuity mismatch")
    if invocation.get("worker_assignment_reference") != execution["worker_assignment_reference"]:
        raise FailClosedRuntimeError("completion failed closed: assignment continuity mismatch")
    if invocation.get("worker_reference") != execution["worker_reference"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if invocation.get("worker_hash") != execution["worker_hash"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if invocation.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("completion failed closed: duplicate completion")
    return deepcopy(invocation)


def _validate_dispatch_artifact(
    dispatch: dict[str, Any],
    execution: dict[str, Any],
    invocation: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(dispatch, dict):
        raise FailClosedRuntimeError("completion failed closed: dispatch artifact is required")
    _verify_artifact_hash(dispatch, "dispatch artifact")
    if dispatch.get("artifact_type") != DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("completion failed closed: invalid dispatch artifact")
    if dispatch.get("dispatch_status") != DISPATCHED:
        raise FailClosedRuntimeError("completion failed closed: invalid dispatch state")
    if dispatch.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("completion failed closed: chain mismatch")
    if dispatch.get("dispatch_id") != execution["dispatch_reference"]:
        raise FailClosedRuntimeError("completion failed closed: dispatch continuity mismatch")
    if dispatch.get("artifact_hash") != execution["dispatch_hash"]:
        raise FailClosedRuntimeError("completion failed closed: dispatch hash mismatch")
    if dispatch.get("dispatch_id") != invocation["dispatch_reference"]:
        raise FailClosedRuntimeError("completion failed closed: dispatch continuity mismatch")
    if dispatch.get("worker_assignment_reference") != execution["worker_assignment_reference"]:
        raise FailClosedRuntimeError("completion failed closed: assignment continuity mismatch")
    if dispatch.get("worker_reference") != execution["worker_reference"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if dispatch.get("worker_hash") != execution["worker_hash"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if dispatch.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("completion failed closed: duplicate completion")
    return deepcopy(dispatch)


def _validate_worker_assignment_artifact(
    assignment: dict[str, Any],
    execution: dict[str, Any],
    invocation: dict[str, Any],
    dispatch: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(assignment, dict):
        raise FailClosedRuntimeError("completion failed closed: worker assignment artifact is required")
    _verify_artifact_hash(assignment, "worker assignment artifact")
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("completion failed closed: invalid worker assignment artifact")
    if assignment.get("assignment_status") != ASSIGNED:
        raise FailClosedRuntimeError("completion failed closed: invalid assignment state")
    if assignment.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("completion failed closed: chain mismatch")
    if assignment.get("worker_assignment_id") != execution["worker_assignment_reference"]:
        raise FailClosedRuntimeError("completion failed closed: assignment continuity mismatch")
    if assignment.get("artifact_hash") != execution["worker_assignment_hash"]:
        raise FailClosedRuntimeError("completion failed closed: assignment hash mismatch")
    if assignment.get("worker_assignment_id") != invocation["worker_assignment_reference"]:
        raise FailClosedRuntimeError("completion failed closed: assignment continuity mismatch")
    if assignment.get("worker_assignment_id") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("completion failed closed: assignment continuity mismatch")
    if assignment.get("worker_id") != execution["worker_reference"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if assignment.get("worker_hash") != execution["worker_hash"]:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if assignment.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("completion failed closed: duplicate completion")
    return deepcopy(assignment)


def _validate_completion_metadata(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise FailClosedRuntimeError("completion failed closed: completion_metadata is required")
    if FORBIDDEN_COMPLETION_FIELDS.intersection(value):
        raise FailClosedRuntimeError("completion failed closed: authority-bearing completion_metadata")
    return deepcopy(value)


def _validate_completion_artifact(completion: dict[str, Any]) -> None:
    if completion.get("artifact_type") != COMPLETION_ARTIFACT_V1:
        raise FailClosedRuntimeError("completion failed closed: invalid completion artifact")
    if completion.get("completed_by") != "AIGOL":
        raise FailClosedRuntimeError("completion failed closed: completed_by must be AIGOL")
    if completion.get("completion_status") != COMPLETED:
        raise FailClosedRuntimeError("completion failed closed: invalid completion state")
    if completion.get("execution_status_before") != EXECUTING:
        raise FailClosedRuntimeError("completion failed closed: invalid execution state")
    if completion.get("invocation_status_before") != INVOKED:
        raise FailClosedRuntimeError("completion failed closed: invalid invocation state")
    if completion.get("dispatch_status_before") != DISPATCHED:
        raise FailClosedRuntimeError("completion failed closed: invalid dispatch state")
    if completion.get("worker_state_at_completion_boundary") != ASSIGNED:
        raise FailClosedRuntimeError("completion failed closed: worker mismatch")
    if completion.get("completion_metadata_hash") != replay_hash(completion.get("completion_metadata")):
        raise FailClosedRuntimeError("completion failed closed: completion metadata hash mismatch")
    timestamps = completion.get("completion_timestamps")
    if not isinstance(timestamps, dict) or timestamps.get("completed_at") != completion.get("completed_at"):
        raise FailClosedRuntimeError("completion failed closed: invalid completion timestamps")
    if completion.get("replay_visible") is not True:
        raise FailClosedRuntimeError("completion failed closed: replay visibility missing")
    if completion.get("provider_authority") is not False:
        raise FailClosedRuntimeError("completion failed closed: provider authority introduced")
    if completion.get("worker_self_completed") is not False:
        raise FailClosedRuntimeError("completion failed closed: worker self completion introduced")
    if completion.get("completion_recorded") is not True:
        raise FailClosedRuntimeError("completion failed closed: completion record missing")
    if completion.get("result_quality_evaluated") is not False:
        raise FailClosedRuntimeError("completion failed closed: result quality evaluation introduced")
    if completion.get("result_certified") is not False:
        raise FailClosedRuntimeError("completion failed closed: result certification introduced")
    if completion.get("failure_analysis_performed") is not False:
        raise FailClosedRuntimeError("completion failed closed: failure analysis introduced")
    if completion.get("self_improvement_performed") is not False:
        raise FailClosedRuntimeError("completion failed closed: self improvement introduced")
    if completion.get("governance_mutated") is not False:
        raise FailClosedRuntimeError("completion failed closed: governance mutation introduced")
    if completion.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("completion failed closed: replay mutation introduced")
    if completion.get("execution_history_modified") is not False:
        raise FailClosedRuntimeError("completion failed closed: execution history mutation introduced")
    if completion.get("scope_expansion") is not False:
        raise FailClosedRuntimeError("completion failed closed: scope expansion introduced")
    _require_string(completion.get("completion_id"), "completion_id")
    _require_string(completion.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(completion.get("execution_reference"), "execution_reference")
    _require_string(completion.get("execution_hash"), "execution_hash")
    _require_string(completion.get("worker_invocation_reference"), "worker_invocation_reference")
    _require_string(completion.get("dispatch_reference"), "dispatch_reference")
    _require_string(completion.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(completion.get("worker_reference"), "worker_reference")
    _require_string(completion.get("worker_hash"), "worker_hash")
    _require_string(completion.get("execution_request_reference"), "execution_request_reference")
    _require_string(completion.get("request_type"), "request_type")
    _require_string(completion.get("capability_id"), "capability_id")
    _require_string(completion.get("completed_at"), "completed_at")
    _require_string(completion.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("completion replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("completion replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
