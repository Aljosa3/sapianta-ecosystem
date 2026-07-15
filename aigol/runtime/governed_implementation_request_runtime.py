"""Governed implementation request runtime for approved PPP candidates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    PPP_CANDIDATE_ARTIFACT_V1,
    PPP_CANDIDATE_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_VERSION = (
    "AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_V1"
)
IMPLEMENTATION_REQUEST_ARTIFACT_V1 = "IMPLEMENTATION_REQUEST_ARTIFACT_V1"
IMPLEMENTATION_REQUEST_CREATED = "IMPLEMENTATION_REQUEST_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"
HUMAN_APPROVAL_ARTIFACT_V1 = "HUMAN_APPROVAL_ARTIFACT_V1"
APPROVED = "APPROVED"
APPROVED_DURABLE_WORK_PPP_SOURCE = "APPROVED_DURABLE_GOVERNED_WORK"
APPROVED_DURABLE_WORK_PPP_CERTIFICATION = (
    "CERTIFIED_APPROVED_DURABLE_GOVERNED_WORK_ACCEPTED"
)

REPLAY_STEPS = (
    "implementation_request_recorded",
    "implementation_request_returned",
)

DEFAULT_GOVERNANCE_CONSTRAINTS = {
    "human_authority_required": True,
    "implementation_execution_allowed": False,
    "worker_invocation_allowed": False,
    "provider_invocation_allowed": False,
    "code_modification_allowed": False,
    "governance_modification_allowed": False,
    "authorization_artifact_creation_allowed": False,
    "replay_lineage_required": True,
    "fail_closed_required": True,
}


def create_governed_implementation_request(
    *,
    request_id: str,
    ppp_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    implementation_scope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert an explicitly approved PPP candidate into a non-executing implementation request."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        candidate = deepcopy(ppp_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_ppp_candidate(candidate)
        _validate_human_approval(approval, candidate)
        request = _implementation_request_artifact(
            request_id=request_id,
            candidate=candidate,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            implementation_scope=implementation_scope,
            request_status=IMPLEMENTATION_REQUEST_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(request, returned, replay_path)
    except Exception as exc:
        request = _failed_implementation_request_artifact(
            request_id=request_id,
            ppp_candidate_artifact=ppp_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(request)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(request, returned, replay_path)


def reconstruct_governed_implementation_request_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate governed implementation request replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed implementation request replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed implementation request replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("implementation_request_reference") != request["implementation_request_id"]:
        raise FailClosedRuntimeError("governed implementation request returned reference mismatch")
    if returned.get("implementation_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation request returned hash mismatch")
    return {
        "implementation_request_id": request["implementation_request_id"],
        "request_status": request["request_status"],
        "source_ppp_candidate": request["source_ppp_candidate"],
        "source_improvement_intent": request["source_improvement_intent"],
        "source_gap_artifact": request["source_gap_artifact"],
        "replay_lineage_preserved": request["replay_lineage_preserved"],
        "human_approval_required": request["human_approval_required"],
        "implementation_prevented": request["implementation_executed"] is False
        and request["code_modified"] is False
        and request["governance_modified"] is False,
        "ready_for_worker_request_generation": request["ready_for_worker_request_generation"],
        "worker_invoked": False,
        "provider_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_ppp_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "PPP candidate")
    if candidate.get("artifact_type") != PPP_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed implementation request failed closed: invalid artifact type")
    if candidate.get("candidate_status") != PPP_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("governed implementation request failed closed: certified PPP candidate required")
    allowed_certifications = {"CERTIFIED_IMPROVEMENT_INTENT_ACCEPTED"}
    if candidate.get("candidate_source_type") == APPROVED_DURABLE_WORK_PPP_SOURCE:
        allowed_certifications.add(APPROVED_DURABLE_WORK_PPP_CERTIFICATION)
        lineage = candidate.get("source_approved_work_lineage")
        if not isinstance(lineage, dict):
            raise FailClosedRuntimeError(
                "governed implementation request failed closed: approved-work lineage missing"
            )
        for field in (
            "implementation_turn_binding_hash",
            "approval_consumption_hash",
            "development_composition_plan_hash",
            "durable_governed_work_id",
            "durable_governed_work_hash",
            "proposal_preview_hash",
            "approval_request_hash",
        ):
            _require_string(lineage.get(field), field)
        approved_scope = candidate.get("approved_implementation_scope")
        if not isinstance(approved_scope, dict):
            raise FailClosedRuntimeError(
                "governed implementation request failed closed: approved implementation scope missing"
            )
        if candidate.get("approved_implementation_scope_hash") != replay_hash(
            approved_scope
        ):
            raise FailClosedRuntimeError(
                "governed implementation request failed closed: approved implementation scope hash mismatch"
            )
    if candidate.get("certification_status") not in allowed_certifications:
        raise FailClosedRuntimeError("governed implementation request failed closed: certification validation failed")
    if candidate.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("governed implementation request failed closed: replay lineage broken")
    if candidate.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("governed implementation request failed closed: human approval required")
    if candidate.get("ppp_intake_ready") is not True:
        raise FailClosedRuntimeError("governed implementation request failed closed: PPP candidate is not intake ready")
    _require_string(candidate.get("source_improvement_intent"), "source_improvement_intent")
    _require_hash(candidate.get("source_improvement_intent_hash"), "source_improvement_intent_hash")
    _require_string(candidate.get("source_gap_reference"), "source_gap_reference")
    _require_hash(candidate.get("source_gap_hash"), "source_gap_hash")
    if not _string_list(candidate.get("source_replay_references")):
        raise FailClosedRuntimeError("governed implementation request failed closed: replay references required")
    if not _hash_list(candidate.get("source_replay_hashes")):
        raise FailClosedRuntimeError("governed implementation request failed closed: replay hashes required")
    for flag in (
        "proposal_created",
        "ppp_invoked",
        "provider_invoked",
        "worker_invoked",
        "authorization_created",
        "implementation_authorized",
        "implementation_applied",
        "code_modified",
        "governance_modified",
        "execution_requested",
        "dispatch_requested",
    ):
        if candidate.get(flag) is not False:
            raise FailClosedRuntimeError(
                f"governed implementation request failed closed: candidate {flag} must be false"
            )


def _validate_human_approval(approval: dict[str, Any], candidate: dict[str, Any]) -> None:
    _validate_artifact(approval, "human approval")
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed implementation request failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("governed implementation request failed closed: explicit human approval required")
    if approval.get("source_ppp_candidate") != candidate.get("ppp_candidate_id"):
        raise FailClosedRuntimeError("governed implementation request failed closed: approval candidate mismatch")
    if approval.get("source_ppp_candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("governed implementation request failed closed: approval candidate hash mismatch")
    if approval.get("approval_scope") != "CREATE_IMPLEMENTATION_REQUEST_ONLY":
        raise FailClosedRuntimeError("governed implementation request failed closed: approval scope invalid")
    if approval.get("implementation_execution_allowed") is not False:
        raise FailClosedRuntimeError("governed implementation request failed closed: approval scope exceeds request")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _implementation_request_artifact(
    *,
    request_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    implementation_scope: dict[str, Any] | None,
    request_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    scope = _scope(candidate, implementation_scope)
    constraints = deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS)
    artifact = {
        "artifact_type": IMPLEMENTATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_VERSION,
        "implementation_request_id": _require_string(request_id, "request_id"),
        "request_status": request_status,
        "source_ppp_candidate": candidate["ppp_candidate_id"],
        "source_ppp_candidate_hash": candidate["artifact_hash"],
        "source_improvement_intent": candidate["source_improvement_intent"],
        "source_improvement_intent_hash": candidate["source_improvement_intent_hash"],
        "source_gap_artifact": candidate["source_gap_reference"],
        "source_gap_hash": candidate["source_gap_hash"],
        "candidate_source_type": candidate.get("candidate_source_type"),
        "canonical_approved_work_lineage": deepcopy(
            candidate.get("source_approved_work_lineage")
        ),
        "replay_references": deepcopy(candidate["source_replay_references"]),
        "replay_hashes": deepcopy(candidate["source_replay_hashes"]),
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "human_approval_required": True,
        "human_approval_granted": True,
        "human_authority_preserved": True,
        "implementation_objective": candidate["proposal_summary"],
        "implementation_scope": scope,
        "governance_constraints": constraints,
        "governance_classification": deepcopy(candidate["governance_classification"]),
        "affected_runtime": candidate["affected_runtime"],
        "affected_lifecycle_stage": candidate["affected_lifecycle_stage"],
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_lineage_preserved": True,
        "ready_for_worker_request_generation": True,
        "implementation_executed": False,
        "worker_invoked": False,
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


def _failed_implementation_request_artifact(
    *,
    request_id: str,
    ppp_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPLEMENTATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_VERSION,
        "implementation_request_id": request_id if isinstance(request_id, str) else "INVALID",
        "request_status": FAILED_CLOSED,
        "source_ppp_candidate": ppp_candidate_artifact.get("ppp_candidate_id")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "source_ppp_candidate_hash": ppp_candidate_artifact.get("artifact_hash")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "source_improvement_intent": ppp_candidate_artifact.get("source_improvement_intent")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "source_improvement_intent_hash": ppp_candidate_artifact.get("source_improvement_intent_hash")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "source_gap_artifact": ppp_candidate_artifact.get("source_gap_reference")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "source_gap_hash": ppp_candidate_artifact.get("source_gap_hash")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "candidate_source_type": ppp_candidate_artifact.get("candidate_source_type")
        if isinstance(ppp_candidate_artifact, dict)
        else None,
        "canonical_approved_work_lineage": deepcopy(
            ppp_candidate_artifact.get("source_approved_work_lineage")
        )
        if isinstance(ppp_candidate_artifact, dict)
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
        "implementation_objective": None,
        "implementation_scope": {},
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": {},
        "affected_runtime": None,
        "affected_lifecycle_stage": None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "replay_lineage_preserved": False,
        "ready_for_worker_request_generation": False,
        "implementation_executed": False,
        "worker_invoked": False,
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


def _returned_artifact(request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(request)
    artifact = {
        "event_type": "IMPLEMENTATION_REQUEST_RETURNED",
        "implementation_request_reference": request["implementation_request_id"],
        "implementation_request_hash": request["artifact_hash"],
        "request_status": request["request_status"],
        "source_ppp_candidate": request["source_ppp_candidate"],
        "source_improvement_intent": request["source_improvement_intent"],
        "source_gap_artifact": request["source_gap_artifact"],
        "replay_lineage_preserved": request["replay_lineage_preserved"],
        "human_approval_required": request["human_approval_required"],
        "implementation_executed": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "ready_for_worker_request_generation": request["ready_for_worker_request_generation"],
        "replay_visible": True,
        "failure_reason": request["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_VERSION,
        "request_status": request["request_status"],
        "implementation_request_artifact": deepcopy(request),
        "implementation_request_returned_artifact": deepcopy(returned),
        "implementation_request_replay_reference": str(replay_path),
        "implementation_request_artifact_generated": request["request_status"] == IMPLEMENTATION_REQUEST_CREATED,
        "replay_lineage_preserved": request["replay_lineage_preserved"],
        "human_approval_required": request["human_approval_required"],
        "implementation_prevented": request["implementation_executed"] is False
        and request["code_modified"] is False
        and request["governance_modified"] is False,
        "ready_for_worker_request_generation": request["ready_for_worker_request_generation"],
        "failure_reason": request["failure_reason"],
    }
    capture["governed_implementation_request_capture_hash"] = replay_hash(capture)
    return capture


def _scope(candidate: dict[str, Any], implementation_scope: dict[str, Any] | None) -> dict[str, Any]:
    if implementation_scope is None:
        return {
            "objective": candidate["proposal_summary"],
            "affected_runtime": candidate["affected_runtime"],
            "affected_lifecycle_stage": candidate["affected_lifecycle_stage"],
            "affected_domain": candidate["affected_domain"],
            "affected_worker_family": candidate["affected_worker_family"],
            "allowed_next_step": "WORKER_REQUEST_GENERATION",
            "execution_out_of_scope": True,
        }
    if not isinstance(implementation_scope, dict):
        raise FailClosedRuntimeError("governed implementation request failed closed: implementation scope must be object")
    if (
        candidate.get("candidate_source_type") == APPROVED_DURABLE_WORK_PPP_SOURCE
        and implementation_scope != candidate.get("approved_implementation_scope")
    ):
        raise FailClosedRuntimeError(
            "governed implementation request failed closed: approved implementation scope substitution"
        )
    forbidden = {
        "execute_now",
        "invoke_worker",
        "invoke_provider",
        "modify_code_now",
        "modify_governance_now",
        "create_authorization",
    }
    if any(key in implementation_scope for key in forbidden):
        raise FailClosedRuntimeError("governed implementation request failed closed: implementation scope exceeds request")
    return deepcopy(implementation_scope)


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
            raise FailClosedRuntimeError("governed implementation request failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"governed implementation request failed closed: {label} must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("governed implementation request artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("governed implementation request artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("governed implementation request replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("governed implementation request replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed implementation request failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"governed implementation request failed closed: {field_name} must be a replay hash")
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
    return "governed implementation request failed closed"
