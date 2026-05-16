from dataclasses import dataclass
@dataclass(frozen=True)
class DirectRuntimeInteractionResponse:
    direct_runtime_interaction_session_id:str; response_return_id:str
    def to_dict(self)->dict:return {"direct_runtime_interaction_session_id":self.direct_runtime_interaction_session_id,"response_return_id":self.response_return_id,"interaction_status":"DIRECT_RUNTIME_INTERACTION_RETURNED"}
def create_direct_runtime_interaction_response(*,binding:dict)->DirectRuntimeInteractionResponse:
    return DirectRuntimeInteractionResponse(binding["direct_runtime_interaction_session_id"],binding["response_return_id"])
