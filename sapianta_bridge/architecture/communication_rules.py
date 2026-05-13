"""Inter-layer communication rules for AGOL."""

from __future__ import annotations

from typing import Any


ALLOWED_COMMUNICATION_FLOW = (
    ("USER", "INTERACTION_LAYER"),
    ("INTERACTION_LAYER", "GOVERNANCE_LAYER"),
    ("GOVERNANCE_LAYER", "EXECUTION_LAYER"),
    ("EXECUTION_LAYER", "VALIDATION_LAYER"),
    ("VALIDATION_LAYER", "REFLECTION_LAYER"),
    ("REFLECTION_LAYER", "INTERACTION_LAYER"),
)

FORBIDDEN_COMMUNICATION = {
    ("EXECUTION_LAYER", "USER"): "execution cannot communicate directly with user",
    ("REFLECTION_LAYER", "EXECUTION_LAYER"): "reflection cannot trigger execution",
    ("EXECUTION_LAYER", "GOVERNANCE_LAYER"): "execution cannot mutate governance",
    ("VALIDATION_LAYER", "EXECUTION_LAYER"): "validation cannot silently retry execution",
    ("INTERACTION_LAYER", "EXECUTION_LAYER"): "interaction cannot bypass governance",
    ("GOVERNANCE_LAYER", "VALIDATION_LAYER"): "governance cannot bypass execution evidence",
}


def validate_communication(source: str, target: str) -> dict[str, Any]:
    edge = (source, target)
    if edge in ALLOWED_COMMUNICATION_FLOW:
        return {"allowed": True, "errors": [], "required_state": "ALLOWED"}
    if edge in FORBIDDEN_COMMUNICATION:
        return {
            "allowed": False,
            "errors": [{"field": "communication", "reason": FORBIDDEN_COMMUNICATION[edge]}],
            "required_state": "BLOCKED",
        }
    return {
        "allowed": False,
        "errors": [{"field": "communication", "reason": "undefined communication path"}],
        "required_state": "BLOCKED",
    }


def communication_rules() -> dict[str, Any]:
    return {
        "allowed_flow": [
            {"source": source, "target": target} for source, target in ALLOWED_COMMUNICATION_FLOW
        ],
        "forbidden_flow": [
            {"source": source, "target": target, "reason": reason}
            for (source, target), reason in sorted(FORBIDDEN_COMMUNICATION.items())
        ],
        "undefined_flow_policy": "BLOCK",
    }
