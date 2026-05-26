"""Tests for FINALIZE_HUMAN_GOVERNANCE_CHECKPOINTS_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.approval import ApprovalContract, ApprovalEngine, ApprovalRegistry, ApprovalValidator
from aigol.runtime.routing import RoutingContract, RoutingEngine
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.approval.approval_replay import reconstruct_approval_decision


def _payload(capability: str = "analyze_text", **request_overrides):
    request_payload = {"text": "approval checkpoint", "policy_scope": "ANALYSIS_ONLY"}
    capability_request = {"capability": capability, "target": "inline", "request_payload": request_payload}
    capability_request.update(request_overrides)
    return {
        "capability_request": capability_request,
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
        "runtime_id": "approval-v1",
        "package_id": "package-approval-001",
        "provider": "mock",
        "worker_id": "worker-approval-001",
        "task_type": "capability",
        "payload": _payload(),
        "lineage_refs": [{"ref_type": "capability_routing_intelligence", "hash": "sha256:routing-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _approval_contract(package: RuntimePackage | None = None) -> ApprovalContract:
    package = package or _package()
    routing_contract = RoutingContract.from_runtime_package(package, package.payload["capability_request"])
    route, _, _ = RoutingEngine().evaluate(routing_contract)
    return ApprovalContract.from_routing(routing_contract, route)


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_approval_evaluation() -> None:
    request, result, validation = ApprovalEngine().evaluate(_approval_contract())

    assert validation["status"] == "APPROVAL_VALIDATED"
    assert request.risk_class == "LOW_RISK"
    assert result.approval_state == "APPROVED"
    assert result.execution_allowed is True


def test_approval_required_routing() -> None:
    contract = _approval_contract(_package(payload=_payload("mock_write_preview")))
    request, result, _ = ApprovalEngine().evaluate(contract)

    assert request.approval_required is True
    assert result.approval_state == "PENDING_HUMAN_APPROVAL"
    assert result.execution_allowed is False


def test_blocked_restricted_execution() -> None:
    contract = ApprovalContract(
        approval_contract_id="restricted",
        runtime_id="approval-v1",
        goal_id="",
        requested_capability="restricted",
        execution_surface="HUMAN_APPROVAL_REQUIRED",
        approval_scope="RESTRICTED_BLOCKED",
        governance_state="AUTHORIZED",
        lineage_refs=[{"ref": "lineage"}],
        created_at="1970-01-01T00:00:00Z",
    )

    _, result, _ = ApprovalEngine().evaluate(contract)
    assert result.approval_state == "BLOCKED"
    assert result.execution_allowed is False


def test_invalid_replay_hash_blocked() -> None:
    contract = _approval_contract()
    broken = ApprovalContract(
        approval_contract_id=contract.approval_contract_id,
        runtime_id=contract.runtime_id,
        goal_id=contract.goal_id,
        requested_capability=contract.requested_capability,
        execution_surface=contract.execution_surface,
        approval_scope=contract.approval_scope,
        governance_state=contract.governance_state,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        ApprovalValidator().validate(broken)


def test_unknown_approval_scope_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        ApprovalRegistry().risk_for_scope("UNKNOWN_SCOPE")


def test_deterministic_replay_hashing() -> None:
    first_request, first_result, _ = ApprovalEngine().evaluate(_approval_contract())
    second_request, second_result, _ = ApprovalEngine().evaluate(_approval_contract())

    assert first_request.to_dict()["replay_hash"] == second_request.to_dict()["replay_hash"]
    assert first_result.to_dict()["replay_hash"] == second_result.to_dict()["replay_hash"]


def test_append_only_approval_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.approval_contract_path("approval-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_approval_contract("approval-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_approval_decision("approval-v1", tmp_path)

    assert reconstruction["status"] == "APPROVAL_DECISION_RECONSTRUCTED"
    assert reconstruction["approval_result"]["approval_state"] == "APPROVED"


def test_immutable_approval_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.approval_result_path("approval-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_approval_result("approval-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_fail_closed_validation_behavior() -> None:
    contract = ApprovalContract(
        approval_contract_id="missing-lineage",
        runtime_id="approval-v1",
        goal_id="",
        requested_capability="analyze_text",
        execution_surface="SANDBOX_ONLY",
        approval_scope="READ_ONLY_AUTO_ALLOWED",
        governance_state="AUTHORIZED",
        lineage_refs=[],
        created_at="1970-01-01T00:00:00Z",
    )

    with pytest.raises(FailClosedRuntimeError):
        ApprovalEngine().evaluate(contract)


def test_approval_required_runtime_blocks_execution(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    artifact = _engine(store).dispatch(_package(payload=_payload("mock_write_preview"))).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["provider_response"] is None
    assert store.load_approval_result("approval-v1")["approval_state"] == "PENDING_HUMAN_APPROVAL"
    assert not store.capability_result_path("approval-v1").exists()
