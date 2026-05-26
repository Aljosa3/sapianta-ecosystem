"""Tests for REAL_READONLY_FILESYSTEM_PROVIDER_V1."""

from __future__ import annotations

import inspect
import os

import pytest

from aigol.runtime.providers import ReadOnlyFilesystemProvider


def _provider(root) -> ReadOnlyFilesystemProvider:
    return ReadOnlyFilesystemProvider([root])


def test_allowed_file_metadata_inspection(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("hello filesystem", encoding="utf-8")

    evidence = _provider(tmp_path).inspect_metadata(target)

    assert evidence["operation"] == "inspect_metadata"
    assert evidence["allowed"] is True
    assert evidence["status"] == "METADATA_INSPECTED"
    assert evidence["metadata"]["size_bytes"] == len("hello filesystem")
    assert evidence["evidence_hash"].startswith("sha256:")


def test_allowed_bounded_file_read(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("abcdef", encoding="utf-8")

    evidence = _provider(tmp_path).read_file(target, max_bytes=3)

    assert evidence["allowed"] is True
    assert evidence["status"] == "FILE_READ"
    assert evidence["bytes_read"] == 3
    assert evidence["content"] == "abc"
    assert evidence["content_hash"].startswith("sha256:")


def test_allowed_non_recursive_directory_listing(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "hidden.txt").write_text("hidden", encoding="utf-8")

    evidence = _provider(tmp_path).list_allowed_directory(tmp_path, max_entries=10)

    assert evidence["allowed"] is True
    assert evidence["status"] == "DIRECTORY_LISTED"
    assert evidence["entries_returned"] == 2
    assert [entry["name"] for entry in evidence["entries"]] == ["a.txt", "nested"]
    assert "hidden.txt" not in [entry["name"] for entry in evidence["entries"]]


def test_path_traversal_rejection(tmp_path) -> None:
    safe = tmp_path / "safe"
    safe.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("secret", encoding="utf-8")
    traversal = safe / ".." / "secret.txt"

    evidence = _provider(safe).read_file(traversal, max_bytes=10)

    assert evidence["allowed"] is False
    assert evidence["status"] == "FAIL_CLOSED"
    assert "traversal" in evidence["reason"]
    assert evidence["bytes_read"] == 0


def test_symlink_rejection(tmp_path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")

    evidence = _provider(tmp_path).read_file(link, max_bytes=20)

    assert evidence["allowed"] is False
    assert evidence["status"] == "FAIL_CLOSED"
    assert "symlink" in evidence["reason"]


def test_outside_allowlist_rejection(tmp_path) -> None:
    safe = tmp_path / "safe"
    safe.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    evidence = _provider(safe).inspect_metadata(outside)

    assert evidence["allowed"] is False
    assert evidence["status"] == "FAIL_CLOSED"
    assert "outside allowlist" in evidence["reason"]


def test_missing_allowlist_fails_closed(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("sample", encoding="utf-8")

    evidence = ReadOnlyFilesystemProvider([]).read_file(target, max_bytes=10)

    assert evidence["allowed"] is False
    assert evidence["status"] == "FAIL_CLOSED"
    assert "allowlist" in evidence["reason"]


def test_max_bytes_enforcement(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("0123456789", encoding="utf-8")

    evidence = _provider(tmp_path).read_file(target, max_bytes=4)

    assert evidence["bytes_read"] == 4
    assert evidence["content"] == "0123"


def test_deterministic_evidence_structure(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("stable", encoding="utf-8")

    first = _provider(tmp_path).read_file(target, max_bytes=10)
    second = _provider(tmp_path).read_file(target, max_bytes=10)

    assert first == second
    assert set(first) >= {
        "operation",
        "requested_path",
        "normalized_path",
        "allowed",
        "status",
        "reason",
        "bytes_read",
        "entries_returned",
        "evidence_hash",
    }


def test_no_write_subprocess_shell_or_recursive_crawling_surface() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(ReadOnlyFilesystemProvider, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    source = inspect.getsource(ReadOnlyFilesystemProvider)

    assert public_methods == {"inspect_metadata", "read_file", "list_allowed_directory"}
    assert "subprocess" not in source
    assert "system(" not in source
    assert ".write" not in source
    assert "chmod" not in source
    assert "chown" not in source
    assert "mkdir" not in source
    assert "rglob" not in source
    assert "os.walk" not in source
    assert os.name
