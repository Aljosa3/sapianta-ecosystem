"""Metadata-only provider registry for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


DETACHED = "DETACHED"
ATTACHED = "ATTACHED"
AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
VALID_PROVIDER_STATUSES = frozenset({DETACHED, ATTACHED, AVAILABLE, UNAVAILABLE})


@dataclass(frozen=True)
class ProviderMetadata:
    provider_id: str
    provider_type: str
    provider_version: str
    provider_status: str
    domain: str = "unspecified"
    capability: str = "proposal_generation"
    resource_type: str = "provider"

    def to_dict(self) -> dict[str, Any]:
        provider = {
            "provider_id": _normalize_identifier(self.provider_id, "provider_id"),
            "provider_type": _normalize_token(self.provider_type, "provider_type"),
            "provider_version": _require_string(self.provider_version, "provider_version"),
            "provider_status": _normalize_token(self.provider_status, "provider_status"),
            "domain": _normalize_metadata(self.domain, "domain"),
            "capability": _normalize_metadata(self.capability, "capability"),
            "resource_type": _normalize_metadata(self.resource_type, "resource_type"),
            "execution_capable": False,
            "dispatch_capable": False,
            "authority": False,
        }
        if provider["provider_status"] not in VALID_PROVIDER_STATUSES:
            raise FailClosedRuntimeError("provider status is invalid")
        provider["provider_identity_hash"] = replay_hash(provider)
        return provider


class ProviderRegistry:
    """Deterministic metadata registry. It does not dispatch or execute providers."""

    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {}

    def register_provider(self, metadata: ProviderMetadata | dict[str, Any]) -> dict[str, Any]:
        provider = _metadata_to_dict(metadata)
        provider_id = provider["provider_id"]
        if provider_id in self._providers:
            raise FailClosedRuntimeError("provider is already registered")
        self._providers[provider_id] = deepcopy(provider)
        return deepcopy(provider)

    def lookup_provider(self, provider_id: str) -> dict[str, Any]:
        normalized = _normalize_identifier(provider_id, "provider_id")
        provider = self._providers.get(normalized)
        if provider is None:
            raise FailClosedRuntimeError("provider is unknown")
        _validate_provider_metadata(provider)
        return deepcopy(provider)

    def provider_metadata(self) -> list[dict[str, Any]]:
        return [deepcopy(provider) for provider in self._providers.values()]


def _metadata_to_dict(metadata: ProviderMetadata | dict[str, Any]) -> dict[str, Any]:
    provider = metadata.to_dict() if isinstance(metadata, ProviderMetadata) else _canonicalize_metadata_dict(metadata)
    _validate_provider_metadata(provider)
    return provider


def _canonicalize_metadata_dict(metadata: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise FailClosedRuntimeError("provider metadata must be a JSON object")
    provider = deepcopy(metadata)
    existing_hash = provider.pop("provider_identity_hash", None)
    provider["provider_id"] = _normalize_identifier(provider.get("provider_id"), "provider_id")
    provider["provider_type"] = _normalize_token(provider.get("provider_type"), "provider_type")
    provider["provider_version"] = _require_string(provider.get("provider_version"), "provider_version")
    provider["provider_status"] = _normalize_token(provider.get("provider_status"), "provider_status")
    provider["domain"] = _normalize_metadata(provider.get("domain", "unspecified"), "domain")
    provider["capability"] = _normalize_metadata(provider.get("capability", "proposal_generation"), "capability")
    provider["resource_type"] = _normalize_metadata(provider.get("resource_type", "provider"), "resource_type")
    provider["execution_capable"] = provider.get("execution_capable", False)
    provider["dispatch_capable"] = provider.get("dispatch_capable", False)
    provider["authority"] = provider.get("authority", False)
    provider["provider_identity_hash"] = replay_hash(provider)
    if existing_hash is not None and existing_hash != provider["provider_identity_hash"]:
        raise FailClosedRuntimeError("provider identity hash mismatch")
    return provider


def _validate_provider_metadata(provider: dict[str, Any]) -> None:
    if not isinstance(provider, dict):
        raise FailClosedRuntimeError("provider metadata must be a JSON object")
    if provider.get("execution_capable") is not False:
        raise FailClosedRuntimeError("provider metadata cannot be execution capable")
    if provider.get("dispatch_capable") is not False:
        raise FailClosedRuntimeError("provider metadata cannot dispatch")
    if provider.get("authority") is not False:
        raise FailClosedRuntimeError("provider metadata cannot carry authority")
    _normalize_identifier(provider.get("provider_id"), "provider_id")
    _normalize_token(provider.get("provider_type"), "provider_type")
    _require_string(provider.get("provider_version"), "provider_version")
    _normalize_metadata(provider.get("domain", "unspecified"), "domain")
    _normalize_metadata(provider.get("capability", "proposal_generation"), "capability")
    _normalize_metadata(provider.get("resource_type", "provider"), "resource_type")
    status = _normalize_token(provider.get("provider_status"), "provider_status")
    if status not in VALID_PROVIDER_STATUSES:
        raise FailClosedRuntimeError("provider status is invalid")
    actual_hash = _require_string(provider.get("provider_identity_hash"), "provider_identity_hash")
    expected_input = deepcopy(provider)
    expected_input.pop("provider_identity_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider identity hash mismatch")


def _normalize_identifier(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip()


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _normalize_metadata(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().lower().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
