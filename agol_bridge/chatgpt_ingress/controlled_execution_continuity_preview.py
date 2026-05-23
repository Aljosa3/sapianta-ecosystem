"""Controlled execution continuity preview after dispatch authorization.

This module shows which execution path would be used without using it. It does
not call Native Messaging, service workers, Codex, providers, subprocesses, or
runtime execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .explicit_dispatch_authorization import (
    DISPATCH_AUTHORIZED,
    validate_explicit_dispatch_authorization,
)

ARTIFACT_TYPE = "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1"
SCHEMA_VERSION = "1.0"
READY_FOR_CONTROLLED_EXECUTION_HANDOFF = "READY_FOR_CONTROLLED_EXECUTION_HANDOFF"
EXECUTION_CONTINUITY_PREVIEW_REJECTED = "EXECUTION_CONTINUITY_PREVIEW_REJECTED"
ALLOWED_CONTINUITY_PREVIEW_STATUSES = (
    READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
    EXECUTION_CONTINUITY_PREVIEW_REJECTED,
)
BOUNDARY_STATEMENT = (
    "Dispatch authorization is prerequisite visibility only. This continuity "
    "preview does not execute, dispatch Codex, call Native Messaging, call a "
    "service worker, or invoke a provider."
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _execution_path_candidate() -> dict:
    return {
        "path_type": "CONTROLLED_EXECUTION_CONTINUITY_PATH_CANDIDATE",
        "stages": [
            {"stage": "sidepanel", "status": "PREVIEW_ONLY", "called": False},
            {"stage": "service_worker", "status": "NOT_CALLED", "called": False},
            {"stage": "Native Messaging host", "status": "NOT_CALLED", "called": False},
            {"stage": "Python runtime bridge", "status": "NOT_CALLED", "called": False},
            {"stage": "bounded Codex CLI provider", "status": "NOT_CALLED", "called": False},
        ],
    }


def _authority_boundary(*, dispatch_authorized: bool) -> dict:
    return {
        "dispatch_authorized": dispatch_authorized,
        "execution_authorized": False,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "native_messaging_called": False,
        "provider_invoked": False,
        "autonomous_continuation_authorized": False,
        "boundary_statement": BOUNDARY_STATEMENT,
    }


def _continuity_hash_input(preview: dict) -> dict:
    return {
        "replay_identity": preview["replay_identity"],
        "source_dispatch_authorization_hash": preview["source_dispatch_authorization_hash"],
        "source_handoff_preview_hash": preview["source_handoff_preview_hash"],
        "human_approval_hash": preview["human_approval_hash"],
        "governed_task_package_preview_hash": preview["governed_task_package_preview_hash"],
        "semantic_contract_candidate_hash": preview["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": preview["admissibility_gate_hash"],
        "execution_path_candidate": preview["execution_path_candidate"],
        "authority_boundary": preview["authority_boundary"],
        "execution_continuity_status": preview["execution_continuity_status"],
    }


def _reject_preview(*, dispatch_authorization: dict | None, reason: str) -> dict:
    auth = dispatch_authorization if isinstance(dispatch_authorization, dict) else {}
    provenance = auth.get("provenance", {}) if isinstance(auth.get("provenance"), dict) else {}
    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": auth.get("replay_identity", "UNKNOWN"),
        "provenance": {
            "source": "EXPLICIT_DISPATCH_AUTHORIZATION_V1",
            "dispatch_authorization_present": isinstance(dispatch_authorization, dict),
            "rejection_reason": reason,
        },
        "source_dispatch_authorization_hash": auth.get("dispatch_authorization_hash", "UNKNOWN"),
        "source_handoff_preview_hash": auth.get("source_handoff_preview_hash", "UNKNOWN"),
        "human_approval_hash": auth.get("human_approval_hash", "UNKNOWN"),
        "governed_task_package_preview_hash": provenance.get("governed_task_package_preview_hash", "UNKNOWN"),
        "semantic_contract_candidate_hash": provenance.get("semantic_contract_candidate_hash", "NONE"),
        "admissibility_gate_hash": auth.get("admissibility_gate_hash", "NONE"),
        "execution_continuity_status": EXECUTION_CONTINUITY_PREVIEW_REJECTED,
        "execution_path_candidate": _execution_path_candidate(),
        "native_messaging_path_candidate": {"stage": "Native Messaging host", "status": "NOT_CALLED", "called": False},
        "service_worker_path_candidate": {"stage": "service_worker", "status": "NOT_CALLED", "called": False},
        "python_runtime_bridge_candidate": {"stage": "Python runtime bridge", "status": "NOT_CALLED", "called": False},
        "codex_provider_candidate": {"stage": "bounded Codex CLI provider", "status": "NOT_CALLED", "called": False},
        "workspace_scope_candidate": auth.get("workspace_scope_preview", "UNKNOWN"),
        "timeout_policy_candidate": auth.get("timeout_policy_preview", "UNKNOWN"),
        "authority_boundary": _authority_boundary(dispatch_authorized=False),
        "preview_only": True,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "native_messaging_called": False,
        "provider_invoked": False,
        "provider_dispatch_performed": False,
        "service_worker_called": False,
        "executable": False,
        "dispatched": False,
        "autonomous_continuation_performed": False,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
        "rejection_reasons": [reason],
    }
    preview["continuity_preview_hash"] = canonical_hash(_continuity_hash_input(preview))
    return preview


def create_controlled_execution_continuity_preview(*, dispatch_authorization: Any) -> dict:
    """Create execution-path visibility after dispatch authorization and stop."""

    if not isinstance(dispatch_authorization, dict):
        return _reject_preview(dispatch_authorization=None, reason="dispatch authorization missing")

    validation = validate_explicit_dispatch_authorization(dispatch_authorization)
    if validation.get("valid") is not True:
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="dispatch authorization invalid",
        )
    if dispatch_authorization.get("dispatch_authorization_status") != DISPATCH_AUTHORIZED:
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="dispatch authorization status is not DISPATCH_AUTHORIZED",
        )
    if dispatch_authorization.get("dispatch_authorized") is not True:
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="dispatch_authorized flag is not true",
        )
    if not dispatch_authorization.get("replay_identity") or dispatch_authorization.get("replay_identity") == "UNKNOWN":
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="replay identity missing",
        )
    provenance = dispatch_authorization.get("provenance")
    if not isinstance(provenance, dict) or not provenance:
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="provenance missing",
        )
    if provenance.get("replay_identity") and provenance["replay_identity"] != dispatch_authorization["replay_identity"]:
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="replay identity mismatch",
        )
    for field in (
        "source_handoff_preview_hash",
        "human_approval_hash",
        "admissibility_gate_hash",
        "dispatch_authorization_hash",
    ):
        if not isinstance(dispatch_authorization.get(field), str) or not dispatch_authorization[field]:
            return _reject_preview(
                dispatch_authorization=dispatch_authorization,
                reason=f"{field} missing",
            )
    for field in ("governed_task_package_preview_hash", "semantic_contract_candidate_hash"):
        if not isinstance(provenance.get(field), str) or not provenance[field]:
            return _reject_preview(
                dispatch_authorization=dispatch_authorization,
                reason=f"{field} missing",
            )
    if any(
        dispatch_authorization.get(flag) is not False
        for flag in (
            "execution_performed",
            "codex_dispatch_performed",
            "provider_dispatch_performed",
            "native_messaging_called",
            "executable",
            "dispatched",
            "autonomous_continuation_performed",
        )
    ):
        return _reject_preview(
            dispatch_authorization=dispatch_authorization,
            reason="execution, provider, native messaging, or continuation claim exists",
        )

    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": dispatch_authorization["replay_identity"],
        "provenance": {
            "source": "EXPLICIT_DISPATCH_AUTHORIZATION_V1",
            "dispatch_authorization_provenance": _canonical_copy(dispatch_authorization["provenance"]),
            "dispatch_authorization_status": dispatch_authorization["dispatch_authorization_status"],
        },
        "source_dispatch_authorization_hash": dispatch_authorization["dispatch_authorization_hash"],
        "source_handoff_preview_hash": dispatch_authorization["source_handoff_preview_hash"],
        "human_approval_hash": dispatch_authorization["human_approval_hash"],
        "governed_task_package_preview_hash": provenance["governed_task_package_preview_hash"],
        "semantic_contract_candidate_hash": provenance["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": dispatch_authorization["admissibility_gate_hash"],
        "execution_continuity_status": READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
        "execution_path_candidate": _execution_path_candidate(),
        "native_messaging_path_candidate": {"stage": "Native Messaging host", "status": "NOT_CALLED", "called": False},
        "service_worker_path_candidate": {"stage": "service_worker", "status": "NOT_CALLED", "called": False},
        "python_runtime_bridge_candidate": {"stage": "Python runtime bridge", "status": "NOT_CALLED", "called": False},
        "codex_provider_candidate": {"stage": "bounded Codex CLI provider", "status": "NOT_CALLED", "called": False},
        "workspace_scope_candidate": dispatch_authorization["workspace_scope_preview"],
        "timeout_policy_candidate": dispatch_authorization["timeout_policy_preview"],
        "authority_boundary": _authority_boundary(dispatch_authorized=True),
        "preview_only": True,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "native_messaging_called": False,
        "provider_invoked": False,
        "provider_dispatch_performed": False,
        "service_worker_called": False,
        "executable": False,
        "dispatched": False,
        "autonomous_continuation_performed": False,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    }
    preview["continuity_preview_hash"] = canonical_hash(_continuity_hash_input(preview))
    return preview


def validate_controlled_execution_continuity_preview(preview: Any) -> dict:
    """Validate that controlled execution continuity preview is non-executing."""

    errors: list[str] = []
    if not isinstance(preview, dict):
        return {"valid": False, "status": EXECUTION_CONTINUITY_PREVIEW_REJECTED, "errors": ["preview must be a dict"]}
    if preview.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if preview.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if preview.get("execution_continuity_status") not in ALLOWED_CONTINUITY_PREVIEW_STATUSES:
        errors.append("execution_continuity_status invalid")
    for field in (
        "replay_identity",
        "source_dispatch_authorization_hash",
        "source_handoff_preview_hash",
        "human_approval_hash",
        "governed_task_package_preview_hash",
        "semantic_contract_candidate_hash",
        "admissibility_gate_hash",
        "continuity_preview_hash",
    ):
        if not isinstance(preview.get(field), str) or not preview.get(field):
            errors.append(f"{field} is required")
    if not isinstance(preview.get("provenance"), dict) or not preview["provenance"]:
        errors.append("provenance is required")
    for field in ("preview_only",):
        if preview.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in (
        "execution_performed",
        "codex_dispatch_performed",
        "native_messaging_called",
        "provider_invoked",
        "provider_dispatch_performed",
        "service_worker_called",
        "executable",
        "dispatched",
        "autonomous_continuation_performed",
    ):
        if preview.get(field) is not False:
            errors.append(f"{field} must be false")
    stages = (preview.get("execution_path_candidate") or {}).get("stages", [])
    for stage in stages:
        if stage.get("status") not in {"PREVIEW_ONLY", "NOT_CALLED"} or stage.get("called") is not False:
            errors.append("execution path stages must be PREVIEW_ONLY or NOT_CALLED")
    expected_hash = canonical_hash(_continuity_hash_input(preview)) if not errors else None
    if expected_hash is not None and preview.get("continuity_preview_hash") != expected_hash:
        errors.append("continuity_preview_hash mismatch")
    return {
        "valid": not errors,
        "status": preview.get("execution_continuity_status", EXECUTION_CONTINUITY_PREVIEW_REJECTED),
        "errors": errors,
    }


__all__ = [
    "ALLOWED_CONTINUITY_PREVIEW_STATUSES",
    "ARTIFACT_TYPE",
    "EXECUTION_CONTINUITY_PREVIEW_REJECTED",
    "READY_FOR_CONTROLLED_EXECUTION_HANDOFF",
    "SCHEMA_VERSION",
    "create_controlled_execution_continuity_preview",
    "validate_controlled_execution_continuity_preview",
]
