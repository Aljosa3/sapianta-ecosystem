"""Tests for LIVE_PROVIDER_NORMALIZATION_SUCCESS_V1.

Stabilizes the FIRST successful real governed cognition normalization path:
raw provider output -> bounded extraction -> normalized BoundedCognitionProposal
-> readonly governed cognition flow -> operator CLI status=SUCCESS.
"""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import sys
from types import SimpleNamespace

import pytest

from aigol.runtime.bounded_extraction_layer import (
    BOUNDED_SCHEMA_V1,
    BoundedExtractionEvidence,
    NORMALIZATION_FAILURE_NONE,
    NORMALIZED,
    REJECTED,
    SCHEMA_FAILURE_NONE,
    STAGE_BOUNDED_NORMALIZATION,
    extract_bounded_cognition_proposal,
    reconstruct_bounded_extraction_lineage,
)
from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.live_cognition_rejection_analysis import (
    STAGE_BOUNDED_EXTRACTION,
    STAGE_NONE,
    analyze_live_cognition_rejection,
)
from aigol.runtime.live_runtime_usage_validation import validate_live_runtime_usage
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_cli import CLI_SUCCESS, main, run_runtime_operator_cli
from aigol.runtime.raw_provider_response_fixtures import (
    EXPECTED_OUTCOMES,
    FIXTURE_EMPTY_RESPONSE,
    FIXTURE_INVALID_CAPABILITY_ESCALATION,
    FIXTURE_MALFORMED_JSON,
    FIXTURE_MIXED_PROSE_AND_JSON,
    FIXTURE_NON_JSON_OBJECT,
    FIXTURE_PARTIAL_PROPOSAL,
    FIXTURE_SCHEMA_DRIFT,
    FIXTURE_VALID_BOUNDED_PROPOSAL,
    RAW_PROVIDER_RESPONSE_FIXTURES,
    RAW_VALID_BOUNDED_PROPOSAL,
    fixture_names,
)
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:55:00+00:00"


# --- fixtures: deterministic, replay-safe, append-only ----------------------


def test_fixture_set_is_deterministic_and_append_only() -> None:
    names_first = fixture_names()
    names_second = fixture_names()

    assert names_first == names_second
    assert names_first == tuple(sorted(names_first))
    assert set(names_first) == set(RAW_PROVIDER_RESPONSE_FIXTURES)
    # All required fixture cases are present
    required = {
        FIXTURE_VALID_BOUNDED_PROPOSAL,
        FIXTURE_MALFORMED_JSON,
        FIXTURE_MIXED_PROSE_AND_JSON,
        FIXTURE_SCHEMA_DRIFT,
        FIXTURE_PARTIAL_PROPOSAL,
        FIXTURE_INVALID_CAPABILITY_ESCALATION,
        FIXTURE_EMPTY_RESPONSE,
        FIXTURE_NON_JSON_OBJECT,
    }
    assert required.issubset(set(names_first))


def test_fixtures_carry_no_network_dependency_or_runtime_randomness() -> None:
    import aigol.runtime.raw_provider_response_fixtures as fixtures_module

    source = inspect.getsource(fixtures_module)
    forbidden_imports = (
        "import random",
        "import datetime",
        "import time",
        "import uuid",
        "import requests",
        "import urllib",
        "import subprocess",
        "os.system",
        "async ",
        "await ",
        "import threading",
        "import multiprocessing",
        "open(",
        "Path(",
    )
    for token in forbidden_imports:
        assert token not in source, f"fixture module must not reference {token!r}"
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()


# --- bounded extraction layer: deterministic discipline ---------------------


def _extract(fixture_name: str, *, extraction_id: str = "EXTRACTION-1", created_at: str = CREATED_AT):
    return extract_bounded_cognition_proposal(
        extraction_id=extraction_id,
        raw_response_text=RAW_PROVIDER_RESPONSE_FIXTURES[fixture_name],
        created_at=created_at,
    )


def test_valid_bounded_proposal_normalizes() -> None:
    result = _extract(FIXTURE_VALID_BOUNDED_PROPOSAL)
    evidence = result["extraction_evidence"]

    assert evidence.extraction_status == NORMALIZED
    assert evidence.extraction_stage == STAGE_BOUNDED_NORMALIZATION
    assert evidence.normalization_failure_type == NORMALIZATION_FAILURE_NONE
    assert evidence.schema_failure_type == SCHEMA_FAILURE_NONE
    assert evidence.bounded_schema_id == BOUNDED_SCHEMA_V1
    assert evidence.proposal_evidence_hash.startswith("sha256:")
    assert evidence.model_output_hash.startswith("sha256:")
    assert isinstance(result["model_output"], dict)
    assert result["model_output"]["proposal_type"] == "CONTRACT_PROPOSAL"


