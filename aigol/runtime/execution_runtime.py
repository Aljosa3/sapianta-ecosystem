"""Replay-visible Execution Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.dispatch_runtime import DISPATCH_ARTIFACT_V1, DISPATCHED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCH_ARTIFACT_V1,
    WORKER_DISPATCHED,
)
from aigol.runtime.worker_invocation_runtime import (
    INVOKED,
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOCATION_RETURNED,
)
from aigol.runtime.worker_runtime import ASSIGNED, WORKER_ASSIGNMENT_ARTIFACT_V1


EXECUTION_RUNTIME_VERSION = "EXECUTION_RUNTIME_V1"
EXECUTION_ARTIFACT_V1 = "EXECUTION_ARTIFACT_V1"
EXECUTING = "EXECUTING"
EXECUTION_STARTED = "EXECUTION_STARTED"
EXECUTION_RETURNED = "EXECUTION_RETURNED"

REPLAY_STEPS = ("execution_started", "execution_returned")
FORBIDDEN_EXECUTION_FIELDS = frozenset(
    {
        "completion_status",
        "completion_record",
        "result_payload",
        "result_certification",
        "self_improvement",
        "governance_mutation",
        "replay_mutation",
        "constitutional_mutation",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
    }
)


def start_execution(
    *,
    execution_id: str,
    invocation_artifact: dict[str, Any],
    invocation_replay: dict[str, Any],
    dispatch_artifact: dict[str, Any],
    worker_assignment_artifact: dict[str, Any],
    canonical_chain_id: str,
    execution_metadata: dict[str, Any],
    execution_context: dict[str, Any],
    started_by: str,
    started_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record deterministic execution start without completion or result certification."""

    replay_path = Path(replay_dir)
    _ensure_execution_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    invocation = _validate_invocation_artifact(invocation_artifact, chain_id)
    replay = _validate_invocation_replay(invocation_replay, invocation)
    dispatch = _validate_dispatch_artifact(dispatch_artifact, invocation, chain_id)
    assignment = _validate_worker_assignment_artifact(worker_assignment_artifact, invocation, dispatch, chain_id)
    metadata = _validate_execution_map(execution_metadata, "execution_metadata")
    context = _validate_execution_map(execution_context, "execution_context")
    execution = _execution_artifact(
        execution_id=execution_id,
        invocation=invocation,
        invocation_replay=replay,
        dispatch=dispatch,
        assignment=assignment,
        canonical_chain_id=chain_id,
        execution_metadata=metadata,
        execution_context=context,
        started_by=started_by,
        started_at=started_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], execution)
    returned = _execution_returned(execution)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(execution, returned)


