"""Practical AGOL refinement guidance workflow.

This module integrates adaptive intent-awareness into Product 1 refinement
workflow guidance. It recommends strategy and prompt augmentation only; it does
not execute changes, mutate runtime behavior, or grant redesign authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agol_adaptive_intent import (
    BOUNDED_RESTRUCTURING_MODE,
    CONTINUITY_REFINEMENT_MODE,
    ENTERPRISE_TRUST_MODE,
    MONETIZATION_OPTIMIZATION_MODE,
    OPERATIONAL_CLARITY_MODE,
    PERCEPTUAL_IMPACT_MODE,
    PRIMITIVE_ID as ADAPTIVE_INTENT_PRIMITIVE_ID,
    AdaptiveRefinementAssessment,
    AdaptiveRefinementRequest,
    assess_refinement_intent,
)
from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PRIMITIVE_ID = "AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1"
SCOPE_ID = "PRODUCT_1_REFINEMENT_GUIDANCE_ONLY"
NO_COMMAND: tuple[str, ...] = ()
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/AGOL_ADAPTIVE_INTENT_AWARENESS_V1.md",
    "docs/governance/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1.md",
    "runtime/governance/agol_adaptive_intent.py",
    "runtime/governance/agol_refinement_guidance.py",
    "tests/test_agol_refinement_guidance.py",
)

MODE_DIRECTIONS = {
    CONTINUITY_REFINEMENT_MODE: (
        "Preserve the existing composition and make targeted continuity refinements."
    ),
    BOUNDED_RESTRUCTURING_MODE: (
        "Increase compositional restructuring while preserving governance continuity."
    ),
    PERCEPTUAL_IMPACT_MODE: (
        "Make a visibly stronger refinement move while keeping the current architecture bounded."
    ),
    OPERATIONAL_CLARITY_MODE: (
        "Improve first-read comprehension of bounded execution, replay continuity, and evidence flow."
    ),
    MONETIZATION_OPTIMIZATION_MODE: (
        "Clarify enterprise value, buyer relevance, and trust rationale without startup-style hype."
    ),
    ENTERPRISE_TRUST_MODE: (
        "Strengthen institutional credibility, audit confidence, and governance-native restraint."
    ),
}

MODE_PROMPT_AUGMENTATIONS = {
    CONTINUITY_REFINEMENT_MODE: (
        "Preserve the current structure. Make only targeted refinements that improve continuity "
        "and do not change runtime or governance semantics."
    ),
    BOUNDED_RESTRUCTURING_MODE: (
        "Use bounded restructuring rather than another micro-refinement. Rebalance composition, "
        "spacing, hierarchy, and focal emphasis while preserving AGOL governance continuity, "
        "replay-safe messaging, and runtime semantics."
    ),
    PERCEPTUAL_IMPACT_MODE: (
        "Increase perceptual impact with a clearly visible refinement. Keep the change bounded, "
        "enterprise-grade, and governance-native; do not introduce dashboards, live analytics, "
        "or autonomous authority."
    ),
    OPERATIONAL_CLARITY_MODE: (
        "Prioritize first-time visitor comprehension. Make bounded execution, governance checks, "
        "replay evidence, and fail-closed outcomes easier to understand."
    ),
    MONETIZATION_OPTIMIZATION_MODE: (
        "Clarify why the governed operating layer matters to enterprise buyers. Preserve restrained "
        "institutional language and avoid growth-dashboard or startup KPI framing."
    ),
    ENTERPRISE_TRUST_MODE: (
        "Strengthen premium institutional trust signals, audit visibility, and governance confidence "
        "without cyberpunk styling, compliance-banner aesthetics, or visual overload."
    ),
}


@dataclass(frozen=True)
class RefinementGuidanceRequest:
    adaptive_request: AdaptiveRefinementRequest
    workflow_context: str = "product_1_agol_refinement"
    requested_output: str = "refinement_guidance"
    user_final_authority: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "adaptive_request": self.adaptive_request.to_dict(),
            "requested_output": self.requested_output,
            "user_final_authority": self.user_final_authority,
            "workflow_context": self.workflow_context,
        }


@dataclass(frozen=True)
class RefinementRecommendation:
    mode: str
    reason: str
    suggested_direction: str
    prompt_augmentation: str
    escalation_guidance: str
    proposal_only: bool
    user_final_authority: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "escalation_guidance": self.escalation_guidance,
            "mode": self.mode,
            "prompt_augmentation": self.prompt_augmentation,
            "proposal_only": self.proposal_only,
            "reason": self.reason,
            "suggested_direction": self.suggested_direction,
            "user_final_authority": self.user_final_authority,
        }


@dataclass(frozen=True)
class RefinementGuidanceResult:
    primitive_id: str
    adaptive_primitive_id: str
    status: str
    assessment: AdaptiveRefinementAssessment
    recommendation: RefinementRecommendation
    autonomous_execution_authorized: bool
    redesign_authority_granted: bool
    runtime_authority_granted: bool
    mutation_performed: bool
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "adaptive_primitive_id": self.adaptive_primitive_id,
            "assessment": self.assessment.to_dict(),
            "autonomous_execution_authorized": self.autonomous_execution_authorized,
            "command_hash": self.command_hash,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "mutation_performed": self.mutation_performed,
            "primitive_id": self.primitive_id,
            "recommendation": self.recommendation.to_dict(),
            "redesign_authority_granted": self.redesign_authority_granted,
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "runtime_authority_granted": self.runtime_authority_granted,
            "scope_hash": self.scope_hash,
            "status": self.status,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_refinement_guidance_scope() -> dict[str, object]:
    return {
        "allowed": [
            "refinement recommendation",
            "UX adaptation guidance",
            "prompt augmentation assistance",
            "refinement mode suggestion",
            "perceptual-impact escalation guidance",
        ],
        "forbidden": [
            "autonomous redesign",
            "automatic file mutation",
            "runtime behavior change",
            "governance semantic change",
            "deployment automation",
            "orchestration authority",
            "user authority override",
        ],
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
        "execution_authority_granted": False,
    }


def build_refinement_recommendation(
    assessment: AdaptiveRefinementAssessment,
    *,
    user_final_authority: bool = True,
) -> RefinementRecommendation:
    mode = assessment.suggested_mode
    suggested_direction = MODE_DIRECTIONS.get(
        mode,
        MODE_DIRECTIONS[CONTINUITY_REFINEMENT_MODE],
    )
    prompt_augmentation = MODE_PROMPT_AUGMENTATIONS.get(
        mode,
        MODE_PROMPT_AUGMENTATIONS[CONTINUITY_REFINEMENT_MODE],
    )
    escalation_guidance = (
        "Ask the user to confirm bounded higher-impact refinement before making larger changes."
        if assessment.bounded_escalation_suggested
        else "Continue with the current bounded refinement magnitude."
    )
    return RefinementRecommendation(
        mode=mode,
        reason=assessment.reason,
        suggested_direction=suggested_direction,
        prompt_augmentation=prompt_augmentation,
        escalation_guidance=escalation_guidance,
        proposal_only=True,
        user_final_authority=user_final_authority,
    )


def generate_refinement_guidance(
    request: RefinementGuidanceRequest,
) -> RefinementGuidanceResult:
    assessment = assess_refinement_intent(request.adaptive_request)
    recommendation = build_refinement_recommendation(
        assessment,
        user_final_authority=request.user_final_authority,
    )
    forbidden = _forbidden_boundary_checks(request, assessment)
    status = (
        "GUIDANCE_ESCALATION_RECOMMENDED"
        if assessment.bounded_escalation_suggested
        else "GUIDANCE_CONTINUITY_RECOMMENDED"
    )

    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=NO_COMMAND,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "adaptive_primitive_id": ADAPTIVE_INTENT_PRIMITIVE_ID,
        "assessment_hash": assessment.deterministic_hash,
        "autonomous_execution_authorized": False,
        "command_hash": replay_identity["command_hash"],
        "forbidden_boundary_checks": list(forbidden),
        "mutation_performed": False,
        "primitive_id": replay_identity["primitive_id"],
        "recommendation": recommendation.to_dict(),
        "redesign_authority_granted": False,
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "runtime_authority_granted": False,
        "scope_hash": replay_identity["scope_hash"],
        "status": status,
    }
    return RefinementGuidanceResult(
        primitive_id=str(replay_identity["primitive_id"]),
        adaptive_primitive_id=ADAPTIVE_INTENT_PRIMITIVE_ID,
        status=status,
        assessment=assessment,
        recommendation=recommendation,
        autonomous_execution_authorized=False,
        redesign_authority_granted=False,
        runtime_authority_granted=False,
        mutation_performed=False,
        forbidden_boundary_checks=forbidden,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _forbidden_boundary_checks(
    request: RefinementGuidanceRequest,
    assessment: AdaptiveRefinementAssessment,
) -> tuple[str, ...]:
    checks = set(assessment.forbidden_boundary_checks)
    if not request.user_final_authority:
        checks.add("user_final_authority_required")
    if request.requested_output not in {
        "refinement_guidance",
        "prompt_augmentation",
        "mode_recommendation",
    }:
        checks.add("unsupported_guidance_output_requires_approval")
    return tuple(sorted(checks))


def _scope_hash() -> str:
    return str(
        build_replay_identity(
            primitive_id=PRIMITIVE_ID,
            request_payload={},
            command=NO_COMMAND,
            scope_payload=_scope_payload(),
            replay_lineage=REPLAY_LINEAGE,
        )["scope_hash"]
    )


def _scope_payload() -> dict[str, object]:
    return {
        "allowed_outputs": [
            "refinement_guidance",
            "prompt_augmentation",
            "mode_recommendation",
        ],
        "execution_authority_granted": False,
        "mutation_performed": False,
        "primitive_id": PRIMITIVE_ID,
        "scope_id": SCOPE_ID,
        "user_final_authority_required": True,
    }
