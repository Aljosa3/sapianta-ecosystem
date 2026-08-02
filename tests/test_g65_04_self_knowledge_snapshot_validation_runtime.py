"""Focused G65-04 regressions for authenticated snapshot validation."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
)
from aigol.runtime.self_knowledge_snapshot_runtime import (
    build_self_knowledge_snapshot,
)
from aigol.runtime.self_knowledge_snapshot_validation_runtime import (
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATED,
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1,
    SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION,
    validate_authenticated_self_knowledge_snapshot,
)
from aigol.runtime.transport.serialization import replay_hash


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    return json.loads(
        (REPOSITORY_ROOT / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH).read_text(encoding="utf-8")
    )


def _snapshot(manifest: dict | None = None) -> dict:
    return build_self_knowledge_snapshot(
        manifest=manifest or _manifest(),
        repository_root=REPOSITORY_ROOT,
    )


def _rehash(artifact: dict, hash_field: str) -> None:
    body = deepcopy(artifact)
    body.pop(hash_field, None)
    artifact[hash_field] = replay_hash(body)


def test_valid_snapshot_is_accepted_without_input_mutation() -> None:
    manifest = _manifest()
    snapshot = _snapshot(manifest)
    original_manifest = deepcopy(manifest)
    original_snapshot = deepcopy(snapshot)

    validation = validate_authenticated_self_knowledge_snapshot(
        snapshot=snapshot,
        manifest=manifest,
        repository_root=REPOSITORY_ROOT,
    )

    assert manifest == original_manifest
    assert snapshot == original_snapshot
    assert validation["artifact_type"] == SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ARTIFACT_V1
    assert validation["validation_runtime_version"] == (
        SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_RUNTIME_VERSION
    )
    assert validation["validation_status"] == SELF_KNOWLEDGE_SNAPSHOT_VALIDATED
    assert validation["snapshot_hash"] == snapshot["snapshot_hash"]
    assert validation["manifest_hash"] == manifest["manifest_hash"]
    assert validation["evidence_record_count"] == 26
    assert validation["manifest_compatibility_verified"] is True
    assert validation["integrity_verified"] is True
    assert validation["canonical_order_verified"] is True
    assert validation["completeness_verified"] is True
    assert validation["read_only"] is True
    assert validation["snapshot_modified"] is False
    assert validation["manifest_modified"] is False
    assert validation["repository_discovery_performed"] is False
    expected_hash = deepcopy(validation)
    expected_hash.pop("validation_hash")
    assert validation["validation_hash"] == replay_hash(expected_hash)


def test_corrupted_snapshot_is_rejected() -> None:
    manifest = _manifest()
    corrupted = _snapshot(manifest)
    original = corrupted["evidence_records"][0]["content"]
    corrupted["evidence_records"][0]["content"] = (
        ("X" if original[0] != "X" else "Y") + original[1:]
    )
    _rehash(corrupted["evidence_records"][0], "evidence_record_hash")
    _rehash(corrupted, "snapshot_hash")

    with pytest.raises(FailClosedRuntimeError, match="content digest mismatch"):
        validate_authenticated_self_knowledge_snapshot(
            snapshot=corrupted,
            manifest=manifest,
            repository_root=REPOSITORY_ROOT,
        )


def test_incomplete_snapshot_is_rejected() -> None:
    manifest = _manifest()
    incomplete = _snapshot(manifest)
    incomplete["evidence_records"].pop()
    incomplete["evidence_record_count"] -= 1
    _rehash(incomplete, "snapshot_hash")

    with pytest.raises(FailClosedRuntimeError, match="evidence inventory is incomplete"):
        validate_authenticated_self_knowledge_snapshot(
            snapshot=incomplete,
            manifest=manifest,
            repository_root=REPOSITORY_ROOT,
        )


def test_noncanonical_snapshot_order_is_rejected() -> None:
    manifest = _manifest()
    reordered = _snapshot(manifest)
    reordered["evidence_records"][0], reordered["evidence_records"][1] = (
        reordered["evidence_records"][1],
        reordered["evidence_records"][0],
    )
    _rehash(reordered, "snapshot_hash")

    with pytest.raises(FailClosedRuntimeError, match="manifest binding"):
        validate_authenticated_self_knowledge_snapshot(
            snapshot=reordered,
            manifest=manifest,
            repository_root=REPOSITORY_ROOT,
        )


def test_snapshot_manifest_mismatch_is_rejected() -> None:
    manifest = _manifest()
    mismatched = _snapshot(manifest)
    mismatched["manifest_hash"] = "sha256:" + "a" * 64
    _rehash(mismatched, "snapshot_hash")

    with pytest.raises(FailClosedRuntimeError, match="manifest_hash binding is invalid"):
        validate_authenticated_self_knowledge_snapshot(
            snapshot=mismatched,
            manifest=manifest,
            repository_root=REPOSITORY_ROOT,
        )


def test_rehashed_but_unauthenticated_manifest_is_rejected() -> None:
    manifest = _manifest()
    manifest["sources"][0]["sha256"] = "sha256:" + "b" * 64
    _rehash(manifest, "manifest_hash")

    with pytest.raises(FailClosedRuntimeError, match="source inventory or digest binding"):
        validate_authenticated_self_knowledge_snapshot(
            snapshot=_snapshot(),
            manifest=manifest,
            repository_root=REPOSITORY_ROOT,
        )


def test_validation_runtime_has_no_discovery_or_execution_owner_imports() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/self_knowledge_snapshot_validation_runtime.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert "subprocess" not in imports
    assert not any(
        "conversation" in imported or "provider" in imported or "worker" in imported
        for imported in imports
    )
    assert "os.walk" not in source
    assert ".rglob(" not in source
    assert ".glob(" not in source
