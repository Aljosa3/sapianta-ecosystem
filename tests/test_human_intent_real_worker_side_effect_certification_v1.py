"""Tests for AIGOL_HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.human_intent_real_worker_side_effect_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    MILESTONE_ID,
    run_human_intent_real_worker_side_effect_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_real_worker_side_effect_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert all(result["assertions"].values())
    assert len(result["scenario_results"]) == 8

    root = Path(result["cert_root"])
    assert (
        root
        / "evidence_package"
        / "000_human_intent_real_worker_side_effect_evidence_package.json"
    ).exists()
    assert (
        root
        / "replay_package"
        / "000_human_intent_real_worker_side_effect_replay_package.json"
    ).exists()
    assert (
        root
        / "certification_report"
        / "000_human_intent_real_worker_side_effect_certification_report.json"
    ).exists()


def test_positive_side_effect_workers_create_update_and_generate_artifacts(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )
    sandbox = Path(result["sandbox_root"])

    created = sandbox / "RWS-001" / "created" / "proof_note.txt"
    updated = sandbox / "RWS-002" / "updated" / "status_note.txt"
    generated = sandbox / "RWS-003" / "artifacts" / "generated_proof_artifact.json"

    assert created.read_text(encoding="utf-8") == "AIGOL_REAL_WORKER_SIDE_EFFECT_FILE_CREATED\n"
    assert updated.read_text(encoding="utf-8") == "status=pending\nstatus=certified\n"
    generated_artifact = load_json(generated)
    assert generated_artifact["artifact_type"] == "REAL_WORKER_SIDE_EFFECT_GENERATED_ARTIFACT_V1"
    assert generated_artifact["worker_type"] == "ARTIFACT_GENERATION_WORKER"


def test_rejection_scenarios_block_unauthorized_side_effects(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )
    sandbox = Path(result["sandbox_root"])

    blocked_paths = (
        sandbox / "RWS-004" / "rejected" / "missing_approval.txt",
        sandbox / "RWS-005" / "rejected" / "missing_authorization.txt",
        sandbox / "RWS-006" / "rejected" / "modified_authorization.txt",
        sandbox / "RWS-007" / "rejected" / "replay_mismatch.txt",
    )
    for path in blocked_paths:
        assert not path.exists()

    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_real_worker_side_effect_certification_report.json"
    )
    failures = {item["scenario_id"]: item["failure_reason"] for item in report["scenario_results"]}
    assert failures["RWS-004"] == "MISSING_HUMAN_APPROVAL"
    assert failures["RWS-005"] == "MISSING_EXECUTION_AUTHORIZATION"
    assert failures["RWS-006"] == "MODIFIED_AUTHORIZATION_DETECTED"
    assert failures["RWS-007"] == "REPLAY_MISMATCH_DETECTED"


def test_verification_failure_is_detected_after_real_side_effect(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )
    sandbox = Path(result["sandbox_root"])
    failed_verification_file = sandbox / "RWS-008" / "failed_verification" / "wrong_content.txt"

    assert failed_verification_file.exists()
    assert failed_verification_file.read_text(encoding="utf-8") == "actual-side-effect-content\n"

    verification = load_json(
        Path(result["cert_root"])
        / "scenarios"
        / "RWS-008"
        / "replay"
        / "007_side_effect_verification_recorded.json"
    )["artifact"]
    assert verification["verification_passed"] is False
    assert verification["failure_reason"] == "SIDE_EFFECT_VERIFICATION_FAILED"


def test_real_worker_side_effect_certification_report_assertions(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_human_intent_real_worker_side_effect_certification_report.json"
    )
    observed = report["observed"]

    assert observed["intent_detection"] is True
    assert observed["clarification_if_required"] is True
    assert observed["workflow_selection"] is True
    assert observed["execution_summary_generation"] is True
    assert observed["human_approval_requirement"] is True
    assert observed["authorization_issuance"] is True
    assert observed["worker_handoff_generation"] is True
    assert observed["side_effect_execution"] is True
    assert observed["side_effect_verification"] is True
    assert observed["replay_reconstruction"] is True
    assert observed["authority_boundary_preservation"] is True
    assert observed["secret_free_evidence"] is True


def test_real_worker_side_effect_replay_is_secret_free(tmp_path):
    result = run_human_intent_real_worker_side_effect_certification(
        replay_base=tmp_path / "real_worker_side_effect"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
