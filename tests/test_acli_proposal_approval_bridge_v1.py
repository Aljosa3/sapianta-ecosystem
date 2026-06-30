"""Tests for G3 ACLI proposal and approval-request bridge."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.acli_proposal_approval_bridge import (
    ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1,
    APPROVAL_CLARIFICATION_REQUESTED,
    APPROVAL_NOT_REQUESTED,
    APPROVAL_REJECTED,
    APPROVAL_REQUESTED,
    CLARIFICATION_RETURNED,
    PROPOSAL_DRAFTED,
    PROPOSAL_REJECTED,
    PROPOSAL_REVISED,
    create_conversational_development_proposal,
    generate_conversational_approval_request,
    reconstruct_acli_proposal_approval_bridge_replay,
    record_conversational_approval_decision,
    revise_conversational_development_proposal,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
PROPOSAL_AT = "2026-06-29T00:02:00Z"
REQUESTED_AT = "2026-06-29T00:03:00Z"
DECIDED_AT = "2026-06-29T00:04:00Z"


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
            "replay_reference": f"runtime/g3/proposal/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-BRIDGE-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-BRIDGE-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-bridge"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-BRIDGE-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-BRIDGE-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "prepare a governed change proposal"}),
        canonical_semantic_artifact_reference="CSA-TURN-BRIDGE-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-bridge"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CONFIRMATION_REQUIRED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PROPOSAL-BRIDGE-000001",
        confirmation_request_reference="CONFIRM-BRIDGE-000001",
    )["conversation_artifact"]


def _proposal(tmp_path, replay_name: str = "bridge") -> dict:
    return create_conversational_development_proposal(
        proposal_id="ACLI-PROPOSAL-BRIDGE-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-BRIDGE-000001",
        proposal_version=1,
        proposal_summary="Prepare a governed development proposal for operator review.",
        rollback_reference="rollback:ACLI-PROPOSAL-BRIDGE-000001:v1",
        created_at=PROPOSAL_AT,
        replay_dir=tmp_path / replay_name,
    )["proposal_artifact"]


def _approval_requested_proposal(tmp_path, replay_name: str = "bridge") -> dict:
    proposal = _proposal(tmp_path, replay_name)
    return generate_conversational_approval_request(
        proposal_artifact=proposal,
        approval_request_id="ACLI-APPROVAL-REQUEST-BRIDGE-000001",
        requested_at=REQUESTED_AT,
        replay_dir=tmp_path / replay_name,
    )["proposal_artifact"]


def test_creates_proposal_from_conversational_turn_with_required_fields(tmp_path) -> None:
    capture = create_conversational_development_proposal(
        proposal_id="ACLI-PROPOSAL-BRIDGE-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-BRIDGE-000001",
        proposal_version=1,
        proposal_summary="Prepare a governed development proposal for operator review.",
        rollback_reference="rollback:ACLI-PROPOSAL-BRIDGE-000001:v1",
        created_at=PROPOSAL_AT,
        replay_dir=tmp_path / "bridge",
    )
    artifact = capture["proposal_artifact"]

    assert artifact["artifact_type"] == ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1
    assert artifact["proposal_id"] == "ACLI-PROPOSAL-BRIDGE-000001"
    assert artifact["originating_session_id"] == "ACLI-G3-SESSION-BRIDGE-000001"
    assert artifact["originating_turn_id"] == "TURN-BRIDGE-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-BRIDGE-000001"
    assert artifact["proposal_version"] == 1
    assert artifact["proposal_status"] == PROPOSAL_DRAFTED
    assert artifact["approval_status"] == APPROVAL_NOT_REQUESTED
    assert artifact["rollback_reference"] == "rollback:ACLI-PROPOSAL-BRIDGE-000001:v1"
    assert artifact["approval_created"] is False
    assert artifact["authorization_created"] is False
    assert artifact["execution_requested"] is False
    assert len(artifact["replay_lineage"]) == 3
    assert artifact["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert artifact["uhcl_wrapper_wiring"]["uhcl_artifact_type"] == "UHCL_TYPED_COMMUNICATION_SECTION_ARTIFACT_V1"

    reconstructed = reconstruct_acli_proposal_approval_bridge_replay(tmp_path / "bridge")
    assert reconstructed["proposal_id"] == "ACLI-PROPOSAL-BRIDGE-000001"
    assert reconstructed["proposal_version_count"] == 1
    assert reconstructed["event_count"] == 1


def test_revises_proposal_version_and_preserves_lineage(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    capture = revise_conversational_development_proposal(
        proposal_artifact=proposal,
        proposal_version=2,
        proposal_summary="Revise the governed proposal after operator modification request.",
        rollback_reference="rollback:ACLI-PROPOSAL-BRIDGE-000001:v2",
        revised_at=REQUESTED_AT,
        replay_dir=tmp_path / "bridge",
    )
    artifact = capture["proposal_artifact"]

    assert artifact["proposal_version"] == 2
    assert artifact["proposal_status"] == PROPOSAL_REVISED
    assert artifact["approval_status"] == APPROVAL_NOT_REQUESTED
    assert artifact["proposal_versions"][1]["previous_version_hash"] == proposal["proposal_versions"][0][
        "proposal_version_hash"
    ]
    assert artifact["rollback_reference"] == "rollback:ACLI-PROPOSAL-BRIDGE-000001:v2"

    reconstructed = reconstruct_acli_proposal_approval_bridge_replay(tmp_path / "bridge")
    assert reconstructed["proposal_version_count"] == 2
    assert reconstructed["event_count"] == 2


def test_generates_approval_request_without_approval_authorization_or_execution(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    capture = generate_conversational_approval_request(
        proposal_artifact=proposal,
        approval_request_id="ACLI-APPROVAL-REQUEST-BRIDGE-000001",
        requested_at=REQUESTED_AT,
        replay_dir=tmp_path / "bridge",
    )
    artifact = capture["proposal_artifact"]

    assert artifact["proposal_status"] == APPROVAL_REQUESTED
    assert artifact["approval_status"] == APPROVAL_REQUESTED
    assert artifact["approval_request_generated"] is True
    assert artifact["approval_requests"][0]["approval_request_id"] == "ACLI-APPROVAL-REQUEST-BRIDGE-000001"
    assert artifact["approval_requests"][0]["approval_request"]["approval_required"] is True
    assert artifact["approval_created"] is False
    assert artifact["authorization_created"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutated"] is False
    assert artifact["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert artifact["uhcl_wrapper_wiring"]["uhcl_artifact_type"] == "UHCL_SHARED_CONFIRMATION_MODEL_ARTIFACT_V1"


def test_records_rejection_handling_without_execution(tmp_path) -> None:
    proposal = _approval_requested_proposal(tmp_path)
    capture = record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id="ACLI-APPROVAL-DECISION-REJECT-000001",
        decision="REJECTED",
        decision_rationale_hash=replay_hash({"rationale": "operator rejected proposal"}),
        rejection_reference="rejection:ACLI-PROPOSAL-BRIDGE-000001",
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / "bridge",
    )
    artifact = capture["proposal_artifact"]

    assert artifact["proposal_status"] == PROPOSAL_REJECTED
    assert artifact["approval_status"] == APPROVAL_REJECTED
    assert artifact["rejection_handling_visible"] is True
    assert artifact["rejection_reference"] == "rejection:ACLI-PROPOSAL-BRIDGE-000001"
    assert artifact["approval_decisions"][0]["decision"] == "REJECTED"
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_acli_proposal_approval_bridge_replay(tmp_path / "bridge")
    assert reconstructed["approval_request_count"] == 1
    assert reconstructed["approval_decision_count"] == 1
    assert reconstructed["approval_created"] is False


def test_records_clarification_return_path_without_approval(tmp_path) -> None:
    proposal = _approval_requested_proposal(tmp_path, "clarify_bridge")
    capture = record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id="ACLI-APPROVAL-DECISION-CLARIFY-000001",
        decision="CLARIFICATION_REQUESTED",
        decision_rationale_hash=replay_hash({"rationale": "operator requested clarification"}),
        clarification_return_reference="clarification:ACLI-PROPOSAL-BRIDGE-000001",
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / "clarify_bridge",
    )
    artifact = capture["proposal_artifact"]

    assert artifact["proposal_status"] == CLARIFICATION_RETURNED
    assert artifact["approval_status"] == APPROVAL_CLARIFICATION_REQUESTED
    assert artifact["clarification_return_path_visible"] is True
    assert artifact["clarification_return_reference"] == "clarification:ACLI-PROPOSAL-BRIDGE-000001"
    assert artifact["approval_created"] is False
    assert artifact["authorization_created"] is False


def test_approval_decision_before_request_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="approval request is required"):
        record_conversational_approval_decision(
            proposal_artifact=_proposal(tmp_path),
            approval_decision_id="ACLI-APPROVAL-DECISION-FAIL-000001",
            decision="APPROVED",
            decision_rationale_hash=replay_hash({"rationale": "too early"}),
            decided_at=DECIDED_AT,
            replay_dir=tmp_path / "bridge",
        )


def test_proposal_approval_replay_tamper_fails_closed(tmp_path) -> None:
    _approval_requested_proposal(tmp_path)
    path = tmp_path / "bridge" / "001_acli_approval_request_generated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_created"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_proposal_approval_bridge_replay(tmp_path / "bridge")


def test_runtime_has_no_authorization_execution_provider_worker_or_mutation_surfaces() -> None:
    import aigol.runtime.acli_proposal_approval_bridge as runtime

    source = inspect.getsource(runtime)

    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
    assert '"approval_created": True' not in source
    assert '"authorization_created": True' not in source
    assert '"execution_requested": True' not in source
