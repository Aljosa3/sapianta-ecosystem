"""Governed live request ingestion controller."""

from .live_request_ingestion_binding import create_live_request_ingestion_binding
from .live_request_ingestion_evidence import live_request_ingestion_evidence
from .live_request_ingestion_request import create_live_request_ingestion_request
from .live_request_ingestion_response import create_live_request_ingestion_response
from .live_request_ingestion_session import create_live_request_ingestion_session
from .live_request_ingestion_state import SUCCESS_PATH
from .live_request_ingestion_validator import validate_live_request_ingestion


def ingest_live_request(*, gateway_output: dict, request_activation_id: str, prior_output: dict | None = None) -> dict:
    try:
        ingestion_session = create_live_request_ingestion_session(
            gateway_output=gateway_output,
            request_activation_id=request_activation_id,
        ).to_dict()
        request = create_live_request_ingestion_request(ingestion_session=ingestion_session).to_dict()
        binding = create_live_request_ingestion_binding(ingestion_session=ingestion_session, gateway_output=gateway_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "live_request_ingestion", "reason": "gateway linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_live_request_ingestion(
        ingestion_session=ingestion_session,
        binding=binding,
        gateway_output=gateway_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_live_request_ingestion_response(binding=binding).to_dict() if validation["valid"] else {"ingestion_status": "BLOCKED"}
    evidence = live_request_ingestion_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "live_request_ingestion_session": ingestion_session,
        "live_request_ingestion_request": request,
        "live_request_ingestion_binding": binding,
        "live_request_ingestion_response": response,
        "live_request_ingestion_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
