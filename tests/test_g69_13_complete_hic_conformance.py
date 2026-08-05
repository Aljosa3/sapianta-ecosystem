"""Focused G69-13 HIC conformance and historical-independence tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import aigol.runtime.canonical_hic_conformance_runtime_v1 as hic_runtime
from aigol.cli.clia import session as clia_session
from aigol.cli.clia import transport as clia_transport
from aigol.runtime.canonical_common_failure_presentation_owner_projection_contract_v1 import (
    CanonicalCommonFailureV1,
    CanonicalOwnerProjectionV1,
    CanonicalPresentationV1,
)
from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CERTIFIED_G69_13_HIC_PROFILES,
    CLIA_CONFORMANCE_PROFILE_V1,
    CONFORMANCE_HARNESS,
    DEVELOPMENT_HIC,
    NON_CLI_CONFORMANCE_PROFILE_V1,
    CanonicalHICProfileV1,
    create_canonical_hic_delivery_resolution_request_v1,
    create_canonical_hic_text_request_v1,
    reject_hic_owned_workflow_v1,
    transport_canonical_hic_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    DELIVERY_COMMITTED_RESPONSE_FOUND,
    DELIVERY_NOT_APPLICABLE,
    HUMAN_ACTOR,
    NOT_APPLICABLE,
    REFERENCE_NOT_APPLICABLE,
    REFUSAL_RESPONSE,
    REFUSED_ADVANCEMENT,
    REFUSED_DISPOSITION,
    RESUBMIT_PERMITTED_CONTROL,
    RETRYABLE as CHE_RETRYABLE,
    TERMINAL_ADVANCEMENT,
    TERMINAL_DISPOSITION,
    TERMINAL_RESPONSE,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryOwnerTransitionV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
)
from aigol.runtime.canonical_opaque_reference_contract_v1 import (
    AVAILABLE,
    CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
    CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
    CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
    CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
    DOCUMENT,
    NOT_APPLICABLE as REFERENCE_NOT_APPLICABLE_VALUE,
    PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
    SHA256,
    CanonicalOpaqueReferenceSetV1,
    CanonicalOpaqueReferenceV1,
    canonical_ordered_reference_set_digest_v1,
    canonical_reference_validation_evidence_digest_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-05T15:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HIC_SOURCE_PATHS = (
    REPOSITORY_ROOT / "aigol/runtime/canonical_hic_conformance_runtime_v1.py",
    REPOSITORY_ROOT / "aigol/cli/clia/session.py",
    REPOSITORY_ROOT / "aigol/cli/clia/transport.py",
    REPOSITORY_ROOT / "aigol/cli/clia/presentation.py",
)


def _text_request(
    root: Path,
    profile: CanonicalHICProfileV1,
    number: int,
    *,
    source_act_identity: str | None = None,
    text: str = "Implement a validator.",
) -> CanonicalHumanEntryRequestEnvelopeV1:
    prefix = f"G69-13-{profile.channel_kind}-{number:06d}"
    return create_canonical_hic_text_request_v1(
        profile=profile,
        actor_identity="G69-13-HUMAN",
        session_identity=f"G69-13-{profile.channel_kind}-SESSION",
        workspace_identity=str(root / "workspace"),
        runtime_scope_identity=str(root / "runtime"),
        request_identity=f"{prefix}-REQUEST",
        source_act_identity=source_act_identity or f"{prefix}-SOURCE-ACT",
        order_identity=f"{prefix}-ORDER",
        idempotency_identity=f"{prefix}-IDEMPOTENCY",
        exact_text=text,
        created_at=CREATED_AT,
    )


def _initial_exchange(root: Path, profile: CanonicalHICProfileV1):
    request = _text_request(root, profile, 1)
    return transport_canonical_hic_request_v1(
        profile=profile,
        request_envelope=request,
    )


def _authority_request(
    root: Path,
    profile: CanonicalHICProfileV1,
    prior: CanonicalHumanEntryResponseEnvelopeV1,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    continuation = prior.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    binding = prior.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    request_identity = f"G69-13-{profile.channel_kind}-AUTHORITY-REQUEST"
    act_identity = f"G69-13-{profile.channel_kind}-AUTHORITY-ACT"
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
        metadata={"transport_interface_identity": profile.interface_identity},
    )
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=profile.interface_identity,
        adapter_identity=profile.adapter_identity,
        actor_identity=continuation.actor_identity,
        actor_class=HUMAN_ACTOR,
        session_identity=continuation.session_identity,
        workspace_identity=continuation.workspace_identity,
        runtime_scope_identity=continuation.runtime_scope_identity,
        request_identity=request_identity,
        source_act_identity=act_identity,
        order_identity=f"G69-13-{profile.channel_kind}-AUTHORITY-ORDER",
        idempotency_identity=f"G69-13-{profile.channel_kind}-AUTHORITY-IDEMPOTENCY",
        source_payload=act.to_dict(),
        source_encoding="UTF-8",
        source_modality="STRUCTURED",
        declared_capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
        metadata={"transport_profile_version": profile.conformance_version},
        created_at=CREATED_AT,
    )


def _reference_request(
    root: Path,
    profile: CanonicalHICProfileV1,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    prefix = f"G69-13-{profile.channel_kind}-REFERENCE"
    reference_identity = f"{prefix}-000001"
    validation_identity = f"{prefix}-VALIDATION"
    integrity = replay_hash({"reference_identity": reference_identity})
    evidence_digest = canonical_reference_validation_evidence_digest_v1(
        reference_identity=reference_identity,
        validation_owner_identity=PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
        custody_owner_identity=f"{prefix}-CUSTODY",
        availability_status=AVAILABLE,
        integrity_algorithm=SHA256,
        integrity_reference=integrity,
        access_scope_identity=f"{prefix}-ACCESS",
        validation_evidence_identity=validation_identity,
        retryability=REFERENCE_NOT_APPLICABLE_VALUE,
        correction_requirement=REFERENCE_NOT_APPLICABLE_VALUE,
    )
    reference = CanonicalOpaqueReferenceV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION,
        reference_identity=reference_identity,
        reference_kind=DOCUMENT,
        modality="TEXT",
        ordered_position=1,
        provenance_identity=f"{prefix}-PROVENANCE",
        content_owner_identity=f"{prefix}-CONTENT",
        custody_owner_identity=f"{prefix}-CUSTODY",
        validation_owner_identity=PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
        integrity_algorithm=SHA256,
        integrity_reference=integrity,
        availability_status=AVAILABLE,
        access_scope_identity=f"{prefix}-ACCESS",
        source_channel_identity=profile.interface_identity,
        source_actor_identity="G69-13-HUMAN",
        validation_evidence_identity=validation_identity,
        validation_evidence_digest=evidence_digest,
        retryability=REFERENCE_NOT_APPLICABLE_VALUE,
        correction_requirement=REFERENCE_NOT_APPLICABLE_VALUE,
        created_at=CREATED_AT,
        metadata={},
    )
    references = (reference,)
    digest = canonical_ordered_reference_set_digest_v1(references)
    request_identity = f"{prefix}-REQUEST"
    source_act_identity = f"{prefix}-SOURCE-ACT"
    order_identity = f"{prefix}-ORDER"
    reference_set = CanonicalOpaqueReferenceSetV1(
        contract_version=CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION,
        reference_set_identity="OPAQUE-REFERENCE-SET-" + digest,
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        interaction_identity=NOT_APPLICABLE,
        session_identity=f"G69-13-{profile.channel_kind}-SESSION",
        actor_identity="G69-13-HUMAN",
        workspace_identity=str(root / "workspace"),
        ordered_reference_set_digest=digest,
        retry_of_source_act_identity=None,
        retry_of_order_identity=None,
        retry_of_reference_set_digest=None,
        references=references,
        metadata={},
    )
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=profile.interface_identity,
        adapter_identity=profile.adapter_identity,
        actor_identity="G69-13-HUMAN",
        actor_class=HUMAN_ACTOR,
        session_identity=reference_set.session_identity,
        workspace_identity=reference_set.workspace_identity,
        runtime_scope_identity=str(root / "runtime"),
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        idempotency_identity=f"{prefix}-IDEMPOTENCY",
        source_payload={
            "contract_version": CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION,
            "source_payload": "Review the supplied Reference.",
            "reference_set": reference_set.to_dict(),
        },
        source_encoding="UTF-8",
        source_modality="MULTIMODAL",
        declared_capabilities=(
            CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY,
            "TEXT_INPUT",
        ),
        metadata={"transport_profile_version": profile.conformance_version},
        created_at=CREATED_AT,
    )


@pytest.mark.parametrize("profile", CERTIFIED_G69_13_HIC_PROFILES)
def test_every_certified_hic_transports_exact_request_response_and_continuation(
    tmp_path: Path,
    profile: CanonicalHICProfileV1,
) -> None:
    exchange = _initial_exchange(tmp_path / profile.channel_kind, profile)

    assert isinstance(exchange.request, CanonicalHumanEntryRequestEnvelopeV1)
    assert isinstance(exchange.response, CanonicalHumanEntryResponseEnvelopeV1)
    assert isinstance(
        exchange.response.continuation_envelope,
        CanonicalContinuationEnvelopeV1,
    )
    assert isinstance(exchange.response.owner_projection, CanonicalOwnerProjectionV1)
    assert isinstance(exchange.response.presentation, CanonicalPresentationV1)
    assert exchange.response.correlation_identity
    assert exchange.response.evidence_references
    assert "workflow" not in exchange.presentation_facts
    assert "semantic" not in exchange.presentation_facts


@pytest.mark.parametrize("profile", CERTIFIED_G69_13_HIC_PROFILES)
def test_every_certified_hic_transports_exact_human_authority_act(
    tmp_path: Path,
    profile: CanonicalHICProfileV1,
) -> None:
    initial = _initial_exchange(tmp_path / profile.channel_kind, profile)
    continuation = initial.response.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    request = _authority_request(
        tmp_path / profile.channel_kind,
        profile,
        initial.response,
    )

    exchange = transport_canonical_hic_request_v1(
        profile=profile,
        request_envelope=request,
        continuation_envelope=continuation,
    )

    assert exchange.request.source_payload["authority_act_identity"] == (
        request.source_act_identity
    )
    assert exchange.response.owner_transition.owner_revision_before == 1
    assert exchange.response.owner_transition.owner_revision_after > (
        exchange.response.owner_transition.owner_revision_before
    )


@pytest.mark.parametrize("profile", CERTIFIED_G69_13_HIC_PROFILES)
def test_every_certified_hic_transports_opaque_references_without_inspection(
    tmp_path: Path,
    profile: CanonicalHICProfileV1,
) -> None:
    request = _reference_request(tmp_path / profile.channel_kind, profile)
    exchange = transport_canonical_hic_request_v1(
        profile=profile,
        request_envelope=request,
    )

    projection = exchange.response.presentation_metadata[
        "opaque_reference_validation"
    ]
    assert projection["availability_statuses"] == (AVAILABLE,)
    assert exchange.response.producing_owner != profile.interface_identity


def test_delivery_reconnect_uses_only_certified_query_and_response(tmp_path: Path) -> None:
    initial = _initial_exchange(tmp_path, NON_CLI_CONFORMANCE_PROFILE_V1)
    continuation = initial.response.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    query = create_canonical_hic_delivery_resolution_request_v1(
        profile=NON_CLI_CONFORMANCE_PROFILE_V1,
        actor_identity=initial.request.actor_identity,
        session_identity=initial.request.session_identity,
        workspace_identity=initial.request.workspace_identity,
        runtime_scope_identity=initial.request.runtime_scope_identity,
        request_identity="G69-13-RECONNECT-REQUEST",
        source_act_identity="G69-13-RECONNECT-SOURCE-ACT",
        order_identity="G69-13-RECONNECT-ORDER",
        idempotency_identity="G69-13-RECONNECT-IDEMPOTENCY",
        target_request=initial.request,
        target_interaction_identity=continuation.interaction_identity,
        created_at=CREATED_AT,
    )
    resolved = transport_canonical_hic_request_v1(
        profile=NON_CLI_CONFORMANCE_PROFILE_V1,
        request_envelope=query,
    )

    assert resolved.response.owner_transition.delivery_resolution_status == (
        DELIVERY_COMMITTED_RESPONSE_FOUND
    )
    assert resolved.response.owner_transition.resolved_response_identity == (
        initial.response.response_identity
    )


def _refusal_response(
    request: CanonicalHumanEntryRequestEnvelopeV1,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="CONVERSATION_OWNER",
        owner_state_identity="G69-13-REFUSAL-OWNER-STATE",
        owner_revision_before=1,
        owner_revision_after=1,
        response_disposition=REFUSED_DISPOSITION,
        advancement_outcome=REFUSED_ADVANCEMENT,
        next_act_identity="G69-13-REFUSAL-NEXT-ACT",
        next_act_kind="CLARIFICATION_RESPONSE",
        next_act_target_identity="G69-13-REFUSAL-TARGET",
        next_act_target_digest="sha256:" + "1" * 64,
        next_act_expected_owner_revision=1,
        permitted_controls=("action: <value>",),
        payload_constraints={},
        exact_human_act_required=True,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity="G69-13-REFUSAL",
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
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity=request.request_identity + ":REFUSAL-RESPONSE",
        request_identity=request.request_identity,
        response_type=REFUSAL_RESPONSE,
        producing_owner=transition.producing_owner,
        owner_status="OWNER_INPUT_NOT_ADMITTED",
        advancement_state=REFUSED_ADVANCEMENT,
        presentation_payload=("The owner refused the submitted act.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
        },
        correlation_identity=request.request_identity + ":REFUSAL-CORRELATION",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
    )


@pytest.mark.parametrize("profile", CERTIFIED_G69_13_HIC_PROFILES)
def test_every_certified_hic_transports_common_failure_without_interpretation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    profile: CanonicalHICProfileV1,
) -> None:
    request = _text_request(tmp_path / profile.channel_kind, profile, 1)
    monkeypatch.setattr(
        hic_runtime,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: _refusal_response(request),
    )

    exchange = transport_canonical_hic_request_v1(
        profile=profile,
        request_envelope=request,
    )

    assert isinstance(exchange.response.common_failure, CanonicalCommonFailureV1)
    assert exchange.response.common_failure.failure_reason == (
        "OWNER_INPUT_NOT_ADMITTED"
    )
    assert exchange.presentation_facts["presentation_kind"] == "COMMON_FAILURE"


def _terminal_response(request: CanonicalHumanEntryRequestEnvelopeV1):
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="CERTIFICATION_OWNER",
        owner_state_identity="G69-13-TERMINAL-OWNER-STATE",
        owner_revision_before=1,
        owner_revision_after=2,
        response_disposition=TERMINAL_DISPOSITION,
        advancement_outcome=TERMINAL_ADVANCEMENT,
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
        terminal_identity="G69-13-TERMINAL",
        terminal_type="COMPLETE",
        terminal_status="CERTIFIED_COMPLETE",
        retryability=NOT_APPLICABLE,
        recovery_requirement=NOT_APPLICABLE,
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity="G69-13-TERMINAL-RESPONSE",
        request_identity=request.request_identity,
        response_type=TERMINAL_RESPONSE,
        producing_owner=transition.producing_owner,
        owner_status="CERTIFIED_COMPLETE",
        advancement_state=TERMINAL_ADVANCEMENT,
        presentation_payload=("The owner reports terminal completion.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
        },
        correlation_identity="G69-13-TERMINAL-CORRELATION",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
        continuation_envelope=None,
    )


def test_terminal_response_is_presented_without_hic_inference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _text_request(tmp_path, NON_CLI_CONFORMANCE_PROFILE_V1, 1)
    monkeypatch.setattr(
        hic_runtime,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: _terminal_response(request),
    )

    exchange = transport_canonical_hic_request_v1(
        profile=NON_CLI_CONFORMANCE_PROFILE_V1,
        request_envelope=request,
    )

    assert exchange.response.response_type == TERMINAL_RESPONSE
    assert exchange.response.continuation_envelope is None
    assert exchange.presentation_facts["presentation_kind"] == "TERMINAL_OUTCOME"


def test_development_clia_consumes_failure_and_terminal_responses_mechanically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    results = []
    for index, response_factory in enumerate(
        (_refusal_response, _terminal_response),
        start=1,
    ):
        root = tmp_path / str(index)
        value = clia_session.create_clia_transport_session_v1(
            transport_session_identity=f"G69-13-CLIA-CONSUMER-{index}",
            human_actor_reference="G69-13-HUMAN",
            workspace_reference=str(root / "workspace"),
            runtime_root_reference=str(root / "runtime"),
            created_at=CREATED_AT,
        )
        clia_session.open_clia_transport_session_v1(value)
        monkeypatch.setattr(
            clia_transport,
            "run_human_interface_runtime_entry",
            lambda **kwargs: response_factory(kwargs["request_envelope"]),
        )
        results.append(
            clia_transport.submit_clia_human_act_v1(
                session=value,
                human_act="Exact Human act.",
            )
        )

    assert isinstance(
        results[0].canonical_response.common_failure,
        CanonicalCommonFailureV1,
    )
    assert results[1].canonical_response.response_type == TERMINAL_RESPONSE
    assert all(
        result.che_response == result.canonical_response.to_dict()
        for result in results
    )


def test_malformed_response_profile_and_continuation_fail_closed(
    tmp_path: Path,
) -> None:
    request = _text_request(tmp_path, CLIA_CONFORMANCE_PROFILE_V1, 1)
    with pytest.raises(FailClosedRuntimeError, match="interface binding"):
        transport_canonical_hic_request_v1(
            profile=NON_CLI_CONFORMANCE_PROFILE_V1,
            request_envelope=request,
        )
    initial = _initial_exchange(tmp_path / "initial", CLIA_CONFORMANCE_PROFILE_V1)
    continuation = initial.response.continuation_envelope
    assert isinstance(continuation, CanonicalContinuationEnvelopeV1)
    mismatched = CanonicalContinuationEnvelopeV1.from_dict(
        {
            **continuation.to_dict(),
            "session_identity": "DIFFERENT-SESSION",
        }
    )
    next_request = _text_request(
        tmp_path / "initial",
        CLIA_CONFORMANCE_PROFILE_V1,
        2,
        source_act_identity=continuation.expected_next_act_identity,
        text="action: implement",
    )
    with pytest.raises(FailClosedRuntimeError, match="Continuation Request"):
        transport_canonical_hic_request_v1(
            profile=CLIA_CONFORMANCE_PROFILE_V1,
            request_envelope=next_request,
            continuation_envelope=mismatched,
        )


def test_development_clia_uses_certified_contracts_and_retains_continuation(
    tmp_path: Path,
) -> None:
    value = clia_session.create_clia_transport_session_v1(
        transport_session_identity="G69-13-CLIA-SESSION",
        human_actor_reference="G69-13-HUMAN",
        workspace_reference=str(tmp_path / "workspace"),
        runtime_root_reference=str(tmp_path / "runtime"),
        created_at=CREATED_AT,
    )
    clia_session.open_clia_transport_session_v1(value)
    first = clia_transport.submit_clia_human_act_v1(
        session=value,
        human_act="Implement a validator.",
    )
    second = clia_transport.submit_clia_human_act_v1(
        session=value,
        human_act="action: implement",
    )

    assert first.canonical_response.request_identity.endswith(":CHE-REQUEST")
    assert isinstance(value.last_che_continuation_envelope, CanonicalContinuationEnvelopeV1)
    assert second.canonical_response.owner_transition.owner_revision_before == 1
    assert second.canonical_response.owner_transition.owner_revision_after > (
        second.canonical_response.owner_transition.owner_revision_before
    )
    assert value.status is clia_session.CliaTransportStatus.OPEN


def test_certified_hic_profiles_are_bounded_and_non_production() -> None:
    assert CERTIFIED_G69_13_HIC_PROFILES == (
        CLIA_CONFORMANCE_PROFILE_V1,
        NON_CLI_CONFORMANCE_PROFILE_V1,
    )
    assert {profile.certification_scope for profile in CERTIFIED_G69_13_HIC_PROFILES} == {
        DEVELOPMENT_HIC,
        CONFORMANCE_HARNESS,
    }
    assert clia_session.CLIA_DEVELOPMENT_STATUS == (
        "CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER"
    )


def test_hic_sources_are_historically_independent_and_owner_isolated() -> None:
    forbidden_imports = (
        "aigol.cli.aicli",
        "aigol.cli.aigol_cli",
        "human_interface_conversation",
        "production_conversation_flow",
        "platform_core",
        "governance",
        "authorization",
        "worker",
        "provider",
        "replay",
        "certification",
        "constitutional_runtime_observatory",
    )
    forbidden_calls = (
        "route",
        "interpret",
        "classify",
        "authorize",
        "execute",
        "mutate",
        "replay",
        "observe",
        "certify",
    )
    for path in HIC_SOURCE_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: list[str] = []
        calls: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id.lower())
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr.lower())
        assert not any(
            fragment in imported
            for imported in imports
            for fragment in forbidden_imports
        )
        assert not any(
            call.startswith(fragment)
            for call in calls
            for fragment in forbidden_calls
        )


def test_che_and_production_counts_remain_one() -> None:
    che_source = Path(
        run_human_interface_runtime_entry.__code__.co_filename
    ).read_text(encoding="utf-8")
    assert che_source.count("def run_human_interface_runtime_entry(") == 1
    assert "def run_canonical_human_entry" not in che_source
    assert clia_session.CLIA_DEVELOPMENT_STATUS.endswith("NOT_PRODUCTION_CUTOVER")
    assert len(CERTIFIED_G69_13_HIC_PROFILES) == 2
    assert sum(
        profile.certification_scope == DEVELOPMENT_HIC
        for profile in CERTIFIED_G69_13_HIC_PROFILES
    ) == 1


def test_hic_owned_workflow_is_rejected() -> None:
    with pytest.raises(FailClosedRuntimeError, match="cannot supply"):
        reject_hic_owned_workflow_v1()
