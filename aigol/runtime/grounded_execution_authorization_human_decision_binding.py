"""Bind one distinct human decision to a pending grounded execution review."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.execution_summary_runtime import (
    create_execution_summary_confirmation,
    verify_execution_summary_confirmation,
)
from aigol.runtime.grounded_worker_request_execution_authorization_binding import (
    EXECUTION_AUTHORIZATION_REVIEW_REQUIRED,
    reconstruct_grounded_worker_request_execution_authorization_review,
    validate_grounded_worker_request_execution_authorization_review,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)
RUNTIME_VERSION = "G31_09_DISTINCT_HUMAN_EXECUTION_DECISION_BINDING_V1"
HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1 = "GROUNDED_EXECUTION_AUTHORIZATION_HUMAN_DECISION_RESULT_ARTIFACT_V1"
EXECUTION_DECISION_APPROVED = "EXECUTION_DECISION_HUMAN_CONFIRMED"
EXECUTION_DECISION_REJECTED = "EXECUTION_DECISION_REJECTED"
EXECUTION_DECISION_FAILED_CLOSED = "EXECUTION_DECISION_FAILED_CLOSED"
REPLAY_STEPS = (
    "execution_authorization_review_source_recorded",
    "execution_human_decision_recorded",
)

FALSE_BOUNDARIES = {
    "proposal_approval_is_execution_authorization": False,
    "authorization_request_created": False,
    "authorization_decision_created": False,
    "execution_authorization_artifact_created": False,
    "execution_authorized": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "command_executed": False,
    "repository_mutated": False,
    "deployment_reached": False,
    "human_interface_authority": False,
    "human_interface_decision_authority": False,
    "human_interface_authorization_authority": False,
}
def bind_distinct_human_execution_decision(
    *,
    authorization_review_artifact: dict[str, Any],
    human_decision: str,
    session_id: str,
    decided_by: str,
    decided_at: str,
    workspace: str | Path,
    session_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record one explicit approve/reject decision without authorizing execution."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    if not destination.is_relative_to(root):
        raise FailClosedRuntimeError("human execution decision Replay is cross-session")
    _ensure_replay_available(destination)
    observed = deepcopy(authorization_review_artifact)
    _persist(destination, 0, REPLAY_STEPS[0], observed)
    try:
        session = _text(session_id, "session_id")
        if root.name != session:
            raise FailClosedRuntimeError("human execution decision session mismatch")
        decision = _text(human_decision, "human_decision").upper()
        if decision not in {"APPROVE", "REJECT"}:
            raise FailClosedRuntimeError(
                "human execution decision must be explicit APPROVE or REJECT"
            )
        review = validate_grounded_worker_request_execution_authorization_review(
            authorization_review_artifact,
            workspace=workspace,
        )
        if review["authorization_review_status"] != EXECUTION_AUTHORIZATION_REVIEW_REQUIRED:
            raise FailClosedRuntimeError("human execution decision review is not pending")
        review_replay = Path(review["replay_reference"]).resolve()
        if not review_replay.is_relative_to(root):
            raise FailClosedRuntimeError("human execution decision review is cross-session")
        reconstructed = reconstruct_grounded_worker_request_execution_authorization_review(
            review_replay, workspace=workspace
        )
        if reconstructed["artifact_hash"] != review["artifact_hash"]:
            raise FailClosedRuntimeError("human execution decision review Replay mismatch")
        _reject_prior_decision(root, review["artifact_hash"])
        confirmation = None
        status = EXECUTION_DECISION_REJECTED
        if decision == "APPROVE":
            confirmation = create_execution_summary_confirmation(
                confirmation_id=f"{session}:{review['artifact_hash']}:EXECUTION-DECISION",
                execution_summary_artifact=review["execution_summary_artifact"],
                decision=decision,
                confirmed_by=_text(decided_by, "decided_by"),
                confirmed_at=_text(decided_at, "decided_at"),
            )
            status = EXECUTION_DECISION_APPROVED
        result = _accepted_result(
            review=review,
            confirmation=confirmation,
            decision=decision,
            status=status,
            session_id=session,
            decided_by=_text(decided_by, "decided_by"),
            decided_at=_text(decided_at, "decided_at"),
            replay_reference=str(destination),
        )
        validate_distinct_human_execution_decision(
            result,
            workspace=workspace,
            session_root=root,
        )
    except Exception as exc:
        result = _failed_result(
            observation=observed,
            session_id=session_id,
            decided_at=decided_at,
            replay_reference=str(destination),
            failure_reason=(str(exc) if isinstance(exc, FailClosedRuntimeError)
                            else "human execution decision failed closed"),
        )
    _persist(destination, 1, REPLAY_STEPS[1], result)
    return deepcopy(result)
def validate_distinct_human_execution_decision(
    artifact: dict[str, Any],
    *,
    workspace: str | Path | None = None,
    session_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate exact review lineage, the second decision, and stop boundaries."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human execution decision artifact required")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("human execution decision artifact type is invalid")
    if candidate.get("runtime_version") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("human execution decision runtime version is invalid")
    verify_replay_hash(candidate, hash_field="artifact_hash")
    for field, expected in FALSE_BOUNDARIES.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                f"human execution decision authority boundary mismatch: {field}"
            )
    if candidate.get("dispatch_blocked") is not True:
        raise FailClosedRuntimeError("human execution decision must block dispatch")
    if candidate.get("decision_status") == EXECUTION_DECISION_FAILED_CLOSED:
        if candidate.get("fail_closed") is not True or not candidate.get("failure_reason"):
            raise FailClosedRuntimeError("failed human execution decision reason required")
        if candidate.get("human_confirmation_artifact") is not None:
            raise FailClosedRuntimeError("failed human execution decision cannot confirm")
        return candidate
    if candidate.get("decision_status") not in {
        EXECUTION_DECISION_APPROVED,
        EXECUTION_DECISION_REJECTED,
    }:
        raise FailClosedRuntimeError("human execution decision status is invalid")
    if candidate.get("fail_closed") is not False:
        raise FailClosedRuntimeError("accepted human execution decision failed closed")
    review = validate_grounded_worker_request_execution_authorization_review(
        candidate.get("source_authorization_review_artifact"),
        workspace=workspace,
    )
    if candidate.get("source_authorization_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("human execution decision review hash mismatch")
    expected = {
        "project_objective_hash": review["authorization_scope"]["project_objective_hash"],
        "durable_governed_work_hash": review["source_durable_governed_work_hash"],
        "proposal_preview_hash": review["source_proposal_preview_hash"],
        "repository_scope_grounding_hash": review["source_repository_scope_grounding_hash"],
        "grounded_worker_request_hash": review["source_grounded_worker_request_hash"],
        "execution_summary_hash": review["execution_summary_hash"],
        "authorization_scope_hash": review["authorization_scope_hash"],
    }
    for field, value in expected.items():
        if candidate.get(field) != value:
            raise FailClosedRuntimeError(
                f"human execution decision lineage mismatch: {field}"
            )
    if session_root is not None:
        root = Path(session_root).resolve()
        if candidate.get("session_id") != root.name:
            raise FailClosedRuntimeError("human execution decision session mismatch")
        if not Path(review["replay_reference"]).resolve().is_relative_to(root):
            raise FailClosedRuntimeError("human execution decision review is cross-session")
    confirmation = candidate.get("human_confirmation_artifact")
    if candidate["decision_status"] == EXECUTION_DECISION_APPROVED:
        verified = verify_execution_summary_confirmation(
            review["execution_summary_artifact"], confirmation
        )
        if candidate.get("human_confirmation_hash") != verified["artifact_hash"]:
            raise FailClosedRuntimeError("human execution decision confirmation mismatch")
        if candidate.get("execution_summary_human_confirmation") is not True:
            raise FailClosedRuntimeError("human execution decision confirmation missing")
        if candidate.get("execution_decision_rejected") is not False:
            raise FailClosedRuntimeError("approved execution decision marked rejected")
    elif (confirmation is not None
          or candidate.get("execution_summary_human_confirmation") is not False
          or candidate.get("execution_decision_rejected") is not True):
        raise FailClosedRuntimeError("rejected execution decision state is invalid")
    return candidate
def reconstruct_distinct_human_execution_decision(
    replay_dir: str | Path,
    *,
    workspace: str | Path | None = None,
    session_root: str | Path | None = None,
) -> dict[str, Any]:
    """Reconstruct the ordered G31-08-review to G31-09-decision Replay."""

    root = Path(replay_dir)
    wrappers = [load_json(root / f"{index:03d}_{step}.json")
                for index, step in enumerate(REPLAY_STEPS)]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human execution decision Replay ordering mismatch")
        verify_replay_hash(wrapper, hash_field="replay_hash")
    result = validate_distinct_human_execution_decision(
        wrappers[1]["artifact"],
        workspace=workspace,
        session_root=session_root,
    )
    if result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED:
        if result.get("source_review_observation_hash") != replay_hash(wrappers[0]["artifact"]):
            raise FailClosedRuntimeError("failed human decision observation mismatch")
    elif result["source_authorization_review_hash"] != wrappers[0]["artifact"].get("artifact_hash"):
        raise FailClosedRuntimeError("human execution decision Replay lineage mismatch")
    return result
def render_distinct_human_execution_decision(artifact: dict[str, Any]) -> str:
    decision = validate_distinct_human_execution_decision(artifact)
    return "\n".join(
        [
            "Distinct human execution decision",
            f"decision_status: {decision['decision_status']}",
            f"proposal_approval_consumed: {decision.get('proposal_approval_consumed')}",
            f"proposal_approval_is_execution_authorization: {decision['proposal_approval_is_execution_authorization']}",
            f"execution_summary_human_confirmation: {decision.get('execution_summary_human_confirmation')}",
            f"execution_decision_rejected: {decision.get('execution_decision_rejected')}",
            f"execution_authorized: {decision['execution_authorized']}",
            f"worker_selected: {decision['worker_selected']}",
            f"worker_dispatched: {decision['worker_dispatched']}",
            f"repository_mutated: {decision['repository_mutated']}",
            f"failure_reason: {decision.get('failure_reason')}",
            f"replay_reference: {decision['replay_reference']}",
        ]
    )
def _accepted_result(
    *,
    review: dict[str, Any],
    confirmation: dict[str, Any] | None,
    decision: str,
    status: str,
    session_id: str,
    decided_by: str,
    decided_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    scope = review["authorization_scope"]
    artifact = {
        "artifact_type": HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "decision_status": status,
        "session_id": session_id,
        "human_decision": decision,
        "decided_by": decided_by,
        "decided_at": decided_at,
        "replay_reference": replay_reference,
        "source_authorization_review_artifact": deepcopy(review),
        "source_authorization_review_hash": review["artifact_hash"],
        "project_objective_hash": scope["project_objective_hash"],
        "durable_governed_work_hash": review["source_durable_governed_work_hash"],
        "proposal_preview_hash": review["source_proposal_preview_hash"],
        "repository_scope_grounding_hash": review["source_repository_scope_grounding_hash"],
        "grounded_worker_request_hash": review["source_grounded_worker_request_hash"],
        "execution_summary_hash": review["execution_summary_hash"],
        "authorization_scope_hash": review["authorization_scope_hash"],
        "human_confirmation_artifact": deepcopy(confirmation),
        "human_confirmation_hash": confirmation["artifact_hash"] if confirmation else None,
        "proposal_approval_consumed": True,
        "second_human_decision_recorded": True,
        "execution_summary_human_confirmation": confirmation is not None,
        "execution_decision_rejected": decision == "REJECT",
        "dispatch_blocked": True,
        "fail_closed": False,
        "failure_reason": None,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact
def _failed_result(
    *,
    observation: Any,
    session_id: Any,
    decided_at: Any,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "decision_status": EXECUTION_DECISION_FAILED_CLOSED,
        "session_id": session_id if isinstance(session_id, str) else "INVALID",
        "human_decision": None,
        "decided_by": None,
        "decided_at": decided_at if isinstance(decided_at, str) else "INVALID",
        "replay_reference": replay_reference,
        "source_review_observation_hash": replay_hash(observation),
        "source_authorization_review_artifact": None,
        "human_confirmation_artifact": None,
        "human_confirmation_hash": None,
        "proposal_approval_consumed": False,
        "second_human_decision_recorded": False,
        "execution_summary_human_confirmation": False,
        "execution_decision_rejected": False,
        "dispatch_blocked": True,
        "fail_closed": True,
        "failure_reason": failure_reason,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact
def _reject_prior_decision(session_root: Path, review_hash: str) -> None:
    for path in session_root.rglob("001_execution_human_decision_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper, hash_field="replay_hash")
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("prior human execution decision is malformed")
        verify_replay_hash(artifact, hash_field="artifact_hash")
        if (
            artifact.get("source_authorization_review_hash") == review_hash
            and artifact.get("decision_status")
            in {EXECUTION_DECISION_APPROVED, EXECUTION_DECISION_REJECTED}
        ):
            raise FailClosedRuntimeError("human execution decision already recorded")


def _ensure_replay_available(root: Path) -> None:
    if any((root / f"{index:03d}_{step}.json").exists()
           for index, step in enumerate(REPLAY_STEPS)):
        raise FailClosedRuntimeError("human execution decision Replay already exists")


def _persist(root: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step,
               "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"human execution decision {field_name} required")
    return value.strip()
