"""Replay-safe governed session context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionContext:
    ingress_reference: dict[str, Any]
    envelope_reference: dict[str, Any]
    provider_invocation_reference: dict[str, Any]
    result_loop_reference: dict[str, Any]
    evidence_references: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingress_reference": self.ingress_reference,
            "envelope_reference": self.envelope_reference,
            "provider_invocation_reference": self.provider_invocation_reference,
            "result_loop_reference": self.result_loop_reference,
            "evidence_references": self.evidence_references,
            "mutable_hidden_memory_present": False,
            "autonomous_plan_present": False,
            "retry_queue_present": False,
            "routing_decision_present": False,
            "future_task_instructions_present": False,
            "replay_safe": True,
        }


def create_session_context(
    *,
    ingress_output: dict[str, Any],
    invocation_output: dict[str, Any],
    result_output: dict[str, Any],
) -> SessionContext:
    proposal = ingress_output["envelope_proposal"]
    envelope = proposal["execution_envelope"]
    invocation_result = invocation_output["invocation_result"]
    result_payload = result_output["result_payload"]
    return SessionContext(
        ingress_reference={
            "session_id": ingress_output["session"]["session_id"],
            "request_id": ingress_output["ingress_request"]["session"]["request_id"],
            "semantic_request_id": proposal["semantic_request"]["semantic_request_id"],
        },
        envelope_reference={
            "envelope_id": envelope["envelope_id"],
            "provider_id": envelope["provider_id"],
            "replay_identity": envelope["replay_identity"],
        },
        provider_invocation_reference={
            "invocation_id": invocation_result["invocation_id"],
            "provider_id": invocation_result["provider_id"],
            "envelope_id": invocation_result["envelope_id"],
        },
        result_loop_reference={
            "result_return_id": result_payload["result_return_id"],
            "invocation_id": result_payload["invocation_id"],
            "envelope_id": result_payload["envelope_id"],
        },
        evidence_references={
            "ingress_evidence": ingress_output.get("ingress_evidence", {}),
            "invocation_evidence": invocation_output.get("invocation_evidence", {}),
            "result_evidence": result_output.get("result_evidence", {}),
        },
    )


def validate_session_context(context: Any) -> dict[str, Any]:
    value = context.to_dict() if isinstance(context, SessionContext) else context
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "session_context", "reason": "must be an object"}]}
    for field in (
        "ingress_reference",
        "envelope_reference",
        "provider_invocation_reference",
        "result_loop_reference",
        "evidence_references",
    ):
        if not isinstance(value.get(field), dict) or not value.get(field):
            errors.append({"field": field, "reason": "missing session context reference"})
    for field in (
        "mutable_hidden_memory_present",
        "autonomous_plan_present",
        "retry_queue_present",
        "routing_decision_present",
        "future_task_instructions_present",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "session context contains forbidden autonomous state"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}
