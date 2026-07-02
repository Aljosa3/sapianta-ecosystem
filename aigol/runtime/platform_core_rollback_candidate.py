"""OCS-owned rollback candidate helpers."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_replay import load_existing_file_mutation_replay
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.platform_core_patch_mutation_replay import load_patch_mutation_replay
from aigol.runtime.platform_core_replay_mutation_evidence import load_first_mutating_worker_replay
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_rollback_worker import (
    AUTHORIZED_ROLLBACK_SCOPE,
    FILESYSTEM_ROLLBACK_WORKER_ID,
    OPERATION_EXECUTE_ROLLBACK,
    ROLLBACK_DELETE_CREATED_FILE,
    ROLLBACK_RESTORE_ORIGINAL_CONTENT,
)


ROLLBACK_CANDIDATE_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
ROLLBACK_CANDIDATE_ARTIFACT_V1 = "ROLLBACK_CANDIDATE_ARTIFACT_V1"
EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK = "EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK"

PRIOR_FIRST_MUTATING_WORKER = "first_mutating_worker"
PRIOR_EXISTING_FILE_MUTATION = "existing_file_mutation"
PRIOR_PATCH_MUTATION = "single_file_patch_mutation"
SUPPORTED_PRIOR_MUTATION_TYPES = {
    PRIOR_FIRST_MUTATING_WORKER,
    PRIOR_EXISTING_FILE_MUTATION,
    PRIOR_PATCH_MUTATION,
}


def create_governed_rollback_candidate_from_replay(
    *,
    candidate_id: str,
    session_id: str,
    prior_mutation_type: str,
    prior_replay_dir: str | Path,
    target_path: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    """Create a deterministic OCS rollback candidate from prior Replay evidence."""

    mutation_type = _validate_prior_type(prior_mutation_type)
    if mutation_type == PRIOR_FIRST_MUTATING_WORKER:
        source = _first_mutation_source(prior_replay_dir, target_path)
    elif mutation_type == PRIOR_PATCH_MUTATION:
        source = _patch_mutation_source(prior_replay_dir, target_path)
    else:
        source = _existing_file_source(prior_replay_dir, target_path)
    artifact = {
        "artifact_type": ROLLBACK_CANDIDATE_ARTIFACT_V1,
        "runtime_version": ROLLBACK_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK,
        "worker_id": FILESYSTEM_ROLLBACK_WORKER_ID,
        "worker_scope": AUTHORIZED_ROLLBACK_SCOPE,
        "worker_operation": OPERATION_EXECUTE_ROLLBACK,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "prior_mutation_type": mutation_type,
        "prior_execution_id": source["prior_execution_id"],
        "prior_replay_reference": str(Path(prior_replay_dir)),
        "prior_replay_hash": source["prior_replay_hash"],
        "rollback_metadata_hash": source["rollback_metadata_hash"],
        "target_path": _validate_relative_path(target_path),
        "rollback_action": source["rollback_action"],
        "authorized_current_hash": source["authorized_current_hash"],
        "expected_rollback_result_hash": source["expected_rollback_result_hash"],
        "canonical_restore_artifact_hash": source["canonical_restore_artifact_hash"],
        "restore_content": source["restore_content"],
        "restore_content_hash": source["restore_content_hash"],
        "file_count": 1,
        "target_count": 1,
        "single_prior_mutation": True,
        "replay_reconstructed": True,
        "rollback_metadata_present": True,
        "governance_authorization_required": True,
        "human_approval_required": True,
        "worker_execution_only": True,
        "multi_target_rollback_allowed": False,
        "rollback_orchestration_allowed": False,
        "automatic_rollback_allowed": False,
        "git_allowed": False,
        "branch_manipulation_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "dependency_rollback_allowed": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_rollback_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ROLLBACK_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed rollback failed closed: candidate artifact required")
    if artifact.get("operation") != EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK:
        raise FailClosedRuntimeError("governed rollback failed closed: operation mismatch")
    if artifact.get("worker_id") != FILESYSTEM_ROLLBACK_WORKER_ID:
        raise FailClosedRuntimeError("governed rollback failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_ROLLBACK_SCOPE:
        raise FailClosedRuntimeError("governed rollback failed closed: Worker scope mismatch")
    _validate_prior_type(artifact.get("prior_mutation_type"))
    _validate_relative_path(artifact.get("target_path"))
    if artifact.get("rollback_action") not in {
        ROLLBACK_DELETE_CREATED_FILE,
        ROLLBACK_RESTORE_ORIGINAL_CONTENT,
    }:
        raise FailClosedRuntimeError("governed rollback failed closed: rollback action invalid")
    _require_string(artifact.get("authorized_current_hash"), "authorized_current_hash")
    _require_string(artifact.get("expected_rollback_result_hash"), "expected_rollback_result_hash")
    _require_string(artifact.get("canonical_restore_artifact_hash"), "canonical_restore_artifact_hash")
    if artifact["rollback_action"] == ROLLBACK_RESTORE_ORIGINAL_CONTENT:
        restore = _validate_optional_content(artifact.get("restore_content"), required=True)
        if artifact.get("restore_content_hash") != replay_hash(restore):
            raise FailClosedRuntimeError("governed rollback failed closed: restore content hash mismatch")
        if artifact.get("expected_rollback_result_hash") != replay_hash(restore):
            raise FailClosedRuntimeError("governed rollback failed closed: restore result hash mismatch")
    else:
        if artifact.get("restore_content") is not None or artifact.get("restore_content_hash") is not None:
            raise FailClosedRuntimeError("governed rollback failed closed: delete rollback must not contain content")
    for flag in (
        "multi_target_rollback_allowed",
        "rollback_orchestration_allowed",
        "automatic_rollback_allowed",
        "git_allowed",
        "branch_manipulation_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "dependency_rollback_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"governed rollback failed closed: {flag} must be false")
    return artifact


def _first_mutation_source(prior_replay_dir: str | Path, target_path: str) -> dict[str, Any]:
    wrappers = load_first_mutating_worker_replay(prior_replay_dir)
    replay_summary = _first_summary(wrappers)
    candidate = wrappers[0]["artifact"]
    rollback = wrappers[7]["artifact"]
    completion = wrappers[8]["artifact"]
    if candidate["target_filename"] != target_path:
        raise FailClosedRuntimeError("governed rollback failed closed: target mismatch")
    if rollback["rollback_operation"] != ROLLBACK_DELETE_CREATED_FILE:
        raise FailClosedRuntimeError("governed rollback failed closed: unsupported rollback action")
    return {
        "prior_execution_id": completion["execution_id"],
        "prior_replay_hash": replay_summary,
        "rollback_metadata_hash": rollback["artifact_hash"],
        "rollback_action": ROLLBACK_DELETE_CREATED_FILE,
        "authorized_current_hash": rollback["content_hash"],
        "expected_rollback_result_hash": replay_hash({"target_absent": target_path}),
        "canonical_restore_artifact_hash": replay_hash({"target_absent": target_path}),
        "restore_content": None,
        "restore_content_hash": None,
    }


def _patch_mutation_source(prior_replay_dir: str | Path, target_path: str) -> dict[str, Any]:
    wrappers = load_patch_mutation_replay(prior_replay_dir)
    candidate = wrappers[0]["artifact"]
    rollback = wrappers[7]["artifact"]
    completion = wrappers[8]["artifact"]
    if candidate["target_path"] != target_path:
        raise FailClosedRuntimeError("governed rollback failed closed: target mismatch")
    if rollback["rollback_operation"] != ROLLBACK_RESTORE_ORIGINAL_CONTENT:
        raise FailClosedRuntimeError("governed rollback failed closed: unsupported rollback action")
    restore_content = _restore_content_from_patch_candidate(candidate)
    return {
        "prior_execution_id": completion["execution_id"],
        "prior_replay_hash": replay_hash(wrappers),
        "rollback_metadata_hash": rollback["artifact_hash"],
        "rollback_action": ROLLBACK_RESTORE_ORIGINAL_CONTENT,
        "authorized_current_hash": rollback["authorized_post_mutation_hash"],
        "expected_rollback_result_hash": rollback["original_content_hash"],
        "canonical_restore_artifact_hash": replay_hash(restore_content),
        "restore_content": restore_content,
        "restore_content_hash": replay_hash(restore_content),
    }


def _existing_file_source(prior_replay_dir: str | Path, target_path: str) -> dict[str, Any]:
    wrappers = load_existing_file_mutation_replay(prior_replay_dir)
    candidate = wrappers[0]["artifact"]
    if candidate["target_path"] != target_path:
        raise FailClosedRuntimeError("governed rollback failed closed: target mismatch")
    raise FailClosedRuntimeError(
        "governed rollback failed closed: existing-file rollback requires complete original content evidence"
    )


def _restore_content_from_patch_candidate(candidate: dict[str, Any]) -> str:
    resulting = _validate_optional_content(candidate.get("expected_resulting_content"), required=True)
    old_text = _validate_optional_content(candidate.get("old_text"), required=True)
    new_text = _validate_optional_content(candidate.get("new_text"), required=True)
    occurrences = resulting.count(new_text)
    if occurrences != 1:
        raise FailClosedRuntimeError("governed rollback failed closed: inverse patch context ambiguous")
    restored = resulting.replace(new_text, old_text, 1)
    if replay_hash(restored) != candidate["pre_content_hash"]:
        raise FailClosedRuntimeError("governed rollback failed closed: reconstructed restore hash mismatch")
    return restored


def _first_summary(wrappers: list[dict[str, Any]]) -> str:
    return replay_hash(wrappers)


def _validate_prior_type(value: Any) -> str:
    text = _require_string(value, "prior_mutation_type")
    if text not in SUPPORTED_PRIOR_MUTATION_TYPES:
        raise FailClosedRuntimeError("governed rollback failed closed: prior mutation type unsupported")
    return text


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("governed rollback failed closed: target path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("governed rollback failed closed: target path must not contain traversal")
    return path.as_posix()


def _validate_optional_content(value: Any, *, required: bool) -> str:
    if value is None and not required:
        return ""
    content = _require_string(value, "restore_content")
    if "\x00" in content:
        raise FailClosedRuntimeError("governed rollback failed closed: restore content must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("governed rollback failed closed: restore content too large")
    return content


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed rollback artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed rollback requires {field}")
    return value
