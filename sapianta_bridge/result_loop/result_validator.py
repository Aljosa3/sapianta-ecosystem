"""Fail-closed result return validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.active_invocation.invocation_lifecycle import validate_lifecycle
from sapianta_bridge.active_invocation.invocation_result import validate_invocation_result
from sapianta_bridge.providers.normalized_result import validate_normalized_result

from .result_binding import deterministic_hash, validate_result_binding


def validate_result_payload(payload: Any) -> dict[str, Any]:
    value = payload.to_dict() if hasattr(payload, "to_dict") else payload
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "result_payload", "reason": "must be an object"}]}
    required = (
        "result_return_id",
        "invocation_id",
        "provider_id",
        "envelope_id",
        "execution_status",
        "invocation_status",
        "normalized_provider_result",
        "replay_identity",
        "replay_hash",
        "evidence_references",
        "result_binding",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing result payload field"})
    for field in ("result_return_id", "invocation_id", "provider_id", "envelope_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "result payload field must be non-empty"})
    binding_validation = validate_result_binding(value.get("result_binding"))
    errors.extend(binding_validation["errors"])
    binding = value.get("result_binding", {})
    for field in ("result_return_id", "invocation_id", "provider_id", "envelope_id", "replay_identity"):
        if isinstance(binding, dict) and value.get(field) != binding.get(field):
            errors.append({"field": field, "reason": "payload/result binding mismatch"})
    normalized_validation = validate_normalized_result(value.get("normalized_provider_result"))
    errors.extend(normalized_validation["errors"])
    evidence_refs = value.get("evidence_references")
    if not isinstance(evidence_refs, dict):
        errors.append({"field": "evidence_references", "reason": "evidence references must be an object"})
    elif not evidence_refs.get("invocation_evidence_hash"):
        errors.append({"field": "evidence_references", "reason": "missing invocation evidence hash"})
    if isinstance(evidence_refs, dict):
        lifecycle_validation = validate_lifecycle(evidence_refs.get("lifecycle"))
        if not lifecycle_validation["valid"]:
            errors.append({"field": "lifecycle", "reason": "invalid result lifecycle"})
    if value.get("execution_status") != value.get("normalized_provider_result", {}).get("execution_status"):
        errors.append({"field": "execution_status", "reason": "execution status mismatch"})
    if value.get("interpretation_ready") is not True:
        errors.append({"field": "interpretation_ready", "reason": "payload must be interpretation-ready"})
    for field in (
        "autonomous_interpretation_present",
        "hidden_instructions_generated",
        "provider_invocation_present",
        "retry_present",
        "orchestration_present",
        "execution_authority_granted",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "return loop authority expansion is forbidden"})
    expected_replay_hash = None
    if not errors:
        expected_replay_hash = deterministic_hash(
            {
                "result_binding": value["result_binding"],
                "normalized_provider_result": value["normalized_provider_result"],
                "evidence_references": value["evidence_references"],
            }
        )
        if value.get("replay_hash") != expected_replay_hash:
            errors.append({"field": "replay_hash", "reason": "result replay hash mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "result_binding_valid": binding_validation["valid"],
        "normalized_result_valid": normalized_validation["valid"],
        "replay_hash": expected_replay_hash,
        "replay_safe": not errors,
    }


def validate_result_inputs(invocation_result: Any, invocation_evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    result_validation = validate_invocation_result(invocation_result)
    if not result_validation["valid"]:
        errors.append({"field": "invocation_result", "reason": "invocation result invalid"})
    if not isinstance(invocation_evidence, dict):
        errors.append({"field": "invocation_evidence", "reason": "invocation evidence must be an object"})
    else:
        for field in ("invocation_id", "provider_id", "envelope_id", "replay_identity"):
            if invocation_result.get(field) != invocation_evidence.get(field):
                errors.append({"field": field, "reason": "invocation result/evidence mismatch"})
        if invocation_evidence.get("replay_safe") is not True:
            errors.append({"field": "invocation_evidence", "reason": "invocation evidence must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "invocation_result_valid": result_validation["valid"],
        "replay_safe": not errors,
    }
