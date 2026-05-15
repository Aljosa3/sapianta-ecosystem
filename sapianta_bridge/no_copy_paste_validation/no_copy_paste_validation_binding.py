"""Replay-visible validation binding."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class ValidationBinding:
    ingress_artifact_id: str
    execution_gate_id: str
    provider_invocation_id: str
    bounded_runtime_id: str
    result_capture_id: str
    response_return_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["binding_sha256"] = stable_hash(value)
        value["replay_safe"] = True
        return value


def capture_id_for(gate_id: str) -> str:
    return f"CAPTURE-{stable_hash({'execution_gate_id': gate_id})[:24]}"


def validate_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, ValidationBinding) else binding
    errors = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "binding", "reason": "must be object"}]}
    for field in ("ingress_artifact_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id","replay_identity"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append({"field": field, "reason": "binding field must be non-empty"})
    return {"valid": not errors, "errors": errors}
