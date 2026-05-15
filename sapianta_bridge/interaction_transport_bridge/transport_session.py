"""Deterministic interaction transport session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class TransportSession:
    interaction_session_id: str
    governed_session_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "interaction_session_id": self.interaction_session_id,
            "governed_session_id": self.governed_session_id,
            "replay_identity": self.replay_identity,
        }
        value["transport_session_id"] = f"TRANSPORT-SESSION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        value["immutable"] = True
        return value


def create_transport_session(*, interaction_response: dict[str, Any]) -> TransportSession:
    return TransportSession(
        interaction_session_id=interaction_response["interaction_session_id"],
        governed_session_id=interaction_response["governed_session_id"],
        replay_identity=interaction_response["replay_identity"],
    )


def validate_transport_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, TransportSession) else session
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_session", "reason": "must be object"}]}
    for field in ("transport_session_id", "interaction_session_id", "governed_session_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "transport session field must be non-empty"})
    if not errors:
        payload = {field: value[field] for field in ("interaction_session_id", "governed_session_id", "replay_identity")}
        if value["transport_session_id"] != f"TRANSPORT-SESSION-{stable_hash(payload)[:24]}":
            errors.append({"field": "transport_session_id", "reason": "transport session identity mismatch"})
    return {"valid": not errors, "errors": errors}
