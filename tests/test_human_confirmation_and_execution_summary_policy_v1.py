"""Certification tests for AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "governance" / "AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_V1.md"
CERTIFICATION_PATH = (
    ROOT / "governance" / "AIGOL_HUMAN_CONFIRMATION_AND_EXECUTION_SUMMARY_POLICY_CERTIFICATION.json"
)

REQUIRED_SUMMARY_FIELDS = {
    "original_human_request",
    "interpreted_intent",
    "selected_route",
    "planned_actions",
    "expected_outputs",
    "risk_classification",
    "assumptions",
    "constraints",
    "execution_scope",
    "authorization_required",
    "replay_references",
}

REQUIRED_RESPONSE_OPTIONS = {
    "APPROVE",
    "MODIFY",
    "CLARIFY",
    "EXPAND",
    "REDUCE_SCOPE",
    "REJECT",
    "CONTINUE_CONVERSATION",
}

REQUIRED_CASES = {
    "CASE_1_DETERMINISTIC_DEVELOPMENT_INTENT",
    "CASE_2_OCS_COGNITION_INTENT",
    "CASE_3_REPLAY_DERIVED_IMPROVEMENT",
    "CASE_4_HUMAN_MODIFIES_SCOPE",
    "CASE_5_HUMAN_REQUESTS_CLARIFICATION",
    "CASE_6_MISSING_HUMAN_RESPONSE",
}

FINAL_FIELDS = {
    "EXECUTION_SUMMARY_REQUIRED": "YES",
    "HUMAN_CONFIRMATION_REQUIRED": "YES",
    "DETERMINISTIC_AUTO_EXECUTION_PROHIBITED": "YES",
    "LLM_AUTO_EXECUTION_PROHIBITED": "YES",
    "REPLAY_AUDITABILITY_PRESERVED": "YES",
    "FAIL_CLOSED_PRESERVED": "YES",
    "POLICY_CERTIFIED": "YES",
}


def _certification() -> dict:
    return json.loads(CERTIFICATION_PATH.read_text(encoding="utf-8"))


def test_policy_document_declares_required_human_confirmation_boundary() -> None:
    policy = POLICY_PATH.read_text(encoding="utf-8")

    assert "INTENT_RESOLUTION != HUMAN_CONFIRMATION" in policy
    assert "EXECUTION_SUMMARY_ARTIFACT_V1" in policy
    assert "Deterministic Intent\n-> Automatic Execution" in policy
    assert "Intent Resolution\n-> Execution Summary\n-> Human Review\n-> Human Confirmation" in policy
    assert "Deterministic Route\n-> Execute" in policy
    assert "FAIL_CLOSED" in policy
    for field, value in FINAL_FIELDS.items():
        assert f"{field} = {value}" in policy


def test_certification_requires_execution_summary_before_execution_capable_transition() -> None:
    certification = _certification()
    summary = certification["execution_summary_artifact"]
    boundary = certification["boundary_certification"]

    assert certification["certification_status"] == "CERTIFIED"
    assert certification["canonical_invariant"] == "INTENT_RESOLUTION != HUMAN_CONFIRMATION"
    assert certification["prohibited_transition"] == "Deterministic Intent -> Automatic Execution"
    assert summary["artifact_type"] == "EXECUTION_SUMMARY_ARTIFACT_V1"
    assert summary["required_before_execution_capable_transition"] is True
    assert summary["must_be_presented_to_human"] is True
    assert set(summary["minimum_required_fields"]) == REQUIRED_SUMMARY_FIELDS
    assert set(certification["human_response_options"]) == REQUIRED_RESPONSE_OPTIONS
    assert boundary["successful_intent_classification_is_execution_authorization"] is False
    assert boundary["deterministic_routing_can_authorize_execution"] is False
    assert boundary["llm_can_authorize_execution"] is False
    assert boundary["human_confirmation_required_before_authorization"] is True
    assert boundary["execution_authorization_required_before_execution"] is True
    assert boundary["binary_approval_only_workflow_required"] is False


def test_certification_cases_block_execution_until_confirmation() -> None:
    certification = _certification()
    cases = {case["case_id"]: case for case in certification["certification_cases"]}

    assert set(cases) == REQUIRED_CASES
    for case_id in (
        "CASE_1_DETERMINISTIC_DEVELOPMENT_INTENT",
        "CASE_2_OCS_COGNITION_INTENT",
        "CASE_3_REPLAY_DERIVED_IMPROVEMENT",
    ):
        case = cases[case_id]
        assert case["summary_generated"] is True
        assert case["human_approval_required"] is True
        assert case["execution_blocked_until_confirmation"] is True
        assert case["execution_allowed_directly_from_intent"] is False

    assert cases["CASE_4_HUMAN_MODIFIES_SCOPE"]["updated_summary_required"] is True
    assert cases["CASE_4_HUMAN_MODIFIES_SCOPE"]["execution_blocked_until_reconfirmed"] is True
    assert cases["CASE_4_HUMAN_MODIFIES_SCOPE"]["execution_allowed_directly_from_modification"] is False
    assert cases["CASE_5_HUMAN_REQUESTS_CLARIFICATION"]["conversation_continues"] is True
    assert cases["CASE_5_HUMAN_REQUESTS_CLARIFICATION"]["execution_allowed"] is False
    assert cases["CASE_6_MISSING_HUMAN_RESPONSE"]["fail_closed"] is True
    assert cases["CASE_6_MISSING_HUMAN_RESPONSE"]["execution_allowed"] is False
    assert cases["CASE_6_MISSING_HUMAN_RESPONSE"]["authorization_created"] is False


def test_replay_and_fail_closed_policy_are_certified() -> None:
    certification = _certification()

    assert all(certification["replay_policy"].values())
    assert all(certification["fail_closed_certification"].values())
    assert certification["final_fields"] == FINAL_FIELDS
