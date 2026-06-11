"""Tests for AIGOL_GOVERNED_IMPLEMENTATION_REQUEST_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_CREATED,
    create_governed_implementation_request,
    reconstruct_governed_implementation_request_replay,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-GOVERNED-IMPLEMENTATION-REQUEST-000001"


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


def _ppp_candidate(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-IMPLEMENTATION-REQUEST-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-IMPLEMENTATION-REQUEST-000001",
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
        bridge_id="PPP-CANDIDATE-IMPLEMENTATION-REQUEST-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )
    return candidate["ppp_candidate_artifact"]


def _human_approval(candidate: dict, *, status: str = APPROVED, granted: bool = True) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-IMPLEMENTATION-REQUEST-000001",
        "approval_status": status,
        "approval_granted": granted,
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


def test_approved_ppp_candidate_generates_implementation_request_without_execution(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    approval = _human_approval(candidate)
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-000001",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=approval,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "implementation_request",
    )
    request = capture["implementation_request_artifact"]
    reconstructed = reconstruct_governed_implementation_request_replay(tmp_path / "implementation_request")

    assert capture["request_status"] == IMPLEMENTATION_REQUEST_CREATED
    assert request["artifact_type"] == IMPLEMENTATION_REQUEST_ARTIFACT_V1
    assert request["source_ppp_candidate"] == candidate["ppp_candidate_id"]
    assert request["source_ppp_candidate_hash"] == candidate["artifact_hash"]
    assert request["source_improvement_intent"] == candidate["source_improvement_intent"]
    assert request["source_gap_artifact"] == candidate["source_gap_reference"]
    assert request["replay_references"] == candidate["source_replay_references"]
    assert request["implementation_objective"] == candidate["proposal_summary"]
    assert request["implementation_scope"]["allowed_next_step"] == "WORKER_REQUEST_GENERATION"
    assert request["governance_constraints"]["human_authority_required"] is True
    assert request["governance_constraints"]["implementation_execution_allowed"] is False
    assert request["human_approval_required"] is True
    assert request["human_approval_granted"] is True
    assert request["replay_lineage_preserved"] is True
    assert request["ready_for_worker_request_generation"] is True
    assert request["implementation_executed"] is False
    assert request["worker_invoked"] is False
    assert request["provider_invoked"] is False
    assert request["code_modified"] is False
    assert request["governance_modified"] is False
    assert request["authorization_created"] is False
    assert request["execution_requested"] is False
    assert reconstructed["request_status"] == IMPLEMENTATION_REQUEST_CREATED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["implementation_prevented"] is True
    assert reconstructed["ready_for_worker_request_generation"] is True


def test_missing_explicit_human_approval_fails_closed(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    approval = _human_approval(candidate, status="PENDING", granted=False)
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-NO-APPROVAL",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=approval,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_approval",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "explicit human approval required" in capture["failure_reason"]
    assert capture["implementation_request_artifact_generated"] is False
    assert capture["human_approval_required"] is True
    assert capture["implementation_prevented"] is True


def test_non_ppp_candidate_artifact_fails_closed(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    candidate["artifact_type"] = "IMPROVEMENT_INTENT_ARTIFACT_V1"
    candidate.pop("artifact_hash")
    candidate["artifact_hash"] = replay_hash(candidate)
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-WRONG-TYPE",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_human_approval(candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_implementation_request_replay(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-CORRUPT",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_human_approval(candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_request",
    )
    path = tmp_path / "corrupt_request" / "000_implementation_request_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_governed_implementation_request_replay(tmp_path / "corrupt_request")


def test_governed_implementation_request_runtime_has_no_execution_provider_worker_or_mutation_surfaces() -> None:
    import aigol.runtime.governed_implementation_request_runtime as runtime

    source = inspect.getsource(runtime)

    assert "start_execution(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "write_text(" not in source
    assert "subprocess" not in source
    assert "os.system" not in source
