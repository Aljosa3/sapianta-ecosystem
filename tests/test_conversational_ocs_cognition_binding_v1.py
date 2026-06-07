"""Tests for AIGOL_CONVERSATIONAL_OCS_COGNITION_BINDING_V1."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.conversational_cli_runtime import OCS_LLM_COGNITION
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1,
    STATUS_COMPLETED,
    reconstruct_ocs_llm_cognition_end_to_end_replay,
)


CREATED_AT = "2026-06-06T00:00:00Z"
SESSION_ID = "SESSION-CONVERSATIONAL-OCS-COGNITION-000001"
PROMPT = "I want to create the first real commercial Sapianta product."
PROGRESS_LINES = [
    "[1/8] Routing",
    "[2/8] Cognition",
    "[3/8] Provider Invocation",
    "[4/8] Comparison",
    "[5/8] Continuity",
    "[6/8] Clarification",
    "[7/8] Result Assembly",
    "[8/8] Replay",
]


def _progress_lines(rendered: str) -> list[str]:
    return [line for line in rendered.splitlines() if line.startswith("[") and len(line) > 1 and line[1].isdigit()]


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


def _openai_response_text() -> str:
    return json.dumps(
        {
            "findings": [
                "The prompt requests governed product cognition before any execution.",
                "The real OpenAI provider is attached as a non-authoritative cognition source.",
            ],
            "assumptions": [
                "The operator wants analysis and recommendations, not automatic mutation.",
            ],
            "alternatives": [
                "AI Decision Validator",
                "Governed platform licensing",
                "Managed governance review service",
            ],
            "risks": [
                "Provider output remains untrusted until normalized and reviewed.",
            ],
            "uncertainties": [
                "The first buyer profile remains underspecified.",
            ],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _install_openai_adapter(monkeypatch):
    captured: dict[str, object] = {}

    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        captured["payload"] = payload
        captured["api_key"] = api_key
        captured["endpoint"] = endpoint
        captured["timeout_seconds"] = timeout_seconds
        return {
            "id": "resp-conversational-openai-001",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": _openai_response_text(),
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


def test_broad_conversational_prompt_runs_certified_ocs_cognition_path(tmp_path, monkeypatch) -> None:
    output: list[str] = []
    captured = _install_openai_adapter(monkeypatch)

    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence([PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    replay_dir = (
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "ocs_llm_cognition_end_to_end"
    )
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(replay_dir)

    assert result["failed_turns"] == 0
    assert turn["response_status"] == STATUS_COMPLETED
    assert turn["response_source"] == "OCS_LLM_COGNITION_END_TO_END"
    assert turn["conversational_workflow_id"] == OCS_LLM_COGNITION
    assert turn["ocs_llm_cognition_artifact_type"] == OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1
    assert turn["provider_invoked"] is True
    assert turn["successful_provider_count"] == 1
    assert turn["provider_ids"] == ["openai"]
    assert "openai" in turn["provider_ids"]
    assert turn["real_llm_provider_used_by_ocs"] is True
    assert turn["cognition_artifact_count"] == 1
    assert captured["api_key"] == "test-openai-key"
    assert turn["comparison_artifact_hash"]
    assert turn["continuity_artifact_hash"]
    assert turn["clarification_artifact_hash"]
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert turn["approval_created"] is False
    assert _progress_lines(output[0])[:8] == PROGRESS_LINES
    assert "AIGOL OCS LLM COGNITION END-TO-END" in output[0]
    assert "REAL_LLM_PROVIDER_USED_BY_OCS = true" in output[0]
    assert output[0].splitlines()[-8:-2] == [
        "================================",
        "TURN COMPLETED",
        "turn_id: TURN-000001",
        "providers: openai",
        "status: COMPLETED",
        "result_delivered: TRUE",
    ]
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["provider_count"] == 1
    assert replay["cognition_artifact_count"] == 1
    assert replay["stage_replay"]["cognition_comparison"]["final_status"] == STATUS_COMPLETED
    assert replay["stage_replay"]["context"]["context_status"] == "OCS_CONTEXT_ASSEMBLED"
    assert replay["stage_replay"]["cognition_comparison"]["source_cognition_artifact_count"] == 1
    assert replay["stage_replay"]["continuity_and_clarification"]["clarification_candidate_count"] >= 1


def test_legacy_provider_unavailable_fallback_remains_available_for_narrow_prompt(tmp_path, monkeypatch) -> None:
    from aigol.cli import aigol_cli

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
            "canonical_chain_id": "CHAIN-LEGACY-FALLBACK-000001",
            "current_chain_id": "CHAIN-LEGACY-FALLBACK-000001",
            "latest_chain_id": "CHAIN-LEGACY-FALLBACK-000001",
        }

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", provider_unavailable)

    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence(["Create a workstation.", "exit"]),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_status"] == "HUMAN_CLARIFICATION_REQUIRED"
    assert "HUMAN_CLARIFICATION_REQUIRED" in output[0]
