"""Governed runtime activation gate response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeActivationGateResponse:
    runtime_activation_gate_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "runtime_activation_gate_id": self.runtime_activation_gate_id,
            "response_return_id": self.response_return_id,
            "activation_status": "RUNTIME_ACTIVATION_APPROVED",
        }


def create_runtime_activation_gate_response(*, binding: dict) -> RuntimeActivationGateResponse:
    return RuntimeActivationGateResponse(binding["runtime_activation_gate_id"], binding["response_return_id"])
