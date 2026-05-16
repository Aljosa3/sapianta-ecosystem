"""Governed runtime delivery finalization controller."""

from .runtime_delivery_finalization_binding import create_runtime_delivery_finalization_binding
from .runtime_delivery_finalization_evidence import runtime_delivery_finalization_evidence
from .runtime_delivery_finalization_request import create_runtime_delivery_finalization_request
from .runtime_delivery_finalization_response import create_runtime_delivery_finalization_response
from .runtime_delivery_finalization_session import create_runtime_delivery_finalization_session
from .runtime_delivery_finalization_state import SUCCESS_PATH
from .runtime_delivery_finalization_validator import validate_runtime_delivery_finalization


def create_runtime_delivery_finalization(*, commit_output: dict, prior_output: dict | None = None) -> dict:
    try:
        finalization_session = create_runtime_delivery_finalization_session(commit_output=commit_output).to_dict()
        request = create_runtime_delivery_finalization_request(finalization_session=finalization_session).to_dict()
        binding = create_runtime_delivery_finalization_binding(finalization_session=finalization_session, commit_output=commit_output).to_dict()
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_delivery_finalization", "reason": "execution commit linkage incomplete"}]},
            "states": ["RUNTIME_DELIVERY_FINALIZATION_BLOCKED"],
        }
    validation = validate_runtime_delivery_finalization(
        finalization_session=finalization_session,
        binding=binding,
        commit_output=commit_output,
        prior_output=prior_output,
    )
    error_fields = {error["field"] for error in validation["errors"]}
    if validation["valid"]:
        states = SUCCESS_PATH
        response = create_runtime_delivery_finalization_response(binding=binding).to_dict()
    elif error_fields & {"activation_authorized", "approved_by"}:
        states = ("RUNTIME_DELIVERY_FINALIZATION_REJECTED",)
        response = {"finalization_status": "RUNTIME_DELIVERY_FINALIZATION_REJECTED"}
    else:
        states = ("RUNTIME_DELIVERY_FINALIZATION_BLOCKED",)
        response = {"finalization_status": "RUNTIME_DELIVERY_FINALIZATION_BLOCKED"}
    evidence = runtime_delivery_finalization_evidence(binding=binding, valid=validation["valid"], states=states)
    return {
        "runtime_delivery_finalization_session": finalization_session,
        "runtime_delivery_finalization_request": request,
        "runtime_delivery_finalization_binding": binding,
        "runtime_delivery_finalization_response": response,
        "runtime_delivery_finalization_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
