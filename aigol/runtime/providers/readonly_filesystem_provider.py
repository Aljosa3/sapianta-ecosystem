"""Bounded read-only filesystem provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


class ReadOnlyFilesystemProvider:
    """Read-only filesystem access through explicit safe path allowlists."""

    def __init__(self, allowed_roots: list[str | Path]) -> None:
        self._allowed_roots = tuple(Path(root) for root in allowed_roots)

    def inspect_metadata(self, path: str | Path) -> dict[str, Any]:
        return self._operate("inspect_metadata", path, self._inspect_metadata)

    def read_file(self, path: str | Path, max_bytes: int) -> dict[str, Any]:
        if not isinstance(max_bytes, int) or max_bytes < 0:
            return self._evidence("read_file", path, "", False, "FAIL_CLOSED", "max_bytes must be non-negative", bytes_read=0)
        return self._operate("read_file", path, lambda normalized: self._read_file(normalized, max_bytes))

    def list_allowed_directory(self, path: str | Path, max_entries: int) -> dict[str, Any]:
        if not isinstance(max_entries, int) or max_entries < 0:
            return self._evidence(
                "list_allowed_directory",
                path,
                "",
                False,
                "FAIL_CLOSED",
                "max_entries must be non-negative",
                entries_returned=0,
            )
        return self._operate(
            "list_allowed_directory",
            path,
            lambda normalized: self._list_allowed_directory(normalized, max_entries),
        )

    def _operate(self, operation: str, requested_path: str | Path, handler) -> dict[str, Any]:
        try:
            normalized = self._normalize_allowed_path(requested_path)
            return handler(normalized)
        except OSError as exc:
            return self._evidence(operation, requested_path, "", False, "FAIL_CLOSED", str(exc))

    def _normalize_allowed_path(self, requested_path: str | Path) -> Path:
        if not self._allowed_roots:
            raise OSError("allowlist is required")
        requested = Path(requested_path)
        if ".." in requested.parts:
            raise OSError("path traversal is rejected")
        if not requested.exists():
            raise OSError("path does not exist")
        self._reject_symlink_component(requested)
        normalized = requested.resolve(strict=True)
        allowed_roots = []
        for root in self._allowed_roots:
            if not root.exists():
                raise OSError("allowlist root does not exist")
            self._reject_symlink_component(root)
            allowed_roots.append(root.resolve(strict=True))
        if not any(normalized == root or root in normalized.parents for root in allowed_roots):
            raise OSError("path is outside allowlist")
        return normalized

    def _reject_symlink_component(self, path: Path) -> None:
        current = Path(path.anchor) if path.is_absolute() else Path()
        for part in path.parts:
            if part == path.anchor:
                continue
            current = current / part
            if current.is_symlink():
                raise OSError("symlink traversal is rejected")

    def _inspect_metadata(self, normalized: Path) -> dict[str, Any]:
        try:
            stat = normalized.stat()
        except OSError as exc:
            return self._evidence("inspect_metadata", normalized, str(normalized), False, "FAIL_CLOSED", str(exc))
        return self._evidence(
            "inspect_metadata",
            normalized,
            str(normalized),
            True,
            "METADATA_INSPECTED",
            "metadata inspected",
            metadata={
                "name": normalized.name,
                "path_type": "directory" if normalized.is_dir() else "file" if normalized.is_file() else "other",
                "size_bytes": stat.st_size,
            },
        )

    def _read_file(self, normalized: Path, max_bytes: int) -> dict[str, Any]:
        if not normalized.is_file():
            return self._evidence("read_file", normalized, str(normalized), False, "FAIL_CLOSED", "path is not a file", bytes_read=0)
        try:
            with normalized.open("rb") as handle:
                data = handle.read(max_bytes)
        except OSError as exc:
            return self._evidence("read_file", normalized, str(normalized), False, "FAIL_CLOSED", str(exc), bytes_read=0)
        return self._evidence(
            "read_file",
            normalized,
            str(normalized),
            True,
            "FILE_READ",
            "bounded read completed",
            bytes_read=len(data),
            content_hash=replay_hash({"bytes": data.hex()}),
            content=data.decode("utf-8", errors="replace"),
        )

    def _list_allowed_directory(self, normalized: Path, max_entries: int) -> dict[str, Any]:
        if not normalized.is_dir():
            return self._evidence(
                "list_allowed_directory",
                normalized,
                str(normalized),
                False,
                "FAIL_CLOSED",
                "path is not a directory",
                entries_returned=0,
            )
        try:
            entries = sorted(normalized.iterdir(), key=lambda item: item.name)[:max_entries]
        except OSError as exc:
            return self._evidence(
                "list_allowed_directory",
                normalized,
                str(normalized),
                False,
                "FAIL_CLOSED",
                str(exc),
                entries_returned=0,
            )
        rendered = [
            {
                "name": entry.name,
                "path_type": "symlink" if entry.is_symlink() else "directory" if entry.is_dir() else "file" if entry.is_file() else "other",
            }
            for entry in entries
        ]
        return self._evidence(
            "list_allowed_directory",
            normalized,
            str(normalized),
            True,
            "DIRECTORY_LISTED",
            "non-recursive directory listing completed",
            entries_returned=len(rendered),
            entries=rendered,
        )

    def _evidence(
        self,
        operation: str,
        requested_path: str | Path,
        normalized_path: str,
        allowed: bool,
        status: str,
        reason: str,
        **extra: Any,
    ) -> dict[str, Any]:
        evidence = {
            "operation": operation,
            "requested_path": str(requested_path),
            "normalized_path": normalized_path,
            "allowed": allowed,
            "status": status,
            "reason": reason,
            "bytes_read": extra.pop("bytes_read", 0),
            "entries_returned": extra.pop("entries_returned", 0),
        }
        evidence.update(extra)
        evidence["evidence_hash"] = replay_hash(evidence)
        return evidence
