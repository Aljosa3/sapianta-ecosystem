"""Replay-safe runtime evidence generation."""

from __future__ import annotations

from typing import Any

from .runtime_result import RuntimeResult, validate_runtime_result


def runtime_evidence(
    *,
    runtime_result: RuntimeResult,
    envelope_validation: dict[str, Any],
    guard_status: dict[str, Any],
) -> dict[str, Any]:
    result_validation = validate_runtime_result(runtime_result)
    value = runtime_result.to_dict()
    return {
        "runtime_executed": guard_status.get("runtime_allowed") is True,
        "envelope_id": value["envelope_id"],
        "provider_id": value["provider_id"],
        "runtime_status": value["runtime_status"],
        "envelope_valid": envelope_validation.get("valid", envelope_validation.get("envelope_valid", False)),
        "provider_bound": guard_status.get("provider_identity_valid") is True,
        "authority_scope_preserved": envelope_validation.get("authority_scope_valid") is True,
        "workspace_scope_preserved": envelope_validation.get("workspace_scope_valid") is True,
        "normalized_result_valid": result_validation["normalized_result_valid"],
        "replay_safe": value["replay_safe"] is True,
        "routing_present": False,
        "orchestration_present": False,
        "fallback_present": False,
        "retry_present": False,
        "external_api_calls_present": False,
    }
