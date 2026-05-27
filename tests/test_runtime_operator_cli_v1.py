"""Tests for RUNTIME_OPERATOR_CLI_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.operator_cli import (
    CLI_COMPLETED,
    CLI_REJECTED,
    RuntimeOperatorCLIEvidence,
    main,
    reconstruct_runtime_operator_cli_lineage,
    run_runtime_operator_cli,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:23:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("operator CLI must not mutate runtime state")


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"CLI-PROPOSAL-{index}",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:CLI-CONTRACT-{index}",
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


def _run(monkeypatch, output: dict | str | None = None, *, cli_id: str = "RUNTIME-OPERATOR-CLI-1", created_at: str = CREATED_AT):
    captured = _install_openai_stub(monkeypatch, output)
    result = run_runtime_operator_cli(
        cli_invocation_id=cli_id,
        operator_id="operator-1",
        operator_prompt="  inspect runtime status  ",
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_successful_readonly_operator_cli_request(monkeypatch, capsys) -> None:
    captured = _install_openai_stub(monkeypatch)

    exit_code = main(
        [
            "inspect runtime status",
            "--operator-id",
            "operator-1",
            "--cli-id",
            "RUNTIME-OPERATOR-CLI-1",
            "--created-at",
            CREATED_AT,
            "--timeout-seconds",
            "7",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "status=COMPLETED" in output
    assert "return=operation=inspect_runtime" in output
    assert "cli_evidence_hash=sha256:" in output
    assert "operator_usage_evidence_hash=sha256:" in output
    assert "activation_evidence_hash=sha256:" in output
    assert captured["api_key"] == "test-openai-key"
    assert captured["max_retries"] == 0


def test_malformed_cognition_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, "not-json")

    assert result["exit_code"] == 1
    assert result["cli_evidence"].cli_status == CLI_REJECTED
    assert "status=REJECTED" in result["rendered_output"]
    assert result["operator_usage"]["operator_usage_evidence"].operator_usage_status == "REJECTED"


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, _model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["exit_code"] == 1
    assert result["cli_evidence"].cli_status == CLI_REJECTED
    assert result["operator_usage"]["activation"]["usage_validation"]["usage_records"][0]["usage_status"] == "REJECTED"


def test_replay_continuity_preservation(monkeypatch) -> None:
    first, _captured = _run(monkeypatch, cli_id="RUNTIME-OPERATOR-CLI-1", created_at="2026-05-27T00:23:00+00:00")
    second, _captured = _run(
        monkeypatch,
        _model_output(
            index=2,
            proposal_id="CLI-PROPOSAL-2",
            proposed_contract_reference="contract:CLI-CONTRACT-2",
        ),
        cli_id="RUNTIME-OPERATOR-CLI-2",
        created_at="2026-05-27T00:23:01+00:00",
    )

    lineage_a = reconstruct_runtime_operator_cli_lineage(
        [first["cli_evidence"].to_dict(), second["cli_evidence"].to_dict()]
    )
    lineage_b = reconstruct_runtime_operator_cli_lineage(
        [first["cli_evidence"].to_dict(), second["cli_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["cli_invocation_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result, _captured = _run(monkeypatch)
    artifact = result["cli_evidence"].to_dict()
    reconstructed = RuntimeOperatorCLIEvidence.from_dict(artifact).to_dict()

    assert result["cli_evidence"].cli_status == CLI_COMPLETED
    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior(monkeypatch) -> None:
    result, _captured = _run(monkeypatch, _model_output(proposed_contract_reference="CLI-CONTRACT-1"))

    assert result["exit_code"] == 1
    assert result["cli_evidence"].cli_status == CLI_REJECTED
    assert result["operator_usage"]["activation"]["usage_validation"]["usage_records"][0]["execution"] is None


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.operator_cli as operator_cli

    sentinel = MutationSentinel()
    _run(monkeypatch)

    source = inspect.getsource(operator_cli)

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
