from .runtime_persistent_channel_validator import LINEAGE_FIELDS
def runtime_persistent_channel_evidence(*,binding:dict,valid:bool,states:tuple[str,...])->dict:
    return {**{f:binding.get(f,"") for f in LINEAGE_FIELDS},"close_requested":binding.get("close_requested") is True,"states":list(states),"replay_safe":valid,"persistent_channel_continuity":valid,"continuity_fabricated":False,"hidden_provider_memory_trusted":False}
