"""G22-10B regressions for lifecycle-state-aware routing precedence."""

from __future__ import annotations

from aigol.runtime.platform_capability_composition_coverage import (
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    compose_platform_development_plan,
)
from aigol.runtime.platform_query_router import (
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    DURABLE_GOVERNED_WORK_ROUTE,
    ROUTE_READY,
    route_platform_query,
    validate_platform_query_router_response,
)


CREATED_AT = "2026-07-12T00:00:00Z"
NEW_LIFECYCLE_REQUEST = (
    "Create a governed Development Composition Plan, then create Durable Governed Work."
)
DOWNSTREAM_AUDIT_REQUEST = """Perform an AUDIT_ONLY lifecycle readiness audit.

Development Composition Plan to Durable Governed Work is already complete.

Instead inspect only the transition from Durable Governed Work to Human Approval.
Do not implement anything.
"""


def _plan() -> dict:
    coverage = discover_platform_capability_composition_coverage(
        query="Assess platform knowledge and query routing.",
        created_at=CREATED_AT,
    )
    return compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=CREATED_AT,
    )


def test_unbound_lifecycle_request_still_enters_development_plan() -> None:
    response = route_platform_query(
        query=NEW_LIFECYCLE_REQUEST,
        created_at=CREATED_AT,
    )

    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert response["lifecycle_precedence"]["lifecycle_stage"] == (
        "DEVELOPMENT_COMPOSITION_PLAN"
    )
    assert response["lifecycle_precedence"]["upstream_plan_hash"] is None
    assert response["lifecycle_precedence"]["precedence_reason"] == (
        "UNBOUND_CANONICAL_ENTRY_PRECEDENCE"
    )


def test_downstream_approval_audit_continues_from_durable_work() -> None:
    plan = _plan()
    response = route_platform_query(
        query=DOWNSTREAM_AUDIT_REQUEST,
        development_plan_artifact=plan,
        created_at=CREATED_AT,
    )

    durable = response["service_response"]
    precedence = response["lifecycle_precedence"]
    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
    assert precedence["lifecycle_stage"] == "DURABLE_GOVERNED_WORK"
    assert precedence["upstream_plan_hash"] == plan["artifact_hash"]
    assert precedence["precedence_reason"] == (
        "VALIDATED_UPSTREAM_PLAN_DOWNSTREAM_TARGET"
    )
    assert precedence["suppressed_entry_routes"] == [
        DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    ]
    assert precedence["clause_role_interpretation_reused"] is True
    assert durable["source_development_plan_hash"] == plan["artifact_hash"]
    assert durable["provider_invoked"] is False
    assert durable["worker_invoked"] is False
    assert durable["repository_mutated"] is False
    assert validate_platform_query_router_response(response) == response


def test_historical_plan_reference_does_not_force_reentry_with_valid_state() -> None:
    response = route_platform_query(
        query=DOWNSTREAM_AUDIT_REQUEST,
        development_plan_artifact=_plan(),
        created_at=CREATED_AT,
    )

    assert response["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
    assert response["suppressed_downstream_lifecycle_routes"] == []
