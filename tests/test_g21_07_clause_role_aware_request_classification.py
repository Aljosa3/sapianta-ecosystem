from __future__ import annotations

from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    resolve_development_intent,
    resolve_governed_work_type,
)


def test_non_mutating_validation_binds_to_existing_audit_only_work_type() -> None:
    request = (
        "Validate implementation. Do not implement. "
        "Return the governed read-only result only."
    )

    resolution = resolve_development_intent(message=request)

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert resolution["prepared_work_type"] == "AUDIT_ONLY"
    assert resolution["summary_admissible"] is False
    assert resolution["requires_human_approval"] is False
    assert resolution["read_only_work_binding_admissible"] is True
    assert resolution["governed_work_type_metadata"]["work_type_source"] == (
        "EXPLICIT_NON_MUTATING_VALIDATION_OBJECTIVE"
    )


def test_architectural_and_tool_references_do_not_become_capability_targets(tmp_path) -> None:
    request = (
        "Perform a root cause audit of request classification. "
        "Runtime evidence referenced ./aicli, the Human Interface, Providers, and Workers. "
        "Those components behaved correctly and are architectural boundaries. "
        "Do not implement anything."
    )

    context = prepare_unified_human_interface_project_context(
        interface_name="test-uhi",
        session_id="G21-07-REFERENCES",
        message=request,
        runtime_root=tmp_path,
        workspace=".",
        created_at="2026-07-12T00:00:00Z",
    )
    resolution = context["development_intent_resolution"]
    discovery = resolution["candidate_capability_discovery"]

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert discovery["selected_goal_target"] == "general_project_goal"
    assert discovery["candidate_capabilities"] == []
    assert resolution["clarification_required"] is False
    assert resolution.get("selected_missing_semantic_slot") != "reuse_delta"
    assert resolution["summary_admissible"] is False
    assert context["governed_read_only_work_result"]["provider_invoked"] is False
    assert context["governed_read_only_work_result"]["worker_invoked"] is False
    assert context["governed_read_only_work_result"]["repository_mutated"] is False


def test_validate_without_non_mutation_constraint_remains_implementation() -> None:
    resolution = resolve_development_intent(
        message="Implement validation for replay evidence."
    )

    assert resolution["requested_work_type"] == "IMPLEMENTATION"
    assert resolution["summary_admissible"] is True
    assert resolution["mutation_allowed"] is True


def test_explicit_canonical_work_type_retains_precedence() -> None:
    metadata = resolve_governed_work_type(
        "work_type: REVIEW\nValidate the implementation. Do not implement."
    )

    assert metadata["requested_work_type"] == "REVIEW"
    assert metadata["work_type_source"] == "EXPLICIT_HUMAN_WORK_TYPE_DECLARATION"


def test_existing_fail_closed_ambiguity_is_preserved() -> None:
    metadata = resolve_governed_work_type(
        "work_type: REVIEW\nwork_type: ANALYSIS\nConfirm the result. Do not modify."
    )

    assert metadata["requested_work_type"] == "REVIEW"
    assert metadata["work_type_source"] == (
        "CONFLICTING_EXPLICIT_HUMAN_WORK_TYPE_DECLARATIONS"
    )
