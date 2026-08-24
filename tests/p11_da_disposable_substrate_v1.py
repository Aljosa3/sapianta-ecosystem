"""Disposable construction-only P11 D-A substrate core (S1, S3, S4, S5).

This module is test-only.  It cannot authorize an operational P11 attempt and
does not provide production routing, retries, a resolver, or a parallel ledger.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any, Mapping

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CanonicalCHEEvidenceCorrelationV1,
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    CanonicalHumanAuthorityActV1,
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
    replay_hash,
    verify_replay_hash,
    with_replay_hash,
    write_json_immutable,
)


PROFILE_ID = "SAPIANTA_P11_BOUNDED_RECORD_CANONICAL_JSON_V1"
INPUT_SCHEMA_ID = "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1"
OUTPUT_SCHEMA_ID = "SAPIANTA_P11_BOUNDED_CONSUMER_OUTPUT_V1"
SCHEMA_VERSION = "1.0.0"
INPUT_RECORD_KIND = "P11_BOUNDED_CONSUMER_INPUT"
OUTPUT_RECORD_KIND = "P11_BOUNDED_CONSUMER_OUTCOME"
REPLAY_BINDING_SCHEMA_ID = "SAPIANTA_P11_REPLAY_BINDING_V1"

OUTCOME_VOCABULARY = frozenset({"EQUAL", "MISMATCH", "FAILED_CLOSED"})
MAXIMUM_DURATION_NS = 10_000_000_000
AUTOMATIC_RETRY_COUNT = 0
INVOCATIONS_PER_CLAIM = 1
OUTPUT_RECORD_COUNT = 1
PRODUCTION_ROUTE_COUNT = 0
OUTPUT_RECORD_AUTHORITY_EFFECT = 0
OUTPUT_RECORD_PRODUCTION_ROUTING_EFFECT = 0

OPERATIONAL_EVIDENCE_GENERATION_AUTHORIZED = False
HUMAN_OPERATIONAL_TEST_AUTHORITY_ACT_CREATION_OR_CONSUMPTION = "PROHIBITED"
E01_E12_EXECUTION = "PROHIBITED"
P11_OPERATIONAL_ENTRY = "PROHIBITED"
P12_ENTRY = "PROHIBITED"

INPUT_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "record_kind",
        "record_identity",
        "attempt_identity",
        "input_identity",
        "provenance_identity",
        "contract_identity",
        "contract_version",
        "contract_content_sha256",
        "authorization_reference",
        "caller_identity_reference",
        "preflight_binding_identity",
        "preflight_status",
        "p10_inventory_identity",
        "comparator_outcome_identity",
        "comparator_outcome",
        "replay_context_identity",
    }
)

OUTPUT_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "record_kind",
        "record_identity",
        "attempt_identity",
        "input_identity",
        "input_record_identity",
        "authorization_identity",
        "contract_identity",
        "contract_version",
        "contract_content_sha256",
        "provenance_identity",
        "outcome",
        "failure_class_or_reason",
        "started_at_unix_ns",
        "terminal_at_unix_ns",
        "duration_ns",
        "disposal_completion_proof_identity",
    }
)

_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("P11 record contains a duplicate key")
        value[key] = item
    return value


def _nonempty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field_name} must be a non-empty string")
    return value


def _hash_string(value: Any, field_name: str) -> str:
    text = _nonempty_string(value, field_name)
    if _HASH_PATTERN.fullmatch(text) is None:
        _fail(f"{field_name} must be a canonical sha256 identity")
    return text


def _nonnegative_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail(f"{field_name} must be a non-negative integer")
    return value


def _canonical_record_from_bytes(
    serialized: bytes, expected_fields: frozenset[str]
) -> dict[str, Any]:
    if not isinstance(serialized, bytes) or not serialized:
        _fail("P11 record must be non-empty canonical UTF-8 bytes")
    try:
        text = serialized.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_duplicate_rejecting_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("P11 record is not canonical JSON") from exc
    if not isinstance(value, dict) or set(value) != expected_fields:
        _fail("P11 record field set is invalid")
    if canonical_serialize(value).encode("utf-8") != serialized:
        _fail("P11 record bytes are not in the canonical profile")
    return value


def record_identity(value: Mapping[str, Any]) -> str:
    """Reuse the canonical transport hash over the full record minus identity."""

    preimage = deepcopy(dict(value))
    preimage.pop("record_identity", None)
    return replay_hash(preimage)


def bind_record_identity(value: Mapping[str, Any]) -> bytes:
    """Return exact canonical bytes after binding the existing record identity."""

    artifact = deepcopy(dict(value))
    artifact["record_identity"] = record_identity(artifact)
    return canonical_serialize(artifact).encode("utf-8")


def _validate_record_identity(value: Mapping[str, Any]) -> None:
    _hash_string(value.get("record_identity"), "record_identity")
    if value["record_identity"] != record_identity(value):
        _fail("P11 record identity mismatch")


def validate_input_record_bytes(serialized: bytes) -> dict[str, Any]:
    value = _canonical_record_from_bytes(serialized, INPUT_FIELDS)
    if (
        value["schema_id"] != INPUT_SCHEMA_ID
        or value["schema_version"] != SCHEMA_VERSION
        or value["record_kind"] != INPUT_RECORD_KIND
    ):
        _fail("P11 input schema constants are invalid")
    for field_name in INPUT_FIELDS - {"record_identity", "contract_content_sha256"}:
        _nonempty_string(value[field_name], field_name)
    _hash_string(value["contract_content_sha256"], "contract_content_sha256")
    if value["preflight_status"] != "PASSED":
        _fail("P11 input preflight status must be PASSED")
    if value["comparator_outcome"] not in OUTCOME_VOCABULARY:
        _fail("P11 input comparator outcome is outside the closed vocabulary")
    _validate_record_identity(value)
    return deepcopy(value)


def validate_output_record_bytes(
    serialized: bytes,
    input_record: Mapping[str, Any],
    *,
    validated_authorization_identity: str,
) -> dict[str, Any]:
    if not isinstance(input_record, Mapping) or set(input_record) != INPUT_FIELDS:
        _fail("validated P11 input record is required for output lineage")
    _validate_record_identity(input_record)
    value = _canonical_record_from_bytes(serialized, OUTPUT_FIELDS)
    _nonempty_string(validated_authorization_identity, "authorization identity")
    if (
        value["schema_id"] != OUTPUT_SCHEMA_ID
        or value["schema_version"] != SCHEMA_VERSION
        or value["record_kind"] != OUTPUT_RECORD_KIND
    ):
        _fail("P11 output schema constants are invalid")
    for field_name in OUTPUT_FIELDS - {
        "record_identity",
        "contract_content_sha256",
        "failure_class_or_reason",
        "started_at_unix_ns",
        "terminal_at_unix_ns",
        "duration_ns",
        "disposal_completion_proof_identity",
    }:
        _nonempty_string(value[field_name], field_name)
    _hash_string(value["contract_content_sha256"], "contract_content_sha256")
    _validate_record_identity(value)
    if value["outcome"] not in OUTCOME_VOCABULARY:
        _fail("P11 output outcome is outside the closed vocabulary")

    started = _nonnegative_integer(value["started_at_unix_ns"], "started timestamp")
    terminal = _nonnegative_integer(value["terminal_at_unix_ns"], "terminal timestamp")
    duration = _nonnegative_integer(value["duration_ns"], "duration")
    if terminal < started or duration != terminal - started:
        _fail("P11 output timestamp lineage is invalid")
    if duration > MAXIMUM_DURATION_NS:
        _fail("P11 output exceeds the maximum duration")

    if value["outcome"] == "FAILED_CLOSED":
        _nonempty_string(value["failure_class_or_reason"], "failure reason")
        _nonempty_string(
            value["disposal_completion_proof_identity"], "disposal proof identity"
        )
    elif (
        value["failure_class_or_reason"] is not None
        or value["disposal_completion_proof_identity"] is not None
    ):
        _fail("non-failure P11 output must have null failure fields")

    equalities = {
        "attempt_identity": input_record["attempt_identity"],
        "input_identity": input_record["input_identity"],
        "input_record_identity": input_record["record_identity"],
        "authorization_identity": validated_authorization_identity,
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "provenance_identity": input_record["provenance_identity"],
    }
    for field_name, expected in equalities.items():
        if value[field_name] != expected:
            _fail(f"P11 output {field_name} lineage mismatch")
    return deepcopy(value)


def replay_binding_identity(
    input_record: Mapping[str, Any], output_record: Mapping[str, Any]
) -> str:
    value = {
        "attempt_identity": output_record["attempt_identity"],
        "authorization_identity": output_record["authorization_identity"],
        "contract_content_sha256": output_record["contract_content_sha256"],
        "contract_identity": output_record["contract_identity"],
        "contract_version": output_record["contract_version"],
        "input_record_identity": input_record["record_identity"],
        "output_record_identity": output_record["record_identity"],
        "provenance_identity": output_record["provenance_identity"],
        "replay_context_identity": input_record["replay_context_identity"],
        "schema_id": REPLAY_BINDING_SCHEMA_ID,
    }
    return replay_hash(value)


def write_record_immutable(
    path: Path,
    serialized: bytes,
    *,
    kind: str,
    input_record: Mapping[str, Any] | None = None,
    validated_authorization_identity: str | None = None,
) -> None:
    if kind == "INPUT":
        value = validate_input_record_bytes(serialized)
    elif kind == "OUTPUT":
        if input_record is None or validated_authorization_identity is None:
            _fail("output persistence requires validated input and authorization lineage")
        value = validate_output_record_bytes(
            serialized,
            input_record,
            validated_authorization_identity=validated_authorization_identity,
        )
    else:
        _fail("immutable P11 record kind is invalid")
    write_json_immutable(path, value)


class OwnerStateName(str, Enum):
    AVAILABLE = "AVAILABLE"
    CLAIMED = "CLAIMED"
    CONSUMED = "CONSUMED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


ALLOWED_OWNER_STATE_TRANSITIONS = frozenset(
    {
        (OwnerStateName.AVAILABLE, OwnerStateName.CLAIMED),
        (OwnerStateName.AVAILABLE, OwnerStateName.REVOKED),
        (OwnerStateName.AVAILABLE, OwnerStateName.SUPERSEDED),
        (OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED),
        (OwnerStateName.CLAIMED, OwnerStateName.CONSUMED),
        (OwnerStateName.CLAIMED, OwnerStateName.RECONCILIATION_REQUIRED),
        (OwnerStateName.RECONCILIATION_REQUIRED, OwnerStateName.CONSUMED),
    }
)


@dataclass(frozen=True, slots=True)
class AuthorityBinding:
    authenticated_caller_principal_identity: str
    authority_act_identity: str
    authority_act_content_identity: str
    authorization_identity: str
    attempt_identity: str
    input_record_identity: str
    input_identity: str
    provenance_identity: str
    contract_identity: str
    contract_version: str
    contract_content_sha256: str
    authorized_scope: str
    valid_from_unix_ns: int
    valid_until_unix_ns: int

    def __post_init__(self) -> None:
        for field_name in (
            "authenticated_caller_principal_identity",
            "authority_act_identity",
            "authority_act_content_identity",
            "authorization_identity",
            "attempt_identity",
            "input_record_identity",
            "input_identity",
            "provenance_identity",
            "contract_identity",
            "contract_version",
            "authorized_scope",
        ):
            _nonempty_string(getattr(self, field_name), field_name)
        _hash_string(self.contract_content_sha256, "contract_content_sha256")
        _nonnegative_integer(self.valid_from_unix_ns, "valid_from_unix_ns")
        _nonnegative_integer(self.valid_until_unix_ns, "valid_until_unix_ns")
        if self.valid_until_unix_ns <= self.valid_from_unix_ns:
            _fail("authority validity interval is invalid")


@dataclass(frozen=True, slots=True)
class DisposableOwnerState:
    binding: AuthorityBinding
    state: OwnerStateName = OwnerStateName.AVAILABLE
    revision: int = 0
    output_record_identity: str | None = None
    outcome: str | None = None
    disposal_completion_proof_identity: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.binding, AuthorityBinding):
            _fail("owner state authority binding is required")
        if not isinstance(self.state, OwnerStateName):
            _fail("owner state value is invalid")
        _nonnegative_integer(self.revision, "owner state revision")
        if self.state is OwnerStateName.CONSUMED:
            _nonempty_string(self.output_record_identity, "terminal output identity")
            if self.outcome not in OUTCOME_VOCABULARY:
                _fail("terminal owner-state outcome is invalid")
        elif any(
            item is not None
            for item in (
                self.output_record_identity,
                self.outcome,
                self.disposal_completion_proof_identity,
            )
        ):
            _fail("non-consumed owner state cannot contain terminal bindings")


def transition_owner_state(
    owner_state: DisposableOwnerState,
    target: OwnerStateName,
    *,
    reconciliation_establishes_terminal_exhaustion: bool = False,
) -> DisposableOwnerState:
    transition = (owner_state.state, target)
    if transition not in ALLOWED_OWNER_STATE_TRANSITIONS:
        _fail("owner-state transition is prohibited")
    if owner_state.state is OwnerStateName.RECONCILIATION_REQUIRED and not (
        reconciliation_establishes_terminal_exhaustion
    ):
        _fail("reconciliation cannot authorize a transition without exhaustion proof")
    if target is OwnerStateName.CONSUMED:
        _fail("CONSUMED requires exact terminal output binding")
    return replace(owner_state, state=target, revision=owner_state.revision + 1)


def atomically_claim_construction_state(
    owner_state: DisposableOwnerState,
    *,
    claim_time_unix_ns: int,
    authenticated_caller_principal_identity: str,
) -> DisposableOwnerState:
    claim_time = _nonnegative_integer(claim_time_unix_ns, "claim time")
    binding = owner_state.binding
    if authenticated_caller_principal_identity != (
        binding.authenticated_caller_principal_identity
    ):
        _fail("claim caller principal mismatch")
    if not (binding.valid_from_unix_ns <= claim_time < binding.valid_until_unix_ns):
        _fail("authority is not current at claim time")
    return transition_owner_state(owner_state, OwnerStateName.CLAIMED)


def terminal_bind_and_consume(
    owner_state: DisposableOwnerState,
    output_record: Mapping[str, Any],
    *,
    reconciliation_establishes_terminal_exhaustion: bool = False,
) -> DisposableOwnerState:
    if owner_state.state not in {
        OwnerStateName.CLAIMED,
        OwnerStateName.RECONCILIATION_REQUIRED,
    }:
        _fail("terminal binding requires a non-reusable claimed state")
    if (
        owner_state.state is OwnerStateName.RECONCILIATION_REQUIRED
        and not reconciliation_establishes_terminal_exhaustion
    ):
        _fail("reconciliation lacks exact terminal exhaustion proof")
    if output_record.get("authorization_identity") != (
        owner_state.binding.authorization_identity
    ):
        _fail("terminal authorization identity mismatch")
    if output_record.get("attempt_identity") != owner_state.binding.attempt_identity:
        _fail("terminal attempt identity mismatch")
    outcome = output_record.get("outcome")
    if outcome not in OUTCOME_VOCABULARY:
        _fail("terminal outcome is invalid")
    output_identity = _hash_string(
        output_record.get("record_identity"), "terminal output identity"
    )
    if output_identity != record_identity(output_record):
        _fail("terminal output record identity mismatch")
    terminal_equalities = {
        "input_record_identity": owner_state.binding.input_record_identity,
        "input_identity": owner_state.binding.input_identity,
        "provenance_identity": owner_state.binding.provenance_identity,
        "contract_identity": owner_state.binding.contract_identity,
        "contract_version": owner_state.binding.contract_version,
        "contract_content_sha256": owner_state.binding.contract_content_sha256,
    }
    for field_name, expected in terminal_equalities.items():
        if output_record.get(field_name) != expected:
            _fail(f"terminal {field_name} binding mismatch")
    disposal = output_record.get("disposal_completion_proof_identity")
    if outcome == "FAILED_CLOSED":
        _nonempty_string(disposal, "terminal disposal proof identity")
    elif disposal is not None:
        _fail("terminal non-failure disposal proof must be null")
    return DisposableOwnerState(
        binding=owner_state.binding,
        state=OwnerStateName.CONSUMED,
        revision=owner_state.revision + 1,
        output_record_identity=output_identity,
        outcome=outcome,
        disposal_completion_proof_identity=disposal,
    )


class D3Phase(str, Enum):
    PRECLAIM = "PRECLAIM"
    CLAIM = "CLAIM"
    ONE_BOUNDED_INVOCATION = "ONE_BOUNDED_INVOCATION"
    TERMINAL_BIND = "TERMINAL_BIND"
    PERMANENT_EXHAUSTION = "PERMANENT_EXHAUSTION"


D3_PHASE_SEQUENCE = (
    D3Phase.PRECLAIM,
    D3Phase.CLAIM,
    D3Phase.ONE_BOUNDED_INVOCATION,
    D3Phase.TERMINAL_BIND,
    D3Phase.PERMANENT_EXHAUSTION,
)


@dataclass(frozen=True, slots=True)
class D3TransactionPlan:
    phases: tuple[D3Phase, ...] = D3_PHASE_SEQUENCE
    invocations_per_claim: int = INVOCATIONS_PER_CLAIM
    maximum_duration_ns: int = MAXIMUM_DURATION_NS
    automatic_retry_count: int = AUTOMATIC_RETRY_COUNT
    output_record_count: int = OUTPUT_RECORD_COUNT
    production_route_count: int = PRODUCTION_ROUTE_COUNT

    def __post_init__(self) -> None:
        if self.phases != D3_PHASE_SEQUENCE:
            _fail("D3 transaction phase sequence is invalid")
        if (
            self.invocations_per_claim != 1
            or self.maximum_duration_ns != 10_000_000_000
            or self.automatic_retry_count != 0
            or self.output_record_count != 1
            or self.production_route_count != 0
        ):
            _fail("D3 transaction constants are invalid")


class ConstructionOnlyConsumerStub:
    """Deterministic zero-production record constructor, never a P11 entry."""

    authority_effect = 0
    production_route_count = 0
    operational_p11_entry = False

    @staticmethod
    def invoke_once(
        input_record_canonical_bytes: bytes,
        *,
        validated_authorization_identity: str,
        outcome: str,
        started_at_unix_ns: int,
        terminal_at_unix_ns: int,
        failure_class_or_reason: str | None = None,
        disposal_completion_proof_identity: str | None = None,
    ) -> bytes:
        input_record = validate_input_record_bytes(input_record_canonical_bytes)
        if outcome not in OUTCOME_VOCABULARY:
            _fail("construction output outcome is invalid")
        output = {
            "schema_id": OUTPUT_SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "record_kind": OUTPUT_RECORD_KIND,
            "record_identity": "",
            "attempt_identity": input_record["attempt_identity"],
            "input_identity": input_record["input_identity"],
            "input_record_identity": input_record["record_identity"],
            "authorization_identity": validated_authorization_identity,
            "contract_identity": input_record["contract_identity"],
            "contract_version": input_record["contract_version"],
            "contract_content_sha256": input_record["contract_content_sha256"],
            "provenance_identity": input_record["provenance_identity"],
            "outcome": outcome,
            "failure_class_or_reason": failure_class_or_reason,
            "started_at_unix_ns": started_at_unix_ns,
            "terminal_at_unix_ns": terminal_at_unix_ns,
            "duration_ns": terminal_at_unix_ns - started_at_unix_ns,
            "disposal_completion_proof_identity": (
                disposal_completion_proof_identity
            ),
        }
        serialized = bind_record_identity(output)
        validate_output_record_bytes(
            serialized,
            input_record,
            validated_authorization_identity=validated_authorization_identity,
        )
        return serialized


HUMAN_ACT_VALIDATOR = validate_canonical_human_authority_act_v1
CHE_CORRELATION_VALIDATOR = validate_canonical_che_evidence_correlation_v1


class P11CaptureReplayAdapter:
    """Thin P11 mapping over the existing RuntimeLedger; never authoritative."""

    _EVENT_TYPES = frozenset(
        {
            "P11_DA_CONSTRUCTION_INPUT",
            "P11_DA_CONSTRUCTION_OUTPUT",
            "P11_DA_CONSTRUCTION_STATE",
        }
    )

    def __init__(self, disposable_fixture_root: Path | str) -> None:
        self._ledger = RuntimeLedger(disposable_fixture_root)

    @property
    def ledger_implementation(self) -> type[RuntimeLedger]:
        return type(self._ledger)

    def append_construction_capture(
        self, fixture_identity: str, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        _nonempty_string(fixture_identity, "fixture identity")
        if event_type not in self._EVENT_TYPES:
            _fail("construction capture event type is invalid")
        return self._ledger.append(fixture_identity, event_type, payload)

    def read_only_validate(
        self, fixture_identity: str
    ) -> tuple[dict[str, Any], ...]:
        entries = self._ledger.read(fixture_identity)
        canonical_serialize(entries)
        return tuple(deepcopy(entry) for entry in entries)

    @staticmethod
    def validate_existing_authority_sources(
        act: CanonicalHumanAuthorityActV1,
        correlation: CanonicalCHEEvidenceCorrelationV1,
    ) -> tuple[CanonicalHumanAuthorityActV1, CanonicalCHEEvidenceCorrelationV1]:
        validated_act = HUMAN_ACT_VALIDATOR(act)
        validated_correlation = CHE_CORRELATION_VALIDATOR(correlation)
        if validated_correlation.authority_act_identity != (
            validated_act.authority_act_identity
        ):
            _fail("CHE correlation does not bind the canonical Human act")
        return validated_act, validated_correlation


REUSED_SERIALIZATION_SURFACES = (
    canonical_serialize,
    replay_hash,
    with_replay_hash,
    verify_replay_hash,
    write_json_immutable,
    load_json,
)
REUSED_LEDGER_SURFACES = (RuntimeLedger.append, RuntimeLedger.read)


__all__ = [
    "ALLOWED_OWNER_STATE_TRANSITIONS",
    "AUTOMATIC_RETRY_COUNT",
    "AuthorityBinding",
    "CHE_CORRELATION_VALIDATOR",
    "ConstructionOnlyConsumerStub",
    "D3Phase",
    "D3TransactionPlan",
    "DisposableOwnerState",
    "HUMAN_ACT_VALIDATOR",
    "INPUT_FIELDS",
    "INVOCATIONS_PER_CLAIM",
    "MAXIMUM_DURATION_NS",
    "OPERATIONAL_EVIDENCE_GENERATION_AUTHORIZED",
    "OUTPUT_FIELDS",
    "OUTPUT_RECORD_COUNT",
    "OUTCOME_VOCABULARY",
    "OwnerStateName",
    "P11CaptureReplayAdapter",
    "PRODUCTION_ROUTE_COUNT",
    "REUSED_LEDGER_SURFACES",
    "REUSED_SERIALIZATION_SURFACES",
    "atomically_claim_construction_state",
    "bind_record_identity",
    "record_identity",
    "replay_binding_identity",
    "terminal_bind_and_consume",
    "transition_owner_state",
    "validate_input_record_bytes",
    "validate_output_record_bytes",
    "write_record_immutable",
]
