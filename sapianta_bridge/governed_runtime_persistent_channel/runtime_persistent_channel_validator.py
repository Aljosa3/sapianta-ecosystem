from typing import Any
from .runtime_persistent_channel_session import validate_runtime_persistent_channel_session
from .runtime_persistent_channel_binding import SOURCE_FIELDS
LINEAGE_FIELDS=("runtime_persistent_channel_id","direct_runtime_interaction_session_id",*SOURCE_FIELDS)
def validate_runtime_persistent_channel(*,channel_session:dict,binding:dict,interaction_output:dict,prior_output:dict|None=None)->dict[str,Any]:
    errors=list(validate_runtime_persistent_channel_session(channel_session)["errors"])
    if interaction_output.get("validation",{}).get("valid") is not True: errors.append({"field":"direct_runtime_interaction","reason":"direct runtime interaction continuity invalid"})
    ib=interaction_output.get("direct_runtime_interaction_binding",{})
    if ib.get("direct_runtime_interaction_session_id")!=channel_session.get("direct_runtime_interaction_session_id"): errors.append({"field":"direct_runtime_interaction_session_id","reason":"interaction linkage mismatch"})
    if prior_output is not None:
        prior=prior_output.get("runtime_persistent_channel_session",{})
        if prior.get("runtime_persistent_channel_id")!=channel_session.get("runtime_persistent_channel_id"): errors.append({"field":"runtime_persistent_channel_id","reason":"persistent channel identity changed"})
        if prior.get("close_requested") is True: errors.append({"field":"close_requested","reason":"closed channel cannot be silently reopened"})
    for f in LINEAGE_FIELDS:
        if not isinstance(binding.get(f),str) or not binding[f].strip(): errors.append({"field":f,"reason":"persistent channel lineage missing"})
    return {"valid":not errors,"errors":errors}
