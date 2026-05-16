"""Governed local runtime bridge response envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalRuntimeBridgeResponse:
    local_runtime_bridge_session_id: str
    runtime_transport_bridge_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "local_runtime_bridge_session_id": self.local_runtime_bridge_session_id,
            "runtime_transport_bridge_id": self.runtime_transport_bridge_id,
            "response_return_id": self.response_return_id,
            "bridge_status": "LOCAL_RUNTIME_BRIDGE_RESPONSE_EMITTED",
        }


def create_local_runtime_bridge_response(*, binding: dict) -> LocalRuntimeBridgeResponse:
    return LocalRuntimeBridgeResponse(binding["local_runtime_bridge_session_id"], binding["runtime_transport_bridge_id"], binding["response_return_id"])
