"""Controller for the first deterministic no-copy/paste loop."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge

from .loop_binding import create_loop_binding
from .loop_evidence import loop_evidence
from .loop_lifecycle import blocked_loop_lifecycle, complete_loop_lifecycle
from .loop_request import create_loop_request, validate_loop_request
from .loop_response import create_loop_response
from .loop_validator import validate_loop_artifacts


def _blocked_loop(request: dict[str, Any], reason: str) -> dict[str, Any]:
    binding = {
        "loop_id": "",
        "loop_request_id": request.get("loop_request_id", ""),
        "bridge_id": "",
        "session_id": "",
        "envelope_id": "",
        "provider_id": request.get("requested_provider_id", ""),
        "invocation_id": "",
        "result_return_id": "",
        "replay_identity": request.get("replay_identity", ""),
        "evidence_hashes": {},
        "binding_sha256": "",
        "immutable": True,
        "replay_safe": False,
    }
    response = {
        "loop_id": "",
        "bridge_id": "",
        "session_id": "",
        "invocation_id": "",
        "provider_id": request.get("requested_provider_id", ""),
        "envelope_id": "",
        "result_status": "BLOCKED",
        "chatgpt_response_payload": {},
        "replay_identity": request.get("replay_identity", ""),
        "evidence_references": {"blocked_reason": reason},
        "autonomous_continuation_present": False,
        "recursive_execution_present": False,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "hidden_execution_present": False,
        "execution_authority_granted": False,
        "replay_safe": False,
    }
    lifecycle = blocked_loop_lifecycle()
    validation = {
        "valid": False,
        "errors": [{"field": "loop", "reason": reason}],
        "request_valid": validate_loop_request(request)["valid"],
        "binding_valid": False,
        "response_valid": False,
        "lifecycle_valid": True,
        "lineage_continuity_valid": False,
        "provider_identity_consistent": False,
        "replay_safe": False,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }
    evidence = loop_evidence(binding=binding, response=response, validation=validation)
    return {
        "loop_request": request,
        "bridge_output": {},
        "loop_binding": binding,
        "loop_response": response,
        "loop_lifecycle": lifecycle,
        "loop_validation": validation,
        "loop_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }


def run_no_copy_paste_loop(
    chatgpt_input: str,
    *,
    requested_provider_id: str = "deterministic_mock",
    conversation_id: str = "CHATGPT-SESSION",
    timestamp: str = "1970-01-01T00:00:00Z",
    workspace_hint: dict[str, Any] | None = None,
    authority_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = create_loop_request(
        chatgpt_input,
        requested_provider_id=requested_provider_id,
        conversation_id=conversation_id,
        timestamp=timestamp,
        workspace_hint=workspace_hint,
        authority_hint=authority_hint,
    ).to_dict()
    request_validation = validate_loop_request(request)
    if not request_validation["valid"]:
        return _blocked_loop(request, "loop request invalid")
    bridge_output = run_active_chatgpt_bridge(
        chatgpt_input,
        requested_provider_id=requested_provider_id,
        timestamp=timestamp,
        conversation_id=conversation_id,
        workspace_hint=workspace_hint,
        authority_hint=authority_hint,
    )
    if not bridge_output.get("bridge_validation", {}).get("valid", False):
        return _blocked_loop(request, "active bridge failed closed")
    binding = create_loop_binding(loop_request=request, bridge_output=bridge_output).to_dict()
    response = create_loop_response(binding=binding, bridge_output=bridge_output).to_dict()
    lifecycle = complete_loop_lifecycle()
    validation = validate_loop_artifacts(
        request=request,
        binding=binding,
        response=response,
        lifecycle=lifecycle,
    )
    evidence = loop_evidence(binding=binding, response=response, validation=validation)
    return {
        "loop_request": request,
        "bridge_output": bridge_output,
        "loop_binding": binding,
        "loop_response": response,
        "loop_lifecycle": lifecycle if validation["valid"] else blocked_loop_lifecycle(),
        "loop_validation": validation,
        "loop_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }
