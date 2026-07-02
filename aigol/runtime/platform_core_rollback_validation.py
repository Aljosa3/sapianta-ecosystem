"""Validation helpers for governed rollback execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_mutation_validation import (
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
)
from aigol.runtime.platform_core_rollback_candidate import validate_governed_rollback_candidate
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_rollback_worker import (
    ROLLBACK_DELETE_CREATED_FILE,
    ROLLBACK_RESTORE_ORIGINAL_CONTENT,
)


ROLLBACK_VALIDATION_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
ROLLBACK_PRE_VALIDATION_ARTIFACT_V1 = "ROLLBACK_PRE_VALIDATION_ARTIFACT_V1"
ROLLBACK_POST_VALIDATION_ARTIFACT_V1 = "ROLLBACK_POST_VALIDATION_ARTIFACT_V1"


def resolve_rollback_target(*, workspace_path: Path, target_path: str) -> Path:
    relative_path = Path(_validate_relative_path(target_path))
    target = (workspace_path / relative_path).resolve()
    try:
        target.relative_to(workspace_path.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("governed rollback failed closed: target escaped workspace") from exc
    return target


def pre_rollback_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    target: Path,
    created_at: str,
) -> dict[str, Any]:
    """Record pre-rollback target state and conflict status."""

    validated = validate_governed_rollback_candidate(candidate)
    target_exists = target.exists()
    target_regular = target.is_file() and not target.is_symlink()
    current_hash = None
    if target_exists and target_regular:
        current_hash = replay_hash(_read_plaintext(target))
    hash_matches = current_hash == validated["authorized_current_hash"]
    artifact = {
        "artifact_type": ROLLBACK_PRE_VALIDATION_ARTIFACT_V1,
        "runtime_version": ROLLBACK_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": validated["candidate_id"],
        "candidate_hash": validated["artifact_hash"],
        "workspace_path": str(workspace_path),
        "target_path": str(target),
        "target_relative_path": validated["target_path"],
        "rollback_action": validated["rollback_action"],
        "target_exists_before": target_exists,
        "target_regular_file_before": target_regular,
        "target_content_hash_before": current_hash,
        "authorized_current_hash": validated["authorized_current_hash"],
        "current_hash_matches_authorized_state": hash_matches,
        "single_target_scope": True,
        "workspace_allowlisted": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def post_rollback_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    pre_validation: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Validate post-rollback target state."""

    validated = validate_governed_rollback_candidate(candidate)
    if pre_validation["current_hash_matches_authorized_state"] is not True:
        raise FailClosedRuntimeError("governed rollback validation failed closed: current hash conflict")
    if worker_result.get("rollback_executed") is not True:
        raise FailClosedRuntimeError("governed rollback validation failed closed: Worker did not execute")
    if worker_result.get("post_rollback_hash") != validated["expected_rollback_result_hash"]:
        raise FailClosedRuntimeError("governed rollback validation failed closed: Worker result hash mismatch")
    if validated["rollback_action"] == ROLLBACK_DELETE_CREATED_FILE:
        if target.exists():
            raise FailClosedRuntimeError("governed rollback validation failed closed: target still exists")
        target_exists_after = False
        post_hash = validated["expected_rollback_result_hash"]
    elif validated["rollback_action"] == ROLLBACK_RESTORE_ORIGINAL_CONTENT:
        if target.is_symlink() or not target.exists() or not target.is_file():
            raise FailClosedRuntimeError("governed rollback validation failed closed: restore target missing")
        content = _read_plaintext(target)
        post_hash = replay_hash(content)
        if post_hash != validated["expected_rollback_result_hash"]:
            raise FailClosedRuntimeError("governed rollback validation failed closed: restored hash mismatch")
        target_exists_after = True
    else:
        raise FailClosedRuntimeError("governed rollback validation failed closed: invalid rollback action")
    artifact = {
        "artifact_type": ROLLBACK_POST_VALIDATION_ARTIFACT_V1,
        "runtime_version": ROLLBACK_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": validated["candidate_id"],
        "candidate_hash": validated["artifact_hash"],
        "target_relative_path": validated["target_path"],
        "rollback_action": validated["rollback_action"],
        "pre_rollback_hash": pre_validation["target_content_hash_before"],
        "post_rollback_hash": post_hash,
        "expected_rollback_result_hash": validated["expected_rollback_result_hash"],
        "target_exists_after": target_exists_after,
        "worker_replay_hash": worker_replay["replay_hash"],
        "mutated_file_count": 1,
        "extra_mutation_detected": False,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "validation_status": "VALIDATED",
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _read_plaintext(target: Path) -> str:
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("governed rollback failed closed: target must be UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("governed rollback failed closed: target must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("governed rollback failed closed: target content too large")
    return content


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("governed rollback failed closed: target path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("governed rollback failed closed: target path must not contain traversal")
    return path.as_posix()


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed rollback requires {field}")
    return value


__all__ = [
    "post_rollback_validation_artifact",
    "pre_rollback_validation_artifact",
    "resolve_allowlisted_workspace",
    "resolve_existing_repository_dir",
    "resolve_rollback_target",
]