def test_malformed_json_is_rejected_with_invalid_json_failure() -> None:
    result = _extract(FIXTURE_MALFORMED_JSON)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_MALFORMED_JSON]

    assert evidence.extraction_status == REJECTED
    assert evidence.extraction_stage == expected["extraction_stage"]
    assert evidence.normalization_failure_type == expected["normalization_failure_type"]
    assert evidence.schema_failure_type == expected["schema_failure_type"]
    assert result["model_output"] is None


def test_mixed_prose_and_json_is_rejected_with_mixed_content_failure() -> None:
    result = _extract(FIXTURE_MIXED_PROSE_AND_JSON)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_MIXED_PROSE_AND_JSON]

    assert evidence.extraction_status == REJECTED
    assert evidence.normalization_failure_type == expected["normalization_failure_type"]
    assert evidence.schema_failure_type == expected["schema_failure_type"]
    assert result["model_output"] is None


def test_schema_drift_is_rejected_with_extra_fields_failure() -> None:
    result = _extract(FIXTURE_SCHEMA_DRIFT)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_SCHEMA_DRIFT]

    assert evidence.extraction_status == REJECTED
    assert evidence.normalization_failure_type == expected["normalization_failure_type"]
    assert evidence.schema_failure_type == expected["schema_failure_type"]
    assert result["model_output"] is None


def test_partial_proposal_is_rejected_with_missing_fields_failure() -> None:
    result = _extract(FIXTURE_PARTIAL_PROPOSAL)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_PARTIAL_PROPOSAL]

    assert evidence.extraction_status == REJECTED
    assert evidence.schema_failure_type == expected["schema_failure_type"]
    assert result["model_output"] is None


def test_invalid_capability_escalation_is_rejected_with_unauthorized_failure() -> None:
    result = _extract(FIXTURE_INVALID_CAPABILITY_ESCALATION)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_INVALID_CAPABILITY_ESCALATION]

    assert evidence.extraction_status == REJECTED
    assert evidence.schema_failure_type == expected["schema_failure_type"]
    assert result["model_output"] is None


def test_empty_response_is_rejected_with_empty_response_failure() -> None:
    result = _extract(FIXTURE_EMPTY_RESPONSE)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_EMPTY_RESPONSE]

    assert evidence.extraction_status == REJECTED
    assert evidence.normalization_failure_type == expected["normalization_failure_type"]
    assert evidence.raw_response_present is False


def test_non_json_object_is_rejected() -> None:
    result = _extract(FIXTURE_NON_JSON_OBJECT)
    evidence = result["extraction_evidence"]
    expected = EXPECTED_OUTCOMES[FIXTURE_NON_JSON_OBJECT]

    assert evidence.extraction_status == REJECTED
    assert evidence.normalization_failure_type == expected["normalization_failure_type"]


def test_extraction_hash_is_deterministic_across_runs() -> None:
    first = _extract(FIXTURE_VALID_BOUNDED_PROPOSAL)
    second = _extract(FIXTURE_VALID_BOUNDED_PROPOSAL)

    assert first["extraction_evidence"].evidence_hash == second["extraction_evidence"].evidence_hash
    assert first["extraction_evidence"].raw_response_hash == second["extraction_evidence"].raw_response_hash
    assert first["extraction_evidence"].proposal_evidence_hash == second["extraction_evidence"].proposal_evidence_hash


def test_raw_response_hash_matches_text_hash() -> None:
    result = _extract(FIXTURE_VALID_BOUNDED_PROPOSAL)

    assert result["extraction_evidence"].raw_response_hash == replay_hash(RAW_VALID_BOUNDED_PROPOSAL)


def test_extraction_evidence_round_trip() -> None:
    result = _extract(FIXTURE_VALID_BOUNDED_PROPOSAL)
    artifact = result["extraction_evidence"].to_dict()
    reconstructed = BoundedExtractionEvidence.from_dict(artifact).to_dict()
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")

    assert artifact == reconstructed
    assert evidence_hash == replay_hash(without_hash)


