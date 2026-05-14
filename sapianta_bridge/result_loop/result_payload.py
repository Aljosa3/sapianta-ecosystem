"""Interpretation-ready result return payload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .result_binding import create_result_binding, deterministic_hash


@dataclass(frozen=True)
class ResultPayload:
    result_return_id: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    execution_status: str
    invocation_status: str
    normalized_provider_result: dict[str, Any]
    replay_identity: str
    replay_hash: str
    evidence_references: dict[str, Any]
    result_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_return_id": self.result_return_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "execution_status": self.execution_status,
            "invocation_status": self.invocation_status,
            "normalized_provider_result": self.normalized_provider_result,
            "replay_identity": self.replay_identity,
            "replay_hash": self.replay_hash,
            "evidence_references": self.evidence_references,
            "result_binding": self.result_binding,
            "interpretation_ready": True,
            "autonomous_interpretation_present": False,
            "hidden_instructions_generated": False,
            "provider_invocation_present": False,
            "retry_present": False,
            "orchestration_present": False,
            "execution_authority_granted": False,
            "replay_safe": True,
        }


def create_result_payload(invocation_result: dict[str, Any], invocation_evidence: dict[str, Any]) -> ResultPayload:
    binding = create_result_binding(invocation_result, invocation_evidence).to_dict()
    normalized_result = invocation_result.get("normalized_result", {})
    evidence_references = {
        "invocation_evidence_hash": deterministic_hash(invocation_evidence),
        "runtime_result_hash": deterministic_hash(invocation_result.get("runtime_result", {})),
        "normalized_result_hash": deterministic_hash(normalized_result),
        "lifecycle": list(invocation_result.get("lifecycle", [])),
    }
    replay_hash = deterministic_hash(
        {
            "result_binding": binding,
            "normalized_provider_result": normalized_result,
            "evidence_references": evidence_references,
        }
    )
    return ResultPayload(
        result_return_id=binding["result_return_id"],
        invocation_id=invocation_result.get("invocation_id", ""),
        provider_id=invocation_result.get("provider_id", ""),
        envelope_id=invocation_result.get("envelope_id", ""),
        execution_status=normalized_result.get("execution_status", "BLOCKED"),
        invocation_status=invocation_result.get("invocation_status", "BLOCKED"),
        normalized_provider_result=normalized_result,
        replay_identity=invocation_result.get("replay_identity", ""),
        replay_hash=replay_hash,
        evidence_references=evidence_references,
        result_binding=binding,
    )
