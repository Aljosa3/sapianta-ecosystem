"""Focused regression coverage for the G65-02 fixed evidence manifest."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    REQUIRED_SOURCE_CLASSES,
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
    build_self_knowledge_evidence_manifest,
    self_knowledge_evidence_manifest_source_paths,
    validate_self_knowledge_evidence_manifest,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _checked_in_manifest() -> dict:
    return json.loads(
        (REPOSITORY_ROOT / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH).read_text(encoding="utf-8")
    )


def test_checked_in_manifest_is_deterministic_and_valid() -> None:
    first = build_self_knowledge_evidence_manifest(REPOSITORY_ROOT)
    second = build_self_knowledge_evidence_manifest(REPOSITORY_ROOT)
    checked_in = _checked_in_manifest()

    assert first == second == checked_in
    assert validate_self_knowledge_evidence_manifest(checked_in, REPOSITORY_ROOT) == checked_in


def test_sources_are_canonically_ordered_and_cover_each_required_class() -> None:
    manifest = _checked_in_manifest()
    sources = manifest["sources"]

    assert [source["source_class"] for source in sources] == sorted(
        source["source_class"] for source in sources
    )
    assert [(source["source_class"], source["source_id"], source["path"]) for source in sources] == sorted(
        (source["source_class"], source["source_id"], source["path"]) for source in sources
    )
    assert tuple(manifest["required_source_classes"]) == REQUIRED_SOURCE_CLASSES
    assert set(source["source_class"] for source in sources) == set(REQUIRED_SOURCE_CLASSES)
    assert tuple(source["path"] for source in sources) == self_knowledge_evidence_manifest_source_paths()


def test_digest_tampering_fails_closed() -> None:
    tampered = deepcopy(_checked_in_manifest())
    tampered["sources"][0]["sha256"] = "sha256:" + "0" * 64

    with pytest.raises(FailClosedRuntimeError, match="source inventory or digest binding"):
        validate_self_knowledge_evidence_manifest(tampered, REPOSITORY_ROOT)


def test_noncanonical_source_order_fails_closed() -> None:
    tampered = deepcopy(_checked_in_manifest())
    tampered["sources"][0], tampered["sources"][1] = (
        tampered["sources"][1],
        tampered["sources"][0],
    )

    with pytest.raises(FailClosedRuntimeError, match="source inventory or digest binding"):
        validate_self_knowledge_evidence_manifest(tampered, REPOSITORY_ROOT)


def test_unknown_source_and_version_binding_fail_closed() -> None:
    unknown_source = deepcopy(_checked_in_manifest())
    unknown_source["sources"].append(deepcopy(unknown_source["sources"][0]))

    with pytest.raises(FailClosedRuntimeError, match="source inventory or digest binding"):
        validate_self_knowledge_evidence_manifest(unknown_source, REPOSITORY_ROOT)

    invalid_version = deepcopy(_checked_in_manifest())
    invalid_version["manifest_version"] = "UNBOUND_VERSION"

    with pytest.raises(FailClosedRuntimeError, match="manifest manifest_version is invalid"):
        validate_self_knowledge_evidence_manifest(invalid_version, REPOSITORY_ROOT)


def test_manifest_hash_tampering_fails_closed() -> None:
    tampered = deepcopy(_checked_in_manifest())
    tampered["manifest_hash"] = "sha256:" + "f" * 64

    with pytest.raises(FailClosedRuntimeError, match="manifest hash mismatch"):
        validate_self_knowledge_evidence_manifest(tampered, REPOSITORY_ROOT)


def test_implementation_does_not_import_discovery_or_execution_owners() -> None:
    source = (
        REPOSITORY_ROOT / "aigol/runtime/self_knowledge_evidence_manifest.py"
    ).read_text(encoding="utf-8")
    imports = {
        alias.name
        for node in ast.walk(ast.parse(source))
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
