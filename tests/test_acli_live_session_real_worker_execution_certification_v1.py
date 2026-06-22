"""Tests for AIGOL_ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.acli_live_session_real_worker_execution_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    MILESTONE_ID,
    run_acli_live_session_real_worker_execution_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_acli_live_session_real_worker_execution_produces_required_artifacts(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert all(result["assertions"].values())
    assert len(result["scenario_results"]) == 10

    root = Path(result["cert_root"])
    assert (
        root
        / "evidence_package"
        / "000_acli_live_session_real_worker_execution_evidence_package.json"
    ).exists()
    assert (
        root
        / "replay_package"
        / "000_acli_live_session_real_worker_execution_replay_package.json"
    ).exists()
    assert (
        root
        / "certification_report"
        / "000_acli_live_session_real_worker_execution_certification_report.json"
    ).exists()


def test_positive_live_session_workers_create_update_and_generate_artifacts(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )
    sandbox = Path(result["sandbox_root"])

    created = sandbox / "ALS-001" / "created" / "live_session_proof.txt"
    updated = sandbox / "ALS-002" / "updated" / "live_status.txt"
    generated = sandbox / "ALS-003" / "artifacts" / "operator_safe_proof.json"

    assert created.read_text(encoding="utf-8") == "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFIED\n"
    assert updated.read_text(encoding="utf-8") == (
        "live_session_worker_path=pending\nlive_session_worker_path=certified\n"
    )
    generated_artifact = load_json(generated)
    assert generated_artifact["artifact_type"] == "ACLI_LIVE_SESSION_GENERATED_SIDE_EFFECT_ARTIFACT_V1"
    assert generated_artifact["correction_before_approval"] == "detailed_to_short_operator_safe"


def test_rejection_and_fail_closed_cases_block_unauthorized_side_effects(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )
    sandbox = Path(result["sandbox_root"])

    blocked_paths = (
        sandbox / "ALS-004" / "blocked" / "human_rejection.txt",
        sandbox / "ALS-005" / "blocked" / "no_approval.txt",
        sandbox / "ALS-006" / "blocked" / "no_authorization.txt",
        sandbox / "ALS-007" / "blocked" / "modified_handoff.txt",
        sandbox / "ALS-009" / "blocked" / "replay_mismatch.txt",
    )
    for path in blocked_paths:
        assert not path.exists()

    outside = sandbox / "outside_sandbox.txt"
    invalid_placeholder = sandbox / "ALS-008" / "INVALID_TARGET_BLOCKED"
    assert not outside.exists()
    assert not invalid_placeholder.exists()

    failures = {
        item["scenario_id"]: item["failure_reason"]
        for item in load_json(
            Path(result["cert_root"])
            / "certification_report"
            / "000_acli_live_session_real_worker_execution_certification_report.json"
        )["scenario_results"]
    }
    assert failures["ALS-004"] == "HUMAN_REJECTED_EXECUTION"
    assert failures["ALS-005"] == "MISSING_HUMAN_APPROVAL"
    assert failures["ALS-006"] == "MISSING_EXECUTION_AUTHORIZATION"
    assert failures["ALS-007"] == "MODIFIED_HANDOFF_PACKAGE_DETECTED"
    assert failures["ALS-008"] == "INVALID_WORKER_TARGET"
    assert failures["ALS-009"] == "REPLAY_MISMATCH_DETECTED"


def test_side_effect_verification_failure_is_replay_visible(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )
    sandbox = Path(result["sandbox_root"])
    failed = sandbox / "ALS-010" / "failed_verification" / "wrong_content.txt"

    assert failed.exists()
    assert failed.read_text(encoding="utf-8") == "actual-live-session-content\n"

    verification = load_json(
        Path(result["cert_root"])
        / "scenarios"
        / "ALS-010"
        / "replay"
        / "008_side_effect_verification_recorded.json"
    )["artifact"]
    assert verification["verification_passed"] is False
    assert verification["failure_reason"] == "SIDE_EFFECT_VERIFICATION_FAILED"


def test_acli_live_session_report_assertions(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_acli_live_session_real_worker_execution_certification_report.json"
    )
    observed = report["observed"]

    assert observed["live_acli_session_simulated"] is True
    assert observed["natural_language_user_input"] is True
    assert observed["intent_resolution"] is True
    assert observed["clarification_if_required"] is True
    assert observed["execution_summary_generation"] is True
    assert observed["human_approval_requirement"] is True
    assert observed["authorization_issuance"] is True
    assert observed["worker_handoff_generation"] is True
    assert observed["real_worker_execution"] is True
    assert observed["side_effect_verification"] is True
    assert observed["replay_reconstruction"] is True
    assert observed["authority_boundary_preservation"] is True
    assert observed["secret_free_evidence"] is True


def test_acli_live_session_replay_is_secret_free(tmp_path):
    result = run_acli_live_session_real_worker_execution_certification(
        replay_base=tmp_path / "acli_live_real_worker"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
