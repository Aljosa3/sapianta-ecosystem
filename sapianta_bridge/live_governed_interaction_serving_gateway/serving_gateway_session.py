"""Replay-safe serving gateway session identity."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class ServingGatewaySession:
    runtime_serving_session_id: str
    terminal_attachment_session_id: str
    ingress_id: str
    egress_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["serving_gateway_session_id"] = f"SERVING-GATEWAY-{stable_hash(value)[:24]}"
        value["replay_safe"] = True
        return value


def create_serving_gateway_session(*, terminal_output: dict, ingress_id: str, egress_id: str) -> ServingGatewaySession:
    binding = terminal_output["terminal_attachment_binding"]
    return ServingGatewaySession(binding["runtime_serving_session_id"], binding["terminal_attachment_session_id"], ingress_id, egress_id)


def validate_serving_gateway_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, ServingGatewaySession) else session
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "serving_gateway_session", "reason": "must be object"}]}
    errors = []
    for field in ("serving_gateway_session_id", "runtime_serving_session_id", "terminal_attachment_session_id", "ingress_id", "egress_id"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "serving gateway field missing"})
    return {"valid": not errors, "errors": errors}
