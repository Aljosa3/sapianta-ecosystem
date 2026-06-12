"""Tests for AIGOL_UNIVERSAL_INTAKE_LAYER_V1."""

from __future__ import annotations

import json

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.conversational_cli_runtime import OCS_LLM_COGNITION
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import STATUS_COMPLETED
from aigol.runtime.universal_intake_layer_runtime import (
    DOMAIN_INTAKE,
    NATIVE_DEVELOPMENT_INTAKE,
    OCS_COGNITION_INTAKE,
    UNIVERSAL_INTAKE_ARTIFACT_V1,
    UNIVERSAL_INTAKE_RECORDED,
    reconstruct_universal_intake_replay,
)


CREATED_AT = "2026-06-12T00:00:00Z"
NATIVE_PROMPT = (
    "Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1. Goal: Extend the certified "
    "provider-neutral external worker architecture with Claude support while reusing existing governance, "
    "replay, validation, mutation, and worker lifecycle infrastructure."
)
OCS_PROMPT = "I want to create the first real commercial Sapianta product."


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


def _universal_replay(tmp_path, session_id: str):
    return reconstruct_universal_intake_replay(
        tmp_path / "interactive_runtime" / session_id / "TURN-000001" / "universal_intake"
    )


def _install_openai_adapter(monkeypatch) -> None:
    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-universal-intake-ocs-001",
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
                                    "findings": ["Governed cognition is required before execution."],
                                    "assumptions": ["The prompt asks for product recommendation."],
                                    "alternatives": ["AI Decision Validator", "Platform licensing"],
                                    "risks": ["Provider output remains non-authoritative."],
                                    "uncertainties": ["Buyer profile remains open."],
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

    monkeypatch.setattr(
        aigol_cli,
        "_conversation_openai_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client),
    )


def test_universal_intake_classifies_domain_prompt_without_downstream_change(tmp_path) -> None:
    session_id = "SESSION-UNIVERSAL-INTAKE-DOMAIN-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Create a compliance domain.", "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    replay = _universal_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert turn["response_source"] == "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    assert turn["universal_intake_artifact_type"] == UNIVERSAL_INTAKE_ARTIFACT_V1
    assert turn["universal_intake_status"] == UNIVERSAL_INTAKE_RECORDED
    assert turn["universal_intake_classification"] == DOMAIN_INTAKE
    assert replay["intake_classification"] == DOMAIN_INTAKE
    assert replay["next_backbone_target"] == "CLARIFICATION"
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["approval_created"] is False
    assert replay["ppp_artifact_mutated"] is False
    assert replay["source_router_replay_reference"].endswith("source_router")


def test_universal_intake_classifies_native_development_without_downstream_change(tmp_path) -> None:
    session_id = "SESSION-UNIVERSAL-INTAKE-NATIVE-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence([NATIVE_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    replay = _universal_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert turn["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert turn["context_status"] == "CONTEXT_ASSEMBLED"
    assert turn["universal_intake_classification"] == NATIVE_DEVELOPMENT_INTAKE
    assert replay["intake_classification"] == NATIVE_DEVELOPMENT_INTAKE
    assert replay["cognition_required"] is False
    assert replay["next_backbone_target"] == "PPP_ROUTING"
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["approval_created"] is False
    assert replay["ppp_artifact_mutated"] is False


def test_universal_intake_classifies_ocs_prompt_without_downstream_change(tmp_path, monkeypatch) -> None:
    session_id = "SESSION-UNIVERSAL-INTAKE-OCS-000001"
    output: list[str] = []
    _install_openai_adapter(monkeypatch)

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence([OCS_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    replay = _universal_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert turn["response_status"] == STATUS_COMPLETED
    assert turn["response_source"] == "OCS_LLM_COGNITION_END_TO_END"
    assert turn["conversational_workflow_id"] == OCS_LLM_COGNITION
    assert turn["universal_intake_classification"] == OCS_COGNITION_INTAKE
    assert replay["intake_classification"] == OCS_COGNITION_INTAKE
    assert replay["cognition_required"] is True
    assert replay["next_backbone_target"] == "OCS_COGNITION"
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["approval_created"] is False
    assert replay["ppp_artifact_mutated"] is False
