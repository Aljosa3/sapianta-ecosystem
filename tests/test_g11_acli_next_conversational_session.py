"""Tests for the G11-02 ACLI Next conversational development session UX."""

from __future__ import annotations

import builtins
import json
import os
import pty
import select
import subprocess
import sys
import time
from pathlib import Path

from aigol.acli_next import (
    ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION,
    ACLI_NEXT_MESSAGE_COMPOSER_VERSION,
    ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_VERSION,
    run_acli_next_conversational_session,
    run_acli_next_persistent_conversational_session,
)
from aigol.acli_next.conversational import (
    ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED,
    ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETED,
)
from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command


CREATED_AT = "2026-07-02T00:00:00Z"


def _run_acli_next_pty(tmp_path, lines: list[str]) -> str:
    master_fd, slave_fd = pty.openpty()
    runtime_root = tmp_path / "runtime"
    command = [
        sys.executable,
        "-m",
        "aigol.cli.aigol_cli",
        "next",
        "--session-id",
        "ACLI-NEXT-COMPOSER-PTY",
        "--runtime-root",
        str(runtime_root),
        "--workspace",
        str(tmp_path),
        "--created-at",
        CREATED_AT,
    ]
    process = subprocess.Popen(
        command,
        cwd=Path.cwd(),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)
    output = bytearray()
    try:
        os.write(master_fd, ("\n".join(lines) + "\n").encode("utf-8"))
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            ready, _, _ = select.select([master_fd], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(master_fd, 8192)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
            if process.poll() is not None:
                while True:
                    ready, _, _ = select.select([master_fd], [], [], 0)
                    if not ready:
                        break
                    try:
                        chunk = os.read(master_fd, 8192)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
                break
        process.wait(timeout=5)
    finally:
        os.close(master_fd)
        if process.poll() is None:
            process.kill()
    assert process.returncode == 0
    return output.decode("utf-8", errors="replace")


def test_acli_next_conversational_session_composes_existing_capabilities(tmp_path) -> None:
    result = run_acli_next_conversational_session(
        session_id="ACLI-NEXT-CONVERSATIONAL-TEST",
        prompts=["Implement governed Git remote workflow."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next"
    assert result["runtime_version"] == ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION
    assert result["session_status"] == ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED
    assert result["turn_count"] == 1
    assert result["session_resumed"] is False
    assert result["show_guide_delegate_only"] is True
    assert result["minimal_ux_extension_only"] is True
    assert result["platform_core_coordinates"] is True
    assert result["governance_authority_preserved"] is True
    assert result["replay_authority_preserved"] is True
    assert result["worker_execution_authority_preserved"] is True
    assert result["architectural_health_advisory_only"] is True
    assert result["acli_next_authorizes"] is False
    assert result["acli_next_executes"] is False
    assert result["acli_next_records_replay_evidence"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert result["dashboard_summary"]["hybrid_operation"]["operation_type"] == "git_remote"
    assert result["dashboard_summary"]["hybrid_operation"]["hybrid_status"] == "HYBRID_REQUIRED"
    assert (tmp_path / "runtime" / "ACLI-NEXT-CONVERSATIONAL-TEST" / "RUN-000001").exists()


def test_acli_next_conversational_session_resumes_by_creating_next_run(tmp_path) -> None:
    kwargs = {
        "session_id": "ACLI-NEXT-CONVERSATIONAL-RESUME",
        "prompts": ["Show governed development status."],
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "runtime",
        "workspace": tmp_path,
    }

    first = run_acli_next_conversational_session(**kwargs)
    second = run_acli_next_conversational_session(**kwargs)

    assert first["run_id"] == "RUN-000001"
    assert first["session_resumed"] is False
    assert second["run_id"] == "RUN-000002"
    assert second["session_resumed"] is True


def test_acli_next_conversational_cli_route_renders_summary(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "--session-id",
            "ACLI-NEXT-CONVERSATIONAL-CLI",
            "--prompt",
            "Prepare a governed development readiness review.",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol next"
    assert result["session_status"] == ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED
    assert result["dashboard_summary"]["active_task"]["current_milestone"] == "G11_02"
    assert result["acli_next_executes"] is False
    assert "AIGOL NEXT" in rendered
    assert "session_id: ACLI-NEXT-CONVERSATIONAL-CLI" in rendered
    assert "hybrid_status: FULLY_GOVERNED" in rendered


def test_acli_next_persistent_conversational_session_loops_until_exit(tmp_path) -> None:
    inputs = iter(
        [
            "Show governed development status.",
            "/send",
            "Implement governed Git remote workflow.",
            "/send",
            "exit",
        ]
    )
    outputs: list[str] = []

    result = run_acli_next_persistent_conversational_session(
        session_id="ACLI-NEXT-PERSISTENT-TEST",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=outputs.append,
    )

    assert result["command"] == "aigol next"
    assert result["runtime_version"] == ACLI_NEXT_MESSAGE_COMPOSER_VERSION
    assert result["persistent_session_runtime_version"] == ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_VERSION
    assert result["session_status"] == ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETED
    assert result["turn_count"] == 2
    assert result["message_composer_enabled"] is True
    assert result["submitted_message_count"] == 2
    assert result["composer_creates_turn_before_send"] is False
    assert result["composer_creates_replay_before_send"] is False
    assert result["one_submitted_message_per_turn"] is True
    assert result["exit_reason"] == "EXIT_COMMAND"
    assert result["show_guide_delegate_only"] is True
    assert result["acli_next_authorizes"] is False
    assert result["acli_next_executes"] is False
    assert result["acli_next_records_replay_evidence"] is False
    assert (tmp_path / "runtime" / "ACLI-NEXT-PERSISTENT-TEST" / "RUN-000001").exists()
    assert (tmp_path / "runtime" / "ACLI-NEXT-PERSISTENT-TEST" / "RUN-000002").exists()
    assert any("hybrid_status: HYBRID_REQUIRED" in output for output in outputs)


def test_acli_next_message_composer_submits_multiline_message_as_one_turn(tmp_path) -> None:
    inputs = iter(
        [
            "We are beginning Generation 12.",
            "",
            "Objective:",
            "",
            "G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1",
            "/preview",
            "/send",
            "exit",
        ]
    )
    outputs: list[str] = []

    result = run_acli_next_persistent_conversational_session(
        session_id="ACLI-NEXT-COMPOSER-MULTILINE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=outputs.append,
    )

    run_root = tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-MULTILINE" / "RUN-000001"
    assert result["turn_count"] == 1
    assert result["submitted_message_count"] == 1
    assert result["preview_count"] == 1
    assert run_root.exists()
    assert not (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-MULTILINE" / "RUN-000002").exists()
    turn_artifact = json.loads((run_root / "000_acli_next_conversational_session_presented.json").read_text())
    assert turn_artifact["turn_count"] == 1
    assert "We are beginning Generation 12." in turn_artifact["latest_prompt"]
    assert "G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1" in turn_artifact["latest_prompt"]
    assert any("Message buffer preview:" in output for output in outputs)
    assert any("G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1" in output for output in outputs)


def test_acli_next_message_composer_clear_and_cancel_create_no_turns(tmp_path) -> None:
    inputs = iter(
        [
            "This should be cleared.",
            "/clear",
            "This should be canceled.",
            "/cancel",
            "exit",
        ]
    )
    outputs: list[str] = []

    result = run_acli_next_persistent_conversational_session(
        session_id="ACLI-NEXT-COMPOSER-NO-TURN",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=outputs.append,
    )

    assert result["turn_count"] == 0
    assert result["submitted_message_count"] == 0
    assert result["clear_count"] == 1
    assert result["cancel_count"] == 1
    assert result["composer_creates_turn_before_send"] is False
    assert not (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-NO-TURN" / "RUN-000001").exists()
    assert any("Message buffer cleared." in output for output in outputs)
    assert any("Message composition canceled." in output for output in outputs)


def test_acli_next_message_composer_accepts_pasted_format_character_commands(tmp_path) -> None:
    inputs = iter(
        [
            "Message pasted from a formatted source.",
            "/preview\u200b",
            "/send\u200b",
            "exit",
        ]
    )
    outputs: list[str] = []

    result = run_acli_next_persistent_conversational_session(
        session_id="ACLI-NEXT-COMPOSER-FORMAT-COMMANDS",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=outputs.append,
    )

    assert result["turn_count"] == 1
    assert result["submitted_message_count"] == 1
    assert result["preview_count"] == 1
    assert (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-FORMAT-COMMANDS" / "RUN-000001").exists()
    assert any("Message buffer preview:" in output for output in outputs)
    assert any("session_status: ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED" in output for output in outputs)


def test_acli_next_message_composer_accepts_copied_prompt_prefixed_commands(tmp_path) -> None:
    inputs = iter(
        [
            "Message pasted from a transcript.",
            "AiGOL compose> /preview",
            "AiGOL compose> /send",
            "AiGOL> exit",
        ]
    )
    outputs: list[str] = []

    result = run_acli_next_persistent_conversational_session(
        session_id="ACLI-NEXT-COMPOSER-PROMPT-PREFIXED-COMMANDS",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=outputs.append,
    )

    assert result["turn_count"] == 1
    assert result["submitted_message_count"] == 1
    assert result["preview_count"] == 1
    assert (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-PROMPT-PREFIXED-COMMANDS" / "RUN-000001").exists()
    assert any("Message buffer preview:" in output for output in outputs)
    assert any("session_status: ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED" in output for output in outputs)


def test_acli_next_message_composer_main_interactive_path_submits_one_turn(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    inputs = iter(
        [
            "Interactive main path.",
            "",
            "G12_02B regression.",
            "/preview",
            "/send",
            "exit",
        ]
    )

    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

    result = aigol_cli.main(
        [
            "next",
            "--session-id",
            "ACLI-NEXT-COMPOSER-MAIN",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert "Message buffer preview:" in output
    assert "session_status: ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED" in output
    assert "message_composer_enabled: True" in output
    assert "submitted_message_count: 1" in output
    assert (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-MAIN" / "RUN-000001").exists()
    assert not (tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-MAIN" / "RUN-000002").exists()


def test_acli_next_message_composer_real_pty_interactive_flow(tmp_path) -> None:
    output = _run_acli_next_pty(
        tmp_path,
        [
            "First composed message before clear.",
            "",
            "Objective:",
            "/preview",
            "/clear",
            "/send",
            "Second composed message.",
            "",
            "G12_02C regression.",
            "/send",
            "Third composed message.",
            "/send",
            "Canceled message.",
            "/cancel",
            "exit",
        ],
    )

    runtime_root = tmp_path / "runtime" / "ACLI-NEXT-COMPOSER-PTY"
    assert "Message buffer preview:" in output
    assert "First composed message before clear." in output
    assert "Message buffer cleared." in output
    assert "Message buffer is empty. Add content before /send." in output
    assert "Message composition canceled." in output
    assert "session_status: ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED" in output
    assert "run_id: RUN-000001" in output
    assert "run_id: RUN-000002" in output
    assert "message_composer_enabled: True" in output
    assert "submitted_message_count: 2" in output
    assert "AiGOL compose>" not in output
    assert (runtime_root / "RUN-000001").exists()
    assert (runtime_root / "RUN-000002").exists()
    assert not (runtime_root / "RUN-000003").exists()
