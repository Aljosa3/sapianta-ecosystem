"""Evaluation for AIGOL_REAL_WORKER_EVALUATION_V1."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from aigol.runtime.external_worker_adapter_runtime import (
    accept_external_worker_result_package,
    create_external_worker_task_package,
    reconstruct_external_worker_adapter_replay,
)
from aigol.runtime.first_external_llm_worker_runtime import (
    FIRST_EXTERNAL_LLM_WORKER_ID,
    run_first_external_llm_worker,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED, certify_validated_replay
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED, validate_governed_execution_result
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-06-12T00:00:00Z"


def _load_execution_candidate_helper():
    helper_path = Path(__file__).with_name("test_governed_worker_execution_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("governed_worker_execution_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("governed worker execution helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._execution_candidate


_execution_candidate = _load_execution_candidate_helper()


def _task_approval(execution_candidate: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-REAL-WORKER-EVALUATION-000001",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_execution_candidate": execution_candidate["execution_candidate_id"],
        "source_execution_candidate_hash": execution_candidate["artifact_hash"],
        "approval_scope": "CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY",
        "external_worker_task_allowed": True,
        "implementation_result_creation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capability() -> dict:
    return {
        "worker_interface": FIRST_EXTERNAL_LLM_WORKER_ID,
        "worker_family": "PROVIDER_NEUTRAL_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _proposal_quality_score(payload: dict) -> float:
    checks = [
        payload.get("proposal_authority") == "PROPOSAL_ONLY",
        bool(payload.get("patch_proposals")),
        bool(payload.get("file_proposals")),
        bool(payload.get("test_proposals")),
        payload.get("repository_mutation_performed") is False,
        payload.get("command_execution_performed") is False,
        payload.get("replay_compatible") is True,
        payload.get("certification_compatible") is True,
    ]
    return round(100.0 * sum(1 for check in checks if check) / len(checks), 1)


def test_real_worker_evaluation_completes_governed_path(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    implementation_request_wrapper = load_json(
        tmp_path / "implementation_request" / "000_implementation_request_recorded.json"
    )
    implementation_request = implementation_request_wrapper["artifact"]
    task_capture = create_external_worker_task_package(
        task_id="REAL-WORKER-EVALUATION-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "real_worker_evaluation_adapter",
        worker_capability_declaration=_capability(),
    )
    worker_capture = run_first_external_llm_worker(
        result_id="REAL-WORKER-EVALUATION-RESULT-PACKAGE-000001",
        task_package_artifact=task_capture["external_worker_task_package"],
        completed_at=CREATED_AT,
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=worker_capture["external_worker_result_package"],
        task_package_artifact=task_capture["external_worker_task_package"],
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "real_worker_evaluation_adapter",
    )
    validation = validate_governed_execution_result(
        validation_id="REAL-WORKER-EVALUATION-VALIDATION-000001",
        worker_execution_result_artifact=adapter_capture["worker_execution_result_artifact"],
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "real_worker_evaluation_validation",
    )
    certification = certify_validated_replay(
        certification_id="REAL-WORKER-EVALUATION-REPLAY-CERTIFICATION-000001",
        result_validation_artifact=validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "real_worker_evaluation_replay_certification",
    )
    reconstructed = reconstruct_external_worker_adapter_replay(tmp_path / "real_worker_evaluation_adapter")
    payload = worker_capture["external_worker_result_package"]["worker_result_payload"]

    assert implementation_request["artifact_type"] == "IMPLEMENTATION_REQUEST_ARTIFACT_V1"
    assert execution_candidate["source_implementation_request"] == implementation_request["implementation_request_id"]
    assert task_capture["task_package_generated"] is True
    assert worker_capture["task_package_consumed"] is True
    assert worker_capture["result_package_generated"] is True
    assert adapter_capture["result_package_accepted"] is True
    assert adapter_capture["worker_execution_result_artifact"]["provider_neutrality_preserved"] is True
    assert validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["provider_neutrality_preserved"] is True
    assert _proposal_quality_score(payload) == 100.0


def test_real_worker_evaluation_report_matches_measured_scores() -> None:
    report_path = Path(__file__).resolve().parents[1] / ".github/governance/review/REAL_WORKER_EVALUATION_REPORT_V1.json"
    report = load_json(report_path)
    outputs = report["final_outputs"]

    assert report["artifact_type"] == "REAL_WORKER_EVALUATION_REPORT_V1"
    assert report["selected_real_task"]["task_id"] == "AIGOL_REAL_WORKER_EVALUATION_V1"
    assert report["measurement"]["proposal_quality_score"] == 100.0
    assert report["measurement"]["worker_reliability_score"] == 100.0
    assert report["measurement"]["replay_integrity"] is True
    assert report["measurement"]["governance_integrity"] is True
    assert outputs["REAL_WORKER_EVALUATION_PASSED"] == "YES"
    assert outputs["REPLAY_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["GOVERNANCE_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["WORKER_RELIABILITY_SCORE"] == "100.0"
    assert outputs["READY_FOR_SUPERVISED_REAL_PROJECT_USAGE"] == "YES"
