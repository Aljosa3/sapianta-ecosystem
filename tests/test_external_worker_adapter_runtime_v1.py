"""Tests for AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.external_worker_adapter_runtime import (
    EXTERNAL_WORKER_RESULT_PACKAGE_V1,
    EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
    EXTERNAL_WORKER_TASK_PACKAGE_V1,
    accept_external_worker_result_package,
    create_external_worker_result_package,
    create_external_worker_task_package,
    reconstruct_external_worker_adapter_replay,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    WORKER_EXECUTION_RESULT_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED, validate_governed_execution_result
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


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


def _task_approval(execution_candidate: dict, *, granted: bool = True) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-EXTERNAL-WORKER-TASK-000001",
        "approval_status": APPROVED if granted else "PENDING",
        "approval_granted": granted,
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


def _capability(worker_interface: str = "generic-local-worker") -> dict:
    return {
        "worker_interface": worker_interface,
        "worker_family": "GENERIC_EXTERNAL_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _task_package(tmp_path, execution_candidate: dict | None = None) -> dict:
    candidate = execution_candidate or _execution_candidate(tmp_path)
    return create_external_worker_task_package(
        task_id="EXTERNAL-WORKER-TASK-000001",
        execution_candidate_artifact=candidate,
        human_approval_artifact=_task_approval(candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_adapter",
        worker_capability_declaration=_capability(),
    )["external_worker_task_package"]


def test_external_worker_adapter_converts_candidate_to_task_to_result(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    task_capture = create_external_worker_task_package(
        task_id="EXTERNAL-WORKER-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_adapter",
        worker_capability_declaration=_capability(),
    )
    task = task_capture["external_worker_task_package"]
    result_package = create_external_worker_result_package(
        result_id="RESULT-PACKAGE-000001",
        task_package_artifact=task,
        worker_result_payload={"files_changed": [], "summary": "bounded external worker result"},
        worker_evidence={
            "worker_runtime": "fixture-worker",
            "commands_executed": [],
            "implementation_result_created": False,
        },
        execution_logs=["received task package", "completed bounded worker task"],
        completed_at=CREATED_AT,
    )
    result_capture = accept_external_worker_result_package(
        result_package=result_package,
        task_package_artifact=task,
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_adapter",
    )
    result = result_capture["worker_execution_result_artifact"]
    reconstructed = reconstruct_external_worker_adapter_replay(tmp_path / "external_worker_adapter")

    assert task_capture["task_status"] == EXTERNAL_WORKER_TASK_PACKAGE_CREATED
    assert task_capture["task_package_generated"] is True
    assert task["artifact_type"] == EXTERNAL_WORKER_TASK_PACKAGE_V1
    assert task["source_execution_candidate"] == execution_candidate["execution_candidate_id"]
    assert task["source_implementation_request"] == execution_candidate["source_implementation_request"]
    assert task["worker_authorization"]["authorized"] is True
    assert task["worker_authorization"]["worker_interface"] == "generic-local-worker"
    assert task["provider_neutral"] is True
    assert task["provider_specific_logic_used"] is False
    assert result_package["artifact_type"] == EXTERNAL_WORKER_RESULT_PACKAGE_V1
    assert result_capture["result_package_accepted"] is True
    assert result_capture["execution_result_artifact_generated"] is True
    assert result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1
    assert result["execution_status"] == WORKER_EXECUTION_COMPLETED
    assert result["source_execution_candidate"] == execution_candidate["execution_candidate_id"]
    assert result["external_worker_task_package_hash"] == task["artifact_hash"]
    assert result["external_worker_result_package_hash"] == result_package["artifact_hash"]
    assert result["worker_evidence"]["provider_neutral_contract"] is True
    assert result["worker_evidence"]["governed_execution"] is True
    assert result["worker_evidence"]["external_provider_invoked"] is False
    assert result["worker_evidence"]["subprocess_invoked"] is False
    assert result["validation_inputs"]["validation_performed"] is True
    assert result["worker_executed"] is True
    assert result["implementation_result_created"] is False
    assert result["code_modified"] is False
    assert result["governance_modified"] is False
    assert result["provider_invoked"] is False
    assert result["provider_neutrality_preserved"] is True
    assert result["ready_for_result_validation_runtime"] is True
    assert reconstructed["task_package_generated"] is True
    assert reconstructed["result_package_accepted"] is True
    assert reconstructed["execution_result_generated"] is True
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["provider_neutrality_preserved"] is True
    assert reconstructed["ready_for_first_external_worker"] is True
    validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-EXTERNAL-WORKER-000001",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_result_validation",
    )
    assert validation["validation_status"] == RESULT_VALIDATION_COMPLETED


def test_external_worker_adapter_rejects_non_execution_candidate(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    execution_candidate["artifact_type"] = "WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1"
    execution_candidate.pop("artifact_hash")
    execution_candidate["artifact_hash"] = replay_hash(execution_candidate)
    capture = create_external_worker_task_package(
        task_id="EXTERNAL-WORKER-TASK-WRONG-TYPE",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
        worker_capability_declaration=_capability(),
    )

    assert capture["task_status"] == "FAILED_CLOSED"
    assert capture["task_package_generated"] is False
    assert capture["replay_lineage_preserved"] is False
    assert "invalid artifact type" in capture["failure_reason"]


def test_external_worker_adapter_rejects_result_package_lineage_mismatch(tmp_path) -> None:
    task = _task_package(tmp_path)
    result_package = create_external_worker_result_package(
        result_id="RESULT-PACKAGE-MISMATCH",
        task_package_artifact=task,
        worker_result_payload={"summary": "bounded external worker result"},
        worker_evidence={"worker_runtime": "fixture-worker"},
        execution_logs=["completed bounded worker task"],
        completed_at=CREATED_AT,
    )
    result_package["task_package_hash"] = "sha256:" + "0" * 64
    result_package.pop("artifact_hash")
    result_package["artifact_hash"] = replay_hash(result_package)
    capture = accept_external_worker_result_package(
        result_package=result_package,
        task_package_artifact=task,
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_adapter",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert capture["result_package_accepted"] is False
    assert capture["replay_lineage_preserved"] is False
    assert "task hash mismatch" in capture["failure_reason"]


def test_external_worker_adapter_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    task = _task_package(tmp_path)
    result_package = create_external_worker_result_package(
        result_id="RESULT-PACKAGE-CORRUPT",
        task_package_artifact=task,
        worker_result_payload={"summary": "bounded external worker result"},
        worker_evidence={"worker_runtime": "fixture-worker"},
        execution_logs=["completed bounded worker task"],
        completed_at=CREATED_AT,
    )
    accept_external_worker_result_package(
        result_package=result_package,
        task_package_artifact=task,
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_adapter",
    )
    path = tmp_path / "external_worker_adapter" / "002_external_worker_execution_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_external_worker_adapter_replay(tmp_path / "external_worker_adapter")


def test_external_worker_adapter_runtime_has_no_provider_specific_logic_or_execution_surfaces() -> None:
    import aigol.runtime.external_worker_adapter_runtime as runtime

    source = inspect.getsource(runtime)

    for forbidden in (
        "Codex",
        "Claude",
        "Mistral",
        "OpenAI",
        "subprocess.",
        "os.system",
        "invoke_worker(",
        "execute_worker(",
        "invoke_live_external_llm_provider(",
        "modify_governance(",
        "modify_code(",
    ):
        assert forbidden not in source
