"""Replay-safe transport binding for envelope delivery."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


TRANSPORT_BINDING_FIELDS = (
    "transport_id",
    "provider_id",
    "envelope_id",
    "replay_identity",
    "runtime_binding_hash",
)


@dataclass(frozen=True)
class TransportBinding:
    transport_id: str
    provider_id: str
    envelope_id: str
    replay_identity: str
    runtime_binding_hash: str

    def to_dict(self) -> dict[str, str]:
        value = {
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "replay_identity": self.replay_identity,
            "runtime_binding_hash": self.runtime_binding_hash,
        }
        value["transport_binding_sha256"] = compute_transport_binding_hash(value)
        return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_transport_binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in TRANSPORT_BINDING_FIELDS}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def create_transport_binding(
    *,
    envelope: dict[str, Any],
    runtime_binding: dict[str, Any],
) -> TransportBinding:
    envelope_id = envelope["envelope_id"]
    return TransportBinding(
        transport_id=f"TRANSPORT-{envelope_id}",
        provider_id=envelope["provider_id"],
        envelope_id=envelope_id,
        replay_identity=envelope["replay_identity"],
        runtime_binding_hash=runtime_binding["binding_sha256"],
    )


def validate_transport_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, TransportBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "transport_binding", "reason": "transport binding must be an object"}],
        }
    for field in TRANSPORT_BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing transport binding field"})
    for field in TRANSPORT_BINDING_FIELDS:
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "transport binding field must be non-empty"})
    expected = compute_transport_binding_hash(value) if not errors else None
    if "transport_binding_sha256" in value and value["transport_binding_sha256"] != expected:
        errors.append({"field": "transport_binding_sha256", "reason": "transport binding hash mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "transport_binding_sha256": expected,
        "immutable": True,
        "replay_safe": not errors,
    }
