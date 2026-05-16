"""Governed runtime delivery finalization response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeDeliveryFinalizationResponse:
    runtime_delivery_finalization_id: str
    result_capture_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "runtime_delivery_finalization_id": self.runtime_delivery_finalization_id,
            "result_capture_id": self.result_capture_id,
            "response_return_id": self.response_return_id,
            "finalization_status": "RUNTIME_DELIVERY_FINALIZATION_CLOSED",
        }


def create_runtime_delivery_finalization_response(*, binding: dict) -> RuntimeDeliveryFinalizationResponse:
    return RuntimeDeliveryFinalizationResponse(binding["runtime_delivery_finalization_id"], binding["result_capture_id"], binding["response_return_id"])
