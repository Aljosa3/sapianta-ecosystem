"""Tests for G18 universal provider Worker runtime binding."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from aigol.runtime.external_worker_adapter_runtime import create_external_worker_task_package
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.universal_provider_worker_runtime import (
    UNIVERSAL_PROVIDER_WORKER_COMPLETED,
    UNIVERSAL_PROVIDER_WORKER_INTERFACE,
    run_universal_provider_worker_runtime,
)


CREATED_AT = "2026-06-13T00:00:00Z"


def _load_execution_candidate_helper():
    helper_path = Path(__file__).with_name("test_governed_worker_execution_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("governed_worker_execution_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("governed worker execution helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._execution_candidate


_execution_candidate = _load_execution_candidate_helper()


def _task_approval(execution_candidate: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-UNIVERSAL-PROVIDER-WORKER-000001",
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


def _capability() -> dict[str, Any]:
    return {
        "worker_interface": UNIVERSAL_PROVIDER_WORKER_INTERFACE,
        "worker_family": "UNIVERSAL_PROVIDER_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _task_package(tmp_path: Path) -> dict[str, Any]:
    execution_candidate = _execution_candidate(tmp_path)
    return create_external_worker_task_package(
        task_id="UNIVERSAL-PROVIDER-WORKER-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_path",
        worker_capability_declaration=_capability(),
    )["external_worker_task_package"]


def _openai_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
    assert request_metadata["provider_identity"] == "OPENAI"
    assert request_metadata["tool_use"] is False
    assert request_metadata["function_calling"] is False
    assert request_metadata["streaming"] is False
    return {
        "id": "universal-provider-worker-openai-response-001",
        "output_text": "Inspect runtime metadata and return bounded findings.",
    }


def test_universal_provider_worker_selects_provider_then_delegates_to_certified_attachment(tmp_path) -> None:
    capture = run_universal_provider_worker_runtime(
        result_id="UNIVERSAL-PROVIDER-WORKER-RESULT-000001",
        task_package_artifact=_task_package(tmp_path),
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "universal_provider_worker",
        openai_client=_openai_client,
        api_key="test-openai-key",
        model="gpt-5.1",
        timeout_seconds=20,
    )

    assert capture["universal_provider_worker_status"] == UNIVERSAL_PROVIDER_WORKER_COMPLETED
    assert capture["universal_provider_runtime_reached"] is True
    assert capture["smart_selection_executed"] is True
    assert capture["selected_resource_id"] == "OPENAI"
    assert capture["openai_provider_connected"] is True
    assert capture["result_package_generated"] is True
    assert capture["replay_lineage_preserved"] is True
    assert (tmp_path / "universal_provider_worker" / "universal_resource_selection").exists()
    assert (
        tmp_path
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "certified_provider_attachment"
        / "002_certified_provider_attachment_recorded.json"
    ).exists()
