"""Focused G69-02 Canonical Human Entry contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path

import pytest

from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    HUMAN_ACTOR,
    OWNER_RESPONSE,
    UNKNOWN_ADVANCEMENT,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    deserialize_canonical_che_request_envelope_v1,
    deserialize_canonical_che_response_envelope_v1,
    serialize_canonical_che_request_envelope_v1,
    serialize_canonical_che_response_envelope_v1,
    validate_canonical_che_request_envelope_v1,
    validate_canonical_che_response_envelope_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-08-04T14:00:00Z"


def _request(tmp_path: Path, *, payload="  Implement a validator.\n"):
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G69-02-TEST-INTERFACE",
        adapter_identity="G69-02-TEST-ADAPTER",
        actor_identity="G69-02-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-02-SESSION",
        workspace_identity=str(tmp_path / "workspace"),
        runtime_scope_identity=str(tmp_path / "runtime"),
        request_identity="G69-02-REQUEST-000001",
        source_act_identity="G69-02-SOURCE-ACT-000001",
        order_identity="G69-02-ORDER-000001",
        idempotency_identity="G69-02-IDEMPOTENCY-000001",
        source_payload=payload,
        source_encoding="UTF-8",
        source_modality="TEXT",
        declared_capabilities=("TEXT_INPUT", "TEXT_PRESENTATION"),
        metadata={"transport_trace_identity": "G69-02-TRACE-000001"},
        created_at=CREATED_AT,
    )


def _response() -> CanonicalHumanEntryResponseEnvelopeV1:
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity="G69-02-RESPONSE-000001",
        request_identity="G69-02-REQUEST-000001",
        response_type=OWNER_RESPONSE,
        producing_owner="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        owner_status="OWNER_RESPONSE_AVAILABLE",
        advancement_state=UNKNOWN_ADVANCEMENT,
        presentation_payload=("Owner response available.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
        },
        correlation_identity="G69-02-CORRELATION-000001",
        evidence_references=("sha256:" + "1" * 64,),
        replay_references=("/replay/G69-02",),
        certification_references=("/certification/G69-02",),
    )


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def test_request_envelope_is_deeply_immutable_and_preserves_exact_payload(
    tmp_path: Path,
) -> None:
    envelope = _request(
        tmp_path,
        payload={"exact_text": "  first\nsecond  ", "segments": ["a", "b"]},
    )

    assert envelope.to_dict()["source_payload"] == {
        "exact_text": "  first\nsecond  ",
        "segments": ["a", "b"],
    }
    with pytest.raises(FrozenInstanceError):
        envelope.request_identity = "CHANGED"  # type: ignore[misc]
    with pytest.raises(TypeError):
        envelope.metadata["transport_trace_identity"] = "CHANGED"  # type: ignore[index]
    with pytest.raises(TypeError):
        envelope.source_payload["exact_text"] = "CHANGED"  # type: ignore[index]


def test_request_validation_rejects_workflow_metadata_and_unknown_fields(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path).to_dict()
    request["metadata"] = {"conversation_state": "FORBIDDEN"}
    with pytest.raises(FailClosedRuntimeError):
        CanonicalHumanEntryRequestEnvelopeV1.from_dict(request)

    request = _request(tmp_path).to_dict()
    request["declared_capabilities"] = ["WORKER_EXECUTION"]
    with pytest.raises(FailClosedRuntimeError):
        CanonicalHumanEntryRequestEnvelopeV1.from_dict(request)

    request = _request(tmp_path).to_dict()
    request["source_modality"] = "WORKFLOW"
    with pytest.raises(FailClosedRuntimeError):
        CanonicalHumanEntryRequestEnvelopeV1.from_dict(request)

    request = _request(tmp_path).to_dict()
    request["workflow"] = "FORBIDDEN"
    with pytest.raises(FailClosedRuntimeError):
        CanonicalHumanEntryRequestEnvelopeV1.from_dict(request)


def test_request_serialization_is_deterministic_and_round_trips(tmp_path: Path) -> None:
    request = _request(tmp_path)

    first = serialize_canonical_che_request_envelope_v1(request)
    second = serialize_canonical_che_request_envelope_v1(request)
    reconstructed = deserialize_canonical_che_request_envelope_v1(first)

    assert first == second
    assert reconstructed.to_dict() == request.to_dict()
    assert validate_canonical_che_request_envelope_v1(reconstructed) is reconstructed


def test_response_envelope_is_immutable_deterministic_and_strict() -> None:
    response = _response()

    with pytest.raises(FrozenInstanceError):
        response.owner_status = "CHANGED"  # type: ignore[misc]
    with pytest.raises(TypeError):
        response.presentation_metadata["language"] = "en"  # type: ignore[index]
    serialized = serialize_canonical_che_response_envelope_v1(response)
    assert serialized == serialize_canonical_che_response_envelope_v1(response)
    reconstructed = deserialize_canonical_che_response_envelope_v1(serialized)
    assert reconstructed.to_dict() == response.to_dict()
    assert validate_canonical_che_response_envelope_v1(reconstructed) is reconstructed

    malformed = response.to_dict()
    malformed["owner_internal_state"] = {}
    with pytest.raises(FailClosedRuntimeError):
        CanonicalHumanEntryResponseEnvelopeV1.from_dict(malformed)


def test_che_accepts_only_request_envelope_mode_and_returns_only_response_envelope(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    response = run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )

    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    assert response.request_identity == request.request_identity
    assert response.contract_version == CANONICAL_CHE_RESPONSE_CONTRACT_VERSION
    assert response.response_type == OWNER_RESPONSE
    assert response.producing_owner == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    assert response.correlation_identity.startswith("CHE-CORRELATION-")
    serialized = serialize_canonical_che_response_envelope_v1(response)
    for forbidden in (
        "production_conversation_bindings",
        "platform_core_project_services_context",
        "g31_application_state",
        "canonical_typed_semantic_composition",
    ):
        assert forbidden not in serialized


def test_che_request_envelope_cannot_be_mixed_with_legacy_or_workflow_inputs(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    with pytest.raises(FailClosedRuntimeError):
        run_human_interface_runtime_entry(
            request_envelope=request,
            interface_name="LEGACY-INTERFACE",
            governed_runtime_runner=_fail_runner,
        )
    with pytest.raises(FailClosedRuntimeError):
        run_human_interface_runtime_entry(
            request_envelope=request,
            g31_human_action="APPROVE",
            governed_runtime_runner=_fail_runner,
        )


def test_legacy_che_callers_receive_the_existing_dictionary_projection(
    tmp_path: Path,
) -> None:
    result = run_human_interface_runtime_entry(
        interface_name="G69-02-LEGACY-INTERFACE",
        session_id="G69-02-LEGACY-SESSION",
        human_requests=["Implement a validator."],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path / "workspace",
        governed_runtime_runner=_fail_runner,
    )

    assert isinstance(result, dict)
    assert result["canonical_runtime_entry_interface"] == "G69-02-LEGACY-INTERFACE"
    assert result["canonical_runtime_entry_session_id"] == "G69-02-LEGACY-SESSION"
    assert "production_conversation_binding" in result


def test_one_che_entry_and_owner_boundaries_remain_visible() -> None:
    signature = inspect.signature(run_human_interface_runtime_entry)
    public_source = inspect.getsource(run_human_interface_runtime_entry)
    module_source = Path(
        inspect.getsourcefile(run_human_interface_runtime_entry) or ""
    ).read_text(encoding="utf-8")

    assert list(signature.parameters)[-1] == "request_envelope"
    assert "compose_production_conversation_flow_binding_v1(" in module_source
    assert "conversation_result = governed_runtime_runner(" in module_source
    assert "request_envelope" in public_source
