"""Continuously attachable serving session identity."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeServingSession:
    session_runtime_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {"session_runtime_id": self.session_runtime_id}
        value["runtime_serving_session_id"] = f"RUNTIME-SERVING-{stable_hash(value)[:24]}"
        value["continuously_attachable"] = True
        value["replay_safe"] = True
        return value


def create_runtime_serving_session(*, session_runtime: dict) -> RuntimeServingSession:
    return RuntimeServingSession(session_runtime["session_runtime_id"])


def validate_runtime_serving_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeServingSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "serving_session", "reason": "must be object"}]}
    for field in ("runtime_serving_session_id","session_runtime_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "serving session field missing"})
    return {"valid": not errors, "errors": errors}
