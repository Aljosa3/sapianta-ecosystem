"""Governed runtime activation gate authority binding."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeActivationGateBinding:
    runtime_activation_gate_id: str
    runtime_activation_boundary_id: str
    operational_entry_contract_id: str
    operational_entry_admission_id: str
    execution_exchange_session_id: str
    execution_relay_session_id: str
    runtime_execution_commit_id: str
    runtime_delivery_finalization_id: str
    operational_runtime_entrypoint_id: str
    response_return_id: str
    activation_authorized: bool
    approved_by: str
    activation_source_kind: str
    local_runtime_bridge_session_id: str = ""
    live_request_ingestion_session_id: str = ""
    serving_gateway_session_id: str = ""
    runtime_serving_session_id: str = ""
    terminal_attachment_session_id: str = ""
    session_runtime_id: str = ""
    interaction_loop_session_id: str = ""
    interaction_turn_id: str = ""
    live_runtime_session_id: str = ""
    runtime_attachment_session_id: str = ""
    transport_session_id: str = ""
    governed_session_id: str = ""
    execution_gate_id: str = ""
    provider_invocation_id: str = ""
    bounded_runtime_id: str = ""
    result_capture_id: str = ""
    stdin_relay_id: str = ""
    stdout_relay_id: str = ""
    runtime_transport_bridge_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["binding_sha256"] = stable_hash(value)
        return value


def create_runtime_activation_gate_binding(
    *,
    gate_session: dict,
    entrypoint_output: dict | None = None,
    bridge_output: dict | None = None,
) -> RuntimeActivationGateBinding:
    if entrypoint_output is not None:
        activation = entrypoint_output["activation"]
        evidence = entrypoint_output["evidence"]
        admission = entrypoint_output["admission"]
        return RuntimeActivationGateBinding(
            gate_session["runtime_activation_gate_id"],
            activation["runtime_activation_boundary_id"],
            activation["operational_entry_contract_id"],
            activation["operational_entry_admission_id"],
            evidence["execution_exchange_session_id"],
            evidence["execution_relay_session_id"],
            evidence["runtime_execution_commit_id"],
            evidence["runtime_delivery_finalization_id"],
            activation["operational_runtime_entrypoint_id"],
            evidence["response_return_id"],
            admission["admitted"],
            admission["approved_by"],
            "operational_entrypoint",
        )

    binding = bridge_output["local_runtime_bridge_binding"]
    return RuntimeActivationGateBinding(
        gate_session["runtime_activation_gate_id"],
        "",
        "",
        "",
        binding["execution_exchange_session_id"],
        binding["execution_relay_session_id"],
        "",
        "",
        "",
        binding["response_return_id"],
        bridge_output.get("activation_authorized", True),
        bridge_output.get("approved_by", "human"),
        "legacy_local_runtime_bridge",
        binding["local_runtime_bridge_session_id"],
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
        binding["stdin_relay_id"],
        binding["stdout_relay_id"],
        binding["runtime_transport_bridge_id"],
    )
