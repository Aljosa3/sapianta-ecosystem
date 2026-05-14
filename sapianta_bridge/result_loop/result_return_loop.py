"""Canonical bounded result return loop."""

from __future__ import annotations

from typing import Any

from .result_evidence import result_return_evidence
from .result_payload import create_result_payload
from .result_validator import validate_result_inputs, validate_result_payload


def _blocked_payload(invocation_result: Any) -> dict[str, Any]:
    value = invocation_result if isinstance(invocation_result, dict) else {}
    return {
        "result_return_id": "",
        "invocation_id": value.get("invocation_id", ""),
        "provider_id": value.get("provider_id", ""),
        "envelope_id": value.get("envelope_id", ""),
        "execution_status": "BLOCKED",
        "invocation_status": value.get("invocation_status", "BLOCKED"),
        "normalized_provider_result": {},
        "replay_identity": value.get("replay_identity", ""),
        "replay_hash": "",
        "evidence_references": {},
        "result_binding": {},
        "interpretation_ready": False,
        "autonomous_interpretation_present": False,
        "hidden_instructions_generated": False,
        "provider_invocation_present": False,
        "retry_present": False,
        "orchestration_present": False,
        "execution_authority_granted": False,
        "replay_safe": False,
    }


def return_invocation_result(
    *,
    invocation_result: dict[str, Any],
    invocation_evidence: dict[str, Any],
) -> dict[str, Any]:
    input_validation = validate_result_inputs(invocation_result, invocation_evidence)
    if not input_validation["valid"]:
        payload = _blocked_payload(invocation_result)
        evidence = result_return_evidence(payload=payload, validation=input_validation)
        return {
            "result_payload": payload,
            "result_validation": input_validation,
            "result_evidence": evidence,
            "provider_invocation_present": False,
            "retry_present": False,
            "orchestration_present": False,
            "autonomous_interpretation_present": False,
        }

    payload = create_result_payload(invocation_result, invocation_evidence).to_dict()
    validation = validate_result_payload(payload)
    if not validation["valid"]:
        blocked = _blocked_payload(invocation_result)
        evidence = result_return_evidence(payload=blocked, validation=validation)
        return {
            "result_payload": blocked,
            "result_validation": validation,
            "result_evidence": evidence,
            "provider_invocation_present": False,
            "retry_present": False,
            "orchestration_present": False,
            "autonomous_interpretation_present": False,
        }
    evidence = result_return_evidence(payload=payload, validation=validation)
    return {
        "result_payload": payload,
        "result_validation": validation,
        "result_evidence": evidence,
        "provider_invocation_present": False,
        "retry_present": False,
        "orchestration_present": False,
        "autonomous_interpretation_present": False,
    }
