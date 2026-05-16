"""Governed runtime activation gate controller."""

from .runtime_activation_gate_binding import create_runtime_activation_gate_binding
from .runtime_activation_gate_evidence import runtime_activation_gate_evidence
from .runtime_activation_gate_request import create_runtime_activation_gate_request
from .runtime_activation_gate_response import create_runtime_activation_gate_response
from .runtime_activation_gate_session import create_runtime_activation_gate_session
from .runtime_activation_gate_state import SUCCESS_PATH
from .runtime_activation_gate_validator import validate_runtime_activation_gate


def create_runtime_activation_gate(
    *,
    entrypoint_output: dict | None = None,
    bridge_output: dict | None = None,
    activation_authorized: bool | None = None,
    approved_by: str | None = None,
    prior_output: dict | None = None,
) -> dict:
    try:
        source_bridge = None
        if entrypoint_output is None and bridge_output is not None:
            source_bridge = {**bridge_output, "activation_authorized": activation_authorized, "approved_by": approved_by}
        gate_session = create_runtime_activation_gate_session(entrypoint_output=entrypoint_output, bridge_output=bridge_output).to_dict()
        request = create_runtime_activation_gate_request(gate_session=gate_session).to_dict()
        binding = create_runtime_activation_gate_binding(
            gate_session=gate_session,
            entrypoint_output=entrypoint_output,
            bridge_output=source_bridge,
        ).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_activation_gate", "reason": "activation linkage incomplete"}]},
            "states": ["BLOCKED"],
        }

    validation = validate_runtime_activation_gate(
        gate_session=gate_session,
        binding=binding,
        entrypoint_output=entrypoint_output,
        bridge_output=bridge_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_runtime_activation_gate_response(binding=binding).to_dict() if validation["valid"] else {"activation_status": "BLOCKED"}
    evidence = runtime_activation_gate_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "runtime_activation_gate_session": gate_session,
        "runtime_activation_gate_request": request,
        "runtime_activation_gate_binding": binding,
        "runtime_activation_gate_response": response,
        "runtime_activation_gate_evidence": evidence,
        "validation": validation,
        "states": list(states),
        "closed": False,
    }
