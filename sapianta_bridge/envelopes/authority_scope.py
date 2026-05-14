"""Explicit bounded execution authority scope semantics."""

from __future__ import annotations

from typing import Any


AUTHORITY_SCOPES = (
    "READ_ONLY",
    "PATCH_EXISTING_FILES",
    "CREATE_NEW_FILES",
    "RUN_TESTS",
    "NO_NETWORK",
    "NO_RUNTIME_EXECUTION",
    "NO_PRIVILEGE_ESCALATION",
)

REQUIRED_DENY_SCOPES = ("NO_NETWORK", "NO_PRIVILEGE_ESCALATION")

CONFLICTING_SCOPES = (
    ("READ_ONLY", "PATCH_EXISTING_FILES"),
    ("READ_ONLY", "CREATE_NEW_FILES"),
)


def validate_authority_scope(scopes: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(scopes, list) or not scopes:
        return {
            "valid": False,
            "errors": [{"field": "authority_scope", "reason": "authority scope must be a non-empty list"}],
        }
    for scope in scopes:
        if scope not in AUTHORITY_SCOPES:
            errors.append({"field": "authority_scope", "reason": f"undefined authority scope: {scope}"})
    for required in REQUIRED_DENY_SCOPES:
        if required not in scopes:
            errors.append({"field": "authority_scope", "reason": f"required deny scope missing: {required}"})
    for left, right in CONFLICTING_SCOPES:
        if left in scopes and right in scopes:
            errors.append({"field": "authority_scope", "reason": f"conflicting authority scopes: {left}/{right}"})
    return {
        "valid": not errors,
        "errors": errors,
        "implicit_authority_allowed": False,
        "hidden_authority_detected": bool(errors),
    }


def authority_scope_rules() -> dict[str, Any]:
    return {
        "allowed_scopes": list(AUTHORITY_SCOPES),
        "required_deny_scopes": list(REQUIRED_DENY_SCOPES),
        "conflicting_scopes": [list(pair) for pair in CONFLICTING_SCOPES],
        "undefined_authority_policy": "FAIL_CLOSED",
        "implicit_authority_allowed": False,
    }
