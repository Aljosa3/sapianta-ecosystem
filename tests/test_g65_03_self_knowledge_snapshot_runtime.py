"""Focused G65-03 regressions for deterministic Self Knowledge snapshots."""

from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
)
from aigol.runtime.self_knowledge_snapshot_runtime import (
    SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS,
    SELF_KNOWLEDGE_SNAPSHOT_V1,
    SELF_KNOWLEDGE_SNAPSHOT_VERSION,
    build_self_knowledge_snapshot,
    validate_self_knowledge_snapshot,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    return json.loads(
        (REPOSITORY_ROOT / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH).read_text(encoding="utf-8")
    )


def _snapshot() -> dict:
    return build_self_knowledge_snapshot(
        manifest=_manifest(),
        repository_root=REPOSITORY_ROOT,
    )


def test_snapshot_construction_is_deterministic_and_manifest_compatible() -> None:
    manifest = _manifest()
    original_manifest = deepcopy(manifest)
    first = build_self_knowledge_snapshot(manifest=manifest, repository_root=REPOSITORY_ROOT)
    second = build_self_knowledge_snapshot(manifest=manifest, repository_root=REPOSITORY_ROOT)

    assert first == second
    assert manifest == original_manifest
    assert first["artifact_type"] == SELF_KNOWLEDGE_SNAPSHOT_V1
    assert first["snapshot_version"] == SELF_KNOWLEDGE_SNAPSHOT_VERSION
    assert first["manifest_hash"] == manifest["manifest_hash"]
    assert first["manifest_version"] == manifest["manifest_version"]
    assert first["required_source_classes"] == manifest["required_source_classes"]
    assert first["evidence_record_count"] == len(manifest["sources"]) == 26
    assert first["boundary_flags"] == SELF_KNOWLEDGE_SNAPSHOT_BOUNDARY_FLAGS


def test_snapshot_loads_exact_evidence_bytes_in_manifest_order() -> None:
    manifest = _manifest()
    snapshot = _snapshot()

    for source, record in zip(manifest["sources"], snapshot["evidence_records"]):
        for field in source:
            assert record[field] == source[field]
        content_bytes = record["content"].encode("utf-8")
        assert record["content_encoding"] == "UTF-8"
        assert record["content_byte_length"] == len(content_bytes)
        assert "sha256:" + sha256(content_bytes).hexdigest() == source["sha256"]


def test_snapshot_validation_is_read_only_and_uses_no_repository_io(monkeypatch) -> None:
    manifest = _manifest()
    snapshot = _snapshot()

    def fail_read_bytes(_path):
        raise AssertionError("snapshot integrity validation must not reread repository evidence")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)
    assert validate_self_knowledge_snapshot(snapshot, manifest=manifest) == snapshot


def test_evidence_content_tampering_fails_closed() -> None:
    manifest = _manifest()
    tampered = _snapshot()
    original = tampered["evidence_records"][0]["content"]
    replacement = "X" if original[0] != "X" else "Y"
    tampered["evidence_records"][0]["content"] = replacement + original[1:]

    with pytest.raises(FailClosedRuntimeError, match="content digest mismatch"):
        validate_self_knowledge_snapshot(tampered, manifest=manifest)


def test_evidence_manifest_binding_and_inventory_tampering_fail_closed() -> None:
    manifest = _manifest()
    changed_binding = _snapshot()
    changed_binding["evidence_records"][0]["source_id"] = "UNAUTHENTICATED_SOURCE"

    with pytest.raises(FailClosedRuntimeError, match="evidence manifest binding"):
        validate_self_knowledge_snapshot(changed_binding, manifest=manifest)

    incomplete = _snapshot()
    incomplete["evidence_records"].pop()
    incomplete["evidence_record_count"] -= 1

    with pytest.raises(FailClosedRuntimeError, match="evidence inventory is incomplete"):
        validate_self_knowledge_snapshot(incomplete, manifest=manifest)


def test_snapshot_identity_and_boundary_tampering_fail_closed() -> None:
    manifest = _manifest()
    changed_hash = _snapshot()
    changed_hash["snapshot_hash"] = "sha256:" + "0" * 64

    with pytest.raises(FailClosedRuntimeError, match="snapshot hash mismatch"):
        validate_self_knowledge_snapshot(changed_hash, manifest=manifest)

    changed_boundary = _snapshot()
    changed_boundary["boundary_flags"]["query_supported"] = True

    with pytest.raises(FailClosedRuntimeError, match="boundary flags"):
        validate_self_knowledge_snapshot(changed_boundary, manifest=manifest)


def test_incompatible_manifest_and_missing_evidence_fail_closed(tmp_path) -> None:
    incompatible = _manifest()
    incompatible["manifest_version"] = "UNBOUND_VERSION"

    with pytest.raises(FailClosedRuntimeError, match="manifest manifest_version is invalid"):
        build_self_knowledge_snapshot(
            manifest=incompatible,
            repository_root=REPOSITORY_ROOT,
        )

    with pytest.raises(FailClosedRuntimeError, match="manifest source is missing"):
        build_self_knowledge_snapshot(
            manifest=_manifest(),
            repository_root=tmp_path,
        )


def test_runtime_has_no_discovery_query_or_execution_owner_imports() -> None:
    source = (
        REPOSITORY_ROOT / "aigol/runtime/self_knowledge_snapshot_runtime.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    assert not any(name.startswith("query") or "answer" in name for name in functions)
    assert "subprocess" not in imports
    assert not any(
        "conversation" in imported or "provider" in imported or "worker" in imported
        for imported in imports
    )
    assert "os.walk" not in source
    assert ".rglob(" not in source
    assert ".glob(" not in source
