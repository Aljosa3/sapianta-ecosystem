from .direct_runtime_interaction_binding import create_direct_runtime_interaction_binding
from .direct_runtime_interaction_evidence import direct_runtime_interaction_evidence
from .direct_runtime_interaction_request import create_direct_runtime_interaction_request
from .direct_runtime_interaction_response import create_direct_runtime_interaction_response
from .direct_runtime_interaction_session import create_direct_runtime_interaction_session
from .direct_runtime_interaction_state import SUCCESS_PATH
from .direct_runtime_interaction_validator import validate_direct_runtime_interaction
def create_direct_runtime_interaction(*,surface_output:dict,interaction_admission_id:str,prior_output:dict|None=None)->dict:
    try:
        s=create_direct_runtime_interaction_session(surface_output=surface_output,interaction_admission_id=interaction_admission_id).to_dict()
        req=create_direct_runtime_interaction_request(interaction_session=s).to_dict()
        b=create_direct_runtime_interaction_binding(interaction_session=s,surface_output=surface_output).to_dict()
    except KeyError:return {"validation":{"valid":False,"errors":[{"field":"direct_runtime_interaction","reason":"surface linkage incomplete"}]},"states":["BLOCKED"]}
    v=validate_direct_runtime_interaction(interaction_session=s,binding=b,surface_output=surface_output,prior_output=prior_output)
    states=SUCCESS_PATH if v["valid"] else ("BLOCKED",)
    resp=create_direct_runtime_interaction_response(binding=b).to_dict() if v["valid"] else {"interaction_status":"BLOCKED"}
    ev=direct_runtime_interaction_evidence(binding=b,valid=v["valid"],states=states)
    return {"direct_runtime_interaction_session":s,"direct_runtime_interaction_request":req,"direct_runtime_interaction_binding":b,"direct_runtime_interaction_response":resp,"direct_runtime_interaction_evidence":ev,"validation":v,"states":list(states)}
