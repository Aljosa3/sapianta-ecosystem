"""Deterministic execution envelope constraints."""

from __future__ import annotations

from typing import Any


CONSTRAINTS = (
    "NO_NETWORK",
    "NO_SHELL_ACCESS",
    "NO_FILESYSTEM_OUTSIDE_SCOPE",
    "NO_HIDDEN_EXECUTION",
    "BOUNDED_RUNTIME_DURATION",
    "VALIDATION_REQUIRED_BEFORE_CERTIFICATION",
)

REQUIRED_CONSTRAINTS = CONSTRAINTS


def validate_constraints(constraints: Any, timeout_seconds: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(constraints, list) or not constraints:
        errors.append({"field": "constraints", "reason": "constraints must be a non-empty list"})
        constraints = []
    for constraint in constraints:
        if constraint not in CONSTRAINTS:
            errors.append({"field": "constraints", "reason": f"undefined constraint: {constraint}"})
    for required in REQUIRED_CONSTRAINTS:
        if required not in constraints:
            errors.append({"field": "constraints", "reason": f"required constraint missing: {required}"})
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0 or timeout_seconds > 3600:
        errors.append({"field": "timeout_seconds", "reason": "timeout must be integer between 1 and 3600"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_execution_allowed": False,
        "adaptive_retry_allowed": False,
    }


def default_constraints() -> list[str]:
    return list(REQUIRED_CONSTRAINTS)
