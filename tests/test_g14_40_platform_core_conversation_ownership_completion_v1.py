from __future__ import annotations

from pathlib import Path

from aigol.acli_next.conversational import run_acli_next_persistent_conversational_session
from aigol.cli import aicli
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)


CREATED_AT = "2026-07-05T00:00:00Z"


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def test_platform_core_owns_approval_summary_and_fail_closed_response(tmp_path: Path) -> None:
    approval_context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-40-APPROVAL",
        message="Implement governance validation utility.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    approval = approval_context["human_conversation_experience"]["approval_summary"]

    assert approval["summary_authority"] == "PLATFORM_CORE"
    assert approval["summary_title"] == "Governed implementation summary"
    assert approval["runtime_after_approval"] == "CERTIFIED_PLATFORM_CORE_RUNTIME"
    assert approval["human_interface_authorizes"] is False
    assert approval["human_interface_executes"] is False

    fail_closed_context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-40-FAIL-CLOSED",
        message="I think this could be better.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    response = fail_closed_context["human_conversation_experience"]["fail_closed_response"]

    assert response["response_authority"] == "PLATFORM_CORE"
    assert response["response_title"] == "No governed implementation summary was produced."
    assert response["human_interface_generates_explanation"] is False


def test_aicli_and_acli_next_render_platform_core_approval_summary(tmp_path: Path) -> None:
    prompt = "Implement governance validation utility."
    aicli_output: list[str] = []
    next_output: list[str] = []

    aicli.run_reference_uhi_session(
        session_id="G14-40-AICLI-APPROVAL",
        runtime_root=tmp_path / "aicli",
        workspace=".",
        input_reader=_reader([prompt, "/send", "/exit"]),
        output_writer=aicli_output.append,
        runtime_runner=lambda **_kwargs: {},
    )
    run_acli_next_persistent_conversational_session(
        created_at=CREATED_AT,
        replay_dir=tmp_path / "next",
        session_id="G14-40-NEXT-APPROVAL",
        workspace=".",
        input_reader=_reader([prompt, "/send", "exit"]),
        output_writer=next_output.append,
        guided_development_workflow=True,
        turn_runner=lambda **_kwargs: {},
    )

    aicli_rendered = "\n".join(aicli_output)
    next_rendered = "\n".join(next_output)
    shared_lines = [
        "Governed implementation summary",
        f"original_request: {prompt}",
        "runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME",
        "Approval delegates to the certified runtime; the Human Interface does not authorize or execute.",
    ]

    for line in shared_lines:
        assert line in aicli_rendered
        assert line in next_rendered


def test_aicli_and_acli_next_render_platform_core_fail_closed_response(tmp_path: Path) -> None:
    prompt = "I think this could be better."
    aicli_output: list[str] = []
    next_output: list[str] = []

    aicli.run_reference_uhi_session(
        session_id="G14-40-AICLI-FAIL-CLOSED",
        runtime_root=tmp_path / "aicli-fail",
        workspace=".",
        input_reader=_reader([prompt, "/send", "/exit"]),
        output_writer=aicli_output.append,
        runtime_runner=lambda **_kwargs: {},
    )
    run_acli_next_persistent_conversational_session(
        created_at=CREATED_AT,
        replay_dir=tmp_path / "next-fail",
        session_id="G14-40-NEXT-FAIL-CLOSED",
        workspace=".",
        input_reader=_reader([prompt, "/send", "exit"]),
        output_writer=next_output.append,
        guided_development_workflow=True,
        turn_runner=lambda **_kwargs: {},
    )

    aicli_rendered = "\n".join(aicli_output)
    next_rendered = "\n".join(next_output)
    shared_lines = [
        "No governed implementation summary was produced.",
        "reason: request is not a deterministic development request",
        "When intent is incomplete, AiGOL asks for clarification instead of guessing or executing.",
        "next_step: Describe the capability, improvement, or decision you want AiGOL to help with.",
    ]

    for line in shared_lines:
        assert line in aicli_rendered
        assert line in next_rendered


def test_current_human_interfaces_do_not_generate_conversation_semantics() -> None:
    aicli_source = Path("aigol/cli/aicli.py").read_text()
    next_source = Path("aigol/acli_next/conversational.py").read_text()

    assert "_summary_from_resolution" not in aicli_source
    assert "Platform Core approval_summary is required" in aicli_source
    assert "Platform Core fail_closed_response is required" in aicli_source
    assert "Platform Core approval_summary is required" in next_source
    assert "Platform Core fail_closed_response is required" in next_source
