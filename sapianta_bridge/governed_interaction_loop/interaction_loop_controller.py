"""Governed real-time interaction loop controller."""

from typing import Any

from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge

from .interaction_loop_binding import create_loop_binding
from .interaction_loop_evidence import loop_evidence
from .interaction_loop_state import SUCCESS_PATH
from .interaction_loop_turn import create_loop_turn
from .interaction_loop_validator import validate_turn_continuity


def run_interaction_loop_turn(
    human_input: str,
    *,
    session: dict[str, Any],
    turn_index: int,
    execution_gate_id: str,
    bounded_runtime_id: str,
    result_capture_id: str,
    prior_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prior_turn_id = prior_output.get("turn", {}).get("turn_id") if prior_output else None
    prior_response_id = prior_output.get("binding", {}).get("response_return_id") if prior_output else None
    turn = create_loop_turn(session=session, turn_index=turn_index, human_input=human_input, prior_turn_id=prior_turn_id, prior_response_id=prior_response_id).to_dict()
    transport = run_interaction_transport_bridge(
        human_input,
        execution_gate_id=execution_gate_id,
        bounded_runtime_id=bounded_runtime_id,
        result_capture_id=result_capture_id,
        conversation_id=session["conversation_id"],
    )
    if transport.get("transport_validation", {}).get("valid") is not True:
        return {"turn": turn, "binding": {}, "validation": {"valid": False, "errors": [{"field": "transport", "reason": "invalid transport"}]}, "states": ["BLOCKED"]}
    binding = create_loop_binding(turn=turn, transport_binding=transport["transport_binding"]).to_dict()
    validation = validate_turn_continuity(session=session, turn=turn, prior_output=prior_output, binding=binding, transport_output=transport)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    evidence = loop_evidence(session=session, binding=binding, valid=validation["valid"], states=states)
    return {
        "turn": turn,
        "binding": binding,
        "transport_output": transport,
        "validation": validation,
        "evidence": evidence,
        "states": list(states),
        "provider_hidden_state_trusted": False,
        "hidden_context_reconstruction_present": False,
        "autonomous_continuation_present": False,
    }
