from dataclasses import dataclass
@dataclass(frozen=True)
class DirectRuntimeInteractionRequest:
    direct_runtime_interaction_session_id:str; runtime_surface_session_id:str; interaction_admission_id:str
    def to_dict(self)->dict:return self.__dict__.copy()
def create_direct_runtime_interaction_request(*,interaction_session:dict)->DirectRuntimeInteractionRequest:
    return DirectRuntimeInteractionRequest(interaction_session["direct_runtime_interaction_session_id"],interaction_session["runtime_surface_session_id"],interaction_session["interaction_admission_id"])
