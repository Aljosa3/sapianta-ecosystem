"""Tests for FINALIZE_RUNTIME_TRANSPORT_PERSISTENCE_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.transport import RuntimeStore, canonical_serialize, reconstruct_runtime_lineage, replay_hash
from aigol.runtime.transport.serialization import load_json


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "transport-v1",
        "package_id": "package-transport-001",
        "provider": "mock",
        "worker_id": "worker-transport-001",
        "task_type": "echo",
        "payload": {"message": "transport persistence"},
        "lineage_refs": [{"ref_type": "runtime_engine_foundation", "hash": "sha256:engine-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _engine(store: RuntimeStore) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_canonical_serialization_is_deterministic() -> None:
    first = canonical_serialize({"b": 2, "a": {"d": 4, "c": 3}})
    second = canonical_serialize({"a": {"c": 3, "d": 4}, "b": 2})

    assert first == second
    assert first == '{"a":{"c":3,"d":4},"b":2}'


def test_replay_hash_is_stable() -> None:
    assert replay_hash({"b": 2, "a": 1}) == replay_hash({"a": 1, "b": 2})


def test_dispatch_and_result_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    artifact = _engine(store).dispatch(_package()).to_dict()

    dispatch = load_json(store.dispatch_path("transport-v1"))
    result = load_json(store.result_path("transport-v1"))

    assert dispatch["runtime_id"] == "transport-v1"
    assert dispatch["replay_hash"].startswith("sha256:")
    assert result["provider_response"] == artifact["provider_response"]
    assert result["boundary_guarantees"]["real_execution"] is False


def test_append_only_duplicate_dispatch_is_blocked(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    duplicate = _engine(store).dispatch(_package()).to_dict()

    assert duplicate["status"] == "FAIL_CLOSED"
    assert duplicate["runtime_dispatch_artifact"]["fail_closed"] is True


def test_store_duplicate_dispatch_raises_fail_closed(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    package = _package()
    artifact = RuntimeEngine()._dispatch_artifact(package, lifecycle=type("L", (), {"state": "DISPATCHED"})())

    store.persist_dispatch(package, artifact)

    with pytest.raises(FailClosedRuntimeError):
        store.persist_dispatch(package, artifact)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_runtime_lineage("transport-v1", tmp_path)

    assert reconstruction["status"] == "RECONSTRUCTED"
    assert reconstruction["dispatch"]["runtime_id"] == "transport-v1"
    assert reconstruction["result"]["runtime_id"] == "transport-v1"
    assert [entry["sequence"] for entry in reconstruction["ledger_entries"]] == list(
        range(len(reconstruction["ledger_entries"]))
    )


def test_corrupted_replay_hash_blocks_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    dispatch_path = store.dispatch_path("transport-v1")
    dispatch = load_json(dispatch_path)
    dispatch["replay_hash"] = "sha256:corrupted"
    dispatch_path.write_text(json.dumps(dispatch, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_runtime_lineage("transport-v1", tmp_path)


def test_missing_artifact_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError):
        reconstruct_runtime_lineage("missing-runtime", tmp_path)


def test_result_is_immutable_after_write(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    package = _package()
    result = _engine(store).dispatch(package)

    with pytest.raises(FailClosedRuntimeError):
        store.persist_result(package, result)


def test_ledger_ordering_is_deterministic(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    entries = store.ledger.read("transport-v1")

    assert [entry["event_type"] for entry in entries] == [
        "DISPATCH_PERSISTED",
        "LIFECYCLE_TRANSITION",
        "LIFECYCLE_TRANSITION",
        "LIFECYCLE_TRANSITION",
        "LIFECYCLE_TRANSITION",
        "LIFECYCLE_TRANSITION",
        "RESULT_PERSISTED",
        "RUNTIME_CLOSED",
        "CONTINUITY_CONTRACT_PERSISTED",
        "RETRY_EVALUATION_PERSISTED",
        "CONTINUITY_RESULT_PERSISTED",
    ]
    assert [entry["sequence"] for entry in entries] == list(range(11))
