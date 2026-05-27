"""Tests for PROVIDER_AGNOSTIC_RAW_RESPONSE_CAPTURE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.live_openai_runtime_connector import (
    NORMALIZED as CONNECTOR_NORMALIZED,
    REJECTED as CONNECTOR_REJECTED,
    LiveOpenAIRuntimeConnectorEvidence,
    invoke_live_openai_runtime_connector,
)
from aigol.runtime.live_runtime_usage_validation import validate_live_runtime_usage
from aigol.runtime.live_cognition_rejection_analysis import (
    STAGE_NONE,
    STAGE_PROPOSAL_NORMALIZATION,
    analyze_live_cognition_rejection,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.raw_provider_response_capture import (
    ABSENT,
    NORMALIZED,
    REJECTED,
    RawProviderResponseEvidence,
    capture_raw_provider_response,
    reconstruct_raw_provider_response_lineage,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:40:00+00:00"


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"PARC-PROPOSAL-{index}",
        "natural_language_input": "Inspect bounded runtime metadata.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:PARC-CONTRACT-{index}",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _openai_call(output_text: str):
    def _call(_normalized_request: dict):
        return SimpleNamespace(output_text=output_text)

    return _call


def _install_openai_sdk_stub(monkeypatch, outputs: list[dict | str]) -> dict:
    serialized = [
        json.dumps(o, sort_keys=True, separators=(",", ":")) if isinstance(o, dict) else o
        for o in outputs
    ]
    captured = {"calls": []}

    class Responses:
        def create(self, *, model: str, input: str):
            captured["calls"].append({"model": model, "input": input})
            return SimpleNamespace(output_text=serialized.pop(0))

    class OpenAI:
        def __init__(self, *, api_key: str, timeout: int, max_retries: int) -> None:
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            captured["max_retries"] = max_retries
            self.responses = Responses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAI))
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    return captured


# --- generic capture model ----------------------------------------------------


def test_capture_raw_provider_response_normalized_path() -> None:
    text = "raw provider output"
    evidence = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-1",
        provider_name="openai",
        model_name="gpt-5.5",
        raw_response_text=text,
        normalization_status=NORMALIZED,
        normalization_reason="captured",
        created_at=CREATED_AT,
    )

    assert evidence.raw_response_present is True
    assert evidence.raw_response_text == text
    assert evidence.raw_response_hash == replay_hash(text)
    assert evidence.evidence_hash.startswith("sha256:")


def test_capture_raw_provider_response_absent_path() -> None:
    evidence = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-ABSENT",
        provider_name="openai",
        model_name="gpt-5.5",
        raw_response_text=None,
        normalization_status=REJECTED,
        normalization_reason="raw response not captured",
        created_at=CREATED_AT,
    )

    assert evidence.raw_response_present is False
    assert evidence.raw_response_text == ""
    assert evidence.raw_response_hash == ""


def test_capture_raw_provider_response_round_trip() -> None:
    evidence = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-2",
        provider_name="claude",
        model_name="claude-opus-4-7",
        raw_response_text="placeholder claude response",
        normalization_status=REJECTED,
        normalization_reason="not yet implemented",
        created_at=CREATED_AT,
    )

    artifact = evidence.to_dict()
    reconstructed = RawProviderResponseEvidence.from_dict(artifact).to_dict()
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")

    assert artifact == reconstructed
    # evidence_hash hashes only the canonical input view (not raw_response_text itself)
    assert evidence_hash.startswith("sha256:")
    assert RawProviderResponseEvidence.from_dict(artifact).evidence_hash == evidence_hash


def test_capture_raw_provider_response_hash_tamper_fails_closed() -> None:
    evidence = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-TAMPER",
        provider_name="openai",
        model_name="gpt-5.5",
        raw_response_text="text-A",
        normalization_status=NORMALIZED,
        normalization_reason="captured",
        created_at=CREATED_AT,
    )
    tampered = deepcopy(evidence.to_dict())
    tampered["raw_response_text"] = "text-B"

    with pytest.raises(FailClosedRuntimeError):
        RawProviderResponseEvidence.from_dict(tampered)


def test_capture_raw_provider_response_invalid_status_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError):
        capture_raw_provider_response(
            raw_response_id="RAW-RESPONSE-INVALID",
            provider_name="openai",
            model_name="gpt-5.5",
            raw_response_text="some text",
            normalization_status="UNKNOWN",
            normalization_reason="bad status",
            created_at=CREATED_AT,
        )


def test_raw_response_lineage_is_append_only_and_deterministic() -> None:
    first = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-A",
        provider_name="openai",
        model_name="gpt-5.5",
        raw_response_text="alpha",
        normalization_status=NORMALIZED,
        normalization_reason="ok",
        created_at="2026-05-27T00:40:00+00:00",
    )
    second = capture_raw_provider_response(
        raw_response_id="RAW-RESPONSE-B",
        provider_name="claude",
        model_name="claude-opus-4-7",
        raw_response_text="beta",
        normalization_status=REJECTED,
        normalization_reason="not implemented",
        created_at="2026-05-27T00:40:01+00:00",
    )

    lineage_a = reconstruct_raw_provider_response_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_raw_provider_response_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["raw_response_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["llm_boundary"] == "raw_response_pre_normalization_only"


def test_raw_response_evidence_has_no_provider_lock_in() -> None:
    import aigol.runtime.raw_provider_response_capture as capture_module

    source = inspect.getsource(capture_module)
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "claude" not in source.lower()
    assert "gpt" not in source.lower()


# --- OpenAI adapter integration ----------------------------------------------


def _invoke_openai_connector(output_text: str, *, inference_id="OPENAI-PARC-1", created_at=CREATED_AT):
    return invoke_live_openai_runtime_connector(
        inference_id=inference_id,
        prompt="Inspect runtime metadata",
        openai_call=_openai_call(output_text),
        created_at=created_at,
    )


def test_openai_adapter_captures_raw_text_on_malformed_output() -> None:
    raw_text = "not-json garbage"
    result = _invoke_openai_connector(raw_text)
    connector_evidence: LiveOpenAIRuntimeConnectorEvidence = result["connector_evidence"]
    raw_evidence: RawProviderResponseEvidence = result["raw_provider_response"]

    assert connector_evidence.connector_status == CONNECTOR_REJECTED
    assert connector_evidence.raw_response_evidence_hash == raw_evidence.evidence_hash
    assert raw_evidence.provider_name == "openai"
    assert raw_evidence.model_name == "gpt-5.5"
    assert raw_evidence.raw_response_present is True
    assert raw_evidence.raw_response_text == raw_text
    assert raw_evidence.raw_response_hash == replay_hash(raw_text)
    assert raw_evidence.normalization_status == REJECTED
    assert result["proposal"] is None


def test_openai_adapter_captures_raw_text_on_normalized_output() -> None:
    text = json.dumps(_model_output(1), sort_keys=True, separators=(",", ":"))
    result = _invoke_openai_connector(text)
    raw_evidence: RawProviderResponseEvidence = result["raw_provider_response"]

    assert result["connector_evidence"].connector_status == CONNECTOR_NORMALIZED
    assert raw_evidence.raw_response_present is True
    assert raw_evidence.raw_response_text == text
    assert raw_evidence.raw_response_hash == replay_hash(text)
    assert raw_evidence.normalization_status == NORMALIZED
    assert isinstance(result["proposal"], BoundedCognitionProposal)


def test_raw_hash_is_deterministic_across_invocations() -> None:
    text = "deterministic raw response"
    first = _invoke_openai_connector(text)["raw_provider_response"]
    second = _invoke_openai_connector(text, inference_id="OPENAI-PARC-2", created_at="2026-05-27T00:40:05+00:00")[
        "raw_provider_response"
    ]

    assert first.raw_response_hash == second.raw_response_hash
    assert first.raw_response_hash == replay_hash(text)


def test_openai_adapter_absent_raw_response_fails_closed() -> None:
    def _call(_normalized_request: dict):
        return SimpleNamespace()  # no output_text attribute

    result = invoke_live_openai_runtime_connector(
        inference_id="OPENAI-PARC-ABSENT",
        prompt="Inspect runtime metadata",
        openai_call=_call,
        created_at=CREATED_AT,
    )

    assert result["connector_evidence"].connector_status == CONNECTOR_REJECTED
    raw_evidence: RawProviderResponseEvidence = result["raw_provider_response"]
    assert raw_evidence.raw_response_present is False
    assert raw_evidence.raw_response_text == ""
    assert raw_evidence.raw_response_hash == ""
    assert raw_evidence.normalization_status == REJECTED


def test_normalization_only_promotes_bounded_cognition_proposal() -> None:
    """AiGOL core must only consume normalized BoundedCognitionProposal artifacts."""

    text = "not-json garbage"
    result = _invoke_openai_connector(text)

    assert result["proposal"] is None
    assert result["proposal_lineage"] is None
    assert result["external_model_response"] is None
    # raw evidence is preserved separately and is NOT a BoundedCognitionProposal
    assert not isinstance(result["raw_provider_response"], BoundedCognitionProposal)


# --- rejection analysis integration ------------------------------------------


def test_rejection_analysis_surfaces_raw_response_on_failed_normalization(monkeypatch) -> None:
    _install_openai_sdk_stub(monkeypatch, ["not-json"])
    usage = validate_live_runtime_usage(
        validation_id="PARC-LCRA-USAGE-1",
        human_prompts=["inspect runtime status"],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    usage_record = usage["usage_records"][0]
    analysis = analyze_live_cognition_rejection(
        analysis_id="PARC-LCRA-ANALYSIS-1",
        usage_record=usage_record,
        created_at=CREATED_AT,
    )
    evidence = analysis["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_PROPOSAL_NORMALIZATION
    assert evidence.raw_provider_response_present is True
    assert evidence.raw_provider_response_provider_name == "openai"
    assert evidence.raw_provider_response_model_name == "gpt-5.5"
    assert evidence.raw_provider_response_normalization_status == REJECTED
    assert evidence.raw_provider_response_normalization_reason
    assert evidence.raw_provider_response_hash == replay_hash("not-json")
    assert isinstance(analysis["raw_provider_response_evidence"], RawProviderResponseEvidence)


def test_rejection_analysis_links_raw_evidence_hash_to_connector(monkeypatch) -> None:
    _install_openai_sdk_stub(
        monkeypatch,
        [json.dumps(_model_output(1), sort_keys=True, separators=(",", ":"))],
    )
    usage = validate_live_runtime_usage(
        validation_id="PARC-LCRA-USAGE-2",
        human_prompts=["inspect runtime status"],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    usage_record = usage["usage_records"][0]
    connector_evidence: LiveOpenAIRuntimeConnectorEvidence = usage_record["invocation"]["connector"]["connector_evidence"]
    raw_evidence: RawProviderResponseEvidence = usage_record["invocation"]["connector"]["raw_provider_response"]
    analysis = analyze_live_cognition_rejection(
        analysis_id="PARC-LCRA-ANALYSIS-2",
        usage_record=usage_record,
        created_at=CREATED_AT,
    )

    assert analysis["analysis_evidence"].rejection_stage == STAGE_NONE
    assert connector_evidence.raw_response_evidence_hash == raw_evidence.evidence_hash
    assert analysis["analysis_evidence"].raw_provider_response_evidence_hash == raw_evidence.evidence_hash


# --- structural assertions ----------------------------------------------------


def test_no_orchestration_or_runtime_mutation_in_capture_module() -> None:
    import aigol.runtime.raw_provider_response_capture as capture_module

    source = inspect.getsource(capture_module)
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


def test_normalization_failure_preserves_fail_closed_boundary() -> None:
    result = _invoke_openai_connector("not-json garbage")

    assert result["connector_evidence"].connector_status == CONNECTOR_REJECTED
    assert result["connector_evidence"].reason == "OpenAI inference normalization failed closed"
    assert result["external_model_response"] is None
    assert result["proposal"] is None
    assert result["proposal_lineage"] is None
    # raw response is still preserved despite fail-closed
    assert result["raw_provider_response"].raw_response_present is True
