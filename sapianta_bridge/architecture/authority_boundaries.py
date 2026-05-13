"""Authority boundary rules for AGOL layers."""

from __future__ import annotations

from typing import Any


AUTHORITY_ACTIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "INTERACTION_LAYER": {
        "allowed": ("proposal_generation", "interpretation", "explanation", "user_communication"),
        "forbidden": (
            "direct_execution",
            "direct_filesystem_mutation",
            "governance_override",
            "certification",
            "silent_task_execution",
            "self_promote_authority",
        ),
    },
    "GOVERNANCE_LAYER": {
        "allowed": ("allow", "block", "escalate", "constrain_execution"),
        "forbidden": (
            "direct_execution",
            "direct_code_mutation",
            "hidden_orchestration",
            "silent_approval_bypass",
            "self_promote_authority",
        ),
    },
    "EXECUTION_LAYER": {
        "allowed": ("bounded_execution", "patch_generation", "test_generation", "artifact_creation"),
        "forbidden": (
            "self_authorize",
            "governance_modification",
            "approval_override",
            "policy_mutation",
            "autonomous_task_generation",
            "replay_mutation",
            "self_promote_authority",
        ),
    },
    "VALIDATION_LAYER": {
        "allowed": ("certify", "reject", "produce_evidence", "verify_determinism"),
        "forbidden": (
            "execution_planning",
            "hidden_repair",
            "silent_mutation",
            "approval_override",
            "silent_execution_retry",
            "self_promote_authority",
        ),
    },
    "REFLECTION_LAYER": {
        "allowed": ("advisory_reasoning", "explanation", "next_step_proposals"),
        "forbidden": (
            "execution",
            "task_enqueueing",
            "hidden_orchestration",
            "governance_mutation",
            "autonomous_escalation",
            "self_promote_authority",
        ),
    },
}


def can_perform(layer: str, action: str) -> bool:
    rules = AUTHORITY_ACTIONS.get(layer)
    if rules is None:
        return False
    return action in rules["allowed"] and action not in rules["forbidden"]


def validate_authority_request(layer: str, action: str) -> dict[str, Any]:
    rules = AUTHORITY_ACTIONS.get(layer)
    if rules is None:
        return {
            "allowed": False,
            "errors": [{"field": "layer", "reason": "unknown layer"}],
            "required_state": "BLOCKED",
        }
    if action in rules["forbidden"]:
        return {
            "allowed": False,
            "errors": [{"field": "action", "reason": "forbidden authority for layer"}],
            "required_state": "BLOCKED",
        }
    if action not in rules["allowed"]:
        return {
            "allowed": False,
            "errors": [{"field": "action", "reason": "undefined authority cannot be inherited"}],
            "required_state": "BLOCKED",
        }
    return {"allowed": True, "errors": [], "required_state": "ALLOWED"}


def authority_boundary_matrix() -> dict[str, Any]:
    return {
        layer: {
            "allowed": list(rules["allowed"]),
            "forbidden": list(rules["forbidden"]),
            "undefined_authority_policy": "BLOCK",
        }
        for layer, rules in AUTHORITY_ACTIONS.items()
    }
