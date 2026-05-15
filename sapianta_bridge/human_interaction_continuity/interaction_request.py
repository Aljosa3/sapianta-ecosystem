"""Human-facing governed interaction request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .interaction_session import stable_hash


@dataclass(frozen=True)
class InteractionRequest:
    human_input: str
    conversation_id: str
    execution_gate_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "human_input": self.human_input,
            "conversation_id": self.conversation_id,
            "execution_gate_id": self.execution_gate_id,
            "replay_identity": self.replay_identity,
            "orchestration_requested": False,
            "autonomous_continuation_requested": False,
            "retry_requested": False,
            "routing_requested": False,
        }
        value["interaction_request_id"] = f"INTERACTION-REQUEST-{stable_hash(value)[:16]}"
        value["replay_safe"] = True
        return value


def create_interaction_request(human_input: str, *, conversation_id: str, execution_gate_id: str, replay_identity: str) -> InteractionRequest:
    return InteractionRequest(human_input, conversation_id, execution_gate_id, replay_identity)


def validate_interaction_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, InteractionRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "interaction_request", "reason": "must be an object"}]}
    for field in ("human_input", "conversation_id", "execution_gate_id", "replay_identity", "interaction_request_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "interaction request field must be non-empty"})
    for field in ("orchestration_requested", "autonomous_continuation_requested", "retry_requested", "routing_requested"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "interaction request contains forbidden behavior"})
    if not errors:
        payload = dict(value)
        payload.pop("interaction_request_id")
        payload.pop("replay_safe")
        if value["interaction_request_id"] != f"INTERACTION-REQUEST-{stable_hash(payload)[:16]}":
            errors.append({"field": "interaction_request_id", "reason": "interaction request identity mismatch"})
    return {"valid": not errors, "errors": errors}
