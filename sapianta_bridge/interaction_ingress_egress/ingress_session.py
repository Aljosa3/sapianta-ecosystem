"""Local ingress session identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LocalIngressSession:
    ingress_artifact_id: str
    transport_session_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {"ingress_artifact_id": self.ingress_artifact_id, "transport_session_id": self.transport_session_id}
        value["ingress_session_id"] = f"LOCAL-INGRESS-SESSION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_ingress_session(*, ingress_artifact: dict[str, Any], transport_session_id: str) -> LocalIngressSession:
    return LocalIngressSession(ingress_artifact["ingress_artifact_id"], transport_session_id)


def validate_ingress_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, LocalIngressSession) else session
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_session", "reason": "must be object"}]}
    for field in ("ingress_artifact_id", "transport_session_id", "ingress_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "ingress session field must be non-empty"})
    return {"valid": not errors, "errors": errors}
