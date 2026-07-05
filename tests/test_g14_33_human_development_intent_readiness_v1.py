from __future__ import annotations

from aigol.runtime.platform_core_project_services import resolve_development_intent


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Implement governance validation utility.",
        "project_knowledge_index": {
            "known_goal_targets": ["active_objective"],
            "certified_artifacts_by_target": {},
            "related_milestones_by_target": {},
            "implementation_history_by_target": {},
        },
    }


def test_human_development_intent_supported_prompt_catalogue() -> None:
    prompts = [
        "I think we should improve this.",
        "Let's continue working on the platform.",
        "I'd like to extend the current functionality.",
        "Can we improve this implementation?",
        "We should probably refactor this.",
        "Continue where we stopped.",
        "Let's finish what we started.",
        "Pick up the previous task.",
        "Resume implementation.",
        "Extend the current capability.",
        "Improve the previous implementation.",
        "Add another feature.",
        "Expand this solution.",
    ]

    for prompt in prompts:
        result = resolve_development_intent(message=prompt, workspace_state=_workspace_state())
        assert result["development_intent_resolution_authority"] == "PLATFORM_CORE"
        assert result["summary_admissible"] is True
        assert result["runtime_binding_admissible"] is True
        assert result["native_development_prompt_detected"] is True
        assert result["clarification_required"] is False


def test_human_development_intent_partial_prompt_catalogue_remains_non_executing() -> None:
    prompts = [
        "I have another idea.",
        "I think something is missing.",
        "Check whether this already exists.",
        "We probably implemented something similar.",
        "Can we reuse an existing capability?",
        "Search previous work before creating anything new.",
        "I have an idea but I'm not sure how to implement it.",
        "Something should be improved here.",
        "Help me decide what to build next.",
        "I'm not sure what to do next.",
        "What do you recommend?",
        "Is there already something similar?",
        "This probably belongs in Platform Core.",
        "Should this stay inside the interface?",
        "Can we make this reusable?",
    ]

    for prompt in prompts:
        result = resolve_development_intent(message=prompt, workspace_state=_workspace_state())
        assert result["runtime_binding_admissible"] is False
        assert result["summary_admissible"] is False


def test_human_development_intent_requires_workspace_for_context_bound_phrasing() -> None:
    prompts = [
        "I think we should improve this.",
        "Can we improve this implementation?",
        "Continue where we stopped.",
        "Resume implementation.",
    ]

    for prompt in prompts:
        result = resolve_development_intent(message=prompt)
        assert result["runtime_binding_admissible"] is False
        assert result["summary_admissible"] is False
        assert result["clarification_required"] is True
