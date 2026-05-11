"""Bounded AGOL convergence-aware refinement guidance.

This module detects Product 1 refinement convergence and recommends narrower
continuity-protected refinement scope. It never freezes files, refuses human
changes, mutates UI, executes commands, or grants redesign/runtime authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agol_adaptive_intent import PRIMITIVE_ID as ADAPTIVE_INTENT_PRIMITIVE_ID
from .agol_refinement_guidance import PRIMITIVE_ID as REFINEMENT_GUIDANCE_PRIMITIVE_ID
from .agol_visual_continuity_memory import (
    PRIMITIVE_ID as VISUAL_CONTINUITY_MEMORY_PRIMITIVE_ID,
)
from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PRIMITIVE_ID = "AGOL_CONVERGENCE_AWARE_REFINEMENT_V1"
SCOPE_ID = "PRODUCT_1_CONVERGENCE_AWARE_REFINEMENT_GUIDANCE_ONLY"
NO_COMMAND: tuple[str, ...] = ()
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/AGOL_ADAPTIVE_INTENT_AWARENESS_V1.md",
    "docs/governance/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1.md",
    "docs/governance/AGOL_VISUAL_CONTINUITY_MEMORY_V1.md",
    "docs/governance/AGOL_CONVERGENCE_AWARE_REFINEMENT_V1.md",
    "runtime/governance/agol_adaptive_intent.py",
    "runtime/governance/agol_refinement_guidance.py",
    "runtime/governance/agol_visual_continuity_memory.py",
    "runtime/governance/agol_convergence_aware_refinement.py",
    "tests/test_agol_convergence_aware_refinement.py",
)

POSITIVE_CONVERGENCE_TERMS = (
    "better",
    "direction works",
    "good",
    "much better",
    "now good",
    "this works",
    "works",
)
PRESERVATION_TERMS = (
    "do not change",
    "don't change",
    "keep",
    "preserve",
    "protect",
)
DISSATISFACTION_TERMS = (
    "bad",
    "does not work",
    "doesn't work",
    "not enough",
    "still not",
    "too weak",
    "worse",
)
MUTATION_PRESSURE_TERMS = (
    "cosmetic",
    "keep changing",
    "overhaul",
    "redesign",
    "replace",
    "reset",
    "restructure",
    "start over",
    "transform",
)
HIGH_MUTATION_MAGNITUDES = ("major", "large", "transformational", "full_redesign")

REGION_TERMS = {
    "hero_composition": ("hero", "composition", "layout"),
    "operational_symbolism": ("cube", "artifact", "operational symbolism", "symbolism"),
    "institutional_palette": ("blue", "palette", "institutional palette"),
    "enterprise_atmosphere": ("calm", "calmer", "enterprise", "institutional"),
    "replay_safe_operational_framing": ("agol", "governance", "replay", "operational continuity"),
    "lower_dashboard_density": ("density", "less dashboard", "lower dashboard"),
}

PRODUCT_1_STABILIZATION_CANDIDATES = (
    "hero_composition",
    "operational_symbolism",
    "institutional_palette",
    "enterprise_atmosphere",
    "replay_safe_operational_framing",
)


@dataclass(frozen=True)
class ConvergenceSignal:
    feedback_text: str
    ux_region: str = "product_1_hero"
    positive_reinforcement: bool | None = None
    dissatisfaction_signal: bool | None = None
    preservation_intent: bool | None = None
    user_final_authority: bool = True
    runtime_behavior_changed: bool = False
    governance_semantics_changed: bool = False

    def has_positive_reinforcement(self) -> bool:
        if self.positive_reinforcement is not None:
            return self.positive_reinforcement
        normalized = self.feedback_text.lower()
        return any(term in normalized for term in POSITIVE_CONVERGENCE_TERMS)

    def has_dissatisfaction_signal(self) -> bool:
        if self.dissatisfaction_signal is not None:
            return self.dissatisfaction_signal
        normalized = self.feedback_text.lower()
        return any(term in normalized for term in DISSATISFACTION_TERMS)

    def has_preservation_intent(self) -> bool:
        if self.preservation_intent is not None:
            return self.preservation_intent
        normalized = self.feedback_text.lower()
        return any(term in normalized for term in PRESERVATION_TERMS)

    def detected_regions(self) -> tuple[str, ...]:
        normalized = self.feedback_text.lower()
        regions = {
            region
            for region, terms in REGION_TERMS.items()
            if any(term in normalized for term in terms)
        }
        return tuple(sorted(regions))

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected_regions": list(self.detected_regions()),
            "dissatisfaction_signal": self.has_dissatisfaction_signal(),
            "feedback_text": self.feedback_text,
            "governance_semantics_changed": self.governance_semantics_changed,
            "positive_reinforcement": self.has_positive_reinforcement(),
            "preservation_intent": self.has_preservation_intent(),
            "runtime_behavior_changed": self.runtime_behavior_changed,
            "user_final_authority": self.user_final_authority,
            "ux_region": self.ux_region,
        }


@dataclass(frozen=True)
class ConvergenceAwareRefinementRequest:
    signals: tuple[ConvergenceSignal, ...]
    proposed_refinement_intent: str = ""
    requested_mutation_magnitude: str = "minor"
    refinement_cycles_after_positive_feedback: int = 0
    reduced_dissatisfaction_signals: bool = False
    stabilization_candidates: tuple[str, ...] = PRODUCT_1_STABILIZATION_CANDIDATES
    requested_output: str = "convergence_aware_refinement_guidance"
    user_final_authority: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "refinement_cycles_after_positive_feedback": (
                self.refinement_cycles_after_positive_feedback
            ),
            "reduced_dissatisfaction_signals": self.reduced_dissatisfaction_signals,
            "proposed_refinement_intent": self.proposed_refinement_intent,
            "requested_mutation_magnitude": self.requested_mutation_magnitude,
            "requested_output": self.requested_output,
            "signals": [signal.to_dict() for signal in self.signals],
            "stabilization_candidates": list(self.stabilization_candidates),
            "user_final_authority": self.user_final_authority,
        }


@dataclass(frozen=True)
class ConvergenceAwareRefinementResult:
    primitive_id: str
    related_primitive_ids: tuple[str, ...]
    status: str
    convergence_detected: bool
    convergence_confidence: str
    stabilized_regions: tuple[str, ...]
    freeze_zone_recommendations: tuple[str, ...]
    continuity_protection_recommended: bool
    mutation_pressure_risk: str
    recommended_refinement_scope: str
    preserve_existing_direction: bool
    local_refinement_only: bool
    proposal_only: bool
    autonomous_freeze_authorized: bool
    autonomous_redesign_authorized: bool
    runtime_authority_granted: bool
    mutation_performed: bool
    user_override_preserved: bool
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "autonomous_freeze_authorized": self.autonomous_freeze_authorized,
            "autonomous_redesign_authorized": self.autonomous_redesign_authorized,
            "command_hash": self.command_hash,
            "continuity_protection_recommended": self.continuity_protection_recommended,
            "convergence_confidence": self.convergence_confidence,
            "convergence_detected": self.convergence_detected,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "freeze_zone_recommendations": list(self.freeze_zone_recommendations),
            "local_refinement_only": self.local_refinement_only,
            "mutation_performed": self.mutation_performed,
            "mutation_pressure_risk": self.mutation_pressure_risk,
            "preserve_existing_direction": self.preserve_existing_direction,
            "primitive_id": self.primitive_id,
            "proposal_only": self.proposal_only,
            "recommended_refinement_scope": self.recommended_refinement_scope,
            "related_primitive_ids": list(self.related_primitive_ids),
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "runtime_authority_granted": self.runtime_authority_granted,
            "scope_hash": self.scope_hash,
            "stabilized_regions": list(self.stabilized_regions),
            "status": self.status,
            "user_override_preserved": self.user_override_preserved,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_convergence_aware_refinement_scope() -> dict[str, object]:
    return {
        "allowed": [
            "detect bounded convergence",
            "recommend refinement stabilization",
            "warn about mutation pressure risk",
            "propose continuity-protected regions",
            "recommend local-only refinement scope",
        ],
        "forbidden": [
            "autonomous UI governance",
            "automatic redesign freezing",
            "file mutation",
            "runtime control",
            "orchestration authority",
            "self-modifying behavior",
            "human intent override",
        ],
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
        "execution_authority_granted": False,
    }


def generate_convergence_aware_refinement(
    request: ConvergenceAwareRefinementRequest,
) -> ConvergenceAwareRefinementResult:
    stabilized_regions = _stabilized_regions(request)
    convergence_detected = _convergence_detected(request, stabilized_regions)
    confidence = _convergence_confidence(request, stabilized_regions, convergence_detected)
    mutation_risk = _mutation_pressure_risk(request, stabilized_regions, convergence_detected)
    continuity_protection = convergence_detected or mutation_risk in {"medium", "high"}
    preserve_existing = bool(stabilized_regions) and continuity_protection
    local_only = preserve_existing and mutation_risk in {"medium", "high"}
    freeze_zones = _freeze_zone_recommendations(stabilized_regions, continuity_protection)
    recommended_scope = _recommended_refinement_scope(
        preserve_existing,
        local_only,
        mutation_risk,
    )
    forbidden = _forbidden_boundary_checks(request)
    status = (
        "CONVERGENCE_STABILIZATION_RECOMMENDED"
        if convergence_detected
        else "CONVERGENCE_MONITORING_RECOMMENDED"
    )
    related = (
        ADAPTIVE_INTENT_PRIMITIVE_ID,
        REFINEMENT_GUIDANCE_PRIMITIVE_ID,
        VISUAL_CONTINUITY_MEMORY_PRIMITIVE_ID,
    )

    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=NO_COMMAND,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "autonomous_freeze_authorized": False,
        "autonomous_redesign_authorized": False,
        "command_hash": replay_identity["command_hash"],
        "continuity_protection_recommended": continuity_protection,
        "convergence_confidence": confidence,
        "convergence_detected": convergence_detected,
        "forbidden_boundary_checks": list(forbidden),
        "freeze_zone_recommendations": list(freeze_zones),
        "local_refinement_only": local_only,
        "mutation_performed": False,
        "mutation_pressure_risk": mutation_risk,
        "preserve_existing_direction": preserve_existing,
        "primitive_id": replay_identity["primitive_id"],
        "proposal_only": True,
        "recommended_refinement_scope": recommended_scope,
        "related_primitive_ids": list(related),
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "runtime_authority_granted": False,
        "scope_hash": replay_identity["scope_hash"],
        "stabilized_regions": list(stabilized_regions),
        "status": status,
        "user_override_preserved": True,
    }
    return ConvergenceAwareRefinementResult(
        primitive_id=str(replay_identity["primitive_id"]),
        related_primitive_ids=related,
        status=status,
        convergence_detected=convergence_detected,
        convergence_confidence=confidence,
        stabilized_regions=stabilized_regions,
        freeze_zone_recommendations=freeze_zones,
        continuity_protection_recommended=continuity_protection,
        mutation_pressure_risk=mutation_risk,
        recommended_refinement_scope=recommended_scope,
        preserve_existing_direction=preserve_existing,
        local_refinement_only=local_only,
        proposal_only=True,
        autonomous_freeze_authorized=False,
        autonomous_redesign_authorized=False,
        runtime_authority_granted=False,
        mutation_performed=False,
        user_override_preserved=True,
        forbidden_boundary_checks=forbidden,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _stabilized_regions(request: ConvergenceAwareRefinementRequest) -> tuple[str, ...]:
    candidate_set = set(request.stabilization_candidates)
    regions: set[str] = set()
    for signal in request.signals:
        if signal.has_positive_reinforcement() or signal.has_preservation_intent():
            detected = set(signal.detected_regions())
            if detected:
                regions.update(detected & candidate_set)
            elif signal.ux_region in candidate_set:
                regions.add(signal.ux_region)
    return tuple(sorted(regions))


def _convergence_detected(
    request: ConvergenceAwareRefinementRequest,
    stabilized_regions: tuple[str, ...],
) -> bool:
    positive_count = sum(
        1 for signal in request.signals if signal.has_positive_reinforcement()
    )
    preservation_count = sum(1 for signal in request.signals if signal.has_preservation_intent())
    dissatisfaction_count = sum(
        1 for signal in request.signals if signal.has_dissatisfaction_signal()
    )
    enough_positive_signal = positive_count >= 2 or (
        positive_count >= 1 and preservation_count >= 1
    )
    dissatisfaction_reduced = request.reduced_dissatisfaction_signals or dissatisfaction_count == 0
    return bool(stabilized_regions) and enough_positive_signal and dissatisfaction_reduced


def _convergence_confidence(
    request: ConvergenceAwareRefinementRequest,
    stabilized_regions: tuple[str, ...],
    convergence_detected: bool,
) -> str:
    if not convergence_detected:
        return "low"
    positive_count = sum(
        1 for signal in request.signals if signal.has_positive_reinforcement()
    )
    preservation_count = sum(1 for signal in request.signals if signal.has_preservation_intent())
    if len(stabilized_regions) >= 3 and positive_count + preservation_count >= 3:
        return "high"
    return "medium"


def _mutation_pressure_risk(
    request: ConvergenceAwareRefinementRequest,
    stabilized_regions: tuple[str, ...],
    convergence_detected: bool,
) -> str:
    proposed = request.proposed_refinement_intent.lower()
    pressure_terms_present = any(term in proposed for term in MUTATION_PRESSURE_TERMS)
    high_magnitude = request.requested_mutation_magnitude in HIGH_MUTATION_MAGNITUDES
    repeated_cycles = request.refinement_cycles_after_positive_feedback >= 2
    if stabilized_regions and pressure_terms_present and (high_magnitude or repeated_cycles):
        return "high"
    if convergence_detected and (high_magnitude or pressure_terms_present or repeated_cycles):
        return "medium"
    if stabilized_regions and repeated_cycles:
        return "medium"
    return "low"


def _freeze_zone_recommendations(
    stabilized_regions: tuple[str, ...],
    continuity_protection: bool,
) -> tuple[str, ...]:
    if not continuity_protection:
        return ()
    return tuple(f"protect:{region}" for region in stabilized_regions)


def _recommended_refinement_scope(
    preserve_existing_direction: bool,
    local_refinement_only: bool,
    mutation_pressure_risk: str,
) -> str:
    if local_refinement_only and mutation_pressure_risk == "high":
        return "local_refinements_only_in_unstabilized_regions"
    if local_refinement_only:
        return "local_refinements_only"
    if preserve_existing_direction:
        return "continuity_protected_bounded_refinement"
    return "bounded_refinement_with_convergence_monitoring"


def _forbidden_boundary_checks(
    request: ConvergenceAwareRefinementRequest,
) -> tuple[str, ...]:
    checks: set[str] = set()
    if not request.user_final_authority:
        checks.add("user_final_authority_required")
    if request.requested_output not in {
        "convergence_aware_refinement_guidance",
        "stabilization_recommendation",
        "mutation_pressure_assessment",
    }:
        checks.add("unsupported_guidance_output_requires_approval")
    for signal in request.signals:
        if not signal.user_final_authority:
            checks.add("signal_user_authority_required")
        if signal.runtime_behavior_changed:
            checks.add("runtime_behavior_mutation_forbidden")
        if signal.governance_semantics_changed:
            checks.add("governance_semantic_mutation_forbidden")
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
            "convergence_aware_refinement_guidance",
            "stabilization_recommendation",
            "mutation_pressure_assessment",
        ],
        "automatic_freezing_allowed": False,
        "execution_authority_granted": False,
        "human_override_preserved": True,
        "mutation_performed": False,
        "primitive_id": PRIMITIVE_ID,
        "runtime_authority_granted": False,
        "scope_id": SCOPE_ID,
        "user_final_authority_required": True,
    }
