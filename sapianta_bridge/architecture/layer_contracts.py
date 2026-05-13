"""Deterministic layer contract validation."""

from __future__ import annotations

from typing import Any

from .layer_model import LAYER_DEFINITIONS, LAYER_ORDER, PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS


REQUIRED_LAYER_FIELDS = ("responsibilities", "allowed", "forbidden", "authority")


def validate_layer_contract(layer: str, contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if layer not in LAYER_DEFINITIONS:
        errors.append({"field": "layer", "reason": "unknown layer"})
    for field in REQUIRED_LAYER_FIELDS:
        if field not in contract:
            errors.append({"field": field, "reason": "missing layer contract field"})
    for field in ("responsibilities", "allowed", "forbidden"):
        values = contract.get(field)
        if not isinstance(values, (tuple, list)) or not values:
            errors.append({"field": field, "reason": "contract field must be a non-empty sequence"})
    if not isinstance(contract.get("authority"), str) or not contract.get("authority", "").strip():
        errors.append({"field": "authority", "reason": "authority must be explicit"})
    return {"valid": not errors, "errors": errors}


def validate_all_layer_contracts() -> dict[str, Any]:
    results = {
        layer: validate_layer_contract(layer, LAYER_DEFINITIONS[layer])
        for layer in LAYER_ORDER
    }
    return {
        "valid": all(result["valid"] for result in results.values()),
        "layers": results,
        "provider_independent_execution": dict(PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS),
    }


def validate_provider_contract(provider: str) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(provider, str) or not provider.strip():
        errors.append({"field": "provider", "reason": "provider identity must be non-empty"})
    if PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS[
        "provider_identity_affects_governance_semantics"
    ]:
        errors.append(
            {
                "field": "provider_identity",
                "reason": "provider identity must not affect governance semantics",
            }
        )
    if not PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS["providers_non_authoritative"]:
        errors.append({"field": "provider_authority", "reason": "providers must be non-authoritative"})
    return {"valid": not errors, "errors": errors}
