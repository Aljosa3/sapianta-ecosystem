from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.minimal_human_prompt_interface import (
    generate_prompt_id,
    reconstruct_human_prompt_replay,
    submit_human_prompt,
)
from aigol.runtime.models import FailClosedRuntimeError


def test_submit_human_prompt_creates_replay_visible_prompt_intent_and_routing(tmp_path):
    result = submit_human_prompt(
        human_prompt="Explain how AiGOL preserves replay.",
        replay_dir=tmp_path / "prompt_runtime",
    )
    reconstructed = reconstruct_human_prompt_replay(tmp_path / "prompt_runtime", prompt_id=result["prompt_id"])

    assert result["command"] == "aigol prompt submit"
    assert result["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert result["classification_destination"] == "CONVERSATION"
    assert result["routing_destination"] == "CONVERSATION"
    assert result["cognition_path_entered"] is True
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    assert result["fail_closed"] is False
    assert reconstructed["prompt_text"] == "Explain how AiGOL preserves replay."
    assert reconstructed["intent_classification"]["classification_destination"] == "CONVERSATION"
    assert reconstructed["routing_decision"]["destination"] == "CONVERSATION"
    assert reconstructed["replay_visible"] is True


def test_prompt_id_is_deterministic_when_default_is_used(tmp_path):
    prompt = "Retrieve Constitutional Memory citation for the freeze manifest."
    result = submit_human_prompt(human_prompt=prompt, replay_dir=tmp_path / "prompt_runtime")

    assert result["prompt_id"] == generate_prompt_id(human_prompt=prompt)
    assert result["classification_destination"] == "CONSTITUTIONAL_MEMORY_CONSULTATION"


def test_cli_prompt_submit_renders_operator_result(tmp_path):
    parser = build_parser()
    args = parser.parse_args(
        [
            "prompt",
            "submit",
            "--prompt",
            "Ask provider for a proposal.",
            "--runtime-root",
            str(tmp_path / "prompt_runtime"),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert result["classification_destination"] == "PROVIDER_PROPOSAL"
    assert "AIGOL PROMPT SUBMIT" in rendered
    assert "provider_invoked: False" in rendered
    assert "worker_invoked: False" in rendered


def test_missing_prompt_fails_closed(tmp_path):
    result = submit_human_prompt(human_prompt=" ", replay_dir=tmp_path / "prompt_runtime")

    assert result["prompt_status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["cognition_path_entered"] is False
    assert "human prompt is required" in result["failure_reason"]


def test_unknown_intent_fails_closed_but_prompt_remains_replay_visible(tmp_path):
    result = submit_human_prompt(human_prompt="Make it wonderful.", replay_dir=tmp_path / "prompt_runtime")
    reconstructed = reconstruct_human_prompt_replay(tmp_path / "prompt_runtime", prompt_id=result["prompt_id"])

    assert result["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert result["fail_closed"] is False
    assert result["classification_destination"] is None
    assert result["routing_destination"] is None
    assert reconstructed["intent_classification"]["classification_status"] == "FAILED_CLOSED"
    assert reconstructed["routing_decision"]["routing_status"] == "FAILED_CLOSED"


def test_reconstruct_detects_corrupt_prompt_artifact(tmp_path):
    result = submit_human_prompt(
        human_prompt="Inspect runtime status.",
        replay_dir=tmp_path / "prompt_runtime",
    )
    path = tmp_path / "prompt_runtime" / result["prompt_id"] / "000_human_prompt_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["prompt_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_human_prompt_replay(tmp_path / "prompt_runtime", prompt_id=result["prompt_id"])


def test_append_only_prompt_replay_advances_default_prompt_id(tmp_path):
    prompt = "Explain how AiGOL preserves replay."
    first = submit_human_prompt(human_prompt=prompt, replay_dir=tmp_path / "prompt_runtime")
    second = submit_human_prompt(human_prompt=prompt, replay_dir=tmp_path / "prompt_runtime")

    assert first["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert second["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert second["prompt_id"].endswith("-0002")
