"""Certification tests for AIGOL_EXECUTION_SUMMARY_ARTIFACT_STANDARD_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARD_PATH = ROOT / "governance" / "AIGOL_EXECUTION_SUMMARY_ARTIFACT_STANDARD_V1.md"
CERTIFICATION_PATH = ROOT / "governance" / "AIGOL_EXECUTION_SUMMARY_ARTIFACT_STANDARD_CERTIFICATION.json"
POLICY_CERTIFICATION_PATH = (
    ROOT / "governance" / "AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_CERTIFICATION.json"
)

MANDATORY_FIELDS = {
    "artifact_type",
    "schema_version",
    "summary_id",
    "created_at",
    "created_by",
    "original_request",
    "interpreted_intent",
    "selected_route",
    "planned_actions",
    "expected_outputs",
    "assumptions",
    "constraints",
    "risk_classification",
    "authorization_required",
    "human_review_required",
    "human_response_options",
    "execution_scope",
    "replay_references",
    "authority_flags",
    "summary_status",
    "artifact_hash",
}

MINIMUM_REQUIRED_CONTENT = {
    "Original Request",
    "Interpreted Intent",
    "Selected Route",
    "Planned Actions",
    "Expected Outputs",
    "Assumptions",
    "Constraints",
    "Risk Classification",
    "Authorization Required",
    "Replay References",
}

HUMAN_OPTIONS = {
    "APPROVE",
    "CLARIFY",
    "MODIFY",
    "EXPAND_SCOPE",
    "REDUCE_SCOPE",
    "REJECT",
    "CONTINUE_CONVERSATION",
}

FINAL_FIELDS = {
    "EXECUTION_SUMMARY_ARTIFACT_DEFINED": "YES",
    "HUMAN_REVIEW_MODEL_DEFINED": "YES",
    "REPLAY_REQUIREMENTS_DEFINED": "YES",
    "FAIL_CLOSED_REQUIREMENTS_DEFINED": "YES",
    "ARTIFACT_STANDARD_CERTIFIED": "YES",
}


def _certification() -> dict:
    return json.loads(CERTIFICATION_PATH.read_text(encoding="utf-8"))


def _policy_certification() -> dict:
    return json.loads(POLICY_CERTIFICATION_PATH.read_text(encoding="utf-8"))


def test_standard_document_defines_execution_summary_artifact() -> None:
    standard = STANDARD_PATH.read_text(encoding="utf-8")

    assert "EXECUTION_SUMMARY_ARTIFACT_V1" in standard
    assert "Artifact Schema" in standard
    assert "Mandatory Fields" in standard
    assert "Optional Fields" in standard
    assert "Human Interaction Model" in standard
    assert "Replay Requirements" in standard
    assert "Fail-Closed Requirements" in standard
    assert "PENDING_HUMAN_CONFIRMATION" in standard
    for field, value in FINAL_FIELDS.items():
        assert f"{field} = {value}" in standard


def test_certification_pins_schema_and_mandatory_content() -> None:
    certification = _certification()
    schema = certification["artifact_schema"]

    assert certification["certification_status"] == "CERTIFIED"
    assert certification["standardized_artifact_type"] == "EXECUTION_SUMMARY_ARTIFACT_V1"
    assert certification["policy_dependency"] == "AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_V1"
    assert schema["artifact_type"] == "EXECUTION_SUMMARY_ARTIFACT_V1"
    assert schema["schema_version"] == "1.0"
    assert schema["valid_initial_status"] == "PENDING_HUMAN_CONFIRMATION"
    assert set(schema["mandatory_fields"]) == MANDATORY_FIELDS
    assert set(schema["minimum_required_content"]) == MINIMUM_REQUIRED_CONTENT
    assert "known_gaps" in schema["optional_fields"]
    assert "operator_notes" in schema["optional_fields"]


def test_human_review_model_matches_policy_and_remains_non_binary() -> None:
    certification = _certification()
    policy = _policy_certification()
    human_model = certification["human_interaction_model"]

    assert human_model["must_be_presented_to_human"] is True
    assert human_model["human_review_required"] is True
    assert human_model["authorization_required"] is True
    assert set(human_model["response_options"]) == HUMAN_OPTIONS
    assert set(policy["human_response_options"]) == {
        "APPROVE",
        "MODIFY",
        "CLARIFY",
        "EXPAND",
        "REDUCE_SCOPE",
        "REJECT",
        "CONTINUE_CONVERSATION",
    }
    assert human_model["response_effects"]["APPROVE"].startswith("CREATE_EXECUTION_AUTHORIZATION_ARTIFACT_V1")
    assert human_model["response_effects"]["CONTINUE_CONVERSATION"].endswith(
        "WITHOUT_EXECUTION_AUTHORIZATION"
    )


def test_authority_flags_do_not_grant_execution_authority() -> None:
    certification = _certification()

    assert all(value is False for value in certification["authority_flags"].values())
    assert "EXECUTION_AUTHORIZED" in certification["invalid_summary_states"]
    assert "HUMAN_CONFIRMED" in certification["invalid_summary_states"]


def test_replay_and_fail_closed_requirements_are_complete() -> None:
    certification = _certification()

    assert all(certification["replay_requirements"].values())
    assert all(certification["fail_closed_requirements"].values())
    assert certification["fail_closed_requirements"]["authorization_required_false_fails_closed"] is True
    assert certification["fail_closed_requirements"]["human_review_required_false_fails_closed"] is True
    assert certification["fail_closed_requirements"]["authority_granting_flag_fails_closed"] is True
    assert certification["final_fields"] == FINAL_FIELDS
