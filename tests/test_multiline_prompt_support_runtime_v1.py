"""Tests for AIGOL_MULTILINE_PROMPT_SUPPORT_RUNTIME_V1."""

from __future__ import annotations

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import (
    INTERACTIVE_CONVERSATION_MULTILINE_BANNER,
    MULTILINE_PROMPT_TERMINATOR,
    build_parser,
    run_interactive_conversation,
)
from aigol.runtime.multiline_prompt_support_runtime import (
    MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1,
    MULTILINE_PROMPT_CAPTURED,
    TURN_STARTED,
    reconstruct_multiline_prompt_capture_replay,
)
from aigol.runtime.conversational_turn_completion_runtime import (
    reconstruct_conversational_turn_completion_replay,
)


CREATED_AT = "2026-06-06T00:00:00Z"
SESSION_ID = "SESSION-MULTILINE-PROMPT-SUPPORT-000001"
CASE_B_LINES = [
    "I want to create the first real commercial Sapianta product.",
    "",
    "Use the current AiGOL architecture and repository state.",
    "",
    "Produce:",
    "1. Findings",
    "2. Assumptions",
    "3. Alternatives",
    "4. Risks",
    "5. Recommendation",
    "",
    "Explain your reasoning.",
    "",
    "Do not create or modify anything.",
    "",
    "Provide cognition output only.",
]


class BufferedPasteInput:
    def __init__(self, values: list[str]):
        self.values = list(values)
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.values:
            raise EOFError
        return self.values.pop(0)

    def has_pending_input(self) -> bool:
        return bool(self.values) and self.values[0] != "exit"


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


def _single_line_input(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_case_b_multiline_paste_creates_one_turn_without_fragmentation(tmp_path, monkeypatch) -> None:
    output: list[str] = []
    pasted = BufferedPasteInput(CASE_B_LINES + [MULTILINE_PROMPT_TERMINATOR, "exit"])

    def deterministic_conversation(**kwargs):
        prompt_id = kwargs["prompt_id"]
        return {
            "prompt_id": prompt_id,
            "response_status": "READY",
            "response_source": "DETERMINISTIC_TEST_CONVERSATION",
            "response_text": "Findings\nAssumptions\nAlternatives\nRisks\nRecommendation",
            "conversation_replay_reference": "deterministic/conversation",
            "replay_reference": "deterministic/prompt",
            "fail_closed": False,
            "failure_reason": None,
            "canonical_chain_id": f"{prompt_id}:CHAIN",
            "current_chain_id": f"{prompt_id}:CHAIN",
            "latest_chain_id": f"{prompt_id}:CHAIN",
            "suggested_inspection_commands": [],
        }

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", deterministic_conversation)

    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=pasted,
        output_func=output.append,
    )

    session_root = tmp_path / "interactive_runtime" / SESSION_ID
    turn_root = session_root / "TURN-000001"
    prompt_replay = reconstruct_multiline_prompt_capture_replay(turn_root / "multiline_prompt_capture")
    completion_replay = reconstruct_conversational_turn_completion_replay(turn_root / "turn_completion")

    assert result["turn_count"] == 1
    assert len(result["turns"]) == 1
    assert result["turns"][0]["turn_id"] == "TURN-000001"
    assert result["turns"][0]["turn_started"] is True
    assert result["turns"][0]["turn_completed"] is True
    assert result["turns"][0]["result_delivered"] is True
    assert result["turns"][0]["multiline_prompt_capture_artifact_type"] == MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1
    assert result["turns"][0]["multiline_line_count"] == len(CASE_B_LINES)
    assert result["turns"][0]["multiline_input_mode"] == "MULTILINE_SENTINEL"
    assert result["turns"][0]["fragment_turns_created"] is False
    assert result["turns"][0]["partial_routing_allowed"] is False
    assert prompt_replay["event_type"] == MULTILINE_PROMPT_CAPTURED
    assert prompt_replay["turn_boundary_event"] == TURN_STARTED
    assert prompt_replay["line_count"] == len(CASE_B_LINES)
    assert prompt_replay["terminator_included"] is False
    assert prompt_replay["single_turn_guarantee"] is True
    assert completion_replay["turn_completed"] is True
    assert completion_replay["result_delivered"] is True
    assert len(list((turn_root / "source_router").glob("*source_of_truth_router_returned.json"))) == 1
    assert len(list((turn_root / "turn_completion").glob("*turn_completed.json"))) == 1
    assert len(list(session_root.glob("TURN-*"))) == 1
    assert "TURN COMPLETED" in output[0]
    assert pasted.prompts.count("AiGOL > ") == 2
    assert pasted.prompts.count("... ") == len(CASE_B_LINES)


def test_single_line_prompt_still_creates_one_turn(tmp_path, monkeypatch) -> None:
    output: list[str] = []

    def deterministic_conversation(**kwargs):
        prompt_id = kwargs["prompt_id"]
        return {
            "prompt_id": prompt_id,
            "response_status": "READY",
            "response_source": "DETERMINISTIC_TEST_CONVERSATION",
            "response_text": "single-line response",
            "conversation_replay_reference": "deterministic/conversation",
            "replay_reference": "deterministic/prompt",
            "fail_closed": False,
            "failure_reason": None,
            "canonical_chain_id": f"{prompt_id}:CHAIN",
            "current_chain_id": f"{prompt_id}:CHAIN",
            "latest_chain_id": f"{prompt_id}:CHAIN",
            "suggested_inspection_commands": [],
        }

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", deterministic_conversation)

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-MULTILINE-SINGLE-LINE-000001"),
        input_func=_single_line_input(["hello", "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    replay = reconstruct_multiline_prompt_capture_replay(
        tmp_path
        / "interactive_runtime"
        / "SESSION-MULTILINE-SINGLE-LINE-000001"
        / "TURN-000001"
        / "multiline_prompt_capture"
    )

    assert result["turn_count"] == 1
    assert turn["multiline_input_mode"] == "SINGLE_LINE"
    assert turn["multiline_line_count"] == 1
    assert replay["input_mode"] == "SINGLE_LINE"
    assert replay["line_count"] == 1
    assert "single-line response" in output[0]


def test_multiline_startup_banner_is_discoverable() -> None:
    assert "Multi-line mode enabled." in INTERACTIVE_CONVERSATION_MULTILINE_BANNER
    assert "Finish prompt with a single '.' on its own line." in INTERACTIVE_CONVERSATION_MULTILINE_BANNER
