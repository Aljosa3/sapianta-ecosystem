"""Governed worker request to dispatch candidate runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    WORKER_REQUEST_ARTIFACT_V1,
    WORKER_REQUEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_WORKER_REQUEST_TO_WORKER_DISPATCH_GOVERNANCE_VERSION = (
    "AIGOL_WORKER_REQUEST_TO_WORKER_DISPATCH_GOVERNANCE_V1"
)
WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1 = "WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1"
WORKER_DISPATCH_CANDIDATE_CREATED = "WORKER_DISPATCH_CANDIDATE_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "worker_dispatch_candidate_recorded",
    "worker_dispatch_candidate_returned",
)

DEFAULT_EXECUTION_CONSTRAINTS = {
    "dispatch_allowed": False,
    "worker_invocation_allowed": False,
    "implementation_execution_allowed": False,
    "provider_invocation_allowed": False,
    "code_modification_allowed": False,
    "governance_modification_allowed": False,
    "human_approval_required": True,
}

DEFAULT_GOVERNANCE_CONSTRAINTS = {
    "human_authority_required": True,
    "dispatch_requires_separate_governance": True,
    "worker_invocation_requires_separate_governance": True,
    "execution_requires_separate_authorization": True,
    "replay_lineage_required": True,
    "fail_closed_required": True,
}


def create_worker_dispatch_candidate(
    *,
    candidate_id: str,
    worker_request_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    execution_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert an approved worker request into a dispatch candidate without dispatching a worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        worker_request = deepcopy(worker_request_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_worker_request(worker_request)
        _validate_human_approval(approval, worker_request)
        candidate = _dispatch_candidate_artifact(
            candidate_id=candidate_id,
            worker_request=worker_request,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            execution_constraints=execution_constraints,
            candidate_status=WORKER_DISPATCH_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(candidate)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_dispatch_candidate_artifact(
            candidate_id=candidate_id,
            worker_request_artifact=worker_request_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(candidate)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)


def reconstruct_worker_request_to_worker_dispatch_governance_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate worker request to dispatch candidate replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker request to dispatch candidate replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker request to dispatch candidate artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    candidate = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("dispatch_candidate_reference") != candidate["dispatch_candidate_id"]:
        raise FailClosedRuntimeError("worker request to dispatch candidate returned reference mismatch")
    if returned.get("dispatch_candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("worker request to dispatch candidate returned hash mismatch")
    return {
        "dispatch_candidate_id": candidate["dispatch_candidate_id"],
        "candidate_status": candidate["candidate_status"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "source_ppp_candidate": candidate["source_ppp_candidate"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "dispatch_prevented": candidate["dispatch_requested"] is False
        and candidate["worker_dispatched"] is False
        and candidate["worker_invoked"] is False
        and candidate["implementation_executed"] is False,
        "ready_for_worker_invocation_governance": candidate["ready_for_worker_invocation_governance"],
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_worker_request(worker_request: dict[str, Any]) -> None:
    _validate_artifact(worker_request)
    if worker_request.get("artifact_type") != WORKER_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: invalid artifact type")
    if worker_request.get("request_status") != WORKER_REQUEST_CREATED:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: certified worker request required")
    if worker_request.get("certification_status") != "CERTIFIED_IMPLEMENTATION_REQUEST_ACCEPTED":
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: certification validation failed")
    if worker_request.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: replay lineage broken")
    if worker_request.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: human approval required")
    if worker_request.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: human authority missing")
    if worker_request.get("ready_for_worker_dispatch_governance") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: request is not dispatch-ready")
    _require_string(worker_request.get("source_implementation_request"), "source_implementation_request")
    _require_hash(worker_request.get("source_implementation_request_hash"), "source_implementation_request_hash")
    _require_string(worker_request.get("source_ppp_candidate"), "source_ppp_candidate")
    _require_hash(worker_request.get("source_ppp_candidate_hash"), "source_ppp_candidate_hash")
    if not _string_list(worker_request.get("replay_references")):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: replay references required")
    if not _hash_list(worker_request.get("replay_hashes")):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: replay hashes required")
    constraints = worker_request.get("worker_constraints")
    if not isinstance(constraints, dict) or constraints.get("dispatch_allowed") is not False:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: worker constraints invalid")
    requirements = worker_request.get("governance_requirements")
    if not isinstance(requirements, dict) or requirements.get("dispatch_requires_separate_governance") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: governance requirements invalid")
    for flag in (
        "worker_dispatched",
        "worker_invoked",
        "implementation_executed",
        "provider_invoked",
        "code_modified",
        "governance_modified",
        "authorization_created",
        "execution_requested",
        "dispatch_requested",
    ):
        if worker_request.get(flag) is not False:
            raise FailClosedRuntimeError(f"worker request to dispatch candidate failed closed: request {flag} must be false")


def _validate_human_approval(approval: dict[str, Any], worker_request: dict[str, Any]) -> None:
    _validate_artifact(approval)
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: explicit human approval required")
    if approval.get("source_worker_request") != worker_request.get("worker_request_id"):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: approval worker request mismatch")
    if approval.get("source_worker_request_hash") != worker_request.get("artifact_hash"):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: approval worker request hash mismatch")
    if approval.get("approval_scope") != "CREATE_WORKER_DISPATCH_CANDIDATE_ONLY":
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: approval scope invalid")
    if approval.get("worker_dispatch_allowed") is not False:
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: approval scope exceeds candidate")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _dispatch_candidate_artifact(
    *,
    candidate_id: str,
    worker_request: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    execution_constraints: dict[str, Any] | None,
    candidate_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    constraints = _execution_constraints(execution_constraints)
    artifact = {
        "artifact_type": WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_REQUEST_TO_WORKER_DISPATCH_GOVERNANCE_VERSION,
        "dispatch_candidate_id": _require_string(candidate_id, "candidate_id"),
        "candidate_status": candidate_status,
        "source_worker_request": worker_request["worker_request_id"],
        "source_worker_request_hash": worker_request["artifact_hash"],
        "source_implementation_request": worker_request["source_implementation_request"],
        "source_implementation_request_hash": worker_request["source_implementation_request_hash"],
        "source_ppp_candidate": worker_request["source_ppp_candidate"],
        "source_ppp_candidate_hash": worker_request["source_ppp_candidate_hash"],
        "source_improvement_intent": worker_request["source_improvement_intent"],
        "source_improvement_intent_hash": worker_request["source_improvement_intent_hash"],
        "source_gap_artifact": worker_request["source_gap_artifact"],
        "source_gap_hash": worker_request["source_gap_hash"],
        "replay_references": deepcopy(worker_request["replay_references"]),
        "replay_hashes": deepcopy(worker_request["replay_hashes"]),
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "human_approval_required": True,
        "human_approval_granted": True,
        "human_authority_preserved": True,
        "worker_objective": worker_request["worker_objective"],
        "execution_constraints": constraints,
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": deepcopy(worker_request["governance_classification"]),
        "affected_runtime": worker_request["affected_runtime"],
        "affected_lifecycle_stage": worker_request["affected_lifecycle_stage"],
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "certification_status": "CERTIFIED_WORKER_REQUEST_ACCEPTED",
        "replay_lineage_preserved": True,
        "ready_for_worker_invocation_governance": True,
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_dispatch_candidate_artifact(
    *,
    candidate_id: str,
    worker_request_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_REQUEST_TO_WORKER_DISPATCH_GOVERNANCE_VERSION,
        "dispatch_candidate_id": candidate_id if isinstance(candidate_id, str) else "INVALID",
        "candidate_status": FAILED_CLOSED,
        "source_worker_request": worker_request_artifact.get("worker_request_id")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_worker_request_hash": worker_request_artifact.get("artifact_hash")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_implementation_request": worker_request_artifact.get("source_implementation_request")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_implementation_request_hash": worker_request_artifact.get("source_implementation_request_hash")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_ppp_candidate": worker_request_artifact.get("source_ppp_candidate")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_ppp_candidate_hash": worker_request_artifact.get("source_ppp_candidate_hash")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_improvement_intent": worker_request_artifact.get("source_improvement_intent")
        if isinstance(worker_request_artifact, dict)
        else None,
        "source_gap_artifact": worker_request_artifact.get("source_gap_artifact")
        if isinstance(worker_request_artifact, dict)
        else None,
        "replay_references": [],
        "replay_hashes": [],
        "human_approval_reference": human_approval_artifact.get("approval_id")
        if isinstance(human_approval_artifact, dict)
        else None,
        "human_approval_hash": human_approval_artifact.get("artifact_hash")
        if isinstance(human_approval_artifact, dict)
        else None,
        "human_approval_required": True,
        "human_approval_granted": False,
        "human_authority_preserved": True,
        "worker_objective": None,
        "execution_constraints": deepcopy(DEFAULT_EXECUTION_CONSTRAINTS),
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": {},
        "affected_runtime": None,
        "affected_lifecycle_stage": None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "certification_status": FAILED_CLOSED,
        "replay_lineage_preserved": False,
        "ready_for_worker_invocation_governance": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(candidate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(candidate)
    artifact = {
        "event_type": "WORKER_DISPATCH_CANDIDATE_RETURNED",
        "dispatch_candidate_reference": candidate["dispatch_candidate_id"],
        "dispatch_candidate_hash": candidate["artifact_hash"],
        "candidate_status": candidate["candidate_status"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "source_ppp_candidate": candidate["source_ppp_candidate"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "ready_for_worker_invocation_governance": candidate["ready_for_worker_invocation_governance"],
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": candidate["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(candidate: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_WORKER_REQUEST_TO_WORKER_DISPATCH_GOVERNANCE_VERSION,
        "candidate_status": candidate["candidate_status"],
        "worker_dispatch_candidate_artifact": deepcopy(candidate),
        "worker_dispatch_candidate_returned_artifact": deepcopy(returned),
        "worker_dispatch_candidate_replay_reference": str(replay_path),
        "worker_dispatch_candidate_generated": candidate["candidate_status"] == WORKER_DISPATCH_CANDIDATE_CREATED,
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "dispatch_prevented": candidate["dispatch_requested"] is False
        and candidate["worker_dispatched"] is False
        and candidate["worker_invoked"] is False
        and candidate["implementation_executed"] is False,
        "ready_for_worker_invocation_governance": candidate["ready_for_worker_invocation_governance"],
        "failure_reason": candidate["failure_reason"],
    }
    capture["worker_request_to_dispatch_candidate_capture_hash"] = replay_hash(capture)
    return capture


def _execution_constraints(execution_constraints: dict[str, Any] | None) -> dict[str, Any]:
    constraints = deepcopy(DEFAULT_EXECUTION_CONSTRAINTS)
    if execution_constraints is None:
        return constraints
    if not isinstance(execution_constraints, dict):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: execution constraints invalid")
    forbidden_true = {
        "dispatch_allowed",
        "worker_invocation_allowed",
        "implementation_execution_allowed",
        "provider_invocation_allowed",
        "code_modification_allowed",
        "governance_modification_allowed",
    }
    for key, value in execution_constraints.items():
        if key in forbidden_true and value is not False:
            raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: execution constraints exceed bridge")
        constraints[key] = deepcopy(value)
    return constraints


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("worker request to dispatch candidate failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("worker request to dispatch candidate artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("worker request to dispatch candidate artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("worker request to dispatch candidate replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("worker request to dispatch candidate replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker request to dispatch candidate failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"worker request to dispatch candidate failed closed: {field_name} must be a replay hash")
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _hash_list(value: Any) -> list[str]:
    return [item for item in _string_list(value) if item.startswith("sha256:")]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "worker request to dispatch candidate failed closed"
