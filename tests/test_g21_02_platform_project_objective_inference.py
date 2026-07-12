from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    resolve_development_intent,
)
from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_READY,
    present_platform_response,
    validate_platform_presentation,
)
from aigol.runtime.platform_project_objective_inference import (
    OBJECTIVE_AMBIGUOUS,
    OBJECTIVE_SUFFICIENT,
    infer_platform_project_objective,
    validate_platform_project_objective,
)
from aigol.runtime.platform_query_router import (
    PROJECT_OBJECTIVE_INFERENCE_ROUTE,
    ROUTE_READY,
    route_platform_query,
    validate_platform_query_router_response,
)


OBSERVED_REQUEST = (
    "Audit the current Platform Core capabilities for implementing deterministic "
    "dependency impact analysis. Do not implement anything. Determine what already "
    "exists, what can be reused, what certified compositions already exist, what is "
    "missing and prepare a governed development plan."
)


def test_complete_request_composes_sufficient_read_only_objective() -> None:
    intent = resolve_development_intent(message=OBSERVED_REQUEST)

    first = infer_platform_project_objective(
        request=OBSERVED_REQUEST,
        development_intent=intent,
    )
    second = infer_platform_project_objective(
        request=OBSERVED_REQUEST,
        development_intent=intent,
    )

    assert first == second
    assert first["objective_status"] == OBJECTIVE_SUFFICIENT
    assert first["objective_sufficient"] is True
    assert first["requested_work_type"] == "AUDIT_ONLY"
    assert first["mutation_allowed"] is False
    assert first["runtime_implementation"] is False
    assert first["objective_subject"] == "deterministic dependency impact analysis"
    assert "architecture_subject" in first["satisfied_semantic_slots"]
    assert "architecture_outcome" in first["satisfied_semantic_slots"]
    assert first["provider_invoked"] is False
    assert first["worker_invoked"] is False
    assert first["repository_mutated"] is False
    assert validate_platform_project_objective(first) == first


def test_observed_request_continues_without_objective_clarification(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test-uhi",
        session_id="G21-02-OBSERVED",
        message=OBSERVED_REQUEST,
        runtime_root=tmp_path,
        workspace=".",
        created_at="2026-07-11T00:00:00Z",
    )

    intent = context["development_intent_resolution"]
    result = context["governed_read_only_work_result"]
    assert context["project_objective_inference"]["objective_sufficient"] is True
    assert intent["clarification_required"] is False
    assert intent["remaining_missing_semantic_slots"] == []
    assert intent["work_type"] == "AUDIT_ONLY"
    assert context["human_conversation_experience"]["response_mode"] == "READ_ONLY_RESULT"
    assert result["binding_status"] == "GOVERNED_READ_ONLY_WORK_BOUND"
    assert result["selected_read_only_service"] == "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME"
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_material_candidate_ambiguity_fails_objective_sufficiency() -> None:
    intent = resolve_development_intent(message=OBSERVED_REQUEST)
    intent = deepcopy(intent)
    intent["candidate_capability_discovery"][
        "ambiguity_remaining_after_deterministic_analysis"
    ] = True

    artifact = infer_platform_project_objective(
        request=OBSERVED_REQUEST,
        development_intent=intent,
    )

    assert artifact["objective_status"] == OBJECTIVE_AMBIGUOUS
    assert artifact["objective_sufficient"] is False
    assert artifact["clarification_required"] is True
    assert artifact["satisfied_semantic_slots"] == []


def test_objective_artifact_hash_validation_fails_closed() -> None:
    artifact = infer_platform_project_objective(
        request=OBSERVED_REQUEST,
        development_intent=resolve_development_intent(message=OBSERVED_REQUEST),
    )
    artifact["canonical_project_objective"] = "mutated"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_project_objective(artifact)


def test_query_router_and_presentation_expose_objective_composition() -> None:
    response = route_platform_query(
        query=(
            "Infer project objective and objective sufficiency for auditing replay "
            "coverage. Do not implement anything."
        )
    )

    assert response["route_status"] == ROUTE_READY
    assert response["selected_service"] == PROJECT_OBJECTIVE_INFERENCE_ROUTE
    assert response["service_response"]["artifact_type"] == (
        "PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1"
    )
    validate_platform_query_router_response(response)
    presentation = present_platform_response(response)
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["selected_service"] == PROJECT_OBJECTIVE_INFERENCE_ROUTE
    validate_platform_presentation(presentation)

