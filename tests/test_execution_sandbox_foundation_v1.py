"""Tests for FINALIZE_EXECUTION_SANDBOX_FOUNDATION_V1."""

from __future__ import annotations

import os
import subprocess
from urllib import request

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.sandbox import SandboxContext, SandboxExecutor, SandboxValidator
from aigol.runtime.transport import RuntimeStore, reconstruct_sandbox_execution
from aigol.runtime.transport.serialization import load_json, replay_hash


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "sandbox-v1",
        "package_id": "package-sandbox-001",
        "provider": "mock",
        "worker_id": "worker-sandbox-001",
        "task_type": "sandbox",
        "payload": {
            "requires_sandbox": True,
            "mock_payload": {"message": "bounded sandbox"},
            "sandbox": {
                "execution_mode": "MOCK_EXECUTION",
                "allowed_capabilities": ["mock_execute"],
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
        },
        "lineage_refs": [{"ref_type": "governed_provider_activation", "hash": "sha256:provider-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _context(**sandbox_overrides) -> SandboxContext:
    package = _package()
    payload = dict(package.payload)
    sandbox = dict(payload["sandbox"])
    sandbox.update(sandbox_overrides)
    payload["sandbox"] = sandbox
    return SandboxContext.from_runtime_package(_package(payload=payload))


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def test_valid_sandbox_creation() -> None:
    context = _context()
    validation = SandboxValidator().validate(context)

    assert validation["status"] == "SANDBOX_VALIDATED"
    assert context.to_dict()["replay_hash"].startswith("sha256:")


def test_invalid_capability_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        SandboxValidator().validate(_context(allowed_capabilities=["unknown_capability"]))


def test_forbidden_capability_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        SandboxValidator().validate(_context(allowed_capabilities=["shell_execution"]))


def test_malformed_sandbox_blocked() -> None:
    broken = SandboxContext(
        sandbox_id="sandbox",
        runtime_id="",
        package_id="package",
        worker_id="worker",
        execution_mode="MOCK_EXECUTION",
        allowed_capabilities=["mock_execute"],
        denied_capabilities=[],
        resource_limits={"max_memory_mb": 64, "max_runtime_seconds": 1},
        execution_ttl_seconds=1,
        lineage_refs=[{"ref": "lineage"}],
        created_at="1970-01-01T00:00:00Z",
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        SandboxValidator().validate(broken)


def test_invalid_ttl_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        SandboxValidator().validate(_context(execution_ttl_seconds=0))


def test_invalid_resource_limits_blocked() -> None:
    with pytest.raises(FailClosedRuntimeError):
        SandboxValidator().validate(_context(resource_limits={"max_memory_mb": 0, "max_runtime_seconds": 1}))


def test_deterministic_replay_hashing() -> None:
    first = _context().to_dict()
    second = _context().to_dict()

    assert first["replay_hash"] == second["replay_hash"]


def test_append_only_sandbox_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    context = _context()
    validation = SandboxValidator().validate(context)

    store.persist_sandbox_context("sandbox-v1", context.to_dict())
    store.persist_sandbox_validation("sandbox-v1", validation)

    with pytest.raises(FailClosedRuntimeError):
        store.persist_sandbox_context("sandbox-v1", context.to_dict())


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    artifact = _engine(store).dispatch(_package()).to_dict()

    reconstruction = reconstruct_sandbox_execution("sandbox-v1", tmp_path)

    assert artifact["provider_response"]["status"] == "SANDBOX_RETURNED"
    assert reconstruction["status"] == "SANDBOX_EXECUTION_RECONSTRUCTED"
    assert reconstruction["sandbox_result"]["execution_status"] == "SANDBOX_EXECUTION_SIMULATED"


def test_executor_cannot_spawn_subprocess(monkeypatch) -> None:
    def fail_subprocess(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("subprocess execution invoked")

    monkeypatch.setattr(subprocess, "run", fail_subprocess)

    result = SandboxExecutor().execute(_context(), {"command": "echo forbidden"}).to_dict()

    assert result["boundary_guarantees"]["subprocess_execution"] is False


def test_executor_cannot_mutate_filesystem(tmp_path) -> None:
    target = tmp_path / "should-not-exist.txt"

    result = SandboxExecutor().execute(_context(), {"write_path": str(target), "content": "forbidden"}).to_dict()

    assert result["boundary_guarantees"]["filesystem_write"] is False
    assert not target.exists()


def test_executor_cannot_access_network(monkeypatch) -> None:
    def fail_network(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("network access invoked")

    monkeypatch.setattr(request, "urlopen", fail_network)

    result = SandboxExecutor().execute(_context(), {"url": "https://example.invalid"}).to_dict()

    assert result["boundary_guarantees"]["unrestricted_network"] is False


def test_executor_cannot_spawn_workers(monkeypatch) -> None:
    def fail_fork(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("worker spawn invoked")

    monkeypatch.setattr(os, "fork", fail_fork, raising=False)

    result = SandboxExecutor().execute(_context(), {"spawn_worker": True}).to_dict()

    assert result["boundary_guarantees"]["worker_spawn"] is False


def test_fail_closed_validation_behavior() -> None:
    artifact = _engine().dispatch(
        _package(
            payload={
                "requires_sandbox": True,
                "sandbox": {
                    "execution_mode": "UNRESTRICTED",
                    "allowed_capabilities": ["mock_execute"],
                    "denied_capabilities": [],
                    "resource_limits": {"max_memory_mb": 64, "max_runtime_seconds": 1},
                    "execution_ttl_seconds": 1,
                },
            }
        )
    ).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["runtime_dispatch_artifact"]["fail_closed"] is True


def test_immutable_sandbox_result_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    result = SandboxExecutor().execute(_context(), {"payload": True}).to_dict()

    store.persist_sandbox_result("sandbox-v1", result)

    with pytest.raises(FailClosedRuntimeError):
        store.persist_sandbox_result("sandbox-v1", result)

    assert load_json(store.sandbox_result_path("sandbox-v1"))["replay_hash"] == replay_hash(
        {k: v for k, v in result.items() if k != "replay_hash"}
    )
