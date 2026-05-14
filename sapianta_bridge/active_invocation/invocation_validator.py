"""Fail-closed active provider invocation validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.providers.provider_contracts import validate_provider_contract
from sapianta_bridge.runtime.runtime_binding import validate_runtime_binding

from .invocation_binding import validate_invocation_binding
from .invocation_lifecycle import validate_lifecycle


def validate_invocation_request(
    *,
    request: Any,
    provider: ExecutionProvider,
    lifecycle: list[str] | None = None,
) -> dict[str, Any]:
    value = request.to_dict() if hasattr(request, "to_dict") else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "invocation_request", "reason": "invocation request must be an object"}],
        }

    envelope = value.get("envelope")
    envelope_validation = validate_execution_envelope(envelope)
    contract_validation = validate_provider_contract(provider.contract)
    runtime_validation = validate_runtime_binding(value.get("runtime_binding"))
    binding_validation = validate_invocation_binding(value.get("invocation_binding"))
    lifecycle_validation = validate_lifecycle(lifecycle or ["PROPOSED"])

    if not envelope_validation.get("valid", False):
        errors.append({"field": "envelope", "reason": "envelope validation failed"})
    if not contract_validation["valid"]:
        errors.append({"field": "provider_contract", "reason": "provider contract invalid"})
    if not runtime_validation["valid"]:
        errors.append({"field": "runtime_binding", "reason": "runtime binding invalid"})
    if not binding_validation["valid"]:
        errors.append({"field": "invocation_binding", "reason": "invocation binding invalid"})
    if not lifecycle_validation["valid"]:
        errors.append({"field": "lifecycle", "reason": "invocation lifecycle invalid"})

    request_provider = value.get("provider_id")
    envelope_provider = envelope.get("provider_id") if isinstance(envelope, dict) else None
    provider_identity_valid = request_provider == provider.contract.provider_id == envelope_provider
    if not provider_identity_valid:
        errors.append({"field": "provider_id", "reason": "provider identity mismatch"})

    if value.get("provider_auto_selection") is not False:
        errors.append({"field": "provider_auto_selection", "reason": "provider auto-selection is forbidden"})
    for field in (
        "routing_present",
        "retry_present",
        "fallback_present",
        "concurrent_execution_present",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "orchestration behavior is forbidden"})

    return {
        "valid": not errors,
        "errors": errors,
        "envelope_valid": envelope_validation.get("valid", False),
        "provider_identity_valid": provider_identity_valid,
        "runtime_binding_valid": runtime_validation["valid"],
        "invocation_binding_valid": binding_validation["valid"],
        "lifecycle_valid": lifecycle_validation["valid"],
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
    }
