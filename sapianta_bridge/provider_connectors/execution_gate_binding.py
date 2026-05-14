"""Replay-safe execution gate binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


BINDING_FIELDS = (
    "execution_gate_id",
    "connector_id",
    "transport_id",
    "provider_id",
    "envelope_id",
    "invocation_id",
    "replay_identity",
    "workspace_path",
    "timeout_seconds",
    "operation",
)


def execution_gate_binding_hash(value: dict[str, Any]) -> str:
    return stable_hash({field: value.get(field) for field in BINDING_FIELDS})


@dataclass(frozen=True)
class ExecutionGateBinding:
    execution_gate_id: str
    connector_id: str
    transport_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    replay_identity: str
    workspace_path: str
    timeout_seconds: int
    operation: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "execution_gate_id": self.execution_gate_id,
            "connector_id": self.connector_id,
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
            "workspace_path": self.workspace_path,
            "timeout_seconds": self.timeout_seconds,
            "operation": self.operation,
        }
        value["binding_sha256"] = execution_gate_binding_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_execution_gate_binding(
    *,
    execution_gate_id: str,
    connector_request: dict[str, Any],
    workspace_path: str,
    timeout_seconds: int,
    operation: str,
) -> ExecutionGateBinding:
    return ExecutionGateBinding(
        execution_gate_id=execution_gate_id,
        connector_id=connector_request["connector_id"],
        transport_id=connector_request["transport_id"],
        provider_id=connector_request["provider_id"],
        envelope_id=connector_request["envelope_id"],
        invocation_id=connector_request["invocation_id"],
        replay_identity=connector_request["replay_identity"],
        workspace_path=workspace_path,
        timeout_seconds=timeout_seconds,
        operation=operation,
    )


def validate_execution_gate_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if hasattr(binding, "to_dict") else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_gate_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if field == "timeout_seconds":
            if not isinstance(value.get(field), int) or value.get(field, 0) <= 0:
                errors.append({"field": field, "reason": "timeout must be a positive integer"})
            continue
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "execution gate binding field must be non-empty"})
    expected_hash = None
    if not errors:
        expected_hash = execution_gate_binding_hash(value)
        if value.get("binding_sha256") != expected_hash:
            errors.append({"field": "binding_sha256", "reason": "execution gate binding hash mismatch"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "execution gate binding must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "execution gate binding must be replay-safe"})
    return {"valid": not errors, "errors": errors, "binding_sha256": expected_hash}
