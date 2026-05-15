"""Replay-visible interaction transport binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class TransportBinding:
    transport_session_id: str
    interaction_session_id: str
    governed_session_id: str
    execution_gate_id: str
    provider_invocation_id: str
    bounded_runtime_id: str
    result_capture_id: str
    response_return_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "transport_session_id": self.transport_session_id,
            "interaction_session_id": self.interaction_session_id,
            "governed_session_id": self.governed_session_id,
            "execution_gate_id": self.execution_gate_id,
            "provider_invocation_id": self.provider_invocation_id,
            "bounded_runtime_id": self.bounded_runtime_id,
            "result_capture_id": self.result_capture_id,
            "response_return_id": self.response_return_id,
            "replay_identity": self.replay_identity,
        }
        value["binding_sha256"] = stable_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_transport_binding(
    *,
    transport_session: dict[str, Any],
    interaction_response: dict[str, Any],
    bounded_runtime_id: str,
    result_capture_id: str,
) -> TransportBinding:
    payload = interaction_response["result_payload"]
    return TransportBinding(
        transport_session_id=transport_session["transport_session_id"],
        interaction_session_id=interaction_response["interaction_session_id"],
        governed_session_id=interaction_response["governed_session_id"],
        execution_gate_id=interaction_response["execution_gate_id"],
        provider_invocation_id=interaction_response["invocation_id"],
        bounded_runtime_id=bounded_runtime_id,
        result_capture_id=result_capture_id,
        response_return_id=payload["result_return_id"],
        replay_identity=interaction_response["replay_identity"],
    )


def validate_transport_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, TransportBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_binding", "reason": "must be object"}]}
    fields = (
        "transport_session_id", "interaction_session_id", "governed_session_id", "execution_gate_id",
        "provider_invocation_id", "bounded_runtime_id", "result_capture_id", "response_return_id",
        "replay_identity", "binding_sha256",
    )
    for field in fields:
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "transport binding field must be non-empty"})
    if not errors:
        payload = {field: value[field] for field in fields if field != "binding_sha256"}
        if value["binding_sha256"] != stable_hash(payload):
            errors.append({"field": "binding_sha256", "reason": "transport binding hash mismatch"})
    return {"valid": not errors, "errors": errors}
