"""Tests for FINALIZE_GOVERNED_PROVIDER_ACTIVATION_V1."""

from __future__ import annotations

import os
import subprocess

import pytest

from aigol.runtime import FailClosedRuntimeError, RuntimeEngine, RuntimePackage
from aigol.runtime.providers import OpenAIProvider, ProviderActivationGate, ProviderEnvelope
from aigol.runtime.transport import RuntimeStore, reconstruct_provider_invocation
from aigol.runtime.transport.serialization import load_json, replay_hash


def _package(**overrides) -> RuntimePackage:
    values = {
        "runtime_id": "provider-activation-v1",
        "package_id": "package-provider-001",
        "provider": "openai",
        "worker_id": "worker-provider-001",
        "task_type": "prompt",
        "payload": {"prompt": "Return bounded governance evidence."},
        "lineage_refs": [{"ref_type": "runtime_transport_persistence", "hash": "sha256:transport-v1"}],
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return RuntimePackage(**values)


def _transport(request_body, api_key):
    assert api_key == "test-key"
    assert isinstance(request_body["input"], str)
    return {"id": "response-001", "output_text": "bounded provider response"}


def _engine(store: RuntimeStore | None = None) -> RuntimeEngine:
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(OpenAIProvider(transport=_transport))
    return engine


def test_provider_activation_success(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    store = RuntimeStore(tmp_path)

    artifact = _engine(store).dispatch(_package()).to_dict()

    assert artifact["status"] == "RETURNED"
    response = artifact["provider_response"]["output"]
    assert response["provider"] == "openai"
    assert response["response_id"] == "response-001"
    assert response["response_text"] == "bounded provider response"
    assert response["bounded_execution_guarantees"]["no_tool_execution"] is True


def test_unknown_provider_blocked() -> None:
    envelope = ProviderEnvelope.from_runtime_package(_package(provider="unknown"))

    with pytest.raises(FailClosedRuntimeError):
        ProviderActivationGate(registered_providers={"openai"}).validate(envelope)


def test_unauthorized_governance_state_blocked(monkeypatch) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")

    artifact = _engine().dispatch(_package(governance_state="APPROVED")).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["runtime_dispatch_artifact"]["fail_closed"] is True


def test_malformed_provider_envelope_blocked() -> None:
    envelope = ProviderEnvelope.from_dict(
        {
            "provider_request_id": "bad",
            "runtime_id": "provider-activation-v1",
            "package_id": "package-provider-001",
            "provider": "openai",
            "governance_state": "AUTHORIZED",
            "invocation_type": "prompt_response",
            "request_payload": {"prompt": "hi"},
            "lineage_refs": [{"ref": "lineage"}],
            "boundary_guarantees": {"tool_execution": True},
            "created_at": "1970-01-01T00:00:00Z",
            "replay_hash": "sha256:bad",
        }
    )

    with pytest.raises(FailClosedRuntimeError):
        ProviderActivationGate(registered_providers={"openai"}).validate(envelope)


def test_missing_api_key_blocked(monkeypatch) -> None:
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)

    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"
    assert artifact["provider_response"] is None


def test_replay_visible_invocation_persistence(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    store = RuntimeStore(tmp_path)

    _engine(store).dispatch(_package())

    envelope = load_json(store.provider_envelope_path("provider-activation-v1"))
    assert envelope["provider_request_id"] == "provider-activation-v1:package-provider-001:openai"
    assert envelope["replay_hash"] == replay_hash({k: v for k, v in envelope.items() if k != "replay_hash"})


def test_deterministic_replay_hashing(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    first_store = RuntimeStore(tmp_path / "first")
    second_store = RuntimeStore(tmp_path / "second")

    first = _engine(first_store).dispatch(_package()).to_dict()
    second = _engine(second_store).dispatch(_package()).to_dict()

    assert first["provider_response"]["output"]["replay_hash"] == second["provider_response"]["output"]["replay_hash"]
    assert first["replay_hash"] == second["replay_hash"]


def test_provider_response_persistence(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    store = RuntimeStore(tmp_path)

    _engine(store).dispatch(_package())
    response = load_json(store.provider_response_path("provider-activation-v1"))

    assert response["provider"] == "openai"
    assert response["bounded_execution_guarantees"]["no_shell_execution"] is True
    assert response["bounded_execution_guarantees"]["no_recursive_runtime_dispatch"] is True


def test_fail_closed_provider_validation(monkeypatch) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    package = _package(payload=None)

    artifact = _engine().dispatch(package).to_dict()

    assert artifact["status"] == "FAIL_CLOSED"


def test_provider_cannot_bypass_runtime_authority(monkeypatch) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")

    artifact = _engine().dispatch(_package()).to_dict()

    assert artifact["boundary_guarantees"]["provider_authority"] is False
    assert artifact["provider_response"]["metadata"]["provider_authority"] is False


def test_provider_cannot_trigger_execution(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")

    def fail_shell(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("shell execution invoked")

    monkeypatch.setattr(subprocess, "run", fail_shell)
    monkeypatch.setattr(os, "system", fail_shell)

    artifact = _engine(RuntimeStore(tmp_path)).dispatch(_package(payload={"prompt": "echo forbidden"})).to_dict()

    guarantees = artifact["provider_response"]["output"]["bounded_execution_guarantees"]
    assert guarantees == {
        "no_tool_execution": True,
        "no_shell_execution": True,
        "no_filesystem_execution": True,
        "no_worker_spawn": True,
        "no_recursive_runtime_dispatch": True,
    }


def test_provider_invocation_replay_reconstruction(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-key")
    store = RuntimeStore(tmp_path)
    _engine(store).dispatch(_package())

    reconstruction = reconstruct_provider_invocation("provider-activation-v1", tmp_path)

    assert reconstruction["status"] == "PROVIDER_INVOCATION_RECONSTRUCTED"
    assert reconstruction["provider_envelope"]["provider"] == "openai"
    assert reconstruction["provider_response"]["response_text"] == "bounded provider response"
    assert reconstruction["ledger_entries"][1]["event_type"] == "PROVIDER_ENVELOPE_PERSISTED"
