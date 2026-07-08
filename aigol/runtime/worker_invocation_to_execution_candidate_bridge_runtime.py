"""Bridge certified Worker invocation artifacts into governed execution candidates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOKED,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    DEFAULT_EXECUTION_CONSTRAINTS,
    DEFAULT_GOVERNANCE_CONSTRAINTS,
    WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
    WORKER_EXECUTION_CANDIDATE_CREATED,
)


AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION = (
    "AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_V1"
)
FAILED_CLOSED = "FAILED_CLOSED"
APPROVAL_SCOPE = "CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY"

REPLAY_STEPS = (
    "worker_invocation_execution_candidate_bridge_recorded",
    "worker_invocation_execution_candidate_recorded",
    "worker_invocation_execution_candidate_returned",
)


def bridge_worker_invocation_to_execution_candidate(
    *,
    candidate_id: str,
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    execution_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1 from a certified Worker invocation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        invocation = deepcopy(worker_invocation_artifact)
        approval = deepcopy(human_approval_artifact)
        lineage = _load_invocation_lineage(
            invocation=invocation,
            worker_invocation_replay_reference=worker_invocation_replay_reference,
        )
        _validate_human_approval(approval, lineage["invocation"])
        bridge = _bridge_evidence_artifact(
            bridge_id=f"{_require_string(candidate_id, 'candidate_id')}:BRIDGE",
            lineage=lineage,
            approval=approval,
            created_at=created_at,
        )
        candidate = _execution_candidate_artifact(
            candidate_id=candidate_id,
            lineage=lineage,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            execution_constraints=execution_constraints,
            bridge=bridge,
            candidate_status=WORKER_EXECUTION_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(candidate)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], bridge)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], candidate)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(bridge, candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_execution_candidate_artifact(
            candidate_id=candidate_id,
            worker_invocation_artifact=worker_invocation_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(candidate)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], candidate)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(None, candidate, returned, replay_path)


def reconstruct_worker_invocation_to_execution_candidate_bridge_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and validate Worker invocation to execution candidate bridge replay."""

    replay_path = Path(replay_dir)
    candidate_wrapper = load_json(replay_path / "001_worker_invocation_execution_candidate_recorded.json")
    returned_wrapper = load_json(replay_path / "002_worker_invocation_execution_candidate_returned.json")
    _verify_wrapper_hash(candidate_wrapper)
    _verify_wrapper_hash(returned_wrapper)
    candidate = candidate_wrapper.get("artifact")
    returned = returned_wrapper.get("artifact")
    if not isinstance(candidate, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("worker invocation bridge replay artifact must be a JSON object")
    _verify_artifact_hash(candidate)
    _verify_artifact_hash(returned)
    if candidate.get("candidate_status") == WORKER_EXECUTION_CANDIDATE_CREATED:
        bridge_wrapper = load_json(replay_path / "000_worker_invocation_execution_candidate_bridge_recorded.json")
        if bridge_wrapper.get("replay_index") != 0 or bridge_wrapper.get("replay_step") != REPLAY_STEPS[0]:
            raise FailClosedRuntimeError("worker invocation bridge replay ordering mismatch")
        _verify_wrapper_hash(bridge_wrapper)
        bridge = bridge_wrapper.get("artifact")
        if not isinstance(bridge, dict):
            raise FailClosedRuntimeError("worker invocation bridge evidence must be a JSON object")
        _verify_artifact_hash(bridge)
        if candidate.get("bridge_evidence_hash") != bridge["artifact_hash"]:
            raise FailClosedRuntimeError("worker invocation bridge evidence hash mismatch")
        replay_artifact_count = 3
    else:
        replay_artifact_count = 2
    if candidate_wrapper.get("replay_index") != 1 or candidate_wrapper.get("replay_step") != REPLAY_STEPS[1]:
        raise FailClosedRuntimeError("worker invocation bridge replay ordering mismatch")
    if returned_wrapper.get("replay_index") != 2 or returned_wrapper.get("replay_step") != REPLAY_STEPS[2]:
        raise FailClosedRuntimeError("worker invocation bridge replay ordering mismatch")
    if returned.get("execution_candidate_reference") != candidate["execution_candidate_id"]:
        raise FailClosedRuntimeError("worker invocation bridge returned reference mismatch")
    if returned.get("execution_candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge returned hash mismatch")
    return {
        "execution_candidate_id": candidate["execution_candidate_id"],
        "candidate_status": candidate["candidate_status"],
        "source_worker_invocation": candidate.get("source_worker_invocation"),
        "source_invocation_candidate": candidate["source_invocation_candidate"],
        "source_dispatch_candidate": candidate["source_dispatch_candidate"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "worker_identity": deepcopy(candidate.get("worker_identity")),
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "human_approval_granted": candidate["human_approval_granted"],
        "ready_for_governed_worker_execution": candidate["ready_for_governed_worker_execution"],
        "worker_executed": candidate["worker_executed"],
        "implementation_result_created": candidate["implementation_result_created"],
        "code_modified": candidate["code_modified"],
        "governance_modified": candidate["governance_modified"],
        "provider_invoked": candidate["provider_invoked"],
        "execution_requested": candidate["execution_requested"],
        "replay_visible": True,
        "replay_artifact_count": replay_artifact_count,
        "replay_hash": replay_hash([candidate_wrapper, returned_wrapper]),
    }


def _load_invocation_lineage(
    *,
    invocation: dict[str, Any],
    worker_invocation_replay_reference: str,
) -> dict[str, Any]:
    _validate_invocation_artifact(invocation)
    invocation_path = Path(_require_string(worker_invocation_replay_reference, "worker_invocation_replay_reference"))
    reconstructed = reconstruct_worker_invocation_replay(invocation_path)
    if reconstructed.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: invocation not certified")
    if reconstructed.get("worker_invocation_id") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: invocation replay mismatch")
    invocation_wrapper = load_json(invocation_path / "002_invocation_artifact_recorded.json")
    invocation_evidence_wrapper = load_json(invocation_path / "000_invocation_evidence_recorded.json")
    for wrapper in (invocation_wrapper, invocation_evidence_wrapper):
        _verify_wrapper_hash(wrapper)
    replay_invocation = invocation_wrapper.get("artifact")
    invocation_evidence = invocation_evidence_wrapper.get("artifact")
    if not isinstance(replay_invocation, dict) or not isinstance(invocation_evidence, dict):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: invocation replay invalid")
    _verify_artifact_hash(replay_invocation)
    _verify_artifact_hash(invocation_evidence)
    if replay_invocation.get("artifact_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: invocation hash mismatch")

    dispatch_path = _resolve_replay_reference(
        invocation_evidence["worker_dispatch_replay_reference"],
        anchor=invocation_path,
    )
    dispatch_evidence = _load_wrapped_artifact(dispatch_path / "000_dispatch_evidence_recorded.json")
    dispatch = _load_wrapped_artifact(dispatch_path / "002_dispatch_artifact_recorded.json")
    if dispatch.get("worker_dispatch_id") != invocation["worker_dispatch_reference"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: dispatch reference mismatch")
    if dispatch.get("artifact_hash") != invocation["worker_dispatch_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: dispatch hash mismatch")

    assignment_path = _resolve_replay_reference(
        dispatch_evidence["worker_assignment_replay_reference"],
        anchor=dispatch_path,
    )
    assignment_evidence = _load_wrapped_artifact(assignment_path / "000_assignment_evidence_recorded.json")
    assignment = _load_wrapped_artifact(assignment_path / "002_assignment_artifact_recorded.json")
    if assignment.get("worker_assignment_id") != invocation["worker_assignment_reference"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: assignment reference mismatch")
    if assignment.get("artifact_hash") != invocation["worker_assignment_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: assignment hash mismatch")

    request_path = _resolve_replay_reference(
        assignment_evidence["worker_invocation_request_replay_reference"],
        anchor=assignment_path,
    )
    request = _load_wrapped_artifact(request_path / "002_invocation_request_artifact_recorded.json")
    if request.get("worker_invocation_request_id") != invocation["worker_invocation_request_reference"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: worker request reference mismatch")
    if request.get("artifact_hash") != invocation["worker_invocation_request_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: worker request hash mismatch")

    authorization_path = _resolve_replay_reference(
        request["replay_references"]["execution_authorization_replay_reference"],
        anchor=request_path,
    )
    authorization_request = _load_wrapped_artifact(authorization_path / "000_authorization_request_recorded.json")
    execution_ready_path = _resolve_replay_reference(
        authorization_request["execution_ready_replay_reference"],
        anchor=authorization_path,
    )
    dry_run_candidate = _load_wrapped_artifact(execution_ready_path / "000_execution_candidate_recorded.json")
    return {
        "invocation": deepcopy(invocation),
        "invocation_replay_reference": str(invocation_path),
        "invocation_evidence": invocation_evidence,
        "dispatch": dispatch,
        "dispatch_replay_reference": str(dispatch_path),
        "dispatch_evidence": dispatch_evidence,
        "assignment": assignment,
        "assignment_replay_reference": str(assignment_path),
        "request": request,
        "request_replay_reference": str(request_path),
        "authorization_request": authorization_request,
        "authorization_replay_reference": str(authorization_path),
        "dry_run_candidate": dry_run_candidate,
        "execution_ready_replay_reference": str(execution_ready_path),
    }


def _validate_invocation_artifact(invocation: dict[str, Any]) -> None:
    _verify_artifact_hash(invocation)
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: invalid invocation artifact type")
    if invocation.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: worker invocation required")
    for field in (
        "worker_invocation_id",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "worker_invocation_request_reference",
        "worker_invocation_request_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
    ):
        _require_string(invocation.get(field), field)
    if invocation.get("provider_invoked") not in (None, False):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: provider already invoked")
    if invocation.get("result_created") is not False:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: result already created")
    if invocation.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: replay visibility missing")


def _validate_human_approval(approval: dict[str, Any], invocation: dict[str, Any]) -> None:
    _verify_artifact_hash(approval)
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: explicit human approval required")
    if approval.get("source_worker_invocation") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: approval invocation mismatch")
    if approval.get("source_worker_invocation_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: approval invocation hash mismatch")
    if approval.get("approval_scope") != APPROVAL_SCOPE:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: approval scope invalid")
    if approval.get("worker_execution_allowed") is not False:
        raise FailClosedRuntimeError("worker invocation bridge failed closed: approval scope exceeds bridge")
    if approval.get("provider_invocation_allowed") not in (None, False):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: provider approval exceeds bridge")
    if approval.get("implementation_result_creation_allowed") not in (None, False):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: implementation approval exceeds bridge")
    _require_string(approval.get("approval_id"), "approval_id")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _bridge_evidence_artifact(
    *,
    bridge_id: str,
    lineage: dict[str, Any],
    approval: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    invocation = lineage["invocation"]
    dry_run_candidate = lineage["dry_run_candidate"]
    artifact = {
        "artifact_type": "WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_EVIDENCE_V1",
        "runtime_version": AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION,
        "bridge_id": _require_string(bridge_id, "bridge_id"),
        "source_worker_invocation": invocation["worker_invocation_id"],
        "source_worker_invocation_hash": invocation["artifact_hash"],
        "source_worker_invocation_replay_reference": lineage["invocation_replay_reference"],
        "source_dispatch": invocation["worker_dispatch_reference"],
        "source_dispatch_hash": invocation["worker_dispatch_hash"],
        "source_dispatch_replay_reference": lineage["dispatch_replay_reference"],
        "source_worker_request": invocation["worker_invocation_request_reference"],
        "source_worker_request_hash": invocation["worker_invocation_request_hash"],
        "source_worker_request_replay_reference": lineage["request_replay_reference"],
        "source_implementation_request": dry_run_candidate["handoff_reference"],
        "source_implementation_request_hash": dry_run_candidate["handoff_hash"],
        "source_ppp_candidate": dry_run_candidate["upstream_lineage_reference"],
        "source_ppp_candidate_hash": dry_run_candidate["upstream_lineage_hash"],
        "worker_identity": _worker_identity(invocation),
        "execution_candidate_scope": _execution_candidate_scope(invocation, dry_run_candidate),
        "approval_reference": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "approval_status": approval["approval_status"],
        "created_at": _require_string(created_at, "created_at"),
        "replay_lineage_preserved": True,
        "human_approval_required": True,
        "human_approval_granted": True,
        "worker_invocation_accepted": True,
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_candidate_artifact(
    *,
    candidate_id: str,
    lineage: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    execution_constraints: dict[str, Any] | None,
    bridge: dict[str, Any],
    candidate_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    invocation = lineage["invocation"]
    dry_run_candidate = lineage["dry_run_candidate"]
    constraints = _execution_constraints(execution_constraints)
    artifact = {
        "artifact_type": WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION,
        "execution_candidate_id": _require_string(candidate_id, "candidate_id"),
        "candidate_status": candidate_status,
        "source_invocation_candidate": invocation["worker_invocation_id"],
        "source_invocation_candidate_hash": invocation["artifact_hash"],
        "source_worker_invocation": invocation["worker_invocation_id"],
        "source_worker_invocation_hash": invocation["artifact_hash"],
        "source_dispatch_candidate": invocation["worker_dispatch_reference"],
        "source_dispatch_candidate_hash": invocation["worker_dispatch_hash"],
        "source_worker_request": invocation["worker_invocation_request_reference"],
        "source_worker_request_hash": invocation["worker_invocation_request_hash"],
        "source_implementation_request": dry_run_candidate["handoff_reference"],
        "source_implementation_request_hash": dry_run_candidate["handoff_hash"],
        "source_ppp_candidate": dry_run_candidate["upstream_lineage_reference"],
        "source_ppp_candidate_hash": dry_run_candidate["upstream_lineage_hash"],
        "replay_references": _replay_references(lineage),
        "replay_hashes": _replay_hashes(lineage),
        "bridge_evidence_reference": bridge["bridge_id"],
        "bridge_evidence_hash": bridge["artifact_hash"],
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "human_approval_required": True,
        "human_approval_granted": True,
        "human_authority_preserved": True,
        "execution_objective": _execution_objective(invocation),
        "execution_candidate_scope": _execution_candidate_scope(invocation, dry_run_candidate),
        "worker_identity": _worker_identity(invocation),
        "execution_constraints": constraints,
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": {
            "source_runtime": "DOMAIN_WORKER_INVOCATION",
            "bridge_runtime": AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION,
            "candidate_creation_only": True,
            "external_task_package_requires_separate_approval": True,
        },
        "affected_runtime": invocation["worker_family"],
        "affected_lifecycle_stage": "DOMAIN_WORKER_INVOCATION",
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "certification_status": "CERTIFIED_WORKER_INVOCATION_CANDIDATE_ACCEPTED",
        "replay_lineage_preserved": True,
        "ready_for_governed_worker_execution": True,
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_execution_candidate_artifact(
    *,
    candidate_id: str,
    worker_invocation_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION,
        "execution_candidate_id": candidate_id if isinstance(candidate_id, str) else "INVALID",
        "candidate_status": FAILED_CLOSED,
        "source_invocation_candidate": worker_invocation_artifact.get("worker_invocation_id")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_invocation_candidate_hash": worker_invocation_artifact.get("artifact_hash")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_worker_invocation": worker_invocation_artifact.get("worker_invocation_id")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_worker_invocation_hash": worker_invocation_artifact.get("artifact_hash")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_dispatch_candidate": worker_invocation_artifact.get("worker_dispatch_reference")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_worker_request": worker_invocation_artifact.get("worker_invocation_request_reference")
        if isinstance(worker_invocation_artifact, dict)
        else None,
        "source_implementation_request": None,
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
        "execution_objective": None,
        "execution_candidate_scope": {},
        "worker_identity": {},
        "execution_constraints": deepcopy(DEFAULT_EXECUTION_CONSTRAINTS),
        "governance_constraints": deepcopy(DEFAULT_GOVERNANCE_CONSTRAINTS),
        "governance_classification": {},
        "affected_runtime": None,
        "affected_lifecycle_stage": None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "certification_status": FAILED_CLOSED,
        "replay_lineage_preserved": False,
        "ready_for_governed_worker_execution": False,
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(candidate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(candidate)
    artifact = {
        "event_type": "WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_RETURNED",
        "execution_candidate_reference": candidate["execution_candidate_id"],
        "execution_candidate_hash": candidate["artifact_hash"],
        "candidate_status": candidate["candidate_status"],
        "source_worker_invocation": candidate.get("source_worker_invocation"),
        "source_invocation_candidate": candidate["source_invocation_candidate"],
        "source_dispatch_candidate": candidate["source_dispatch_candidate"],
        "source_worker_request": candidate["source_worker_request"],
        "source_implementation_request": candidate["source_implementation_request"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "human_approval_granted": candidate["human_approval_granted"],
        "ready_for_governed_worker_execution": candidate["ready_for_governed_worker_execution"],
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "failure_reason": candidate["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    bridge: dict[str, Any] | None,
    candidate: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_VERSION,
        "candidate_status": candidate["candidate_status"],
        "bridge_evidence_artifact": deepcopy(bridge) if bridge is not None else None,
        "worker_execution_candidate_artifact": deepcopy(candidate),
        "worker_execution_candidate_returned_artifact": deepcopy(returned),
        "worker_execution_candidate_replay_reference": str(replay_path),
        "worker_invocation_accepted": candidate["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED,
        "worker_execution_candidate_generated": candidate["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED,
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "human_approval_granted": candidate["human_approval_granted"],
        "approval_boundary_preserved": candidate["human_approval_required"] is True
        and candidate["human_approval_granted"] is (candidate["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED),
        "execution_prevented": candidate["worker_executed"] is False
        and candidate["implementation_result_created"] is False
        and candidate["code_modified"] is False
        and candidate["governance_modified"] is False
        and candidate["provider_invoked"] is False
        and candidate["execution_requested"] is False,
        "ready_for_governed_worker_execution": candidate["ready_for_governed_worker_execution"],
        "failure_reason": candidate["failure_reason"],
    }
    capture["worker_invocation_to_execution_candidate_bridge_capture_hash"] = replay_hash(capture)
    return capture


def _execution_constraints(execution_constraints: dict[str, Any] | None) -> dict[str, Any]:
    constraints = deepcopy(DEFAULT_EXECUTION_CONSTRAINTS)
    if execution_constraints is None:
        return constraints
    if not isinstance(execution_constraints, dict):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: execution constraints invalid")
    forbidden_true = {
        "worker_execution_allowed",
        "implementation_result_creation_allowed",
        "code_modification_allowed",
        "governance_modification_allowed",
        "provider_invocation_allowed",
    }
    for key, value in execution_constraints.items():
        if key in forbidden_true and value is not False:
            raise FailClosedRuntimeError("worker invocation bridge failed closed: execution constraints exceed bridge")
        constraints[key] = deepcopy(value)
    return constraints


def _execution_objective(invocation: dict[str, Any]) -> str:
    return (
        f"Create a governed external worker task package for certified invocation "
        f"{invocation['worker_invocation_id']} assigned to {invocation['worker_id']}."
    )


def _execution_candidate_scope(invocation: dict[str, Any], dry_run_candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_worker_invocation": invocation["worker_invocation_id"],
        "source_worker_invocation_hash": invocation["artifact_hash"],
        "target_domain": invocation.get("target_domain"),
        "target_worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "implementation_handoff_reference": dry_run_candidate["handoff_reference"],
        "implementation_handoff_hash": dry_run_candidate["handoff_hash"],
        "implementation_result_creation_allowed": False,
        "provider_invocation_allowed": False,
        "repository_mutation_allowed": False,
    }


def _worker_identity(invocation: dict[str, Any]) -> dict[str, Any]:
    return {
        "worker_id": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
    }


def _replay_references(lineage: dict[str, Any]) -> list[str]:
    dry_run_candidate = lineage["dry_run_candidate"]
    references = [
        lineage["invocation_replay_reference"],
        lineage["dispatch_replay_reference"],
        lineage["assignment_replay_reference"],
        lineage["request_replay_reference"],
        lineage["authorization_replay_reference"],
        lineage["execution_ready_replay_reference"],
        dry_run_candidate.get("handoff_replay_reference"),
    ]
    return [item for item in references if isinstance(item, str) and item.strip()]


def _replay_hashes(lineage: dict[str, Any]) -> list[str]:
    invocation = lineage["invocation"]
    dispatch = lineage["dispatch"]
    assignment = lineage["assignment"]
    request = lineage["request"]
    authorization = lineage["authorization_request"]
    dry_run_candidate = lineage["dry_run_candidate"]
    hashes = [
        invocation["artifact_hash"],
        dispatch["artifact_hash"],
        assignment["artifact_hash"],
        request["artifact_hash"],
        authorization["artifact_hash"],
        dry_run_candidate["artifact_hash"],
        dry_run_candidate["handoff_hash"],
        dry_run_candidate["upstream_lineage_hash"],
    ]
    return [item for item in hashes if isinstance(item, str) and item.startswith("sha256:")]


def _load_wrapped_artifact(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: replay artifact must be object")
    _verify_artifact_hash(artifact)
    return artifact


def _resolve_replay_reference(reference: str, *, anchor: Path) -> Path:
    text = _require_string(reference, "replay_reference")
    path = Path(text)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] in {".runtime", "runtime"}:
        return path.resolve()
    return (anchor.parent / path).resolve()


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
            raise FailClosedRuntimeError("worker invocation bridge failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: artifact must be object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("worker invocation bridge artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("worker invocation bridge artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("worker invocation bridge failed closed: replay wrapper must be object")
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("worker invocation bridge replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("worker invocation bridge replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker invocation bridge failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "worker invocation bridge failed closed"
