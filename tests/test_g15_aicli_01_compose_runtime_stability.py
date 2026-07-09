from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli


def _successful_runner(calls: list[dict]):
    def run(**kwargs):
        calls.append(kwargs)
        return {
            "runtime_binding_status": aicli.REFERENCE_UHI_BOUND,
            "runtime_entered": True,
            "governance_authorization_reached": True,
            "provider_invocation_reached": True,
            "worker_execution_reached": True,
            "replay_certification_reached": True,
            "runtime_replay_reference": "/tmp/aicli-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def _prompt_recording_reader(values: list[object], prompts: list[str]):
    iterator = iter(values)

    def read(prompt: str) -> str:
        prompts.append(prompt)
        value = next(iterator)
        if value is KeyboardInterrupt:
            raise KeyboardInterrupt
        return str(value)

    return read


def test_short_compose_session_still_prompts_once_per_input_cycle(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    prompts: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G15-SHORT-COMPOSE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(
            ["Implement governance validation utility.", "/approve", "/exit"],
            prompts,
        ),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 1
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert calls[0]["prompt"] == "Implement governance validation utility."
    assert prompts == ["aicli> ", "", "aicli> "]
    assert any("Request submitted to Platform Core." in line for line in output)


def test_pending_approval_eof_is_awaiting_human_approval(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    prompts: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G17-APPROVAL-EOF",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(
            ["Implement governance validation utility.", "/send"],
            prompts,
        ),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SESSION_AWAITING_HUMAN_APPROVAL"
    assert result["exit_reason"] == "EOF_AWAITING_APPROVAL"
    assert result["pending_approval"] is True
    assert result["runtime_entered"] is False
    assert result["runtime_status"] == aicli.REFERENCE_UHI_NOT_REQUIRED
    assert calls == []
    assert {"event": "eof_awaiting_approval"} in result["transcript"]
    assert any("Platform Core is waiting for approval." in line for line in output)
    assert any("aicli session awaiting human input." in line for line in output)
    assert any("session_status: REFERENCE_UHI_SESSION_AWAITING_HUMAN_APPROVAL" in line for line in output)
    assert any("pending_approval: True" in line for line in output)
    assert prompts == ["aicli> ", "", "aicli> "]


def test_cancel_clears_pending_approval_before_exit(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G17-APPROVAL-CANCEL",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(
            ["Implement governance validation utility.", "/send", "/cancel", "/exit"],
            [],
        ),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SESSION_COMPLETED"
    assert result["exit_reason"] == "EXIT_COMMAND"
    assert result["pending_approval"] is False
    assert result["runtime_entered"] is False
    assert calls == []
    assert {"event": "cancel"} in result["transcript"]
    assert any("Pending request canceled." in line for line in output)


def test_large_pasted_compose_chunk_is_consumed_without_prompt_flood(tmp_path: Path) -> None:
    calls: list[dict] = []
    prompts: list[str] = []
    request_lines = [
        "Implement governance validation utility for replay observation reporting.",
        "",
        "Generation 14 is fully certified.",
        "Treat every Generation 14 architectural invariant as immutable.",
        "",
        "Objective:",
        "Implement deterministic replay observations.",
        "",
        "Constraints:",
        "- Preserve Platform Core ownership.",
        "- Keep Human Interfaces thin.",
        "- Do not invoke providers.",
        "- Do not create improvement proposals.",
        "",
        "Validation:",
        "- existing replay behavior remains unchanged",
        "- deterministic replay preserved",
    ]
    large_paste = "\n".join([*request_lines, "/send", "/approve", "/exit"]) + "\n"

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G15-LARGE-PASTE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader([large_paste], prompts),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 1
    assert result["multiline_request_count"] == 1
    assert result["unsubmitted_compose_line_count"] == 0
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert calls[0]["prompt"] == "\n".join(request_lines)
    assert prompts == ["aicli> "]


def test_large_paste_preserves_blank_lines_and_handles_eof_after_buffer(tmp_path: Path) -> None:
    calls: list[dict] = []
    prompts: list[str] = []
    request_lines = [
        "Implement replay observation indexing.",
        "",
        "",
        "The blank lines above are intentional.",
    ]
    large_paste_without_send = "\n".join(request_lines) + "\n"

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G15-LARGE-PASTE-EOF",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader([large_paste_without_send], prompts),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SESSION_AWAITING_HUMAN_APPROVAL"
    assert result["exit_reason"] == "EOF_AWAITING_APPROVAL"
    assert result["pending_approval"] is True
    assert result["submitted_request_count"] == 1
    assert result["multiline_request_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []
    assert result["development_intent_resolution"]["raw_prompt"] == "\n".join(request_lines)
    assert prompts == ["aicli> ", ""]


def test_line_by_line_multiline_paste_uses_blank_buffer_prompt(tmp_path: Path) -> None:
    calls: list[dict] = []
    prompts: list[str] = []
    request_lines = [
        "Implement replay observation indexing.",
        "",
        "Preserve Human Interface boundaries.",
    ]

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G17-LINE-BY-LINE-PASTE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(
            [*request_lines, "/send", "/approve", "/exit"],
            prompts,
        ),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 1
    assert result["multiline_request_count"] == 1
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert calls[0]["prompt"] == "\n".join(request_lines)
    assert "aicli compose> " not in prompts
    assert prompts == ["aicli> ", "", "", "", "aicli> ", "aicli> "]


def test_keyboard_interrupt_cancels_compose_without_traceback(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    prompts: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G17-KEYBOARD-INTERRUPT",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(
            ["Implement partial governed request.", KeyboardInterrupt],
            prompts,
        ),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["exit_reason"] == "KEYBOARD_INTERRUPT"
    assert result["canceled_compose_count"] == 1
    assert result["unsubmitted_compose_line_count"] == 0
    assert result["runtime_entered"] is False
    assert calls == []
    assert {"event": "keyboard_interrupt"} in result["transcript"]
    assert any("Session interrupted." in line for line in output)
    assert prompts == ["aicli> ", ""]


def test_top_level_blank_paste_is_ignored_without_submitting(tmp_path: Path) -> None:
    calls: list[dict] = []
    prompts: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G15-BLANK-PASTE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_prompt_recording_reader(["\n\n\n/exit\n"], prompts),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 0
    assert result["runtime_entered"] is False
    assert result["exit_reason"] == "EXIT_COMMAND"
    assert calls == []
    assert prompts == ["aicli> "]
