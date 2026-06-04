"""Tests for AIGOL_HUMAN_DECISION_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import run_conversation_native_development_intent_routing
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.human_decision_runtime import (
    APPROVE,
    CLARIFICATION_REQUIRED,
    GOVERNED_REJECTION_RECORDED,
    HUMAN_DECISION_RECORDED,
    MODIFICATION_REQUEST_RECORDED,
    REJECT,
    REQUEST_MODIFICATION,
    reconstruct_human_decision_replay,
    record_human_decision,
)


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-HUMAN-DECISION-000001"


def _args(tmp_path, *, session_id: str):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _approval_required(tmp_path):
    allocation = resume_conversation_session(
        session_id=SESSION_ID,
        runtime_root=tmp_path / "routing_runtime",
        created_at=CREATED_AT,
    )
    prompt_id = f"{SESSION_ID}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt="Improve trading strategy.",
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_required",
    )


@pytest.mark.parametrize(
    ("decision", "expected_status", "expected_terminal"),
    [
        (APPROVE, HUMAN_DECISION_RECORDED, "APPROVAL_DECISION_RECORDED"),
        (REJECT, GOVERNED_REJECTION_RECORDED, "GOVERNED_REJECTION_TERMINATED"),
        (REQUEST_MODIFICATION, MODIFICATION_REQUEST_RECORDED, CLARIFICATION_REQUIRED),
    ],
)
def test_human_decision_runtime_records_replay_visible_decisions(
    tmp_path,
    decision: str,
    expected_status: str,
    expected_terminal: str,
) -> None:
    approval_required = _approval_required(tmp_path)
    capture = record_human_decision(
        human_decision_id=f"HUMAN-DECISION-{decision}",
        approval_required_artifact=approval_required["conversation_to_ppp_handoff_execution_artifact"],
        decision=decision,
        decision_reason=f"Operator selected {decision}.",
        decided_by="human.operator",
        decided_at=CREATED_AT,
        replay_dir=tmp_path / f"decision_{decision.lower()}",
    )
    reconstructed = reconstruct_human_decision_replay(tmp_path / f"decision_{decision.lower()}")

    assert approval_required["terminal_status"] == HUMAN_APPROVAL_REQUIRED
    assert capture["decision_status"] == expected_status
    assert capture["terminal_status"] == expected_terminal
    assert capture["replay_visible"] is True
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["decision"] == decision
    assert reconstructed["terminal_status"] == expected_terminal


def test_interactive_cli_approval_decision_path_remains_existing_resume(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-HUMAN-DECISION-APPROVE-000001"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_status"] == HUMAN_APPROVAL_REQUIRED
    assert result["turns"][1]["response_source"] == "IMPLEMENTATION_APPROVAL_RESUME"
    assert result["turns"][1]["human_decision"] == APPROVE
    assert result["turns"][1]["human_decision_replay_reference"]
    assert "APPROVE" in output[0]
    assert "REJECT" in output[0]
    assert "REQUEST_MODIFICATION" in output[0]
    assert "approval_resume_status: IMPLEMENTATION_APPROVAL_RESUMED" in output[1]


def test_interactive_cli_reject_decision_records_terminal_rejection(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-HUMAN-DECISION-REJECT-000001"),
        input_func=_input_sequence(["Improve trading strategy.", "Reject", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert result["turns"][1]["response_source"] == "HUMAN_DECISION_RUNTIME"
    assert result["turns"][1]["human_decision"] == REJECT
    assert result["turns"][1]["response_status"] == "GOVERNED_REJECTION_TERMINATED"
    assert result["turns"][1]["implementation_rejected"] is True
    assert result["turns"][1]["execution_requested"] is False
    assert "Decision: REJECT" in output[1]


def test_interactive_cli_request_modification_records_clarification_state(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-HUMAN-DECISION-MODIFY-000001"),
        input_func=_input_sequence(["Improve trading strategy.", "Request modification", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert result["turns"][1]["response_source"] == "HUMAN_DECISION_RUNTIME"
    assert result["turns"][1]["human_decision"] == REQUEST_MODIFICATION
    assert result["turns"][1]["response_status"] == CLARIFICATION_REQUIRED
    assert result["turns"][1]["clarification_required"] is True
    assert result["turns"][1]["execution_requested"] is False
    assert "Decision: REQUEST_MODIFICATION" in output[1]
    assert "Clarification State: REQUIRED" in output[1]


def test_human_decision_runtime_preserves_authority_boundaries() -> None:
    import aigol.runtime.human_decision_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "dispatch_worker(" not in source
    assert "start_execution(" not in source
    assert "mutate_governance(" not in source
    assert "automatic_approval\": True" not in source
