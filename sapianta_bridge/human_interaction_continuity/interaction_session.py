"""Deterministic human interaction session identity."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class InteractionSession:
    conversation_id: str
    request_id: str
    governed_session_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "conversation_id": self.conversation_id,
            "request_id": self.request_id,
            "governed_session_id": self.governed_session_id,
            "replay_identity": self.replay_identity,
        }
        value["interaction_session_id"] = f"INTERACTION-SESSION-{stable_hash(value)[:24]}"
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_interaction_session(*, request: dict[str, Any], governed_session_id: str) -> InteractionSession:
    return InteractionSession(
        conversation_id=request["conversation_id"],
        request_id=request["interaction_request_id"],
        governed_session_id=governed_session_id,
        replay_identity=request["replay_identity"],
    )


def validate_interaction_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, InteractionSession) else session
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "interaction_session", "reason": "must be an object"}]}
    for field in ("conversation_id", "request_id", "governed_session_id", "replay_identity", "interaction_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "interaction session field must be non-empty"})
    if not errors:
        payload = {field: value[field] for field in ("conversation_id", "request_id", "governed_session_id", "replay_identity")}
        if value["interaction_session_id"] != f"INTERACTION-SESSION-{stable_hash(payload)[:24]}":
            errors.append({"field": "interaction_session_id", "reason": "interaction session identity mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "interaction session must be replay-safe"})
    return {"valid": not errors, "errors": errors}
