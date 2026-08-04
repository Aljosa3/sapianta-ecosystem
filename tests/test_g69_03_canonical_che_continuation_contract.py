"""Focused G69-03 Canonical Human Entry continuation tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    HUMAN_ACTOR,
    TERMINAL_CONTINUATION,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    deserialize_canonical_che_continuation_envelope_v1,
    serialize_canonical_che_continuation_envelope_v1,
    serialize_canonical_che_response_envelope_v1,
    validate_canonical_che_continuation_envelope_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-08-04T15:00:00Z"


def _request(
    root: Path,
    number: int,
    *,
    source_act_identity: str,
    interface_identity: str = "G69-03-CLIA",
    adapter_identity: str = "G69-03-CLIA-ADAPTER",
    actor_identity: str = "G69-03-HUMAN",
    session_identity: str = "G69-03-SESSION",
    workspace_identity: str | None = None,
    runtime_scope_identity: str | None = None,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=interface_identity,
        adapter_identity=adapter_identity,
        actor_identity=actor_identity,
        actor_class=HUMAN_ACTOR,
        session_identity=session_identity,
        workspace_identity=workspace_identity or str(root / "workspace"),
        runtime_scope_identity=runtime_scope_identity or str(root / "runtime"),
        request_identity=f"G69-03-REQUEST-{number:06d}",
        source_act_identity=source_act_identity,
        order_identity=f"G69-03-ORDER-{number:06d}",
        idempotency_identity=f"G69-03-IDEMPOTENCY-{number:06d}",
        source_payload=(
            "Implement a validator."
            if number == 1
            else "action: implement"
        ),
        source_encoding="UTF-8",
        source_modality="TEXT",
        declared_capabilities=("TEXT_INPUT", "TEXT_PRESENTATION"),
        metadata={"transport_trace_identity": f"G69-03-TRACE-{number:06d}"},
        created_at=CREATED_AT,
    )


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _initial(
    root: Path,
) -> tuple[
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    CanonicalContinuationEnvelopeV1,
]:
    request = _request(root, 1, source_act_identity="G69-03-SOURCE-ACT-000001")
    response = run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    continuation = response.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    return request, response, continuation


def _changed(
    continuation: CanonicalContinuationEnvelopeV1,
    **changes,
) -> CanonicalContinuationEnvelopeV1:
    value = continuation.to_dict()
    value.update(changes)
    return CanonicalContinuationEnvelopeV1.from_dict(value)


def test_continuation_is_immutable_strict_and_deterministically_serialized(
    tmp_path: Path,
) -> None:
    _, response, continuation = _initial(tmp_path)

    assert continuation.contract_version == CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION
    assert continuation.continuation_state == ACTIVE_CONTINUATION
    assert continuation.continuation_sequence == 1
    assert continuation.previous_response_identity == response.response_identity
    assert continuation.expected_owner_state_identity == (
        response.owner_transition.owner_state_identity
    )
    assert continuation.expected_owner_revision == (
        response.owner_transition.owner_revision_after
    )
    with pytest.raises(FrozenInstanceError):
        continuation.continuation_sequence = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        continuation.metadata["transport_note"] = "changed"  # type: ignore[index]

    serialized = serialize_canonical_che_continuation_envelope_v1(continuation)
    assert serialized == serialize_canonical_che_continuation_envelope_v1(
        continuation
    )
    reconstructed = deserialize_canonical_che_continuation_envelope_v1(serialized)
    assert reconstructed.to_dict() == continuation.to_dict()
    assert validate_canonical_che_continuation_envelope_v1(reconstructed) is reconstructed

    response_serialized = serialize_canonical_che_response_envelope_v1(response)
    assert json.loads(response_serialized)["continuation_envelope"] == (
        continuation.to_dict()
    )


def test_continuation_contract_rejects_workflow_metadata_unknown_fields_and_sequence(
    tmp_path: Path,
) -> None:
    _, _, continuation = _initial(tmp_path)

    invalid = continuation.to_dict()
    invalid["metadata"] = {"transport_workflow_state": "FORBIDDEN"}
    with pytest.raises(FailClosedRuntimeError):
        CanonicalContinuationEnvelopeV1.from_dict(invalid)

    invalid = continuation.to_dict()
    invalid["owner_state"] = {}
    with pytest.raises(FailClosedRuntimeError):
        CanonicalContinuationEnvelopeV1.from_dict(invalid)

    invalid = continuation.to_dict()
    invalid["continuation_sequence"] = 0
    with pytest.raises(FailClosedRuntimeError, match="positive integer"):
        CanonicalContinuationEnvelopeV1.from_dict(invalid)


def test_che_restores_same_interaction_across_channel_types_without_owner_state(
    tmp_path: Path,
) -> None:
    _, _, continuation = _initial(tmp_path)
    next_request = _request(
        tmp_path,
        2,
        source_act_identity=continuation.expected_next_act_identity,
        interface_identity="G69-03-GUI",
        adapter_identity="G69-03-GUI-ADAPTER",
    )

    response = run_human_interface_runtime_entry(
        request_envelope=next_request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )

    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    resumed = response.continuation_envelope
    assert isinstance(resumed, CanonicalContinuationEnvelopeV1)
    assert resumed.interaction_identity == continuation.interaction_identity
    assert resumed.conversation_identity == continuation.conversation_identity
    assert resumed.continuation_sequence == 2
    assert resumed.request_identity == next_request.request_identity
    assert resumed.continuation_identity != continuation.continuation_identity

    binding_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(
            (tmp_path / "runtime" / "canonical_human_entry_continuations_v1").glob(
                "binding-*.json"
            )
        )
    )
    for forbidden in (
        "g31_application_state",
        "owner_bound_clarification_envelope",
        "semantic_slots",
        "canonical_working_memory",
        "proposal_operations",
        "source_payload",
    ):
        assert forbidden not in binding_text


def test_che_rejects_missing_duplicate_and_stale_continuations(tmp_path: Path) -> None:
    _, _, continuation = _initial(tmp_path)

    missing_request = _request(
        tmp_path,
        2,
        source_act_identity=continuation.expected_next_act_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="continuation is required"):
        run_human_interface_runtime_entry(
            request_envelope=missing_request,
            governed_runtime_runner=_fail_runner,
        )

    valid_request = _request(
        tmp_path,
        3,
        source_act_identity=continuation.expected_next_act_identity,
    )
    committed = run_human_interface_runtime_entry(
        request_envelope=valid_request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )
    duplicate = run_human_interface_runtime_entry(
        request_envelope=valid_request,
        continuation_envelope=continuation,
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(committed, CanonicalHumanEntryResponseEnvelopeV1)
    assert isinstance(duplicate, CanonicalHumanEntryResponseEnvelopeV1)
    assert duplicate.to_dict() == committed.to_dict()

    stale_request = _request(
        tmp_path,
        4,
        source_act_identity=continuation.expected_next_act_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="stale"):
        run_human_interface_runtime_entry(
            request_envelope=stale_request,
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("session_identity", "WRONG-SESSION", "session is mismatched"),
        ("actor_identity", "WRONG-ACTOR", "actor is mismatched"),
        ("interaction_identity", "WRONG-INTERACTION", "interaction is mismatched"),
        ("continuation_sequence", 2, "sequence is non-monotonic"),
        ("previous_response_identity", "WRONG-RESPONSE", "previous response is invalid"),
    ),
)
def test_che_rejects_tampered_continuation_bindings(
    tmp_path: Path,
    field: str,
    value: str | int,
    message: str,
) -> None:
    case_root = tmp_path / field
    _, _, continuation = _initial(case_root)
    request = _request(
        case_root,
        2,
        source_act_identity=continuation.expected_next_act_identity,
    )

    with pytest.raises(FailClosedRuntimeError, match=message):
        run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=_changed(continuation, **{field: value}),
            governed_runtime_runner=_fail_runner,
        )


def test_che_rejects_unknown_terminal_and_invalid_next_act_continuations(
    tmp_path: Path,
) -> None:
    _, _, continuation = _initial(tmp_path)
    request = _request(
        tmp_path,
        2,
        source_act_identity=continuation.expected_next_act_identity,
    )

    with pytest.raises(FailClosedRuntimeError, match="unknown"):
        run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=_changed(
                continuation,
                continuation_identity="G69-03-UNKNOWN-CONTINUATION",
            ),
            governed_runtime_runner=_fail_runner,
        )

    terminal_request = _request(
        tmp_path,
        3,
        source_act_identity=continuation.expected_next_act_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="terminal"):
        run_human_interface_runtime_entry(
            request_envelope=terminal_request,
            continuation_envelope=_changed(
                continuation,
                continuation_state=TERMINAL_CONTINUATION,
            ),
            governed_runtime_runner=_fail_runner,
        )

    invalid_act_request = _request(
        tmp_path,
        4,
        source_act_identity="WRONG-NEXT-ACT",
    )
    with pytest.raises(FailClosedRuntimeError, match="next act identity is invalid"):
        run_human_interface_runtime_entry(
            request_envelope=invalid_act_request,
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )


@pytest.mark.parametrize(
    ("request_change", "message"),
    (
        ({"session_identity": "WRONG-SESSION"}, "request session is mismatched"),
        ({"actor_identity": "WRONG-ACTOR"}, "request actor is mismatched"),
        (
            {"workspace_identity": "WRONG-WORKSPACE"},
            "request workspace is mismatched",
        ),
    ),
)
def test_che_rejects_request_scope_mismatch(
    tmp_path: Path,
    request_change: dict[str, str],
    message: str,
) -> None:
    case_root = tmp_path / next(iter(request_change))
    _, _, continuation = _initial(case_root)
    request = _request(
        case_root,
        2,
        source_act_identity=continuation.expected_next_act_identity,
        **request_change,
    )

    with pytest.raises(FailClosedRuntimeError, match=message):
        run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )


def test_continuation_requires_canonical_request_and_legacy_compatibility_remains(
    tmp_path: Path,
) -> None:
    _, _, continuation = _initial(tmp_path / "canonical")
    with pytest.raises(FailClosedRuntimeError, match="requires a canonical request"):
        run_human_interface_runtime_entry(
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )

    result = run_human_interface_runtime_entry(
        interface_name="G69-03-LEGACY",
        session_id="G69-03-LEGACY-SESSION",
        human_requests=["Implement a validator."],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "legacy-runtime",
        workspace=tmp_path / "legacy-workspace",
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(result, dict)
    assert result["canonical_runtime_entry_interface"] == "G69-03-LEGACY"


def test_one_che_entry_and_protected_owner_modules_remain_unchanged() -> None:
    source_path = Path(
        inspect.getsourcefile(run_human_interface_runtime_entry) or ""
    )
    source = source_path.read_text(encoding="utf-8")
    assert source.count("def run_human_interface_runtime_entry(") == 1
    assert "continuation_envelope" in inspect.signature(
        run_human_interface_runtime_entry
    ).parameters
    assert "compose_production_conversation_flow_binding_v1(" in source
    assert "conversation_result = governed_runtime_runner(" in source
