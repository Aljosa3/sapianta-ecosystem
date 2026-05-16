"""Governed execution relay request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionRelayRequest:
    execution_relay_session_id: str
    execution_exchange_session_id: str
    stdin_relay_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_execution_relay_request(*, relay_session: dict) -> ExecutionRelayRequest:
    return ExecutionRelayRequest(
        relay_session["execution_relay_session_id"],
        relay_session["execution_exchange_session_id"],
        relay_session["stdin_relay_id"],
    )
