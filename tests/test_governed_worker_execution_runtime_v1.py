"""Tests for AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    create_governed_implementation_request,
)
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    WORKER_EXECUTION_RESULT_ARTIFACT_V1,
    reconstruct_governed_worker_execution_replay,
    run_governed_worker_execution,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    bridge_implementation_request_to_worker_request,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
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
CHAIN_ID = "CHAIN-GOVERNED-WORKER-EXECUTION-000001"


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


def _execution_approval(execution_candidate: dict, *, granted: bool = True) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-GOVERNED-WORKER-EXECUTION-000001",
        "approval_status": APPROVED if granted else "PENDING",
        "approval_granted": granted,
        "source_execution_candidate": execution_candidate["execution_candidate_id"],
        "source_execution_candidate_hash": execution_candidate["artifact_hash"],
        "approval_scope": "RUN_GOVERNED_WORKER_EXECUTION_ONLY",
        "worker_execution_allowed": True,
        "implementation_result_creation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_candidate(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-GOVERNED-WORKER-EXECUTION-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-GOVERNED-WORKER-EXECUTION-000001",
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
        bridge_id="PPP-CANDIDATE-GOVERNED-WORKER-EXECUTION-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )["ppp_candidate_artifact"]
    implementation_request = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-GOVERNED-WORKER-EXECUTION-000001",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-GOVERNED-WORKER-EXECUTION-IMPLEMENTATION-000001",
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
        bridge_id="WORKER-REQUEST-GOVERNED-WORKER-EXECUTION-000001",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )["worker_request_artifact"]
    dispatch_candidate = create_worker_dispatch_candidate(
        candidate_id="WORKER-DISPATCH-CANDIDATE-GOVERNED-WORKER-EXECUTION-000001",
        worker_request_artifact=worker_request,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-GOVERNED-WORKER-EXECUTION-DISPATCH-000001",
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
        candidate_id="WORKER-INVOCATION-CANDIDATE-GOVERNED-WORKER-EXECUTION-000001",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-GOVERNED-WORKER-EXECUTION-INVOCATION-000001",
            source_dispatch_candidate=dispatch_candidate["dispatch_candidate_id"],
            source_dispatch_candidate_hash=dispatch_candidate["artifact_hash"],
            approval_scope="CREATE_WORKER_INVOCATION_CANDIDATE_ONLY",
            worker_invocation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_candidate",
    )["worker_invocation_candidate_artifact"]
    return create_worker_execution_candidate(
        candidate_id="WORKER-EXECUTION-CANDIDATE-GOVERNED-WORKER-EXECUTION-000001",
        invocation_candidate_artifact=invocation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-GOVERNED-WORKER-EXECUTION-CANDIDATE-000001",
            source_invocation_candidate=invocation_candidate["invocation_candidate_id"],
            source_invocation_candidate_hash=invocation_candidate["artifact_hash"],
            approval_scope="CREATE_WORKER_EXECUTION_CANDIDATE_ONLY",
            worker_execution_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution_candidate",
    )["worker_execution_candidate_artifact"]


def test_approved_execution_candidate_runs_governed_worker_execution_and_generates_result(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_execution_approval(execution_candidate),
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "governed_worker_execution",
        validation_inputs={"operator_review": "approved"},
    )
    result = capture["worker_execution_result_artifact"]
    reconstructed = reconstruct_governed_worker_execution_replay(tmp_path / "governed_worker_execution")

    assert capture["execution_status"] == WORKER_EXECUTION_COMPLETED
    assert capture["worker_execution_completed"] is True
    assert capture["execution_result_artifact_generated"] is True
    assert result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1
    assert result["execution_outcome"] == "COMPLETED"
    assert result["source_execution_candidate"] == execution_candidate["execution_candidate_id"]
    assert result["source_invocation_candidate"] == execution_candidate["source_invocation_candidate"]
    assert result["source_dispatch_candidate"] == execution_candidate["source_dispatch_candidate"]
    assert result["source_worker_request"] == execution_candidate["source_worker_request"]
    assert result["source_implementation_request"] == execution_candidate["source_implementation_request"]
    assert result["replay_references"] == execution_candidate["replay_references"]
    assert result["execution_objective"] == execution_candidate["execution_objective"]
    assert result["worker_evidence"]["governed_execution"] is True
    assert result["worker_evidence"]["external_provider_invoked"] is False
    assert result["worker_evidence"]["subprocess_invoked"] is False
    assert result["validation_inputs"]["validation_performed"] is True
    assert result["worker_executed"] is True
    assert result["implementation_result_created"] is False
    assert result["code_modified"] is False
    assert result["governance_modified"] is False
    assert result["provider_invoked"] is False
    assert result["replay_lineage_preserved"] is True
    assert result["fail_closed_preserved"] is True
    assert result["ready_for_result_validation_runtime"] is True
    assert reconstructed["execution_status"] == WORKER_EXECUTION_COMPLETED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["fail_closed_preserved"] is True
    assert reconstructed["ready_for_result_validation_runtime"] is True
    assert reconstructed["implementation_result_created"] is False


def test_non_execution_candidate_artifact_fails_closed(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    execution_candidate["artifact_type"] = "WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1"
    execution_candidate.pop("artifact_hash")
    execution_candidate["artifact_hash"] = replay_hash(execution_candidate)
    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-WRONG-TYPE",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_execution_approval(execution_candidate),
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["worker_execution_completed"] is False
    assert capture["execution_result_artifact_generated"] is True
    assert capture["fail_closed_preserved"] is True


def test_missing_explicit_human_execution_approval_fails_closed(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-NO-APPROVAL",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_execution_approval(execution_candidate, granted=False),
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "no_approval",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert "explicit human approval required" in capture["failure_reason"]
    assert capture["worker_execution_completed"] is False
    assert capture["fail_closed_preserved"] is True


def test_approval_cannot_authorize_implementation_result_creation(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    approval = _execution_approval(execution_candidate)
    approval["implementation_result_creation_allowed"] = True
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)
    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-OVERSCOPE",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=approval,
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "overscope",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert "approval scope exceeds execution" in capture["failure_reason"]
    assert capture["fail_closed_preserved"] is True


def test_reconstruction_detects_corrupt_governed_worker_execution_replay(tmp_path) -> None:
    execution_candidate = _execution_candidate(tmp_path)
    run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-CORRUPT",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_execution_approval(execution_candidate),
        executed_by="HUMAN_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_execution",
    )
    path = tmp_path / "corrupt_execution" / "001_worker_execution_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["code_modified"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_governed_worker_execution_replay(tmp_path / "corrupt_execution")


def test_governed_worker_execution_runtime_has_no_provider_subprocess_code_or_governance_mutation_surfaces() -> None:
    import aigol.runtime.governed_worker_execution_runtime as runtime

    source = inspect.getsource(runtime)

    assert "import subprocess" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "create_implementation_result(" not in source
    assert "modify_governance(" not in source
    assert "modify_code(" not in source
    assert "write_text(" not in source
