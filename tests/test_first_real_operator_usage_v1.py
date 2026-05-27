"""Tests for FIRST_REAL_OPERATOR_USAGE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.first_real_operator_usage import (
    OPERATOR_COMPLETED,
    OPERATOR_REJECTED,
    FirstRealOperatorUsageEvidence,
    reconstruct_first_real_operator_usage_lineage,
    run_first_real_operator_usage,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:21:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("first real operator usage must not mutate runtime state")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "OPERATOR-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:OPERATOR-CONTRACT-1",
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
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    return captured


def _run(monkeypatch, output: dict | str | None = None, *, usage_id: str = "OPERATOR-USAGE-1", created_at: str = CREATED_AT):
    captured = _install_openai_stub(monkeypatch, output)
    result = run_first_real_operator_usage(
        operator_usage_id=usage_id,
        operator_id="operator-1",
        operator_request="  inspect runtime status  ",
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_successful_readonly_operator_request(monkeypatch) -> None:
    result, captured = _run(monkeypatch)
    evidence = result["operator_usage_evidence"]

    assert evidence.operator_usage_status == OPERATOR_COMPLETED
    assert result["activation"]["activation_evidence"].activation_status == "ACTIVATED"
    assert result["operator_return"].startswith("operation=inspect_runtime")
    assert result["operator_lineage"]["operator_usage_count"] == 1
    assert result["governance_authority_separated"] is True
    assert captured["api_key"] == "test-openai-key"
    assert captured["max_retries"] == 0


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, "not-json")

    assert result["operator_usage_evidence"].operator_usage_status == OPERATOR_REJECTED
    assert result["activation"]["activation_evidence"].activation_status == "REJECTED"
    assert result["operator_return"] == "operator usage rejected"


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, _model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["operator_usage_evidence"].operator_usage_status == OPERATOR_REJECTED
    assert result["activation"]["usage_validation"]["usage_records"][0]["usage_status"] == "REJECTED"


def test_replay_continuity_preservation(monkeypatch) -> None:
    first, _captured = _run(monkeypatch, usage_id="OPERATOR-USAGE-1", created_at="2026-05-27T00:21:00+00:00")
    second, _captured = _run(
        monkeypatch,
        _model_output(
            proposal_id="OPERATOR-PROPOSAL-2",
            proposed_contract_reference="contract:OPERATOR-CONTRACT-2",
        ),
        usage_id="OPERATOR-USAGE-2",
        created_at="2026-05-27T00:21:01+00:00",
    )

    lineage_a = reconstruct_first_real_operator_usage_lineage(
        [first["operator_usage_evidence"].to_dict(), second["operator_usage_evidence"].to_dict()]
    )
    lineage_b = reconstruct_first_real_operator_usage_lineage(
        [first["operator_usage_evidence"].to_dict(), second["operator_usage_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["operator_usage_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _run(monkeypatch)
    artifact = result["operator_usage_evidence"].to_dict()
    reconstructed = FirstRealOperatorUsageEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, _model_output(proposed_contract_reference="OPERATOR-CONTRACT-1"))

    assert result["operator_usage_evidence"].operator_usage_status == OPERATOR_REJECTED
    assert result["activation"]["usage_validation"]["usage_records"][0]["execution"] is None


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.first_real_operator_usage as operator_usage

    sentinel = MutationSentinel()
    _run(monkeypatch)

    source = inspect.getsource(operator_usage)

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
