"""Channel-neutral opaque Reference and ordered reference-set contracts.

The contracts carry owner-issued identity, custody, integrity, availability,
and validation facts.  They contain no referenced content, local path, upload
handle, semantic classification, workflow state, or authority implication.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import re
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_human_entry_contract_v1 import (
    ALLOWED_SOURCE_MODALITIES,
    NOT_APPLICABLE,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION = (
    "G69_08_CANONICAL_OPAQUE_REFERENCE_V1"
)
CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION = (
    "G69_08_CANONICAL_OPAQUE_REFERENCE_SET_V1"
)
CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION = (
    "G69_08_CANONICAL_OPAQUE_REFERENCE_REQUEST_V1"
)
CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY = "OPAQUE_REFERENCE_SET"

DOCUMENT = "DOCUMENT"
ARTIFACT = "ARTIFACT"
DATASET = "DATASET"
IMAGE = "IMAGE"
AUDIO = "AUDIO"
VIDEO = "VIDEO"
STRUCTURED_DATA = "STRUCTURED_DATA"
EXTERNAL_RESOURCE = "EXTERNAL_RESOURCE"
OTHER_DECLARED_REFERENCE = "OTHER_DECLARED_REFERENCE"
CANONICAL_REFERENCE_KINDS = frozenset(
    {
        DOCUMENT,
        ARTIFACT,
        DATASET,
        IMAGE,
        AUDIO,
        VIDEO,
        STRUCTURED_DATA,
        EXTERNAL_RESOURCE,
        OTHER_DECLARED_REFERENCE,
    }
)

AVAILABLE = "AVAILABLE"
MISSING = "MISSING"
INACCESSIBLE = "INACCESSIBLE"
EXPIRED = "EXPIRED"
REVOKED = "REVOKED"
PENDING_VALIDATION = "PENDING_VALIDATION"
INTEGRITY_MISMATCH = "INTEGRITY_MISMATCH"
CANONICAL_REFERENCE_AVAILABILITY_STATUSES = frozenset(
    {
        AVAILABLE,
        MISSING,
        INACCESSIBLE,
        EXPIRED,
        REVOKED,
        PENDING_VALIDATION,
        INTEGRITY_MISMATCH,
    }
)

SHA256 = "SHA256"
SHA512 = "SHA512"
NOT_AVAILABLE = "NOT_AVAILABLE"
CANONICAL_REFERENCE_INTEGRITY_ALGORITHMS = frozenset(
    {SHA256, SHA512, NOT_AVAILABLE, NOT_APPLICABLE, PENDING_VALIDATION}
)

RETRYABLE = "RETRYABLE"
NOT_RETRYABLE = "NOT_RETRYABLE"
CANONICAL_REFERENCE_RETRYABILITY = frozenset(
    {RETRYABLE, NOT_RETRYABLE, NOT_APPLICABLE}
)

PROVIDE_AVAILABLE_REFERENCE = "PROVIDE_AVAILABLE_REFERENCE"
RESTORE_ACCESS = "RESTORE_ACCESS"
PROVIDE_CURRENT_REFERENCE = "PROVIDE_CURRENT_REFERENCE"
REQUEST_NEW_REFERENCE = "REQUEST_NEW_REFERENCE"
OBTAIN_VALIDATION = "OBTAIN_VALIDATION"
PROVIDE_INTEGRITY_MATCHING_REFERENCE = (
    "PROVIDE_INTEGRITY_MATCHING_REFERENCE"
)
CANONICAL_REFERENCE_CORRECTION_REQUIREMENTS = frozenset(
    {
        PROVIDE_AVAILABLE_REFERENCE,
        RESTORE_ACCESS,
        PROVIDE_CURRENT_REFERENCE,
        REQUEST_NEW_REFERENCE,
        OBTAIN_VALIDATION,
        PROVIDE_INTEGRITY_MATCHING_REFERENCE,
        NOT_APPLICABLE,
    }
)

PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER = (
    "PLATFORM_CORE_PROJECT_SERVICES"
)
CANONICAL_REFERENCE_VALIDATION_OWNERS = frozenset(
    {
        PLATFORM_CORE_PROJECT_SERVICES_VALIDATION_OWNER,
    }
)

_REFERENCE_FIELDS = frozenset(
    {
        "contract_version",
        "reference_identity",
        "reference_kind",
        "modality",
        "ordered_position",
        "provenance_identity",
        "content_owner_identity",
        "custody_owner_identity",
        "validation_owner_identity",
        "integrity_algorithm",
        "integrity_reference",
        "availability_status",
        "access_scope_identity",
        "source_channel_identity",
        "source_actor_identity",
        "validation_evidence_identity",
        "validation_evidence_digest",
        "retryability",
        "correction_requirement",
        "created_at",
        "metadata",
    }
)
_REFERENCE_SET_FIELDS = frozenset(
    {
        "contract_version",
        "reference_set_identity",
        "request_identity",
        "source_act_identity",
        "order_identity",
        "interaction_identity",
        "session_identity",
        "actor_identity",
        "workspace_identity",
        "ordered_reference_set_digest",
        "retry_of_source_act_identity",
        "retry_of_order_identity",
        "retry_of_reference_set_digest",
        "references",
        "metadata",
    }
)
_REFERENCE_REQUEST_FIELDS = frozenset(
    {"contract_version", "source_payload", "reference_set"}
)
_FORBIDDEN_METADATA_TOKENS = frozenset(
    {
        "authority",
        "classification",
        "command",
        "content",
        "custody",
        "handle",
        "instruction",
        "owner_state",
        "path",
        "operation",
        "script",
        "semantic",
        "stage",
        "upload",
        "workflow",
    }
)
_CORRECTION_BY_STATUS = {
    AVAILABLE: NOT_APPLICABLE,
    MISSING: PROVIDE_AVAILABLE_REFERENCE,
    INACCESSIBLE: RESTORE_ACCESS,
    EXPIRED: PROVIDE_CURRENT_REFERENCE,
    REVOKED: REQUEST_NEW_REFERENCE,
    PENDING_VALIDATION: OBTAIN_VALIDATION,
    INTEGRITY_MISMATCH: PROVIDE_INTEGRITY_MATCHING_REFERENCE,
}
_RETRYABILITY_BY_STATUS = {
    AVAILABLE: NOT_APPLICABLE,
    MISSING: RETRYABLE,
    INACCESSIBLE: RETRYABLE,
    EXPIRED: RETRYABLE,
    REVOKED: NOT_RETRYABLE,
    PENDING_VALIDATION: RETRYABLE,
    INTEGRITY_MISMATCH: RETRYABLE,
}
_SHA256_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_SHA512_PATTERN = re.compile(r"sha512:[0-9a-f]{128}")


def _identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if value != value.strip():
        raise FailClosedRuntimeError(
            f"{field_name} must not contain boundary whitespace"
        )
    lowered = value.lower()
    if (
        "/" in value
        or "\\" in value
        or ".." in value
        or lowered.startswith("file:")
        or lowered.startswith("upload:")
        or lowered.startswith("handle:")
    ):
        raise FailClosedRuntimeError(
            f"{field_name} must be an opaque identity, not a local path or handle"
        )
    return value


def _required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if value != value.strip():
        raise FailClosedRuntimeError(
            f"{field_name} must not contain boundary whitespace"
        )
    return value


def _immutable_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError(
                "opaque Reference object keys must be strings"
            )
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


def _validate_metadata(metadata: Mapping[str, Any]) -> None:
    for key, value in metadata.items():
        normalized = key.lower().replace("-", "_")
        if not normalized.startswith("transport_") or any(
            token in normalized for token in _FORBIDDEN_METADATA_TOKENS
        ):
            raise FailClosedRuntimeError(
                "opaque Reference metadata must contain transport facts only"
            )
        _validate_metadata_value(value)


def _validate_metadata_value(value: Any) -> None:
    if isinstance(value, Mapping):
        _validate_metadata(value)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_metadata_value(item)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if (
            "/" in value
            or "\\" in value
            or lowered.startswith("file:")
            or lowered.startswith("upload:")
            or lowered.startswith("handle:")
        ):
            raise FailClosedRuntimeError(
                "opaque Reference metadata contains a local path or handle"
            )


def canonical_reference_validation_evidence_digest_v1(
    *,
    reference_identity: str,
    validation_owner_identity: str,
    custody_owner_identity: str,
    availability_status: str,
    integrity_algorithm: str,
    integrity_reference: str,
    access_scope_identity: str,
    validation_evidence_identity: str,
    retryability: str,
    correction_requirement: str,
) -> str:
    return replay_hash(
        {
            "reference_identity": reference_identity,
            "validation_owner_identity": validation_owner_identity,
            "custody_owner_identity": custody_owner_identity,
            "availability_status": availability_status,
            "integrity_algorithm": integrity_algorithm,
            "integrity_reference": integrity_reference,
            "access_scope_identity": access_scope_identity,
            "validation_evidence_identity": validation_evidence_identity,
            "retryability": retryability,
            "correction_requirement": correction_requirement,
        }
    )


@dataclass(frozen=True, slots=True)
class CanonicalOpaqueReferenceV1:
    """One immutable opaque reference with owner-issued validation facts."""

    contract_version: str
    reference_identity: str
    reference_kind: str
    modality: str
    ordered_position: int
    provenance_identity: str
    content_owner_identity: str
    custody_owner_identity: str
    validation_owner_identity: str
    integrity_algorithm: str
    integrity_reference: str
    availability_status: str
    access_scope_identity: str
    source_channel_identity: str
    source_actor_identity: str
    validation_evidence_identity: str
    validation_evidence_digest: str
    retryability: str
    correction_requirement: str
    created_at: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_OPAQUE_REFERENCE_CONTRACT_VERSION:
            raise FailClosedRuntimeError("opaque Reference version is invalid")
        for field_name in (
            "reference_identity",
            "provenance_identity",
            "content_owner_identity",
            "custody_owner_identity",
            "validation_owner_identity",
            "access_scope_identity",
            "source_channel_identity",
            "source_actor_identity",
            "validation_evidence_identity",
            "validation_evidence_digest",
            "created_at",
        ):
            _identity(getattr(self, field_name), field_name)
        if (
            not isinstance(self.reference_kind, str)
            or self.reference_kind not in CANONICAL_REFERENCE_KINDS
        ):
            raise FailClosedRuntimeError("opaque Reference kind is invalid")
        if (
            not isinstance(self.modality, str)
            or self.modality not in ALLOWED_SOURCE_MODALITIES
        ):
            raise FailClosedRuntimeError("opaque Reference modality is invalid")
        if (
            not isinstance(self.ordered_position, int)
            or isinstance(self.ordered_position, bool)
            or self.ordered_position < 1
        ):
            raise FailClosedRuntimeError(
                "opaque Reference ordered position must be positive"
            )
        if self.validation_owner_identity not in (
            CANONICAL_REFERENCE_VALIDATION_OWNERS
        ):
            raise FailClosedRuntimeError(
                "opaque Reference validation owner evidence is unknown"
            )
        if self.source_channel_identity in {
            self.content_owner_identity,
            self.custody_owner_identity,
            self.validation_owner_identity,
        }:
            raise FailClosedRuntimeError(
                "source channel cannot assume Reference ownership"
            )
        if (
            not isinstance(self.integrity_algorithm, str)
            or self.integrity_algorithm
            not in CANONICAL_REFERENCE_INTEGRITY_ALGORITHMS
        ):
            raise FailClosedRuntimeError(
                "opaque Reference integrity algorithm is invalid"
            )
        _validate_integrity_reference(
            self.integrity_algorithm, self.integrity_reference
        )
        if (
            not isinstance(self.availability_status, str)
            or self.availability_status
            not in CANONICAL_REFERENCE_AVAILABILITY_STATUSES
        ):
            raise FailClosedRuntimeError(
                "opaque Reference availability status is invalid"
            )
        if (
            not isinstance(self.retryability, str)
            or self.retryability not in CANONICAL_REFERENCE_RETRYABILITY
        ):
            raise FailClosedRuntimeError(
                "opaque Reference retryability is invalid"
            )
        if (
            not isinstance(self.correction_requirement, str)
            or self.correction_requirement
            not in CANONICAL_REFERENCE_CORRECTION_REQUIREMENTS
        ):
            raise FailClosedRuntimeError(
                "opaque Reference correction requirement is invalid"
            )
        if self.retryability != _RETRYABILITY_BY_STATUS[self.availability_status]:
            raise FailClosedRuntimeError(
                "opaque Reference retryability does not match availability"
            )
        if self.correction_requirement != _CORRECTION_BY_STATUS[
            self.availability_status
        ]:
            raise FailClosedRuntimeError(
                "opaque Reference correction does not match availability"
            )
        if self.availability_status == AVAILABLE and (
            self.integrity_algorithm == PENDING_VALIDATION
        ):
            raise FailClosedRuntimeError(
                "available Reference cannot have pending integrity"
            )
        expected_evidence_digest = (
            canonical_reference_validation_evidence_digest_v1(
                reference_identity=self.reference_identity,
                validation_owner_identity=self.validation_owner_identity,
                custody_owner_identity=self.custody_owner_identity,
                availability_status=self.availability_status,
                integrity_algorithm=self.integrity_algorithm,
                integrity_reference=self.integrity_reference,
                access_scope_identity=self.access_scope_identity,
                validation_evidence_identity=self.validation_evidence_identity,
                retryability=self.retryability,
                correction_requirement=self.correction_requirement,
            )
        )
        if self.validation_evidence_digest != expected_evidence_digest:
            raise FailClosedRuntimeError(
                "opaque Reference validation evidence integrity is invalid"
            )
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError(
                "opaque Reference metadata must be an object"
            )
        _validate_metadata(self.metadata)
        metadata = _immutable_json(self.metadata)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "reference_identity": self.reference_identity,
            "reference_kind": self.reference_kind,
            "modality": self.modality,
            "ordered_position": self.ordered_position,
            "provenance_identity": self.provenance_identity,
            "content_owner_identity": self.content_owner_identity,
            "custody_owner_identity": self.custody_owner_identity,
            "validation_owner_identity": self.validation_owner_identity,
            "integrity_algorithm": self.integrity_algorithm,
            "integrity_reference": self.integrity_reference,
            "availability_status": self.availability_status,
            "access_scope_identity": self.access_scope_identity,
            "source_channel_identity": self.source_channel_identity,
            "source_actor_identity": self.source_actor_identity,
            "validation_evidence_identity": self.validation_evidence_identity,
            "validation_evidence_digest": self.validation_evidence_digest,
            "retryability": self.retryability,
            "correction_requirement": self.correction_requirement,
            "created_at": self.created_at,
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalOpaqueReferenceV1":
        if not isinstance(value, dict) or set(value) != _REFERENCE_FIELDS:
            raise FailClosedRuntimeError("opaque Reference structure is invalid")
        return cls(**value)


def _validate_integrity_reference(algorithm: str, reference: Any) -> None:
    if not isinstance(reference, str) or not reference:
        raise FailClosedRuntimeError(
            "opaque Reference integrity reference is required"
        )
    if algorithm == SHA256 and _SHA256_PATTERN.fullmatch(reference) is None:
        raise FailClosedRuntimeError(
            "opaque Reference SHA256 integrity reference is invalid"
        )
    if algorithm == SHA512 and _SHA512_PATTERN.fullmatch(reference) is None:
        raise FailClosedRuntimeError(
            "opaque Reference SHA512 integrity reference is invalid"
        )
    if algorithm in {NOT_AVAILABLE, NOT_APPLICABLE, PENDING_VALIDATION} and (
        reference != algorithm
    ):
        raise FailClosedRuntimeError(
            "opaque Reference explicit integrity status is invalid"
        )


def validate_canonical_opaque_reference_v1(
    value: Any,
) -> CanonicalOpaqueReferenceV1:
    reference = CanonicalOpaqueReferenceV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(reference, CanonicalOpaqueReferenceV1):
        raise FailClosedRuntimeError("opaque Reference is invalid")
    canonical_serialize(reference.to_dict())
    return reference


def canonical_ordered_reference_set_digest_v1(
    references: list[Any] | tuple[Any, ...],
) -> str:
    if not isinstance(references, (list, tuple)) or not references:
        raise FailClosedRuntimeError("ordered opaque References are required")
    validated = tuple(
        validate_canonical_opaque_reference_v1(item) for item in references
    )
    return replay_hash(
        {"ordered_references": [item.to_dict() for item in validated]}
    )


@dataclass(frozen=True, slots=True)
class CanonicalOpaqueReferenceSetV1:
    """One ordered immutable Reference role bound to a canonical Request."""

    contract_version: str
    reference_set_identity: str
    request_identity: str
    source_act_identity: str
    order_identity: str
    interaction_identity: str
    session_identity: str
    actor_identity: str
    workspace_identity: str
    ordered_reference_set_digest: str
    retry_of_source_act_identity: str | None
    retry_of_order_identity: str | None
    retry_of_reference_set_digest: str | None
    references: tuple[CanonicalOpaqueReferenceV1, ...]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != (
            CANONICAL_OPAQUE_REFERENCE_SET_CONTRACT_VERSION
        ):
            raise FailClosedRuntimeError(
                "opaque Reference set version is invalid"
            )
        for field_name in (
            "reference_set_identity",
            "request_identity",
            "source_act_identity",
            "order_identity",
            "interaction_identity",
            "session_identity",
            "actor_identity",
            "ordered_reference_set_digest",
        ):
            _identity(getattr(self, field_name), field_name)
        _required_text(self.workspace_identity, "workspace_identity")
        if not isinstance(self.references, (list, tuple)) or not self.references:
            raise FailClosedRuntimeError("opaque Reference set is empty")
        references = tuple(
            validate_canonical_opaque_reference_v1(item)
            for item in self.references
        )
        positions = [item.ordered_position for item in references]
        if positions != list(range(1, len(references) + 1)):
            raise FailClosedRuntimeError(
                "opaque Reference ordering is duplicate, missing, or ambiguous"
            )
        identities = [item.reference_identity for item in references]
        if len(identities) != len(set(identities)):
            raise FailClosedRuntimeError(
                "opaque Reference identities conflict within the ordered set"
            )
        expected_digest = canonical_ordered_reference_set_digest_v1(references)
        if self.ordered_reference_set_digest != expected_digest:
            raise FailClosedRuntimeError(
                "opaque Reference ordered-set digest is invalid"
            )
        expected_set_identity = "OPAQUE-REFERENCE-SET-" + expected_digest
        if self.reference_set_identity != expected_set_identity:
            raise FailClosedRuntimeError(
                "opaque Reference set identity is invalid"
            )
        retry_values = (
            self.retry_of_source_act_identity,
            self.retry_of_order_identity,
            self.retry_of_reference_set_digest,
        )
        if any(value is not None for value in retry_values):
            if any(value is None for value in retry_values):
                raise FailClosedRuntimeError(
                    "opaque Reference retry lineage is incomplete"
                )
            for field_name, value in zip(
                (
                    "retry_of_source_act_identity",
                    "retry_of_order_identity",
                    "retry_of_reference_set_digest",
                ),
                retry_values,
            ):
                _identity(value, field_name)
            if (
                self.source_act_identity == self.retry_of_source_act_identity
                or self.order_identity == self.retry_of_order_identity
                or self.ordered_reference_set_digest
                == self.retry_of_reference_set_digest
            ):
                raise FailClosedRuntimeError(
                    "corrected opaque Reference retry must use new identities"
                )
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError(
                "opaque Reference set metadata must be an object"
            )
        _validate_metadata(self.metadata)
        metadata = _immutable_json(self.metadata)
        object.__setattr__(self, "references", references)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "reference_set_identity": self.reference_set_identity,
            "request_identity": self.request_identity,
            "source_act_identity": self.source_act_identity,
            "order_identity": self.order_identity,
            "interaction_identity": self.interaction_identity,
            "session_identity": self.session_identity,
            "actor_identity": self.actor_identity,
            "workspace_identity": self.workspace_identity,
            "ordered_reference_set_digest": self.ordered_reference_set_digest,
            "retry_of_source_act_identity": self.retry_of_source_act_identity,
            "retry_of_order_identity": self.retry_of_order_identity,
            "retry_of_reference_set_digest": (
                self.retry_of_reference_set_digest
            ),
            "references": [item.to_dict() for item in self.references],
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(
        cls, value: dict[str, Any]
    ) -> "CanonicalOpaqueReferenceSetV1":
        if not isinstance(value, dict) or set(value) != _REFERENCE_SET_FIELDS:
            raise FailClosedRuntimeError(
                "opaque Reference set structure is invalid"
            )
        normalized = dict(value)
        references = normalized.get("references")
        if not isinstance(references, list):
            raise FailClosedRuntimeError(
                "opaque Reference set references are invalid"
            )
        normalized["references"] = tuple(
            CanonicalOpaqueReferenceV1.from_dict(item) for item in references
        )
        return cls(**normalized)


def validate_canonical_opaque_reference_set_v1(
    value: Any,
) -> CanonicalOpaqueReferenceSetV1:
    reference_set = CanonicalOpaqueReferenceSetV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(reference_set, CanonicalOpaqueReferenceSetV1):
        raise FailClosedRuntimeError("opaque Reference set is invalid")
    canonical_serialize(reference_set.to_dict())
    return reference_set


def canonical_opaque_reference_set_from_request_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
    continuation: CanonicalContinuationEnvelopeV1 | dict[str, Any] | None,
) -> CanonicalOpaqueReferenceSetV1 | None:
    request = validate_canonical_che_request_envelope_v1(envelope)
    payload = request.to_dict()["source_payload"]
    if CANONICAL_OPAQUE_REFERENCE_SET_CAPABILITY not in (
        request.declared_capabilities
    ):
        if isinstance(payload, dict) and (
            payload.get("contract_version")
            == CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION
            or "reference_set" in payload
        ):
            raise FailClosedRuntimeError(
                "opaque Reference Request capability is absent"
            )
        return None
    if "HUMAN_AUTHORITY_ACT" in request.declared_capabilities:
        raise FailClosedRuntimeError(
            "opaque Reference presence cannot transport Human Authority"
        )
    if not isinstance(payload, dict) or set(payload) != _REFERENCE_REQUEST_FIELDS:
        raise FailClosedRuntimeError(
            "opaque Reference Request payload structure is invalid"
        )
    if payload.get("contract_version") != (
        CANONICAL_OPAQUE_REFERENCE_REQUEST_VERSION
    ):
        raise FailClosedRuntimeError(
            "opaque Reference Request payload version is invalid"
        )
    if payload.get("source_payload") is None:
        raise FailClosedRuntimeError(
            "opaque Reference Request source payload is required"
        )
    reference_set = validate_canonical_opaque_reference_set_v1(
        payload.get("reference_set")
    )
    supplied_continuation = (
        validate_canonical_che_continuation_envelope_v1(continuation)
        if continuation is not None
        else None
    )
    expected_interaction = (
        supplied_continuation.interaction_identity
        if supplied_continuation is not None
        else NOT_APPLICABLE
    )
    bindings = (
        (reference_set.request_identity, request.request_identity, "Request"),
        (
            reference_set.source_act_identity,
            request.source_act_identity,
            "source act",
        ),
        (reference_set.order_identity, request.order_identity, "order"),
        (
            reference_set.interaction_identity,
            expected_interaction,
            "interaction",
        ),
        (reference_set.session_identity, request.session_identity, "session"),
        (reference_set.actor_identity, request.actor_identity, "actor"),
        (
            reference_set.workspace_identity,
            request.workspace_identity,
            "workspace",
        ),
    )
    for actual, expected, label in bindings:
        if actual != expected:
            raise FailClosedRuntimeError(
                f"opaque Reference {label} binding is invalid"
            )
    for reference in reference_set.references:
        if reference.source_channel_identity != request.interface_identity:
            raise FailClosedRuntimeError(
                "opaque Reference source channel binding is invalid"
            )
        if reference.source_actor_identity != request.actor_identity:
            raise FailClosedRuntimeError(
                "opaque Reference source actor binding is invalid"
            )
    return reference_set


def canonical_opaque_reference_source_payload_from_request_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
) -> Any:
    request = validate_canonical_che_request_envelope_v1(envelope)
    payload = request.to_dict()["source_payload"]
    if not isinstance(payload, dict) or set(payload) != _REFERENCE_REQUEST_FIELDS:
        raise FailClosedRuntimeError(
            "opaque Reference Request payload structure is invalid"
        )
    return deepcopy(payload["source_payload"])


def serialize_canonical_opaque_reference_v1(
    value: CanonicalOpaqueReferenceV1,
) -> str:
    validated = validate_canonical_opaque_reference_v1(value)
    return canonical_serialize(validated.to_dict())


def deserialize_canonical_opaque_reference_v1(
    serialized: str,
) -> CanonicalOpaqueReferenceV1:
    return CanonicalOpaqueReferenceV1.from_dict(
        _deserialize_object(serialized, "opaque Reference")
    )


def serialize_canonical_opaque_reference_set_v1(
    value: CanonicalOpaqueReferenceSetV1,
) -> str:
    validated = validate_canonical_opaque_reference_set_v1(value)
    return canonical_serialize(validated.to_dict())


def deserialize_canonical_opaque_reference_set_v1(
    serialized: str,
) -> CanonicalOpaqueReferenceSetV1:
    return CanonicalOpaqueReferenceSetV1.from_dict(
        _deserialize_object(serialized, "opaque Reference set")
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
