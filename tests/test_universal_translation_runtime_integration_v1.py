"""Tests for UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1."""

from __future__ import annotations

import pytest

from aigol.runtime.conversational_cli_runtime import (
    GOVERNED_DEVELOPMENT_WORKFLOW,
    reconstruct_conversational_cli_routing_replay,
    route_conversational_cli_intent,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.universal_translation_artifact_schema import GOVERNANCE_TO_HUMAN, HUMAN_TO_GOVERNANCE
from aigol.runtime.universal_translation_runtime_integration import (
    FULLY_INTEGRATED,
    create_operator_explanation_through_universal_translation,
    reconstruct_universal_translation_runtime_integration_replay,
    route_human_request_through_universal_translation,
)


CREATED_AT = "2026-06-25T00:00:00Z"


def _governance_state() -> dict:
    return {
        "workflow": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "workflow_state": "WAITING_FOR_APPROVAL",
        "intent_family": "GOVERNANCE_CREATE_INTENT",
        "decision": "PROPOSAL_CREATED",
        "approval_required": True,
    }


def _replay_evidence() -> dict:
    return {
        "replay_reference": "/tmp/aigol/replay/universal-integration",
        "replay_status": "RECORDED",
    }


def _approval_state() -> dict:
    return {
        "approval_id": "approval-001",
        "approval_status": "PENDING_APPROVAL",
    }


def test_conversational_routing_records_universal_translation_reference(tmp_path) -> None:
    capture = route_conversational_cli_intent(
        routing_id="ROUTE-UNIVERSAL-001",
        prompt_id="PROMPT-001",
        human_prompt="Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
        canonical_chain_id="CHAIN-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )

    decision = capture["routing_decision_artifact"]

    assert capture["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert decision["universal_translation_reference"].endswith("human_to_governance")
    assert decision["universal_translation_hash"].startswith("sha256:")
    assert decision["universal_translation_direction"] == HUMAN_TO_GOVERNANCE
    assert capture["universal_translation_hash"] == decision["universal_translation_hash"]
    assert decision["canonical_semantic_artifact_reference"].endswith("canonical_semantic_artifact")
    assert decision["canonical_semantic_artifact_hash"].startswith("sha256:")
    assert decision["semantic_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert decision["migration_batch_id"] == "UBTR_CONSUMER_MIGRATION_BATCH_01_ACLI_ROUTING_V1"
    assert decision["previous_routing_source"] == "LOCAL_COMPATIBILITY_MARKERS"
    assert decision["previous_compatibility_workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert decision["new_csa_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert decision["ubtr_semantic_cognition_orchestration_reference"].endswith(
        "ubtr_semantic_cognition_orchestration"
    )
    assert decision["ubtr_semantic_cognition_decision"] == "DETERMINISTIC_SEMANTIC_ARTIFACT_VALID"
    assert decision["ubtr_semantic_cognition_reasons"] == []
    assert decision["ubtr_ocs_cognition_request_hash"] is None
    assert decision["ubtr_ocs_cognition_handoff_reference"] is None
    assert decision["ubtr_cognition_result_integration_reference"] is None
    assert capture["canonical_semantic_artifact_hash"] == decision["canonical_semantic_artifact_hash"]
    assert capture["ubtr_semantic_cognition_decision"] == "DETERMINISTIC_SEMANTIC_ARTIFACT_VALID"

    reconstructed = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")
    assert reconstructed["universal_translation_hash"] == decision["universal_translation_hash"]
    assert reconstructed["canonical_semantic_artifact_hash"] == decision["canonical_semantic_artifact_hash"]
    assert reconstructed["semantic_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert reconstructed["migration_batch_id"] == "UBTR_CONSUMER_MIGRATION_BATCH_01_ACLI_ROUTING_V1"
    assert reconstructed["previous_compatibility_workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert reconstructed["new_csa_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert reconstructed["ubtr_semantic_cognition_decision"] == "DETERMINISTIC_SEMANTIC_ARTIFACT_VALID"
    assert reconstructed["ubtr_ocs_cognition_request_hash"] is None


def test_conversational_routing_keeps_compatibility_fallback_when_semantics_are_ambiguous(tmp_path) -> None:
    capture = route_conversational_cli_intent(
        routing_id="ROUTE-UNIVERSAL-AMBIGUOUS-001",
        prompt_id="PROMPT-AMBIGUOUS-001",
        human_prompt="Create a governance artifact for the new runtime",
        canonical_chain_id="CHAIN-AMBIGUOUS-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )

    decision = capture["routing_decision_artifact"]

    assert capture["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert decision["canonical_semantic_artifact_hash"].startswith("sha256:")
    assert decision["semantic_routing_source"] == "COMPATIBILITY_FALLBACK"
    assert decision["ubtr_semantic_cognition_decision"] == "OCS_COGNITION_REQUESTED"
    assert "GOVERNANCE_TARGET_ENTITY_MISSING" in decision["ubtr_semantic_cognition_reasons"]
    assert decision["ubtr_ocs_cognition_request_hash"].startswith("sha256:")
    assert decision["ubtr_ocs_cognition_handoff_reference"].endswith("ubtr_ocs_cognition_handoff")
    assert decision["ubtr_ocs_cognition_handoff_status"] == "UBTR_OCS_COGNITION_HANDOFF_COMPLETED"
    assert decision["ubtr_ocs_context_hash"].startswith("sha256:")
    assert decision["ubtr_ocs_cognition_hash"].startswith("sha256:")
    assert decision["ubtr_ocs_provider_necessity"]["necessity_classification"] == "PROVIDER_REQUIRED"
    assert decision["ubtr_cognition_result_integration_reference"].endswith("ubtr_cognition_result_integration")
    assert decision["ubtr_cognition_result_integration_status"] == "UBTR_COGNITION_RESULT_INTEGRATION_COMPLETED"
    assert decision["ubtr_cognition_integrated_semantic_artifact_hash"].startswith("sha256:")
    assert capture["semantic_routing_source"] == "COMPATIBILITY_FALLBACK"
    assert capture["ubtr_ocs_cognition_handoff_status"] == "UBTR_OCS_COGNITION_HANDOFF_COMPLETED"
    assert capture["ubtr_cognition_result_integration_status"] == "UBTR_COGNITION_RESULT_INTEGRATION_COMPLETED"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_deterministic_development_intent_routes_through_canonical_semantic_artifact(tmp_path) -> None:
    capture = route_conversational_cli_intent(
        routing_id="ROUTE-UNIVERSAL-DEVELOPMENT-001",
        prompt_id="PROMPT-DEVELOPMENT-001",
        human_prompt="Implement worker authorization",
        canonical_chain_id="CHAIN-DEVELOPMENT-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )

    decision = capture["routing_decision_artifact"]

    assert capture["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert decision["semantic_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert decision["migration_batch_id"] == "UBTR_CONSUMER_MIGRATION_BATCH_01_ACLI_ROUTING_V1"
    assert decision["matched_terms"] == [
        "ubtr",
        "canonical-semantic-artifact",
        "governed-development",
        "development",
        "implement",
    ]
    assert decision["previous_routing_source"] == "LOCAL_COMPATIBILITY_MARKERS"
    assert decision["previous_compatibility_workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert decision["previous_compatibility_matched_terms"] == ["authorization", "implement", "worker"]
    assert decision["new_csa_routing_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert decision["ubtr_semantic_cognition_decision"] == "DETERMINISTIC_SEMANTIC_ARTIFACT_VALID"
    assert decision["ubtr_ocs_cognition_request_hash"] is None
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_human_request_integration_wraps_translation_then_hirr_routing(tmp_path) -> None:
    result = route_human_request_through_universal_translation(
        integration_id="INTEGRATION-001",
        prompt_id="PROMPT-002",
        human_prompt="Create governance artifact ACLI_OPERATOR_GUIDE_V1.",
        canonical_chain_id="CHAIN-002",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )

    artifact = result["integration_artifact"]

    assert result["integration_status"] == FULLY_INTEGRATED
    assert result["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert artifact["integration_direction"] == HUMAN_TO_GOVERNANCE
    assert artifact["deprecated_direct_path"] == "Human -> HIRR without Universal Translation evidence"
    assert artifact["compatibility_layer_active"] is True
    assert artifact["authority_granted"] is False

    reconstructed = reconstruct_universal_translation_runtime_integration_replay(
        tmp_path / "integration",
        direction=HUMAN_TO_GOVERNANCE,
    )
    assert reconstructed["universal_translation_hash"] == result["universal_translation_hash"]
    assert reconstructed["authority_granted"] is False


def test_governance_to_operator_explanation_uses_universal_translation(tmp_path) -> None:
    result = create_operator_explanation_through_universal_translation(
        integration_id="INTEGRATION-002",
        translation_request_id="GTH-INTEGRATION-002",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )

    artifact = result["integration_artifact"]

    assert result["integration_status"] == FULLY_INTEGRATED
    assert artifact["integration_direction"] == GOVERNANCE_TO_HUMAN
    assert artifact["universal_translation_hash"].startswith("sha256:")
    assert artifact["llm_assisted_explanation_reference"] is None
    assert "GOVERNANCE STATE EXPLANATION" in result["operator_explanation"]
    assert result["authority_granted"] is False
    assert result["execution_requested"] is False


def test_governance_to_operator_explanation_can_use_optional_advisory_provider(tmp_path) -> None:
    def provider(request: dict) -> dict:
        state = request["authoritative_state"]
        return {
            "explanation_text": "A proposal is waiting for your approval. This is advisory only.",
            "preserved_artifact_identifiers": list(state["artifact_identifiers"]),
            "preserved_target_paths": list(state["target_paths"]),
            "preserved_approval_state": state["approval_state"],
            "preserved_replay_references": list(state["replay_references"]),
            "advisory_only": True,
            "authority_granted": False,
        }

    result = create_operator_explanation_through_universal_translation(
        integration_id="INTEGRATION-003",
        translation_request_id="GTH-INTEGRATION-003",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
        llm_explanation_provider=provider,
        llm_explanation_provider_id="test-provider",
    )

    artifact = result["integration_artifact"]

    assert artifact["llm_assisted_explanation_reference"] is not None
    assert artifact["llm_assisted_explanation_hash"].startswith("sha256:")
    assert "test-provider" in result["operator_explanation"]
    assert "Advisory Only" in result["operator_explanation"]
    assert result["authority_granted"] is False


def test_integration_replay_tampering_fails_closed(tmp_path) -> None:
    route_human_request_through_universal_translation(
        integration_id="INTEGRATION-004",
        prompt_id="PROMPT-004",
        human_prompt="Create governance artifact ACLI_TAMPER_TEST_V1.",
        canonical_chain_id="CHAIN-004",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )
    replay_file = tmp_path / "integration" / "000_universal_human_to_governance_integration_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["authority_granted"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_universal_translation_runtime_integration_replay(
            tmp_path / "integration",
            direction=HUMAN_TO_GOVERNANCE,
        )
