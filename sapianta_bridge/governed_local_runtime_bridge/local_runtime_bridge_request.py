"""Governed local runtime bridge request envelope."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalRuntimeBridgeRequest:
    local_runtime_bridge_session_id: str
    execution_relay_session_id: str
    runtime_transport_bridge_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_local_runtime_bridge_request(*, bridge_session: dict) -> LocalRuntimeBridgeRequest:
    return LocalRuntimeBridgeRequest(
        bridge_session["local_runtime_bridge_session_id"],
        bridge_session["execution_relay_session_id"],
        bridge_session["runtime_transport_bridge_id"],
    )
