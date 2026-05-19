"""Fail-closed schema validation for AGOL Bridge transport packages."""

from __future__ import annotations

from typing import Any

from .schemas.result_schema import RESULT_REQUIRED_FIELDS
from .schemas.task_schema import TASK_REQUIRED_FIELDS


def _validate_required_fields(package: Any, required_fields: dict[str, type], *, package_type: str) -> dict:
    errors: list[dict[str, str]] = []
    if not isinstance(package, dict):
        return {
            "valid": False,
            "errors": [{"field": package_type, "error": "package must be a JSON object"}],
        }
    for field, expected_type in required_fields.items():
        if field not in package:
            errors.append({"field": field, "error": "required field missing"})
            continue
        if not isinstance(package[field], expected_type):
            errors.append(
                {
                    "field": field,
                    "error": f"expected {expected_type.__name__}",
                }
            )
    return {"valid": not errors, "errors": errors}


def validate_task_package(package: Any) -> dict:
    validation = _validate_required_fields(package, TASK_REQUIRED_FIELDS, package_type="task_package")
    if not validation["valid"]:
        return validation
    errors = []
    if not package["task_id"].strip():
        errors.append({"field": "task_id", "error": "task_id must not be empty"})
    if not package["codex_prompt"].strip():
        errors.append({"field": "codex_prompt", "error": "codex_prompt must not be empty"})
    lifecycle_state = package["metadata"].get("lifecycle_state", "CREATED")
    if not isinstance(lifecycle_state, str):
        errors.append({"field": "metadata.lifecycle_state", "error": "expected str"})
    approved = package["metadata"].get("approved", False)
    if not isinstance(approved, bool):
        errors.append({"field": "metadata.approved", "error": "expected bool"})
    return {"valid": not errors, "errors": errors}


def validate_result_package(package: Any) -> dict:
    validation = _validate_required_fields(package, RESULT_REQUIRED_FIELDS, package_type="result_package")
    if not validation["valid"]:
        return validation
    errors = []
    if not package["status"].strip():
        errors.append({"field": "status", "error": "status must not be empty"})
    if not package["summary"].strip():
        errors.append({"field": "summary", "error": "summary must not be empty"})
    return {"valid": not errors, "errors": errors}
