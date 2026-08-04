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
from aigol.runtime.transport.serialization import canonical_serialize


CANONICAL_CHE_REQUEST_CONTRACT_VERSION = (
    "G69_02_CANONICAL_CHE_REQUEST_ENVELOPE_V1"
)
CANONICAL_CHE_RESPONSE_CONTRACT_VERSION = (
    "G69_02_CANONICAL_CHE_RESPONSE_ENVELOPE_V1"
)
CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION = (
    "G69_03_CANONICAL_CHE_CONTINUATION_ENVELOPE_V1"
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

OWNER_RESPONSE = "OWNER_RESPONSE"
INFORMATIONAL_RESPONSE = "INFORMATIONAL"
PENDING_RESPONSE = "PENDING"
REFUSAL_RESPONSE = "REFUSAL"
TERMINAL_RESPONSE = "TERMINAL"
ALLOWED_RESPONSE_TYPES = frozenset(
    {
        OWNER_RESPONSE,
        INFORMATIONAL_RESPONSE,
        PENDING_RESPONSE,
        REFUSAL_RESPONSE,
        TERMINAL_RESPONSE,
    }
)

ADVANCED = "ADVANCED"
NOT_ADVANCED = "NOT_ADVANCED"
UNCHANGED = "UNCHANGED"
UNKNOWN_ADVANCEMENT = "UNKNOWN"
ALLOWED_ADVANCEMENT_STATES = frozenset(
    {ADVANCED, NOT_ADVANCED, UNCHANGED, UNKNOWN_ADVANCEMENT}
)

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
        "continuation_state",
        "correlation_identity",
        "metadata",
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
            "correlation_identity",
        ):
            _require_identity(getattr(self, field_name), field_name)
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
