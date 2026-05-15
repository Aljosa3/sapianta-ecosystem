"""Runtime serving attachment request."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeServingRequest:
    runtime_serving_session_id: str
    session_runtime_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_runtime_serving_request(*, serving_session: dict) -> RuntimeServingRequest:
    return RuntimeServingRequest(serving_session["runtime_serving_session_id"], serving_session["session_runtime_id"])
