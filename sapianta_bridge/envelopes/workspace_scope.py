"""Deterministic workspace scope boundaries."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


def normalize_workspace_path(path: str) -> str:
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _path_is_safe(path: str) -> bool:
    normalized = normalize_workspace_path(path)
    parts = PurePosixPath(normalized).parts
    return bool(normalized) and not normalized.startswith("/") and ".." not in parts


def validate_workspace_scope(scope: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(scope, dict):
        return {
            "valid": False,
            "errors": [{"field": "workspace_scope", "reason": "workspace scope must be an object"}],
        }
    allowed = scope.get("allowed_roots")
    forbidden = scope.get("forbidden_roots", [])
    generated = scope.get("generated_artifact_roots", [])
    if not isinstance(allowed, list) or not allowed:
        errors.append({"field": "workspace_scope.allowed_roots", "reason": "allowed roots must be non-empty"})
    for field, paths in (
        ("allowed_roots", allowed or []),
        ("forbidden_roots", forbidden),
        ("generated_artifact_roots", generated),
    ):
        if not isinstance(paths, list):
            errors.append({"field": f"workspace_scope.{field}", "reason": "workspace paths must be a list"})
            continue
        for path in paths:
            if not isinstance(path, str) or not _path_is_safe(path):
                errors.append({"field": f"workspace_scope.{field}", "reason": f"unsafe path: {path}"})
    allowed_normalized = {normalize_workspace_path(path) for path in allowed or [] if isinstance(path, str)}
    forbidden_normalized = {normalize_workspace_path(path) for path in forbidden if isinstance(path, str)}
    if allowed_normalized & forbidden_normalized:
        errors.append({"field": "workspace_scope", "reason": "path cannot be both allowed and forbidden"})
    return {
        "valid": not errors,
        "errors": errors,
        "workspace_escape_allowed": False,
        "self_expansion_allowed": False,
    }


def workspace_scope(
    allowed_roots: list[str],
    *,
    forbidden_roots: list[str] | None = None,
    generated_artifact_roots: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "allowed_roots": [normalize_workspace_path(path) for path in allowed_roots],
        "forbidden_roots": [normalize_workspace_path(path) for path in forbidden_roots or []],
        "generated_artifact_roots": [
            normalize_workspace_path(path) for path in generated_artifact_roots or []
        ],
    }
