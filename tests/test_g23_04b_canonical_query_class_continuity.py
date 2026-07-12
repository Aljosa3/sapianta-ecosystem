"""G23-04B regressions for query-class continuity across clarification."""

from __future__ import annotations

from aigol.runtime.platform_core_project_services import (
    resolve_uhi_clarification_continuity,
    run_governed_read_only_work_binding,
)
from aigol.runtime.platform_query_router import (
    ARCHITECTURAL_META_AUDIT_ROUTE,
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
)


CREATED_AT = "2026-07-12T00:00:00Z"
ORIGINAL_QUERY = "Perform an AUDIT_ONLY architectural certification audit."
CLARIFICATION_REPLY = (
    "The certification workflow architecture decision shall determine whether "
    "Platform Core should transition from cognition toward governed execution "
    "using existing deterministic evidence and preserving constitutional boundaries, "
    "providing a reusable Platform Core behavior and observable user-visible outcome."
)


def _active_state() -> dict:
    return {
        "session_id": "G23-04B",
        "original_message": ORIGINAL_QUERY,
        "requested_work_type": "AUDIT_ONLY",
        "work_type": "AUDIT_ONLY",
        "prepared_work_type": "AUDIT_ONLY",
        "work_type_source": "EXPLICIT_HUMAN_WORK_TYPE_DECLARATION",
        "work_type_source_text": "audit_only",
        "clarification_questions": [
            "What outcome should the certification workflow architecture decision enable?"
        ],
        "workspace_state_reference": ".runtime/test/workspace_state",
        "workspace_state_hash": "sha256:test-workspace-state",
    }


def test_architectural_certification_query_class_survives_clarification(tmp_path) -> None:
    resolution, continuity = resolve_uhi_clarification_continuity(
        message=CLARIFICATION_REPLY,
        workspace_state=None,
        active_clarification_state=_active_state(),
        session_root=tmp_path / "G23-04B",
        created_at=CREATED_AT,
    )
    result = run_governed_read_only_work_binding(
        message=resolution["clarification_resolved_query"],
        workspace_state=None,
        development_intent=resolution,
        created_at=CREATED_AT,
    )

    assert continuity["original_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert continuity["clarification_query_class"] == "ARCHITECTURAL_KNOWLEDGE"
    assert continuity["final_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert continuity["query_class_continuity_preserved"] is True
    assert continuity["query_class_continuity_decision"] == (
        "ORIGINAL_QUERY_CLASS_PRESERVED"
    )
    assert continuity["original_selected_composition_capability"] == (
        ARCHITECTURAL_META_AUDIT_ROUTE
    )
    assert continuity["final_selected_composition_capability"] == (
        ARCHITECTURAL_META_AUDIT_ROUTE
    )
    assert result["selected_read_only_service"] == ARCHITECTURAL_META_AUDIT_ROUTE
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_explicit_clarification_intent_change_reclassifies(tmp_path) -> None:
    resolution, continuity = resolve_uhi_clarification_continuity(
        message=(
            "Instead, create a governed Development Composition Plan with an "
            "ordered implementation sequence."
        ),
        workspace_state=None,
        active_clarification_state=_active_state(),
        session_root=tmp_path / "G23-04B-RECLASSIFIED",
        created_at=CREATED_AT,
    )

    assert continuity["original_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert continuity["final_query_class"] == "DEVELOPMENT_COMPOSITION_PLAN"
    assert continuity["query_class_continuity_preserved"] is False
    assert continuity["clarification_explicit_intent_change"] is True
    assert continuity["query_class_continuity_decision"] == (
        "QUERY_CLASS_RECLASSIFIED_EXPLICIT_INTENT_CHANGE"
    )
    assert continuity["final_selected_composition_capability"] == (
        DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    )
    assert resolution["clarification_resolved_query"].startswith("Instead,")


def test_undeclared_query_class_change_fails_closed(tmp_path) -> None:
    active = _active_state()
    active["original_message"] = (
        "Create a governed Development Composition Plan with an ordered "
        "implementation sequence."
    )
    resolution, continuity = resolve_uhi_clarification_continuity(
        message=(
            "The architectural certification audit should provide a reusable "
            "Platform Core behavior and observable user-visible outcome."
        ),
        workspace_state=None,
        active_clarification_state=active,
        session_root=tmp_path / "G23-04B-FAILED-CLOSED",
        created_at=CREATED_AT,
    )

    assert continuity["original_query_class"] == "DEVELOPMENT_COMPOSITION_PLAN"
    assert continuity["final_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert continuity["query_class_continuity_decision"] == (
        "QUERY_CLASS_CONTINUITY_FAILED_CLOSED"
    )
    assert resolution["query_class_continuity_failed_closed"] is True
    assert resolution["clarification_required"] is True
    assert resolution["read_only_work_binding_admissible"] is False
    assert resolution["runtime_binding_admissible"] is False
