"""Tests for AIGOL_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME_V1."""

from __future__ import annotations

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import (
    CREATE_DOMAIN_MARKETING,
    OCS_LLM_COGNITION,
    OPERATOR_DECISION_SUPPORT,
    SHOW_LATEST_REPLAY_CHAIN,
)
from aigol.runtime.conversational_routing_visibility_runtime import (
    CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1,
    MEDIUM,
    NO_CERTIFIED_WORKFLOW_MATCHED,
    ROUTING_FAILED_CLOSED,
    ROUTING_SELECTED,
    reconstruct_conversational_routing_visibility_replay,
)


CREATED_AT = "2026-06-06T00:00:00Z"


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
            "--workspace",
            str(tmp_path),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _routing_replay(tmp_path, session_id: str):
    return reconstruct_conversational_routing_visibility_replay(
        tmp_path / "interactive_runtime" / session_id / "TURN-000001" / "routing_visibility"
    )


def test_ocs_cognition_prompt_renders_and_reconstructs_competing_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-OCS-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(
            [
                "Should Sapianta primarily sell domains, license the platform, or offer managed services?",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)
    turn = result["turns"][0]

    assert turn["routing_visibility_artifact_type"] == CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1
    assert replay["workflow_id"] == OCS_LLM_COGNITION
    assert replay["routing_status"] == ROUTING_SELECTED
    assert replay["routing_confidence"] == MEDIUM
    assert OPERATOR_DECISION_SUPPORT in replay["competing_signals"]
    assert "sell domains" in replay["matched_signals"]
    assert "comparative strategic analysis" in replay["routing_reason"]
    assert output[0].splitlines()[0:4] == [
        "================================",
        "ROUTING DECISION",
        "workflow: OCS_LLM_COGNITION",
        "confidence: MEDIUM",
    ]
    assert "[1/8] Routing" in output[0]


def test_operator_decision_support_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-OPERATOR-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Which capability should we prioritize next?", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert replay["workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert replay["routing_confidence"] == "HIGH"
    assert "which" in replay["matched_signals"]
    assert replay["routing_reason"] == "Operator decision-support request detected."
    assert "workflow: OPERATOR_DECISION_SUPPORT" in output[0]


def test_domain_creation_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-DOMAIN-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert replay["workflow_id"] == CREATE_DOMAIN_MARKETING
    assert replay["routing_confidence"] == "HIGH"
    assert "create" in replay["matched_signals"]
    assert "domain" in replay["matched_signals"]
    assert "Native development intent signals detected." == replay["routing_reason"]
    assert "workflow: CREATE_DOMAIN_MARKETING" in output[0]


def test_replay_review_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-REPLAY-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Show latest replay chain.", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert replay["workflow_id"] == SHOW_LATEST_REPLAY_CHAIN
    assert replay["routing_confidence"] == "HIGH"
    assert replay["routing_reason"] == "Replay chain inspection request detected."
    assert "latest" in replay["matched_signals"]
    assert "workflow: SHOW_LATEST_REPLAY_CHAIN" in output[0]


def test_failed_routing_prompt_renders_visibility_before_fallback(tmp_path, monkeypatch) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-FAILED-000001"
    output: list[str] = []

    def provider_unavailable(**kwargs):
        prompt_id = kwargs["prompt_id"]
        return {
            "prompt_id": prompt_id,
            "response_status": "FAILED_CLOSED",
            "response_source": "UNAVAILABLE",
            "response_text": "",
            "conversation_replay_reference": "provider/conversation_response",
            "prompt_to_conversation_capture_hash": "sha256:provider-failure",
            "provider_used": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "dispatch_requested": False,
            "fail_closed": True,
            "failure_reason": "provider-assisted conversation failed closed: OpenAI provider unavailable",
            "canonical_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
            "current_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
            "latest_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
        }

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", provider_unavailable)

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["nonsense followup", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 1
    assert replay["workflow_id"] == NO_CERTIFIED_WORKFLOW_MATCHED
    assert replay["routing_status"] == ROUTING_FAILED_CLOSED
    assert replay["routing_confidence"] == "LOW"
    assert replay["matched_signals"] == []
    assert replay["competing_signals"] == []
    assert replay["routing_reason"] == "No certified workflow matched."
    assert output[0].splitlines()[0:3] == [
        "================================",
        "ROUTING FAILED CLOSED",
        "confidence: LOW",
    ]
    assert output[-1].startswith("FAILED_CLOSED:")
