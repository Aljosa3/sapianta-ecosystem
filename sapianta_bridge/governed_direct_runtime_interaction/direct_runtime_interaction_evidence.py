from .direct_runtime_interaction_validator import LINEAGE_FIELDS
def direct_runtime_interaction_evidence(*,binding:dict,valid:bool,states:tuple[str,...])->dict:
    return {**{f:binding.get(f,"") for f in LINEAGE_FIELDS},"states":list(states),"replay_safe":valid,"interaction_runtime_coupled":valid,"continuity_fabricated":False,"hidden_provider_memory_trusted":False}
