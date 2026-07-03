"""Tests for G13_08 live conversational clarification runtime certification."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.g13_08_live_conversational_clarification_runtime_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    MILESTONE_ID,
    run_g13_08_live_conversational_clarification_runtime_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_live_conversational_clarification_certifies_complete_runtime(tmp_path):
    result = run_g13_08_live_conversational_clarification_runtime_certification(
        replay_base=tmp_path / "g13_08"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert all(result["assertions"].values())


def test_live_conversational_clarification_preserves_same_session_and_worker_execution(tmp_path):
    result = run_g13_08_live_conversational_clarification_runtime_certification(
        replay_base=tmp_path / "g13_08"
    )
    transcript = load_json(Path(result["conversation_transcript_path"]))
    governance = load_json(Path(result["governance_evidence_path"]))
    worker = load_json(Path(result["worker_evidence_path"]))

    assert transcript["session_restart_required"] is False
    assert {turn["turn_id"] for turn in transcript["turns"]} == {"TURN-000001", "TURN-000002"}
    assert governance["authorization_state"] == "AUTHORIZED_AFTER_HUMAN_CLARIFICATION"
    assert governance["provider_identity_merged_with_worker"] is False
    assert worker["worker_invoked"] is True
    assert worker["execution_outcome_status"] == "WORKER_EXECUTION_COMPLETED"


def test_live_conversational_clarification_records_replay_visible_evidence(tmp_path):
    result = run_g13_08_live_conversational_clarification_runtime_certification(
        replay_base=tmp_path / "g13_08"
    )
    replay = load_json(Path(result["replay_evidence_path"]))
    clarification = load_json(Path(result["clarification_artifact_path"]))

    assert replay["complete_clarification_cycle_replay_visible"] is True
    assert replay["recorded_file_count"] > 0
    assert clarification["clarification_required"] is True
    assert {item["trigger"] for item in clarification["clarification_candidates"]} >= {
        "DISAGREEMENT_THRESHOLD_EXCEEDED",
        "UNCERTAINTY_THRESHOLD_EXCEEDED",
    }


def test_live_conversational_clarification_evidence_is_secret_free(tmp_path):
    result = run_g13_08_live_conversational_clarification_runtime_certification(
        replay_base=tmp_path / "g13_08"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "bearer " not in serialized.lower()
    assert "api_key" not in serialized.lower()
