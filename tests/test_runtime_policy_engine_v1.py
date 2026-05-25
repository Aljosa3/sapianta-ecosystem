"""Tests for FINALIZE_RUNTIME_POLICY_ENGINE_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.capabilities import CapabilityRequest
from aigol.runtime.policy import PolicyContract, PolicyRegistry, PolicyValidator, RuntimePolicyEngine
from aigol.runtime.policy.policy_replay import reconstruct_policy_decision
from aigol.runtime.sandbox import SandboxContext
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _payload(capability: str = "analyze_text", policy_scope: str | None = None):
    request_payload = {"text": "centralized runtime policy"}
    if policy_scope is not None:
        request_payload["policy_scope"] = policy_scope
    return {
        "capability_request": {
            "capability": capability,
            "target": "inline",
            "request_payload": request_payload,
        },
        "sandbox": {
            "execution_mode": "MOCK_EXECUTION",
            "allowed_capabilities": [capability],
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
    }


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "policy-v1",
        "package_id": "package-policy-001",
        "provider": "mock",
        "worker_id": "worker-policy-001",
        "task_type": "capability",
        "payload": _payload(),
        "lineage_refs": [{"ref_type": "tool_capability_layer", "hash": "sha256:capability-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _request_and_context(package: RuntimePackage | None = None):
    package = package or _package()
    context = SandboxContext.from_runtime_package(package)
    request = CapabilityRequest.from_runtime_package(package, context.sandbox_id)
    return request, context


def _contract(package: RuntimePackage | None = None) -> tuple[PolicyContract, SandboxContext]:
    request, context = _request_and_context(package)
    return PolicyContract.from_capability_request(request, context), context


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_policy_evaluation() -> None:
    contract, context = _contract()
    result, validation = RuntimePolicyEngine().evaluate(contract, sandbox_context=context)

    assert validation["status"] == "POLICY_VALIDATED"
    assert result.decision == "ALLOW"
    assert result.decision_reason == "capability allowed by registered policy scope"


def test_forbidden_capability_blocked() -> None:
    package = _package(payload=_payload("shell_execution"))
    contract, context = _contract(package)

    with pytest.raises(FailClosedRuntimeError):
        RuntimePolicyEngine().evaluate(contract, sandbox_context=context)


def test_unauthorized_governance_state_blocked() -> None:
    contract, context = _contract(_package(governance_state="APPROVED"))

    with pytest.raises(FailClosedRuntimeError):
        RuntimePolicyEngine().evaluate(contract, sandbox_context=context)


def test_invalid_replay_hash_blocked() -> None:
    contract, context = _contract()
    broken = PolicyContract(
        policy_id=contract.policy_id,
        runtime_id=contract.runtime_id,
        sandbox_id=contract.sandbox_id,
        capability_request_id=contract.capability_request_id,
        policy_scope=contract.policy_scope,
        requested_capability=contract.requested_capability,
        requested_target=contract.requested_target,
        governance_state=contract.governance_state,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        PolicyValidator().validate(broken, sandbox_context=context)


def test_unknown_policy_scope_blocked() -> None:
    contract, context = _contract(_package(payload=_payload("analyze_text", policy_scope="UNKNOWN_SCOPE")))

    with pytest.raises(FailClosedRuntimeError):
        RuntimePolicyEngine().evaluate(contract, sandbox_context=context)


def test_deterministic_replay_hashing() -> None:
    first, context = _contract()
    second, _ = _contract()
    first_result, _ = RuntimePolicyEngine().evaluate(first, sandbox_context=context)
    second_result, _ = RuntimePolicyEngine().evaluate(second, sandbox_context=context)

    assert first.to_dict()["replay_hash"] == second.to_dict()["replay_hash"]
    assert first_result.to_dict()["replay_hash"] == second_result.to_dict()["replay_hash"]


def test_append_only_policy_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.policy_contract_path("policy-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_policy_contract("policy-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_policy_decision("policy-v1", tmp_path)

    assert reconstruction["status"] == "POLICY_DECISION_RECONSTRUCTED"
    assert reconstruction["policy_result"]["decision"] == "ALLOW"


def test_denied_capability_execution_blocked() -> None:
    payload = _payload("read_text", policy_scope="ANALYSIS_ONLY")
    artifact = _engine().dispatch(_package(payload=payload)).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["provider_response"] is None


def test_fail_closed_behavior_missing_lineage() -> None:
    artifact = _engine().dispatch(_package(lineage_refs=[])).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_immutable_policy_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.policy_result_path("policy-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_policy_result("policy-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_registry_is_explicit_allowlist() -> None:
    registry = PolicyRegistry()

    assert registry.capabilities_for_scope("ANALYSIS_ONLY") == ["analyze_text", "inspect_json"]
    with pytest.raises(FailClosedRuntimeError):
        registry.capabilities_for_scope("*")
