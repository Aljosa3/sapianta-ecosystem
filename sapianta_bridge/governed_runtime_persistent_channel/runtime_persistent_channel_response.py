from dataclasses import dataclass
@dataclass(frozen=True)
class RuntimePersistentChannelResponse:
    runtime_persistent_channel_id:str; response_return_id:str; closed:bool
    def to_dict(self)->dict:return {"runtime_persistent_channel_id":self.runtime_persistent_channel_id,"response_return_id":self.response_return_id,"channel_status":"RUNTIME_PERSISTENT_CHANNEL_CLOSED" if self.closed else "RUNTIME_PERSISTENT_CHANNEL_READY"}
def create_runtime_persistent_channel_response(*,binding:dict)->RuntimePersistentChannelResponse:
    return RuntimePersistentChannelResponse(binding["runtime_persistent_channel_id"],binding["response_return_id"],binding["close_requested"])
