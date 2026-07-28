from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION,
    G31_APPROVE,
    G31_CANONICAL_CONDENSATION_DECISION,
    G31_REJECT,
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError


REPRESENTATIONS = {
    "requested_capability": "condense",
    "user_visible_outcome": "bounded runtime task",
    "allowed_operations": "inspect source",
    "prohibited_operations": "no mutation",
    "architectural_placement": "pre-G31 entry",
    "acceptance_conditions": "all requirements mapped",
    "testing_validation_requirements": "run deterministic tests",
    "explicit_exclusions": "no Worker activation",
    "safety_governance_constraints": "fail closed",
}


def _over_bound_request() -> str:
    return (
        "Implement the governed condensation entry integration while preserving "
        "the exact source request, every constitutional boundary, immutable "
        "Replay lineage, explicit human approval, deterministic validation, "
        "the dedicated Model D input binding, unchanged G31 preflight behavior, "
        "and the prohibition on Worker, Provider, authorization, or mutation "
        "authority before later distinct decisions."
    )


def _proposal_inputs(*, ambiguities=()) -> dict:
    commitments = {
        field: value
        if field
        in {
            "requested_capability",
            "user_visible_outcome",
            "architectural_placement",
        }
        else [value]
        for field, value in REPRESENTATIONS.items()
    }
    requirements = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "requirement_type": field,
            "source_text": f"source requirement for {value}",
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    mappings = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "target_field": field,
            "exact_condensed_representation": value,
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    return {
        "original_request_id": "REQUEST-35-13",
        "clarification_evidence": [
            {
                "question_id": "QUESTION-1",
                "question": "Does semantic approval authorize execution?",
                "answer_id": "ANSWER-1",
                "answer": "No; all later authority remains distinct.",
                "resolved": True,
            }
        ],
        "clarification_complete": True,
        "completed_objective_id": "OBJECTIVE-35-13",
        "completed_objective": (
            "Reach unchanged G31 preflight through the approved Model D binding."
        ),
        "project_id": "SAPIANTA",
        "invocation_id": "INVOCATION-35-13",
        "chain_id": "CHAIN-35-13",
        "semantic_commitments": commitments,
        "source_requirements": requirements,
        "requirement_mappings": mappings,
        "proposed_synthesis_body": (
            "runtime validation; " + "; ".join(REPRESENTATIONS.values())
        ),
        "unresolved_ambiguities": list(ambiguities),
    }


def _entry(tmp_path, **overrides):
    arguments = {
        "interface_name": "test-human-interface",
        "session_id": "SESSION-35-13",
        "human_requests": [],
        "created_at": "2026-07-28T15:00:00Z",
        "runtime_root": tmp_path,
        "workspace": "/workspace/sapianta",
        "governed_runtime_runner": lambda **_: {},
        "g31_human_actor_id": "HUMAN-35-13",
    }
    arguments.update(overrides)
    return run_human_interface_runtime_entry(**arguments)


def _begin(tmp_path, *, proposal_inputs=None):
    return _entry(
        tmp_path,
        g31_synthesis_preflight_prompt=_over_bound_request(),
        canonical_condensation_proposal_inputs=(
            _proposal_inputs() if proposal_inputs is None else proposal_inputs
        ),
    )


def test_over_bound_entry_stops_on_exact_explicit_human_review(tmp_path):
    result = _begin(tmp_path)

    assert result["canonical_condensation_entry_integration_version"] == (
        CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION
    )
    assert result["canonical_condensation_entry_status"] == (
        "CANONICAL_CONDENSATION_HUMAN_REVIEW_REQUIRED"
    )
    assert result["canonical_condensation_required"] is True
    assert result["canonical_condensation_validation_capture"][
        "validation_status"
    ] == "PASS"
    assert result["g31_pending_action"]["action_type"] == (
        G31_CANONICAL_CONDENSATION_DECISION
    )
    assert result["g31_pending_action"]["valid_values"] == ["APPROVE", "REJECT"]
    assert result["codex_synthesis_preflight_capture"] is None
    assert result["semantic_representation_approved"] is False
    assert result["execution_authorized"] is False
    assert result["worker_invoked"] is False
    assert result["provider_invoked"] is False
    assert result["repository_mutated"] is False


