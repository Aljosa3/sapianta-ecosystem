"""Tests for AIGOL_HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_end_to_end_real_user_worker_execution_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    MILESTONE_ID,
    run_human_intent_end_to_end_real_user_worker_execution_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_end_to_end_worker_execution_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_end_to_end_real_user_worker_execution_certification(
        replay_base=tmp_path / "end_to_end_worker_execution"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert all(result["assertions"].values())
    assert len(result["scenario_results"]) == 8

    root = Path(result["cert_root"])
    assert (
        root
        / "evidence_package"
        / "000_human_intent_end_to_end_worker_execution_evidence_package.json"
    ).exists()
    assert (
        root
        / "replay_package"
        / "000_human_intent_end_to_end_worker_execution_replay_package.json"
    ).exists()
    assert (
        root
        / "certification_report"
        / "000_human_intent_end_to_end_worker_execution_certification_report.json"
    ).exists()


def test_end_to_end_worker_execution_certification_report_assertions(tmp_path):
    result = run_human_intent_end_to_end_real_user_worker_execution_certification(
        replay_base=tmp_path / "end_to_end_worker_execution"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_end_to_end_worker_execution_certification_report.json"
    )
    observed = report["observed"]

    assert observed["intent_detected"] is True
    assert observed["clarification_generated"] is True
    assert observed["clarification_accepted"] is True
    assert observed["context_updated"] is True
    assert observed["workflow_selected"] is True
    assert observed["execution_summary_generated"] is True
    assert observed["human_approval_required"] is True
    assert observed["authorization_issued"] is True
    assert observed["worker_handoff_generated"] is True
    assert observed["worker_executed"] is True
    assert observed["execution_outcome_recorded"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["authority_boundary_preserved"] is True
    assert observed["secret_free_evidence"] is True


def test_rejection_scenario_blocks_authorization_and_worker_invocation(tmp_path):
    result = run_human_intent_end_to_end_real_user_worker_execution_certification(
        replay_base=tmp_path / "end_to_end_worker_execution"
    )
    root = Path(result["cert_root"])
    authorization = load_json(
        root
        / "scenarios"
        / "E2E-007"
        / "end_to_end_boundary"
        / "009_execution_authorization_recorded.json"
    )["artifact"]
    invocation = load_json(
        root
        / "scenarios"
        / "E2E-007"
        / "end_to_end_boundary"
        / "011_worker_invocation_recorded.json"
    )["artifact"]
    outcome = load_json(
        root
        / "scenarios"
        / "E2E-007"
        / "end_to_end_boundary"
        / "012_execution_outcome_recorded.json"
    )["artifact"]

    assert authorization["authorization_issued"] is False
    assert authorization["authorization_status"] == "BLOCKED_BY_HUMAN_REJECTION"
    assert invocation["worker_executed"] is False
    assert outcome["execution_outcome_status"] == "EXECUTION_BLOCKED_BY_HUMAN_REJECTION"


def test_modification_before_approval_is_replay_visible_and_still_authorized(tmp_path):
    result = run_human_intent_end_to_end_real_user_worker_execution_certification(
        replay_base=tmp_path / "end_to_end_worker_execution"
    )
    root = Path(result["cert_root"])
    context = load_json(
        root
        / "scenarios"
        / "E2E-008"
        / "end_to_end_boundary"
        / "004_ocs_context_update_recorded.json"
    )["artifact"]
    approval = load_json(
        root
        / "scenarios"
        / "E2E-008"
        / "end_to_end_boundary"
        / "008_human_approval_recorded.json"
    )["artifact"]
    invocation = load_json(
        root
        / "scenarios"
        / "E2E-008"
        / "end_to_end_boundary"
        / "011_worker_invocation_recorded.json"
    )["artifact"]

    assert context["modification_before_approval"] == "one_page_customer_facing_only"
    assert approval["approval_decision"] == "APPROVE_MODIFIED"
    assert approval["approved_for_execution"] is True
    assert invocation["worker_executed"] is True


def test_end_to_end_worker_execution_replay_is_secret_free(tmp_path):
    result = run_human_intent_end_to_end_real_user_worker_execution_certification(
        replay_base=tmp_path / "end_to_end_worker_execution"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
