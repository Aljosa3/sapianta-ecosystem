"""OCS-owned mutation candidate artifact helpers for the first governed mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE as FILESYSTEM_CREATE_FILE_SCOPE,
    FILESYSTEM_WORKER_ID,
    OPERATION_CREATE_FILE,
)


MUTATION_CANDIDATE_SERVICE_VERSION = "G8_09B_PLATFORM_CORE_MUTATION_RUNTIME_REFACTORING_V1"
FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1"
CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE = "CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE"
DEFAULT_ALLOWLISTED_WORKSPACE = "runtime/governed_mutation_workspace"
MAX_CONTENT_BYTES = 64 * 1024


def create_first_mutating_worker_candidate(
    *,
    candidate_id: str,
    session_id: str,
    target_filename: str,
    content: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    """Create the OCS candidate for the first governed create-only mutation."""

    filename = validate_mutation_target_filename(target_filename)
    normalized_content = validate_plaintext_mutation_content(content)
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1,
        "runtime_version": MUTATION_CANDIDATE_SERVICE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE,
        "worker_id": FILESYSTEM_WORKER_ID,
        "worker_scope": FILESYSTEM_CREATE_FILE_SCOPE,
        "worker_operation": OPERATION_CREATE_FILE,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "target_filename": filename,
        "content": normalized_content,
        "content_hash": replay_hash(normalized_content),
        "file_count": 1,
        "plaintext_utf8_only": True,
        "existing_file_modification_allowed": False,
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


def validate_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate an OCS mutation candidate without executing it."""

    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("first mutating Worker failed closed: candidate artifact required")
    if artifact.get("operation") != CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE:
        raise FailClosedRuntimeError("first mutating Worker failed closed: operation not authorized")
    if artifact.get("worker_id") != FILESYSTEM_WORKER_ID:
        raise FailClosedRuntimeError("first mutating Worker failed closed: Worker mismatch")
    if artifact.get("worker_scope") != FILESYSTEM_CREATE_FILE_SCOPE:
        raise FailClosedRuntimeError("first mutating Worker failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_CREATE_FILE:
        raise FailClosedRuntimeError("first mutating Worker failed closed: Worker operation mismatch")
    if artifact.get("file_count") != 1:
        raise FailClosedRuntimeError("first mutating Worker failed closed: exactly one file required")
    for flag in (
        "existing_file_modification_allowed",
        "multi_file_mutation_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "additional_worker_dispatch_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"first mutating Worker failed closed: {flag} must be false")
    validate_mutation_target_filename(artifact.get("target_filename"))
    content = validate_plaintext_mutation_content(artifact.get("content"))
    if artifact.get("content_hash") != replay_hash(content):
        raise FailClosedRuntimeError("first mutating Worker failed closed: candidate content hash mismatch")
    return artifact


def validate_mutation_target_filename(value: Any) -> str:
    filename = _require_string(value, "target_filename")
    path = Path(filename)
    if path.is_absolute() or path.name != filename or filename in {".", ".."}:
        raise FailClosedRuntimeError("first mutating Worker failed closed: target must be one relative filename")
    return filename


def validate_plaintext_mutation_content(value: Any) -> str:
    content = _require_string(value, "content")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("first mutating Worker failed closed: content too large")
    if "\x00" in content:
        raise FailClosedRuntimeError("first mutating Worker failed closed: binary content not allowed")
    return content


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first mutating Worker artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first mutating Worker requires {field}")
    return value
