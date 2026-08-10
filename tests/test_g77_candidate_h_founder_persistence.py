from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from threading import Barrier, Thread

import pytest

from aigol.runtime.candidate_h_founder import persistence
from aigol.runtime.candidate_h_founder.models import HUMAN_AUTHORITY, MODEL_REGISTRY
from aigol.runtime.candidate_h_founder.persistence import (
    ArtifactAddress,
    CandidateHStore,
    CandidatePersistenceError,
    InjectedPersistenceCrash,
)
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    expected_artifact_identifiers,
)


MODEL_TYPE = MODEL_REGISTRY["ExternalConstituentHumanFirstAdoptionDecisionV2"]
SLOT = "fixture:human-decision-slot"
EPOCH = 1


def _values(**changes: object) -> dict[str, object]:
    values = {field.name: f"fixture:{field.name}" for field in fields(MODEL_TYPE)}
    values.update(MODEL_TYPE.CONSTANTS)
    for name, allowed in MODEL_TYPE.ALLOWED_VALUES.items():
        values[name] = sorted(allowed, key=repr)[0]
    for name in MODEL_TYPE.REQUIRED_NULL_FIELDS:
        values[name] = None
    values.update(changes)
    return values


def _decision(label: str = "one"):
    pending = MODEL_TYPE(**_values(decision_effective_at=f"fixture:instant:{label}"))
    idem, identity, digest = expected_artifact_identifiers(pending)
    spec = ARTIFACT_IDENTITY_SPECS[MODEL_TYPE]
    return replace(
        pending,
        idempotency_identity=idem,
        **{spec.identity_field: identity, spec.digest_field: digest},
    )


def _address(model) -> ArtifactAddress:
    spec = ARTIFACT_IDENTITY_SPECS[type(model)]
    return ArtifactAddress(
        getattr(model, spec.identity_field), getattr(model, spec.digest_field)
    )


def _crash_at(target: str):
    def hook(point: str) -> None:
        if point == target:
            raise InjectedPersistenceCrash(target)

    return hook


def _initial_cas(store: CandidateHStore, model, **changes):
    values = {
        "owner": HUMAN_AUTHORITY,
        "slot_identity": SLOT,
        "slot_epoch": EPOCH,
        "expected_slot_digest": None,
        "expected_status": None,
        "successor_status": "FINAL",
        "model": model,
        "logical_instant": "fixture:cas:one",
    }
    values.update(changes)
    return store.compare_and_swap(**values)


def test_immutable_write_persists_exact_cj1_and_reads_identical_model(tmp_path: Path) -> None:
    model = _decision()
    store = CandidateHStore(tmp_path / "store")

    result = store.write_immutable(model)
    reconstructed, read_back = store.read_immutable(MODEL_TYPE, _address(model))

    assert result.outcome == "CREATED"
    assert result.read_back == read_back
    assert read_back.canonical_bytes == model.to_cj1_bytes()
    assert reconstructed == model
    assert read_back.address == _address(model)


