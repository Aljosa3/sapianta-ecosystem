"""Deterministic local ingress response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LocalIngressResponse:
    ingress_session_id: str
    normalized_response: dict[str, Any]
    lineage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingress_session_id": self.ingress_session_id,
            "normalized_response": self.normalized_response,
            "lineage": self.lineage,
            "provider_output_rewritten": False,
            "execution_success_fabricated": False,
            "interaction_history_synthesized": False,
            "replay_safe": True,
        }


def create_ingress_response(*, ingress_session: dict[str, Any], transport_output: dict[str, Any], binding: dict[str, Any]) -> LocalIngressResponse:
    return LocalIngressResponse(ingress_session["ingress_session_id"], transport_output["normalized_result"], binding)


def validate_ingress_response(response: Any) -> dict[str, Any]:
    value = response.to_dict() if isinstance(response, LocalIngressResponse) else response
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_response", "reason": "must be object"}]}
    if not isinstance(value.get("normalized_response"), dict):
        errors.append({"field": "normalized_response", "reason": "normalized response required"})
    if not isinstance(value.get("lineage"), dict):
        errors.append({"field": "lineage", "reason": "lineage required"})
    for field in ("provider_output_rewritten", "execution_success_fabricated", "interaction_history_synthesized"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "egress response contains forbidden mutation"})
    return {"valid": not errors, "errors": errors}
