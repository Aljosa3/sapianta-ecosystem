"""Governed runtime surface binding."""
from dataclasses import dataclass
from typing import Any
from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


LINEAGE_SOURCE_FIELDS = (
    "interaction_loop_session_id","interaction_turn_id","live_runtime_session_id","runtime_attachment_session_id",
    "session_runtime_id","runtime_serving_session_id","terminal_attachment_session_id","serving_gateway_session_id",
    "live_request_ingestion_session_id","execution_exchange_session_id","execution_relay_session_id",
    "runtime_execution_commit_id","runtime_delivery_finalization_id","transport_session_id","governed_session_id",
    "execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id",
    "stdin_relay_id","stdout_relay_id","runtime_transport_bridge_id","runtime_activation_gate_id","local_runtime_bridge_session_id",
)


@dataclass(frozen=True)
class RuntimeSurfaceBinding:
    runtime_surface_session_id: str
    surface_ingress_id: str
    surface_egress_id: str
    interaction_loop_session_id: str
    interaction_turn_id: str
    live_runtime_session_id: str
    runtime_attachment_session_id: str
    session_runtime_id: str
    runtime_serving_session_id: str
    terminal_attachment_session_id: str
    serving_gateway_session_id: str
    live_request_ingestion_session_id: str
    execution_exchange_session_id: str
    execution_relay_session_id: str
    runtime_execution_commit_id: str
    runtime_delivery_finalization_id: str
    transport_session_id: str
    governed_session_id: str
    execution_gate_id: str
    provider_invocation_id: str
    bounded_runtime_id: str
    result_capture_id: str
    response_return_id: str
    stdin_relay_id: str
    stdout_relay_id: str
    runtime_transport_bridge_id: str
    runtime_activation_gate_id: str
    local_runtime_bridge_session_id: str
    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["binding_sha256"] = stable_hash(value)
        return value


def create_runtime_surface_binding(*, surface_session: dict, finalization_output: dict) -> RuntimeSurfaceBinding:
    b = finalization_output["runtime_delivery_finalization_binding"]
    return RuntimeSurfaceBinding(surface_session["runtime_surface_session_id"], surface_session["surface_ingress_id"], surface_session["surface_egress_id"], *(b[field] for field in LINEAGE_SOURCE_FIELDS))
