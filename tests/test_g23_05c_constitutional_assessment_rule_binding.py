"""G23-05C regressions for the constitutional assessment-rule binding."""

from __future__ import annotations

from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_FAILED_CLOSED,
    PRESENTATION_READY,
    present_platform_response,
)
from aigol.runtime.platform_query_router import (
    ARCHITECTURAL_META_AUDIT_ROUTE,
    CONSTITUTIONAL_ASSESSMENT_RULE,
    route_platform_query,
)


CREATED_AT = "2026-07-12T00:00:00Z"
QUERY = (
    "Perform an AUDIT_ONLY constitutional certification audit. Determine whether "
    "Platform Core is constitutionally regarded as the stable deterministic "
    "cognition and governance infrastructure for AiGOL."
)
WORKSPACE_STATE = {
    "replay_reference": ".runtime/aicli/G23-05C/workspace_state",
    "artifact_hash": "sha256:g23-05c-workspace-state",
}


def test_constitutional_certification_produces_substantive_verdict() -> None:
    response = route_platform_query(
        query=QUERY,
        workspace_state=WORKSPACE_STATE,
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    assessment = audit["constitutional_assessment"]
    assert response["selected_service"] == ARCHITECTURAL_META_AUDIT_ROUTE
    assert assessment["assessment_rule"] == CONSTITUTIONAL_ASSESSMENT_RULE
    assert assessment["assessment_rule_applied"] is True
    assert assessment["assessment_status"] == "CONSTITUTIONAL_ASSESSMENT_READY"
    assert assessment["constitutional_verdict"] == (
        "PLATFORM_CORE_CONSTITUTIONALLY_READY_AS_STABLE_DETERMINISTIC_COGNITION_AND_GOVERNANCE_INFRASTRUCTURE_WITH_BOUNDED_STABILIZATION_REMAINING"
    )
    assert assessment["required_evidence_complete"] is True
    assert assessment["criteria"]
    assert assessment["evidence_consumed"]["replay_evidence"]
    assert assessment["provider_invoked"] is False
    assert assessment["worker_invoked"] is False
    assert assessment["repository_mutated"] is False
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["answer"]["constitutional_verdict"] == assessment[
        "constitutional_verdict"
    ]


def test_constitutional_assessment_fails_closed_without_replay_evidence() -> None:
    response = route_platform_query(query=QUERY, created_at=CREATED_AT)
    presentation = present_platform_response(response, created_at=CREATED_AT)

    assessment = response["service_response"]["constitutional_assessment"]
    assert assessment["assessment_status"] == "CONSTITUTIONAL_ASSESSMENT_FAILED_CLOSED"
    assert assessment["constitutional_verdict"] == "CONSTITUTIONAL_CERTIFICATION_NOT_DETERMINED"
    assert "replay lineage evidence" in assessment["required_evidence_missing"]
    assert presentation["presentation_status"] == PRESENTATION_FAILED_CLOSED


def test_existing_architectural_meta_audit_contract_remains_unchanged() -> None:
    response = route_platform_query(
        query=(
            "Perform an AUDIT_ONLY architectural completion meta-audit. Determine "
            "whether Platform Core is architecturally complete. Do not implement or "
            "plan anything."
        ),
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    assert audit["constitutional_assessment"] is None
    assert audit["architectural_certification_assessment"]["assessment_verdict"] == (
        "EXISTING_CERTIFIED_PLATFORM_CAPABILITIES_SATISFY_REQUESTED_COMPOSITION"
    )
    assert presentation["answer"]["constitutional_verdict"] is None
