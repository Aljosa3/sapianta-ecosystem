"""Deterministic, read-only Self Knowledge Snapshot assembly.

The runtime loads only evidence named by an authenticated G65-02 manifest. It
does not discover files, interpret evidence, answer queries, invoke providers
or Workers, interact with Conversation, or mutate repository/replay state.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    REQUIRED_SOURCE_CLASSES,
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT,
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1,
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION,
    SOURCE_DIGEST_ALGORITHM,
    validate_self_knowledge_evidence_manifest,
)
from aigol.runtime.transport.serialization import replay_hash


SELF_KNOWLEDGE_SNAPSHOT_V1 = "SELF_KNOWLEDGE_SNAPSHOT_V1"
SELF_KNOWLEDGE_SNAPSHOT_VERSION = "G65_03_SELF_KNOWLEDGE_SNAPSHOT_RUNTIME_V1"
EVIDENCE_CONTENT_ENCODING = "UTF-8"

SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS = {
    "read_only": True,
    "query_supported": False,
    "evidence_semantics_interpreted": False,
    "repository_discovery_performed": False,
    "conversation_invoked": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "governance_modified": False,
    "replay_modified": False,
}

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
_MANIFEST_FIELDS = frozenset(
    {
        "artifact_type",
        "manifest_version",
        "manifest_contract",
        "constitutional_baseline",
        "self_knowledge_architecture_verdict",
        "source_digest_algorithm",
        "required_source_classes",
        "sources",
        "manifest_hash",
    }
)
_SOURCE_FIELDS = frozenset(
    {
        "source_id",
        "source_class",
        "path",
        "sha256",
        "schema_or_section_identifier",
        "authority_class",
        "required",
    }
)
_EVIDENCE_RECORD_FIELDS = _SOURCE_FIELDS.union(
    {
        "content_encoding",
        "content_byte_length",
        "content",
        "evidence_record_hash",
    }
)


def build_self_knowledge_snapshot(
    *,
    manifest: dict[str, Any],
    repository_root: str | Path,
) -> dict[str, Any]:
    """Build one deterministic snapshot from an authenticated V1 manifest."""

    root = _repository_root(repository_root)
    validated_manifest = validate_self_knowledge_evidence_manifest(manifest, root)
    evidence_records = [
        _load_evidence_record(root=root, source=source)
        for source in validated_manifest["sources"]
    ]
    snapshot = {
        "artifact_type": SELF_KNOWLEDGE_SNAPSHOT_V1,
        "snapshot_version": SELF_KNOWLEDGE_SNAPSHOT_VERSION,
        "manifest_artifact_type": validated_manifest["artifact_type"],
        "manifest_version": validated_manifest["manifest_version"],
        "manifest_contract": validated_manifest["manifest_contract"],
        "manifest_hash": validated_manifest["manifest_hash"],
        "source_digest_algorithm": validated_manifest["source_digest_algorithm"],
        "required_source_classes": deepcopy(validated_manifest["required_source_classes"]),
        "evidence_record_count": len(evidence_records),
        "evidence_records": evidence_records,
        "boundary_flags": deepcopy(SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS),
    }
    snapshot["snapshot_hash"] = replay_hash(snapshot)
    return snapshot


def validate_self_knowledge_snapshot(
    snapshot: dict[str, Any],
    *,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Validate snapshot integrity against its manifest without repository I/O."""

    validated_manifest = _validate_manifest_reference(manifest)
    if not isinstance(snapshot, dict) or set(snapshot) != _SNAPSHOT_FIELDS:
        _fail("snapshot schema is invalid")
    expected_header = {
        "artifact_type": SELF_KNOWLEDGE_SNAPSHOT_V1,
        "snapshot_version": SELF_KNOWLEDGE_SNAPSHOT_VERSION,
        "manifest_artifact_type": validated_manifest["artifact_type"],
        "manifest_version": validated_manifest["manifest_version"],
        "manifest_contract": validated_manifest["manifest_contract"],
        "manifest_hash": validated_manifest["manifest_hash"],
        "source_digest_algorithm": validated_manifest["source_digest_algorithm"],
        "required_source_classes": validated_manifest["required_source_classes"],
    }
    for field, expected_value in expected_header.items():
        if snapshot.get(field) != expected_value:
            _fail(f"snapshot {field} binding is invalid")
    if snapshot.get("boundary_flags") != SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS:
        _fail("snapshot boundary flags are invalid")
    records = snapshot.get("evidence_records")
    if not isinstance(records, list):
        _fail("snapshot evidence records must be a list")
    if snapshot.get("evidence_record_count") != len(records):
        _fail("snapshot evidence record count is invalid")
    if len(records) != len(validated_manifest["sources"]):
        _fail("snapshot evidence inventory is incomplete")
    for record, source in zip(records, validated_manifest["sources"]):
        _validate_evidence_record(record=record, source=source)
    snapshot_hash = snapshot.get("snapshot_hash")
    body = deepcopy(snapshot)
    body.pop("snapshot_hash", None)
    if snapshot_hash != replay_hash(body):
        _fail("snapshot hash mismatch")
    return deepcopy(snapshot)


