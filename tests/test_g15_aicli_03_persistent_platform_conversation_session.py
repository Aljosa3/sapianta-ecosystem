from __future__ import annotations

import json
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


def _contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_clarification_continuity").glob("*.json"))
    ]


def _workspace_states(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "workspace_state").glob("*.json"))
    ]


def test_submit_mode_continues_clarification_then_approval_to_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-AICLI-03-CLARIFY-RUN",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["Implement governance documentation indexing utility.", "/send", "/approve"]),
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


def test_interactive_mode_binds_clarification_response_through_platform_core_replay(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    output: list[str] = []
    session_id = "G17-HI-03-INTERACTIVE-CLARIFICATION-BINDING"

    result = aicli.run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(
            [
                "I have an idea.",
                "/send",
                "Implement governance documentation indexing utility.",
                "/send",
                "/approve",
                "/exit",
            ]
        ),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _contexts(tmp_path, session_id)
    continuities = _continuity(tmp_path, session_id)
    workspace_states = _workspace_states(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SESSION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["clarification_question_count"] == 1
    assert result["approval_count"] == 1
    assert result["runtime_entered"] is True
    assert calls[0]["prompt"] == "Implement governance documentation indexing utility."
    assert resolution["clarification_reply_bound"] is True
    assert resolution["clarification_resolved"] is True
    assert resolution["new_governed_request_created"] is False
    assert continuities[0]["reply_bound_to_active_clarification"] is True
    assert continuities[0]["human_interface_authority"] is False
    assert workspace_states[0]["pending_clarification_request"] is not None
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert any("Clarification required before governed execution." in line for line in output)
    assert any("Certified runtime result" in line for line in output)


def test_interactive_mode_clears_pending_state_between_governed_interactions(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    session_id = "G17-HI-03-INTERACTIVE-MULTI-TURN"

    result = aicli.run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(
            [
                "Implement governance validation utility.",
                "/approve",
                "Implement replay summary utility.",
                "/approve",
                "/exit",
            ]
        ),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    workspace_states = _workspace_states(tmp_path, session_id)

    assert result["session_status"] == "REFERENCE_UHI_SESSION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["approval_count"] == 2
    assert result["runtime_entered"] is True
    assert [call["prompt"] for call in calls] == [
        "Implement governance validation utility.",
        "Implement replay summary utility.",
    ]
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert workspace_states[-1]["pending_implementation_summary"] is None
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


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
                "/send",
                "Implement replay observation diagnostics utility.",
                "/send",
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
