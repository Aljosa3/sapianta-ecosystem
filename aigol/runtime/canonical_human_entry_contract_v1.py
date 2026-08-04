"""Channel-neutral Canonical Human Entry transport contracts.

These immutable envelopes carry transport information only.  They do not
represent Human authority acts, references, failures, semantic state, workflow
state, or any downstream owner artifact.  Continuation is an opaque binding
contract: channels store and return it without interpreting its identities.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_CHE_REQUEST_CONTRACT_VERSION = (
    "G69_02_CANONICAL_CHE_REQUEST_ENVELOPE_V1"
)
CANONICAL_CHE_RESPONSE_CONTRACT_VERSION = (
    "G69_05_CANONICAL_CHE_RESPONSE_ENVELOPE_V2"
)
CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION = (
    "G69_05_CANONICAL_CHE_CONTINUATION_ENVELOPE_V2"
)
CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION = (
    "G69_05_CANONICAL_CHE_OWNER_TRANSITION_V1"
)
CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION = (
    "G69_05_CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_V1"
)

HUMAN_ACTOR = "HUMAN"
ELIGIBLE_SOURCE_ACTOR = "ELIGIBLE_SOURCE_ACTOR"
ALLOWED_ACTOR_CLASSES = frozenset({HUMAN_ACTOR, ELIGIBLE_SOURCE_ACTOR})
ALLOWED_SOURCE_MODALITIES = frozenset(
    {
        "TEXT",
        "STRUCTURED",
        "AUDIO",
        "VISUAL",
        "MULTIMODAL",
        "AGENT_MESSAGE",
        "TRANSPORT_COLLECTION",
    }
)

INFORMATIONAL_RESPONSE = "INFORMATIONAL"
PENDING_RESPONSE = "PENDING"
REFUSAL_RESPONSE = "REFUSAL"
TERMINAL_RESPONSE = "TERMINAL"
OWNER_RESPONSE = PENDING_RESPONSE
ALLOWED_RESPONSE_TYPES = frozenset(
    {
        INFORMATIONAL_RESPONSE,
        PENDING_RESPONSE,
        REFUSAL_RESPONSE,
        TERMINAL_RESPONSE,
    }
)

ADVANCED = "ADVANCED"
NOT_ADVANCED = "NOT_ADVANCED"
TERMINAL_ADVANCEMENT = "TERMINAL"
REFUSED_ADVANCEMENT = "REFUSED"
DELIVERY_OUTCOME_UNKNOWN = "DELIVERY_OUTCOME_UNKNOWN"
UNCHANGED = NOT_ADVANCED
UNKNOWN_ADVANCEMENT = DELIVERY_OUTCOME_UNKNOWN
ALLOWED_ADVANCEMENT_STATES = frozenset(
    {
        ADVANCED,
        NOT_ADVANCED,
        TERMINAL_ADVANCEMENT,
        REFUSED_ADVANCEMENT,
        DELIVERY_OUTCOME_UNKNOWN,
    }
)

PENDING_DISPOSITION = "PENDING"
INFORMATIONAL_DISPOSITION = "INFORMATIONAL"
REFUSED_DISPOSITION = "REFUSED"
TERMINAL_DISPOSITION = "TERMINAL"
DELIVERY_RESOLUTION_DISPOSITION = "DELIVERY_RESOLUTION"
ALLOWED_RESPONSE_DISPOSITIONS = frozenset(
    {
        PENDING_DISPOSITION,
        INFORMATIONAL_DISPOSITION,
        REFUSED_DISPOSITION,
        TERMINAL_DISPOSITION,
        DELIVERY_RESOLUTION_DISPOSITION,
    }
)

NOT_APPLICABLE = "NOT_APPLICABLE"
RETRYABLE = "RETRYABLE"
NOT_RETRYABLE = "NOT_RETRYABLE"
ALLOWED_RETRYABILITY = frozenset({RETRYABLE, NOT_RETRYABLE, NOT_APPLICABLE})

NO_RECOVERY_REQUIRED = "NO_RECOVERY_REQUIRED"
RESUBMIT_PERMITTED_CONTROL = "RESUBMIT_PERMITTED_CONTROL"
RESUBMIT_EXACT_REQUEST = "RESUBMIT_EXACT_REQUEST"
USE_RESOLVED_RESPONSE = "USE_RESOLVED_RESPONSE"
QUERY_DELIVERY_STATUS = "QUERY_DELIVERY_STATUS"
MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
ALLOWED_RECOVERY_REQUIREMENTS = frozenset(
    {
        NO_RECOVERY_REQUIRED,
        RESUBMIT_PERMITTED_CONTROL,
        RESUBMIT_EXACT_REQUEST,
        USE_RESOLVED_RESPONSE,
        QUERY_DELIVERY_STATUS,
        MANUAL_REVIEW_REQUIRED,
        NOT_APPLICABLE,
    }
)

REFERENCE_CREATED = "CREATED"
REFERENCE_NOT_CREATED = "NOT_CREATED"
REFERENCE_NOT_APPLICABLE = NOT_APPLICABLE
ALLOWED_REFERENCE_STATUSES = frozenset(
    {REFERENCE_CREATED, REFERENCE_NOT_CREATED, REFERENCE_NOT_APPLICABLE}
)

DELIVERY_NOT_APPLICABLE = NOT_APPLICABLE
DELIVERY_RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN = (
    "RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN"
)
DELIVERY_COMMITTED_RESPONSE_FOUND = "COMMITTED_RESPONSE_FOUND"
DELIVERY_COMMITTED_NOT_ADVANCED = "COMMITTED_NOT_ADVANCED"
DELIVERY_ENTERED_NOT_ADVANCED = "ENTERED_NOT_ADVANCED"
DELIVERY_NOT_FOUND = "NOT_FOUND"
ALLOWED_DELIVERY_RESOLUTION_STATUSES = frozenset(
    {
        DELIVERY_NOT_APPLICABLE,
        DELIVERY_RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN,
        DELIVERY_COMMITTED_RESPONSE_FOUND,
        DELIVERY_COMMITTED_NOT_ADVANCED,
        DELIVERY_ENTERED_NOT_ADVANCED,
        DELIVERY_OUTCOME_UNKNOWN,
        DELIVERY_NOT_FOUND,
    }
)

DELIVERY_RESOLUTION_QUERY_CAPABILITY = "DELIVERY_RESOLUTION_QUERY"

ACTIVE_CONTINUATION = "ACTIVE"
TERMINAL_CONTINUATION = "TERMINAL"
ALLOWED_CONTINUATION_STATES = frozenset(
    {ACTIVE_CONTINUATION, TERMINAL_CONTINUATION}
)

_REQUEST_FIELDS = frozenset(
    {
        "contract_version",
        "interface_identity",
        "adapter_identity",
        "actor_identity",
        "actor_class",
        "session_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "request_identity",
        "source_act_identity",
        "order_identity",
        "idempotency_identity",
        "source_payload",
        "source_encoding",
        "source_modality",
        "declared_capabilities",
        "metadata",
        "created_at",
    }
)
_RESPONSE_FIELDS = frozenset(
    {
        "contract_version",
        "response_identity",
        "request_identity",
        "response_type",
        "producing_owner",
        "owner_status",
        "advancement_state",
        "presentation_payload",
        "presentation_metadata",
        "correlation_identity",
        "evidence_references",
        "replay_references",
        "certification_references",
        "owner_transition",
        "continuation_envelope",
    }
)
_CONTINUATION_FIELDS = frozenset(
    {
        "contract_version",
        "continuation_identity",
        "interaction_identity",
        "conversation_identity",
        "session_identity",
        "actor_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "request_identity",
        "previous_response_identity",
        "previous_order_identity",
        "previous_idempotency_identity",
        "continuation_sequence",
        "expected_next_act_identity",
        "expected_owner_state_identity",
        "expected_owner_revision",
        "continuation_state",
        "correlation_identity",
        "metadata",
    }
)
_OWNER_TRANSITION_FIELDS = frozenset(
    {
        "contract_version",
        "producing_owner",
        "owner_state_identity",
        "owner_revision_before",
        "owner_revision_after",
        "response_disposition",
        "advancement_outcome",
        "next_act_identity",
        "next_act_kind",
        "next_act_target_identity",
        "next_act_target_digest",
        "next_act_expected_owner_revision",
        "permitted_controls",
        "payload_constraints",
        "exact_human_act_required",
        "cancellation_permitted",
        "interruption_permitted",
        "refusal_identity",
        "refusal_type",
        "refusal_status",
        "terminal_identity",
        "terminal_type",
        "terminal_status",
        "retryability",
        "recovery_requirement",
        "delivery_resolution_status",
        "resolved_response_identity",
        "resolved_response_hash",
        "replay_reference_status",
        "certification_reference_status",
    }
)
_DELIVERY_RESOLUTION_QUERY_FIELDS = frozenset(
    {
        "contract_version",
        "target_request_identity",
        "target_idempotency_identity",
        "target_source_act_digest",
        "target_interaction_identity",
    }
)
_FORBIDDEN_REQUEST_METADATA_TOKENS = frozenset(
    {
        "authorization",
        "certification",
        "commitment",
        "continuation",
        "conversation",
        "cwm",
        "governance",
        "objective",
        "owner_state",
        "proposal",
        "replay",
        "semantic",
        "worker",
        "workflow",
    }
)


def _require_identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if value != value.strip():
        raise FailClosedRuntimeError(f"{field_name} must not contain boundary whitespace")
    return value


def _immutable_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError("CHE envelope object keys must be strings")
        return MappingProxyType(
            {key: _immutable_json(value[key]) for key in sorted(value)}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_json(item) for item in value)
    immutable = deepcopy(value)
    canonical_serialize(immutable)
    return immutable


def _plain_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain_json(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return deepcopy(value)


def _immutable_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{field_name} must be an ordered list")
    result = tuple(_require_identity(item, field_name) for item in value)
    if len(set(result)) != len(result):
        raise FailClosedRuntimeError(f"{field_name} must not contain duplicates")
    return result


def _validate_request_metadata(metadata: Mapping[str, Any]) -> None:
    for key, value in metadata.items():
        normalized = key.lower().replace("-", "_")
        if not normalized.startswith("transport_") or any(
            token in normalized for token in _FORBIDDEN_REQUEST_METADATA_TOKENS
        ):
            raise FailClosedRuntimeError(
                "CHE request metadata must contain transport information only"
            )
        if isinstance(value, Mapping):
            _validate_request_metadata(value)


def _validate_transport_capabilities(capabilities: tuple[str, ...]) -> None:
    for capability in capabilities:
        normalized = capability.lower().replace("-", "_")
        if any(token in normalized for token in _FORBIDDEN_REQUEST_METADATA_TOKENS):
            raise FailClosedRuntimeError(
                "CHE declared capabilities must be transport capabilities only"
            )


def _revision(value: Any, field_name: str) -> int | str:
    if value == NOT_APPLICABLE:
        return value
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(
            f"{field_name} must be a non-negative revision or NOT_APPLICABLE"
        )
    return value


def _optional_identity(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_identity(value, field_name)


@dataclass(frozen=True, slots=True)
class CanonicalHumanEntryDeliveryResolutionQueryV1:
    """Exact transport query submitted through the sole CHE request contract."""

    contract_version: str
    target_request_identity: str
    target_idempotency_identity: str
    target_source_act_digest: str
    target_interaction_identity: str

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_DELIVERY_RESOLUTION_QUERY_VERSION:
            raise FailClosedRuntimeError(
                "CHE delivery resolution query version is invalid"
            )
        for field_name in (
            "target_request_identity",
            "target_idempotency_identity",
            "target_source_act_digest",
            "target_interaction_identity",
        ):
            _require_identity(getattr(self, field_name), field_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "target_request_identity": self.target_request_identity,
            "target_idempotency_identity": self.target_idempotency_identity,
            "target_source_act_digest": self.target_source_act_digest,
            "target_interaction_identity": self.target_interaction_identity,
        }

    @classmethod
    def from_dict(
        cls, envelope: dict[str, Any]
    ) -> "CanonicalHumanEntryDeliveryResolutionQueryV1":
        if not isinstance(envelope, dict) or set(envelope) != (
            _DELIVERY_RESOLUTION_QUERY_FIELDS
        ):
            raise FailClosedRuntimeError(
                "CHE delivery resolution query structure is invalid"
            )
        return cls(**envelope)


@dataclass(frozen=True, slots=True)
class CanonicalHumanEntryOwnerTransitionV1:
    """Channel-neutral projection of explicit producing-owner transition facts."""

    contract_version: str
    producing_owner: str
    owner_state_identity: str
    owner_revision_before: int | str
    owner_revision_after: int | str
    response_disposition: str
    advancement_outcome: str
    next_act_identity: str | None
    next_act_kind: str | None
    next_act_target_identity: str | None
    next_act_target_digest: str | None
    next_act_expected_owner_revision: int | str
    permitted_controls: tuple[str, ...]
    payload_constraints: Mapping[str, Any]
    exact_human_act_required: bool
    cancellation_permitted: bool
    interruption_permitted: bool
    refusal_identity: str | None
    refusal_type: str
    refusal_status: str
    terminal_identity: str | None
    terminal_type: str
    terminal_status: str
    retryability: str
    recovery_requirement: str
    delivery_resolution_status: str
    resolved_response_identity: str | None
    resolved_response_hash: str | None
    replay_reference_status: str
    certification_reference_status: str

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION:
            raise FailClosedRuntimeError("CHE owner transition version is invalid")
        _require_identity(self.producing_owner, "producing_owner")
        _require_identity(self.owner_state_identity, "owner_state_identity")
        _revision(self.owner_revision_before, "owner_revision_before")
        _revision(self.owner_revision_after, "owner_revision_after")
        _revision(
            self.next_act_expected_owner_revision,
            "next_act_expected_owner_revision",
        )
        if self.response_disposition not in ALLOWED_RESPONSE_DISPOSITIONS:
            raise FailClosedRuntimeError("CHE response disposition is invalid")
        if self.advancement_outcome not in ALLOWED_ADVANCEMENT_STATES:
            raise FailClosedRuntimeError("CHE owner advancement outcome is invalid")
        for field_name in (
            "next_act_identity",
            "next_act_kind",
            "next_act_target_identity",
            "next_act_target_digest",
            "refusal_identity",
            "terminal_identity",
            "resolved_response_identity",
            "resolved_response_hash",
        ):
            _optional_identity(getattr(self, field_name), field_name)
        for field_name in (
            "refusal_type",
            "refusal_status",
            "terminal_type",
            "terminal_status",
        ):
            _require_identity(getattr(self, field_name), field_name)
        controls = _immutable_string_tuple(
            self.permitted_controls, "permitted_controls"
        )
        if not isinstance(self.payload_constraints, Mapping):
            raise FailClosedRuntimeError("CHE payload constraints must be an object")
        constraints = _immutable_json(self.payload_constraints)
        for field_name in (
            "exact_human_act_required",
            "cancellation_permitted",
            "interruption_permitted",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(f"{field_name} must be boolean")
        if self.retryability not in ALLOWED_RETRYABILITY:
            raise FailClosedRuntimeError("CHE retryability is invalid")
        if self.recovery_requirement not in ALLOWED_RECOVERY_REQUIREMENTS:
            raise FailClosedRuntimeError("CHE recovery requirement is invalid")
        if self.delivery_resolution_status not in (
            ALLOWED_DELIVERY_RESOLUTION_STATUSES
        ):
            raise FailClosedRuntimeError("CHE delivery resolution status is invalid")
        if self.replay_reference_status not in ALLOWED_REFERENCE_STATUSES:
            raise FailClosedRuntimeError("CHE Replay reference status is invalid")
        if self.certification_reference_status not in ALLOWED_REFERENCE_STATUSES:
            raise FailClosedRuntimeError(
                "CHE Certification reference status is invalid"
            )
        if self.response_disposition in {
            PENDING_DISPOSITION,
            REFUSED_DISPOSITION,
        }:
            if any(
                value is None
                for value in (
                    self.next_act_identity,
                    self.next_act_kind,
                    self.next_act_target_identity,
                    self.next_act_target_digest,
                )
            ) or not controls:
                raise FailClosedRuntimeError(
                    "CHE pending or refused transition requires a complete next act"
                )
        if self.response_disposition == REFUSED_DISPOSITION:
            if self.refusal_identity is None or self.advancement_outcome != (
                REFUSED_ADVANCEMENT
            ):
                raise FailClosedRuntimeError(
                    "CHE refusal transition is incomplete"
                )
        if self.response_disposition == TERMINAL_DISPOSITION:
            if self.terminal_identity is None or self.advancement_outcome != (
                TERMINAL_ADVANCEMENT
            ):
                raise FailClosedRuntimeError(
                    "CHE terminal transition is incomplete"
                )
            if any(
                value is not None
                for value in (
                    self.next_act_identity,
                    self.next_act_kind,
                    self.next_act_target_identity,
                    self.next_act_target_digest,
                )
            ) or controls:
                raise FailClosedRuntimeError(
                    "CHE terminal transition cannot request another act"
                )
        if self.response_disposition == DELIVERY_RESOLUTION_DISPOSITION:
            if self.delivery_resolution_status == DELIVERY_NOT_APPLICABLE:
                raise FailClosedRuntimeError(
                    "CHE delivery resolution status is required"
                )
            if (self.resolved_response_identity is None) != (
                self.resolved_response_hash is None
            ):
                raise FailClosedRuntimeError(
                    "CHE resolved Response identity and hash must be bound together"
                )
        if self.response_disposition != DELIVERY_RESOLUTION_DISPOSITION and (
            self.delivery_resolution_status != DELIVERY_NOT_APPLICABLE
            or self.resolved_response_identity is not None
            or self.resolved_response_hash is not None
        ):
            raise FailClosedRuntimeError(
                "CHE owner transition contains delivery-resolution facts"
            )
        object.__setattr__(self, "permitted_controls", controls)
        object.__setattr__(self, "payload_constraints", constraints)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "producing_owner": self.producing_owner,
            "owner_state_identity": self.owner_state_identity,
            "owner_revision_before": self.owner_revision_before,
            "owner_revision_after": self.owner_revision_after,
            "response_disposition": self.response_disposition,
            "advancement_outcome": self.advancement_outcome,
            "next_act_identity": self.next_act_identity,
            "next_act_kind": self.next_act_kind,
            "next_act_target_identity": self.next_act_target_identity,
            "next_act_target_digest": self.next_act_target_digest,
            "next_act_expected_owner_revision": (
                self.next_act_expected_owner_revision
            ),
            "permitted_controls": list(self.permitted_controls),
            "payload_constraints": _plain_json(self.payload_constraints),
            "exact_human_act_required": self.exact_human_act_required,
            "cancellation_permitted": self.cancellation_permitted,
            "interruption_permitted": self.interruption_permitted,
            "refusal_identity": self.refusal_identity,
            "refusal_type": self.refusal_type,
            "refusal_status": self.refusal_status,
            "terminal_identity": self.terminal_identity,
            "terminal_type": self.terminal_type,
            "terminal_status": self.terminal_status,
            "retryability": self.retryability,
            "recovery_requirement": self.recovery_requirement,
            "delivery_resolution_status": self.delivery_resolution_status,
            "resolved_response_identity": self.resolved_response_identity,
            "resolved_response_hash": self.resolved_response_hash,
            "replay_reference_status": self.replay_reference_status,
            "certification_reference_status": self.certification_reference_status,
        }

    @classmethod
    def from_dict(
        cls, envelope: dict[str, Any]
    ) -> "CanonicalHumanEntryOwnerTransitionV1":
        if not isinstance(envelope, dict) or set(envelope) != (
            _OWNER_TRANSITION_FIELDS
        ):
            raise FailClosedRuntimeError(
                "CHE owner transition structure is invalid"
            )
        return cls(**envelope)


@dataclass(frozen=True, slots=True)
class CanonicalHumanEntryRequestEnvelopeV1:
    """Immutable channel-neutral transport request accepted by CHE."""

    contract_version: str
    interface_identity: str
    adapter_identity: str
    actor_identity: str
    actor_class: str
    session_identity: str
    workspace_identity: str
    runtime_scope_identity: str
    request_identity: str
    source_act_identity: str
    order_identity: str
    idempotency_identity: str
    source_payload: Any
    source_encoding: str
    source_modality: str
    declared_capabilities: tuple[str, ...]
    metadata: Mapping[str, Any]
    created_at: str

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_REQUEST_CONTRACT_VERSION:
            raise FailClosedRuntimeError("CHE request contract version is invalid")
        for field_name in (
            "interface_identity",
            "adapter_identity",
            "actor_identity",
            "session_identity",
            "workspace_identity",
            "runtime_scope_identity",
            "request_identity",
            "source_act_identity",
            "order_identity",
            "idempotency_identity",
            "source_encoding",
            "source_modality",
            "created_at",
        ):
            _require_identity(getattr(self, field_name), field_name)
        if self.actor_class not in ALLOWED_ACTOR_CLASSES:
            raise FailClosedRuntimeError("CHE request actor class is invalid")
        if self.source_modality not in ALLOWED_SOURCE_MODALITIES:
            raise FailClosedRuntimeError("CHE request source modality is invalid")
        if self.source_payload is None:
            raise FailClosedRuntimeError("CHE request source payload is required")
        payload = _immutable_json(self.source_payload)
        capabilities = _immutable_string_tuple(
            self.declared_capabilities, "declared_capabilities"
        )
        _validate_transport_capabilities(capabilities)
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError("CHE request metadata must be an object")
        _validate_request_metadata(self.metadata)
        metadata = _immutable_json(self.metadata)
        canonical_serialize(_plain_json(payload))
        canonical_serialize(_plain_json(metadata))
        object.__setattr__(self, "source_payload", payload)
        object.__setattr__(self, "declared_capabilities", capabilities)
        object.__setattr__(self, "metadata", metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "interface_identity": self.interface_identity,
            "adapter_identity": self.adapter_identity,
            "actor_identity": self.actor_identity,
            "actor_class": self.actor_class,
            "session_identity": self.session_identity,
            "workspace_identity": self.workspace_identity,
            "runtime_scope_identity": self.runtime_scope_identity,
            "request_identity": self.request_identity,
            "source_act_identity": self.source_act_identity,
            "order_identity": self.order_identity,
            "idempotency_identity": self.idempotency_identity,
            "source_payload": _plain_json(self.source_payload),
            "source_encoding": self.source_encoding,
            "source_modality": self.source_modality,
            "declared_capabilities": list(self.declared_capabilities),
            "metadata": _plain_json(self.metadata),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(
        cls, envelope: dict[str, Any]
    ) -> "CanonicalHumanEntryRequestEnvelopeV1":
        if not isinstance(envelope, dict) or set(envelope) != _REQUEST_FIELDS:
            raise FailClosedRuntimeError("CHE request envelope structure is invalid")
        return cls(**envelope)


@dataclass(frozen=True, slots=True)
class CanonicalContinuationEnvelopeV1:
    """Opaque immutable continuation returned by CHE and echoed by a HIC."""

    contract_version: str
    continuation_identity: str
    interaction_identity: str
    conversation_identity: str
    session_identity: str
    actor_identity: str
    workspace_identity: str
    runtime_scope_identity: str
    request_identity: str
    previous_response_identity: str
    previous_order_identity: str
    previous_idempotency_identity: str
    continuation_sequence: int
    expected_next_act_identity: str
    expected_owner_state_identity: str
    expected_owner_revision: int | str
    continuation_state: str
    correlation_identity: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION:
            raise FailClosedRuntimeError(
                "CHE continuation contract version is invalid"
            )
        for field_name in (
            "continuation_identity",
            "interaction_identity",
            "conversation_identity",
            "session_identity",
            "actor_identity",
            "workspace_identity",
            "runtime_scope_identity",
            "request_identity",
            "previous_response_identity",
            "previous_order_identity",
            "previous_idempotency_identity",
            "expected_next_act_identity",
            "expected_owner_state_identity",
            "correlation_identity",
        ):
            _require_identity(getattr(self, field_name), field_name)
        _revision(self.expected_owner_revision, "expected_owner_revision")
        if (
            not isinstance(self.continuation_sequence, int)
            or isinstance(self.continuation_sequence, bool)
            or self.continuation_sequence < 1
        ):
            raise FailClosedRuntimeError(
                "CHE continuation sequence must be a positive integer"
            )
        if self.continuation_state not in ALLOWED_CONTINUATION_STATES:
            raise FailClosedRuntimeError("CHE continuation state is invalid")
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError("CHE continuation metadata must be an object")
        _validate_request_metadata(self.metadata)
        metadata = _immutable_json(self.metadata)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "continuation_identity": self.continuation_identity,
            "interaction_identity": self.interaction_identity,
            "conversation_identity": self.conversation_identity,
            "session_identity": self.session_identity,
            "actor_identity": self.actor_identity,
            "workspace_identity": self.workspace_identity,
            "runtime_scope_identity": self.runtime_scope_identity,
            "request_identity": self.request_identity,
            "previous_response_identity": self.previous_response_identity,
            "previous_order_identity": self.previous_order_identity,
            "previous_idempotency_identity": self.previous_idempotency_identity,
            "continuation_sequence": self.continuation_sequence,
            "expected_next_act_identity": self.expected_next_act_identity,
            "expected_owner_state_identity": self.expected_owner_state_identity,
            "expected_owner_revision": self.expected_owner_revision,
            "continuation_state": self.continuation_state,
            "correlation_identity": self.correlation_identity,
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(cls, envelope: dict[str, Any]) -> "CanonicalContinuationEnvelopeV1":
        if not isinstance(envelope, dict) or set(envelope) != _CONTINUATION_FIELDS:
            raise FailClosedRuntimeError(
                "CHE continuation envelope structure is invalid"
            )
        return cls(**envelope)


@dataclass(frozen=True, slots=True)
class CanonicalHumanEntryResponseEnvelopeV1:
    """Immutable channel-neutral transport response produced by CHE."""

    contract_version: str
    response_identity: str
    request_identity: str
    response_type: str
    producing_owner: str
    owner_status: str
    advancement_state: str
    presentation_payload: Any
    presentation_metadata: Mapping[str, Any]
    correlation_identity: str
    evidence_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    certification_references: tuple[str, ...]
    owner_transition: CanonicalHumanEntryOwnerTransitionV1
    continuation_envelope: CanonicalContinuationEnvelopeV1 | None = None

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_RESPONSE_CONTRACT_VERSION:
            raise FailClosedRuntimeError("CHE response contract version is invalid")
        for field_name in (
            "response_identity",
            "request_identity",
            "producing_owner",
            "owner_status",
            "correlation_identity",
        ):
            _require_identity(getattr(self, field_name), field_name)
        if self.response_type not in ALLOWED_RESPONSE_TYPES:
            raise FailClosedRuntimeError("CHE response type is invalid")
        if self.advancement_state not in ALLOWED_ADVANCEMENT_STATES:
            raise FailClosedRuntimeError("CHE advancement state is invalid")
        transition = (
            CanonicalHumanEntryOwnerTransitionV1.from_dict(self.owner_transition)
            if isinstance(self.owner_transition, dict)
            else self.owner_transition
        )
        if not isinstance(transition, CanonicalHumanEntryOwnerTransitionV1):
            raise FailClosedRuntimeError("CHE owner transition is invalid")
        if transition.producing_owner != self.producing_owner:
            raise FailClosedRuntimeError("CHE producing owner binding is invalid")
        if transition.advancement_outcome != self.advancement_state:
            raise FailClosedRuntimeError("CHE advancement binding is invalid")
        response_type_for_disposition = {
            PENDING_DISPOSITION: PENDING_RESPONSE,
            INFORMATIONAL_DISPOSITION: INFORMATIONAL_RESPONSE,
            REFUSED_DISPOSITION: REFUSAL_RESPONSE,
            TERMINAL_DISPOSITION: TERMINAL_RESPONSE,
            DELIVERY_RESOLUTION_DISPOSITION: INFORMATIONAL_RESPONSE,
        }
        if self.response_type != response_type_for_disposition[
            transition.response_disposition
        ]:
            raise FailClosedRuntimeError("CHE response disposition binding is invalid")
        if isinstance(self.presentation_payload, str):
            payload: Any = self.presentation_payload
        elif isinstance(self.presentation_payload, (list, tuple)) and all(
            isinstance(item, str) for item in self.presentation_payload
        ):
            payload = tuple(self.presentation_payload)
        else:
            raise FailClosedRuntimeError(
                "CHE presentation payload must contain exact presentation text"
            )
        if not isinstance(self.presentation_metadata, Mapping):
            raise FailClosedRuntimeError("CHE presentation metadata must be an object")
        metadata = _immutable_json(self.presentation_metadata)
        object.__setattr__(self, "presentation_payload", payload)
        object.__setattr__(self, "presentation_metadata", metadata)
        object.__setattr__(self, "owner_transition", transition)
        for field_name in (
            "evidence_references",
            "replay_references",
            "certification_references",
        ):
            object.__setattr__(
                self,
                field_name,
                _immutable_string_tuple(getattr(self, field_name), field_name),
            )
        if self.continuation_envelope is not None:
            object.__setattr__(
                self,
                "continuation_envelope",
                validate_canonical_che_continuation_envelope_v1(
                    self.continuation_envelope
                ),
            )
            if self.response_type == TERMINAL_RESPONSE and (
                self.continuation_envelope.continuation_state
                != TERMINAL_CONTINUATION
            ):
                raise FailClosedRuntimeError(
                    "CHE terminal Response cannot carry an active continuation"
                )
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "response_identity": self.response_identity,
            "request_identity": self.request_identity,
            "response_type": self.response_type,
            "producing_owner": self.producing_owner,
            "owner_status": self.owner_status,
            "advancement_state": self.advancement_state,
            "presentation_payload": _plain_json(self.presentation_payload),
            "presentation_metadata": _plain_json(self.presentation_metadata),
            "correlation_identity": self.correlation_identity,
            "evidence_references": list(self.evidence_references),
            "replay_references": list(self.replay_references),
            "certification_references": list(self.certification_references),
            "owner_transition": self.owner_transition.to_dict(),
            "continuation_envelope": (
                self.continuation_envelope.to_dict()
                if self.continuation_envelope is not None
                else None
            ),
        }

    @classmethod
    def from_dict(
        cls, envelope: dict[str, Any]
    ) -> "CanonicalHumanEntryResponseEnvelopeV1":
        if not isinstance(envelope, dict) or set(envelope) != _RESPONSE_FIELDS:
            raise FailClosedRuntimeError("CHE response envelope structure is invalid")
        normalized = dict(envelope)
        owner_transition = normalized.get("owner_transition")
        if isinstance(owner_transition, dict):
            normalized["owner_transition"] = (
                CanonicalHumanEntryOwnerTransitionV1.from_dict(owner_transition)
            )
        else:
            raise FailClosedRuntimeError("CHE response owner transition is invalid")
        continuation = normalized.get("continuation_envelope")
        if isinstance(continuation, dict):
            normalized["continuation_envelope"] = (
                CanonicalContinuationEnvelopeV1.from_dict(continuation)
            )
        elif continuation is not None:
            raise FailClosedRuntimeError(
                "CHE response continuation envelope is invalid"
            )
        return cls(**normalized)


def validate_canonical_che_continuation_envelope_v1(
    envelope: Any,
) -> CanonicalContinuationEnvelopeV1:
    continuation = (
        CanonicalContinuationEnvelopeV1.from_dict(envelope)
        if isinstance(envelope, dict)
        else envelope
    )
    if not isinstance(continuation, CanonicalContinuationEnvelopeV1):
        raise FailClosedRuntimeError("CHE continuation envelope is invalid")
    canonical_serialize(continuation.to_dict())
    return continuation


def validate_canonical_che_delivery_resolution_query_v1(
    envelope: Any,
) -> CanonicalHumanEntryDeliveryResolutionQueryV1:
    query = (
        CanonicalHumanEntryDeliveryResolutionQueryV1.from_dict(envelope)
        if isinstance(envelope, dict)
        else envelope
    )
    if not isinstance(query, CanonicalHumanEntryDeliveryResolutionQueryV1):
        raise FailClosedRuntimeError("CHE delivery resolution query is invalid")
    canonical_serialize(query.to_dict())
    return query


def canonical_che_request_source_act_digest_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
) -> str:
    request = validate_canonical_che_request_envelope_v1(envelope)
    return replay_hash(
        {
            "source_act_identity": request.source_act_identity,
            "source_payload": request.to_dict()["source_payload"],
            "source_encoding": request.source_encoding,
            "source_modality": request.source_modality,
        }
    )


def canonical_che_delivery_resolution_query_from_request_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
) -> CanonicalHumanEntryDeliveryResolutionQueryV1 | None:
    request = validate_canonical_che_request_envelope_v1(envelope)
    if DELIVERY_RESOLUTION_QUERY_CAPABILITY not in request.declared_capabilities:
        return None
    if request.declared_capabilities != (DELIVERY_RESOLUTION_QUERY_CAPABILITY,):
        raise FailClosedRuntimeError(
            "CHE delivery resolution query capability must be exclusive"
        )
    if request.source_modality != "STRUCTURED":
        raise FailClosedRuntimeError(
            "CHE delivery resolution query must use STRUCTURED modality"
        )
    payload = request.to_dict()["source_payload"]
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError(
            "CHE delivery resolution query payload must be an object"
        )
    return validate_canonical_che_delivery_resolution_query_v1(payload)


def validate_canonical_che_request_envelope_v1(
    envelope: Any,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    request = (
        CanonicalHumanEntryRequestEnvelopeV1.from_dict(envelope)
        if isinstance(envelope, dict)
        else envelope
    )
    if not isinstance(request, CanonicalHumanEntryRequestEnvelopeV1):
        raise FailClosedRuntimeError("CHE request envelope is invalid")
    canonical_serialize(request.to_dict())
    return request


def validate_canonical_che_response_envelope_v1(
    envelope: Any,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    response = (
        CanonicalHumanEntryResponseEnvelopeV1.from_dict(envelope)
        if isinstance(envelope, dict)
        else envelope
    )
    if not isinstance(response, CanonicalHumanEntryResponseEnvelopeV1):
        raise FailClosedRuntimeError("CHE response envelope is invalid")
    canonical_serialize(response.to_dict())
    return response


def serialize_canonical_che_request_envelope_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1,
) -> str:
    return canonical_serialize(validate_canonical_che_request_envelope_v1(envelope).to_dict())


def deserialize_canonical_che_request_envelope_v1(
    serialized: str,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    return CanonicalHumanEntryRequestEnvelopeV1.from_dict(
        _deserialize_object(serialized, "CHE request")
    )


def serialize_canonical_che_response_envelope_v1(
    envelope: CanonicalHumanEntryResponseEnvelopeV1,
) -> str:
    return canonical_serialize(validate_canonical_che_response_envelope_v1(envelope).to_dict())


def deserialize_canonical_che_response_envelope_v1(
    serialized: str,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    return CanonicalHumanEntryResponseEnvelopeV1.from_dict(
        _deserialize_object(serialized, "CHE response")
    )


def serialize_canonical_che_continuation_envelope_v1(
    envelope: CanonicalContinuationEnvelopeV1,
) -> str:
    return canonical_serialize(
        validate_canonical_che_continuation_envelope_v1(envelope).to_dict()
    )


def deserialize_canonical_che_continuation_envelope_v1(
    serialized: str,
) -> CanonicalContinuationEnvelopeV1:
    return CanonicalContinuationEnvelopeV1.from_dict(
        _deserialize_object(serialized, "CHE continuation")
    )


def _deserialize_object(serialized: str, label: str) -> dict[str, Any]:
    if not isinstance(serialized, str) or not serialized:
        raise FailClosedRuntimeError(f"{label} serialization is required")
    try:
        value = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"{label} serialization is invalid") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} serialization must be an object")
    return value
