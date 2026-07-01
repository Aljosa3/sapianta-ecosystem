"""OCS-owned candidate helpers for governed local Git commits."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.git_commit_worker import (
    AUTHORIZED_GIT_COMMIT_SCOPE,
    GIT_COMMIT_WORKER_ID,
    OPERATION_CREATE_LOCAL_GIT_COMMIT,
)


GIT_COMMIT_CANDIDATE_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GIT_COMMIT_CANDIDATE_ARTIFACT_V1 = "GIT_COMMIT_CANDIDATE_ARTIFACT_V1"
CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT = "CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT"
ADD_TEXT_FILE = "ADD_TEXT_FILE"
REPLACE_TEXT_FILE = "REPLACE_TEXT_FILE"
ALLOWED_CHANGE_TYPES = frozenset({ADD_TEXT_FILE, REPLACE_TEXT_FILE})
MAX_COMMIT_MESSAGE_BYTES = 4096


def create_governed_git_commit_candidate(
    *,
    candidate_id: str,
    session_id: str,
    repository_id: str,
    branch_name: str,
    expected_head: str,
    file_set: list[dict[str, Any]],
    commit_message: dict[str, Any],
    author: dict[str, Any],
    validation_artifact: dict[str, Any],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create an OCS commit candidate for one local Git commit."""

    files = _validate_file_set(file_set)
    message = _validate_commit_message(commit_message)
    author_metadata = _validate_identity(author, "author")
    validation = _validate_validation_artifact(validation_artifact)
    artifact = {
        "artifact_type": GIT_COMMIT_CANDIDATE_ARTIFACT_V1,
        "runtime_version": GIT_COMMIT_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT,
        "repository_id": _require_string(repository_id, "repository_id"),
        "branch_name": _require_string(branch_name, "branch_name"),
        "expected_head": _require_string(expected_head, "expected_head"),
        "staged_content_model": "EXPLICIT_FILE_SET_STAGED_BY_COMMIT_WORKER",
        "file_set": files,
        "file_set_hash": replay_hash(files),
        "file_count": len(files),
        "commit_message": message,
        "commit_message_hash": replay_hash(message),
        "author": author_metadata,
        "author_hash": replay_hash(author_metadata),
        "committer_policy": "USE_AUTHORIZED_AUTHOR_METADATA",
        "validation_artifact_hash": validation["artifact_hash"],
        "validation_status": validation["validation_status"],
        "validation_passed": validation["validation_status"] == "VALIDATION_PASSED",
        "worker_id": GIT_COMMIT_WORKER_ID,
        "worker_scope": AUTHORIZED_GIT_COMMIT_SCOPE,
        "worker_operation": OPERATION_CREATE_LOCAL_GIT_COMMIT,
        "commit_count": 1,
        "local_commit_only": True,
        "push_allowed": False,
        "remote_interaction_allowed": False,
        "branch_management_allowed": False,
        "merge_allowed": False,
        "rebase_allowed": False,
        "checkout_allowed": False,
        "reset_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "arbitrary_shell_allowed": False,
        "human_approval_required": True,
        "governance_authorization_required": True,
        "validation_required": True,
        "replay_required": True,
        "rollback_metadata_required": True,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_git_commit_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate an OCS commit candidate without executing Git."""

    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != GIT_COMMIT_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed Git commit failed closed: candidate artifact required")
    if artifact.get("operation") != CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT:
        raise FailClosedRuntimeError("governed Git commit failed closed: operation not authorized")
    if artifact.get("worker_id") != GIT_COMMIT_WORKER_ID:
        raise FailClosedRuntimeError("governed Git commit failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_GIT_COMMIT_SCOPE:
        raise FailClosedRuntimeError("governed Git commit failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_CREATE_LOCAL_GIT_COMMIT:
        raise FailClosedRuntimeError("governed Git commit failed closed: Worker operation mismatch")
    if artifact.get("commit_count") != 1:
        raise FailClosedRuntimeError("governed Git commit failed closed: exactly one commit required")
    files = _validate_file_set(artifact.get("file_set"))
    if artifact.get("file_set_hash") != replay_hash(files):
        raise FailClosedRuntimeError("governed Git commit failed closed: file set hash mismatch")
    if artifact.get("file_count") != len(files):
        raise FailClosedRuntimeError("governed Git commit failed closed: file count mismatch")
    message = _validate_commit_message(artifact.get("commit_message"))
    if artifact.get("commit_message_hash") != replay_hash(message):
        raise FailClosedRuntimeError("governed Git commit failed closed: commit message hash mismatch")
    author = _validate_identity(artifact.get("author"), "author")
    if artifact.get("author_hash") != replay_hash(author):
        raise FailClosedRuntimeError("governed Git commit failed closed: author hash mismatch")
    if artifact.get("validation_passed") is not True or artifact.get("validation_status") != "VALIDATION_PASSED":
        raise FailClosedRuntimeError("governed Git commit failed closed: successful validation required")
    for flag in (
        "push_allowed",
        "remote_interaction_allowed",
        "branch_management_allowed",
        "merge_allowed",
        "rebase_allowed",
        "checkout_allowed",
        "reset_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "arbitrary_shell_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"governed Git commit failed closed: {flag} must be false")
    return artifact


def _validate_file_set(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("governed Git commit requires a non-empty file set")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("governed Git commit file entry must be a JSON object")
        path = _validate_relative_path(item.get("path"))
        if path in seen:
            raise FailClosedRuntimeError("governed Git commit file set contains duplicate path")
        change_type = _require_string(item.get("change_type"), "change_type")
        if change_type not in ALLOWED_CHANGE_TYPES:
            raise FailClosedRuntimeError("governed Git commit failed closed: change type not authorized")
        normalized.append(
            {
                "path": path,
                "change_type": change_type,
                "content_hash": _require_string(item.get("content_hash"), "content_hash"),
            }
        )
        seen.add(path)
    return normalized


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("governed Git commit path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("governed Git commit path must not contain traversal")
    return path.as_posix()


def _validate_commit_message(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("governed Git commit message must be a JSON object")
    subject = _require_string(value.get("subject"), "subject").strip()
    body = value.get("body", "")
    if body is None:
        body = ""
    if not isinstance(body, str):
        raise FailClosedRuntimeError("governed Git commit body must be a string")
    if "\x00" in subject or "\x00" in body:
        raise FailClosedRuntimeError("governed Git commit message must be plaintext")
    encoded = (subject + "\n\n" + body).encode("utf-8")
    if len(encoded) > MAX_COMMIT_MESSAGE_BYTES:
        raise FailClosedRuntimeError("governed Git commit message too large")
    return {"subject": subject, "body": body}


def _validate_identity(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"governed Git commit {label} must be a JSON object")
    name = _require_string(value.get("name"), f"{label}.name")
    email = _require_string(value.get("email"), f"{label}.email")
    if "\n" in name or "\n" in email or "\x00" in name or "\x00" in email:
        raise FailClosedRuntimeError(f"governed Git commit {label} metadata invalid")
    return {"name": name, "email": email}


def _validate_validation_artifact(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("governed Git commit requires validation artifact")
    artifact = deepcopy(value)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != VALIDATION_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed Git commit requires validation result artifact")
    if artifact.get("validation_status") != "VALIDATION_PASSED":
        raise FailClosedRuntimeError("governed Git commit requires successful governed validation")
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed Git commit artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed Git commit artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git commit requires {field}")
    return value
