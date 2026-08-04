"""Channel-neutral transport contract for authenticated Human Authority acts.

The contract carries one Human decision through Canonical Human Entry (CHE).
It does not interpret the decision, decide its correctness, select a workflow,
or transfer responsibility from the constitutional owner named by the act.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION = (
    "G69_07_CANONICAL_HUMAN_AUTHORITY_ACT_V1"
)
CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY = "HUMAN_AUTHORITY_ACT"
HUMAN_AUTHORITY_OWNER = "HUMAN_AUTHORITY"

CLARIFICATION_RESPONSE = "CLARIFICATION_RESPONSE"
CONFIRMATION = "CONFIRMATION"
COMMITMENT = "COMMITMENT"
APPROVAL = "APPROVAL"
AUTHORIZATION = "AUTHORIZATION"
ACCEPT = "ACCEPT"
REJECT = "REJECT"
CANCEL = "CANCEL"
REWORK = "REWORK"
CONTINUE = "CONTINUE"

CANONICAL_HUMAN_AUTHORITY_KINDS = frozenset(
    {
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
)

_AUTHORITY_ACT_FIELDS = frozenset(
    {
        "contract_version",
        "authority_act_identity",
        "authority_kind",
        "interaction_identity",
        "conversation_identity",
        "session_identity",
        "actor_identity",
        "request_identity",
        "continuation_identity",
        "target_identity",
        "target_revision",
        "producing_owner",
        "expected_owner",
        "authority_scope",
        "payload",
        "payload_digest",
        "metadata",
    }
)


def _identity(value: Any, field_name: str) -> str:
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
                "Human Authority Act object keys must be strings"
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


def canonical_human_authority_payload_digest_v1(payload: Any) -> str:
    """Return the deterministic digest of the exact canonical payload."""

    if payload is None:
        raise FailClosedRuntimeError("Human Authority Act payload is required")
    canonical_serialize(_plain_json(payload))
    return replay_hash({"payload": _plain_json(payload)})


@dataclass(frozen=True, slots=True)
class CanonicalHumanAuthorityActV1:
    """One immutable authenticated Human decision transport artifact."""

    contract_version: str
    authority_act_identity: str
    authority_kind: str
    interaction_identity: str
    conversation_identity: str
    session_identity: str
    actor_identity: str
    request_identity: str
    continuation_identity: str
    target_identity: str
    target_revision: int
    producing_owner: str
    expected_owner: str
    authority_scope: str
    payload: Any
    payload_digest: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION:
            raise FailClosedRuntimeError(
                "Human Authority Act contract version is invalid"
            )
        for field_name in (
            "authority_act_identity",
            "interaction_identity",
            "conversation_identity",
            "session_identity",
            "actor_identity",
            "request_identity",
            "continuation_identity",
            "target_identity",
            "producing_owner",
            "expected_owner",
            "authority_scope",
            "payload_digest",
        ):
            _identity(getattr(self, field_name), field_name)
        if (
            not isinstance(self.authority_kind, str)
            or self.authority_kind not in CANONICAL_HUMAN_AUTHORITY_KINDS
        ):
            raise FailClosedRuntimeError("Human Authority Act kind is invalid")
        if self.producing_owner != HUMAN_AUTHORITY_OWNER:
            raise FailClosedRuntimeError(
                "Human Authority Act producing owner is invalid"
            )
        if (
            not isinstance(self.target_revision, int)
            or isinstance(self.target_revision, bool)
            or self.target_revision < 0
        ):
            raise FailClosedRuntimeError(
                "Human Authority Act target revision is invalid"
            )
        if self.payload is None:
            raise FailClosedRuntimeError("Human Authority Act payload is required")
        payload = _immutable_json(self.payload)
        if self.payload_digest != canonical_human_authority_payload_digest_v1(
            payload
        ):
            raise FailClosedRuntimeError(
                "Human Authority Act payload digest is invalid"
            )
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError(
                "Human Authority Act metadata must be an object"
            )
        metadata = _immutable_json(self.metadata)
        object.__setattr__(self, "payload", payload)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "authority_act_identity": self.authority_act_identity,
            "authority_kind": self.authority_kind,
            "interaction_identity": self.interaction_identity,
            "conversation_identity": self.conversation_identity,
            "session_identity": self.session_identity,
            "actor_identity": self.actor_identity,
            "request_identity": self.request_identity,
            "continuation_identity": self.continuation_identity,
            "target_identity": self.target_identity,
            "target_revision": self.target_revision,
            "producing_owner": self.producing_owner,
            "expected_owner": self.expected_owner,
            "authority_scope": self.authority_scope,
            "payload": _plain_json(self.payload),
            "payload_digest": self.payload_digest,
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalHumanAuthorityActV1":
        if not isinstance(value, dict) or set(value) != _AUTHORITY_ACT_FIELDS:
            raise FailClosedRuntimeError(
                "Human Authority Act structure is invalid"
            )
        return cls(**value)


def validate_canonical_human_authority_act_v1(
    value: Any,
) -> CanonicalHumanAuthorityActV1:
    act = CanonicalHumanAuthorityActV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(act, CanonicalHumanAuthorityActV1):
        raise FailClosedRuntimeError("Human Authority Act is invalid")
    canonical_serialize(act.to_dict())
    return act


def serialize_canonical_human_authority_act_v1(
    value: CanonicalHumanAuthorityActV1,
) -> str:
    validated = validate_canonical_human_authority_act_v1(value)
    return canonical_serialize(validated.to_dict())


def deserialize_canonical_human_authority_act_v1(
    serialized: str,
) -> CanonicalHumanAuthorityActV1:
    if not isinstance(serialized, str) or not serialized:
        raise FailClosedRuntimeError(
            "Human Authority Act serialization is required"
        )
    try:
        value = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "Human Authority Act serialization is invalid"
        ) from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(
            "Human Authority Act serialization must be an object"
        )
    return CanonicalHumanAuthorityActV1.from_dict(value)


def canonical_human_authority_act_from_request_v1(
    envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
) -> CanonicalHumanAuthorityActV1 | None:
    """Read the exclusive structured act capability from the CHE envelope."""

    request = validate_canonical_che_request_envelope_v1(envelope)
    if CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY not in (
        request.declared_capabilities
    ):
        return None
    if request.declared_capabilities != (
        CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    ):
        raise FailClosedRuntimeError(
            "Human Authority Act capability must be exclusive"
        )
    if request.source_modality != "STRUCTURED":
        raise FailClosedRuntimeError(
            "Human Authority Act must use STRUCTURED modality"
        )
    payload = request.to_dict()["source_payload"]
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError(
            "Human Authority Act request payload must be an object"
        )
    return validate_canonical_human_authority_act_v1(payload)


def bind_canonical_human_authority_act_to_che_v1(
    act_value: CanonicalHumanAuthorityActV1 | dict[str, Any],
    request_value: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
    continuation_value: CanonicalContinuationEnvelopeV1 | dict[str, Any],
    *,
    expected_authority_kind: str,
    expected_target_identity: str,
    expected_target_revision: int,
    expected_producing_owner: str,
    expected_owner: str,
    expected_authority_scope: str,
) -> CanonicalHumanAuthorityActV1:
    """Fail closed unless one act matches exact CHE and owner-issued bindings."""

    act = validate_canonical_human_authority_act_v1(act_value)
    request = validate_canonical_che_request_envelope_v1(request_value)
    request_act = canonical_human_authority_act_from_request_v1(request)
    if request_act is None or request_act.to_dict() != act.to_dict():
        raise FailClosedRuntimeError(
            "Human Authority Act Request payload binding is invalid"
        )
    continuation = validate_canonical_che_continuation_envelope_v1(
        continuation_value
    )
    if continuation.continuation_state != ACTIVE_CONTINUATION:
        raise FailClosedRuntimeError(
            "Human Authority Act cannot target a terminal continuation"
        )
    if request.actor_class != HUMAN_ACTOR:
        raise FailClosedRuntimeError(
            "Human Authority Act requires an authenticated Human actor"
        )
    bindings = (
        (act.authority_act_identity, request.source_act_identity, "identity"),
        (act.request_identity, request.request_identity, "request"),
        (act.interaction_identity, continuation.interaction_identity, "interaction"),
        (act.conversation_identity, continuation.conversation_identity, "Conversation"),
        (act.session_identity, request.session_identity, "session"),
        (act.session_identity, continuation.session_identity, "continuation session"),
        (act.actor_identity, request.actor_identity, "actor"),
        (act.actor_identity, continuation.actor_identity, "continuation actor"),
        (
            act.continuation_identity,
            continuation.continuation_identity,
            "continuation",
        ),
        (
            act.target_identity,
            continuation.expected_next_act_identity,
            "continuation target",
        ),
        (act.target_identity, expected_target_identity, "target"),
        (act.authority_kind, expected_authority_kind, "kind"),
        (act.producing_owner, expected_producing_owner, "producing owner"),
        (act.expected_owner, expected_owner, "expected owner"),
        (act.authority_scope, expected_authority_scope, "scope"),
    )
    for actual, expected, label in bindings:
        if actual != expected:
            raise FailClosedRuntimeError(
                f"Human Authority Act {label} binding is invalid"
            )
    if act.target_revision != continuation.expected_owner_revision:
        raise FailClosedRuntimeError("Human Authority Act revision is stale")
    if act.target_revision != expected_target_revision:
        raise FailClosedRuntimeError(
            "Human Authority Act owner revision binding is invalid"
        )
    return act
