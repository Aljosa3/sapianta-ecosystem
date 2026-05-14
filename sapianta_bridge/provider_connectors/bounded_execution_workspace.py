"""Bounded workspace validation for Codex execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .execution_gate_validator import validate_workspace_boundary


def validate_bounded_execution_workspace(*, workspace_path: str, task_artifact_path: str) -> dict[str, Any]:
    validation = validate_workspace_boundary(workspace_path=workspace_path, artifact_path=task_artifact_path)
    errors = list(validation["errors"])
    workspace = Path(workspace_path) if isinstance(workspace_path, str) else Path("")
    if isinstance(workspace_path, str) and workspace_path.strip():
        if not workspace.is_absolute():
            errors.append({"field": "workspace_path", "reason": "workspace path must be absolute"})
    return {
        "valid": not errors,
        "errors": errors,
        "workspace_path": workspace_path,
        "task_artifact_path": task_artifact_path,
        "workspace_bounded": not errors,
        "filesystem_escape_detected": bool(errors),
    }
