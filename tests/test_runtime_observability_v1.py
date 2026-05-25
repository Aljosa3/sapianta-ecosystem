"""Tests for FINALIZE_RUNTIME_OBSERVABILITY_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.observability import (
    CapabilityInspector,
    ContinuityInspector,
    LineageInspector,
    PolicyInspector,
    RuntimeInspector,
)
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _payload():
    return {
        "capability_request": {
            "capability": "analyze_text",
            "target": "inline",
            "request_payload": {"text": "observable runtime", "policy_scope": "ANALYSIS_ONLY"},
        },
        "sandbox": {
            "execution_mode": "MOCK_EXECUTION",
            "allowed_capabilities": ["analyze_text"],
            "denied_capabilities": [
                "shell_execution",
                "subprocess_spawn",
                "filesystem_write",
                "unrestricted_network",
                "worker_spawn",
                "recursive_dispatch",
            ],
            "resource_limits": {"max_memory_mb": 64, "max_runtime_seconds": 1},
            "execution_ttl_seconds": 1,
        },
        "continuity": {
            "continuation_reason": "completed",
            "retry_count": 0,
            "max_retry_limit": 3,
            "parent_runtime_id": "parent-observable-runtime",
        },
    }


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "observability-v1",
        "package_id": "package-observability-001",
        "provider": "mock",
        "worker_id": "worker-observability-001",
        "task_type": "capability",
        "payload": _payload(),
        "lineage_refs": [{"ref_type": "bounded_runtime_continuity", "hash": "sha256:continuity-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _store_with_runtime(tmp_path) -> RuntimeStore:
    store = RuntimeStore(tmp_path)
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    engine.dispatch(_package())
    return store


def test_runtime_inspection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    inspection = RuntimeInspector(store).inspect("observability-v1")

    assert inspection["status"] == "RUNTIME_INSPECTED"
    assert inspection["snapshot"]["lifecycle_state"] == "CLOSED"
    assert inspection["snapshot"]["capability_state"] == "PRESENT"
    assert inspection["snapshot"]["policy_state"] == "PRESENT"
    assert inspection["snapshot"]["continuity_state"] == "PRESENT"


def test_lineage_reconstruction_inspection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    inspection = LineageInspector(store).inspect("observability-v1")

    assert inspection["status"] == "LINEAGE_INSPECTED"
    assert inspection["runtime_lineage"]["status"] == "RECONSTRUCTED"
    assert inspection["capability_lineage"]["status"] == "CAPABILITY_EXECUTION_RECONSTRUCTED"
    assert inspection["continuity_lineage"]["status"] == "CONTINUITY_DECISION_RECONSTRUCTED"


def test_capability_inspection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    inspection = CapabilityInspector(store).inspect("observability-v1")

    assert inspection["status"] == "CAPABILITY_INSPECTED"
    assert inspection["capability_result"]["capability"] == "analyze_text"
    assert inspection["execution_summary"]["word_count"] == 2


def test_policy_inspection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    inspection = PolicyInspector(store).inspect("observability-v1")

    assert inspection["status"] == "POLICY_INSPECTED"
    assert inspection["policy_scope"] == "ANALYSIS_ONLY"
    assert inspection["decision"] == "ALLOW"


def test_continuity_inspection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    inspection = ContinuityInspector(store).inspect("observability-v1")

    assert inspection["status"] == "CONTINUITY_INSPECTED"
    assert inspection["continuation_decision"] == "STOP"
    assert inspection["retry_count"] == 0


def test_deterministic_replay_hashing(tmp_path) -> None:
    first = _store_with_runtime(tmp_path / "first").load_runtime_snapshot("observability-v1")
    second = _store_with_runtime(tmp_path / "second").load_runtime_snapshot("observability-v1")

    assert first["replay_hash"] == second["replay_hash"]


def test_append_only_snapshot_persistence(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    snapshot = load_json(store.runtime_snapshot_path("observability-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_runtime_snapshot("observability-v1", snapshot)


def test_fail_closed_corruption_detection(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    snapshot_path = store.runtime_snapshot_path("observability-v1")
    snapshot = load_json(snapshot_path)
    snapshot["replay_hash"] = "sha256:corrupted"
    snapshot_path.write_text(json.dumps(snapshot, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        store.load_runtime_snapshot("observability-v1")


def test_immutable_snapshot_guarantees(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    snapshot = store.load_runtime_snapshot("observability-v1")

    assert snapshot["replay_hash"] == replay_hash({k: v for k, v in snapshot.items() if k != "replay_hash"})


def test_read_only_observability_guarantees(tmp_path) -> None:
    store = _store_with_runtime(tmp_path)
    before = store.ledger.read("observability-v1")

    RuntimeInspector(store).inspect("observability-v1")
    LineageInspector(store).inspect("observability-v1")
    CapabilityInspector(store).inspect("observability-v1")
    PolicyInspector(store).inspect("observability-v1")
    ContinuityInspector(store).inspect("observability-v1")

    after = store.ledger.read("observability-v1")
    assert before == after
