"""OCS-owned candidate helpers for governed single-file patch mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_patch_worker import (
    AUTHORIZED_PATCH_SCOPE,
    FILESYSTEM_PATCH_WORKER_ID,
    OPERATION_APPLY_CONTEXT_PATCH,
)


PATCH_MUTATION_CANDIDATE_VERSION = "G9_04_SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTATION_V1"
PATCH_MUTATION_CANDIDATE_ARTIFACT_V1 = "PATCH_MUTATION_CANDIDATE_ARTIFACT_V1"
APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE = (
    "APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE"
)
MAX_CONTENT_BYTES = 64 * 1024
VALIDATION_STATES = frozenset(
    {
        "validation_required_before_completion",
        "validation_recommended",
        "validation_deferred",
        "validation_not_applicable",
    }
)


def create_single_file_patch_mutation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    target_path: str,
    current_content: str,
    old_text: str,
    new_text: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
    validation_state: str = "validation_recommended",
) -> dict[str, Any]:
    """Create the OCS candidate for one exact context-bound patch."""

    relative_path = validate_patch_target_path(target_path)
    current = validate_plaintext_content(current_content, "current_content")
    old = validate_plaintext_content(old_text, "old_text")
    new = validate_plaintext_content(new_text, "new_text")
    occurrences = current.count(old)
    if occurrences == 0:
        raise FailClosedRuntimeError("patch mutation failed closed: old text missing")
    if occurrences > 1:
        raise FailClosedRuntimeError("patch mutation failed closed: old text ambiguous")
    resulting_content = current.replace(old, new, 1)
    state = _validate_validation_state(validation_state)
    artifact = {
        "artifact_type": PATCH_MUTATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": PATCH_MUTATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE,
        "worker_id": FILESYSTEM_PATCH_WORKER_ID,
        "worker_scope": AUTHORIZED_PATCH_SCOPE,
        "worker_operation": OPERATION_APPLY_CONTEXT_PATCH,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "target_path": relative_path,
        "pre_content_hash": replay_hash(current),
        "old_text": old,
        "old_text_hash": replay_hash(old),
        "new_text": new,
        "new_text_hash": replay_hash(new),
        "occurrence_policy": "exactly_once",
        "expected_post_content_hash": replay_hash(resulting_content),
        "expected_resulting_content": resulting_content,
        "expected_resulting_content_hash": replay_hash(resulting_content),
        "file_count": 1,
        "patch_count": 1,
        "plaintext_utf8_only": True,
        "existing_file_required": True,
        "complete_resulting_file_is_canonical_artifact": True,
        "patch_is_intent_only": True,
        "line_level_delta_is_not_execution_artifact": True,
        "arbitrary_search_replace_allowed": False,
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
        "validation_state": state,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_single_file_patch_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate an OCS patch mutation candidate without executing it."""

    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != PATCH_MUTATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("patch mutation failed closed: candidate artifact required")
    if artifact.get("operation") != APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE:
        raise FailClosedRuntimeError("patch mutation failed closed: operation not authorized")
    if artifact.get("worker_id") != FILESYSTEM_PATCH_WORKER_ID:
        raise FailClosedRuntimeError("patch mutation failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_PATCH_SCOPE:
        raise FailClosedRuntimeError("patch mutation failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_APPLY_CONTEXT_PATCH:
        raise FailClosedRuntimeError("patch mutation failed closed: Worker operation mismatch")
    if artifact.get("file_count") != 1 or artifact.get("patch_count") != 1:
        raise FailClosedRuntimeError("patch mutation failed closed: exactly one file and one patch required")
    if artifact.get("occurrence_policy") != "exactly_once":
        raise FailClosedRuntimeError("patch mutation failed closed: exactly-once policy required")
    if artifact.get("complete_resulting_file_is_canonical_artifact") is not True:
        raise FailClosedRuntimeError("patch mutation failed closed: complete artifact model required")
    if artifact.get("patch_is_intent_only") is not True:
        raise FailClosedRuntimeError("patch mutation failed closed: patch must be intent-only")
    if artifact.get("line_level_delta_is_not_execution_artifact") is not True:
        raise FailClosedRuntimeError("patch mutation failed closed: line delta must not be execution artifact")
    for flag in (
        "arbitrary_search_replace_allowed",
        "new_file_creation_allowed",
        "multi_file_mutation_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "additional_worker_dispatch_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"patch mutation failed closed: {flag} must be false")
    validate_patch_target_path(artifact.get("target_path"))
    old = validate_plaintext_content(artifact.get("old_text"), "old_text")
    new = validate_plaintext_content(artifact.get("new_text"), "new_text")
    resulting = validate_plaintext_content(artifact.get("expected_resulting_content"), "expected_resulting_content")
    if artifact.get("old_text_hash") != replay_hash(old):
        raise FailClosedRuntimeError("patch mutation failed closed: old text hash mismatch")
    if artifact.get("new_text_hash") != replay_hash(new):
        raise FailClosedRuntimeError("patch mutation failed closed: new text hash mismatch")
    if artifact.get("expected_resulting_content_hash") != replay_hash(resulting):
        raise FailClosedRuntimeError("patch mutation failed closed: resulting content hash mismatch")
    if artifact.get("expected_post_content_hash") != replay_hash(resulting):
        raise FailClosedRuntimeError("patch mutation failed closed: expected post hash mismatch")
    _require_string(artifact.get("pre_content_hash"), "pre_content_hash")
    _validate_validation_state(artifact.get("validation_state"))
    return artifact


def validate_patch_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("patch mutation failed closed: target path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("patch mutation failed closed: target path must not contain traversal")
    return path.as_posix()


def validate_plaintext_content(value: Any, field: str) -> str:
    content = _require_string(value, field)
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError(f"patch mutation failed closed: {field} too large")
    if "\x00" in content:
        raise FailClosedRuntimeError(f"patch mutation failed closed: {field} must be plaintext")
    return content


def _validate_validation_state(value: Any) -> str:
    state = _require_string(value, "validation_state")
    if state not in VALIDATION_STATES:
        raise FailClosedRuntimeError("patch mutation failed closed: validation state invalid")
    return state


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("patch mutation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("patch mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"patch mutation requires {field}")
    return value
