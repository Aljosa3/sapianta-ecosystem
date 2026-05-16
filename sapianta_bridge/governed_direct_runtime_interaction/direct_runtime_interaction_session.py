"""Replay-safe direct runtime interaction session."""
from dataclasses import dataclass
from typing import Any
from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash
@dataclass(frozen=True)
class DirectRuntimeInteractionSession:
    runtime_surface_session_id:str
    interaction_admission_id:str
    def to_dict(self)->dict[str,Any]:
        v=self.__dict__.copy(); v["direct_runtime_interaction_session_id"]=f"DIRECT-RUNTIME-INTERACTION-{stable_hash(v)[:24]}"; v["replay_safe"]=True; return v
def create_direct_runtime_interaction_session(*,surface_output:dict,interaction_admission_id:str)->DirectRuntimeInteractionSession:
    return DirectRuntimeInteractionSession(surface_output["runtime_surface_session"]["runtime_surface_session_id"],interaction_admission_id)
def validate_direct_runtime_interaction_session(session:Any)->dict[str,Any]:
    v=session.to_dict() if hasattr(session,"to_dict") else session
    if not isinstance(v,dict): return {"valid":False,"errors":[{"field":"direct_runtime_interaction_session","reason":"must be object"}]}
    errors=[]
    for f in ("direct_runtime_interaction_session_id","runtime_surface_session_id","interaction_admission_id"):
        if not isinstance(v.get(f),str) or not v[f].strip(): errors.append({"field":f,"reason":"direct interaction field missing"})
    return {"valid":not errors,"errors":errors}
