"""Tests for AIGOL_HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_clarification_live_acli_session_certification_v1 import (
    MILESTONE_ID,
    run_human_intent_clarification_live_acli_session_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_live_acli_session_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_clarification_live_acli_session_certification(
        replay_base=tmp_path / "hic_live"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    evidence_path = (
        root
        / "evidence_package"
        / "000_human_intent_clarification_live_acli_session_evidence_package.json"
    )
    coverage_path = (
        root
        / "evidence_package"
        / "001_human_intent_clarification_live_acli_session_coverage_report.json"
    )
    replay_path = (
        root
        / "replay_package"
        / "000_human_intent_clarification_live_acli_session_replay_package.json"
    )
    report_path = (
        root
        / "certification_report"
        / "000_human_intent_clarification_live_acli_session_certification_report.json"
    )

    assert evidence_path.exists()
    assert coverage_path.exists()
    assert replay_path.exists()
    assert report_path.exists()


def test_live_acli_session_certification_report_assertions(tmp_path):
    result = run_human_intent_clarification_live_acli_session_certification(
        replay_base=tmp_path / "hic_live"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_clarification_live_acli_session_certification_report.json"
    )
    observed = report["observed"]

    assert observed["acli_session_started"] is True
    assert observed["ambiguous_intent_detected"] is True
    assert observed["clarification_generated"] is True
    assert observed["clarification_response_received"] is True
    assert observed["context_updated"] is True
    assert observed["intent_resolved"] is True
    assert observed["workflow_selected"] is True
    assert observed["execution_summary_generated"] is True
    assert observed["human_confirmation_recorded"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["approval_boundaries_preserved"] is True
    assert observed["secret_free_evidence"] is True


def test_live_acli_session_certification_replay_is_secret_free(tmp_path):
    result = run_human_intent_clarification_live_acli_session_certification(
        replay_base=tmp_path / "hic_live"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
