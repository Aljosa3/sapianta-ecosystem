"""Governed dispatch candidate to worker invocation candidate runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_request_to_worker_dispatch_governance_runtime import (
    WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1,
    WORKER_DISPATCH_CANDIDATE_CREATED,
)


AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_VERSION = (
    "AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_V1"
)
WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1 = "WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1"
WORKER_INVOCATION_CANDIDATE_CREATED = "WORKER_INVOCATION_CANDIDATE_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "worker_invocation_candidate_recorded",
    "worker_invocation_candidate_returned",
)

DEFAULT_INVOCATION_CONSTRAINTS = {
    "worker_invocation_allowed": False,
    "implementation_execution_allowed": False,
    "provider_invocation_allowed": False,
    "code_modification_allowed": False,
    "governance_modification_allowed": False,
    "human_approval_required": True,
}

DEFAULT_GOVERNANCE_CONSTRAINTS = {
    "human_authority_required": True,
    "worker_invocation_requires_separate_governance": True,
    "execution_requires_separate_authorization": True,
    "replay_lineage_required": True,
    "fail_closed_required": True,
}


def create_worker_invocation_candidate(
    *,
    candidate_id: str,
    dispatch_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    invocation_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert an approved dispatch candidate into an invocation candidate without invoking a worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        dispatch_candidate = deepcopy(dispatch_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_dispatch_candidate(dispatch_candidate)
        _validate_human_approval(approval, dispatch_candidate)
        candidate = _invocation_candidate_artifact(
            candidate_id=candidate_id,
            dispatch_candidate=dispatch_candidate,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            invocation_constraints=invocation_constraints,
            candidate_status=WORKER_INVOCATION_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(candidate)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_invocation_candidate_artifact(
            candidate_id=candidate_id,
            dispatch_candidate_artifact=dispatch_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(candidate)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)


def reconstruct_worker_dispatch_to_worker_invocation_governance_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate dispatch candidate to invocation candidate replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("dispatch candidate to invocation candidate replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("dispatch candidate to invocation candidate artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    candidate = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("invocation_candidate_reference") != candidate["invocation_candidate_id"]:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate returned reference mismatch")
    if returned.get("invocation_candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate returned hash mismatch")
    return {
        "invocation_candidate_id": candidate["invocation_candidate_id"],
        "candidate_status": candidate["candidate_status"],
        "source_dispatch_candidate": candidate["source_dispatch_candidate"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "invocation_prevented": candidate["worker_invoked"] is False
        and candidate["implementation_executed"] is False
        and candidate["execution_requested"] is False,
        "ready_for_worker_execution_governance": candidate["ready_for_worker_execution_governance"],
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_dispatch_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate)
    if candidate.get("artifact_type") != WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: invalid artifact type")
    if candidate.get("candidate_status") != WORKER_DISPATCH_CANDIDATE_CREATED:
        raise FailClosedRuntimeError(
            "dispatch candidate to invocation candidate failed closed: certified dispatch candidate required"
        )
    if candidate.get("certification_status") != "CERTIFIED_WORKER_REQUEST_ACCEPTED":
        raise FailClosedRuntimeError(
            "dispatch candidate to invocation candidate failed closed: certification validation failed"
        )
    if candidate.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: replay lineage broken")
    if candidate.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: human approval required")
    if candidate.get("human_approval_granted") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: human approval chain required")
    if candidate.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: human authority missing")
    if candidate.get("ready_for_worker_invocation_governance") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: candidate is not ready")
    _require_string(candidate.get("source_worker_request"), "source_worker_request")
    _require_hash(candidate.get("source_worker_request_hash"), "source_worker_request_hash")
    _require_string(candidate.get("source_implementation_request"), "source_implementation_request")
    _require_hash(candidate.get("source_implementation_request_hash"), "source_implementation_request_hash")
    if not _string_list(candidate.get("replay_references")):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: replay references required")
    if not _hash_list(candidate.get("replay_hashes")):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: replay hashes required")
    constraints = candidate.get("execution_constraints")
    if not isinstance(constraints, dict) or constraints.get("worker_invocation_allowed") is not False:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: execution constraints invalid")
    governance = candidate.get("governance_constraints")
    if not isinstance(governance, dict) or governance.get("worker_invocation_requires_separate_governance") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: governance constraints invalid")
    for flag in (
        "worker_invoked",
        "implementation_executed",
        "provider_invoked",
        "code_modified",
        "governance_modified",
        "authorization_created",
        "execution_requested",
    ):
        if candidate.get(flag) is not False:
            raise FailClosedRuntimeError(
                f"dispatch candidate to invocation candidate failed closed: candidate {flag} must be false"
            )


def _validate_human_approval(approval: dict[str, Any], dispatch_candidate: dict[str, Any]) -> None:
    _validate_artifact(approval)
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: explicit human approval required")
    if approval.get("source_dispatch_candidate") != dispatch_candidate.get("dispatch_candidate_id"):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: approval candidate mismatch")
    if approval.get("source_dispatch_candidate_hash") != dispatch_candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: approval candidate hash mismatch")
    if approval.get("approval_scope") != "CREATE_WORKER_INVOCATION_CANDIDATE_ONLY":
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: approval scope invalid")
    if approval.get("worker_invocation_allowed") is not False:
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: approval scope exceeds candidate")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _invocation_candidate_artifact(
    *,
    candidate_id: str,
    dispatch_candidate: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    invocation_constraints: dict[str, Any] | None,
    candidate_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    constraints = _invocation_constraints(invocation_constraints)
    artifact = {
        "artifact_type": WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_VERSION,
        "invocation_candidate_id": _require_string(candidate_id, "candidate_id"),
        "candidate_status": candidate_status,
        "source_dispatch_candidate": dispatch_candidate["dispatch_candidate_id"],
        "source_dispatch_candidate_hash": dispatch_candidate["artifact_hash"],
        "source_worker_request": dispatch_candidate["source_worker_request"],
        "source_worker_request_hash": dispatch_candidate["source_worker_request_hash"],
        "source_implementation_request": dispatch_candidate["source_implementation_request"],
        "source_implementation_request_hash": dispatch_candidate["source_implementation_request_hash"],
        "source_ppp_candidate": dispatch_candidate["source_ppp_candidate"],
        "source_ppp_candidate_hash": dispatch_candidate["source_ppp_candidate_hash"],
        "replay_references": deepcopy(dispatch_candidate["replay_references"]),
        "replay_hashes": deepcopy(dispatch_candidate["replay_hashes"]),
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "human_approval_required": True,
        "human_approval_granted": True,
        "human_authority_preserved": True,
        "worker_objective": dispatch_candidate["worker_objective"],
        "invocation_constraints": constraints,
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": deepcopy(dispatch_candidate["governance_classification"]),
        "affected_runtime": dispatch_candidate["affected_runtime"],
        "affected_lifecycle_stage": dispatch_candidate["affected_lifecycle_stage"],
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "certification_status": "CERTIFIED_WORKER_DISPATCH_CANDIDATE_ACCEPTED",
        "replay_lineage_preserved": True,
        "ready_for_worker_execution_governance": True,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_invocation_candidate_artifact(
    *,
    candidate_id: str,
    dispatch_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_VERSION,
        "invocation_candidate_id": candidate_id if isinstance(candidate_id, str) else "INVALID",
        "candidate_status": FAILED_CLOSED,
        "source_dispatch_candidate": dispatch_candidate_artifact.get("dispatch_candidate_id")
        if isinstance(dispatch_candidate_artifact, dict)
        else None,
        "source_dispatch_candidate_hash": dispatch_candidate_artifact.get("artifact_hash")
        if isinstance(dispatch_candidate_artifact, dict)
        else None,
        "source_worker_request": dispatch_candidate_artifact.get("source_worker_request")
        if isinstance(dispatch_candidate_artifact, dict)
        else None,
        "source_implementation_request": dispatch_candidate_artifact.get("source_implementation_request")
        if isinstance(dispatch_candidate_artifact, dict)
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
        "invocation_constraints": deepcopy(DEFAULT_INVOCATION_CONSTRAINTS),
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": {},
        "affected_runtime": None,
        "affected_lifecycle_stage": None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "certification_status": FAILED_CLOSED,
        "replay_lineage_preserved": False,
        "ready_for_worker_execution_governance": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(candidate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(candidate)
    artifact = {
        "event_type": "WORKER_INVOCATION_CANDIDATE_RETURNED",
        "invocation_candidate_reference": candidate["invocation_candidate_id"],
        "invocation_candidate_hash": candidate["artifact_hash"],
        "candidate_status": candidate["candidate_status"],
        "source_dispatch_candidate": candidate["source_dispatch_candidate"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "ready_for_worker_execution_governance": candidate["ready_for_worker_execution_governance"],
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": candidate["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(candidate: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_VERSION,
        "candidate_status": candidate["candidate_status"],
        "worker_invocation_candidate_artifact": deepcopy(candidate),
        "worker_invocation_candidate_returned_artifact": deepcopy(returned),
        "worker_invocation_candidate_replay_reference": str(replay_path),
        "worker_invocation_candidate_generated": candidate["candidate_status"] == WORKER_INVOCATION_CANDIDATE_CREATED,
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "invocation_prevented": candidate["worker_invoked"] is False
        and candidate["implementation_executed"] is False
        and candidate["execution_requested"] is False,
        "ready_for_worker_execution_governance": candidate["ready_for_worker_execution_governance"],
        "failure_reason": candidate["failure_reason"],
    }
    capture["worker_dispatch_to_invocation_candidate_capture_hash"] = replay_hash(capture)
    return capture


def _invocation_constraints(invocation_constraints: dict[str, Any] | None) -> dict[str, Any]:
    constraints = deepcopy(DEFAULT_INVOCATION_CONSTRAINTS)
    if invocation_constraints is None:
        return constraints
    if not isinstance(invocation_constraints, dict):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: invocation constraints invalid")
    forbidden_true = {
        "worker_invocation_allowed",
        "implementation_execution_allowed",
        "provider_invocation_allowed",
        "code_modification_allowed",
        "governance_modification_allowed",
    }
    for key, value in invocation_constraints.items():
        if key in forbidden_true and value is not False:
            raise FailClosedRuntimeError(
                "dispatch candidate to invocation candidate failed closed: invocation constraints exceed bridge"
            )
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
            raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("dispatch candidate to invocation candidate replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"dispatch candidate to invocation candidate failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"dispatch candidate to invocation candidate failed closed: {field_name} must be a replay hash"
        )
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
    return "dispatch candidate to invocation candidate failed closed"
