from __future__ import annotations

import inspect

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import (
    INTERACTIVE_CONVERSATION_CLI_VERSION,
    build_parser,
    render_command_result,
    run_command,
    run_interactive_conversation,
)
from aigol.runtime.conversational_progress_binding_runtime import (
    reconstruct_conversational_progress_binding,
)


TIMESTAMP = "2026-06-01T00:00:00Z"
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


def _args(tmp_path, *, session_id: str = "INTERACTIVE-TEST-000001"):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            TIMESTAMP,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_interactive_conversation_records_router_and_conversation_replay(tmp_path):
    args = _args(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    session_root = tmp_path / "interactive_runtime" / "INTERACTIVE-TEST-000001"

    assert result["command"] == "aigol conversation"
    assert result["interactive_conversation_cli_version"] == INTERACTIVE_CONVERSATION_CLI_VERSION
    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert result["exit_reason"] == "EXIT_COMMAND"
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    assert result["dispatch_requested"] is False
    assert result["invocation_requested"] is False
    assert turn["selected_source"] == "CONSTITUTIONAL_MEMORY"
    assert turn["response_source"] == "SELF_RESOLUTION"
    assert turn["fail_closed"] is False
    assert output[0].splitlines()[:8] == PROGRESS_LINES
    assert any("governed AI operation path" in line for line in output)
    assert (session_root / "TURN-000001" / "source_router" / "000_source_of_truth_router_selected.json").exists()
    assert (
        session_root
        / "prompt_runtime"
        / "INTERACTIVE-TEST-000001:TURN-000001"
        / "conversation_response"
        / "004_provider_assisted_conversation_response_returned.json"
    ).exists()
    progress = reconstruct_conversational_progress_binding(
        session_root / "TURN-000001" / "conversational_progress"
    )
    assert progress["latest_runtime_status"] == "COMPLETED"
    assert progress["latest_stage"] == "Replay"


def test_interactive_conversation_quit_exits_without_turns(tmp_path):
    args = _args(tmp_path, session_id="INTERACTIVE-QUIT-000001")
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["quit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 0
    assert result["failed_turns"] == 0
    assert result["exit_reason"] == "EXIT_COMMAND"
    assert result["turns"] == []
    assert output == []


def test_interactive_conversation_eof_exits_gracefully(tmp_path):
    args = _args(tmp_path, session_id="INTERACTIVE-EOF-000001")

    def eof(_prompt: str) -> str:
        raise EOFError

    result = run_interactive_conversation(args, input_func=eof, output_func=lambda _line: None)

    assert result["turn_count"] == 0
    assert result["exit_reason"] == "EOF"


def test_interactive_conversation_fails_closed_on_runtime_error(tmp_path, monkeypatch):
    args = _args(tmp_path, session_id="INTERACTIVE-FAIL-CLOSED-000001")
    output: list[str] = []

    def fail_runtime(**_kwargs):
        raise RuntimeError("synthetic runtime failure")

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", fail_runtime)

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 1
    rendered = output[0].splitlines()
    assert rendered[:6] == PROGRESS_LINES[:6]
    assert "[8/8] Replay" in rendered
    assert output[-1] == "FAILED_CLOSED: synthetic runtime failure"
    assert turn["response_status"] == "FAILED_CLOSED"
    assert turn["fail_closed"] is True
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert turn["dispatch_requested"] is False
    assert turn["invocation_requested"] is False


def test_conversation_command_metadata_is_renderable_without_running_loop(tmp_path):
    args = _args(tmp_path, session_id="INTERACTIVE-METADATA-000001")
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol conversation"
    assert result["worker_invoked"] is False
    assert "AIGOL CONVERSATION" in rendered
    assert "execution_requested: False" in rendered


def test_interactive_conversation_cli_does_not_import_legacy_worker_or_dispatch_runtime():
    source = inspect.getsource(aigol_cli)

    assert "from aigol.runtime.dispatch_runtime" not in source
    assert "assign_worker(" not in source
    assert "invoke_worker(" not in source
    assert "dispatch_worker(" not in source
