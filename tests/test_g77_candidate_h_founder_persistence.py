from __future__ import annotations

import json
from dataclasses import fields, replace
from pathlib import Path
from threading import Barrier, Thread

import pytest

from aigol.runtime.candidate_h_founder import persistence
from aigol.runtime.candidate_h_founder.cj1 import cj1_encode, sha256_hex
from aigol.runtime.candidate_h_founder.models import HUMAN_AUTHORITY, MODEL_REGISTRY
from aigol.runtime.candidate_h_founder.persistence import (
    ArtifactAddress,
    CandidateHStore,
    CandidatePersistenceError,
    InjectedPersistenceCrash,
    SUBCONTRACT_KIND_SPECS,
    SubcontractAddress,
)
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    expected_artifact_identifiers,
)


MODEL_TYPE = MODEL_REGISTRY["ExternalConstituentHumanFirstAdoptionDecisionV2"]
SLOT = "fixture:human-decision-slot"
EPOCH = 1
CAS_KINDS = tuple(
    kind for kind, spec in SUBCONTRACT_KIND_SPECS.items() if spec.mode == "CAS"
)
IMMUTABLE_KINDS = tuple(
    kind for kind, spec in SUBCONTRACT_KIND_SPECS.items() if spec.mode == "IMMUTABLE"
)


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


def _sha(value: str) -> str:
    return sha256_hex(value.encode("utf-8"))


def _pair(prefix: str | None, label: str) -> tuple[str, str]:
    digest_hex = _sha(label)
    return f"{prefix or 'external-fixture'}:{digest_hex}", f"sha256:{digest_hex}"


def _subcontract_address(kind: str, canonical_bytes: bytes) -> SubcontractAddress:
    spec = SUBCONTRACT_KIND_SPECS[kind]
    digest_hex = sha256_hex(canonical_bytes)
    return SubcontractAddress(
        kind,
        f"{spec.prefix}:{digest_hex}",
        f"sha256:{digest_hex}",
    )


def _subcontract_body(kind: str, **changes: object) -> dict[str, object]:
    spec = SUBCONTRACT_KIND_SPECS[kind]
    body: dict[str, object] = {
        name: f"fixture:{kind.lower()}:{name}" for name in spec.field_names
    }
    body.update(spec.fixed_constants)
    for name, allowed in spec.closed_values.items():
        body[name] = sorted(allowed, key=repr)[0]
    for base, prefix in spec.pair_domain_rules.items():
        identity, digest = _pair(prefix, f"{kind}:{base}")
        body[f"{base}_identity"] = identity
        body[f"{base}_digest"] = digest
    for name in spec.field_names:
        if name.endswith("_digest") and name not in {
            f"{base}_digest" for base in spec.pair_bases
        }:
            body[name] = f"sha256:{_sha(f'{kind}:{name}')}"
        if name.endswith("_epoch"):
            body[name] = 1
    body.update(
        producing_owner=HUMAN_AUTHORITY,
        signature="fixture:signature",
        signature_digest=f"sha256:{_sha(f'{kind}:signature')}",
        failure_code=None,
    )
    if kind == "SIGNER_OUTCOME_V1":
        body.update(
            outcome_status="VALID_SIGNATURE_FINAL",
            verification_result="TRUE",
            failure_code=None,
        )
    elif kind == "SIGNER_OUTCOME_READ_BACK_V1":
        body["signer_outcome_status"] = "VALID_SIGNATURE_FINAL"
    elif kind == "AUTHENTICATION_TERMINAL_CAS_V1":
        body.update(
            terminal_authentication_slot_status="AUTHENTICATED_FINAL",
            authentication_result="AUTHENTICATED_VALID",
            signature_verification_result="TRUE",
            conflict_status="NONE",
        )
    elif kind == "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1":
        body.update(
            terminal_authentication_slot_status="AUTHENTICATED_FINAL",
            authentication_result="AUTHENTICATED_VALID",
        )
    body.update(changes)
    return {name: body[name] for name in spec.field_names}


