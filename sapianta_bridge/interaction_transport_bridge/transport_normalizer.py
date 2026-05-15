"""Deterministic governed transport response normalization."""

from __future__ import annotations

from typing import Any


def normalize_transport_result(*, interaction_response: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    payload = interaction_response["result_payload"]
    return {
        "normalized_status": payload["execution_status"],
        "provider_id": interaction_response["provider_id"],
        "provider_invocation_id": binding["provider_invocation_id"],
        "bounded_runtime_id": binding["bounded_runtime_id"],
        "result_capture_id": binding["result_capture_id"],
        "response_return_id": binding["response_return_id"],
        "result_payload": payload,
        "replay_identity": binding["replay_identity"],
        "provider_evidence_preserved": True,
        "execution_evidence_altered": False,
        "missing_output_synthesized": False,
        "provider_success_fabricated": False,
        "prompt_rewritten": False,
    }


def validate_transport_normalization(normalized: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(normalized, dict):
        return {"valid": False, "errors": [{"field": "normalized_result", "reason": "must be object"}]}
    for field in ("normalized_status", "provider_id", "provider_invocation_id", "bounded_runtime_id", "result_capture_id", "response_return_id", "replay_identity"):
        if not isinstance(normalized.get(field), str) or not normalized[field].strip():
            errors.append({"field": field, "reason": "normalized result field must be non-empty"})
    payload = normalized.get("result_payload")
    if not isinstance(payload, dict) or payload.get("interpretation_ready") is not True:
        errors.append({"field": "result_payload", "reason": "normalization requires verified governed payload"})
    for field in ("execution_evidence_altered", "missing_output_synthesized", "provider_success_fabricated", "prompt_rewritten"):
        if normalized.get(field) is not False:
            errors.append({"field": field, "reason": "normalization contains forbidden mutation"})
    return {"valid": not errors, "errors": errors}
