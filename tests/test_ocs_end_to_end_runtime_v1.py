"""Tests for AIGOL_OCS_END_TO_END_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_end_to_end_runtime import (
    OCS_END_TO_END_ARTIFACT_V1,
    OCS_END_TO_END_COMPLETED,
    reconstruct_ocs_end_to_end_replay,
    run_ocs_end_to_end,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T15:00:00+00:00"


def _artifact(artifact_type: str, artifact_id: str, **extra: object) -> dict:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "replay_visible": True,
        "authority": False,
        **extra,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _source_context(*, ambiguous: bool = False) -> dict:
    registry = [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-TRADING", domain_id="TRADING")]
    if ambiguous:
        registry.append(_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-HEALTHCARE", domain_id="HEALTHCARE"))
    return {
        "conversation_context": [_artifact("CONVERSATION_RESPONSE_ARTIFACT_V1", "CONVERSATION-000001")],
        "clarification_context": [],
        "ppp_context": [
            _artifact(
                "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                "PPP-TRADING-MARKET_EVIDENCE_NORMALIZATION-000001",
                ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
                provider_necessity_classification="PROVIDER_REQUIRED",
            )
        ],
        "approval_context": [],
        "replay_visible_operation_context": [
            _artifact("UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1", "REPLAY-000001", status="READY")
        ],
        "domain_context": [_artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", "TRADING-DOMAIN", domain_id="TRADING")],
        "registry_context": registry,
    }


def _failure_history() -> list[dict]:
    return [
        _artifact("FAILURE_ARTIFACT_V1", "FAIL-1", failure_reason="missing replay artifact"),
        _artifact("FAILURE_ARTIFACT_V1", "FAIL-2", failure_reason="missing replay artifact"),
    ]


def _validation_history() -> list[dict]:
    return [
        _artifact("VALIDATION_ARTIFACT_V1", "VAL-1", validation_status="FAILED", error_code="MISSING_HASH"),
        _artifact("VALIDATION_ARTIFACT_V1", "VAL-2", validation_status="FAILED", error_code="MISSING_HASH"),
    ]


def test_ocs_end_to_end_runs_complete_chain_and_reconstructs(tmp_path) -> None:
    capture = run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "e2e",
        source_context=_source_context(ambiguous=True),
        source_chain_id="CHAIN-E2E-000001",
        source_request_reference="PROMPT-E2E-000001",
        failure_history=_failure_history(),
        validation_history=_validation_history(),
    )
    reconstructed = reconstruct_ocs_end_to_end_replay(tmp_path / "e2e")
    artifact = capture["ocs_end_to_end_artifact"]

    assert artifact["artifact_type"] == OCS_END_TO_END_ARTIFACT_V1
    assert capture["end_to_end_status"] == OCS_END_TO_END_COMPLETED
    assert len(capture["stage_references"]) == 9
    assert [stage["stage_name"] for stage in capture["stage_references"]] == [
        "CONTEXT_ASSEMBLY",
        "COGNITION",
        "REPLAY_DERIVED_INTENT",
        "MEMORY",
        "CONTINUITY",
        "SEMANTIC_RESOLUTION",
        "CLARIFICATION",
        "OCS_TO_PPP_BINDING",
        "CHAIN_INSPECTION",
    ]
    assert artifact["clarification_summary"]["clarification_required"] is True
    assert artifact["operator_summary"]["end_to_end_stage_count"] == 9
    assert artifact["operator_summary"]["ppp_handoff_candidate_count"] >= 1
    assert capture["ppp_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["approval_created"] is False
    assert reconstructed["end_to_end_hash"] == capture["end_to_end_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_end_to_end_is_deterministic_for_identical_inputs(tmp_path) -> None:
    source = _source_context(ambiguous=True)
    failures = _failure_history()
    validations = _validation_history()
    first = run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-DETERMINISTIC-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
        source_context=source,
        source_chain_id="CHAIN-E2E-000001",
        source_request_reference="PROMPT-E2E-000001",
        failure_history=failures,
        validation_history=validations,
    )
    second = run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-DETERMINISTIC-000002",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
        source_context=source,
        source_chain_id="CHAIN-E2E-000001",
        source_request_reference="PROMPT-E2E-000001",
        failure_history=failures,
        validation_history=validations,
    )

    assert first["end_to_end_hash"] == second["end_to_end_hash"]
    assert reconstruct_ocs_end_to_end_replay(tmp_path / "first")["end_to_end_hash"] == first["end_to_end_hash"]
    assert reconstruct_ocs_end_to_end_replay(tmp_path / "second")["end_to_end_hash"] == second["end_to_end_hash"]


def test_ocs_end_to_end_records_not_required_clarification_for_clear_inputs(tmp_path) -> None:
    capture = run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-CLEAR-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clear",
        source_context=_source_context(ambiguous=False),
        failure_history=_failure_history(),
        validation_history=_validation_history(),
    )

    assert capture["end_to_end_status"] == OCS_END_TO_END_COMPLETED
    assert capture["clarification_summary"]["clarification_required"] is False


def test_ocs_end_to_end_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    source = _source_context(ambiguous=False)
    source["conversation_context"][0]["execution_requested"] = True
    source["conversation_context"][0]["artifact_hash"] = replay_hash(
        {key: value for key, value in source["conversation_context"][0].items() if key != "artifact_hash"}
    )

    capture = run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-AUTHORITY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
        source_context=source,
    )

    assert capture["fail_closed"] is True
    assert capture["end_to_end_status"] == "FAILED_CLOSED"
    assert "prohibited OCS authority flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_end_to_end_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_ocs_end_to_end(
        ocs_run_id="OCS-E2E-CORRUPT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        source_context=_source_context(ambiguous=True),
        failure_history=_failure_history(),
        validation_history=_validation_history(),
    )
    path = tmp_path / "corrupt" / "000_ocs_end_to_end_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["end_to_end_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_end_to_end_replay(tmp_path / "corrupt")


def test_ocs_end_to_end_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_end_to_end_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
