"""Deterministic provider connector identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


CONNECTOR_MODE_PREPARE_ONLY = "PREPARE_ONLY"
CONNECTOR_TYPE_CODEX_CLI = "CODEX_CLI"
SUPPORTED_CONNECTOR_TYPES = (CONNECTOR_TYPE_CODEX_CLI,)
SUPPORTED_CONNECTOR_MODES = (CONNECTOR_MODE_PREPARE_ONLY,)


def connector_id_for(*, provider_id: str, connector_type: str, replay_identity: str) -> str:
    payload = {
        "connector_type": connector_type,
        "provider_id": provider_id,
        "replay_identity": replay_identity,
    }
    return f"PROVIDER-CONNECTOR-{stable_hash(payload)[:24]}"


@dataclass(frozen=True)
class ConnectorIdentity:
    connector_id: str
    provider_id: str
    connector_type: str
    replay_identity: str
    connector_mode: str = CONNECTOR_MODE_PREPARE_ONLY

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "connector_type": self.connector_type,
            "connector_mode": self.connector_mode,
            "replay_identity": self.replay_identity,
            "connector_is_provider_router": False,
            "connector_artifact_is_execution_authority": False,
            "autonomous_execution_present": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "shell_execution_present": False,
            "network_execution_present": False,
            "replay_safe": True,
        }


def create_connector_identity(
    *,
    provider_id: str,
    connector_type: str = CONNECTOR_TYPE_CODEX_CLI,
    replay_identity: str,
) -> ConnectorIdentity:
    return ConnectorIdentity(
        connector_id=connector_id_for(
            provider_id=provider_id,
            connector_type=connector_type,
            replay_identity=replay_identity,
        ),
        provider_id=provider_id,
        connector_type=connector_type,
        replay_identity=replay_identity,
    )


def validate_connector_identity(identity: Any) -> dict[str, Any]:
    value = identity.to_dict() if hasattr(identity, "to_dict") else identity
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "connector_identity", "reason": "must be an object"}]}
    for field in ("connector_id", "provider_id", "connector_type", "connector_mode", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "connector identity field must be non-empty"})
    if value.get("connector_type") not in SUPPORTED_CONNECTOR_TYPES:
        errors.append({"field": "connector_type", "reason": "unsupported connector type"})
    if value.get("connector_mode") not in SUPPORTED_CONNECTOR_MODES:
        errors.append({"field": "connector_mode", "reason": "unsupported connector mode"})
    if not errors:
        expected = connector_id_for(
            provider_id=value["provider_id"],
            connector_type=value["connector_type"],
            replay_identity=value["replay_identity"],
        )
        if value["connector_id"] != expected:
            errors.append({"field": "connector_id", "reason": "connector identity mismatch"})
    for field in (
        "connector_is_provider_router",
        "connector_artifact_is_execution_authority",
        "autonomous_execution_present",
        "routing_present",
        "retry_present",
        "fallback_present",
        "shell_execution_present",
        "network_execution_present",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "connector identity contains forbidden behavior"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "connector identity must be replay-safe"})
    return {"valid": not errors, "errors": errors}
