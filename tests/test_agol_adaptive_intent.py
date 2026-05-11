from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.agol_adaptive_intent import (
    BOUNDED_RESTRUCTURING_MODE,
    CONTINUITY_REFINEMENT_MODE,
    HIGHER_IMPACT_MESSAGE,
    PERCEPTUAL_IMPACT_MODE,
    PRIMITIVE_ID,
    AdaptiveRefinementRequest,
    RefinementIteration,
    assess_refinement_intent,
    describe_adaptive_refinement_scope,
    detect_perceptual_impact_mismatch,
    detect_refinement_stagnation,
)


def test_detects_refinement_stagnation_from_repeated_low_impact_iterations() -> None:
    iterations = (
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

    assert detect_refinement_stagnation(iterations) is True


def test_detects_perceptual_impact_mismatch_for_latest_iteration() -> None:
    iterations = (
        RefinementIteration(
            request_text="It still does not feel premium enough.",
            mutation_magnitude="micro",
            perceptual_delta="low",
            requested_impact="high",
        ),
    )

    assert detect_perceptual_impact_mismatch(iterations) is True


def test_bounded_escalation_suggestion_remains_proposal_only() -> None:
    request = AdaptiveRefinementRequest(
        iterations=(
            RefinementIteration(
                request_text="This still feels crowded.",
                mutation_magnitude="micro",
                perceptual_delta="low",
            ),
            RefinementIteration(
                request_text="This changed almost nothing and still feels underpowered.",
                mutation_magnitude="minor",
                perceptual_delta="none",
            ),
        )
    )

    result = assess_refinement_intent(request)

    assert result.status == "BOUNDED_ESCALATION_SUGGESTED"
    assert result.stagnation_detected is True
    assert result.mismatch_detected is True
    assert result.suggested_mode == BOUNDED_RESTRUCTURING_MODE
    assert result.suggested_message == HIGHER_IMPACT_MESSAGE
    assert result.autonomous_execution_authorized is False
    assert result.redesign_authority_granted is False
    assert result.runtime_authority_granted is False


def test_single_low_delta_signal_suggests_perceptual_impact_mode() -> None:
    request = AdaptiveRefinementRequest(
        iterations=(
            RefinementIteration(
                request_text="This still feels too conservative relative to the desired impact.",
                mutation_magnitude="minor",
                perceptual_delta="low",
                requested_impact="high",
            ),
        )
    )

    result = assess_refinement_intent(request)

    assert result.stagnation_detected is False
    assert result.mismatch_detected is True
    assert result.suggested_mode == PERCEPTUAL_IMPACT_MODE


def test_continuity_refinement_remains_default_when_no_mismatch_exists() -> None:
    request = AdaptiveRefinementRequest(
        iterations=(
            RefinementIteration(
                request_text="Preserve the current continuity direction.",
                mutation_magnitude="minor",
                perceptual_delta="moderate",
                requested_impact="low",
                dissatisfaction_signal=False,
            ),
        )
    )

    result = assess_refinement_intent(request)

    assert result.status == "CONTINUITY_REFINEMENT_APPROPRIATE"
    assert result.suggested_mode == CONTINUITY_REFINEMENT_MODE
    assert result.bounded_escalation_suggested is False


def test_scope_description_is_non_executing() -> None:
    description = describe_adaptive_refinement_scope()

    assert description["primitive_id"] == PRIMITIVE_ID
    assert description["execution_authority_granted"] is False
    assert "autonomous redesign authority" in description["forbidden"]


def test_boundary_violations_are_reported_without_authority_expansion() -> None:
    request = AdaptiveRefinementRequest(
        iterations=(
            RefinementIteration(
                request_text="Change the runtime behavior while improving UX.",
                mutation_magnitude="minor",
                perceptual_delta="low",
                runtime_behavior_changed=True,
            ),
        )
    )

    result = assess_refinement_intent(request)

    assert "runtime_behavior_mutation_forbidden" in result.forbidden_boundary_checks
    assert result.autonomous_execution_authorized is False


def test_assessment_hash_is_stable_and_replay_visible() -> None:
    request = AdaptiveRefinementRequest(
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

    first = assess_refinement_intent(request)
    second = assess_refinement_intent(request)
    description = describe_adaptive_refinement_scope()

    assert first.deterministic_hash == second.deterministic_hash
    assert first.request_hash == second.request_hash
    assert first.command_hash == second.command_hash
    assert first.scope_hash == description["scope_hash"]
    assert "runtime/governance/agol_adaptive_intent.py" in first.replay_lineage
