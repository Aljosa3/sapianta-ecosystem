"""Regression coverage for G20-05 Development Composition Plan."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
)
from aigol.runtime.platform_core_project_services import (
    GOVERNED_READ_ONLY_WORK_BOUND,
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED,
    DEVELOPMENT_COMPOSITION_PLAN_READY,
    PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1,
    compose_platform_development_plan,
    validate_platform_development_composition_plan,
)
from aigol.runtime.platform_presentation_layer import PRESENTATION_READY, present_platform_response
from aigol.runtime.platform_query_router import (
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    ROUTE_READY,
    route_platform_query,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-11T00:00:00Z"


def _coverage(query: str = "Assess platform knowledge and query routing.") -> dict:
    return discover_platform_capability_composition_coverage(
        query=query,
        created_at=CREATED_AT,
    )


def _coverage_requiring_implementation() -> dict:
    coverage = _coverage()
    coverage["uncovered_residual_gaps"] = [
        {
            "facet": "DEVELOPMENT_PLAN_BINDING",
            "reason": "Canonical coverage-to-plan composition is not yet bound.",
            "gap_classification": "UNCOVERED_CAPABILITY_FACET",
        }
    ]
    coverage["uncovered_residual_gap_count"] = 1
    coverage["minimal_required_platform_extension"] = {
        "classification": "MINIMAL_COMPOSITION_SERVICE_REQUIRED",
        "required": True,
        "recommended_components": [
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
        ],
        "rationale": "Compose existing certified capabilities through one bounded service.",
    }
    coverage.pop("artifact_hash")
    coverage["artifact_hash"] = replay_hash(coverage)
    return coverage


def test_coverage_with_no_gap_produces_reuse_only_plan() -> None:
    plan = compose_platform_development_plan(
        capability_coverage_artifact=_coverage(),
        created_at=CREATED_AT,
    )

    assert plan["artifact_type"] == PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1
    assert plan["plan_status"] == DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED
    assert plan["implementation_required"] is False
    assert plan["ordered_implementation_sequence"] == [
        "REUSE_CERTIFIED_CAPABILITIES",
        "VERIFY_EXISTING_COMPOSITION",
    ]
    assert plan["requires_future_human_approval"] is False
    assert plan["execution_authorized"] is False
    assert plan["provider_invoked"] is False
    assert plan["worker_invoked"] is False
    assert plan["repository_mutated"] is False
    assert validate_platform_development_composition_plan(plan) == plan


def test_residual_gap_produces_ordered_dependency_complete_plan() -> None:
    plan = compose_platform_development_plan(
        capability_coverage_artifact=_coverage_requiring_implementation(),
        created_at=CREATED_AT,
    )

    assert plan["plan_status"] == DEVELOPMENT_COMPOSITION_PLAN_READY
    assert plan["implementation_required"] is True
    assert plan["ordered_implementation_sequence"] == [
        "REUSE_CERTIFIED_CAPABILITIES",
        "IMPLEMENT_RESIDUAL_CAPABILITY_GAPS",
        "DEFINE_CANONICAL_ARTIFACT_CONTRACT",
        "BIND_PLATFORM_QUERY_ROUTER",
        "BIND_CANONICAL_PRESENTATION",
        "ADD_FAIL_CLOSED_REGRESSIONS",
        "VALIDATE_GOVERNANCE_CONFORMANCE",
        "RECORD_IMPLEMENTATION_CERTIFICATION_METADATA",
    ]
    assert plan["dependency_graph"]["topological_order"] == plan[
        "ordered_implementation_sequence"
    ]
    assert len(plan["dependency_graph"]["edges"]) == 7
    assert any(
        item["dependency_type"] == "FUTURE_IMPLEMENTATION_CERTIFICATION"
        for item in plan["certification_dependencies"]
    )
    assert "FULL_REGRESSION_SUITE" in plan["validation_requirements"]
    assert plan["implementation_boundary"]["allowed_scope"] == (
        "RESIDUAL_GAPS_AND_MINIMAL_BINDINGS_ONLY"
    )
    assert plan["requires_future_human_approval"] is True
    assert plan["requires_separate_execution_authorization"] is True


def test_corrupt_coverage_fails_closed() -> None:
    coverage = _coverage()
    coverage["covered_facet_count"] = 999

    plan = compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=CREATED_AT,
    )

    assert plan["plan_status"] == DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED
    assert "hash mismatch" in plan["failure_reason"]
    assert plan["execution_authorized"] is False


def test_router_and_presentation_expose_development_plan_service() -> None:
    router = route_platform_query(
        query=(
            "Create a governed development plan for platform knowledge and query routing "
            "with an ordered implementation sequence."
        ),
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(router, created_at=CREATED_AT)

    assert router["route_status"] == ROUTE_READY
    assert router["selected_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert router["selected_query_class"] == "DEVELOPMENT_COMPOSITION_PLAN"
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert presentation["answer"]["implementation_required"] is False
    assert presentation["answer"]["ordered_implementation_sequence"]


def test_governed_read_only_binding_reaches_development_plan_service(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G20-05-READ-ONLY",
        message=(
            "work_type: AUDIT_ONLY\nCreate a governed development plan for platform "
            "knowledge and query routing with an ordered implementation sequence."
        ),
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]

    assert result["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
    assert result["selected_read_only_service"] == DEVELOPMENT_COMPOSITION_PLAN_ROUTE
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_plan_hash_mutation_is_detected() -> None:
    plan = compose_platform_development_plan(
        capability_coverage_artifact=_coverage(),
        created_at=CREATED_AT,
    )
    mutated = deepcopy(plan)
    mutated["implementation_required"] = True

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_development_composition_plan(mutated)


def test_development_plan_runtime_is_registered_as_certified_capability() -> None:
    assert is_platform_capability_certified(
        "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME"
    ) is True

