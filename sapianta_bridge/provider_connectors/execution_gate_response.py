"""Deterministic execution gate response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


EXECUTION_GATE_RESPONSE_STATUSES = ("SUCCESS", "BLOCKED", "FAILED")
DETERMINISTIC_EXECUTION_STARTED_AT = "1970-01-01T00:00:00Z"
DETERMINISTIC_EXECUTION_ENDED_AT = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class ExecutionGateResponse:
    execution_gate_id: str
    connector_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    transport_id: str
    replay_identity: str
    status: str
    stdout: str
    stderr: str
    exit_code: int
    execution_started_at: str
    execution_ended_at: str
    result_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_gate_id": self.execution_gate_id,
            "connector_id": self.connector_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "transport_id": self.transport_id,
            "replay_identity": self.replay_identity,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_started_at": self.execution_started_at,
            "execution_ended_at": self.execution_ended_at,
            "result_metadata": self.result_metadata,
            "provider_response_is_governance_decision": False,
            "arbitrary_command_execution_present": False,
            "shell_execution_present": False,
            "network_execution_present": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_execution_present": False,
            "replay_safe": True,
        }


def create_execution_gate_response(
    *,
    request: dict[str, Any],
    status: str,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    result_metadata: dict[str, Any] | None = None,
) -> ExecutionGateResponse:
    return ExecutionGateResponse(
        execution_gate_id=request["execution_gate_id"],
        connector_id=request["connector_id"],
        provider_id=request["provider_id"],
        envelope_id=request["envelope_id"],
        invocation_id=request["invocation_id"],
        transport_id=request["transport_id"],
        replay_identity=request["replay_identity"],
        status=status,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        execution_started_at=DETERMINISTIC_EXECUTION_STARTED_AT,
        execution_ended_at=DETERMINISTIC_EXECUTION_ENDED_AT,
        result_metadata=result_metadata or {},
    )
