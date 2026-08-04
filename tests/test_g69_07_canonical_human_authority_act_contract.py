"""Focused G69-07 Canonical Human Authority Act contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import inspect
import json
from pathlib import Path

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    ACCEPT,
    APPROVAL,
    AUTHORIZATION,
    CANCEL,
    CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    CANONICAL_HUMAN_AUTHORITY_KINDS,
    CLARIFICATION_RESPONSE,
    COMMITMENT,
    CONFIRMATION,
    CONTINUE,
    HUMAN_AUTHORITY_OWNER,
    REJECT,
    REWORK,
    CanonicalHumanAuthorityActV1,
    bind_canonical_human_authority_act_to_che_v1,
    canonical_human_authority_payload_digest_v1,
    deserialize_canonical_human_authority_act_v1,
    serialize_canonical_human_authority_act_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    ELIGIBLE_SOURCE_ACTOR,
    HUMAN_ACTOR,
    TERMINAL_CONTINUATION,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-08-04T18:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _request(
    root: Path,
    number: int,
    *,
    source_act_identity: str,
    payload: object,
    interface_identity: str = "G69-07-CLIA",
    modality: str = "TEXT",
    capabilities: tuple[str, ...] = ("TEXT_INPUT", "TEXT_PRESENTATION"),
) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=interface_identity,
        adapter_identity=f"{interface_identity}-ADAPTER",
        actor_identity="G69-07-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity="G69-07-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(root / "runtime"),
        request_identity=f"G69-07-REQUEST-{number:06d}",
        source_act_identity=source_act_identity,
        order_identity=f"G69-07-ORDER-{number:06d}",
        idempotency_identity=f"G69-07-IDEMPOTENCY-{number:06d}",
        source_payload=payload,
        source_encoding="UTF-8",
        source_modality=modality,
        declared_capabilities=capabilities,
        metadata={"transport_trace_identity": f"G69-07-TRACE-{number:06d}"},
        created_at=CREATED_AT,
    )


def _initial(root: Path) -> CanonicalHumanEntryResponseEnvelopeV1:
    request = _request(
        root,
        1,
        source_act_identity="G69-07-SOURCE-ACT-000001",
        payload="Implement a validator.",
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert isinstance(response, CanonicalHumanEntryResponseEnvelopeV1)
    assert response.continuation_envelope is not None
    return response


def _authority_request(
    root: Path,
    number: int,
    response: CanonicalHumanEntryResponseEnvelopeV1,
    *,
    authority_kind: str | None = None,
    payload: object = "action: implement",
    authority_act_identity: str | None = None,
    interface_identity: str = "G69-07-GUI",
) -> tuple[CanonicalHumanEntryRequestEnvelopeV1, CanonicalHumanAuthorityActV1]:
    continuation = response.continuation_envelope
    assert continuation is not None
    binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    act_identity = authority_act_identity or f"G69-07-AUTHORITY-{number:06d}"
    request_identity = f"G69-07-REQUEST-{number:06d}"
    kind = authority_kind or binding["authority_kind"]
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=act_identity,
        authority_kind=kind,
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
        metadata={"transport_interface_identity": interface_identity},
    )
    request = _request(
        root,
        number,
        source_act_identity=act_identity,
        payload=act.to_dict(),
        interface_identity=interface_identity,
        modality="STRUCTURED",
        capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
    )
    assert request.request_identity == request_identity
    return request, act


@pytest.mark.parametrize(
    "authority_kind",
    [
        CLARIFICATION_RESPONSE,
        CONFIRMATION,
        COMMITMENT,
        APPROVAL,
        AUTHORIZATION,
        ACCEPT,
        REJECT,
        CANCEL,
        REWORK,
        CONTINUE,
    ],
)
def test_every_closed_authority_kind_uses_one_channel_neutral_contract(
    tmp_path: Path, authority_kind: str
) -> None:
    response = _initial(tmp_path)
    request, act = _authority_request(
        tmp_path, 2, response, authority_kind=authority_kind
    )
    continuation = response.continuation_envelope
    assert continuation is not None
    binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]

    bound = bind_canonical_human_authority_act_to_che_v1(
        act,
        request,
        continuation,
        expected_authority_kind=authority_kind,
        expected_target_identity=binding["target_identity"],
        expected_target_revision=binding["target_revision"],
        expected_producing_owner=binding["producing_owner"],
        expected_owner=binding["expected_owner"],
        expected_authority_scope=binding["authority_scope"],
    )

    assert bound.authority_kind == authority_kind
    assert CANONICAL_HUMAN_AUTHORITY_KINDS == {
        CLARIFICATION_RESPONSE,
        CONFIRMATION,
        COMMITMENT,
        APPROVAL,
        AUTHORIZATION,
        ACCEPT,
        REJECT,
        CANCEL,
        REWORK,
        CONTINUE,
    }


def test_serialization_round_trip_and_deep_immutability(tmp_path: Path) -> None:
    response = _initial(tmp_path)
    _, act = _authority_request(
        tmp_path,
        2,
        response,
        payload={"decision": ["approve", {"bounded": True}]},
    )

    restored = deserialize_canonical_human_authority_act_v1(
        serialize_canonical_human_authority_act_v1(act)
    )
    assert restored.to_dict() == act.to_dict()
    with pytest.raises(FrozenInstanceError):
        act.authority_kind = REJECT  # type: ignore[misc]
    with pytest.raises(TypeError):
        act.payload["decision"] = []  # type: ignore[index]


def test_invalid_kind_payload_digest_and_structure_fail_closed(
    tmp_path: Path,
) -> None:
    response = _initial(tmp_path)
    _, act = _authority_request(tmp_path, 2, response)
    value = act.to_dict()
    with pytest.raises(FailClosedRuntimeError, match="kind"):
        CanonicalHumanAuthorityActV1.from_dict(
            {**value, "authority_kind": "FREE_FORM_AUTHORITY"}
        )
    with pytest.raises(FailClosedRuntimeError, match="payload digest"):
        CanonicalHumanAuthorityActV1.from_dict(
            {**value, "payload_digest": "sha256:not-the-payload"}
        )
    with pytest.raises(FailClosedRuntimeError, match="structure"):
        CanonicalHumanAuthorityActV1.from_dict(
            {key: item for key, item in value.items() if key != "expected_owner"}
        )


def test_revision_continuation_actor_session_and_owner_mismatch_fail_closed(
    tmp_path: Path,
) -> None:
    response = _initial(tmp_path)
    request, act = _authority_request(tmp_path, 2, response)
    continuation = response.continuation_envelope
    assert continuation is not None
    binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]

    def bind(candidate: CanonicalHumanAuthorityActV1) -> None:
        candidate_request = CanonicalHumanEntryRequestEnvelopeV1.from_dict(
            {**request.to_dict(), "source_payload": candidate.to_dict()}
        )
        bind_canonical_human_authority_act_to_che_v1(
            candidate,
            candidate_request,
            continuation,
            expected_authority_kind=binding["authority_kind"],
            expected_target_identity=binding["target_identity"],
            expected_target_revision=binding["target_revision"],
            expected_producing_owner=binding["producing_owner"],
            expected_owner=binding["expected_owner"],
            expected_authority_scope=binding["authority_scope"],
        )

    with pytest.raises(FailClosedRuntimeError, match="revision"):
        bind(replace(act, target_revision=act.target_revision + 1))
    with pytest.raises(FailClosedRuntimeError, match="continuation"):
        bind(replace(act, continuation_identity="WRONG-CONTINUATION"))
    with pytest.raises(FailClosedRuntimeError, match="actor"):
        bind(replace(act, actor_identity="WRONG-ACTOR"))
    with pytest.raises(FailClosedRuntimeError, match="session"):
        bind(replace(act, session_identity="WRONG-SESSION"))
    with pytest.raises(FailClosedRuntimeError, match="expected owner"):
        bind(replace(act, expected_owner="WRONG-OWNER"))
    non_human_request = CanonicalHumanEntryRequestEnvelopeV1.from_dict(
        {**request.to_dict(), "actor_class": ELIGIBLE_SOURCE_ACTOR}
    )
    with pytest.raises(FailClosedRuntimeError, match="Human actor"):
        bind_canonical_human_authority_act_to_che_v1(
            act,
            non_human_request,
            continuation,
            expected_authority_kind=binding["authority_kind"],
            expected_target_identity=binding["target_identity"],
            expected_target_revision=binding["target_revision"],
            expected_producing_owner=binding["producing_owner"],
            expected_owner=binding["expected_owner"],
            expected_authority_scope=binding["authority_scope"],
        )


def test_che_binds_and_forwards_only_the_exact_authority_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    response = _initial(tmp_path)
    request, act = _authority_request(tmp_path, 2, response)
    captured: list[list[str]] = []
    original = che_service._run_human_interface_runtime_entry_owner_execution_v1

    def capture(*args, **kwargs):
        captured.append(list(kwargs["human_requests"]))
        return original(*args, **kwargs)

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        capture,
    )
    advanced = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=response.continuation_envelope,
        governed_runtime_runner=_fail_runner,
    )

    assert advanced.owner_transition.owner_revision_after > (
        response.owner_transition.owner_revision_after
    )
    assert captured == [[act.payload]]
    assert advanced.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]["authority_kind"] == CLARIFICATION_RESPONSE


def test_confirmation_and_commitment_use_the_same_che_act_contract(
    tmp_path: Path,
) -> None:
    response = _initial(tmp_path)
    number = 2
    for payload in (
        "action: implement",
        "subject: validator",
        "outcome: validated requests",
        "work-type: ANALYSIS",
    ):
        request, act = _authority_request(
            tmp_path, number, response, payload=payload
        )
        assert act.authority_kind == CLARIFICATION_RESPONSE
        response = che_service.run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=response.continuation_envelope,
            governed_runtime_runner=_fail_runner,
        )
        number += 1

    confirmation_binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    assert confirmation_binding["authority_kind"] == CONFIRMATION
    confirmation_request, confirmation = _authority_request(
        tmp_path,
        number,
        response,
        payload=response.owner_transition.permitted_controls[0],
    )
    assert confirmation.authority_kind == CONFIRMATION
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=confirmation_request,
        continuation_envelope=response.continuation_envelope,
        governed_runtime_runner=_fail_runner,
    )
    number += 1

    commitment_binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    assert commitment_binding["authority_kind"] == COMMITMENT
    commitment_request, commitment = _authority_request(
        tmp_path,
        number,
        response,
        payload=response.owner_transition.permitted_controls[0],
    )
    assert commitment.authority_kind == COMMITMENT
    with pytest.raises(
        FailClosedRuntimeError,
        match="exactly one explicit canonical artifact is required",
    ):
        che_service.run_human_interface_runtime_entry(
            request_envelope=commitment_request,
            continuation_envelope=response.continuation_envelope,
            governed_runtime_runner=_fail_runner,
        )


def test_duplicate_authority_identity_fails_before_second_owner_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    response = _initial(tmp_path)
    first_request, first_act = _authority_request(tmp_path, 2, response)
    original = che_service._run_human_interface_runtime_entry_owner_execution_v1
    calls = 0

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        che_service,
        "_run_human_interface_runtime_entry_owner_execution_v1",
        counted,
    )
    che_service.run_human_interface_runtime_entry(
        request_envelope=first_request,
        continuation_envelope=response.continuation_envelope,
        governed_runtime_runner=_fail_runner,
    )
    duplicate_request, _ = _authority_request(
        tmp_path,
        3,
        response,
        authority_act_identity=first_act.authority_act_identity,
    )
    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=duplicate_request,
            continuation_envelope=response.continuation_envelope,
            governed_runtime_runner=_fail_runner,
        )
    assert calls == 1


def test_terminal_authority_fails_before_owner_invocation(tmp_path: Path) -> None:
    request = _request(
        tmp_path,
        1,
        source_act_identity="G69-07-TERMINAL-SOURCE",
        payload="Show architecture.",
    )
    terminal = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert terminal.continuation_envelope is not None
    assert terminal.continuation_envelope.continuation_state == TERMINAL_CONTINUATION
    continuation = terminal.continuation_envelope
    payload = "continue"
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="G69-07-TERMINAL-AUTHORITY",
        authority_kind=CONTINUE,
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity="G69-07-REQUEST-000002",
        continuation_identity=continuation.continuation_identity,
        target_identity=continuation.expected_next_act_identity,
        target_revision=continuation.expected_owner_revision,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=terminal.producing_owner,
        authority_scope="TERMINAL_RESULT",
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={},
    )
    authority_request = _request(
        tmp_path,
        2,
        source_act_identity=act.authority_act_identity,
        payload=act.to_dict(),
        modality="STRUCTURED",
        capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
    )
    with pytest.raises(FailClosedRuntimeError, match="terminal"):
        che_service.run_human_interface_runtime_entry(
            request_envelope=authority_request,
            continuation_envelope=continuation,
            governed_runtime_runner=_fail_runner,
        )


@pytest.mark.parametrize(
    "interface_identity",
    ["CLIA", "GUI", "REST", "BROWSER", "SPEECH", "AGENT_TO_AGENT"],
)
def test_new_channel_constructs_the_same_contract_without_workflow_logic(
    tmp_path: Path, interface_identity: str
) -> None:
    response = _initial(tmp_path)
    request, act = _authority_request(
        tmp_path,
        2,
        response,
        interface_identity=interface_identity,
    )
    assert request.interface_identity == interface_identity
    assert request.declared_capabilities == (
        CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    )
    assert request.to_dict()["source_payload"] == act.to_dict()
    assert response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ] == {
        "authority_kind": CLARIFICATION_RESPONSE,
        "target_identity": act.target_identity,
        "target_revision": act.target_revision,
        "producing_owner": act.producing_owner,
        "expected_owner": act.expected_owner,
        "authority_scope": act.authority_scope,
    }


def test_existing_callers_remain_compatible_and_che_entry_is_not_duplicated(
    tmp_path: Path,
) -> None:
    raw_response = _initial(tmp_path)
    assert raw_response.continuation_envelope is not None
    signature = inspect.signature(che_service.run_human_interface_runtime_entry)
    assert "request_envelope" in signature.parameters
    assert "continuation_envelope" in signature.parameters
    source = inspect.getsource(che_service)
    assert source.count("def run_human_interface_runtime_entry(") == 1


def test_g69_05_delivery_record_is_read_through_the_che_compatibility_boundary(
    tmp_path: Path,
) -> None:
    request = _request(
        tmp_path,
        1,
        source_act_identity="G69-07-SOURCE-ACT-000001",
        payload="Implement a validator.",
    )
    response = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    path = che_service._canonical_che_delivery_record_path_v1(
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        idempotency_identity=request.idempotency_identity,
    )
    legacy = json.loads(path.read_text(encoding="utf-8"))
    legacy.pop("authority_act_identity")
    legacy.pop("authority_act_digest")
    legacy["record_version"] = (
        "G69_05_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_V1"
    )
    legacy["record_hash"] = che_service._canonical_che_delivery_record_hash_v1(
        legacy
    )
    path.write_text(canonical_serialize(legacy) + "\n", encoding="utf-8")

    duplicate = che_service.run_human_interface_runtime_entry(
        request_envelope=request,
        governed_runtime_runner=_fail_runner,
    )
    assert duplicate.to_dict() == response.to_dict()
