from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


SESSION_ID_PATTERN = re.compile(r"^SESSION-(\d{6})$")
REPLAY_ID_PATTERN = re.compile(r"^PRESSURE-REPLAY-(\d{6})$")


@dataclass(frozen=True)
class PressureValidationResult:
    status: str
    reasons: tuple[str, ...]
    fail_closed: bool
    append_only_preserved: bool
    mutation_performed: bool
    orchestration_requested: bool = False
    adaptive_runtime_requested: bool = False
    cognition_requested: bool = False
    governance_authority_expanded: bool = False


def _fail(*reasons: str, orchestration_requested: bool = False, adaptive_runtime_requested: bool = False, cognition_requested: bool = False) -> PressureValidationResult:
    return PressureValidationResult(
        status="FAIL_CLOSED",
        reasons=tuple(reasons),
        fail_closed=True,
        append_only_preserved=True,
        mutation_performed=False,
        orchestration_requested=orchestration_requested,
        adaptive_runtime_requested=adaptive_runtime_requested,
        cognition_requested=cognition_requested,
        governance_authority_expanded=False,
    )


def _valid() -> PressureValidationResult:
    return PressureValidationResult(
        status="VALIDATED",
        reasons=("continuity_valid",),
        fail_closed=False,
        append_only_preserved=True,
        mutation_performed=False,
        governance_authority_expanded=False,
    )


def validate_replay_chain(entries: Iterable[dict[str, object]]) -> PressureValidationResult:
    materialized = list(entries)
    ids = [str(entry.get("replay_id", "")) for entry in materialized]

    if len(ids) != len(set(ids)):
        return _fail("duplicate_replay_identity")

    numbers: list[int] = []
    for replay_id in ids:
        match = REPLAY_ID_PATTERN.match(replay_id)
        if match is None:
            return _fail("malformed_replay_identity")
        numbers.append(int(match.group(1)))

    if numbers != sorted(numbers):
        return _fail("non_monotonic_replay_ordering")

    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        return _fail("replay_gap")

    roots = 0
    previous_id: str | None = None
    for entry in materialized:
        replay_id = str(entry["replay_id"])
        parent_id = entry.get("parent_replay_id")
        if parent_id is None:
            roots += 1
        elif parent_id != previous_id:
            return _fail("corrupted_replay_ancestry")
        previous_id = replay_id

    if roots != 1:
        return _fail("replay_continuity_fragmentation")

    return _valid()


def validate_governance_alignment(state: dict[str, object]) -> PressureValidationResult:
    if state.get("lineage_consistent") is not True:
        return _fail("invalid_governance_lineage_reference")
    if state.get("topology_valid") is not True:
        return _fail("invalid_governance_topology_reference")
    if state.get("namespace_stable") is not True:
        return _fail("namespace_continuity_divergence")
    if state.get("replay_matches_governance") is not True:
        return _fail("replay_governance_mismatch")
    if state.get("stabilization_boundary_preserved") is not True:
        return _fail("stabilization_boundary_violation")
    return _valid()


def validate_session_continuity(sessions: Iterable[dict[str, object]]) -> PressureValidationResult:
    materialized = list(sessions)
    ids = [str(session.get("session_id", "")) for session in materialized]

    if len(ids) != len(set(ids)):
        return _fail("duplicate_session_identity")

    numbers: list[int] = []
    for session_id in ids:
        match = SESSION_ID_PATTERN.match(session_id)
        if match is None:
            return _fail("malformed_session_identity")
        numbers.append(int(match.group(1)))

    if numbers != sorted(numbers):
        return _fail("invalid_session_transition_order")

    seen: set[str] = set()
    roots = 0
    for session in materialized:
        session_id = str(session["session_id"])
        parent_id = session.get("parent_session_id")
        if parent_id is None:
            roots += 1
        elif parent_id not in seen:
            return _fail("orphan_session_lineage")
        if session.get("ambiguous_transition") is True:
            return _fail("cross_session_continuity_ambiguity")
        if session.get("lineage_claims", 1) != 1:
            return _fail("multi_lineage_continuity_pressure")
        seen.add(session_id)

    if roots != 1:
        return _fail("continuity_fragmentation")

    return _valid()


def validate_bounded_refinement_pressure(proposal: dict[str, object]) -> PressureValidationResult:
    pressure_type = str(proposal.get("pressure_type", ""))
    bounded_evidence = proposal.get("bounded_refinement_evidence") is True
    replay_safe = proposal.get("replay_safe") is True
    stabilization_preserved = proposal.get("stabilization_before_expansion") is True

    if pressure_type in {"orchestration", "subsystem_multiplication", "architecture_explosion"} and not bounded_evidence:
        return _fail(
            "bounded_refinement_required_before_expansion",
            orchestration_requested=pressure_type == "orchestration",
        )
    if pressure_type in {"adaptive_runtime", "semantic_amplification"}:
        return _fail(
            "adaptive_or_semantic_activation_rejected",
            adaptive_runtime_requested=pressure_type == "adaptive_runtime",
            cognition_requested=pressure_type == "semantic_amplification",
        )
    if pressure_type == "recursive_governance_expansion" and not replay_safe:
        return _fail("replay_safe_governance_continuity_required")
    if not stabilization_preserved:
        return _fail("stabilization_before_expansion_required")

    return _valid()
