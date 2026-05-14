"""Deterministic provider capability classes."""

from __future__ import annotations

from typing import Any


CAPABILITY_CLASSES = (
    "CODE_GENERATION",
    "CODE_MODIFICATION",
    "TEST_EXECUTION",
    "DOCUMENT_ANALYSIS",
    "IMAGE_GENERATION",
    "IMAGE_EDITING",
    "DESIGN_GENERATION",
    "CAD_MODELING",
    "AUDIO_GENERATION",
    "VIDEO_GENERATION",
    "BROWSER_OPERATION",
    "ROBOTIC_ACTION",
    "INDUSTRIAL_CONTROL",
    "UNKNOWN",
)


CAPABILITY_TO_MODALITY = {
    "CODE_GENERATION": "CODE",
    "CODE_MODIFICATION": "CODE",
    "TEST_EXECUTION": "CODE",
    "DOCUMENT_ANALYSIS": "TEXT",
    "IMAGE_GENERATION": "IMAGE",
    "IMAGE_EDITING": "IMAGE",
    "DESIGN_GENERATION": "DESIGN",
    "CAD_MODELING": "CAD",
    "AUDIO_GENERATION": "AUDIO",
    "VIDEO_GENERATION": "VIDEO",
    "BROWSER_OPERATION": "BROWSER",
    "ROBOTIC_ACTION": "ROBOTIC",
    "INDUSTRIAL_CONTROL": "INDUSTRIAL",
    "UNKNOWN": "UNKNOWN",
}


def classify_capability(capability: str) -> str:
    return capability if capability in CAPABILITY_CLASSES else "UNKNOWN"


def modality_for_capability(capability: str) -> str:
    return CAPABILITY_TO_MODALITY.get(classify_capability(capability), "UNKNOWN")


def validate_capability_class(capability: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(capability, str) or not capability.strip():
        errors.append({"field": "capability_class", "reason": "capability class must be non-empty"})
    elif classify_capability(capability) == "UNKNOWN":
        errors.append({"field": "capability_class", "reason": "unknown capability fails closed"})
    return {
        "valid": not errors,
        "errors": errors,
        "capability_class": classify_capability(capability) if isinstance(capability, str) else "UNKNOWN",
        "execution_authority_granted": False,
        "routing_enabled": False,
        "orchestration_enabled": False,
    }
