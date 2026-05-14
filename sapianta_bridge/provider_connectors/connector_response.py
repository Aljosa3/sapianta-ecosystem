"""Bounded connector response artifact."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CONNECTOR_RESPONSE_STATUSES = ("SUCCESS", "FAILED", "BLOCKED", "NEEDS_REVIEW")


@dataclass(frozen=True)
class ConnectorResponse:
    connector_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    transport_id: str
    replay_identity: str
    provider_transport_response: dict[str, Any]
    result_artifact_path: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "transport_id": self.transport_id,
            "replay_identity": self.replay_identity,
            "provider_transport_response": self.provider_transport_response,
            "result_artifact_path": self.result_artifact_path,
            "status": self.status,
            "provider_response_is_governance_decision": False,
            "connector_response_is_execution_authority": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_execution_present": False,
            "replay_safe": True,
        }


def create_connector_response(
    *,
    connector_request: dict[str, Any],
    provider_transport_response: dict[str, Any],
    result_artifact_path: str,
) -> ConnectorResponse:
    return ConnectorResponse(
        connector_id=connector_request["connector_id"],
        provider_id=provider_transport_response["provider_id"],
        envelope_id=provider_transport_response["envelope_id"],
        invocation_id=connector_request["invocation_id"],
        transport_id=provider_transport_response["transport_id"],
        replay_identity=provider_transport_response["replay_identity"],
        provider_transport_response=provider_transport_response,
        result_artifact_path=result_artifact_path,
        status=provider_transport_response["status"],
    )
