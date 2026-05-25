"""Tests for FINALIZE_BOUNDED_RUNTIME_CONTINUITY_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.continuity import (
    ContinuationContract,
    ContinuationValidator,
    RuntimeContinuityEngine,
    reconstruct_continuity_decision,
)
from aigol.runtime.models import ProviderResponse
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "continuity-v1",
        "package_id": "package-continuity-001",
        "provider": "mock",
        "worker_id": "worker-continuity-001",
        "task_type": "echo",
        "payload": {
            "message": "bounded continuity",
            "continuity": {
                "continuation_reason": "retry_requested",
                "retry_count": 0,
                "max_retry_limit": 3,
                "parent_runtime_id": "parent-runtime-001",
                "sandbox_id": "continuity-v1:package-continuity-001:sandbox",
                "capability_request_id": "continuity-v1:package-continuity-001:mock",
            },
        },
        "lineage_refs": [{"ref_type": "runtime_policy_engine", "hash": "sha256:policy-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _return(status: str = "RETURNED"):
    return type("ReturnArtifact", (), {"status": status})()


def _contract(**continuity_overrides) -> ContinuationContract:
    package = _package()
    payload = dict(package.payload)
    continuity = dict(payload["continuity"])
    continuity.update(continuity_overrides)
    payload["continuity"] = continuity
    return ContinuationContract.from_runtime_return(_package(payload=payload), _return())


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_continuation_evaluation() -> None:
    result, validation, retry = RuntimeContinuityEngine().evaluate(_contract())

    assert validation["status"] == "CONTINUATION_VALIDATED"
    assert retry["retry_class"] == "RETRY_ALLOWED"
    assert result.continuation_decision == "CONTINUE"
    assert result.retry_allowed is True


def test_retry_limit_enforcement() -> None:
    with pytest.raises(FailClosedRuntimeError):
        RuntimeContinuityEngine().evaluate(_contract(retry_count=4, max_retry_limit=3))


def test_unauthorized_continuation_blocked() -> None:
    package = _package(governance_state="APPROVED")
    contract = ContinuationContract.from_runtime_return(package, _return())

    with pytest.raises(FailClosedRuntimeError):
        RuntimeContinuityEngine().evaluate(contract)


def test_invalid_replay_hash_blocked() -> None:
    contract = _contract()
    broken = ContinuationContract(
        continuation_id=contract.continuation_id,
        runtime_id=contract.runtime_id,
        parent_runtime_id=contract.parent_runtime_id,
        sandbox_id=contract.sandbox_id,
        capability_request_id=contract.capability_request_id,
        continuation_reason=contract.continuation_reason,
        retry_count=contract.retry_count,
        max_retry_limit=contract.max_retry_limit,
        governance_state=contract.governance_state,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        ContinuationValidator().validate(broken)


def test_deterministic_replay_hashing() -> None:
    first = _contract()
    second = _contract()
    first_result, _, _ = RuntimeContinuityEngine().evaluate(first)
    second_result, _, _ = RuntimeContinuityEngine().evaluate(second)

    assert first.to_dict()["replay_hash"] == second.to_dict()["replay_hash"]
    assert first_result.to_dict()["replay_hash"] == second_result.to_dict()["replay_hash"]


def test_append_only_continuity_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.continuity_contract_path("continuity-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_continuity_contract("continuity-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_continuity_decision("continuity-v1", tmp_path)

    assert reconstruction["status"] == "CONTINUITY_DECISION_RECONSTRUCTED"
    assert reconstruction["continuation_result"]["continuation_decision"] == "CONTINUE"


def test_bounded_retry_semantics() -> None:
    result, _, retry = RuntimeContinuityEngine().evaluate(_contract(retry_count=2, max_retry_limit=3))

    assert result.continuation_decision == "CONTINUE"
    assert retry["retry_allowed"] is True


def test_continuation_stop_decisions() -> None:
    result, _, retry = RuntimeContinuityEngine().evaluate(_contract(continuation_reason="completed", retry_count=0))

    assert result.continuation_decision == "STOP"
    assert retry["retry_allowed"] is False


def test_fail_closed_validation_behavior() -> None:
    with pytest.raises(FailClosedRuntimeError):
        RuntimeContinuityEngine().evaluate(_contract(parent_runtime_id=""))


def test_immutable_continuity_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.continuity_result_path("continuity-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_continuity_result("continuity-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_no_automatic_recursive_execution(tmp_path) -> None:
    class CountingProvider(MockProvider):
        def __init__(self) -> None:
            self.calls = 0

        def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
            self.calls += 1
            return super().execute(runtime_package)

    provider = CountingProvider()
    engine = RuntimeEngine(runtime_store=RuntimeStore(tmp_path))
    engine.register_provider(provider)

    artifact = engine.dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    assert provider.calls == 1
    assert load_json(RuntimeStore(tmp_path).continuity_result_path("continuity-v1"))["continuation_decision"] == "CONTINUE"
