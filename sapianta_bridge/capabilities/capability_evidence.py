"""Replay-safe provider capability evidence."""

from __future__ import annotations

from typing import Any

from .capability_validator import validate_capability_declaration


def capability_evidence(declaration: Any) -> dict[str, Any]:
    value = declaration.to_dict() if hasattr(declaration, "to_dict") else declaration
    validation = validate_capability_declaration(value)
    return {
        "provider_id": value.get("provider_id", "") if isinstance(value, dict) else "",
        "capability_class": value.get("capability_class", "UNKNOWN") if isinstance(value, dict) else "UNKNOWN",
        "modality_class": value.get("modality_class", "UNKNOWN") if isinstance(value, dict) else "UNKNOWN",
        "capability_admissible": validation["valid"],
        "execution_authority_granted": False,
        "modality_execution_permission_granted": False,
        "provider_invocation_enabled": False,
        "routing_enabled": False,
        "orchestration_enabled": False,
        "autonomous_provider_selection_enabled": False,
        "replay_safe": validation["valid"],
        "errors": validation["errors"],
    }


def validate_capability_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "capability_evidence", "reason": "must be an object"}]}
    for field in ("provider_id", "capability_class", "modality_class", "capability_admissible", "replay_safe"):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing capability evidence field"})
    for field in (
        "execution_authority_granted",
        "modality_execution_permission_granted",
        "provider_invocation_enabled",
        "routing_enabled",
        "orchestration_enabled",
        "autonomous_provider_selection_enabled",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "capability evidence reports forbidden authority"})
    return {"valid": not errors, "errors": errors}
