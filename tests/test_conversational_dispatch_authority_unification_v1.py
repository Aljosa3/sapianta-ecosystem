"""Tests for AIGOL_CONVERSATIONAL_DISPATCH_AUTHORITY_UNIFICATION_V1."""

from __future__ import annotations

import json

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.conversational_cli_runtime import OCS_LLM_COGNITION, OPERATOR_DECISION_SUPPORT
from aigol.runtime.conversational_routing_visibility_runtime import (
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


def _visibility_replay(tmp_path, session_id: str):
    return reconstruct_conversational_routing_visibility_replay(
        tmp_path / "interactive_runtime" / session_id / "TURN-000001" / "routing_visibility"
    )


def _routing_decision_path(tmp_path, session_id: str):
    return (
        tmp_path
        / "interactive_runtime"
        / session_id
        / "TURN-000001"
        / "conversational_cli_routing"
        / "000_conversational_routing_decision_recorded.json"
    )


def _install_openai_adapter(monkeypatch):
    def fake_client(_payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-dispatch-authority-openai",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["OpenAI provided bounded OCS cognition."],
                                    "assumptions": ["Provider output remains non-authoritative."],
                                    "alternatives": ["AI Decision Validator", "Managed governance review"],
                                    "risks": ["Commercial direction remains underspecified."],
                                    "uncertainties": ["First customer segment remains open."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    def adapter() -> OpenAIProviderAdapter:
        return OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client)

    monkeypatch.setattr(aigol_cli, "_conversation_openai_provider_adapter", adapter)


def test_ocs_visibility_and_dispatch_share_authoritative_workflow(tmp_path, monkeypatch) -> None:
    session_id = "SESSION-DISPATCH-AUTHORITY-OCS-000001"
    prompt = "\n".join(
        [
            "I want to create the first real commercial Sapianta product.",
            "Use the current AiGOL architecture and repository state.",
            "Analyze the opportunity.",
            "Produce provider disagreements and a recommended commercialization path.",
            "Provide cognition output only.",
        ]
    )
    output: list[str] = []
    _install_openai_adapter(monkeypatch)

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    visibility = _visibility_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == OCS_LLM_COGNITION
    assert turn["routing_visibility_workflow_id"] == OCS_LLM_COGNITION
    assert visibility["workflow_id"] == OCS_LLM_COGNITION
    assert turn["response_source"] == "OCS_LLM_COGNITION_END_TO_END"
    assert turn["routing_visibility_workflow_id"] == turn["conversational_workflow_id"]
    assert "workflow: OCS_LLM_COGNITION" in output[0]
    assert "OCS LLM COGNITION END-TO-END" in output[0]
    assert _routing_decision_path(tmp_path, session_id).exists()


def test_operator_support_visibility_and_dispatch_share_authoritative_workflow(tmp_path) -> None:
    session_id = "SESSION-DISPATCH-AUTHORITY-OPERATOR-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Which provider should we use first?", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    visibility = _visibility_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert turn["routing_visibility_workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert visibility["workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert turn["response_source"] == "OPERATOR_DECISION_SUPPORT_RUNTIME"
    assert turn["routing_visibility_workflow_id"] == turn["conversational_workflow_id"]
    assert "workflow: OPERATOR_DECISION_SUPPORT" in output[0]
    assert "Recommendation Generated" in output[0]
    assert _routing_decision_path(tmp_path, session_id).exists()


def test_ordinary_prompt_routes_exactly_once_before_dispatch(tmp_path, monkeypatch) -> None:
    session_id = "SESSION-DISPATCH-AUTHORITY-ROUTE-ONCE-000001"
    output: list[str] = []
    original_route = aigol_cli.route_conversational_cli_intent
    calls: list[str] = []

    def counted_route(**kwargs):
        calls.append(kwargs["prompt_id"])
        return original_route(**kwargs)

    monkeypatch.setattr(aigol_cli, "route_conversational_cli_intent", counted_route)

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Which provider should we use first?", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert calls == [f"{session_id}:TURN-000001"]
    assert result["turns"][0]["routing_visibility_workflow_id"] == result["turns"][0]["conversational_workflow_id"]
