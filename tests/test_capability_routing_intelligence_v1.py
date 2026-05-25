"""Tests for FINALIZE_CAPABILITY_ROUTING_INTELLIGENCE_V1."""

from __future__ import annotations

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.routing import RoutingContract, RoutingEngine, RoutingValidator, reconstruct_routing_decision
from aigol.runtime.transport import RuntimeStore
from aigol.runtime.transport.serialization import load_json, replay_hash


def _payload(capability: str = "analyze_text", **overrides):
    payload = {
        "capability_request": {
            "capability": capability,
            "target": "inline",
            "request_payload": {"text": "routed capability", "policy_scope": "ANALYSIS_ONLY"},
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
    payload.update(overrides)
    return payload


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "routing-v1",
        "package_id": "package-routing-001",
        "provider": "mock",
        "worker_id": "worker-routing-001",
        "task_type": "capability",
        "payload": _payload(),
        "lineage_refs": [{"ref_type": "semantic_continuity_memory", "hash": "sha256:memory-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _contract(package: RuntimePackage | None = None) -> RoutingContract:
    package = package or _package()
    return RoutingContract.from_runtime_package(package, package.payload["capability_request"])


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_routing_evaluation() -> None:
    route, result, validation = RoutingEngine().evaluate(_contract())

    assert validation["status"] == "ROUTING_VALIDATED"
    assert route.capability_class == "ANALYSIS"
    assert result.routing_decision == "ROUTE_ASSIGNED"


def test_unknown_capability_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        RoutingEngine().evaluate(_contract(_package(payload=_payload("unknown_capability"))))


def test_replay_hash_validation() -> None:
    contract = _contract()
    broken = RoutingContract(
        routing_contract_id=contract.routing_contract_id,
        runtime_id=contract.runtime_id,
        goal_id=contract.goal_id,
        requested_capability=contract.requested_capability,
        requested_target=contract.requested_target,
        governance_state=contract.governance_state,
        lineage_refs=contract.lineage_refs,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        RoutingValidator().validate(broken)


def test_execution_surface_assignment() -> None:
    route, result, _ = RoutingEngine().evaluate(_contract())

    assert route.execution_surface == "SANDBOX_ONLY"
    assert result.execution_surface == "SANDBOX_ONLY"


def test_approval_required_routing() -> None:
    route, result, _ = RoutingEngine().evaluate(
        _contract(_package(payload=_payload("mock_write_preview")))
    )

    assert route.approval_required is True
    assert result.execution_surface == "HUMAN_APPROVAL_REQUIRED"


def test_deterministic_replay_hashing() -> None:
    first_route, first_result, _ = RoutingEngine().evaluate(_contract())
    second_route, second_result, _ = RoutingEngine().evaluate(_contract())

    assert first_route.to_dict()["replay_hash"] == second_route.to_dict()["replay_hash"]
    assert first_result.to_dict()["replay_hash"] == second_result.to_dict()["replay_hash"]


def test_append_only_routing_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    contract = load_json(store.routing_contract_path("routing-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_routing_contract("routing-v1", contract)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_routing_decision("routing-v1", tmp_path)

    assert reconstruction["status"] == "ROUTING_DECISION_RECONSTRUCTED"
    assert reconstruction["routing_result"]["routing_decision"] == "ROUTE_ASSIGNED"


def test_immutable_routing_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.routing_result_path("routing-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_routing_result("routing-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_fail_closed_validation_behavior() -> None:
    contract = _contract(_package(lineage_refs=[]))

    with pytest.raises(FailClosedRuntimeError):
        RoutingEngine().evaluate(contract)


def test_runtime_persists_route_before_capability(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    artifact = _engine(store).dispatch(_package()).to_dict()

    events = [entry["event_type"] for entry in store.ledger.read("routing-v1")]
    assert artifact["provider_response"]["status"] == "CAPABILITY_RETURNED"
    assert events.index("ROUTING_RESULT_PERSISTED") < events.index("CAPABILITY_REQUEST_PERSISTED")
