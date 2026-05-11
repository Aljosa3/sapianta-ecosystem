from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.agol_visual_continuity_memory import (
    PRIMITIVE_ID,
    VisualContinuityMemoryRequest,
    VisualContinuityObservation,
    describe_visual_continuity_memory_scope,
    generate_visual_continuity_memory,
)


def test_positive_reinforcement_stabilizes_visual_directions() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This is much better; the blue atmosphere is better.",
            ),
            VisualContinuityObservation(
                feedback_text="The cube feels more premium, preserve this concrete symbolism.",
            ),
        )
    )

    result = generate_visual_continuity_memory(request)

    assert result.status == "CONTINUITY_PRESERVATION_RECOMMENDED"
    assert "restrained_blue_palette" in result.stabilized_visual_directions
    assert "concrete_operational_symbolism" in result.stabilized_visual_directions
    assert result.preserve_existing_direction is True


def test_repeated_successful_feedback_detects_convergence() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This direction works; preserve the calmer enterprise atmosphere.",
            ),
            VisualContinuityObservation(
                feedback_text="This is much better, keep the bounded governance refinement.",
            ),
        )
    )

    result = generate_visual_continuity_memory(request)

    assert result.convergence_detected is True
    assert result.recommended_refinement_scope == "targeted_continuity_refinement_only"
    assert "avoid_reworking_stabilized_ux_zones" in result.continuity_constraints


def test_redesign_pressure_against_stabilized_area_reports_high_risk() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This direction works; preserve the restrained blue palette.",
            ),
            VisualContinuityObservation(
                feedback_text="The calmer enterprise atmosphere is much better.",
            ),
        ),
        proposed_refinement_intent="Redesign and transform the homepage style.",
        requested_mutation_magnitude="major",
    )

    result = generate_visual_continuity_memory(request)

    assert result.refinement_pressure_risk == "high"
    assert result.continuity_degradation_risk == "high"
    assert result.recommended_refinement_scope == (
        "preserve_stabilized_direction_and_limit_changes_to_unresolved_areas"
    )


def test_low_value_extra_mutation_pressure_is_visible_after_convergence() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This is much better; preserve the lower dashboard density.",
            ),
            VisualContinuityObservation(
                feedback_text="This direction works for bounded governance refinement.",
            ),
        ),
        proposed_refinement_intent="Keep tuning everything again.",
        requested_mutation_magnitude="minor",
    )

    result = generate_visual_continuity_memory(request)

    assert result.convergence_detected is True
    assert result.refinement_pressure_risk == "medium"
    assert "preserve:lower_dashboard_density" in result.continuity_constraints


def test_unstabilized_feedback_does_not_force_preservation() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="Try a different layout.",
                positive_reinforcement=False,
            ),
        )
    )

    result = generate_visual_continuity_memory(request)

    assert result.status == "CONTINUITY_MEMORY_RECORDED"
    assert result.stabilized_preferences == ()
    assert result.stabilized_visual_directions == ()
    assert result.preserve_existing_direction is False


def test_scope_and_result_preserve_non_executing_boundaries() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This direction works; preserve this blue atmosphere.",
            ),
        )
    )

    result = generate_visual_continuity_memory(request)
    description = describe_visual_continuity_memory_scope()

    assert description["primitive_id"] == PRIMITIVE_ID
    assert description["execution_authority_granted"] is False
    assert "autonomous learning" in description["forbidden"]
    assert result.proposal_only is True
    assert result.autonomous_learning_authorized is False
    assert result.autonomous_redesign_authorized is False
    assert result.runtime_authority_granted is False
    assert result.mutation_performed is False
    assert result.hidden_adaptation_performed is False


def test_forbidden_uncontrolled_memory_and_missing_authority_are_visible() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="Preserve this.",
                user_final_authority=False,
            ),
        ),
        user_final_authority=False,
        uncontrolled_memory_persistence_requested=True,
    )

    result = generate_visual_continuity_memory(request)

    assert "user_final_authority_required" in result.forbidden_boundary_checks
    assert "observation_user_authority_required" in result.forbidden_boundary_checks
    assert "uncontrolled_memory_persistence_forbidden" in result.forbidden_boundary_checks


def test_visual_continuity_hash_is_stable_and_replay_visible() -> None:
    request = VisualContinuityMemoryRequest(
        observations=(
            VisualContinuityObservation(
                feedback_text="This is much better; preserve the blue atmosphere.",
            ),
            VisualContinuityObservation(
                feedback_text="The cube feels more premium.",
            ),
        ),
        proposed_refinement_intent="Make only targeted refinements.",
    )

    first = generate_visual_continuity_memory(request)
    second = generate_visual_continuity_memory(request)
    description = describe_visual_continuity_memory_scope()

    assert first.deterministic_hash == second.deterministic_hash
    assert first.request_hash == second.request_hash
    assert first.command_hash == second.command_hash
    assert first.scope_hash == description["scope_hash"]
    assert "runtime/governance/agol_visual_continuity_memory.py" in first.replay_lineage
