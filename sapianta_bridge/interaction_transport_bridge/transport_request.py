"""Bounded governed interaction transport request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class TransportRequest:
    transport_session_id: str
    interaction_session_id: str
    governed_session_id: str
    execution_gate_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "transport_session_id": self.transport_session_id,
            "interaction_session_id": self.interaction_session_id,
            "governed_session_id": self.governed_session_id,
            "execution_gate_id": self.execution_gate_id,
            "replay_identity": self.replay_identity,
            "retry_requested": False,
            "routing_requested": False,
            "autonomous_continuation_requested": False,
        }
        value["transport_request_id"] = f"TRANSPORT-REQUEST-{stable_hash(value)[:16]}"
        value["replay_safe"] = True
        return value


def create_transport_request(*, transport_session: dict[str, Any], interaction_response: dict[str, Any]) -> TransportRequest:
    return TransportRequest(
        transport_session_id=transport_session["transport_session_id"],
        interaction_session_id=interaction_response["interaction_session_id"],
        governed_session_id=interaction_response["governed_session_id"],
        execution_gate_id=interaction_response["execution_gate_id"],
        replay_identity=interaction_response["replay_identity"],
    )


def validate_transport_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, TransportRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_request", "reason": "must be object"}]}
    for field in ("transport_request_id", "transport_session_id", "interaction_session_id", "governed_session_id", "execution_gate_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "transport request field must be non-empty"})
    for field in ("retry_requested", "routing_requested", "autonomous_continuation_requested"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "transport request contains forbidden behavior"})
    return {"valid": not errors, "errors": errors}
