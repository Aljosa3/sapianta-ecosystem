"""Regression coverage for G14_48_GOAL_ORIENTED_CLARIFICATION_EXPERIENCE_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli
from aigol.runtime.platform_core_project_services import prepare_unified_human_interface_project_context


CREATED_AT = "2026-07-06T00:00:00Z"
FORBIDDEN_QUESTION_TERMS = (
    "workspace history",
    "certified artifacts",
    "both",
    "knowledge reuse",
    "which capability",
    "what capability",
    "which internal",
    "internal platform core",
    "which internal milestone",
    "evidence sources",
)


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Improve governance validation utility.",
        "project_knowledge_index": {
            "known_goal_targets": ["governance_validation"],
            "certified_artifacts_by_target": {
                "governance_validation": [
                    "runtime/governance/governance_conformance_engine.py",
                ],
            },
            "related_milestones_by_target": {
                "governance_validation": ["GOVERNANCE_CONFORMANCE_SYSTEM_V1"],
            },
            "implementation_history_by_target": {
                "governance_validation": ["Improve governance validation utility."],
            },
        },
    }


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def _questions_for(prompt: str, tmp_path: Path) -> tuple[list[str], dict]:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-48-" + str(abs(hash(prompt))),
        message=prompt,
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    conversation = context["human_conversation_experience"]
    return conversation["clarification_questions"], context


def test_clarification_questions_do_not_expose_internal_evidence_selection(tmp_path: Path) -> None:
    prompts = [
        "Check whether we already implemented this.",
        "Can we reuse an existing capability?",
        "Should this belong in Platform Core?",
        "I have an idea.",
    ]

    for prompt in prompts:
        questions, _context = _questions_for(prompt, tmp_path)
        assert questions
        joined = " ".join(questions).lower()
        for term in FORBIDDEN_QUESTION_TERMS:
            assert term not in joined
        assert any(
            word in joined
            for word in ("outcome", "problem", "goal", "change", "solve", "user-visible")
        )


def test_platform_core_selects_reuse_evidence_sources_automatically(tmp_path: Path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-48-EVIDENCE",
        message="I have an idea to improve governance validation.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    knowledge = context["knowledge_reuse"]
    evidence_selection = knowledge["knowledge_reuse_evidence_selection"]

    assert knowledge["workspace_inspected"] is True
    assert knowledge["certified_artifacts_inspected"] is True
    assert evidence_selection["selection_authority"] == "PLATFORM_CORE"
    assert evidence_selection["human_selects_sources"] is False
    assert knowledge["human_selects_evidence_sources"] is False
    assert knowledge["evidence_selection_authority"] == "PLATFORM_CORE"


def test_goal_oriented_reuse_clarification_uses_inferred_candidate_without_strategy_terms(
    tmp_path: Path,
) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-48-REUSE",
        message="Can we reuse governance validation?",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    conversation = context["human_conversation_experience"]

    assert conversation["response_mode"] == "CLARIFICATION"
    assert conversation["candidate_capabilities"]
    assert conversation["human_capability_name_required"] is False
    joined = " ".join(conversation["clarification_questions"]).lower()
    assert "workspace history" not in joined
    assert "certified artifacts" not in joined
    assert "what problem" in joined or "what outcome" in joined


def test_aicli_remains_thin_adapter_for_goal_oriented_clarification(tmp_path: Path) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G14-48-AICLI",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Can we reuse governance validation?", "/send", "/exit"]),
        output_writer=output.append,
        runtime_runner=lambda **_kwargs: {},
    )
    rendered = "\n".join(output).lower()

    assert result["runtime_entered"] is False
    assert result["platform_core_project_services_context"]["interface_authority"] is False
    assert "workspace history" not in rendered
    assert "certified artifacts" not in rendered
    assert "what problem" in rendered or "what outcome" in rendered
