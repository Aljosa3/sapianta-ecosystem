"""Replay-safe governed runtime activation gate session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeActivationGateSession:
    local_runtime_bridge_session_id: str
    activation_authorized: bool
    approved_by: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_activation_gate_id"] = f"RUNTIME-ACTIVATION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_activation_gate_session(*, bridge_output: dict, activation_authorized: bool, approved_by: str) -> RuntimeActivationGateSession:
    return RuntimeActivationGateSession(
        bridge_output["local_runtime_bridge_session"]["local_runtime_bridge_session_id"],
        activation_authorized,
        approved_by,
    )


def validate_runtime_activation_gate_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeActivationGateSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_activation_gate_session", "reason": "must be object"}]}
    errors = []
    for field in ("runtime_activation_gate_id", "local_runtime_bridge_session_id", "approved_by"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime activation field missing"})
    if value.get("activation_authorized") is not True:
        errors.append({"field": "activation_authorized", "reason": "explicit runtime activation authorization required"})
    if value.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "runtime activation must be human-approved"})
    return {"valid": not errors, "errors": errors}
