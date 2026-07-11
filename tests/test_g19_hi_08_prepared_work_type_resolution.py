from __future__ import annotations

from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION,
    resolve_development_intent,
    resolve_prepared_work_type,
)


def test_runtime_prompt_wording_is_evidence_not_prepared_work_type_authority() -> None:
    result = resolve_development_intent(
        message=(
            "Implement the audit report generator.\n\n"
            "work_type: AUDIT_ONLY\n"
            "Do not implement or modify runtime behavior."
        )
    )

    assert result["requested_work_type"] == "AUDIT_ONLY"
    assert result["prepared_work_type"] == "AUDIT_ONLY"
    assert result["prepared_work_type_resolution_version"] == (
        PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION
    )
    assert result["prepared_work_type_resolution"]["prepared_work_type_source"] == (
        "REQUESTED_WORK_TYPE_METADATA"
    )
    assert result["runtime_prompt_work_type_signal"]["runtime_prompt_work_type_signal"] == (
        "IMPLEMENTATION"
    )
    assert result["prepared_work_type_resolution"][
        "runtime_prompt_wording_changes_prepared_work_type"
    ] is False
    assert result["work_type_conflict_detected"] is False
    assert result["runtime_binding_admissible"] is False


def test_authorized_governed_transition_can_change_prepared_work_type() -> None:
    resolution = resolve_prepared_work_type(
        requested_work_type="AUDIT_ONLY",
        canonical_runtime_prompt="Implement as a governed development workflow.",
        governed_work_type_transition={
            "transition_authority": "PLATFORM_CORE",
            "work_type_change_authorized": True,
            "human_authorization_recorded": True,
            "replay_visible": True,
            "prepared_work_type": "IMPLEMENTATION",
        },
    )

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert resolution["prepared_work_type"] == "IMPLEMENTATION"
    assert resolution["prepared_work_type_source"] == "AUTHORIZED_GOVERNED_WORK_TYPE_TRANSITION"
    assert resolution["governed_work_type_transition_authorized"] is True
    assert resolution["work_type_change_allowed"] is True
    assert resolution["runtime_prompt_wording_changes_prepared_work_type"] is False


def test_unauthorized_governed_transition_does_not_change_prepared_work_type() -> None:
    resolution = resolve_prepared_work_type(
        requested_work_type="AUDIT_ONLY",
        canonical_runtime_prompt="Implement as a governed development workflow.",
        governed_work_type_transition={
            "transition_authority": "PLATFORM_CORE",
            "work_type_change_authorized": True,
            "human_authorization_recorded": False,
            "replay_visible": True,
            "prepared_work_type": "IMPLEMENTATION",
        },
    )

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert resolution["prepared_work_type"] == "AUDIT_ONLY"
    assert resolution["prepared_work_type_source"] == "REQUESTED_WORK_TYPE_METADATA"
    assert resolution["governed_work_type_transition_authorized"] is False
    assert resolution["work_type_change_allowed"] is False
    assert resolution["runtime_prompt_work_type_signal"]["runtime_prompt_work_type_signal"] == (
        "IMPLEMENTATION"
    )
