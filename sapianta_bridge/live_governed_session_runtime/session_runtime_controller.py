"""Persistent governed runtime controller."""

from .session_runtime_binding import create_session_runtime_binding
from .session_runtime_evidence import session_runtime_evidence
from .session_runtime_state import SUCCESS_PATH
from .session_runtime_turn import create_session_runtime_turn
from .session_runtime_validator import validate_session_runtime


def attach_session_runtime_turn(*, session_runtime: dict, attachment_output: dict, prior_output: dict | None = None) -> dict:
    try:
        turn = create_session_runtime_turn(session_runtime=session_runtime, attachment_output=attachment_output, prior_output=prior_output).to_dict()
        binding = create_session_runtime_binding(session_runtime=session_runtime, attachment_output=attachment_output).to_dict()
    except KeyError:
        return {"validation": {"valid": False, "errors": [{"field": "attachment", "reason": "runtime attachment continuity invalid"}]}, "states": ["BLOCKED"]}
    validation = validate_session_runtime(session_runtime=session_runtime, turn=turn, binding=binding, prior_output=prior_output, attachment_output=attachment_output)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    evidence = session_runtime_evidence(binding=binding, valid=validation["valid"], states=states)
    return {"session_runtime": session_runtime, "turn": turn, "binding": binding, "validation": validation, "evidence": evidence, "states": list(states)}
