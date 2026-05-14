"""Bounded connector request artifact."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .connector_binding import create_connector_binding
from .connector_identity import (
    CONNECTOR_MODE_PREPARE_ONLY,
    CONNECTOR_TYPE_CODEX_CLI,
    create_connector_identity,
)


@dataclass(frozen=True)
class ConnectorRequest:
    connector_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    transport_id: str
    replay_identity: str
    provider_transport_request: dict[str, Any]
    bounded_task_artifact_path: str
    expected_result_artifact_path: str
    connector_mode: str
    connector_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "transport_id": self.transport_id,
            "replay_identity": self.replay_identity,
            "provider_transport_request": self.provider_transport_request,
            "bounded_task_artifact_path": self.bounded_task_artifact_path,
            "expected_result_artifact_path": self.expected_result_artifact_path,
            "connector_mode": self.connector_mode,
            "connector_binding": self.connector_binding,
            "connector_artifact_is_execution_authority": False,
            "provider_auto_selection_present": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_execution_present": False,
            "shell_execution_present": False,
            "network_execution_present": False,
            "replay_safe": True,
        }


def create_connector_request(
    *,
    provider_transport_request: dict[str, Any],
    bounded_task_artifact_path: str,
    expected_result_artifact_path: str,
    connector_type: str = CONNECTOR_TYPE_CODEX_CLI,
) -> ConnectorRequest:
    identity = create_connector_identity(
        provider_id=provider_transport_request["provider_id"],
        connector_type=connector_type,
        replay_identity=provider_transport_request["replay_identity"],
    ).to_dict()
    binding = create_connector_binding(
        connector_id=identity["connector_id"],
        transport_id=provider_transport_request["transport_id"],
        provider_id=provider_transport_request["provider_id"],
        envelope_id=provider_transport_request["envelope_id"],
        invocation_id=provider_transport_request["invocation_id"],
        replay_identity=provider_transport_request["replay_identity"],
        task_artifact_path=bounded_task_artifact_path,
        expected_result_artifact_path=expected_result_artifact_path,
    ).to_dict()
    return ConnectorRequest(
        connector_id=identity["connector_id"],
        provider_id=provider_transport_request["provider_id"],
        envelope_id=provider_transport_request["envelope_id"],
        invocation_id=provider_transport_request["invocation_id"],
        transport_id=provider_transport_request["transport_id"],
        replay_identity=provider_transport_request["replay_identity"],
        provider_transport_request=provider_transport_request,
        bounded_task_artifact_path=bounded_task_artifact_path,
        expected_result_artifact_path=expected_result_artifact_path,
        connector_mode=CONNECTOR_MODE_PREPARE_ONLY,
        connector_binding=binding,
    )
