"""Replay-safe active ChatGPT bridge evidence."""

from __future__ import annotations

from typing import Any


def bridge_evidence(
    *,
    binding: dict[str, Any],
    response: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bridge_id": binding.get("bridge_id", ""),
        "bridge_status": "COMPLETED" if validation.get("valid") else "BLOCKED",
        "ingress_bound": bool(binding.get("ingress_session_id")),
        "envelope_bound": bool(binding.get("envelope_id")),
        "session_bound": bool(binding.get("session_id")),
        "provider_invocation_bound": bool(binding.get("invocation_id")),
        "result_return_bound": bool(binding.get("result_return_id")),
        "response_created": bool(response.get("bridge_id")),
        "request_valid": validation.get("request_valid", False),
        "binding_valid": validation.get("binding_valid", False),
        "response_valid": validation.get("response_valid", False),
        "lifecycle_valid": validation.get("lifecycle_valid", False),
        "replay_safe": validation.get("valid") is True,
        "orchestration_introduced": False,
        "retry_introduced": False,
        "provider_routing_introduced": False,
        "autonomous_execution_introduced": False,
        "hidden_memory_mutation_introduced": False,
        "copy_paste_reduction_ready": validation.get("valid") is True,
    }


def validate_bridge_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "bridge_evidence", "reason": "must be an object"}]}
    required = (
        "bridge_id",
        "bridge_status",
        "ingress_bound",
        "envelope_bound",
        "session_bound",
        "provider_invocation_bound",
        "result_return_bound",
        "response_created",
        "replay_safe",
        "copy_paste_reduction_ready",
    )
    for field in required:
        if field not in evidence:
            errors.append({"field": field, "reason": "missing bridge evidence field"})
    for field in (
        "orchestration_introduced",
        "retry_introduced",
        "provider_routing_introduced",
        "autonomous_execution_introduced",
        "hidden_memory_mutation_introduced",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "bridge evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
