"""Governed handoff package preview after human approval evidence.

This module creates a provider-boundary preview only. It does not execute,
dispatch Codex, call Native Messaging, invoke providers, create runtime
dispatch, or continue autonomously.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .governed_task_package_preview import (
    READY_FOR_HUMAN_APPROVAL,
    validate_governed_task_package_preview,
)
from .human_approval_gate import (
    APPROVED_FOR_GOVERNED_HANDOFF,
    validate_human_approval_gate,
)

ARTIFACT_TYPE = "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1"
SCHEMA_VERSION = "1.0"
READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION = "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION"
HANDOFF_PREVIEW_REJECTED = "HANDOFF_PREVIEW_REJECTED"
ALLOWED_HANDOFF_PREVIEW_STATUSES = (
    READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
    HANDOFF_PREVIEW_REJECTED,
)
TARGET_PROVIDER_BOUNDARY = "BOUNDED_PROVIDER_DISPATCH_BOUNDARY_PREVIEW"
ALLOWED_PROVIDER_KIND = "CODEX_CLI_PROVIDER_BOUNDARY_PREVIEW"
WORKSPACE_SCOPE_PREVIEW = "CURRENT_GOVERNED_WORKSPACE_ONLY_PREVIEW"
TIMEOUT_POLICY_PREVIEW = "BOUNDED_TIMEOUT_REQUIRED_BEFORE_DISPATCH_AUTHORIZATION"
BOUNDARY_STATEMENT = (
    "Human approval is present, but it is not dispatch authorization. This "
    "handoff package is a non-executing provider-boundary preview only."
)

FORBIDDEN_OPERATIONS = (
    "codex_dispatch",
    "native_messaging_execution",
    "provider_dispatch",
    "runtime_execution",
    "automatic_handoff",
    "automatic_execution",
    "autonomous_continuation",
    "orchestration",
    "retries",
    "background_workers",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _authority_boundary(*, human_approval_present: bool) -> dict:
    return {
        "human_approval_present": human_approval_present,
        "execution_authorized": False,
        "dispatch_authorized": False,
        "codex_dispatch_authorized": False,
        "provider_dispatch_authorized": False,
        "governance_execution_approved": False,
        "autonomous_continuation_authorized": False,
        "boundary_statement": BOUNDARY_STATEMENT,
    }


def _handoff_hash_input(preview: dict) -> dict:
    return {
        "replay_identity": preview["replay_identity"],
        "source_ingress_artifact_hash": preview["source_ingress_artifact_hash"],
        "semantic_contract_candidate_hash": preview["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": preview["admissibility_gate_hash"],
        "governed_task_package_preview_hash": preview["governed_task_package_preview_hash"],
        "human_approval_hash": preview["human_approval_hash"],
        "target_provider_boundary": preview["target_provider_boundary"],
        "allowed_provider_kind": preview["allowed_provider_kind"],
        "workspace_scope_preview": preview["workspace_scope_preview"],
        "timeout_policy_preview": preview["timeout_policy_preview"],
        "handoff_boundary_state": preview["handoff_boundary_state"],
        "authority_boundary": preview["authority_boundary"],
        "handoff_preview_status": preview["handoff_preview_status"],
    }


def _reject_preview(
    *,
    task_package_preview: dict | None,
    human_approval: dict | None,
    reason: str,
) -> dict:
    task = task_package_preview if isinstance(task_package_preview, dict) else {}
    approval = human_approval if isinstance(human_approval, dict) else {}
    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": task.get("replay_identity", approval.get("replay_identity", "UNKNOWN")),
        "provenance": {
            "source_task_package_preview_present": isinstance(task_package_preview, dict),
            "human_approval_present": isinstance(human_approval, dict),
            "rejection_reason": reason,
        },
        "source_ingress_artifact_hash": task.get("source_ingress_artifact_hash", "UNKNOWN"),
        "semantic_contract_candidate_hash": task.get("semantic_contract_candidate_hash", "NONE"),
        "admissibility_gate_hash": task.get("admissibility_gate_hash", "NONE"),
        "governed_task_package_preview_hash": task.get("preview_hash", "UNKNOWN"),
        "human_approval_hash": approval.get("approval_hash", "UNKNOWN"),
        "handoff_boundary_state": HANDOFF_PREVIEW_REJECTED,
        "target_provider_boundary": TARGET_PROVIDER_BOUNDARY,
        "allowed_provider_kind": ALLOWED_PROVIDER_KIND,
        "workspace_scope_preview": WORKSPACE_SCOPE_PREVIEW,
        "timeout_policy_preview": TIMEOUT_POLICY_PREVIEW,
        "constraints": _canonical_copy(task.get("constraints", [])),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "authority_boundary": _authority_boundary(human_approval_present=False),
        "handoff_preview_status": HANDOFF_PREVIEW_REJECTED,
        "preview_only": True,
        "executable": False,
        "dispatchable": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "explicit_dispatch_authorization_required": True,
        "rejection_reasons": [reason],
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    }
    preview["handoff_preview_hash"] = canonical_hash(_handoff_hash_input(preview))
    return preview


def create_governed_handoff_package_preview(*, task_package_preview: Any, human_approval: Any) -> dict:
    """Create a governed handoff package preview and stop before dispatch."""

    if not isinstance(task_package_preview, dict):
        return _reject_preview(
            task_package_preview=None,
            human_approval=human_approval if isinstance(human_approval, dict) else None,
            reason="governed task package preview missing",
        )
    if not isinstance(human_approval, dict):
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=None,
            reason="human approval missing",
        )

    task_validation = validate_governed_task_package_preview(task_package_preview)
    approval_validation = validate_human_approval_gate(human_approval)
    if task_validation.get("valid") is not True:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="governed task package preview invalid",
        )
    if approval_validation.get("valid") is not True:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="human approval invalid",
        )
    if human_approval.get("approval_status") != APPROVED_FOR_GOVERNED_HANDOFF:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="human approval status is not APPROVED_FOR_GOVERNED_HANDOFF",
        )
    if task_package_preview.get("execution_boundary_state") != READY_FOR_HUMAN_APPROVAL:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="task package preview is not READY_FOR_HUMAN_APPROVAL",
        )
    if task_package_preview.get("replay_identity") != human_approval.get("replay_identity"):
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="replay identity mismatch",
        )
    if task_package_preview.get("preview_hash") != human_approval.get("source_task_package_preview_hash"):
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="task package preview hash mismatch",
        )
    if not isinstance(task_package_preview.get("provenance"), dict) or not task_package_preview["provenance"]:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="task package preview provenance missing",
        )
    if not isinstance(human_approval.get("provenance"), dict) or not human_approval["provenance"]:
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="human approval provenance missing",
        )
    if any(
        task_package_preview.get(flag) is not False
        for flag in (
            "execution_authorized",
            "codex_dispatch_authorized",
            "provider_dispatch_authorized",
            "governance_execution_approved",
            "autonomous_continuation_authorized",
        )
    ):
        return _reject_preview(
            task_package_preview=task_package_preview,
            human_approval=human_approval,
            reason="task package authority boundary violated",
        )

    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": task_package_preview["replay_identity"],
        "provenance": {
            "source": "HUMAN_APPROVAL_GATE_V1",
            "task_package_preview_provenance": _canonical_copy(task_package_preview["provenance"]),
            "human_approval_provenance": _canonical_copy(human_approval["provenance"]),
        },
        "source_ingress_artifact_hash": task_package_preview["source_ingress_artifact_hash"],
        "semantic_contract_candidate_hash": task_package_preview["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": task_package_preview["admissibility_gate_hash"],
        "governed_task_package_preview_hash": task_package_preview["preview_hash"],
        "human_approval_hash": human_approval["approval_hash"],
        "handoff_boundary_state": READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
        "target_provider_boundary": TARGET_PROVIDER_BOUNDARY,
        "allowed_provider_kind": ALLOWED_PROVIDER_KIND,
        "workspace_scope_preview": WORKSPACE_SCOPE_PREVIEW,
        "timeout_policy_preview": TIMEOUT_POLICY_PREVIEW,
        "constraints": _canonical_copy(task_package_preview.get("constraints", [])),
        "forbidden_operations": list(dict.fromkeys(list(task_package_preview.get("forbidden_operations", [])) + list(FORBIDDEN_OPERATIONS))),
        "authority_boundary": _authority_boundary(human_approval_present=True),
        "handoff_preview_status": READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
        "preview_only": True,
        "executable": False,
        "dispatchable": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "explicit_dispatch_authorization_required": True,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    }
    preview["handoff_preview_hash"] = canonical_hash(_handoff_hash_input(preview))
    return preview


def validate_governed_handoff_package_preview(preview: Any) -> dict:
    """Validate that a handoff preview remains non-executing and non-dispatching."""

    errors: list[str] = []
    if not isinstance(preview, dict):
        return {"valid": False, "status": HANDOFF_PREVIEW_REJECTED, "errors": ["preview must be a dict"]}
    if preview.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if preview.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if preview.get("handoff_preview_status") not in ALLOWED_HANDOFF_PREVIEW_STATUSES:
        errors.append("handoff_preview_status invalid")
    if preview.get("handoff_boundary_state") not in ALLOWED_HANDOFF_PREVIEW_STATUSES:
        errors.append("handoff_boundary_state invalid")
    for field in (
        "replay_identity",
        "source_ingress_artifact_hash",
        "semantic_contract_candidate_hash",
        "admissibility_gate_hash",
        "governed_task_package_preview_hash",
        "human_approval_hash",
        "handoff_preview_hash",
    ):
        if not isinstance(preview.get(field), str) or not preview.get(field):
            errors.append(f"{field} is required")
    if not isinstance(preview.get("provenance"), dict) or not preview["provenance"]:
        errors.append("provenance is required")
    for field in ("preview_only", "explicit_dispatch_authorization_required"):
        if preview.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in (
        "executable",
        "dispatchable",
        "execution_performed",
        "codex_dispatch_performed",
        "provider_dispatch_performed",
        "autonomous_continuation_performed",
    ):
        if preview.get(field) is not False:
            errors.append(f"{field} must be false")
    boundary = preview.get("authority_boundary", {})
    for field in (
        "execution_authorized",
        "dispatch_authorized",
        "codex_dispatch_authorized",
        "provider_dispatch_authorized",
        "governance_execution_approved",
        "autonomous_continuation_authorized",
    ):
        if boundary.get(field) is not False:
            errors.append(f"authority_boundary.{field} must be false")
    expected_hash = canonical_hash(_handoff_hash_input(preview)) if not errors else None
    if expected_hash is not None and preview.get("handoff_preview_hash") != expected_hash:
        errors.append("handoff_preview_hash mismatch")
    return {
        "valid": not errors,
        "status": preview.get("handoff_preview_status", HANDOFF_PREVIEW_REJECTED),
        "errors": errors,
    }


__all__ = [
    "ALLOWED_HANDOFF_PREVIEW_STATUSES",
    "ARTIFACT_TYPE",
    "HANDOFF_PREVIEW_REJECTED",
    "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION",
    "SCHEMA_VERSION",
    "create_governed_handoff_package_preview",
    "validate_governed_handoff_package_preview",
]