def _load_evidence_record(*, root: Path, source: dict[str, Any]) -> dict[str, Any]:
    path = _resolve_manifest_path(root, source["path"])
    try:
        content_bytes = path.read_bytes()
    except OSError as exc:
        raise FailClosedRuntimeError(
            "SELF_KNOWLEDGE_SNAPSHOT_INVALID: evidence source cannot be read"
        ) from exc
    content_digest = f"sha256:{sha256(content_bytes).hexdigest()}"
    if content_digest != source["sha256"]:
        _fail("evidence source digest mismatch")
    try:
        content = content_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError(
            "SELF_KNOWLEDGE_SNAPSHOT_INVALID: evidence source is not UTF-8"
        ) from exc
    record = {
        **deepcopy(source),
        "content_encoding": EVIDENCE_CONTENT_ENCODING,
        "content_byte_length": len(content_bytes),
        "content": content,
    }
    record["evidence_record_hash"] = replay_hash(record)
    return record


def _validate_evidence_record(*, record: Any, source: dict[str, Any]) -> None:
    if not isinstance(record, dict) or set(record) != _EVIDENCE_RECORD_FIELDS:
        _fail("snapshot evidence record schema is invalid")
    for field in _SOURCE_FIELDS:
        if record.get(field) != source[field]:
            _fail("snapshot evidence manifest binding is invalid")
    if record.get("content_encoding") != EVIDENCE_CONTENT_ENCODING:
        _fail("snapshot evidence encoding is invalid")
    content = record.get("content")
    if not isinstance(content, str):
        _fail("snapshot evidence content is invalid")
    content_bytes = content.encode("utf-8", errors="strict")
    if record.get("content_byte_length") != len(content_bytes):
        _fail("snapshot evidence byte length is invalid")
    if f"sha256:{sha256(content_bytes).hexdigest()}" != source["sha256"]:
        _fail("snapshot evidence content digest mismatch")
    record_hash = record.get("evidence_record_hash")
    body = deepcopy(record)
    body.pop("evidence_record_hash", None)
    if record_hash != replay_hash(body):
        _fail("snapshot evidence record hash mismatch")


def _validate_manifest_reference(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != _MANIFEST_FIELDS:
        _fail("manifest reference schema is invalid")
    expected_header = {
        "artifact_type": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1,
        "manifest_version": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION,
        "manifest_contract": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT,
        "constitutional_baseline": "CONSTITUTIONAL_GOVERNANCE_CLOSED",
        "self_knowledge_architecture_verdict": "SELF_KNOWLEDGE_ARCHITECTURE_CERTIFIED",
        "source_digest_algorithm": SOURCE_DIGEST_ALGORITHM,
        "required_source_classes": list(REQUIRED_SOURCE_CLASSES),
    }
    for field, expected_value in expected_header.items():
        if manifest.get(field) != expected_value:
            _fail(f"manifest reference {field} is invalid")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        _fail("manifest reference sources are invalid")
    identities: list[tuple[str, str, str]] = []
    for source in sources:
        if not isinstance(source, dict) or set(source) != _SOURCE_FIELDS:
            _fail("manifest reference source schema is invalid")
        if source.get("required") is not True:
            _fail("manifest reference source is not required")
        if source.get("source_class") not in REQUIRED_SOURCE_CLASSES:
            _fail("manifest reference source class is invalid")
        for field in (
            "source_id",
            "source_class",
            "path",
            "schema_or_section_identifier",
            "authority_class",
        ):
            if not isinstance(source.get(field), str) or not source[field]:
                _fail(f"manifest reference source {field} is invalid")
        digest = source.get("sha256")
        if not isinstance(digest, str) or len(digest) != 71 or not digest.startswith("sha256:"):
            _fail("manifest reference source digest is invalid")
        try:
            int(digest.removeprefix("sha256:"), 16)
        except ValueError:
            _fail("manifest reference source digest is invalid")
        identities.append((source["source_class"], source["source_id"], source["path"]))
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        _fail("manifest reference source order or identity is invalid")
    if set(source["source_class"] for source in sources) != set(REQUIRED_SOURCE_CLASSES):
        _fail("manifest reference required source classes are incomplete")
    body = deepcopy(manifest)
    manifest_hash = body.pop("manifest_hash", None)
    if manifest_hash != replay_hash(body):
        _fail("manifest reference hash mismatch")
    return deepcopy(manifest)


def _repository_root(repository_root: str | Path) -> Path:
    root = Path(repository_root)
    if not root.is_dir():
        _fail("repository root is invalid")
    return root.resolve()


def _resolve_manifest_path(root: Path, relative_path: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        _fail("evidence source path is invalid")
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        _fail("evidence source path escapes repository root")
    if not candidate.is_file():
        _fail("evidence source is missing")
    return candidate


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"SELF_KNOWLEDGE_SNAPSHOT_INVALID: {message}")


__all__ = [
    "EVIDENCE_CONTENT_ENCODING",
    "SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS",
    "SELF_KNOWLEDGE_SNAPSHOT_V1",
    "SELF_KNOWLEDGE_SNAPSHOT_VERSION",
    "build_self_knowledge_snapshot",
    "validate_self_knowledge_snapshot",
]
