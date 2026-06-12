"""Demonstration for AIGOL_GOVERNED_AUTONOMOUS_DEVELOPMENT_FLOW_V1."""

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
REPORT = ROOT / ".github/governance/review/AUTONOMOUS_DEVELOPMENT_FLOW_REPORT_V1.json"
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
        "approval_id": "HUMAN-APPROVAL-AUTONOMOUS-FLOW-TASK-000001",
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


def test_governed_autonomous_development_flow_completes_with_existing_runtimes(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target_path = "aigol/runtime/autonomous_flow_generated_worker.py"
    target_content = "def autonomous_flow_status():\n    return 'validated'\n"
    execution_candidate = _execution_candidate(tmp_path)
    implementation_request = load_json(
        tmp_path / "implementation_request" / "000_implementation_request_recorded.json"
    )["artifact"]
    worker_request = load_json(tmp_path / "worker_request" / "000_worker_request_recorded.json")["artifact"]
    dispatch_candidate = load_json(
        tmp_path / "dispatch_candidate" / "000_worker_dispatch_candidate_recorded.json"
    )["artifact"]
    task_capture = create_external_worker_task_package(
        task_id="AUTONOMOUS-DEVELOPMENT-FLOW-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_adapter",
        worker_capability_declaration=_capability(),
    )
    worker_capture = run_first_external_llm_worker(
        result_id="AUTONOMOUS-DEVELOPMENT-FLOW-RESULT-PACKAGE-000001",
        task_package_artifact=task_capture["external_worker_task_package"],
        completed_at=CREATED_AT,
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=worker_capture["external_worker_result_package"],
        task_package_artifact=task_capture["external_worker_task_package"],
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_adapter",
    )
    worker_result = adapter_capture["worker_execution_result_artifact"]
    proposal = create_patch_proposal_artifact(
        proposal_id="PATCH-PROPOSAL-AUTONOMOUS-DEVELOPMENT-FLOW-000001",
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
            adapter_capture["external_worker_replay_reference"],
            worker_result["worker_execution_id"],
        ],
        replay_hashes=[worker_result["artifact_hash"]],
        authorization_references=["HUMAN-AUTHORIZATION-AUTONOMOUS-FLOW-PATCH-000001"],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )
    mutation_capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-AUTONOMOUS-DEVELOPMENT-FLOW-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_mutation",
    )
    mutation = mutation_capture["repository_mutation_artifact"]
    validation_request = create_validation_command_request(
        request_id="VALIDATION-COMMAND-REQUEST-AUTONOMOUS-DEVELOPMENT-FLOW-000001",
        command=["python", "-m", "py_compile", str(repo / target_path)],
        cwd=str(repo),
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=[mutation_capture["repository_mutation_replay_reference"]],
        replay_hashes=[mutation["artifact_hash"]],
        timeout_seconds=30,
    )
    validation_command = execute_validation_command(
        request_artifact=validation_request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_validation_command",
    )
    result_validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-AUTONOMOUS-DEVELOPMENT-FLOW-000001",
        worker_execution_result_artifact=worker_result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-AUTONOMOUS-DEVELOPMENT-FLOW-000001",
        result_validation_artifact=result_validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "autonomous_development_flow_replay_certification",
    )
    adapter_replay = reconstruct_external_worker_adapter_replay(tmp_path / "autonomous_development_flow_adapter")
    mutation_replay = reconstruct_repository_mutation_replay(tmp_path / "autonomous_development_flow_mutation")
    command_replay = reconstruct_validation_command_replay(tmp_path / "autonomous_development_flow_validation_command")
    validation_replay = reconstruct_result_validation_replay(tmp_path / "autonomous_development_flow_result_validation")

    assert implementation_request["artifact_type"] == "IMPLEMENTATION_REQUEST_ARTIFACT_V1"
    assert worker_request["artifact_type"] == "WORKER_REQUEST_ARTIFACT_V1"
    assert dispatch_candidate["artifact_type"] == "WORKER_DISPATCH_CANDIDATE_ARTIFACT_V1"
    assert task_capture["task_package_generated"] is True
    assert worker_capture["task_package_consumed"] is True
    assert worker_capture["result_package_generated"] is True
    assert adapter_capture["result_package_accepted"] is True
    assert mutation_capture["mutation_status"] == REPOSITORY_MUTATION_COMPLETED
    assert mutation["mutated_files"] == [target_path]
    assert (repo / target_path).read_text(encoding="utf-8") == target_content
    assert validation_command["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert validation_command["validation_command_result_artifact"]["exit_code"] == 0
    assert result_validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert adapter_replay["replay_lineage_preserved"] is True
    assert mutation_replay["replay_lineage_preserved"] is True
    assert command_replay["replay_lineage_preserved"] is True
    assert validation_replay["replay_lineage_preserved"] is True
    assert mutation_capture["unauthorized_mutation_prevented"] is True
    assert mutation_capture["fail_closed_preserved"] is True


def test_autonomous_development_flow_report_records_measurements() -> None:
    report = load_json(REPORT)
    outputs = report["final_outputs"]
    measurement = report["measurement"]

    assert report["artifact_type"] == "AUTONOMOUS_DEVELOPMENT_FLOW_REPORT_V1"
    assert report["governance_boundary"]["new_governance_primitives_introduced"] is False
    assert "AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1" in report["certified_components_used"]
    assert "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1" in report["certified_components_used"]
    assert measurement["operator_actions"]["baseline_manual_actions"] == 8
    assert measurement["operator_actions"]["governed_flow_actions"] == 6
    assert measurement["operator_actions"]["actions_reduced"] == 2
    assert measurement["operator_actions"]["operator_actions_reduced"] is True
    assert measurement["replay_integrity"] is True
    assert measurement["governance_integrity"] is True
    assert measurement["repository_mutation_success"] is True
    assert measurement["validation_success"] is True
    assert measurement["replay_certification_success"] is True
    assert outputs["AUTONOMOUS_DEVELOPMENT_FLOW_COMPLETED"] == "YES"
    assert outputs["REPLAY_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["GOVERNANCE_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["OPERATOR_ACTIONS_REDUCED"] == "YES_2_ACTIONS"
    assert outputs["READY_FOR_SUPERVISED_PRODUCTION_DEVELOPMENT"] == "YES"
