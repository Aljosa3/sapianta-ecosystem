"""Regression coverage for G20-03 capability composition coverage."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_COMPLETE,
    COVERAGE_FAILED_CLOSED,
    DISCOVERY_AMBIGUOUS_FAILED_CLOSED,
    NO_GAP_EXISTING_CAPABILITY_SUFFICIENT,
    NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1,
    discover_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage,
)
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
)
from aigol.runtime.platform_core_project_services import (
    GOVERNED_READ_ONLY_WORK_BOUND,
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_presentation_layer import PRESENTATION_READY, present_platform_response
from aigol.runtime.platform_query_router import (
    CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
    ROUTE_READY,
    route_platform_query,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-11T00:00:00Z"


def test_certified_generation_composition_covers_multiple_requested_facets() -> None:
    artifact = discover_platform_capability_composition_coverage(
        query=(
            "Assess platform knowledge, query routing, canonical presentation, "
            "and generation certification using the generation evidence profile."
        ),
        created_at=CREATED_AT,
    )

    assert artifact["artifact_type"] == PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1
    assert artifact["coverage_status"] == COVERAGE_COMPLETE
    assert artifact["request_facet_count"] >= 4
    assert artifact["covered_facet_count"] == artifact["request_facet_count"]
    assert artifact["uncovered_residual_gaps"] == []
    assert artifact["minimal_required_platform_extension"]["classification"] == (
        NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT
    )
    assert any(
        item["composition_identifier"] == "GENERATION_CERTIFICATION_COMPOSITION_SERVICE"
        and item["covers_all_discovered_capabilities"] is True
        for item in artifact["certified_reusable_compositions"]
    )
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutated"] is False
    assert artifact["replay_modified"] is False
    assert validate_platform_capability_composition_coverage(artifact) == artifact


def test_single_certified_capability_requires_no_extension() -> None:
    artifact = discover_platform_capability_composition_coverage(
        query="Observe replay through the replay observation layer.",
        created_at=CREATED_AT,
    )

    assert artifact["coverage_status"] == COVERAGE_COMPLETE
    assert artifact["minimal_required_platform_extension"]["classification"] == (
        NO_GAP_EXISTING_CAPABILITY_SUFFICIENT
    )
    assert artifact["minimal_required_platform_extension"]["required"] is False


def test_unknown_request_fails_closed_without_inventing_capability() -> None:
    artifact = discover_platform_capability_composition_coverage(
        query="Evaluate flibbertigibbet topology.",
        created_at=CREATED_AT,
    )

    assert artifact["coverage_status"] == COVERAGE_FAILED_CLOSED
    assert artifact["discovered_reusable_capabilities"] == []
    assert artifact["minimal_required_platform_extension"]["classification"] == (
        DISCOVERY_AMBIGUOUS_FAILED_CLOSED
    )


def test_invalid_replay_evidence_fails_closed() -> None:
    evidence = {
        "artifact_type": "REPLAY_OBSERVATION_LAYER_ARTIFACT_V1",
        "replay_lineage_preserved": True,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    evidence["artifact_hash"] = "sha256:" + "0" * 64

    artifact = discover_platform_capability_composition_coverage(
        query="Discover capability composition coverage for replay observation.",
        replay_evidence=[evidence],
        created_at=CREATED_AT,
    )

    assert artifact["coverage_status"] == COVERAGE_FAILED_CLOSED
    assert artifact["replay_evidence"][0]["hash_valid"] is False
    assert any(
        item["gap_classification"] == "INVALID_REPLAY_EVIDENCE"
        for item in artifact["uncovered_residual_gaps"]
    )


def test_router_and_presentation_expose_coverage_service() -> None:
    router = route_platform_query(
        query=(
            "Perform capability composition discovery and composition coverage for "
            "platform knowledge and query routing; identify the residual gap."
        ),
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(router, created_at=CREATED_AT)

    assert router["route_status"] == ROUTE_READY
    assert router["selected_service"] == CAPABILITY_COMPOSITION_COVERAGE_ROUTE
    assert router["selected_query_class"] == "CAPABILITY_COMPOSITION_DISCOVERY"
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["service"] == CAPABILITY_COMPOSITION_COVERAGE_ROUTE
    assert presentation["answer"]["uncovered_residual_gaps"] == []


def test_governed_read_only_binding_reaches_coverage_service(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G20-03-READ-ONLY",
        message=(
            "work_type: AUDIT_ONLY\nPerform capability composition discovery and "
            "composition coverage for platform knowledge and query routing."
        ),
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]

    assert result["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
    assert result["selected_read_only_service"] == CAPABILITY_COMPOSITION_COVERAGE_ROUTE
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_coverage_hash_mutation_is_detected() -> None:
    artifact = discover_platform_capability_composition_coverage(
        query="Discover composition coverage for platform knowledge.",
        created_at=CREATED_AT,
    )
    mutated = deepcopy(artifact)
    mutated["coverage_status"] = COVERAGE_FAILED_CLOSED

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_capability_composition_coverage(mutated)


def test_coverage_runtime_is_registered_as_certified_capability() -> None:
    assert is_platform_capability_certified(
        "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME"
    ) is True
