"""Deterministic read-only projection over one validated Self Knowledge Snapshot.

The runtime accepts only the closed G65-05 subject vocabulary. It performs no
repository I/O, evidence reconstruction, semantic inference, natural-language
generation, Conversation interaction, or execution-owner invocation.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from types import MappingProxyType
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_snapshot_runtime import (
    EVIDENCE_CONTENT_ENCODING,
    SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS,
    SELF_KNOWLEDGE_SNAPSHOT_V1,
    SELF_KNOWLEDGE_SNAPSHOT_VERSION,
)
from aigol.runtime.self_knowledge_snapshot_validation_runtime import (
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATED,
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1,
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION,
)
from aigol.runtime.transport.serialization import replay_hash


SELF_KNOWLEDGE_QUERY_REQUEST_V1 = "SELF_KNOWLEDGE_QUERY_REQUEST_V1"
SELF_KNOWLEDGE_QUERY_REQUEST_VERSION = "G65_05_SELF_KNOWLEDGE_QUERY_REQUEST_V1"
SELF_KNOWLEDGE_QUERY_RESPONSE_V1 = "SELF_KNOWLEDGE_QUERY_RESPONSE_V1"
SELF_KNOWLEDGE_QUERY_RESPONSE_VERSION = "G65_05_SELF_KNOWLEDGE_QUERY_RESPONSE_V1"

AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
AUTHENTICATED_EVIDENCE_UNAVAILABLE = "AUTHENTICATED_EVIDENCE_UNAVAILABLE"
AUTHENTICATED_EVIDENCE_CONFLICT = "AUTHENTICATED_EVIDENCE_CONFLICT"

SUPPORTED_QUERY_SUBJECTS = (
    "ARCHITECTURE",
    "RUNTIME_INVENTORY",
    "CERTIFIED_CAPABILITIES",
    "OWNERSHIP",
    "GOVERNANCE_STATE",
    "EXECUTION_BOUNDARIES",
    "CERTIFIED_HISTORY",
    "KNOWN_LIMITATIONS",
)

_VIEW_SOURCE_CLASSES = MappingProxyType(
    {
        "ARCHITECTURE": ("CONSTITUTION", "ENFORCEMENT_AND_LINEAGE"),
        "RUNTIME_INVENTORY": ("CAPABILITY_REGISTRY",),
        "CERTIFIED_CAPABILITIES": ("CAPABILITY_REGISTRY",),
        "OWNERSHIP": ("OWNER_AND_BOUNDARY",),
        "GOVERNANCE_STATE": ("GOVERNANCE_STATE",),
        "EXECUTION_BOUNDARIES": ("ENFORCEMENT_AND_LINEAGE", "OWNER_AND_BOUNDARY"),
        "CERTIFIED_HISTORY": ("CERTIFIED_HISTORY",),
        "KNOWN_LIMITATIONS": ("KNOWN_LIMITATION",),
    }
)

SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS = {
    "read_only": True,
    "exact_source_projection": True,
    "semantic_interpretation_performed": False,
    "conflict_reconciliation_performed": False,
    "dynamic_ranking_performed": False,
    "latest_source_selected": False,
    "natural_language_explanation_generated": False,
    "objective_created": False,
    "reuse_proof_created": False,
    "g47_request_created": False,
    "authorization_created": False,
    "worker_request_created": False,
    "provider_request_created": False,
    "replay_event_created": False,
    "governance_modified": False,
    "execution_initiated": False,
}

_REQUEST_FIELDS = frozenset(
    {
        "artifact_type",
        "request_version",
        "query_subject",
        "snapshot_artifact_type",
        "snapshot_version",
        "snapshot_hash",
        "snapshot_validation_hash",
        "read_only",
        "request_hash",
    }
)
_RESPONSE_FIELDS = frozenset(
    {
        "artifact_type",
        "response_version",
        "request_hash",
        "query_subject",
        "projection_status",
        "unavailable_reason",
        "snapshot_artifact_type",
        "snapshot_version",
        "snapshot_hash",
        "manifest_artifact_type",
        "manifest_version",
        "manifest_hash",
        "snapshot_validation_hash",
        "projected_source_classes",
        "fact_count",
        "facts",
        "boundary_flags",
        "response_hash",
    }
)
_SNAPSHOT_FIELDS = frozenset(
    {
        "artifact_type",
        "snapshot_version",
        "manifest_artifact_type",
        "manifest_version",
        "manifest_contract",
        "manifest_hash",
        "source_digest_algorithm",
        "required_source_classes",
        "evidence_record_count",
        "evidence_records",
        "boundary_flags",
        "snapshot_hash",
    }
)
_EVIDENCE_RECORD_FIELDS = frozenset(
    {
        "source_id",
        "source_class",
        "path",
        "sha256",
        "schema_or_section_identifier",
        "authority_class",
        "required",
        "content_encoding",
        "content_byte_length",
        "content",
        "evidence_record_hash",
    }
)
_VALIDATION_FIELDS = frozenset(
    {
        "artifact_type",
        "validation_runtime_version",
        "validation_status",
        "snapshot_artifact_type",
        "snapshot_version",
        "snapshot_hash",
        "manifest_artifact_type",
        "manifest_version",
        "manifest_hash",
        "evidence_record_count",
        "required_source_classes",
        "manifest_compatibility_verified",
        "integrity_verified",
        "canonical_order_verified",
        "completeness_verified",
        "read_only",
        "snapshot_modified",
        "manifest_modified",
        "repository_discovery_performed",
        "validation_hash",
    }
)
_FORBIDDEN_AUTHORITY_FIELDS = frozenset(
    {
        "objective",
        "objective_id",
        "reuse_proof",
        "g47_request",
        "authorization",
        "authorization_id",
        "worker",
        "worker_request",
        "provider",
        "provider_request",
        "replay",
        "replay_event",
        "governance",
        "governance_mutation",
        "execution",
        "execution_request",
    }
)


def create_self_knowledge_query_request(
    *,
    query_subject: str,
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:
    """Create one closed query request for an exact supported subject."""

    validated_snapshot = _validate_snapshot_envelope(snapshot)
    validated_validation = _validate_snapshot_validation(
        snapshot_validation,
        snapshot=validated_snapshot,
    )
    _require_supported_subject(query_subject)
    request = {
        "artifact_type": SELF_KNOWLEDGE_QUERY_REQUEST_V1,
        "request_version": SELF_KNOWLEDGE_QUERY_REQUEST_VERSION,
        "query_subject": query_subject,
        "snapshot_artifact_type": validated_snapshot["artifact_type"],
        "snapshot_version": validated_snapshot["snapshot_version"],
        "snapshot_hash": validated_snapshot["snapshot_hash"],
        "snapshot_validation_hash": validated_validation["validation_hash"],
        "read_only": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_self_knowledge_query_request(
    request: dict[str, Any],
    *,
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:
    """Validate a closed query request and its snapshot identities."""

    _reject_authority_fields(request)
    validated_snapshot = _validate_snapshot_envelope(snapshot)
    validated_validation = _validate_snapshot_validation(
        snapshot_validation,
        snapshot=validated_snapshot,
    )
    if not isinstance(request, dict) or set(request) != _REQUEST_FIELDS:
        _fail("query request schema is invalid")
    _require_supported_subject(request.get("query_subject"))
    expected = {
        "artifact_type": SELF_KNOWLEDGE_QUERY_REQUEST_V1,
        "request_version": SELF_KNOWLEDGE_QUERY_REQUEST_VERSION,
        "snapshot_artifact_type": validated_snapshot["artifact_type"],
        "snapshot_version": validated_snapshot["snapshot_version"],
        "snapshot_hash": validated_snapshot["snapshot_hash"],
        "snapshot_validation_hash": validated_validation["validation_hash"],
        "read_only": True,
    }
    for field, expected_value in expected.items():
        if request.get(field) != expected_value:
            _fail(f"query request {field} binding is invalid")
    body = deepcopy(request)
    request_hash = body.pop("request_hash", None)
    if request_hash != replay_hash(body):
        _fail("query request hash mismatch")
    return deepcopy(request)


def execute_self_knowledge_query(
    *,
    request: dict[str, Any],
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:
    """Project one deterministic bounded view from a validated snapshot."""

    validated_request = validate_self_knowledge_query_request(
        request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    validated_snapshot = _validate_snapshot_envelope(snapshot)
    validated_validation = _validate_snapshot_validation(
        snapshot_validation,
        snapshot=validated_snapshot,
    )
    subject = validated_request["query_subject"]
    projected_classes = _VIEW_SOURCE_CLASSES[subject]
    facts = [
        deepcopy(record)
        for record in validated_snapshot["evidence_records"]
        if record["source_class"] in projected_classes
    ]
    projection_status, unavailable_reason = _projection_disposition(facts)
    if projection_status == UNAVAILABLE:
        facts = []
    response = {
        "artifact_type": SELF_KNOWLEDGE_QUERY_RESPONSE_V1,
        "response_version": SELF_KNOWLEDGE_QUERY_RESPONSE_VERSION,
        "request_hash": validated_request["request_hash"],
        "query_subject": subject,
        "projection_status": projection_status,
        "unavailable_reason": unavailable_reason,
        "snapshot_artifact_type": validated_snapshot["artifact_type"],
        "snapshot_version": validated_snapshot["snapshot_version"],
        "snapshot_hash": validated_snapshot["snapshot_hash"],
        "manifest_artifact_type": validated_snapshot["manifest_artifact_type"],
        "manifest_version": validated_snapshot["manifest_version"],
        "manifest_hash": validated_snapshot["manifest_hash"],
        "snapshot_validation_hash": validated_validation["validation_hash"],
        "projected_source_classes": list(projected_classes),
        "fact_count": len(facts),
        "facts": facts,
        "boundary_flags": deepcopy(SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS),
    }
    response["response_hash"] = replay_hash(response)
    return response


def validate_self_knowledge_query_response(
    response: dict[str, Any],
    *,
    request: dict[str, Any],
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:
    """Validate a response by deterministic reconstruction from its inputs."""

    if not isinstance(response, dict) or set(response) != _RESPONSE_FIELDS:
        _fail("query response schema is invalid")
    if response.get("boundary_flags") != SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS:
        _fail("query response boundary flags are invalid")
    body = deepcopy(response)
    response_hash = body.pop("response_hash", None)
    if response_hash != replay_hash(body):
        _fail("query response hash mismatch")
    expected = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    if response != expected:
        _fail("query response deterministic reconstruction mismatch")
    return deepcopy(response)


def _validate_snapshot_envelope(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or set(snapshot) != _SNAPSHOT_FIELDS:
        _fail("snapshot schema is invalid")
    if snapshot.get("artifact_type") != SELF_KNOWLEDGE_SNAPSHOT_V1:
        _fail("snapshot artifact type is invalid")
    if snapshot.get("snapshot_version") != SELF_KNOWLEDGE_SNAPSHOT_VERSION:
        _fail("snapshot version is invalid")
    if snapshot.get("boundary_flags") != SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS:
        _fail("snapshot boundary flags are invalid")
    records = snapshot.get("evidence_records")
    if not isinstance(records, list) or snapshot.get("evidence_record_count") != len(records):
        _fail("snapshot evidence inventory is invalid")
    identities: list[tuple[str, str, str]] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != _EVIDENCE_RECORD_FIELDS:
            _fail("snapshot evidence record schema is invalid")
        if record.get("required") is not True:
            _fail("snapshot evidence record is not required")
        for field in (
            "source_id",
            "source_class",
            "path",
            "sha256",
            "schema_or_section_identifier",
            "authority_class",
            "content",
            "evidence_record_hash",
        ):
            if not isinstance(record.get(field), str) or not record[field]:
                _fail(f"snapshot evidence record {field} is invalid")
        if record.get("content_encoding") != EVIDENCE_CONTENT_ENCODING:
            _fail("snapshot evidence encoding is invalid")
        content_bytes = record["content"].encode("utf-8", errors="strict")
        if record.get("content_byte_length") != len(content_bytes):
            _fail("snapshot evidence byte length is invalid")
        if record["sha256"] != f"sha256:{sha256(content_bytes).hexdigest()}":
            _fail("snapshot evidence content digest mismatch")
        record_body = deepcopy(record)
        record_hash = record_body.pop("evidence_record_hash")
        if record_hash != replay_hash(record_body):
            _fail("snapshot evidence record hash mismatch")
        identities.append((record["source_class"], record["source_id"], record["path"]))
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        _fail("snapshot evidence ordering is invalid")
    snapshot_body = deepcopy(snapshot)
    snapshot_hash = snapshot_body.pop("snapshot_hash", None)
    if snapshot_hash != replay_hash(snapshot_body):
        _fail("snapshot hash mismatch")
    return deepcopy(snapshot)


def _validate_snapshot_validation(
    validation: Any,
    *,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(validation, dict) or set(validation) != _VALIDATION_FIELDS:
        _fail("snapshot validation artifact schema is invalid")
    expected = {
        "artifact_type": SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1,
        "validation_runtime_version": SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION,
        "validation_status": SELF_KNOWLEDGE_SNAPSHOT_VALIDATED,
        "snapshot_artifact_type": snapshot["artifact_type"],
        "snapshot_version": snapshot["snapshot_version"],
        "snapshot_hash": snapshot["snapshot_hash"],
        "manifest_artifact_type": snapshot["manifest_artifact_type"],
        "manifest_version": snapshot["manifest_version"],
        "manifest_hash": snapshot["manifest_hash"],
        "evidence_record_count": snapshot["evidence_record_count"],
        "required_source_classes": snapshot["required_source_classes"],
        "manifest_compatibility_verified": True,
        "integrity_verified": True,
        "canonical_order_verified": True,
        "completeness_verified": True,
        "read_only": True,
        "snapshot_modified": False,
        "manifest_modified": False,
        "repository_discovery_performed": False,
    }
    for field, expected_value in expected.items():
        if validation.get(field) != expected_value:
            _fail(f"snapshot validation {field} binding is invalid")
    body = deepcopy(validation)
    validation_hash = body.pop("validation_hash", None)
    if validation_hash != replay_hash(body):
        _fail("snapshot validation hash mismatch")
    return deepcopy(validation)


def _projection_disposition(facts: list[dict[str, Any]]) -> tuple[str, str | None]:
    if not facts:
        return UNAVAILABLE, AUTHENTICATED_EVIDENCE_UNAVAILABLE
    observed: dict[tuple[str, str], tuple[str, str]] = {}
    for fact in facts:
        identity = (fact["source_class"], fact["source_id"])
        binding = (fact["path"], fact["sha256"])
        prior = observed.get(identity)
        if prior is not None and prior != binding:
            return UNAVAILABLE, AUTHENTICATED_EVIDENCE_CONFLICT
        observed[identity] = binding
    return AVAILABLE, None


def _require_supported_subject(value: Any) -> None:
    if not isinstance(value, str) or value not in SUPPORTED_QUERY_SUBJECTS:
        _fail("query subject is unsupported, malformed, free-form, or ambiguous")


def _reject_authority_fields(value: Any) -> None:
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            forbidden = _FORBIDDEN_AUTHORITY_FIELDS.intersection(item)
            if forbidden:
                _fail(f"authority-shaped query field is forbidden: {sorted(forbidden)[0]}")
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"SELF_KNOWLEDGE_QUERY_INVALID: {message}")


__all__ = [
    "AUTHENTICATED_EVIDENCE_CONFLICT",
    "AUTHENTICATED_EVIDENCE_UNAVAILABLE",
    "AVAILABLE",
    "SELF_KNOWLEDGE_QUERY_REQUEST_V1",
    "SELF_KNOWLEDGE_QUERY_REQUEST_VERSION",
    "SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS",
    "SELF_KNOWLEDGE_QUERY_RESPONSE_V1",
    "SELF_KNOWLEDGE_QUERY_RESPONSE_VERSION",
    "SUPPORTED_QUERY_SUBJECTS",
    "UNAVAILABLE",
    "create_self_knowledge_query_request",
    "execute_self_knowledge_query",
    "validate_self_knowledge_query_request",
    "validate_self_knowledge_query_response",
]
