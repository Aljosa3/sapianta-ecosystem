"""Platform Core result helpers for governed Git commits."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


GIT_COMMIT_RESULT_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GIT_COMMIT_PRE_EXECUTION_ARTIFACT_V1 = "GIT_COMMIT_PRE_EXECUTION_ARTIFACT_V1"
GIT_COMMIT_RESULT_ARTIFACT_V1 = "GIT_COMMIT_RESULT_ARTIFACT_V1"
GIT_COMMIT_ROLLBACK_METADATA_ARTIFACT_V1 = "GIT_COMMIT_ROLLBACK_METADATA_ARTIFACT_V1"


def git_commit_pre_execution_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    repository_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GIT_COMMIT_PRE_EXECUTION_ARTIFACT_V1,
        "runtime_version": GIT_COMMIT_RESULT_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "repository_root": str(Path(repository_root).resolve()),
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "expected_head": candidate["expected_head"],
        "file_set_hash": candidate["file_set_hash"],
        "commit_message_hash": candidate["commit_message_hash"],
        "validation_artifact_hash": candidate["validation_artifact_hash"],
        "push_allowed": False,
        "remote_interaction_allowed": False,
        "branch_management_allowed": False,
        "merge_allowed": False,
        "rebase_allowed": False,
        "checkout_allowed": False,
        "reset_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def git_commit_result_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if worker_result.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit result candidate mismatch")
    if worker_result.get("file_set_hash") != candidate["file_set_hash"]:
        raise FailClosedRuntimeError("governed Git commit result file set mismatch")
    if worker_result.get("parent_head") != candidate["expected_head"]:
        raise FailClosedRuntimeError("governed Git commit result parent mismatch")
    artifact = {
        "artifact_type": GIT_COMMIT_RESULT_ARTIFACT_V1,
        "runtime_version": GIT_COMMIT_RESULT_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "parent_head": worker_result["parent_head"],
        "commit_hash": worker_result["commit_hash"],
        "post_commit_head": worker_result["post_commit_head"],
        "file_set_hash": worker_result["file_set_hash"],
        "staged_paths_hash": worker_result["staged_paths_hash"],
        "commit_message_hash": worker_result["commit_message_hash"],
        "author_hash": worker_result["author_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "git_performed": True,
        "commit_created": True,
        "commit_count": 1,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def git_commit_rollback_metadata_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    commit_result: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GIT_COMMIT_ROLLBACK_METADATA_ARTIFACT_V1,
        "runtime_version": GIT_COMMIT_RESULT_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "pre_commit_head": commit_result["parent_head"],
        "created_commit_hash": commit_result["commit_hash"],
        "authorized_file_set": deepcopy(candidate["file_set"]),
        "file_set_hash": candidate["file_set_hash"],
        "recommended_rollback_action": "manual governed review before any revert or reset",
        "rollback_execution_performed": False,
        "git_reset_performed": False,
        "git_revert_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "rollback_metadata_present": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git commit requires {field}")
    return value
