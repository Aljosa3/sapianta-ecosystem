"""Replay-safe runtime binding between envelope and provider."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


BINDING_FIELDS = (
    "envelope_id",
    "provider_id",
    "replay_identity",
    "authority_scope",
    "workspace_scope",
    "validation_requirements",
)


@dataclass(frozen=True)
class RuntimeBinding:
    envelope_id: str
    provider_id: str
    replay_identity: str
    authority_scope: tuple[str, ...]
    workspace_scope: dict[str, Any]
    validation_requirements: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "authority_scope": list(self.authority_scope),
            "workspace_scope": self.workspace_scope,
            "validation_requirements": list(self.validation_requirements),
            "binding_sha256": binding_hash(
                {
                    "envelope_id": self.envelope_id,
                    "provider_id": self.provider_id,
                    "replay_identity": self.replay_identity,
                    "authority_scope": list(self.authority_scope),
                    "workspace_scope": self.workspace_scope,
                    "validation_requirements": list(self.validation_requirements),
                }
            ),
        }


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def create_runtime_binding(envelope: dict[str, Any]) -> RuntimeBinding:
    return RuntimeBinding(
        envelope_id=envelope["envelope_id"],
        provider_id=envelope["provider_id"],
        replay_identity=envelope["replay_identity"],
        authority_scope=tuple(envelope["authority_scope"]),
        workspace_scope=envelope["workspace_scope"],
        validation_requirements=tuple(envelope["validation_requirements"]),
    )


def validate_runtime_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, RuntimeBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "runtime_binding", "reason": "runtime binding must be an object"}],
        }
    for field in BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing runtime binding field"})
    for field in ("envelope_id", "provider_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "runtime binding field must be non-empty"})
    if "authority_scope" in value and (
        not isinstance(value["authority_scope"], list) or not value["authority_scope"]
    ):
        errors.append({"field": "authority_scope", "reason": "authority scope must be non-empty"})
    if "workspace_scope" in value and not isinstance(value["workspace_scope"], dict):
        errors.append({"field": "workspace_scope", "reason": "workspace scope must be an object"})
    if "validation_requirements" in value and (
        not isinstance(value["validation_requirements"], list) or not value["validation_requirements"]
    ):
        errors.append(
            {"field": "validation_requirements", "reason": "validation requirements must be non-empty"}
        )
    expected_hash = binding_hash(value) if not errors else None
    if "binding_sha256" in value and value["binding_sha256"] != expected_hash:
        errors.append({"field": "binding_sha256", "reason": "runtime binding hash mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "binding_sha256": expected_hash,
        "immutable_during_execution": True,
        "replay_safe": not errors,
    }
