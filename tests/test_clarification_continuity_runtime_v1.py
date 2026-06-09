"""Tests for AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.clarification_lifecycle_resolution_runtime import (
    CLARIFICATION_ACTIVE,
    CLARIFICATION_RESOLVED,
    CLARIFICATION_SUPERSEDED,
    resolve_clarification_lifecycle,
)
from aigol.runtime.clarification_continuity_runtime import (
    FAILED_CLOSED,
    WORKFLOW_RESUME_READY,
    reconstruct_clarification_continuity_replay,
    run_clarification_continuity,
)
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unknown_domain_clarification_runtime import run_unknown_domain_clarification_workflow


CREATED_AT = "2026-06-08T00:00:00Z"
SESSION_ID = "SESSION-CLARIFICATION-CONTINUITY-000001"
PROMPT = "Create a new governed domain called PilotDomain."
REPLY = "\n".join(
    [
        "Primary purpose: prove governed pilot domain intake.",
        "Expected capabilities: domain scaffolding review and bounded execution planning.",
        "Target users: internal operators.",
    ]
)
STRUCTURED_REPLY_WITH_GOVERNED_DOMAIN_TEXT = "\n".join(
    [
        "Primary purpose:",
        "Create a safe pilot governed domain.",
        "",
        "Expected capabilities:",
        "Clarification handling and bounded workflow resume.",
        "",
        "Target users:",
        "Internal operators.",
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


def _seed_open_clarification(session_root: Path, turn_id: str = "TURN-000001", prompt: str = PROMPT) -> str:
    prompt_id = f"{SESSION_ID}:{turn_id}"
    turn_root = session_root / turn_id
    route_conversational_cli_intent(
        routing_id=f"{prompt_id}:CONVERSATIONAL-CLI-ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "conversational_cli_routing",
    )
    run_unknown_domain_clarification_workflow(
        clarification_id=f"{prompt_id}:UNKNOWN-DOMAIN-CLARIFICATION",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "unknown_domain_clarification",
    )
    return prompt_id


def _run_continuity(tmp_path, session_root: Path, *, current_chain_id: str | None = None):
    return run_clarification_continuity(
        continuity_id=f"{SESSION_ID}:TURN-000002:CLARIFICATION-CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{SESSION_ID}:TURN-000002",
        operator_reply=REPLY,
        current_chain_id=current_chain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )


def test_interactive_clarification_reply_resumes_without_provider_fallback(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, "exit"]),
        output_func=output.append,
    )
    first, second = result["turns"]
    replay = reconstruct_clarification_continuity_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000002"
        / "clarification_continuity"
    )

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert first["clarification_required"] is True
    assert second["response_status"] == WORKFLOW_RESUME_READY
    assert second["response_source"] == "CLARIFICATION_CONTINUITY_RUNTIME"
    assert second["open_clarification_detected"] is True
    assert second["operator_reply_bound"] is True
    assert second["clarification_resolved"] is True
    assert second["workflow_resumed"] is True
    assert second["proposed_domain"] == "PilotDomain"
    assert second["provider_invoked"] is False
    assert second["worker_invoked"] is False
    assert second["authorization_created"] is False
    assert second["execution_requested"] is False
    assert replay["workflow_resumed"] is True
    assert "Reply Bound" in output[1]
    assert "Clarification Resolved" in output[1]
    assert "Workflow Resumed" in output[1]


def test_structured_fresh_domain_reply_binds_and_resumes_even_with_governed_domain_text(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "Create a new governed domain called FreshDomain.",
                STRUCTURED_REPLY_WITH_GOVERNED_DOMAIN_TEXT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    first, second = result["turns"]
    replay = reconstruct_clarification_continuity_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000002"
        / "clarification_continuity"
    )

    assert result["failed_turns"] == 0
    assert first["proposed_domain"] == "FreshDomain"
    assert second["response_source"] == "CLARIFICATION_CONTINUITY_RUNTIME"
    assert second["proposed_domain"] == "FreshDomain"
    assert second["operator_reply_bound"] is True
    assert second["clarification_resolved"] is True
    assert second["workflow_resumed"] is True
    assert second["provider_invoked"] is False
    assert second["worker_invoked"] is False
    assert second["domain_created"] is False
    assert replay["workflow_resumed"] is True
    assert "Reply Bound" in output[1]
    assert "Clarification Resolved" in output[1]
    assert "Workflow Resumed" in output[1]


def test_unrelated_reply_to_active_clarification_fails_closed_without_provider_fallback(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "Create a new governed domain called FreshDomain.",
                "This is unrelated text that does not answer the requested fields.",
                "exit",
            ]
        ),
        output_func=output.append,
    )
    first, second = result["turns"]

    assert result["failed_turns"] == 1
    assert first["proposed_domain"] == "FreshDomain"
    assert second["response_status"] == "FAILED_CLOSED"
    assert second["response_source"] == "UNAVAILABLE"
    assert "reply does not match active clarification scope" in second["failure_reason"]
    assert second["provider_invoked"] is False
    assert second["worker_invoked"] is False
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[1]


def test_new_domain_request_does_not_attach_to_unrelated_active_clarification(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "Create a compliance domain.",
                "Create a new governed domain called FreshDomain.",
                "exit",
            ]
        ),
        output_func=output.append,
    )
    first, second = result["turns"]
    lifecycle = resolve_clarification_lifecycle(session_root=tmp_path / "interactive_runtime" / SESSION_ID)

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert first["response_source"] == "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    assert first["proposed_domain"] == "COMPLIANCE"
    assert second["response_source"] == "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    assert second["proposed_domain"] == "FreshDomain"
    assert second["clarification_required"] is True
    assert "Clarification Resolved" not in output[1]
    assert "Proposed Domain: FreshDomain" in output[1]
    assert [state["lifecycle_status"] for state in lifecycle["lifecycle_summary"]] == [
        CLARIFICATION_SUPERSEDED,
        CLARIFICATION_ACTIVE,
    ]
    assert lifecycle["active_clarification"]["clarification_request_artifact"]["proposed_domain"] == "FreshDomain"


def test_later_reply_binds_to_fresh_domain_not_prior_compliance(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "Create a compliance domain.",
                "Create a new governed domain called FreshDomain.",
                REPLY,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    first, second, third = result["turns"]
    lifecycle = resolve_clarification_lifecycle(session_root=tmp_path / "interactive_runtime" / SESSION_ID)

    assert result["turn_count"] == 3
    assert result["failed_turns"] == 0
    assert first["proposed_domain"] == "COMPLIANCE"
    assert second["proposed_domain"] == "FreshDomain"
    assert third["response_source"] == "CLARIFICATION_CONTINUITY_RUNTIME"
    assert third["proposed_domain"] == "FreshDomain"
    assert third["clarification_resolved"] is True
    assert third["workflow_resumed"] is True
    assert third["provider_invoked"] is False
    assert third["worker_invoked"] is False
    assert third["domain_created"] is False
    assert "Proposed Domain: FreshDomain" in output[2]
    assert "Proposed Domain: COMPLIANCE" not in output[2]
    assert lifecycle["active_clarification_count"] == 0


def test_clarification_continuity_fails_closed_without_state(tmp_path) -> None:
    capture = _run_continuity(tmp_path, tmp_path / "missing_session")

    assert capture["response_status"] == FAILED_CLOSED
    assert "missing clarification state" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_lifecycle_resolution_allows_only_latest_open_clarification_to_be_active(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    _seed_open_clarification(session_root, "TURN-000001")
    _seed_open_clarification(
        session_root,
        "TURN-000002",
        "Create a new governed domain called SecondDomain.",
    )
    lifecycle = resolve_clarification_lifecycle(session_root=session_root)

    capture = _run_continuity(tmp_path, session_root)

    assert lifecycle["active_clarification_count"] == 1
    assert [state["lifecycle_status"] for state in lifecycle["lifecycle_summary"]] == [
        CLARIFICATION_SUPERSEDED,
        CLARIFICATION_ACTIVE,
    ]
    assert capture["response_status"] == WORKFLOW_RESUME_READY
    assert capture["proposed_domain"] == "SecondDomain"
    assert capture["execution_requested"] is False


def test_resolved_clarifications_are_not_considered_active(tmp_path) -> None:
    output: list[str] = []
    run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, "exit"]),
        output_func=output.append,
    )
    session_root = tmp_path / "interactive_runtime" / SESSION_ID
    lifecycle = resolve_clarification_lifecycle(session_root=session_root)

    assert lifecycle["active_clarification_count"] == 0
    assert lifecycle["lifecycle_summary"][0]["lifecycle_status"] == CLARIFICATION_RESOLVED


def test_clarification_continuity_fails_closed_on_chain_mismatch(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    _seed_open_clarification(session_root)

    capture = _run_continuity(tmp_path, session_root, current_chain_id="OTHER-CHAIN")

    assert capture["response_status"] == FAILED_CLOSED
    assert "clarification chain mismatch" in capture["failure_reason"]


def test_clarification_continuity_fails_closed_on_replay_mismatch(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    _seed_open_clarification(session_root)
    request_path = (
        session_root
        / "TURN-000001"
        / "unknown_domain_clarification"
        / "001_clarification_request_recorded.json"
    )
    wrapper = json.loads(request_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposed_domain"] = "CORRUPTED"
    request_path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = _run_continuity(tmp_path, session_root)

    assert capture["response_status"] == FAILED_CLOSED
    assert "replay mismatch" in capture["failure_reason"]


def test_clarification_continuity_fails_closed_on_workflow_mismatch(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    _seed_open_clarification(session_root)
    routing_path = (
        session_root
        / "TURN-000001"
        / "conversational_cli_routing"
        / "001_conversational_workflow_selection_recorded.json"
    )
    wrapper = json.loads(routing_path.read_text(encoding="utf-8"))
    artifact = wrapper["artifact"]
    artifact["workflow_id"] = "DEFAULT_PROVIDER_ASSISTED_CONVERSATION"
    artifact_hash_input = dict(artifact)
    artifact_hash_input.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact_hash_input)
    wrapper_hash_input = dict(wrapper)
    wrapper_hash_input.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper_hash_input)
    routing_path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = _run_continuity(tmp_path, session_root)

    assert capture["response_status"] == FAILED_CLOSED
    assert "workflow mismatch" in capture["failure_reason"]