def reconstruct_execution_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Execution Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("execution replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("execution replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "execution artifact")
        wrappers.append(wrapper)

    execution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("execution_reference") != execution["execution_id"]:
        raise FailClosedRuntimeError("execution replay reference mismatch")
    if returned.get("execution_hash") != execution["artifact_hash"]:
        raise FailClosedRuntimeError("execution replay hash mismatch")
    if returned.get("worker_invocation_reference") != execution["worker_invocation_reference"]:
        raise FailClosedRuntimeError("execution replay invocation reference mismatch")
    if returned.get("dispatch_reference") != execution["dispatch_reference"]:
        raise FailClosedRuntimeError("execution replay dispatch reference mismatch")
    if returned.get("canonical_chain_id") != execution["canonical_chain_id"]:
        raise FailClosedRuntimeError("execution replay chain mismatch")
    _validate_execution_artifact(execution)
    return {
        "execution_id": execution["execution_id"],
        "canonical_chain_id": execution["canonical_chain_id"],
        "worker_invocation_reference": execution["worker_invocation_reference"],
        "dispatch_reference": execution["dispatch_reference"],
        "worker_assignment_reference": execution["worker_assignment_reference"],
        "worker_reference": execution["worker_reference"],
        "execution_request_reference": execution["execution_request_reference"],
        "execution_status": execution["execution_status"],
        "started_by": execution["started_by"],
        "started_at": execution["started_at"],
        "execution_metadata": deepcopy(execution["execution_metadata"]),
        "execution_context": deepcopy(execution["execution_context"]),
        "execution_timestamps": deepcopy(execution["execution_timestamps"]),
        "replay_reference": execution["replay_reference"],
        "provider_authority": False,
        "worker_self_started": False,
        "completion_recorded": False,
        "result_certified": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _execution_artifact(
    *,
    execution_id: str,
    invocation: dict[str, Any],
    invocation_replay: dict[str, Any],
    dispatch: dict[str, Any],
    assignment: dict[str, Any],
    canonical_chain_id: str,
    execution_metadata: dict[str, Any],
    execution_context: dict[str, Any],
    started_by: str,
    started_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_ARTIFACT_V1,
        "execution_runtime_version": EXECUTION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "canonical_chain_id": canonical_chain_id,
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_invocation_replay_hash": invocation_replay["artifact_hash"],
        "dispatch_reference": invocation["dispatch_reference"],
        "dispatch_hash": invocation["dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_reference": invocation["worker_reference"],
        "worker_hash": invocation["worker_hash"],
        "readiness_reference": invocation["readiness_reference"],
        "execution_request_reference": invocation["execution_request_reference"],
        "request_type": invocation["request_type"],
        "capability_id": invocation["capability_id"],
        "started_by": _normalize_token(started_by, "started_by"),
        "started_at": _require_string(started_at, "started_at"),
        "execution_status": EXECUTING,
        "invocation_status_before": invocation["invocation_status"],
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_before_execution": assignment["worker_state_after"],
        "execution_metadata": deepcopy(execution_metadata),
        "execution_metadata_hash": replay_hash(execution_metadata),
        "execution_context": deepcopy(execution_context),
        "execution_context_hash": replay_hash(execution_context),
        "execution_timestamps": {
            "invoked_at": invocation["invoked_at"],
            "started_at": _require_string(started_at, "started_at"),
        },
        "validation_results": (
            "invocation_valid",
            "invocation_replay_continuous",
            "dispatch_continuous",
            "worker_assignment_continuous",
            "worker_identity_verified",
            "canonical_chain_continuous",
            "execution_metadata_valid",
            "execution_context_valid",
            "completion_absent",
            "result_certification_absent",
            "self_improvement_absent",
            "governance_mutation_absent",
            "replay_mutation_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_started": False,
        "execution_started": True,
        "completion_recorded": False,
        "result_certified": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "scope_expansion": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_execution_artifact(artifact)
    return artifact


def _execution_returned(execution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(execution, "execution artifact")
    returned = {
        "event_type": EXECUTION_RETURNED,
        "execution_reference": execution["execution_id"],
        "execution_hash": execution["artifact_hash"],
        "canonical_chain_id": execution["canonical_chain_id"],
        "worker_invocation_reference": execution["worker_invocation_reference"],
        "worker_invocation_hash": execution["worker_invocation_hash"],
        "dispatch_reference": execution["dispatch_reference"],
        "dispatch_hash": execution["dispatch_hash"],
        "worker_assignment_reference": execution["worker_assignment_reference"],
        "worker_reference": execution["worker_reference"],
        "worker_hash": execution["worker_hash"],
        "execution_request_reference": execution["execution_request_reference"],
        "execution_status": execution["execution_status"],
        "started_at": execution["started_at"],
        "replay_reference": execution["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_started": False,
        "execution_started": True,
        "completion_recorded": False,
        "result_certified": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "scope_expansion": False,
        "reconstruction_metadata": {
            "execution_reconstructable": True,
            "worker_invocation_reconstructable": True,
            "dispatch_reconstructable": True,
            "worker_assignment_reconstructable": True,
            "canonical_chain_continuous": True,
            "completion_recorded": False,
            "result_certified": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(execution: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "execution_artifact": deepcopy(execution),
        "execution_replay": deepcopy(returned),
    }
    capture["execution_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_execution_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("execution replay step ordering mismatch")
    _verify_artifact_hash(artifact, "execution artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": EXECUTION_STARTED if index == 0 else EXECUTION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_invocation_artifact(invocation: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(invocation, dict):
        raise FailClosedRuntimeError("execution failed closed: invocation is required")
    _verify_artifact_hash(invocation, "worker invocation artifact")
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution failed closed: invalid invocation artifact")
    if invocation.get("invocation_status") != INVOKED:
        raise FailClosedRuntimeError("execution failed closed: invalid invocation state")
    if invocation.get("invoked_by") not in {"AIGOL", "AIGOL_GOVERNANCE"}:
        raise FailClosedRuntimeError("execution failed closed: invocation must be AiGOL-created")
    normalized = _normalize_invocation_for_execution(invocation)
    if normalized.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("execution failed closed: chain mismatch")
    if normalized.get("worker_state_before_invocation") != ASSIGNED:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("replay_visible") is not True:
        raise FailClosedRuntimeError("execution failed closed: invocation replay visibility missing")
    if not _false_or_absent(invocation, "provider_authority"):
        raise FailClosedRuntimeError("execution failed closed: provider authority introduced")
    if not _false_or_absent(invocation, "worker_self_invoked"):
        raise FailClosedRuntimeError("execution failed closed: worker self invocation introduced")
    if normalized.get("execution_started") is not False:
        raise FailClosedRuntimeError("execution failed closed: duplicate execution")
    if not _false_or_absent(invocation, "execution_performed"):
        raise FailClosedRuntimeError("execution failed closed: execution already performed")
    if not _false_or_absent(invocation, "completion_recorded"):
        raise FailClosedRuntimeError("execution failed closed: completion recorded")
    if not _false_or_absent(invocation, "automatic_authorization"):
        raise FailClosedRuntimeError("execution failed closed: automatic authorization introduced")
    if not _false_or_absent(invocation, "scope_expansion"):
        raise FailClosedRuntimeError("execution failed closed: scope expansion introduced")
    _require_string(normalized.get("worker_invocation_id"), "worker_invocation_id")
    _require_string(normalized.get("dispatch_reference"), "dispatch_reference")
    _require_string(normalized.get("dispatch_hash"), "dispatch_hash")
    _require_string(normalized.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(normalized.get("worker_assignment_hash"), "worker_assignment_hash")
    _require_string(normalized.get("worker_reference"), "worker_reference")
    _require_string(normalized.get("worker_hash"), "worker_hash")
    _require_string(normalized.get("execution_request_reference"), "execution_request_reference")
    _require_string(normalized.get("request_type"), "request_type")
    _require_string(normalized.get("capability_id"), "capability_id")
    _require_string(normalized.get("invoked_at"), "invoked_at")
    return normalized


def _validate_invocation_replay(replay: dict[str, Any], invocation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("execution failed closed: invocation replay is required")
    _verify_artifact_hash(replay, "worker invocation replay artifact")
    normalized = _normalize_invocation_replay_for_execution(replay)
    if normalized.get("event_type") != WORKER_INVOCATION_RETURNED:
        raise FailClosedRuntimeError("execution failed closed: invalid invocation replay event")
    if normalized.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("execution failed closed: invocation replay reference mismatch")
    if normalized.get("worker_invocation_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("execution failed closed: invocation replay hash mismatch")
    if normalized.get("dispatch_reference") != invocation["dispatch_reference"]:
        raise FailClosedRuntimeError("execution failed closed: dispatch continuity mismatch")
    if normalized.get("canonical_chain_id") != invocation["canonical_chain_id"]:
        raise FailClosedRuntimeError("execution failed closed: chain mismatch")
    if normalized.get("worker_reference") != invocation["worker_reference"]:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("execution_started") is not False:
        raise FailClosedRuntimeError("execution failed closed: duplicate execution")
    if not _false_or_absent(normalized, "execution_performed"):
        raise FailClosedRuntimeError("execution failed closed: execution already performed")
    if not _false_or_absent(normalized, "completion_recorded"):
        raise FailClosedRuntimeError("execution failed closed: completion recorded")
    return normalized


def _validate_dispatch_artifact(
    dispatch: dict[str, Any],
    invocation: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(dispatch, dict):
        raise FailClosedRuntimeError("execution failed closed: dispatch is required")
    _verify_artifact_hash(dispatch, "dispatch artifact")
    normalized = _normalize_dispatch_for_execution(dispatch)
    if normalized.get("artifact_type") != DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution failed closed: invalid dispatch artifact")
    if normalized.get("dispatch_status") != DISPATCHED:
        raise FailClosedRuntimeError("execution failed closed: invalid dispatch state")
    if normalized.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("execution failed closed: chain mismatch")
    if normalized.get("dispatch_id") != invocation["dispatch_reference"]:
        raise FailClosedRuntimeError("execution failed closed: dispatch continuity mismatch")
    if normalized.get("artifact_hash") != invocation["dispatch_hash"]:
        raise FailClosedRuntimeError("execution failed closed: dispatch hash mismatch")
    if normalized.get("worker_assignment_reference") != invocation["worker_assignment_reference"]:
        raise FailClosedRuntimeError("execution failed closed: assignment continuity mismatch")
    if normalized.get("worker_reference") != invocation["worker_reference"]:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("worker_hash") != invocation["worker_hash"]:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("execution_request_reference") != invocation["execution_request_reference"]:
        raise FailClosedRuntimeError("execution failed closed: execution request mismatch")
    if not _false_or_absent(dispatch, "provider_authority"):
        raise FailClosedRuntimeError("execution failed closed: provider authority introduced")
    if not _false_or_absent(dispatch, "worker_self_dispatched"):
        raise FailClosedRuntimeError("execution failed closed: worker self dispatch introduced")
    if normalized.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("execution failed closed: duplicate invocation marker")
    if not _false_or_absent(dispatch, "execution_performed"):
        raise FailClosedRuntimeError("execution failed closed: execution already performed")
    if not _false_or_absent(dispatch, "completion_recorded"):
        raise FailClosedRuntimeError("execution failed closed: completion recorded")
    return normalized


def _validate_worker_assignment_artifact(
    assignment: dict[str, Any],
    invocation: dict[str, Any],
    dispatch: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(assignment, dict):
        raise FailClosedRuntimeError("execution failed closed: worker assignment is required")
    _verify_artifact_hash(assignment, "worker assignment artifact")
    normalized = _normalize_assignment_for_execution(assignment)
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution failed closed: invalid worker assignment artifact")
    if normalized.get("assignment_status") != ASSIGNED:
        raise FailClosedRuntimeError("execution failed closed: invalid assignment state")
    if normalized.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("execution failed closed: chain mismatch")
    if normalized.get("worker_assignment_id") != invocation["worker_assignment_reference"]:
        raise FailClosedRuntimeError("execution failed closed: assignment continuity mismatch")
    if normalized.get("artifact_hash") != invocation["worker_assignment_hash"]:
        raise FailClosedRuntimeError("execution failed closed: assignment hash mismatch")
    if normalized.get("worker_assignment_id") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("execution failed closed: assignment continuity mismatch")
    if normalized.get("worker_id") != invocation["worker_reference"]:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("worker_hash") != invocation["worker_hash"]:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if normalized.get("execution_request_reference") != invocation["execution_request_reference"]:
        raise FailClosedRuntimeError("execution failed closed: execution request mismatch")
    if not _false_or_absent(assignment, "provider_authority"):
        raise FailClosedRuntimeError("execution failed closed: provider authority introduced")
    if not _false_or_absent(assignment, "worker_self_assigned"):
        raise FailClosedRuntimeError("execution failed closed: worker self assignment introduced")
    if not _false_or_absent(assignment, "execution_performed"):
        raise FailClosedRuntimeError("execution failed closed: execution already performed")
    if not _false_or_absent(assignment, "completion_recorded"):
        raise FailClosedRuntimeError("execution failed closed: completion recorded")
    return normalized


def _normalize_invocation_for_execution(invocation: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(invocation)
    normalized.setdefault("canonical_chain_id", invocation.get("chain_id"))
    normalized.setdefault("dispatch_reference", invocation.get("worker_dispatch_reference"))
    normalized.setdefault("dispatch_hash", invocation.get("worker_dispatch_hash"))
    normalized.setdefault("worker_reference", invocation.get("worker_id"))
    normalized.setdefault("execution_request_reference", invocation.get("worker_invocation_request_reference"))
    normalized.setdefault("readiness_reference", invocation.get("execution_packet_reference"))
    normalized.setdefault("request_type", "WORKER_INVOCATION_REQUEST")
    normalized.setdefault("capability_id", invocation.get("worker_role"))
    normalized.setdefault("execution_performed", False)
    normalized.setdefault("completion_recorded", False)
    normalized.setdefault("automatic_authorization", False)
    normalized.setdefault("scope_expansion", False)
    return normalized


def _normalize_invocation_replay_for_execution(replay: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(replay)
    if replay.get("artifact_type") == "WORKER_INVOCATION_RESULT_ARTIFACT_V1":
        normalized.setdefault("event_type", WORKER_INVOCATION_RETURNED)
        normalized.setdefault("dispatch_reference", replay.get("worker_dispatch_reference"))
        normalized.setdefault("dispatch_hash", replay.get("worker_dispatch_hash"))
        normalized.setdefault("canonical_chain_id", replay.get("chain_id"))
        normalized.setdefault("worker_reference", replay.get("worker_reference"))
        normalized.setdefault("execution_started", False)
        normalized.setdefault("execution_performed", False)
        normalized.setdefault("completion_recorded", False)
    return normalized


def _normalize_dispatch_for_execution(dispatch: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(dispatch)
    if dispatch.get("artifact_type") == WORKER_DISPATCH_ARTIFACT_V1:
        normalized["artifact_type"] = DISPATCH_ARTIFACT_V1
        normalized["dispatch_id"] = dispatch.get("worker_dispatch_id")
        normalized["dispatch_status"] = (
            DISPATCHED if dispatch.get("dispatch_status") == WORKER_DISPATCHED else dispatch.get("dispatch_status")
        )
        normalized["canonical_chain_id"] = dispatch.get("chain_id")
        normalized["worker_reference"] = dispatch.get("worker_id")
        normalized["execution_request_reference"] = dispatch.get("worker_invocation_request_reference")
        normalized.setdefault("execution_performed", False)
        normalized.setdefault("completion_recorded", False)
    return normalized


def _normalize_assignment_for_execution(assignment: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(assignment)
    if assignment.get("assignment_status") == "WORKER_ASSIGNED":
        normalized["assignment_status"] = ASSIGNED
    normalized.setdefault("execution_request_reference", assignment.get("worker_invocation_request_reference"))
    normalized.setdefault("execution_performed", False)
    normalized.setdefault("completion_recorded", False)
    return normalized


def _false_or_absent(artifact: dict[str, Any], field_name: str) -> bool:
    return artifact.get(field_name) is False or field_name not in artifact


def _validate_execution_map(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise FailClosedRuntimeError(f"execution failed closed: {field_name} is required")
    if FORBIDDEN_EXECUTION_FIELDS.intersection(value):
        raise FailClosedRuntimeError(f"execution failed closed: authority-bearing {field_name}")
    return deepcopy(value)


def _validate_execution_artifact(execution: dict[str, Any]) -> None:
    if execution.get("artifact_type") != EXECUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution failed closed: invalid execution artifact")
    if execution.get("started_by") != "AIGOL":
        raise FailClosedRuntimeError("execution failed closed: started_by must be AIGOL")
    if execution.get("execution_status") != EXECUTING:
        raise FailClosedRuntimeError("execution failed closed: invalid execution state")
    if execution.get("invocation_status_before") != INVOKED:
        raise FailClosedRuntimeError("execution failed closed: invalid invocation state")
    if execution.get("dispatch_status_before") != DISPATCHED:
        raise FailClosedRuntimeError("execution failed closed: invalid dispatch state")
    if execution.get("worker_state_before_execution") != ASSIGNED:
        raise FailClosedRuntimeError("execution failed closed: worker mismatch")
    if execution.get("execution_metadata_hash") != replay_hash(execution.get("execution_metadata")):
        raise FailClosedRuntimeError("execution failed closed: execution metadata hash mismatch")
    if execution.get("execution_context_hash") != replay_hash(execution.get("execution_context")):
        raise FailClosedRuntimeError("execution failed closed: execution context hash mismatch")
    timestamps = execution.get("execution_timestamps")
    if not isinstance(timestamps, dict) or timestamps.get("started_at") != execution.get("started_at"):
        raise FailClosedRuntimeError("execution failed closed: invalid execution timestamps")
    if execution.get("replay_visible") is not True:
        raise FailClosedRuntimeError("execution failed closed: replay visibility missing")
    if execution.get("provider_authority") is not False:
        raise FailClosedRuntimeError("execution failed closed: provider authority introduced")
    if execution.get("worker_self_started") is not False:
        raise FailClosedRuntimeError("execution failed closed: worker self start introduced")
    if execution.get("execution_started") is not True:
        raise FailClosedRuntimeError("execution failed closed: execution start missing")
    if execution.get("completion_recorded") is not False:
        raise FailClosedRuntimeError("execution failed closed: completion recorded")
    if execution.get("result_certified") is not False:
        raise FailClosedRuntimeError("execution failed closed: result certification introduced")
    if execution.get("self_improvement_performed") is not False:
        raise FailClosedRuntimeError("execution failed closed: self improvement introduced")
    if execution.get("governance_mutated") is not False:
        raise FailClosedRuntimeError("execution failed closed: governance mutation introduced")
    if execution.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("execution failed closed: replay mutation introduced")
    if execution.get("scope_expansion") is not False:
        raise FailClosedRuntimeError("execution failed closed: scope expansion introduced")
    _require_string(execution.get("execution_id"), "execution_id")
    _require_string(execution.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(execution.get("worker_invocation_reference"), "worker_invocation_reference")
    _require_string(execution.get("worker_invocation_hash"), "worker_invocation_hash")
    _require_string(execution.get("dispatch_reference"), "dispatch_reference")
    _require_string(execution.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(execution.get("worker_reference"), "worker_reference")
    _require_string(execution.get("worker_hash"), "worker_hash")
    _require_string(execution.get("execution_request_reference"), "execution_request_reference")
    _require_string(execution.get("request_type"), "request_type")
    _require_string(execution.get("capability_id"), "capability_id")
    _require_string(execution.get("started_at"), "started_at")
    _require_string(execution.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("execution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("execution replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
