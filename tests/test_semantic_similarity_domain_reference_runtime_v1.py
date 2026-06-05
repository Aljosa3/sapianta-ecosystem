"""Tests for AIGOL_SEMANTIC_SIMILARITY_AND_DOMAIN_REFERENCE_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import CREATE_DOMAIN_TRADING, DOMAIN_ADAPTATION_REFERENCE
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.semantic_similarity_domain_reference_runtime import (
    CLARIFICATION_REQUIRED,
    DOMAIN_ADAPTATION,
    DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1,
    DOMAIN_ADAPTATION_CANDIDATE_CREATED,
    DOMAIN_REFERENCE_ARTIFACT_V1,
    DOMAIN_REFERENCE_RESOLVED,
    FINAL_CLASSIFICATION,
    SEMANTIC_SIMILARITY_ARTIFACT_V1,
    is_domain_reference_adaptation_prompt,
    reconstruct_semantic_similarity_domain_reference_replay,
    run_semantic_similarity_domain_reference_resolution,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-05T00:00:00Z"
SESSION_ID = "SESSION-SEMANTIC-DOMAIN-REFERENCE-000001"


def _resolve(tmp_path, prompt: str):
    return run_semantic_similarity_domain_reference_resolution(
        resolution_id="DOMAIN-REFERENCE-RESOLUTION-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt=prompt,
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_reference",
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
    ("prompt", "source_domain", "target_domain"),
    [
        ("Create something similar to the trading domain but focused on healthcare.", "TRADING", "HEALTHCARE"),
        ("Create a healthcare version of the trading domain.", "TRADING", "HEALTHCARE"),
        ("Use the compliance domain as a basis for a financial compliance domain.", "COMPLIANCE", "FINANCIAL_COMPLIANCE"),
    ],
)
def test_semantic_domain_reference_prompts_create_adaptation_candidates(
    tmp_path, prompt: str, source_domain: str, target_domain: str
) -> None:
    capture = _resolve(tmp_path, prompt)
    replay = reconstruct_semantic_similarity_domain_reference_replay(tmp_path / "domain_reference")
    reference = capture["domain_reference_artifact"]
    similarity = capture["semantic_similarity_artifact"]
    candidate = capture["domain_adaptation_candidate_artifact"]

    assert capture["final_classification"] == FINAL_CLASSIFICATION
    assert capture["resolution_status"] == DOMAIN_ADAPTATION_CANDIDATE_CREATED
    assert reference["artifact_type"] == DOMAIN_REFERENCE_ARTIFACT_V1
    assert reference["reference_status"] == DOMAIN_REFERENCE_RESOLVED
    assert reference["referenced_domain_identity"] == source_domain
    assert reference["referenced_capability_identities"]
    assert reference["referenced_runtime_identities"]
    assert similarity["artifact_type"] == SEMANTIC_SIMILARITY_ARTIFACT_V1
    assert candidate["artifact_type"] == DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1
    assert candidate["source_domain"] == source_domain
    assert candidate["target_domain"] == target_domain
    assert candidate["operation"] == DOMAIN_ADAPTATION
    assert candidate["clarification_required"] is False
    assert replay["source_domain"] == source_domain
    assert replay["target_domain"] == target_domain
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False
    assert replay["domain_created"] is False


def test_missing_target_domain_enters_clarification_required(tmp_path) -> None:
    capture = _resolve(tmp_path, "Create something similar to the trading domain.")
    candidate = capture["domain_adaptation_candidate_artifact"]
    replay = reconstruct_semantic_similarity_domain_reference_replay(tmp_path / "domain_reference")

    assert capture["resolution_status"] == CLARIFICATION_REQUIRED
    assert candidate["source_domain"] == "TRADING"
    assert candidate["target_domain"] is None
    assert candidate["missing_information"] == ["target domain"]
    assert candidate["clarification_required"] is True
    assert replay["resolution_status"] == CLARIFICATION_REQUIRED


def test_domain_reference_prompt_detection_is_conservative() -> None:
    assert is_domain_reference_adaptation_prompt(
        "Create something similar to the trading domain but focused on healthcare."
    ) is True
    assert is_domain_reference_adaptation_prompt("Create a trading domain.") is False
    assert is_domain_reference_adaptation_prompt("What is AiGOL?") is False


def test_domain_reference_cli_renders_resolution(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "domain-reference",
            "resolve",
            "--prompt",
            "Create a healthcare version of the trading domain.",
            "--runtime-root",
            str(tmp_path / "cli_runtime"),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol domain-reference resolve"
    assert result["resolution_status"] == DOMAIN_ADAPTATION_CANDIDATE_CREATED
    assert "AIGOL DOMAIN REFERENCE RESOLUTION" in rendered
    assert "Reference Domain: TRADING" in rendered
    assert "Target Domain: HEALTHCARE" in rendered


def test_interactive_conversation_routes_domain_reference_without_provider_fallback(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            ["Create something similar to the trading domain but focused on healthcare.", "exit"]
        ),
        output_func=output.append,
    )
    turn = result["turns"][0]
    replay_path = (
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "semantic_similarity_domain_reference"
        / "000_domain_reference_recorded.json"
    )

    assert result["failed_turns"] == 0
    assert turn["conversational_workflow_id"] == DOMAIN_ADAPTATION_REFERENCE
    assert turn["source_domain"] == "TRADING"
    assert turn["target_domain"] == "HEALTHCARE"
    assert turn["operation"] == DOMAIN_ADAPTATION
    assert turn["provider_invoked"] is False
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert "Reference Domain: TRADING" in output[0]
    assert replay_path.exists()


def test_conversational_routing_preserves_exact_trading_domain_workflow(tmp_path) -> None:
    from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent

    capture = route_conversational_cli_intent(
        routing_id="CONVERSATIONAL-ROUTING-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt="Create a trading domain.",
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )

    assert capture["workflow_id"] == CREATE_DOMAIN_TRADING


def test_replay_tampering_is_detected(tmp_path) -> None:
    _resolve(tmp_path, "Create a healthcare version of the trading domain.")
    path = tmp_path / "domain_reference" / "002_domain_adaptation_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["target_domain"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_semantic_similarity_domain_reference_replay(tmp_path / "domain_reference")
