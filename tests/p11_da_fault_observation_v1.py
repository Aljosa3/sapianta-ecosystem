"""Closed construction fault controls and read-only P11 observation (S6/S7)."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


AUTHORITY_EFFECT = 0
ROUTING_EFFECT = 0
OWNER_STATE_WRITE_EFFECT = 0
P11_INVOCATION_EFFECT = 0
BACKGROUND_WATCHER_COUNT = 0
PRODUCTION_MONITORING_INTEGRATION_COUNT = 0


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


class FaultLabel(str, Enum):
    TIMEOUT = "TIMEOUT"
    EXCEPTION = "EXCEPTION"
    CLAIM_AMBIGUITY = "CLAIM_AMBIGUITY"
    TERMINAL_AMBIGUITY = "TERMINAL_AMBIGUITY"
    INVALID_COORDINATE = "INVALID_COORDINATE"
    REVOKED_AUTHORITY_STATE = "REVOKED_AUTHORITY_STATE"
    SUPERSEDED_AUTHORITY_STATE = "SUPERSEDED_AUTHORITY_STATE"
    EXPIRED_AUTHORITY_STATE = "EXPIRED_AUTHORITY_STATE"
    MALFORMED_OR_TAMPERED_RECORD = "MALFORMED_OR_TAMPERED_RECORD"
    DISPOSAL_FAILURE = "DISPOSAL_FAILURE"
    PEER_MISMATCH = "PEER_MISMATCH"
    CONCURRENCY_COLLISION = "CONCURRENCY_COLLISION"


class FaultPoint(str, Enum):
    PRECLAIM = "PRECLAIM"
    CLAIM_COMMIT = "CLAIM_COMMIT"
    BOUNDED_INVOCATION = "BOUNDED_INVOCATION"
    DISPOSAL = "DISPOSAL"
    TERMINAL_BIND = "TERMINAL_BIND"
    PERMANENT_EXHAUSTION = "PERMANENT_EXHAUSTION"
    READ_ONLY_VALIDATION = "READ_ONLY_VALIDATION"


_ALLOWED_FAULT_POINTS: Mapping[FaultLabel, frozenset[FaultPoint]] = MappingProxyType(
    {
        FaultLabel.TIMEOUT: frozenset({FaultPoint.BOUNDED_INVOCATION}),
        FaultLabel.EXCEPTION: frozenset({FaultPoint.BOUNDED_INVOCATION}),
        FaultLabel.CLAIM_AMBIGUITY: frozenset({FaultPoint.CLAIM_COMMIT}),
        FaultLabel.TERMINAL_AMBIGUITY: frozenset(
            {FaultPoint.TERMINAL_BIND, FaultPoint.PERMANENT_EXHAUSTION}
        ),
        FaultLabel.INVALID_COORDINATE: frozenset({FaultPoint.PRECLAIM}),
        FaultLabel.REVOKED_AUTHORITY_STATE: frozenset({FaultPoint.PRECLAIM}),
        FaultLabel.SUPERSEDED_AUTHORITY_STATE: frozenset({FaultPoint.PRECLAIM}),
        FaultLabel.EXPIRED_AUTHORITY_STATE: frozenset({FaultPoint.PRECLAIM}),
        FaultLabel.MALFORMED_OR_TAMPERED_RECORD: frozenset(
            {FaultPoint.PRECLAIM, FaultPoint.READ_ONLY_VALIDATION}
        ),
        FaultLabel.DISPOSAL_FAILURE: frozenset({FaultPoint.DISPOSAL}),
        FaultLabel.PEER_MISMATCH: frozenset({FaultPoint.PRECLAIM}),
        FaultLabel.CONCURRENCY_COLLISION: frozenset({FaultPoint.CLAIM_COMMIT}),
    }
)


@dataclass(frozen=True, slots=True)
class DeterministicFaultControl:
    label: FaultLabel
    point: FaultPoint

    def __post_init__(self) -> None:
        if not isinstance(self.label, FaultLabel) or not isinstance(
            self.point, FaultPoint
        ):
            _fail("fault control label and point must be closed enum members")
        if self.point not in _ALLOWED_FAULT_POINTS[self.label]:
            _fail("fault control label is not valid at the selected fixed point")

    @property
    def identity(self) -> str:
        return replay_hash(
            {
                "schema_id": "P11_DA_DETERMINISTIC_FAULT_CONTROL_V1",
                "label": self.label.value,
                "point": self.point.value,
            }
        )


FAULT_CONTROL_FIELDS = frozenset(DeterministicFaultControl.__dataclass_fields__)
FORBIDDEN_FAULT_CONTROL_FIELDS = frozenset(
    {"callback", "script", "plugin", "runtime_mutation"}
)


@dataclass(frozen=True, slots=True)
class ReadOnlyObservation:
    observation_identity: str
    source_entry_hash: str
    event_type: str
    canonical_payload: str
    authority_effect: int = AUTHORITY_EFFECT
    routing_effect: int = ROUTING_EFFECT
    owner_state_write_effect: int = OWNER_STATE_WRITE_EFFECT
    p11_invocation_effect: int = P11_INVOCATION_EFFECT

    def __post_init__(self) -> None:
        for field_name in (
            "observation_identity",
            "source_entry_hash",
            "event_type",
            "canonical_payload",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                _fail(f"{field_name} is required")
        if any(
            value != 0
            for value in (
                self.authority_effect,
                self.routing_effect,
                self.owner_state_write_effect,
                self.p11_invocation_effect,
            )
        ):
            _fail("read-only observation cannot have operational effects")


def observe_authenticated_entries(
    entries: Iterable[Mapping[str, Any]],
) -> tuple[ReadOnlyObservation, ...]:
    """Project already-validated ledger entries without retaining mutable refs."""

    observations: list[ReadOnlyObservation] = []
    for expected_sequence, entry in enumerate(entries):
        copied = deepcopy(dict(entry))
        required = {"sequence", "runtime_id", "event_type", "payload", "entry_hash"}
        if set(copied) != required:
            _fail("observed RuntimeLedger entry structure is invalid")
        expected_hash_input = deepcopy(copied)
        actual_hash = expected_hash_input.pop("entry_hash")
        if actual_hash != replay_hash(expected_hash_input):
            _fail("observed RuntimeLedger entry hash mismatch")
        if copied["sequence"] != expected_sequence:
            _fail("observed RuntimeLedger sequence mismatch")
        canonical_payload = canonical_serialize(copied["payload"])
        observation_identity = replay_hash(
            {
                "schema_id": "P11_DA_READ_ONLY_OBSERVATION_V1",
                "source_entry_hash": copied["entry_hash"],
                "event_type": copied["event_type"],
                "canonical_payload": canonical_payload,
            }
        )
        observations.append(
            ReadOnlyObservation(
                observation_identity=observation_identity,
                source_entry_hash=copied["entry_hash"],
                event_type=copied["event_type"],
                canonical_payload=canonical_payload,
            )
        )
    return tuple(observations)


@dataclass(frozen=True, slots=True)
class IncidentReview:
    review_identity: str
    observation_identities: tuple[str, ...]
    classification: str
    authority_effect: int = 0
    routing_effect: int = 0
    owner_state_write_effect: int = 0
    p11_invocation_effect: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.review_identity, str) or not self.review_identity:
            _fail("incident review identity is required")
        if not self.observation_identities or any(
            not isinstance(identity, str) or not identity
            for identity in self.observation_identities
        ):
            _fail("incident review observations are required")
        if self.classification not in {
            "REVIEW_ONLY",
            "RECONCILIATION_REQUIRED",
            "TERMINAL_EXHAUSTION_CONFIRMED",
        }:
            _fail("incident review classification is invalid")
        if any(
            value != 0
            for value in (
                self.authority_effect,
                self.routing_effect,
                self.owner_state_write_effect,
                self.p11_invocation_effect,
            )
        ):
            _fail("incident review cannot have operational effects")


def build_incident_review(
    observations: tuple[ReadOnlyObservation, ...], classification: str
) -> IncidentReview:
    if not observations:
        _fail("incident review requires observations")
    identities = tuple(observation.observation_identity for observation in observations)
    review_identity = replay_hash(
        {
            "schema_id": "P11_DA_INCIDENT_REVIEW_V1",
            "observation_identities": identities,
            "classification": classification,
        }
    )
    return IncidentReview(
        review_identity=review_identity,
        observation_identities=identities,
        classification=classification,
    )


assert not (FAULT_CONTROL_FIELDS & FORBIDDEN_FAULT_CONTROL_FIELDS)


__all__ = [
    "AUTHORITY_EFFECT",
    "BACKGROUND_WATCHER_COUNT",
    "DeterministicFaultControl",
    "FAULT_CONTROL_FIELDS",
    "FORBIDDEN_FAULT_CONTROL_FIELDS",
    "FaultLabel",
    "FaultPoint",
    "IncidentReview",
    "OWNER_STATE_WRITE_EFFECT",
    "P11_INVOCATION_EFFECT",
    "PRODUCTION_MONITORING_INTEGRATION_COUNT",
    "ROUTING_EFFECT",
    "ReadOnlyObservation",
    "build_incident_review",
    "observe_authenticated_entries",
]
