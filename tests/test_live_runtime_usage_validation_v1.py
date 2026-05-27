"""Tests for LIVE_RUNTIME_USAGE_VALIDATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.live_runtime_usage_validation import (
    REJECTED,
    VALIDATED,
    LiveRuntimeUsageValidationEvidence,
    reconstruct_live_runtime_usage_validation_lineage,
    validate_live_runtime_usage,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:19:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("live runtime usage validation must not mutate runtime state")


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"USAGE-PROPOSAL-{index}",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:USAGE-CONTRACT-{index}",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _install_openai_stub(monkeypatch, outputs: list[dict | str]) -> dict:
    serialized_outputs = [
        json.dumps(output, sort_keys=True, separators=(",", ":")) if isinstance(output, dict) else output
        for output in outputs
    ]
    captured = {"calls": []}

    class Responses:
        def create(self, *, model: str, input: str):
            captured["calls"].append({"model": model, "input": input})
            output = serialized_outputs.pop(0)
            return SimpleNamespace(output_text=output)

    class OpenAI:
        def __init__(self, *, api_key: str, timeout: int, max_retries: int) -> None:
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            captured["max_retries"] = max_retries
            self.responses = Responses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAI))
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    return captured


def _validate(monkeypatch, outputs: list[dict | str], requests: list[str] | None = None):
    captured = _install_openai_stub(monkeypatch, outputs)
    result = validate_live_runtime_usage(
        validation_id="USAGE-VALIDATION-1",
        human_prompts=requests or ["Inspect runtime metadata.", "Show runtime isolation state."],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    return result, captured


def test_repeated_readonly_runtime_usage(monkeypatch) -> None:
    result, captured = _validate(monkeypatch, [_model_output(1), _model_output(2)])
    evidence = result["usage_validation_evidence"]

    assert evidence.validation_status == VALIDATED
    assert evidence.usage_count == 2
    assert evidence.successful_count == 2
    assert evidence.rejected_count == 0
    assert len(captured["calls"]) == 2
    assert all(record["usage_status"] == VALIDATED for record in result["usage_records"])
    assert all(record["governed_return"].return_status == "ACCEPTED" for record in result["usage_records"])


def test_replay_continuity_preservation(monkeypatch) -> None:
    result, _captured = _validate(monkeypatch, [_model_output(1), _model_output(2)])

    assert result["invocation_lineage"]["invocation_count"] == 2
    assert result["invocation_lineage"]["append_only_valid"] is True
    assert result["invocation_lineage"]["lineage_valid"] is True
    assert result["usage_validation_evidence"].replay_continuity_valid is True


def test_governed_return_consistency(monkeypatch) -> None:
    result, _captured = _validate(monkeypatch, [_model_output(1), _model_output(2)])

    assert result["usage_validation_evidence"].governed_return_consistent is True
    assert all(
        record["governed_return"].provider_reference == "metadata_inspection_provider.inspect_runtime"
        for record in result["usage_records"]
    )
    assert all(record["return_display"].startswith("operation=inspect_runtime") for record in result["usage_records"])


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _validate(monkeypatch, ["not-json"], requests=["Inspect runtime metadata."])
    evidence = result["usage_validation_evidence"]

    assert evidence.validation_status == REJECTED
    assert evidence.usage_count == 1
    assert evidence.rejected_count == 1
    assert result["usage_records"][0]["usage_status"] == REJECTED
    assert result["usage_records"][0]["execution"] is None


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _validate(
        monkeypatch,
        [_model_output(1, requested_capabilities=["readonly_http_get_provider"])],
        requests=["Inspect runtime metadata."],
    )

    assert result["usage_validation_evidence"].validation_status == REJECTED
    assert result["usage_records"][0]["usage_status"] == REJECTED
    assert result["usage_records"][0]["invocation"]["invocation_evidence"].invocation_status == "REJECTED"


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _validate(monkeypatch, [_model_output(1), _model_output(2)])
    artifact = result["usage_validation_evidence"].to_dict()
    reconstructed = LiveRuntimeUsageValidationEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior(monkeypatch) -> None:
    result, _captured = _validate(
        monkeypatch,
        [_model_output(1, proposed_contract_reference="USAGE-CONTRACT-1")],
        requests=["Inspect runtime metadata."],
    )

    assert result["usage_validation_evidence"].validation_status == REJECTED
    assert result["usage_records"][0]["usage_status"] == REJECTED
    assert result["usage_records"][0]["execution"] is None


def test_append_only_usage_validation_lineage(monkeypatch) -> None:
    first, _captured = _validate(monkeypatch, [_model_output(1), _model_output(2)])
    _install_openai_stub(monkeypatch, [_model_output(3), _model_output(4)])
    second = validate_live_runtime_usage(
        validation_id="USAGE-VALIDATION-2",
        human_prompts=["Inspect runtime metadata.", "Show replay lineage status."],
        created_at="2026-05-27T00:19:01+00:00",
        timeout_seconds=7,
    )

    lineage_a = reconstruct_live_runtime_usage_validation_lineage(
        [first["usage_validation_evidence"].to_dict(), second["usage_validation_evidence"].to_dict()]
    )
    lineage_b = reconstruct_live_runtime_usage_validation_lineage(
        [first["usage_validation_evidence"].to_dict(), second["usage_validation_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["validation_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.live_runtime_usage_validation as usage_validation

    sentinel = MutationSentinel()
    _validate(monkeypatch, [_model_output(1), _model_output(2)])

    source = inspect.getsource(usage_validation)

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
    assert "open(" not in source
    assert "Path(" not in source
