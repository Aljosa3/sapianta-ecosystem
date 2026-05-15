"""Human-centric deterministic interaction response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InteractionResponse:
    interaction_session_id: str
    current_state: str
    execution_phases: list[str]
    provider_id: str
    envelope_id: str
    invocation_id: str
    execution_gate_id: str
    governed_session_id: str
    result_payload: dict[str, Any]
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "interaction_session_id": self.interaction_session_id,
            "current_state": self.current_state,
            "execution_phases": self.execution_phases,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "execution_gate_id": self.execution_gate_id,
            "governed_session_id": self.governed_session_id,
            "result_payload": self.result_payload,
            "replay_identity": self.replay_identity,
            "autonomous_continuation_present": False,
            "orchestration_present": False,
            "retry_present": False,
            "routing_present": False,
            "replay_safe": True,
        }


def create_interaction_response(*, binding: dict[str, Any], states: list[str], bridge_output: dict[str, Any]) -> InteractionResponse:
    return InteractionResponse(
        interaction_session_id=binding["interaction_session_id"],
        current_state=states[-1],
        execution_phases=states,
        provider_id=binding["provider_id"],
        envelope_id=binding["envelope_id"],
        invocation_id=binding["invocation_id"],
        execution_gate_id=binding["execution_gate_id"],
        governed_session_id=binding["governed_session_id"],
        result_payload=bridge_output["bridge_response"]["interpretation_ready_payload"],
        replay_identity=binding["replay_identity"],
    )


def validate_interaction_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, InteractionResponse) else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "interaction_response", "reason": "must be an object"}]}
    for field in ("interaction_session_id", "current_state", "provider_id", "envelope_id", "invocation_id", "execution_gate_id", "governed_session_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "interaction response field must be non-empty"})
    payload = value.get("result_payload")
    if not isinstance(payload, dict) or payload.get("interpretation_ready") is not True:
        errors.append({"field": "result_payload", "reason": "result payload must be interpretation-ready"})
    if isinstance(payload, dict):
        for field in ("provider_id", "envelope_id", "invocation_id", "replay_identity"):
            if value.get(field) != payload.get(field):
                errors.append({"field": field, "reason": "interaction response lineage mismatch"})
    for field in ("autonomous_continuation_present", "orchestration_present", "retry_present", "routing_present"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "interaction response contains forbidden behavior"})
    return {"valid": not errors, "errors": errors}
