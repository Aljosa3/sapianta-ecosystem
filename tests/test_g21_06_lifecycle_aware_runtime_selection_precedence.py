"""Regression coverage for G21-06 lifecycle-aware route precedence."""

from __future__ import annotations

from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_READY,
    present_platform_response,
)
from aigol.runtime.platform_query_router import (
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    DURABLE_GOVERNED_WORK_ROUTE,
    ROUTE_CLARIFICATION_REQUIRED,
    ROUTE_READY,
    PlatformServiceRouteDescriptor,
    route_platform_query,
    validate_platform_query_router_response,
)


CREATED_AT = "2026-07-12T00:00:00Z"
LIFECYCLE_QUERY = (
    "work_type: AUDIT_ONLY\nCreate a governed development plan for platform knowledge "
    "and query routing with an ordered implementation sequence, then create durable "
    "governed work and a durable work artifact."
)


def test_plan_entry_runtime_precedes_tied_automatic_durable_transition() -> None:
    response = route_platform_query(query=LIFECYCLE_QUERY, created_at=CREATED_AT)

    scores = {
        candidate["service_identifier"]: candidate["score"]
        for candidate in response["candidate_routes"]
    }
    assert scores[DEVELOPMENT_COMPOSITION_PLAN_ROUTE] == 100
    assert scores[DURABLE_GOVERNED_WORK_ROUTE] == 100
    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert response["service_invoked"] is True
    assert response["service_response"]["artifact_type"] == (
        "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1"
    )
    assert response["lifecycle_precedence_applied"] is True
    assert response["suppressed_downstream_lifecycle_routes"] == [
        DURABLE_GOVERNED_WORK_ROUTE
    ]
    assert response["lifecycle_precedence"]["canonical_entry_runtime"] == (
        DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    )
    assert validate_platform_query_router_response(response) == response


def test_lifecycle_precedence_produces_ready_presentation() -> None:
    router = route_platform_query(query=LIFECYCLE_QUERY, created_at=CREATED_AT)
    presentation = present_platform_response(router, created_at=CREATED_AT)

    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert presentation["source_artifact_type"] == (
        "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1"
    )


def test_project_services_runs_automatic_durable_transition_after_entry(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G21-06-LIFECYCLE",
        message=LIFECYCLE_QUERY,
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]
    durable = result["durable_governed_work_artifact"]

    assert result["selected_read_only_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert result["presentation_status"] == PRESENTATION_READY
    assert durable["artifact_type"] == "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
    assert durable["provider_invoked"] is False
    assert durable["worker_invoked"] is False
    assert durable["repository_mutated"] is False


def test_unrelated_top_score_tie_still_requires_clarification() -> None:
    first = PlatformServiceRouteDescriptor(
        service_identifier="UNRELATED_RUNTIME_A",
        service_owner="PLATFORM_CORE_TEST",
        implementation_owner="tests.runtime_a",
        query_classes=("TEST_A",),
        required_inputs=("query",),
        response_artifact_type="TEST_A_V1",
        service_version="TEST_A_V1",
        adapter_name="runtime_a",
        routing_terms=("unrelated", "tie"),
    )
    second = PlatformServiceRouteDescriptor(
        service_identifier="UNRELATED_RUNTIME_B",
        service_owner="PLATFORM_CORE_TEST",
        implementation_owner="tests.runtime_b",
        query_classes=("TEST_B",),
        required_inputs=("query",),
        response_artifact_type="TEST_B_V1",
        service_version="TEST_B_V1",
        adapter_name="runtime_b",
        routing_terms=("unrelated", "tie"),
    )

    response = route_platform_query(
        query="unrelated tie",
        route_descriptors=(first, second),
        route_adapters={
            "UNRELATED_RUNTIME_A": lambda **_: {"artifact_type": "TEST_A_V1"},
            "UNRELATED_RUNTIME_B": lambda **_: {"artifact_type": "TEST_B_V1"},
        },
    )

    assert response["route_status"] == ROUTE_CLARIFICATION_REQUIRED
    assert response["service_invoked"] is False
    assert response["lifecycle_precedence_applied"] is False
