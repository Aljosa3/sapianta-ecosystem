"""Fail-closed runtime guard for adapter execution."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.providers.provider_contracts import validate_provider_contract

from .runtime_binding import RuntimeBinding, validate_runtime_binding


def guard_runtime(
    *,
    envelope: dict[str, Any],
    provider: ExecutionProvider,
    binding: RuntimeBinding | None,
    envelope_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    envelope_result = envelope_validation or validate_execution_envelope(envelope)
    contract_result = validate_provider_contract(provider.contract)
    binding_result = (
        validate_runtime_binding(binding)
        if binding is not None
        else {"valid": False, "errors": [{"field": "binding", "reason": "runtime binding missing"}]}
    )
    errors: list[dict[str, str]] = []
    if not envelope_result.get("valid", envelope_result.get("envelope_valid", False)):
        errors.append({"field": "envelope", "reason": "envelope validation failed"})
    if not contract_result["valid"]:
        errors.append({"field": "provider_contract", "reason": "provider contract invalid"})
    if not binding_result["valid"]:
        errors.append({"field": "binding", "reason": "runtime binding invalid"})
    provider_identity_valid = envelope.get("provider_id") == provider.contract.provider_id
    if not provider_identity_valid:
        errors.append({"field": "provider_id", "reason": "provider identity mismatch"})
    authority_escalation_detected = provider.contract.authority_escalation_allowed is True
    if authority_escalation_detected:
        errors.append({"field": "authority", "reason": "authority escalation detected"})
    if provider.contract.governance_mutation_allowed is True:
        errors.append({"field": "governance", "reason": "governance mutation capability detected"})
    if provider.contract.replay_mutation_allowed is True:
        errors.append({"field": "replay", "reason": "replay mutation capability detected"})
    return {
        "runtime_allowed": not errors,
        "blocked_reason": None if not errors else "; ".join(error["reason"] for error in errors),
        "errors": errors,
        "authority_escalation_detected": authority_escalation_detected,
        "provider_identity_valid": provider_identity_valid,
        "envelope_valid": envelope_result.get("valid", envelope_result.get("envelope_valid", False)),
        "binding_valid": binding_result["valid"],
        "routing_present": False,
        "fallback_present": False,
        "retry_present": False,
        "external_api_calls_present": False,
    }
