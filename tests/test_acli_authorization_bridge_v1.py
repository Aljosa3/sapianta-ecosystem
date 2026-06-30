"""Tests for G3 ACLI authorization bridge."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_authorization_bridge import (
    ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1,
    AUTHORIZATION_BLOCKED,
    AUTHORIZATION_READY,
    PRECONDITIONS_FAILED,
    PRECONDITIONS_SATISFIED,
    create_conversational_authorization_bridge,
    reconstruct_acli_authorization_bridge_replay,
)
from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.acli_proposal_approval_bridge import (
    create_conversational_development_proposal,
    generate_conversational_approval_request,
    record_conversational_approval_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
PROPOSAL_AT = "2026-06-29T00:02:00Z"
REQUESTED_AT = "2026-06-29T00:03:00Z"
DECIDED_AT = "2026-06-29T00:04:00Z"
BRIDGED_AT = "2026-06-29T00:05:00Z"


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
            "replay_reference": f"runtime/g3/authorization/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path, suffix: str) -> dict:
    return create_acli_development_session(
        session_id=f"ACLI-G3-SESSION-AUTH-{suffix}",
        canonical_semantic_artifact_reference=f"CSA-SESSION-AUTH-{suffix}",
        canonical_semantic_artifact_hash=replay_hash({"csa": f"session-auth-{suffix}"}),
        replay_lineage=_lineage(f"session-{suffix}"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"session_{suffix}",
    )["session_artifact"]


def _conversation_with_turn(tmp_path, suffix: str) -> dict:
    conversation = start_conversational_development_session(
        conversation_id=f"ACLI-CONVERSATION-AUTH-{suffix}",
        session_artifact=_session(tmp_path, suffix),
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"conversation_{suffix}",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id=f"TURN-AUTH-{suffix}",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / f"conversation_{suffix}",
        prompt_hash=replay_hash({"prompt": f"prepare authorization bridge proposal {suffix}"}),
        canonical_semantic_artifact_reference=f"CSA-TURN-AUTH-{suffix}",
        canonical_semantic_artifact_hash=replay_hash({"csa": f"turn-auth-{suffix}"}),
        replay_lineage=_lineage(f"turn-{suffix}"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CONFIRMATION_REQUIRED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference=f"PROPOSAL-AUTH-{suffix}",
        confirmation_request_reference=f"CONFIRM-AUTH-{suffix}",
    )["conversation_artifact"]


def _proposal(tmp_path, suffix: str) -> dict:
    return create_conversational_development_proposal(
        proposal_id=f"ACLI-PROPOSAL-AUTH-{suffix}",
        conversation_artifact=_conversation_with_turn(tmp_path, suffix),
        originating_turn_id=f"TURN-AUTH-{suffix}",
        proposal_version=1,
        proposal_summary="Prepare an authorization-readiness bridge proposal.",
        rollback_reference=f"rollback:ACLI-PROPOSAL-AUTH-{suffix}:v1",
        created_at=PROPOSAL_AT,
        replay_dir=tmp_path / f"proposal_{suffix}",
    )["proposal_artifact"]


def _approval_requested_proposal(tmp_path, suffix: str) -> dict:
    proposal = _proposal(tmp_path, suffix)
    return generate_conversational_approval_request(
        proposal_artifact=proposal,
        approval_request_id=f"ACLI-APPROVAL-REQUEST-AUTH-{suffix}",
        requested_at=REQUESTED_AT,
        replay_dir=tmp_path / f"proposal_{suffix}",
    )["proposal_artifact"]


def _approved_proposal(tmp_path, suffix: str = "000001") -> dict:
    proposal = _approval_requested_proposal(tmp_path, suffix)
    return record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id=f"ACLI-APPROVAL-DECISION-AUTH-{suffix}",
        decision="APPROVED",
        decision_rationale_hash=replay_hash({"rationale": f"operator approved {suffix}"}),
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / f"proposal_{suffix}",
    )["proposal_artifact"]


def test_creates_authorization_ready_artifact_from_approved_proposal(tmp_path) -> None:
    proposal = _approved_proposal(tmp_path)
    capture = create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-000001",
        proposal_artifact=proposal,
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization_bridge",
    )
    artifact = capture["authorization_bridge_artifact"]

    assert artifact["artifact_type"] == ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1
    assert artifact["authorization_bridge_id"] == "ACLI-AUTHORIZATION-BRIDGE-000001"
    assert artifact["originating_session_id"] == "ACLI-G3-SESSION-AUTH-000001"
    assert artifact["originating_turn_id"] == "TURN-AUTH-000001"
    assert artifact["proposal_id"] == "ACLI-PROPOSAL-AUTH-000001"
    assert artifact["approval_request_id"] == "ACLI-APPROVAL-REQUEST-AUTH-000001"
    assert artifact["approval_decision_reference"] == "ACLI-APPROVAL-DECISION-AUTH-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-AUTH-000001"
    assert artifact["authorization_readiness_status"] == AUTHORIZATION_READY
    assert artifact["precondition_status"] == PRECONDITIONS_SATISFIED
    assert artifact["rollback_reference"] == "rollback:ACLI-PROPOSAL-AUTH-000001:v1"
    assert artifact["authorization_created"] is False
    assert artifact["execution_requested"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert artifact["uhcl_wrapper_wiring"]["authorization_created_by_wiring"] is False
    assert artifact["uhcl_wrapper_wiring"]["execution_authorized_by_wiring"] is False

    reconstructed = reconstruct_acli_authorization_bridge_replay(tmp_path / "authorization_bridge")
    assert reconstructed["authorization_readiness_status"] == AUTHORIZATION_READY
    assert reconstructed["precondition_status"] == PRECONDITIONS_SATISFIED
    assert reconstructed["event_count"] == 1
    assert reconstructed["authorization_created"] is False
    assert reconstructed["uhcl_wrapper_wiring"]["uhcl_consumed"] is True


def test_blocks_authorization_bridge_for_missing_approval(tmp_path) -> None:
    proposal = _proposal(tmp_path, "MISSING")
    capture = create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-MISSING",
        proposal_artifact=proposal,
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization_bridge_missing",
    )
    artifact = capture["authorization_bridge_artifact"]

    assert artifact["authorization_readiness_status"] == AUTHORIZATION_BLOCKED
    assert artifact["precondition_status"] == PRECONDITIONS_FAILED
    assert artifact["approval_request_id"] == "APPROVAL_REQUEST_MISSING"
    assert artifact["approval_decision_reference"] == "APPROVAL_DECISION_MISSING"
    assert "approval_request_present" in artifact["failure_reason"]
    assert artifact["rejection_or_missing_approval_handling_visible"] is True
    assert artifact["execution_requested"] is False
    assert artifact["uhcl_wrapper_wiring"]["uhcl_artifact_type"] == "UHCL_RECOVERY_GUIDANCE_MODEL_ARTIFACT_V1"


def test_blocks_authorization_bridge_for_rejected_proposal(tmp_path) -> None:
    proposal = _approval_requested_proposal(tmp_path, "REJECT")
    rejected = record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id="ACLI-APPROVAL-DECISION-AUTH-REJECT",
        decision="REJECTED",
        decision_rationale_hash=replay_hash({"rationale": "operator rejected"}),
        rejection_reference="rejection:ACLI-PROPOSAL-AUTH-REJECT",
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / "proposal_REJECT",
    )["proposal_artifact"]

    capture = create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-REJECT",
        proposal_artifact=rejected,
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization_bridge_reject",
    )
    artifact = capture["authorization_bridge_artifact"]

    assert artifact["authorization_readiness_status"] == AUTHORIZATION_BLOCKED
    assert artifact["precondition_status"] == PRECONDITIONS_FAILED
    assert artifact["approval_request_id"] == "ACLI-APPROVAL-REQUEST-AUTH-REJECT"
    assert artifact["approval_decision_reference"] == "ACLI-APPROVAL-DECISION-AUTH-REJECT"
    assert "approval_decision_approved" in artifact["failure_reason"]
    assert artifact["authorization_created"] is False


def test_blocks_authorization_bridge_for_clarification_return(tmp_path) -> None:
    proposal = _approval_requested_proposal(tmp_path, "CLARIFY")
    clarified = record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id="ACLI-APPROVAL-DECISION-AUTH-CLARIFY",
        decision="CLARIFICATION_REQUESTED",
        decision_rationale_hash=replay_hash({"rationale": "operator asked for clarification"}),
        clarification_return_reference="clarification:ACLI-PROPOSAL-AUTH-CLARIFY",
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / "proposal_CLARIFY",
    )["proposal_artifact"]

    capture = create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-CLARIFY",
        proposal_artifact=clarified,
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization_bridge_clarify",
        rollback_reference="rollback:clarification-return",
    )
    artifact = capture["authorization_bridge_artifact"]

    assert artifact["authorization_readiness_status"] == AUTHORIZATION_BLOCKED
    assert artifact["precondition_status"] == PRECONDITIONS_FAILED
    assert artifact["approval_decision_reference"] == "ACLI-APPROVAL-DECISION-AUTH-CLARIFY"
    assert artifact["rollback_reference"] == "rollback:clarification-return"
    assert "proposal_status_approved" in artifact["failure_reason"]


def test_authorization_bridge_replay_tamper_fails_closed(tmp_path) -> None:
    create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-TAMPER",
        proposal_artifact=_approved_proposal(tmp_path, "TAMPER"),
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization_bridge_tamper",
    )
    path = tmp_path / "authorization_bridge_tamper" / "000_acli_authorization_bridge_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_requested"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_authorization_bridge_replay(tmp_path / "authorization_bridge_tamper")


def test_runtime_has_no_execution_provider_worker_deployment_or_mutation_surfaces() -> None:
    import aigol.runtime.acli_authorization_bridge as runtime

    source = inspect.getsource(runtime)

    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
    assert '"authorization_created": True' not in source
    assert '"execution_requested": True' not in source
