"""End-to-end no-copy/paste loop validation runner."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop

from .e2e_validation_case import E2EValidationCase, default_e2e_validation_case
from .e2e_validation_evidence import lineage_evidence, validation_report


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def run_e2e_no_copy_paste_validation(case: E2EValidationCase | None = None) -> dict[str, Any]:
    validation_case = case or default_e2e_validation_case()
    loop_output = run_no_copy_paste_loop(
        validation_case.chatgpt_input,
        requested_provider_id=validation_case.requested_provider_id,
        conversation_id=validation_case.conversation_id,
        timestamp=validation_case.timestamp,
    )
    bridge_output = loop_output.get("bridge_output", {})
    ingress_output = bridge_output.get("ingress_output", {})
    invocation_output = bridge_output.get("invocation_output", {})
    result_output = bridge_output.get("result_output", {})
    session_output = bridge_output.get("session_output", {})
    response = loop_output.get("loop_response", {})
    binding = loop_output.get("loop_binding", {})
    checks = {
        "chatgpt_request_bound": _non_empty(loop_output.get("loop_request", {}).get("loop_request_id")),
        "ingress_bound": _non_empty(ingress_output.get("session", {}).get("session_id")),
        "nl_to_envelope_bound": _non_empty(
            ingress_output.get("envelope_proposal", {}).get("execution_envelope", {}).get("envelope_id")
        ),
        "session_bound": _non_empty(session_output.get("session_identity", {}).get("session_id")),
        "provider_invocation_bound": _non_empty(invocation_output.get("invocation_result", {}).get("invocation_id")),
        "result_return_bound": _non_empty(result_output.get("result_payload", {}).get("result_return_id")),
        "chatgpt_response_bound": _non_empty(response.get("loop_id")),
    }
    errors: list[dict[str, str]] = []
    if loop_output.get("loop_validation", {}).get("valid") is not True:
        errors.append({"field": "loop_validation", "reason": "loop validation failed"})
    for name, passed in checks.items():
        if not passed:
            errors.append({"field": name, "reason": "required E2E binding missing"})
    envelope_id = binding.get("envelope_id")
    if envelope_id != invocation_output.get("invocation_result", {}).get("envelope_id"):
        errors.append({"field": "envelope_id", "reason": "envelope identity changed"})
    provider_id = binding.get("provider_id")
    if provider_id != validation_case.requested_provider_id:
        errors.append({"field": "provider_id", "reason": "provider identity changed"})
    if provider_id != invocation_output.get("invocation_result", {}).get("provider_id"):
        errors.append({"field": "provider_id", "reason": "provider invocation identity mismatch"})
    result_return_id = binding.get("result_return_id")
    if result_return_id != result_output.get("result_payload", {}).get("result_return_id"):
        errors.append({"field": "result_return_id", "reason": "result lineage broke"})
    if response.get("chatgpt_response_payload", {}).get("interpretation_ready") is not True:
        errors.append({"field": "chatgpt_response_payload", "reason": "response payload not interpretation-ready"})
    for field in (
        "orchestration_present",
        "retry_present",
        "provider_routing_present",
        "autonomous_execution_present",
        "hidden_memory_mutation_present",
    ):
        if loop_output.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden loop behavior detected"})
    report = validation_report(checks=checks, errors=errors)
    lineage = lineage_evidence(loop_output)
    return {
        "validation_case": validation_case.to_dict(),
        "loop_output": loop_output,
        "validation_report": report,
        "lineage_evidence": lineage,
    }
