"""Fail-closed guard for transport bridge delivery."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.runtime.runtime_binding import validate_runtime_binding

from .transport_binding import validate_transport_binding
from .transport_request import validate_transport_request


def guard_transport(
    *,
    request: dict[str, Any],
    provider: ExecutionProvider,
) -> dict[str, Any]:
    request_validation = validate_transport_request(request)
    runtime_validation = validate_runtime_binding(request.get("runtime_binding"))
    transport_validation = validate_transport_binding(request.get("transport_binding"))
    errors: list[dict[str, str]] = []
    if not request_validation["valid"]:
        errors.append({"field": "transport_request", "reason": "transport request invalid"})
    provider_identity_valid = request.get("provider_id") == provider.contract.provider_id
    if not provider_identity_valid:
        errors.append({"field": "provider_id", "reason": "provider identity mismatch"})
    authority_preserved = request.get("authority_scope") == request.get("runtime_binding", {}).get("authority_scope")
    if not authority_preserved:
        errors.append({"field": "authority_scope", "reason": "authority scope mutation detected"})
    workspace_preserved = request.get("workspace_scope") == request.get("runtime_binding", {}).get("workspace_scope")
    if not workspace_preserved:
        errors.append({"field": "workspace_scope", "reason": "workspace scope mutation detected"})
    if provider.contract.authority_escalation_allowed:
        errors.append({"field": "authority", "reason": "authority escalation detected"})
    if provider.contract.governance_mutation_allowed:
        errors.append({"field": "governance", "reason": "governance mutation capability detected"})
    return {
        "transport_allowed": not errors,
        "errors": errors,
        "blocked_reason": None if not errors else "; ".join(error["reason"] for error in errors),
        "provider_identity_valid": provider_identity_valid,
        "runtime_binding_valid": runtime_validation["valid"],
        "transport_binding_valid": transport_validation["valid"],
        "authority_preserved": authority_preserved,
        "workspace_preserved": workspace_preserved,
        "hidden_transport_mutation_detected": bool(errors),
        "routing_present": False,
        "fallback_present": False,
        "retry_present": False,
    }
