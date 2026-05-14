"""Explicit provider transport response artifact."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TRANSPORT_RESPONSE_STATUSES = ("SUCCESS", "FAILED", "BLOCKED", "NEEDS_REVIEW")


@dataclass(frozen=True)
class ProviderTransportResponse:
    transport_id: str
    provider_id: str
    envelope_id: str
    status: str
    result_payload: dict[str, Any]
    evidence_references: dict[str, Any]
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "status": self.status,
            "result_payload": self.result_payload,
            "evidence_references": self.evidence_references,
            "replay_identity": self.replay_identity,
            "provider_response_is_governance_decision": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "replay_safe": True,
        }


def create_provider_transport_response(
    *,
    request: dict[str, Any],
    status: str = "SUCCESS",
    result_payload: dict[str, Any] | None = None,
    evidence_references: dict[str, Any] | None = None,
) -> ProviderTransportResponse:
    return ProviderTransportResponse(
        transport_id=request["transport_id"],
        provider_id=request["provider_id"],
        envelope_id=request["envelope_id"],
        status=status,
        result_payload=result_payload or {"execution_status": status, "artifacts_created": []},
        evidence_references=evidence_references or {"transport_request_id": request["transport_id"]},
        replay_identity=request["replay_identity"],
    )
