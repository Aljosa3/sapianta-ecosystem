"""Governed runtime activation gate request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeActivationGateRequest:
    runtime_activation_gate_id: str
    local_runtime_bridge_session_id: str
    activation_authorized: bool
    approved_by: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_runtime_activation_gate_request(*, gate_session: dict) -> RuntimeActivationGateRequest:
    return RuntimeActivationGateRequest(
        gate_session["runtime_activation_gate_id"],
        gate_session["local_runtime_bridge_session_id"],
        gate_session["activation_authorized"],
        gate_session["approved_by"],
    )
