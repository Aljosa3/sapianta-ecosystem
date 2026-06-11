"""Tests for AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_V1."""

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
    WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1,
    WORKER_INVOCATION_CANDIDATE_CREATED,
    create_worker_invocation_candidate,
    reconstruct_worker_dispatch_to_worker_invocation_governance_replay,
)
from aigol.runtime.worker_request_to_worker_dispatch_governance_runtime import (
    create_worker_dispatch_candidate,
)


CREATED_AT = "2026-06-11T00:00:00Z"
CHAIN_ID = "CHAIN-WORKER-INVOCATION-GOVERNANCE-000001"


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


def _implementation_approval(candidate: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-INVOCATION-GOV-IMPLEMENTATION-000001",
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


def _dispatch_candidate_approval(worker_request: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-INVOCATION-GOV-DISPATCH-000001",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_worker_request": worker_request["worker_request_id"],
        "source_worker_request_hash": worker_request["artifact_hash"],
        "approval_scope": "CREATE_WORKER_DISPATCH_CANDIDATE_ONLY",
        "worker_dispatch_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invocation_candidate_approval(dispatch_candidate: dict, *, granted: bool = True) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-INVOCATION-CANDIDATE-000001",
        "approval_status": APPROVED if granted else "PENDING",
        "approval_granted": granted,
        "source_dispatch_candidate": dispatch_candidate["dispatch_candidate_id"],
        "source_dispatch_candidate_hash": dispatch_candidate["artifact_hash"],
        "approval_scope": "CREATE_WORKER_INVOCATION_CANDIDATE_ONLY",
        "worker_invocation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _dispatch_candidate(tmp_path) -> dict:
    gap = detect_replay_gaps(
        detection_id="GAP-INVOCATION-GOVERNANCE-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap",
        replay_artifacts=[_evidence()],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-INVOCATION-GOVERNANCE-000001",
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
        bridge_id="PPP-CANDIDATE-INVOCATION-GOVERNANCE-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )["ppp_candidate_artifact"]
    implementation_request = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-INVOCATION-GOVERNANCE-000001",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=_implementation_approval(candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "implementation_request",
    )["implementation_request_artifact"]
    worker_request = bridge_implementation_request_to_worker_request(
        bridge_id="WORKER-REQUEST-INVOCATION-GOVERNANCE-000001",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )["worker_request_artifact"]
    return create_worker_dispatch_candidate(
        candidate_id="WORKER-DISPATCH-CANDIDATE-INVOCATION-GOVERNANCE-000001",
        worker_request_artifact=worker_request,
        human_approval_artifact=_dispatch_candidate_approval(worker_request),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dispatch_candidate",
    )["worker_dispatch_candidate_artifact"]


def test_dispatch_candidate_generates_invocation_candidate_without_invocation_or_execution(tmp_path) -> None:
    dispatch_candidate = _dispatch_candidate(tmp_path)
    capture = create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-000001",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_invocation_candidate_approval(dispatch_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_candidate",
    )
    candidate = capture["worker_invocation_candidate_artifact"]
    reconstructed = reconstruct_worker_dispatch_to_worker_invocation_governance_replay(
        tmp_path / "invocation_candidate"
    )

    assert capture["candidate_status"] == WORKER_INVOCATION_CANDIDATE_CREATED
    assert candidate["artifact_type"] == WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1
    assert candidate["source_dispatch_candidate"] == dispatch_candidate["dispatch_candidate_id"]
    assert candidate["source_worker_request"] == dispatch_candidate["source_worker_request"]
    assert candidate["source_implementation_request"] == dispatch_candidate["source_implementation_request"]
    assert candidate["replay_references"] == dispatch_candidate["replay_references"]
    assert candidate["replay_hashes"] == dispatch_candidate["replay_hashes"]
    assert candidate["worker_objective"] == dispatch_candidate["worker_objective"]
    assert candidate["invocation_constraints"]["worker_invocation_allowed"] is False
    assert candidate["invocation_constraints"]["implementation_execution_allowed"] is False
    assert candidate["governance_constraints"]["worker_invocation_requires_separate_governance"] is True
    assert candidate["human_approval_required"] is True
    assert candidate["human_approval_granted"] is True
    assert candidate["replay_lineage_preserved"] is True
    assert candidate["ready_for_worker_execution_governance"] is True
    assert candidate["worker_invoked"] is False
    assert candidate["implementation_executed"] is False
    assert candidate["provider_invoked"] is False
    assert candidate["code_modified"] is False
    assert candidate["governance_modified"] is False
    assert candidate["execution_requested"] is False
    assert reconstructed["candidate_status"] == WORKER_INVOCATION_CANDIDATE_CREATED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["invocation_prevented"] is True
    assert reconstructed["ready_for_worker_execution_governance"] is True


def test_non_dispatch_candidate_artifact_fails_closed(tmp_path) -> None:
    dispatch_candidate = _dispatch_candidate(tmp_path)
    dispatch_candidate["artifact_type"] = "WORKER_REQUEST_ARTIFACT_V1"
    dispatch_candidate.pop("artifact_hash")
    dispatch_candidate["artifact_hash"] = replay_hash(dispatch_candidate)
    capture = create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-WRONG-TYPE",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_invocation_candidate_approval(dispatch_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong_type",
    )

    assert capture["candidate_status"] == "FAILED_CLOSED"
    assert "invalid artifact type" in capture["failure_reason"]
    assert capture["worker_invocation_candidate_generated"] is False
    assert capture["invocation_prevented"] is True


def test_missing_explicit_human_approval_fails_closed(tmp_path) -> None:
    dispatch_candidate = _dispatch_candidate(tmp_path)
    capture = create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-NO-APPROVAL",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_invocation_candidate_approval(dispatch_candidate, granted=False),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_approval",
    )

    assert capture["candidate_status"] == "FAILED_CLOSED"
    assert "explicit human approval required" in capture["failure_reason"]
    assert capture["human_approval_required"] is True
    assert capture["invocation_prevented"] is True


def test_invocation_constraints_cannot_authorize_worker_invocation(tmp_path) -> None:
    dispatch_candidate = _dispatch_candidate(tmp_path)
    capture = create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-OVERSCOPE",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_invocation_candidate_approval(dispatch_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "overscope",
        invocation_constraints={"worker_invocation_allowed": True},
    )

    assert capture["candidate_status"] == "FAILED_CLOSED"
    assert "invocation constraints exceed bridge" in capture["failure_reason"]
    assert capture["invocation_prevented"] is True


def test_reconstruction_detects_corrupt_invocation_candidate_replay(tmp_path) -> None:
    dispatch_candidate = _dispatch_candidate(tmp_path)
    create_worker_invocation_candidate(
        candidate_id="WORKER-INVOCATION-CANDIDATE-CORRUPT",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_invocation_candidate_approval(dispatch_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_candidate",
    )
    path = tmp_path / "corrupt_candidate" / "000_worker_invocation_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_dispatch_to_worker_invocation_governance_replay(tmp_path / "corrupt_candidate")


def test_worker_dispatch_to_worker_invocation_governance_has_no_invocation_execution_or_mutation_surfaces() -> None:
    import aigol.runtime.worker_dispatch_to_worker_invocation_governance_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "dispatch_worker(" not in source
    assert "start_execution(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "write_text(" not in source
    assert "subprocess" not in source
    assert "os.system" not in source
