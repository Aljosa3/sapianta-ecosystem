"""Tests for AIGOL_RESULT_VALIDATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    create_governed_implementation_request,
)
from aigol.runtime.governed_worker_execution_runtime import run_governed_worker_execution
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    bridge_implementation_request_to_worker_request,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.result_validation_runtime import (
    RESULT_VALIDATION_ARTIFACT_V1,
    RESULT_VALIDATION_COMPLETED,
    reconstruct_result_validation_replay,
    validate_governed_execution_result,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_dispatch_to_worker_invocation_governance_runtime import (
    create_worker_invocation_candidate,
)
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    create_worker_execution_candidate,
)
from aigol.runtime.worker_request_to_worker_dispatch_governance_runtime import (
    create_worker_dispatch_candidate,
)


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-RESULT-VALIDATION-000001"


def _evidence() -> dict:
    payload = {"status": "FAILED", "execution_id": "EXECUTION-000001"}
    return {
        "evidence_id": "VALIDATION-FAIL",
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": "replay/VALIDATION-FAIL.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "Execution validation failed.",
        "expected_condition": "Execution validation should pass.",
        "confidence": "DETERMINISTIC",
        "status": "FAILED",
    }


def _approval(**fields) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_status": APPROVED,
        "approval_granted": True,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact.update(fields)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_execution_result(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-RESULT-VALIDATION-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-RESULT-VALIDATION-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        affected_worker_family="REGRESSION_GAP_ANALYSIS",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
    )
    candidate = bridge_improvement_intent_to_ppp_candidate(
        bridge_id="PPP-CANDIDATE-RESULT-VALIDATION-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )["ppp_candidate_artifact"]
    implementation_request = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-RESULT-VALIDATION-000001",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RESULT-VALIDATION-IMPLEMENTATION-000001",
            source_ppp_candidate=candidate["ppp_candidate_id"],
            source_ppp_candidate_hash=candidate["artifact_hash"],
            approval_scope="CREATE_IMPLEMENTATION_REQUEST_ONLY",
            implementation_execution_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "implementation_request",
    )["implementation_request_artifact"]
    worker_request = bridge_implementation_request_to_worker_request(
        bridge_id="WORKER-REQUEST-RESULT-VALIDATION-000001",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )["worker_request_artifact"]
    dispatch_candidate = create_worker_dispatch_candidate(
        candidate_id="WORKER-DISPATCH-CANDIDATE-RESULT-VALIDATION-000001",
        worker_request_artifact=worker_request,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RESULT-VALIDATION-DISPATCH-000001",
            source_worker_request=worker_request["worker_request_id"],
            source_worker_request_hash=worker_request["artifact_hash"],
            approval_scope="CREATE_WORKER_DISPATCH_CANDIDATE_ONLY",
            worker_dispatch_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dispatch_candidate",
    )["worker_dispatch_candidate_artifact"]
    invocation_candidate = create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-RESULT-VALIDATION-000001",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RESULT-VALIDATION-INVOCATION-000001",
            source_dispatch_candidate=dispatch_candidate["dispatch_candidate_id"],
            source_dispatch_candidate_hash=dispatch_candidate["artifact_hash"],
            approval_scope="CREATE_WORKER_INVOCATION_CANDIDATE_ONLY",
            worker_invocation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_candidate",
    )["worker_invocation_candidate_artifact"]
    execution_candidate = create_worker_execution_candidate(
        candidate_id="WORKER-EXECUTION-CANDIDATE-RESULT-VALIDATION-000001",
        invocation_candidate_artifact=invocation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RESULT-VALIDATION-EXECUTION-CANDIDATE-000001",
            source_invocation_candidate=invocation_candidate["invocation_candidate_id"],
            source_invocation_candidate_hash=invocation_candidate["artifact_hash"],
            approval_scope="CREATE_WORKER_EXECUTION_CANDIDATE_ONLY",
            worker_execution_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution_candidate",
    )["worker_execution_candidate_artifact"]
    return run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-RESULT-VALIDATION-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RESULT-VALIDATION-EXECUTION-000001",
            source_execution_candidate=execution_candidate["execution_candidate_id"],
            source_execution_candidate_hash=execution_candidate["artifact_hash"],
            approval_scope="RUN_GOVERNED_WORKER_EXECUTION_ONLY",
            worker_execution_allowed=True,
            implementation_result_creation_allowed=False,
        ),
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "governed_worker_execution",
        validation_inputs={"operator_review": "approved"},
    )["worker_execution_result_artifact"]


def test_execution_result_validates_to_replay_certification_readiness(tmp_path) -> None:
    result = _worker_execution_result(tmp_path)
    original_hash = result["artifact_hash"]
    capture = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-000001",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "result_validation",
    )
    validation = capture["result_validation_artifact"]
    reconstructed = reconstruct_result_validation_replay(tmp_path / "result_validation")

    assert result["artifact_hash"] == original_hash
    assert capture["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert capture["result_validation_completed"] is True
    assert capture["result_validation_artifact_generated"] is True
    assert validation["artifact_type"] == RESULT_VALIDATION_ARTIFACT_V1
    assert validation["source_worker_execution"] == result["worker_execution_id"]
    assert validation["source_worker_execution_hash"] == result["artifact_hash"]
    assert validation["source_execution_candidate"] == result["source_execution_candidate"]
    assert validation["validation_evidence"]["execution_outcome"] == "COMPLETED"
    assert validation["validation_evidence"]["governance_constraints_validated"] is True
    assert validation["validation_evidence"]["lineage_integrity_validated"] is True
    assert validation["replay_references"] == result["replay_references"]
    assert validation["certification_readiness"]["ready_for_replay_certification"] is True
    assert validation["certification_readiness"]["improvement_loop_entry_allowed"] is False
    assert validation["replay_lineage_preserved"] is True
    assert validation["fail_closed_preserved"] is True
    assert validation["deterministic_validation_preserved"] is True
    assert validation["ready_for_replay_certification"] is True
    assert validation["execution_result_modified"] is False
    assert validation["governance_modified"] is False
    assert validation["worker_invoked"] is False
    assert validation["provider_invoked"] is False
    assert reconstructed["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["fail_closed_preserved"] is True
    assert reconstructed["ready_for_replay_certification"] is True


def test_non_worker_execution_result_artifact_fails_closed(tmp_path) -> None:
    result = _worker_execution_result(tmp_path)
    result["artifact_type"] = "WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1"
    result.pop("artifact_hash")
    result["artifact_hash"] = replay_hash(result)
    capture = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-WRONG-TYPE",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["validation_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["result_validation_completed"] is False
    assert capture["result_validation_artifact_generated"] is True
    assert capture["fail_closed_preserved"] is True


def test_invalid_execution_outcome_fails_closed(tmp_path) -> None:
    result = _worker_execution_result(tmp_path)
    result["execution_outcome"] = "PARTIAL"
    result.pop("artifact_hash")
    result["artifact_hash"] = replay_hash(result)
    capture = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-BAD-OUTCOME",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "bad_outcome",
    )

    assert capture["validation_status"] == "FAILED_CLOSED"
    assert "execution outcome invalid" in capture["failure_reason"]
    assert capture["fail_closed_preserved"] is True


def test_reconstruction_detects_corrupt_result_validation_replay(tmp_path) -> None:
    result = _worker_execution_result(tmp_path)
    validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-CORRUPT",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_validation",
    )
    path = tmp_path / "corrupt_validation" / "001_result_validation_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["governance_modified"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_result_validation_replay(tmp_path / "corrupt_validation")


def test_result_validation_runtime_has_no_worker_provider_or_mutation_surfaces() -> None:
    import aigol.runtime.result_validation_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "modify_governance(" not in source
    assert "modify_code(" not in source
    assert "write_text(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
