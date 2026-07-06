"""Regression coverage for G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION,
    prepare_unified_human_interface_project_context,
    resolve_development_intent,
)


CREATED_AT = "2026-07-06T00:00:00Z"


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Improve governed development experience.",
        "project_knowledge_index": {
            "known_goal_targets": ["development_experience", "replay"],
            "certified_artifacts_by_target": {
                "development_experience": [
                    "docs/governance/G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1.md"
                ],
                "replay": ["governance/UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1.md"],
            },
            "related_milestones_by_target": {
                "development_experience": ["G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1"]
            },
            "implementation_history_by_target": {
                "development_experience": ["Improve governed development experience."]
            },
        },
    }


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def test_natural_language_requests_infer_capabilities_without_capability_names() -> None:
    scenarios = {
        "I have an idea to improve governance documentation.": "governance_documentation",
        "I want to make development easier.": "development_experience",
        "Let's make certification simpler.": "certification",
        "Can we improve replay?": "replay",
    }

    for prompt, expected_target in scenarios.items():
        result = resolve_development_intent(message=prompt, workspace_state=_workspace_state())
        discovery = result["candidate_capability_discovery"]

        assert discovery["runtime_version"] == PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION
        assert discovery["capability_discovery_authority"] == "PLATFORM_CORE"
        assert discovery["selected_goal_target"] == expected_target
        assert discovery["requires_human_capability_name"] is False
        assert result["human_capability_name_required"] is False
        assert result["summary_admissible"] is True
        assert result["runtime_binding_admissible"] is True
        assert result["clarification_required"] is False


def test_knowledge_reuse_receives_inferred_candidates_before_clarification(tmp_path: Path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-47-KNOWLEDGE",
        message="I have an idea to improve governance documentation.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )

    intent = context["development_intent_resolution"]
    knowledge = context["knowledge_reuse"]
    conversation = context["human_conversation_experience"]

    assert intent["candidate_capability_discovery"]["selected_goal_target"] == "governance_documentation"
    assert knowledge["candidate_capabilities_received"]
    assert knowledge["capability_resolution_decision"] == "EXTENDS_EXISTING_CAPABILITY"
    assert knowledge["reuse_recommended"] is True
    assert "Candidate capability discovery completed." in conversation["progress_messages"]
    assert conversation["human_capability_name_required"] is False


def test_clarification_is_goal_oriented_when_inference_is_insufficient(tmp_path: Path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G14-47-CLARIFY",
        message="I have an idea.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    conversation = context["human_conversation_experience"]

    assert conversation["response_mode"] == "CLARIFICATION"
    assert conversation["candidate_capabilities"] == []
    assert conversation["human_capability_name_required"] is False
    assert conversation["clarification_questions"]
    assert all("What capability" not in question for question in conversation["clarification_questions"])
    assert any("outcome" in question.lower() for question in conversation["clarification_questions"])


def test_aicli_remains_thin_adapter_for_capability_resolution(tmp_path: Path) -> None:
    calls: list[dict] = []

    def runtime_runner(**kwargs):
        calls.append(kwargs)
        return {"canonical_runtime_entry_status": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND"}

    result = aicli.run_reference_uhi_session(
        session_id="G14-47-AICLI",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["I have an idea to improve governance documentation.", "/send", "/approve", "/exit"]),
        output_writer=lambda _line: None,
        runtime_runner=runtime_runner,
    )

    context = result["platform_core_project_services_context"]
    assert result["runtime_entered"] is True
    assert calls
    assert context["interface_authority"] is False
    assert context["development_intent_resolution"]["candidate_capability_discovery"][
        "capability_discovery_authority"
    ] == "PLATFORM_CORE"