def test_extraction_lineage_is_append_only_and_deterministic() -> None:
    first = extract_bounded_cognition_proposal(
        extraction_id="EXTRACTION-A",
        raw_response_text=RAW_VALID_BOUNDED_PROPOSAL,
        created_at="2026-05-27T00:55:00+00:00",
    )
    second = extract_bounded_cognition_proposal(
        extraction_id="EXTRACTION-B",
        raw_response_text="not-json",
        created_at="2026-05-27T00:55:01+00:00",
    )
    lineage_a = reconstruct_bounded_extraction_lineage(
        [first["extraction_evidence"].to_dict(), second["extraction_evidence"].to_dict()]
    )
    lineage_b = reconstruct_bounded_extraction_lineage(
        [first["extraction_evidence"].to_dict(), second["extraction_evidence"].to_dict()]
    )

    assert lineage_a == lineage_b
    assert lineage_a["extraction_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["bounded_schema_id"] == BOUNDED_SCHEMA_V1


def test_extraction_layer_has_no_repair_or_retry_logic() -> None:
    import aigol.runtime.bounded_extraction_layer as extraction_module

    source = inspect.getsource(extraction_module)
    lower = source.lower()
    case_insensitive_forbidden = (
        "retry",
        "repair",
        "fallback",
        "fuzzy",
        "orchestrat",
        "autonomous",
    )
    for token in case_insensitive_forbidden:
        assert token not in lower, f"bounded extraction layer must not reference {token!r}"
    case_sensitive_forbidden = (
        "subprocess",
        "os.system",
        "requests",
        "urllib",
        "async ",
        "await ",
        "threading",
        "multiprocessing",
        "open(",
        "Path(",
    )
    for token in case_sensitive_forbidden:
        assert token not in source, f"bounded extraction layer must not reference {token!r}"


def test_extraction_layer_contains_no_provider_lock_in() -> None:
    import aigol.runtime.bounded_extraction_layer as extraction_module

    source = inspect.getsource(extraction_module)
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "claude" not in source.lower()
    assert "gpt" not in source.lower()


def test_fail_closed_input_validation() -> None:
    result = extract_bounded_cognition_proposal(
        extraction_id="",
        raw_response_text="anything",
        created_at=CREATED_AT,
    )
    assert result["extraction_evidence"].extraction_status == REJECTED
    assert result["model_output"] is None


def test_only_bounded_cognition_proposal_is_promoted_past_boundary() -> None:
    rejected_fixtures = [
        FIXTURE_MALFORMED_JSON,
        FIXTURE_MIXED_PROSE_AND_JSON,
        FIXTURE_SCHEMA_DRIFT,
        FIXTURE_PARTIAL_PROPOSAL,
        FIXTURE_INVALID_CAPABILITY_ESCALATION,
        FIXTURE_EMPTY_RESPONSE,
        FIXTURE_NON_JSON_OBJECT,
    ]
    for fixture_name in rejected_fixtures:
        result = _extract(fixture_name, extraction_id=f"EXTRACTION-{fixture_name}")
        assert result["model_output"] is None, f"{fixture_name} must not promote a model_output"


# --- end-to-end operator CLI success path ------------------------------------


def _install_openai_stub_with_text(monkeypatch, output_text: str) -> dict:
    captured: dict = {}

    class Responses:
        def create(self, *, model: str, input: str):
            captured["model"] = model
            captured["input"] = input
            return SimpleNamespace(output_text=output_text)

    class OpenAI:
        def __init__(self, *, api_key: str, timeout: int, max_retries: int) -> None:
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            captured["max_retries"] = max_retries
            self.responses = Responses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAI))
    monkeypatch.setenv(OPENAI_API_KEY_ENV, "test-openai-key")
    return captured


def test_operator_cli_success_path_with_valid_fixture(monkeypatch, capsys) -> None:
    _install_openai_stub_with_text(monkeypatch, RAW_VALID_BOUNDED_PROPOSAL)

    exit_code = main(
        [
            "inspect runtime status",
            "--operator-id",
            "operator-1",
            "--cli-id",
            "LPNS-CLI-1",
            "--created-at",
            CREATED_AT,
            "--timeout-seconds",
            "7",
        ]
    )
    rendered = capsys.readouterr().out

    assert exit_code == 0
    assert "status=SUCCESS" in rendered
    assert "return=operation=inspect_runtime" in rendered
    assert "cli_evidence_hash=sha256:" in rendered
    assert "operator_usage_evidence_hash=sha256:" in rendered
    assert "activation_evidence_hash=sha256:" in rendered


