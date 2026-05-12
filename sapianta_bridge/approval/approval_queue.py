"""Human-governed approval queue operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.reflection.reflection_models import ReflectionError, validate_reflection_artifact
from sapianta_bridge.transport.transport_config import TransportConfig

from .approval_models import ApprovalError, validate_approval_artifact
from .approval_reader import approval_by_id, approval_history, pending_approvals
from .approval_storage import move_pending_to_decided, write_pending_approval
from .governance_decisions import build_decision_artifact, write_decision_artifact


def _approval_id(reflection: dict[str, Any], proposal: dict[str, Any]) -> str:
    digest = compute_hash(
        {
            "source_reflection_id": reflection["reflection_id"],
            "source_task_id": reflection["source_task_id"],
            "proposal_summary": proposal["summary"],
        }
    )
    return f"APPROVAL-{digest[:16].upper()}"


def build_approval_artifact(
    reflection: dict[str, Any],
    proposal: dict[str, Any],
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    try:
        validate_reflection_artifact(reflection)
    except ReflectionError as exc:
        raise ApprovalError(exc.field, exc.reason) from exc
    if not isinstance(proposal, dict):
        raise ApprovalError("proposal", "proposal must be an object")
    if proposal.get("allowed_to_execute_automatically") is not False:
        raise ApprovalError("proposal", "proposal must be advisory-only")
    summary = proposal.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ApprovalError("proposal.summary", "proposal summary must be non-empty")

    artifact = {
        "approval_id": _approval_id(reflection, proposal),
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "source_reflection_id": reflection["reflection_id"],
        "source_task_id": reflection["source_task_id"],
        "proposal_summary": summary,
        "decision": "PENDING",
        "approved_by": None,
        "decision_reason": None,
        "requires_human_action": True,
        "allowed_to_execute_automatically": False,
        "lineage": {
            "source_reflection_id": reflection["reflection_id"],
            "source_task_id": reflection["source_task_id"],
        },
    }
    validate_approval_artifact(artifact)
    return artifact


def enqueue_advisory_proposal(
    reflection: dict[str, Any],
    *,
    proposal_index: int = 0,
    config: TransportConfig | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    try:
        validate_reflection_artifact(reflection)
    except ReflectionError as exc:
        raise ApprovalError(exc.field, exc.reason) from exc
    proposals = reflection.get("advisory_proposals")
    if not isinstance(proposals, list) or proposal_index >= len(proposals):
        raise ApprovalError("advisory_proposals", "proposal index unavailable")
    artifact = build_approval_artifact(
        reflection,
        proposals[proposal_index],
        timestamp=timestamp,
    )
    if approval_by_id(artifact["approval_id"], config) is not None:
        raise ApprovalError("approval_id", "duplicate approval detected")
    path = write_pending_approval(artifact, config)
    return {"enqueued": True, "approval_path": str(path), "approval": artifact}


def inspect_pending(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return pending_approvals(config)


def decide_approval(
    approval_id: str,
    *,
    decision: str,
    approved_by: str,
    reason: str,
    config: TransportConfig | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    if decision not in {"APPROVED", "REJECTED"}:
        raise ApprovalError("decision", "decision must be APPROVED or REJECTED")
    approval = approval_by_id(approval_id, config)
    if approval is None or approval["decision"] != "PENDING":
        raise ApprovalError("approval_id", "pending approval not found")
    decision_artifact = build_decision_artifact(
        approval,
        decision=decision,
        approved_by=approved_by,
        reason=reason,
        timestamp=timestamp,
    )
    write_decision_artifact(decision_artifact, config)
    decided_path = move_pending_to_decided(
        approval_id,
        decision,
        approved_by=approved_by,
        reason=reason,
        config=config,
    )
    return {
        "decided": True,
        "approval_path": str(decided_path),
        "decision": decision_artifact,
    }


def approve_approval(
    approval_id: str,
    *,
    approved_by: str,
    reason: str,
    config: TransportConfig | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return decide_approval(
        approval_id,
        decision="APPROVED",
        approved_by=approved_by,
        reason=reason,
        config=config,
        timestamp=timestamp,
    )


def reject_approval(
    approval_id: str,
    *,
    approved_by: str,
    reason: str,
    config: TransportConfig | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return decide_approval(
        approval_id,
        decision="REJECTED",
        approved_by=approved_by,
        reason=reason,
        config=config,
        timestamp=timestamp,
    )
