"""G23-03B regressions for Architectural Certification query binding."""

from __future__ import annotations

import pytest

from aigol.runtime.platform_presentation_layer import PRESENTATION_READY, present_platform_response
from aigol.runtime.platform_query_router import (
    ARCHITECTURAL_META_AUDIT_ROUTE,
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    PLATFORM_KNOWLEDGE_ROUTE,
    route_platform_query,
)


CREATED_AT = "2026-07-12T00:00:00Z"


@pytest.mark.parametrize(
    "query",
    (
        "Architectural Certification Audit",
        "Platform Certification Audit",
        "Platform Architectural Certification",
        "Platform Certification Assessment",
        "Architectural Certification",
    ),
)
def test_architectural_certification_synonyms_select_existing_meta_audit_route(
    query: str,
) -> None:
    response = route_platform_query(query=query, created_at=CREATED_AT)
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    assessment = audit["architectural_certification_assessment"]
    assert response["selected_service"] == ARCHITECTURAL_META_AUDIT_ROUTE
    assert response["selected_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert response["service_invoked"] is True
    assert assessment["assessment_status"] in {
        "ARCHITECTURAL_CERTIFICATION_ASSESSMENT_READY",
        "ARCHITECTURAL_CERTIFICATION_ASSESSMENT_FAILED_CLOSED",
    }
    assert audit["provider_invoked"] is False
    assert audit["worker_invoked"] is False
    assert audit["repository_mutated"] is False


def test_architectural_certification_audit_presents_integrated_assessment() -> None:
    response = route_platform_query(
        query="Architectural Certification Audit",
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    assessment = audit["architectural_certification_assessment"]
    assert assessment["assessment_status"] == (
        "ARCHITECTURAL_CERTIFICATION_ASSESSMENT_READY"
    )
    assert assessment["assessment_verdict"] == (
        "EXISTING_CERTIFIED_PLATFORM_CAPABILITIES_SATISFY_REQUESTED_COMPOSITION"
    )
    assert assessment["required_evidence_sufficient"] is True
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["answer"]["architectural_certification_verdict"] == (
        assessment["assessment_verdict"]
    )


def test_existing_planning_and_platform_knowledge_routes_are_preserved() -> None:
    planning = route_platform_query(
        query="Create a governed Development Composition Plan.",
        created_at=CREATED_AT,
    )
    knowledge = route_platform_query(
        query="Does the Platform Knowledge Runtime capability exist?",
        created_at=CREATED_AT,
    )

    assert planning["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert knowledge["selected_service"] == PLATFORM_KNOWLEDGE_ROUTE
