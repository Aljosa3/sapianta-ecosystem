"""Replay-safe transport evidence."""

from __future__ import annotations

from typing import Any


def transport_evidence(
    *,
    request: dict[str, Any],
    runtime_output: dict[str, Any],
    guard_status: dict[str, Any],
) -> dict[str, Any]:
    runtime_result = runtime_output["runtime_result"]
    transport_binding = request["transport_binding"]
    return {
        "transport_executed": guard_status["transport_allowed"]
        and runtime_output["runtime_evidence"]["runtime_executed"],
        "transport_id": transport_binding["transport_id"],
        "provider_id": request["provider_id"],
        "envelope_id": request["envelope_id"],
        "runtime_status": runtime_result["runtime_status"],
        "transport_binding_valid": guard_status["transport_binding_valid"],
        "runtime_binding_valid": guard_status["runtime_binding_valid"],
        "authority_preserved": guard_status["authority_preserved"],
        "workspace_preserved": guard_status["workspace_preserved"],
        "replay_safe": runtime_output["runtime_evidence"]["replay_safe"] is True,
        "routing_present": False,
        "orchestration_present": False,
        "fallback_present": False,
        "retry_present": False,
    }
