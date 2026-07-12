"""G22-09 regressions for the direct Durable Governed Work lifecycle binding."""

from __future__ import annotations

from copy import deepcopy
from unittest.mock import patch

from aigol.runtime.platform_capability_composition_coverage import (
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    compose_platform_development_plan,
)
from aigol.runtime.platform_project_objective_inference import (
    infer_platform_project_objective,
)
from aigol.runtime.platform_query_router import (
    DURABLE_GOVERNED_WORK_ROUTE,
    REQUIRED_EVIDENCE_MISSING,
    ROUTE_READY,
    route_platform_query,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-12T00:00:00Z"
QUERY = "Create a durable governed work artifact from the validated development plan."


def _plan() -> dict:
    coverage = discover_platform_capability_composition_coverage(
        query="Assess platform knowledge and query routing.",
        created_at=CREATED_AT,
    )
    return compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=CREATED_AT,
    )


def _objective() -> dict:
    return infer_platform_project_objective(
        request="Audit platform knowledge. Do not implement anything.",
        development_intent={
            "requested_work_type": "AUDIT_ONLY",
            "work_type": "AUDIT_ONLY",
            "candidate_capability_discovery": {},
        },
        created_at=CREATED_AT,
    )


def test_direct_durable_route_consumes_existing_plan_without_regeneration() -> None:
    plan = _plan()
    objective = _objective()

    with patch(
        "aigol.runtime.platform_query_router.compose_platform_development_plan_for_query",
        side_effect=AssertionError("direct durable route must not regenerate a plan"),
    ):
        response = route_platform_query(
            query=QUERY,
            development_plan_artifact=plan,
            project_objective_artifact=objective,
            created_at=CREATED_AT,
        )

    durable = response["service_response"]
    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
    assert durable["work_status"] == "DURABLE_GOVERNED_WORK_NO_IMPLEMENTATION_REQUIRED"
    assert durable["source_development_plan_hash"] == plan["artifact_hash"]
    assert durable["source_project_objective_hash"] == objective["artifact_hash"]
    assert durable["provider_invoked"] is False
    assert durable["worker_invoked"] is False
    assert durable["repository_mutated"] is False


def test_direct_durable_route_fails_closed_without_upstream_plan() -> None:
    response = route_platform_query(query=QUERY, created_at=CREATED_AT)

    assert response["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
    assert response["route_status"] == REQUIRED_EVIDENCE_MISSING
    assert response["required_evidence_missing"] == ["development_plan_artifact"]
    assert response["service_invoked"] is False


def test_direct_durable_route_preserves_invalid_plan_fail_closed_behavior() -> None:
    failed_plan = deepcopy(_plan())
    failed_plan["plan_status"] = DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED
    failed_plan["failure_reason"] = "upstream plan failed closed"
    failed_plan.pop("artifact_hash")
    failed_plan["artifact_hash"] = replay_hash(failed_plan)

    response = route_platform_query(
        query=QUERY,
        development_plan_artifact=failed_plan,
        created_at=CREATED_AT,
    )

    durable = response["service_response"]
    assert response["route_status"] == ROUTE_READY
    assert durable["work_status"] == "DURABLE_GOVERNED_WORK_FAILED_CLOSED"
    assert durable["failure_reason"] == "durable governed work failed closed: source plan failed"
    assert durable["provider_invoked"] is False
    assert durable["worker_invoked"] is False
    assert durable["repository_mutated"] is False
