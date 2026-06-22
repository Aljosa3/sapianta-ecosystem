"""Tests for human-intent clarification execution authorization boundary certification."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_clarification_execution_authorization_boundary_certification_v1 import (
    MILESTONE_ID,
    run_human_intent_clarification_execution_authorization_boundary_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_execution_authorization_boundary_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_clarification_execution_authorization_boundary_certification(
        replay_base=tmp_path / "auth_boundary"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (
        root
        / "evidence_package"
        / "000_human_intent_execution_authorization_boundary_evidence_package.json"
    ).exists()
    assert (
        root
        / "replay_package"
        / "000_human_intent_execution_authorization_boundary_replay_package.json"
    ).exists()
    assert (
        root
        / "certification_report"
        / "000_human_intent_execution_authorization_boundary_certification_report.json"
    ).exists()


def test_execution_authorization_boundary_report_assertions(tmp_path):
    result = run_human_intent_clarification_execution_authorization_boundary_certification(
        replay_base=tmp_path / "auth_boundary"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_execution_authorization_boundary_certification_report.json"
    )
    observed = report["observed"]

    assert observed["ambiguous_intent_detected"] is True
    assert observed["clarification_generated"] is True
    assert observed["clarification_response_received"] is True
    assert observed["context_updated"] is True
    assert observed["intent_resolved"] is True
    assert observed["workflow_selected"] is True
    assert observed["execution_summary_generated"] is True
    assert observed["approval_requested"] is True
    assert observed["approval_denied_path_verified"] is True
    assert observed["execution_blocked_without_approval"] is True
    assert observed["approval_granted_path_verified"] is True
    assert observed["execution_authorized_after_approval"] is True
    assert observed["authority_boundary_preserved"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["secret_free_evidence"] is True


def test_execution_authorization_boundary_denied_and_granted_paths(tmp_path):
    result = run_human_intent_clarification_execution_authorization_boundary_certification(
        replay_base=tmp_path / "auth_boundary"
    )
    evidence = load_json(
        Path(result["cert_root"])
        / "evidence_package"
        / "000_human_intent_execution_authorization_boundary_evidence_package.json"
    )
    denied = evidence["approval_denied_scenario"]
    granted = evidence["approval_granted_scenario"]

    assert denied["execution_authorized"] is False
    assert denied["worker_authorization_issued"] is False
    assert denied["worker_invoked"] is False
    assert granted["execution_authorized"] is True
    assert granted["worker_authorization_issued"] is True
    assert granted["worker_invoked"] is False


def test_execution_authorization_boundary_replay_is_secret_free(tmp_path):
    result = run_human_intent_clarification_execution_authorization_boundary_certification(
        replay_base=tmp_path / "auth_boundary"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
