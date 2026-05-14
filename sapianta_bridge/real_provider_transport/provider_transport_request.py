"""Explicit provider transport request artifact."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.active_invocation.invocation_binding import invocation_identity

from .provider_transport_binding import create_provider_transport_binding


@dataclass(frozen=True)
class ProviderTransportRequest:
    transport_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    replay_identity: str
    bounded_task_payload: dict[str, Any]
    authority_scope: tuple[str, ...]
    workspace_scope: dict[str, Any]
    validation_requirements: tuple[str, ...]
    transport_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "transport_id": self.transport_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
            "bounded_task_payload": self.bounded_task_payload,
            "authority_scope": list(self.authority_scope),
            "workspace_scope": self.workspace_scope,
            "validation_requirements": list(self.validation_requirements),
            "transport_binding": self.transport_binding,
            "transport_artifact_is_execution_authority": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "real_external_api_call_present": False,
            "shell_execution_present": False,
            "replay_safe": True,
        }


def create_provider_transport_request(envelope: dict[str, Any]) -> ProviderTransportRequest:
    invocation_id = invocation_identity(
        envelope_id=envelope["envelope_id"],
        provider_id=envelope["provider_id"],
        replay_identity=envelope["replay_identity"],
    )
    binding = create_provider_transport_binding(
        provider_id=envelope["provider_id"],
        envelope_id=envelope["envelope_id"],
        invocation_id=invocation_id,
        replay_identity=envelope["replay_identity"],
    ).to_dict()
    return ProviderTransportRequest(
        transport_id=binding["transport_id"],
        provider_id=envelope["provider_id"],
        envelope_id=envelope["envelope_id"],
        invocation_id=invocation_id,
        replay_identity=envelope["replay_identity"],
        bounded_task_payload={
            "allowed_actions": list(envelope.get("allowed_actions", [])),
            "forbidden_actions": list(envelope.get("forbidden_actions", [])),
            "constraints": list(envelope.get("constraints", [])),
            "human_approval_required": envelope.get("human_approval_required", False),
        },
        authority_scope=tuple(envelope["authority_scope"]),
        workspace_scope=envelope["workspace_scope"],
        validation_requirements=tuple(envelope["validation_requirements"]),
        transport_binding=binding,
    )
