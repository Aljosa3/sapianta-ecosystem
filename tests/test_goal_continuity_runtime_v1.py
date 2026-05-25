"""Tests for FINALIZE_GOAL_CONTINUITY_RUNTIME_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.goals import GoalContract, GoalContinuityEngine, GoalSequence, GoalValidator, reconstruct_goal_continuity
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _goal_payload(**overrides):
    goal_sequence = {
        "goal_id": "goal-v1",
        "parent_goal_id": "",
        "goal_type": "BOUNDED_OPERATIONAL_SEQUENCE",
        "requested_objective": "inspect bounded operational goal",
        "continuity_scope": "BOUNDED_SEQUENCE",
        "max_step_limit": 3,
        "progression_state": "PENDING",
        "steps": [
            {
                "step_id": "goal-v1:step:0",
                "step_order": 0,
                "capability_request": {"capability": "analyze_text", "target": "inline"},
                "policy_scope": "ANALYSIS_ONLY",
                "sandbox_profile": {"execution_mode": "MOCK_EXECUTION"},
                "execution_state": "PENDING",
            },
            {
                "step_id": "goal-v1:step:1",
                "step_order": 1,
                "capability_request": {"capability": "inspect_json", "target": "inline"},
                "policy_scope": "ANALYSIS_ONLY",
                "sandbox_profile": {"execution_mode": "MOCK_EXECUTION"},
                "execution_state": "PENDING",
            },
        ],
    }
    goal_sequence.update(overrides)
    return {"goal_sequence": goal_sequence}


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "goal-runtime-v1",
        "package_id": "package-goal-001",
        "provider": "mock",
        "worker_id": "worker-goal-001",
        "task_type": "goal",
        "payload": _goal_payload(),
        "lineage_refs": [{"ref_type": "runtime_observability", "hash": "sha256:observability-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _contract_sequence(package: RuntimePackage | None = None):
    package = package or _package()
    contract = GoalContract.from_runtime_package(package)
    sequence = GoalSequence.from_runtime_package(package, contract)
    return contract, sequence


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_goal_continuity() -> None:
    contract, sequence = _contract_sequence()
    result, validation = GoalContinuityEngine().evaluate(contract, sequence)

    assert validation["status"] == "GOAL_VALIDATED"
    assert result["goal_decision"] == "CONTINUE"
    assert result["next_step_id"] == "goal-v1:step:0"


def test_bounded_sequencing() -> None:
    _, sequence = _contract_sequence()

    assert [step.step_order for step in sequence.steps] == [0, 1]
    assert sequence.next_step().step_id == "goal-v1:step:0"


def test_max_step_enforcement() -> None:
    steps = _goal_payload()["goal_sequence"]["steps"] * 2
    package = _package(payload=_goal_payload(max_step_limit=3, steps=steps))
    contract, sequence = _contract_sequence(package)

    with pytest.raises(FailClosedRuntimeError):
        GoalValidator().validate(contract, sequence)


def test_invalid_replay_hash_blocked() -> None:
    contract, sequence = _contract_sequence()
    broken = GoalContract(
        goal_id=contract.goal_id,
        runtime_id=contract.runtime_id,
        parent_goal_id=contract.parent_goal_id,
        goal_type=contract.goal_type,
        requested_objective=contract.requested_objective,
        governance_state=contract.governance_state,
        continuity_scope=contract.continuity_scope,
        max_step_limit=contract.max_step_limit,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        GoalValidator().validate(broken, sequence)


def test_unauthorized_governance_blocked() -> None:
    package = _package(governance_state="APPROVED")
    contract, sequence = _contract_sequence(package)

    with pytest.raises(FailClosedRuntimeError):
        GoalContinuityEngine().evaluate(contract, sequence)


def test_deterministic_replay_hashing() -> None:
    first_contract, first_sequence = _contract_sequence()
    second_contract, second_sequence = _contract_sequence()
    first_result, _ = GoalContinuityEngine().evaluate(first_contract, first_sequence)
    second_result, _ = GoalContinuityEngine().evaluate(second_contract, second_sequence)

    assert first_contract.to_dict()["replay_hash"] == second_contract.to_dict()["replay_hash"]
    assert first_sequence.to_dict()["replay_hash"] == second_sequence.to_dict()["replay_hash"]
    assert first_result["replay_hash"] == second_result["replay_hash"]


def test_append_only_goal_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.goal_contract_path("goal-runtime-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_goal_contract("goal-runtime-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_goal_continuity("goal-runtime-v1", tmp_path)

    assert reconstruction["status"] == "GOAL_CONTINUITY_RECONSTRUCTED"
    assert reconstruction["goal_result"]["goal_decision"] == "CONTINUE"


def test_fail_closed_progression_behavior() -> None:
    package = _package(payload=_goal_payload(steps=[{"step_order": 1, "capability_request": {"capability": "analyze_text"}}]))
    contract, sequence = _contract_sequence(package)

    with pytest.raises(FailClosedRuntimeError):
        GoalContinuityEngine().evaluate(contract, sequence)


def test_immutable_goal_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.goal_result_path("goal-runtime-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_goal_result("goal-runtime-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_no_autonomous_recursive_execution(tmp_path) -> None:
    class CountingProvider(MockProvider):
        def __init__(self) -> None:
            self.calls = 0

        def execute(self, runtime_package: RuntimePackage):
            self.calls += 1
            return super().execute(runtime_package)

    provider = CountingProvider()
    engine = RuntimeEngine(runtime_store=RuntimeStore(tmp_path))
    engine.register_provider(provider)

    artifact = engine.dispatch(_package()).to_dict()

    assert artifact["provider_response"]["status"] == "GOAL_CONTINUITY_EVALUATED"
    assert artifact["provider_response"]["metadata"]["sequencing_only"] is True
    assert provider.calls == 0
