"""Bounded active ChatGPT bridge controller."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.governed_session.session_bridge import create_governed_execution_session
from sapianta_bridge.providers.adapters.claude_adapter import ClaudeAdapter
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.providers.adapters.local_adapter import LocalAdapter
from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result

from .bridge_binding import create_bridge_binding
from .bridge_evidence import bridge_evidence
from .bridge_lifecycle import blocked_bridge_lifecycle, complete_bridge_lifecycle
from .bridge_request import create_bridge_request, validate_bridge_request
from .bridge_response import create_bridge_response
from .bridge_validator import validate_bridge_artifacts


PROVIDER_ADAPTERS: dict[str, type[ExecutionProvider]] = {
    "deterministic_mock": DeterministicMockAdapter,
    "codex": CodexAdapter,
    "claude_code": ClaudeAdapter,
    "local_executor": LocalAdapter,
}


def _provider_for(provider_id: str) -> ExecutionProvider | None:
    adapter = PROVIDER_ADAPTERS.get(provider_id)
    return adapter() if adapter is not None else None


def _blocked_output(request: dict[str, Any], reason: str) -> dict[str, Any]:
    binding = {
        "bridge_id": "",
        "bridge_request_id": request.get("bridge_request_id", ""),
        "ingress_session_id": request.get("ingress_session_identity", ""),
        "semantic_request_id": request.get("semantic_request_identity", ""),
        "envelope_id": "",
        "session_id": "",
        "invocation_id": "",
        "result_return_id": "",
        "replay_identity": request.get("replay_identity", ""),
        "evidence_hashes": {},
        "binding_sha256": "",
        "immutable": True,
        "replay_safe": False,
    }
    response = {
        "bridge_id": "",
        "session_id": "",
        "invocation_id": "",
        "provider_id": request.get("requested_provider_id", ""),
        "envelope_id": "",
        "result_status": "BLOCKED",
        "interpretation_ready_payload": {},
        "evidence_references": {"blocked_reason": reason},
        "replay_identity": request.get("replay_identity", ""),
        "follow_up_tasks_executed": False,
        "autonomous_interpretation_present": False,
        "provider_output_hidden": False,
        "result_lineage_mutated": False,
        "execution_authority_granted": False,
        "replay_safe": False,
    }
    lifecycle = blocked_bridge_lifecycle()
    validation = {
        "valid": False,
        "errors": [{"field": "bridge", "reason": reason}],
        "request_valid": validate_bridge_request(request)["valid"],
        "binding_valid": False,
        "response_valid": False,
        "lifecycle_valid": True,
        "provider_identity_consistent": False,
        "envelope_identity_consistent": False,
        "replay_safe": False,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
    }
    evidence = bridge_evidence(binding=binding, response=response, validation=validation)
    return {
        "bridge_request": request,
        "ingress_output": {},
        "invocation_output": {},
        "result_output": {},
        "session_output": {},
        "bridge_binding": binding,
        "bridge_response": response,
        "bridge_lifecycle": lifecycle,
        "bridge_validation": validation,
        "bridge_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }


def run_active_chatgpt_bridge(
    raw_text: str,
    *,
    requested_provider_id: str = "deterministic_mock",
    timestamp: str = "1970-01-01T00:00:00Z",
    conversation_id: str = "CHATGPT-SESSION",
    workspace_hint: dict[str, Any] | None = None,
    authority_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = create_bridge_request(
        raw_text,
        requested_provider_id=requested_provider_id,
        timestamp=timestamp,
        conversation_id=conversation_id,
        workspace_hint=workspace_hint,
        authority_hint=authority_hint,
    ).to_dict()
    request_validation = validate_bridge_request(request)
    if not request_validation["valid"]:
        return _blocked_output(request, "bridge request invalid")
    provider = _provider_for(requested_provider_id)
    if provider is None:
        return _blocked_output(request, "unknown explicit provider")

    ingress_output = process_chatgpt_ingress(
        raw_text,
        timestamp=timestamp,
        conversation_id=conversation_id,
        provider_id=requested_provider_id,
    )
    envelope = ingress_output.get("envelope_proposal", {}).get("execution_envelope")
    if not isinstance(envelope, dict):
        return _blocked_output(request, "envelope proposal missing")
    invocation_output = invoke_provider(envelope=envelope, provider=provider, provider_id=requested_provider_id)
    result_output = return_invocation_result(
        invocation_result=invocation_output["invocation_result"],
        invocation_evidence=invocation_output["invocation_evidence"],
    )
    session_output = create_governed_execution_session(
        ingress_output=ingress_output,
        invocation_output=invocation_output,
        result_output=result_output,
    )
    binding = create_bridge_binding(
        bridge_request=request,
        ingress_output=ingress_output,
        session_output=session_output,
        invocation_output=invocation_output,
        result_output=result_output,
    ).to_dict()
    response = create_bridge_response(
        binding=binding,
        session_output=session_output,
        result_output=result_output,
    ).to_dict()
    lifecycle = complete_bridge_lifecycle()
    validation = validate_bridge_artifacts(
        request=request,
        binding=binding,
        response=response,
        lifecycle=lifecycle,
    )
    evidence = bridge_evidence(binding=binding, response=response, validation=validation)
    return {
        "bridge_request": request,
        "ingress_output": ingress_output,
        "invocation_output": invocation_output,
        "result_output": result_output,
        "session_output": session_output,
        "bridge_binding": binding,
        "bridge_response": response,
        "bridge_lifecycle": lifecycle if validation["valid"] else blocked_bridge_lifecycle(),
        "bridge_validation": validation,
        "bridge_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }
