"""Tests for FINALIZE_CONTROLLED_RETRY_EXECUTION_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.models import ProviderResponse
from aigol.runtime.retry import RetryContract, RetryEngine, RetryValidator, reconstruct_retry_execution
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "retry-v1",
        "package_id": "package-retry-001",
        "provider": "mock",
        "worker_id": "worker-retry-001",
        "task_type": "echo",
        "payload": {
            "message": "bounded retry",
            "continuity": {
                "continuation_reason": "retry_requested",
                "retry_count": 0,
                "max_retry_limit": 3,
                "parent_runtime_id": "parent-runtime-001",
                "sandbox_id": "retry-v1:package-retry-001:sandbox",
                "capability_request_id": "retry-v1:package-retry-001:mock",
            },
            "retry": {
                "retry_reason": "retry_requested",
                "retry_count": 0,
                "max_retry_limit": 3,
                "parent_runtime_id": "parent-runtime-001",
                "requested_capability": "mock_echo",
                "approval_state": "APPROVED",
            },
        },
        "lineage_refs": [{"ref_type": "human_governance_checkpoints", "hash": "sha256:approval-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _contract(**retry_overrides) -> RetryContract:
    package = _package()
    payload = dict(package.payload)
    retry = dict(payload["retry"])
    retry.update(retry_overrides)
    payload["retry"] = retry
    return RetryContract.from_runtime_package(_package(payload=payload))


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_retry_execution(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    artifact = _engine(store).dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    assert store.load_retry_result("retry-v1")["retry_state"] == "RETRY_EXECUTED"
    assert store.load_retry_validation("retry-v1")["bounded_local_only"] is True


def test_retry_limit_enforcement() -> None:
    request, result, _ = RetryEngine().evaluate(_contract(retry_count=3, max_retry_limit=3))

    assert request.retry_allowed is False
    assert result.retry_state == "RETRY_LIMIT_REACHED"


def test_approval_aware_retry_blocking() -> None:
    request, result, validation = RetryEngine().evaluate(_contract(), approval_state="PENDING_HUMAN_APPROVAL")

    assert request.retry_allowed is False
    assert request.retry_scope == "APPROVAL_BLOCKED"
    assert result.retry_state == "RETRY_BLOCKED"
    assert validation["orchestration"] is False


def test_invalid_replay_hash_blocked() -> None:
    contract = _contract()
    broken = RetryContract(
        retry_contract_id=contract.retry_contract_id,
        runtime_id=contract.runtime_id,
        parent_runtime_id=contract.parent_runtime_id,
        goal_id=contract.goal_id,
        retry_reason=contract.retry_reason,
        retry_count=contract.retry_count,
        max_retry_limit=contract.max_retry_limit,
        governance_state=contract.governance_state,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        RetryValidator().validate(broken)


def test_deterministic_replay_hashing() -> None:
    first_request, first_result, _ = RetryEngine().evaluate(_contract())
    second_request, second_result, _ = RetryEngine().evaluate(_contract())

    assert first_request.to_dict()["replay_hash"] == second_request.to_dict()["replay_hash"]
    assert first_result.to_dict()["replay_hash"] == second_result.to_dict()["replay_hash"]


def test_append_only_retry_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.retry_contract_path("retry-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_retry_contract("retry-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_retry_execution("retry-v1", tmp_path)

    assert reconstruction["status"] == "RETRY_EXECUTION_RECONSTRUCTED"
    assert reconstruction["retry_result"]["retry_state"] == "RETRY_EXECUTED"


def test_immutable_retry_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.retry_result_path("retry-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_retry_result("retry-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_fail_closed_validation_behavior() -> None:
    with pytest.raises(FailClosedRuntimeError):
        RetryEngine().evaluate(_contract(parent_runtime_id=""))


def test_bounded_retry_execution_semantics(tmp_path) -> None:
    class CountingProvider(MockProvider):
        def __init__(self) -> None:
            self.calls = 0

        def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
            self.calls += 1
            return super().execute(runtime_package)

    provider = CountingProvider()
    store = RuntimeStore(tmp_path)
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(provider)

    artifact = engine.dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    assert provider.calls == 1
    assert store.load_retry_result("retry-v1")["retry_state"] == "RETRY_EXECUTED"
    assert store.load_retry_validation("retry-v1")["recursive_autonomous_execution"] is False
