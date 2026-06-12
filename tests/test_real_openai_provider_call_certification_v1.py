"""Live certification for AIGOL_REAL_OPENAI_PROVIDER_CALL_CERTIFICATION_V1."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

from aigol.provider.providers.openai_provider import OpenAIHTTPClient, OPENAI_RESPONSES_ENDPOINT
from aigol.runtime.external_worker_adapter_runtime import accept_external_worker_result_package
from aigol.runtime.external_worker_adapter_runtime import create_external_worker_task_package
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.openai_external_worker_provider_adapter import run_openai_external_worker_provider_adapter
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED, certify_validated_replay
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED, validate_governed_execution_result
from aigol.runtime.transport.serialization import load_json, replay_hash


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = ROOT / ".github/governance/finalize/AIGOL_REAL_OPENAI_PROVIDER_CALL_CERTIFICATION_V1.json"
CREATED_AT = "2026-06-12T00:00:00Z"
LIVE_FLAG = "AIGOL_RUN_REAL_OPENAI_PROVIDER_CALL"


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
        "approval_id": "HUMAN-APPROVAL-REAL-OPENAI-PROVIDER-CALL-000001",
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


def _real_openai_client(record: dict):
    def call(_request_metadata):
        payload = {
            "model": "gpt-5.1",
            "input": (
                "Return exactly this sentence and nothing else: "
                "Proposal only: inspect the task and return a bounded implementation summary."
            ),
            "stream": False,
            "max_output_tokens": 64,
        }
        raw = OpenAIHTTPClient()(
            payload,
            api_key=os.environ["OPENAI_API_KEY"],
            endpoint=OPENAI_RESPONSES_ENDPOINT,
            timeout_seconds=30,
        )
        if isinstance(raw, dict):
            record["response_id"] = raw.get("id")
            record["model"] = raw.get("model")
            record["usage"] = raw.get("usage")
        return raw

    return call


@pytest.mark.skipif(
    os.environ.get(LIVE_FLAG) != "1" or not os.environ.get("OPENAI_API_KEY"),
    reason="set AIGOL_RUN_REAL_OPENAI_PROVIDER_CALL=1 and OPENAI_API_KEY to run live OpenAI certification",
)
def test_real_openai_provider_call_completes_worker_lifecycle(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    task_capture = create_external_worker_task_package(
        task_id="REAL-OPENAI-PROVIDER-CALL-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "real_openai_provider_call_external_adapter",
        worker_capability_declaration=_capability(),
    )
    response_record: dict = {}
    openai_worker = run_openai_external_worker_provider_adapter(
        result_id="REAL-OPENAI-PROVIDER-CALL-RESULT-PACKAGE-000001",
        task_package_artifact=task_capture["external_worker_task_package"],
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "real_openai_provider_call_worker",
        openai_client=_real_openai_client(response_record),
        api_key=None,
        model="gpt-5.1",
        timeout_seconds=30,
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=openai_worker["external_worker_result_package"],
        task_package_artifact=task_capture["external_worker_task_package"],
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "real_openai_provider_call_external_adapter",
    )
    result_validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-REAL-OPENAI-PROVIDER-CALL-000001",
        worker_execution_result_artifact=adapter_capture["worker_execution_result_artifact"],
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "real_openai_provider_call_result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-REAL-OPENAI-PROVIDER-CALL-000001",
        result_validation_artifact=result_validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "real_openai_provider_call_replay_certification",
    )
    provider_artifact = openai_worker["openai_provider_capture_artifact"]

    assert task_capture["task_package_generated"] is True
    assert openai_worker["openai_provider_connected"] is True
    assert openai_worker["task_package_consumed"] is True
    assert openai_worker["result_package_generated"] is True
    assert adapter_capture["result_package_accepted"] is True
    assert result_validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert response_record["response_id"]
    assert isinstance(response_record["usage"], dict)
    assert provider_artifact["provider_status"] == "COMPLETED"
    assert provider_artifact["provider_authority"] is False
    assert provider_artifact["provider_output_authoritative"] is False
    assert provider_artifact["fail_closed_preserved"] is True
    assert provider_artifact["replay_lineage_preserved"] is True


def test_real_openai_provider_call_certification_records_outputs() -> None:
    certification = load_json(CERTIFICATION)
    outputs = certification["final_outputs"]

    assert certification["artifact_type"] == "REAL_OPENAI_PROVIDER_CALL_CERTIFICATION_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert certification["live_provider_evidence"]["real_endpoint_invoked"] is True
    assert certification["live_provider_evidence"]["token_usage_recorded"] is True
    assert certification["governance_guarantees"]["fail_closed_preserved"] is True
    assert certification["governance_guarantees"]["replay_lineage_preserved"] is True
    assert outputs["REAL_OPENAI_API_CALL_COMPLETED"] == "YES"
    assert outputs["REPLAY_INTEGRITY_PRESERVED"] == "YES"
    assert outputs["FAIL_CLOSED_PRESERVED"] == "YES"
    assert outputs["TOKEN_USAGE_RECORDED"] == "YES"
    assert outputs["READY_FOR_PRODUCTION_OPENAI_WORKER_USAGE"] == "YES_SUPERVISED"
