"""Replay-safe provider connector evidence."""

from __future__ import annotations

from typing import Any

from .connector_identity import CONNECTOR_MODE_PREPARE_ONLY


def connector_evidence(
    *,
    connector_request: dict[str, Any],
    connector_response: dict[str, Any] | None = None,
    request_validation: dict[str, Any] | None = None,
    response_validation: dict[str, Any] | None = None,
    task_artifact_written: bool = False,
) -> dict[str, Any]:
    response = connector_response or {}
    request_status = request_validation or {"valid": False}
    response_status = response_validation or {"valid": False}
    return {
        "connector_id": connector_request.get("connector_id", ""),
        "connector_mode": connector_request.get("connector_mode", CONNECTOR_MODE_PREPARE_ONLY),
        "provider_id": connector_request.get("provider_id", ""),
        "envelope_id": connector_request.get("envelope_id", ""),
        "invocation_id": connector_request.get("invocation_id", ""),
        "transport_id": connector_request.get("transport_id", ""),
        "replay_identity": connector_request.get("replay_identity", ""),
        "task_artifact_path": connector_request.get("bounded_task_artifact_path", ""),
        "expected_result_artifact_path": connector_request.get("expected_result_artifact_path", ""),
        "result_artifact_path": response.get("result_artifact_path", ""),
        "connector_request_valid": request_status.get("valid", False),
        "connector_response_valid": response_status.get("valid", False),
        "task_artifact_written": task_artifact_written,
        "codex_cli_invoked": False,
        "real_external_api_call_present": False,
        "shell_execution_present": False,
        "network_execution_present": False,
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
        "provider_auto_selection_present": False,
        "connector_artifact_is_execution_authority": False,
        "provider_response_is_governance_decision": False,
        "replay_safe": request_status.get("valid") is True and (
            not response or response_status.get("valid") is True
        ),
    }


def validate_connector_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "connector_evidence", "reason": "must be an object"}]}
    for field in (
        "connector_id",
        "connector_mode",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "connector_request_valid",
        "task_artifact_written",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing connector evidence field"})
    if evidence.get("connector_mode") != CONNECTOR_MODE_PREPARE_ONLY:
        errors.append({"field": "connector_mode", "reason": "connector evidence must remain PREPARE_ONLY"})
    for field in (
        "codex_cli_invoked",
        "real_external_api_call_present",
        "shell_execution_present",
        "network_execution_present",
        "routing_present",
        "retry_present",
        "fallback_present",
        "orchestration_present",
        "autonomous_execution_present",
        "provider_auto_selection_present",
        "connector_artifact_is_execution_authority",
        "provider_response_is_governance_decision",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "connector evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
