"""Tests for AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_implementation_handoff_runtime import IMPLEMENTATION_HANDOFF_CREATED
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    reconstruct_conversation_to_ppp_handoff_execution_replay,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.development_proposal_contract_runtime import DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unified_resource_selection_ppp_integration import RESOURCE_PPP_INTEGRATED
from aigol.runtime.unified_resource_selection_runtime import RESOURCE_SELECTION_SUCCEEDED


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-CONVERSATION-PPP-HANDOFF-000001"


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


def _routed(tmp_path, *, prompt: str, session_id: str = SESSION_ID):
    runtime_root = tmp_path / "routing_runtime"
    allocation = resume_conversation_session(session_id=session_id, runtime_root=runtime_root, created_at=CREATED_AT)
    prompt_id = f"{session_id}:{allocation['next_turn_id']}"
    return run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )


def _execute(tmp_path, *, prompt: str):
    routed = _routed(tmp_path, prompt=prompt)
    prompt_id = routed["native_development_intent_routed_artifact"]["canonical_chain_id"]
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution",
    )


@pytest.mark.parametrize(
    "prompt",
    [
        "Create a marketing domain.",
        "Add provider Anthropic.",
        "Add provider Claude Code.",
        "Create a server management domain.",
        "Create sentiment analysis worker.",
        "Create a filesystem worker.",
        "Create a monitoring worker.",
    ],
)
def test_native_development_conversation_intents_reach_implementation_handoff(tmp_path, prompt: str) -> None:
    capture = _execute(tmp_path, prompt=prompt)
    reconstructed = reconstruct_conversation_to_ppp_handoff_execution_replay(tmp_path / "execution")

    assert capture["terminal_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert capture["resource_selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["ppp_integration_status"] == RESOURCE_PPP_INTEGRATED
    assert capture["proposal_production_status"] == "PROVIDER_PROPOSAL_PRODUCED"
    assert capture["proposal_validation_status"] == DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
    assert capture["approval_status"] == "APPROVAL_NOT_REQUIRED_FOR_HANDOFF"
    assert capture["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert capture["handoff_reference"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["terminal_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert reconstructed["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED


def test_trading_improvement_requires_human_approval_before_handoff(tmp_path) -> None:
    capture = _execute(tmp_path, prompt="Improve trading strategy.")
    reconstructed = reconstruct_conversation_to_ppp_handoff_execution_replay(tmp_path / "execution")

    assert capture["terminal_status"] == HUMAN_APPROVAL_REQUIRED
    assert capture["intent_class"] == "IMPROVE_EXISTING_CAPABILITY"
    assert capture["approval_status"] == HUMAN_APPROVAL_REQUIRED
    assert capture["handoff_status"] is None
    assert capture["handoff_reference"] is None
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["terminal_status"] == HUMAN_APPROVAL_REQUIRED
    assert reconstructed["authorization_created"] is False


def test_interactive_conversation_continues_marketing_prompt_beyond_native_intake(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CONVERSATION-PPP-CLI-000001"),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_source"] == "CONVERSATION_TO_PPP_HANDOFF_EXECUTION"
    assert result["turns"][0]["response_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert result["turns"][0]["conversation_to_ppp_terminal_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert result["turns"][0]["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert "conversation_to_ppp_terminal_status: IMPLEMENTATION_HANDOFF_CREATED" in output[0]
    assert "NATIVE_DEVELOPMENT_INTAKE" not in output[0]


def test_interactive_conversation_routes_acceptance_scenarios_to_terminal_states(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CONVERSATION-PPP-ACCEPTANCE-000001"),
        input_func=_input_sequence(
            [
                "Create a marketing domain.",
                "Add provider Anthropic.",
                "Add provider Claude Code.",
                "Create a server management domain.",
                "Create sentiment analysis worker.",
                "Create a filesystem worker.",
                "Create a monitoring worker.",
                "Improve trading strategy.",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert [turn["response_status"] for turn in result["turns"]] == [
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        IMPLEMENTATION_HANDOFF_CREATED,
        HUMAN_APPROVAL_REQUIRED,
    ]
    assert all(turn["response_source"] == "CONVERSATION_TO_PPP_HANDOFF_EXECUTION" for turn in result["turns"])
    assert "approval_status: HUMAN_APPROVAL_REQUIRED" in output[7]


def test_handoff_execution_fails_closed_on_invalid_routing_artifact(tmp_path) -> None:
    capture = run_conversation_to_ppp_handoff_execution(
        execution_id="CONVERSATION-PPP-HANDOFF-BAD",
        native_development_intent_routed_artifact={"artifact_type": "WRONG"},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad",
    )

    assert capture["terminal_status"] == "FAILED_CLOSED"
    assert "invalid routed intent" in capture["failure_reason"]
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_handoff_execution_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    _execute(tmp_path, prompt="Create a marketing domain.")
    path = tmp_path / "execution" / "000_conversation_to_ppp_handoff_execution_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["terminal_status"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_to_ppp_handoff_execution_replay(tmp_path / "execution")


def test_conversation_to_ppp_handoff_execution_preserves_authority_boundaries() -> None:
    import aigol.runtime.conversation_to_ppp_handoff_execution as runtime

    source = inspect.getsource(runtime)

    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "authorize_execution(" not in source
    assert "mutate_governance(" not in source
