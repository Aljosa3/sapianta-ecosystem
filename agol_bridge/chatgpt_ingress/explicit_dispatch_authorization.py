"""Explicit dispatch authorization evidence after governed handoff preview.

This module creates dispatch authorization evidence only. It does not execute,
dispatch Codex, call Native Messaging, invoke providers, create runnable
provider tasks, or continue autonomously.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .governed_handoff_package_preview import (
    READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
    validate_governed_handoff_package_preview,
)

ARTIFACT_TYPE = "EXPLICIT_DISPATCH_AUTHORIZATION_V1"
SCHEMA_VERSION = "1.0"
DISPATCH_AUTHORIZED = "DISPATCH_AUTHORIZED"
DISPATCH_REJECTED = "DISPATCH_REJECTED"
ALLOWED_DISPATCH_AUTHORIZATION_STATUSES = (DISPATCH_AUTHORIZED, DISPATCH_REJECTED)
READY_FOR_CONTROLLED_EXECUTION_CONTINUITY = "READY_FOR_CONTROLLED_EXECUTION_CONTINUITY"
BOUNDARY_STATEMENT = (
    "Dispatch authorization is explicit and replay-visible, but it is not "
    "execution. Codex, provider execution, and Native Messaging remain uncalled."
)

FORBIDDEN_OPERATIONS = (
    "codex_dispatch",
    "native_messaging_execution",
    "provider_execution",
    "runtime_execution",
    "automatic_dispatch",
    "automatic_execution",
    "autonomous_continuation",
    "orchestration",
    "retries",
    "background_workers",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _dispatch_authority_boundary(*, dispatch_authorized: bool) -> dict:
    return {
        "dispatch_authorized": dispatch_authorized,
        "execution_authorized": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "native_messaging_called": False,
        "autonomous_continuation_authorized": False,
        "boundary_statement": BOUNDARY_STATEMENT,
    }


def _authorization_hash_input(authorization: dict) -> dict:
    return {
        "replay_identity": authorization["replay_identity"],
        "source_ingress_artifact_hash": authorization["provenance"]["source_ingress_artifact_hash"],
        "semantic_contract_candidate_hash": authorization["provenance"]["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": authorization["admissibility_gate_hash"],
        "governed_task_package_preview_hash": authorization["provenance"]["governed_task_package_preview_hash"],
        "human_approval_hash": authorization["human_approval_hash"],
        "governed_handoff_preview_hash": authorization["source_handoff_preview_hash"],
        "dispatch_authorization_status": authorization["dispatch_authorization_status"],
        "provider_boundary_state": authorization["provider_boundary_state"],
        "dispatch_authority_boundary": authorization["dispatch_authority_boundary"],
    }


def _reject_authorization(*, handoff_preview: dict | None, reason: str) -> dict:
    handoff = handoff_preview if isinstance(handoff_preview, dict) else {}
    authorization = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": handoff.get("replay_identity", "UNKNOWN"),
        "provenance": {
            "source": "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
            "source_ingress_artifact_hash": handoff.get("source_ingress_artifact_hash", "UNKNOWN"),
            "semantic_contract_candidate_hash": handoff.get("semantic_contract_candidate_hash", "NONE"),
            "governed_task_package_preview_hash": handoff.get("governed_task_package_preview_hash", "UNKNOWN"),
            "handoff_preview_present": isinstance(handoff_preview, dict),
            "rejection_reason": reason,
        },
        "source_handoff_preview_hash": handoff.get("handoff_preview_hash", "UNKNOWN"),
        "human_approval_hash": handoff.get("human_approval_hash", "UNKNOWN"),
        "admissibility_gate_hash": handoff.get("admissibility_gate_hash", "NONE"),
        "dispatch_authorization_status": DISPATCH_REJECTED,
        "dispatch_authorization_reason": reason,
        "dispatch_authority_boundary": _dispatch_authority_boundary(dispatch_authorized=False),
        "allowed_provider_kind": handoff.get("allowed_provider_kind", "UNKNOWN"),
        "provider_boundary_state": DISPATCH_REJECTED,
        "workspace_scope_preview": handoff.get("workspace_scope_preview", "UNKNOWN"),
        "timeout_policy_preview": handoff.get("timeout_policy_preview", "UNKNOWN"),
        "constraints": _canonical_copy(handoff.get("constraints", [])),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "dispatch_authorized": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "native_messaging_called": False,
        "executable": False,
        "dispatched": False,
        "autonomous_continuation_performed": False,
        "rejection_reasons": [reason],
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    }
    authorization["dispatch_authorization_hash"] = canonical_hash(_authorization_hash_input(authorization))
    return authorization


def create_explicit_dispatch_authorization(
    *,
    handoff_preview: Any,
    dispatch_decision: str,
    dispatch_authorization_reason: str,
) -> dict:
    """Create explicit dispatch authorization/rejection evidence and stop."""

    if not isinstance(handoff_preview, dict):
        return _reject_authorization(
            handoff_preview=None,
            reason="governed handoff package preview missing",
        )

    validation = validate_governed_handoff_package_preview(handoff_preview)
    if validation.get("valid") is not True:
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="governed handoff package preview invalid",
        )
    if handoff_preview.get("handoff_boundary_state") != READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION:
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="handoff preview is not READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION",
        )
    if not handoff_preview.get("replay_identity") or handoff_preview.get("replay_identity") == "UNKNOWN":
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="replay identity missing",
        )
    if not isinstance(handoff_preview.get("provenance"), dict) or not handoff_preview["provenance"]:
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="provenance missing",
        )
    boundary = handoff_preview.get("authority_boundary", {})
    if any(
        boundary.get(flag) is not False
        for flag in (
            "execution_authorized",
            "dispatch_authorized",
            "codex_dispatch_authorized",
            "provider_dispatch_authorized",
            "governance_execution_approved",
            "autonomous_continuation_authorized",
        )
    ):
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="authority boundary violated",
        )
    if any(
        handoff_preview.get(flag) is not False
        for flag in (
            "execution_performed",
            "codex_dispatch_performed",
            "provider_dispatch_performed",
            "autonomous_continuation_performed",
            "executable",
            "dispatchable",
        )
    ):
        return _reject_authorization(
            handoff_preview=handoff_preview,
            reason="execution or dispatch claim exists",
        )

    authorized = str(dispatch_decision or "").strip().upper() in {
        "AUTHORIZE",
        "AUTHORIZED",
        DISPATCH_AUTHORIZED,
    }
    status = DISPATCH_AUTHORIZED if authorized else DISPATCH_REJECTED
    authorization = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": handoff_preview["replay_identity"],
        "provenance": {
            "source": "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
            "source_ingress_artifact_hash": handoff_preview["source_ingress_artifact_hash"],
            "semantic_contract_candidate_hash": handoff_preview["semantic_contract_candidate_hash"],
            "governed_task_package_preview_hash": handoff_preview["governed_task_package_preview_hash"],
            "handoff_preview_provenance": _canonical_copy(handoff_preview["provenance"]),
        },
        "source_handoff_preview_hash": handoff_preview["handoff_preview_hash"],
        "human_approval_hash": handoff_preview["human_approval_hash"],
        "admissibility_gate_hash": handoff_preview["admissibility_gate_hash"],
        "dispatch_authorization_status": status,
        "dispatch_authorization_reason": str(dispatch_authorization_reason or "").strip(),
        "dispatch_authority_boundary": _dispatch_authority_boundary(dispatch_authorized=authorized),
        "allowed_provider_kind": handoff_preview["allowed_provider_kind"],
        "provider_boundary_state": READY_FOR_CONTROLLED_EXECUTION_CONTINUITY if authorized else DISPATCH_REJECTED,
        "workspace_scope_preview": handoff_preview["workspace_scope_preview"],
        "timeout_policy_preview": handoff_preview["timeout_policy_preview"],
        "constraints": _canonical_copy(handoff_preview.get("constraints", [])),
        "forbidden_operations": list(dict.fromkeys(list(handoff_preview.get("forbidden_operations", [])) + list(FORBIDDEN_OPERATIONS))),
        "dispatch_authorized": authorized,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "native_messaging_called": False,
        "executable": False,
        "dispatched": False,
        "autonomous_continuation_performed": False,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    }
    authorization["dispatch_authorization_hash"] = canonical_hash(_authorization_hash_input(authorization))
    return authorization


def validate_explicit_dispatch_authorization(authorization: Any) -> dict:
    """Validate that dispatch authorization evidence remains non-executing."""

    errors: list[str] = []
    if not isinstance(authorization, dict):
        return {"valid": False, "status": DISPATCH_REJECTED, "errors": ["authorization must be a dict"]}
    if authorization.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if authorization.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if authorization.get("dispatch_authorization_status") not in ALLOWED_DISPATCH_AUTHORIZATION_STATUSES:
        errors.append("dispatch_authorization_status invalid")
    for field in (
        "replay_identity",
        "source_handoff_preview_hash",
        "human_approval_hash",
        "admissibility_gate_hash",
        "dispatch_authorization_reason",
        "allowed_provider_kind",
        "provider_boundary_state",
        "workspace_scope_preview",
        "timeout_policy_preview",
        "dispatch_authorization_hash",
    ):
        if not isinstance(authorization.get(field), str) or not authorization.get(field):
            errors.append(f"{field} is required")
    if not isinstance(authorization.get("provenance"), dict) or not authorization["provenance"]:
        errors.append("provenance is required")
    for field in (
        "execution_performed",
        "codex_dispatch_performed",
        "provider_dispatch_performed",
        "native_messaging_called",
        "executable",
        "dispatched",
        "autonomous_continuation_performed",
    ):
        if authorization.get(field) is not False:
            errors.append(f"{field} must be false")
    boundary = authorization.get("dispatch_authority_boundary", {})
    for field in (
        "execution_authorized",
        "execution_performed",
        "codex_dispatch_performed",
        "provider_dispatch_performed",
        "native_messaging_called",
        "autonomous_continuation_authorized",
    ):
        if boundary.get(field) is not False:
            errors.append(f"dispatch_authority_boundary.{field} must be false")
    expected_hash = canonical_hash(_authorization_hash_input(authorization)) if not errors else None
    if expected_hash is not None and authorization.get("dispatch_authorization_hash") != expected_hash:
        errors.append("dispatch_authorization_hash mismatch")
    return {
        "valid": not errors,
        "status": authorization.get("dispatch_authorization_status", DISPATCH_REJECTED),
        "errors": errors,
    }


__all__ = [
    "ALLOWED_DISPATCH_AUTHORIZATION_STATUSES",
    "ARTIFACT_TYPE",
    "DISPATCH_AUTHORIZED",
    "DISPATCH_REJECTED",
    "READY_FOR_CONTROLLED_EXECUTION_CONTINUITY",
    "SCHEMA_VERSION",
    "create_explicit_dispatch_authorization",
    "validate_explicit_dispatch_authorization",
]
