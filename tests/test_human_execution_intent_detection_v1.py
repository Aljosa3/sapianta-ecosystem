"""Tests for deterministic human execution intent coverage."""

from __future__ import annotations

from aigol.runtime.canonical_semantic_artifact_runtime import create_canonical_semantic_artifact_from_translation
from aigol.runtime.human_execution_intent_detection import (
    GENERIC_GOVERNED_ARTIFACT_CREATION,
    GENERIC_GOVERNED_EXECUTION_REQUEST,
    NO_EXECUTION_INTENT,
    detect_human_execution_intent,
)
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance


CREATED_AT = "2026-06-28T00:00:00Z"


def test_governance_artifact_creation_is_detected_without_granting_authority() -> None:
    result = detect_human_execution_intent(
        "Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested."
    )

    assert result["intent_detected"] is True
    assert result["intent_class"] == GENERIC_GOVERNED_ARTIFACT_CREATION
    assert result["target_kind"] == "ARTIFACT"
    assert result["execution_authority_granted"] is False
    assert result["routing_action"] == "ROUTE_TO_GOVERNED_DEVELOPMENT_WORKFLOW"


def test_generic_unclear_change_does_not_create_execution_intent() -> None:
    result = detect_human_execution_intent("Make the platform better.")

    assert result["intent_detected"] is False
    assert result["intent_class"] == NO_EXECUTION_INTENT
    assert result["execution_authority_granted"] is False


def test_governance_artifact_creation_uses_csa_primary_when_parity_proven(tmp_path) -> None:
    prompt = (
        "Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge "
        "was successfully tested."
    )
    csa = _canonical_semantic_capture(tmp_path, prompt)

    result = detect_human_execution_intent(
        prompt,
        canonical_semantic_capture=csa,
        replay_reference=str(tmp_path / "execution_intent"),
        detection_id="EXECUTION-INTENT-G2-05-001",
        created_at=CREATED_AT,
    )

    assert result["intent_class"] == GENERIC_GOVERNED_ARTIFACT_CREATION
    assert result["semantic_execution_intent_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert result["migration_batch_id"] == (
        "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1"
    )
    assert result["canonical_semantic_artifact_hash"].startswith("sha256:")
    assert result["previous_compatibility_interpretation"]["intent_class"] == (
        GENERIC_GOVERNED_ARTIFACT_CREATION
    )
    assert result["semantic_comparison_hash"].startswith("sha256:")
    assert result["semantic_comparison_artifact"]["artifact_hash"] == result["semantic_comparison_hash"]
    assert result["semantic_comparison_parity_status"] == "CSA_COMPATIBILITY_EQUIVALENT"
    assert result["semantic_parity_evidence"]["parity_status"] == "CSA_COMPATIBILITY_PARITY_PROVEN"
    assert result["semantic_parity_evidence"]["execution_authority_granted"] is False
    assert result["compatibility_fallback_available"] is True
    assert result["compatibility_fallback_authoritative"] is False
    assert result["execution_authority_granted"] is False


def test_no_execution_intent_uses_csa_primary_when_parity_proven(tmp_path) -> None:
    prompt = "Make the platform better."
    csa = _canonical_semantic_capture(tmp_path, prompt)

    result = detect_human_execution_intent(
        prompt,
        canonical_semantic_capture=csa,
        replay_reference=str(tmp_path / "execution_intent"),
        detection_id="EXECUTION-INTENT-G2-05-002",
        created_at=CREATED_AT,
    )

    assert result["intent_detected"] is False
    assert result["intent_class"] == NO_EXECUTION_INTENT
    assert result["semantic_execution_intent_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert result["semantic_comparison_parity_status"] == "CSA_COMPATIBILITY_EQUIVALENT"
    assert result["semantic_parity_evidence"]["parity_status"] == "CSA_COMPATIBILITY_PARITY_PROVEN"
    assert result["execution_authority_granted"] is False


def test_generic_execution_request_keeps_compatibility_fallback_when_csa_diverges(tmp_path) -> None:
    prompt = "Run the governed execution workflow."
    csa = _canonical_semantic_capture(tmp_path, prompt)

    result = detect_human_execution_intent(
        prompt,
        canonical_semantic_capture=csa,
        replay_reference=str(tmp_path / "execution_intent"),
        detection_id="EXECUTION-INTENT-G2-05-003",
        created_at=CREATED_AT,
    )

    assert result["intent_class"] == GENERIC_GOVERNED_EXECUTION_REQUEST
    assert result["semantic_execution_intent_source"] == "COMPATIBILITY_FALLBACK"
    assert result["semantic_comparison_parity_status"] == "CSA_COMPATIBILITY_DIVERGENT"
    assert result["semantic_parity_evidence"]["compatibility_fallback_authoritative"] is True
    assert result["routing_action"] == "FAIL_CLOSED_NO_CERTIFIED_GENERIC_EXECUTION_ENTRYPOINT"
    assert result["execution_authority_granted"] is False


def _canonical_semantic_capture(tmp_path, prompt: str) -> dict:
    translation = translate_human_to_governance(
        translation_request_id="HTG-EXECUTION-INTENT-G2-05",
        human_request=prompt,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )
    return create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id="CSA-EXECUTION-INTENT-G2-05",
        translation_artifact=translation["translation_artifact"],
        conversation_id="CONVERSATION-EXECUTION-INTENT-G2-05",
        workflow_id=None,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "canonical_semantic_artifact",
    )
