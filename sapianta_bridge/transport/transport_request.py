"""Deterministic transport request model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.runtime.runtime_binding import create_runtime_binding, validate_runtime_binding

from .transport_binding import create_transport_binding, validate_transport_binding


@dataclass(frozen=True)
class TransportRequest:
    envelope_id: str
    provider_id: str
    replay_identity: str
    runtime_binding: dict[str, Any]
    transport_binding: dict[str, Any]
    authority_scope: tuple[str, ...]
    workspace_scope: dict[str, Any]
    validation_requirements: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "runtime_binding": self.runtime_binding,
            "transport_binding": self.transport_binding,
            "authority_scope": list(self.authority_scope),
            "workspace_scope": self.workspace_scope,
            "validation_requirements": list(self.validation_requirements),
            "implicit_authority_allowed": False,
            "provider_specific_permissions_injected": False,
        }


def create_transport_request(envelope: dict[str, Any]) -> TransportRequest:
    runtime_binding = create_runtime_binding(envelope).to_dict()
    transport_binding = create_transport_binding(
        envelope=envelope,
        runtime_binding=runtime_binding,
    ).to_dict()
    return TransportRequest(
        envelope_id=envelope["envelope_id"],
        provider_id=envelope["provider_id"],
        replay_identity=envelope["replay_identity"],
        runtime_binding=runtime_binding,
        transport_binding=transport_binding,
        authority_scope=tuple(envelope["authority_scope"]),
        workspace_scope=envelope["workspace_scope"],
        validation_requirements=tuple(envelope["validation_requirements"]),
    )


def validate_transport_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, TransportRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "transport_request", "reason": "transport request must be an object"}],
        }
    required = (
        "envelope_id",
        "provider_id",
        "replay_identity",
        "runtime_binding",
        "transport_binding",
        "authority_scope",
        "workspace_scope",
        "validation_requirements",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing transport request field"})
    for field in ("envelope_id", "provider_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "transport request field must be non-empty"})
    if value.get("implicit_authority_allowed") is True:
        errors.append({"field": "implicit_authority_allowed", "reason": "implicit authority is forbidden"})
    if value.get("provider_specific_permissions_injected") is True:
        errors.append(
            {
                "field": "provider_specific_permissions_injected",
                "reason": "provider-specific permissions are forbidden",
            }
        )
    runtime_validation = validate_runtime_binding(value.get("runtime_binding"))
    transport_validation = validate_transport_binding(value.get("transport_binding"))
    errors.extend(runtime_validation["errors"])
    errors.extend(transport_validation["errors"])
    if "runtime_binding" in value and isinstance(value.get("runtime_binding"), dict):
        runtime = value["runtime_binding"]
        for field in ("envelope_id", "provider_id", "replay_identity"):
            if value.get(field) != runtime.get(field):
                errors.append({"field": field, "reason": "transport request/runtime binding mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "runtime_binding_valid": runtime_validation["valid"],
        "transport_binding_valid": transport_validation["valid"],
        "immutable_after_validation": not errors,
        "replay_safe": not errors,
    }
