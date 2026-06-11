"""Tests for AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.gap_to_improvement_intent_e2e_runtime import (
    GAP_TO_IMPROVEMENT_INTENT_E2E_ARTIFACT_V1,
    GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED,
    HUMAN_REVIEW_GATE_ARTIFACT_V1,
    PENDING_HUMAN_REVIEW,
    reconstruct_gap_to_improvement_intent_e2e,
    run_gap_to_improvement_intent_e2e,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-GAP-INTENT-E2E-000001"


def _execution_replay(status: str = "FAILED", *, chain_id: str = CHAIN_ID) -> dict:
    payload = {
        "execution_id": "EXECUTION-REPLAY-000001",
        "execution_status": "TERMINATED",
        "result_validation_status": status,
        "repair_started": False,
        "worker_execution_requested_by_e2e": False,
        "provider_change_requested": False,
    }
    return {
        "evidence_id": "EXECUTION-VALIDATION-REPLAY-000001",
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": "replay/execution-validation-000001.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": chain_id,
        "observed_condition": "Execution replay records failed validation.",
        "expected_condition": "Execution replay should record validated result.",
        "confidence": "DETERMINISTIC",
        "status": status,
    }


def test_gap_to_improvement_intent_e2e_reaches_human_review_without_repair_or_execution(tmp_path) -> None:
    capture = run_gap_to_improvement_intent_e2e(
        run_id="GAP-INTENT-E2E-000001",
        execution_replay_artifacts=[_execution_replay()],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap_intent_e2e",
        domain_id="AIGOL_CORE",
        affected_layer="GOVERNANCE",
        affected_worker_family="REGRESSION_GAP_ANALYSIS",
    )
    e2e = capture["gap_to_improvement_intent_e2e_artifact"]
    intent = capture["improvement_intent_capture"]["improvement_intent_artifact"]
    human_gate = capture["human_review_gate_artifact"]
    reconstructed = reconstruct_gap_to_improvement_intent_e2e(tmp_path / "gap_intent_e2e")

    assert e2e["artifact_type"] == GAP_TO_IMPROVEMENT_INTENT_E2E_ARTIFACT_V1
    assert e2e["e2e_status"] == GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED
    assert e2e["improvement_intent_artifact_generated"] is True
    assert e2e["replay_lineage_preserved"] is True
    assert e2e["human_approval_required"] is True
    assert e2e["self_modification_prevented"] is True
    assert e2e["repair_prevented"] is True
    assert e2e["ready_for_ppp_integration"] is True

    assert intent["intent_status"] == "IMPROVEMENT_INTENT_CREATED"
    assert intent["proposal_created"] is False
    assert intent["ppp_invoked"] is False
    assert intent["provider_invoked"] is False
    assert intent["worker_invoked"] is False
    assert intent["execution_requested"] is False
    assert intent["self_modification_authority"] is False

    assert human_gate["artifact_type"] == HUMAN_REVIEW_GATE_ARTIFACT_V1
    assert human_gate["review_status"] == PENDING_HUMAN_REVIEW
    assert human_gate["approval_required"] is True
    assert human_gate["approval_granted"] is False
    assert human_gate["repair_invoked"] is False
    assert human_gate["self_modification_performed"] is False
    assert human_gate["allowed_next_step"] == "HUMAN_REVIEW"

    assert reconstructed["e2e_status"] == GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED
    assert reconstructed["improvement_intent_artifact_generated"] is True
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["ready_for_ppp_integration"] is True


def test_chain_mismatch_fails_closed_before_gap_detection(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain continuity failed"):
        run_gap_to_improvement_intent_e2e(
            run_id="GAP-INTENT-E2E-CHAIN-MISMATCH",
            execution_replay_artifacts=[_execution_replay(chain_id="OTHER-CHAIN")],
            canonical_chain_id=CHAIN_ID,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "gap_intent_e2e_chain",
        )


def test_reconstruction_detects_e2e_replay_corruption(tmp_path) -> None:
    run_gap_to_improvement_intent_e2e(
        run_id="GAP-INTENT-E2E-CORRUPT",
        execution_replay_artifacts=[_execution_replay()],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap_intent_e2e_corrupt",
    )
    path = tmp_path / "gap_intent_e2e_corrupt" / "001_human_review_gate.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_granted"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_gap_to_improvement_intent_e2e(tmp_path / "gap_intent_e2e_corrupt")


def test_gap_to_improvement_intent_e2e_runtime_has_no_repair_ppp_provider_worker_or_execution_calls() -> None:
    import aigol.runtime.gap_to_improvement_intent_e2e_runtime as runtime

    source = inspect.getsource(runtime)

    assert "repair_and_retry" not in source
    assert "run_conversation_ppp" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "subprocess" not in source
    assert "os.system" not in source
