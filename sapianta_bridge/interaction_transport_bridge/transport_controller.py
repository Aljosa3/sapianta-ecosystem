"""Deterministic governed interaction transport controller."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_controller import run_human_interaction_continuity

from .transport_binding import create_transport_binding, validate_transport_binding
from .transport_evidence import transport_evidence
from .transport_normalizer import normalize_transport_result, validate_transport_normalization
from .transport_request import create_transport_request, validate_transport_request
from .transport_response import create_transport_response, validate_transport_response
from .transport_session import create_transport_session, validate_transport_session
from .transport_state import SUCCESS_PATH, validate_transport_state_chain


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "transport_session": {},
        "transport_request": {},
        "transport_binding": {},
        "normalized_result": {},
        "transport_response": {"transport_state": "BLOCKED"},
        "transport_evidence": {"transport_state": "BLOCKED", "blocked_reason": reason},
        "transport_validation": {"valid": False, "errors": [{"field": "transport", "reason": reason}]},
        "orchestration_present": False,
        "retry_present": False,
        "fallback_present": False,
        "routing_present": False,
        "autonomous_continuation_present": False,
    }


def run_interaction_transport_bridge(
    human_input: str,
    *,
    execution_gate_id: str,
    bounded_runtime_id: str,
    result_capture_id: str,
    requested_provider_id: str = "deterministic_mock",
    conversation_id: str = "CHATGPT-SESSION",
) -> dict[str, Any]:
    if not all(isinstance(value, str) and value.strip() for value in (execution_gate_id, bounded_runtime_id, result_capture_id)):
        return _blocked("execution lineage incomplete")
    interaction = run_human_interaction_continuity(
        human_input,
        execution_gate_id=execution_gate_id,
        requested_provider_id=requested_provider_id,
        conversation_id=conversation_id,
    )
    if interaction.get("interaction_validation", {}).get("valid") is not True:
        return _blocked("interaction continuity invalid")
    interaction_response = interaction["interaction_response"]
    session = create_transport_session(interaction_response=interaction_response).to_dict()
    request = create_transport_request(transport_session=session, interaction_response=interaction_response).to_dict()
    binding = create_transport_binding(
        transport_session=session,
        interaction_response=interaction_response,
        bounded_runtime_id=bounded_runtime_id,
        result_capture_id=result_capture_id,
    ).to_dict()
    normalized = normalize_transport_result(interaction_response=interaction_response, binding=binding)
    response = create_transport_response(transport_session=session, normalized_result=normalized).to_dict()
    states = list(SUCCESS_PATH)
    validations = (
        validate_transport_session(session),
        validate_transport_request(request),
        validate_transport_binding(binding),
        validate_transport_normalization(normalized),
        validate_transport_response(response),
        validate_transport_state_chain(states),
    )
    valid = all(validation["valid"] for validation in validations)
    evidence = transport_evidence(binding=binding, response=response, valid=valid, states=states)
    return {
        "transport_session": session,
        "transport_request": request,
        "transport_binding": binding,
        "normalized_result": normalized,
        "transport_response": response,
        "transport_evidence": evidence,
        "transport_validation": {"valid": valid, "errors": [error for validation in validations for error in validation["errors"]]},
        "interaction_output": interaction,
        "orchestration_present": False,
        "retry_present": False,
        "fallback_present": False,
        "routing_present": False,
        "autonomous_continuation_present": False,
    }
