"""Continuously attachable governed runtime serving controller."""

from .runtime_serving_binding import create_runtime_serving_binding
from .runtime_serving_evidence import runtime_serving_evidence
from .runtime_serving_request import create_runtime_serving_request
from .runtime_serving_response import create_runtime_serving_response
from .runtime_serving_state import SUCCESS_PATH
from .runtime_serving_validator import validate_runtime_serving


def attach_runtime_serving_turn(*, serving_session: dict, session_runtime_output: dict, prior_output: dict | None = None) -> dict:
    try:
        request = create_runtime_serving_request(serving_session=serving_session).to_dict()
        binding = create_runtime_serving_binding(serving_session=serving_session, session_runtime_output=session_runtime_output).to_dict()
    except KeyError:
        return {"validation": {"valid": False, "errors": [{"field": "serving", "reason": "runtime serving continuity invalid"}]}, "states": ["BLOCKED"]}
    validation = validate_runtime_serving(serving_session=serving_session, binding=binding, prior_output=prior_output, session_runtime_output=session_runtime_output)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_runtime_serving_response(binding=binding).to_dict() if validation["valid"] else {"serving_status": "BLOCKED"}
    evidence = runtime_serving_evidence(binding=binding, valid=validation["valid"], states=states)
    return {"runtime_serving_session": serving_session, "runtime_serving_request": request, "runtime_serving_binding": binding, "runtime_serving_response": response, "runtime_serving_evidence": evidence, "validation": validation, "states": list(states)}
