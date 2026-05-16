"""Governed runtime delivery finalization request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeDeliveryFinalizationRequest:
    runtime_delivery_finalization_id: str
    runtime_execution_commit_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_runtime_delivery_finalization_request(*, finalization_session: dict) -> RuntimeDeliveryFinalizationRequest:
    return RuntimeDeliveryFinalizationRequest(
        finalization_session["runtime_delivery_finalization_id"],
        finalization_session["runtime_execution_commit_id"],
    )
