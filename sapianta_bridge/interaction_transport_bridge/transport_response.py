"""Normalized governed interaction transport response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TransportResponse:
    transport_session_id: str
    transport_state: str
    normalized_result: dict[str, Any]
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transport_session_id": self.transport_session_id,
            "transport_state": self.transport_state,
            "normalized_result": self.normalized_result,
            "replay_identity": self.replay_identity,
            "orchestration_present": False,
            "retry_present": False,
            "fallback_present": False,
            "routing_present": False,
            "autonomous_continuation_present": False,
            "replay_safe": True,
        }


def create_transport_response(*, transport_session: dict[str, Any], normalized_result: dict[str, Any]) -> TransportResponse:
    return TransportResponse(
        transport_session_id=transport_session["transport_session_id"],
        transport_state="RESULT_RETURNED",
        normalized_result=normalized_result,
        replay_identity=normalized_result["replay_identity"],
    )


def validate_transport_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, TransportResponse) else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_response", "reason": "must be object"}]}
    for field in ("transport_session_id", "transport_state", "replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "transport response field must be non-empty"})
    if not isinstance(value.get("normalized_result"), dict):
        errors.append({"field": "normalized_result", "reason": "transport response requires normalized result"})
    for field in ("orchestration_present", "retry_present", "fallback_present", "routing_present", "autonomous_continuation_present"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "transport response contains forbidden behavior"})
    return {"valid": not errors, "errors": errors}
