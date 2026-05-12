"""Approval artifact models and fail-closed validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DECISIONS = {"PENDING", "APPROVED", "REJECTED"}


@dataclass(frozen=True)
class ApprovalError(Exception):
    field: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "reason": self.reason}


def validate_approval_artifact(artifact: Any) -> None:
    if not isinstance(artifact, dict):
        raise ApprovalError("approval", "approval artifact must be an object")
    required = (
        "approval_id",
        "timestamp",
        "source_reflection_id",
        "source_task_id",
        "proposal_summary",
        "decision",
        "approved_by",
        "decision_reason",
        "requires_human_action",
        "allowed_to_execute_automatically",
        "lineage",
    )
    for field in required:
        if field not in artifact:
            raise ApprovalError(field, "missing approval field")
    for field in ("approval_id", "source_reflection_id", "source_task_id", "proposal_summary"):
        if not isinstance(artifact[field], str) or not artifact[field].strip():
            raise ApprovalError(field, "field must be non-empty")
    if artifact["decision"] not in DECISIONS:
        raise ApprovalError("decision", "invalid approval decision")
    if artifact["requires_human_action"] is not True:
        raise ApprovalError("requires_human_action", "approval requires human action")
    if artifact["allowed_to_execute_automatically"] is not False:
        raise ApprovalError(
            "allowed_to_execute_automatically",
            "approval must not allow automatic execution",
        )
    lineage = artifact["lineage"]
    if not isinstance(lineage, dict):
        raise ApprovalError("lineage", "lineage must be an object")
    if lineage.get("source_reflection_id") != artifact["source_reflection_id"]:
        raise ApprovalError("lineage.source_reflection_id", "lineage reflection mismatch")
    if lineage.get("source_task_id") != artifact["source_task_id"]:
        raise ApprovalError("lineage.source_task_id", "lineage task mismatch")
    if artifact["decision"] == "PENDING":
        if artifact["approved_by"] is not None or artifact["decision_reason"] is not None:
            raise ApprovalError("decision", "pending approval cannot contain a decision")
    else:
        if not isinstance(artifact["approved_by"], str) or not artifact["approved_by"].strip():
            raise ApprovalError("approved_by", "decision requires approver identity")
        if not isinstance(artifact["decision_reason"], str) or not artifact["decision_reason"].strip():
            raise ApprovalError("decision_reason", "decision requires reason")


def validate_decision_artifact(artifact: Any) -> None:
    if not isinstance(artifact, dict):
        raise ApprovalError("decision", "decision artifact must be an object")
    required = (
        "decision_id",
        "approval_id",
        "decision",
        "approved_by",
        "timestamp",
        "reason",
        "source_reflection_id",
        "execution_authority_granted",
    )
    for field in required:
        if field not in artifact:
            raise ApprovalError(field, "missing decision field")
    if artifact["decision"] not in {"APPROVED", "REJECTED"}:
        raise ApprovalError("decision", "decision artifact must approve or reject")
    for field in ("decision_id", "approval_id", "approved_by", "reason", "source_reflection_id"):
        if not isinstance(artifact[field], str) or not artifact[field].strip():
            raise ApprovalError(field, "field must be non-empty")
    if artifact["execution_authority_granted"] is not False:
        raise ApprovalError(
            "execution_authority_granted",
            "approval decisions never grant execution authority in v1",
        )
