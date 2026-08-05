"""Channel-neutral constitutional owner-outcome transport contracts.

Owners decide and produce outcome facts.  Canonical Human Entry (CHE) binds
and transports those facts.  A Human Interaction Channel (HIC) may render the
canonical Presentation and capture the next Human act, but it may not infer
failure meaning, workflow state, controls, or owner semantics.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import re
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_COMMON_FAILURE_CONTRACT_VERSION = (
    "G69_10_CANONICAL_COMMON_FAILURE_V1"
)
CANONICAL_PRESENTATION_CONTRACT_VERSION = (
    "G69_10_CANONICAL_PRESENTATION_V1"
)
CANONICAL_OWNER_PROJECTION_CONTRACT_VERSION = (
    "G69_10_CANONICAL_OWNER_PROJECTION_V1"
)

NOT_APPLICABLE = "NOT_APPLICABLE"

ADVANCED = "ADVANCED"
NOT_ADVANCED = "NOT_ADVANCED"
TERMINAL = "TERMINAL"
REFUSED = "REFUSED"
DELIVERY_OUTCOME_UNKNOWN = "DELIVERY_OUTCOME_UNKNOWN"
CANONICAL_OWNER_ADVANCEMENTS = frozenset(
    {ADVANCED, NOT_ADVANCED, TERMINAL, REFUSED, DELIVERY_OUTCOME_UNKNOWN}
)

PENDING = "PENDING"
INFORMATIONAL = "INFORMATIONAL"
FAILURE = "FAILURE"
TERMINAL_PRESENTATION = "TERMINAL"
CANONICAL_PRESENTATION_STATES = frozenset(
    {PENDING, INFORMATIONAL, FAILURE, TERMINAL_PRESENTATION}
)

OWNER_OUTCOME = "OWNER_OUTCOME"
NEXT_ACT = "NEXT_ACT"
COMMON_FAILURE = "COMMON_FAILURE"
TERMINAL_OUTCOME = "TERMINAL_OUTCOME"
DELIVERY_RESOLUTION = "DELIVERY_RESOLUTION"
CANONICAL_PRESENTATION_KINDS = frozenset(
    {
        OWNER_OUTCOME,
        NEXT_ACT,
        COMMON_FAILURE,
        TERMINAL_OUTCOME,
        DELIVERY_RESOLUTION,
    }
)

LOW = "LOW"
NORMAL = "NORMAL"
HIGH = "HIGH"
CRITICAL = "CRITICAL"
CANONICAL_PRESENTATION_PRIORITIES = frozenset({LOW, NORMAL, HIGH, CRITICAL})

HUMAN_VISIBLE = "HUMAN_VISIBLE"
ELIGIBLE_SOURCE_VISIBLE = "ELIGIBLE_SOURCE_VISIBLE"
HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE = "HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE"
CANONICAL_PRESENTATION_VISIBILITIES = frozenset(
    {
        HUMAN_VISIBLE,
        ELIGIBLE_SOURCE_VISIBLE,
        HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE,
    }
)

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL_SEVERITY = "CRITICAL"
CANONICAL_FAILURE_SEVERITIES = frozenset(
    {INFO, WARNING, ERROR, CRITICAL_SEVERITY}
)

RECOVERABLE = "RECOVERABLE"
NON_RECOVERABLE = "NON_RECOVERABLE"
RECOVERY_UNKNOWN = "RECOVERY_UNKNOWN"
CANONICAL_FAILURE_RECOVERABILITY = frozenset(
    {RECOVERABLE, NON_RECOVERABLE, RECOVERY_UNKNOWN}
)

RETRYABLE = "RETRYABLE"
NOT_RETRYABLE = "NOT_RETRYABLE"
RETRY_NOT_APPLICABLE = NOT_APPLICABLE
CANONICAL_FAILURE_RETRYABILITY = frozenset(
    {RETRYABLE, NOT_RETRYABLE, RETRY_NOT_APPLICABLE}
)

MALFORMED_INPUT = "MALFORMED_INPUT"
INVALID_OR_STALE_CONTINUATION = "INVALID_OR_STALE_CONTINUATION"
DUPLICATE_SOURCE_ACT = "DUPLICATE_SOURCE_ACT"
IDENTITY_CONTENT_CONFLICT = "IDENTITY_CONTENT_CONFLICT"
UNKNOWN_DELIVERY = "UNKNOWN_DELIVERY"
OWNER_REFUSAL = "OWNER_REFUSAL"
UNSUPPORTED_ACT = "UNSUPPORTED_ACT"
OWNER_UNAVAILABLE = "OWNER_UNAVAILABLE"
INCOMPLETE_OWNER_RESPONSE = "INCOMPLETE_OWNER_RESPONSE"
EVIDENCE_WRITE_FAILURE = "EVIDENCE_WRITE_FAILURE"
PRE_WRITE_FAILURE = "PRE_WRITE_FAILURE"
TRANSPORT_INTERRUPTION = "TRANSPORT_INTERRUPTION"
REFERENCE_UNAVAILABLE = "REFERENCE_UNAVAILABLE"
OWNER_FAILURE = "OWNER_FAILURE"
CANONICAL_FAILURE_KINDS = frozenset(
    {
        MALFORMED_INPUT,
        INVALID_OR_STALE_CONTINUATION,
        DUPLICATE_SOURCE_ACT,
        IDENTITY_CONTENT_CONFLICT,
        UNKNOWN_DELIVERY,
        OWNER_REFUSAL,
        UNSUPPORTED_ACT,
        OWNER_UNAVAILABLE,
        INCOMPLETE_OWNER_RESPONSE,
        EVIDENCE_WRITE_FAILURE,
        PRE_WRITE_FAILURE,
        TRANSPORT_INTERRUPTION,
        REFERENCE_UNAVAILABLE,
        OWNER_FAILURE,
    }
)

_OWNER_NEXT_ACT_FIELDS = frozenset(
    {
        "next_act_identity",
        "next_act_kind",
        "target_identity",
        "target_digest",
        "expected_owner_revision",
        "permitted_controls",
        "payload_constraints",
        "exact_human_act_required",
        "cancellation_permitted",
        "interruption_permitted",
    }
)
_OWNER_TERMINAL_FIELDS = frozenset(
    {"terminal", "terminal_identity", "terminal_type", "terminal_status"}
)
_OWNER_CONTINUATION_FIELDS = frozenset(
    {
        "continuation_identity",
        "continuation_state",
        "expected_next_act_identity",
        "expected_owner_state_identity",
        "expected_owner_revision",
    }
)
_PRESENTATION_ACCESSIBILITY_FIELDS = frozenset(
    {
        "ordered_text_available",
        "structured_facts_available",
        "language",
        "reading_order",
    }
)
_OWNER_PROJECTION_FIELDS = frozenset(
    {
        "contract_version",
        "projection_identity",
        "request_identity",
        "response_identity",
        "owner_identity",
        "owner_state",
        "owner_next_act",
        "owner_advancement",
        "owner_revision_before",
        "owner_revision",
        "owner_terminal_state",
        "owner_continuation",
        "owner_result_projection",
        "metadata",
    }
)
_PRESENTATION_FIELDS = frozenset(
    {
        "contract_version",
        "presentation_identity",
        "request_identity",
        "response_identity",
        "presentation_state",
        "presentation_kind",
        "presentation_message",
        "presentation_controls",
        "presentation_priority",
        "presentation_visibility",
        "presentation_accessibility",
        "presentation_metadata",
    }
)
_FAILURE_FIELDS = frozenset(
    {
        "contract_version",
        "failure_identity",
        "failure_kind",
        "failure_scope",
        "failure_owner",
        "severity",
        "recoverability",
        "retryability",
        "failure_reason",
        "owner_projection",
        "continuation",
        "revision",
        "request_identity",
        "response_identity",
        "presentation_identity",
        "metadata",
    }
)
_FORBIDDEN_PRESENTATION_TOKENS = frozenset(
    {
        "browser_control",
        "cli_format",
        "gui_layout",
        "html",
        "speech_rendering",
        "terminal_escape",
        "visual_layout",
    }
)
_FORBIDDEN_OWNER_RESULT_TOKENS = frozenset(
    {
        "full_state",
        "internal_state",
        "owner_artifact_graph",
        "private_state",
        "raw_owner_result",
        "runtime_state",
    }
)
_HTML_TAG_PATTERN = re.compile(
    r"<\s*/?\s*(?:html|body|button|div|span|script|style|form|input|img|a|p|ul|ol|li)(?:\s|>|/)",
    re.IGNORECASE,
)


def _identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if value != value.strip():
        raise FailClosedRuntimeError(
            f"{field_name} must not contain boundary whitespace"
        )
    return value


def _revision(value: Any, field_name: str) -> int | str:
    if value == NOT_APPLICABLE:
        return value
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(
            f"{field_name} must be a non-negative revision or NOT_APPLICABLE"
        )
    return value


def _immutable_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError(
                "canonical outcome object keys must be strings"
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


def _string_tuple(value: Any, field_name: str, *, required: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{field_name} must be an ordered list")
    result = tuple(_identity(item, field_name) for item in value)
    if required and not result:
        raise FailClosedRuntimeError(f"{field_name} must not be empty")
    if len(set(result)) != len(result):
        raise FailClosedRuntimeError(f"{field_name} must not contain duplicates")
    return result


def _validate_forbidden_keys(
    value: Any, forbidden: frozenset[str], failure_message: str
) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if any(token in normalized for token in forbidden):
                raise FailClosedRuntimeError(failure_message)
            _validate_forbidden_keys(item, forbidden, failure_message)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_forbidden_keys(item, forbidden, failure_message)


def _validate_presentation_messages(messages: tuple[str, ...]) -> None:
    for message in messages:
        if "\x1b" in message or _HTML_TAG_PATTERN.search(message):
            raise FailClosedRuntimeError(
                "canonical Presentation contains channel-specific rendering logic"
            )


def _canonical_identity(prefix: str, facts: Mapping[str, Any]) -> str:
    return prefix + replay_hash(_plain_json(facts)).removeprefix("sha256:")


def _owner_projection_facts(
    *,
    request_identity: str,
    response_identity: str,
    owner_identity: str,
    owner_state: str,
    owner_next_act: Mapping[str, Any],
    owner_advancement: str,
    owner_revision_before: int | str,
    owner_revision: int | str,
    owner_terminal_state: Mapping[str, Any],
    owner_continuation: Mapping[str, Any],
    owner_result_projection: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "contract_version": CANONICAL_OWNER_PROJECTION_CONTRACT_VERSION,
        "request_identity": request_identity,
        "response_identity": response_identity,
        "owner_identity": owner_identity,
        "owner_state": owner_state,
        "owner_next_act": _plain_json(owner_next_act),
        "owner_advancement": owner_advancement,
        "owner_revision_before": owner_revision_before,
        "owner_revision": owner_revision,
        "owner_terminal_state": _plain_json(owner_terminal_state),
        "owner_continuation": _plain_json(owner_continuation),
        "owner_result_projection": _plain_json(owner_result_projection),
        "metadata": _plain_json(metadata),
    }


@dataclass(frozen=True, slots=True)
class CanonicalOwnerProjectionV1:
    """Deterministic constitutional facts exposed by one producing owner."""

    contract_version: str
    projection_identity: str
    request_identity: str
    response_identity: str
    owner_identity: str
    owner_state: str
    owner_next_act: Mapping[str, Any]
    owner_advancement: str
    owner_revision_before: int | str
    owner_revision: int | str
    owner_terminal_state: Mapping[str, Any]
    owner_continuation: Mapping[str, Any]
    owner_result_projection: Mapping[str, Any]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_OWNER_PROJECTION_CONTRACT_VERSION:
            raise FailClosedRuntimeError("canonical Owner Projection version is invalid")
        for field_name in (
            "projection_identity",
            "request_identity",
            "response_identity",
            "owner_identity",
            "owner_state",
        ):
            _identity(getattr(self, field_name), field_name)
        if self.owner_advancement not in CANONICAL_OWNER_ADVANCEMENTS:
            raise FailClosedRuntimeError("canonical Owner advancement is invalid")
        before = _revision(self.owner_revision_before, "owner_revision_before")
        after = _revision(self.owner_revision, "owner_revision")
        if isinstance(before, int) and isinstance(after, int) and after < before:
            raise FailClosedRuntimeError("canonical Owner Projection is stale")
        for field_name in (
            "owner_next_act",
            "owner_terminal_state",
            "owner_continuation",
            "owner_result_projection",
            "metadata",
        ):
            if not isinstance(getattr(self, field_name), Mapping):
                raise FailClosedRuntimeError(f"{field_name} must be an object")
        next_act = _immutable_json(self.owner_next_act)
        terminal_state = _immutable_json(self.owner_terminal_state)
        continuation = _immutable_json(self.owner_continuation)
        result_projection = _immutable_json(self.owner_result_projection)
        metadata = _immutable_json(self.metadata)
        if set(next_act) != _OWNER_NEXT_ACT_FIELDS:
            raise FailClosedRuntimeError("canonical Owner next act is incomplete")
        if set(terminal_state) != _OWNER_TERMINAL_FIELDS:
            raise FailClosedRuntimeError("canonical Owner terminal state is incomplete")
        if set(continuation) != _OWNER_CONTINUATION_FIELDS:
            raise FailClosedRuntimeError("canonical Owner continuation is incomplete")
        controls = _string_tuple(
            next_act["permitted_controls"], "permitted_controls"
        )
        payload_constraints = next_act["payload_constraints"]
        if not isinstance(payload_constraints, Mapping):
            raise FailClosedRuntimeError("owner next-act payload constraints are invalid")
        for key in (
            "exact_human_act_required",
            "cancellation_permitted",
            "interruption_permitted",
        ):
            if not isinstance(next_act[key], bool):
                raise FailClosedRuntimeError(f"{key} must be boolean")
        next_revision = _revision(
            next_act["expected_owner_revision"], "next_act expected revision"
        )
        continuation_revision = _revision(
            continuation["expected_owner_revision"],
            "continuation expected owner revision",
        )
        if next_act["next_act_identity"] != NOT_APPLICABLE:
            for key in (
                "next_act_identity",
                "next_act_kind",
                "target_identity",
                "target_digest",
            ):
                _identity(next_act[key], key)
            if next_revision != after or not controls:
                raise FailClosedRuntimeError(
                    "canonical Owner next act revision is stale"
                )
        elif controls or any(
            next_act[key] != NOT_APPLICABLE
            for key in ("next_act_kind", "target_identity", "target_digest")
        ):
            raise FailClosedRuntimeError(
                "canonical Owner next act absence is inconsistent"
            )
        if not isinstance(terminal_state["terminal"], bool):
            raise FailClosedRuntimeError("canonical terminal flag must be boolean")
        if terminal_state["terminal"]:
            for key in ("terminal_identity", "terminal_type", "terminal_status"):
                _identity(terminal_state[key], key)
            if next_act["next_act_identity"] != NOT_APPLICABLE:
                raise FailClosedRuntimeError(
                    "terminal Owner Projection cannot request a next act"
                )
        elif any(
            terminal_state[key] != NOT_APPLICABLE
            for key in ("terminal_identity", "terminal_type", "terminal_status")
        ):
            raise FailClosedRuntimeError(
                "non-terminal Owner Projection contains terminal facts"
            )
        if continuation["continuation_identity"] != NOT_APPLICABLE:
            for key in (
                "continuation_identity",
                "continuation_state",
                "expected_next_act_identity",
                "expected_owner_state_identity",
            ):
                _identity(continuation[key], key)
            if continuation_revision != after:
                raise FailClosedRuntimeError(
                    "canonical Owner continuation projection is stale"
                )
            if continuation["expected_owner_state_identity"] != self.owner_state:
                raise FailClosedRuntimeError(
                    "canonical Owner continuation state binding is invalid"
                )
        elif any(
            continuation[key] != NOT_APPLICABLE
            for key in (
                "continuation_state",
                "expected_next_act_identity",
                "expected_owner_state_identity",
                "expected_owner_revision",
            )
        ):
            raise FailClosedRuntimeError(
                "canonical Owner continuation absence is inconsistent"
            )
        _validate_forbidden_keys(
            result_projection,
            _FORBIDDEN_OWNER_RESULT_TOKENS,
            "canonical Owner Projection exposes owner-internal runtime state",
        )
        normalized_next_act = dict(_plain_json(next_act))
        normalized_next_act["permitted_controls"] = list(controls)
        normalized_next_act["payload_constraints"] = _plain_json(
            payload_constraints
        )
        next_act = _immutable_json(normalized_next_act)
        facts = _owner_projection_facts(
            request_identity=self.request_identity,
            response_identity=self.response_identity,
            owner_identity=self.owner_identity,
            owner_state=self.owner_state,
            owner_next_act=next_act,
            owner_advancement=self.owner_advancement,
            owner_revision_before=self.owner_revision_before,
            owner_revision=self.owner_revision,
            owner_terminal_state=terminal_state,
            owner_continuation=continuation,
            owner_result_projection=result_projection,
            metadata=metadata,
        )
        expected_identity = _canonical_identity(
            "CANONICAL-OWNER-PROJECTION-", facts
        )
        if self.projection_identity != expected_identity:
            raise FailClosedRuntimeError(
                "canonical Owner Projection identity is invalid"
            )
        object.__setattr__(self, "owner_next_act", next_act)
        object.__setattr__(self, "owner_terminal_state", terminal_state)
        object.__setattr__(self, "owner_continuation", continuation)
        object.__setattr__(self, "owner_result_projection", result_projection)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "projection_identity": self.projection_identity,
            "request_identity": self.request_identity,
            "response_identity": self.response_identity,
            "owner_identity": self.owner_identity,
            "owner_state": self.owner_state,
            "owner_next_act": _plain_json(self.owner_next_act),
            "owner_advancement": self.owner_advancement,
            "owner_revision_before": self.owner_revision_before,
            "owner_revision": self.owner_revision,
            "owner_terminal_state": _plain_json(self.owner_terminal_state),
            "owner_continuation": _plain_json(self.owner_continuation),
            "owner_result_projection": _plain_json(self.owner_result_projection),
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalOwnerProjectionV1":
        if not isinstance(value, dict) or set(value) != _OWNER_PROJECTION_FIELDS:
            raise FailClosedRuntimeError(
                "canonical Owner Projection structure is invalid"
            )
        return cls(**value)


def create_canonical_owner_projection_v1(
    *,
    request_identity: str,
    response_identity: str,
    owner_identity: str,
    owner_state: str,
    owner_next_act: Mapping[str, Any],
    owner_advancement: str,
    owner_revision_before: int | str,
    owner_revision: int | str,
    owner_terminal_state: Mapping[str, Any],
    owner_continuation: Mapping[str, Any],
    owner_result_projection: Mapping[str, Any],
    metadata: Mapping[str, Any] | None = None,
) -> CanonicalOwnerProjectionV1:
    metadata_value = metadata or {}
    facts = _owner_projection_facts(
        request_identity=request_identity,
        response_identity=response_identity,
        owner_identity=owner_identity,
        owner_state=owner_state,
        owner_next_act=owner_next_act,
        owner_advancement=owner_advancement,
        owner_revision_before=owner_revision_before,
        owner_revision=owner_revision,
        owner_terminal_state=owner_terminal_state,
        owner_continuation=owner_continuation,
        owner_result_projection=owner_result_projection,
        metadata=metadata_value,
    )
    return CanonicalOwnerProjectionV1(
        projection_identity=_canonical_identity(
            "CANONICAL-OWNER-PROJECTION-", facts
        ),
        **facts,
    )


def _presentation_facts(
    *,
    request_identity: str,
    response_identity: str,
    presentation_state: str,
    presentation_kind: str,
    presentation_message: tuple[str, ...],
    presentation_controls: tuple[str, ...],
    presentation_priority: str,
    presentation_visibility: str,
    presentation_accessibility: Mapping[str, Any],
    presentation_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "contract_version": CANONICAL_PRESENTATION_CONTRACT_VERSION,
        "request_identity": request_identity,
        "response_identity": response_identity,
        "presentation_state": presentation_state,
        "presentation_kind": presentation_kind,
        "presentation_message": list(presentation_message),
        "presentation_controls": list(presentation_controls),
        "presentation_priority": presentation_priority,
        "presentation_visibility": presentation_visibility,
        "presentation_accessibility": _plain_json(presentation_accessibility),
        "presentation_metadata": _plain_json(presentation_metadata),
    }


@dataclass(frozen=True, slots=True)
class CanonicalPresentationV1:
    """Channel-neutral presentation facts, never channel rendering logic."""

    contract_version: str
    presentation_identity: str
    request_identity: str
    response_identity: str
    presentation_state: str
    presentation_kind: str
    presentation_message: tuple[str, ...]
    presentation_controls: tuple[str, ...]
    presentation_priority: str
    presentation_visibility: str
    presentation_accessibility: Mapping[str, Any]
    presentation_metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_PRESENTATION_CONTRACT_VERSION:
            raise FailClosedRuntimeError("canonical Presentation version is invalid")
        for field_name in (
            "presentation_identity",
            "request_identity",
            "response_identity",
        ):
            _identity(getattr(self, field_name), field_name)
        if self.presentation_state not in CANONICAL_PRESENTATION_STATES:
            raise FailClosedRuntimeError("canonical Presentation state is invalid")
        if self.presentation_kind not in CANONICAL_PRESENTATION_KINDS:
            raise FailClosedRuntimeError("canonical Presentation kind is invalid")
        messages = _string_tuple(
            self.presentation_message, "presentation_message", required=True
        )
        _validate_presentation_messages(messages)
        controls = _string_tuple(
            self.presentation_controls, "presentation_controls"
        )
        if self.presentation_priority not in CANONICAL_PRESENTATION_PRIORITIES:
            raise FailClosedRuntimeError("canonical Presentation priority is invalid")
        if self.presentation_visibility not in CANONICAL_PRESENTATION_VISIBILITIES:
            raise FailClosedRuntimeError("canonical Presentation visibility is invalid")
        if not isinstance(self.presentation_accessibility, Mapping):
            raise FailClosedRuntimeError(
                "canonical Presentation accessibility must be an object"
            )
        if not isinstance(self.presentation_metadata, Mapping):
            raise FailClosedRuntimeError(
                "canonical Presentation metadata must be an object"
            )
        accessibility = _immutable_json(self.presentation_accessibility)
        metadata = _immutable_json(self.presentation_metadata)
        if set(accessibility) != _PRESENTATION_ACCESSIBILITY_FIELDS:
            raise FailClosedRuntimeError(
                "canonical Presentation accessibility is incomplete"
            )
        if not isinstance(accessibility["ordered_text_available"], bool) or not isinstance(
            accessibility["structured_facts_available"], bool
        ):
            raise FailClosedRuntimeError(
                "canonical Presentation accessibility flags must be boolean"
            )
        _identity(accessibility["language"], "presentation language")
        _identity(accessibility["reading_order"], "presentation reading order")
        _validate_forbidden_keys(
            {"accessibility": accessibility, "metadata": metadata},
            _FORBIDDEN_PRESENTATION_TOKENS,
            "canonical Presentation contains channel-specific rendering logic",
        )
        facts = _presentation_facts(
            request_identity=self.request_identity,
            response_identity=self.response_identity,
            presentation_state=self.presentation_state,
            presentation_kind=self.presentation_kind,
            presentation_message=messages,
            presentation_controls=controls,
            presentation_priority=self.presentation_priority,
            presentation_visibility=self.presentation_visibility,
            presentation_accessibility=accessibility,
            presentation_metadata=metadata,
        )
        expected_identity = _canonical_identity("CANONICAL-PRESENTATION-", facts)
        if self.presentation_identity != expected_identity:
            raise FailClosedRuntimeError("canonical Presentation identity is invalid")
        object.__setattr__(self, "presentation_message", messages)
        object.__setattr__(self, "presentation_controls", controls)
        object.__setattr__(self, "presentation_accessibility", accessibility)
        object.__setattr__(self, "presentation_metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "presentation_identity": self.presentation_identity,
            "request_identity": self.request_identity,
            "response_identity": self.response_identity,
            "presentation_state": self.presentation_state,
            "presentation_kind": self.presentation_kind,
            "presentation_message": list(self.presentation_message),
            "presentation_controls": list(self.presentation_controls),
            "presentation_priority": self.presentation_priority,
            "presentation_visibility": self.presentation_visibility,
            "presentation_accessibility": _plain_json(
                self.presentation_accessibility
            ),
            "presentation_metadata": _plain_json(self.presentation_metadata),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalPresentationV1":
        if not isinstance(value, dict) or set(value) != _PRESENTATION_FIELDS:
            raise FailClosedRuntimeError(
                "canonical Presentation structure is invalid"
            )
        return cls(**value)


def create_canonical_presentation_v1(
    *,
    request_identity: str,
    response_identity: str,
    presentation_state: str,
    presentation_kind: str,
    presentation_message: tuple[str, ...] | list[str],
    presentation_controls: tuple[str, ...] | list[str] = (),
    presentation_priority: str = NORMAL,
    presentation_visibility: str = HUMAN_AND_ELIGIBLE_SOURCE_VISIBLE,
    presentation_accessibility: Mapping[str, Any] | None = None,
    presentation_metadata: Mapping[str, Any] | None = None,
) -> CanonicalPresentationV1:
    messages = tuple(presentation_message)
    controls = tuple(presentation_controls)
    accessibility = presentation_accessibility or {
        "ordered_text_available": True,
        "structured_facts_available": True,
        "language": "und",
        "reading_order": "DOCUMENT_ORDER",
    }
    metadata = presentation_metadata or {}
    facts = _presentation_facts(
        request_identity=request_identity,
        response_identity=response_identity,
        presentation_state=presentation_state,
        presentation_kind=presentation_kind,
        presentation_message=messages,
        presentation_controls=controls,
        presentation_priority=presentation_priority,
        presentation_visibility=presentation_visibility,
        presentation_accessibility=accessibility,
        presentation_metadata=metadata,
    )
    return CanonicalPresentationV1(
        presentation_identity=_canonical_identity("CANONICAL-PRESENTATION-", facts),
        **facts,
    )


def _failure_facts(
    *,
    failure_kind: str,
    failure_scope: str,
    failure_owner: str,
    severity: str,
    recoverability: str,
    retryability: str,
    failure_reason: str,
    owner_projection: CanonicalOwnerProjectionV1,
    continuation: Mapping[str, Any],
    revision: int | str,
    request_identity: str,
    response_identity: str,
    presentation_identity: str,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "contract_version": CANONICAL_COMMON_FAILURE_CONTRACT_VERSION,
        "failure_kind": failure_kind,
        "failure_scope": failure_scope,
        "failure_owner": failure_owner,
        "severity": severity,
        "recoverability": recoverability,
        "retryability": retryability,
        "failure_reason": failure_reason,
        "owner_projection": owner_projection.to_dict(),
        "continuation": _plain_json(continuation),
        "revision": revision,
        "request_identity": request_identity,
        "response_identity": response_identity,
        "presentation_identity": presentation_identity,
        "metadata": _plain_json(metadata),
    }


@dataclass(frozen=True, slots=True)
class CanonicalCommonFailureV1:
    """One immutable owner-attributed constitutional failure outcome."""

    contract_version: str
    failure_identity: str
    failure_kind: str
    failure_scope: str
    failure_owner: str
    severity: str
    recoverability: str
    retryability: str
    failure_reason: str
    owner_projection: CanonicalOwnerProjectionV1
    continuation: Mapping[str, Any]
    revision: int | str
    request_identity: str
    response_identity: str
    presentation_identity: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_COMMON_FAILURE_CONTRACT_VERSION:
            raise FailClosedRuntimeError("canonical Common Failure version is invalid")
        for field_name in (
            "failure_identity",
            "failure_scope",
            "failure_owner",
            "failure_reason",
            "request_identity",
            "response_identity",
            "presentation_identity",
        ):
            _identity(getattr(self, field_name), field_name)
        if self.failure_kind not in CANONICAL_FAILURE_KINDS:
            raise FailClosedRuntimeError("canonical Common Failure kind is invalid")
        if self.severity not in CANONICAL_FAILURE_SEVERITIES:
            raise FailClosedRuntimeError("canonical Common Failure severity is invalid")
        if self.recoverability not in CANONICAL_FAILURE_RECOVERABILITY:
            raise FailClosedRuntimeError(
                "canonical Common Failure recoverability is invalid"
            )
        if self.retryability not in CANONICAL_FAILURE_RETRYABILITY:
            raise FailClosedRuntimeError(
                "canonical Common Failure retryability is invalid"
            )
        projection = validate_canonical_owner_projection_v1(self.owner_projection)
        if not isinstance(self.continuation, Mapping):
            raise FailClosedRuntimeError(
                "canonical Common Failure continuation must be an object"
            )
        continuation = _immutable_json(self.continuation)
        metadata = _immutable_json(self.metadata)
        revision = _revision(self.revision, "failure revision")
        if projection.owner_identity != self.failure_owner:
            raise FailClosedRuntimeError(
                "canonical Common Failure owner binding is invalid"
            )
        if projection.request_identity != self.request_identity or (
            projection.response_identity != self.response_identity
        ):
            raise FailClosedRuntimeError(
                "canonical Common Failure response binding is invalid"
            )
        if projection.owner_revision != revision:
            raise FailClosedRuntimeError(
                "canonical Common Failure projection is stale"
            )
        if _plain_json(continuation) != _plain_json(projection.owner_continuation):
            raise FailClosedRuntimeError(
                "canonical Common Failure continuation binding is invalid"
            )
        if self.retryability == RETRYABLE and self.recoverability != RECOVERABLE:
            raise FailClosedRuntimeError(
                "retryable Common Failure must be recoverable"
            )
        facts = _failure_facts(
            failure_kind=self.failure_kind,
            failure_scope=self.failure_scope,
            failure_owner=self.failure_owner,
            severity=self.severity,
            recoverability=self.recoverability,
            retryability=self.retryability,
            failure_reason=self.failure_reason,
            owner_projection=projection,
            continuation=continuation,
            revision=self.revision,
            request_identity=self.request_identity,
            response_identity=self.response_identity,
            presentation_identity=self.presentation_identity,
            metadata=metadata,
        )
        expected_identity = _canonical_identity("CANONICAL-FAILURE-", facts)
        if self.failure_identity != expected_identity:
            raise FailClosedRuntimeError(
                "canonical Common Failure identity-content conflict"
            )
        object.__setattr__(self, "owner_projection", projection)
        object.__setattr__(self, "continuation", continuation)
        object.__setattr__(self, "metadata", metadata)
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "failure_identity": self.failure_identity,
            "failure_kind": self.failure_kind,
            "failure_scope": self.failure_scope,
            "failure_owner": self.failure_owner,
            "severity": self.severity,
            "recoverability": self.recoverability,
            "retryability": self.retryability,
            "failure_reason": self.failure_reason,
            "owner_projection": self.owner_projection.to_dict(),
            "continuation": _plain_json(self.continuation),
            "revision": self.revision,
            "request_identity": self.request_identity,
            "response_identity": self.response_identity,
            "presentation_identity": self.presentation_identity,
            "metadata": _plain_json(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalCommonFailureV1":
        if not isinstance(value, dict) or set(value) != _FAILURE_FIELDS:
            raise FailClosedRuntimeError(
                "canonical Common Failure structure is invalid"
            )
        normalized = dict(value)
        projection = normalized.get("owner_projection")
        if not isinstance(projection, dict):
            raise FailClosedRuntimeError(
                "canonical Common Failure Owner Projection is invalid"
            )
        normalized["owner_projection"] = CanonicalOwnerProjectionV1.from_dict(
            projection
        )
        return cls(**normalized)


def create_canonical_common_failure_v1(
    *,
    failure_kind: str,
    failure_scope: str,
    failure_owner: str,
    severity: str,
    recoverability: str,
    retryability: str,
    failure_reason: str,
    owner_projection: CanonicalOwnerProjectionV1 | dict[str, Any],
    continuation: Mapping[str, Any],
    revision: int | str,
    request_identity: str,
    response_identity: str,
    presentation_identity: str,
    metadata: Mapping[str, Any] | None = None,
) -> CanonicalCommonFailureV1:
    projection = validate_canonical_owner_projection_v1(owner_projection)
    metadata_value = metadata or {}
    facts = _failure_facts(
        failure_kind=failure_kind,
        failure_scope=failure_scope,
        failure_owner=failure_owner,
        severity=severity,
        recoverability=recoverability,
        retryability=retryability,
        failure_reason=failure_reason,
        owner_projection=projection,
        continuation=continuation,
        revision=revision,
        request_identity=request_identity,
        response_identity=response_identity,
        presentation_identity=presentation_identity,
        metadata=metadata_value,
    )
    return CanonicalCommonFailureV1(
        failure_identity=_canonical_identity("CANONICAL-FAILURE-", facts),
        **facts,
    )


def validate_canonical_owner_projection_v1(value: Any) -> CanonicalOwnerProjectionV1:
    projection = CanonicalOwnerProjectionV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(projection, CanonicalOwnerProjectionV1):
        raise FailClosedRuntimeError("canonical Owner Projection is invalid")
    canonical_serialize(projection.to_dict())
    return projection


def validate_canonical_presentation_v1(value: Any) -> CanonicalPresentationV1:
    presentation = CanonicalPresentationV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(presentation, CanonicalPresentationV1):
        raise FailClosedRuntimeError("canonical Presentation is invalid")
    canonical_serialize(presentation.to_dict())
    return presentation


def validate_canonical_common_failure_v1(value: Any) -> CanonicalCommonFailureV1:
    failure = CanonicalCommonFailureV1.from_dict(value) if isinstance(
        value, dict
    ) else value
    if not isinstance(failure, CanonicalCommonFailureV1):
        raise FailClosedRuntimeError("canonical Common Failure is invalid")
    canonical_serialize(failure.to_dict())
    return failure


def canonical_presentation_facts_v1(
    value: CanonicalPresentationV1 | dict[str, Any]
) -> dict[str, Any]:
    """Return the same channel-neutral facts for every conforming HIC."""

    return validate_canonical_presentation_v1(value).to_dict()


def _serialize(value: Any, validator: Any) -> str:
    return canonical_serialize(validator(value).to_dict())


def _deserialize(serialized: str, label: str) -> dict[str, Any]:
    if not isinstance(serialized, str) or not serialized:
        raise FailClosedRuntimeError(f"{label} serialization is required")
    try:
        value = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"{label} serialization is invalid") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} serialization must be an object")
    return value


def serialize_canonical_owner_projection_v1(value: CanonicalOwnerProjectionV1) -> str:
    return _serialize(value, validate_canonical_owner_projection_v1)


def deserialize_canonical_owner_projection_v1(serialized: str) -> CanonicalOwnerProjectionV1:
    return CanonicalOwnerProjectionV1.from_dict(
        _deserialize(serialized, "canonical Owner Projection")
    )


def serialize_canonical_presentation_v1(value: CanonicalPresentationV1) -> str:
    return _serialize(value, validate_canonical_presentation_v1)


def deserialize_canonical_presentation_v1(serialized: str) -> CanonicalPresentationV1:
    return CanonicalPresentationV1.from_dict(
        _deserialize(serialized, "canonical Presentation")
    )


def serialize_canonical_common_failure_v1(value: CanonicalCommonFailureV1) -> str:
    return _serialize(value, validate_canonical_common_failure_v1)


def deserialize_canonical_common_failure_v1(serialized: str) -> CanonicalCommonFailureV1:
    return CanonicalCommonFailureV1.from_dict(
        _deserialize(serialized, "canonical Common Failure")
    )
