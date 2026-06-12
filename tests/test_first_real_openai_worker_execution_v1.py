"""Demonstration for AIGOL_FIRST_REAL_OPENAI_WORKER_EXECUTION_V1."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from aigol.runtime.external_worker_adapter_runtime import (
    accept_external_worker_result_package,
    create_external_worker_task_package,
    reconstruct_external_worker_adapter_replay,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.openai_external_worker_provider_adapter import (
    reconstruct_openai_external_worker_provider_adapter_replay,
    run_openai_external_worker_provider_adapter,
)
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED, certify_validated_replay
from aigol.runtime.repository_mutation_worker_runtime import (
    REPOSITORY_MUTATION_COMPLETED,
    apply_repository_mutation,
    create_patch_proposal_artifact,
    reconstruct_repository_mutation_replay,
)
from aigol.runtime.result_validation_runtime import (
    RESULT_VALIDATION_COMPLETED,
    reconstruct_result_validation_replay,
    validate_governed_execution_result,
)
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
    reconstruct_validation_command_replay,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/FIRST_REAL_OPENAI_WORKER_EXECUTION_REPORT_V1.json"
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
        "approval_id": "HUMAN-APPROVAL-FIRST-REAL-OPENAI-WORKER-000001",
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
        "worker_interface": "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1",
        "worker_family": "REAL_PROVIDER_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _openai_client():
    text = (
        "Proposal only: inspect the task and return a bounded implementation summary."
    )

    def call(request_metadata):
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        assert request_metadata["automatic_retries"] is False
        return {"id": "first-real-openai-worker-response-001", "output_text": text}

    return call


def _provider_response_quality_score(payload: dict, evidence: dict) -> float:
    text = payload.get("provider_response_text", "")
    checks = [
        isinstance(text, str) and "Proposal only" in text,
        isinstance(text, str) and "bounded implementation summary" in text,
        payload.get("proposal_authority") == "PROPOSAL_ONLY",
        payload.get("repository_mutation_performed") is False,
        payload.get("command_execution_performed") is False,
        payload.get("provider_output_authoritative") is False,
        payload.get("provider_neutral_above_adapter") is True,
        evidence.get("provider_authority") is False,
        evidence.get("provider_invoked_inside_adapter") is True,
        evidence.get("fail_closed_preserved") is True,
    ]
    return round(100.0 * sum(1 for check in checks if check) / len(checks), 1)


def test_first_real_openai_worker_execution_completes_repository_task(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target_path = "aigol/runtime/first_real_openai_worker_execution_marker.py"
    target_content = (
        "def first_real_openai_worker_execution_status():\n"
        "    return 'validated-openai-worker-execution'\n"
    )
    execution_candidate = _execution_candidate(tmp_path)
    task_capture = create_external_worker_task_package(
        task_id="FIRST-REAL-OPENAI-WORKER-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_external_adapter",
        worker_capability_declaration=_capability(),
    )
    openai_worker = run_openai_external_worker_provider_adapter(
        result_id="FIRST-REAL-OPENAI-WORKER-RESULT-PACKAGE-000001",
        task_package_artifact=task_capture["external_worker_task_package"],
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_provider",
        openai_client=_openai_client(),
        api_key="test-openai-key",
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=openai_worker["external_worker_result_package"],
        task_package_artifact=task_capture["external_worker_task_package"],
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_external_adapter",
    )
    worker_result = adapter_capture["worker_execution_result_artifact"]
    provider_payload = openai_worker["external_worker_result_package"]["worker_result_payload"]
    provider_evidence = openai_worker["external_worker_result_package"]["worker_evidence"]
    proposal = create_patch_proposal_artifact(
        proposal_id="PATCH-PROPOSAL-FIRST-REAL-OPENAI-WORKER-000001",
        file_mutations=[
            {
                "target_path": target_path,
                "operation": "CREATE_OR_REPLACE",
                "new_content": target_content,
                "new_content_hash": replay_hash(target_content),
                "approved": True,
            }
        ],
        replay_references=[
            openai_worker["openai_external_worker_replay_reference"],
            adapter_capture["external_worker_replay_reference"],
            worker_result["worker_execution_id"],
        ],
        replay_hashes=[
            openai_worker["external_worker_result_package"]["artifact_hash"],
            worker_result["artifact_hash"],
        ],
        authorization_references=["HUMAN-AUTHORIZATION-FIRST-REAL-OPENAI-WORKER-PATCH-000001"],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )
    mutation_capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-FIRST-REAL-OPENAI-WORKER-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_mutation",
    )
    validation_request = create_validation_command_request(
        request_id="VALIDATION-COMMAND-FIRST-REAL-OPENAI-WORKER-000001",
        command=["python", "-m", "py_compile", str(repo / target_path)],
        cwd=str(repo),
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=[mutation_capture["repository_mutation_replay_reference"]],
        replay_hashes=[mutation_capture["repository_mutation_artifact"]["artifact_hash"]],
        timeout_seconds=30,
    )
    validation_command = execute_validation_command(
        request_artifact=validation_request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_validation_command",
    )
    result_validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-FIRST-REAL-OPENAI-WORKER-000001",
        worker_execution_result_artifact=worker_result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-FIRST-REAL-OPENAI-WORKER-000001",
        result_validation_artifact=result_validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "first_real_openai_worker_replay_certification",
    )
    provider_replay = reconstruct_openai_external_worker_provider_adapter_replay(
        tmp_path / "first_real_openai_worker_provider"
    )
    external_adapter_replay = reconstruct_external_worker_adapter_replay(
        tmp_path / "first_real_openai_worker_external_adapter"
    )
    mutation_replay = reconstruct_repository_mutation_replay(tmp_path / "first_real_openai_worker_mutation")
    command_replay = reconstruct_validation_command_replay(tmp_path / "first_real_openai_worker_validation_command")
    result_validation_replay = reconstruct_result_validation_replay(tmp_path / "first_real_openai_worker_result_validation")

    assert task_capture["task_package_generated"] is True
    assert openai_worker["openai_provider_connected"] is True
    assert openai_worker["task_package_consumed"] is True
    assert openai_worker["result_package_generated"] is True
    assert _provider_response_quality_score(provider_payload, provider_evidence) == 100.0
    assert adapter_capture["result_package_accepted"] is True
    assert mutation_capture["mutation_status"] == REPOSITORY_MUTATION_COMPLETED
    assert (repo / target_path).read_text(encoding="utf-8") == target_content
    assert validation_command["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert validation_command["validation_command_result_artifact"]["exit_code"] == 0
    assert result_validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert provider_replay["replay_lineage_preserved"] is True
    assert external_adapter_replay["replay_lineage_preserved"] is True
    assert mutation_replay["replay_lineage_preserved"] is True
    assert command_replay["replay_lineage_preserved"] is True
    assert result_validation_replay["replay_lineage_preserved"] is True


def test_first_real_openai_worker_execution_report_records_measurement() -> None:
    report = load_json(REPORT)
    outputs = report["final_outputs"]
    measurement = report["measurement"]

    assert report["artifact_type"] == "FIRST_REAL_OPENAI_WORKER_EXECUTION_REPORT_V1"
    assert report["selected_real_repository_task"]["task_id"] == "AIGOL_FIRST_REAL_OPENAI_WORKER_EXECUTION_V1"
    assert report["selected_real_repository_task"]["provider_worker"] == "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"
    assert measurement["provider_response_quality_score"] == 100.0
    assert measurement["replay_integrity"] is True
    assert measurement["governance_integrity"] is True
    assert measurement["operator_effort"]["operator_actions_reduced"] is True
    assert measurement["validation_success"] is True
    assert outputs["REAL_OPENAI_WORKER_EXECUTION_COMPLETED"] == "YES"
    assert outputs["REPLAY_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["GOVERNANCE_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["VALIDATION_PASSED"] == "YES"
    assert outputs["READY_FOR_ROUTINE_OPENAI_WORKER_USAGE"] == "YES_SUPERVISED"
