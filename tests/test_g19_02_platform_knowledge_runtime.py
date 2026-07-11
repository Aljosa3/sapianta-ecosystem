"""Regression coverage for G19-02 Platform Knowledge Runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_knowledge_runtime import (
    PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
    query_platform_knowledge,
    validate_platform_knowledge_response,
)


def _workspace_state() -> dict:
    return {
        "active_development_objective": "Improve governed development experience.",
        "project_knowledge_index": {
            "known_goal_targets": ["development_experience", "replay"],
            "certified_artifacts_by_target": {
                "development_experience": [
                    "docs/governance/G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1.md"
                ],
                "replay": ["governance/UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1.md"],
            },
            "related_milestones_by_target": {
                "development_experience": ["G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1"]
            },
            "implementation_history_by_target": {
                "development_experience": ["Improve governed development experience."]
            },
        },
    }


def test_explicit_certification_lookup_composes_registry_and_knowledge_reuse() -> None:
    response = query_platform_knowledge(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
        workspace_state=_workspace_state(),
    )

    assert response["platform_knowledge_runtime_version"] == PLATFORM_KNOWLEDGE_RUNTIME_VERSION
    assert response["query_classification"] == "CERTIFIED_CAPABILITY_WITH_PROJECT_REUSE_CONTEXT"
    assert response["canonical_capability_identifier"] == "REPLAY_CERTIFICATION_RUNTIME"
    assert response["certified_capability_exists"] is True
    assert response["capability_exists"] is True
    assert response["capability_owner"] == "PLATFORM_CORE_REPLAY"
    assert response["implementation_owner"] == "aigol.runtime.replay_certification_runtime"
    assert response["certification_status"] == "CERTIFIED"
    assert response["certification_scope"] == "RUNTIME"
    assert response["is_certified"] is True
    assert response["goal_target"] == "replay"
    assert response["knowledge_reuse_classification"] in {
        "ALREADY_SATISFIED",
        "RELATES_TO_CERTIFIED_CAPABILITY",
        "MODIFIES_EXISTING_CAPABILITY",
        "EXTENDS_EXISTING_MILESTONE",
    }
    assert response["reuse_recommended"] is True
    assert response["recommended_platform_service"] == "aigol.runtime.replay_certification_runtime"
    assert response["source_evidence"][0]["source_type"] == "CERTIFICATION_REGISTRY"
    assert validate_platform_knowledge_response(response) == response


def test_natural_language_query_reuses_project_services_without_new_registry() -> None:
    response = query_platform_knowledge(
        query="I have an idea to improve governance documentation.",
        workspace_state=_workspace_state(),
    )

    assert response["query_classification"] == "PROJECT_CAPABILITY_KNOWLEDGE"
    assert response["canonical_capability_identifier"] is None
    assert response["goal_target"] == "governance_documentation"
    assert response["project_capability_detected"] is True
    assert response["capability_exists"] is True
    assert response["certified_capability_exists"] is False
    assert response["knowledge_reuse_classification"] == "RELATES_TO_CERTIFIED_CAPABILITY"
    assert response["reuse_recommended"] is True
    assert response["recommended_platform_service"] == "aigol.runtime.platform_core_project_services"
    assert "NO_CERTIFICATION_REGISTRY_MATCH" in response["unknown_or_missing_evidence"]
    assert response["source_evidence"][0]["source_type"] == "CAPABILITY_DISCOVERY"
    assert response["source_evidence"][1]["source_type"] == "KNOWLEDGE_REUSE"
    assert response["new_registry_created"] is False
    assert response["duplicate_architectural_metadata_created"] is False
    assert response["knowledge_reuse_replaced"] is False


def test_root_cause_trace_is_reported_as_capability_without_diagnostics() -> None:
    response = query_platform_knowledge(
        query="Does deterministic root cause trace binding already exist?",
    )

    assert response["canonical_capability_identifier"] == "DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING"
    assert response["certified_capability_exists"] is True
    assert response["implementation_owner"] == "aigol.runtime.platform_core_root_cause_trace"
    assert response["root_cause_trace_boundary_preserved"] is True
    assert response["root_cause_trace_invoked"] is False
    assert response["runtime_diagnostics_performed"] is False


def test_explicit_unknown_capability_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unknown capability"):
        query_platform_knowledge(
            query="Does this platform capability exist?",
            capability_identifier="NOT_A_PLATFORM_CAPABILITY",
        )


def test_response_preserves_read_only_boundaries_and_pccl_reference_owners() -> None:
    response = query_platform_knowledge(
        query="Which Platform Core service owns provider attachment?",
    )

    assert response["read_only"] is True
    assert response["composition_layer_only"] is True
    assert response["certification_owned"] is False
    assert response["capability_discovery_owned"] is False
    assert response["provider_invoked"] is False
    assert response["worker_invoked"] is False
    assert response["replay_modified"] is False
    assert response["governance_modified"] is False
    assert response["human_interface_authority"] is False
    assert response["pccl_reference_owners"]["CAPABILITY_DISCOVERY"] == (
        "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION"
    )
    assert response["pccl_reference_owners"]["KNOWLEDGE_REUSE"] == "PLATFORM_CORE_KNOWLEDGE_REUSE"
    assert response["pccl_reference_owners"]["CERTIFICATION_REGISTRY"] == "PLATFORM_CORE_CERTIFICATION"
    assert response["source_precedence"] == [
        "CERTIFICATION_REGISTRY",
        "PLATFORM_CORE_PROJECT_SERVICES",
        "PROJECT_KNOWLEDGE_REUSE",
        "GOVERNANCE_EVIDENCE",
        "PCCL_REFERENCE_METADATA",
        "REPLAY_WORKSPACE_METADATA",
    ]


def test_response_validation_detects_hash_mutation() -> None:
    response = query_platform_knowledge(
        query="Where is replay certification runtime implemented?",
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
    )
    mutated = dict(response)
    mutated["provider_invoked"] = True

    with pytest.raises(FailClosedRuntimeError, match="boundary flags"):
        validate_platform_knowledge_response(mutated)
