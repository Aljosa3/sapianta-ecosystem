"""Replay-safe governed local runtime bridge session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LocalRuntimeBridgeSession:
    execution_relay_session_id: str
    runtime_transport_bridge_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["local_runtime_bridge_session_id"] = f"LOCAL-RUNTIME-BRIDGE-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_local_runtime_bridge_session(*, relay_output: dict, runtime_transport_bridge_id: str) -> LocalRuntimeBridgeSession:
    return LocalRuntimeBridgeSession(relay_output["execution_relay_session"]["execution_relay_session_id"], runtime_transport_bridge_id)


def validate_local_runtime_bridge_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, LocalRuntimeBridgeSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "local_runtime_bridge_session", "reason": "must be object"}]}
    errors = []
    for field in ("local_runtime_bridge_session_id", "execution_relay_session_id", "runtime_transport_bridge_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "local runtime bridge field missing"})
    return {"valid": not errors, "errors": errors}
