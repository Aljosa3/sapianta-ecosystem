"""OCS-owned candidate helpers for governed multi-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_mutation_candidate import (
    create_existing_file_mutation_candidate,
    validate_existing_file_mutation_candidate,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import (
    DEFAULT_ALLOWLISTED_WORKSPACE,
    create_first_mutating_worker_candidate,
    validate_mutation_candidate,
)
from aigol.runtime.platform_core_patch_mutation_candidate import (
    create_single_file_patch_mutation_candidate,
    validate_single_file_patch_mutation_candidate,
)
from aigol.runtime.transport.serialization import replay_hash


MULTI_FILE_MUTATION_CANDIDATE_VERSION = "G9_11_GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTATION_V1"
MULTI_FILE_MUTATION_CANDIDATE_ARTIFACT_V1 = "MULTI_FILE_MUTATION_CANDIDATE_ARTIFACT_V1"
EXECUTE_GOVERNED_MULTI_FILE_MUTATION = "EXECUTE_GOVERNED_MULTI_FILE_MUTATION"

OP_CREATE = "create"
OP_REPLACE = "replace"
OP_PATCH = "patch"
SUPPORTED_OPERATION_TYPES = {OP_CREATE, OP_REPLACE, OP_PATCH}


def create_multi_file_mutation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    operations: list[dict[str, Any]],
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    """Create a deterministic multi-file transaction candidate from per-file candidates."""

    if not isinstance(operations, list) or len(operations) < 2:
        raise FailClosedRuntimeError("multi-file mutation requires at least two operations")
    operation_records: list[dict[str, Any]] = []
    seen_targets: set[str] = set()
    for index, operation in enumerate(operations):
        record = _operation_record(
            index=index,
            session_id=session_id,
            operation=operation,
            created_by=created_by,
            created_at=created_at,
            workspace=workspace,
        )
        if record["target_path"] in seen_targets:
            raise FailClosedRuntimeError("multi-file mutation failed closed: duplicate target path")
        seen_targets.add(record["target_path"])
        operation_records.append(record)
    artifact = {
        "artifact_type": MULTI_FILE_MUTATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": EXECUTE_GOVERNED_MULTI_FILE_MUTATION,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "operation_count": len(operation_records),
        "file_count": len(operation_records),
        "operation_order": [record["operation_id"] for record in operation_records],
        "target_paths": [record["target_path"] for record in operation_records],
        "operations": operation_records,
        "deterministic_ordering": True,
        "transaction_envelope_only": True,
        "composes_certified_single_file_capabilities": True,
        "worker_execution_only": True,
        "governance_authorization_required": True,
        "human_approval_required": True,
        "replay_required": True,
        "rollback_metadata_required": True,
        "validation_required": True,
        "automatic_rollback_allowed": False,
        "autonomous_planning_allowed": False,
        "git_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "dependency_installation_allowed": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_multi_file_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != MULTI_FILE_MUTATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("multi-file mutation failed closed: candidate artifact required")
    if artifact.get("operation") != EXECUTE_GOVERNED_MULTI_FILE_MUTATION:
        raise FailClosedRuntimeError("multi-file mutation failed closed: operation mismatch")
    if artifact.get("operation_count") != len(artifact.get("operations", [])):
        raise FailClosedRuntimeError("multi-file mutation failed closed: operation count mismatch")
    if artifact.get("file_count") != artifact.get("operation_count"):
        raise FailClosedRuntimeError("multi-file mutation failed closed: file count mismatch")
    if artifact.get("operation_count", 0) < 2:
        raise FailClosedRuntimeError("multi-file mutation failed closed: multiple files required")
    seen_targets: set[str] = set()
    operation_ids: list[str] = []
    for index, record in enumerate(artifact["operations"]):
        _validate_operation_record(record, index)
        if record["target_path"] in seen_targets:
            raise FailClosedRuntimeError("multi-file mutation failed closed: duplicate target path")
        seen_targets.add(record["target_path"])
        operation_ids.append(record["operation_id"])
    if artifact.get("operation_order") != operation_ids:
        raise FailClosedRuntimeError("multi-file mutation failed closed: operation order mismatch")
    if artifact.get("target_paths") != [record["target_path"] for record in artifact["operations"]]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: target path list mismatch")
    for flag in (
        "automatic_rollback_allowed",
        "autonomous_planning_allowed",
        "git_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "dependency_installation_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"multi-file mutation failed closed: {flag} must be false")
    return artifact


def _operation_record(
    *,
    index: int,
    session_id: str,
    operation: dict[str, Any],
    created_by: str,
    created_at: str,
    workspace: str,
) -> dict[str, Any]:
    if not isinstance(operation, dict):
        raise FailClosedRuntimeError("multi-file operation must be an object")
    op_type = _require_string(operation.get("operation_type"), "operation_type")
    if op_type not in SUPPORTED_OPERATION_TYPES:
        raise FailClosedRuntimeError("multi-file mutation failed closed: unsupported operation type")
    candidate_id = f"{_require_string(operation.get('operation_id'), 'operation_id')}:CANDIDATE"
    if op_type == OP_CREATE:
        candidate = create_first_mutating_worker_candidate(
            candidate_id=candidate_id,
            session_id=session_id,
            target_filename=_validate_relative_path(operation.get("target_path")),
            content=_require_string(operation.get("content"), "content"),
            created_by=created_by,
            created_at=created_at,
            workspace=workspace,
        )
        target_path = candidate["target_filename"]
        expected_post_hash = candidate["content_hash"]
        pre_hash = None
        rollback_state = "delete_created_file_available"
    elif op_type == OP_REPLACE:
        candidate = create_existing_file_mutation_candidate(
            candidate_id=candidate_id,
            session_id=session_id,
            target_path=_validate_relative_path(operation.get("target_path")),
            expected_content_hash=_require_string(operation.get("expected_content_hash"), "expected_content_hash"),
            replacement_content=_require_string(operation.get("replacement_content"), "replacement_content"),
            created_by=created_by,
            created_at=created_at,
            workspace=workspace,
        )
        target_path = candidate["target_path"]
        expected_post_hash = candidate["replacement_content_hash"]
        pre_hash = candidate["expected_content_hash"]
        rollback_state = "hash_only_prior_content_requires_future_complete_content_evidence"
    else:
        candidate = create_single_file_patch_mutation_candidate(
            candidate_id=candidate_id,
            session_id=session_id,
            target_path=_validate_relative_path(operation.get("target_path")),
            current_content=_require_string(operation.get("current_content"), "current_content"),
            old_text=_require_string(operation.get("old_text"), "old_text"),
            new_text=_require_string(operation.get("new_text"), "new_text"),
            created_by=created_by,
            created_at=created_at,
            workspace=workspace,
        )
        target_path = candidate["target_path"]
        expected_post_hash = candidate["expected_post_content_hash"]
        pre_hash = candidate["pre_content_hash"]
        rollback_state = "restore_complete_prior_content_available"
    return {
        "operation_id": _require_string(operation.get("operation_id"), "operation_id"),
        "operation_index": index,
        "operation_type": op_type,
        "target_path": target_path,
        "pre_content_hash": pre_hash,
        "expected_post_content_hash": expected_post_hash,
        "single_file_candidate": candidate,
        "single_file_candidate_hash": candidate["artifact_hash"],
        "worker_id": candidate["worker_id"],
        "worker_scope": candidate["worker_scope"],
        "worker_operation": candidate["worker_operation"],
        "rollback_metadata_state": rollback_state,
        "complete_resulting_file_is_canonical_artifact": op_type != OP_CREATE,
        "new_file_creation_operation": op_type == OP_CREATE,
        "worker_execution_only": True,
        "replay_visible": True,
    }


def _validate_operation_record(record: dict[str, Any], index: int) -> None:
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("multi-file operation record must be an object")
    if record.get("operation_index") != index:
        raise FailClosedRuntimeError("multi-file mutation failed closed: operation index mismatch")
    op_type = _require_string(record.get("operation_type"), "operation_type")
    if op_type not in SUPPORTED_OPERATION_TYPES:
        raise FailClosedRuntimeError("multi-file mutation failed closed: unsupported operation type")
    _validate_relative_path(record.get("target_path"))
    candidate = record.get("single_file_candidate")
    if op_type == OP_CREATE:
        validated = validate_mutation_candidate(candidate)
        if record.get("target_path") != validated["target_filename"]:
            raise FailClosedRuntimeError("multi-file mutation failed closed: create target mismatch")
        expected_hash = validated["content_hash"]
    elif op_type == OP_REPLACE:
        validated = validate_existing_file_mutation_candidate(candidate)
        if record.get("target_path") != validated["target_path"]:
            raise FailClosedRuntimeError("multi-file mutation failed closed: replace target mismatch")
        expected_hash = validated["replacement_content_hash"]
    else:
        validated = validate_single_file_patch_mutation_candidate(candidate)
        if record.get("target_path") != validated["target_path"]:
            raise FailClosedRuntimeError("multi-file mutation failed closed: patch target mismatch")
        expected_hash = validated["expected_post_content_hash"]
    if record.get("single_file_candidate_hash") != validated["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: single-file candidate hash mismatch")
    if record.get("worker_id") != validated["worker_id"] or record.get("worker_scope") != validated["worker_scope"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: Worker boundary mismatch")
    if record.get("expected_post_content_hash") != expected_hash:
        raise FailClosedRuntimeError("multi-file mutation failed closed: expected post hash mismatch")


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("multi-file mutation failed closed: path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("multi-file mutation failed closed: path must not contain traversal")
    return path.as_posix()


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("multi-file mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multi-file mutation requires {field}")
    return value
