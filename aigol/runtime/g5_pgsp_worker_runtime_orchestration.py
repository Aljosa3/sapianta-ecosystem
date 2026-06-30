"""PGSP orchestration over the existing Worker runtime stack for G5-09."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.execution_runtime import reconstruct_execution_replay, start_execution
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import (
    REVIEW_COMPLETED,
    reconstruct_post_execution_replay_review,
    review_validated_worker_result,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    dispatch_assigned_worker,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_INVOCATION_REQUEST_CREATED,
    create_worker_invocation_request,
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    invoke_dispatched_worker,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_result_capture_runtime import (
    WORKER_RESULT_CAPTURED,
    capture_worker_result,
    default_worker_output_for_invocation,
    reconstruct_worker_result_capture_replay,
)
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    reconstruct_worker_result_validation_replay,
    validate_worker_result,
)


G5_09_RUNTIME_VERSION = "G5_09_PGSP_WORKER_RUNTIME_ORCHESTRATION_AND_WIRING_V1"
PGSP_WORKER_ORCHESTRATION_CONTEXT_ARTIFACT_V1 = "G5_09_PGSP_WORKER_ORCHESTRATION_CONTEXT_ARTIFACT_V1"
PGSP_WORKER_ORCHESTRATION_SUMMARY_ARTIFACT_V1 = "G5_09_PGSP_WORKER_ORCHESTRATION_SUMMARY_ARTIFACT_V1"

PGSP_WORKER_ORCHESTRATION_COMPLETED = "G5_09_PGSP_WORKER_ORCHESTRATION_COMPLETED"
PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED = "G5_09_PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED"

REPLAY_STEPS = (
    "pgsp_worker_orchestration_context_recorded",
    "pgsp_worker_orchestration_summary_recorded",
)


def run_g5_pgsp_worker_runtime_orchestration(
    *,
    session_id: str,
    execution_authorization_replay_reference: str,
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    worker_registry_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run a PGSP-owned orchestration over the existing Worker runtime stack."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    context = _context_artifact(
        session_id=session_id,
        execution_authorization_replay_reference=execution_authorization_replay_reference,
        requested_by=requested_by,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], context)

    try:
        captures = _run_worker_stack(
            session_id=context["session_id"],
            execution_authorization_replay_reference=context["execution_authorization_replay_reference"],
            requested_by=context["requested_by"],
            created_at=context["created_at"],
            replay_path=replay_path,
            worker_registry_artifacts=worker_registry_artifacts,
        )
        summary = _summary_artifact(
            session_id=context["session_id"],
            context=context,
            captures=captures,
            status=PGSP_WORKER_ORCHESTRATION_COMPLETED,
            failure_reason=None,
            created_at=context["created_at"],
            replay_reference=str(replay_path),
        )
    except Exception as exc:
        summary = _summary_artifact(
            session_id=context["session_id"],
            context=context,
            captures={},
            status=PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
            created_at=context["created_at"],
            replay_reference=str(replay_path),
        )

    _persist_step(replay_path, 1, REPLAY_STEPS[1], summary)
    return _capture(summary, replay_path)


def reconstruct_g5_pgsp_worker_orchestration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct a G5-09 PGSP Worker orchestration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G5-09 PGSP Worker orchestration replay ordering mismatch")
        _verify_hash(wrapper, "replay_hash", "G5-09 PGSP Worker orchestration replay hash mismatch")
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_hash(artifact, "artifact_hash", "G5-09 PGSP Worker orchestration artifact hash mismatch")
        _validate_boundary_flags(artifact)
        wrappers.append(wrapper)

    context = wrappers[0]["artifact"]
    summary = wrappers[1]["artifact"]
    if summary["context_hash"] != context["artifact_hash"]:
        raise FailClosedRuntimeError("G5-09 PGSP Worker orchestration context lineage mismatch")
    if summary["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_COMPLETED:
        nested = summary["nested_replay_references"]
        reconstructed = {
            "worker_invocation_request": reconstruct_worker_invocation_request_replay(nested["worker_invocation_request"]),
            "worker_assignment": reconstruct_worker_assignment_runtime_replay(nested["worker_assignment"]),
            "worker_dispatch": reconstruct_worker_dispatch_replay(nested["worker_dispatch"]),
            "worker_invocation": reconstruct_worker_invocation_replay(nested["worker_invocation"]),
            "execution": reconstruct_execution_replay(nested["execution"]),
            "worker_result_capture": reconstruct_worker_result_capture_replay(nested["worker_result_capture"]),
            "worker_result_validation": reconstruct_worker_result_validation_replay(nested["worker_result_validation"]),
            "post_execution_replay_review": reconstruct_post_execution_replay_review(nested["post_execution_replay_review"]),
        }
        if replay_hash(reconstructed) != summary["nested_replay_reconstruction_hash"]:
            raise FailClosedRuntimeError("G5-09 PGSP Worker orchestration nested replay hash mismatch")

    return {
        "runtime_version": G5_09_RUNTIME_VERSION,
        "session_id": summary["session_id"],
        "orchestration_status": summary["orchestration_status"],
        "worker_invocation_request_status": summary["worker_invocation_request_status"],
        "worker_assignment_status": summary["worker_assignment_status"],
        "worker_dispatch_status": summary["worker_dispatch_status"],
        "worker_invocation_status": summary["worker_invocation_status"],
        "execution_status": summary["execution_status"],
        "result_capture_status": summary["result_capture_status"],
        "result_validation_status": summary["result_validation_status"],
        "post_execution_review_status": summary["post_execution_review_status"],
        "governance_checkpoint_status": summary["governance_checkpoint_status"],
        "uhcl_summary_status": summary["uhcl_summary_status"],
        "worker_runtime_reused": True,
        "worker_architecture_created": False,
        "duplicate_worker_authorization_created": False,
        "duplicate_worker_replay_created": False,
        "duplicate_worker_identity_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "replay_reference": str(replay_path),
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": summary["failure_reason"],
    }


def _run_worker_stack(
    *,
    session_id: str,
    execution_authorization_replay_reference: str,
    requested_by: str,
    created_at: str,
    replay_path: Path,
    worker_registry_artifacts: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    request = create_worker_invocation_request(
        invocation_request_id=f"{session_id}:WORKER-INVOCATION-REQUEST",
        execution_authorization_replay_reference=execution_authorization_replay_reference,
        requested_by=requested_by,
        requested_at=created_at,
        replay_dir=replay_path / "worker_invocation_request",
    )
    _require_status(request, "request_status", WORKER_INVOCATION_REQUEST_CREATED)
    registry = (
        deepcopy(worker_registry_artifacts)
        if worker_registry_artifacts is not None
        else default_worker_registry_for_request(request["worker_invocation_request_artifact"], created_at=created_at)
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id=f"{session_id}:WORKER-ASSIGNMENT",
        worker_invocation_request_artifact=request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=registry,
        assigned_by=requested_by,
        assigned_at=created_at,
        replay_dir=replay_path / "worker_assignment",
    )
    _require_status(assignment, "assignment_status", WORKER_ASSIGNED)
    dispatch = dispatch_assigned_worker(
        worker_dispatch_id=f"{session_id}:WORKER-DISPATCH",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by=requested_by,
        dispatched_at=created_at,
        replay_dir=replay_path / "worker_dispatch",
    )
    _require_status(dispatch, "dispatch_status", WORKER_DISPATCHED)
    invocation = invoke_dispatched_worker(
        worker_invocation_id=f"{session_id}:WORKER-INVOCATION",
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by=requested_by,
        invoked_at=created_at,
        replay_dir=replay_path / "worker_invocation",
    )
    _require_status(invocation, "invocation_status", WORKER_INVOKED)
    execution = start_execution(
        execution_id=f"{session_id}:WORKER-EXECUTION",
        invocation_artifact=invocation["worker_invocation_artifact"],
        invocation_replay=invocation["invocation_result_artifact"],
        dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        canonical_chain_id=invocation["worker_invocation_artifact"]["chain_id"],
        execution_metadata={"pgsp_runtime": G5_09_RUNTIME_VERSION, "worker_runtime_reused": True},
        execution_context={
            "session_id": session_id,
            "authorization_replay": execution_authorization_replay_reference,
            "requested_by": requested_by,
        },
        started_by="AIGOL",
        started_at=created_at,
        replay_reference=str(replay_path / "execution"),
        replay_dir=replay_path / "execution",
    )
    worker_output = default_worker_output_for_invocation(
        invocation["worker_invocation_artifact"],
        captured_at=created_at,
    )
    result_capture = capture_worker_result(
        worker_result_capture_id=f"{session_id}:WORKER-RESULT-CAPTURE",
        worker_invocation_artifact=invocation["worker_invocation_artifact"],
        worker_invocation_replay_reference=invocation["worker_invocation_replay_reference"],
        worker_output=worker_output,
        captured_by=requested_by,
        captured_at=created_at,
        replay_dir=replay_path / "worker_result_capture",
        execution_artifact=execution["execution_artifact"],
        execution_replay=execution["execution_replay"],
        execution_replay_reference=str(replay_path / "execution"),
    )
    _require_status(result_capture, "result_capture_status", WORKER_RESULT_CAPTURED)
    result_validation = validate_worker_result(
        worker_result_validation_id=f"{session_id}:WORKER-RESULT-VALIDATION",
        worker_result_capture_artifact=result_capture["worker_result_capture_artifact"],
        worker_result_capture_replay_reference=result_capture["worker_result_capture_replay_reference"],
        validated_by=requested_by,
        validated_at=created_at,
        replay_dir=replay_path / "worker_result_validation",
    )
    _require_status(result_validation, "validation_status", RESULT_VALIDATED)
    post_review = review_validated_worker_result(
        post_execution_replay_review_id=f"{session_id}:POST-EXECUTION-REPLAY-REVIEW",
        worker_result_validation_artifact=result_validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=result_validation["worker_result_validation_replay_reference"],
        reviewed_by=requested_by,
        reviewed_at=created_at,
        replay_dir=replay_path / "post_execution_replay_review",
    )
    _require_status(post_review, "review_status", REVIEW_COMPLETED)
    return {
        "worker_invocation_request": request,
        "worker_assignment": assignment,
        "worker_dispatch": dispatch,
        "worker_invocation": invocation,
        "execution": execution,
        "worker_result_capture": result_capture,
        "worker_result_validation": result_validation,
        "post_execution_replay_review": post_review,
    }


def _context_artifact(
    *,
    session_id: str,
    execution_authorization_replay_reference: str,
    requested_by: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_WORKER_ORCHESTRATION_CONTEXT_ARTIFACT_V1,
            "runtime_version": G5_09_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "execution_authorization_replay_reference": _require_string(
                execution_authorization_replay_reference,
                "execution_authorization_replay_reference",
            ),
            "requested_by": _require_string(requested_by, "requested_by"),
            "created_at": _require_string(created_at, "created_at"),
            "worker_runtime_reused": True,
            "worker_architecture_created": False,
        }
    )
    return _with_hash(artifact)


def _summary_artifact(
    *,
    session_id: str,
    context: dict[str, Any],
    captures: dict[str, Any],
    status: str,
    failure_reason: str | None,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    nested_replays = _nested_replay_references(captures)
    nested_reconstruction = _nested_reconstruction(nested_replays) if nested_replays else {}
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_WORKER_ORCHESTRATION_SUMMARY_ARTIFACT_V1,
            "runtime_version": G5_09_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "context_hash": context["artifact_hash"],
            "orchestration_status": status,
            "worker_invocation_request_status": _capture_value(captures, "worker_invocation_request", "request_status"),
            "worker_assignment_status": _capture_value(captures, "worker_assignment", "assignment_status"),
            "worker_dispatch_status": _capture_value(captures, "worker_dispatch", "dispatch_status"),
            "worker_invocation_status": _capture_value(captures, "worker_invocation", "invocation_status"),
            "execution_status": _capture_value(captures, "execution", "execution_artifact", "execution_status"),
            "result_capture_status": _capture_value(captures, "worker_result_capture", "result_capture_status"),
            "result_validation_status": _capture_value(captures, "worker_result_validation", "validation_status"),
            "post_execution_review_status": _capture_value(captures, "post_execution_replay_review", "review_status"),
            "governance_checkpoint_status": (
                "G5_09_PGSP_WORKER_ORCHESTRATION_GOVERNANCE_PASSED"
                if status == PGSP_WORKER_ORCHESTRATION_COMPLETED
                else "G5_09_PGSP_WORKER_ORCHESTRATION_GOVERNANCE_FAILED_CLOSED"
            ),
            "uhcl_summary_status": (
                "G5_09_UHCL_WORKER_EXECUTION_SUMMARY_AVAILABLE"
                if status == PGSP_WORKER_ORCHESTRATION_COMPLETED
                else "G5_09_UHCL_WORKER_EXECUTION_SUMMARY_FAILED_CLOSED"
            ),
            "nested_replay_references": nested_replays,
            "nested_replay_reconstruction_hash": replay_hash(nested_reconstruction),
            "worker_runtime_reused": True,
            "worker_architecture_created": False,
            "duplicate_worker_authorization_created": False,
            "duplicate_worker_replay_created": False,
            "duplicate_worker_identity_created": False,
            "created_at": _require_string(created_at, "created_at"),
            "replay_reference": _require_string(replay_reference, "replay_reference"),
            "failure_reason": failure_reason,
        }
    )
    return _with_hash(artifact)


def _capture(summary: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": G5_09_RUNTIME_VERSION,
        "session_id": summary["session_id"],
        "orchestration_status": summary["orchestration_status"],
        "worker_invocation_request_status": summary["worker_invocation_request_status"],
        "worker_assignment_status": summary["worker_assignment_status"],
        "worker_dispatch_status": summary["worker_dispatch_status"],
        "worker_invocation_status": summary["worker_invocation_status"],
        "execution_status": summary["execution_status"],
        "result_capture_status": summary["result_capture_status"],
        "result_validation_status": summary["result_validation_status"],
        "post_execution_review_status": summary["post_execution_review_status"],
        "governance_checkpoint_status": summary["governance_checkpoint_status"],
        "uhcl_summary_status": summary["uhcl_summary_status"],
        "worker_runtime_reused": True,
        "worker_architecture_created": False,
        "duplicate_worker_authorization_created": False,
        "duplicate_worker_replay_created": False,
        "duplicate_worker_identity_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "summary_artifact": deepcopy(summary),
        "summary_hash": summary["artifact_hash"],
        "replay_reference": str(replay_path),
        "failure_reason": summary["failure_reason"],
        "replay_visible": True,
    }


def _nested_replay_references(captures: dict[str, Any]) -> dict[str, str]:
    if not captures:
        return {}
    return {
        "worker_invocation_request": captures["worker_invocation_request"]["worker_invocation_request_replay_reference"],
        "worker_assignment": captures["worker_assignment"]["worker_assignment_replay_reference"],
        "worker_dispatch": captures["worker_dispatch"]["worker_dispatch_replay_reference"],
        "worker_invocation": captures["worker_invocation"]["worker_invocation_replay_reference"],
        "execution": captures["execution"]["execution_artifact"]["replay_reference"],
        "worker_result_capture": captures["worker_result_capture"]["worker_result_capture_replay_reference"],
        "worker_result_validation": captures["worker_result_validation"]["worker_result_validation_replay_reference"],
        "post_execution_replay_review": captures["post_execution_replay_review"][
            "post_execution_replay_review_replay_reference"
        ],
    }


def _nested_reconstruction(nested_replays: dict[str, str]) -> dict[str, Any]:
    return {
        "worker_invocation_request": reconstruct_worker_invocation_request_replay(nested_replays["worker_invocation_request"]),
        "worker_assignment": reconstruct_worker_assignment_runtime_replay(nested_replays["worker_assignment"]),
        "worker_dispatch": reconstruct_worker_dispatch_replay(nested_replays["worker_dispatch"]),
        "worker_invocation": reconstruct_worker_invocation_replay(nested_replays["worker_invocation"]),
        "execution": reconstruct_execution_replay(nested_replays["execution"]),
        "worker_result_capture": reconstruct_worker_result_capture_replay(nested_replays["worker_result_capture"]),
        "worker_result_validation": reconstruct_worker_result_validation_replay(nested_replays["worker_result_validation"]),
        "post_execution_replay_review": reconstruct_post_execution_replay_review(nested_replays["post_execution_replay_review"]),
    }


def _base_artifact(values: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "provider_invoked": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "worker_self_authorized": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
    }
    artifact.update(values)
    if values.get("artifact_type") == PGSP_WORKER_ORCHESTRATION_SUMMARY_ARTIFACT_V1:
        artifact["worker_assigned"] = values.get("worker_assignment_status") == WORKER_ASSIGNED
        artifact["worker_dispatched"] = values.get("worker_dispatch_status") == WORKER_DISPATCHED
        artifact["worker_invoked"] = values.get("worker_invocation_status") == WORKER_INVOKED
        artifact["execution_started"] = values.get("execution_status") == "EXECUTING"
    return artifact


def _with_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(artifact)
    result["artifact_hash"] = replay_hash(result)
    return result


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("G5-09 PGSP Worker orchestration failed closed: replay directory already contains artifacts")
    replay_path.mkdir(parents=True, exist_ok=True)


def _validate_boundary_flags(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "repository_mutated",
        "deployment_performed",
        "retry_performed",
        "fallback_performed",
        "worker_self_authorized",
        "governance_mutated",
        "replay_mutated",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G5-09 PGSP Worker orchestration failed closed: {field} must be false")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("G5-09 PGSP Worker orchestration failed closed: replay must be visible")


def _verify_hash(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _require_status(capture: dict[str, Any], field_name: str, expected: str) -> None:
    if capture.get(field_name) != expected:
        failure_reason = capture.get("failure_reason")
        if isinstance(failure_reason, str) and failure_reason:
            raise FailClosedRuntimeError(failure_reason)
        raise FailClosedRuntimeError(
            f"G5-09 PGSP Worker orchestration failed closed: {field_name}={capture.get(field_name)}"
        )


def _capture_value(captures: dict[str, Any], *keys: str) -> str | None:
    value: Any = captures
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value if isinstance(value, str) else None


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"G5-09 PGSP Worker orchestration failed closed: {field_name} must be object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G5-09 PGSP Worker orchestration failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__
