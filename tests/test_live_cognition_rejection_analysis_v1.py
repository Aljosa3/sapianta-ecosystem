"""Tests for LIVE_COGNITION_REJECTION_ANALYSIS_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

from aigol.runtime.live_cognition_rejection_analysis import (
    ANALYSIS_MODE,
    LiveCognitionRejectionAnalysisEvidence,
    STAGE_NONE,
    STAGE_OPENAI_INVOCATION,
    STAGE_USAGE_INPUT,
    analyze_live_cognition_rejection,
    reconstruct_live_cognition_rejection_analysis_lineage,
    render_rejection_analysis_summary,
)
from aigol.runtime.live_cognition_rejection_analysis_cli import (
    run_live_cognition_rejection_analysis_cli,
)
from aigol.runtime.live_runtime_usage_validation import validate_live_runtime_usage
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:30:00+00:00"


def _model_output(index: int = 1, **overrides) -> dict:
    output = {
        "proposal_id": f"REJECTION-ANALYSIS-PROPOSAL-{index}",
        "natural_language_input": "Inspect bounded runtime metadata.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:REJECTION-ANALYSIS-CONTRACT-{index}",
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


def _run_usage(monkeypatch, outputs, *, validation_id="LCRA-VALIDATION-1", created_at=CREATED_AT):
    _install_openai_stub(monkeypatch, outputs)
    usage = validate_live_runtime_usage(
        validation_id=validation_id,
        human_prompts=["inspect runtime status"],
        created_at=created_at,
        timeout_seconds=7,
    )
    return usage["usage_records"][0]


def _analyze(monkeypatch, outputs, *, analysis_id="LCRA-ANALYSIS-1", created_at=CREATED_AT):
    usage_record = _run_usage(monkeypatch, outputs, created_at=created_at)
    return analyze_live_cognition_rejection(
        analysis_id=analysis_id,
        usage_record=usage_record,
        created_at=created_at,
    )


def test_valid_request_emits_no_rejection(monkeypatch) -> None:
    result = _analyze(monkeypatch, [_model_output(1)])
    evidence = result["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_NONE
    assert evidence.usage_status == "VALIDATED"
    assert evidence.openai_connector_status == "NORMALIZED"
    assert evidence.raw_openai_output_present is True
    assert evidence.normalized_proposal_present is True
    assert result["raw_openai_output"]["proposed_contract_reference"].startswith("contract:")
    assert result["normalized_proposal"]["proposal_type"] == "CONTRACT_PROPOSAL"
    assert evidence.cognition_review_decision["status"] == "REVIEWED"
    assert evidence.authorization_decision["status"] == "AUTHORIZED"
    assert evidence.routing_decision["status"] == "ROUTED"
    assert evidence.isolation_decision["status"] == "ISOLATED"
    assert evidence.governed_return_decision["status"] == "ACCEPTED"


def test_malformed_cognition_rejection_is_attributed_to_openai_stage(monkeypatch) -> None:
    result = _analyze(monkeypatch, ["not-json"])
    evidence = result["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_OPENAI_INVOCATION
    assert evidence.usage_status == "REJECTED"
    assert evidence.openai_connector_status == "REJECTED"
    assert evidence.openai_connector_reason
    assert evidence.raw_openai_output_present is False
    assert evidence.normalized_proposal_present is False
    assert evidence.cognition_review_decision == {}
    assert evidence.authorization_decision == {}
    assert evidence.routing_decision == {}


def test_unauthorized_capability_rejection_is_attributed_to_openai_stage(monkeypatch) -> None:
    result = _analyze(
        monkeypatch,
        [_model_output(1, requested_capabilities=["readonly_http_get_provider"])],
    )
    evidence = result["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_OPENAI_INVOCATION
    assert evidence.usage_status == "REJECTED"
    assert evidence.openai_connector_status == "REJECTED"
    assert evidence.raw_openai_output_present is False


def test_invalid_contract_reference_is_attributed_to_openai_stage(monkeypatch) -> None:
    result = _analyze(
        monkeypatch,
        [_model_output(1, proposed_contract_reference="MISSING-PREFIX")],
    )
    evidence = result["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_OPENAI_INVOCATION
    assert evidence.usage_status == "REJECTED"
    assert evidence.openai_connector_status == "REJECTED"


def test_missing_usage_record_fails_closed() -> None:
    result = analyze_live_cognition_rejection(
        analysis_id="LCRA-ANALYSIS-MISSING",
        usage_record=None,
        created_at=CREATED_AT,
    )
    evidence = result["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_USAGE_INPUT
    assert evidence.usage_status == "REJECTED"
    assert evidence.usage_id == "USAGE-INVALID"


def test_deterministic_evidence_generation(monkeypatch) -> None:
    result = _analyze(monkeypatch, [_model_output(1)])
    artifact = result["analysis_evidence"].to_dict()
    reconstructed = LiveCognitionRejectionAnalysisEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_analysis_lineage(monkeypatch) -> None:
    first = _analyze(monkeypatch, [_model_output(1)])
    second = _analyze(
        monkeypatch,
        [_model_output(2, proposal_id="REJECTION-ANALYSIS-PROPOSAL-2", proposed_contract_reference="contract:REJECTION-ANALYSIS-CONTRACT-2")],
        analysis_id="LCRA-ANALYSIS-2",
        created_at="2026-05-27T00:30:01+00:00",
    )
    lineage = reconstruct_live_cognition_rejection_analysis_lineage(
        [first["analysis_evidence"].to_dict(), second["analysis_evidence"].to_dict()]
    )
    repeated = reconstruct_live_cognition_rejection_analysis_lineage(
        [first["analysis_evidence"].to_dict(), second["analysis_evidence"].to_dict()]
    )

    assert lineage == repeated
    assert lineage["analysis_count"] == 2
    assert lineage["append_only_valid"] is True
    assert lineage["governance_authority_separated"] is True


def test_rendered_summary_surfaces_inspection_fields(monkeypatch) -> None:
    result = _analyze(monkeypatch, ["not-json"])
    summary = render_rejection_analysis_summary(result["analysis_evidence"])

    assert "rejection_stage=OPENAI_INVOCATION" in summary
    assert "openai_connector_status=REJECTED" in summary
    assert "raw_openai_output_present=False" in summary
    assert "normalized_proposal_present=False" in summary
    assert "cognition_review_status=ABSENT" in summary
    assert "authorization_status=ABSENT" in summary
    assert "routing_status=ABSENT" in summary
    assert "isolation_status=ABSENT" in summary
    assert "governed_return_status=ABSENT" in summary


def test_cli_surface_runs_inspection_for_rejected_prompt(monkeypatch) -> None:
    _install_openai_stub(monkeypatch, ["not-json"])
    result = run_live_cognition_rejection_analysis_cli(
        analysis_id="LCRA-CLI-1",
        operator_prompt="inspect runtime status",
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    evidence = result["analysis"]["analysis_evidence"]

    assert result["exit_code"] == 1
    assert evidence.rejection_stage == STAGE_OPENAI_INVOCATION
    assert evidence.analysis_mode == ANALYSIS_MODE
    assert "rejection_stage=OPENAI_INVOCATION" in result["rendered_output"]


def test_cli_surface_runs_inspection_for_completed_prompt(monkeypatch) -> None:
    _install_openai_stub(monkeypatch, [json.dumps(_model_output(1), sort_keys=True, separators=(",", ":"))])
    result = run_live_cognition_rejection_analysis_cli(
        analysis_id="LCRA-CLI-2",
        operator_prompt="inspect runtime status",
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    evidence = result["analysis"]["analysis_evidence"]

    assert result["exit_code"] == 0
    assert evidence.rejection_stage == STAGE_NONE
    assert evidence.openai_connector_status == "NORMALIZED"


def test_no_unbounded_runtime_surface() -> None:
    import aigol.runtime.live_cognition_rejection_analysis as analysis_module
    import aigol.runtime.live_cognition_rejection_analysis_cli as cli_module

    for module in (analysis_module, cli_module):
        source = inspect.getsource(module)
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
