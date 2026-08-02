"""Authenticated validation owner for Self Knowledge Snapshots.

The runtime composes the existing G65-02 manifest authentication owner and
G65-03 snapshot integrity owner. It performs no repository discovery and does
not modify either supplied artifact.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    validate_self_knowledge_evidence_manifest,
)
from aigol.runtime.self_knowledge_snapshot_runtime import (
    validate_self_knowledge_snapshot,
)
from aigol.runtime.transport.serialization import replay_hash


SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1 = (
    "SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1"
)
SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION = (
    "G65_04_SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_V1"
)
SELF_KNOWLEDGE_SNAPSHOT_VALIDATED = "SELF_KNOWLEDGE_SNAPSHOT_VALIDATED"

_SOURCE_IDENTITY_FIELDS = ("source_class", "source_id", "path")


def validate_authenticated_self_knowledge_snapshot(
    *,
    snapshot: dict[str, Any],
    manifest: dict[str, Any],
    repository_root: str | Path,
) -> dict[str, Any]:
    """Authenticate one complete, canonically ordered snapshot read-only."""

    validated_manifest = validate_self_knowledge_evidence_manifest(
        manifest,
        repository_root,
    )
    validated_snapshot = validate_self_knowledge_snapshot(
        snapshot,
        manifest=validated_manifest,
    )
    _validate_canonical_order(
        evidence_records=validated_snapshot["evidence_records"],
        sources=validated_manifest["sources"],
    )
    _validate_completeness(
        snapshot=validated_snapshot,
        manifest=validated_manifest,
    )
    validation = {
        "artifact_type": SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1,
        "validation_runtime_version": SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION,
        "validation_status": SELF_KNOWLEDGE_SNAPSHOT_VALIDATED,
        "snapshot_artifact_type": validated_snapshot["artifact_type"],
        "snapshot_version": validated_snapshot["snapshot_version"],
        "snapshot_hash": validated_snapshot["snapshot_hash"],
        "manifest_artifact_type": validated_manifest["artifact_type"],
        "manifest_version": validated_manifest["manifest_version"],
        "manifest_hash": validated_manifest["manifest_hash"],
        "evidence_record_count": validated_snapshot["evidence_record_count"],
        "required_source_classes": deepcopy(validated_manifest["required_source_classes"]),
        "manifest_compatibility_verified": True,
        "integrity_verified": True,
        "canonical_order_verified": True,
        "completeness_verified": True,
        "read_only": True,
        "snapshot_modified": False,
        "manifest_modified": False,
        "repository_discovery_performed": False,
    }
    validation["validation_hash"] = replay_hash(validation)
    return validation


def _validate_canonical_order(
    *,
    evidence_records: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> None:
    source_identities = [_source_identity(source) for source in sources]
    record_identities = [_source_identity(record) for record in evidence_records]
    if source_identities != sorted(source_identities):
        _fail("authenticated manifest source order is not canonical")
    if len(source_identities) != len(set(source_identities)):
        _fail("authenticated manifest source identity is duplicated")
    if record_identities != source_identities:
        _fail("snapshot evidence order is not manifest canonical order")


def _validate_completeness(
    *,
    snapshot: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    sources = manifest["sources"]
    records = snapshot["evidence_records"]
    if snapshot["evidence_record_count"] != len(sources) or len(records) != len(sources):
        _fail("snapshot evidence inventory is incomplete")
    required_classes = manifest["required_source_classes"]
    source_classes = {source["source_class"] for source in sources}
    record_classes = {record["source_class"] for record in records}
    if source_classes != set(required_classes) or record_classes != set(required_classes):
        _fail("snapshot required source classes are incomplete")
    for source, record in zip(sources, records):
        for field, expected_value in source.items():
            if record.get(field) != expected_value:
                _fail("snapshot is not fully derived from authenticated manifest")


def _source_identity(value: dict[str, Any]) -> tuple[str, str, str]:
    try:
        return (
            value[_SOURCE_IDENTITY_FIELDS[0]],
            value[_SOURCE_IDENTITY_FIELDS[1]],
            value[_SOURCE_IDENTITY_FIELDS[2]],
        )
    except (KeyError, TypeError) as exc:
        raise FailClosedRuntimeError(
            "SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_FAILED: source identity is invalid"
        ) from exc


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_FAILED: {message}")


__all__ = [
    "SELF_KNOWLEDGE_SNAPSHOT_VALIDATED",
    "SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1",
    "SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION",
    "validate_authenticated_self_knowledge_snapshot",
]
