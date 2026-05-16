"""Governed execution relay controller."""

from .execution_relay_binding import create_execution_relay_binding
from .execution_relay_evidence import execution_relay_evidence
from .execution_relay_request import create_execution_relay_request
from .execution_relay_response import create_execution_relay_response
from .execution_relay_session import create_execution_relay_session
from .execution_relay_state import SUCCESS_PATH
from .execution_relay_validator import validate_execution_relay


def create_execution_relay(*, exchange_output: dict, terminal_output: dict, prior_output: dict | None = None) -> dict:
    try:
        relay_session = create_execution_relay_session(exchange_output=exchange_output, terminal_output=terminal_output).to_dict()
        request = create_execution_relay_request(relay_session=relay_session).to_dict()
        binding = create_execution_relay_binding(relay_session=relay_session, exchange_output=exchange_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "execution_relay", "reason": "relay linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_execution_relay(
        relay_session=relay_session,
        binding=binding,
        exchange_output=exchange_output,
        terminal_output=terminal_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_execution_relay_response(binding=binding).to_dict() if validation["valid"] else {"relay_status": "BLOCKED"}
    evidence = execution_relay_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "execution_relay_session": relay_session,
        "execution_relay_request": request,
        "execution_relay_binding": binding,
        "execution_relay_response": response,
        "execution_relay_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
