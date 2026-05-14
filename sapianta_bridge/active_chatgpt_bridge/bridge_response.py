"""Deterministic ChatGPT-facing bridge response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActiveChatGPTBridgeResponse:
    bridge_id: str
    session_id: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    result_status: str
    interpretation_ready_payload: dict[str, Any]
    evidence_references: dict[str, Any]
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "session_id": self.session_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "result_status": self.result_status,
            "interpretation_ready_payload": self.interpretation_ready_payload,
            "evidence_references": self.evidence_references,
            "replay_identity": self.replay_identity,
            "follow_up_tasks_executed": False,
            "autonomous_interpretation_present": False,
            "provider_output_hidden": False,
            "result_lineage_mutated": False,
            "execution_authority_granted": False,
            "replay_safe": True,
        }


def create_bridge_response(
    *,
    binding: dict[str, Any],
    session_output: dict[str, Any],
    result_output: dict[str, Any],
) -> ActiveChatGPTBridgeResponse:
    payload = result_output["result_payload"]
    return ActiveChatGPTBridgeResponse(
        bridge_id=binding["bridge_id"],
        session_id=session_output["session_identity"]["session_id"],
        invocation_id=payload["invocation_id"],
        provider_id=payload["provider_id"],
        envelope_id=payload["envelope_id"],
        result_status=payload["execution_status"],
        interpretation_ready_payload=payload,
        evidence_references={
            "bridge_binding_hash": binding["binding_sha256"],
            "session_evidence": session_output.get("session_evidence", {}),
            "result_evidence": result_output.get("result_evidence", {}),
        },
        replay_identity=payload["replay_identity"],
    )


def validate_bridge_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, ActiveChatGPTBridgeResponse) else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "bridge_response", "reason": "must be an object"}]}
    for field in (
        "bridge_id",
        "session_id",
        "invocation_id",
        "provider_id",
        "envelope_id",
        "result_status",
        "interpretation_ready_payload",
        "evidence_references",
        "replay_identity",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing bridge response field"})
    for field in ("bridge_id", "session_id", "invocation_id", "provider_id", "envelope_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "bridge response field must be non-empty"})
    payload = value.get("interpretation_ready_payload")
    if not isinstance(payload, dict) or payload.get("interpretation_ready") is not True:
        errors.append({"field": "interpretation_ready_payload", "reason": "payload must be interpretation-ready"})
    if isinstance(payload, dict):
        for field in ("invocation_id", "provider_id", "envelope_id", "replay_identity"):
            if value.get(field) != payload.get(field):
                errors.append({"field": field, "reason": "bridge response payload lineage mismatch"})
    for field in (
        "follow_up_tasks_executed",
        "autonomous_interpretation_present",
        "provider_output_hidden",
        "result_lineage_mutated",
        "execution_authority_granted",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "bridge response contains forbidden authority"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}
