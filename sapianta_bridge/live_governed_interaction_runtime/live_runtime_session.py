"""Deterministic live runtime session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LiveRuntimeSession:
    interaction_loop_session_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {"interaction_loop_session_id": self.interaction_loop_session_id, "replay_identity": self.replay_identity}
        value["live_runtime_session_id"] = f"LIVE-RUNTIME-{stable_hash(value)[:24]}"
        value["hidden_memory_present"] = False
        value["replay_safe"] = True
        return value


def create_live_runtime_session(*, loop_session: dict[str, Any]) -> LiveRuntimeSession:
    return LiveRuntimeSession(loop_session["interaction_session_id"], loop_session["replay_identity"])


def validate_live_runtime_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, LiveRuntimeSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "live_runtime_session", "reason": "must be object"}]}
    for field in ("live_runtime_session_id","interaction_loop_session_id","replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime session field missing"})
    if value.get("hidden_memory_present") is not False:
        errors.append({"field": "hidden_memory_present", "reason": "hidden memory forbidden"})
    return {"valid": not errors, "errors": errors}
