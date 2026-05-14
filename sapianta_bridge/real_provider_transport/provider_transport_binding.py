"""Replay-safe provider transport binding."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


BINDING_FIELDS = (
    "transport_id",
    "provider_id",
    "envelope_id",
    "invocation_id",
    "replay_identity",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def transport_id_for(*, provider_id: str, envelope_id: str, invocation_id: str, replay_identity: str) -> str:
    return f"PROVIDER-TRANSPORT-{stable_hash({'provider_id': provider_id, 'envelope_id': envelope_id, 'invocation_id': invocation_id, 'replay_identity': replay_identity})[:24]}"


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return stable_hash(payload)


@dataclass(frozen=True)
class ProviderTransportBinding:
    transport_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
        }
        value["binding_sha256"] = binding_hash(value)
        value["replay_safe"] = True
        value["immutable"] = True
        return value


def create_provider_transport_binding(
    *,
    provider_id: str,
    envelope_id: str,
    invocation_id: str,
    replay_identity: str,
) -> ProviderTransportBinding:
    return ProviderTransportBinding(
        transport_id=transport_id_for(
            provider_id=provider_id,
            envelope_id=envelope_id,
            invocation_id=invocation_id,
            replay_identity=replay_identity,
        ),
        provider_id=provider_id,
        envelope_id=envelope_id,
        invocation_id=invocation_id,
        replay_identity=replay_identity,
    )


def validate_provider_transport_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, ProviderTransportBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "transport binding field must be non-empty"})
    expected_id = None
    expected_hash = None
    if not errors:
        expected_id = transport_id_for(
            provider_id=value["provider_id"],
            envelope_id=value["envelope_id"],
            invocation_id=value["invocation_id"],
            replay_identity=value["replay_identity"],
        )
        expected_hash = binding_hash(value)
        if value["transport_id"] != expected_id:
            errors.append({"field": "transport_id", "reason": "transport identity mismatch"})
        if value.get("binding_sha256") != expected_hash:
            errors.append({"field": "binding_sha256", "reason": "transport binding hash mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "transport binding must be replay-safe"})
    return {"valid": not errors, "errors": errors, "transport_id": expected_id, "binding_sha256": expected_hash}
