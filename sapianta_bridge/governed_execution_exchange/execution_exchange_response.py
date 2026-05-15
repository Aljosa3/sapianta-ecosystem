"""Governed execution exchange response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionExchangeResponse:
    execution_exchange_session_id: str
    result_capture_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "execution_exchange_session_id": self.execution_exchange_session_id,
            "result_capture_id": self.result_capture_id,
            "response_return_id": self.response_return_id,
            "exchange_status": "EXECUTION_EXCHANGE_RESPONSE_EMITTED",
        }


def create_execution_exchange_response(*, binding: dict) -> ExecutionExchangeResponse:
    return ExecutionExchangeResponse(binding["execution_exchange_session_id"], binding["result_capture_id"], binding["response_return_id"])