def test_explicit_approval_reaches_unchanged_g31_with_exact_model_d_values(
    tmp_path,
):
    pending = _begin(tmp_path)
    result = _entry(
        tmp_path,
        g31_application_state=pending,
        g31_human_action=G31_APPROVE,
    )

    binding = result["canonical_condensation_g31_input_binding_capture"]
    preflight = result["codex_synthesis_preflight_capture"]
    continuity = result["canonical_condensation_preflight_continuity_capture"]
    proposal = result["canonical_condensation_proposal_capture"]

    assert result["canonical_condensation_entry_status"] == (
        "CANONICAL_CONDENSATION_G31_PREFLIGHT_READY"
    )
    assert result["g31_pending_action"] is None
    assert binding["original_source_request"] == _over_bound_request()
    assert binding["g31_function_argument"] == proposal[
        "proposed_synthesis_body"
    ]
    assert binding["g31_function_argument"] != binding[
        "original_source_request"
    ]
    assert preflight["raw_request"] == binding["g31_function_argument"]
    assert preflight["canonical_prefix"] == binding[
        "approved_projection_prefix"
    ]
    assert preflight["final_synthesized_request"] == binding[
        "g31_final_measured_request"
    ]
    assert preflight["synthesis_preflight_status"] == (
        "SYNTHESIS_PREFLIGHT_READY"
    )
    assert continuity["all_equal"] is True
    assert continuity["g31_preflight_invoked"] is True
    assert continuity["g31_preflight_behavior_modified"] is False
    assert result["semantic_representation_approved"] is True
    assert result["execution_authorized"] is False
    assert result["worker_invoked"] is False
    assert result["provider_invoked"] is False
    assert result["repository_mutated"] is False


def test_explicit_rejection_records_replay_without_g31_or_execution(tmp_path):
    pending = _begin(tmp_path)
    result = _entry(
        tmp_path,
        g31_application_state=pending,
        g31_human_action=G31_REJECT,
    )

    assert result["canonical_condensation_entry_status"] == (
        "CANONICAL_CONDENSATION_REJECTED"
    )
    assert result["canonical_condensation_human_decision_capture"][
        "decision"
    ] == "REJECT"
    assert result["canonical_condensation_phase2_replay_capture"][
        "decision"
    ] == "REJECT"
    assert result["canonical_condensation_g31_input_binding_capture"] is None
    assert result["codex_synthesis_preflight_capture"] is None
    assert result["execution_authorized"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_validation_failure_is_terminal_before_human_review_and_g31(tmp_path):
    result = _begin(
        tmp_path,
        proposal_inputs=_proposal_inputs(
            ambiguities=("The requested capability remains ambiguous.",)
        ),
    )

    assert result["canonical_condensation_entry_status"] == (
        "CANONICAL_CONDENSATION_VALIDATION_FAILED_CLOSED"
    )
    assert result["canonical_condensation_validation_capture"][
        "validation_status"
    ] == "FAIL"
    assert result["g31_pending_action"] is None
    assert result["canonical_condensation_human_review_capture"] is None
    assert result["codex_synthesis_preflight_capture"] is None
    assert result["worker_invoked"] is False


def test_over_bound_entry_without_proposal_inputs_preserves_legacy_failure(tmp_path):
    result = _entry(
        tmp_path,
        g31_synthesis_preflight_prompt=_over_bound_request(),
    )

    assert result["codex_synthesis_preflight_capture"][
        "synthesis_preflight_status"
    ] == "SYNTHESIS_PREFLIGHT_FAILED_CLOSED"
    assert result["canonical_condensation_required"] is True
    assert result["canonical_condensation_entry_status"] == (
        "CANONICAL_CONDENSATION_PROPOSAL_INPUT_REQUIRED_FAILED_CLOSED"
    )
    assert result["codex_synthesis_preflight_capture"]["provider_invoked"] is False
    assert result["codex_synthesis_preflight_capture"]["repository_mutated"] is False


def test_short_direct_request_preserves_historical_preflight_branch(tmp_path):
    result = _entry(
        tmp_path,
        g31_synthesis_preflight_prompt="validate the exact runtime",
    )

    assert result["codex_synthesis_preflight_capture"][
        "synthesis_preflight_status"
    ] == "SYNTHESIS_PREFLIGHT_READY"
    assert "canonical_condensation_entry_integration_version" not in result
    assert "canonical_condensation_required" not in result
    assert result["g31_pending_action"] is None


def test_direct_mode_rejects_mixed_condensation_inputs(tmp_path):
    with pytest.raises(FailClosedRuntimeError):
        _entry(
            tmp_path,
            g31_synthesis_preflight_prompt="validate the exact runtime",
            canonical_condensation_proposal_inputs=_proposal_inputs(),
        )


def test_pending_review_substitution_fails_closed_before_decision(tmp_path):
    pending = _begin(tmp_path)
    changed = deepcopy(pending)
    changed["g31_pending_action"]["context"]["review_warning"] = "substituted"

    with pytest.raises(FailClosedRuntimeError):
        _entry(
            tmp_path,
            g31_application_state=changed,
            g31_human_action=G31_APPROVE,
        )


@pytest.mark.parametrize("action", ["approve", "YES", "", "RETRY"])
def test_ambiguous_or_alternate_decision_values_fail_closed(tmp_path, action):
    pending = _begin(tmp_path)

    with pytest.raises((FailClosedRuntimeError, ValueError)):
        _entry(
            tmp_path,
            g31_application_state=pending,
            g31_human_action=action,
        )
