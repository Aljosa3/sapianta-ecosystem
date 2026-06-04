"""Tests for AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import (
    ADD_PROVIDER,
    CREATE_DOMAIN,
    CREATE_WORKER,
    IMPROVE_EXISTING_CAPABILITY,
    NATIVE_DEVELOPMENT_INTENT_ROUTED,
    is_conversation_native_development_intent,
    reconstruct_conversation_native_development_intent_routing_replay,
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_to_implementation_handoff_runtime import IMPLEMENTATION_HANDOFF_CREATED
from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-03T13:30:00+00:00"
SESSION_ID = "SESSION-NATIVE-INTENT-ROUTING-000001"


def _args(tmp_path, *, session_id: str = SESSION_ID):
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


def _routing(tmp_path, *, prompt: str):
    runtime_root = tmp_path / "runtime"
    allocation = resume_conversation_session(session_id=SESSION_ID, runtime_root=runtime_root, created_at=CREATED_AT)
    prompt_id = f"{SESSION_ID}:{allocation['next_turn_id']}"
    return run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )


@pytest.mark.parametrize(
    ("prompt", "intent_class", "target_domain", "target_resource"),
    [
        ("Create a marketing domain.", CREATE_DOMAIN, "MARKETING", "DOMAIN"),
        ("Add provider Anthropic.", ADD_PROVIDER, "AIGOL_CORE", "PROVIDER"),
        ("Create sentiment analysis worker.", CREATE_WORKER, "MARKETING", "WORKER"),
        ("Improve trading strategy.", IMPROVE_EXISTING_CAPABILITY, "TRADING", "CAPABILITY"),
    ],
)
def test_classifies_supported_native_development_intents(
    tmp_path,
    prompt: str,
    intent_class: str,
    target_domain: str,
    target_resource: str,
) -> None:
    capture = _routing(tmp_path, prompt=prompt)
    reconstructed = reconstruct_conversation_native_development_intent_routing_replay(tmp_path / "routing")

    assert capture["routing_status"] == NATIVE_DEVELOPMENT_INTENT_ROUTED
    assert capture["intent_class"] == intent_class
    assert capture["target_domain"] == target_domain
    assert capture["target_resource"] == target_resource
    assert capture["next_pipeline_stage"] == "NATIVE_DEVELOPMENT_INTAKE"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["intent_class"] == intent_class
    assert reconstructed["turn_id"] == "TURN-000001"


def test_workstation_remains_clarification_not_native_development() -> None:
    assert is_conversation_native_development_intent("Create a workstation.") is False


def test_interactive_conversation_routes_acceptance_prompts_without_provider_entry_failure(tmp_path) -> None:
    prompts = [
        "Create a marketing domain.",
        "Add provider Anthropic.",
        "Create sentiment analysis worker.",
        "Improve trading strategy.",
        "exit",
    ]
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence(prompts),
        output_func=output.append,
    )

    assert result["turn_count"] == 4
    assert result["failed_turns"] == 0
    assert [turn["turn_id"] for turn in result["turns"]] == [
        "TURN-000001",
        "TURN-000002",
        "TURN-000003",
        "TURN-000004",
    ]
    assert [turn["response_status"] for turn in result["turns"]] == [
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        HUMAN_APPROVAL_REQUIRED,
    ]
    assert all(turn["response_source"] == "CONVERSATION_TO_PPP_HANDOFF_EXECUTION" for turn in result["turns"])
    assert all(turn["recognized_development_task"] is True for turn in result["turns"])
    assert result["turns"][0]["intent_class"] == CREATE_DOMAIN
    assert result["turns"][1]["target_provider"] == "ANTHROPIC"
    assert result["turns"][2]["target_worker_family"] == "SENTIMENT_ANALYSIS"
    assert result["turns"][3]["intent_class"] == IMPROVE_EXISTING_CAPABILITY
    assert "conversation_to_ppp_terminal_status: IMPLEMENTATION_HANDOFF_CREATED" in output[0]
    assert "approval_status: HUMAN_APPROVAL_REQUIRED" in output[3]


def test_turn_allocation_uses_fresh_resume_state_for_each_turn(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-TURN-ALLOCATION-FIX-000001"),
        input_func=_input_sequence(["Create sentiment analysis worker.", "Create sentiment analysis worker.", "exit"]),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert [turn["turn_id"] for turn in result["turns"]] == ["TURN-000001", "TURN-000002"]
    assert "turn allocation mismatch" not in "\n".join(output)


def test_routing_fails_closed_when_turn_allocation_invalid(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    allocation = resume_conversation_session(session_id=SESSION_ID, runtime_root=runtime_root, created_at=CREATED_AT)
    capture = run_conversation_native_development_intent_routing(
        routing_id="ROUTING-BAD-TURN",
        prompt_id=f"{SESSION_ID}:TURN-999999",
        human_prompt="Create a marketing domain.",
        canonical_chain_id="CHAIN-BAD-TURN",
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad_turn",
    )

    assert capture["routing_status"] == "FAILED_CLOSED"
    assert "turn allocation invalid" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_routing_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    _routing(tmp_path, prompt="Create a marketing domain.")
    path = tmp_path / "routing" / "002_native_development_intent_routed_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["intent_class"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_native_development_intent_routing_replay(tmp_path / "routing")


def test_routing_runtime_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.conversation_native_development_intent_routing as runtime

    source = inspect.getsource(runtime)

    assert "run_provider_attachment(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
