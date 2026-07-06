from __future__ import annotations

import io
import sys
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_submit_mode_accepts_large_multiline_prompt_once(tmp_path: Path) -> None:
    output: list[str] = []
    request_lines = [
        "Implement a Generation 15 replay observation validation utility.",
        "",
        "Requirements:",
        "- preserve Platform Core ownership",
        "- keep Human Interfaces thin",
        "- emit deterministic replay-safe evidence",
        "- avoid provider calls",
    ]
    request = "\n".join(request_lines)

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-02-LARGE",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: request,
        output_writer=output.append,
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
    assert result["submitted_request_count"] == 1
    assert result["submitted_message_count"] == 1
    assert result["multiline_request_count"] == 1
    assert result["runtime_entered"] is False
    assert result["pending_approval"] is True
    assert result["development_intent_resolution"]["raw_prompt"] == request
    assert len(list((tmp_path / "G15-AICLI-02-LARGE" / "uhi_project_services").glob("*.json"))) == 1
    assert any("Request submitted to Platform Core." in line for line in output)


def test_submit_mode_preserves_internal_line_breaks_and_strips_outer_empty_input(tmp_path: Path) -> None:
    request = (
        "\n\n"
        "Implement governance documentation indexing.\n"
        "\n"
        "Acceptance:\n"
        "- preserve blank lines inside the request\n"
        "- submit a single Platform Core request\n"
        "\n\n"
    )
    expected = (
        "Implement governance documentation indexing.\n"
        "\n"
        "Acceptance:\n"
        "- preserve blank lines inside the request\n"
        "- submit a single Platform Core request"
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-02-PRESERVE",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: request,
        output_writer=lambda _line: None,
    )

    assert result["submitted_request_count"] == 1
    assert result["development_intent_resolution"]["raw_prompt"] == expected


def test_submit_mode_rejects_empty_input_without_platform_core_submission(tmp_path: Path) -> None:
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-02-EMPTY",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: " \n\n\t",
        output_writer=output.append,
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_REJECTED_EMPTY_INPUT"
    assert result["exit_reason"] == "EMPTY_INPUT"
    assert result["submitted_request_count"] == 0
    assert result["platform_core_project_services_context"] is None
    assert result["runtime_entered"] is False
    assert not (tmp_path / "G15-AICLI-02-EMPTY" / "uhi_project_services").exists()
    assert any("Submit mode received empty input." in line for line in output)


def test_submit_mode_main_reads_stdin_and_keeps_aicli_non_authoritative(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO("Implement deterministic replay observation export.\n- keep replay authority preserved\n"),
    )

    exit_code = aicli.main(
        [
            "--session-id",
            "G15-AICLI-02-MAIN",
            "--runtime-root",
            str(tmp_path),
            "submit",
        ]
    )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Paste request below." in captured
    assert "Request submitted to Platform Core." in captured
    assert "aicli_authorizes: False" in captured
    assert "aicli_executes: False" in captured
    assert "aicli_owns_replay: False" in captured


def test_interactive_mode_still_accepts_short_compose_session(tmp_path: Path) -> None:
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="G15-AICLI-02-INTERACTIVE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement replay evidence report.", "/send", "/exit"]),
        output_writer=output.append,
    )

    assert result["command"] == "aicli"
    assert result["submitted_request_count"] == 1
    assert result["runtime_entered"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert any("Request submitted to Platform Core." in line for line in output)
