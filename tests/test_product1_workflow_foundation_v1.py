"""Tests for G3 Product 1 workflow foundation."""

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
from aigol.runtime.product1_workflow_foundation import (
    GOVERNANCE_BLOCKED,
    GOVERNANCE_PASSED,
    GOVERNANCE_PENDING,
    OPERATOR_REVIEW_PENDING,
    OPERATOR_REVIEW_RECORDED,
    PRODUCT1_IDENTITY,
    PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1,
    WORKFLOW_ACTIVE,
    WORKFLOW_CREATED,
    WORKFLOW_READY_FOR_DECISION_PACKET,
    create_product1_workflow,
    reconstruct_product1_workflow_foundation_replay,
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
            "replay_reference": f"runtime/g3/product1/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-PRODUCT1-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-PRODUCT1-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-product1"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-PRODUCT1-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-PRODUCT1-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "validate an AI execution decision"}),
        canonical_semantic_artifact_reference="CSA-TURN-PRODUCT1-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-product1"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PRODUCT1-PROPOSAL-000001",
        confirmation_request_reference="PRODUCT1-CONFIRMATION-000001",
    )["conversation_artifact"]


def _workflow(tmp_path, replay_name: str = "product1_workflow") -> dict:
    return create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-PRODUCT1-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]


def _governance_passed_workflow(tmp_path, replay_name: str = "product1_workflow") -> dict:
    workflow = _workflow(tmp_path, replay_name)
    return record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-GOVERNANCE-000001",
        checkpoint_status=GOVERNANCE_PASSED,
        checkpoint_scope="AI_DECISION_VALIDATOR_INTAKE",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "governance-passed"}),
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]


def test_creates_product1_workflow_identity_from_acli_turn(tmp_path) -> None:
    capture = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-PRODUCT1-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "product1_workflow",
    )
    artifact = capture["workflow_artifact"]

    assert artifact["artifact_type"] == PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1
    assert artifact["product_identity"] == PRODUCT1_IDENTITY
    assert artifact["workflow_id"] == "PRODUCT1-WORKFLOW-000001"
    assert artifact["acli_session_id"] == "ACLI-G3-SESSION-PRODUCT1-000001"
    assert artifact["originating_turn_id"] == "TURN-PRODUCT1-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-PRODUCT1-000001"
    assert artifact["workflow_status"] == WORKFLOW_CREATED
    assert artifact["governance_checkpoint_status"] == GOVERNANCE_PENDING
    assert artifact["operator_review_status"] == OPERATOR_REVIEW_PENDING
    assert artifact["rollback_reference"] == "rollback:PRODUCT1-WORKFLOW-000001"
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_product1_workflow_foundation_replay(tmp_path / "product1_workflow")
    assert reconstructed["workflow_id"] == "PRODUCT1-WORKFLOW-000001"
    assert reconstructed["event_count"] == 1
    assert reconstructed["product_identity"] == PRODUCT1_IDENTITY


def test_records_governance_and_operator_review_then_ready_transition(tmp_path) -> None:
    workflow = _governance_passed_workflow(tmp_path)
    workflow = record_product1_operator_review_checkpoint(
        workflow_artifact=workflow,
        review_id="PRODUCT1-OPERATOR-REVIEW-000001",
        review_status=OPERATOR_REVIEW_RECORDED,
        review_evidence_hash=replay_hash({"review": "operator-reviewed"}),
        required_next_action="assemble Product 1 decision packet",
        reviewed_at=REVIEW_AT,
        replay_dir=tmp_path / "product1_workflow",
    )["workflow_artifact"]
    capture = transition_product1_workflow_state(
        workflow_artifact=workflow,
        workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
        transition_reason_hash=replay_hash({"transition": "ready-for-decision-packet"}),
        transitioned_at=TRANSITION_AT,
        replay_dir=tmp_path / "product1_workflow",
    )
    artifact = capture["workflow_artifact"]

    assert artifact["workflow_status"] == WORKFLOW_READY_FOR_DECISION_PACKET
    assert artifact["governance_checkpoint_status"] == GOVERNANCE_PASSED
    assert artifact["operator_review_status"] == OPERATOR_REVIEW_RECORDED
    assert len(artifact["governance_checkpoints"]) == 1
    assert len(artifact["operator_review_checkpoints"]) == 1

    reconstructed = reconstruct_product1_workflow_foundation_replay(tmp_path / "product1_workflow")
    assert reconstructed["workflow_status"] == WORKFLOW_READY_FOR_DECISION_PACKET
    assert reconstructed["governance_checkpoint_count"] == 1
    assert reconstructed["operator_review_checkpoint_count"] == 1
    assert reconstructed["event_count"] == 4


def test_ready_transition_requires_governance_and_operator_review(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="governance checkpoint must pass"):
        transition_product1_workflow_state(
            workflow_artifact=_workflow(tmp_path),
            workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
            transition_reason_hash=replay_hash({"transition": "too-early"}),
            transitioned_at=TRANSITION_AT,
            replay_dir=tmp_path / "product1_workflow",
        )


def test_governance_block_fails_closed_without_execution(tmp_path) -> None:
    workflow = _workflow(tmp_path, "blocked_workflow")
    capture = record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-GOVERNANCE-BLOCK-000001",
        checkpoint_status=GOVERNANCE_BLOCKED,
        checkpoint_scope="AI_DECISION_VALIDATOR_INTAKE",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "blocked"}),
        failure_reason="proposed execution scope is missing",
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / "blocked_workflow",
    )
    artifact = capture["workflow_artifact"]

    assert artifact["workflow_status"] == "FAILED_CLOSED"
    assert artifact["governance_checkpoint_status"] == GOVERNANCE_BLOCKED
    assert artifact["failure_reason"] == "proposed execution scope is missing"
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutated"] is False


def test_product1_workflow_replay_tamper_fails_closed(tmp_path) -> None:
    _workflow(tmp_path)
    path = tmp_path / "product1_workflow" / "000_product1_workflow_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_product1_workflow_foundation_replay(tmp_path / "product1_workflow")


def test_runtime_has_no_provider_worker_mutation_deployment_or_external_surfaces() -> None:
    import aigol.runtime.product1_workflow_foundation as runtime

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
    assert '"execution_requested": True' not in source
    assert '"repository_mutated": True' not in source
