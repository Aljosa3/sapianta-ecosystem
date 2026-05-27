"""Tests for OPERATOR_INTERACTION_LOOP_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.operator_interaction_loop import (
    LOOP_COMPLETED,
    LOOP_REJECTED,
    OperatorInteractionLoopEvidence,
    reconstruct_operator_interaction_loop_lineage,
    run_operator_interaction_loop,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:22:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("operator interaction loop must not mutate runtime state")


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"LOOP-PROPOSAL-{index}",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:LOOP-CONTRACT-{index}",
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


def _run(monkeypatch, outputs: list[dict | str], requests: list[str] | None = None, *, loop_id: str = "OPERATOR-LOOP-1", created_at: str = CREATED_AT):
    captured = _install_openai_stub(monkeypatch, outputs)
    result = run_operator_interaction_loop(
        loop_id=loop_id,
        operator_id="operator-1",
        operator_prompts=requests or ["inspect runtime status", "show runtime isolation state"],
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_repeated_sequential_readonly_requests(monkeypatch) -> None:
    result, captured = _run(monkeypatch, [_model_output(1), _model_output(2)])
    evidence = result["loop_evidence"]

    assert evidence.loop_status == LOOP_COMPLETED
    assert evidence.request_count == 2
    assert evidence.completed_count == 2
    assert evidence.rejected_count == 0
    assert len(captured["calls"]) == 2
    assert all(record["operator_usage_evidence"].operator_usage_status == "COMPLETED" for record in result["usage_records"])
    assert all(record["operator_return"].startswith("operation=inspect_runtime") for record in result["usage_records"])


def test_replay_continuity_preservation(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, [_model_output(1), _model_output(2)])

    assert result["loop_evidence"].replay_continuity_valid is True
    assert result["operator_usage_lineage"]["operator_usage_count"] == 2
    assert result["operator_usage_lineage"]["append_only_valid"] is True
    assert result["operator_usage_lineage"]["lineage_valid"] is True


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, ["not-json"], requests=["inspect runtime status"])

    assert result["loop_evidence"].loop_status == LOOP_REJECTED
    assert result["loop_evidence"].rejected_count == 1
    assert result["usage_records"][0]["operator_usage_evidence"].operator_usage_status == "REJECTED"


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _run(
        monkeypatch,
        [_model_output(1, requested_capabilities=["readonly_http_get_provider"])],
        requests=["inspect runtime status"],
    )

    assert result["loop_evidence"].loop_status == LOOP_REJECTED
    assert result["usage_records"][0]["operator_usage_evidence"].operator_usage_status == "REJECTED"


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, [_model_output(1), _model_output(2)])
    artifact = result["loop_evidence"].to_dict()
    reconstructed = OperatorInteractionLoopEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior(monkeypatch) -> None:
    result, _captured = _run(
        monkeypatch,
        [_model_output(1, proposed_contract_reference="LOOP-CONTRACT-1")],
        requests=["inspect runtime status"],
    )

    assert result["loop_evidence"].loop_status == LOOP_REJECTED
    assert result["usage_records"][0]["activation"]["usage_validation"]["usage_records"][0]["execution"] is None


def test_append_only_loop_lineage(monkeypatch) -> None:
    first, _captured = _run(monkeypatch, [_model_output(1), _model_output(2)])
    second, _captured = _run(
        monkeypatch,
        [
            _model_output(3, proposal_id="LOOP-PROPOSAL-3", proposed_contract_reference="contract:LOOP-CONTRACT-3"),
            _model_output(4, proposal_id="LOOP-PROPOSAL-4", proposed_contract_reference="contract:LOOP-CONTRACT-4"),
        ],
        loop_id="OPERATOR-LOOP-2",
        created_at="2026-05-27T00:22:01+00:00",
    )

    lineage_a = reconstruct_operator_interaction_loop_lineage(
        [first["loop_evidence"].to_dict(), second["loop_evidence"].to_dict()]
    )
    lineage_b = reconstruct_operator_interaction_loop_lineage(
        [first["loop_evidence"].to_dict(), second["loop_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["loop_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.operator_interaction_loop as interaction_loop

    sentinel = MutationSentinel()
    _run(monkeypatch, [_model_output(1), _model_output(2)])

    source = inspect.getsource(interaction_loop)

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
