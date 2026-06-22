"""Tests for AIGOL_HUMAN_INTENT_CLARIFICATION_WORKER_INVOCATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_clarification_worker_invocation_certification_v1 import (
    MILESTONE_ID,
    run_human_intent_clarification_worker_invocation_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_worker_invocation_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_clarification_worker_invocation_certification(
        replay_base=tmp_path / "worker_invocation"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "HUMAN_INTENT_WORKER_INVOCATION_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "evidence_package" / "000_human_intent_worker_invocation_evidence_package.json").exists()
    assert (root / "replay_package" / "000_human_intent_worker_invocation_replay_package.json").exists()
    assert (root / "certification_report" / "000_human_intent_worker_invocation_certification_report.json").exists()


def test_worker_invocation_certification_report_assertions(tmp_path):
    result = run_human_intent_clarification_worker_invocation_certification(
        replay_base=tmp_path / "worker_invocation"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_worker_invocation_certification_report.json"
    )
    observed = report["observed"]

    assert observed["ambiguous_intent_detected"] is True
    assert observed["clarification_generated"] is True
    assert observed["clarification_response_received"] is True
    assert observed["context_updated"] is True
    assert observed["intent_resolved"] is True
    assert observed["workflow_selected"] is True
    assert observed["execution_summary_generated"] is True
    assert observed["human_confirmation_recorded"] is True
    assert observed["worker_authorization_issued"] is True
    assert observed["worker_handoff_package_generated"] is True
    assert observed["worker_invoked"] is True
    assert observed["execution_outcome_recorded"] is True
    assert observed["replay_contains_invocation"] is True
    assert observed["replay_contains_outcome"] is True
    assert observed["authority_boundary_preserved"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["secret_free_evidence"] is True


def test_worker_invocation_boundary_contains_handoff_invocation_and_outcome(tmp_path):
    result = run_human_intent_clarification_worker_invocation_certification(
        replay_base=tmp_path / "worker_invocation"
    )
    package_wrapper = load_json(
        Path(result["cert_root"])
        / "scenario"
        / "worker_invocation_boundary"
        / "004_worker_handoff_package_recorded.json"
    )
    invocation_wrapper = load_json(
        Path(result["cert_root"])
        / "scenario"
        / "worker_invocation_boundary"
        / "005_worker_invocation_recorded.json"
    )
    outcome_wrapper = load_json(
        Path(result["cert_root"])
        / "scenario"
        / "worker_invocation_boundary"
        / "006_execution_outcome_recorded.json"
    )
    package = package_wrapper["artifact"]
    invocation = invocation_wrapper["artifact"]
    outcome = outcome_wrapper["artifact"]

    assert package["handoff_package_generated"] is True
    assert package["resolved_intent"]
    assert package["execution_authorization_reference"]
    assert package["worker_authorization_reference"]
    assert package["continuity_replay_reference"]
    assert package["worker_invoked"] is False
    assert package["execution_started"] is False
    assert invocation["worker_invoked"] is True
    assert invocation["handoff_package_reference"] == package["handoff_package_id"]
    assert invocation["worker_authorization_reference"] == package["worker_authorization_reference"]
    assert outcome["execution_outcome_recorded"] is True
    assert outcome["worker_invocation_reference"] == invocation["worker_invocation_id"]
    assert outcome["execution_outcome_status"] == "WORKER_EXECUTION_COMPLETED"


def test_worker_invocation_certification_replay_is_secret_free(tmp_path):
    result = run_human_intent_clarification_worker_invocation_certification(
        replay_base=tmp_path / "worker_invocation"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
