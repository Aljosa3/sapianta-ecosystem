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
    bridge_output: dict,
    activation_authorized: bool,
    approved_by: str,
    prior_output: dict | None = None,
) -> dict:
    try:
        gate_session = create_runtime_activation_gate_session(
            bridge_output=bridge_output,
            activation_authorized=activation_authorized,
            approved_by=approved_by,
        ).to_dict()
        request = create_runtime_activation_gate_request(gate_session=gate_session).to_dict()
        binding = create_runtime_activation_gate_binding(gate_session=gate_session, bridge_output=bridge_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_activation_gate", "reason": "bridge linkage incomplete"}]},
            "states": ["RUNTIME_ACTIVATION_BLOCKED"],
        }
    validation = validate_runtime_activation_gate(
        gate_session=gate_session,
        binding=binding,
        bridge_output=bridge_output,
        prior_output=prior_output,
    )
    authorization_errors = {"activation_authorized", "approved_by"}
    error_fields = {error["field"] for error in validation["errors"]}
    if validation["valid"]:
        states = SUCCESS_PATH
        response = create_runtime_activation_gate_response(binding=binding).to_dict()
    elif error_fields & authorization_errors:
        states = ("RUNTIME_ACTIVATION_REJECTED",)
        response = {"activation_status": "RUNTIME_ACTIVATION_REJECTED"}
    else:
        states = ("RUNTIME_ACTIVATION_BLOCKED",)
        response = {"activation_status": "RUNTIME_ACTIVATION_BLOCKED"}
    evidence = runtime_activation_gate_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "runtime_activation_gate_session": gate_session,
        "runtime_activation_gate_request": request,
        "runtime_activation_gate_binding": binding,
        "runtime_activation_gate_response": response,
        "runtime_activation_gate_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
