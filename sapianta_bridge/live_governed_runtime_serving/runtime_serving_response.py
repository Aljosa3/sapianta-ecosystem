"""Serving response."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeServingResponse:
    runtime_serving_session_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {"runtime_serving_session_id": self.runtime_serving_session_id, "response_return_id": self.response_return_id, "serving_status": "RUNTIME_SERVING_RESPONSE_EMITTED"}


def create_runtime_serving_response(*, binding: dict) -> RuntimeServingResponse:
    return RuntimeServingResponse(binding["runtime_serving_session_id"], binding["response_return_id"])
