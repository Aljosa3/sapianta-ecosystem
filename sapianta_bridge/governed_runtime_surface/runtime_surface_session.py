"""Replay-safe governed runtime surface session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeSurfaceSession:
    runtime_delivery_finalization_id: str
    surface_ingress_id: str
    surface_egress_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_surface_session_id"] = f"RUNTIME-SURFACE-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_surface_session(*, finalization_output: dict, surface_ingress_id: str, surface_egress_id: str) -> RuntimeSurfaceSession:
    return RuntimeSurfaceSession(finalization_output["runtime_delivery_finalization_session"]["runtime_delivery_finalization_id"], surface_ingress_id, surface_egress_id)


def validate_runtime_surface_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeSurfaceSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_surface_session", "reason": "must be object"}]}
    errors = []
    for field in ("runtime_surface_session_id", "runtime_delivery_finalization_id", "surface_ingress_id", "surface_egress_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime surface field missing"})
    return {"valid": not errors, "errors": errors}
