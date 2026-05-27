"""Tests for REAL_OPERATOR_RUNTIME_EXPERIMENTS_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.real_operator_runtime_experiments import (
    EXPERIMENT_COMPLETED,
    EXPERIMENT_REJECTED,
    RealOperatorRuntimeExperimentsEvidence,
    reconstruct_real_operator_runtime_experiments_lineage,
    run_real_operator_runtime_experiments,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:24:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("operator runtime experiments must not mutate runtime state")


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"EXPERIMENT-PROPOSAL-{index}",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:EXPERIMENT-CONTRACT-{index}",
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


def _run(
    monkeypatch,
    outputs: list[dict | str],
    prompts: list[str] | None = None,
    *,
    experiment_id: str = "OPERATOR-RUNTIME-EXPERIMENT-1",
    created_at: str = CREATED_AT,
):
    captured = _install_openai_stub(monkeypatch, outputs)
    result = run_real_operator_runtime_experiments(
        experiment_id=experiment_id,
        operator_id="operator-1",
        operator_prompts=prompts
        or [
            "inspect runtime status",
            "inspect governance metadata",
            "inspect replay continuity",
            "inspect readonly filesystem state",
        ],
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_repeated_readonly_operator_experiments(monkeypatch) -> None:
    result, captured = _run(
        monkeypatch,
        [_model_output(1), _model_output(2), _model_output(3), _model_output(4)],
    )
    evidence = result["experiment_evidence"]

    assert evidence.experiment_status == EXPERIMENT_COMPLETED
    assert evidence.scenario_count == 4
    assert evidence.completed_count == 4
    assert evidence.rejected_count == 0
    assert len(captured["calls"]) == 4
    assert all(record["cli_evidence"].cli_status == "SUCCESS" for record in result["cli_records"])


def test_replay_continuity_preservation(monkeypatch) -> None:
    result, _captured = _run(
        monkeypatch,
        [_model_output(1), _model_output(2)],
        prompts=["inspect runtime status", "inspect replay continuity"],
    )

    assert result["experiment_evidence"].replay_continuity_valid is True
    assert result["cli_lineage"]["cli_invocation_count"] == 2
    assert result["cli_lineage"]["append_only_valid"] is True
    assert result["cli_lineage"]["lineage_valid"] is True


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, ["not-json"], prompts=["inspect runtime status"])

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["experiment_evidence"].rejected_count == 1
    assert result["cli_records"][0]["cli_evidence"].cli_status == "REJECTED"


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _run(
        monkeypatch,
        [_model_output(1, requested_capabilities=["readonly_http_get_provider"])],
        prompts=["inspect runtime status"],
    )

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["cli_records"][0]["operator_usage"]["activation"]["usage_validation"]["usage_records"][0]["usage_status"] == "REJECTED"


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, [_model_output(1), _model_output(2)])
    artifact = result["experiment_evidence"].to_dict()
    reconstructed = RealOperatorRuntimeExperimentsEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior(monkeypatch) -> None:
    result, _captured = _run(
        monkeypatch,
        [_model_output(1, proposed_contract_reference="EXPERIMENT-CONTRACT-1")],
        prompts=["inspect runtime status"],
    )

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["cli_records"][0]["operator_usage"]["activation"]["usage_validation"]["usage_records"][0]["execution"] is None


def test_append_only_experiment_lineage(monkeypatch) -> None:
    first, _captured = _run(monkeypatch, [_model_output(1), _model_output(2)])
    second, _captured = _run(
        monkeypatch,
        [
            _model_output(3, proposal_id="EXPERIMENT-PROPOSAL-3", proposed_contract_reference="contract:EXPERIMENT-CONTRACT-3"),
            _model_output(4, proposal_id="EXPERIMENT-PROPOSAL-4", proposed_contract_reference="contract:EXPERIMENT-CONTRACT-4"),
        ],
        experiment_id="OPERATOR-RUNTIME-EXPERIMENT-2",
        created_at="2026-05-27T00:24:01+00:00",
    )

    lineage_a = reconstruct_real_operator_runtime_experiments_lineage(
        [first["experiment_evidence"].to_dict(), second["experiment_evidence"].to_dict()]
    )
    lineage_b = reconstruct_real_operator_runtime_experiments_lineage(
        [first["experiment_evidence"].to_dict(), second["experiment_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["experiment_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.real_operator_runtime_experiments as experiments

    sentinel = MutationSentinel()
    _run(monkeypatch, [_model_output(1), _model_output(2)])

    source = inspect.getsource(experiments)

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
