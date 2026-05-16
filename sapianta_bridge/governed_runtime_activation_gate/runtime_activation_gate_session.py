"""Replay-safe governed runtime activation gate session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeActivationGateSession:
    activation_source_id: str
    activation_source_kind: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_activation_gate_id"] = f"RUNTIME-ACTIVATION-GATE-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_activation_gate_session(
    *,
    entrypoint_output: dict | None = None,
    bridge_output: dict | None = None,
) -> RuntimeActivationGateSession:
    if entrypoint_output is not None:
        return RuntimeActivationGateSession(
            entrypoint_output["activation"]["operational_runtime_entrypoint_id"],
            "operational_entrypoint",
        )
    if bridge_output is not None:
        return RuntimeActivationGateSession(
            bridge_output["local_runtime_bridge_session"]["local_runtime_bridge_session_id"],
            "legacy_local_runtime_bridge",
        )
    raise KeyError("activation source missing")


def validate_runtime_activation_gate_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeActivationGateSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_activation_gate_session", "reason": "must be object"}]}
    errors = []
    for field in ("runtime_activation_gate_id", "activation_source_id", "activation_source_kind"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime activation field missing"})
    return {"valid": not errors, "errors": errors}
