"""Tests for AIGOL_REPLAY_CERTIFICATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import importlib.util
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_certification_runtime import (
    REPLAY_CERTIFICATION_ARTIFACT_V1,
    REPLAY_CERTIFICATION_COMPLETED,
    certify_validated_replay,
    reconstruct_replay_certification_replay,
)
from aigol.runtime.result_validation_runtime import validate_governed_execution_result
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-11T00:00:00Z"


def _load_result_validation_helper():
    helper_path = Path(__file__).with_name("test_result_validation_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("result_validation_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("result validation helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._worker_execution_result


_worker_execution_result = _load_result_validation_helper()


def _result_validation(tmp_path) -> dict:
    result = _worker_execution_result(tmp_path)
    return validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-FOR-REPLAY-CERTIFICATION-000001",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "result_validation",
    )["result_validation_artifact"]


def test_result_validation_generates_replay_certification(tmp_path) -> None:
    validation = _result_validation(tmp_path)
    original_hash = validation["artifact_hash"]
    capture = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-000001",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "replay_certification",
    )
    certification = capture["replay_certification_artifact"]
    reconstructed = reconstruct_replay_certification_replay(tmp_path / "replay_certification")

    assert validation["artifact_hash"] == original_hash
    assert capture["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert capture["replay_certification_completed"] is True
    assert capture["replay_certification_artifact_generated"] is True
    assert certification["artifact_type"] == REPLAY_CERTIFICATION_ARTIFACT_V1
    assert certification["certification_decision"] == "CERTIFIED_FOR_CLOSED_IMPROVEMENT_LOOP"
    assert certification["source_result_validation"] == validation["result_validation_id"]
    assert certification["source_result_validation_hash"] == validation["artifact_hash"]
    assert certification["source_worker_execution"] == validation["source_worker_execution"]
    assert certification["validation_references"]["validation_status"] == validation["validation_status"]
    assert certification["replay_references"] == validation["replay_references"]
    assert certification["lineage_evidence"]["lineage_integrity_validated"] is True
    assert certification["replay_lineage_preserved"] is True
    assert certification["fail_closed_preserved"] is True
    assert certification["deterministic_certification_preserved"] is True
    assert certification["ready_for_closed_improvement_loop"] is True
    assert certification["validation_result_modified"] is False
    assert certification["governance_modified"] is False
    assert certification["worker_invoked"] is False
    assert certification["provider_invoked"] is False
    assert certification["improvement_intent_created"] is False
    assert reconstructed["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["fail_closed_preserved"] is True
    assert reconstructed["ready_for_closed_improvement_loop"] is True


def test_non_result_validation_artifact_fails_closed(tmp_path) -> None:
    validation = _result_validation(tmp_path)
    validation["artifact_type"] = "WORKER_EXECUTION_RESULT_ARTIFACT_V1"
    validation.pop("artifact_hash")
    validation["artifact_hash"] = replay_hash(validation)
    capture = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-WRONG-TYPE",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["certification_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["replay_certification_completed"] is False
    assert capture["replay_certification_artifact_generated"] is True
    assert capture["fail_closed_preserved"] is True


def test_validation_not_ready_for_certification_fails_closed(tmp_path) -> None:
    validation = _result_validation(tmp_path)
    validation["ready_for_replay_certification"] = False
    validation.pop("artifact_hash")
    validation["artifact_hash"] = replay_hash(validation)
    capture = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-NOT-READY",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "not_ready",
    )

    assert capture["certification_status"] == "FAILED_CLOSED"
    assert "certification readiness missing" in capture["failure_reason"]
    assert capture["ready_for_closed_improvement_loop"] is False
    assert capture["fail_closed_preserved"] is True


def test_premature_improvement_loop_entry_fails_closed(tmp_path) -> None:
    validation = _result_validation(tmp_path)
    validation["certification_readiness"]["improvement_loop_entry_allowed"] = True
    validation.pop("artifact_hash")
    validation["artifact_hash"] = replay_hash(validation)
    capture = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-PREMATURE-LOOP",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "premature_loop",
    )

    assert capture["certification_status"] == "FAILED_CLOSED"
    assert "premature improvement loop entry detected" in capture["failure_reason"]
    assert capture["fail_closed_preserved"] is True


def test_reconstruction_detects_corrupt_replay_certification_replay(tmp_path) -> None:
    validation = _result_validation(tmp_path)
    certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-CORRUPT",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_certification",
    )
    path = tmp_path / "corrupt_certification" / "000_replay_certification_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["governance_modified"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_certification_replay(tmp_path / "corrupt_certification")


def test_replay_certification_runtime_has_no_worker_provider_or_mutation_surfaces() -> None:
    import aigol.runtime.replay_certification_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "modify_governance(" not in source
    assert "modify_code(" not in source
    assert "write_text(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
