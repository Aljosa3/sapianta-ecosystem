from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _prompt_recording_reader(values: list[str], prompts: list[str]):
    iterator = iter(values)

    def read(prompt: str) -> str:
        prompts.append(prompt)
        return next(iterator)

    return read


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
            "runtime_replay_reference": "/tmp/g15-hir-05-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def _load_contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def test_submit_mode_multiline_clarification_reply_is_submitted_once(tmp_path: Path) -> None:
    calls: list[dict] = []
    session_id = "G15-HIR-05-MULTILINE"
    clarification_reply = "\n".join(
        [
            "Implement Governed Development Execution Bridge validation.",
            "",
            "The bridge should preserve Platform Core ownership.",
            "No Human Interface behaviour shall change.",
        ]
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader([f"{clarification_reply}\n/send\n", "/approve"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_contexts(tmp_path, session_id)
    clarification_context = contexts[1]
    resolution = clarification_context["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["multiline_request_count"] == 1
    assert result["clarification_question_count"] == 1
    assert len(contexts) == 2
    assert calls[0]["prompt"] == clarification_reply
    assert resolution["raw_prompt"] == clarification_reply
    assert resolution["clarification_reply_bound"] is True
    assert resolution["clarification_resolved"] is True
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False


def test_submit_mode_clarification_compose_cancel_discards_buffer(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    session_id = "G15-HIR-05-CANCEL"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["This buffered answer is not ready.", "/cancel"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_contexts(tmp_path, session_id)

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert result["exit_reason"] == "CANCEL_COMMAND"
    assert result["submitted_request_count"] == 1
    assert len(contexts) == 1
    assert calls == []
    assert any("Pending request canceled." in line for line in output)


def test_submit_mode_clarification_line_by_line_paste_renders_prompt_once(tmp_path: Path) -> None:
    calls: list[dict] = []
    prompts: list[str] = []
    session_id = "G15-AICLI-08-SINGLE-PROMPT"
    clarification_reply = "\n".join(
        [
            "Implement Governed Development Execution Bridge validation.",
            "",
            "The bridge should preserve Platform Core ownership.",
            "No Human Interface behaviour shall change.",
        ]
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_prompt_recording_reader(
            [
                "Implement Governed Development Execution Bridge validation.",
                "",
                "The bridge should preserve Platform Core ownership.",
                "No Human Interface behaviour shall change.",
                "/send",
                "/approve",
            ],
            prompts,
        ),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_contexts(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["multiline_request_count"] == 1
    assert calls[0]["prompt"] == clarification_reply
    assert resolution["raw_prompt"] == clarification_reply
    assert prompts[:5] == ["aicli clarification> ", "", "", "", ""]
    assert "aicli clarification compose> " not in prompts
    assert prompts[-1] == "aicli approval> "
