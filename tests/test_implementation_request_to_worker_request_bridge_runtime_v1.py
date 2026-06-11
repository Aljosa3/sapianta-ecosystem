"""Tests for AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    create_governed_implementation_request,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    WORKER_REQUEST_ARTIFACT_V1,
    WORKER_REQUEST_CREATED,
    bridge_implementation_request_to_worker_request,
    reconstruct_implementation_request_to_worker_request_bridge_replay,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-IMPLEMENTATION-WORKER-BRIDGE-000001"


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


def _human_approval(candidate: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-WORKER-BRIDGE-000001",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_ppp_candidate": candidate["ppp_candidate_id"],
        "source_ppp_candidate_hash": candidate["artifact_hash"],
        "approval_scope": "CREATE_IMPLEMENTATION_REQUEST_ONLY",
        "implementation_execution_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _implementation_request(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-WORKER-BRIDGE-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-WORKER-BRIDGE-000001",
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
        bridge_id="PPP-CANDIDATE-WORKER-BRIDGE-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )["ppp_candidate_artifact"]
    request = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-WORKER-BRIDGE-000001",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_human_approval(candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "implementation_request",
    )
    return request["implementation_request_artifact"]


def test_implementation_request_generates_worker_request_without_execution_or_dispatch(tmp_path) -> None:
    implementation_request = _implementation_request(tmp_path)
    capture = bridge_implementation_request_to_worker_request(
        bridge_id="IMPLEMENTATION-WORKER-BRIDGE-000001",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )
    worker_request = capture["worker_request_artifact"]
    reconstructed = reconstruct_implementation_request_to_worker_request_bridge_replay(
        tmp_path / "worker_request"
    )

    assert capture["request_status"] == WORKER_REQUEST_CREATED
    assert worker_request["artifact_type"] == WORKER_REQUEST_ARTIFACT_V1
    assert worker_request["source_implementation_request"] == implementation_request["implementation_request_id"]
    assert worker_request["source_ppp_candidate"] == implementation_request["source_ppp_candidate"]
    assert worker_request["source_improvement_intent"] == implementation_request["source_improvement_intent"]
    assert worker_request["source_gap_artifact"] == implementation_request["source_gap_artifact"]
    assert worker_request["replay_references"] == implementation_request["replay_references"]
    assert worker_request["worker_objective"] == implementation_request["implementation_objective"]
    assert worker_request["worker_constraints"]["dispatch_allowed"] is False
    assert worker_request["worker_constraints"]["worker_invocation_allowed"] is False
    assert worker_request["governance_requirements"]["dispatch_requires_separate_governance"] is True
    assert worker_request["human_approval_required"] is True
    assert worker_request["replay_lineage_preserved"] is True
    assert worker_request["ready_for_worker_dispatch_governance"] is True
    assert worker_request["worker_dispatched"] is False
    assert worker_request["worker_invoked"] is False
    assert worker_request["implementation_executed"] is False
    assert worker_request["code_modified"] is False
    assert worker_request["execution_requested"] is False
    assert reconstructed["request_status"] == WORKER_REQUEST_CREATED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["execution_prevented"] is True
    assert reconstructed["ready_for_worker_dispatch_governance"] is True


def test_non_implementation_request_artifact_fails_closed(tmp_path) -> None:
    implementation_request = _implementation_request(tmp_path)
    implementation_request["artifact_type"] = "PPP_CANDIDATE_ARTIFACT_V1"
    implementation_request.pop("artifact_hash")
    implementation_request["artifact_hash"] = replay_hash(implementation_request)
    capture = bridge_implementation_request_to_worker_request(
        bridge_id="IMPLEMENTATION-WORKER-BRIDGE-WRONG-TYPE",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["worker_request_artifact_generated"] is False


def test_broken_human_approval_chain_fails_closed(tmp_path) -> None:
    implementation_request = _implementation_request(tmp_path)
    implementation_request["human_approval_granted"] = False
    implementation_request.pop("artifact_hash")
    implementation_request["artifact_hash"] = replay_hash(implementation_request)
    capture = bridge_implementation_request_to_worker_request(
        bridge_id="IMPLEMENTATION-WORKER-BRIDGE-NO-APPROVAL",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_approval",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "human approval chain required" in capture["failure_reason"]
    assert capture["human_approval_required"] is True
    assert capture["execution_prevented"] is True


def test_reconstruction_detects_corrupt_worker_request_replay(tmp_path) -> None:
    bridge_implementation_request_to_worker_request(
        bridge_id="IMPLEMENTATION-WORKER-BRIDGE-CORRUPT",
        implementation_request_artifact=_implementation_request(tmp_path),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_worker_request",
    )
    path = tmp_path / "corrupt_worker_request" / "000_worker_request_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_implementation_request_to_worker_request_bridge_replay(
            tmp_path / "corrupt_worker_request"
        )


def test_implementation_request_to_worker_request_bridge_has_no_dispatch_invocation_execution_or_mutation_surfaces() -> None:
    import aigol.runtime.implementation_request_to_worker_request_bridge_runtime as runtime

    source = inspect.getsource(runtime)

    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "write_text(" not in source
    assert "subprocess" not in source
    assert "os.system" not in source
