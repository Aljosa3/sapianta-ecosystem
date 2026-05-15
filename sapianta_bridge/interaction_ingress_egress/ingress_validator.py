"""Fail-closed local ingress validation."""

from __future__ import annotations

from typing import Any

from .ingress_request import LocalIngressRequest


def validate_ingress_artifact(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, LocalIngressRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_artifact", "reason": "must be object"}]}
    for field in ("ingress_artifact_id", "human_input", "conversation_id", "execution_gate_id", "bounded_runtime_id", "result_capture_id", "requested_provider_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "ingress artifact field must be non-empty"})
    for field in ("orchestration_requested", "retry_requested", "routing_requested", "autonomous_continuation_requested"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "ingress artifact contains forbidden behavior"})
    return {"valid": not errors, "errors": errors}
