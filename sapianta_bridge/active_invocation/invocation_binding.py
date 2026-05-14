"""Replay-safe invocation binding."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sapianta_bridge.runtime.runtime_binding import create_runtime_binding, validate_runtime_binding


BINDING_FIELDS = (
    "invocation_id",
    "envelope_id",
    "provider_id",
    "replay_identity",
    "runtime_binding_hash",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deterministic_hash(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def invocation_identity(*, envelope_id: str, provider_id: str, replay_identity: str) -> str:
    digest = deterministic_hash(
        {
            "envelope_id": envelope_id,
            "provider_id": provider_id,
            "replay_identity": replay_identity,
        }
    )
    return f"INVOCATION-{digest[:24]}"


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return deterministic_hash(payload)


@dataclass(frozen=True)
class InvocationBinding:
    invocation_id: str
    envelope_id: str
    provider_id: str
    replay_identity: str
    runtime_binding_hash: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "invocation_id": self.invocation_id,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "runtime_binding_hash": self.runtime_binding_hash,
        }
        value["binding_sha256"] = binding_hash(value)
        value["replay_safe"] = True
        value["immutable"] = True
        return value


def create_invocation_binding(envelope: dict[str, Any], provider_id: str | None = None) -> InvocationBinding:
    explicit_provider_id = provider_id or envelope["provider_id"]
    runtime_binding = create_runtime_binding(envelope).to_dict()
    runtime_validation = validate_runtime_binding(runtime_binding)
    invocation_id = invocation_identity(
        envelope_id=envelope["envelope_id"],
        provider_id=explicit_provider_id,
        replay_identity=envelope["replay_identity"],
    )
    return InvocationBinding(
        invocation_id=invocation_id,
        envelope_id=envelope["envelope_id"],
        provider_id=explicit_provider_id,
        replay_identity=envelope["replay_identity"],
        runtime_binding_hash=runtime_validation.get("binding_sha256", ""),
    )


def validate_invocation_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, InvocationBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "invocation_binding", "reason": "invocation binding must be an object"}],
        }
    for field in BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing invocation binding field"})
    for field in ("invocation_id", "envelope_id", "provider_id", "replay_identity", "runtime_binding_hash"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "invocation binding field must be non-empty"})
    expected_id = None
    if not errors:
        expected_id = invocation_identity(
            envelope_id=value["envelope_id"],
            provider_id=value["provider_id"],
            replay_identity=value["replay_identity"],
        )
        if value["invocation_id"] != expected_id:
            errors.append({"field": "invocation_id", "reason": "invocation identity mismatch"})
    expected_hash = binding_hash(value) if not errors else None
    if "binding_sha256" in value and value["binding_sha256"] != expected_hash:
        errors.append({"field": "binding_sha256", "reason": "invocation binding hash mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "invocation binding must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "invocation_id": expected_id,
        "binding_sha256": expected_hash,
        "replay_safe": not errors,
        "immutable": not errors,
    }
