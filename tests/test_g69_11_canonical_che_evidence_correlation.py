"""Focused G69-11 CHE source and decision evidence correlation tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    DELIVERY_OUTCOME_UNKNOWN,
    NOT_APPLICABLE,
    RECORDED,
    UNAVAILABLE_PRE_WRITE,
    canonical_che_evidence_correlation_record_path_v1,
    deserialize_canonical_che_evidence_correlation_v1,
    observe_canonical_che_evidence_for_cro_v1,
    read_canonical_che_evidence_correlation_v1,
    reconstruct_canonical_che_evidence_record_v1,
    serialize_canonical_che_evidence_correlation_v1,
    unavailable_pre_write_canonical_che_evidence_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
)
from aigol.runtime.canonical_opaque_reference_contract_v1 import (
    AVAILABLE,
    CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
    CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
    CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
    CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
    DOCUMENT,
    MISSING,
    NOT_APPLICABLE as REFERENCE_NOT_APPLICABLE,
    PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
    PROVIDE_AVAILABLE_REFERENCE,
    RETRYABLE,
    SHA256,
    CanonicalOpaqueReferenceSetV1,
    CanonicalOpaqueReferenceV1,
    canonical_ordered_reference_set_digest_v1,
    canonical_reference_validation_evidence_digest_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-08-05T18:00:00Z"


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _request(
    root: Path,
    number: int,
    *,
    interface: str = "G69-11-CLI",
    source_act: str | None = None,
    payload: object = "Implement a bounded validator.",
    modality: str = "TEXT",
    capabilities: tuple[str, ...] = ("TEXT_INPUT",),
    idempotency: str | None = None,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=interface,
        adapter_identity=interface + "-ADAPTER",
        actor_identity="G69-11-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-11-SESSION",
        workspace_identity=str(root / "workspace"),
        runtime_scope_identity=str(root / "runtime"),
        request_identity=f"G69-11-REQUEST-{number:06d}",
        source_act_identity=source_act or f"G69-11-SOURCE-{number:06d}",
        order_identity=f"G69-11-ORDER-{number:06d}",
        idempotency_identity=idempotency or f"G69-11-IDEMPOTENCY-{number:06d}",
        source_payload=payload,
        source_encoding="UTF-8",
        source_modality=modality,
        declared_capabilities=capabilities,
        metadata={"transport_trace_identity": f"G69-11-TRACE-{number:06d}"},
        created_at=CREATED_AT,
    )


def _run(root: Path, number: int = 1, **kwargs):
    request = _request(root, number, **kwargs)
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    path = canonical_che_evidence_correlation_record_path_v1(
        request.runtime_scope_identity, response.correlation_identity
    )
    return request, response, read_canonical_che_evidence_correlation_v1(path), path


def _authority_request(
    root: Path, response, number: int = 2
) -> tuple[CanonicalHumanEntryRequestEnvelopeV1, CanonicalHumanAuthorityActV1]:
    continuation = response.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    request_identity = f"G69-11-REQUEST-{number:06d}"
    act_identity = f"G69-11-AUTHORITY-{number:06d}"
    payload = "action: implement"
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=act_identity,
        authority_kind=binding["authority_kind"],
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity=request_identity,
        continuation_identity=continuation.continuation_identity,
        target_identity=binding["target_identity"],
        target_revision=binding["target_revision"],
        producing_owner=binding["producing_owner"],
        expected_owner=binding["expected_owner"],
        authority_scope=binding["authority_scope"],
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={},
    )
    request = _request(
        root,
        number,
        interface="G69-11-GUI",
        source_act=act_identity,
        payload=act.to_dict(),
        modality="STRUCTURED",
        capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
    )
    return request, act


def _reference(number: int, *, status: str = AVAILABLE, position: int = 1):
    identity = f"G69-11-REFERENCE-{number:06d}"
    validation_identity = f"G69-11-REFERENCE-EVIDENCE-{number:06d}"
    integrity = replay_hash({"reference_identity": identity})
    retryability = REFERENCE_NOT_APPLICABLE if status == AVAILABLE else RETRYABLE
    correction = (
        REFERENCE_NOT_APPLICABLE
        if status == AVAILABLE
        else PROVIDE_AVAILABLE_REFERENCE
    )
    digest = canonical_reference_validation_evidence_digest_v1(
        reference_identity=identity,
        validation_owner_identity=PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
        custody_owner_identity="G69-11-CUSTODY",
        availability_status=status,
        integrity_algorithm=SHA256,
        integrity_reference=integrity,
        access_scope_identity="G69-11-ACCESS",
        validation_evidence_identity=validation_identity,
        retryability=retryability,
        correction_requirement=correction,
    )
    return CanonicalOpaqueReferenceV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
        reference_identity=identity,
        reference_kind=DOCUMENT,
        modality="TEXT",
        ordered_position=position,
        provenance_identity=f"G69-11-PROVENANCE-{number:06d}",
        content_owner_identity="G69-11-CONTENT",
        custody_owner_identity="G69-11-CUSTODY",
        validation_owner_identity=PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
        integrity_algorithm=SHA256,
        integrity_reference=integrity,
        availability_status=status,
        access_scope_identity="G69-11-ACCESS",
        source_channel_identity="G69-11-CLI",
        source_actor_identity="G69-11-HUMAN",
        validation_evidence_identity=validation_identity,
        validation_evidence_digest=digest,
        retryability=retryability,
        correction_requirement=correction,
        created_at=CREATED_AT,
        metadata={},
    )


def _reference_request(root: Path, number: int, references):
    request_identity = f"G69-11-REQUEST-{number:06d}"
    source_identity = f"G69-11-SOURCE-{number:06d}"
    order_identity = f"G69-11-ORDER-{number:06d}"
    ordered_digest = canonical_ordered_reference_set_digest_v1(references)
    reference_set = CanonicalOpaqueReferenceSetV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
        reference_set_identity="OPAQUE-REFERENCE-SET-" + ordered_digest,
        request_identity=request_identity,
        source_act_identity=source_identity,
        order_identity=order_identity,
        interaction_identity=NOT_APPLICABLE,
        session_identity="G69-11-SESSION",
        actor_identity="G69-11-HUMAN",
        workspace_identity=str(root / "workspace"),
        ordered_reference_set_digest=ordered_digest,
        retry_of_source_act_identity=None,
        retry_of_order_identity=None,
        retry_of_reference_set_digest=None,
        references=tuple(references),
        metadata={},
    )
    request = _request(
        root,
        number,
        source_act=source_identity,
        payload={
            "contract_version": CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
            "source_payload": "Review the exact References.",
            "reference_set": reference_set.to_dict(),
        },
        modality="MULTIMODAL",
        capabilities=(CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY, "TEXT_INPUT"),
    )
    return request, reference_set


def test_initial_request_has_one_deterministic_immutable_correlation(tmp_path: Path):
    request, response, correlation, path = _run(tmp_path)
    assert correlation.evidence_status == RECORDED
    assert correlation.request_identity == request.request_identity
    assert correlation.source_act_digest == che_service.canonical_che_request_source_act_digest_v1(request)
    assert response.correlation_identity == correlation.correlation_identity
    assert deserialize_canonical_che_evidence_correlation_v1(
        serialize_canonical_che_evidence_correlation_v1(correlation)
    ).to_dict() == correlation.to_dict()
    assert path.is_file()
    with pytest.raises(FrozenInstanceError):
        correlation.delivery_status = NOT_APPLICABLE  # type: ignore[misc]


def test_continuation_and_authority_act_bind_exact_decision_and_new_turn(tmp_path: Path):
    _, initial, initial_correlation, _ = _run(tmp_path)
    request, act = _authority_request(tmp_path, initial)
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=initial.continuation_envelope,
        governed_runtime_runner=_fail_runner,
    )
    path = canonical_che_evidence_correlation_record_path_v1(
        request.runtime_scope_identity, response.correlation_identity
    )
    correlation = read_canonical_che_evidence_correlation_v1(path)
    assert correlation.interaction_identity == initial_correlation.interaction_identity
    assert correlation.conversation_identity == initial_correlation.conversation_identity
    assert correlation.correlation_identity != initial_correlation.correlation_identity
    assert correlation.authority_act_identity == act.authority_act_identity
    assert correlation.authority_kind == act.authority_kind
    assert correlation.authority_target_identity == act.target_identity
    assert correlation.authority_target_revision == act.target_revision
    assert correlation.authority_payload_digest == act.payload_digest
    assert correlation.owner_revision_before == act.target_revision


def test_ordered_opaque_references_and_owner_outcome_are_exact(tmp_path: Path):
    references = (_reference(1, position=1), _reference(2, position=2))
    request, reference_set = _reference_request(tmp_path, 3, references)
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    path = canonical_che_evidence_correlation_record_path_v1(
        request.runtime_scope_identity, response.correlation_identity
    )
    correlation = read_canonical_che_evidence_correlation_v1(path)
    assert correlation.opaque_reference_set_identity == reference_set.reference_set_identity
    assert correlation.ordered_reference_set_digest == reference_set.ordered_reference_set_digest
    assert [item["reference_identity"] for item in correlation.opaque_reference_correlations] == [item.reference_identity for item in references]
    assert [item["ordered_position"] for item in correlation.opaque_reference_correlations] == [1, 2]
    assert correlation.owner_projection_identity == response.owner_projection.projection_identity
    assert correlation.presentation_identity == response.presentation.presentation_identity


def test_unavailable_reference_records_non_advancement_without_owner(tmp_path: Path, monkeypatch):
    request, _ = _reference_request(tmp_path, 4, (_reference(4, status=MISSING),))
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: pytest.fail("semantic owner was invoked"),
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    path = canonical_che_evidence_correlation_record_path_v1(
        request.runtime_scope_identity, response.correlation_identity
    )
    correlation = read_canonical_che_evidence_correlation_v1(path)
    assert correlation.owner_advancement == "NOT_ADVANCED"
    assert correlation.failure_identity == response.common_failure.failure_identity
    assert correlation.presentation_identity == response.presentation.presentation_identity


def test_exact_duplicate_returns_same_response_and_correlation_without_owner(tmp_path: Path, monkeypatch):
    request, response, correlation, _ = _run(tmp_path)
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: pytest.fail("owner was reinvoked"),
    )
    duplicate = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    assert duplicate.to_dict() == response.to_dict()
    assert duplicate.correlation_identity == correlation.correlation_identity


def test_conflicting_idempotency_content_fails_without_reusing_correlation(tmp_path: Path):
    request, response, _, _ = _run(tmp_path)
    conflict = replace(
        request,
        request_identity="G69-11-CONFLICT-REQUEST",
        source_act_identity="G69-11-CONFLICT-SOURCE",
        source_payload="Conflicting content.",
    )
    with pytest.raises(FailClosedRuntimeError, match="idempotency"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=conflict, governed_runtime_runner=_fail_runner
        )
    records = list(
        (Path(request.runtime_scope_identity) / "canonical_che_evidence_correlations_v1").glob("*.json")
    )
    assert len(records) == 1
    assert response.correlation_identity in records[0].read_text(encoding="utf-8")


def test_stale_revision_records_explicit_pre_owner_evidence(tmp_path: Path):
    _, initial, _, _ = _run(tmp_path)
    continuation = initial.continuation_envelope
    assert continuation is not None
    stale = replace(continuation, expected_owner_revision=continuation.expected_owner_revision + 1)
    request = _request(
        tmp_path,
        5,
        source_act=continuation.expected_next_act_identity,
        payload="action: implement",
    )
    with pytest.raises(FailClosedRuntimeError):
        che_service.run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=stale,
            governed_runtime_runner=_fail_runner,
        )
    delivery = che_service._existing_canonical_che_delivery_record_v1(request)
    assert delivery is not None
    correlation = delivery["evidence_correlation"]
    assert correlation["evidence_status"] == UNAVAILABLE_PRE_WRITE
    assert correlation["response_identity"] == NOT_APPLICABLE
    assert correlation["owner_advancement"] == NOT_APPLICABLE


def test_unknown_owner_projection_records_unknown_without_inference(tmp_path: Path, monkeypatch):
    request = _request(tmp_path, 6)
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: {"unknown_owner_shape": True},
    )
    with pytest.raises(FailClosedRuntimeError, match="supported Conversation projection"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=request, governed_runtime_runner=_fail_runner
        )
    delivery = che_service._existing_canonical_che_delivery_record_v1(request)
    assert delivery["evidence_correlation"]["evidence_status"] == DELIVERY_OUTCOME_UNKNOWN
    assert delivery["evidence_correlation"]["producing_owner_identity"] == NOT_APPLICABLE


def test_terminal_response_correlates_terminal_owner_and_no_active_continuation(
    tmp_path: Path, monkeypatch
):
    request = _request(tmp_path, 7)
    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        lambda **_kwargs: {
            "production_conversation_binding": {
                "conversation_identity": "G69-11-TERMINAL-CONVERSATION",
                "conversation_state": {"revision": 1},
            },
            "platform_core_project_services_context": {
                "human_conversation_experience": {
                    "response_mode": "READ_ONLY_RESULT"
                }
            },
            "governed_read_only_work_result": {
                "artifact_hash": "sha256:" + "a" * 64
            },
        },
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request, governed_runtime_runner=_fail_runner
    )
    assert response.response_type == "TERMINAL"
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.continuation_state == "TERMINAL"
    correlation = read_canonical_che_evidence_correlation_v1(
        canonical_che_evidence_correlation_record_path_v1(
            request.runtime_scope_identity, response.correlation_identity
        )
    )
    assert correlation.terminal_identity == response.owner_transition.terminal_identity
    assert correlation.next_act_identity == NOT_APPLICABLE
    assert correlation.replay_status in {"CREATED", "NOT_CREATED"}
    assert correlation.certification_status in {"CREATED", "NOT_CREATED"}


def test_pre_write_absence_is_explicit_and_never_fabricated():
    result = unavailable_pre_write_canonical_che_evidence_v1()
    assert result["evidence_status"] == UNAVAILABLE_PRE_WRITE
    assert result["correlation_identity"] == "NOT_RECORDED"
    assert result["inference_performed"] is False


def test_replay_and_cro_reconstruct_exactly_without_inference(tmp_path: Path):
    _, _, correlation, path = _run(tmp_path)
    first = reconstruct_canonical_che_evidence_record_v1(path)
    second = reconstruct_canonical_che_evidence_record_v1(path)
    assert canonical_serialize(first) == canonical_serialize(second)
    assert first["correlation_identity"] == correlation.correlation_identity
    assert first["inference_performed"] is False
    assert "authority_act_identity" in first["explicit_gaps"]
    observation = observe_canonical_che_evidence_for_cro_v1(path)
    assert observation["read_only"] is True
    assert observation["post_hoc"] is True
    assert observation["runtime_predecessor"] is False
    assert observation["authoritative"] is False


def test_tampered_correlation_record_fails_closed(tmp_path: Path):
    _, _, _, path = _run(tmp_path)
    value = json.loads(path.read_text(encoding="utf-8"))
    value["correlation"]["owner_revision_after"] = 999
    path.write_text(canonical_serialize(value) + "\n", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="integrity"):
        read_canonical_che_evidence_correlation_v1(path)


def test_two_hics_have_same_closed_structure_without_hic_workflow_fields(tmp_path: Path):
    _, _, first, _ = _run(tmp_path / "one", interface="G69-11-CLI")
    _, _, second, _ = _run(tmp_path / "two", interface="G69-11-GUI")
    assert set(first.to_dict()) == set(second.to_dict())
    assert first.source_channel_identity != second.source_channel_identity
    forbidden = {"workflow", "semantic_meaning", "owner_application_state", "replay_created_by_hic"}
    assert forbidden.isdisjoint(first.to_dict())


def test_one_che_definition_and_one_entry_path_remain():
    source = Path(che_service.__file__).read_text(encoding="utf-8")
    assert source.count("def run_human_interface_runtime_entry(") == 1
    assert "def run_canonical_human_entry" not in source
