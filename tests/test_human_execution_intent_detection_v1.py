"""Tests for deterministic human execution intent coverage."""

from __future__ import annotations

from aigol.runtime.human_execution_intent_detection import (
    GENERIC_GOVERNED_ARTIFACT_CREATION,
    NO_EXECUTION_INTENT,
    detect_human_execution_intent,
)


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
