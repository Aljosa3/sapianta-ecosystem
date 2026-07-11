"""Regression coverage for G20-01 Generation Certification composition."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.generation_certification_composition import (
    GENERATION_CERTIFICATION_FAILED_CLOSED,
    GENERATION_CERTIFICATION_INCOMPLETE,
    GENERATION_CERTIFICATION_READY,
    GENERATION_CERTIFICATION_RESULT_V1,
    GENERATION_CERTIFIED,
    canonical_generation_evidence_profile,
    compose_generation_certification,
    validate_generation_certification_result,
)
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
)
from aigol.runtime.platform_core_project_services import (
    GOVERNED_READ_ONLY_WORK_BOUND,
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_READY,
    present_platform_response,
)
from aigol.runtime.platform_query_router import (
    GENERATION_CERTIFICATION_ROUTE,
    ROUTE_READY,
    route_platform_query,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-11T00:00:00Z"


def _rehash_profile(profile: dict) -> dict:
    value = deepcopy(profile)
    value.pop("profile_hash", None)
    value["profile_hash"] = replay_hash(value)
    return value


def test_canonical_generation_19_profile_composes_ready_result() -> None:
    result = compose_generation_certification(
        generation_identifier="Generation 19",
        created_at=CREATED_AT,
    )

    assert result["artifact_type"] == GENERATION_CERTIFICATION_RESULT_V1
    assert result["certification_status"] == GENERATION_CERTIFICATION_READY
    assert result["generation_certified"] is False
    assert result["durable_certification_recorded"] is False
    assert result["required_evidence_count"] == result["resolved_evidence_count"]
    assert result["completeness_findings"] == []
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert result["replay_modified"] is False
    assert validate_generation_certification_result(result) == result


def test_missing_required_governance_evidence_is_incomplete(tmp_path) -> None:
    result = compose_generation_certification(
        generation_identifier="GENERATION_19",
        governance_root=tmp_path,
        created_at=CREATED_AT,
    )

    assert result["certification_status"] == GENERATION_CERTIFICATION_INCOMPLETE
    assert any(item["code"] == "REQUIRED_EVIDENCE_MISSING" for item in result["completeness_findings"])


def test_declared_governance_hash_disagreement_fails_closed() -> None:
    profile = canonical_generation_evidence_profile()
    profile["required_governance_artifacts"][0]["artifact_hash"] = "sha256:" + "0" * 64
    profile = _rehash_profile(profile)

    result = compose_generation_certification(
        generation_identifier="GENERATION_19",
        generation_evidence_profile=profile,
        created_at=CREATED_AT,
    )

    assert result["certification_status"] == GENERATION_CERTIFICATION_FAILED_CLOSED
    assert any(item["code"] == "EVIDENCE_HASH_MISMATCH" for item in result["completeness_findings"])


def test_profile_hash_mutation_fails_closed() -> None:
    profile = canonical_generation_evidence_profile()
    profile["known_observations"].append("unhashed mutation")

    result = compose_generation_certification(
        generation_identifier="GENERATION_19",
        generation_evidence_profile=profile,
        created_at=CREATED_AT,
    )

    assert result["certification_status"] == GENERATION_CERTIFICATION_FAILED_CLOSED
    assert "profile hash mismatch" in result["failure_reason"]


def test_runtime_replay_observation_and_replay_certification_evidence_are_composed() -> None:
    profile = canonical_generation_evidence_profile()
    runtime_evidence = {
        "artifact_type": "GENERATION_RUNTIME_EVIDENCE_V1",
        "lineage_complete": True,
    }
    runtime_evidence["artifact_hash"] = replay_hash(runtime_evidence)
    observation = {
        "artifact_type": "REPLAY_OBSERVATION_LAYER_ARTIFACT_V1",
        "replay_lineage_preserved": True,
    }
    observation["artifact_hash"] = replay_hash(observation)
    replay_certification = {
        "artifact_type": "REPLAY_CERTIFICATION_ARTIFACT_V1",
        "replay_lineage_preserved": True,
    }
    replay_certification["artifact_hash"] = replay_hash(replay_certification)
    profile["required_runtime_evidence"] = [
        {
            "artifact_type": "GENERATION_RUNTIME_EVIDENCE_V1",
            "artifact_hash": runtime_evidence["artifact_hash"],
            "evidence": runtime_evidence,
        }
    ]
    profile["required_replay_evidence"] = [
        {"artifact_type": observation["artifact_type"], "evidence": observation},
        {"artifact_type": replay_certification["artifact_type"], "evidence": replay_certification},
    ]
    profile = _rehash_profile(profile)

    result = compose_generation_certification(
        generation_identifier="GENERATION_19",
        generation_evidence_profile=profile,
        created_at=CREATED_AT,
    )

    assert result["certification_status"] == GENERATION_CERTIFICATION_READY
    assert result["runtime_evidence"][0]["hash_matches"] is True
    assert result["replay_evidence"][0]["replay_observation"] is True
    assert result["replay_evidence"][1]["replay_certification"] is True


def test_generation_certified_requires_valid_durable_record() -> None:
    profile = canonical_generation_evidence_profile()
    durable = {
        "artifact_type": "DURABLE_GENERATION_CERTIFICATION_EVIDENCE_V1",
        "generation_identifier": "GENERATION_19",
        "certification_status": GENERATION_CERTIFIED,
        "recorded": True,
        "replay_visible": True,
        "replay_reference": ".runtime/certification/generation_19",
    }
    durable["artifact_hash"] = replay_hash(durable)
    profile["durable_certification_evidence"] = durable
    profile = _rehash_profile(profile)

    result = compose_generation_certification(
        generation_identifier="GENERATION_19",
        generation_evidence_profile=profile,
        created_at=CREATED_AT,
    )

    assert result["certification_status"] == GENERATION_CERTIFIED
    assert result["generation_certified"] is True
    assert result["durable_certification_recorded"] is True


def test_router_selects_generation_certification_and_presentation_normalizes() -> None:
    router = route_platform_query(
        query="work_type: CERTIFICATION\nCertify Generation 19 using its generation evidence profile.",
        generation_identifier="GENERATION_19",
        created_at=CREATED_AT,
    )
    presentation = present_platform_response(router, created_at=CREATED_AT)

    assert router["route_status"] == ROUTE_READY
    assert router["selected_service"] == GENERATION_CERTIFICATION_ROUTE
    assert router["selected_query_class"] == "GENERATION_CERTIFICATION"
    assert router["service_response"]["certification_status"] == GENERATION_CERTIFICATION_READY
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["service"] == GENERATION_CERTIFICATION_ROUTE
    assert presentation["certification_status"] == GENERATION_CERTIFICATION_READY
    assert presentation["answer"]["generation_certified"] is False


def test_governed_read_only_binding_reaches_generation_certification_service(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G20-01-READ-ONLY",
        message="work_type: CERTIFICATION\nCertify Generation 19 using the generation evidence profile.",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]

    assert result["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
    assert result["selected_read_only_service"] == GENERATION_CERTIFICATION_ROUTE
    assert result["presentation_answer"]["certification_status"] == GENERATION_CERTIFICATION_READY
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_composition_service_is_registered_as_certified_platform_capability() -> None:
    assert is_platform_capability_certified("GENERATION_CERTIFICATION_COMPOSITION_SERVICE") is True
