"""Tests for G3 Product 1 decision packet runtime."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_decision_packet import (
    PACKET_CREATED,
    PRODUCT1_DECISION_PACKET_ARTIFACT_V1,
    create_product1_decision_packet,
    reconstruct_product1_decision_packet_replay,
)
from aigol.runtime.product1_workflow_foundation import (
    GOVERNANCE_PASSED,
    OPERATOR_REVIEW_RECORDED,
    WORKFLOW_READY_FOR_DECISION_PACKET,
    create_product1_workflow,
    record_product1_governance_checkpoint,
    record_product1_operator_review_checkpoint,
    transition_product1_workflow_state,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
GOVERNANCE_AT = "2026-06-29T00:02:00Z"
REVIEW_AT = "2026-06-29T00:03:00Z"
TRANSITION_AT = "2026-06-29T00:04:00Z"
PACKET_AT = "2026-06-29T00:05:00Z"


def _governance_checkpoints() -> dict:
    return {
        "semantic_authority_preserved": True,
        "governance_authority_preserved": True,
        "approval_boundary_preserved": True,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "replay_boundary_preserved": True,
        "execution_boundary_preserved": True,
    }


def _lineage(name: str) -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/g3/product1-packet/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-PACKET-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-PACKET-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-packet"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-PACKET-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-PACKET-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "validate an AI execution decision packet"}),
        canonical_semantic_artifact_reference="CSA-TURN-PACKET-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-packet"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PRODUCT1-PACKET-PROPOSAL-000001",
        confirmation_request_reference="PRODUCT1-PACKET-CONFIRMATION-000001",
    )["conversation_artifact"]


def _workflow(tmp_path, replay_name: str = "workflow") -> dict:
    workflow = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-PACKET-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-PACKET-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-PACKET-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-PACKET-GOVERNANCE-000001",
        checkpoint_status=GOVERNANCE_PASSED,
        checkpoint_scope="AI_DECISION_VALIDATOR_PACKET",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "packet-governance"}),
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_operator_review_checkpoint(
        workflow_artifact=workflow,
        review_id="PRODUCT1-PACKET-REVIEW-000001",
        review_status=OPERATOR_REVIEW_RECORDED,
        review_evidence_hash=replay_hash({"review": "packet-review"}),
        required_next_action="create deterministic decision packet",
        reviewed_at=REVIEW_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    return transition_product1_workflow_state(
        workflow_artifact=workflow,
        workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
        transition_reason_hash=replay_hash({"transition": "packet-ready"}),
        transitioned_at=TRANSITION_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]


def _evidence() -> list[dict]:
    return [
        {
            "evidence_id": "EVIDENCE-CSA-000001",
            "evidence_type": "CSA_LINEAGE",
            "evidence_reference": "CSA-TURN-PACKET-000001",
            "evidence_hash": replay_hash({"evidence": "csa"}),
            "evidence_role": "semantic source",
        },
        {
            "evidence_id": "EVIDENCE-GOVERNANCE-000001",
            "evidence_type": "GOVERNANCE_CHECKPOINT",
            "evidence_reference": "PRODUCT1-PACKET-GOVERNANCE-000001",
            "evidence_hash": replay_hash({"evidence": "governance"}),
            "evidence_role": "checkpoint source",
        },
    ]


def _assumptions() -> list[dict]:
    return [
        {
            "assumption_id": "ASSUMPTION-000001",
            "statement": "The proposed execution decision remains pre-runtime.",
            "source_reference": "operator-review",
            "severity": "medium",
        }
    ]


def _risks() -> list[dict]:
    return [
        {
            "risk_id": "RISK-000001",
            "statement": "Downstream execution would require separate authorization.",
            "source_reference": "governance-checkpoint",
            "severity": "high",
        }
    ]


def _uncertainties() -> list[dict]:
    return [
        {
            "uncertainty_id": "UNCERTAINTY-000001",
            "statement": "Provider-assisted advisory analysis is deferred.",
            "source_reference": "G3-03 program",
            "severity": "low",
        }
    ]


def _recommendation() -> dict:
    return {
        "recommendation_id": "RECOMMENDATION-000001",
        "recommendation_status": "APPROVAL_REQUIRED",
        "summary": "Proceed to human review before any downstream authorization.",
        "recommended_next_action": "request explicit scoped approval",
        "confidence": "deterministic",
    }


def _packet(tmp_path):
    return create_product1_decision_packet(
        packet_id="PRODUCT1-DECISION-PACKET-000001",
        workflow_artifact=_workflow(tmp_path),
        evidence_references=_evidence(),
        assumptions=_assumptions(),
        risks=_risks(),
        uncertainties=_uncertainties(),
        recommendation_summary=_recommendation(),
        created_at=PACKET_AT,
        replay_dir=tmp_path / "packet",
    )


def test_creates_decision_packet_from_product1_workflow(tmp_path) -> None:
    capture = _packet(tmp_path)
    artifact = capture["decision_packet_artifact"]

    assert artifact["artifact_type"] == PRODUCT1_DECISION_PACKET_ARTIFACT_V1
    assert artifact["packet_id"] == "PRODUCT1-DECISION-PACKET-000001"
    assert artifact["packet_status"] == PACKET_CREATED
    assert artifact["workflow_id"] == "PRODUCT1-WORKFLOW-PACKET-000001"
    assert artifact["acli_session_id"] == "ACLI-G3-SESSION-PACKET-000001"
    assert artifact["originating_turn_id"] == "TURN-PACKET-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-PACKET-000001"
    assert artifact["evidence_reference_count"] == 2
    assert artifact["assumption_count"] == 1
    assert artifact["risk_count"] == 1
    assert artifact["uncertainty_count"] == 1
    assert artifact["recommendation_summary"]["recommendation_status"] == "APPROVAL_REQUIRED"
    assert artifact["governance_status"] == GOVERNANCE_PASSED
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_product1_decision_packet_replay(tmp_path / "packet")
    assert reconstructed["packet_id"] == "PRODUCT1-DECISION-PACKET-000001"
    assert reconstructed["evidence_reference_count"] == 2
    assert reconstructed["replay_lineage_count"] == 6


def test_decision_packet_requires_packet_ready_workflow(tmp_path) -> None:
    workflow = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-NOT-READY-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-PACKET-000001",
        rollback_reference="rollback:not-ready",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "not_ready_workflow",
    )["workflow_artifact"]

    with pytest.raises(FailClosedRuntimeError, match="workflow is not packet-ready"):
        create_product1_decision_packet(
            packet_id="PRODUCT1-DECISION-PACKET-NOT-READY",
            workflow_artifact=workflow,
            evidence_references=_evidence(),
            assumptions=_assumptions(),
            risks=_risks(),
            uncertainties=_uncertainties(),
            recommendation_summary=_recommendation(),
            created_at=PACKET_AT,
            replay_dir=tmp_path / "not_ready_packet",
        )


def test_decision_packet_rejects_duplicate_evidence_id(tmp_path) -> None:
    evidence = _evidence()
    evidence[1] = {**evidence[1], "evidence_id": evidence[0]["evidence_id"]}

    with pytest.raises(FailClosedRuntimeError, match="duplicate evidence id"):
        create_product1_decision_packet(
            packet_id="PRODUCT1-DECISION-PACKET-DUPLICATE",
            workflow_artifact=_workflow(tmp_path),
            evidence_references=evidence,
            assumptions=_assumptions(),
            risks=_risks(),
            uncertainties=_uncertainties(),
            recommendation_summary=_recommendation(),
            created_at=PACKET_AT,
            replay_dir=tmp_path / "duplicate_packet",
        )


def test_decision_packet_replay_tamper_fails_closed(tmp_path) -> None:
    _packet(tmp_path)
    path = tmp_path / "packet" / "000_product1_decision_packet_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_product1_decision_packet_replay(tmp_path / "packet")


def test_decision_packet_runtime_has_no_authority_or_execution_surfaces() -> None:
    import aigol.runtime.product1_decision_packet as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
    assert '"provider_invoked": True' not in source
    assert '"worker_invoked": True' not in source
    assert '"approval_created": True' not in source
    assert '"execution_requested": True' not in source
