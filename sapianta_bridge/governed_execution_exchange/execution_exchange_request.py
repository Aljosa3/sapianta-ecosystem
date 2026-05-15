"""Governed execution exchange request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionExchangeRequest:
    execution_exchange_session_id: str
    live_request_ingestion_session_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_execution_exchange_request(*, exchange_session: dict) -> ExecutionExchangeRequest:
    return ExecutionExchangeRequest(
        exchange_session["execution_exchange_session_id"],
        exchange_session["live_request_ingestion_session_id"],
    )
