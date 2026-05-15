"""Replay-visible ingress to transport binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LocalIngressBinding:
    ingress_session_id: str
    interaction_session_id: str
    transport_session_id: str
    governed_session_id: str
    execution_gate_id: str
    provider_invocation_id: str
    result_capture_id: str
    response_return_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "ingress_session_id": self.ingress_session_id,
            "interaction_session_id": self.interaction_session_id,
            "transport_session_id": self.transport_session_id,
            "governed_session_id": self.governed_session_id,
            "execution_gate_id": self.execution_gate_id,
            "provider_invocation_id": self.provider_invocation_id,
            "result_capture_id": self.result_capture_id,
            "response_return_id": self.response_return_id,
        }
        value["binding_sha256"] = stable_hash(value)
        value["replay_safe"] = True
        return value


def create_ingress_binding(*, ingress_session: dict[str, Any], transport_binding: dict[str, Any]) -> LocalIngressBinding:
    return LocalIngressBinding(
        ingress_session_id=ingress_session["ingress_session_id"],
        interaction_session_id=transport_binding["interaction_session_id"],
        transport_session_id=transport_binding["transport_session_id"],
        governed_session_id=transport_binding["governed_session_id"],
        execution_gate_id=transport_binding["execution_gate_id"],
        provider_invocation_id=transport_binding["provider_invocation_id"],
        result_capture_id=transport_binding["result_capture_id"],
        response_return_id=transport_binding["response_return_id"],
    )


def validate_ingress_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, LocalIngressBinding) else binding
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_binding", "reason": "must be object"}]}
    for field in ("ingress_session_id", "interaction_session_id", "transport_session_id", "governed_session_id", "execution_gate_id", "provider_invocation_id", "result_capture_id", "response_return_id", "binding_sha256"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "ingress binding field must be non-empty"})
    return {"valid": not errors, "errors": errors}