def _seed_subcontract_predecessor(
    store: CandidateHStore,
    kind: str,
    label: str,
):
    spec = SUBCONTRACT_KIND_SPECS[kind]
    body = _subcontract_body(kind)
    owner = body[spec.cas_argument_bindings["owner"]]
    slot_identity = f"fixture:{kind.lower()}:slot:{label}"
    slot_epoch = 1
    expected_status = body[spec.cas_argument_bindings["expected_status"]]
    seed = store.compare_and_swap(
        owner=owner,
        slot_identity=slot_identity,
        slot_epoch=slot_epoch,
        expected_slot_digest=None,
        expected_status=None,
        successor_status=expected_status,
        model=_decision(f"seed:{kind}:{label}"),
        logical_instant=f"fixture:seed:{kind}:{label}",
    )
    return seed.read_back


def _cas_fixture(
    store: CandidateHStore,
    kind: str,
    label: str,
) -> tuple[SubcontractAddress, bytes, dict[str, object]]:
    spec = SUBCONTRACT_KIND_SPECS[kind]
    predecessor = _seed_subcontract_predecessor(store, kind, label)
    successor = {
        "AUTHENTICATION_CLAIM_CAS_V1": "AUTHENTICATING",
        "SIGNER_ACCEPTANCE_CAS_V1": "ACCEPTED_IN_PROGRESS",
        "SIGNER_OUTCOME_V1": "VALID_SIGNATURE_FINAL",
        "AUTHENTICATION_TERMINAL_CAS_V1": "AUTHENTICATED_FINAL",
    }[kind]
    logical_instant = f"fixture:cas:{kind}:{label}"
    arguments = {
        "owner": predecessor.owner,
        "slot_identity": predecessor.slot_identity,
        "slot_epoch": predecessor.slot_epoch,
        "expected_slot_digest": predecessor.slot_digest,
        "expected_status": predecessor.current_status,
        "successor_status": successor,
        "logical_instant": logical_instant,
    }
    body_changes = {
        spec.cas_argument_bindings[argument]: value
        for argument, value in arguments.items()
    }
    body = _subcontract_body(kind, **body_changes)
    canonical_bytes = cj1_encode(body)
    return _subcontract_address(kind, canonical_bytes), canonical_bytes, arguments


def _filesystem_snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


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


