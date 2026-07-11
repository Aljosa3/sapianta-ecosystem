"""Regression coverage for G19-06 Canonical Platform Presentation Layer."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_component_owner,
    platform_capability_owner,
)
from aigol.runtime.platform_core_project_services import resolve_development_intent
from aigol.runtime.platform_core_root_cause_trace import trace_platform_core_root_cause
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.platform_presentation_layer import (
    CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1,
    PRESENTATION_MISSING_EVIDENCE,
    PRESENTATION_READY,
    present_platform_response,
    validate_platform_presentation,
)
from aigol.runtime.platform_query_router import (
    GOVERNED_DEVELOPMENT_ROUTE,
    PLATFORM_KNOWLEDGE_ROUTE,
    ROOT_CAUSE_TRACE_ROUTE,
    route_platform_query,
)


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Improve platform presentation evidence.",
        "project_knowledge_index": {
            "known_goal_targets": ["replay", "platform_presentation"],
            "certified_artifacts_by_target": {
                "replay": ["governance/UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1.md"],
                "platform_presentation": [
                    "docs/governance/G19_05_CANONICAL_PLATFORM_PRESENTATION_LAYER_AUDIT.md"
                ],
            },
            "related_milestones_by_target": {
                "platform_presentation": ["G19-05"],
            },
            "implementation_history_by_target": {
                "platform_presentation": ["Canonical Platform Presentation Layer audit."],
            },
        },
    }


def test_platform_knowledge_response_normalizes_to_canonical_presentation() -> None:
    knowledge = query_platform_knowledge(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
        workspace_state=_workspace_state(),
    )

    presentation = present_platform_response(knowledge)

    assert presentation["artifact_type"] == CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["service"] == PLATFORM_KNOWLEDGE_ROUTE
    assert presentation["answer"]["implementation_owner"] == "aigol.runtime.replay_certification_runtime"
    assert presentation["certification_status"] == "CERTIFIED"
    assert "CAPABILITY_CERTIFICATION_REGISTRY" in presentation["reusable_components"]
    assert presentation["provider_invoked"] is False
    assert presentation["worker_invoked"] is False
    assert validate_platform_presentation(presentation) == presentation


def test_router_response_preserves_selected_service_and_one_presentation_shape() -> None:
    router_response = route_platform_query(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
        workspace_state=_workspace_state(),
    )

    presentation = present_platform_response(router_response)

    assert presentation["service"] == PLATFORM_KNOWLEDGE_ROUTE
    assert presentation["source_artifact_type"] == "PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1"
    assert presentation["router_response_hash"] == router_response["artifact_hash"]
    assert presentation["reasoning_path"][0]["step"] == "PLATFORM_QUERY_ROUTER"
    assert presentation["answer"]["certified_capability_exists"] is True


def test_missing_evidence_router_response_has_canonical_presentation_without_service_response() -> None:
    router_response = route_platform_query(
        query="Why is worker_execution_reached false?",
        workspace_state=_workspace_state(),
    )

    presentation = present_platform_response(router_response)

    assert presentation["service"] == ROOT_CAUSE_TRACE_ROUTE
    assert presentation["presentation_status"] == PRESENTATION_MISSING_EVIDENCE
    assert presentation["answer"]["required_evidence_missing"] == ["runtime_or_replay_evidence"]
    assert presentation["service"] == presentation["selected_service"]
    assert presentation["reusable_components"] == ["UNIFIED_PLATFORM_QUERY_ROUTER"]
    assert validate_platform_presentation(presentation) == presentation


def test_root_cause_trace_response_normalizes_existing_explanation_and_evidence() -> None:
    trace = trace_platform_core_root_cause(
        observed_field="runtime_status",
        observed_value="REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND",
        runtime_result={"runtime_status": "REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND"},
    )

    presentation = present_platform_response(trace)

    assert presentation["service"] == ROOT_CAUSE_TRACE_ROUTE
    assert presentation["source_artifact_type"] == "PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1"
    assert presentation["summary"] == trace["root_cause_explanation"]
    assert presentation["answer"]["observed_result"]["field"] == "runtime_status"
    assert "DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME" in presentation["reusable_components"]
    assert presentation["provider_invoked"] is False
    assert presentation["worker_invoked"] is False


def test_governed_development_response_normalizes_handoff_without_execution() -> None:
    router_response = route_platform_query(
        query="Implement a governed improvement to platform presentation handling.",
        workspace_state=_workspace_state(),
    )
    assert router_response["selected_service"] == GOVERNED_DEVELOPMENT_ROUTE
    development_response = router_response["service_response"]

    presentation = present_platform_response(development_response)

    assert presentation["service"] == GOVERNED_DEVELOPMENT_ROUTE
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["answer"]["runtime_execution_invoked"] is False
    assert presentation["answer"]["requires_human_approval"] is True
    assert presentation["governance_status"] == "PENDING_HUMAN_APPROVAL"
    assert "HUMAN_CONVERSATION_EXPERIENCE" in presentation["reusable_components"]


def test_direct_development_intent_response_is_supported() -> None:
    development = resolve_development_intent(
        message="Implement a governed improvement to platform presentation handling.",
        workspace_state=_workspace_state(),
    )

    presentation = present_platform_response(development)

    assert presentation["service"] == GOVERNED_DEVELOPMENT_ROUTE
    assert presentation["answer"]["summary_admissible"] is True
    assert presentation["recommended_next_step"]


def test_presentation_validation_detects_mutation() -> None:
    knowledge = query_platform_knowledge(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
    )
    presentation = present_platform_response(knowledge)
    mutated = dict(presentation)
    mutated["summary"] = "mutated"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_presentation(mutated)


def test_certification_registry_exposes_presentation_layer() -> None:
    assert is_platform_capability_certified("CANONICAL_PLATFORM_PRESENTATION_LAYER") is True
    assert platform_capability_owner("CANONICAL_PLATFORM_PRESENTATION_LAYER") == (
        "PLATFORM_CORE_PRESENTATION"
    )
    assert platform_capability_component_owner("CANONICAL_PLATFORM_PRESENTATION_LAYER") == (
        "aigol.runtime.platform_presentation_layer"
    )
