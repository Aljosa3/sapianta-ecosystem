"""Replay-safe binding for the real Codex E2E loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


BINDING_FIELDS = (
    "loop_id",
    "ingress_request_id",
    "semantic_request_id",
    "envelope_id",
    "connector_id",
    "execution_gate_id",
    "invocation_id",
    "result_return_id",
    "provider_id",
    "replay_identity",
)


def e2e_binding_hash(value: dict[str, Any]) -> str:
    return stable_hash({field: value.get(field) for field in BINDING_FIELDS})


@dataclass(frozen=True)
class RealE2ELoopBinding:
    loop_id: str
    ingress_request_id: str
    semantic_request_id: str
    envelope_id: str
    connector_id: str
    execution_gate_id: str
    invocation_id: str
    result_return_id: str
    provider_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "loop_id": self.loop_id,
            "ingress_request_id": self.ingress_request_id,
            "semantic_request_id": self.semantic_request_id,
            "envelope_id": self.envelope_id,
            "connector_id": self.connector_id,
            "execution_gate_id": self.execution_gate_id,
            "invocation_id": self.invocation_id,
            "result_return_id": self.result_return_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
        }
        value["binding_sha256"] = e2e_binding_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_e2e_loop_binding(
    *,
    request: dict[str, Any],
    ingress_request: dict[str, Any],
    semantic_request: dict[str, Any],
    envelope: dict[str, Any],
    connector_request: dict[str, Any],
    gate_request: dict[str, Any],
    result_payload: dict[str, Any],
) -> RealE2ELoopBinding:
    return RealE2ELoopBinding(
        loop_id=request["loop_id"],
        ingress_request_id=ingress_request["session"]["request_id"],
        semantic_request_id=semantic_request["semantic_request_id"],
        envelope_id=envelope["envelope_id"],
        connector_id=connector_request["connector_id"],
        execution_gate_id=gate_request["execution_gate_id"],
        invocation_id=connector_request["invocation_id"],
        result_return_id=result_payload["result_return_id"],
        provider_id=request["provider_id"],
        replay_identity=request["replay_identity"],
    )


def validate_e2e_loop_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if hasattr(binding, "to_dict") else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "e2e_loop_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "loop binding field must be non-empty"})
    if not errors and value.get("binding_sha256") != e2e_binding_hash(value):
        errors.append({"field": "binding_sha256", "reason": "loop binding hash mismatch"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "loop binding must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "loop binding must be replay-safe"})
    return {"valid": not errors, "errors": errors}
