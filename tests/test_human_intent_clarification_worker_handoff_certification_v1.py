"""Tests for AIGOL_HUMAN_INTENT_CLARIFICATION_WORKER_HANDOFF_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_clarification_worker_handoff_certification_v1 import (
    MILESTONE_ID,
    run_human_intent_clarification_worker_handoff_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_worker_handoff_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_clarification_worker_handoff_certification(
        replay_base=tmp_path / "worker_handoff"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "HUMAN_INTENT_WORKER_HANDOFF_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "evidence_package" / "000_human_intent_worker_handoff_evidence_package.json").exists()
    assert (root / "replay_package" / "000_human_intent_worker_handoff_replay_package.json").exists()
    assert (root / "certification_report" / "000_human_intent_worker_handoff_certification_report.json").exists()


def test_worker_handoff_certification_report_assertions(tmp_path):
    result = run_human_intent_clarification_worker_handoff_certification(
        replay_base=tmp_path / "worker_handoff"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_worker_handoff_certification_report.json"
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
    assert observed["worker_handoff_contains_resolved_intent"] is True
    assert observed["worker_handoff_contains_authorization_reference"] is True
    assert observed["worker_handoff_contains_replay_reference"] is True
    assert observed["worker_not_invoked_automatically"] is True
    assert observed["authority_boundary_preserved"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["secret_free_evidence"] is True


def test_worker_handoff_package_contains_required_fields_and_does_not_invoke_worker(tmp_path):
    result = run_human_intent_clarification_worker_handoff_certification(
        replay_base=tmp_path / "worker_handoff"
    )
    package_wrapper = load_json(
        Path(result["cert_root"])
        / "scenario"
        / "worker_handoff_boundary"
        / "004_worker_handoff_package_recorded.json"
    )
    package = package_wrapper["artifact"]

    assert package["handoff_package_generated"] is True
    assert package["resolved_intent"]
    assert package["execution_authorization_reference"]
    assert package["worker_authorization_reference"]
    assert package["continuity_replay_reference"]
    assert package["worker_invoked"] is False
    assert package["execution_started"] is False


def test_worker_handoff_certification_replay_is_secret_free(tmp_path):
    result = run_human_intent_clarification_worker_handoff_certification(
        replay_base=tmp_path / "worker_handoff"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
