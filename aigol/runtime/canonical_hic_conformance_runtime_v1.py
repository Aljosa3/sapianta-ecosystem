"""Thin channel-neutral HIC transport over certified CHE contracts only.

This module owns no workflow, semantic, authority, Replay, CRO, or owner logic.
It validates exact transport envelopes, invokes the sole Canonical Human Entry,
and exposes only the certified response and presentation facts returned by CHE.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_common_failure_presentation_owner_projection_contract_v1 import (
    canonical_presentation_facts_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    DELIVERY_RESOLUTION_QUERY_CAPABILITY,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryDeliveryResolutionQueryV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
    validate_canonical_che_response_envelope_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError


CANONICAL_HIC_CONFORMANCE_VERSION = (
    "G69_13_COMPLETE_HIC_CONFORMANCE_AND_HISTORICAL_INDEPENDENCE_V1"
)
DEVELOPMENT_HIC = "DEVELOPMENT_HIC"
CONFORMANCE_HARNESS = "CONFORMANCE_HARNESS"
PRODUCTION_HIC = "PRODUCTION_HIC"
ALLOWED_HIC_CERTIFICATION_SCOPES = frozenset(
    {DEVELOPMENT_HIC, CONFORMANCE_HARNESS, PRODUCTION_HIC}
)
ALLOWED_HIC_CHANNEL_KINDS = frozenset(
    {"CLI", "GUI", "REST", "BROWSER", "SPEECH", "AGENT_TO_AGENT"}
)


@dataclass(frozen=True, slots=True)
class CanonicalHICProfileV1:
    """Identity-only HIC profile with no workflow or semantic configuration."""

    conformance_version: str
    interface_identity: str
    adapter_identity: str
    channel_kind: str
    certification_scope: str

    def __post_init__(self) -> None:
        if self.conformance_version != CANONICAL_HIC_CONFORMANCE_VERSION:
            raise FailClosedRuntimeError("HIC conformance version is invalid")
        for field_name in ("interface_identity", "adapter_identity"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise FailClosedRuntimeError(f"HIC {field_name} is invalid")
        if self.channel_kind not in ALLOWED_HIC_CHANNEL_KINDS:
            raise FailClosedRuntimeError("HIC channel kind is invalid")
        if self.certification_scope not in ALLOWED_HIC_CERTIFICATION_SCOPES:
            raise FailClosedRuntimeError("HIC certification scope is invalid")


CLIA_CONFORMANCE_PROFILE_V1 = CanonicalHICProfileV1(
    conformance_version=CANONICAL_HIC_CONFORMANCE_VERSION,
    interface_identity="CLIA",
    adapter_identity="CLIA_G69_13_DEVELOPMENT_HIC",
    channel_kind="CLI",
    certification_scope=DEVELOPMENT_HIC,
)

# G69-13 remains immutable conformance evidence.  B10 promotes the same thin
# CLIA HIC family through a distinct production identity so production
# Requests cannot be confused with development evidence.
CLIA_PRODUCTION_PROFILE_V1 = CanonicalHICProfileV1(
    conformance_version=CANONICAL_HIC_CONFORMANCE_VERSION,
    interface_identity="CLIA",
    adapter_identity="CLIA_G69_19_PRODUCTION_HIC",
    channel_kind="CLI",
    certification_scope=PRODUCTION_HIC,
)

NON_CLI_CONFORMANCE_PROFILE_V1 = CanonicalHICProfileV1(
    conformance_version=CANONICAL_HIC_CONFORMANCE_VERSION,
    interface_identity="G69_13_NON_CLI_HIC_HARNESS",
    adapter_identity="G69_13_NON_CLI_HIC_HARNESS_ADAPTER",
    channel_kind="GUI",
    certification_scope=CONFORMANCE_HARNESS,
)

CERTIFIED_G69_13_HIC_PROFILES = (
    CLIA_CONFORMANCE_PROFILE_V1,
    NON_CLI_CONFORMANCE_PROFILE_V1,
)


@dataclass(frozen=True, slots=True)
class CanonicalHICExchangeV1:
    """Validated CHE exchange retained by a HIC without interpretation."""

    profile: CanonicalHICProfileV1
    request: CanonicalHumanEntryRequestEnvelopeV1
    response: CanonicalHumanEntryResponseEnvelopeV1
    presentation_facts: Mapping[str, Any]

    def __post_init__(self) -> None:
        request = validate_canonical_che_request_envelope_v1(self.request)
        response = validate_canonical_che_response_envelope_v1(self.response)
        if request.interface_identity != self.profile.interface_identity:
            raise FailClosedRuntimeError("HIC Request interface binding is invalid")
        if request.adapter_identity != self.profile.adapter_identity:
            raise FailClosedRuntimeError("HIC Request adapter binding is invalid")
        if response.request_identity != request.request_identity:
            raise FailClosedRuntimeError("HIC Response Request binding is invalid")
        expected_facts = canonical_presentation_facts_v1(response.presentation)
        if dict(self.presentation_facts) != expected_facts:
            raise FailClosedRuntimeError("HIC Presentation facts are invalid")
        object.__setattr__(self, "request", request)
        object.__setattr__(self, "response", response)
        object.__setattr__(
            self,
            "presentation_facts",
            MappingProxyType(dict(expected_facts)),
        )


def reject_hic_owned_workflow_v1(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Fail closed if CHE asks a thin HIC to supply owner workflow behavior."""

    raise FailClosedRuntimeError(
        "a conformant HIC cannot supply historical or owner workflow behavior"
    )


