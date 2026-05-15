"""Replay-safe governed live request ingestion session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LiveRequestIngestionSession:
    serving_gateway_session_id: str
    request_activation_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["live_request_ingestion_session_id"] = f"LIVE-REQUEST-INGESTION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_live_request_ingestion_session(*, gateway_output: dict, request_activation_id: str) -> LiveRequestIngestionSession:
    return LiveRequestIngestionSession(gateway_output["serving_gateway_session"]["serving_gateway_session_id"], request_activation_id)


def validate_live_request_ingestion_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, LiveRequestIngestionSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "live_request_ingestion_session", "reason": "must be object"}]}
    errors = []
    for field in ("live_request_ingestion_session_id", "serving_gateway_session_id", "request_activation_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "live ingestion field missing"})
    return {"valid": not errors, "errors": errors}
