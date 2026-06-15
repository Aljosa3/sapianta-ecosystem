"""Tests for AIGOL_ACLI_POST_ENTRY_CONTINUATION_GATE_V1."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_entry_continuation_gate_runtime import (
    CLARIFICATION_REQUIRED,
    COGNITION_BOUNDARY_REACHED,
    CONTINUATION_ALLOWED,
    FAILED_CLOSED,
    NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
    OPERATOR_DECISION_SUPPORT,
    POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1,
    PROPOSAL_BOUNDARY_REACHED,
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    evaluate_post_entry_continuation_gate,
    reconstruct_post_entry_continuation_gate_replay,
)


CREATED_AT = "2026-06-15T00:00:00Z"


def _gate(tmp_path, **overrides):
    params = {
        "gate_id": "POST-ENTRY-GATE-000001",
        "prompt_id": "PROMPT-POST-ENTRY-GATE-000001",
        "human_prompt": "Implement provider adapter milestone.",
        "workflow_id": NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        "lifecycle_entry_status": "CONTEXT_ASSEMBLED",
        "provider_necessity_classification": "PROVIDER_REQUIRED_FOR_PROPOSAL",
        "auto_continue_enabled": False,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "gate",
        "lifecycle_replay_reference": "turn/native_context",
    }
    params.update(overrides)
    return evaluate_post_entry_continuation_gate(**params)


def test_gate_allows_execution_capable_continuation_only_when_explicit(tmp_path) -> None:
    capture = _gate(tmp_path, auto_continue_enabled=True)
    replay = reconstruct_post_entry_continuation_gate_replay(tmp_path / "gate")
    artifact = capture["post_entry_continuation_gate_artifact"]

    assert artifact["artifact_type"] == POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1
    assert capture["gate_status"] == CONTINUATION_ALLOWED
    assert capture["continuation_allowed"] is True
    assert capture["execution_summary_required"] is True
    assert capture["human_confirmation_required"] is True
    assert capture["authorization_required"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["authorization_created"] is False
    assert replay["gate_status"] == CONTINUATION_ALLOWED
    assert replay["continuation_runtime"] == "context_assembled_to_ppp_routing_continuation"


def test_gate_requests_clarification_for_ambiguous_execution_capable_entry(tmp_path) -> None:
    capture = _gate(tmp_path)

    assert capture["gate_status"] == CLARIFICATION_REQUIRED
    assert capture["continuation_allowed"] is False
    assert capture["execution_summary_required"] is False
    assert capture["human_confirmation_required"] is False
    assert capture["authorization_required"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_gate_stops_proposal_only_entry_at_review_boundary(tmp_path) -> None:
    capture = _gate(
        tmp_path,
        workflow_id=CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        lifecycle_entry_status="CLARIFICATION_REQUIRED",
        provider_necessity_classification=None,
    )

    assert capture["gate_status"] == PROPOSAL_BOUNDARY_REACHED
    assert capture["continuation_allowed"] is False
    assert capture["execution_summary_required"] is False
    assert capture["authorization_required"] is False


def test_gate_stops_cognition_only_entry_without_execution_request(tmp_path) -> None:
    capture = _gate(
        tmp_path,
        workflow_id=OPERATOR_DECISION_SUPPORT,
        lifecycle_entry_status="RECOMMENDATION_CREATED",
        provider_necessity_classification=None,
    )

    assert capture["gate_status"] == COGNITION_BOUNDARY_REACHED
    assert capture["continuation_allowed"] is False
    assert capture["execution_requested"] is False
    assert capture["worker_invoked"] is False


def test_gate_fails_closed_when_no_certified_mapping_exists(tmp_path) -> None:
    capture = _gate(
        tmp_path,
        workflow_id="UNMAPPED_EXECUTION_ENTRY",
        lifecycle_entry_status="READY",
        provider_necessity_classification=None,
    )

    assert capture["gate_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert capture["failure_reason"] == "no certified post-entry continuation mapping exists"


def test_gate_reconstruction_detects_replay_corruption(tmp_path) -> None:
    _gate(tmp_path, auto_continue_enabled=True)
    path = tmp_path / "gate" / "000_post_entry_continuation_gate_recorded.json"
    wrapper = path.read_text(encoding="utf-8")
    path.write_text(wrapper.replace("CONTINUATION_ALLOWED", "FAILED_CLOSED", 1), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_post_entry_continuation_gate_replay(tmp_path / "gate")
