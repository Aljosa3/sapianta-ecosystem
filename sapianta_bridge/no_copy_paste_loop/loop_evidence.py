"""Replay-safe no-copy/paste loop evidence."""

from __future__ import annotations

from typing import Any


def loop_evidence(
    *,
    binding: dict[str, Any],
    response: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "loop_id": binding.get("loop_id", ""),
        "loop_status": "COMPLETED" if validation.get("valid") else "BLOCKED",
        "bridge_bound": bool(binding.get("bridge_id")),
        "session_bound": bool(binding.get("session_id")),
        "envelope_bound": bool(binding.get("envelope_id")),
        "provider_invocation_bound": bool(binding.get("invocation_id")),
        "result_return_bound": bool(binding.get("result_return_id")),
        "response_delivered": bool(response.get("loop_id")),
        "lineage_continuity_valid": validation.get("lineage_continuity_valid", False),
        "replay_safe": validation.get("valid") is True,
        "copy_paste_removed_for_single_pass": validation.get("valid") is True,
        "chatgpt_is_governance": False,
        "natural_language_is_execution_authority": False,
        "proposal_is_execution": False,
        "provider_is_governance": False,
        "loop_is_orchestration": False,
        "orchestration_introduced": False,
        "retry_introduced": False,
        "provider_routing_introduced": False,
        "autonomous_execution_introduced": False,
        "hidden_memory_mutation_introduced": False,
    }


def validate_loop_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "loop_evidence", "reason": "must be an object"}]}
    for field in (
        "loop_id",
        "loop_status",
        "bridge_bound",
        "session_bound",
        "envelope_bound",
        "provider_invocation_bound",
        "result_return_bound",
        "response_delivered",
        "lineage_continuity_valid",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing loop evidence field"})
    for field in (
        "chatgpt_is_governance",
        "natural_language_is_execution_authority",
        "proposal_is_execution",
        "provider_is_governance",
        "loop_is_orchestration",
        "orchestration_introduced",
        "retry_introduced",
        "provider_routing_introduced",
        "autonomous_execution_introduced",
        "hidden_memory_mutation_introduced",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "loop evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
