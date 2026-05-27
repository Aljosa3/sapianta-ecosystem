"""Tests for REAL_OPENAI_API_INVOCATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.real_openai_api_invocation import (
    INVOKED,
    OPENAI_API_KEY_ENV,
    REJECTED,
    RealOpenAIAPIInvocationEvidence,
    invoke_real_openai_api,
    reconstruct_real_openai_api_invocation_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:18:00+00:00"


class RuntimeMutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("real OpenAI API invocation must not mutate runtime state")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "REAL-OPENAI-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:REAL-OPENAI-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _install_openai_stub(monkeypatch, output: dict | str | None = None, captured: dict | None = None) -> dict:
    if output is None:
        output = _model_output()
    if isinstance(output, dict):
        output = json.dumps(output, sort_keys=True, separators=(",", ":"))
    captured = {} if captured is None else captured

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


def _invoke(monkeypatch, output: dict | str | None = None, *, invocation_id: str = "REAL-OPENAI-1", created_at: str = CREATED_AT):
    captured = _install_openai_stub(monkeypatch, output)
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    result = invoke_real_openai_api(
        invocation_id=invocation_id,
        human_request="  Inspect runtime metadata.  ",
        created_at=created_at,
        timeout_seconds=7,
    )
    return result, captured


def test_valid_live_openai_inference_normalization(monkeypatch) -> None:
    result, captured = _invoke(monkeypatch)
    evidence = result["invocation_evidence"]

    assert evidence.invocation_status == INVOKED
    assert result["connector"]["connector_evidence"].connector_status == "NORMALIZED"
    assert result["proposal"].proposal_id == "REAL-OPENAI-PROPOSAL-1"
    assert result["proposal"].requested_capabilities == ("metadata_inspection_provider",)
    assert captured["api_key"] == "test-openai-key"
    assert captured["timeout"] == 7
    assert captured["max_retries"] == 0
    assert captured["model"] == "gpt-5.5"
    assert "bounded_cognition_proposal_v1" in captured["input"]


def test_missing_api_key_rejection(monkeypatch) -> None:
    _install_openai_stub(monkeypatch)
    monkeypatch.delenv(OPENAI_API_KEY_ENV, raising=False)

    result = invoke_real_openai_api(
        invocation_id="REAL-OPENAI-MISSING-KEY",
        human_request="Inspect runtime metadata.",
        created_at=CREATED_AT,
    )

    assert result["invocation_evidence"].invocation_status == REJECTED
    assert result["connector"] is None
    assert result["proposal"] is None


def test_malformed_response_rejection(monkeypatch) -> None:
    result, _captured = _invoke(monkeypatch, "not-json")

    assert result["invocation_evidence"].invocation_status == REJECTED
    assert result["connector"]["connector_evidence"].connector_status == "REJECTED"
    assert result["proposal"] is None


def test_unauthorized_capability_rejection(monkeypatch) -> None:
    result, _captured = _invoke(monkeypatch, _model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["invocation_evidence"].invocation_status == REJECTED
    assert result["connector"]["connector_evidence"].connector_status == "REJECTED"
    assert result["proposal"] is None


def test_deterministic_proposal_lineage(monkeypatch) -> None:
    first, _captured = _invoke(monkeypatch, invocation_id="REAL-OPENAI-1", created_at="2026-05-27T00:18:00+00:00")
    second, _captured = _invoke(
        monkeypatch,
        _model_output(
            proposal_id="REAL-OPENAI-PROPOSAL-2",
            proposed_contract_reference="contract:REAL-OPENAI-CONTRACT-2",
        ),
        invocation_id="REAL-OPENAI-2",
        created_at="2026-05-27T00:18:01+00:00",
    )

    lineage_a = reconstruct_real_openai_api_invocation_lineage(
        [first["invocation_evidence"].to_dict(), second["invocation_evidence"].to_dict()]
    )
    lineage_b = reconstruct_real_openai_api_invocation_lineage(
        [first["invocation_evidence"].to_dict(), second["invocation_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["invocation_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_replay_visible_inference_evidence(monkeypatch) -> None:
    result, _captured = _invoke(monkeypatch)
    artifact = result["invocation_evidence"].to_dict()
    reconstructed = RealOpenAIAPIInvocationEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation(monkeypatch) -> None:
    result, _captured = _invoke(monkeypatch)
    proposal = result["proposal"].to_dict()

    assert result["governance_authority_separated"] is True
    assert "authorization_id" not in proposal
    assert "routing_id" not in proposal
    assert "session_id" not in proposal


def test_fail_closed_normalization_validation(monkeypatch) -> None:
    result, _captured = _invoke(monkeypatch, _model_output(proposed_contract_reference="REAL-OPENAI-CONTRACT-1"))

    assert result["invocation_evidence"].invocation_status == REJECTED
    assert result["proposal"] is None


def test_no_unbounded_runtime_surface(monkeypatch) -> None:
    import aigol.runtime.real_openai_api_invocation as invocation

    sentinel = RuntimeMutationSentinel()
    _invoke(monkeypatch)

    source = inspect.getsource(invocation)

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
    assert "max_retries=0" in source
