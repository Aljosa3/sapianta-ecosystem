"""Runtime-native interaction attachment controller."""

from .runtime_attachment_binding import create_runtime_attachment_binding
from .runtime_attachment_evidence import runtime_attachment_evidence
from .runtime_attachment_request import create_runtime_attachment_request
from .runtime_attachment_response import create_runtime_attachment_response
from .runtime_attachment_session import create_runtime_attachment_session
from .runtime_attachment_state import SUCCESS_PATH
from .runtime_attachment_validator import validate_runtime_attachment


def attach_live_runtime_interaction(*, live_runtime_output: dict) -> dict:
    try:
        session = create_runtime_attachment_session(live_runtime_output=live_runtime_output).to_dict()
        request = create_runtime_attachment_request(session=session).to_dict()
        binding = create_runtime_attachment_binding(session=session, live_runtime_output=live_runtime_output).to_dict()
    except KeyError:
        return {"validation": {"valid": False, "errors": [{"field": "attachment", "reason": "runtime lineage incomplete"}]}, "states": ["BLOCKED"]}
    validation = validate_runtime_attachment(session=session, live_runtime_output=live_runtime_output, binding=binding)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_runtime_attachment_response(binding=binding).to_dict() if validation["valid"] else {"attachment_status": "BLOCKED"}
    evidence = runtime_attachment_evidence(binding=binding, valid=validation["valid"], states=states)
    return {"runtime_attachment_session": session, "runtime_attachment_request": request, "runtime_attachment_binding": binding, "runtime_attachment_response": response, "runtime_attachment_evidence": evidence, "validation": validation, "states": list(states)}
