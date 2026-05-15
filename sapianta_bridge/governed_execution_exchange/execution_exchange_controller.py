"""Governed execution exchange controller."""

from .execution_exchange_binding import create_execution_exchange_binding
from .execution_exchange_evidence import execution_exchange_evidence
from .execution_exchange_request import create_execution_exchange_request
from .execution_exchange_response import create_execution_exchange_response
from .execution_exchange_session import create_execution_exchange_session
from .execution_exchange_state import SUCCESS_PATH
from .execution_exchange_validator import validate_execution_exchange


def create_execution_exchange(*, ingestion_output: dict, prior_output: dict | None = None) -> dict:
    try:
        exchange_session = create_execution_exchange_session(ingestion_output=ingestion_output).to_dict()
        request = create_execution_exchange_request(exchange_session=exchange_session).to_dict()
        binding = create_execution_exchange_binding(exchange_session=exchange_session, ingestion_output=ingestion_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "execution_exchange", "reason": "ingestion linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_execution_exchange(
        exchange_session=exchange_session,
        binding=binding,
        ingestion_output=ingestion_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_execution_exchange_response(binding=binding).to_dict() if validation["valid"] else {"exchange_status": "BLOCKED"}
    evidence = execution_exchange_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "execution_exchange_session": exchange_session,
        "execution_exchange_request": request,
        "execution_exchange_binding": binding,
        "execution_exchange_response": response,
        "execution_exchange_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
