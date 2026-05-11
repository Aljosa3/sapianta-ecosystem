from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.agol_convergence_aware_refinement import (
    PRIMITIVE_ID,
    ConvergenceAwareRefinementRequest,
    ConvergenceSignal,
    describe_convergence_aware_refinement_scope,
    generate_convergence_aware_refinement,
)


def test_repeated_positive_reinforcement_detects_convergence() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal("This is now good; preserve the hero composition."),
            ConvergenceSignal("The cube operational symbolism works much better."),
            ConvergenceSignal("The restrained blue institutional palette is better."),
        )
    )

    result = generate_convergence_aware_refinement(request)

    assert result.status == "CONVERGENCE_STABILIZATION_RECOMMENDED"
    assert result.convergence_detected is True
    assert result.convergence_confidence == "high"
    assert "hero_composition" in result.stabilized_regions
    assert "operational_symbolism" in result.stabilized_regions
    assert "institutional_palette" in result.stabilized_regions


def test_current_product_one_direction_is_stabilization_candidate() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal("The calmer enterprise atmosphere works."),
            ConvergenceSignal("Preserve AGOL operational continuity and replay framing."),
        ),
        reduced_dissatisfaction_signals=True,
    )

    result = generate_convergence_aware_refinement(request)

    assert result.convergence_detected is True
    assert "enterprise_atmosphere" in result.stabilized_regions
    assert "replay_safe_operational_framing" in result.stabilized_regions
    assert result.continuity_protection_recommended is True


def test_restructuring_pressure_on_stabilized_regions_reports_high_risk() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal("This is now good; preserve the hero composition."),
            ConvergenceSignal("The cube symbolism works better."),
        ),
        proposed_refinement_intent="Redesign and restructure the hero again.",
        requested_mutation_magnitude="major",
    )

    result = generate_convergence_aware_refinement(request)

    assert result.mutation_pressure_risk == "high"
    assert result.local_refinement_only is True
    assert result.recommended_refinement_scope == (
        "local_refinements_only_in_unstabilized_regions"
    )


def test_freeze_zone_recommendations_are_proposal_only_protection() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal("Preserve the blue institutional palette."),
            ConvergenceSignal("This enterprise atmosphere works better."),
        ),
        proposed_refinement_intent="Keep changing the full style.",
        refinement_cycles_after_positive_feedback=2,
    )

    result = generate_convergence_aware_refinement(request)

    assert "protect:institutional_palette" in result.freeze_zone_recommendations
    assert "protect:enterprise_atmosphere" in result.freeze_zone_recommendations
    assert result.autonomous_freeze_authorized is False
    assert result.user_override_preserved is True


def test_no_convergence_keeps_monitoring_scope() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal(
                "This is still not good enough.",
                positive_reinforcement=False,
                dissatisfaction_signal=True,
            ),
        ),
        proposed_refinement_intent="Continue bounded refinement.",
    )

    result = generate_convergence_aware_refinement(request)

    assert result.status == "CONVERGENCE_MONITORING_RECOMMENDED"
    assert result.convergence_detected is False
    assert result.convergence_confidence == "low"
    assert result.freeze_zone_recommendations == ()
    assert result.recommended_refinement_scope == (
        "bounded_refinement_with_convergence_monitoring"
    )


def test_scope_and_result_preserve_non_authority_boundaries() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(ConvergenceSignal("This direction works; preserve the hero."),)
    )

    result = generate_convergence_aware_refinement(request)
    description = describe_convergence_aware_refinement_scope()

    assert description["primitive_id"] == PRIMITIVE_ID
    assert description["execution_authority_granted"] is False
    assert "automatic redesign freezing" in description["forbidden"]
    assert result.proposal_only is True
    assert result.autonomous_redesign_authorized is False
    assert result.runtime_authority_granted is False
    assert result.mutation_performed is False


def test_forbidden_boundary_checks_remain_visible() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal(
                "Preserve this.",
                user_final_authority=False,
                runtime_behavior_changed=True,
            ),
        ),
        requested_output="freeze_files",
        user_final_authority=False,
    )

    result = generate_convergence_aware_refinement(request)

    assert "user_final_authority_required" in result.forbidden_boundary_checks
    assert "signal_user_authority_required" in result.forbidden_boundary_checks
    assert "runtime_behavior_mutation_forbidden" in result.forbidden_boundary_checks
    assert "unsupported_guidance_output_requires_approval" in result.forbidden_boundary_checks


def test_convergence_guidance_hash_is_stable_and_replay_visible() -> None:
    request = ConvergenceAwareRefinementRequest(
        signals=(
            ConvergenceSignal("This is now good; preserve the hero composition."),
            ConvergenceSignal("The cube symbolism works better."),
        ),
        proposed_refinement_intent="Make only local refinements.",
        reduced_dissatisfaction_signals=True,
    )

    first = generate_convergence_aware_refinement(request)
    second = generate_convergence_aware_refinement(request)
    description = describe_convergence_aware_refinement_scope()

    assert first.deterministic_hash == second.deterministic_hash
    assert first.request_hash == second.request_hash
    assert first.command_hash == second.command_hash
    assert first.scope_hash == description["scope_hash"]
    assert "runtime/governance/agol_convergence_aware_refinement.py" in first.replay_lineage
