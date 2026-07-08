"""Regression coverage for G16-02 PCCL session runtime."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_cognition_layer import (
    PCCL_SESSION_ACTIVE,
    PCCL_SESSION_CLOSED,
    PCCL_SESSION_COMPLETED,
    PCCL_SESSION_CREATED,
    PCCL_SESSION_ESCALATED,
    PCCL_SESSION_RUNTIME_ARTIFACT_V1,
    PCCL_SESSION_RUNTIME_VERSION,
    PCCL_SESSION_WAITING,
    PlatformCoreCognitionLayer,
    close_pccl_session,
    create_pccl_session,
    mark_pccl_session_completed,
    mark_pccl_session_escalated,
    mark_pccl_session_waiting,
    start_pccl_session,
)


CREATED_AT = "2026-07-08T00:00:00Z"
UPDATED_AT = "2026-07-08T00:01:00Z"


def _session() -> dict:
    return create_pccl_session(
        session_id="PCCL-G16-02-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-02-001",
        replay_reference=".runtime/aicli/session/project_context",
        runtime_reference="RUNTIME-G16-02-001",
        certification_reference="CERT-G16-02-FOUNDATION",
        provider_budget=3,
    )


def test_create_pccl_session_runtime_state_without_cognition_behavior() -> None:
    session = _session()

    assert session["artifact_type"] == PCCL_SESSION_RUNTIME_ARTIFACT_V1
    assert session["pccl_session_runtime_version"] == PCCL_SESSION_RUNTIME_VERSION
    assert session["session_status"] == PCCL_SESSION_CREATED
    assert session["iteration_counter"] == 0
    assert session["provider_budget"] == 3
    assert session["provider_budget_remaining"] == 3
    assert session["termination_reason"] is None
    assert session["replay_reference"] == ".runtime/aicli/session/project_context"
    assert session["originating_human_goal_reference"] == "HUMAN-GOAL-G16-02-001"
    assert session["runtime_reference"] == "RUNTIME-G16-02-001"
    assert session["certification_reference"] == "CERT-G16-02-FOUNDATION"
    assert session["provider_invoked"] is False
    assert session["proposal_generated"] is False
    assert session["context_assembled"] is False
    assert session["policy_evaluated"] is False
    assert session["clarification_requested"] is False
    assert session["governance_performed"] is False
    assert session["worker_invoked"] is False
    assert session["replay_implemented"] is False
    assert session["replay_certified"] is False
    assert len(session["lifecycle_events"]) == 1
    assert session["lifecycle_events"][0]["event_type"] == "pccl_session_created"
    assert session["artifact_hash"].startswith("sha256:")


def test_pccl_session_lifecycle_transitions_are_deterministic_and_do_not_spend_budget() -> None:
    created = _session()
    active = start_pccl_session(session=created, updated_at=UPDATED_AT)
    waiting = mark_pccl_session_waiting(
        session=active,
        waiting_reason="future context assembler not implemented",
        updated_at="2026-07-08T00:02:00Z",
    )
    active_again = start_pccl_session(session=waiting, updated_at="2026-07-08T00:03:00Z")
    completed = mark_pccl_session_completed(
        session=active_again,
        completion_reference="PCCL-COMPLETION-G16-02-001",
        updated_at="2026-07-08T00:04:00Z",
    )

    assert active["session_status"] == PCCL_SESSION_ACTIVE
    assert waiting["session_status"] == PCCL_SESSION_WAITING
    assert waiting["waiting_reason"] == "future context assembler not implemented"
    assert active_again["session_status"] == PCCL_SESSION_ACTIVE
    assert completed["session_status"] == PCCL_SESSION_COMPLETED
    assert completed["completion_reference"] == "PCCL-COMPLETION-G16-02-001"
    assert completed["termination_reason"] == "completed"
    assert completed["iteration_counter"] == 0
    assert completed["provider_budget_remaining"] == 3
    assert [event["event_index"] for event in completed["lifecycle_events"]] == [0, 1, 2, 3, 4]
    assert completed["lifecycle_events"][1]["previous_event_hash"] == completed["lifecycle_events"][0]["event_hash"]


def test_pccl_session_escalation_and_close_are_terminal() -> None:
    active = start_pccl_session(session=_session(), updated_at=UPDATED_AT)
    escalated = mark_pccl_session_escalated(
        session=active,
        escalation_reference="HUMAN-REVIEW-G16-02-001",
        termination_reason="human approval required before future cognition can continue",
        updated_at="2026-07-08T00:02:00Z",
    )

    assert escalated["session_status"] == PCCL_SESSION_ESCALATED
    assert escalated["escalation_reference"] == "HUMAN-REVIEW-G16-02-001"
    assert escalated["termination_reason"] == "human approval required before future cognition can continue"
    with pytest.raises(FailClosedRuntimeError, match="terminal session"):
        start_pccl_session(session=escalated, updated_at="2026-07-08T00:03:00Z")

    closed = close_pccl_session(
        session=active,
        termination_reason="future PCCL service unavailable",
        updated_at="2026-07-08T00:04:00Z",
    )
    assert closed["session_status"] == PCCL_SESSION_CLOSED
    assert closed["termination_reason"] == "future PCCL service unavailable"
    with pytest.raises(FailClosedRuntimeError, match="terminal session"):
        mark_pccl_session_waiting(
            session=closed,
            waiting_reason="cannot wait after close",
            updated_at="2026-07-08T00:05:00Z",
        )


def test_platform_core_cognition_layer_exposes_session_runtime_operations() -> None:
    service = PlatformCoreCognitionLayer()
    created = service.create_session(
        session_id="PCCL-SERVICE-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-SERVICE-001",
        provider_budget=1,
    )
    active = service.start_session(session=created, updated_at=UPDATED_AT)
    waiting = service.mark_session_waiting(
        session=active,
        waiting_reason="future provider runtime not implemented",
        updated_at="2026-07-08T00:02:00Z",
    )
    completed = service.mark_session_completed(
        session=waiting,
        completion_reference="PCCL-SERVICE-COMPLETION",
        updated_at="2026-07-08T00:03:00Z",
    )

    assert completed["session_status"] == PCCL_SESSION_COMPLETED
    assert completed["provider_invoked"] is False
    assert completed["worker_invoked"] is False


def test_pccl_session_runtime_fails_closed_on_invalid_budget_and_tampering() -> None:
    with pytest.raises(FailClosedRuntimeError, match="provider_budget"):
        create_pccl_session(
            session_id="PCCL-BAD-BUDGET",
            creation_timestamp=CREATED_AT,
            originating_human_goal_reference="HUMAN-GOAL",
            provider_budget=-1,
        )

    tampered = deepcopy(_session())
    tampered["provider_invoked"] = True
    with pytest.raises(FailClosedRuntimeError, match="artifact hash mismatch"):
        start_pccl_session(session=tampered, updated_at=UPDATED_AT)


def test_pccl_session_runtime_fails_closed_on_tampered_rehashed_authority_flag() -> None:
    tampered = deepcopy(_session())
    tampered["provider_invoked"] = True
    original_hash = tampered.pop("artifact_hash")
    assert original_hash.startswith("sha256:")
    from aigol.runtime.transport.serialization import replay_hash

    tampered["artifact_hash"] = replay_hash(tampered)
    with pytest.raises(FailClosedRuntimeError, match="provider_invoked must be false"):
        start_pccl_session(session=tampered, updated_at=UPDATED_AT)
