"""Replay-safe result return evidence."""

from __future__ import annotations

from typing import Any


def result_return_evidence(*, payload: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_returned": validation.get("valid") is True,
        "result_return_id": payload.get("result_return_id", ""),
        "invocation_id": payload.get("invocation_id", ""),
        "provider_id": payload.get("provider_id", ""),
        "envelope_id": payload.get("envelope_id", ""),
        "replay_identity": payload.get("replay_identity", ""),
        "execution_status": payload.get("execution_status", "BLOCKED"),
        "invocation_status": payload.get("invocation_status", "BLOCKED"),
        "result_binding_valid": validation.get("result_binding_valid", False),
        "normalized_result_valid": validation.get("normalized_result_valid", False),
        "replay_hash": payload.get("replay_hash", ""),
        "interpretation_ready": payload.get("interpretation_ready") is True,
        "autonomous_interpretation_present": False,
        "provider_invocation_present": False,
        "retry_present": False,
        "orchestration_present": False,
        "execution_authority_granted": False,
        "replay_safe": validation.get("valid") is True,
    }


def validate_result_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "result_evidence", "reason": "must be an object"}]}
    required = (
        "result_returned",
        "result_return_id",
        "invocation_id",
        "provider_id",
        "envelope_id",
        "replay_identity",
        "result_binding_valid",
        "normalized_result_valid",
        "interpretation_ready",
        "replay_safe",
    )
    for field in required:
        if field not in evidence:
            errors.append({"field": field, "reason": "missing result evidence field"})
    for field in (
        "autonomous_interpretation_present",
        "provider_invocation_present",
        "retry_present",
        "orchestration_present",
        "execution_authority_granted",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "return loop authority expansion is forbidden"})
    return {"valid": not errors, "errors": errors}
