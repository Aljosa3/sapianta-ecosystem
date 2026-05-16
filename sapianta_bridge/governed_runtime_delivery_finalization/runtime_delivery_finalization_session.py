"""Replay-safe governed runtime delivery finalization session."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class RuntimeDeliveryFinalizationSession:
    runtime_execution_commit_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["runtime_delivery_finalization_id"] = f"RUNTIME-DELIVERY-FINALIZATION-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_runtime_delivery_finalization_session(*, commit_output: dict) -> RuntimeDeliveryFinalizationSession:
    return RuntimeDeliveryFinalizationSession(commit_output["runtime_execution_commit_session"]["runtime_execution_commit_id"])


def validate_runtime_delivery_finalization_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, RuntimeDeliveryFinalizationSession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_delivery_finalization_session", "reason": "must be object"}]}
    errors = []
    for field in ("runtime_delivery_finalization_id", "runtime_execution_commit_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "runtime delivery finalization field missing"})
    return {"valid": not errors, "errors": errors}
