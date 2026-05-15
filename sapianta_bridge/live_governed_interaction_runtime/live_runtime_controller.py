"""Live governed interaction runtime controller."""

from typing import Any

from .live_runtime_binding import create_live_runtime_binding
from .live_runtime_evidence import live_runtime_evidence
from .live_runtime_request import create_live_runtime_request
from .live_runtime_response import create_live_runtime_response
from .live_runtime_session import create_live_runtime_session
from .live_runtime_state import SUCCESS_PATH
from .live_runtime_validator import validate_live_runtime


def run_live_governed_interaction_runtime(*, loop_session: dict[str, Any], loop_output: dict[str, Any]) -> dict[str, Any]:
    session = create_live_runtime_session(loop_session=loop_session).to_dict()
    request = create_live_runtime_request(session=session, loop_output=loop_output).to_dict()
    try:
        binding = create_live_runtime_binding(session=session, loop_output=loop_output).to_dict()
    except KeyError:
        return {"live_runtime_session": session, "live_runtime_request": request, "validation": {"valid": False, "errors": [{"field": "binding", "reason": "loop lineage incomplete"}]}, "states": ["BLOCKED"]}
    validation = validate_live_runtime(session=session, loop_output=loop_output, binding=binding)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_live_runtime_response(binding=binding).to_dict() if validation["valid"] else {"runtime_status": "BLOCKED"}
    evidence = live_runtime_evidence(binding=binding, valid=validation["valid"], states=states)
    return {"live_runtime_session": session, "live_runtime_request": request, "live_runtime_binding": binding, "live_runtime_response": response, "live_runtime_evidence": evidence, "validation": validation, "states": list(states)}
