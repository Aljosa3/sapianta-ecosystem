"""Tests for AIGOL_OPERATOR_DECISION_SUPPORT_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import OPERATOR_DECISION_SUPPORT
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_decision_support_runtime import (
    CAPABILITY_PRIORITIZATION,
    DOMAIN_SELECTION,
    FINAL_CLASSIFICATION,
    OPERATOR_DECISION_SUPPORT_ARTIFACT_V1,
    PROVIDER_COMPARISON,
    RECOMMENDATION_GENERATED,
    is_operator_decision_support_prompt,
    reconstruct_operator_decision_support_replay,
    run_operator_decision_support,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-05T00:00:00Z"
SESSION_ID = "SESSION-OPERATOR-DECISION-SUPPORT-000001"


def _recommend(tmp_path, prompt: str):
    return run_operator_decision_support(
        recommendation_id="OPERATOR-DECISION-SUPPORT-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt=prompt,
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "decision_support",
    )


def _conversation_args(tmp_path):
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "aigol" / "runtime").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
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


@pytest.mark.parametrize(
    ("prompt", "category", "expected_recommendation"),
    [
        (
            "I want to create the first real AiGOL product domain.",
            DOMAIN_SELECTION,
            "SAPIANTA_AI_PR_GATE",
        ),
        (
            "Which capability should be implemented next?",
            CAPABILITY_PRIORITIZATION,
            "CLARIFICATION_RESPONSE_INGESTION",
        ),
        (
            "Which provider should be attached first?",
            PROVIDER_COMPARISON,
            "OPENAI_RESPONSES_PROVIDER",
        ),
    ],
)
def test_operator_decision_support_generates_replay_visible_recommendations(
    tmp_path, prompt: str, category: str, expected_recommendation: str
) -> None:
    capture = _recommend(tmp_path, prompt)
    replay = reconstruct_operator_decision_support_replay(tmp_path / "decision_support")
    artifact = capture["operator_decision_support_artifact"]
    llm_candidate = artifact["llm_analysis_candidate"]

    assert capture["final_classification"] == FINAL_CLASSIFICATION
    assert capture["recommendation_status"] == RECOMMENDATION_GENERATED
    assert artifact["artifact_type"] == OPERATOR_DECISION_SUPPORT_ARTIFACT_V1
    assert artifact["category"] == category
    assert artifact["recommendation"] == expected_recommendation
    assert artifact["alternatives"]
    assert artifact["risks"]
    assert artifact["confidence"]
    assert artifact["reasoning"]
    assert artifact["recommendation_hash"]
    assert artifact["human_authority"] == "APPROVE_REJECT_IGNORE"
    assert llm_candidate["can_analyze"] is True
    assert llm_candidate["can_recommend"] is True
    assert llm_candidate["provider_invoked"] is False
    assert llm_candidate["can_authorize"] is False
    assert llm_candidate["can_execute"] is False
    assert llm_candidate["can_approve"] is False
    assert llm_candidate["can_mutate_governance"] is False
    assert llm_candidate["can_create_domains"] is False
    assert replay["recommendation"] == expected_recommendation
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False
    assert replay["domain_created"] is False
    assert replay["approval_bypassed"] is False


def test_operator_decision_support_prompt_detection_is_conservative() -> None:
    assert is_operator_decision_support_prompt("Which provider should be attached first?") is True
    assert is_operator_decision_support_prompt("Which capability should be implemented next?") is True
    assert is_operator_decision_support_prompt("I want to create the first real AiGOL product domain.") is True
    assert is_operator_decision_support_prompt("Create a trading domain.") is False
    assert is_operator_decision_support_prompt("Show latest replay chain.") is False


def test_decision_support_cli_renders_recommendation(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "decision-support",
            "recommend",
            "--prompt",
            "I want to create the first real AiGOL product domain.",
            "--runtime-root",
            str(tmp_path / "cli_runtime"),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol decision-support recommend"
    assert result["recommendation_status"] == RECOMMENDATION_GENERATED
    assert "AIGOL OPERATOR DECISION SUPPORT" in rendered
    assert "Recommended: SAPIANTA_AI_PR_GATE" in rendered
    assert "Human Decision Required: Approve / Reject / Ignore" in rendered


def test_interactive_conversation_routes_decision_support_without_authority(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["I want to create the first real AiGOL product domain.", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    replay_path = (
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "operator_decision_support"
        / "000_operator_decision_support_recorded.json"
    )

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert turn["recommendation_category"] == DOMAIN_SELECTION
    assert turn["recommendation"] == "SAPIANTA_AI_PR_GATE"
    assert turn["human_authority"] == "APPROVE_REJECT_IGNORE"
    assert turn["provider_invoked"] is False
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert turn["domain_created"] is False
    assert "Recommended: SAPIANTA_AI_PR_GATE" in output[0]
    assert replay_path.exists()


def test_replay_tampering_is_detected(tmp_path) -> None:
    _recommend(tmp_path, "Which provider should be attached first?")
    path = tmp_path / "decision_support" / "000_operator_decision_support_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["recommendation"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_operator_decision_support_replay(tmp_path / "decision_support")
