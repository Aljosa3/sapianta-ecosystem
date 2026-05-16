from .runtime_persistent_channel_binding import create_runtime_persistent_channel_binding
from .runtime_persistent_channel_evidence import runtime_persistent_channel_evidence
from .runtime_persistent_channel_request import create_runtime_persistent_channel_request
from .runtime_persistent_channel_response import create_runtime_persistent_channel_response
from .runtime_persistent_channel_session import create_runtime_persistent_channel_session
from .runtime_persistent_channel_state import READY_PATH,CLOSED_PATH
from .runtime_persistent_channel_validator import validate_runtime_persistent_channel
def create_runtime_persistent_channel(*,interaction_output:dict,close_requested:bool=False,prior_output:dict|None=None)->dict:
    try:
        s=create_runtime_persistent_channel_session(interaction_output=interaction_output,close_requested=close_requested).to_dict(); req=create_runtime_persistent_channel_request(channel_session=s).to_dict(); b=create_runtime_persistent_channel_binding(channel_session=s,interaction_output=interaction_output).to_dict()
    except KeyError:return {"validation":{"valid":False,"errors":[{"field":"runtime_persistent_channel","reason":"interaction linkage incomplete"}]},"states":["BLOCKED"]}
    v=validate_runtime_persistent_channel(channel_session=s,binding=b,interaction_output=interaction_output,prior_output=prior_output)
    states=(CLOSED_PATH if close_requested else READY_PATH) if v["valid"] else ("BLOCKED",)
    resp=create_runtime_persistent_channel_response(binding=b).to_dict() if v["valid"] else {"channel_status":"BLOCKED"}
    ev=runtime_persistent_channel_evidence(binding=b,valid=v["valid"],states=states)
    return {"runtime_persistent_channel_session":s,"runtime_persistent_channel_request":req,"runtime_persistent_channel_binding":b,"runtime_persistent_channel_response":resp,"runtime_persistent_channel_evidence":ev,"validation":v,"states":list(states)}
