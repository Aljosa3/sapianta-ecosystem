"""Regression coverage for G19-04 Unified Platform Query Router."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_component_owner,
    platform_capability_owner,
)
from aigol.runtime.platform_query_router import (
    CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
    GENERATION_CERTIFICATION_ROUTE,
    GOVERNED_DEVELOPMENT_ROUTE,
    PLATFORM_KNOWLEDGE_ROUTE,
    REQUIRED_EVIDENCE_MISSING,
    ROOT_CAUSE_TRACE_ROUTE,
    ROUTE_READY,
    PlatformServiceRouteDescriptor,
    platform_query_route_descriptors,
    route_platform_query,
    validate_platform_query_router_response,
)


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Improve replay-backed platform evidence.",
        "project_knowledge_index": {
            "known_goal_targets": ["replay", "platform_query_routing"],
            "certified_artifacts_by_target": {
                "replay": ["governance/UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1.md"],
                "platform_query_routing": [
                    "docs/governance/G19_03_UNIFIED_PLATFORM_QUERY_ROUTER_AUDIT.md"
                ],
            },
            "related_milestones_by_target": {
                "platform_query_routing": ["G19-03"],
            },
            "implementation_history_by_target": {
                "platform_query_routing": ["Unified Platform Query Router audit."],
            },
        },
    }


def test_architectural_query_routes_to_platform_knowledge_runtime() -> None:
    response = route_platform_query(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
        workspace_state=_workspace_state(),
    )

    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == PLATFORM_KNOWLEDGE_ROUTE
    assert response["service_invoked"] is True
    assert response["service_response"]["artifact_type"] == "PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1"
    assert response["service_response"]["canonical_capability_identifier"] == "REPLAY_CERTIFICATION_RUNTIME"
    assert response["human_interface_selects_service"] is False
    assert response["provider_invoked"] is False
    assert response["worker_invoked"] is False
    assert validate_platform_query_router_response(response) == response


def test_root_cause_query_without_runtime_or_replay_evidence_requires_evidence() -> None:
    response = route_platform_query(
        query="Why is worker_execution_reached false?",
        workspace_state=_workspace_state(),
    )

    assert response["selected_service"] == ROOT_CAUSE_TRACE_ROUTE
    assert response["route_status"] == REQUIRED_EVIDENCE_MISSING
    assert response["required_evidence_missing"] == ["runtime_or_replay_evidence"]
    assert response["service_response"] is None
    assert response["service_invoked"] is False
    assert response["runtime_diagnostics_performed_by_router"] is False
    assert validate_platform_query_router_response(response) == response


def test_root_cause_query_with_runtime_evidence_invokes_trace_adapter_without_router_diagnostics() -> None:
    response = route_platform_query(
        query="Explain why runtime_status was REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND.",
        runtime_result={"runtime_status": "REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND"},
        observed_field="runtime_status",
        observed_value="REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND",
        workspace_state=_workspace_state(),
    )

    assert response["selected_service"] == ROOT_CAUSE_TRACE_ROUTE
    assert response["route_status"] == ROUTE_READY
    assert response["service_invoked"] is True
    assert response["service_response"]["artifact_type"] == "PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1"
    assert response["root_cause_trace_replaced"] is False
    assert response["runtime_diagnostics_performed_by_router"] is False
    assert response["provider_invoked"] is False
    assert response["worker_invoked"] is False


def test_development_query_routes_to_governed_development_handoff_without_execution() -> None:
    response = route_platform_query(
        query="Implement a governed improvement to replay evidence handling.",
        workspace_state=_workspace_state(),
    )

    assert response["selected_service"] == GOVERNED_DEVELOPMENT_ROUTE
    assert response["route_status"] == ROUTE_READY
    assert response["service_response"]["artifact_type"] == (
        "PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1"
    )
    assert response["service_response"]["router_handoff_status"] == (
        "GOVERNED_DEVELOPMENT_HANDOFF_PREPARED"
    )
    assert response["service_response"]["runtime_execution_invoked"] is False
    assert response["governed_development_replaced"] is False
    assert response["provider_invoked"] is False
    assert response["worker_invoked"] is False


def test_route_descriptors_are_reusable_platform_core_metadata() -> None:
    descriptors = platform_query_route_descriptors()
    services = {descriptor["service_identifier"] for descriptor in descriptors}

    assert services == {
        CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
        GENERATION_CERTIFICATION_ROUTE,
        PLATFORM_KNOWLEDGE_ROUTE,
        ROOT_CAUSE_TRACE_ROUTE,
        GOVERNED_DEVELOPMENT_ROUTE,
    }
    for descriptor in descriptors:
        assert descriptor["route_descriptor_authority"] == "PLATFORM_CORE"
        assert descriptor["human_interface_authority"] is False
        assert descriptor["provider_invoked"] is False
        assert descriptor["worker_invoked"] is False
        assert descriptor["route_descriptor_hash"].startswith("sha256:")


def test_future_service_can_register_through_descriptor_and_adapter_map() -> None:
    future_descriptor = PlatformServiceRouteDescriptor(
        service_identifier="IMPROVEMENT_ANALYSIS_RUNTIME",
        service_owner="PLATFORM_CORE_IMPROVEMENT_ANALYSIS",
        implementation_owner="aigol.runtime.future_improvement_analysis_runtime",
        query_classes=("IMPROVEMENT_ANALYSIS",),
        required_inputs=("query",),
        response_artifact_type="FUTURE_IMPROVEMENT_ANALYSIS_ARTIFACT_V1",
        service_version="FUTURE_SERVICE_TEST_V1",
        adapter_name="_route_future_improvement_analysis",
        routing_terms=("assess", "backlog", "telemetry"),
    )

    response = route_platform_query(
        query="Assess backlog telemetry.",
        route_descriptors=(
            *(
                PlatformServiceRouteDescriptor(
                    service_identifier=descriptor["service_identifier"],
                    service_owner=descriptor["service_owner"],
                    implementation_owner=descriptor["implementation_owner"],
                    query_classes=tuple(descriptor["query_classes"]),
                    required_inputs=tuple(descriptor["required_inputs"]),
                    response_artifact_type=descriptor["response_artifact_type"],
                    service_version=descriptor["service_version"],
                    adapter_name=descriptor["adapter_name"],
                    routing_terms=tuple(descriptor["routing_terms"]),
                )
                for descriptor in platform_query_route_descriptors()
            ),
            future_descriptor,
        ),
        route_adapters={
            "IMPROVEMENT_ANALYSIS_RUNTIME": lambda **kwargs: {
                "artifact_type": "FUTURE_IMPROVEMENT_ANALYSIS_ARTIFACT_V1",
                "query": kwargs["query"],
                "provider_invoked": False,
                "worker_invoked": False,
            }
        },
    )

    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == "IMPROVEMENT_ANALYSIS_RUNTIME"
    assert response["service_response"]["artifact_type"] == "FUTURE_IMPROVEMENT_ANALYSIS_ARTIFACT_V1"
    assert response["future_services_registerable"] is True


def test_router_response_validation_detects_hash_mutation() -> None:
    response = route_platform_query(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
    )
    mutated = dict(response)
    mutated["selected_service"] = ROOT_CAUSE_TRACE_ROUTE

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_query_router_response(mutated)


def test_certification_registry_exposes_unified_platform_query_router() -> None:
    assert is_platform_capability_certified("UNIFIED_PLATFORM_QUERY_ROUTER") is True
    assert platform_capability_owner("UNIFIED_PLATFORM_QUERY_ROUTER") == "PLATFORM_CORE_QUERY_ROUTING"
    assert platform_capability_component_owner("UNIFIED_PLATFORM_QUERY_ROUTER") == (
        "aigol.runtime.platform_query_router"
    )
