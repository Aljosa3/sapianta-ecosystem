"""Fail-closed capability declaration validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.providers.provider_identity import validate_provider_identity

from .capability_declaration import CapabilityDeclaration
from .capability_model import modality_for_capability, validate_capability_class
from .modality_model import validate_modality_class


def validate_capability_declaration(declaration: Any) -> dict[str, Any]:
    value = declaration.to_dict() if isinstance(declaration, CapabilityDeclaration) else declaration
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "capability_declaration", "reason": "must be an object"}]}
    provider_validation = validate_provider_identity(
        {"provider_id": value.get("provider_id"), "provider_type": "CAPABILITY_DECLARATION"}
    )
    errors.extend(error for error in provider_validation["errors"] if error["field"] == "provider_id")
    capability_validation = validate_capability_class(value.get("capability_class"))
    modality_validation = validate_modality_class(value.get("modality_class"))
    errors.extend(capability_validation["errors"])
    errors.extend(modality_validation["errors"])
    if not capability_validation["errors"] and not modality_validation["errors"]:
        expected_modality = modality_for_capability(value["capability_class"])
        if value.get("modality_class") != expected_modality:
            errors.append({"field": "modality_class", "reason": "capability/modality mismatch"})
    if not isinstance(value.get("evidence_refs"), list):
        errors.append({"field": "evidence_refs", "reason": "evidence refs must be a list"})
    required_false_fields = (
        "execution_authority_granted",
        "envelope_bypass_allowed",
        "provider_abstraction_bypass_allowed",
        "routing_enabled",
        "orchestration_enabled",
        "autonomous_provider_selection_enabled",
    )
    for field in required_false_fields:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "capability declaration cannot grant authority"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "capability declaration must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "capability_admissible": not errors,
        "capability_authority_granted": False,
        "modality_execution_permission_granted": False,
        "routing_enabled": False,
        "orchestration_enabled": False,
        "autonomous_provider_selection_enabled": False,
        "replay_safe": not errors,
    }
