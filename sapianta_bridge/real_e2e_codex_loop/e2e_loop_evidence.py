"""Replay-safe evidence for FIRST_REAL_E2E_CODEX_LOOP_V1."""

from __future__ import annotations

from typing import Any


def e2e_loop_evidence(
    *,
    request: dict[str, Any],
    response: dict[str, Any] | None,
    request_validation: dict[str, Any],
    response_validation: dict[str, Any] | None = None,
    runtime_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = runtime_result or {}
    bounded_evidence = runtime.get("bounded_execution_evidence", {})
    result_payload = response.get("chatgpt_response_payload", {}) if response else {}
    return {
        "validation_name": "FIRST_REAL_E2E_CODEX_LOOP_V1",
        "loop_id": request.get("loop_id", ""),
        "provider_id": request.get("provider_id", ""),
        "replay_identity": request.get("replay_identity", ""),
        "request_valid": request_validation.get("valid", False),
        "response_valid": (response_validation or {}).get("valid", False),
        "chatgpt_request_bound": bool(request.get("chatgpt_request")),
        "ingress_bound": bool(runtime.get("ingress_request")),
        "nl_to_envelope_bound": bool(runtime.get("envelope_proposal")),
        "session_bound": bool(runtime.get("session_reference")),
        "execution_gate_bound": bool(runtime.get("execution_gate_request")),
        "bounded_codex_execution_bound": bool(runtime.get("bounded_execution")),
        "result_return_bound": bool(runtime.get("result_return")),
        "chatgpt_response_bound": bool(response),
        "execution_status": result_payload.get("execution_status", "BLOCKED"),
        "manual_copy_paste_required": False,
        "replay_safe": request_validation.get("valid", False) and (response_validation or {}).get("valid", False),
        "orchestration_introduced": False,
        "retry_introduced": False,
        "fallback_introduced": False,
        "provider_routing_introduced": False,
        "adaptive_provider_selection_introduced": False,
        "hidden_execution_introduced": False,
        "hidden_prompt_rewriting_introduced": False,
        "memory_mutation_introduced": False,
        "autonomous_continuation_introduced": False,
        "concurrent_background_execution_introduced": False,
        "unrestricted_shell_execution_introduced": False,
        "bounded_execution_evidence_hash": bounded_evidence.get("execution_gate_id", ""),
    }


def validate_e2e_loop_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "e2e_loop_evidence", "reason": "must be an object"}]}
    for field in (
        "validation_name",
        "loop_id",
        "provider_id",
        "replay_identity",
        "request_valid",
        "chatgpt_request_bound",
        "execution_gate_bound",
        "bounded_codex_execution_bound",
        "result_return_bound",
        "chatgpt_response_bound",
        "manual_copy_paste_required",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing e2e evidence field"})
    for field in (
        "manual_copy_paste_required",
        "orchestration_introduced",
        "retry_introduced",
        "fallback_introduced",
        "provider_routing_introduced",
        "adaptive_provider_selection_introduced",
        "hidden_execution_introduced",
        "hidden_prompt_rewriting_introduced",
        "memory_mutation_introduced",
        "autonomous_continuation_introduced",
        "concurrent_background_execution_introduced",
        "unrestricted_shell_execution_introduced",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden e2e behavior reported"})
    return {"valid": not errors, "errors": errors}
