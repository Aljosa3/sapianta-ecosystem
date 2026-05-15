"""Deterministic runtime attachment session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeAttachmentSession:
    live_runtime_session_id: str
    interaction_loop_session_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_attachment_session_id"] = f"RUNTIME-ATTACHMENT-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_attachment_session(*, live_runtime_output: dict[str, Any]) -> RuntimeAttachmentSession:
    session = live_runtime_output["live_runtime_session"]
    return RuntimeAttachmentSession(session["live_runtime_session_id"], session["interaction_loop_session_id"])


def validate_runtime_attachment_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeAttachmentSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "attachment_session", "reason": "must be object"}]}
    for field in ("runtime_attachment_session_id","live_runtime_session_id","interaction_loop_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "attachment session lineage missing"})
    return {"valid": not errors, "errors": errors}
