"""Canonical AGOL layer definitions.

This module is declarative. It defines authority separation without executing,
routing, optimizing, or mutating runtime behavior.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


STABILIZATION_BASELINE = "STABILIZATION_CERTIFICATION_EPOCH_V1"

LAYER_ORDER = (
    "INTERACTION_LAYER",
    "GOVERNANCE_LAYER",
    "EXECUTION_LAYER",
    "VALIDATION_LAYER",
    "REFLECTION_LAYER",
)

LAYER_DEFINITIONS: dict[str, dict[str, Any]] = {
    "INTERACTION_LAYER": {
        "responsibilities": (
            "receive_user_intent",
            "create_structured_proposal",
            "explain_outcomes",
            "summarize_replay_evidence",
            "provide_strategic_reasoning",
        ),
        "allowed": (
            "proposal_generation",
            "interpretation",
            "explanation",
            "user_communication",
        ),
        "forbidden": (
            "direct_execution",
            "direct_filesystem_mutation",
            "governance_override",
            "certification",
            "silent_task_execution",
        ),
        "authority": "NONE_OVER_EXECUTION",
    },
    "GOVERNANCE_LAYER": {
        "responsibilities": (
            "intent_classification",
            "admissibility_analysis",
            "risk_classification",
            "execution_envelope_creation",
            "escalation_decisions",
            "approval_requirements",
            "replay_identity_creation",
        ),
        "allowed": (
            "allow",
            "block",
            "escalate",
            "constrain_execution",
        ),
        "forbidden": (
            "direct_execution",
            "direct_code_mutation",
            "hidden_orchestration",
            "silent_approval_bypass",
        ),
        "authority": "CONTROLS_EXECUTION_ADMISSIBILITY",
    },
    "EXECUTION_LAYER": {
        "responsibilities": (
            "execute_bounded_execution_envelope",
            "generate_artifacts",
            "return_normalized_results",
        ),
        "allowed": (
            "bounded_execution",
            "patch_generation",
            "test_generation",
            "artifact_creation",
        ),
        "forbidden": (
            "governance_modification",
            "approval_override",
            "policy_mutation",
            "autonomous_task_generation",
            "replay_mutation",
        ),
        "authority": "ONLY_INSIDE_PROVIDED_ENVELOPE",
    },
    "VALIDATION_LAYER": {
        "responsibilities": (
            "guardian_validation",
            "test_execution",
            "policy_validation",
            "certification",
            "replay_safe_verification",
        ),
        "allowed": (
            "certify",
            "reject",
            "produce_evidence",
            "verify_determinism",
        ),
        "forbidden": (
            "execution_planning",
            "hidden_repair",
            "silent_mutation",
            "approval_override",
        ),
        "authority": "DETERMINES_ARTIFACT_VALIDITY",
    },
    "REFLECTION_LAYER": {
        "responsibilities": (
            "interpret_evidence",
            "summarize_capability_deltas",
            "summarize_governance_risk",
            "propose_future_directions",
        ),
        "allowed": (
            "advisory_reasoning",
            "explanation",
            "next_step_proposals",
        ),
        "forbidden": (
            "execution",
            "task_enqueueing",
            "hidden_orchestration",
            "governance_mutation",
            "autonomous_escalation",
        ),
        "authority": "ADVISORY_ONLY",
    },
}

PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS = {
    "providers_replaceable": True,
    "providers_non_authoritative": True,
    "provider_identity_affects_governance_semantics": False,
    "replay_evidence_format_stable_across_providers": True,
    "supported_provider_examples": (
        "codex",
        "claude_code",
        "gemini",
        "local_executor",
        "deterministic_symbolic_executor",
    ),
}


def list_layers() -> tuple[str, ...]:
    return LAYER_ORDER


def get_layer_definition(layer: str) -> dict[str, Any]:
    if layer not in LAYER_DEFINITIONS:
        raise ValueError(f"unknown layer: {layer}")
    return deepcopy(LAYER_DEFINITIONS[layer])


def canonical_layer_model() -> dict[str, Any]:
    return {
        "model_id": "AGOL_LAYER_SEPARATION_MODEL_V1",
        "stabilization_baseline": STABILIZATION_BASELINE,
        "agol_role": "GOVERNANCE_CONTROL_PLANE",
        "agol_is_execution_intelligence": False,
        "permanent_invariant": "INTERACTION_LAYER != EXECUTION_LAYER",
        "layers": {layer: get_layer_definition(layer) for layer in LAYER_ORDER},
        "provider_independent_execution": deepcopy(PROVIDER_INDEPENDENT_EXECUTION_SEMANTICS),
    }


def replay_safe_layer_evidence(
    *,
    provider: str = "codex",
    governance_decision: str = "ALLOW",
    risk_class: str = "LOW",
    certification: str = "CERTIFIED",
) -> dict[str, Any]:
    return {
        "interaction_layer": {"proposal_created": True, "execution_authority": False},
        "governance_layer": {
            "decision": governance_decision,
            "risk_class": risk_class,
            "controls_execution_admissibility": True,
        },
        "execution_layer": {
            "provider": provider,
            "bounded_execution": True,
            "provider_authoritative": False,
        },
        "validation_layer": {
            "certification": certification,
            "determines_artifact_validity": True,
        },
        "reflection_layer": {
            "advisory_generated": True,
            "allowed_to_execute_automatically": False,
        },
    }
