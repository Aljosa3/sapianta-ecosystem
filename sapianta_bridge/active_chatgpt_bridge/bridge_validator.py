"""Fail-closed active ChatGPT bridge validation."""

from __future__ import annotations

from typing import Any

from .bridge_binding import validate_bridge_binding
from .bridge_lifecycle import validate_bridge_lifecycle
from .bridge_request import validate_bridge_request
from .bridge_response import validate_bridge_response


def validate_bridge_artifacts(
    *,
    request: dict[str, Any],
    binding: dict[str, Any],
    response: dict[str, Any],
    lifecycle: list[str],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    request_validation = validate_bridge_request(request)
    binding_validation = validate_bridge_binding(binding)
    response_validation = validate_bridge_response(response)
    lifecycle_validation = validate_bridge_lifecycle(lifecycle)
    if not request_validation["valid"]:
        errors.append({"field": "request", "reason": "bridge request invalid"})
    if not binding_validation["valid"]:
        errors.append({"field": "binding", "reason": "bridge binding invalid"})
    if not response_validation["valid"]:
        errors.append({"field": "response", "reason": "bridge response invalid"})
    if not lifecycle_validation["valid"]:
        errors.append({"field": "lifecycle", "reason": "bridge lifecycle invalid"})
    if binding_validation["valid"] and isinstance(response, dict):
        if binding["bridge_id"] != response["bridge_id"]:
            errors.append({"field": "bridge_id", "reason": "bridge response binding mismatch"})
        for field in ("invocation_id", "provider_id", "envelope_id", "replay_identity"):
            if binding[field] != response.get(field):
                errors.append({"field": field, "reason": "bridge response lineage mismatch"})
    if request_validation["valid"] and binding_validation["valid"]:
        if request["bridge_request_id"] != binding["bridge_request_id"]:
            errors.append({"field": "bridge_request_id", "reason": "bridge request binding mismatch"})
        if request["semantic_request_identity"] != binding["semantic_request_id"]:
            errors.append({"field": "semantic_request_id", "reason": "semantic identity mismatch"})
        if request["replay_identity"] != binding["replay_identity"]:
            errors.append({"field": "replay_identity", "reason": "bridge replay identity mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "request_valid": request_validation["valid"],
        "binding_valid": binding_validation["valid"],
        "response_valid": response_validation["valid"],
        "lifecycle_valid": lifecycle_validation["valid"],
        "provider_identity_consistent": not any(error["field"] == "provider_id" for error in errors),
        "envelope_identity_consistent": not any(error["field"] == "envelope_id" for error in errors),
        "replay_safe": not errors,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
    }
