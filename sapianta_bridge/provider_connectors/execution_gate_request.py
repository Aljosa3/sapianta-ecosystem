"""Human-approved execution gate request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .execution_gate_binding import create_execution_gate_binding
from .execution_gate_identity import create_execution_gate_identity


EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK = "CAPTURE_CONNECTOR_TASK"
EXECUTION_GATE_OPERATION_CODEX_CLI_RUN = "CODEX_CLI_RUN"


@dataclass(frozen=True)
class ExecutionGateRequest:
    execution_gate_id: str
    connector_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    transport_id: str
    replay_identity: str
    connector_request: dict[str, Any]
    execution_authorized: bool
    approved_by: str
    workspace_path: str
    timeout_seconds: int
    operation: str
    execution_gate_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_gate_id": self.execution_gate_id,
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "transport_id": self.transport_id,
            "replay_identity": self.replay_identity,
            "connector_request": self.connector_request,
            "execution_authorized": self.execution_authorized,
            "approved_by": self.approved_by,
            "workspace_path": self.workspace_path,
            "timeout_seconds": self.timeout_seconds,
            "operation": self.operation,
            "execution_gate_binding": self.execution_gate_binding,
            "prepared_artifact_is_execution_authority": False,
            "arbitrary_command_execution_present": False,
            "shell_execution_present": False,
            "network_execution_present": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_execution_present": False,
            "background_execution_present": False,
            "concurrent_execution_present": False,
            "memory_mutation_present": False,
            "replay_safe": True,
        }


def create_execution_gate_request(
    *,
    connector_request: dict[str, Any],
    execution_authorized: bool,
    approved_by: str,
    workspace_path: str,
    timeout_seconds: int,
    operation: str = EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK,
) -> ExecutionGateRequest:
    identity = create_execution_gate_identity(connector_request=connector_request).to_dict()
    binding = create_execution_gate_binding(
        execution_gate_id=identity["execution_gate_id"],
        connector_request=connector_request,
        workspace_path=workspace_path,
        timeout_seconds=timeout_seconds,
        operation=operation,
    ).to_dict()
    return ExecutionGateRequest(
        execution_gate_id=identity["execution_gate_id"],
        connector_id=connector_request["connector_id"],
        provider_id=connector_request["provider_id"],
        envelope_id=connector_request["envelope_id"],
        invocation_id=connector_request["invocation_id"],
        transport_id=connector_request["transport_id"],
        replay_identity=connector_request["replay_identity"],
        connector_request=connector_request,
        execution_authorized=execution_authorized,
        approved_by=approved_by,
        workspace_path=workspace_path,
        timeout_seconds=timeout_seconds,
        operation=operation,
        execution_gate_binding=binding,
    )
