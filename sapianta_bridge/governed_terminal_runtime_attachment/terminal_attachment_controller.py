"""Governed terminal attachment controller."""

from .terminal_attachment_binding import create_terminal_attachment_binding
from .terminal_attachment_evidence import terminal_attachment_evidence
from .terminal_attachment_request import create_terminal_attachment_request
from .terminal_attachment_response import create_terminal_attachment_response
from .terminal_attachment_session import create_terminal_attachment_session
from .terminal_attachment_state import SUCCESS_PATH
from .terminal_attachment_validator import validate_terminal_attachment


def attach_governed_terminal_runtime(
    *,
    runtime_serving_output: dict,
    stdin_binding_id: str,
    stdout_binding_id: str,
    prior_output: dict | None = None,
) -> dict:
    try:
        terminal_session = create_terminal_attachment_session(
            runtime_serving_session=runtime_serving_output["runtime_serving_session"],
            stdin_binding_id=stdin_binding_id,
            stdout_binding_id=stdout_binding_id,
        ).to_dict()
        request = create_terminal_attachment_request(terminal_session=terminal_session).to_dict()
        binding = create_terminal_attachment_binding(
            terminal_session=terminal_session,
            runtime_serving_output=runtime_serving_output,
        ).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "terminal_attachment", "reason": "runtime linkage incomplete"}]},
            "states": ["BLOCKED"],
        }

    validation = validate_terminal_attachment(
        terminal_session=terminal_session,
        binding=binding,
        runtime_serving_output=runtime_serving_output,
        prior_output=prior_output,
    )
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_terminal_attachment_response(binding=binding).to_dict() if validation["valid"] else {"terminal_status": "BLOCKED"}
    evidence = terminal_attachment_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "terminal_attachment_session": terminal_session,
        "terminal_attachment_request": request,
        "terminal_attachment_binding": binding,
        "terminal_attachment_response": response,
        "terminal_attachment_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
