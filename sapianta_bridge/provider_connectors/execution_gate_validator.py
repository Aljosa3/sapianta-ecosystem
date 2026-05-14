"""Fail-closed validation for bounded execution gate requests and responses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .connector_validator import validate_connector_request
from .execution_gate_binding import validate_execution_gate_binding
from .execution_gate_identity import validate_execution_gate_identity
from .execution_gate_request import (
    EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK,
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
)
from .execution_gate_response import EXECUTION_GATE_RESPONSE_STATUSES


MAX_TIMEOUT_SECONDS = 300
SUPPORTED_EXECUTION_GATE_OPERATIONS = (
    EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK,
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
)

FORBIDDEN_REQUEST_FLAGS = (
    "prepared_artifact_is_execution_authority",
    "arbitrary_command_execution_present",
    "shell_execution_present",
    "network_execution_present",
    "routing_present",
    "retry_present",
    "fallback_present",
    "orchestration_present",
    "autonomous_execution_present",
    "background_execution_present",
    "concurrent_execution_present",
    "memory_mutation_present",
)

FORBIDDEN_RESPONSE_FLAGS = (
    "provider_response_is_governance_decision",
    "arbitrary_command_execution_present",
    "shell_execution_present",
    "network_execution_present",
    "routing_present",
    "retry_present",
    "fallback_present",
    "orchestration_present",
    "autonomous_execution_present",
)


def _as_dict(value: Any) -> Any:
    return value.to_dict() if hasattr(value, "to_dict") else value


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate_workspace_boundary(*, workspace_path: str, artifact_path: str) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(workspace_path, str) or not workspace_path.strip():
        errors.append({"field": "workspace_path", "reason": "workspace path must be non-empty"})
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        errors.append({"field": "artifact_path", "reason": "artifact path must be non-empty"})
    if errors:
        return {"valid": False, "errors": errors}
    workspace = Path(workspace_path)
    artifact = Path(artifact_path)
    if ".." in workspace.parts:
        errors.append({"field": "workspace_path", "reason": "workspace path must not contain parent traversal"})
    if ".." in artifact.parts:
        errors.append({"field": "artifact_path", "reason": "artifact path must not contain parent traversal"})
    if not workspace.exists() or not workspace.is_dir():
        errors.append({"field": "workspace_path", "reason": "workspace path must exist and be a directory"})
    if not artifact.exists():
        errors.append({"field": "artifact_path", "reason": "artifact path must exist before execution"})
    if artifact.exists() and not _is_relative_to(artifact, workspace):
        errors.append({"field": "artifact_path", "reason": "artifact path escapes workspace"})
    return {"valid": not errors, "errors": errors}


def validate_execution_gate_request(request: Any) -> dict[str, Any]:
    value = _as_dict(request)
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_gate_request", "reason": "must be an object"}]}
    required = (
        "execution_gate_id",
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "connector_request",
        "execution_authorized",
        "approved_by",
        "workspace_path",
        "timeout_seconds",
        "operation",
        "execution_gate_binding",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing execution gate request field"})
    for field in (
        "execution_gate_id",
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "approved_by",
        "workspace_path",
        "operation",
    ):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "execution gate request field must be non-empty"})
    if value.get("execution_authorized") is not True:
        errors.append({"field": "execution_authorized", "reason": "explicit execution authorization is required"})
    if value.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "execution must be explicitly approved by human"})
    if not isinstance(value.get("timeout_seconds"), int):
        errors.append({"field": "timeout_seconds", "reason": "timeout must be an explicit integer"})
    elif value["timeout_seconds"] <= 0 or value["timeout_seconds"] > MAX_TIMEOUT_SECONDS:
        errors.append({"field": "timeout_seconds", "reason": "timeout must be positive and bounded"})
    if value.get("operation") not in SUPPORTED_EXECUTION_GATE_OPERATIONS:
        errors.append({"field": "operation", "reason": "unsupported execution gate operation"})
    connector_validation = validate_connector_request(value.get("connector_request"))
    identity_validation = validate_execution_gate_identity(
        {
            "execution_gate_id": value.get("execution_gate_id", ""),
            "connector_id": value.get("connector_id", ""),
            "provider_id": value.get("provider_id", ""),
            "envelope_id": value.get("envelope_id", ""),
            "invocation_id": value.get("invocation_id", ""),
            "replay_identity": value.get("replay_identity", ""),
            "immutable": True,
            "replay_safe": True,
        }
    )
    binding_validation = validate_execution_gate_binding(value.get("execution_gate_binding"))
    errors.extend(connector_validation["errors"])
    errors.extend(identity_validation["errors"])
    errors.extend(binding_validation["errors"])
    workspace_validation = {"valid": False, "errors": []}
    if isinstance(value.get("connector_request"), dict):
        workspace_validation = validate_workspace_boundary(
            workspace_path=value.get("workspace_path", ""),
            artifact_path=value["connector_request"].get("bounded_task_artifact_path", ""),
        )
        errors.extend(workspace_validation["errors"])
        connector_request = value["connector_request"]
        for field in ("connector_id", "provider_id", "envelope_id", "invocation_id", "transport_id", "replay_identity"):
            if value.get(field) != connector_request.get(field):
                errors.append({"field": field, "reason": "execution gate request/connector request mismatch"})
    if binding_validation["valid"]:
        binding = value["execution_gate_binding"]
        binding_map = {
            "execution_gate_id": "execution_gate_id",
            "connector_id": "connector_id",
            "transport_id": "transport_id",
            "provider_id": "provider_id",
            "envelope_id": "envelope_id",
            "invocation_id": "invocation_id",
            "replay_identity": "replay_identity",
            "workspace_path": "workspace_path",
            "timeout_seconds": "timeout_seconds",
            "operation": "operation",
        }
        for request_field, binding_field in binding_map.items():
            if value.get(request_field) != binding.get(binding_field):
                errors.append({"field": request_field, "reason": "execution gate request/binding mismatch"})
    for field in FORBIDDEN_REQUEST_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "execution gate request contains forbidden behavior"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "execution gate request must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "authorization_valid": value.get("execution_authorized") is True and value.get("approved_by") == "human",
        "connector_request_valid": connector_validation["valid"],
        "workspace_boundary_valid": workspace_validation["valid"],
        "binding_valid": binding_validation["valid"],
        "replay_safe": not errors,
    }


def validate_execution_gate_response(response: Any, request: dict[str, Any] | None = None) -> dict[str, Any]:
    value = _as_dict(response)
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_gate_response", "reason": "must be an object"}]}
    required = (
        "execution_gate_id",
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "status",
        "stdout",
        "stderr",
        "exit_code",
        "execution_started_at",
        "execution_ended_at",
        "result_metadata",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing execution gate response field"})
    if value.get("status") not in EXECUTION_GATE_RESPONSE_STATUSES:
        errors.append({"field": "status", "reason": "unsupported execution gate response status"})
    if not isinstance(value.get("exit_code"), int):
        errors.append({"field": "exit_code", "reason": "exit code must be an integer"})
    if not isinstance(value.get("stdout"), str):
        errors.append({"field": "stdout", "reason": "stdout must be captured as a string"})
    if not isinstance(value.get("stderr"), str):
        errors.append({"field": "stderr", "reason": "stderr must be captured as a string"})
    if not isinstance(value.get("result_metadata"), dict):
        errors.append({"field": "result_metadata", "reason": "result metadata must be an object"})
    if request is not None:
        for field in ("execution_gate_id", "connector_id", "provider_id", "envelope_id", "invocation_id", "transport_id", "replay_identity"):
            if value.get(field) != request.get(field):
                errors.append({"field": field, "reason": "execution gate response/request mismatch"})
    for field in FORBIDDEN_RESPONSE_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "execution gate response contains forbidden behavior"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "execution gate response must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "identity_continuity_valid": not any("mismatch" in error["reason"] for error in errors),
        "replay_safe": not errors,
    }
