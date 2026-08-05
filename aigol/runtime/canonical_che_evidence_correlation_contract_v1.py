"""Immutable CHE source and decision evidence correlation contract.

The contract binds identities already emitted by constitutional owners.  It
does not interpret source content, create Human authority, project application
state, create Replay or Certification evidence, or give CRO runtime authority.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION = (
    "G69_11_CANONICAL_CHE_EVIDENCE_CORRELATION_V1"
)
CANONICAL_CHE_EVIDENCE_CORRELATION_RECORD_VERSION = (
    "G69_11_CANONICAL_CHE_EVIDENCE_CORRELATION_RECORD_V1"
)
CANONICAL_CHE_JOURNEY_RECONSTRUCTION_VERSION = (
    "G69_11_CANONICAL_CHE_JOURNEY_RECONSTRUCTION_V1"
)
CANONICAL_CHE_CRO_OBSERVATION_VERSION = (
    "G69_11_PASSIVE_CRO_CHE_JOURNEY_OBSERVATION_V1"
)

NOT_APPLICABLE = "NOT_APPLICABLE"
NOT_RECORDED = "NOT_RECORDED"
RECORDED = "RECORDED"
UNAVAILABLE_PRE_WRITE = "UNAVAILABLE_PRE_WRITE"
DELIVERY_OUTCOME_UNKNOWN = "DELIVERY_OUTCOME_UNKNOWN"
REFERENCE_NOT_CREATED = "NOT_CREATED"
REFERENCE_CREATED = "CREATED"

EVIDENCE_STATUSES = frozenset(
    {
        RECORDED,
        NOT_RECORDED,
        NOT_APPLICABLE,
        UNAVAILABLE_PRE_WRITE,
        DELIVERY_OUTCOME_UNKNOWN,
    }
)
REFERENCE_STATUSES = frozenset(
    {REFERENCE_CREATED, REFERENCE_NOT_CREATED, NOT_APPLICABLE, NOT_RECORDED}
)
DELIVERY_STATUSES = frozenset(
    {
        "RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN",
        "COMMITTED_RESPONSE_FOUND",
        "COMMITTED_NOT_ADVANCED",
        "ENTERED_NOT_ADVANCED",
        DELIVERY_OUTCOME_UNKNOWN,
        "NOT_FOUND",
        NOT_APPLICABLE,
    }
)

_REFERENCE_CORRELATION_FIELDS = frozenset(
    {
        "reference_identity",
        "ordered_position",
        "provenance_identity",
        "content_owner_identity",
        "custody_owner_identity",
        "validation_owner_identity",
        "availability_status",
        "integrity_algorithm",
        "integrity_reference",
        "validation_evidence_identity",
        "validation_evidence_digest",
        "retry_of_reference_set_digest",
    }
)
_CORRELATION_FIELDS = frozenset(
    {
        "contract_version",
        "correlation_identity",
        "interaction_identity",
        "conversation_identity",
        "session_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "actor_identity",
        "source_channel_identity",
        "adapter_identity",
        "request_identity",
        "che_entry_identity",
        "source_act_identity",
        "source_act_digest",
        "order_identity",
        "idempotency_identity",
        "continuation_identity",
        "continuation_sequence",
        "authority_act_identity",
        "authority_kind",
        "authority_requesting_owner_identity",
        "authority_target_identity",
        "authority_target_revision",
        "authority_payload_digest",
        "authority_result_identity",
        "opaque_reference_set_identity",
        "ordered_reference_set_digest",
        "opaque_reference_correlations",
        "producing_owner_identity",
        "owner_state_identity",
        "owner_revision_before",
        "owner_revision_after",
        "owner_advancement",
        "owner_disposition",
        "next_act_identity",
        "refusal_identity",
        "terminal_identity",
        "owner_projection_identity",
        "failure_identity",
        "presentation_identity",
        "response_identity",
        "response_digest",
        "delivery_record_identity",
        "delivery_status",
        "duplicate_resolution",
        "acknowledgement_state",
        "replay_references",
        "replay_status",
        "certification_references",
        "certification_status",
        "evidence_status",
        "metadata",
    }
)
_RECORD_FIELDS = frozenset(
    {"record_version", "correlation", "integrity_hash"}
)


def _identity(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"CHE evidence {label} is invalid")
    return value


def _revision(value: Any, label: str) -> int | str:
    if value == NOT_APPLICABLE:
        return value
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(f"CHE evidence {label} is invalid")
    return value


def _plain_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain_json(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return deepcopy(value)


def _immutable_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError("CHE evidence object keys must be strings")
        return MappingProxyType(
            {key: _immutable_json(value[key]) for key in sorted(value)}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_json(item) for item in value)
    copied = deepcopy(value)
    canonical_serialize(copied)
    return copied


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"CHE evidence {label} is invalid")
    result = tuple(value)
    if any(not isinstance(item, str) or not item for item in result):
        raise FailClosedRuntimeError(f"CHE evidence {label} is invalid")
    if len(result) != len(set(result)):
        raise FailClosedRuntimeError(f"CHE evidence {label} contains duplicates")
    return result


def _reference_correlations(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(
            "CHE opaque Reference correlations are invalid"
        )
    normalized: list[Mapping[str, Any]] = []
    positions: list[int] = []
    identities: list[str] = []
    for item in value:
        if not isinstance(item, Mapping) or set(item) != _REFERENCE_CORRELATION_FIELDS:
            raise FailClosedRuntimeError(
                "CHE opaque Reference correlation structure is invalid"
            )
        record = dict(item)
        for key in _REFERENCE_CORRELATION_FIELDS - {"ordered_position"}:
            _identity(record[key], f"opaque Reference {key}")
        position = record["ordered_position"]
        if not isinstance(position, int) or isinstance(position, bool) or position < 1:
            raise FailClosedRuntimeError(
                "CHE opaque Reference ordered position is invalid"
            )
        positions.append(position)
        identities.append(record["reference_identity"])
        normalized.append(_immutable_json(record))
    if positions and positions != list(range(1, len(positions) + 1)):
        raise FailClosedRuntimeError(
            "CHE opaque Reference correlation ordering is invalid"
        )
    if len(identities) != len(set(identities)):
        raise FailClosedRuntimeError(
            "CHE opaque Reference correlation identities conflict"
        )
    return tuple(normalized)


def canonical_che_response_evidence_digest_v1(response: Any) -> str:
    """Digest a Response without its correlation pointer, avoiding recursion."""

    value = response.to_dict() if hasattr(response, "to_dict") else response
    if not isinstance(value, Mapping):
        raise FailClosedRuntimeError("CHE evidence Response is invalid")
    facts = dict(_plain_json(value))
    if "correlation_identity" not in facts:
        raise FailClosedRuntimeError("CHE Response correlation field is absent")
    facts["correlation_identity"] = NOT_APPLICABLE
    continuation = facts.get("continuation_envelope")
    if isinstance(continuation, dict):
        continuation = dict(continuation)
        continuation["correlation_identity"] = NOT_APPLICABLE
        facts["continuation_envelope"] = continuation
    return replay_hash({"canonical_response_facts": facts})


def _correlation_identity_facts(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _plain_json(value[key])
        for key in sorted(_CORRELATION_FIELDS - {"correlation_identity", "metadata"})
    }


def canonical_che_evidence_correlation_identity_v1(
    value: Mapping[str, Any],
) -> str:
    return "CHE-CORRELATION-" + replay_hash(
        _correlation_identity_facts(value)
    ).removeprefix("sha256:")


@dataclass(frozen=True, slots=True)
class CanonicalCHEEvidenceCorrelationV1:
    """One turn-level, owner-preserving correlation of recorded evidence."""

    contract_version: str
    correlation_identity: str
    interaction_identity: str
    conversation_identity: str
    session_identity: str
    workspace_identity: str
    runtime_scope_identity: str
    actor_identity: str
    source_channel_identity: str
    adapter_identity: str
    request_identity: str
    che_entry_identity: str
    source_act_identity: str
    source_act_digest: str
    order_identity: str
    idempotency_identity: str
    continuation_identity: str
    continuation_sequence: int | str
    authority_act_identity: str
    authority_kind: str
    authority_requesting_owner_identity: str
    authority_target_identity: str
    authority_target_revision: int | str
    authority_payload_digest: str
    authority_result_identity: str
    opaque_reference_set_identity: str
    ordered_reference_set_digest: str
    opaque_reference_correlations: tuple[Mapping[str, Any], ...]
    producing_owner_identity: str
    owner_state_identity: str
    owner_revision_before: int | str
    owner_revision_after: int | str
    owner_advancement: str
    owner_disposition: str
    next_act_identity: str
    refusal_identity: str
    terminal_identity: str
    owner_projection_identity: str
    failure_identity: str
    presentation_identity: str
    response_identity: str
    response_digest: str
    delivery_record_identity: str
    delivery_status: str
    duplicate_resolution: str
    acknowledgement_state: str
    replay_references: tuple[str, ...]
    replay_status: str
    certification_references: tuple[str, ...]
    certification_status: str
    evidence_status: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.contract_version != CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION:
            raise FailClosedRuntimeError(
                "CHE evidence correlation contract version is invalid"
            )
        for field_name in (
            "correlation_identity",
            "interaction_identity",
            "conversation_identity",
            "session_identity",
            "workspace_identity",
            "runtime_scope_identity",
            "actor_identity",
            "source_channel_identity",
            "adapter_identity",
            "request_identity",
            "che_entry_identity",
            "source_act_identity",
            "source_act_digest",
            "order_identity",
            "idempotency_identity",
            "continuation_identity",
            "authority_act_identity",
            "authority_kind",
            "authority_requesting_owner_identity",
            "authority_target_identity",
            "authority_payload_digest",
            "authority_result_identity",
            "opaque_reference_set_identity",
            "ordered_reference_set_digest",
            "producing_owner_identity",
            "owner_state_identity",
            "owner_advancement",
            "owner_disposition",
            "next_act_identity",
            "refusal_identity",
            "terminal_identity",
            "owner_projection_identity",
            "failure_identity",
            "presentation_identity",
            "response_identity",
            "response_digest",
            "delivery_record_identity",
            "duplicate_resolution",
            "acknowledgement_state",
        ):
            _identity(getattr(self, field_name), field_name)
        _revision(self.continuation_sequence, "continuation sequence")
        _revision(self.authority_target_revision, "authority target revision")
        _revision(self.owner_revision_before, "owner revision before")
        _revision(self.owner_revision_after, "owner revision after")
        if self.delivery_status not in DELIVERY_STATUSES:
            raise FailClosedRuntimeError("CHE evidence delivery status is invalid")
        if self.evidence_status not in EVIDENCE_STATUSES:
            raise FailClosedRuntimeError("CHE evidence status is invalid")
        if self.replay_status not in REFERENCE_STATUSES:
            raise FailClosedRuntimeError("CHE Replay reference status is invalid")
        if self.certification_status not in REFERENCE_STATUSES:
            raise FailClosedRuntimeError(
                "CHE Certification reference status is invalid"
            )
        references = _reference_correlations(self.opaque_reference_correlations)
        replay = _string_tuple(self.replay_references, "Replay references")
        certification = _string_tuple(
            self.certification_references, "Certification references"
        )
        if bool(references) != (
            self.opaque_reference_set_identity != NOT_APPLICABLE
        ):
            raise FailClosedRuntimeError(
                "CHE opaque Reference set correlation is incomplete"
            )
        if bool(replay) != (self.replay_status == REFERENCE_CREATED):
            raise FailClosedRuntimeError("CHE Replay status binding is invalid")
        if bool(certification) != (
            self.certification_status == REFERENCE_CREATED
        ):
            raise FailClosedRuntimeError(
                "CHE Certification status binding is invalid"
            )
        if not isinstance(self.metadata, Mapping):
            raise FailClosedRuntimeError("CHE evidence metadata is invalid")
        metadata = _immutable_json(self.metadata)
        object.__setattr__(self, "opaque_reference_correlations", references)
        object.__setattr__(self, "replay_references", replay)
        object.__setattr__(self, "certification_references", certification)
        object.__setattr__(self, "metadata", metadata)
        if self.correlation_identity != canonical_che_evidence_correlation_identity_v1(
            self.to_dict()
        ):
            raise FailClosedRuntimeError(
                "CHE evidence correlation identity is invalid"
            )
        canonical_serialize(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            field_name: _plain_json(getattr(self, field_name))
            for field_name in sorted(_CORRELATION_FIELDS)
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CanonicalCHEEvidenceCorrelationV1":
        if not isinstance(value, dict) or set(value) != _CORRELATION_FIELDS:
            raise FailClosedRuntimeError(
                "CHE evidence correlation structure is invalid"
            )
        return cls(**value)


def create_canonical_che_evidence_correlation_v1(
    **facts: Any,
) -> CanonicalCHEEvidenceCorrelationV1:
    expected = _CORRELATION_FIELDS - {"correlation_identity"}
    if set(facts) != expected:
        raise FailClosedRuntimeError(
            "CHE evidence correlation facts are incomplete"
        )
    value = dict(facts)
    value["correlation_identity"] = canonical_che_evidence_correlation_identity_v1(
        value
    )
    return CanonicalCHEEvidenceCorrelationV1(**value)


def validate_canonical_che_evidence_correlation_v1(
    value: Any,
) -> CanonicalCHEEvidenceCorrelationV1:
    correlation = (
        CanonicalCHEEvidenceCorrelationV1.from_dict(value)
        if isinstance(value, dict)
        else value
    )
    if not isinstance(correlation, CanonicalCHEEvidenceCorrelationV1):
        raise FailClosedRuntimeError("CHE evidence correlation is invalid")
    canonical_serialize(correlation.to_dict())
    return correlation


def serialize_canonical_che_evidence_correlation_v1(
    value: CanonicalCHEEvidenceCorrelationV1,
) -> str:
    return canonical_serialize(
        validate_canonical_che_evidence_correlation_v1(value).to_dict()
    )


def deserialize_canonical_che_evidence_correlation_v1(
    serialized: str,
) -> CanonicalCHEEvidenceCorrelationV1:
    if not isinstance(serialized, str) or not serialized:
        raise FailClosedRuntimeError("CHE evidence serialization is required")
    try:
        value = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError("CHE evidence serialization is invalid") from exc
    return CanonicalCHEEvidenceCorrelationV1.from_dict(value)


def canonical_che_evidence_correlation_record_path_v1(
    runtime_scope_identity: str, correlation_identity: str
) -> Path:
    _identity(runtime_scope_identity, "runtime scope")
    _identity(correlation_identity, "correlation identity")
    digest = replay_hash(
        {"correlation_identity": correlation_identity}
    ).removeprefix("sha256:")
    return Path(runtime_scope_identity) / "canonical_che_evidence_correlations_v1" / (
        f"correlation-{digest}.json"
    )


def _record(correlation: CanonicalCHEEvidenceCorrelationV1) -> dict[str, Any]:
    value = {
        "record_version": CANONICAL_CHE_EVIDENCE_CORRELATION_RECORD_VERSION,
        "correlation": correlation.to_dict(),
        "integrity_hash": "",
    }
    value["integrity_hash"] = replay_hash(
        {key: item for key, item in value.items() if key != "integrity_hash"}
    )
    return value


def persist_canonical_che_evidence_correlation_v1(
    value: CanonicalCHEEvidenceCorrelationV1,
) -> Path:
    correlation = validate_canonical_che_evidence_correlation_v1(value)
    path = canonical_che_evidence_correlation_record_path_v1(
        correlation.runtime_scope_identity, correlation.correlation_identity
    )
    record = _record(correlation)
    if path.exists():
        if read_canonical_che_evidence_correlation_v1(path).to_dict() != correlation.to_dict():
            raise FailClosedRuntimeError("CHE evidence correlation identity conflicts")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".che-evidence-", suffix=".tmp", dir=path.parent, text=True
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(canonical_serialize(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        raise FailClosedRuntimeError("CHE evidence correlation write failed") from exc
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return path


def read_canonical_che_evidence_correlation_v1(
    path: str | Path,
) -> CanonicalCHEEvidenceCorrelationV1:
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("CHE evidence correlation is unreadable") from exc
    if not isinstance(record, dict) or set(record) != _RECORD_FIELDS:
        raise FailClosedRuntimeError("CHE evidence correlation record is invalid")
    if record["record_version"] != CANONICAL_CHE_EVIDENCE_CORRELATION_RECORD_VERSION:
        raise FailClosedRuntimeError("CHE evidence correlation record version is invalid")
    expected = replay_hash(
        {key: item for key, item in record.items() if key != "integrity_hash"}
    )
    if record["integrity_hash"] != expected:
        raise FailClosedRuntimeError("CHE evidence correlation integrity is invalid")
    return CanonicalCHEEvidenceCorrelationV1.from_dict(record["correlation"])


def reconstruct_canonical_che_evidence_journey_v1(
    value: CanonicalCHEEvidenceCorrelationV1 | dict[str, Any],
) -> dict[str, Any]:
    """Read-only exact reconstruction; absent facts remain explicit gaps."""

    correlation = validate_canonical_che_evidence_correlation_v1(value)
    facts = correlation.to_dict()
    gaps = tuple(
        field_name
        for field_name in sorted(_CORRELATION_FIELDS - {"metadata"})
        if isinstance(facts[field_name], str)
        and facts[field_name] in {NOT_APPLICABLE, NOT_RECORDED}
    )
    journey = (
        {"stage": "SOURCE_ACT", "owner": "HIC_SOURCE", "identity": correlation.source_act_identity},
        {"stage": "CHE_REQUEST", "owner": "CANONICAL_HUMAN_ENTRY", "identity": correlation.request_identity},
        {"stage": "OPAQUE_REFERENCES", "owner": "REFERENCE_OWNERS", "identity": correlation.opaque_reference_set_identity},
        {"stage": "HUMAN_AUTHORITY_ACT", "owner": "HUMAN_AUTHORITY", "identity": correlation.authority_act_identity},
        {"stage": "CONTINUATION", "owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT", "identity": correlation.continuation_identity},
        {"stage": "OWNER_TRANSITION", "owner": correlation.producing_owner_identity, "identity": correlation.owner_projection_identity},
        {"stage": "COMMON_FAILURE", "owner": correlation.producing_owner_identity, "identity": correlation.failure_identity},
        {"stage": "PRESENTATION", "owner": correlation.producing_owner_identity, "identity": correlation.presentation_identity},
        {"stage": "CANONICAL_RESPONSE", "owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT", "identity": correlation.response_identity},
        {"stage": "DELIVERY", "owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT", "identity": correlation.delivery_record_identity},
        {"stage": "REPLAY_REFERENCES", "owner": "OWNER_LOCAL_REPLAY", "identity": correlation.replay_status},
        {"stage": "CERTIFICATION_REFERENCES", "owner": "CERTIFICATION_OWNERS", "identity": correlation.certification_status},
    )
    result = {
        "reconstruction_version": CANONICAL_CHE_JOURNEY_RECONSTRUCTION_VERSION,
        "correlation_identity": correlation.correlation_identity,
        "evidence_status": correlation.evidence_status,
        "journey": list(journey),
        "explicit_gaps": list(gaps),
        "inference_performed": False,
        "repair_performed": False,
    }
    result["reconstruction_hash"] = replay_hash(result)
    return result


def reconstruct_canonical_che_evidence_record_v1(path: str | Path) -> dict[str, Any]:
    return reconstruct_canonical_che_evidence_journey_v1(
        read_canonical_che_evidence_correlation_v1(path)
    )


def observe_canonical_che_evidence_for_cro_v1(path: str | Path) -> dict[str, Any]:
    """Passive, post-hoc CRO adapter over one authenticated record."""

    reconstruction = reconstruct_canonical_che_evidence_record_v1(path)
    observation = {
        "observation_version": CANONICAL_CHE_CRO_OBSERVATION_VERSION,
        "correlation_identity": reconstruction["correlation_identity"],
        "reconstruction": reconstruction,
        "read_only": True,
        "post_hoc": True,
        "out_of_band": True,
        "authoritative": False,
        "runtime_predecessor": False,
        "inference_performed": False,
        "repair_performed": False,
    }
    observation["observation_hash"] = replay_hash(observation)
    return observation


def unavailable_pre_write_canonical_che_evidence_v1(
    *, request_identity: str = NOT_RECORDED, source_act_identity: str = NOT_RECORDED
) -> dict[str, Any]:
    """Report an absent pre-write record without fabricating correlation facts."""

    _identity(request_identity, "unavailable Request identity")
    _identity(source_act_identity, "unavailable source act identity")
    value = {
        "reconstruction_version": CANONICAL_CHE_JOURNEY_RECONSTRUCTION_VERSION,
        "correlation_identity": NOT_RECORDED,
        "request_identity": request_identity,
        "source_act_identity": source_act_identity,
        "evidence_status": UNAVAILABLE_PRE_WRITE,
        "explicit_gaps": ["CORRELATION_RECORD"],
        "inference_performed": False,
        "repair_performed": False,
    }
    value["reconstruction_hash"] = replay_hash(value)
    return value
