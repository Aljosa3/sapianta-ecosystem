"""Replay-safe binding between transport artifacts and provider connector artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


BINDING_FIELDS = (
    "connector_id",
    "transport_id",
    "provider_id",
    "envelope_id",
    "invocation_id",
    "replay_identity",
    "task_artifact_path",
    "expected_result_artifact_path",
)


def connector_binding_hash(value: dict[str, Any]) -> str:
    return stable_hash({field: value.get(field) for field in BINDING_FIELDS})


@dataclass(frozen=True)
class ConnectorBinding:
    connector_id: str
    transport_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    replay_identity: str
    task_artifact_path: str
    expected_result_artifact_path: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "connector_id": self.connector_id,
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
            "task_artifact_path": self.task_artifact_path,
            "expected_result_artifact_path": self.expected_result_artifact_path,
        }
        value["binding_sha256"] = connector_binding_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_connector_binding(
    *,
    connector_id: str,
    transport_id: str,
    provider_id: str,
    envelope_id: str,
    invocation_id: str,
    replay_identity: str,
    task_artifact_path: str,
    expected_result_artifact_path: str,
) -> ConnectorBinding:
    return ConnectorBinding(
        connector_id=connector_id,
        transport_id=transport_id,
        provider_id=provider_id,
        envelope_id=envelope_id,
        invocation_id=invocation_id,
        replay_identity=replay_identity,
        task_artifact_path=task_artifact_path,
        expected_result_artifact_path=expected_result_artifact_path,
    )


def validate_connector_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if hasattr(binding, "to_dict") else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "connector_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "connector binding field must be non-empty"})
    expected_hash = None
    if not errors:
        expected_hash = connector_binding_hash(value)
        if value.get("binding_sha256") != expected_hash:
            errors.append({"field": "binding_sha256", "reason": "connector binding hash mismatch"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "connector binding must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "connector binding must be replay-safe"})
    return {"valid": not errors, "errors": errors, "binding_sha256": expected_hash}
