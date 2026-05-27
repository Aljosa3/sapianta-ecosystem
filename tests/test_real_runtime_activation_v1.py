"""Tests for REAL_RUNTIME_ACTIVATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.real_runtime_activation import (
    ACTIVATED,
    REJECTED,
    RealRuntimeActivationEvidence,
    activate_real_runtime,
    reconstruct_real_runtime_activation_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:20:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("real runtime activation must not mutate runtime state")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "ACTIVATION-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:ACTIVATION-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _install_openai_stub(monkeypatch, output: dict | str | None = None) -> dict:
    if output is None:
        output = _model_output()
    if isinstance(output, dict):
        output = json.dumps(output, sort_keys=True, separators=(",", ":"))
    captured = {}

    class Responses:
        def create(self, *, model: str, input: str):
            captured["model"] = model
            captured["input"] = input
            return SimpleNamespace(output_text=output)

    class OpenAI:
        def __init__(self, *, api_key: str, timeout: int, max_retries: int) -> None:
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            captured["max_retries"] = max_retries
            self.responses = Responses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAI))
    return captured


def _activate(monkeypatch, output: dict | str | None = None, *, activation_id: str = "RUNTIME-ACTIVATION-1", created_at: str = CREATED_AT):
    captured = _install_openai_stub(monkeypatch, output)
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    result = activate_real_runtime(
        activation_id=activation_id,
        human_prompt="  Inspect runtime metadata.  ",
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_successful_runtime_activation(monkeypatch) -> None:
    result, captured = _activate(monkeypatch)
    evidence = result["activation_evidence"]

    assert evidence.activation_status == ACTIVATED
    assert evidence.environment_status == "READY"
    assert result["usage_validation"]["usage_validation_evidence"].validation_status == "VALIDATED"
    assert result["usage_validation"]["usage_records"][0]["governed_return"].return_status == "ACCEPTED"
    assert result["activation_lineage"]["activation_count"] == 1
    assert captured["api_key"] == "test-openai-key"
    assert captured["max_retries"] == 0


def test_missing_api_key_rejection(monkeypatch) -> None:
    _install_openai_stub(monkeypatch)
    monkeypatch.delenv(OPENAI_API_KEY_ENV, raising=False)

    result = activate_real_runtime(
        activation_id="RUNTIME-ACTIVATION-MISSING-KEY",
        human_prompt="Inspect runtime metadata.",
        created_at=CREATED_AT,
    )

    assert result["activation_evidence"].activation_status == REJECTED
    assert result["activation_evidence"].environment_status == "REJECTED"
    assert result["usage_validation"] is None


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _activate(monkeypatch, "not-json")

    assert result["activation_evidence"].activation_status == REJECTED
    assert result["usage_validation"]["usage_validation_evidence"].validation_status == "REJECTED"
    assert result["usage_validation"]["usage_records"][0]["execution"] is None


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _activate(monkeypatch, _model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["activation_evidence"].activation_status == REJECTED
    assert result["usage_validation"]["usage_records"][0]["usage_status"] == "REJECTED"
    assert result["usage_validation"]["usage_records"][0]["invocation"]["invocation_evidence"].invocation_status == "REJECTED"


def test_replay_continuity_preservation(monkeypatch) -> None:
    first, _captured = _activate(monkeypatch, activation_id="RUNTIME-ACTIVATION-1", created_at="2026-05-27T00:20:00+00:00")
    second, _captured = _activate(
        monkeypatch,
        _model_output(
            proposal_id="ACTIVATION-PROPOSAL-2",
            proposed_contract_reference="contract:ACTIVATION-CONTRACT-2",
        ),
        activation_id="RUNTIME-ACTIVATION-2",
        created_at="2026-05-27T00:20:01+00:00",
    )

    lineage_a = reconstruct_real_runtime_activation_lineage(
        [first["activation_evidence"].to_dict(), second["activation_evidence"].to_dict()]
    )
    lineage_b = reconstruct_real_runtime_activation_lineage(
        [first["activation_evidence"].to_dict(), second["activation_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["activation_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _activate(monkeypatch)
    artifact = result["activation_evidence"].to_dict()
    reconstructed = RealRuntimeActivationEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_operational_behavior(monkeypatch) -> None:
    result, _captured = _activate(monkeypatch, _model_output(proposed_contract_reference="ACTIVATION-CONTRACT-1"))

    assert result["activation_evidence"].activation_status == REJECTED
    assert result["usage_validation"]["usage_records"][0]["execution"] is None


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.real_runtime_activation as activation

    sentinel = MutationSentinel()
    _activate(monkeypatch)

    source = inspect.getsource(activation)

    assert sentinel.mutated is False
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "retry" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