def validate_production_hic_activation_v1(runtime_root: str) -> dict[str, Any]:
    """Validate release status without giving the HIC workflow knowledge."""

    from aigol.runtime.constitutional_production_cutover_v1 import (
        validate_active_constitutional_production_cutover_v1,
    )

    return validate_active_constitutional_production_cutover_v1(runtime_root)


def create_canonical_hic_text_request_v1(
    *,
    profile: CanonicalHICProfileV1,
    actor_identity: str,
    session_identity: str,
    workspace_identity: str,
    runtime_scope_identity: str,
    request_identity: str,
    source_act_identity: str,
    order_identity: str,
    idempotency_identity: str,
    exact_text: str,
    created_at: str,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    """Create one exact text transport Request without semantic reduction."""

    if not isinstance(exact_text, str) or not exact_text.strip():
        raise FailClosedRuntimeError("HIC exact text is required")
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=profile.interface_identity,
        adapter_identity=profile.adapter_identity,
        actor_identity=actor_identity,
        actor_class=HUMAN_ACTOR,
        session_identity=session_identity,
        workspace_identity=workspace_identity,
        runtime_scope_identity=runtime_scope_identity,
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        idempotency_identity=idempotency_identity,
        source_payload=exact_text,
        source_encoding="UTF-8",
        source_modality="TEXT",
        declared_capabilities=("TEXT_INPUT", "TEXT_PRESENTATION"),
        metadata={"transport_profile_version": profile.conformance_version},
        created_at=created_at,
    )


def create_canonical_hic_delivery_resolution_request_v1(
    *,
    profile: CanonicalHICProfileV1,
    actor_identity: str,
    session_identity: str,
    workspace_identity: str,
    runtime_scope_identity: str,
    request_identity: str,
    source_act_identity: str,
    order_identity: str,
    idempotency_identity: str,
    target_request: CanonicalHumanEntryRequestEnvelopeV1,
    target_interaction_identity: str,
    created_at: str,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    """Create the certified reconnect query without retry inference."""

    target = validate_canonical_che_request_envelope_v1(target_request)
    query = CanonicalHumanEntryDeliveryResolutionQueryV1(
        contract_version=CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION,
        target_request_identity=target.request_identity,
        target_idempotency_identity=target.idempotency_identity,
        target_source_act_digest=canonical_che_request_source_act_digest_v1(target),
        target_interaction_identity=target_interaction_identity,
    )
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=profile.interface_identity,
        adapter_identity=profile.adapter_identity,
        actor_identity=actor_identity,
        actor_class=target.actor_class,
        session_identity=session_identity,
        workspace_identity=workspace_identity,
        runtime_scope_identity=runtime_scope_identity,
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=order_identity,
        idempotency_identity=idempotency_identity,
        source_payload=query.to_dict(),
        source_encoding="UTF-8",
        source_modality="STRUCTURED",
        declared_capabilities=(DELIVERY_RESOLUTION_QUERY_CAPABILITY,),
        metadata={"transport_profile_version": profile.conformance_version},
        created_at=created_at,
    )


def transport_canonical_hic_request_v1(
    *,
    profile: CanonicalHICProfileV1,
    request_envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
    continuation_envelope: CanonicalContinuationEnvelopeV1 | dict[str, Any] | None = None,
) -> CanonicalHICExchangeV1:
    """Transport exactly one certified Request to the sole CHE."""

    request = validate_canonical_che_request_envelope_v1(request_envelope)
    if request.interface_identity != profile.interface_identity:
        raise FailClosedRuntimeError("HIC Request interface binding is invalid")
    if request.adapter_identity != profile.adapter_identity:
        raise FailClosedRuntimeError("HIC Request adapter binding is invalid")
    continuation = (
        validate_canonical_che_continuation_envelope_v1(continuation_envelope)
        if continuation_envelope is not None
        else None
    )
    if continuation is not None and any(
        (
            continuation.actor_identity != request.actor_identity,
            continuation.session_identity != request.session_identity,
            continuation.workspace_identity != request.workspace_identity,
            continuation.runtime_scope_identity != request.runtime_scope_identity,
        )
    ):
        raise FailClosedRuntimeError("HIC Continuation Request binding is invalid")
    response = run_human_interface_runtime_entry(
        request_envelope=request,
        continuation_envelope=continuation,
        governed_runtime_runner=reject_hic_owned_workflow_v1,
    )
    canonical_response = validate_canonical_che_response_envelope_v1(response)
    return CanonicalHICExchangeV1(
        profile=profile,
        request=request,
        response=canonical_response,
        presentation_facts=canonical_presentation_facts_v1(
            canonical_response.presentation
        ),
    )
