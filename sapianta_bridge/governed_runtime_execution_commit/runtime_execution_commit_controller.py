"""Governed runtime execution commit controller."""

from .runtime_execution_commit_binding import create_runtime_execution_commit_binding
from .runtime_execution_commit_evidence import runtime_execution_commit_evidence
from .runtime_execution_commit_request import create_runtime_execution_commit_request
from .runtime_execution_commit_response import create_runtime_execution_commit_response
from .runtime_execution_commit_session import create_runtime_execution_commit_session
from .runtime_execution_commit_state import SUCCESS_PATH
from .runtime_execution_commit_validator import validate_runtime_execution_commit


def create_runtime_execution_commit(*, activation_output: dict, prior_output: dict | None = None) -> dict:
    try:
        commit_session = create_runtime_execution_commit_session(activation_output=activation_output).to_dict()
        request = create_runtime_execution_commit_request(commit_session=commit_session).to_dict()
        binding = create_runtime_execution_commit_binding(commit_session=commit_session, activation_output=activation_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_execution_commit", "reason": "activation linkage incomplete"}]},
            "states": ["RUNTIME_EXECUTION_COMMIT_BLOCKED"],
        }
    validation = validate_runtime_execution_commit(
        commit_session=commit_session,
        binding=binding,
        activation_output=activation_output,
        prior_output=prior_output,
    )
    error_fields = {error["field"] for error in validation["errors"]}
    if validation["valid"]:
        states = SUCCESS_PATH
        response = create_runtime_execution_commit_response(binding=binding).to_dict()
    elif error_fields & {"activation_authorized", "approved_by"}:
        states = ("RUNTIME_EXECUTION_COMMIT_REJECTED",)
        response = {"commit_status": "RUNTIME_EXECUTION_COMMIT_REJECTED"}
    else:
        states = ("RUNTIME_EXECUTION_COMMIT_BLOCKED",)
        response = {"commit_status": "RUNTIME_EXECUTION_COMMIT_BLOCKED"}
    evidence = runtime_execution_commit_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "runtime_execution_commit_session": commit_session,
        "runtime_execution_commit_request": request,
        "runtime_execution_commit_binding": binding,
        "runtime_execution_commit_response": response,
        "runtime_execution_commit_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
