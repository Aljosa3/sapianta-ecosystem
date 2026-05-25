"""Tests for FINALIZE_SEMANTIC_CONTINUITY_MEMORY_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.goals import GoalContract, GoalContinuityEngine, GoalSequence
from aigol.runtime.memory import (
    MemoryContract,
    MemoryRecord,
    MemoryRetentionPolicy,
    MemoryStore,
    MemoryValidator,
    SemanticSummary,
    reconstruct_memory_lineage,
)
from aigol.runtime.memory.semantic_summary import MAX_SUMMARY_LENGTH
from aigol.runtime.transport import RuntimeStore


def _goal_payload(**overrides):
    goal_sequence = {
        "goal_id": "memory-goal-v1",
        "goal_type": "BOUNDED_OPERATIONAL_SEQUENCE",
        "requested_objective": "capture bounded continuity memory",
        "continuity_scope": "BOUNDED_SEQUENCE",
        "max_step_limit": 2,
        "steps": [
            {
                "step_id": "memory-goal-v1:step:0",
                "step_order": 0,
                "capability_request": {"capability": "analyze_text", "target": "inline"},
                "policy_scope": "ANALYSIS_ONLY",
                "sandbox_profile": {"execution_mode": "MOCK_EXECUTION"},
                "execution_state": "PENDING",
            }
        ],
    }
    goal_sequence.update(overrides)
    return {"goal_sequence": goal_sequence}


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "memory-v1",
        "package_id": "package-memory-001",
        "provider": "mock",
        "worker_id": "worker-memory-001",
        "task_type": "goal",
        "payload": _goal_payload(),
        "lineage_refs": [{"ref_type": "goal_continuity_runtime", "hash": "sha256:goal-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _memory_objects(package: RuntimePackage | None = None):
    package = package or _package()
    goal_contract = GoalContract.from_runtime_package(package)
    goal_sequence = GoalSequence.from_runtime_package(package, goal_contract)
    goal_result, _ = GoalContinuityEngine().evaluate(goal_contract, goal_sequence)
    summary = SemanticSummary.from_goal_artifacts(goal_contract.to_dict(), goal_sequence.to_dict(), goal_result).to_dict()
    memory_contract = MemoryContract.from_goal_contract(goal_contract.to_dict())
    record = MemoryRecord.from_contract(memory_contract, summary)
    return memory_contract, record, summary


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_memory_contract_creation() -> None:
    contract, _, _ = _memory_objects()

    assert contract.runtime_id == "memory-v1"
    assert contract.retention_policy == "SESSION"
    assert contract.to_dict()["replay_hash"].startswith("sha256:")


def test_valid_memory_record_creation() -> None:
    _, record, _ = _memory_objects()

    assert record.memory_class == "SEMANTIC_CONTINUITY"
    assert record.semantic_summary["policy_continuity_constraints"] == "bounded_replay_visible_no_vector_memory_no_search"


def test_bounded_semantic_summaries() -> None:
    _, _, summary = _memory_objects()

    assert len(SemanticSummary.as_text(summary)) <= MAX_SUMMARY_LENGTH
    assert "summary_replay_hash" in summary


def test_oversized_semantic_summary_blocked() -> None:
    summary = SemanticSummary("x" * 2100, "", "", "", "")

    with pytest.raises(FailClosedRuntimeError):
        summary.to_dict()


def test_retention_policy_enforcement() -> None:
    policy = MemoryRetentionPolicy()

    assert policy.validate("TRANSIENT")["unlimited_retention"] is False
    with pytest.raises(FailClosedRuntimeError):
        policy.validate("UNLIMITED")


def test_invalid_replay_hash_blocked() -> None:
    contract, record, _ = _memory_objects()
    broken = MemoryContract(
        memory_contract_id=contract.memory_contract_id,
        runtime_id=contract.runtime_id,
        goal_id=contract.goal_id,
        continuity_scope=contract.continuity_scope,
        governance_state=contract.governance_state,
        retention_policy=contract.retention_policy,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        MemoryValidator().validate(broken, record)


def test_malformed_memory_blocked() -> None:
    contract, record, _ = _memory_objects()
    malformed = MemoryRecord.from_contract(contract, dict(record.semantic_summary))
    malformed = MemoryRecord(
        memory_id=malformed.memory_id,
        runtime_id="different",
        goal_id=malformed.goal_id,
        continuity_scope=malformed.continuity_scope,
        semantic_summary=malformed.semantic_summary,
        memory_class=malformed.memory_class,
        retention_policy=malformed.retention_policy,
        lineage_refs=malformed.lineage_refs,
        created_at=malformed.created_at,
        replay_hash=malformed.replay_hash,
    )

    with pytest.raises(FailClosedRuntimeError):
        MemoryValidator().validate(contract, malformed)


def test_unauthorized_governance_state_blocked() -> None:
    contract, record, _ = _memory_objects()
    contract = MemoryContract(
        memory_contract_id=contract.memory_contract_id,
        runtime_id=contract.runtime_id,
        goal_id=contract.goal_id,
        continuity_scope=contract.continuity_scope,
        governance_state="APPROVED",
        retention_policy=contract.retention_policy,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
    )

    with pytest.raises(FailClosedRuntimeError):
        MemoryValidator().validate(contract, record)


def test_missing_lineage_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        _memory_objects(_package(lineage_refs=[]))


def test_deterministic_replay_hashing() -> None:
    first_contract, first_record, first_summary = _memory_objects()
    second_contract, second_record, second_summary = _memory_objects()

    assert first_contract.to_dict()["replay_hash"] == second_contract.to_dict()["replay_hash"]
    assert first_record.to_dict()["replay_hash"] == second_record.to_dict()["replay_hash"]
    assert first_summary["summary_replay_hash"] == second_summary["summary_replay_hash"]


def test_append_only_memory_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    memory_store = MemoryStore(tmp_path)
    contract = memory_store.load_contract("memory-v1")

    with pytest.raises(FailClosedRuntimeError):
        memory_store.persist_contract("memory-v1", contract)


def test_overwrite_blocked(tmp_path) -> None:
    contract, record, summary = _memory_objects()
    memory_store = MemoryStore(tmp_path)
    validation = MemoryValidator().validate(contract, record)
    memory_store.persist_summary("memory-v1", summary)
    memory_store.persist_record("memory-v1", record.to_dict())
    memory_store.persist_validation("memory-v1", validation)

    with pytest.raises(FailClosedRuntimeError):
        memory_store.persist_record("memory-v1", record.to_dict())


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_memory_lineage("memory-v1", tmp_path)

    assert reconstruction["status"] == "MEMORY_LINEAGE_RECONSTRUCTED"
    assert reconstruction["memory_record"]["memory_class"] == "SEMANTIC_CONTINUITY"


def test_immutable_memory_guarantees() -> None:
    contract, record, _ = _memory_objects()
    validation = MemoryValidator().validate(contract, record)

    assert validation["status"] == "MEMORY_VALIDATED"
    assert record.to_dict()["replay_hash"].startswith("sha256:")


def test_fail_closed_validation_behavior() -> None:
    contract, record, _ = _memory_objects()
    bad_record = MemoryRecord(
        memory_id=record.memory_id,
        runtime_id=record.runtime_id,
        goal_id=record.goal_id,
        continuity_scope="",
        semantic_summary=record.semantic_summary,
        memory_class=record.memory_class,
        retention_policy=record.retention_policy,
        lineage_refs=record.lineage_refs,
        created_at=record.created_at,
    )

    with pytest.raises(FailClosedRuntimeError):
        MemoryValidator().validate(contract, bad_record)


def test_no_vector_memory_or_semantic_search_introduced() -> None:
    assert not hasattr(MemoryStore, "search")
    assert not hasattr(MemoryStore, "embed")
    assert not hasattr(MemoryStore, "vector_index")


def test_no_memory_without_goal_continuity(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(
        _package(
            payload={"message": "no goal"},
            runtime_id="no-memory-v1",
        )
    )

    assert not MemoryStore(tmp_path).memory_record_path("no-memory-v1").exists()
