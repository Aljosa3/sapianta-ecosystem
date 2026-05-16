"""Replay-safe governed execution relay session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class ExecutionRelaySession:
    execution_exchange_session_id: str
    stdin_relay_id: str
    stdout_relay_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["execution_relay_session_id"] = f"EXECUTION-RELAY-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_execution_relay_session(*, exchange_output: dict, terminal_output: dict) -> ExecutionRelaySession:
    terminal_binding = terminal_output["terminal_attachment_binding"]
    return ExecutionRelaySession(
        exchange_output["execution_exchange_session"]["execution_exchange_session_id"],
        terminal_binding["stdin_binding_id"],
        terminal_binding["stdout_binding_id"],
    )


def validate_execution_relay_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, ExecutionRelaySession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "execution_relay_session", "reason": "must be object"}]}
    errors = []
    for field in ("execution_relay_session_id", "execution_exchange_session_id", "stdin_relay_id", "stdout_relay_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "execution relay field missing"})
    return {"valid": not errors, "errors": errors}
