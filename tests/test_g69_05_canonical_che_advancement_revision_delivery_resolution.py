"""Focused G69-05 CHE advancement, revision, and delivery tests."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ADVANCED,
    CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    DELIVERY_COMMITTED_RESPONSE_FOUND,
    DELIVERY_ENTERED_NOT_ADVANCED,
    DELIVERY_NOT_FOUND,
    DELIVERY_OUTCOME_UNKNOWN,
    DELIVERY_RESOLUTION_QUERY_CAPABILITY,
    HUMAN_ACTOR,
    MANUAL_REVIEW_REQUIRED,
    NOT_RETRYABLE,
    PENDING_RESPONSE,
    QUERY_DELIVERY_STATUS,
    REFUSED_ADVANCEMENT,
    REFUSAL_RESPONSE,
    REFERENCE_CREATED,
    REFERENCE_NOT_CREATED,
    TERMINAL_CONTINUATION,
    TERMINAL_RESPONSE,
    CanonicalHumanEntryDeliveryResolutionQueryV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
    serialize_canonical_che_response_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-08-04T16:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _request(
    root: Path,
    number: int,
    *,
    source_act_identity: str,
    payload: object = "Implement a validator.",
    interface_identity: str = "G69-05-CLIA",
    adapter_identity: str = "G69-05-CLIA-ADAPTER",
    idempotency_identity: str | None = None,
    modality: str = "TEXT",
    capabilities: tuple[str, ...] = ("TEXT_INPUT", "TEXT_PRESENTATION"),
) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=interface_identity,
        adapter_identity=adapter_identity,
        actor_identity="G69-05-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-05-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(root / "runtime"),
        request_identity=f"G69-05-REQUEST-{number:06d}",
        source_act_identity=source_act_identity,
        order_identity=f"G69-05-ORDER-{number:06d}",
        idempotency_identity=(
            idempotency_identity or f"G69-05-IDEMPOTENCY-{number:06d}"
        ),
        source_payload=payload,
        source_encoding="UTF-8",
        source_modality=modality,
        declared_capabilities=capabilities,
        metadata={"transport_trace_identity": f"G69-05-TRACE-{number:06d}"},
        created_at=CREATED_AT,
    )


def _initial(
    root: Path,
) -> tuple[CanonicalHumanEntryRequestEnvelopeV1, CanonicalHumanEntryResponseEnvelopeV1]:
    request = _request(root, 1, source_act_identity="G69-05-SOURCE-ACT-000001")
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    return request, response


def _resolution_request(
    root: Path,
    number: int,
    *,
    target_request_identity: str,
    target_idempotency_identity: str,
    target_source_act_digest: str,
    target_interaction_identity: str,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    query = CanonicalHumanEntryDeliveryResolutionQueryV1(
        contract_version=CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION,
        target_request_identity=target_request_identity,
        target_idempotency_identity=target_idempotency_identity,
        target_source_act_digest=target_source_act_digest,
        target_interaction_identity=target_interaction_identity,
    )
    return _request(
        root,
        number,
        source_act_identity=f"G69-05-DELIVERY-QUERY-{number:06d}",
        payload=query.to_dict(),
        modality="STRUCTURED",
        capabilities=(DELIVERY_RESOLUTION_QUERY_CAPABILITY,),
    )


def test_advanced_conversation_continuation_binds_revision_and_changed_next_act(
    tmp_path: Path,
) -> None:
    _, initial = _initial(tmp_path)
    first = initial.owner_transition
    continuation = initial.continuation_envelope
    assert continuation is not None
    request = _request(
        tmp_path,
        2,
        source_act_identity=continuation.expected_next_act_identity,
        payload="action: implement",
        interface_identity="G69-05-GUI",
        adapter_identity="G69-05-GUI-ADAPTER",
    )

    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )

    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    transition = response.owner_transition
    assert response.response_type == PENDING_RESPONSE
    assert transition.advancement_outcome == ADVANCED
    assert transition.owner_state_identity == first.owner_state_identity
    assert transition.owner_revision_before == first.owner_revision_after == 1
    assert transition.owner_revision_after > transition.owner_revision_before
    assert transition.next_act_expected_owner_revision == (
        transition.owner_revision_after
    )
    assert transition.next_act_identity != first.next_act_identity
    assert transition.permitted_controls == ("subject: <value>",)
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.interaction_identity == (
        continuation.interaction_identity
    )
    assert response.continuation_envelope.expected_owner_revision == (
        transition.owner_revision_after
    )


def test_malformed_continuation_is_stable_refusal_without_fork(
    tmp_path: Path,
) -> None:
    _, initial = _initial(tmp_path)
    continuation = initial.continuation_envelope
    assert continuation is not None
    request = _request(
        tmp_path,
        2,
        source_act_identity=continuation.expected_next_act_identity,
        payload="action create",
    )

    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )

    transition = response.owner_transition
    assert response.response_type == REFUSAL_RESPONSE
    assert transition.advancement_outcome == REFUSED_ADVANCEMENT
    assert transition.owner_revision_before == transition.owner_revision_after == 1
    assert transition.next_act_identity == initial.owner_transition.next_act_identity
    assert transition.permitted_controls == ("action: <value>",)
    assert transition.refusal_identity
    assert transition.refusal_type == "OWNER_INPUT_NOT_ADMITTED"
    assert transition.refusal_status == "STABLE_REFUSAL"
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.interaction_identity == (
        continuation.interaction_identity
    )


def test_pending_response_is_complete_and_contains_no_owner_application_state(
    tmp_path: Path,
) -> None:
    _, response = _initial(tmp_path)
    transition = response.owner_transition

    assert transition.next_act_identity
    assert transition.next_act_kind == (
        "CONVERSATION_SEMANTIC_INPUT_OR_EXACT_COMMIT_ACT"
    )
    assert transition.next_act_target_identity == "objective_readiness"
    assert transition.next_act_target_digest.startswith("sha256:")
    assert transition.next_act_expected_owner_revision == 1
    assert transition.permitted_controls == ("action: <value>",)
    assert transition.exact_human_act_required is True
    serialized = serialize_canonical_che_response_envelope_v1(response)
    for forbidden in (
        "canonical_working_memory",
        "semantic_slots",
        "proposal_operations",
        "governance_state",
        "worker_state",
    ):
        assert forbidden not in serialized


def test_terminal_read_only_response_has_terminal_continuation_and_exact_statuses(
    tmp_path: Path,
) -> None:
    request = _request(
        tmp_path,
        1,
        source_act_identity="G69-05-SOURCE-ACT-TERMINAL",
        payload="Show architecture.",
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )

    assert response.response_type == TERMINAL_RESPONSE
    transition = response.owner_transition
    assert transition.terminal_identity
    assert transition.terminal_type == "READ_ONLY_RESULT_COMPLETE"
    assert transition.terminal_status == "TERMINAL_COMPLETE"
    assert transition.replay_reference_status == REFERENCE_CREATED
    assert transition.certification_reference_status == REFERENCE_NOT_CREATED
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.continuation_state == TERMINAL_CONTINUATION

    resumed = _request(
        tmp_path,
        2,
        source_act_identity=response.continuation_envelope.expected_next_act_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="terminal"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=resumed,
            continuation_envelope=response.continuation_envelope,
            governed_runtime_runner=_fail_runner,
        )


def test_identical_duplicate_returns_committed_response_and_conflict_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0
    original = che_service._run_human_interface_runtime_entry_owner_execution_v1

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        counted,
    )
    request, first = _initial(tmp_path)
    duplicate = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert duplicate.to_dict() == first.to_dict()
    assert calls == 1

    conflicting = CanonicalHumanEntryRequestEnvelopeV1.from_dict(
        {
            **request.to_dict(),
            "source_payload": "Different exact content.",
        }
    )
    with pytest.raises(FailClosedRuntimeError, match="identity-content conflict"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=conflicting,
            governed_runtime_runner=_fail_runner,
        )
    assert calls == 1


def test_delivery_resolution_reports_not_found_and_committed_response(
    tmp_path: Path,
) -> None:
    not_found_query = _resolution_request(
        tmp_path,
        90,
        target_request_identity="G69-05-ABSENT-REQUEST",
        target_idempotency_identity="G69-05-ABSENT-IDEMPOTENCY",
        target_source_act_digest="sha256:" + "0" * 64,
        target_interaction_identity="NOT_APPLICABLE",
    )
    not_found = che_service.run_human_interface_runtime_entry(
        request_envelope=not_found_query,
        governed_runtime_runner=_fail_runner,
    )
    assert not_found.owner_transition.delivery_resolution_status == DELIVERY_NOT_FOUND

    request, committed = _initial(tmp_path / "committed")
    continuation = committed.continuation_envelope
    assert continuation is not None
    committed_query = _resolution_request(
        tmp_path / "committed",
        91,
        target_request_identity=request.request_identity,
        target_idempotency_identity=request.idempotency_identity,
        target_source_act_digest=canonical_che_request_source_act_digest_v1(request),
        target_interaction_identity=continuation.interaction_identity,
    )
    found = che_service.run_human_interface_runtime_entry(
        request_envelope=committed_query,
        governed_runtime_runner=_fail_runner,
    )
    transition = found.owner_transition
    assert transition.delivery_resolution_status == (
        DELIVERY_COMMITTED_RESPONSE_FOUND
    )
    assert transition.resolved_response_identity == committed.response_identity
    assert transition.resolved_response_hash


def test_post_owner_commit_failure_remains_explicitly_unknown_without_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0
    original_owner = che_service._run_human_interface_runtime_entry_owner_execution_v1
    original_commit = che_service._commit_canonical_che_delivery_response_v1

    def counted_owner(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original_owner(*args, **kwargs)

    def fail_commit(*_args, **_kwargs):
        raise FailClosedRuntimeError("simulated acknowledgement boundary failure")

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        counted_owner,
    )
    monkeypatch.setattr(
        che_service, "_commit_canonical_che_delivery_response_v1", fail_commit
    )
    request = _request(
        tmp_path, 1, source_act_identity="G69-05-SOURCE-ACT-UNKNOWN"
    )
    with pytest.raises(FailClosedRuntimeError, match="acknowledgement"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=request,
            governed_runtime_runner=_fail_runner,
        )
    assert calls == 1

    monkeypatch.setattr(
        che_service,
        "_commit_canonical_che_delivery_response_v1",
        original_commit,
    )
    query_request = _resolution_request(
        tmp_path,
        92,
        target_request_identity=request.request_identity,
        target_idempotency_identity=request.idempotency_identity,
        target_source_act_digest=canonical_che_request_source_act_digest_v1(request),
        target_interaction_identity="NOT_APPLICABLE",
    )
    resolution = che_service.run_human_interface_runtime_entry(
        request_envelope=query_request,
        governed_runtime_runner=_fail_runner,
    )
    transition = resolution.owner_transition
    assert transition.delivery_resolution_status == DELIVERY_OUTCOME_UNKNOWN
    assert transition.retryability == NOT_RETRYABLE
    assert transition.recovery_requirement == QUERY_DELIVERY_STATUS
    assert calls == 1


def test_stale_owner_revision_fails_before_canonical_owner_advancement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, initial = _initial(tmp_path)
    continuation = initial.continuation_envelope
    assert continuation is not None

    legacy = che_service.run_human_interface_runtime_entry(
        interface_name="G69-05-LEGACY-COMPATIBILITY",
        session_id="G69-05-SESSION",
        human_requests=["action: implement"],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=REPOSITORY_ROOT,
        governed_runtime_runner=_fail_runner,
    )
    assert legacy["production_conversation_binding"]["conversation_state"][
        "revision"
    ] > (
        continuation.expected_owner_revision
    )

    calls = 0
    original = che_service._run_human_interface_runtime_entry_owner_execution_v1

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        counted,
    )
    stale_request = _request(
        tmp_path,
        3,
        source_act_identity=continuation.expected_next_act_identity,
        payload="action: implement",
    )
    with pytest.raises(FailClosedRuntimeError, match="owner revision is stale"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=stale_request,
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )
    assert calls == 0

    query_request = _resolution_request(
        tmp_path,
        93,
        target_request_identity=stale_request.request_identity,
        target_idempotency_identity=stale_request.idempotency_identity,
        target_source_act_digest=canonical_che_request_source_act_digest_v1(
            stale_request
        ),
        target_interaction_identity=continuation.interaction_identity,
    )
    resolution = che_service.run_human_interface_runtime_entry(
        request_envelope=query_request,
        governed_runtime_runner=_fail_runner,
    )
    transition = resolution.owner_transition
    assert transition.delivery_resolution_status == DELIVERY_ENTERED_NOT_ADVANCED
    assert transition.retryability == NOT_RETRYABLE
    assert transition.recovery_requirement == MANUAL_REVIEW_REQUIRED
    assert calls == 0


def test_unknown_owner_shape_fails_closed_and_is_not_reinvoked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def malformed(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return {"conversation_identity": "UNSUPPORTED-OWNER"}

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        malformed,
    )
    request = _request(
        tmp_path, 1, source_act_identity="G69-05-SOURCE-ACT-MALFORMED"
    )
    with pytest.raises(FailClosedRuntimeError, match="supported Conversation"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=request,
            governed_runtime_runner=_fail_runner,
        )
    resolution = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert resolution.owner_transition.delivery_resolution_status == (
        DELIVERY_OUTCOME_UNKNOWN
    )
    assert calls == 1


def test_delivery_record_is_atomic_integrity_bound_and_tamper_evident(
    tmp_path: Path,
) -> None:
    request, _ = _initial(tmp_path)
    store = tmp_path / "runtime" / "canonical_human_entry_delivery_resolution_v1"
    records = sorted(store.glob("record-*.json"))
    assert len(records) == 1
    assert not list(store.glob("*.tmp"))
    record = json.loads(records[0].read_text(encoding="utf-8"))
    record["owner_revision_after"] = 999
    records[0].write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="integrity"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=request,
            governed_runtime_runner=_fail_runner,
        )


def test_one_che_entry_and_production_path_count_remain_one() -> None:
    source = Path(inspect.getsourcefile(che_service.run_human_interface_runtime_entry) or "").read_text(
        encoding="utf-8"
    )
    assert source.count("def run_human_interface_runtime_entry(") == 1
    assert "def resolve_canonical_human_entry" not in source
    assert "compose_production_conversation_flow_binding_v1(" in source
    assert "canonical_che_delivery_resolution_query_from_request_v1(" in source
