"""Governed runtime surface controller."""
from .runtime_surface_binding import create_runtime_surface_binding
from .runtime_surface_evidence import runtime_surface_evidence
from .runtime_surface_request import create_runtime_surface_request
from .runtime_surface_response import create_runtime_surface_response
from .runtime_surface_session import create_runtime_surface_session
from .runtime_surface_state import SUCCESS_PATH
from .runtime_surface_validator import validate_runtime_surface

def create_runtime_surface(*, finalization_output: dict, surface_ingress_id: str, surface_egress_id: str, prior_output: dict | None = None) -> dict:
    try:
        session = create_runtime_surface_session(finalization_output=finalization_output, surface_ingress_id=surface_ingress_id, surface_egress_id=surface_egress_id).to_dict()
        request = create_runtime_surface_request(surface_session=session).to_dict()
        binding = create_runtime_surface_binding(surface_session=session, finalization_output=finalization_output).to_dict()
    except KeyError:
        return {"validation":{"valid":False,"errors":[{"field":"runtime_surface","reason":"finalization linkage incomplete"}]},"states":["BLOCKED"]}
    validation = validate_runtime_surface(surface_session=session, binding=binding, finalization_output=finalization_output, prior_output=prior_output)
    states = SUCCESS_PATH if validation["valid"] else ("BLOCKED",)
    response = create_runtime_surface_response(binding=binding).to_dict() if validation["valid"] else {"surface_status":"BLOCKED"}
    evidence = runtime_surface_evidence(binding=binding, valid=validation["valid"], states=states)
    return {"runtime_surface_session":session,"runtime_surface_request":request,"runtime_surface_binding":binding,"runtime_surface_response":response,"runtime_surface_evidence":evidence,"validation":validation,"states":list(states)}
