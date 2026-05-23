"""Controlled execution handoff through the canonical native bridge path."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_ACTION,
    handle_native_message,
)
from agol_bridge.transport.local_governed_transport import canonical_hash

from .controlled_execution_continuity_preview import (
    READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
    validate_controlled_execution_continuity_preview,
)

ARTIFACT_TYPE = "CONTROLLED_EXECUTION_HANDOFF_V1"
SCHEMA_VERSION = "1.0"
EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
EXECUTION_FAILED = "EXECUTION_FAILED"
EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
ALLOWED_EXECUTION_STATUSES = (EXECUTION_COMPLETED, EXECUTION_FAILED, EXECUTION_BLOCKED)
CODEX_PROVIDER = "BOUNDED_CODEX_CLI_PROVIDER"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _execution_result_hash(result_summary: dict) -> str:
    return canonical_hash(result_summary)


def _governance_hash_input(artifact: dict) -> dict:
    return {
        "replay_identity": artifact["replay_identity"],
        "source_dispatch_authorization_hash": artifact["source_dispatch_authorization_hash"],
        "source_continuity_preview_hash": artifact["source_continuity_preview_hash"],
        "execution_path_used": artifact["execution_path_used"],
        "execution_status": artifact["execution_status"],
        "execution_result_hash": artifact["execution_result_hash"],
        "execution_boundary": artifact["execution_boundary"],
    }


def _blocked(*, continuity_preview: dict | None, reason: str) -> dict:
    preview = continuity_preview if isinstance(continuity_preview, dict) else {}
    result_summary = {
        "status": EXECUTION_BLOCKED,
        "reason": reason,
        "native_response_status": "NOT_CALLED",
        "provider_status": "NOT_INVOKED",
    }
    artifact = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": preview.get("replay_identity", "UNKNOWN"),
        "provenance": {
            "source": "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1",
            "continuity_preview_present": isinstance(continuity_preview, dict),
            "rejection_reason": reason,
        },
        "source_dispatch_authorization_hash": preview.get("source_dispatch_authorization_hash", "UNKNOWN"),
        "source_continuity_preview_hash": preview.get("continuity_preview_hash", "UNKNOWN"),
        "execution_status": EXECUTION_BLOCKED,
        "execution_boundary": {
            "single_path": True,
            "single_provider": True,
            "fail_closed": True,
            "retries": False,
            "autonomous_continuation": False,
            "orchestration": False,
        },
        "execution_path_used": [],
        "native_messaging_called": False,
        "service_worker_called": False,
        "provider_invoked": False,
        "codex_provider_used": "",
        "execution_started_at": "",
        "execution_completed_at": "",
        "execution_result_summary": result_summary,
        "execution_result_hash": _execution_result_hash(result_summary),
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "rejection_reasons": [reason],
    }
    artifact["execution_governance_hash"] = canonical_hash(_governance_hash_input(artifact))
    return artifact


def _native_message(*, continuity_preview: dict, workspace_path: str, timeout_seconds: int) -> dict:
    replay_identity = continuity_preview["replay_identity"]
    return {
        "action": NATIVE_BRIDGE_ACTION,
        "request_id": f"CONTROLLED-HANDOFF-{canonical_hash(replay_identity)[7:23]}",
        "human_request": f"Review controlled execution handoff for replay {replay_identity}.",
        "session_id": f"SESSION-{canonical_hash(replay_identity)[7:23]}",
        "workspace_path": str(Path(workspace_path or Path.cwd()).expanduser().resolve()),
        "timeout_seconds": int(timeout_seconds),
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def create_controlled_execution_handoff(
    *,
    continuity_preview: Any,
    workspace_path: str | None = None,
    timeout_seconds: int = 600,
    execution_started_at: str = "1970-01-01T00:00:00Z",
    execution_completed_at: str = "1970-01-01T00:00:00Z",
    prior_execution_artifact: dict | None = None,
    native_message_handler: Callable[[dict], dict] = handle_native_message,
) -> dict:
    """Execute once through the existing service-worker/native/Python/Codex path."""

    if prior_execution_artifact and prior_execution_artifact.get("execution_performed") is True:
        return _blocked(
            continuity_preview=continuity_preview if isinstance(continuity_preview, dict) else None,
            reason="execution already performed",
        )
    if not isinstance(continuity_preview, dict):
        return _blocked(continuity_preview=None, reason="controlled execution continuity preview missing")

    validation = validate_controlled_execution_continuity_preview(continuity_preview)
    if validation.get("valid") is not True:
        return _blocked(continuity_preview=continuity_preview, reason="controlled execution continuity preview invalid")
    if continuity_preview.get("execution_continuity_status") != READY_FOR_CONTROLLED_EXECUTION_HANDOFF:
        return _blocked(continuity_preview=continuity_preview, reason="continuity preview is not READY_FOR_CONTROLLED_EXECUTION_HANDOFF")
    if not continuity_preview.get("replay_identity") or continuity_preview.get("replay_identity") == "UNKNOWN":
        return _blocked(continuity_preview=continuity_preview, reason="replay identity invalid")
    if not isinstance(continuity_preview.get("provenance"), dict) or not continuity_preview["provenance"]:
        return _blocked(continuity_preview=continuity_preview, reason="provenance missing")
    for field in ("source_dispatch_authorization_hash", "continuity_preview_hash"):
        if not isinstance(continuity_preview.get(field), str) or not continuity_preview[field]:
            return _blocked(continuity_preview=continuity_preview, reason=f"{field} missing")
    if any(
        continuity_preview.get(flag) is not False
        for flag in (
            "execution_performed",
            "codex_dispatch_performed",
            "native_messaging_called",
            "provider_invoked",
            "provider_dispatch_performed",
            "service_worker_called",
            "executable",
            "dispatched",
            "autonomous_continuation_performed",
        )
    ):
        return _blocked(continuity_preview=continuity_preview, reason="continuity preview already claims execution")

    message = _native_message(
        continuity_preview=continuity_preview,
        workspace_path=workspace_path or str(Path.cwd()),
        timeout_seconds=timeout_seconds,
    )
    native_response = native_message_handler(message)
    accepted = native_response.get("status") == NATIVE_BRIDGE_ACCEPTED
    result_artifact = native_response.get("result_artifact", {}) if accepted else {}
    codex_result = result_artifact.get("codex_cli_result", {}) if isinstance(result_artifact, dict) else {}
    provider_result = codex_result.get("provider_result", {}) if isinstance(codex_result, dict) else {}
    provider_status = codex_result.get("bounded_execution_status", provider_result.get("status", "UNKNOWN"))
    provider_invoked = codex_result.get("provider_invoked") is True
    completed = accepted and provider_status == "COMPLETED"
    execution_status = EXECUTION_COMPLETED if completed else EXECUTION_FAILED
    result_summary = {
        "status": execution_status,
        "native_response_status": native_response.get("status", "UNKNOWN"),
        "provider_status": provider_status,
        "governed_return_status": (native_response.get("governed_return") or {}).get("status", "UNKNOWN"),
        "summary": codex_result.get("summary", native_response.get("rejection_reason", "")),
        "artifact_hash": result_artifact.get("artifact_hash", ""),
    }
    artifact = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": continuity_preview["replay_identity"],
        "provenance": {
            "source": "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1",
            "continuity_preview_provenance": _canonical_copy(continuity_preview["provenance"]),
            "native_response_status": native_response.get("status", "UNKNOWN"),
        },
        "source_dispatch_authorization_hash": continuity_preview["source_dispatch_authorization_hash"],
        "source_continuity_preview_hash": continuity_preview["continuity_preview_hash"],
        "execution_status": execution_status,
        "execution_boundary": {
            "single_path": True,
            "single_provider": True,
            "fail_closed": True,
            "retries": False,
            "autonomous_continuation": False,
            "orchestration": False,
        },
        "execution_path_used": [
            "sidepanel",
            "service_worker",
            "Native Messaging",
            "Python runtime bridge",
            "bounded Codex CLI provider",
        ],
        "native_messaging_called": True,
        "service_worker_called": True,
        "provider_invoked": provider_invoked,
        "codex_provider_used": CODEX_PROVIDER if provider_invoked else "",
        "execution_started_at": str(execution_started_at),
        "execution_completed_at": str(execution_completed_at),
        "execution_result_summary": result_summary,
        "execution_result_hash": _execution_result_hash(result_summary),
        "execution_performed": accepted,
        "codex_dispatch_performed": provider_invoked,
        "autonomous_continuation_performed": False,
        "native_response": _canonical_copy(native_response),
    }
    artifact["execution_governance_hash"] = canonical_hash(_governance_hash_input(artifact))
    return artifact


def validate_controlled_execution_handoff(artifact: Any) -> dict:
    errors: list[str] = []
    if not isinstance(artifact, dict):
        return {"valid": False, "status": EXECUTION_BLOCKED, "errors": ["artifact must be a dict"]}
    if artifact.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if artifact.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if artifact.get("execution_status") not in ALLOWED_EXECUTION_STATUSES:
        errors.append("execution_status invalid")
    for field in (
        "replay_identity",
        "source_dispatch_authorization_hash",
        "source_continuity_preview_hash",
        "execution_started_at",
        "execution_completed_at",
        "execution_result_hash",
        "execution_governance_hash",
    ):
        if artifact.get("execution_status") != EXECUTION_BLOCKED and (not isinstance(artifact.get(field), str) or not artifact[field]):
            errors.append(f"{field} is required")
    if artifact.get("autonomous_continuation_performed") is not False:
        errors.append("autonomous_continuation_performed must be false")
    boundary = artifact.get("execution_boundary", {})
    if boundary.get("single_path") is not True or boundary.get("single_provider") is not True:
        errors.append("execution must remain single-path and single-provider")
    if boundary.get("retries") is not False or boundary.get("orchestration") is not False:
        errors.append("retries and orchestration must be false")
    expected_hash = canonical_hash(_governance_hash_input(artifact)) if not errors else None
    if expected_hash is not None and artifact.get("execution_governance_hash") != expected_hash:
        errors.append("execution_governance_hash mismatch")
    return {"valid": not errors, "status": artifact.get("execution_status", EXECUTION_BLOCKED), "errors": errors}


__all__ = [
    "ALLOWED_EXECUTION_STATUSES",
    "ARTIFACT_TYPE",
    "EXECUTION_BLOCKED",
    "EXECUTION_COMPLETED",
    "EXECUTION_FAILED",
    "SCHEMA_VERSION",
    "create_controlled_execution_handoff",
    "validate_controlled_execution_handoff",
]