def test_same_immutable_value_is_idempotent(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()

    assert store.write_immutable(model).outcome == "CREATED"
    assert store.write_immutable(model).outcome == "IDEMPOTENT"


def test_stage_2_validation_failure_precedes_any_write(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = replace(_decision(), artifact_digest="sha256:" + "0" * 64)

    with pytest.raises(CandidateValidationError, match="ARTIFACT_DIGEST_MISMATCH"):
        store.write_immutable(model)

    assert list((tmp_path / "store" / "records").glob("*.cj1")) == []


def test_existing_identity_with_different_bytes_fails_closed(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()
    store.write_immutable(model)
    record_path = store._record_path(model.artifact_identity)
    record_path.write_bytes(_decision("different").to_cj1_bytes())

    with pytest.raises(CandidatePersistenceError, match="IMMUTABLE_RECORD_CONFLICT"):
        store.write_immutable(model)


def test_missing_and_corrupt_immutable_records_fail_closed(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()
    address = _address(model)
    with pytest.raises(CandidatePersistenceError, match="MISSING_IMMUTABLE_RECORD"):
        store.read_immutable(MODEL_TYPE, address)

    store._record_path(address.artifact_identity).write_bytes(b'{"partial":')
    with pytest.raises(CandidatePersistenceError, match="CORRUPT_IMMUTABLE_RECORD"):
        store.read_immutable(MODEL_TYPE, address)


def test_initial_cas_wins_and_authoritative_read_back_matches(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()

    result = _initial_cas(store, model)
    restarted = CandidateHStore(tmp_path / "store")

    assert result.outcome == "WON"
    assert restarted.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH) == result.read_back
    assert result.read_back.generation == 1
    assert result.read_back.predecessor_slot_digest is None
    assert result.read_back.predecessor_status is None
    assert result.read_back.artifact_identity == model.artifact_identity


def test_identical_cas_delivery_returns_same_read_back(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()
    winner = _initial_cas(store, model)
    duplicate = _initial_cas(store, model)

    assert duplicate.outcome == "IDEMPOTENT"
    assert duplicate.read_back == winner.read_back
    assert duplicate.read_back.generation == 1


def test_different_value_reuse_of_occupied_slot_conflicts(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    winner = _initial_cas(store, _decision("winner"))
    loser = _initial_cas(store, _decision("loser"), logical_instant="fixture:cas:loser")

    assert loser.outcome == "CONFLICT"
    assert loser.read_back == winner.read_back
    assert store.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH).generation == 1


def test_exact_predecessor_allows_one_forward_successor(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    first = _initial_cas(store, _decision("first"), successor_status="AUTHENTICATING")
    second_model = _decision("second")

    second = store.compare_and_swap(
        owner=HUMAN_AUTHORITY,
        slot_identity=SLOT,
        slot_epoch=EPOCH,
        expected_slot_digest=first.read_back.slot_digest,
        expected_status="AUTHENTICATING",
        successor_status="FINAL",
        model=second_model,
        logical_instant="fixture:cas:two",
    )

    assert second.outcome == "WON"
    assert second.read_back.generation == 2
    assert second.read_back.predecessor_slot_digest == first.read_back.slot_digest
    assert second.read_back.predecessor_status == "AUTHENTICATING"


def test_wrong_predecessor_returns_conflict_read_back(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    first = _initial_cas(store, _decision("first"))

    result = store.compare_and_swap(
        owner=HUMAN_AUTHORITY,
        slot_identity=SLOT,
        slot_epoch=EPOCH,
        expected_slot_digest="sha256:" + "0" * 64,
        expected_status="FINAL",
        successor_status="OTHER_FINAL",
        model=_decision("other"),
        logical_instant="fixture:cas:other",
    )

    assert result.outcome == "CONFLICT"
    assert result.read_back == first.read_back


def test_concurrent_competitors_have_exactly_one_winner(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    barrier = Barrier(3)
    outcomes: list[str] = []

    def compete(label: str) -> None:
        barrier.wait()
        result = _initial_cas(
            store, _decision(label), logical_instant=f"fixture:cas:{label}"
        )
        outcomes.append(result.outcome)

    threads = [Thread(target=compete, args=(label,)) for label in ("a", "b")]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["CONFLICT", "WON"]
    assert store.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH).generation == 1


@pytest.mark.parametrize(
    ("point", "record_exists"),
    [
        (persistence.IMMUTABLE_AFTER_TEMP_FSYNC, False),
        (persistence.IMMUTABLE_AFTER_PUBLISH, True),
    ],
)
def test_immutable_crash_boundary_has_deterministic_restart(
    tmp_path: Path, point: str, record_exists: bool
) -> None:
    root = tmp_path / "store"
    model = _decision()
    store = CandidateHStore(root)
    with pytest.raises(InjectedPersistenceCrash, match=point):
        store.write_immutable(model, _fixture_crash_hook=_crash_at(point))

    restarted = CandidateHStore(root)
    if record_exists:
        reconstructed, _ = restarted.read_immutable(MODEL_TYPE, _address(model))
        assert reconstructed == model
        assert restarted.write_immutable(model).outcome == "IDEMPOTENT"
    else:
        with pytest.raises(CandidatePersistenceError, match="MISSING_IMMUTABLE_RECORD"):
            restarted.read_immutable(MODEL_TYPE, _address(model))
        assert restarted.write_immutable(model).outcome == "CREATED"


@pytest.mark.parametrize(
    ("point", "slot_exists"),
    [
        (persistence.SLOT_AFTER_GENERATION_FSYNC, False),
        (persistence.SLOT_AFTER_GENERATION_PUBLISH, False),
        (persistence.SLOT_AFTER_POINTER_FSYNC, False),
        (persistence.SLOT_AFTER_POINTER_REPLACE, True),
    ],
)
def test_slot_crash_boundary_has_zero_or_one_winner_and_retry_read_back(
    tmp_path: Path, point: str, slot_exists: bool
) -> None:
    root = tmp_path / "store"
    model = _decision()
    store = CandidateHStore(root)
    with pytest.raises(InjectedPersistenceCrash, match=point):
        _initial_cas(store, model, _fixture_crash_hook=_crash_at(point))

    restarted = CandidateHStore(root)
    if slot_exists:
        persisted = restarted.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH)
        retry = _initial_cas(restarted, model)
        assert retry.outcome == "IDEMPOTENT"
        assert retry.read_back == persisted
    else:
        with pytest.raises(CandidatePersistenceError, match="MISSING_SLOT"):
            restarted.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH)
        retry = _initial_cas(restarted, model)
        assert retry.outcome == "WON"
    assert restarted.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH).generation == 1


def test_cas_uses_file_and_directory_fsync_and_atomic_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fsync_calls: list[int] = []
    replace_calls: list[tuple[object, object]] = []
    real_fsync = persistence.os.fsync
    real_replace = persistence.os.replace

    def tracked_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    def tracked_replace(source, destination) -> None:
        replace_calls.append((source, destination))
        real_replace(source, destination)

    monkeypatch.setattr(persistence.os, "fsync", tracked_fsync)
    monkeypatch.setattr(persistence.os, "replace", tracked_replace)
    _initial_cas(CandidateHStore(tmp_path / "store"), _decision())

    assert len(fsync_calls) >= 6
    assert len(replace_calls) == 1


def test_partial_or_corrupt_current_slot_fails_closed(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    winner = _initial_cas(store, _decision())
    slot_key = store._slot_key(HUMAN_AUTHORITY, SLOT, EPOCH)
    generation = store._generation_path(slot_key, 1, winner.read_back.slot_digest)
    generation.write_bytes(b"{}")

    with pytest.raises(CandidatePersistenceError, match="CORRUPT_SLOT"):
        store.read_slot(HUMAN_AUTHORITY, SLOT, EPOCH)


def test_read_only_capability_has_no_writer_or_cas(tmp_path: Path) -> None:
    read_only = CandidateHStore(tmp_path / "store").readonly()

    assert hasattr(read_only, "read_immutable")
    assert hasattr(read_only, "read_slot")
    assert not hasattr(read_only, "write_immutable")
    assert not hasattr(read_only, "compare_and_swap")


def test_owner_mismatch_and_expected_half_pair_fail_closed(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    model = _decision()
    with pytest.raises(CandidatePersistenceError, match="PERSISTENCE_OWNER_MISMATCH"):
        _initial_cas(store, model, owner="fixture:not-human-authority")
    with pytest.raises(CandidatePersistenceError, match="INVALID_EXPECTED_SLOT"):
        _initial_cas(store, model, expected_slot_digest="sha256:" + "0" * 64)


def test_stage_3_module_has_no_stage_4_or_root_dependency() -> None:
    source = Path(persistence.__file__).read_text(encoding="utf-8")

    assert "from .authentication" not in source
    assert "from .orchestration" not in source
    assert "BEGIN(" not in source
    assert "root mutation" not in source.lower()
