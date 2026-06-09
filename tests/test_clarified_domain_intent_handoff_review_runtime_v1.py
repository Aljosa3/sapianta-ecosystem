from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.clarification_continuity_runtime import run_clarification_continuity
from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    CLARIFICATION_REQUIRED,
    FAIL_CLOSED,
    OCS_HANDOFF_APPROVED,
    WORKER_BINDING_APPROVED,
    reconstruct_clarified_domain_intent_handoff_review_replay,
    review_clarified_domain_intent,
)
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unknown_domain_clarification_runtime import run_unknown_domain_clarification_workflow
from aigol.workers.domain_artifact_worker import DOMAIN_ARTIFACT_WORKER_ID


CREATED_AT = "2026-06-09T00:00:00Z"
SESSION_ID = "SESSION-CLARIFIED-DOMAIN-HANDOFF-REVIEW-000001"
PROMPT = "Create a new governed domain called FreshDomain."
REPLY = "\n".join(
    [
        "Primary purpose: Create a safe pilot governed domain.",
        "Expected capabilities: Clarification handling and bounded workflow resume.",
        "Target users: Internal operators.",
    ]
)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _conversation_args(tmp_path):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )


def _seed_open_clarification(session_root, turn_id: str = "TURN-000001") -> str:
    prompt_id = f"{SESSION_ID}:{turn_id}"
    turn_root = session_root / turn_id
    route_conversational_cli_intent(
        routing_id=f"{prompt_id}:CONVERSATIONAL-CLI-ROUTING",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "conversational_cli_routing",
    )
    run_unknown_domain_clarification_workflow(
        clarification_id=f"{prompt_id}:UNKNOWN-DOMAIN-CLARIFICATION",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "unknown_domain_clarification",
    )
    return prompt_id


def _continuity(tmp_path):
    session_root = tmp_path / "runtime" / SESSION_ID
    prompt_id = _seed_open_clarification(session_root)
    return run_clarification_continuity(
        continuity_id=f"{SESSION_ID}:TURN-000002:CLARIFICATION-CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{SESSION_ID}:TURN-000002",
        operator_reply=REPLY,
        current_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )


def _review(tmp_path, *, decision: str = WORKER_BINDING_APPROVED, questions: list[str] | None = None):
    continuity = _continuity(tmp_path)
    return review_clarified_domain_intent(
        review_id="HANDOFF-REVIEW-FRESHDOMAIN-000001",
        clarification_continuity_replay_reference=continuity["clarification_continuity_replay_reference"],
        review_decision=decision,
        reviewed_by="AIGOL_GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff_review",
        clarification_questions=questions,
    )


def test_successful_worker_binding_review_preserves_replay_continuity(tmp_path) -> None:
    capture = _review(tmp_path, decision=WORKER_BINDING_APPROVED)
    replay = reconstruct_clarified_domain_intent_handoff_review_replay(tmp_path / "handoff_review")
    decision = capture["handoff_review_decision_artifact"]

    assert capture["review_decision"] == WORKER_BINDING_APPROVED
    assert capture["proposed_domain"] == "FreshDomain"
    assert capture["next_certified_stage"] == "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW"
    assert decision["worker_binding"]["target_worker_id"] == DOMAIN_ARTIFACT_WORKER_ID
    assert decision["worker_request_created"] is False
    assert decision["authorization_created"] is False
    assert decision["worker_invoked"] is False
    assert replay["review_decision"] == WORKER_BINDING_APPROVED
    assert replay["proposed_domain"] == "FreshDomain"
    assert replay["target_worker_id"] == DOMAIN_ARTIFACT_WORKER_ID


def test_ocs_handoff_approved_review_path(tmp_path) -> None:
    capture = _review(tmp_path, decision=OCS_HANDOFF_APPROVED)
    decision = capture["handoff_review_decision_artifact"]

    assert capture["review_decision"] == OCS_HANDOFF_APPROVED
    assert capture["next_certified_stage"] == "AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1"
    assert decision["ocs_handoff_decision"]["handoff_preparation_allowed"] is True
    assert decision["worker_binding"] == {}
    assert decision["authorization_created"] is False


def test_clarification_reentry_path_records_questions(tmp_path) -> None:
    capture = _review(
        tmp_path,
        decision=CLARIFICATION_REQUIRED,
        questions=["Please identify domain compliance owner."],
    )
    replay = reconstruct_clarified_domain_intent_handoff_review_replay(tmp_path / "handoff_review")

    assert capture["review_decision"] == CLARIFICATION_REQUIRED
    assert capture["next_certified_stage"] == "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    assert capture["handoff_review_decision_artifact"]["worker_binding"] == {}
    assert replay["clarification_questions"] == ["Please identify domain compliance owner."]


def test_clarification_required_without_questions_fails_closed(tmp_path) -> None:
    capture = _review(tmp_path, decision=CLARIFICATION_REQUIRED)

    assert capture["review_decision"] == FAIL_CLOSED
    assert capture["fail_closed"] is True
    assert "clarification_questions is required" in capture["failure_reason"]


def test_invalid_review_decision_fails_closed(tmp_path) -> None:
    capture = _review(tmp_path, decision="AUTONOMOUS_DOMAIN_APPROVAL")

    assert capture["review_decision"] == FAIL_CLOSED
    assert capture["fail_closed"] is True
    assert "invalid review decision" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_invoked"] is False


def test_replay_corruption_is_detected(tmp_path) -> None:
    _review(tmp_path, decision=WORKER_BINDING_APPROVED)
    replay_file = tmp_path / "handoff_review" / "000_handoff_review_decision_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposed_domain"] = "TamperedDomain"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_domain_intent_handoff_review_replay(tmp_path / "handoff_review")


def test_acli_freshdomain_reaches_handoff_review_without_execution(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, "exit"]),
        output_func=output.append,
    )
    first, second = result["turns"]
    replay = reconstruct_clarified_domain_intent_handoff_review_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000002"
        / "clarified_domain_handoff_review"
    )

    assert result["failed_turns"] == 0
    assert first["proposed_domain"] == "FreshDomain"
    assert second["workflow_resumed"] is True
    assert second["handoff_review_decision"] == WORKER_BINDING_APPROVED
    assert second["handoff_review_next_certified_stage"] == "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW"
    assert second["authorization_created"] is False
    assert second["worker_invoked"] is False
    assert second["domain_created"] is False
    assert replay["review_decision"] == WORKER_BINDING_APPROVED
    assert "Handoff Review" in output[1]
    assert "Review Decision: WORKER_BINDING_APPROVED" in output[1]

