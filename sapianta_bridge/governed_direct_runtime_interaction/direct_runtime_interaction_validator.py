from typing import Any
from .direct_runtime_interaction_session import validate_direct_runtime_interaction_session
from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import LINEAGE_SOURCE_FIELDS
LINEAGE_FIELDS=("direct_runtime_interaction_session_id","interaction_admission_id","runtime_surface_session_id","surface_ingress_id","surface_egress_id",*LINEAGE_SOURCE_FIELDS)
def validate_direct_runtime_interaction(*,interaction_session:dict,binding:dict,surface_output:dict,prior_output:dict|None=None)->dict[str,Any]:
    errors=list(validate_direct_runtime_interaction_session(interaction_session)["errors"])
    if surface_output.get("validation",{}).get("valid") is not True: errors.append({"field":"runtime_surface","reason":"runtime surface continuity invalid"})
    sb=surface_output.get("runtime_surface_binding",{})
    if sb.get("runtime_surface_session_id")!=interaction_session.get("runtime_surface_session_id"): errors.append({"field":"runtime_surface_session_id","reason":"surface linkage mismatch"})
    if prior_output is not None and prior_output.get("direct_runtime_interaction_session",{}).get("direct_runtime_interaction_session_id")!=interaction_session.get("direct_runtime_interaction_session_id"): errors.append({"field":"direct_runtime_interaction_session_id","reason":"runtime interaction identity changed"})
    for f in LINEAGE_FIELDS:
        if not isinstance(binding.get(f),str) or not binding[f].strip(): errors.append({"field":f,"reason":"direct runtime interaction lineage missing"})
    return {"valid":not errors,"errors":errors}
