"""First governed mutating Worker runtime for create-only file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE as FILESYSTEM_CREATE_FILE_SCOPE,
    FILESYSTEM_WORKER_ID,
    FILESYSTEM_WORKER_EXECUTED,
    OPERATION_CREATE_FILE,
    create_authorized_worker_request,
    execute_filesystem_create_request,
    reconstruct_filesystem_worker_replay,
)


FIRST_MUTATING_WORKER_RUNTIME_VERSION = "G8_09_FIRST_MUTATING_WORKER_IMPLEMENTATION_V1"
FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1"
FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1"
FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1"
FIRST_MUTATING_WORKER_VALIDATION_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_VALIDATION_ARTIFACT_V1"
FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1"
FIRST_MUTATING_WORKER_COMPLETION_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_COMPLETION_ARTIFACT_V1"

CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE = "CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE"
FIRST_MUTATING_WORKER_COMPLETED = "FIRST_MUTATING_WORKER_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

DEFAULT_ALLOWLISTED_WORKSPACE = "runtime/governed_mutation_workspace"
MAX_CONTENT_BYTES = 64 * 1024

REPLAY_STEPS = (
    "mutation_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "worker_request_recorded",
    "pre_mutation_state_recorded",
    "worker_result_recorded",
    "post_mutation_validation_recorded",
    "rollback_metadata_recorded",
    "completion_recorded",
)


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
    """Create an OCS-style mutation candidate for the first governed mutation."""

    filename = _validate_filename(target_filename)
    normalized_content = _validate_plaintext_content(content)
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_CANDIDATE_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
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


def create_first_mutating_worker_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to the exact mutation candidate hash."""

    candidate = _validate_candidate(candidate_artifact)
    expected_confirmation = f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("first mutating Worker failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "mutation_authorized_by_approval_only": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def execute_first_mutating_worker(
    *,
    execution_id: str,
    candidate_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    workspace: str | Path = DEFAULT_ALLOWLISTED_WORKSPACE,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute the first governed create-only mutation through the Worker Platform."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        candidate = _validate_candidate(candidate_artifact)
        approval = _validate_approval(approval_artifact, candidate)
        root = _resolve_existing_dir(repository_root, "repository_root")
        workspace_path = _resolve_workspace(root=root, workspace=workspace, expected=candidate["allowlisted_workspace"])
        target = _target_path(workspace_path, candidate["target_filename"])
        pre_mutation = _pre_mutation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            workspace_path=workspace_path,
            target=target,
            created_at=executed_at,
        )
        if pre_mutation["target_exists_before"] is not False:
            raise FailClosedRuntimeError("first mutating Worker failed closed: target file already exists")
        authorization = create_authorization_record(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            proposal_id=candidate["candidate_id"],
            worker_id=FILESYSTEM_WORKER_ID,
            authorization_scope=FILESYSTEM_CREATE_FILE_SCOPE,
            authorization_timestamp=executed_at,
        ).to_dict()
        authorization = validate_authorization_record(authorization)
        worker_request = create_authorized_worker_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:WORKER-REQUEST",
            file_path=candidate["target_filename"],
            content=candidate["content"],
            request_timestamp=executed_at,
            proposal_reference={
                "candidate_id": candidate["candidate_id"],
                "candidate_hash": candidate["artifact_hash"],
                "approval_id": approval["approval_id"],
                "approval_hash": approval["artifact_hash"],
            },
            replay_reference=str(replay_path),
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], approval)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], authorization)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], worker_request)
        _persist_step(replay_path, 4, REPLAY_STEPS[4], pre_mutation)
        worker_capture = execute_filesystem_create_request(
            authorized_request=worker_request,
            base_dir=workspace_path,
            replay_dir=replay_path / "filesystem_worker",
        )
        worker_result = worker_capture["filesystem_worker_execution"]
        if worker_result.get("event_type") != FILESYSTEM_WORKER_EXECUTED:
            raise FailClosedRuntimeError("first mutating Worker failed closed: Worker execution failed")
        worker_replay = reconstruct_filesystem_worker_replay(replay_path / "filesystem_worker")
        validation = _validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            target=target,
            pre_mutation=pre_mutation,
            worker_result=worker_result,
            worker_replay=worker_replay,
            created_at=executed_at,
        )
        rollback = _rollback_artifact(
            execution_id=execution_id,
            candidate=candidate,
            target=target,
            validation=validation,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=FIRST_MUTATING_WORKER_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            worker_request=worker_request,
            pre_mutation=pre_mutation,
            worker_result=worker_result,
            validation=validation,
            rollback=rollback,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        _persist_step(replay_path, 5, REPLAY_STEPS[5], worker_result)
        _persist_step(replay_path, 6, REPLAY_STEPS[6], validation)
        _persist_step(replay_path, 7, REPLAY_STEPS[7], rollback)
        _persist_step(replay_path, 8, REPLAY_STEPS[8], completion)
        return _capture(completion, validation, rollback, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 8, REPLAY_STEPS[8], completion)
        return _capture(completion, None, None, replay_path)


def reconstruct_first_mutating_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate the first governed mutation replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("first mutating Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("first mutating Worker replay artifact must be a JSON object")
        _verify_known_hash(artifact)
        wrappers.append(wrapper)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    worker_request = wrappers[3]["artifact"]
    pre_mutation = wrappers[4]["artifact"]
    worker_result = wrappers[5]["artifact"]
    validation = wrappers[6]["artifact"]
    rollback = wrappers[7]["artifact"]
    completion = wrappers[8]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker approval candidate hash mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("first mutating Worker authorization candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("first mutating Worker worker request authorization mismatch")
    if pre_mutation["target_exists_before"] is not False:
        raise FailClosedRuntimeError("first mutating Worker pre-mutation state mismatch")
    if validation["validation_status"] != "VALIDATED":
        raise FailClosedRuntimeError("first mutating Worker validation missing")
    if rollback["content_hash"] != candidate["content_hash"]:
        raise FailClosedRuntimeError("first mutating Worker rollback hash mismatch")
    if completion["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion candidate mismatch")
    if completion["worker_result_hash"] != worker_result["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion Worker hash mismatch")
    if completion["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion validation hash mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": candidate["operation"],
        "target_filename": candidate["target_filename"],
        "content_hash": candidate["content_hash"],
        "worker_id": authorization["worker_id"],
        "worker_invoked": worker_result["worker_invoked"],
        "repository_mutated": completion["repository_mutated"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "rollback_metadata_present": rollback["rollback_metadata_present"],
        "validation_status": validation["validation_status"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _pre_mutation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    target: Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "workspace_path": str(workspace_path),
        "target_path": str(target),
        "target_filename": candidate["target_filename"],
        "target_exists_before": target.exists(),
        "workspace_allowlisted": True,
        "single_file_scope": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    pre_mutation: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if pre_mutation["target_exists_before"] is not False:
        raise FailClosedRuntimeError("first mutating Worker validation failed closed: target existed before mutation")
    if not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("first mutating Worker validation failed closed: target missing")
    content = target.read_text(encoding="utf-8")
    content_hash = replay_hash(content)
    if content_hash != candidate["content_hash"]:
        raise FailClosedRuntimeError("first mutating Worker validation failed closed: content hash mismatch")
    if worker_result.get("content_hash") != candidate["content_hash"]:
        raise FailClosedRuntimeError("first mutating Worker validation failed closed: Worker hash mismatch")
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_VALIDATION_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_filename": candidate["target_filename"],
        "target_exists_after": True,
        "content_hash": content_hash,
        "expected_content_hash": candidate["content_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "created_file_count": 1,
        "extra_mutation_detected": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "validation_status": "VALIDATED",
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _rollback_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    validation: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_path": str(target),
        "target_filename": candidate["target_filename"],
        "rollback_operation": "DELETE_CREATED_FILE_IF_HASH_MATCHES",
        "content_hash": validation["content_hash"],
        "rollback_authorization_required": True,
        "automatic_rollback_allowed": False,
        "delete_directories_allowed": False,
        "delete_preexisting_file_allowed": False,
        "rollback_metadata_present": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    worker_request: dict[str, Any],
    pre_mutation: dict[str, Any],
    worker_result: dict[str, Any],
    validation: dict[str, Any],
    rollback: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_COMPLETION_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "worker_request_hash": worker_request["request_hash"],
        "pre_mutation_hash": pre_mutation["artifact_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
        "rollback_hash": rollback["artifact_hash"],
        "operation": candidate["operation"],
        "target_filename": candidate["target_filename"],
        "content_hash": candidate["content_hash"],
        "replay_reference": str(replay_path),
        "repository_mutated": True,
        "file_created": True,
        "mutated_file_count": 1,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "additional_worker_dispatched": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
        "rollback_metadata_present": True,
        "fail_closed": False,
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_completion_artifact(
    *,
    execution_id: str,
    executed_by: str,
    executed_at: str,
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_COMPLETION_ARTIFACT_V1,
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "worker_request_hash": None,
        "pre_mutation_hash": None,
        "worker_result_hash": None,
        "validation_hash": None,
        "rollback_hash": None,
        "operation": CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE,
        "target_filename": None,
        "content_hash": None,
        "replay_reference": str(replay_path),
        "repository_mutated": False,
        "file_created": False,
        "mutated_file_count": 0,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "additional_worker_dispatched": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
        "rollback_metadata_present": False,
        "fail_closed": True,
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    completion: dict[str, Any],
    validation: dict[str, Any] | None,
    rollback: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": FIRST_MUTATING_WORKER_RUNTIME_VERSION,
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": completion["operation"],
        "target_filename": completion["target_filename"],
        "content_hash": completion["content_hash"],
        "validation_artifact": deepcopy(validation),
        "rollback_artifact": deepcopy(rollback),
        "completion_artifact": deepcopy(completion),
        "replay_reference": str(replay_path),
        "repository_mutated": completion["repository_mutated"],
        "file_created": completion["file_created"],
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
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
    _validate_filename(artifact.get("target_filename"))
    content = _validate_plaintext_content(artifact.get("content"))
    if artifact.get("content_hash") != replay_hash(content):
        raise FailClosedRuntimeError("first mutating Worker failed closed: candidate content hash mismatch")
    return artifact


def _validate_approval(approval: dict[str, Any] | None, candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval confirmation mismatch")
    if artifact.get("approval_bypassed") is not False or artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("first mutating Worker failed closed: human authority evidence invalid")
    return artifact


def _resolve_existing_dir(path: str | Path, field: str) -> Path:
    resolved = Path(path).resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise FailClosedRuntimeError(f"first mutating Worker failed closed: {field} must exist")
    return resolved


def _resolve_workspace(*, root: Path, workspace: str | Path, expected: str) -> Path:
    workspace_text = _require_string(str(workspace), "workspace")
    expected_text = _require_string(expected, "expected_workspace")
    if workspace_text != expected_text:
        raise FailClosedRuntimeError("first mutating Worker failed closed: workspace is not allowlisted")
    workspace_path = (root / workspace_text).resolve()
    if not _is_relative_to(workspace_path, root):
        raise FailClosedRuntimeError("first mutating Worker failed closed: workspace escapes repository root")
    if not workspace_path.exists() or not workspace_path.is_dir():
        raise FailClosedRuntimeError("first mutating Worker failed closed: allowlisted workspace must exist")
    return workspace_path


def _target_path(workspace_path: Path, filename: str) -> Path:
    target = (workspace_path / _validate_filename(filename)).resolve()
    if target.parent != workspace_path.resolve():
        raise FailClosedRuntimeError("first mutating Worker failed closed: target escaped workspace")
    return target


def _validate_filename(value: Any) -> str:
    filename = _require_string(value, "target_filename")
    path = Path(filename)
    if path.is_absolute() or path.name != filename or filename in {".", ".."}:
        raise FailClosedRuntimeError("first mutating Worker failed closed: target must be one relative filename")
    return filename


def _validate_plaintext_content(value: Any) -> str:
    content = _require_string(value, "content")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("first mutating Worker failed closed: content too large")
    if "\x00" in content:
        raise FailClosedRuntimeError("first mutating Worker failed closed: binary content not allowed")
    return content


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("first mutating Worker replay step ordering mismatch")
    _verify_known_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("first mutating Worker failed closed: replay artifact already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first mutating Worker artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker artifact hash mismatch")


def _verify_known_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("first mutating Worker artifact hash field missing")


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first mutating Worker artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker replay hash mismatch")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first mutating Worker requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "first mutating Worker failed closed"
