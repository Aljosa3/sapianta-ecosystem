"""Certification tests for AIGOL_REPLAY_DERIVED_IMPROVEMENT_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_CREATED,
    create_governed_implementation_request,
)
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    run_governed_worker_execution,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    WORKER_REQUEST_CREATED,
    bridge_implementation_request_to_worker_request,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    PPP_CANDIDATE_CREATED,
    bridge_improvement_intent_to_ppp_candidate,
)
from aigol.runtime.replay_derived_improvement_certification_v1 import (
    MILESTONE_ID,
    run_replay_derived_improvement_certification_v1,
)
from aigol.runtime.replay_certification_runtime import (
    REPLAY_CERTIFICATION_COMPLETED,
    certify_validated_replay,
)
from aigol.runtime.replay_gap_detection_runtime import GAPS_DETECTED, detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import (
    IMPROVEMENT_INTENT_CREATED,
    create_improvement_intent_from_replay_gap,
)
from aigol.runtime.result_validation_runtime import (
    RESULT_VALIDATION_COMPLETED,
    validate_governed_execution_result,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from aigol.runtime.worker_dispatch_to_worker_invocation_governance_runtime import (
    WORKER_INVOCATION_CANDIDATE_CREATED,
    create_worker_invocation_candidate,
)
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    WORKER_EXECUTION_CANDIDATE_CREATED,
    create_worker_execution_candidate,
)
from aigol.runtime.worker_request_to_worker_dispatch_governance_runtime import (
    WORKER_DISPATCH_CANDIDATE_CREATED,
    create_worker_dispatch_candidate,
)

CREATED_AT = "2026-06-13T00:00:00Z"
CHAIN_ID = "CHAIN-REPLAY-DERIVED-IMPROVEMENT-CERTIFICATION-000001"


def _failed_execution_replay() -> dict:
    payload = {
        "execution_id": "EXECUTION-REPLAY-DERIVED-IMPROVEMENT-000001",
        "execution_status": "COMPLETED",
        "result_validation_status": "FAILED",
        "worker_execution_requested_by_replay_improvement": False,
        "provider_change_requested": False,
    }
    return {
        "evidence_id": "VALIDATION-FAIL-REPLAY-DERIVED-IMPROVEMENT-000001",
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": "replay/validation-fail-replay-derived-improvement-000001.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "Replay records failed result validation.",
        "expected_condition": "Replay should record validated execution result.",
        "confidence": "DETERMINISTIC",
        "status": "FAILED",
    }


def _approval(**fields: object) -> dict:
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


def _gap_capture(tmp_path) -> dict:
    return detect_replay_gaps(
        detection_id="GAP-REPLAY-DERIVED-IMPROVEMENT-000001",
        replay_artifacts=[_failed_execution_replay()],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap_detection",
        domain_id="AIGOL_CORE",
    )


def _intent_capture(tmp_path, gap: dict | None = None) -> dict:
    gap = gap or _gap_capture(tmp_path)
    return create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-REPLAY-DERIVED-CERTIFICATION-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "improvement_intent",
        affected_layer="GOVERNANCE",
        affected_worker_family="REPLAY_DERIVED_IMPROVEMENT",
    )


def _ppp_candidate(tmp_path, intent: dict | None = None) -> dict:
    intent = intent or _intent_capture(tmp_path)["improvement_intent_artifact"]
    return bridge_improvement_intent_to_ppp_candidate(
        bridge_id="PPP-CANDIDATE-REPLAY-DERIVED-CERTIFICATION-000001",
        improvement_intent_artifact=intent,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ppp_candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )["ppp_candidate_artifact"]


def _implementation_request(tmp_path, ppp_candidate: dict) -> dict:
    return create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-REPLAY-DERIVED-CERTIFICATION-000001",
        ppp_candidate_artifact=ppp_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-IMPLEMENTATION-000001",
            source_ppp_candidate=ppp_candidate["ppp_candidate_id"],
            source_ppp_candidate_hash=ppp_candidate["artifact_hash"],
            approval_scope="CREATE_IMPLEMENTATION_REQUEST_ONLY",
            implementation_execution_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "implementation_request",
    )["implementation_request_artifact"]


def _worker_candidates(tmp_path, implementation_request: dict) -> dict:
    worker_request = bridge_implementation_request_to_worker_request(
        bridge_id="WORKER-REQUEST-REPLAY-DERIVED-CERTIFICATION-000001",
        implementation_request_artifact=implementation_request,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )["worker_request_artifact"]
    dispatch_candidate = create_worker_dispatch_candidate(
        candidate_id="WORKER-DISPATCH-CANDIDATE-REPLAY-DERIVED-CERTIFICATION-000001",
        worker_request_artifact=worker_request,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-DISPATCH-000001",
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
        candidate_id="WORKER-INVOCATION-CANDIDATE-REPLAY-DERIVED-CERTIFICATION-000001",
        dispatch_candidate_artifact=dispatch_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-INVOCATION-000001",
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
        candidate_id="WORKER-EXECUTION-CANDIDATE-REPLAY-DERIVED-CERTIFICATION-000001",
        invocation_candidate_artifact=invocation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-EXECUTION-CANDIDATE-000001",
            source_invocation_candidate=invocation_candidate["invocation_candidate_id"],
            source_invocation_candidate_hash=invocation_candidate["artifact_hash"],
            approval_scope="CREATE_WORKER_EXECUTION_CANDIDATE_ONLY",
            worker_execution_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution_candidate",
    )["worker_execution_candidate_artifact"]
    return {
        "worker_request": worker_request,
        "dispatch_candidate": dispatch_candidate,
        "invocation_candidate": invocation_candidate,
        "execution_candidate": execution_candidate,
    }


def test_replay_failure_gap_detection_and_improvement_intent_are_non_authoritative(tmp_path) -> None:
    gap = _gap_capture(tmp_path)
    detection = gap["gap_detection_artifact"]
    classification = gap["gap_classification_artifact"]
    intent = _intent_capture(tmp_path, gap)["improvement_intent_artifact"]

    assert detection["detection_status"] == GAPS_DETECTED
    assert "VALIDATION_GAP" in detection["gap_categories"]
    assert detection["improvement_intent_allowed"] is True
    assert classification["improvement_intent_allowed"] is True
    assert detection["proposal_created"] is False
    assert detection["ppp_invoked"] is False
    assert detection["worker_invoked"] is False
    assert detection["execution_requested"] is False

    assert intent["intent_status"] == IMPROVEMENT_INTENT_CREATED
    assert intent["intent_source"] == "REPLAY_GAP_DETECTION"
    assert intent["ppp_eligible"] is True
    assert intent["human_review_required"] is True
    assert intent["proposal_created"] is False
    assert intent["ppp_invoked"] is False
    assert intent["worker_invoked"] is False
    assert intent["execution_requested"] is False
    assert intent["implementation_authorized"] is False
    assert intent["self_modification_authority"] is False


def test_improvement_intent_without_human_approval_does_not_execute(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    pending_approval = _approval(
        approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-PENDING-000001",
        approval_status="PENDING",
        approval_granted=False,
        source_ppp_candidate=candidate["ppp_candidate_id"],
        source_ppp_candidate_hash=candidate["artifact_hash"],
        approval_scope="CREATE_IMPLEMENTATION_REQUEST_ONLY",
        implementation_execution_allowed=False,
    )
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-REPLAY-DERIVED-NO-APPROVAL",
        ppp_candidate_artifact=candidate,
        human_approval_artifact=pending_approval,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_approval",
    )

    assert candidate["candidate_status"] == PPP_CANDIDATE_CREATED
    assert candidate["human_approval_required"] is True
    assert candidate["approval_granted"] is False
    assert candidate["worker_invoked"] is False
    assert candidate["execution_requested"] is False
    assert capture["request_status"] == "FAILED_CLOSED"
    assert capture["implementation_request_artifact_generated"] is False
    assert capture["implementation_prevented"] is True
    assert capture["implementation_request_artifact"]["worker_invoked"] is False
    assert capture["implementation_request_artifact"]["provider_invoked"] is False
    assert capture["implementation_request_artifact"]["execution_requested"] is False


def test_approved_replay_derived_improvement_reaches_worker_candidates_validation_and_replay(tmp_path) -> None:
    candidate = _ppp_candidate(tmp_path)
    implementation_request = _implementation_request(tmp_path, candidate)
    worker_candidates = _worker_candidates(tmp_path, implementation_request)
    execution_candidate = worker_candidates["execution_candidate"]
    execution = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-REPLAY-DERIVED-CERTIFICATION-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-FINAL-EXECUTION-000001",
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
    )
    validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-REPLAY-DERIVED-CERTIFICATION-000001",
        worker_execution_result_artifact=execution["worker_execution_result_artifact"],
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-REPLAY-DERIVED-IMPROVEMENT-000001",
        result_validation_artifact=validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "replay_certification",
    )

    worker_request = worker_candidates["worker_request"]
    dispatch_candidate = worker_candidates["dispatch_candidate"]
    invocation_candidate = worker_candidates["invocation_candidate"]

    assert candidate["candidate_status"] == PPP_CANDIDATE_CREATED
    assert implementation_request["request_status"] == IMPLEMENTATION_REQUEST_CREATED
    assert worker_request["request_status"] == WORKER_REQUEST_CREATED
    assert dispatch_candidate["candidate_status"] == WORKER_DISPATCH_CANDIDATE_CREATED
    assert invocation_candidate["candidate_status"] == WORKER_INVOCATION_CANDIDATE_CREATED
    assert execution_candidate["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED
    assert execution["execution_status"] == WORKER_EXECUTION_COMPLETED
    assert validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED

    assert implementation_request["human_approval_granted"] is True
    assert worker_request["human_approval_required"] is True
    assert dispatch_candidate["human_approval_granted"] is True
    assert invocation_candidate["human_approval_granted"] is True
    assert execution_candidate["human_approval_granted"] is True
    assert execution["worker_execution_result_artifact"]["human_approval_reference"]
    assert execution["validation_inputs_artifact"]["human_approval_reference"]

    assert worker_request["worker_dispatched"] is False
    assert dispatch_candidate["worker_dispatched"] is False
    assert invocation_candidate["worker_invoked"] is False
    assert execution_candidate["worker_executed"] is False
    assert validation["result_validation_artifact"]["worker_invoked"] is False
    assert replay_certification["replay_certification_artifact"]["worker_invoked"] is False

    assert candidate["source_replay_references"]
    assert worker_request["replay_references"] == candidate["source_replay_references"]
    assert execution_candidate["replay_references"] == worker_request["replay_references"]
    assert validation["result_validation_artifact"]["replay_references"] == execution_candidate["replay_references"]
    assert replay_certification["replay_certification_artifact"]["replay_references"] == execution_candidate["replay_references"]
    assert replay_certification["replay_certification_artifact"]["replay_lineage_preserved"] is True
    assert replay_certification["replay_certification_artifact"]["fail_closed_preserved"] is True


def test_replay_derived_improvement_certification_produces_expected_packages(tmp_path) -> None:
    result = run_replay_derived_improvement_certification_v1(
        replay_base=tmp_path / "replay_derived_improvement_certification"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "REPLAY_DERIVED_IMPROVEMENT_CERTIFIED"
    assert all(result["assertions"].values())
    for key in (
        "coverage_report_path",
        "evidence_package_path",
        "replay_package_path",
        "improvement_proposal_package_path",
        "certification_report_path",
    ):
        assert load_json(Path(result[key]))["runtime_version"] == MILESTONE_ID


def test_replay_derived_improvement_certification_is_proposal_only(tmp_path) -> None:
    result = run_replay_derived_improvement_certification_v1(
        replay_base=tmp_path / "replay_derived_improvement_certification"
    )
    proposal = load_json(Path(result["improvement_proposal_package_path"]))

    assert proposal["proposal_status"] == "PROPOSAL_ONLY"
    assert proposal["human_approval_required"] is True
    assert proposal["implementation_executed"] is False
    assert proposal["code_modified"] is False
    assert proposal["governance_modified"] is False
    assert proposal["worker_invoked"] is False
    assert proposal["provider_invoked"] is False
    assert proposal["authority_transferred"] is False


def test_replay_derived_improvement_certification_replay_closure_is_traceable(tmp_path) -> None:
    result = run_replay_derived_improvement_certification_v1(
        replay_base=tmp_path / "replay_derived_improvement_certification"
    )
    replay = load_json(Path(result["replay_package_path"]))
    evidence = load_json(Path(result["evidence_package_path"]))

    assert replay["replay_reconstructed"] is True
    assert replay["replay_closure"]["improvement_linked_to_originating_replay"] is True
    assert replay["replay_closure"]["improvement_evidence_traceable"] is True
    assert evidence["gap_detection"]["status"] == GAPS_DETECTED
    assert evidence["improvement_intent"]["status"] == IMPROVEMENT_INTENT_CREATED
    assert evidence["ppp_routing"]["status"] == PPP_CANDIDATE_CREATED


def test_replay_derived_improvement_certification_evidence_is_secret_free(tmp_path) -> None:
    result = run_replay_derived_improvement_certification_v1(
        replay_base=tmp_path / "replay_derived_improvement_certification"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
