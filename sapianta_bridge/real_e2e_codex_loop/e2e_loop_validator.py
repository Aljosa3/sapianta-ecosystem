"""Fail-closed validation for the real bounded Codex E2E loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sapianta_bridge.provider_connectors.bounded_execution_runtime import validate_bounded_execution_runtime_request

from .e2e_loop_binding import validate_e2e_loop_binding
from .e2e_loop_identity import validate_e2e_loop_identity
from .e2e_loop_request import REQUIRED_PROVIDER_ID


FORBIDDEN_FLAGS = (
    "manual_copy_paste_required",
    "hidden_prompt_rewriting_present",
    "provider_routing_present",
    "retry_present",
    "fallback_present",
    "orchestration_present",
    "autonomous_continuation_present",
)


def validate_e2e_loop_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if hasattr(request, "to_dict") else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "e2e_loop_request", "reason": "must be an object"}]}
    for field in (
        "loop_identity",
        "loop_id",
        "chatgpt_request",
        "provider_id",
        "workspace_path",
        "timeout_seconds",
        "execution_authorized",
        "approved_by",
        "codex_executable",
        "replay_identity",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing e2e loop request field"})
    for field in ("loop_id", "chatgpt_request", "provider_id", "workspace_path", "approved_by", "codex_executable", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "e2e loop request field must be non-empty"})
    if value.get("provider_id") != REQUIRED_PROVIDER_ID:
        errors.append({"field": "provider_id", "reason": "real E2E Codex loop requires provider_id codex_cli"})
    if value.get("execution_authorized") is not True:
        errors.append({"field": "execution_authorized", "reason": "explicit human authorization is required"})
    if value.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "execution must be approved by human"})
    if not isinstance(value.get("timeout_seconds"), int) or value.get("timeout_seconds", 0) <= 0:
        errors.append({"field": "timeout_seconds", "reason": "bounded timeout is required"})
    if isinstance(value.get("workspace_path"), str):
        workspace = Path(value["workspace_path"])
        if ".." in workspace.parts or not workspace.exists() or not workspace.is_dir():
            errors.append({"field": "workspace_path", "reason": "workspace must be an existing bounded directory"})
    identity_validation = validate_e2e_loop_identity(value.get("loop_identity"), chatgpt_request=value.get("chatgpt_request", ""))
    errors.extend(identity_validation["errors"])
    for field in FORBIDDEN_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden e2e loop behavior present"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "e2e loop request must be replay-safe"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}


def validate_e2e_loop_response(response: Any, request: dict[str, Any] | None = None) -> dict[str, Any]:
    value = response.to_dict() if hasattr(response, "to_dict") else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "e2e_loop_response", "reason": "must be an object"}]}
    for field in (
        "loop_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "result_return_id",
        "replay_identity",
        "execution_status",
        "chatgpt_response_payload",
        "loop_binding",
        "evidence_references",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing e2e loop response field"})
    binding_validation = validate_e2e_loop_binding(value.get("loop_binding"))
    errors.extend(binding_validation["errors"])
    if request is not None:
        for field in ("loop_id", "provider_id", "replay_identity"):
            if value.get(field) != request.get(field):
                errors.append({"field": field, "reason": "e2e response/request mismatch"})
    payload = value.get("chatgpt_response_payload")
    if not isinstance(payload, dict) or payload.get("interpretation_ready") is not True:
        errors.append({"field": "chatgpt_response_payload", "reason": "response payload must be interpretation-ready"})
    if not isinstance(value.get("evidence_references"), dict) or not value.get("evidence_references"):
        errors.append({"field": "evidence_references", "reason": "response must reference evidence"})
    for field in FORBIDDEN_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden e2e loop behavior present"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "e2e loop response must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "binding_valid": binding_validation["valid"],
        "identity_continuity_valid": not any("mismatch" in error["reason"] for error in errors),
        "replay_safe": not errors,
    }


def validate_real_e2e_runtime_request(*, gate_request: dict[str, Any], codex_executable: str) -> dict[str, Any]:
    return validate_bounded_execution_runtime_request(
        gate_request=gate_request,
        codex_executable=codex_executable,
    )
