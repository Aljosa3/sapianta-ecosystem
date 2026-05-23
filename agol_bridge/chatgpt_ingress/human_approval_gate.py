"""Human approval evidence gate for governed task package previews.

This module creates approval or rejection evidence only. It does not execute,
dispatch Codex, call Native Messaging, invoke providers, create executable
handoffs, or continue autonomously.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .governed_task_package_preview import (
    ARTIFACT_TYPE as TASK_PREVIEW_ARTIFACT_TYPE,
    READY_FOR_HUMAN_APPROVAL,
    validate_governed_task_package_preview,
)

ARTIFACT_TYPE = "HUMAN_APPROVAL_GATE_V1"
SCHEMA_VERSION = "1.0"
APPROVED_FOR_GOVERNED_HANDOFF = "APPROVED_FOR_GOVERNED_HANDOFF"
REJECTED_BY_HUMAN = "REJECTED_BY_HUMAN"
ALLOWED_APPROVAL_STATUSES = (APPROVED_FOR_GOVERNED_HANDOFF, REJECTED_BY_HUMAN)
APPROVE_DECISIONS = ("APPROVE", "APPROVED", APPROVED_FOR_GOVERNED_HANDOFF)
REJECT_DECISIONS = ("REJECT", "REJECTED", REJECTED_BY_HUMAN)
BOUNDARY_STATEMENT = (
    "Human approval gate creates approval evidence only. It does not execute, "
    "dispatch Codex, dispatch providers, call Native Messaging, or authorize "
    "autonomous continuation."
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _approval_hash_input(approval: dict) -> dict:
    return {
        "replay_identity": approval["replay_identity"],
        "source_task_package_preview_hash": approval["source_task_package_preview_hash"],
        "human_decision": approval["human_decision"],
        "approval_status": approval["approval_status"],
        "approval_reason": approval["approval_reason"],
        "authority_boundary": approval["authority_boundary"],
        "provenance": approval["provenance"],
    }


def _authority_boundary() -> dict:
    return {
        "human_authority": True,
        "execution_authority": False,
        "codex_dispatch_authority": False,
        "provider_dispatch_authority": False,
        "governance_execution_authority": False,
        "autonomous_continuation_authority": False,
        "semantic_correctness_authority": False,
        "boundary_statement": BOUNDARY_STATEMENT,
    }


def _decision_status(decision: str) -> tuple[str, bool]:
    normalized = str(decision or "").strip().upper()
    if normalized in APPROVE_DECISIONS:
        return APPROVED_FOR_GOVERNED_HANDOFF, True
    return REJECTED_BY_HUMAN, False


def _reject_gate(
    *,
    preview: dict | None,
    human_decision: str,
    approval_reason: str,
    operator_label: str,
    created_at: str,
    reason: str,
) -> dict:
    safe_preview = preview if isinstance(preview, dict) else {}
    approval = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": safe_preview.get("replay_identity", "UNKNOWN"),
        "source_task_package_preview_hash": safe_preview.get("preview_hash", "UNKNOWN"),
        "human_decision": str(human_decision or "").strip() or "REJECT",
        "approval_status": REJECTED_BY_HUMAN,
        "approval_reason": str(approval_reason or reason).strip(),
        "operator_label": str(operator_label or "UNKNOWN_OPERATOR").strip(),
        "created_at": str(created_at or "").strip(),
        "provenance": {
            "source": TASK_PREVIEW_ARTIFACT_TYPE,
            "source_preview_status": safe_preview.get("governance_status", "UNKNOWN"),
            "source_execution_boundary_state": safe_preview.get("execution_boundary_state", "UNKNOWN"),
            "rejection_reason": reason,
        },
        "authority_boundary": _authority_boundary(),
        "human_approved": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "semantic_correctness_verified": False,
        "approval_evidence_only": True,
        "rejection_reasons": [reason],
    }
    approval["approval_hash"] = canonical_hash(_approval_hash_input(approval))
    return approval


def create_human_approval_gate(
    *,
    preview: Any,
    human_decision: str,
    approval_reason: str,
    operator_label: str,
    created_at: str,
) -> dict:
    """Create deterministic human approval/rejection evidence and stop."""

    if not isinstance(preview, dict):
        return _reject_gate(
            preview={},
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="preview must be a dict",
        )

    preview_validation = validate_governed_task_package_preview(preview)
    if preview_validation.get("valid") is not True:
        return _reject_gate(
            preview=preview,
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="preview validation failed",
        )
    if preview.get("governance_status") != READY_FOR_HUMAN_APPROVAL:
        return _reject_gate(
            preview=preview,
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="preview is not READY_FOR_HUMAN_APPROVAL",
        )
    if not preview.get("replay_identity") or preview.get("replay_identity") == "UNKNOWN":
        return _reject_gate(
            preview=preview,
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="replay identity missing",
        )
    if not isinstance(preview.get("provenance"), dict) or not preview["provenance"]:
        return _reject_gate(
            preview=preview,
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="provenance missing",
        )
    if any(
        preview.get(flag) is not False
        for flag in (
            "execution_authorized",
            "codex_dispatch_authorized",
            "provider_dispatch_authorized",
            "governance_execution_approved",
            "autonomous_continuation_authorized",
        )
    ):
        return _reject_gate(
            preview=preview,
            human_decision=human_decision,
            approval_reason=approval_reason,
            operator_label=operator_label,
            created_at=created_at,
            reason="authority boundary violated",
        )

    approval_status, human_approved = _decision_status(human_decision)
    approval = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": preview["replay_identity"],
        "source_task_package_preview_hash": preview["preview_hash"],
        "human_decision": str(human_decision or "").strip().upper(),
        "approval_status": approval_status,
        "approval_reason": str(approval_reason or "").strip(),
        "operator_label": str(operator_label or "UNKNOWN_OPERATOR").strip(),
        "created_at": str(created_at or "").strip(),
        "provenance": {
            "source": TASK_PREVIEW_ARTIFACT_TYPE,
            "source_preview_status": preview["governance_status"],
            "source_execution_boundary_state": preview["execution_boundary_state"],
            "source_provenance": _canonical_copy(preview["provenance"]),
        },
        "authority_boundary": _authority_boundary(),
        "human_approved": human_approved,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "semantic_correctness_verified": False,
        "approval_evidence_only": True,
        "rejection_reasons": [] if human_approved else ["human explicitly rejected preview"],
    }
    approval["approval_hash"] = canonical_hash(_approval_hash_input(approval))
    return approval


def validate_human_approval_gate(approval: Any) -> dict:
    """Validate that human approval evidence remains non-executing."""

    errors: list[str] = []
    if not isinstance(approval, dict):
        return {"valid": False, "status": REJECTED_BY_HUMAN, "errors": ["approval must be a dict"]}
    if approval.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if approval.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if approval.get("approval_status") not in ALLOWED_APPROVAL_STATUSES:
        errors.append("approval_status invalid")
    for field in (
        "replay_identity",
        "source_task_package_preview_hash",
        "human_decision",
        "approval_reason",
        "operator_label",
        "created_at",
        "approval_hash",
    ):
        if not isinstance(approval.get(field), str) or not approval.get(field):
            errors.append(f"{field} is required")
    if not isinstance(approval.get("provenance"), dict) or not approval["provenance"]:
        errors.append("provenance is required")
    boundary = approval.get("authority_boundary", {})
    if boundary.get("human_authority") is not True:
        errors.append("human_authority must be true")
    for field in (
        "execution_authority",
        "codex_dispatch_authority",
        "provider_dispatch_authority",
        "governance_execution_authority",
        "autonomous_continuation_authority",
        "semantic_correctness_authority",
    ):
        if boundary.get(field) is not False:
            errors.append(f"authority_boundary.{field} must be false")
    for field in (
        "execution_performed",
        "codex_dispatch_performed",
        "provider_dispatch_performed",
        "autonomous_continuation_performed",
        "semantic_correctness_verified",
    ):
        if approval.get(field) is not False:
            errors.append(f"{field} must be false")
    expected_hash = canonical_hash(_approval_hash_input(approval)) if not errors else None
    if expected_hash is not None and approval.get("approval_hash") != expected_hash:
        errors.append("approval_hash mismatch")
    return {
        "valid": not errors,
        "status": approval.get("approval_status", REJECTED_BY_HUMAN),
        "errors": errors,
    }


__all__ = [
    "ALLOWED_APPROVAL_STATUSES",
    "APPROVED_FOR_GOVERNED_HANDOFF",
    "ARTIFACT_TYPE",
    "BOUNDARY_STATEMENT",
    "REJECTED_BY_HUMAN",
    "SCHEMA_VERSION",
    "create_human_approval_gate",
    "validate_human_approval_gate",
]
