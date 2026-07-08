"""Regression coverage for G16-01 PCCL foundation."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    CERTIFIED,
    IMPLEMENTATION,
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_cognition_layer import (
    CognitiveLoopController,
    ContextAssembler,
    PCCL_FOUNDATION_STATUS,
    PCCL_SERVICE_NAME,
    PCCL_SERVICE_VERSION,
    PlatformCoreCognitionLayer,
    PolicyEnvelope,
    ProposalPipeline,
    ProviderRuntime,
    platform_core_cognition_layer_contract_descriptors,
    platform_core_cognition_layer_manifest,
)


def test_pccl_manifest_registers_platform_core_service_without_behavior() -> None:
    manifest = platform_core_cognition_layer_manifest()

    assert manifest["service_name"] == PCCL_SERVICE_NAME
    assert manifest["service_version"] == PCCL_SERVICE_VERSION
    assert manifest["foundation_status"] == PCCL_FOUNDATION_STATUS
    assert manifest["platform_core_service"] is True
    assert manifest["architectural_owner"] == "PLATFORM_CORE"
    assert "cognition orchestration" in manifest["responsibilities"]
    assert "semantic interpretation" in manifest["non_responsibilities"]
    assert "Human Intent Resolution" in manifest["integration_points"]
    assert manifest["deterministic_lifecycle"] == [
        "Human Goal",
        "Platform Core",
        "PlatformCoreCognitionLayer",
        "existing Platform Core services",
        "Runtime",
        "Replay",
        "Certification",
    ]
    assert manifest["cognition_loop_implemented"] is False
    assert manifest["provider_invocation_implemented"] is False
    assert manifest["context_assembly_implemented"] is False
    assert manifest["policy_evaluation_implemented"] is False
    assert manifest["proposal_generation_implemented"] is False
    assert manifest["authority_flags"]["governance_authority"] is False
    assert manifest["authority_flags"]["replay_authority"] is False
    assert manifest["authority_flags"]["worker_execution_authority"] is False
    assert manifest["artifact_hash"].startswith("sha256:")


def test_pccl_declares_session_lifecycle_without_starting_cognition() -> None:
    service = PlatformCoreCognitionLayer()
    session = service.declare_session(
        session_id="PCCL-SESSION-001",
        human_goal_reference="HUMAN-GOAL-001",
        created_at="2026-07-08T00:00:00Z",
    )

    assert session["artifact_type"] == "PCCL_SESSION_V1"
    assert session["lifecycle_status"] == "PCCL_SESSION_DECLARED"
    assert session["cognition_loop_started"] is False
    assert session["context_assembled"] is False
    assert session["policy_evaluated"] is False
    assert session["provider_invoked"] is False
    assert session["proposal_generated"] is False
    assert session["worker_invoked"] is False
    assert session["replay_certified"] is False
    assert session["authority_flags"]["provider_execution_authority"] is False


def test_pccl_future_contracts_are_descriptors_only() -> None:
    descriptors = platform_core_cognition_layer_contract_descriptors()
    names = {descriptor["contract_name"] for descriptor in descriptors}

    assert names == {
        "PCCLSession",
        "ContextAssembler",
        "PolicyEnvelope",
        "ProviderRuntime",
        "ProposalPipeline",
        "CognitiveLoopController",
    }
    for descriptor in descriptors:
        assert descriptor["contract_status"] == "PCCL_RESERVED_FOR_FUTURE_MILESTONE"
        assert descriptor["behavior_implemented"] is False
        assert descriptor["authority_flags"]["semantic_interpretation_authority"] is False


def test_pccl_future_contract_methods_fail_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="reserved for a future governed milestone"):
        ContextAssembler().assemble_context()
    with pytest.raises(FailClosedRuntimeError, match="reserved for a future governed milestone"):
        PolicyEnvelope().evaluate_policy()
    with pytest.raises(FailClosedRuntimeError, match="reserved for a future governed milestone"):
        ProviderRuntime().invoke_provider()
    with pytest.raises(FailClosedRuntimeError, match="reserved for a future governed milestone"):
        ProposalPipeline().create_proposal()
    with pytest.raises(FailClosedRuntimeError, match="reserved for a future governed milestone"):
        CognitiveLoopController().run_loop()


def test_pccl_foundation_is_registered_as_metadata_only_platform_capability() -> None:
    record = lookup_platform_capability_certification("PLATFORM_CORE_COGNITION_LAYER_FOUNDATION")

    assert is_platform_capability_certified("PLATFORM_CORE_COGNITION_LAYER_FOUNDATION") is True
    assert record["certification_status"] == CERTIFIED
    assert record["certification_scope"] == IMPLEMENTATION
    assert record["certification_milestone"] == "G16-01"
    assert record["implementation_owner"] == "aigol.runtime.platform_core_cognition_layer"
    assert record["runtime_execution_authority"] is False
    assert record["human_interface_authority"] is False
    assert record["provider_invoked"] is False
    assert record["worker_invoked"] is False
    assert record["replay_modified"] is False
