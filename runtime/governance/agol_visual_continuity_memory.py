"""Bounded AGOL visual continuity memory.

This module preserves replay-visible UX continuity signals for Product 1
refinement work. It behaves as deterministic continuity constraints, not as
autonomous learning, hidden adaptation, redesign authority, or runtime control.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PRIMITIVE_ID = "AGOL_VISUAL_CONTINUITY_MEMORY_V1"
SCOPE_ID = "PRODUCT_1_VISUAL_CONTINUITY_CONSTRAINTS_ONLY"
NO_COMMAND: tuple[str, ...] = ()
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/AGOL_ADAPTIVE_INTENT_AWARENESS_V1.md",
    "docs/governance/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1.md",
    "docs/governance/AGOL_VISUAL_CONTINUITY_MEMORY_V1.md",
    "runtime/governance/agol_adaptive_intent.py",
    "runtime/governance/agol_refinement_guidance.py",
    "runtime/governance/agol_visual_continuity_memory.py",
    "tests/test_agol_visual_continuity_memory.py",
)

POSITIVE_REINFORCEMENT_TERMS = (
    "better",
    "direction works",
    "feels more premium",
    "keep",
    "much better",
    "preserve",
    "preserve this",
    "this works",
    "works",
)
DEGRADATION_PRESSURE_TERMS = (
    "dramatic",
    "overhaul",
    "replace",
    "reset",
    "redesign",
    "restructure",
    "start over",
    "transform",
)
HIGH_MUTATION_MAGNITUDES = ("major", "large", "transformational", "full_redesign")

VISUAL_DIRECTION_TERMS = {
    "restrained_blue_palette": (
        "blue",
        "blue atmosphere",
        "restrained blue",
    ),
    "calmer_enterprise_atmosphere": (
        "calm",
        "calmer",
        "enterprise atmosphere",
        "institutional",
    ),
    "concrete_operational_symbolism": (
        "artifact",
        "concrete",
        "cube",
        "operational symbolism",
        "symbolism",
    ),
    "lower_dashboard_density": (
        "dashboard density",
        "density",
        "less dashboard",
        "lower dashboard",
    ),
    "bounded_governance_refinement": (
        "bounded",
        "governance",
        "preserve scope",
        "replay",
    ),
}


@dataclass(frozen=True)
class VisualContinuityObservation:
    feedback_text: str
    ux_zone: str = "product_1_homepage"
    mutation_magnitude: str = "minor"
    positive_reinforcement: bool | None = None
    user_final_authority: bool = True
    runtime_behavior_changed: bool = False
    governance_semantics_changed: bool = False

    def has_positive_reinforcement(self) -> bool:
        if self.positive_reinforcement is not None:
            return self.positive_reinforcement
        normalized = self.feedback_text.lower()
        return any(term in normalized for term in POSITIVE_REINFORCEMENT_TERMS)

    def detected_visual_directions(self) -> tuple[str, ...]:
        normalized = self.feedback_text.lower()
        directions = {
            direction
            for direction, terms in VISUAL_DIRECTION_TERMS.items()
            if any(term in normalized for term in terms)
        }
        return tuple(sorted(directions))

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected_visual_directions": list(self.detected_visual_directions()),
            "feedback_text": self.feedback_text,
            "governance_semantics_changed": self.governance_semantics_changed,
            "mutation_magnitude": self.mutation_magnitude,
            "positive_reinforcement": self.has_positive_reinforcement(),
            "runtime_behavior_changed": self.runtime_behavior_changed,
            "user_final_authority": self.user_final_authority,
            "ux_zone": self.ux_zone,
        }


@dataclass(frozen=True)
class VisualContinuityMemoryRequest:
    observations: tuple[VisualContinuityObservation, ...]
    proposed_refinement_intent: str = ""
    requested_mutation_magnitude: str = "minor"
    requested_output: str = "visual_continuity_guidance"
    user_final_authority: bool = True
    uncontrolled_memory_persistence_requested: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "observations": [observation.to_dict() for observation in self.observations],
            "proposed_refinement_intent": self.proposed_refinement_intent,
            "requested_mutation_magnitude": self.requested_mutation_magnitude,
            "requested_output": self.requested_output,
            "uncontrolled_memory_persistence_requested": (
                self.uncontrolled_memory_persistence_requested
            ),
            "user_final_authority": self.user_final_authority,
        }


@dataclass(frozen=True)
class VisualContinuityMemoryResult:
    primitive_id: str
    status: str
    stabilized_preferences: tuple[str, ...]
    stabilized_visual_directions: tuple[str, ...]
    continuity_constraints: tuple[str, ...]
    convergence_detected: bool
    refinement_pressure_risk: str
    continuity_degradation_risk: str
    recommended_refinement_scope: str
    preserve_existing_direction: bool
    proposal_only: bool
    autonomous_learning_authorized: bool
    autonomous_redesign_authorized: bool
    runtime_authority_granted: bool
    mutation_performed: bool
    hidden_adaptation_performed: bool
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "autonomous_learning_authorized": self.autonomous_learning_authorized,
            "autonomous_redesign_authorized": self.autonomous_redesign_authorized,
            "command_hash": self.command_hash,
            "continuity_constraints": list(self.continuity_constraints),
            "continuity_degradation_risk": self.continuity_degradation_risk,
            "convergence_detected": self.convergence_detected,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "hidden_adaptation_performed": self.hidden_adaptation_performed,
            "mutation_performed": self.mutation_performed,
            "preserve_existing_direction": self.preserve_existing_direction,
            "primitive_id": self.primitive_id,
            "proposal_only": self.proposal_only,
            "recommended_refinement_scope": self.recommended_refinement_scope,
            "refinement_pressure_risk": self.refinement_pressure_risk,
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "runtime_authority_granted": self.runtime_authority_granted,
            "scope_hash": self.scope_hash,
            "stabilized_preferences": list(self.stabilized_preferences),
            "stabilized_visual_directions": list(self.stabilized_visual_directions),
            "status": self.status,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_visual_continuity_memory_scope() -> dict[str, object]:
    return {
        "allowed": [
            "detect positive refinement reinforcement",
            "preserve stabilized visual direction guidance",
            "detect refinement convergence",
            "warn about continuity degradation risk",
            "expose replay-visible continuity constraints",
        ],
        "forbidden": [
            "autonomous learning",
            "autonomous redesign",
            "automatic file mutation",
            "runtime authority",
            "orchestration authority",
            "uncontrolled memory accumulation",
            "hidden adaptation",
            "user intent override",
        ],
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
        "execution_authority_granted": False,
    }


def generate_visual_continuity_memory(
    request: VisualContinuityMemoryRequest,
) -> VisualContinuityMemoryResult:
    stabilized_preferences = _stabilized_preferences(request.observations)
    stabilized_directions = _stabilized_visual_directions(request.observations)
    convergence = _convergence_detected(request.observations, stabilized_directions)
    degradation_risk = _continuity_degradation_risk(request, stabilized_directions)
    pressure_risk = _refinement_pressure_risk(request, convergence, degradation_risk)
    constraints = _continuity_constraints(stabilized_directions, convergence)
    preserve_existing = bool(stabilized_directions) and (
        convergence or degradation_risk in {"medium", "high"}
    )
    recommended_scope = _recommended_refinement_scope(
        preserve_existing,
        pressure_risk,
        degradation_risk,
    )
    forbidden = _forbidden_boundary_checks(request)
    status = (
        "CONTINUITY_PRESERVATION_RECOMMENDED"
        if preserve_existing
        else "CONTINUITY_MEMORY_RECORDED"
    )

    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=NO_COMMAND,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "autonomous_learning_authorized": False,
        "autonomous_redesign_authorized": False,
        "command_hash": replay_identity["command_hash"],
        "continuity_constraints": list(constraints),
        "continuity_degradation_risk": degradation_risk,
        "convergence_detected": convergence,
        "forbidden_boundary_checks": list(forbidden),
        "hidden_adaptation_performed": False,
        "mutation_performed": False,
        "preserve_existing_direction": preserve_existing,
        "primitive_id": replay_identity["primitive_id"],
        "proposal_only": True,
        "recommended_refinement_scope": recommended_scope,
        "refinement_pressure_risk": pressure_risk,
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "runtime_authority_granted": False,
        "scope_hash": replay_identity["scope_hash"],
        "stabilized_preferences": list(stabilized_preferences),
        "stabilized_visual_directions": list(stabilized_directions),
        "status": status,
    }
    return VisualContinuityMemoryResult(
        primitive_id=str(replay_identity["primitive_id"]),
        status=status,
        stabilized_preferences=stabilized_preferences,
        stabilized_visual_directions=stabilized_directions,
        continuity_constraints=constraints,
        convergence_detected=convergence,
        refinement_pressure_risk=pressure_risk,
        continuity_degradation_risk=degradation_risk,
        recommended_refinement_scope=recommended_scope,
        preserve_existing_direction=preserve_existing,
        proposal_only=True,
        autonomous_learning_authorized=False,
        autonomous_redesign_authorized=False,
        runtime_authority_granted=False,
        mutation_performed=False,
        hidden_adaptation_performed=False,
        forbidden_boundary_checks=forbidden,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _stabilized_preferences(
    observations: tuple[VisualContinuityObservation, ...],
) -> tuple[str, ...]:
    preferences = {
        observation.feedback_text.strip()
        for observation in observations
        if observation.has_positive_reinforcement()
    }
    return tuple(sorted(preferences))


def _stabilized_visual_directions(
    observations: tuple[VisualContinuityObservation, ...],
) -> tuple[str, ...]:
    directions: set[str] = set()
    for observation in observations:
        if observation.has_positive_reinforcement():
            directions.update(observation.detected_visual_directions())
    return tuple(sorted(directions))


def _convergence_detected(
    observations: tuple[VisualContinuityObservation, ...],
    stabilized_directions: tuple[str, ...],
) -> bool:
    positive_count = sum(
        1 for observation in observations if observation.has_positive_reinforcement()
    )
    stabilized_zones = {
        observation.ux_zone
        for observation in observations
        if observation.has_positive_reinforcement()
    }
    return positive_count >= 2 and bool(stabilized_directions) and bool(stabilized_zones)


def _continuity_degradation_risk(
    request: VisualContinuityMemoryRequest,
    stabilized_directions: tuple[str, ...],
) -> str:
    if not stabilized_directions:
        return "low"
    proposed = request.proposed_refinement_intent.lower()
    pressure_terms_present = any(term in proposed for term in DEGRADATION_PRESSURE_TERMS)
    high_magnitude = request.requested_mutation_magnitude in HIGH_MUTATION_MAGNITUDES
    if pressure_terms_present and high_magnitude:
        return "high"
    if pressure_terms_present or high_magnitude:
        return "medium"
    return "low"


def _refinement_pressure_risk(
    request: VisualContinuityMemoryRequest,
    convergence_detected: bool,
    continuity_degradation_risk: str,
) -> str:
    if continuity_degradation_risk == "high":
        return "high"
    if convergence_detected and request.requested_mutation_magnitude in HIGH_MUTATION_MAGNITUDES:
        return "high"
    if convergence_detected or continuity_degradation_risk == "medium":
        return "medium"
    return "low"


def _continuity_constraints(
    stabilized_directions: tuple[str, ...],
    convergence_detected: bool,
) -> tuple[str, ...]:
    constraints = [
        f"preserve:{direction}" for direction in stabilized_directions
    ]
    if convergence_detected:
        constraints.append("prefer_targeted_refinement_over_restructuring")
        constraints.append("avoid_reworking_stabilized_ux_zones")
    return tuple(sorted(constraints))


def _recommended_refinement_scope(
    preserve_existing_direction: bool,
    refinement_pressure_risk: str,
    continuity_degradation_risk: str,
) -> str:
    if preserve_existing_direction and (
        refinement_pressure_risk == "high" or continuity_degradation_risk == "high"
    ):
        return "preserve_stabilized_direction_and_limit_changes_to_unresolved_areas"
    if preserve_existing_direction:
        return "targeted_continuity_refinement_only"
    return "bounded_refinement_without_stabilized_area_constraints"


def _forbidden_boundary_checks(
    request: VisualContinuityMemoryRequest,
) -> tuple[str, ...]:
    checks: set[str] = set()
    if not request.user_final_authority:
        checks.add("user_final_authority_required")
    if request.uncontrolled_memory_persistence_requested:
        checks.add("uncontrolled_memory_persistence_forbidden")
    if request.requested_output not in {
        "visual_continuity_guidance",
        "continuity_constraints",
        "convergence_assessment",
    }:
        checks.add("unsupported_guidance_output_requires_approval")
    for observation in request.observations:
        if not observation.user_final_authority:
            checks.add("observation_user_authority_required")
        if observation.runtime_behavior_changed:
            checks.add("runtime_behavior_mutation_forbidden")
        if observation.governance_semantics_changed:
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
            "visual_continuity_guidance",
            "continuity_constraints",
            "convergence_assessment",
        ],
        "autonomous_learning_authorized": False,
        "execution_authority_granted": False,
        "hidden_adaptation_performed": False,
        "mutation_performed": False,
        "primitive_id": PRIMITIVE_ID,
        "scope_id": SCOPE_ID,
        "uncontrolled_memory_persistence_allowed": False,
        "user_final_authority_required": True,
    }
