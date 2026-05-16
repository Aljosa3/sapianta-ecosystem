"""Replay-safe governed runtime execution commit session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeExecutionCommitSession:
    runtime_activation_gate_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_execution_commit_id"] = f"RUNTIME-EXECUTION-COMMIT-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_execution_commit_session(*, activation_output: dict) -> RuntimeExecutionCommitSession:
    return RuntimeExecutionCommitSession(activation_output["runtime_activation_gate_session"]["runtime_activation_gate_id"])


def validate_runtime_execution_commit_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeExecutionCommitSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_execution_commit_session", "reason": "must be object"}]}
    errors = []
    for field in ("runtime_execution_commit_id", "runtime_activation_gate_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime execution commit field missing"})
    return {"valid": not errors, "errors": errors}
