"""Deterministic provider identity handling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


SUPPORTED_PROVIDER_IDS = ("codex", "claude_code", "local_executor", "deterministic_mock")
PROVIDER_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


@dataclass(frozen=True)
class ProviderIdentity:
    provider_id: str
    provider_type: str

    def to_dict(self) -> dict[str, str]:
        return {"provider_id": self.provider_id, "provider_type": self.provider_type}


def normalize_provider_id(provider_id: str) -> str:
    return provider_id.strip().lower().replace("-", "_")


def create_provider_identity(provider_id: str, provider_type: str) -> ProviderIdentity:
    normalized = normalize_provider_id(provider_id)
    return ProviderIdentity(provider_id=normalized, provider_type=provider_type)


def validate_provider_identity(identity: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if isinstance(identity, ProviderIdentity):
        value = identity.to_dict()
    elif isinstance(identity, dict):
        value = identity
    else:
        value = {}
        errors.append({"field": "provider_identity", "reason": "provider identity must be an object"})
    provider_id = value.get("provider_id")
    if not isinstance(provider_id, str) or not provider_id.strip():
        errors.append({"field": "provider_id", "reason": "provider_id must be non-empty"})
    elif normalize_provider_id(provider_id) != provider_id:
        errors.append({"field": "provider_id", "reason": "provider_id must be normalized"})
    elif PROVIDER_ID_PATTERN.match(provider_id) is None:
        errors.append({"field": "provider_id", "reason": "provider_id has invalid format"})
    provider_type = value.get("provider_type")
    if not isinstance(provider_type, str) or not provider_type.strip():
        errors.append({"field": "provider_type", "reason": "provider_type must be non-empty"})
    return {
        "valid": not errors,
        "errors": errors,
        "provider_identity_affects_governance": False,
        "provider_identity_affects_validation": False,
        "provider_identity_affects_replay": False,
    }
