"""Focused G69-10 common Failure, Presentation, and Owner Projection tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_common_failure_presentation_owner_projection_contract_v1 import (
    CANONICAL_COMMON_FAILURE_CONTRACT_VERSION,
    CANONICAL_OWNER_PROJECTION_CONTRACT_VERSION,
    CANONICAL_PRESENTATION_CONTRACT_VERSION,
    COMMON_FAILURE,
    ERROR,
    FAILURE,
    HIGH,
    HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE,
    NON_RECOVERABLE,
    NORMAL,
    OWNER_OUTCOME,
    OWNER_REFUSAL,
    REFERENCE_UNAVAILABLE,
    RECOVERABLE,
    RETRYABLE,
    NOT_RETRYABLE,
    CanonicalCommonFailureV1,
    CanonicalOwnerProjectionV1,
    CanonicalPresentationV1,
    canonical_presentation_facts_v1,
    create_canonical_common_failure_v1,
    create_canonical_owner_projection_v1,
    create_canonical_presentation_v1,
    deserialize_canonical_common_failure_v1,
    deserialize_canonical_owner_projection_v1,
    deserialize_canonical_presentation_v1,
    serialize_canonical_common_failure_v1,
    serialize_canonical_owner_projection_v1,
    serialize_canonical_presentation_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    DELIVERY_NOT_APPLICABLE,
    HUMAN_ACTOR,
    LEGACY_CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    NOT_ADVANCED,
    NOT_APPLICABLE,
    REFERENCE_NOT_APPLICABLE,
    REFUSED_ADVANCEMENT,
    REFUSED_DISPOSITION,
    REFUSAL_RESPONSE,
    RESUBMIT_PERMITTED_CONTROL,
    RETRYABLE as CHE_RETRYABLE,
    CanonicalHumanEntryOwnerTransitionV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-08-05T12:00:00Z"


def _next_act(*, present: bool = True) -> dict[str, object]:
    return {
        "next_act_identity": "NEXT-ACT-1" if present else NOT_APPLICABLE,
        "next_act_kind": "CLARIFICATION_RESPONSE" if present else NOT_APPLICABLE,
        "target_identity": "TARGET-1" if present else NOT_APPLICABLE,
        "target_digest": "sha256:" + "1" * 64 if present else NOT_APPLICABLE,
        "expected_owner_revision": 2 if present else NOT_APPLICABLE,
        "permitted_controls": ["action:"] if present else [],
        "payload_constraints": {"value_required": True} if present else {},
        "exact_human_act_required": present,
        "cancellation_permitted": False,
        "interruption_permitted": False,
    }


def _continuation(
    *, present: bool = True, terminal: bool = False
) -> dict[str, object]:
    return {
        "continuation_identity": "CONTINUATION-1" if present else NOT_APPLICABLE,
        "continuation_state": (
            "TERMINAL" if terminal else "ACTIVE"
        ) if present else NOT_APPLICABLE,
        "expected_next_act_identity": (
            "TERMINAL-1" if terminal else "NEXT-ACT-1"
        ) if present else NOT_APPLICABLE,
        "expected_owner_state_identity": (
            "OWNER-STATE-1" if present else NOT_APPLICABLE
        ),
        "expected_owner_revision": 2 if present else NOT_APPLICABLE,
    }


def _terminal_state(*, terminal: bool = False) -> dict[str, object]:
    return {
        "terminal": terminal,
        "terminal_identity": "TERMINAL-1" if terminal else NOT_APPLICABLE,
        "terminal_type": "COMPLETE" if terminal else NOT_APPLICABLE,
        "terminal_status": "TERMINAL_COMPLETE" if terminal else NOT_APPLICABLE,
    }


def _projection(
    *, terminal: bool = False, continuation: bool = True
) -> CanonicalOwnerProjectionV1:
    return create_canonical_owner_projection_v1(
        request_identity="REQUEST-1",
        response_identity="RESPONSE-1",
        owner_identity="CONVERSATION_OWNER",
        owner_state="OWNER-STATE-1",
        owner_next_act=_next_act(present=not terminal),
        owner_advancement="TERMINAL" if terminal else "ADVANCED",
        owner_revision_before=1,
        owner_revision=2,
        owner_terminal_state=_terminal_state(terminal=terminal),
        owner_continuation=_continuation(
            present=continuation, terminal=terminal
        ),
        owner_result_projection={
            "owner_status": "COMPLETE" if terminal else "CLARIFICATION_REQUIRED",
            "response_disposition": "TERMINAL" if terminal else "PENDING",
        },
        metadata={},
    )


def _presentation(
    *, failure: bool = False
) -> CanonicalPresentationV1:
    return create_canonical_presentation_v1(
        request_identity="REQUEST-1",
        response_identity="RESPONSE-1",
        presentation_state=FAILURE if failure else "PENDING",
        presentation_kind=COMMON_FAILURE if failure else OWNER_OUTCOME,
        presentation_message=(
            "The owner refused the act."
            if failure
            else "Provide the exact requested action."
        ,),
        presentation_controls=("action:",),
        presentation_priority=HIGH if failure else NORMAL,
        presentation_visibility=HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE,
        presentation_accessibility={
            "ordered_text_available": True,
            "structured_facts_available": True,
            "language": "und",
            "reading_order": "DOCUMENT_ORDER",
        },
        presentation_metadata={"owner_attribution": "CONVERSATION_OWNER"},
    )


def _failure(
    *, recoverable: bool = True
) -> CanonicalCommonFailureV1:
    projection = _projection()
    presentation = _presentation(failure=True)
    return create_canonical_common_failure_v1(
        failure_kind=OWNER_REFUSAL,
        failure_scope="TARGET-1",
        failure_owner="CONVERSATION_OWNER",
        severity=ERROR,
        recoverability=RECOVERABLE if recoverable else NON_RECOVERABLE,
        retryability=RETRYABLE if recoverable else NOT_RETRYABLE,
        failure_reason="OWNER_INPUT_NOT_ADMITTED",
        owner_projection=projection,
        continuation=projection.owner_continuation,
        revision=2,
        request_identity="REQUEST-1",
        response_identity="RESPONSE-1",
        presentation_identity=presentation.presentation_identity,
        metadata={"recovery_requirement": "RESUBMIT_PERMITTED_CONTROL"},
    )


def _request(root: Path) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G69-10-CLIA",
        adapter_identity="G69-10-ADAPTER",
        actor_identity="G69-10-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-10-SESSION",
        workspace_identity=str(root / "workspace"),
        runtime_scope_identity=str(root / "runtime"),
        request_identity="G69-10-REQUEST-000001",
        source_act_identity="G69-10-SOURCE-ACT-000001",
        order_identity="G69-10-ORDER-000001",
        idempotency_identity="G69-10-IDEMPOTENCY-000001",
        source_payload="Implement a validator.",
        source_encoding="UTF-8",
        source_modality="TEXT",
        declared_capabilities=("TEXT_INPUT", "TEXT_PRESENTATION"),
        metadata={"transport_trace_identity": "G69-10-TRACE-000001"},
        created_at=CREATED_AT,
    )


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def test_success_owner_projection_and_presentation_are_complete() -> None:
    projection = _projection()
    presentation = _presentation()

    assert projection.contract_version == CANONICAL_OWNER_PROJECTION_CONTRACT_VERSION
    assert projection.owner_next_act["next_act_identity"] == "NEXT-ACT-1"
    assert projection.owner_continuation["continuation_identity"] == (
        "CONTINUATION-1"
    )
    assert presentation.contract_version == CANONICAL_PRESENTATION_CONTRACT_VERSION
    assert presentation.presentation_controls == ("action:",)


@pytest.mark.parametrize(
    "owner_identity",
    [
        "CONVERSATION_OWNER",
        "PLATFORM_CORE_OWNER",
        "GOVERNANCE_OWNER",
        "AUTHORIZATION_OWNER",
        "WORKER_OWNER",
        "RESULT_OWNER",
        "REPLAY_OWNER",
        "CERTIFICATION_OWNER",
    ],
)
def test_owner_projection_contract_is_owner_neutral(owner_identity: str) -> None:
    projection = create_canonical_owner_projection_v1(
        request_identity="REQUEST-OWNER-NEUTRAL",
        response_identity="RESPONSE-OWNER-NEUTRAL",
        owner_identity=owner_identity,
        owner_state="OWNER-STATE-1",
        owner_next_act=_next_act(),
        owner_advancement="ADVANCED",
        owner_revision_before=1,
        owner_revision=2,
        owner_terminal_state=_terminal_state(),
        owner_continuation=_continuation(),
        owner_result_projection={"owner_status": "OUTCOME_AVAILABLE"},
    )

    assert projection.owner_identity == owner_identity
    assert "internal_state" not in projection.to_dict()


def test_recoverable_and_non_recoverable_failures_are_distinct() -> None:
    recoverable = _failure(recoverable=True)
    terminal = _failure(recoverable=False)

    assert recoverable.contract_version == CANONICAL_COMMON_FAILURE_CONTRACT_VERSION
    assert recoverable.recoverability == RECOVERABLE
    assert recoverable.retryability == RETRYABLE
    assert terminal.recoverability == NON_RECOVERABLE
    assert terminal.retryability == NOT_RETRYABLE


def test_terminal_projection_is_complete_and_has_no_next_act() -> None:
    projection = _projection(terminal=True)

    assert projection.owner_advancement == "TERMINAL"
    assert projection.owner_terminal_state["terminal"] is True
    assert projection.owner_terminal_state["terminal_identity"] == "TERMINAL-1"
    assert projection.owner_next_act["next_act_identity"] == NOT_APPLICABLE
    assert projection.owner_continuation["continuation_state"] == "TERMINAL"


def test_serialization_round_trip_and_deep_immutability() -> None:
    projection = _projection()
    presentation = _presentation()
    failure = _failure()

    assert deserialize_canonical_owner_projection_v1(
        serialize_canonical_owner_projection_v1(projection)
    ).to_dict() == projection.to_dict()
    assert deserialize_canonical_presentation_v1(
        serialize_canonical_presentation_v1(presentation)
    ).to_dict() == presentation.to_dict()
    assert deserialize_canonical_common_failure_v1(
        serialize_canonical_common_failure_v1(failure)
    ).to_dict() == failure.to_dict()
    with pytest.raises(FrozenInstanceError):
        projection.owner_state = "CHANGED"  # type: ignore[misc]
    with pytest.raises(TypeError):
        projection.owner_next_act["next_act_identity"] = "CHANGED"  # type: ignore[index]
    with pytest.raises(TypeError):
        presentation.presentation_metadata["new"] = True  # type: ignore[index]
    with pytest.raises(TypeError):
        failure.metadata["new"] = True  # type: ignore[index]


def test_duplicate_failure_identity_conflict_fails_closed() -> None:
    failure = _failure()
    identical = CanonicalCommonFailureV1.from_dict(failure.to_dict())
    assert identical.to_dict() == failure.to_dict()

    conflicting = failure.to_dict()
    conflicting["failure_reason"] = "DIFFERENT_REASON"
    with pytest.raises(FailClosedRuntimeError, match="identity-content conflict"):
        CanonicalCommonFailureV1.from_dict(conflicting)


def test_stale_projection_and_terminal_inconsistency_fail_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="stale"):
        create_canonical_owner_projection_v1(
            request_identity="REQUEST-1",
            response_identity="RESPONSE-1",
            owner_identity="OWNER-1",
            owner_state="OWNER-STATE-1",
            owner_next_act=_next_act(),
            owner_advancement="ADVANCED",
            owner_revision_before=2,
            owner_revision=1,
            owner_terminal_state=_terminal_state(),
            owner_continuation=_continuation(),
            owner_result_projection={"owner_status": "PENDING"},
        )
    with pytest.raises(FailClosedRuntimeError, match="terminal"):
        create_canonical_owner_projection_v1(
            request_identity="REQUEST-1",
            response_identity="RESPONSE-1",
            owner_identity="OWNER-1",
            owner_state="OWNER-STATE-1",
            owner_next_act=_next_act(),
            owner_advancement="TERMINAL",
            owner_revision_before=1,
            owner_revision=2,
            owner_terminal_state=_terminal_state(terminal=True),
            owner_continuation=_continuation(terminal=True),
            owner_result_projection={"owner_status": "TERMINAL"},
        )


def test_presentation_rejects_channel_specific_logic() -> None:
    with pytest.raises(FailClosedRuntimeError, match="channel-specific"):
        create_canonical_presentation_v1(
            request_identity="REQUEST-1",
            response_identity="RESPONSE-1",
            presentation_state="INFORMATIONAL",
            presentation_kind=OWNER_OUTCOME,
            presentation_message=("Owner response available.",),
            presentation_metadata={"gui_layout": "two-column"},
        )
    with pytest.raises(FailClosedRuntimeError, match="channel-specific"):
        create_canonical_presentation_v1(
            request_identity="REQUEST-1",
            response_identity="RESPONSE-1",
            presentation_state="INFORMATIONAL",
            presentation_kind=OWNER_OUTCOME,
            presentation_message=("<button>Continue</button>",),
        )


def test_owner_projection_rejects_owner_internal_runtime_state() -> None:
    with pytest.raises(FailClosedRuntimeError, match="owner-internal"):
        create_canonical_owner_projection_v1(
            request_identity="REQUEST-1",
            response_identity="RESPONSE-1",
            owner_identity="OWNER-1",
            owner_state="OWNER-STATE-1",
            owner_next_act=_next_act(),
            owner_advancement="ADVANCED",
            owner_revision_before=1,
            owner_revision=2,
            owner_terminal_state=_terminal_state(),
            owner_continuation=_continuation(),
            owner_result_projection={"internal_state": {"secret": True}},
        )


@pytest.mark.parametrize(
    "channel",
    ["CLIA", "GUI", "BROWSER", "REST", "SPEECH", "AGENT_TO_AGENT"],
)
def test_same_presentation_facts_support_every_channel_without_workflow_logic(
    channel: str,
) -> None:
    presentation = _presentation()
    facts = canonical_presentation_facts_v1(presentation)

    assert channel in {"CLIA", "GUI", "BROWSER", "REST", "SPEECH", "AGENT_TO_AGENT"}
    assert facts == canonical_presentation_facts_v1(presentation)
    serialized = serialize_canonical_presentation_v1(presentation).lower()
    for forbidden in (
        "gui_layout",
        "cli_format",
        "html",
        "terminal_escape",
        "browser_control",
        "speech_rendering",
    ):
        assert forbidden not in serialized


def test_che_binds_all_three_contracts_and_duplicate_response(tmp_path: Path) -> None:
    request = _request(tmp_path)
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    duplicate = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )

    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    assert response.contract_version == CANONICAL_CHE_RESPONSE_CONTRACT_VERSION
    assert isinstance(response.owner_projection, CanonicalOwnerProjectionV1)
    assert isinstance(response.presentation, CanonicalPresentationV1)
    assert response.common_failure is None
    assert response.continuation_envelope is not None
    assert response.owner_projection.owner_continuation[
        "continuation_identity"
    ] == response.continuation_envelope.continuation_identity
    assert duplicate.to_dict() == response.to_dict()


def test_che_refusal_response_binds_common_failure() -> None:
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="CONVERSATION_OWNER",
        owner_state_identity="OWNER-STATE-1",
        owner_revision_before=2,
        owner_revision_after=2,
        response_disposition=REFUSED_DISPOSITION,
        advancement_outcome=REFUSED_ADVANCEMENT,
        next_act_identity="NEXT-ACT-1",
        next_act_kind="CLARIFICATION_RESPONSE",
        next_act_target_identity="TARGET-1",
        next_act_target_digest="sha256:" + "1" * 64,
        next_act_expected_owner_revision=2,
        permitted_controls=("action:",),
        payload_constraints={},
        exact_human_act_required=True,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity="REFUSAL-1",
        refusal_type="OWNER_INPUT_NOT_ADMITTED",
        refusal_status="STABLE_REFUSAL",
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=CHE_RETRYABLE,
        recovery_requirement=RESUBMIT_PERMITTED_CONTROL,
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    response = CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity="RESPONSE-1",
        request_identity="REQUEST-1",
        response_type=REFUSAL_RESPONSE,
        producing_owner="CONVERSATION_OWNER",
        owner_status="OWNER_INPUT_NOT_ADMITTED",
        advancement_state=REFUSED_ADVANCEMENT,
        presentation_payload=("The owner refused the submitted act.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
        },
        correlation_identity="CORRELATION-1",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
    )

    assert response.common_failure is not None
    assert response.common_failure.failure_kind == OWNER_REFUSAL
    assert response.common_failure.retryability == RETRYABLE
    assert response.presentation.presentation_state == FAILURE


def test_che_reference_failure_uses_common_failure_contract() -> None:
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="PLATFORM_CORE_PROJECT_SERVICES",
        owner_state_identity=NOT_APPLICABLE,
        owner_revision_before=NOT_APPLICABLE,
        owner_revision_after=NOT_APPLICABLE,
        response_disposition="INFORMATIONAL",
        advancement_outcome=NOT_ADVANCED,
        next_act_identity=None,
        next_act_kind=None,
        next_act_target_identity=None,
        next_act_target_digest=None,
        next_act_expected_owner_revision=NOT_APPLICABLE,
        permitted_controls=(),
        payload_constraints={"availability_status": "MISSING"},
        exact_human_act_required=False,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=None,
        refusal_type=NOT_APPLICABLE,
        refusal_status=NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=CHE_RETRYABLE,
        recovery_requirement=RESUBMIT_PERMITTED_CONTROL,
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    response = CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity="REFERENCE-RESPONSE-1",
        request_identity="REFERENCE-REQUEST-1",
        response_type="INFORMATIONAL",
        producing_owner=transition.producing_owner,
        owner_status="OPAQUE_REFERENCE_MISSING",
        advancement_state=NOT_ADVANCED,
        presentation_payload=("The Reference is unavailable.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
            "opaque_reference_validation": {
                "availability_statuses": ["MISSING"],
            },
        },
        correlation_identity="REFERENCE-CORRELATION-1",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
    )

    assert response.common_failure is not None
    assert response.common_failure.failure_kind == REFERENCE_UNAVAILABLE
    assert response.common_failure.recoverability == RECOVERABLE


def test_legacy_response_translation_occurs_inside_che_contract() -> None:
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="LEGACY_CHE_BOUNDARY_COMPATIBILITY",
        owner_state_identity=NOT_APPLICABLE,
        owner_revision_before=NOT_APPLICABLE,
        owner_revision_after=NOT_APPLICABLE,
        response_disposition="INFORMATIONAL",
        advancement_outcome=NOT_ADVANCED,
        next_act_identity=None,
        next_act_kind=None,
        next_act_target_identity=None,
        next_act_target_digest=None,
        next_act_expected_owner_revision=NOT_APPLICABLE,
        permitted_controls=(),
        payload_constraints={},
        exact_human_act_required=False,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=None,
        refusal_type=NOT_APPLICABLE,
        refusal_status=NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=NOT_APPLICABLE,
        recovery_requirement=NOT_APPLICABLE,
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    current = CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity="RESPONSE-LEGACY-1",
        request_identity="REQUEST-LEGACY-1",
        response_type="INFORMATIONAL",
        producing_owner=transition.producing_owner,
        owner_status="OWNER_RESPONSE_AVAILABLE",
        advancement_state=NOT_ADVANCED,
        presentation_payload=("Owner response available.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
        },
        correlation_identity="CORRELATION-LEGACY-1",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
    )
    legacy = current.to_dict()
    legacy["contract_version"] = LEGACY_CANONICAL_CHE_RESPONSE_CONTRACT_VERSION
    for field_name in ("owner_projection", "presentation", "common_failure"):
        legacy.pop(field_name)

    translated = CanonicalHumanEntryResponseEnvelopeV1.from_dict(legacy)
    assert translated.contract_version == CANONICAL_CHE_RESPONSE_CONTRACT_VERSION
    assert isinstance(translated.owner_projection, CanonicalOwnerProjectionV1)
    assert isinstance(translated.presentation, CanonicalPresentationV1)
    assert translated.common_failure is None


def test_explicit_projection_tampering_fails_che_binding() -> None:
    projection = _projection().to_dict()
    projection["owner_state"] = "DIFFERENT-STATE"
    with pytest.raises(FailClosedRuntimeError):
        CanonicalOwnerProjectionV1.from_dict(projection)
