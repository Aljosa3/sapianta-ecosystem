"""Replay-safe terminal attachment session identity."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class TerminalAttachmentSession:
    runtime_serving_session_id: str
    stdin_binding_id: str
    stdout_binding_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "runtime_serving_session_id": self.runtime_serving_session_id,
            "stdin_binding_id": self.stdin_binding_id,
            "stdout_binding_id": self.stdout_binding_id,
        }
        value["terminal_attachment_session_id"] = f"TERMINAL-ATTACHMENT-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_terminal_attachment_session(*, runtime_serving_session: dict, stdin_binding_id: str, stdout_binding_id: str) -> TerminalAttachmentSession:
    return TerminalAttachmentSession(runtime_serving_session["runtime_serving_session_id"], stdin_binding_id, stdout_binding_id)


def validate_terminal_attachment_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, TerminalAttachmentSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "terminal_attachment_session", "reason": "must be object"}]}
    errors = []
    for field in ("terminal_attachment_session_id", "runtime_serving_session_id", "stdin_binding_id", "stdout_binding_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "terminal attachment field missing"})
    return {"valid": not errors, "errors": errors}
