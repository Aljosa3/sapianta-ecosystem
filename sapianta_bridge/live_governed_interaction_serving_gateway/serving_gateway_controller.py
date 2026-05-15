"""Live governed interaction serving gateway controller."""

from .serving_gateway_binding import create_serving_gateway_binding
from .serving_gateway_evidence import serving_gateway_evidence
from .serving_gateway_request import create_serving_gateway_request
from .serving_gateway_response import create_serving_gateway_response
from .serving_gateway_session import create_serving_gateway_session
from .serving_gateway_state import SUCCESS_PATH
from .serving_gateway_validator import validate_serving_gateway


def run_serving_gateway(*, terminal_output: dict, ingress_id: str, egress_id: str, prior_output: dict | None = None) -> dict:
    try:
        gateway_session = create_serving_gateway_session(terminal_output=terminal_output, ingress_id=ingress_id, egress_id=egress_id).to_dict()
        request = create_serving_gateway_request(gateway_session=gateway_session).to_dict()
        binding = create_serving_gateway_binding(gateway_session=gateway_session, terminal_output=terminal_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "serving_gateway", "reason": "serving linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_serving_gateway(
        gateway_session=gateway_session,
        binding=binding,
        terminal_output=terminal_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_serving_gateway_response(gateway_session=gateway_session, binding=binding).to_dict() if validation["valid"] else {"serving_status": "BLOCKED"}
    evidence = serving_gateway_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "serving_gateway_session": gateway_session,
        "serving_gateway_request": request,
        "serving_gateway_binding": binding,
        "serving_gateway_response": response,
        "serving_gateway_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
