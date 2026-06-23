"""Tests for AIGOL_CONVERSATIONAL_OPENAI_OUTPUT_BUDGET_RUNTIME_V1."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import (
    CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET,
    CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS,
    OPENAI_OUTPUT_BUDGET_ARTIFACT_V1,
    build_parser,
    run_interactive_conversation,
)
from aigol.provider.providers.openai_provider import MAX_OPENAI_RESPONSE_CHARS, OpenAIProviderAdapter
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-06-06T00:00:00Z"
SESSION_ID = "SESSION-CONVERSATIONAL-OPENAI-OUTPUT-BUDGET-000001"
PROMPT = "I want to create the first real AiGOL product."


def _args(tmp_path):
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


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _bounded_response_text(provider_call: int) -> str:
    return json.dumps(
        {
            "findings": [f"Budgeted OpenAI cognition call {provider_call} stayed bounded."],
            "assumptions": ["Provider output is non-authoritative."],
            "alternatives": ["AI Decision Validator", "Managed governance review"],
            "risks": ["Commercial assumptions still require validation."],
            "uncertainties": ["First buyer remains open."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _install_budgeted_openai_adapter(monkeypatch):
    captured: dict[str, object] = {"payloads": []}

    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        captured["payloads"].append(payload)
        response_text = _bounded_response_text(len(captured["payloads"]))
        assert len(response_text) <= MAX_OPENAI_RESPONSE_CHARS
        return {
            "id": f"resp-budgeted-openai-{len(captured['payloads'])}",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": response_text,
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    def adapter() -> OpenAIProviderAdapter:
        return OpenAIProviderAdapter(
            api_key="test-openai-key",
            client=fake_client,
            max_output_tokens=CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS,
        )

    from aigol.cli import aigol_cli

    monkeypatch.setattr(aigol_cli, "_conversation_openai_provider_adapter", adapter)
    return captured


def _output_budget_artifact(turn_root, provider_id: str) -> dict:
    path = (
        turn_root
        / "ocs_llm_cognition_end_to_end"
        / "real_openai_provider_attachment"
        / provider_id
        / "000_openai_output_budget_recorded.json"
    )
    return json.loads(path.read_text())["artifact"]


def test_conversational_openai_output_budget_is_replay_visible_and_comparison_compatible(tmp_path, monkeypatch) -> None:
    output: list[str] = []
    captured = _install_budgeted_openai_adapter(monkeypatch)

    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence([PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    turn_root = tmp_path / "interactive_runtime" / SESSION_ID / "TURN-000001"
    provider_ids = turn["provider_ids"]
    budget_artifacts = {
        provider_id: _output_budget_artifact(turn_root, provider_id)
        for provider_id in provider_ids
    }

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == "OCS_LLM_COGNITION"
    assert turn["successful_provider_count"] == len(provider_ids)
    assert turn["comparison_artifact_hash"]
    assert len(captured["payloads"]) == len(provider_ids)
    assert all(payload["max_output_tokens"] == CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS for payload in captured["payloads"])

    for provider_id, artifact in budget_artifacts.items():
        assert artifact["artifact_type"] == OPENAI_OUTPUT_BUDGET_ARTIFACT_V1
        assert artifact["provider_id"] == provider_id
        assert artifact["max_output_tokens"] == CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS
        assert artifact["estimated_char_budget"] == CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET
        assert artifact["estimated_char_budget"] <= MAX_OPENAI_RESPONSE_CHARS
        assert artifact["budget_status"] == "ACTIVE"
        assert artifact["budget_deterministic"] is True
        assert artifact["provider_invocation_allowed"] is True
        assert artifact["fail_closed"] is True
        assert artifact["replay_visible"] is True
        assert artifact["artifact_hash"].startswith("sha256:")

    assert "OCS_LLM_COGNITION_END_TO_END" in output[0]


def test_conversational_openai_output_budget_fails_closed_when_estimate_exceeds_bound(tmp_path, monkeypatch) -> None:
    from aigol.cli import aigol_cli

    monkeypatch.setattr(
        aigol_cli,
        "CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET",
        MAX_OPENAI_RESPONSE_CHARS + 1,
    )

    try:
        aigol_cli._record_conversational_openai_output_budget(
            provider_id="openai",
            model="gpt-5.1",
            created_at=CREATED_AT,
            replay_dir=tmp_path,
        )
    except FailClosedRuntimeError as exc:
        assert str(exc) == "conversational OpenAI output budget exceeds provider response bound"
    else:
        raise AssertionError("expected output budget to fail closed")

    assert not (tmp_path / "000_openai_output_budget_recorded.json").exists()
