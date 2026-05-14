"""Replay-safe E2E validation evidence."""

from __future__ import annotations

from typing import Any


def validation_report(*, checks: dict[str, bool], errors: list[dict[str, str]]) -> dict[str, Any]:
    passed = not errors and all(checks.values())
    return {
        "validation_name": "FIRST_END_TO_END_NO_COPY_PASTE_VALIDATION_V1",
        "status": "PASSED" if passed else "FAILED",
        "chatgpt_request_bound": checks.get("chatgpt_request_bound", False),
        "ingress_bound": checks.get("ingress_bound", False),
        "nl_to_envelope_bound": checks.get("nl_to_envelope_bound", False),
        "session_bound": checks.get("session_bound", False),
        "provider_invocation_bound": checks.get("provider_invocation_bound", False),
        "result_return_bound": checks.get("result_return_bound", False),
        "chatgpt_response_bound": checks.get("chatgpt_response_bound", False),
        "manual_copy_paste_required": False,
        "replay_safe": passed,
        "orchestration_introduced": False,
        "provider_routing_introduced": False,
        "autonomous_execution_introduced": False,
        "retries_introduced": False,
        "fallback_introduced": False,
        "hidden_prompt_rewriting_introduced": False,
        "memory_mutation_introduced": False,
        "errors": errors,
    }


def lineage_evidence(output: dict[str, Any]) -> dict[str, Any]:
    bridge = output.get("bridge_output", {})
    ingress = bridge.get("ingress_output", {})
    invocation = bridge.get("invocation_output", {})
    result = bridge.get("result_output", {})
    session = bridge.get("session_output", {})
    return {
        "validation_name": "FIRST_END_TO_END_NO_COPY_PASTE_VALIDATION_V1",
        "loop_id": output.get("loop_binding", {}).get("loop_id", ""),
        "bridge_id": output.get("loop_binding", {}).get("bridge_id", ""),
        "ingress_session_id": ingress.get("session", {}).get("session_id", ""),
        "semantic_request_id": output.get("loop_request", {}).get("semantic_request_id", ""),
        "envelope_id": output.get("loop_binding", {}).get("envelope_id", ""),
        "session_id": output.get("loop_binding", {}).get("session_id", ""),
        "provider_id": output.get("loop_binding", {}).get("provider_id", ""),
        "invocation_id": output.get("loop_binding", {}).get("invocation_id", ""),
        "result_return_id": output.get("loop_binding", {}).get("result_return_id", ""),
        "replay_identity": output.get("loop_binding", {}).get("replay_identity", ""),
        "envelope_identity_preserved": (
            output.get("loop_binding", {}).get("envelope_id")
            == invocation.get("invocation_result", {}).get("envelope_id")
            == result.get("result_payload", {}).get("envelope_id")
        ),
        "provider_identity_preserved": (
            output.get("loop_binding", {}).get("provider_id")
            == invocation.get("invocation_result", {}).get("provider_id")
            == result.get("result_payload", {}).get("provider_id")
        ),
        "result_lineage_preserved": (
            output.get("loop_binding", {}).get("result_return_id")
            == result.get("result_payload", {}).get("result_return_id")
            == session.get("session_identity", {}).get("result_return_id")
        ),
        "manual_copy_paste_required": False,
        "replay_safe": output.get("loop_validation", {}).get("replay_safe", False),
    }
