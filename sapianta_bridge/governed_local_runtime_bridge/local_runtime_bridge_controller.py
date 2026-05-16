"""Governed local runtime bridge controller."""

from .local_runtime_bridge_binding import create_local_runtime_bridge_binding
from .local_runtime_bridge_evidence import local_runtime_bridge_evidence
from .local_runtime_bridge_request import create_local_runtime_bridge_request
from .local_runtime_bridge_response import create_local_runtime_bridge_response
from .local_runtime_bridge_session import create_local_runtime_bridge_session
from .local_runtime_bridge_state import SUCCESS_PATH
from .local_runtime_bridge_validator import validate_local_runtime_bridge


def create_local_runtime_bridge(*, relay_output: dict, runtime_transport_bridge_id: str, prior_output: dict | None = None) -> dict:
    try:
        bridge_session = create_local_runtime_bridge_session(relay_output=relay_output, runtime_transport_bridge_id=runtime_transport_bridge_id).to_dict()
        request = create_local_runtime_bridge_request(bridge_session=bridge_session).to_dict()
        binding = create_local_runtime_bridge_binding(bridge_session=bridge_session, relay_output=relay_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "local_runtime_bridge", "reason": "relay linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_local_runtime_bridge(
        bridge_session=bridge_session,
        binding=binding,
        relay_output=relay_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_local_runtime_bridge_response(binding=binding).to_dict() if validation["valid"] else {"bridge_status": "BLOCKED"}
    evidence = local_runtime_bridge_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "local_runtime_bridge_session": bridge_session,
        "local_runtime_bridge_request": request,
        "local_runtime_bridge_binding": binding,
        "local_runtime_bridge_response": response,
        "local_runtime_bridge_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
