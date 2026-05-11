from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.agol_adaptive_intent import (
    BOUNDED_RESTRUCTURING_MODE,
    CONTINUITY_REFINEMENT_MODE,
    AdaptiveRefinementRequest,
    RefinementIteration,
)
from runtime.governance.agol_refinement_guidance import (
    PRIMITIVE_ID,
    RefinementGuidanceRequest,
    build_refinement_recommendation,
    describe_refinement_guidance_scope,
    generate_refinement_guidance,
)


def test_stagnation_triggers_bounded_refinement_guidance() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="This still feels crowded.",
                    mutation_magnitude="micro",
                    perceptual_delta="low",
                ),
                RefinementIteration(
                    request_text="This changed almost nothing and still does not feel premium.",
                    mutation_magnitude="minor",
                    perceptual_delta="none",
                ),
            )
        )
    )

    result = generate_refinement_guidance(request)

    assert result.status == "GUIDANCE_ESCALATION_RECOMMENDED"
    assert result.assessment.stagnation_detected is True
    assert result.recommendation.mode == BOUNDED_RESTRUCTURING_MODE
    assert "Increase compositional restructuring" in result.recommendation.suggested_direction


def test_refinement_mode_recommendation_preserves_continuity_when_proportionate() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="Preserve continuity and lightly improve hierarchy.",
                    mutation_magnitude="minor",
                    perceptual_delta="moderate",
                    requested_impact="low",
                    dissatisfaction_signal=False,
                ),
            )
        )
    )

    result = generate_refinement_guidance(request)

    assert result.status == "GUIDANCE_CONTINUITY_RECOMMENDED"
    assert result.recommendation.mode == CONTINUITY_REFINEMENT_MODE
    assert result.recommendation.escalation_guidance == (
        "Continue with the current bounded refinement magnitude."
    )


def test_prompt_augmentation_names_bounded_higher_impact_strategy() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="This still feels underpowered.",
                    mutation_magnitude="micro",
                    perceptual_delta="low",
                ),
                RefinementIteration(
                    request_text="It still changed almost nothing.",
                    mutation_magnitude="minor",
                    perceptual_delta="none",
                ),
            )
        ),
        requested_output="prompt_augmentation",
    )

    result = generate_refinement_guidance(request)

    assert "bounded restructuring" in result.recommendation.prompt_augmentation
    assert "preserving AGOL governance continuity" in result.recommendation.prompt_augmentation
    assert "runtime semantics" in result.recommendation.prompt_augmentation


def test_build_recommendation_is_proposal_only() -> None:
    result = generate_refinement_guidance(
        RefinementGuidanceRequest(
            adaptive_request=AdaptiveRefinementRequest(
                iterations=(
                    RefinementIteration(
                        request_text="This still feels too conservative.",
                        mutation_magnitude="minor",
                        perceptual_delta="low",
                    ),
                )
            )
        )
    )
    recommendation = build_refinement_recommendation(result.assessment)

    assert recommendation.proposal_only is True
    assert recommendation.user_final_authority is True


def test_guidance_preserves_proposal_only_behavior_and_user_authority() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="This still feels crowded.",
                    mutation_magnitude="micro",
                    perceptual_delta="low",
                ),
            )
        )
    )

    result = generate_refinement_guidance(request)

    assert result.autonomous_execution_authorized is False
    assert result.redesign_authority_granted is False
    assert result.runtime_authority_granted is False
    assert result.mutation_performed is False
    assert result.recommendation.user_final_authority is True


def test_guidance_reports_missing_user_authority_as_boundary_violation() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="Improve enterprise trust.",
                    mutation_magnitude="minor",
                    perceptual_delta="moderate",
                    dissatisfaction_signal=False,
                ),
            )
        ),
        user_final_authority=False,
    )

    result = generate_refinement_guidance(request)

    assert "user_final_authority_required" in result.forbidden_boundary_checks
    assert result.autonomous_execution_authorized is False


def test_guidance_scope_is_non_executing() -> None:
    description = describe_refinement_guidance_scope()

    assert description["primitive_id"] == PRIMITIVE_ID
    assert description["execution_authority_granted"] is False
    assert "prompt augmentation assistance" in description["allowed"]
    assert "automatic file mutation" in description["forbidden"]


def test_guidance_hash_is_stable_and_replay_visible() -> None:
    request = RefinementGuidanceRequest(
        adaptive_request=AdaptiveRefinementRequest(
            iterations=(
                RefinementIteration(
                    request_text="This still feels crowded.",
                    mutation_magnitude="micro",
                    perceptual_delta="low",
                ),
                RefinementIteration(
                    request_text="This changed almost nothing.",
                    mutation_magnitude="minor",
                    perceptual_delta="none",
                ),
            )
        )
    )

    first = generate_refinement_guidance(request)
    second = generate_refinement_guidance(request)
    description = describe_refinement_guidance_scope()

    assert first.deterministic_hash == second.deterministic_hash
    assert first.request_hash == second.request_hash
    assert first.command_hash == second.command_hash
    assert first.scope_hash == description["scope_hash"]
    assert "runtime/governance/agol_refinement_guidance.py" in first.replay_lineage
