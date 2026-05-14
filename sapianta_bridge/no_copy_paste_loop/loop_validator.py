"""Fail-closed no-copy/paste loop validation."""

from __future__ import annotations

from typing import Any

from .loop_binding import validate_loop_binding
from .loop_lifecycle import validate_loop_lifecycle
from .loop_request import validate_loop_request
from .loop_response import validate_loop_response


def validate_loop_artifacts(
    *,
    request: dict[str, Any],
    binding: dict[str, Any],
    response: dict[str, Any],
    lifecycle: list[str],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    request_validation = validate_loop_request(request)
    binding_validation = validate_loop_binding(binding)
    response_validation = validate_loop_response(response)
    lifecycle_validation = validate_loop_lifecycle(lifecycle)
    if not request_validation["valid"]:
        errors.append({"field": "request", "reason": "loop request invalid"})
    if not binding_validation["valid"]:
        errors.append({"field": "binding", "reason": "loop binding invalid"})
    if not response_validation["valid"]:
        errors.append({"field": "response", "reason": "loop response invalid"})
    if not lifecycle_validation["valid"]:
        errors.append({"field": "lifecycle", "reason": "loop lifecycle invalid"})
    if binding_validation["valid"] and isinstance(response, dict):
        for field in ("loop_id", "bridge_id", "session_id", "invocation_id", "provider_id", "envelope_id", "replay_identity"):
            if binding[field] != response.get(field):
                errors.append({"field": field, "reason": "loop response binding mismatch"})
    if request_validation["valid"] and binding_validation["valid"]:
        if request["loop_request_id"] != binding["loop_request_id"]:
            errors.append({"field": "loop_request_id", "reason": "loop request binding mismatch"})
        if request["requested_provider_id"] != binding["provider_id"]:
            errors.append({"field": "provider_id", "reason": "loop provider identity mismatch"})
        if request["replay_identity"] != binding["replay_identity"]:
            errors.append({"field": "replay_identity", "reason": "loop replay identity mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "request_valid": request_validation["valid"],
        "binding_valid": binding_validation["valid"],
        "response_valid": response_validation["valid"],
        "lifecycle_valid": lifecycle_validation["valid"],
        "lineage_continuity_valid": not errors,
        "provider_identity_consistent": not any(error["field"] == "provider_id" for error in errors),
        "replay_safe": not errors,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }
