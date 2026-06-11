"""Tests for AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    PPP_CANDIDATE_ARTIFACT_V1,
    PPP_CANDIDATE_CREATED,
    reconstruct_improvement_intent_to_ppp_bridge_replay,
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-IMPROVEMENT-PPP-BRIDGE-000001"


def _evidence(evidence_id: str = "VALIDATION-FAIL") -> dict:
    payload = {"status": "FAILED", "execution_id": "EXECUTION-000001"}
    return {
        "evidence_id": evidence_id,
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": f"replay/{evidence_id}.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "Execution validation failed.",
        "expected_condition": "Execution validation should pass.",
        "confidence": "DETERMINISTIC",
        "status": "FAILED",
    }


def _intent_artifact(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-PPP-BRIDGE-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-PPP-BRIDGE-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        affected_worker_family="REGRESSION_GAP_ANALYSIS",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
    )
    return intent["improvement_intent_artifact"]


def test_certified_improvement_intent_bridges_to_ppp_candidate_without_implementation(tmp_path) -> None:
    intent = _intent_artifact(tmp_path)
    capture = bridge_improvement_intent_to_ppp_candidate(
        bridge_id="IMPROVEMENT-PPP-BRIDGE-000001",
        improvement_intent_artifact=intent,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )
    candidate = capture["ppp_candidate_artifact"]
    reconstructed = reconstruct_improvement_intent_to_ppp_bridge_replay(tmp_path / "bridge")

    assert capture["candidate_status"] == PPP_CANDIDATE_CREATED
    assert candidate["artifact_type"] == PPP_CANDIDATE_ARTIFACT_V1
    assert candidate["source_improvement_intent"] == intent["improvement_intent_id"]
    assert candidate["source_improvement_intent_hash"] == intent["artifact_hash"]
    assert candidate["source_gap_reference"] == intent["gap_reference"]
    assert candidate["source_gap_hash"] == intent["gap_hash"]
    assert candidate["source_replay_references"] == intent["source_replay_reference"]
    assert candidate["proposal_summary"] == intent["intent_summary"]
    assert candidate["affected_runtime"] == "GOVERNANCE"
    assert candidate["affected_lifecycle_stage"] == "RESULT_VALIDATED"
    assert candidate["governance_classification"]["source"] == "CERTIFIED_IMPROVEMENT_INTENT"
    assert candidate["human_approval_requirement"] == "MANDATORY"
    assert candidate["human_approval_required"] is True
    assert candidate["approval_granted"] is False
    assert candidate["replay_lineage_preserved"] is True
    assert candidate["certification_status"] == "CERTIFIED_IMPROVEMENT_INTENT_ACCEPTED"
    assert candidate["proposal_created"] is False
    assert candidate["ppp_invoked"] is False
    assert candidate["provider_invoked"] is False
    assert candidate["worker_invoked"] is False
    assert candidate["authorization_created"] is False
    assert candidate["implementation_authorized"] is False
    assert candidate["implementation_applied"] is False
    assert candidate["code_modified"] is False
    assert candidate["governance_modified"] is False
    assert candidate["execution_requested"] is False
    assert reconstructed["candidate_status"] == PPP_CANDIDATE_CREATED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["implementation_prevented"] is True
    assert reconstructed["ready_for_governed_implementation_requests"] is True


def test_bridge_fails_closed_for_non_improvement_intent_artifact(tmp_path) -> None:
    artifact = _intent_artifact(tmp_path)
    artifact["artifact_type"] = "COGNITION_ROUTED_INTENT_ARTIFACT_V1"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = bridge_improvement_intent_to_ppp_candidate(
        bridge_id="IMPROVEMENT-PPP-BRIDGE-WRONG-TYPE",
        improvement_intent_artifact=artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["candidate_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["ppp_candidate_artifact_generated"] is False
    assert capture["human_approval_required"] is True
    assert capture["implementation_prevented"] is True


def test_bridge_fails_closed_when_human_review_is_not_required(tmp_path) -> None:
    artifact = _intent_artifact(tmp_path)
    artifact["human_review_required"] = False
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = bridge_improvement_intent_to_ppp_candidate(
        bridge_id="IMPROVEMENT-PPP-BRIDGE-NO-HUMAN-REVIEW",
        improvement_intent_artifact=artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_human_review",
    )

    assert capture["candidate_status"] == "FAILED_CLOSED"
    assert "human review required" in capture["failure_reason"]
    assert capture["ppp_candidate_artifact"]["authorization_created"] is False


def test_reconstruction_detects_corrupt_ppp_candidate_replay(tmp_path) -> None:
    bridge_improvement_intent_to_ppp_candidate(
        bridge_id="IMPROVEMENT-PPP-BRIDGE-CORRUPT",
        improvement_intent_artifact=_intent_artifact(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_bridge",
    )
    path = tmp_path / "corrupt_bridge" / "000_ppp_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["implementation_authorized"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_intent_to_ppp_bridge_replay(tmp_path / "corrupt_bridge")


def test_improvement_intent_to_ppp_bridge_has_no_execution_or_authorization_surfaces() -> None:
    import aigol.runtime.improvement_intent_to_ppp_bridge_runtime as runtime

    source = inspect.getsource(runtime)

    assert "start_execution(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "authorize_execution" not in source
    assert "approval_granted = True" not in source
    assert "implementation_authorized = True" not in source
    assert "subprocess" not in source
    assert "os.system" not in source
