"""Persistent governed runtime session identity."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class SessionRuntimeSession:
    interaction_loop_session_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {"interaction_loop_session_id": self.interaction_loop_session_id}
        value["session_runtime_id"] = f"SESSION-RUNTIME-{stable_hash(value)[:24]}"
        value["persistent_across_turns"] = True
        value["replay_safe"] = True
        return value


def create_session_runtime_session(*, interaction_loop_session_id: str) -> SessionRuntimeSession:
    return SessionRuntimeSession(interaction_loop_session_id)


def validate_session_runtime_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, SessionRuntimeSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "session_runtime", "reason": "must be object"}]}
    for field in ("session_runtime_id","interaction_loop_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "session runtime field missing"})
    return {"valid": not errors, "errors": errors}
