"""Tests for AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1."""

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
    AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
    OPENAI_EXTERNAL_WORKER_COMPLETED,
    reconstruct_openai_external_worker_provider_adapter_replay,
    run_openai_external_worker_provider_adapter,
)
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED, certify_validated_replay
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
        "approval_id": "HUMAN-APPROVAL-OPENAI-EXTERNAL-WORKER-000001",
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


def _task_package(tmp_path) -> dict:
    execution_candidate = _execution_candidate(tmp_path)
    return create_external_worker_task_package(
        task_id="OPENAI-EXTERNAL-WORKER-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_path",
        worker_capability_declaration=_capability(),
    )["external_worker_task_package"]


def _openai_client(text: str = "Proposal only: inspect the task and return a bounded implementation summary."):
    def call(request_metadata):
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        assert request_metadata["automatic_retries"] is False
        return {"id": "openai-external-worker-response-001", "output_text": text}

    return call


def test_openai_external_worker_provider_adapter_connects_task_to_result_package(tmp_path) -> None:
    task = _task_package(tmp_path)
    capture = run_openai_external_worker_provider_adapter(
        result_id="OPENAI-EXTERNAL-WORKER-RESULT-000001",
        task_package_artifact=task,
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker",
        openai_client=_openai_client(),
        api_key="test-openai-key",
    )
    result_package = capture["external_worker_result_package"]
    replay = reconstruct_openai_external_worker_provider_adapter_replay(tmp_path / "openai_external_worker")

    assert capture["worker_status"] == OPENAI_EXTERNAL_WORKER_COMPLETED
    assert capture["openai_provider_connected"] is True
    assert capture["task_package_consumed"] is True
    assert capture["result_package_generated"] is True
    assert capture["replay_lineage_preserved"] is True
    assert capture["fail_closed_preserved"] is True
    assert capture["ready_for_first_real_openai_worker_execution"] is True
    assert result_package["artifact_type"] == "EXTERNAL_WORKER_RESULT_PACKAGE_V1"
    assert result_package["provider_neutral"] is True
    assert result_package["worker_evidence"]["worker_runtime"] == AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION
    assert result_package["worker_evidence"]["provider_invoked_inside_adapter"] is True
    assert result_package["worker_evidence"]["provider_authority"] is False
    assert replay["openai_provider_connected"] is True
    assert replay["ready_for_external_worker_adapter_runtime"] is True


def test_openai_external_worker_routes_through_adapter_validation_and_replay_certification(tmp_path) -> None:
    task = _task_package(tmp_path)
    openai_capture = run_openai_external_worker_provider_adapter(
        result_id="OPENAI-EXTERNAL-WORKER-RESULT-FULL-CHAIN-000001",
        task_package_artifact=task,
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker",
        openai_client=_openai_client(),
        api_key="test-openai-key",
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=openai_capture["external_worker_result_package"],
        task_package_artifact=task,
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_path",
    )
    result_validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-OPENAI-EXTERNAL-WORKER-000001",
        worker_execution_result_artifact=adapter_capture["worker_execution_result_artifact"],
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker_result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-OPENAI-EXTERNAL-WORKER-000001",
        result_validation_artifact=result_validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker_replay_certification",
    )
    adapter_replay = reconstruct_external_worker_adapter_replay(tmp_path / "external_worker_path")

    assert adapter_capture["result_package_accepted"] is True
    assert adapter_capture["replay_lineage_preserved"] is True
    assert adapter_capture["provider_neutrality_preserved"] is True
    assert adapter_replay["result_package_accepted"] is True
    assert result_validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED


def test_openai_external_worker_fails_closed_on_provider_failure(tmp_path) -> None:
    task = _task_package(tmp_path)

    def failing_client(_request_metadata):
        raise RuntimeError("provider unavailable")

    capture = run_openai_external_worker_provider_adapter(
        result_id="OPENAI-EXTERNAL-WORKER-RESULT-FAILED-000001",
        task_package_artifact=task,
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker_failed",
        openai_client=failing_client,
        api_key="test-openai-key",
    )

    assert capture["worker_status"] == "FAILED_CLOSED"
    assert capture["openai_provider_connected"] is False
    assert capture["task_package_consumed"] is False
    assert capture["result_package_generated"] is True
    assert capture["replay_lineage_preserved"] is False
    assert capture["fail_closed_preserved"] is True
    assert capture["ready_for_first_real_openai_worker_execution"] is False
    assert capture["external_worker_result_package"]["execution_status"] == "FAILED_CLOSED"


def test_openai_external_worker_fails_closed_before_provider_on_invalid_task(tmp_path) -> None:
    task = _task_package(tmp_path)
    task["artifact_type"] = "INVALID_TASK"
    task.pop("artifact_hash")
    task["artifact_hash"] = replay_hash(task)
    called = False

    def client(_request_metadata):
        nonlocal called
        called = True
        return {"output_text": "should not be called"}

    capture = run_openai_external_worker_provider_adapter(
        result_id="OPENAI-EXTERNAL-WORKER-RESULT-INVALID-TASK",
        task_package_artifact=task,
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "openai_external_worker_invalid_task",
        openai_client=client,
        api_key="test-openai-key",
    )

    assert called is False
    assert capture["worker_status"] == "FAILED_CLOSED"
    assert "invalid task package type" in capture["failure_reason"]
