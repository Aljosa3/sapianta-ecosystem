from dataclasses import dataclass
from typing import Any
from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash
@dataclass(frozen=True)
class RuntimePersistentChannelSession:
    direct_runtime_interaction_session_id:str; close_requested:bool
    def to_dict(self)->dict[str,Any]:
        v=self.__dict__.copy(); v["runtime_persistent_channel_id"]=f"RUNTIME-PERSISTENT-CHANNEL-{stable_hash(v)[:24]}"; v["replay_safe"]=True; return v
def create_runtime_persistent_channel_session(*,interaction_output:dict,close_requested:bool=False)->RuntimePersistentChannelSession:
    return RuntimePersistentChannelSession(interaction_output["direct_runtime_interaction_session"]["direct_runtime_interaction_session_id"],close_requested)
def validate_runtime_persistent_channel_session(session:Any)->dict[str,Any]:
    v=session.to_dict() if hasattr(session,"to_dict") else session
    if not isinstance(v,dict): return {"valid":False,"errors":[{"field":"runtime_persistent_channel_session","reason":"must be object"}]}
    errors=[]
    for f in ("runtime_persistent_channel_id","direct_runtime_interaction_session_id"):
        if not isinstance(v.get(f),str) or not v[f].strip(): errors.append({"field":f,"reason":"persistent channel field missing"})
    if not isinstance(v.get("close_requested"),bool): errors.append({"field":"close_requested","reason":"must be boolean"})
    return {"valid":not errors,"errors":errors}
