"""Bounded human interaction continuity controller."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge

from .interaction_binding import create_interaction_binding, validate_interaction_binding
from .interaction_evidence import interaction_evidence
from .interaction_request import create_interaction_request, validate_interaction_request
from .interaction_response import create_interaction_response, validate_interaction_response
from .interaction_session import create_interaction_session, validate_interaction_session
from .interaction_state import SUCCESS_PATH, validate_interaction_state_chain


def _blocked(reason: str, request: dict[str, Any]) -> dict[str, Any]:
    return {
        "interaction_request": request,
        "interaction_session": {},
        "interaction_binding": {},
        "interaction_response": {"current_state": "BLOCKED"},
        "interaction_evidence": {"current_state": "BLOCKED", "blocked_reason": reason},
        "interaction_validation": {"valid": False, "errors": [{"field": "interaction", "reason": reason}]},
        "orchestration_present": False,
        "autonomous_continuation_present": False,
        "retry_present": False,
        "routing_present": False,
    }


def run_human_interaction_continuity(
    human_input: str,
    *,
    execution_gate_id: str,
    requested_provider_id: str = "deterministic_mock",
    conversation_id: str = "CHATGPT-SESSION",
) -> dict[str, Any]:
    bridge_output = run_active_chatgpt_bridge(
        human_input,
        requested_provider_id=requested_provider_id,
        conversation_id=conversation_id,
    )
    bridge_response = bridge_output.get("bridge_response", {})
    request = create_interaction_request(
        human_input,
        conversation_id=conversation_id,
        execution_gate_id=execution_gate_id,
        replay_identity=bridge_response.get("replay_identity", ""),
    ).to_dict()
    if not validate_interaction_request(request)["valid"]:
        return _blocked("interaction request invalid", request)
    if bridge_output.get("bridge_validation", {}).get("valid") is not True:
        return _blocked("governed bridge output invalid", request)
    session = create_interaction_session(request=request, governed_session_id=bridge_response["session_id"]).to_dict()
    binding = create_interaction_binding(request=request, session=session, bridge_output=bridge_output).to_dict()
    states = list(SUCCESS_PATH)
    response = create_interaction_response(binding=binding, states=states, bridge_output=bridge_output).to_dict()
    validations = (
        validate_interaction_session(session),
        validate_interaction_binding(binding),
        validate_interaction_state_chain(states),
        validate_interaction_response(response),
    )
    valid = all(validation["valid"] for validation in validations)
    evidence = interaction_evidence(request=request, session=session, binding=binding, response=response, valid=valid)
    return {
        "interaction_request": request,
        "interaction_session": session,
        "interaction_binding": binding,
        "interaction_response": response,
        "interaction_evidence": evidence,
        "interaction_validation": {"valid": valid, "errors": [error for validation in validations for error in validation["errors"]]},
        "bridge_output": bridge_output,
        "orchestration_present": False,
        "autonomous_continuation_present": False,
        "retry_present": False,
        "routing_present": False,
    }
