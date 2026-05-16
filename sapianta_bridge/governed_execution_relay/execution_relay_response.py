"""Governed execution relay response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionRelayResponse:
    execution_relay_session_id: str
    stdout_relay_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "execution_relay_session_id": self.execution_relay_session_id,
            "stdout_relay_id": self.stdout_relay_id,
            "response_return_id": self.response_return_id,
            "relay_status": "EXECUTION_RELAY_RESPONSE_EMITTED",
        }


def create_execution_relay_response(*, binding: dict) -> ExecutionRelayResponse:
    return ExecutionRelayResponse(binding["execution_relay_session_id"], binding["stdout_relay_id"], binding["response_return_id"])