def test_all_nine_subcontract_kinds_round_trip_exact_bytes_and_pairs(
    tmp_path: Path,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    observed: set[str] = set()
    for kind in IMMUTABLE_KINDS:
        body = _subcontract_body(kind)
        canonical_bytes = cj1_encode(body)
        address = _subcontract_address(kind, canonical_bytes)
        result = store.write_subcontract(address, canonical_bytes)
        assert result.outcome == "CREATED"
        assert result.read_back == store.read_subcontract(address)
        assert result.read_back.canonical_bytes == canonical_bytes
        assert result.read_back.storage_digest == address.digest
        observed.add(kind)
    for index, kind in enumerate(CAS_KINDS):
        address, canonical_bytes, arguments = _cas_fixture(store, kind, str(index))
        result = store.compare_and_swap_subcontract(
            **arguments,
            address=address,
            canonical_bytes=canonical_bytes,
        )
        assert result.outcome == "WON"
        assert store.read_subcontract(address).canonical_bytes == canonical_bytes
        observed.add(kind)
    assert observed == set(SUBCONTRACT_KIND_SPECS)
    assert len(SUBCONTRACT_KIND_SPECS) == 9


def test_unknown_kind_prefix_digest_and_noncanonical_bytes_fail_before_write(
    tmp_path: Path,
) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    body = _subcontract_body("AUTHENTICATION_OPERATION_V1")
    canonical_bytes = cj1_encode(body)
    address = _subcontract_address("AUTHENTICATION_OPERATION_V1", canonical_bytes)
    initial = _filesystem_snapshot(root)

    with pytest.raises(CandidatePersistenceError, match="UNKNOWN_SUBCONTRACT_KIND"):
        store.write_subcontract(
            SubcontractAddress("UNKNOWN_V1", address.identity, address.digest),
            canonical_bytes,
        )
    with pytest.raises(CandidatePersistenceError, match="SUBCONTRACT_ADDRESS_MISMATCH"):
        store.write_subcontract(
            replace(address, identity=f"wrong-prefix:{address.identity.rsplit(':', 1)[1]}"),
            canonical_bytes,
        )
    with pytest.raises(CandidatePersistenceError, match="SUBCONTRACT_ADDRESS_MISMATCH"):
        store.write_subcontract(
            replace(address, digest="sha256:" + "0" * 64), canonical_bytes
        )
    noncanonical = json.dumps(body, ensure_ascii=False).encode("utf-8")
    with pytest.raises(CandidatePersistenceError, match="INVALID_SUBCONTRACT_INPUT"):
        store.write_subcontract(
            _subcontract_address("AUTHENTICATION_OPERATION_V1", noncanonical),
            noncanonical,
        )
    assert _filesystem_snapshot(root) == initial


def test_subcontract_mode_is_closed(tmp_path: Path) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    immutable_body = _subcontract_body(IMMUTABLE_KINDS[0])
    immutable_bytes = cj1_encode(immutable_body)
    immutable_address = _subcontract_address(IMMUTABLE_KINDS[0], immutable_bytes)
    with pytest.raises(CandidatePersistenceError, match="SUBCONTRACT_MODE_MISMATCH"):
        store.compare_and_swap_subcontract(
            owner=HUMAN_AUTHORITY,
            slot_identity="fixture:mode-slot",
            slot_epoch=1,
            expected_slot_digest=None,
            expected_status=None,
            successor_status="FINAL",
            address=immutable_address,
            canonical_bytes=immutable_bytes,
            logical_instant="fixture:mode",
        )

    cas_body = _subcontract_body(CAS_KINDS[0])
    cas_bytes = cj1_encode(cas_body)
    with pytest.raises(CandidatePersistenceError, match="SUBCONTRACT_MODE_MISMATCH"):
        store.write_subcontract(_subcontract_address(CAS_KINDS[0], cas_bytes), cas_bytes)
    assert _filesystem_snapshot(root) == {}


def test_subcontract_identity_conflict_and_idempotence_share_record_path(
    tmp_path: Path,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    kind = "AUTHENTICATION_OPERATION_V1"
    canonical_bytes = cj1_encode(_subcontract_body(kind))
    address = _subcontract_address(kind, canonical_bytes)
    assert store.write_subcontract(address, canonical_bytes).outcome == "CREATED"
    assert store.write_subcontract(address, canonical_bytes).outcome == "IDEMPOTENT"

    different = cj1_encode(
        _subcontract_body(kind, human_actor_identity="fixture:different-actor")
    )
    store._record_path(address.identity).write_bytes(different)
    with pytest.raises(CandidatePersistenceError, match="IMMUTABLE_RECORD_CONFLICT"):
        store.write_subcontract(address, canonical_bytes)


def test_subcontract_cas_reuses_lock_generation_pointer_and_read_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    called = 0
    shared = CandidateHStore._compare_and_swap_bytes

    def tracked(self, **arguments):
        nonlocal called
        called += 1
        return shared(self, **arguments)

    monkeypatch.setattr(CandidateHStore, "_compare_and_swap_bytes", tracked)
    _initial_cas(store, _decision("shared-model"), slot_identity="fixture:shared:model")
    address, canonical_bytes, arguments = _cas_fixture(
        store, "AUTHENTICATION_CLAIM_CAS_V1", "shared-subcontract"
    )
    result = store.compare_and_swap_subcontract(
        **arguments, address=address, canonical_bytes=canonical_bytes
    )

    assert called == 3  # model seed, subcontract predecessor seed, subcontract CAS
    assert result.read_back.generation == 2
    assert store.read_subcontract(address).canonical_bytes == canonical_bytes
    assert len(list((tmp_path / "store" / "slots").glob("*.current.cj1"))) == 2


def test_historical_generation_read_survives_current_pointer_advance(
    tmp_path: Path,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    first = _initial_cas(
        store,
        _decision("history-one"),
        slot_identity="fixture:history-slot",
        successor_status="AUTHENTICATING",
    )
    second = store.compare_and_swap(
        owner=HUMAN_AUTHORITY,
        slot_identity="fixture:history-slot",
        slot_epoch=EPOCH,
        expected_slot_digest=first.read_back.slot_digest,
        expected_status="AUTHENTICATING",
        successor_status="FINAL",
        model=_decision("history-two"),
        logical_instant="fixture:history:two",
    )

    assert store.read_slot_generation(
        HUMAN_AUTHORITY,
        "fixture:history-slot",
        EPOCH,
        1,
        first.read_back.slot_digest,
    ) == first.read_back
    assert store.read_slot_generation(
        HUMAN_AUTHORITY,
        "fixture:history-slot",
        EPOCH,
        2,
        second.read_back.slot_digest,
    ) == second.read_back


def test_historical_generation_missing_corrupt_and_misbound_fail_closed(
    tmp_path: Path,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    winner = _initial_cas(
        store, _decision("history-negative"), slot_identity="fixture:history-negative"
    )
    with pytest.raises(CandidatePersistenceError, match="MISSING_SLOT"):
        store.read_slot_generation(
            HUMAN_AUTHORITY,
            "fixture:history-negative",
            EPOCH,
            2,
            "sha256:" + "0" * 64,
        )
    with pytest.raises(CandidatePersistenceError, match="MISSING_SLOT"):
        store.read_slot_generation(
            HUMAN_AUTHORITY,
            "fixture:other-slot",
            EPOCH,
            1,
            winner.read_back.slot_digest,
        )
    slot_key = store._slot_key(HUMAN_AUTHORITY, "fixture:history-negative", EPOCH)
    generation_path = store._generation_path(slot_key, 1, winner.read_back.slot_digest)
    generation_path.write_bytes(b"{}")
    with pytest.raises(CandidatePersistenceError, match="CORRUPT_SLOT"):
        store.read_slot_generation(
            HUMAN_AUTHORITY,
            "fixture:history-negative",
            EPOCH,
            1,
            winner.read_back.slot_digest,
        )


def test_read_only_store_adds_only_subcontract_and_historical_reads(
    tmp_path: Path,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    body = _subcontract_body("AUTHENTICATION_OPERATION_V1")
    canonical_bytes = cj1_encode(body)
    address = _subcontract_address("AUTHENTICATION_OPERATION_V1", canonical_bytes)
    store.write_subcontract(address, canonical_bytes)
    slot = _initial_cas(store, _decision("readonly"), slot_identity="fixture:readonly")
    read_only = store.readonly()

    assert read_only.read_subcontract(address) == store.read_subcontract(address)
    assert read_only.read_slot_generation(
        HUMAN_AUTHORITY,
        "fixture:readonly",
        EPOCH,
        1,
        slot.read_back.slot_digest,
    ) == slot.read_back
    assert not hasattr(read_only, "write_subcontract")
    assert not hasattr(read_only, "compare_and_swap_subcontract")
    assert not hasattr(read_only, "repair")
    assert not hasattr(read_only, "sign")


@pytest.mark.parametrize("kind", IMMUTABLE_KINDS)
@pytest.mark.parametrize(
    ("point", "record_exists"),
    [
        (persistence.IMMUTABLE_AFTER_TEMP_FSYNC, False),
        (persistence.IMMUTABLE_AFTER_PUBLISH, True),
    ],
)
def test_subcontract_immutable_crash_points_have_deterministic_restart(
    tmp_path: Path,
    kind: str,
    point: str,
    record_exists: bool,
) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    canonical_bytes = cj1_encode(_subcontract_body(kind))
    address = _subcontract_address(kind, canonical_bytes)
    with pytest.raises(InjectedPersistenceCrash, match=point):
        store.write_subcontract(
            address,
            canonical_bytes,
            _fixture_crash_hook=_crash_at(point),
        )
    restarted = CandidateHStore(root)
    if record_exists:
        assert restarted.read_subcontract(address).canonical_bytes == canonical_bytes
        assert restarted.write_subcontract(address, canonical_bytes).outcome == "IDEMPOTENT"
    else:
        with pytest.raises(CandidatePersistenceError, match="MISSING_IMMUTABLE_RECORD"):
            restarted.read_subcontract(address)
        assert restarted.write_subcontract(address, canonical_bytes).outcome == "CREATED"


@pytest.mark.parametrize("kind", CAS_KINDS)
@pytest.mark.parametrize(
    ("point", "slot_exists"),
    [
        (persistence.SLOT_AFTER_GENERATION_FSYNC, False),
        (persistence.SLOT_AFTER_GENERATION_PUBLISH, False),
        (persistence.SLOT_AFTER_POINTER_FSYNC, False),
        (persistence.SLOT_AFTER_POINTER_REPLACE, True),
    ],
)
def test_subcontract_cas_crash_points_have_zero_or_one_winner(
    tmp_path: Path,
    kind: str,
    point: str,
    slot_exists: bool,
) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    address, canonical_bytes, arguments = _cas_fixture(store, kind, point)
    with pytest.raises(InjectedPersistenceCrash, match=point):
        store.compare_and_swap_subcontract(
            **arguments,
            address=address,
            canonical_bytes=canonical_bytes,
            _fixture_crash_hook=_crash_at(point),
        )
    restarted = CandidateHStore(root)
    if slot_exists:
        persisted = restarted.read_slot(
            arguments["owner"], arguments["slot_identity"], arguments["slot_epoch"]
        )
        retry = restarted.compare_and_swap_subcontract(
            **arguments, address=address, canonical_bytes=canonical_bytes
        )
        assert retry.outcome == "IDEMPOTENT"
        assert retry.read_back == persisted
    else:
        current = restarted.read_slot(
            arguments["owner"], arguments["slot_identity"], arguments["slot_epoch"]
        )
        assert current.current_status == arguments["expected_status"]
        retry = restarted.compare_and_swap_subcontract(
            **arguments, address=address, canonical_bytes=canonical_bytes
        )
        assert retry.outcome == "WON"


def test_registered_model_persistence_api_remains_byte_compatible(tmp_path: Path) -> None:
    test_immutable_write_persists_exact_cj1_and_reads_identical_model(tmp_path)


def test_persistence_dependency_boundary_remains_closed() -> None:
    source = Path(persistence.__file__).read_text(encoding="utf-8")
    assert "from .authentication" not in source
    assert "orchestration" not in source
    assert "Replay" not in source
    assert "CRO" not in source


@pytest.mark.parametrize(
    ("kind", "invalid_variant"),
    [
        ("AUTHENTICATION_OPERATION_V1", "wrong_field_set"),
        ("AUTHENTICATION_OPERATION_V1", "wrong_fixed_constant"),
        ("AUTHENTICATION_OPERATION_V1", "malformed_pair_shape"),
        ("SIGNER_OUTCOME_V1", "invalid_conditional_null"),
        ("SIGNER_OUTCOME_V1", "invalid_state_value"),
    ],
)
def test_public_subcontract_persistence_rejects_semantically_invalid_known_kind_before_write(
    tmp_path: Path,
    kind: str,
    invalid_variant: str,
) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    body = _subcontract_body(kind)
    if invalid_variant == "wrong_field_set":
        body.pop(next(iter(body)))
    elif invalid_variant == "wrong_fixed_constant":
        body["authentication_sequence"] = 2
    elif invalid_variant == "malformed_pair_shape":
        body["external_premise_digest"] = None
    elif invalid_variant == "invalid_conditional_null":
        body["signature"] = None
    elif invalid_variant == "invalid_state_value":
        body["outcome_status"] = "UNKNOWN_FINAL"
    canonical_bytes = cj1_encode(body)
    address = _subcontract_address(kind, canonical_bytes)
    initial = _filesystem_snapshot(root)
    if SUBCONTRACT_KIND_SPECS[kind].mode == "IMMUTABLE":
        operation = lambda: store.write_subcontract(address, canonical_bytes)
    else:
        spec = SUBCONTRACT_KIND_SPECS[kind]
        arguments = {
            argument: body[spec.cas_argument_bindings[argument]]
            for argument in persistence.CAS_ARGUMENT_NAMES
        }
        operation = lambda: store.compare_and_swap_subcontract(
            **arguments, address=address, canonical_bytes=canonical_bytes
        )
    with pytest.raises(
        CandidatePersistenceError, match="SUBCONTRACT_SEMANTIC_ADMISSION_FAILED"
    ):
        operation()
    assert _filesystem_snapshot(root) == initial


def test_read_subcontract_revalidates_frozen_admission_contract(tmp_path: Path) -> None:
    store = CandidateHStore(tmp_path / "store")
    kind = "AUTHENTICATION_OPERATION_V1"
    body = _subcontract_body(kind, authentication_sequence=2)
    canonical_bytes = cj1_encode(body)
    address = _subcontract_address(kind, canonical_bytes)
    store._record_path(address.identity).write_bytes(canonical_bytes)
    with pytest.raises(
        CandidatePersistenceError, match="SUBCONTRACT_SEMANTIC_ADMISSION_FAILED"
    ):
        store.read_subcontract(address)


def test_schema_declaration_order_is_metadata_and_cj1_wire_order_is_canonical(
    tmp_path: Path,
) -> None:
    kind = "AUTHENTICATION_OPERATION_V1"
    spec = SUBCONTRACT_KIND_SPECS[kind]
    assert spec.field_names != tuple(sorted(spec.field_names))
    body = _subcontract_body(kind)
    declaration_order_body = {name: body[name] for name in spec.field_names}
    canonical_bytes = cj1_encode(declaration_order_body)
    assert tuple(json.loads(canonical_bytes).keys()) == tuple(sorted(spec.field_names))
    address = _subcontract_address(kind, canonical_bytes)
    read_back = CandidateHStore(tmp_path / "store").write_subcontract(
        address, canonical_bytes
    ).read_back
    assert read_back.canonical_bytes == canonical_bytes


def test_field_membership_cannot_bypass_strict_cj1_wire_order(tmp_path: Path) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    kind = "AUTHENTICATION_OPERATION_V1"
    spec = SUBCONTRACT_KIND_SPECS[kind]
    body = _subcontract_body(kind)
    noncanonical = json.dumps(
        {name: body[name] for name in spec.field_names},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")
    assert noncanonical != cj1_encode(body)
    hook_called = False

    def hook(_: str) -> None:
        nonlocal hook_called
        hook_called = True

    with pytest.raises(CandidatePersistenceError, match="INVALID_SUBCONTRACT_INPUT"):
        store.write_subcontract(
            _subcontract_address(kind, noncanonical),
            noncanonical,
            _fixture_crash_hook=hook,
        )
    assert not hook_called
    assert _filesystem_snapshot(root) == {}


@pytest.mark.parametrize("subcontract_kind", CAS_KINDS)
@pytest.mark.parametrize("mismatched_argument", persistence.CAS_ARGUMENT_NAMES)
def test_public_subcontract_cas_rejects_every_coordinate_body_mismatch_before_effect(
    tmp_path: Path,
    subcontract_kind: str,
    mismatched_argument: str,
) -> None:
    root = tmp_path / "store"
    store = CandidateHStore(root)
    address, canonical_bytes, arguments = _cas_fixture(
        store, subcontract_kind, mismatched_argument
    )
    alternatives = {
        "owner": "HUMAN_AUTHORITY_DIFFERENT",
        "slot_identity": "fixture:different-slot",
        "slot_epoch": 2,
        "expected_slot_digest": "sha256:" + "0" * 64,
        "expected_status": "DIFFERENT_PREDECESSOR",
        "successor_status": "DIFFERENT_SUCCESSOR",
        "logical_instant": "fixture:different-instant",
    }
    mutated = dict(arguments)
    mutated[mismatched_argument] = alternatives[mismatched_argument]
    initial = _filesystem_snapshot(root)
    hook_called = False

    def hook(_: str) -> None:
        nonlocal hook_called
        hook_called = True

    with pytest.raises(
        CandidatePersistenceError,
        match=(
            "SUBCONTRACT_SEMANTIC_ADMISSION_FAILED:"
            f"cas_binding:{mismatched_argument}"
        ),
    ):
        store.compare_and_swap_subcontract(
            **mutated,
            address=address,
            canonical_bytes=canonical_bytes,
            _fixture_crash_hook=hook,
        )
    assert not hook_called
    assert _filesystem_snapshot(root) == initial


@pytest.mark.parametrize("subcontract_kind", CAS_KINDS)
def test_public_subcontract_cas_exact_binding_reaches_existing_engine(
    tmp_path: Path,
    subcontract_kind: str,
) -> None:
    store = CandidateHStore(tmp_path / "store")
    address, canonical_bytes, arguments = _cas_fixture(
        store, subcontract_kind, "positive"
    )
    result = store.compare_and_swap_subcontract(
        **arguments, address=address, canonical_bytes=canonical_bytes
    )
    assert result.outcome == "WON"
    assert result.read_back.current_status == arguments["successor_status"]
    assert store.read_subcontract(address).canonical_bytes == canonical_bytes
