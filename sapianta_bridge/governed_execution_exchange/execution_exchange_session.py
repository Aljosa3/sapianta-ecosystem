"""Replay-safe governed execution exchange session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class ExecutionExchangeSession:
    live_request_ingestion_session_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["execution_exchange_session_id"] = f"EXECUTION-EXCHANGE-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_execution_exchange_session(*, ingestion_output: dict) -> ExecutionExchangeSession:
    return ExecutionExchangeSession(ingestion_output["live_request_ingestion_session"]["live_request_ingestion_session_id"])


def validate_execution_exchange_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, ExecutionExchangeSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_exchange_session", "reason": "must be object"}]}
    errors = []
    for field in ("execution_exchange_session_id", "live_request_ingestion_session_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "execution exchange field missing"})
    return {"valid": not errors, "errors": errors}
