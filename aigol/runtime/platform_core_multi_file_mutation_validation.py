"""Validation and rollback metadata helpers for governed multi-file mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_multi_file_mutation_candidate import (
    OP_CREATE,
    OP_PATCH,
    OP_REPLACE,
    validate_multi_file_mutation_candidate,
)
from aigol.runtime.platform_core_mutation_validation import (
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
)
from aigol.runtime.transport.serialization import replay_hash


MULTI_FILE_VALIDATION_VERSION = "G9_11_GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTATION_V1"
MULTI_FILE_PRE_VALIDATION_ARTIFACT_V1 = "MULTI_FILE_PRE_VALIDATION_ARTIFACT_V1"
MULTI_FILE_POST_VALIDATION_ARTIFACT_V1 = "MULTI_FILE_POST_VALIDATION_ARTIFACT_V1"
MULTI_FILE_ROLLBACK_METADATA_ARTIFACT_V1 = "MULTI_FILE_ROLLBACK_METADATA_ARTIFACT_V1"


def pre_multi_file_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    created_at: str,
) -> dict[str, Any]:
    validated = validate_multi_file_mutation_candidate(candidate)
    records = []
    for operation in validated["operations"]:
        target = resolve_multi_file_target(workspace_path=workspace_path, target_path=operation["target_path"])
        exists = target.exists()
        regular = target.is_file() and not target.is_symlink()
        current_content = _read_plaintext(target) if exists and regular else None
        current_hash = replay_hash(current_content) if current_content is not None else None
        if operation["operation_type"] == OP_CREATE:
            ready = exists is False
            conflict = "target_exists" if exists else None
        elif operation["operation_type"] == OP_REPLACE:
            ready = regular and current_hash == operation["pre_content_hash"]
            conflict = None if ready else "target_hash_conflict"
        else:
            old_text = operation["single_file_candidate"]["old_text"]
            old_occurrences = current_content.count(old_text) if current_content is not None else 0
            ready = regular and current_hash == operation["pre_content_hash"] and old_occurrences == 1
            conflict = None if ready else "target_hash_or_context_conflict"
        records.append(
            {
                "operation_id": operation["operation_id"],
                "operation_index": operation["operation_index"],
                "operation_type": operation["operation_type"],
                "target_path": operation["target_path"],
                "target_exists_before": exists,
                "target_regular_file_before": regular,
                "current_content_hash": current_hash,
                "expected_pre_content_hash": operation["pre_content_hash"],
                "ready_to_execute": ready,
                "conflict_reason": conflict,
            }
        )
    ready_all = all(record["ready_to_execute"] is True for record in records)
    artifact = {
        "artifact_type": MULTI_FILE_PRE_VALIDATION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": validated["candidate_id"],
        "candidate_hash": validated["artifact_hash"],
        "operation_count": validated["operation_count"],
        "workspace_path": str(workspace_path),
        "operation_validations": records,
        "all_operations_ready": ready_all,
        "single_transaction_scope": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def post_multi_file_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    execution_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    validated = validate_multi_file_mutation_candidate(candidate)
    records = []
    for operation in validated["operations"]:
        target = resolve_multi_file_target(workspace_path=workspace_path, target_path=operation["target_path"])
        if operation["operation_type"] == OP_CREATE:
            content = _read_plaintext(target) if target.exists() and target.is_file() and not target.is_symlink() else None
            post_hash = replay_hash(content) if content is not None else None
        else:
            content = _read_plaintext(target) if target.exists() and target.is_file() and not target.is_symlink() else None
            post_hash = replay_hash(content) if content is not None else None
        valid = post_hash == operation["expected_post_content_hash"]
        records.append(
            {
                "operation_id": operation["operation_id"],
                "operation_index": operation["operation_index"],
                "operation_type": operation["operation_type"],
                "target_path": operation["target_path"],
                "post_content_hash": post_hash,
                "expected_post_content_hash": operation["expected_post_content_hash"],
                "post_state_valid": valid,
            }
        )
    all_valid = all(record["post_state_valid"] is True for record in records)
    if execution_artifact.get("execution_status") != "PER_FILE_EXECUTION_COMPLETED":
        all_valid = False
    artifact = {
        "artifact_type": MULTI_FILE_POST_VALIDATION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": validated["candidate_id"],
        "candidate_hash": validated["artifact_hash"],
        "execution_hash": execution_artifact["artifact_hash"],
        "operation_count": validated["operation_count"],
        "operation_validations": records,
        "all_operations_valid": all_valid,
        "validation_status": "VALIDATED" if all_valid else "FAILED_CLOSED",
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_installation_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def multi_file_rollback_metadata_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    post_validation: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    validated = validate_multi_file_mutation_candidate(candidate)
    records = []
    for operation in validated["operations"]:
        if operation["operation_type"] == OP_CREATE:
            rollback_action = "DELETE_CREATED_FILE_IF_HASH_MATCHES"
            executable = True
        elif operation["operation_type"] == OP_PATCH:
            rollback_action = "RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH"
            executable = True
        else:
            rollback_action = "RESTORE_ORIGINAL_CONTENT_REQUIRES_COMPLETE_PRIOR_CONTENT_EVIDENCE"
            executable = False
        records.append(
            {
                "operation_id": operation["operation_id"],
                "operation_index": operation["operation_index"],
                "operation_type": operation["operation_type"],
                "target_path": operation["target_path"],
                "authorized_post_mutation_hash": operation["expected_post_content_hash"],
                "rollback_action": rollback_action,
                "rollback_execution_supported": executable,
                "rollback_metadata_state": operation["rollback_metadata_state"],
            }
        )
    artifact = {
        "artifact_type": MULTI_FILE_ROLLBACK_METADATA_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": validated["candidate_id"],
        "candidate_hash": validated["artifact_hash"],
        "post_validation_hash": post_validation["artifact_hash"],
        "operation_count": validated["operation_count"],
        "rollback_records": records,
        "rollback_metadata_present": True,
        "automatic_rollback_allowed": False,
        "human_approval_required_for_rollback_execution": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def resolve_multi_file_target(*, workspace_path: Path, target_path: str) -> Path:
    relative = Path(_validate_relative_path(target_path))
    target = (workspace_path / relative).resolve()
    try:
        target.relative_to(workspace_path.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("multi-file mutation failed closed: target escaped workspace") from exc
    return target


def _read_plaintext(target: Path) -> str:
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("multi-file mutation failed closed: target must be UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("multi-file mutation failed closed: target must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("multi-file mutation failed closed: target content too large")
    return content


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("multi-file mutation failed closed: path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("multi-file mutation failed closed: path must not contain traversal")
    return path.as_posix()


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multi-file mutation requires {field}")
    return value


__all__ = [
    "multi_file_rollback_metadata_artifact",
    "post_multi_file_validation_artifact",
    "pre_multi_file_validation_artifact",
    "resolve_allowlisted_workspace",
    "resolve_existing_repository_dir",
    "resolve_multi_file_target",
]
