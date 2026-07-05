from __future__ import annotations

from pathlib import Path

from aigol.acli_next.conversational import run_acli_next_persistent_conversational_session
from aigol.cli import aicli
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_VERSION,
    prepare_unified_human_interface_project_context,
)


CREATED_AT = "2026-07-05T00:00:00Z"


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def test_platform_core_conversation_model_clarifies_vague_human_requests(tmp_path: Path) -> None:
    prompts = [
        "This implementation can be better.",
        "Check whether we already implemented this.",
        "I'm not sure how to solve this.",
        "Should this belong in Platform Core?",
        "I have an idea.",
    ]

    for index, prompt in enumerate(prompts, start=1):
        context = prepare_unified_human_interface_project_context(
            interface_name="test",
            session_id=f"G14-38-{index}",
            message=prompt,
            runtime_root=tmp_path,
            workspace=".",
            created_at=CREATED_AT,
        )
        conversation = context["human_conversation_experience"]

        assert conversation["runtime_version"] == PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_VERSION
        assert conversation["conversation_authority"] == "PLATFORM_CORE"
        assert conversation["interface_executes_conversation"] is False
        assert conversation["response_mode"] == "CLARIFICATION"
        assert conversation["clarification_questions"]
        assert conversation["fail_closed_explanation"]


def test_aicli_renders_platform_core_conversation_clarification(tmp_path: Path) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G14-38-AICLI",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["This implementation can be better.", "/send", "/exit"]),
        output_writer=output.append,
        runtime_runner=lambda **_kwargs: {},
    )
    rendered = "\n".join(output)

    assert result["clarification_question_count"] == 1
    assert result["runtime_entered"] is False
    assert "I can help turn this into governed development work." in rendered
    assert "What should be improved or built?" in rendered
    assert result["platform_core_project_services_context"]["human_conversation_experience_authority"] == (
        "PLATFORM_CORE"
    )


def test_acli_next_renders_same_platform_core_conversation_clarification(tmp_path: Path) -> None:
    output: list[str] = []
    result = run_acli_next_persistent_conversational_session(
        created_at=CREATED_AT,
        replay_dir=tmp_path,
        session_id="G14-38-ACLI-NEXT",
        workspace=".",
        input_reader=_reader(["Should this belong in Platform Core?", "/send", "exit"]),
        output_writer=output.append,
        guided_development_workflow=True,
        turn_runner=lambda **_kwargs: {},
    )
    rendered = "\n".join(output)

    assert result["clarification_question_count"] == 1
    assert result["turn_count"] == 0
    assert "I can help place this architecturally, but I need the subject." in rendered
    assert "What capability, behavior, or artifact are you asking about?" in rendered
