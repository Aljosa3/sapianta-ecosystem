"""G23-02B regressions for the Architectural Meta-Audit query binding."""

from __future__ import annotations

from unittest.mock import patch

from aigol.runtime.platform_knowledge_runtime import validate_platform_knowledge_response
from aigol.runtime.platform_presentation_layer import PRESENTATION_FAILED_CLOSED, PRESENTATION_READY, present_platform_response
from aigol.runtime.platform_query_router import (
    ARCHITECTURAL_META_AUDIT_ROUTE,
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    ROUTE_READY,
    route_platform_query,
    validate_platform_query_router_response,
)


CREATED_AT = "2026-07-12T00:00:00Z"
META_AUDIT_REQUEST = """Perform an AUDIT_ONLY architectural completion meta-audit.

Determine whether Platform Core is architecturally complete. Do not implement or plan anything.

Evaluate the existing inventory: Project Objective, Capability Coverage, Development
Composition Plan, Durable Governed Work, Approval, Replay, and Certification.
"""


def test_architectural_completion_audit_selects_canonical_query_class() -> None:
    response = route_platform_query(query=META_AUDIT_REQUEST, created_at=CREATED_AT)
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    plan_candidate = next(
        item
        for item in response["candidate_routes"]
        if item["service_identifier"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    )
    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == ARCHITECTURAL_META_AUDIT_ROUTE
    assert response["selected_query_class"] == "ARCHITECTURAL_META_AUDIT"
    assert plan_candidate["score"] == 0
    assert response["classification_evidence"][
        "clause_role_interpretation_authoritative"
    ] is True
    assert audit["architectural_meta_audit_status"] == "ARCHITECTURAL_META_AUDIT_READY"
    assert audit["capability_certification_record_count"] > 0
    assert audit["project_objective_hash"]
    assert audit["governance_evidence"]
    assert audit["provider_invoked"] is False
    assert audit["worker_invoked"] is False
    assert audit["repository_mutated"] is False
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert validate_platform_query_router_response(response) == response
    assert validate_platform_knowledge_response(audit) == audit


def test_explicit_planning_request_still_selects_development_plan() -> None:
    response = route_platform_query(
        query=(
            "Create a governed Development Composition Plan for platform knowledge "
            "with an ordered implementation sequence."
        ),
        created_at=CREATED_AT,
    )

    assert response["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert response["selected_query_class"] == "DEVELOPMENT_COMPOSITION_PLAN"


def test_meta_audit_fails_closed_when_registry_evidence_is_missing() -> None:
    with patch(
        "aigol.runtime.platform_query_router.list_platform_capability_certifications",
        return_value=[],
    ):
        response = route_platform_query(query=META_AUDIT_REQUEST, created_at=CREATED_AT)
    presentation = present_platform_response(response, created_at=CREATED_AT)

    audit = response["service_response"]
    assert audit["architectural_meta_audit_status"] == (
        "ARCHITECTURAL_META_AUDIT_FAILED_CLOSED"
    )
    assert "capability certification registry evidence" in audit[
        "required_architectural_evidence_missing"
    ]
    assert presentation["presentation_status"] == PRESENTATION_FAILED_CLOSED
