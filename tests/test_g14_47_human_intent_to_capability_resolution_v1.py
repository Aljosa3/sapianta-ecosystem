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


def test_aicli_remains_thin_adapter_for_capability_resolution(tmp_path: Path, monkeypatch) -> None:
    import re
    from test_g66_13_canonical_typed_semantic_composition_convergence import _manifest

    # A raw development turn no longer enters the legacy runner. Use the
    # current certified normalization route with exact G59/G66 controls.
    _manifest(tmp_path / "workspace" / "artifact")
    manifest_path = (
        tmp_path / "workspace" / "artifact" / "manifest"
        / "000_implementation_manifest_recorded.json"
    )
    calls: list[dict] = []
    original_entry = aicli.run_human_interface_runtime_entry
    def observe_entry(**kwargs):
        result = original_entry(**kwargs)
        calls.append(result)
        return result
    monkeypatch.setattr(aicli, "run_human_interface_runtime_entry", observe_entry)

    output: list[str] = []
    fixed = iter([
        "I have an idea to improve governance documentation.", "/send",
        "action: Implement and normalize", "/send",
        "subject: a repository implementation change", "/send",
        "outcome: canonical change evidence", "/send",
        "work-type: ANALYSIS", "/send",
    ])
    phase = 0
    def reader(_prompt: str) -> str:
        nonlocal phase
        try:
            return next(fixed)
        except StopIteration:
            controls = ("confirm", "commit")
            if phase in (0, 2):
                control = controls[phase // 2]
                matches = re.findall(r"/" + control + r" sha256:[0-9a-f]{64}", "\n".join(output))
                assert matches, control
                phase += 1
                return matches[-1]
            if phase in (1, 3):
                phase += 1
                return "/send"
            return "/exit"

    def unexpected_runner(**kwargs):
        raise AssertionError("AiCLI must not bypass certified admission through the legacy runner")

    result = aicli.run_reference_uhi_session(
        session_id="G14-47-AICLI", created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime", workspace=tmp_path / "workspace",
        input_reader=reader, output_writer=output.append,
        runtime_runner=unexpected_runner, artifact_references=[str(manifest_path)],
    )
    assert calls
    confirmed = next(
        call for call in calls
        if (call.get("canonical_typed_semantic_composition") or {}).get("control")
        == "CANDIDATE_CONFIRMATION"
    )
    assert confirmed["production_conversation_binding"]["objective_readiness_report"][
        "readiness_disposition"
    ] == "READY"
    committed = next(
        call for call in calls
        if (call.get("canonical_typed_semantic_composition") or {}).get("control")
        == "OBJECTIVE_COMMITMENT"
    )
    admission = committed["committed_objective_admission"]
    assert admission["admission_status"] == "COMMITTED_OBJECTIVE_ADMITTED_TO_PLATFORM_CORE"
    assert admission["platform_core_admission"]["admission_status"] == (
        "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
    )
    assert admission["authorization_granted"] is False
    assert admission["worker_dispatched"] is False
    assert admission["execution_started"] is False
    assert result["runtime_entered"] is False
    context = result["platform_core_project_services_context"]
    assert context["interface_authority"] is False
    assert context["semantic_capability_runtime_route"]["selected_capability_identifier"] == (
        "PLATFORM_CHANGE_NORMALIZATION"
    )
