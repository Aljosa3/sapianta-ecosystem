from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

from aigol.runtime.candidate_h_founder.orchestration import (
    CandidateOrchestrationError,
    orchestrate_fixture_candidate_h,
)
from aigol.runtime.candidate_h_founder.persistence import CandidateHStore

from test_g77_candidate_h_founder_authority import _model, _run, build_fixture


def _invoke(fixture, *, store=None, composition=None):
    active_store = fixture[0] if store is None else store
    active_composition = fixture[5] if composition is None else composition
    return orchestrate_fixture_candidate_h(
        active_store,
        capacity=fixture[1],
        authentication_commitment=fixture[2],
        authentication=fixture[3],
        decision=fixture[4],
        composition=active_composition,
    )


def test_first_valid_fixture_composition_consumes_one_bounded_effect(tmp_path: Path) -> None:
    result = _run(build_fixture(tmp_path))
    assert result.outcome == "FIXTURE_EFFECT_CONSUMED"
    assert result.fixture_effects_applied == 1
    assert result.production_effects_applied == 0
    assert result.fixture_authority_permanently_exhausted is True


def test_identical_observation_is_exhausted_and_creates_no_second_effect(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    first = _invoke(fixture)
    observed = _invoke(fixture)
    assert first.fixture_effects_applied == 1
    assert observed.outcome == "IDENTICAL_EXHAUSTED_OBSERVATION"
    assert observed.fixture_effects_applied == 0
    assert observed.retained_root_cas.outcome == "IDEMPOTENT"
    assert observed.retained_root_cas.read_back == first.retained_root_cas.read_back


def test_repeated_consumption_never_exceeds_one_effect(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    results = [_invoke(fixture) for _ in range(4)]
    assert sum(result.fixture_effects_applied for result in results) == 1
    assert [result.outcome for result in results[1:]] == [
        "IDENTICAL_EXHAUSTED_OBSERVATION",
        "IDENTICAL_EXHAUSTED_OBSERVATION",
        "IDENTICAL_EXHAUSTED_OBSERVATION",
    ]


def test_concurrent_repetition_has_one_winner_and_no_parallel_effect(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: _invoke(fixture), range(2)))
    assert sum(result.fixture_effects_applied for result in results) == 1
    assert sorted(result.retained_root_cas.outcome for result in results) == [
        "IDEMPOTENT",
        "WON",
    ]
    assert len({result.retained_root_cas.read_back.slot_digest for result in results}) == 1


def test_divergent_retry_cannot_escape_exhaustion(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    _invoke(fixture)
    original = fixture[5]
    divergent_root = _model(
        "ConstitutionalRootEvolutionSnapshotV4",
        predecessor_snapshot_root_identity=original.resulting_root.predecessor_snapshot_root_identity,
        predecessor_snapshot_root_digest=original.resulting_root.predecessor_snapshot_root_digest,
        predecessor_root_generation=1,
        root_generation=2,
        meta_repair_state_identity=original.meta_repair_state.meta_repair_state_identity,
        meta_repair_state_digest=original.meta_repair_state.meta_repair_state_digest,
        cap_reachability_state_identity=original.cap_reachability_state.reachability_state_identity,
        cap_reachability_state_digest=original.cap_reachability_state.reachability_state_digest,
        serialization_coordinator_state_identity=original.terminal_coordinator_state.coordinator_state_identity,
        serialization_coordinator_state_digest=original.terminal_coordinator_state.coordinator_state_digest,
        normative_registry_entry_count=1,
        source_evidence_registry_epoch=1,
        effective_logical_instant="fixture:divergent-root-two",
    )
    divergent = replace(original, resulting_root=divergent_root)
    with pytest.raises(CandidateOrchestrationError, match="FIXTURE_AUTHORITY_EXHAUSTED"):
        _invoke(fixture, composition=divergent)


@pytest.mark.parametrize("prohibited_operation", ["reset", "reissue", "revive"])
def test_reset_reissue_and_revival_are_not_orchestration_capabilities(
    tmp_path: Path,
    prohibited_operation: str,
) -> None:
    fixture = build_fixture(tmp_path)
    _invoke(fixture)
    assert not hasattr(fixture[5], prohibited_operation)
    assert not hasattr(orchestrate_fixture_candidate_h, prohibited_operation)
    observed = _invoke(fixture)
    assert observed.fixture_effects_applied == 0
    assert observed.fixture_authority_permanently_exhausted is True


def test_process_restart_does_not_restore_fixture_authority(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    first = _invoke(fixture)
    reopened = CandidateHStore(tmp_path / "store")
    after_restart = _invoke(fixture, store=reopened)
    assert first.fixture_effects_applied == 1
    assert after_restart.fixture_effects_applied == 0
    assert after_restart.outcome == "IDENTICAL_EXHAUSTED_OBSERVATION"
    assert after_restart.retained_root_cas.read_back == first.retained_root_cas.read_back


def test_retained_root_coordinate_remains_unique(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    first = _invoke(fixture)
    observed = _invoke(fixture)
    predecessor = fixture[5].retained_root_predecessor
    current = fixture[0].read_slot(
        predecessor.owner,
        predecessor.slot_identity,
        predecessor.slot_epoch,
    )
    assert current == first.retained_root_cas.read_back == observed.retained_root_cas.read_back
    assert current.generation == predecessor.generation + 1
    assert current.slot_identity == predecessor.slot_identity
    assert current.slot_epoch == predecessor.slot_epoch
