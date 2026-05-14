"""Transport response wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TRANSPORT_RESPONSE_STATUSES = ("SUCCESS", "FAILED", "BLOCKED", "NEEDS_REVIEW")


@dataclass(frozen=True)
class TransportResponse:
    transport_status: str
    envelope_id: str
    provider_id: str
    replay_identity: str
    runtime_result: dict[str, Any]
    normalized_result: dict[str, Any]
    runtime_evidence: dict[str, Any]
    transport_evidence: dict[str, Any]
    replay_safe: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "transport_status": self.transport_status,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "runtime_result": self.runtime_result,
            "normalized_result": self.normalized_result,
            "runtime_evidence": self.runtime_evidence,
            "transport_evidence": self.transport_evidence,
            "replay_safe": self.replay_safe,
        }


def create_transport_response(
    *,
    request: dict[str, Any],
    runtime_output: dict[str, Any],
    evidence: dict[str, Any],
) -> TransportResponse:
    runtime_result = runtime_output["runtime_result"]
    status = runtime_result["runtime_status"]
    return TransportResponse(
        transport_status=status if status in TRANSPORT_RESPONSE_STATUSES else "NEEDS_REVIEW",
        envelope_id=request["envelope_id"],
        provider_id=request["provider_id"],
        replay_identity=request["replay_identity"],
        runtime_result=runtime_result,
        normalized_result=runtime_result["normalized_result"],
        runtime_evidence=runtime_output["runtime_evidence"],
        transport_evidence=evidence,
        replay_safe=evidence["replay_safe"] is True,
    )


def validate_transport_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, TransportResponse) else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "transport_response", "reason": "transport response must be an object"}],
        }
    if value.get("transport_status") not in TRANSPORT_RESPONSE_STATUSES:
        errors.append({"field": "transport_status", "reason": "unsupported transport status"})
    for field in ("envelope_id", "provider_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "transport response field must be non-empty"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "transport response must be replay-safe"})
    for field in ("runtime_result", "normalized_result", "runtime_evidence", "transport_evidence"):
        if not isinstance(value.get(field), dict):
            errors.append({"field": field, "reason": "transport response field must be an object"})
    return {"valid": not errors, "errors": errors}
