"""Governed runtime operational entrypoint controller."""

from .runtime_operational_entrypoint_binding import create_runtime_operational_entrypoint_binding
from .runtime_operational_entrypoint_evidence import runtime_operational_entrypoint_evidence
from .runtime_operational_entrypoint_request import create_runtime_operational_entrypoint_request
from .runtime_operational_entrypoint_response import create_runtime_operational_entrypoint_response
from .runtime_operational_entrypoint_session import create_runtime_operational_entrypoint_session
from .runtime_operational_entrypoint_state import FINALIZED_PATH
from .runtime_operational_entrypoint_validator import validate_runtime_operational_entrypoint


def create_runtime_operational_entrypoint(
    *,
    realization_output: dict,
    supplemental_lineage: dict,
    prior_output: dict | None = None,
) -> dict:
    try:
        realization_evidence = realization_output["runtime_execution_realization_evidence"]
        session = create_runtime_operational_entrypoint_session(
            runtime_execution_realization_id=realization_evidence["runtime_execution_realization_id"]
        )
        lineage = {**realization_evidence, **supplemental_lineage}
        request = create_runtime_operational_entrypoint_request(session=session)
        binding = create_runtime_operational_entrypoint_binding(
            runtime_operational_entrypoint_id=session["runtime_operational_entrypoint_id"],
            lineage=lineage,
        )
        response = create_runtime_operational_entrypoint_response(session=session, binding=binding)
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_operational_entrypoint", "reason": "entrypoint linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_runtime_operational_entrypoint(
        session=session,
        request=request,
        response=response,
        binding=binding,
        realization_output=realization_output,
        prior_output=prior_output,
    )
    states = FINALIZED_PATH if validation["valid"] else ("BLOCKED",)
    evidence = runtime_operational_entrypoint_evidence(
        session=session,
        request=request,
        response=response,
        binding=binding,
        valid=validation["valid"],
        states=states,
    )
    return {
        "runtime_operational_entrypoint_session": session,
        "runtime_operational_entrypoint_request": request,
        "runtime_operational_entrypoint_binding": binding,
        "runtime_operational_entrypoint_response": response,
        "runtime_operational_entrypoint_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
