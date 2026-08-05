"""Focused G69-08 channel-neutral opaque Reference contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    HUMAN_ACTOR,
    NOT_APPLICABLE,
    NOT_ADVANCED,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
)
from aigol.runtime.canonical_opaque_reference_contract_v1 import (
    ARTIFACT,
    AUDIO,
    AVAILABLE,
    CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
    CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
    CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
    CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
    DATASET,
    DOCUMENT,
    EXPIRED,
    EXTERNAL_RESOURCE,
    IMAGE,
    INACCESSIBLE,
    INTEGRITY_MISMATCH,
    MISSING,
    NOT_AVAILABLE,
    NOT_RETRYABLE,
    OBTAIN_VALIDATION,
    OTHER_DECLARED_REFERENCE,
    PENDING_VALIDATION,
    PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
    PROVIDE_AVAILABLE_REFERENCE,
    PROVIDE_CURRENT_REFERENCE,
    PROVIDE_INTEGRITY_MATCHING_REFERENCE,
    REQUEST_NEW_REFERENCE,
    RESTORE_ACCESS,
    RETRYABLE,
    REVOKED,
    SHA256,
    STRUCTURED_DATA,
    VIDEO,
    CanonicalOpaqueReferenceSetV1,
    CanonicalOpaqueReferenceV1,
    canonical_opaque_reference_set_from_request_v1,
    canonical_ordered_reference_set_digest_v1,
    canonical_reference_validation_evidence_digest_v1,
    deserialize_canonical_opaque_reference_set_v1,
    deserialize_canonical_opaque_reference_v1,
    serialize_canonical_opaque_reference_set_v1,
    serialize_canonical_opaque_reference_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-04T20:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_CORRECTION = {
    AVAILABLE: NOT_APPLICABLE,
    MISSING: PROVIDE_AVAILABLE_REFERENCE,
    INACCESSIBLE: RESTORE_ACCESS,
    EXPIRED: PROVIDE_CURRENT_REFERENCE,
    REVOKED: REQUEST_NEW_REFERENCE,
    PENDING_VALIDATION: OBTAIN_VALIDATION,
    INTEGRITY_MISMATCH: PROVIDE_INTEGRITY_MATCHING_REFERENCE,
}
_RETRY = {
    AVAILABLE: NOT_APPLICABLE,
    MISSING: RETRYABLE,
    INACCESSIBLE: RETRYABLE,
    EXPIRED: RETRYABLE,
    REVOKED: NOT_RETRYABLE,
    PENDING_VALIDATION: RETRYABLE,
    INTEGRITY_MISMATCH: RETRYABLE,
}


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _reference(
    number: int,
    *,
    position: int = 1,
    status: str = AVAILABLE,
    kind: str = DOCUMENT,
    modality: str = "TEXT",
    channel: str = "G69-08-CLI",
    reference_identity: str | None = None,
    validation_owner: str = PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
    content_owner: str = "G69-08-CONTENT-OWNER",
    custody_owner: str = "G69-08-CUSTODY-OWNER",
) -> CanonicalOpaqueReferenceV1:
    identity = reference_identity or f"G69-08-REFERENCE-{number:06d}"
    evidence = f"G69-08-VALIDATION-EVIDENCE-{number:06d}"
    algorithm = PENDING_VALIDATION if status == PENDING_VALIDATION else SHA256
    integrity = (
        PENDING_VALIDATION
        if algorithm == PENDING_VALIDATION
        else replay_hash({"reference_identity": identity})
    )
    retryability = _RETRY[status]
    correction = _CORRECTION[status]
    evidence_digest = canonical_reference_validation_evidence_digest_v1(
        reference_identity=identity,
        validation_owner_identity=validation_owner,
        custody_owner_identity=custody_owner,
        availability_status=status,
        integrity_algorithm=algorithm,
        integrity_reference=integrity,
        access_scope_identity="G69-08-ACCESS-SCOPE",
        validation_evidence_identity=evidence,
        retryability=retryability,
        correction_requirement=correction,
    )
    return CanonicalOpaqueReferenceV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
        reference_identity=identity,
        reference_kind=kind,
        modality=modality,
        ordered_position=position,
        provenance_identity=f"G69-08-PROVENANCE-{number:06d}",
        content_owner_identity=content_owner,
        custody_owner_identity=custody_owner,
        validation_owner_identity=validation_owner,
        integrity_algorithm=algorithm,
        integrity_reference=integrity,
        availability_status=status,
        access_scope_identity="G69-08-ACCESS-SCOPE",
        source_channel_identity=channel,
        source_actor_identity="G69-08-HUMAN",
        validation_evidence_identity=evidence,
        validation_evidence_digest=evidence_digest,
        retryability=retryability,
        correction_requirement=correction,
        created_at=CREATED_AT,
        metadata={},
    )


def _request_with_references(
    root: Path,
    number: int,
    references: tuple[CanonicalOpaqueReferenceV1, ...],
    *,
    channel: str = "G69-08-CLI",
    source_payload: object = "Review the supplied material.",
    interaction_identity: str = NOT_APPLICABLE,
    retry_of: tuple[str, str, str] | None = None,
    idempotency_identity: str | None = None,
) -> tuple[CanonicalHumanEntryRequestEnvelopeV1, CanonicalOpaqueReferenceSetV1]:
    request_identity = f"G69-08-REQUEST-{number:06d}"
    source_act_identity = f"G69-08-SOURCE-ACT-{number:06d}"
    order_identity = f"G69-08-ORDER-{number:06d}"
    digest = canonical_ordered_reference_set_digest_v1(references)
    retry_source, retry_order, retry_digest = retry_of or (None, None, None)
    reference_set = CanonicalOpaqueReferenceSetV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
        reference_set_identity="OPAQUE-REFERENCE-SET-" + digest,
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        interaction_identity=interaction_identity,
        session_identity="G69-08-SESSION",
        actor_identity="G69-08-HUMAN",
        workspace_identity=str(REPOSITORY_ROOT),
        ordered_reference_set_digest=digest,
        retry_of_source_act_identity=retry_source,
        retry_of_order_identity=retry_order,
        retry_of_reference_set_digest=retry_digest,
        references=references,
        metadata={},
    )
    request = CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=channel,
        adapter_identity=channel + "-ADAPTER",
        actor_identity="G69-08-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-08-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(root / "runtime"),
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        idempotency_identity=(
            idempotency_identity or f"G69-08-IDEMPOTENCY-{number:06d}"
        ),
        source_payload={
            "contract_version": CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
            "source_payload": source_payload,
            "reference_set": reference_set.to_dict(),
        },
        source_encoding="UTF-8",
        source_modality="MULTIMODAL",
        declared_capabilities=(
            CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
            "TEXT_INPUT",
        ),
        metadata={"transport_trace_identity": f"G69-08-TRACE-{number:06d}"},
        created_at=CREATED_AT,
    )
    return request, reference_set


def _ordinary_request(root: Path) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G69-08-CLI",
        adapter_identity="G69-08-CLI-ADAPTER",
        actor_identity="G69-08-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-08-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(root / "runtime"),
        request_identity="G69-08-INITIAL-REQUEST",
        source_act_identity="G69-08-INITIAL-SOURCE-ACT",
        order_identity="G69-08-INITIAL-ORDER",
        idempotency_identity="G69-08-INITIAL-IDEMPOTENCY",
        source_payload="Implement a bounded validator.",
        source_encoding="UTF-8",
        source_modality="TEXT",
        declared_capabilities=("TEXT_INPUT",),
        metadata={"transport_trace_identity": "G69-08-INITIAL-TRACE"},
        created_at=CREATED_AT,
    )


def test_available_document_reference_enters_che_and_preserves_projection(
    tmp_path: Path,
) -> None:
    request, reference_set = _request_with_references(
        tmp_path, 1, (_reference(1),)
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    projection = response.presentation_metadata["opaque_reference_validation"]
    assert projection["reference_set_identity"] == reference_set.reference_set_identity
    assert projection["availability_statuses"] == (AVAILABLE,)
    assert response.producing_owner != request.interface_identity


def test_multi_reference_order_is_exact_and_not_reordered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    references = (
        _reference(1, position=1, status=MISSING),
        _reference(2, position=2, status=INACCESSIBLE),
        _reference(3, position=3, status=EXPIRED),
    )
    request, _ = _request_with_references(tmp_path, 2, references)
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: pytest.fail("semantic owner was entered"),
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    projection = response.presentation_metadata["opaque_reference_validation"]
    assert projection["ordered_reference_identities"] == tuple(
        reference.reference_identity for reference in references
    )
    assert projection["ordered_positions"] == (1, 2, 3)


def test_duplicate_missing_and_reordered_positions_fail_closed() -> None:
    first = _reference(1, position=1)
    duplicate_position = _reference(2, position=1)
    missing_position = _reference(2, position=3)
    for references in ((first, duplicate_position), (first, missing_position)):
        digest = canonical_ordered_reference_set_digest_v1(references)
        with pytest.raises(FailClosedRuntimeError, match="ordering"):
            CanonicalOpaqueReferenceSetV1(
                contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
                reference_set_identity="OPAQUE-REFERENCE-SET-" + digest,
                request_identity="REQUEST",
                source_act_identity="SOURCE",
                order_identity="ORDER",
                interaction_identity=NOT_APPLICABLE,
                session_identity="SESSION",
                actor_identity="G69-08-HUMAN",
                workspace_identity=str(REPOSITORY_ROOT),
                ordered_reference_set_digest=digest,
                retry_of_source_act_identity=None,
                retry_of_order_identity=None,
                retry_of_reference_set_digest=None,
                references=references,
                metadata={},
            )
    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        replace(
            _request_with_references(
                Path("/tmp"), 90, (first, _reference(2, position=2))
            )[1],
            references=(_reference(2, position=2), first),
        )
    duplicate_identity = _reference(
        2,
        position=2,
        reference_identity=first.reference_identity,
    )
    duplicate_digest = canonical_ordered_reference_set_digest_v1(
        (first, duplicate_identity)
    )
    with pytest.raises(FailClosedRuntimeError, match="identities conflict"):
        CanonicalOpaqueReferenceSetV1(
            contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
            reference_set_identity="OPAQUE-REFERENCE-SET-" + duplicate_digest,
            request_identity="REQUEST-DUPLICATE",
            source_act_identity="SOURCE-DUPLICATE",
            order_identity="ORDER-DUPLICATE",
            interaction_identity=NOT_APPLICABLE,
            session_identity="SESSION-DUPLICATE",
            actor_identity="G69-08-HUMAN",
            workspace_identity=str(REPOSITORY_ROOT),
            ordered_reference_set_digest=duplicate_digest,
            retry_of_source_act_identity=None,
            retry_of_order_identity=None,
            retry_of_reference_set_digest=None,
            references=(first, duplicate_identity),
            metadata={},
        )


@pytest.mark.parametrize(
    "status",
    [MISSING, INACCESSIBLE, EXPIRED, REVOKED, PENDING_VALIDATION, INTEGRITY_MISMATCH],
)
def test_every_non_available_status_rejects_before_semantic_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    request, _ = _request_with_references(
        tmp_path, 10, (_reference(10, status=status),)
    )
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: pytest.fail("semantic owner was entered"),
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    assert response.advancement_state == NOT_ADVANCED
    assert response.owner_status == "OPAQUE_REFERENCE_" + status
    assert response.continuation_envelope is None


def test_rejection_preserves_active_continuation_without_consumption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initial = che_service.run_human_interface_runtime_entry(
        request_envelope=_ordinary_request(tmp_path),
        governed_runtime_runner=_fail_runner,
    )
    continuation = initial.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    request, _ = _request_with_references(
        tmp_path,
        11,
        (_reference(11, status=MISSING),),
        interaction_identity=continuation.interaction_identity,
    )
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: pytest.fail("semantic owner was entered"),
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )
    assert response.continuation_envelope == continuation
    resolved = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )
    assert resolved.to_dict() == response.to_dict()


def test_corrected_retry_requires_new_bound_lineage(tmp_path: Path) -> None:
    failed_request, failed_set = _request_with_references(
        tmp_path, 20, (_reference(20, status=MISSING),)
    )
    failed = che_service.run_human_interface_runtime_entry(
        request_envelope=failed_request, governed_runtime_runner=_fail_runner
    )
    assert failed.advancement_state == NOT_ADVANCED

    repeated_request, _ = _request_with_references(
        tmp_path, 21, (_reference(20, status=MISSING),)
    )
    with pytest.raises(FailClosedRuntimeError, match="retry lineage"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=repeated_request,
            governed_runtime_runner=_fail_runner,
        )

    retry = (
        failed_set.source_act_identity,
        failed_set.order_identity,
        failed_set.ordered_reference_set_digest,
    )
    corrected_request, corrected_set = _request_with_references(
        tmp_path, 22, (_reference(22, status=AVAILABLE),), retry_of=retry
    )
    corrected = che_service.run_human_interface_runtime_entry(
        request_envelope=corrected_request, governed_runtime_runner=_fail_runner
    )
    projection = corrected.presentation_metadata["opaque_reference_validation"]
    assert projection["retry_of_reference_set_digest"] == (
        failed_set.ordered_reference_set_digest
    )
    assert corrected_set.source_act_identity != failed_set.source_act_identity


@pytest.mark.parametrize(
    ("kind", "modality"),
    [
        (DOCUMENT, "TEXT"),
        (ARTIFACT, "STRUCTURED"),
        (DATASET, "TRANSPORT_COLLECTION"),
        (IMAGE, "VISUAL"),
        (AUDIO, "AUDIO"),
        (VIDEO, "MULTIMODAL"),
        (STRUCTURED_DATA, "STRUCTURED"),
        (EXTERNAL_RESOURCE, "AGENT_MESSAGE"),
        (OTHER_DECLARED_REFERENCE, "AGENT_MESSAGE"),
    ],
)
def test_reference_modalities_reuse_closed_che_vocabulary(
    kind: str, modality: str
) -> None:
    assert _reference(30, kind=kind, modality=modality).modality == modality


def test_contract_is_immutable_serializable_and_contains_no_raw_path() -> None:
    reference = _reference(40)
    reference_set_digest = canonical_ordered_reference_set_digest_v1((reference,))
    reference_set = CanonicalOpaqueReferenceSetV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
        reference_set_identity="OPAQUE-REFERENCE-SET-" + reference_set_digest,
        request_identity="REQUEST-40",
        source_act_identity="SOURCE-40",
        order_identity="ORDER-40",
        interaction_identity=NOT_APPLICABLE,
        session_identity="SESSION-40",
        actor_identity="G69-08-HUMAN",
        workspace_identity=str(REPOSITORY_ROOT),
        ordered_reference_set_digest=reference_set_digest,
        retry_of_source_act_identity=None,
        retry_of_order_identity=None,
        retry_of_reference_set_digest=None,
        references=(reference,),
        metadata={},
    )
    assert deserialize_canonical_opaque_reference_v1(
        serialize_canonical_opaque_reference_v1(reference)
    ) == reference
    assert deserialize_canonical_opaque_reference_set_v1(
        serialize_canonical_opaque_reference_set_v1(reference_set)
    ) == reference_set
    assert "/tmp/" not in serialize_canonical_opaque_reference_v1(reference)
    with pytest.raises(FrozenInstanceError):
        reference.reference_kind = ARTIFACT  # type: ignore[misc]
    with pytest.raises(FailClosedRuntimeError, match="local path"):
        replace(reference, provenance_identity="/tmp/private-upload")


def test_source_channel_cannot_become_owner_and_reference_grants_no_authority(
    tmp_path: Path,
) -> None:
    with pytest.raises(FailClosedRuntimeError, match="source channel"):
        _reference(50, content_owner="G69-08-CLI")
    with pytest.raises(FailClosedRuntimeError, match="source channel"):
        _reference(
            50,
            channel=PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
        )
    request, _ = _request_with_references(tmp_path, 50, (_reference(51),))
    authority_value = request.to_dict()
    authority_value["declared_capabilities"] = [
        CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
        "HUMAN_AUTHORITY_ACT",
    ]
    with pytest.raises(FailClosedRuntimeError, match="cannot transport Human Authority"):
        canonical_opaque_reference_set_from_request_v1(
            CanonicalHumanEntryRequestEnvelopeV1.from_dict(authority_value), None
        )
    undeclared_value = request.to_dict()
    undeclared_value["declared_capabilities"] = ["TEXT_INPUT"]
    with pytest.raises(FailClosedRuntimeError, match="capability is absent"):
        canonical_opaque_reference_set_from_request_v1(
            CanonicalHumanEntryRequestEnvelopeV1.from_dict(undeclared_value), None
        )


def test_unknown_validation_owner_and_tampered_evidence_fail_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unknown"):
        _reference(60, validation_owner="UNKNOWN-VALIDATION-OWNER")
    reference = _reference(61)
    with pytest.raises(FailClosedRuntimeError, match="kind"):
        replace(reference, reference_kind="UNDECLARED_KIND")
    with pytest.raises(FailClosedRuntimeError, match="availability"):
        replace(reference, availability_status="UNKNOWN_AVAILABILITY")
    with pytest.raises(FailClosedRuntimeError, match="evidence integrity"):
        replace(reference, validation_evidence_digest="sha256:" + "0" * 64)
    with pytest.raises(FailClosedRuntimeError, match="local path"):
        replace(
            reference,
            metadata={"transport_trace_values": ["/tmp/channel-upload"]},
        )
    with pytest.raises(FailClosedRuntimeError, match="transport facts only"):
        replace(reference, metadata={"transport_command": "OWNER-COMMAND"})


def test_duplicate_delivery_is_idempotent_and_conflict_fails_closed(
    tmp_path: Path,
) -> None:
    request, _ = _request_with_references(
        tmp_path, 70, (_reference(70, status=MISSING),)
    )
    first = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    second = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    assert first.to_dict() == second.to_dict()
    conflict_request, _ = _request_with_references(
        tmp_path,
        71,
        (_reference(71, status=MISSING),),
        idempotency_identity=request.idempotency_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="idempotency"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=conflict_request, governed_runtime_runner=_fail_runner
        )


def test_two_hics_use_one_contract_and_one_che_path(tmp_path: Path) -> None:
    for number, channel in ((80, "G69-08-CLI"), (81, "G69-08-GUI")):
        request, reference_set = _request_with_references(
            tmp_path,
            number,
            (_reference(number, status=MISSING, channel=channel),),
            channel=channel,
        )
        bound = canonical_opaque_reference_set_from_request_v1(request, None)
        assert isinstance(bound, CanonicalOpaqueReferenceSetV1)
        response = che_service.run_human_interface_runtime_entry(
            request_envelope=request, governed_runtime_runner=_fail_runner
        )
        assert response.request_identity == reference_set.request_identity
        assert response.advancement_state == NOT_ADVANCED


def test_not_available_integrity_is_explicit_not_an_implicit_hash() -> None:
    reference = _reference(90)
    digest = canonical_reference_validation_evidence_digest_v1(
        reference_identity=reference.reference_identity,
        validation_owner_identity=reference.validation_owner_identity,
        custody_owner_identity=reference.custody_owner_identity,
        availability_status=reference.availability_status,
        integrity_algorithm=NOT_AVAILABLE,
        integrity_reference=NOT_AVAILABLE,
        access_scope_identity=reference.access_scope_identity,
        validation_evidence_identity=reference.validation_evidence_identity,
        retryability=reference.retryability,
        correction_requirement=reference.correction_requirement,
    )
    explicit = replace(
        reference,
        integrity_algorithm=NOT_AVAILABLE,
        integrity_reference=NOT_AVAILABLE,
        validation_evidence_digest=digest,
    )
    assert explicit.integrity_reference == NOT_AVAILABLE
