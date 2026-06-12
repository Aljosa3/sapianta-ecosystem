"""Tests for AIGOL_FIRST_EXTERNAL_LLM_WORKER_V1."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from aigol.runtime.external_worker_adapter_runtime import (
    accept_external_worker_result_package,
    create_external_worker_task_package,
    reconstruct_external_worker_adapter_replay,
)
from aigol.runtime.first_external_llm_worker_runtime import (
    AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
    FIRST_EXTERNAL_LLM_WORKER_ID,
    run_first_external_llm_worker,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.governed_worker_execution_runtime import WORKER_EXECUTION_RESULT_ARTIFACT_V1
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED, validate_governed_execution_result
from aigol.runtime.transport.serialization import replay_hash


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
        "approval_id": "HUMAN-APPROVAL-FIRST-EXTERNAL-WORKER-000001",
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


def _task_package(tmp_path) -> dict:
    execution_candidate = _execution_candidate(tmp_path)
    return create_external_worker_task_package(
        task_id="FIRST-EXTERNAL-WORKER-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_path",
        worker_capability_declaration=_capability(),
    )["external_worker_task_package"]


def test_first_external_llm_worker_generates_proposal_only_result_package(tmp_path) -> None:
    task = _task_package(tmp_path)
    worker_capture = run_first_external_llm_worker(
        result_id="FIRST-EXTERNAL-WORKER-RESULT-000001",
        task_package_artifact=task,
        completed_at=CREATED_AT,
    )
    result_package = worker_capture["external_worker_result_package"]
    payload = result_package["worker_result_payload"]
    evidence = result_package["worker_evidence"]

    assert worker_capture["worker_status"] == "WORKER_EXECUTION_COMPLETED"
    assert worker_capture["task_package_consumed"] is True
    assert worker_capture["result_package_generated"] is True
    assert worker_capture["patch_proposal_generated"] is True
    assert worker_capture["file_proposal_generated"] is True
    assert worker_capture["test_proposal_generated"] is True
    assert worker_capture["repository_mutation_performed"] is False
    assert worker_capture["command_execution_performed"] is False
    assert worker_capture["replay_compatibility_confirmed"] is True
    assert worker_capture["provider_neutrality_confirmed"] is True
    assert worker_capture["ready_for_real_worker_evaluation"] is True
    assert payload["proposal_authority"] == "PROPOSAL_ONLY"
    assert payload["patch_proposals"][0]["applied"] is False
    assert payload["file_proposals"][0]["created"] is False
    assert payload["test_proposals"][0]["created"] is False
    assert payload["test_proposals"][0]["executed"] is False
    assert payload["repository_mutation_performed"] is False
    assert payload["command_execution_performed"] is False
    assert evidence["worker_runtime"] == AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION
    assert evidence["repository_mutation_performed"] is False
    assert evidence["command_execution_performed"] is False
    assert evidence["provider_neutral"] is True


def test_first_external_llm_worker_completes_adapter_to_validation_path(tmp_path) -> None:
    task = _task_package(tmp_path)
    worker_capture = run_first_external_llm_worker(
        result_id="FIRST-EXTERNAL-WORKER-RESULT-ADAPTER-000001",
        task_package_artifact=task,
        completed_at=CREATED_AT,
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=worker_capture["external_worker_result_package"],
        task_package_artifact=task,
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_path",
    )
    result = adapter_capture["worker_execution_result_artifact"]
    reconstructed = reconstruct_external_worker_adapter_replay(tmp_path / "external_worker_path")
    validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-FIRST-EXTERNAL-WORKER-000001",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "first_external_worker_validation",
    )

    assert adapter_capture["result_package_accepted"] is True
    assert result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1
    assert result["provider_neutrality_preserved"] is True
    assert result["worker_result_payload"]["proposal_authority"] == "PROPOSAL_ONLY"
    assert result["implementation_result_created"] is False
    assert result["code_modified"] is False
    assert result["provider_invoked"] is False
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["provider_neutrality_preserved"] is True
    assert validation["validation_status"] == RESULT_VALIDATION_COMPLETED


def test_first_external_llm_worker_fails_closed_on_non_task_package(tmp_path) -> None:
    task = _task_package(tmp_path)
    task["artifact_type"] = "WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1"
    task.pop("artifact_hash")
    task["artifact_hash"] = replay_hash(task)
    capture = run_first_external_llm_worker(
        result_id="FIRST-EXTERNAL-WORKER-WRONG-TYPE",
        task_package_artifact=task,
        completed_at=CREATED_AT,
    )

    assert capture["worker_status"] == "FAILED_CLOSED"
    assert capture["task_package_consumed"] is False
    assert capture["result_package_generated"] is True
    assert capture["repository_mutation_performed"] is False
    assert capture["command_execution_performed"] is False
    assert "invalid task package type" in capture["failure_reason"]


def test_first_external_llm_worker_has_no_mutation_command_or_provider_specific_surfaces() -> None:
    import aigol.runtime.first_external_llm_worker_runtime as runtime

    source = inspect.getsource(runtime)

    for forbidden in (
        "Codex",
        "Claude",
        "Mistral",
        "OpenAI",
        "write_json_immutable",
        "write_text(",
        "apply_patch",
        "subprocess.",
        "os.system",
        "invoke_live_external_llm_provider(",
        "modify_governance(",
        "modify_code(",
    ):
        assert forbidden not in source
