from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
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
            "runtime_replay_reference": "/tmp/aicli-submit-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def test_submit_mode_continues_clarification_then_approval_to_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-CLARIFY-RUN",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["Implement governance documentation indexing utility.", "/approve"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["exit_reason"] == "RUNTIME_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["clarification_question_count"] == 1
    assert result["approval_count"] == 1
    assert result["runtime_entered"] is True
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert calls[0]["prompt"] == "Implement governance documentation indexing utility."
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert any("Clarification required before governed execution." in line for line in output)
    assert any("Certified runtime result" in line for line in output)


def test_submit_mode_supports_multiple_platform_core_clarification_rounds(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-MULTI-CLARIFY",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(
            [
                "Improve this.",
                "Implement replay observation diagnostics utility.",
                "/approve",
            ]
        ),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 3
    assert result["clarification_question_count"] == 2
    assert result["approval_count"] == 1
    assert result["runtime_entered"] is True
    assert calls[0]["prompt"] == "Implement replay observation diagnostics utility."
    assert result["development_intent_resolution"]["raw_prompt"] == "Implement replay observation diagnostics utility."


def test_submit_mode_can_cancel_pending_clarification(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-CANCEL-CLARIFICATION",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["/cancel"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert result["exit_reason"] == "CANCEL_COMMAND"
    assert result["submitted_request_count"] == 1
    assert result["canceled_conversation_count"] == 1
    assert result["pending_approval"] is False
    assert result["runtime_entered"] is False
    assert calls == []
    assert any("Pending request canceled." in line for line in output)


def test_submit_mode_can_cancel_pending_approval(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-CANCEL-APPROVAL",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Implement deterministic governance report exporter.",
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert result["exit_reason"] == "CANCEL_COMMAND"
    assert result["submitted_request_count"] == 1
    assert result["canceled_conversation_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []


def test_submit_mode_without_followup_reader_records_awaiting_input(tmp_path: Path) -> None:
    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-AWAITING",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        output_writer=lambda _line: None,
    )

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
    assert result["exit_reason"] == "AWAITING_HUMAN_INPUT"
    assert result["submitted_request_count"] == 1
    assert result["runtime_entered"] is False
    assert result["transcript"][0]["conversation_response_mode"] == "CLARIFICATION"
