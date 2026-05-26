"""Tests for FINALIZE_GOVERNED_TOOL_CAPABILITY_LAYER_V1."""

from __future__ import annotations

import os
import subprocess

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.capabilities import CapabilityRequest, CapabilityValidator
from aigol.runtime.sandbox import SandboxContext
from aigol.runtime.transport import RuntimeStore, reconstruct_capability_execution
from aigol.runtime.transport.serialization import load_json, replay_hash


def _payload(capability: str = "analyze_text", **overrides):
    capability_request = {
        "capability": capability,
        "target": "inline",
        "request_payload": {"text": "bounded capability analysis"},
    }
    capability_request.update(overrides.pop("capability_request", {}))
    sandbox = {
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
    }
    sandbox.update(overrides.pop("sandbox", {}))
    payload = {"capability_request": capability_request, "sandbox": sandbox}
    payload.update(overrides)
    return payload


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "capability-v1",
        "package_id": "package-capability-001",
        "provider": "mock",
        "worker_id": "worker-capability-001",
        "task_type": "capability",
        "payload": _payload(),
        "lineage_refs": [{"ref_type": "execution_sandbox_foundation", "hash": "sha256:sandbox-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    return engine


def _request(package: RuntimePackage | None = None):
    package = package or _package()
    context = SandboxContext.from_runtime_package(package)
    return CapabilityRequest.from_runtime_package(package, context.sandbox_id), context


def test_valid_capability_request() -> None:
    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    assert artifact["provider_response"]["status"] == "CAPABILITY_RETURNED"
    assert artifact["provider_response"]["output"]["capability"] == "analyze_text"


def test_unknown_capability_blocked() -> None:
    artifact = _engine().dispatch(_package(payload=_payload("unknown_capability"))).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_forbidden_capability_blocked() -> None:
    artifact = _engine().dispatch(_package(payload=_payload("shell_execution"))).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_malformed_request_blocked() -> None:
    artifact = _engine().dispatch(_package(payload={"capability_request": {}, "sandbox": {}})).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_invalid_replay_hash_blocked() -> None:
    request, context = _request()
    broken = CapabilityRequest(
        capability_request_id=request.capability_request_id,
        runtime_id=request.runtime_id,
        sandbox_id=request.sandbox_id,
        package_id=request.package_id,
        worker_id=request.worker_id,
        provider=request.provider,
        capability=request.capability,
        target=request.target,
        request_payload=request.request_payload,
        governance_state=request.governance_state,
        lineage_refs=request.lineage_refs,
        created_at=request.created_at,
        boundary_guarantees=request.boundary_guarantees,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        CapabilityValidator().validate(broken, context)


def test_unauthorized_governance_state_blocked() -> None:
    artifact = _engine().dispatch(_package(governance_state="APPROVED")).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_sandbox_capability_mismatch_blocked() -> None:
    payload = _payload("analyze_text", sandbox={"allowed_capabilities": ["inspect_json"]})
    artifact = _engine().dispatch(_package(payload=payload)).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_deterministic_replay_hashing() -> None:
    first = _engine().dispatch(_package()).to_dict()
    second = _engine().dispatch(_package()).to_dict()

    assert first["provider_response"]["output"]["replay_hash"] == second["provider_response"]["output"]["replay_hash"]


def test_append_only_capability_persistence(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    request = load_json(store.capability_request_path("capability-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_capability_request("capability-v1", request)


def test_replay_reconstruction(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_capability_execution("capability-v1", tmp_path)

    assert reconstruction["status"] == "CAPABILITY_EXECUTION_RECONSTRUCTED"
    assert reconstruction["capability_result"]["capability"] == "analyze_text"


def test_read_text_safe_path_enforcement(tmp_path) -> None:
    safe_file = tmp_path / "safe.txt"
    safe_file.write_text("safe text", encoding="utf-8")
    payload = _payload(
        "read_text",
        capability_request={
            "target": str(safe_file),
            "request_payload": {"safe_paths": [str(tmp_path)]},
        },
    )

    artifact = _engine().dispatch(_package(payload=payload)).to_dict()

    assert artifact["provider_response"]["output"]["execution_summary"]["text"] == "safe text"


def test_path_traversal_blocked(tmp_path) -> None:
    safe_root = tmp_path / "safe"
    unsafe_root = tmp_path / "unsafe"
    safe_root.mkdir()
    unsafe_root.mkdir()
    unsafe_file = unsafe_root / "secret.txt"
    unsafe_file.write_text("secret", encoding="utf-8")
    payload = _payload(
        "read_text",
        capability_request={
            "target": str(unsafe_file),
            "request_payload": {"safe_paths": [str(safe_root)]},
        },
    )

    artifact = _engine().dispatch(_package(payload=payload)).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_mock_write_preview_performs_no_write(tmp_path) -> None:
    target = tmp_path / "preview.txt"
    payload = _payload(
        "mock_write_preview",
        capability_request={"target": str(target), "request_payload": {"content": "preview only"}},
    )

    artifact = _engine().dispatch(_package(payload=payload)).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["provider_response"] is None
    assert not target.exists()


def test_no_subprocess_execution_possible(monkeypatch) -> None:
    def fail_subprocess(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("subprocess invoked")

    monkeypatch.setattr(subprocess, "run", fail_subprocess)

    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["provider_response"]["output"]["boundary_guarantees"]["no_subprocess_execution"] is True


def test_no_shell_execution_possible(monkeypatch) -> None:
    def fail_shell(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("shell invoked")

    monkeypatch.setattr(os, "system", fail_shell)

    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["provider_response"]["output"]["boundary_guarantees"]["no_shell_execution"] is True


def test_immutable_capability_guarantees(tmp_path) -> None:
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())
    result = load_json(store.capability_result_path("capability-v1"))

    with pytest.raises(FailClosedRuntimeError):
        store.persist_capability_result("capability-v1", result)

    assert result["replay_hash"] == replay_hash({k: v for k, v in result.items() if k != "replay_hash"})


def test_fail_closed_behavior_for_missing_lineage() -> None:
    artifact = _engine().dispatch(_package(lineage_refs=[])).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
