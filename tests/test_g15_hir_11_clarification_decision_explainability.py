from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (runtime_root / session_id / "uhi_clarification_continuity").glob("*.json")
        )
    ]


def _conversation(context: dict) -> dict:
    conversation = context["human_conversation_experience"]
    assert isinstance(conversation, dict)
    return conversation


def test_rejected_clarification_answer_explains_decision_without_repeating_blindly(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    session_id = "G15-HIR-11-EXPLAINABILITY"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader([
            "It should be reusable and shared by all Human Interfaces.",
            "/send",
            "/cancel",
        ]),
        output_writer=output.append,
    )

    contexts = _contexts(tmp_path, session_id)
    first_question = _conversation(contexts[0])["clarification_questions"][0]
    second_conversation = _conversation(contexts[1])
    second_question = second_conversation["clarification_questions"][0]
    resolution = contexts[1]["development_intent_resolution"]
    explainability = resolution["clarification_decision_explainability"]
    continuity = _continuity(tmp_path, session_id)[0]
    rendered = "\n".join(output)

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert result["clarification_question_count"] == 2
    assert first_question == "What outcome should the human interface architecture decision enable?"
    assert second_question != first_question

    assert explainability["active_semantic_slot"] == "architecture_outcome"
    assert explainability["expected_semantic_outcome"] == (
        "a reusable architecture outcome with an observable user-facing effect"
    )
    assert explainability["accepted_semantic_requirements"] == [
        "Human Interface neutrality",
        "reusable Platform Core behavior",
    ]
    assert explainability["unresolved_semantic_requirements"] == [
        "observable user-visible outcome"
    ]
    assert explainability["deterministic_continuation_status"] == "BLOCKED"
    assert explainability["semantic_reasoning_only"] is True
    assert explainability["implementation_internals_exposed"] is False
    assert explainability["human_interface_authority"] is False

    assert "Current semantic slot: architecture outcome." in second_conversation["user_explanation"]
    assert "Accepted: Human Interface neutrality, reusable Platform Core behavior." in rendered
    assert "Still required: observable user-visible outcome." in rendered
    assert "Deterministic continuation is blocked" in rendered

    satisfaction = resolution["clarification_satisfaction_verification"]
    assert satisfaction["clarification_decision_explainability"] == explainability
    assert continuity["clarification_satisfaction_verification"][
        "clarification_decision_explainability"
    ] == explainability
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
