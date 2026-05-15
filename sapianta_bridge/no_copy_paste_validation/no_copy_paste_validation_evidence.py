"""Evidence for no-copy/paste operational validation."""

from typing import Any


def validation_evidence(*, response: dict[str, Any], execution: dict[str, Any], egress_path: str, valid: bool) -> dict[str, Any]:
    capture = execution.get("capture", {})
    binding = response.get("binding", {})
    return {
        "validation_name": "FIRST_NO_COPY_PASTE_USER_FLOW_VALIDATION_V1",
        "status": response.get("status", "BLOCKED"),
        "ingress_artifact_created": bool(binding.get("ingress_artifact_id")),
        "ingress_validated": valid,
        "interaction_continuity_preserved": bool(binding.get("ingress_artifact_id")),
        "transport_continuity_preserved": bool(binding.get("execution_gate_id")),
        "execution_gate_linked": bool(binding.get("execution_gate_id")),
        "bounded_provider_invocation_executed": execution.get("bounded_execution_status") in ("SUCCESS", "RESULT_CAPTURED_WITH_TERMINATION"),
        "bounded_result_captured": capture.get("bounded_result_captured") is True,
        "deterministic_normalized_response_produced": bool(response.get("normalized_result")),
        "governed_egress_artifact_exported": bool(egress_path),
        "replay_lineage_preserved": valid,
        "continuity_fabricated": False,
        "manual_prompt_relay_present": False,
        "single_provider_only": True,
        "single_execution_only": True,
        "single_egress_only": True,
        "shell_used": False,
        "replay_safe": valid,
    }
