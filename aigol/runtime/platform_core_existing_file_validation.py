"""Validation helpers for governed existing-file mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_mutation_candidate import validate_existing_file_target_path
from aigol.runtime.platform_core_mutation_validation import (
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
)
from aigol.runtime.transport.serialization import replay_hash


EXISTING_FILE_VALIDATION_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_PRE_MUTATION_ARTIFACT_V1 = "EXISTING_FILE_PRE_MUTATION_ARTIFACT_V1"
EXISTING_FILE_VALIDATION_ARTIFACT_V1 = "EXISTING_FILE_VALIDATION_ARTIFACT_V1"


def resolve_existing_file_target(*, workspace_path: Path, target_path: str) -> Path:
    relative_path = Path(validate_existing_file_target_path(target_path))
    target = (workspace_path / relative_path).resolve()
    try:
        target.relative_to(workspace_path.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("existing-file mutation failed closed: target escaped workspace") from exc
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("existing-file mutation failed closed: target must be existing regular file")
    return target


def pre_existing_file_mutation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    target: Path,
    created_at: str,
) -> dict[str, Any]:
    content = _read_plaintext(target)
    content_hash = replay_hash(content)
    artifact = {
        "artifact_type": EXISTING_FILE_PRE_MUTATION_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "workspace_path": str(workspace_path),
        "target_path": str(target),
        "target_relative_path": candidate["target_path"],
        "target_exists_before": True,
        "target_regular_file_before": True,
        "target_plaintext_utf8_before": True,
        "target_content_hash_before": content_hash,
        "expected_content_hash": candidate["expected_content_hash"],
        "hash_matches_candidate": content_hash == candidate["expected_content_hash"],
        "workspace_allowlisted": True,
        "single_file_scope": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def post_existing_file_mutation_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    pre_mutation: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if pre_mutation["hash_matches_candidate"] is not True:
        raise FailClosedRuntimeError("existing-file mutation validation failed closed: pre-hash mismatch")
    content = _read_plaintext(target)
    content_hash = replay_hash(content)
    if content_hash != candidate["replacement_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation validation failed closed: post-hash mismatch")
    if worker_result.get("old_content_hash") != candidate["expected_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation validation failed closed: Worker old hash mismatch")
    if worker_result.get("new_content_hash") != candidate["replacement_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation validation failed closed: Worker new hash mismatch")
    artifact = {
        "artifact_type": EXISTING_FILE_VALIDATION_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_relative_path": candidate["target_path"],
        "target_exists_after": True,
        "target_regular_file_after": True,
        "target_plaintext_utf8_after": True,
        "old_content_hash": candidate["expected_content_hash"],
        "new_content_hash": content_hash,
        "expected_new_content_hash": candidate["replacement_content_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "mutated_file_count": 1,
        "extra_mutation_detected": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
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
        raise FailClosedRuntimeError("existing-file mutation failed closed: target must be UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("existing-file mutation failed closed: target must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("existing-file mutation failed closed: target content too large")
    return content


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"existing-file mutation requires {field}")
    return value


__all__ = [
    "post_existing_file_mutation_validation_artifact",
    "pre_existing_file_mutation_artifact",
    "resolve_allowlisted_workspace",
    "resolve_existing_file_target",
    "resolve_existing_repository_dir",
]
