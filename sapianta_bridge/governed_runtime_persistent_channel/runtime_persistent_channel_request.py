from dataclasses import dataclass
@dataclass(frozen=True)
class RuntimePersistentChannelRequest:
    runtime_persistent_channel_id:str; direct_runtime_interaction_session_id:str; close_requested:bool
    def to_dict(self)->dict:return self.__dict__.copy()
def create_runtime_persistent_channel_request(*,channel_session:dict)->RuntimePersistentChannelRequest:
    return RuntimePersistentChannelRequest(channel_session["runtime_persistent_channel_id"],channel_session["direct_runtime_interaction_session_id"],channel_session["close_requested"])
