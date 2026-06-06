"""Tests for AIGOL_REAL_OPENAI_CONVERSATIONAL_ATTACHMENT_V1."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_runtime import reconstruct_provider_attachment_replay
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter


CREATED_AT = "2026-06-06T00:00:00Z"
SESSION_ID = "SESSION-REAL-OPENAI-CONVERSATIONAL-ATTACHMENT-000001"
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


def _response_text(provider_call: int) -> str:
    return json.dumps(
        {
            "findings": [f"OpenAI cognition call {provider_call} produced governed product analysis."],
            "assumptions": ["Provider output is non-authoritative and requires human review."],
            "alternatives": ["AI Decision Validator", "Licensed platform", "Managed governance review"],
            "risks": ["Commercial path remains underspecified."],
            "uncertainties": ["First buyer and packaging remain open."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _install_openai_adapter(monkeypatch):
    captured: dict[str, object] = {"call_count": 0}

    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        captured["call_count"] = int(captured["call_count"]) + 1
        captured["last_payload"] = payload
        captured["api_key"] = api_key
        captured["endpoint"] = endpoint
        captured["timeout_seconds"] = timeout_seconds
        return {
            "id": f"resp-real-openai-conversational-{captured['call_count']}",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": _response_text(int(captured["call_count"])),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    def adapter() -> OpenAIProviderAdapter:
        return OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client)

    from aigol.cli import aigol_cli

    monkeypatch.setattr(aigol_cli, "_conversation_openai_provider_adapter", adapter)
    return captured


def test_conversational_ocs_uses_real_openai_attachment_boundary(tmp_path, monkeypatch) -> None:
    output: list[str] = []
    captured = _install_openai_adapter(monkeypatch)

    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence([PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    turn_root = tmp_path / "interactive_runtime" / SESSION_ID / "TURN-000001"
    attachment_root = turn_root / "ocs_llm_cognition_end_to_end" / "real_openai_provider_attachment"
    openai_replay = reconstruct_provider_attachment_replay(attachment_root / "openai")
    comparison_replay = reconstruct_provider_attachment_replay(attachment_root / "openai-comparison")

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == "OCS_LLM_COGNITION"
    assert turn["provider_count"] > 0
    assert turn["provider_ids"] == ["openai", "openai-comparison"]
    assert turn["real_llm_provider_used_by_ocs"] is True
    assert "aigol-cognition-alpha" not in turn["provider_ids"]
    assert "aigol-cognition-beta" not in turn["provider_ids"]
    assert "providers: openai, openai-comparison" in output[0]
    assert "REAL_LLM_PROVIDER_USED_BY_OCS = true" in output[0]
    assert captured["call_count"] == 2
    assert captured["api_key"] == "test-openai-key"
    assert openai_replay["provider_id"] == "openai"
    assert comparison_replay["provider_id"] == "openai"
    assert openai_replay["provider_invoked"] is True
    assert comparison_replay["provider_invoked"] is True
