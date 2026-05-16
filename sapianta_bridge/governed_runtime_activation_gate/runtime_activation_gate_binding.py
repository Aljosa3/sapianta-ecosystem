"""Governed runtime activation gate continuity binding."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeActivationGateBinding:
    runtime_activation_gate_id: str
    local_runtime_bridge_session_id: str
    execution_relay_session_id: str
    execution_exchange_session_id: str
    live_request_ingestion_session_id: str
    serving_gateway_session_id: str
    runtime_serving_session_id: str
    terminal_attachment_session_id: str
    session_runtime_id: str
    interaction_loop_session_id: str
    interaction_turn_id: str
    live_runtime_session_id: str
    runtime_attachment_session_id: str
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
    activation_authorized: bool
    approved_by: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["binding_sha256"] = stable_hash(value)
        return value


def create_runtime_activation_gate_binding(*, gate_session: dict, bridge_output: dict) -> RuntimeActivationGateBinding:
    binding = bridge_output["local_runtime_bridge_binding"]
    return RuntimeActivationGateBinding(
        gate_session["runtime_activation_gate_id"],
        binding["local_runtime_bridge_session_id"],
        binding["execution_relay_session_id"],
        binding["execution_exchange_session_id"],
        binding["live_request_ingestion_session_id"],
        binding["serving_gateway_session_id"],
        binding["runtime_serving_session_id"],
        binding["terminal_attachment_session_id"],
        binding["session_runtime_id"],
        binding["interaction_loop_session_id"],
        binding["interaction_turn_id"],
        binding["live_runtime_session_id"],
        binding["runtime_attachment_session_id"],
        binding["transport_session_id"],
        binding["governed_session_id"],
        binding["execution_gate_id"],
        binding["provider_invocation_id"],
        binding["bounded_runtime_id"],
        binding["result_capture_id"],
        binding["response_return_id"],
        binding["stdin_relay_id"],
        binding["stdout_relay_id"],
        binding["runtime_transport_bridge_id"],
        gate_session["activation_authorized"],
        gate_session["approved_by"],
    )
