"""Replay-safe interaction continuity binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .interaction_session import stable_hash


@dataclass(frozen=True)
class InteractionBinding:
    interaction_session_id: str
    interaction_request_id: str
    bridge_id: str
    governed_session_id: str
    envelope_id: str
    provider_id: str
    invocation_id: str
    execution_gate_id: str
    result_return_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "interaction_session_id": self.interaction_session_id,
            "interaction_request_id": self.interaction_request_id,
            "bridge_id": self.bridge_id,
            "governed_session_id": self.governed_session_id,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "invocation_id": self.invocation_id,
            "execution_gate_id": self.execution_gate_id,
            "result_return_id": self.result_return_id,
            "replay_identity": self.replay_identity,
        }
        value["binding_sha256"] = stable_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_interaction_binding(*, request: dict[str, Any], session: dict[str, Any], bridge_output: dict[str, Any]) -> InteractionBinding:
    response = bridge_output["bridge_response"]
    payload = response["interpretation_ready_payload"]
    return InteractionBinding(
        interaction_session_id=session["interaction_session_id"],
        interaction_request_id=request["interaction_request_id"],
        bridge_id=response["bridge_id"],
        governed_session_id=response["session_id"],
        envelope_id=response["envelope_id"],
        provider_id=response["provider_id"],
        invocation_id=response["invocation_id"],
        execution_gate_id=request["execution_gate_id"],
        result_return_id=payload["result_return_id"],
        replay_identity=response["replay_identity"],
    )


def validate_interaction_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, InteractionBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "interaction_binding", "reason": "must be an object"}]}
    fields = (
        "interaction_session_id", "interaction_request_id", "bridge_id", "governed_session_id", "envelope_id",
        "provider_id", "invocation_id", "execution_gate_id", "result_return_id", "replay_identity", "binding_sha256",
    )
    for field in fields:
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "interaction binding field must be non-empty"})
    if not errors:
        payload = {field: value[field] for field in fields if field != "binding_sha256"}
        if value["binding_sha256"] != stable_hash(payload):
            errors.append({"field": "binding_sha256", "reason": "interaction binding hash mismatch"})
    return {"valid": not errors, "errors": errors}
