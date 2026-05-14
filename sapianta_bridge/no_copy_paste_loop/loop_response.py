"""Deterministic no-copy/paste loop response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NoCopyPasteLoopResponse:
    loop_id: str
    bridge_id: str
    session_id: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    result_status: str
    chatgpt_response_payload: dict[str, Any]
    replay_identity: str
    evidence_references: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "bridge_id": self.bridge_id,
            "session_id": self.session_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "result_status": self.result_status,
            "chatgpt_response_payload": self.chatgpt_response_payload,
            "replay_identity": self.replay_identity,
            "evidence_references": self.evidence_references,
            "autonomous_continuation_present": False,
            "recursive_execution_present": False,
            "orchestration_present": False,
            "retry_present": False,
            "provider_routing_present": False,
            "hidden_execution_present": False,
            "execution_authority_granted": False,
            "replay_safe": True,
        }


def create_loop_response(*, binding: dict[str, Any], bridge_output: dict[str, Any]) -> NoCopyPasteLoopResponse:
    bridge_response = bridge_output["bridge_response"]
    return NoCopyPasteLoopResponse(
        loop_id=binding["loop_id"],
        bridge_id=bridge_response["bridge_id"],
        session_id=bridge_response["session_id"],
        invocation_id=bridge_response["invocation_id"],
        provider_id=bridge_response["provider_id"],
        envelope_id=bridge_response["envelope_id"],
        result_status=bridge_response["result_status"],
        chatgpt_response_payload=bridge_response["interpretation_ready_payload"],
        replay_identity=bridge_response["replay_identity"],
        evidence_references={
            "loop_binding_hash": binding["binding_sha256"],
            "bridge_evidence": bridge_output.get("bridge_evidence", {}),
            "session_evidence": bridge_output.get("session_output", {}).get("session_evidence", {}),
            "result_evidence": bridge_output.get("result_output", {}).get("result_evidence", {}),
        },
    )


def validate_loop_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, NoCopyPasteLoopResponse) else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "loop_response", "reason": "must be an object"}]}
    for field in (
        "loop_id",
        "bridge_id",
        "session_id",
        "invocation_id",
        "provider_id",
        "envelope_id",
        "result_status",
        "chatgpt_response_payload",
        "replay_identity",
        "evidence_references",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing loop response field"})
    for field in ("loop_id", "bridge_id", "session_id", "invocation_id", "provider_id", "envelope_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "loop response field must be non-empty"})
    payload = value.get("chatgpt_response_payload")
    if not isinstance(payload, dict) or payload.get("interpretation_ready") is not True:
        errors.append({"field": "chatgpt_response_payload", "reason": "payload must be interpretation-ready"})
    if isinstance(payload, dict):
        for field in ("invocation_id", "provider_id", "envelope_id", "replay_identity"):
            if value.get(field) != payload.get(field):
                errors.append({"field": field, "reason": "loop response lineage mismatch"})
    for field in (
        "autonomous_continuation_present",
        "recursive_execution_present",
        "orchestration_present",
        "retry_present",
        "provider_routing_present",
        "hidden_execution_present",
        "execution_authority_granted",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "loop response contains forbidden behavior"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}
