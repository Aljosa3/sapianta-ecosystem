"""Tests for G3 ACLI conversational development sessions."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
    CONVERSATION_STARTED,
    TURN_RECORDED,
    record_conversational_development_turn,
    reconstruct_acli_conversational_development_session_replay,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-28T00:00:00Z"
TURN_AT = "2026-06-28T00:01:00Z"
SECOND_TURN_AT = "2026-06-28T00:02:00Z"


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
            "replay_reference": f"runtime/g3/conversation/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-CONV-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation(tmp_path) -> dict:
    return start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )


def test_starts_conversational_development_session_from_lifecycle_session(tmp_path) -> None:
    capture = _conversation(tmp_path)
    artifact = capture["conversation_artifact"]
    reconstructed = reconstruct_acli_conversational_development_session_replay(tmp_path / "conversation")

    assert artifact["artifact_type"] == ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1
    assert artifact["conversation_id"] == "ACLI-CONVERSATION-000001"
    assert artifact["session_id"] == "ACLI-G3-SESSION-CONV-000001"
    assert artifact["conversation_status"] == CONVERSATION_STARTED
    assert artifact["turns"] == []
    assert artifact["current_csa_reference"] == "CSA-SESSION-000001"
    assert artifact["conversation_history_associated"] is True
    assert artifact["csa_continuity_preserved"] is True
    assert artifact["replay_turn_lineage_preserved"] is True
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutated"] is False
    assert reconstructed["conversation_id"] == artifact["conversation_id"]
    assert reconstructed["turn_count"] == 0


def test_records_first_conversational_turn_with_required_statuses(tmp_path) -> None:
    started = _conversation(tmp_path)
    capture = record_conversational_development_turn(
        conversation_artifact=started["conversation_artifact"],
        turn_id="TURN-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "what should I do"}),
        canonical_semantic_artifact_reference="CSA-TURN-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-1"}),
        replay_lineage=_lineage("turn-1"),
        clarification_status="CLARIFICATION_REQUESTED",
        proposal_status="PROPOSAL_NOT_CREATED",
        confirmation_status="CONFIRMATION_NOT_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        clarification_request_reference="CLARIFY-000001",
    )
    artifact = capture["conversation_artifact"]
    turn = artifact["turns"][0]
    reconstructed = reconstruct_acli_conversational_development_session_replay(tmp_path / "conversation")

    assert artifact["conversation_status"] == TURN_RECORDED
    assert artifact["turns"][0]["turn_id"] == "TURN-000001"
    assert turn["parent_turn_id"] is None
    assert turn["previous_turn_hash"] == ""
    assert turn["previous_csa_hash"] == replay_hash({"csa": "session"})
    assert turn["clarification_status"] == "CLARIFICATION_REQUESTED"
    assert artifact["clarification_requests_visible"] is True
    assert reconstructed["turn_count"] == 1
    assert reconstructed["clarification_statuses"] == ["CLARIFICATION_REQUESTED"]


def test_records_parented_continuation_turn_with_csa_continuity(tmp_path) -> None:
    started = _conversation(tmp_path)
    first = record_conversational_development_turn(
        conversation_artifact=started["conversation_artifact"],
        turn_id="TURN-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "draft proposal"}),
        canonical_semantic_artifact_reference="CSA-TURN-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-1"}),
        replay_lineage=_lineage("turn-1"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PROPOSAL-000001",
        confirmation_request_reference="CONFIRM-000001",
    )
    second = record_conversational_development_turn(
        conversation_artifact=first["conversation_artifact"],
        turn_id="TURN-000002",
        parent_turn_id="TURN-000001",
        recorded_at=SECOND_TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "continue"}),
        canonical_semantic_artifact_reference="CSA-TURN-000002",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-2"}),
        replay_lineage=_lineage("turn-2"),
        clarification_status="CLARIFICATION_NOT_REQUIRED",
        proposal_status="PROPOSAL_CONFIRMATION_REQUIRED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="CONTINUATION_FROM_PARENT_TURN",
        proposal_reference="PROPOSAL-000001",
        confirmation_request_reference="CONFIRM-000002",
    )
    artifact = second["conversation_artifact"]
    turns = artifact["turns"]
    reconstructed = reconstruct_acli_conversational_development_session_replay(tmp_path / "conversation")

    assert len(turns) == 2
    assert turns[1]["parent_turn_id"] == "TURN-000001"
    assert turns[1]["previous_turn_hash"] == turns[0]["turn_hash"]
    assert turns[1]["previous_csa_hash"] == replay_hash({"csa": "turn-1"})
    assert artifact["current_csa_reference"] == "CSA-TURN-000002"
    assert artifact["proposal_lifecycle_visible"] is True
    assert artifact["confirmation_requests_visible"] is True
    assert reconstructed["continuation_statuses"] == [
        "NEW_CONVERSATION",
        "CONTINUATION_FROM_PARENT_TURN",
    ]
    assert reconstructed["turn_hash_chain"] == [turn["turn_hash"] for turn in turns]


def test_parent_turn_is_required_for_continuation(tmp_path) -> None:
    started = _conversation(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="parent turn required"):
        record_conversational_development_turn(
            conversation_artifact=started["conversation_artifact"],
            turn_id="TURN-BROKEN",
            recorded_at=TURN_AT,
            replay_dir=tmp_path / "conversation",
            prompt_hash=replay_hash({"prompt": "continue"}),
            canonical_semantic_artifact_reference="CSA-BROKEN",
            canonical_semantic_artifact_hash=replay_hash({"csa": "broken"}),
            replay_lineage=_lineage("broken"),
            clarification_status="CLARIFICATION_NOT_REQUIRED",
            proposal_status="PROPOSAL_NOT_CREATED",
            confirmation_status="CONFIRMATION_NOT_REQUIRED",
            continuation_status="CONTINUATION_FROM_PARENT_TURN",
        )


def test_conversational_replay_tamper_fails_closed(tmp_path) -> None:
    started = _conversation(tmp_path)
    record_conversational_development_turn(
        conversation_artifact=started["conversation_artifact"],
        turn_id="TURN-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "review this"}),
        canonical_semantic_artifact_reference="CSA-TURN-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-1"}),
        replay_lineage=_lineage("turn-1"),
        clarification_status="CLARIFICATION_REQUESTED",
        proposal_status="PROPOSAL_NOT_CREATED",
        confirmation_status="CONFIRMATION_NOT_REQUIRED",
        continuation_status="NEW_CONVERSATION",
    )
    path = tmp_path / "conversation" / "001_acli_conversational_development_turn_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["turns"][0]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_conversational_development_session_replay(tmp_path / "conversation")


def test_runtime_has_no_provider_worker_product_deployment_or_mutation_surfaces() -> None:
    import aigol.runtime.acli_conversational_development_session as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
