"""OCS-owned candidate helpers for governed existing-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_replace_worker import (
    AUTHORIZED_REPLACE_SCOPE,
    FILESYSTEM_REPLACE_WORKER_ID,
    OPERATION_REPLACE_EXISTING_TEXT_FILE,
)


EXISTING_FILE_MUTATION_CANDIDATE_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1 = "EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1"
REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE = (
    "REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE"
)
MAX_CONTENT_BYTES = 64 * 1024


def create_existing_file_mutation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    target_path: str,
    expected_content_hash: str,
    replacement_content: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    """Create the OCS candidate for replacing one existing plaintext file."""

    relative_path = validate_existing_file_target_path(target_path)
    content = validate_plaintext_replacement_content(replacement_content)
    artifact = {
        "artifact_type": EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE,
        "worker_id": FILESYSTEM_REPLACE_WORKER_ID,
        "worker_scope": AUTHORIZED_REPLACE_SCOPE,
        "worker_operation": OPERATION_REPLACE_EXISTING_TEXT_FILE,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "target_path": relative_path,
        "expected_content_hash": _require_string(expected_content_hash, "expected_content_hash"),
        "replacement_content": content,
        "replacement_content_hash": replay_hash(content),
        "file_count": 1,
        "plaintext_utf8_only": True,
        "existing_file_required": True,
        "full_file_replacement_only": True,
        "new_file_creation_allowed": False,
        "multi_file_mutation_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "additional_worker_dispatch_allowed": False,
        "human_approval_required": True,
        "governance_authorization_required": True,
        "rollback_required": True,
        "validation_required": True,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_existing_file_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate an OCS existing-file mutation candidate without executing it."""

    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("existing-file mutation failed closed: candidate artifact required")
    if artifact.get("operation") != REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: operation not authorized")
    if artifact.get("worker_id") != FILESYSTEM_REPLACE_WORKER_ID:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_REPLACE_SCOPE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_REPLACE_EXISTING_TEXT_FILE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker operation mismatch")
    if artifact.get("file_count") != 1:
        raise FailClosedRuntimeError("existing-file mutation failed closed: exactly one file required")
    if artifact.get("existing_file_required") is not True or artifact.get("full_file_replacement_only") is not True:
        raise FailClosedRuntimeError("existing-file mutation failed closed: full replacement of existing file required")
    for flag in (
        "new_file_creation_allowed",
        "multi_file_mutation_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "additional_worker_dispatch_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"existing-file mutation failed closed: {flag} must be false")
    validate_existing_file_target_path(artifact.get("target_path"))
    content = validate_plaintext_replacement_content(artifact.get("replacement_content"))
    if artifact.get("replacement_content_hash") != replay_hash(content):
        raise FailClosedRuntimeError("existing-file mutation failed closed: replacement content hash mismatch")
    _require_string(artifact.get("expected_content_hash"), "expected_content_hash")
    return artifact


def validate_existing_file_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("existing-file mutation failed closed: target path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("existing-file mutation failed closed: target path must not contain traversal")
    return path.as_posix()


def validate_plaintext_replacement_content(value: Any) -> str:
    content = _require_string(value, "replacement_content")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("existing-file mutation failed closed: replacement content too large")
    if "\x00" in content:
        raise FailClosedRuntimeError("existing-file mutation failed closed: binary content not allowed")
    return content


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("existing-file mutation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("existing-file mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"existing-file mutation requires {field}")
    return value
