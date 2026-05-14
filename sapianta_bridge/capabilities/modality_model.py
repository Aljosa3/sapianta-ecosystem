"""Deterministic modality classes."""

from __future__ import annotations

from typing import Any


MODALITY_CLASSES = (
    "TEXT",
    "CODE",
    "IMAGE",
    "DESIGN",
    "CAD",
    "AUDIO",
    "VIDEO",
    "BROWSER",
    "ROBOTIC",
    "INDUSTRIAL",
    "UNKNOWN",
)


def classify_modality(modality: str) -> str:
    return modality if modality in MODALITY_CLASSES else "UNKNOWN"


def validate_modality_class(modality: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(modality, str) or not modality.strip():
        errors.append({"field": "modality_class", "reason": "modality class must be non-empty"})
    elif classify_modality(modality) == "UNKNOWN":
        errors.append({"field": "modality_class", "reason": "unknown modality fails closed"})
    return {
        "valid": not errors,
        "errors": errors,
        "modality_class": classify_modality(modality) if isinstance(modality, str) else "UNKNOWN",
        "execution_permission_granted": False,
        "provider_invocation_enabled": False,
    }
