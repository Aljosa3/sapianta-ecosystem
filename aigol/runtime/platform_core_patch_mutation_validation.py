"""Validation helpers for governed single-file patch mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_mutation_validation import (
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
)
from aigol.runtime.platform_core_patch_mutation_candidate import validate_patch_target_path
from aigol.runtime.transport.serialization import replay_hash


PATCH_MUTATION_VALIDATION_VERSION = "G9_04_SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTATION_V1"
PATCH_MUTATION_PRE_ARTIFACT_V1 = "PATCH_MUTATION_PRE_ARTIFACT_V1"
PATCH_MUTATION_VALIDATION_ARTIFACT_V1 = "PATCH_MUTATION_VALIDATION_ARTIFACT_V1"


def resolve_patch_target(*, workspace_path: Path, target_path: str) -> Path:
    relative_path = Path(validate_patch_target_path(target_path))
    target = (workspace_path / relative_path).resolve()
    try:
        target.relative_to(workspace_path.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("patch mutation failed closed: target escaped workspace") from exc
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("patch mutation failed closed: target must be existing regular file")
    return target


def pre_patch_mutation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    target: Path,
    created_at: str,
) -> dict[str, Any]:
    content = _read_plaintext(target)
    content_hash = replay_hash(content)
    old_occurrences = content.count(candidate["old_text"])
    artifact = {
        "artifact_type": PATCH_MUTATION_PRE_ARTIFACT_V1,
        "runtime_version": PATCH_MUTATION_VALIDATION_VERSION,
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
        "expected_pre_content_hash": candidate["pre_content_hash"],
        "hash_matches_candidate": content_hash == candidate["pre_content_hash"],
        "old_text_occurrence_count": old_occurrences,
        "old_text_occurs_exactly_once": old_occurrences == 1,
        "workspace_allowlisted": True,
        "single_file_scope": True,
        "patch_count": 1,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def post_patch_mutation_validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    pre_mutation: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
    validation_result_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if pre_mutation["hash_matches_candidate"] is not True:
        raise FailClosedRuntimeError("patch mutation validation failed closed: pre-hash mismatch")
    if pre_mutation["old_text_occurs_exactly_once"] is not True:
        raise FailClosedRuntimeError("patch mutation validation failed closed: old text conflict")
    content = _read_plaintext(target)
    content_hash = replay_hash(content)
    if content_hash != candidate["expected_post_content_hash"]:
        raise FailClosedRuntimeError("patch mutation validation failed closed: post-hash mismatch")
    if content != candidate["expected_resulting_content"]:
        raise FailClosedRuntimeError("patch mutation validation failed closed: complete artifact mismatch")
    if worker_result.get("pre_content_hash") != candidate["pre_content_hash"]:
        raise FailClosedRuntimeError("patch mutation validation failed closed: Worker pre hash mismatch")
    if worker_result.get("post_content_hash") != candidate["expected_post_content_hash"]:
        raise FailClosedRuntimeError("patch mutation validation failed closed: Worker post hash mismatch")
    validation_state = candidate["validation_state"]
    if validation_state == "validation_required_before_completion" and validation_result_artifact is None:
        raise FailClosedRuntimeError("patch mutation validation failed closed: validation evidence required")
    artifact = {
        "artifact_type": PATCH_MUTATION_VALIDATION_ARTIFACT_V1,
        "runtime_version": PATCH_MUTATION_VALIDATION_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_relative_path": candidate["target_path"],
        "target_exists_after": True,
        "target_regular_file_after": True,
        "target_plaintext_utf8_after": True,
        "pre_content_hash": candidate["pre_content_hash"],
        "post_content_hash": content_hash,
        "expected_post_content_hash": candidate["expected_post_content_hash"],
        "complete_resulting_content": content,
        "complete_resulting_content_hash": replay_hash(content),
        "complete_resulting_file_is_canonical_artifact": True,
        "patch_is_intent_only": True,
        "worker_replay_hash": worker_replay["replay_hash"],
        "validation_interaction_state": validation_state,
        "external_validation_evidence_present": validation_result_artifact is not None,
        "external_validation_artifact_hash": (
            validation_result_artifact.get("artifact_hash")
            if isinstance(validation_result_artifact, dict)
            else None
        ),
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
        raise FailClosedRuntimeError("patch mutation failed closed: target must be UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("patch mutation failed closed: target must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("patch mutation failed closed: target content too large")
    return content


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"patch mutation requires {field}")
    return value


__all__ = [
    "post_patch_mutation_validation_artifact",
    "pre_patch_mutation_artifact",
    "resolve_allowlisted_workspace",
    "resolve_existing_repository_dir",
    "resolve_patch_target",
]
