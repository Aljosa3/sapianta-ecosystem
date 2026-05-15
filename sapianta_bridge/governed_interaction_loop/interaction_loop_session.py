"""Replay-safe governed interaction loop session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class InteractionLoopSession:
    conversation_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {"conversation_id": self.conversation_id, "replay_identity": self.replay_identity}
        value["interaction_session_id"] = f"LOOP-SESSION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        value["implicit_memory_present"] = False
        return value


def create_loop_session(*, conversation_id: str, replay_identity: str) -> InteractionLoopSession:
    return InteractionLoopSession(conversation_id, replay_identity)


def validate_loop_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, InteractionLoopSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "loop_session", "reason": "must be object"}]}
    for field in ("conversation_id", "replay_identity", "interaction_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "loop session field must be non-empty"})
    if value.get("implicit_memory_present") is not False:
        errors.append({"field": "implicit_memory_present", "reason": "implicit memory forbidden"})
    return {"valid": not errors, "errors": errors}
