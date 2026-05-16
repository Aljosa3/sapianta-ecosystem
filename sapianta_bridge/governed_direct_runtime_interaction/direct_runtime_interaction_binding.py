from dataclasses import dataclass
from typing import Any
from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash
from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import LINEAGE_SOURCE_FIELDS
@dataclass(frozen=True)
class DirectRuntimeInteractionBinding:
    direct_runtime_interaction_session_id:str; interaction_admission_id:str; runtime_surface_session_id:str; surface_ingress_id:str; surface_egress_id:str
    interaction_loop_session_id:str; interaction_turn_id:str; live_runtime_session_id:str; runtime_attachment_session_id:str; session_runtime_id:str; runtime_serving_session_id:str; terminal_attachment_session_id:str; serving_gateway_session_id:str; live_request_ingestion_session_id:str; execution_exchange_session_id:str; execution_relay_session_id:str; runtime_execution_commit_id:str; runtime_delivery_finalization_id:str; transport_session_id:str; governed_session_id:str; execution_gate_id:str; provider_invocation_id:str; bounded_runtime_id:str; result_capture_id:str; response_return_id:str; stdin_relay_id:str; stdout_relay_id:str; runtime_transport_bridge_id:str; runtime_activation_gate_id:str; local_runtime_bridge_session_id:str
    def to_dict(self)->dict[str,Any]:
        v=self.__dict__.copy(); v["binding_sha256"]=stable_hash(v); return v
def create_direct_runtime_interaction_binding(*,interaction_session:dict,surface_output:dict)->DirectRuntimeInteractionBinding:
    b=surface_output["runtime_surface_binding"]
    return DirectRuntimeInteractionBinding(interaction_session["direct_runtime_interaction_session_id"],interaction_session["interaction_admission_id"],b["runtime_surface_session_id"],b["surface_ingress_id"],b["surface_egress_id"],*(b[f] for f in LINEAGE_SOURCE_FIELDS))
