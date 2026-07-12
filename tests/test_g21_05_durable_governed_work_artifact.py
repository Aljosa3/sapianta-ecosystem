from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_development_composition_plan import (
    compose_platform_development_plan,
)
from aigol.runtime.platform_durable_governed_work import (
    DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED,
    DURABLE_WORK_READY_FOR_REVIEW,
    compose_durable_governed_work,
    reconstruct_durable_governed_work,
    validate_durable_governed_work,
)
from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_READY,
    present_platform_response,
)
from aigol.runtime.platform_query_router import (
    DURABLE_GOVERNED_WORK_ROUTE,
    ROUTE_READY,
    route_platform_query,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-12T00:00:00Z"


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _plan(*, implementation_required: bool) -> dict:
    coverage = discover_platform_capability_composition_coverage(
        query="Assess platform knowledge and query routing.",
        created_at=CREATED_AT,
    )
    if implementation_required:
        coverage["uncovered_residual_gaps"] = [
            {
                "facet": "DURABLE_WORK_BINDING",
                "reason": "Plan-to-work lifecycle binding is required.",
                "gap_classification": "UNCOVERED_CAPABILITY_FACET",
            }
        ]
        coverage["uncovered_residual_gap_count"] = 1
        coverage["minimal_required_platform_extension"] = {
            "classification": "MINIMAL_COMPOSITION_SERVICE_REQUIRED",
            "required": True,
            "recommended_components": ["PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME"],
            "rationale": "Bind the existing plan into durable governed work.",
        }
        coverage.pop("artifact_hash")
        coverage["artifact_hash"] = replay_hash(coverage)
    return compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=CREATED_AT,
    )


def test_plan_becomes_stable_approval_ready_durable_work(tmp_path) -> None:
    plan = _plan(implementation_required=True)
    first = compose_durable_governed_work(
        development_plan_artifact=plan,
        source_work_type="AUDIT_ONLY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "durable-work",
    )
    second = compose_durable_governed_work(
        development_plan_artifact=plan,
        source_work_type="AUDIT_ONLY",
        created_at=CREATED_AT,
    )

    assert first["governed_work_id"] == second["governed_work_id"]
    assert first["work_status"] == DURABLE_WORK_READY_FOR_REVIEW
    assert first["source_work_type"] == "AUDIT_ONLY"
    assert first["proposed_next_phase_work_type"] == "IMPLEMENTATION"
    assert first["approval_request_ready"] is True
    assert first["approval_request"]["approval_required"] is True
    assert first["approval_granted"] is False
    assert first["execution_authorized"] is False
    assert first["provider_invoked"] is False
    assert first["worker_invoked"] is False
    assert first["repository_mutated"] is False
    assert validate_durable_governed_work(first) == first
    assert reconstruct_durable_governed_work(tmp_path / "durable-work") == first


def test_no_gap_plan_is_durable_without_inventing_approval() -> None:
    artifact = compose_durable_governed_work(
        development_plan_artifact=_plan(implementation_required=False),
        source_work_type="AUDIT_ONLY",
        created_at=CREATED_AT,
    )

    assert artifact["work_status"] == DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED
    assert artifact["approval_request_ready"] is False
    assert artifact["approval_request"]["approval_required"] is False
    assert artifact["proposed_next_phase_work_type"] == "AUDIT_ONLY"


def test_tampered_durable_work_fails_closed() -> None:
    artifact = compose_durable_governed_work(
        development_plan_artifact=_plan(implementation_required=True),
        created_at=CREATED_AT,
    )
    artifact["review_state"] = "APPROVED"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_durable_governed_work(artifact)


def test_project_services_automatically_persist_plan_handoff(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G21-05-AUTOMATIC",
        message=(
            "work_type: AUDIT_ONLY\nCreate a governed development plan for platform "
            "knowledge and query routing with an ordered implementation sequence."
        ),
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]
    durable = result["durable_governed_work_artifact"]

    assert durable["artifact_type"] == "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
    assert result["durable_governed_work_id"] == durable["governed_work_id"]
    assert result["manual_copy_paste_required"] is False
    assert durable["replay_reference"]
    assert durable["provider_invoked"] is False
    assert durable["worker_invoked"] is False
    assert durable["repository_mutated"] is False


def test_aicli_plan_result_automatically_contains_durable_work(tmp_path) -> None:
    request = (
        "work_type: AUDIT_ONLY\nCreate a governed development plan for platform "
        "knowledge and query routing with an ordered implementation sequence."
    )
    result = aicli.run_reference_uhi_session(
        session_id="G21-05-AICLI",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
        input_reader=_reader([request, "/send", "/exit"]),
        output_writer=lambda _line: None,
    )

    context = result["platform_core_project_services_context"]
    durable = context["durable_governed_work_artifact"]
    assert durable["artifact_type"] == "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
    assert durable["governed_work_id"]
    assert context["governed_read_only_work_result"]["manual_copy_paste_required"] is False
    assert result["runtime_entered"] is False


def test_router_and_presentation_expose_durable_work_service() -> None:
    plan = _plan(implementation_required=False)
    router = route_platform_query(
        query=(
            "Create a durable governed work artifact for platform knowledge and query "
            "routing with approval-ready governed work evidence."
        ),
        development_plan_artifact=plan,
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(router, created_at=CREATED_AT)

    assert router["route_status"] == ROUTE_READY
    assert router["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
    assert router["service_response"]["artifact_type"] == (
        "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
    )
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["selected_service"] == DURABLE_GOVERNED_WORK_ROUTE
