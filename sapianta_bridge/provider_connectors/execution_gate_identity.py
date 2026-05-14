"""Deterministic execution gate identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


def execution_gate_id_for(
    *,
    connector_id: str,
    provider_id: str,
    envelope_id: str,
    invocation_id: str,
    replay_identity: str,
) -> str:
    payload = {
        "connector_id": connector_id,
        "envelope_id": envelope_id,
        "invocation_id": invocation_id,
        "provider_id": provider_id,
        "replay_identity": replay_identity,
    }
    return f"EXECUTION-GATE-{stable_hash(payload)[:24]}"


@dataclass(frozen=True)
class ExecutionGateIdentity:
    execution_gate_id: str
    connector_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_gate_id": self.execution_gate_id,
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
            "replay_safe": True,
            "immutable": True,
        }


def create_execution_gate_identity(*, connector_request: dict[str, Any]) -> ExecutionGateIdentity:
    return ExecutionGateIdentity(
        execution_gate_id=execution_gate_id_for(
            connector_id=connector_request["connector_id"],
            provider_id=connector_request["provider_id"],
            envelope_id=connector_request["envelope_id"],
            invocation_id=connector_request["invocation_id"],
            replay_identity=connector_request["replay_identity"],
        ),
        connector_id=connector_request["connector_id"],
        provider_id=connector_request["provider_id"],
        envelope_id=connector_request["envelope_id"],
        invocation_id=connector_request["invocation_id"],
        replay_identity=connector_request["replay_identity"],
    )


def validate_execution_gate_identity(identity: Any) -> dict[str, Any]:
    value = identity.to_dict() if hasattr(identity, "to_dict") else identity
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_gate_identity", "reason": "must be an object"}]}
    for field in (
        "execution_gate_id",
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "replay_identity",
    ):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "execution gate identity field must be non-empty"})
    if not errors:
        expected = execution_gate_id_for(
            connector_id=value["connector_id"],
            provider_id=value["provider_id"],
            envelope_id=value["envelope_id"],
            invocation_id=value["invocation_id"],
            replay_identity=value["replay_identity"],
        )
        if value["execution_gate_id"] != expected:
            errors.append({"field": "execution_gate_id", "reason": "execution gate identity mismatch"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "execution gate identity must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "execution gate identity must be replay-safe"})
    return {"valid": not errors, "errors": errors}
