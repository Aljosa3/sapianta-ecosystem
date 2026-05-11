"""Bounded adaptive intent interpretation for AGOL refinement work.

This module detects refinement stagnation and perceptual-impact mismatch for
AGOL-assisted development. It is proposal-only: it never modifies files,
executes commands, authorizes redesigns, or grants runtime authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PRIMITIVE_ID = "AGOL_ADAPTIVE_INTENT_AWARENESS_V1"
SCOPE_ID = "BOUNDED_REFINEMENT_INTERPRETATION_ONLY"
NO_COMMAND: tuple[str, ...] = ()
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/LLM_ROLE_AND_BOUNDARY_MODEL_V1.md",
    "docs/governance/AGOL_ADAPTIVE_INTENT_AWARENESS_V1.md",
    "runtime/governance/agol_adaptive_intent.py",
    "tests/test_agol_adaptive_intent.py",
)

CONTINUITY_REFINEMENT_MODE = "continuity_refinement"
BOUNDED_RESTRUCTURING_MODE = "bounded_restructuring"
PERCEPTUAL_IMPACT_MODE = "perceptual_impact"
OPERATIONAL_CLARITY_MODE = "operational_clarity"
MONETIZATION_OPTIMIZATION_MODE = "monetization_optimization"
ENTERPRISE_TRUST_MODE = "enterprise_trust"

REFINEMENT_MODES = (
    CONTINUITY_REFINEMENT_MODE,
    BOUNDED_RESTRUCTURING_MODE,
    PERCEPTUAL_IMPACT_MODE,
    OPERATIONAL_CLARITY_MODE,
    MONETIZATION_OPTIMIZATION_MODE,
    ENTERPRISE_TRUST_MODE,
)

LOW_MUTATION_MAGNITUDES = ("micro", "minor")
LOW_PERCEPTUAL_DELTAS = ("none", "low")
HIGH_IMPACT_EXPECTATIONS = ("moderate", "high", "transformational")
HIGHER_IMPACT_MESSAGE = (
    "Current refinement magnitude appears too conservative relative to the requested impact."
)

DISSATISFACTION_TERMS = (
    "changed almost nothing",
    "crowded",
    "does not feel",
    "doesn't feel",
    "insufficient",
    "low impact",
    "not enough",
    "not premium",
    "still",
    "too conservative",
    "underpowered",
)

OPERATIONAL_CLARITY_TERMS = ("clarity", "understand", "readable", "explain")
MONETIZATION_TERMS = ("monetization", "conversion", "pricing", "buyer", "revenue")
ENTERPRISE_TRUST_TERMS = ("enterprise", "trust", "institutional", "premium", "credible")


@dataclass(frozen=True)
class RefinementIteration:
    request_text: str
    mutation_magnitude: str
    perceptual_delta: str
    requested_impact: str = "moderate"
    dissatisfaction_signal: bool | None = None
    scope_preserved: bool = True
    runtime_behavior_changed: bool = False
    governance_semantics_changed: bool = False

    def has_dissatisfaction_signal(self) -> bool:
        if self.dissatisfaction_signal is not None:
            return self.dissatisfaction_signal
        normalized = self.request_text.lower()
        return any(term in normalized for term in DISSATISFACTION_TERMS)

    def is_low_impact_iteration(self) -> bool:
        return (
            self.mutation_magnitude in LOW_MUTATION_MAGNITUDES
            and self.perceptual_delta in LOW_PERCEPTUAL_DELTAS
        )

    def expects_more_than_low_impact(self) -> bool:
        return self.requested_impact in HIGH_IMPACT_EXPECTATIONS

    def to_dict(self) -> dict[str, Any]:
        return {
            "dissatisfaction_signal": self.has_dissatisfaction_signal(),
            "governance_semantics_changed": self.governance_semantics_changed,
            "mutation_magnitude": self.mutation_magnitude,
            "perceptual_delta": self.perceptual_delta,
            "request_text": self.request_text,
            "requested_impact": self.requested_impact,
            "runtime_behavior_changed": self.runtime_behavior_changed,
            "scope_preserved": self.scope_preserved,
        }


@dataclass(frozen=True)
class AdaptiveRefinementRequest:
    iterations: tuple[RefinementIteration, ...]
    domain_context: str = "agol_product_ux"
    allowed_modes: tuple[str, ...] = field(default_factory=lambda: REFINEMENT_MODES)
    user_final_authority: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_modes": list(self.allowed_modes),
            "domain_context": self.domain_context,
            "iterations": [iteration.to_dict() for iteration in self.iterations],
            "user_final_authority": self.user_final_authority,
        }


@dataclass(frozen=True)
class AdaptiveRefinementAssessment:
    primitive_id: str
    status: str
    stagnation_detected: bool
    mismatch_detected: bool
    suggested_mode: str
    suggested_message: str
    bounded_escalation_suggested: bool
    autonomous_execution_authorized: bool
    redesign_authority_granted: bool
    runtime_authority_granted: bool
    reason: str
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "autonomous_execution_authorized": self.autonomous_execution_authorized,
            "bounded_escalation_suggested": self.bounded_escalation_suggested,
            "command_hash": self.command_hash,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "mismatch_detected": self.mismatch_detected,
            "primitive_id": self.primitive_id,
            "reason": self.reason,
            "redesign_authority_granted": self.redesign_authority_granted,
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "runtime_authority_granted": self.runtime_authority_granted,
            "scope_hash": self.scope_hash,
            "stagnation_detected": self.stagnation_detected,
            "status": self.status,
            "suggested_message": self.suggested_message,
            "suggested_mode": self.suggested_mode,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_adaptive_refinement_scope() -> dict[str, object]:
    return {
        "allowed_modes": list(REFINEMENT_MODES),
        "forbidden": [
            "autonomous redesign authority",
            "unrestricted exploration",
            "self-directed execution",
            "runtime behavior mutation",
            "governance semantic mutation",
            "deployment automation",
            "orchestration authority",
        ],
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
        "execution_authority_granted": False,
    }


def detect_refinement_stagnation(
    iterations: tuple[RefinementIteration, ...],
    *,
    review_window: int = 4,
) -> bool:
    recent = iterations[-review_window:]
    low_impact_dissatisfied = [
        iteration
        for iteration in recent
        if iteration.is_low_impact_iteration() and iteration.has_dissatisfaction_signal()
    ]
    return len(low_impact_dissatisfied) >= 2


def detect_perceptual_impact_mismatch(
    iterations: tuple[RefinementIteration, ...],
) -> bool:
    if not iterations:
        return False

    latest = iterations[-1]
    latest_mismatch = (
        latest.has_dissatisfaction_signal()
        and latest.is_low_impact_iteration()
        and latest.expects_more_than_low_impact()
    )
    return latest_mismatch or detect_refinement_stagnation(iterations)


def suggest_refinement_mode(
    request: AdaptiveRefinementRequest,
    *,
    stagnation_detected: bool | None = None,
    mismatch_detected: bool | None = None,
) -> str:
    iterations = request.iterations
    stagnation = (
        detect_refinement_stagnation(iterations)
        if stagnation_detected is None
        else stagnation_detected
    )
    mismatch = (
        detect_perceptual_impact_mismatch(iterations)
        if mismatch_detected is None
        else mismatch_detected
    )
    combined_text = " ".join(iteration.request_text.lower() for iteration in iterations)

    if mismatch:
        if stagnation and BOUNDED_RESTRUCTURING_MODE in request.allowed_modes:
            return BOUNDED_RESTRUCTURING_MODE
        if PERCEPTUAL_IMPACT_MODE in request.allowed_modes:
            return PERCEPTUAL_IMPACT_MODE
    if any(term in combined_text for term in OPERATIONAL_CLARITY_TERMS):
        return OPERATIONAL_CLARITY_MODE
    if any(term in combined_text for term in MONETIZATION_TERMS):
        return MONETIZATION_OPTIMIZATION_MODE
    if any(term in combined_text for term in ENTERPRISE_TRUST_TERMS):
        return ENTERPRISE_TRUST_MODE
    return CONTINUITY_REFINEMENT_MODE


def assess_refinement_intent(
    request: AdaptiveRefinementRequest,
) -> AdaptiveRefinementAssessment:
    forbidden = _forbidden_boundary_checks(request)
    stagnation = detect_refinement_stagnation(request.iterations)
    mismatch = detect_perceptual_impact_mismatch(request.iterations)
    suggested_mode = suggest_refinement_mode(
        request,
        stagnation_detected=stagnation,
        mismatch_detected=mismatch,
    )
    bounded_escalation = mismatch or stagnation
    status = (
        "BOUNDED_ESCALATION_SUGGESTED"
        if bounded_escalation
        else "CONTINUITY_REFINEMENT_APPROPRIATE"
    )
    suggested_message = (
        HIGHER_IMPACT_MESSAGE
        if bounded_escalation
        else "Current refinement mode remains proportionate to the detected intent."
    )
    reason = (
        "repeated low-impact refinements with dissatisfaction require a higher-impact proposal"
        if stagnation
        else "latest refinement impact is below the requested perceptual outcome"
        if mismatch
        else "no refinement stagnation or perceptual-impact mismatch detected"
    )

    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=NO_COMMAND,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "autonomous_execution_authorized": False,
        "bounded_escalation_suggested": bounded_escalation,
        "command_hash": replay_identity["command_hash"],
        "forbidden_boundary_checks": list(forbidden),
        "mismatch_detected": mismatch,
        "primitive_id": replay_identity["primitive_id"],
        "reason": reason,
        "redesign_authority_granted": False,
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "runtime_authority_granted": False,
        "scope_hash": replay_identity["scope_hash"],
        "stagnation_detected": stagnation,
        "status": status,
        "suggested_message": suggested_message,
        "suggested_mode": suggested_mode,
    }
    return AdaptiveRefinementAssessment(
        primitive_id=str(replay_identity["primitive_id"]),
        status=status,
        stagnation_detected=stagnation,
        mismatch_detected=mismatch,
        suggested_mode=suggested_mode,
        suggested_message=suggested_message,
        bounded_escalation_suggested=bounded_escalation,
        autonomous_execution_authorized=False,
        redesign_authority_granted=False,
        runtime_authority_granted=False,
        reason=reason,
        forbidden_boundary_checks=forbidden,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _forbidden_boundary_checks(
    request: AdaptiveRefinementRequest,
) -> tuple[str, ...]:
    checks: list[str] = []
    if not request.user_final_authority:
        checks.append("user_final_authority_required")
    if any(mode not in REFINEMENT_MODES for mode in request.allowed_modes):
        checks.append("unknown_refinement_mode_forbidden")
    for iteration in request.iterations:
        if iteration.runtime_behavior_changed:
            checks.append("runtime_behavior_mutation_forbidden")
        if iteration.governance_semantics_changed:
            checks.append("governance_semantic_mutation_forbidden")
        if not iteration.scope_preserved:
            checks.append("scope_expansion_requires_approval")
    return tuple(sorted(set(checks)))


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
        "allowed_modes": list(REFINEMENT_MODES),
        "execution_authority_granted": False,
        "primitive_id": PRIMITIVE_ID,
        "scope_id": SCOPE_ID,
        "user_final_authority_required": True,
    }
