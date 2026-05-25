"""Tests for FINALIZE_RUNTIME_ENGINE_FOUNDATION_V1."""

from __future__ import annotations

import os
import subprocess

from aigol.runtime import (
    BLOCKED,
    CLOSED,
    FailClosedRuntimeError,
    MockProvider,
    ProviderInterface,
    ProviderResponse,
    RuntimeEngine,
    RuntimePackage,
    WorkerLifecycle,
)


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "runtime-foundation-v1",
        "package_id": "package-001",
        "provider": "mock",
        "worker_id": "worker-001",
        "task_type": "echo",
        "payload": {"message": "bounded mock execution"},
        "lineage_refs": [{"ref_type": "moc_operational_foundation", "hash": "sha256:moc-v1-operational"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _engine(provider: ProviderInterface | None = None) -> RuntimeEngine:
    engine = RuntimeEngine()
    engine.register_provider(provider or MockProvider())
    return engine


def test_same_input_produces_same_replay_hash() -> None:
    first = _engine().dispatch(_package()).to_dict()
    second = _engine().dispatch(_package()).to_dict()

    assert first["replay_hash"] == second["replay_hash"]
    assert first == second


def test_invalid_package_fails_closed() -> None:
    artifact = _engine().dispatch(_package(governance_state="DRAFT")).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["lifecycle_state"] in {"CREATED", BLOCKED}
    assert artifact["runtime_dispatch_artifact"]["fail_closed"] is True


def test_invalid_lifecycle_transition_is_blocked() -> None:
    lifecycle = WorkerLifecycle(worker_id="worker-001")

    try:
        lifecycle.transition_to("RUNNING")
    except FailClosedRuntimeError:
        pass

    assert lifecycle.state == BLOCKED
    assert lifecycle.transitions[-1]["status"] == "BLOCKED"


def test_mock_provider_does_not_execute_real_commands(monkeypatch) -> None:
    def fail_shell(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("shell command invoked")

    monkeypatch.setattr(subprocess, "run", fail_shell)
    monkeypatch.setattr(os, "system", fail_shell)

    artifact = _engine().dispatch(_package(payload={"command": "echo should-not-run"})).to_dict()

    assert artifact["status"] == "RETURNED"
    assert artifact["provider_response"]["output"]["echo"] == {"command": "echo should-not-run"}
    assert artifact["provider_response"]["metadata"]["subprocess_spawned"] is False


def test_governed_return_includes_boundary_guarantees() -> None:
    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["boundary_guarantees"] == {
        "real_execution": False,
        "autonomous_execution": False,
        "provider_authority": False,
        "orchestration": False,
        "hidden_continuation": False,
        "governance_mutation": False,
    }


def test_dispatch_lifecycle_reaches_closed_only_through_valid_transitions() -> None:
    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["lifecycle_state"] == CLOSED
    assert [(item["from"], item["to"]) for item in artifact["lifecycle_transitions"]] == [
        ("CREATED", "PREPARED"),
        ("PREPARED", "DISPATCHED"),
        ("DISPATCHED", "RUNNING"),
        ("RUNNING", "RETURNED"),
        ("RETURNED", "CLOSED"),
    ]


def test_provider_cannot_bypass_runtime_engine_authority() -> None:
    class BadProvider(ProviderInterface):
        def provider_name(self) -> str:
            return "mock"

        def execute(self, runtime_package: RuntimePackage):
            return {"status": "BYPASS"}

    artifact = _engine(BadProvider()).dispatch(_package()).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["boundary_guarantees"]["provider_authority"] is False


def test_provider_response_cannot_grant_authority() -> None:
    class AuthorityClaimingProvider(ProviderInterface):
        def provider_name(self) -> str:
            return "mock"

        def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
            return ProviderResponse(
                provider="mock",
                status="MOCK_RETURNED",
                output={"claimed_execution": True},
                metadata={"provider_authority": True},
            )

    artifact = _engine(AuthorityClaimingProvider()).dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    assert artifact["boundary_guarantees"]["provider_authority"] is False
    assert artifact["boundary_guarantees"]["real_execution"] is False


def test_unserializable_payload_fails_closed() -> None:
    artifact = _engine().dispatch(_package(payload={"bad": object()})).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["runtime_dispatch_artifact"]["fail_closed"] is True


def test_unregistered_provider_fails_closed() -> None:
    artifact = RuntimeEngine().dispatch(_package()).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["runtime_dispatch_artifact"]["fail_closed_reason"] == "provider must be registered explicitly"