def test_operator_cli_success_preserves_governed_lineage(monkeypatch) -> None:
    _install_openai_stub_with_text(monkeypatch, RAW_VALID_BOUNDED_PROPOSAL)

    result = run_runtime_operator_cli(
        cli_invocation_id="LPNS-CLI-2",
        operator_id="operator-1",
        operator_prompt="inspect runtime status",
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    operator_usage = result["operator_usage"]
    activation = operator_usage["activation"]
    usage_record = activation["usage_validation"]["usage_records"][0]
    execution = usage_record["execution"]

    assert result["cli_evidence"].cli_status == CLI_SUCCESS
    assert result["exit_code"] == 0
    assert activation["activation_evidence"].activation_status == "ACTIVATED"
    assert usage_record["usage_status"] == "VALIDATED"
    assert execution["execution_result"].execution_status == "EXECUTED"
    assert execution["review"].review_status == "REVIEWED"
    assert execution["authorization"].status == "AUTHORIZED"
    assert execution["routing"].status == "ROUTED"
    assert usage_record["isolation"].isolation_status == "ISOLATED"
    assert usage_record["governed_return"].return_status == "ACCEPTED"


def test_rejection_analyzer_reports_no_rejection_on_success(monkeypatch) -> None:
    _install_openai_stub_with_text(monkeypatch, RAW_VALID_BOUNDED_PROPOSAL)
    usage = validate_live_runtime_usage(
        validation_id="LPNS-USAGE-SUCCESS",
        human_prompts=["inspect runtime status"],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    analysis = analyze_live_cognition_rejection(
        analysis_id="LPNS-ANALYSIS-SUCCESS",
        usage_record=usage["usage_records"][0],
        created_at=CREATED_AT,
    )
    evidence = analysis["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_NONE
    assert evidence.bounded_extraction_status == NORMALIZED
    assert evidence.bounded_extraction_stage == STAGE_BOUNDED_NORMALIZATION
    assert evidence.normalization_failure_type == NORMALIZATION_FAILURE_NONE
    assert evidence.schema_failure_type == SCHEMA_FAILURE_NONE
    assert evidence.bounded_extraction_evidence_hash.startswith("sha256:")
    assert evidence.normalized_proposal_present is True


def test_rejection_analyzer_classifies_extraction_failure_for_malformed_json(monkeypatch) -> None:
    _install_openai_stub_with_text(monkeypatch, "not-json")
    usage = validate_live_runtime_usage(
        validation_id="LPNS-USAGE-MALFORMED",
        human_prompts=["inspect runtime status"],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    analysis = analyze_live_cognition_rejection(
        analysis_id="LPNS-ANALYSIS-MALFORMED",
        usage_record=usage["usage_records"][0],
        created_at=CREATED_AT,
    )
    evidence = analysis["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_BOUNDED_EXTRACTION
    assert evidence.bounded_extraction_status == REJECTED
    assert evidence.normalization_failure_type == "MIXED_CONTENT"
    assert evidence.schema_failure_type == SCHEMA_FAILURE_NONE


def test_rejection_analyzer_classifies_schema_failure_for_capability_escalation(monkeypatch) -> None:
    _install_openai_stub_with_text(
        monkeypatch,
        RAW_PROVIDER_RESPONSE_FIXTURES[FIXTURE_INVALID_CAPABILITY_ESCALATION],
    )
    usage = validate_live_runtime_usage(
        validation_id="LPNS-USAGE-ESCALATION",
        human_prompts=["inspect runtime status"],
        created_at=CREATED_AT,
        timeout_seconds=7,
    )
    analysis = analyze_live_cognition_rejection(
        analysis_id="LPNS-ANALYSIS-ESCALATION",
        usage_record=usage["usage_records"][0],
        created_at=CREATED_AT,
    )
    evidence = analysis["analysis_evidence"]

    assert evidence.rejection_stage == STAGE_BOUNDED_EXTRACTION
    assert evidence.bounded_extraction_status == REJECTED
    assert evidence.normalization_failure_type == NORMALIZATION_FAILURE_NONE
    assert evidence.schema_failure_type == "UNAUTHORIZED_CAPABILITY"


# --- discipline / no provider lock-in in AiGOL core --------------------------


def test_aigol_core_has_no_provider_lock_in() -> None:
    import aigol.runtime.bounded_extraction_layer as extraction_module
    import aigol.runtime.raw_provider_response_capture as capture_module
    import aigol.runtime.raw_provider_response_fixtures as fixtures_module

    for module in (extraction_module, capture_module, fixtures_module):
        source = inspect.getsource(module).lower()
        for forbidden in ("openai", "anthropic", "claude", "gpt"):
            assert forbidden not in source, (
                f"AiGOL core module {module.__name__} must not reference provider {forbidden!r}"
            )


def test_no_orchestration_or_runtime_mutation_introduced() -> None:
    new_modules = [
        "aigol.runtime.bounded_extraction_layer",
        "aigol.runtime.raw_provider_response_fixtures",
    ]
    for module_name in new_modules:
        module = __import__(module_name, fromlist=["__name__"])
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
        assert "open(" not in source
        assert "Path(" not in source
