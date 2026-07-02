"""Governed filesystem Worker for one authorized rollback action."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


FILESYSTEM_ROLLBACK_WORKER_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
FILESYSTEM_ROLLBACK_WORKER_ID = "FILESYSTEM_SINGLE_TARGET_ROLLBACK_WORKER"
AUTHORIZED_ROLLBACK_REQUEST_TYPE = "AUTHORIZED_SINGLE_TARGET_ROLLBACK_REQUEST_V1"
AUTHORIZED_ROLLBACK_SCOPE = "FILESYSTEM_SINGLE_TARGET_ROLLBACK"
OPERATION_EXECUTE_ROLLBACK = "EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK"
ROLLBACK_DELETE_CREATED_FILE = "DELETE_CREATED_FILE_IF_HASH_MATCHES"
ROLLBACK_RESTORE_ORIGINAL_CONTENT = "RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH"
FILESYSTEM_ROLLBACK_WORKER_EXECUTED = "FILESYSTEM_ROLLBACK_WORKER_EXECUTED"
FILESYSTEM_ROLLBACK_WORKER_FAILED = "FILESYSTEM_ROLLBACK_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorized_rollback_request", "filesystem_rollback_worker_execution")
MAX_CONTENT_BYTES = 64 * 1024

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_provider_output",
        "raw_proposal",
        "raw_authorization_artifact",
        "dispatch_request",
        "orchestration_request",
        "planning_request",
        "reflection_request",
        "memory_mutation",
        "replay_mutation",
        "git_operation",
        "commit_request",
        "deployment_request",
        "provider_invocation",
    }
)


def create_authorized_rollback_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    rollback_action: str,
    file_path: str,
    authorized_current_hash: str,
    expected_rollback_result_hash: str,
    restore_content: str | None,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the bounded request accepted by the rollback Worker."""

    record = _validate_rollback_authorization(authorization_record)
    action = _validate_action(rollback_action)
    content = None if restore_content is None else _validate_plaintext(restore_content)
    if action == ROLLBACK_RESTORE_ORIGINAL_CONTENT and content is None:
        raise FailClosedRuntimeError("rollback Worker requires restore content")
    if action == ROLLBACK_DELETE_CREATED_FILE and content is not None:
        raise FailClosedRuntimeError("rollback Worker delete action must not include restore content")
    request = {
        "request_type": AUTHORIZED_ROLLBACK_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "proposal_reference": deepcopy(proposal_reference),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_EXECUTE_ROLLBACK,
        "rollback_action": action,
        "file_path": _validate_relative_path(file_path),
        "authorized_current_hash": _require_string(authorized_current_hash, "authorized_current_hash"),
        "expected_rollback_result_hash": _require_string(
            expected_rollback_result_hash,
            "expected_rollback_result_hash",
        ),
        "restore_content": content,
        "restore_content_hash": replay_hash(content) if content is not None else None,
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "authorization_hash": record["authorization_hash"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "authority": False,
        "provider_authority": False,
        "proposal_authority": False,
        "governance_authority": False,
        "authorization_authority": False,
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "certification_performed": False,
        "multi_target_rollback": False,
        "automatic_rollback": False,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_rollback_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized rollback request is required")
    if FORBIDDEN_REQUEST_FIELDS.intersection(request):
        raise FailClosedRuntimeError("authorized rollback request contains forbidden field")
    if request.get("request_type") != AUTHORIZED_ROLLBACK_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized rollback request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    if request.get("worker_id") != FILESYSTEM_ROLLBACK_WORKER_ID:
        raise FailClosedRuntimeError("authorized rollback request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_ROLLBACK_SCOPE:
        raise FailClosedRuntimeError("authorized rollback request scope mismatch")
    if request.get("operation") != OPERATION_EXECUTE_ROLLBACK:
        raise FailClosedRuntimeError("authorized rollback request operation mismatch")
    action = _validate_action(request.get("rollback_action"))
    _validate_relative_path(request.get("file_path"))
    _require_string(request.get("authorized_current_hash"), "authorized_current_hash")
    _require_string(request.get("expected_rollback_result_hash"), "expected_rollback_result_hash")
    content = request.get("restore_content")
    if content is not None:
        content = _validate_plaintext(content)
    if action == ROLLBACK_RESTORE_ORIGINAL_CONTENT:
        if content is None:
            raise FailClosedRuntimeError("authorized rollback request restore content required")
        if request.get("restore_content_hash") != replay_hash(content):
            raise FailClosedRuntimeError("authorized rollback request restore content hash mismatch")
    if action == ROLLBACK_DELETE_CREATED_FILE:
        if content is not None or request.get("restore_content_hash") is not None:
            raise FailClosedRuntimeError("authorized rollback request delete content forbidden")
    _require_string(request.get("request_timestamp"), "request_timestamp")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_string(request.get("replay_reference"), "replay_reference")
    for field in (
        "authority",
        "provider_authority",
        "proposal_authority",
        "governance_authority",
        "authorization_authority",
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
        "planning_performed",
        "certification_performed",
        "multi_target_rollback",
        "automatic_rollback",
        "git_performed",
        "branch_manipulation_performed",
        "deployment_performed",
        "provider_invoked",
        "dependency_rollback_performed",
    ):
        _require_false(request.get(field), field)
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized rollback request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorized rollback request hash mismatch")
    if authorization_record is not None:
        record = _validate_rollback_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized rollback request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized rollback request authorization hash mismatch")
    return deepcopy(request)


def execute_filesystem_rollback_request(
    *,
    authorized_request: dict[str, Any],
    base_dir: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute exactly one authorized rollback action."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_rollback_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        target = _resolve_target(base_dir=Path(base_dir), file_path=request["file_path"])
        if request["rollback_action"] == ROLLBACK_DELETE_CREATED_FILE:
            result = _execute_delete(request, target)
        else:
            result = _execute_restore(request, target)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(failure, result)


def reconstruct_filesystem_rollback_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("filesystem rollback Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("filesystem rollback Worker replay artifact must be an object")
        _verify_artifact_hash(artifact, "filesystem rollback Worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("filesystem rollback Worker replay request hash mismatch")
    if result_artifact.get("request_artifact_hash") != request_artifact.get("artifact_hash"):
        raise FailClosedRuntimeError("filesystem rollback Worker replay request artifact mismatch")
    return {
        "authorization_id": request_artifact["authorization_id"],
        "request_id": request_artifact["request_id"],
        "worker_id": request_artifact["worker_id"],
        "rollback_action": request_artifact["rollback_action"],
        "file_path": request_artifact["file_path"],
        "pre_rollback_hash": result_artifact["pre_rollback_hash"],
        "post_rollback_hash": result_artifact["post_rollback_hash"],
        "target_exists_after": result_artifact["target_exists_after"],
        "worker_invoked": result_artifact["worker_invoked"],
        "rollback_executed": result_artifact["rollback_executed"],
        "git_performed": result_artifact["git_performed"],
        "deployment_performed": result_artifact["deployment_performed"],
        "provider_invoked": result_artifact["provider_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _execute_delete(request: dict[str, Any], target: Path) -> dict[str, Any]:
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("filesystem rollback Worker delete target invalid")
    current = _read_plaintext(target)
    current_hash = replay_hash(current)
    if current_hash != request["authorized_current_hash"]:
        raise FailClosedRuntimeError("filesystem rollback Worker current hash conflict")
    target.unlink()
    if target.exists():
        raise FailClosedRuntimeError("filesystem rollback Worker delete failed")
    return _execution_result(
        request=request,
        target=target,
        pre_rollback_hash=current_hash,
        post_rollback_hash=request["expected_rollback_result_hash"],
        target_exists_after=False,
        status=FILESYSTEM_ROLLBACK_WORKER_EXECUTED,
        failure_reason=None,
    )


def _execute_restore(request: dict[str, Any], target: Path) -> dict[str, Any]:
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("filesystem rollback Worker restore target invalid")
    current = _read_plaintext(target)
    current_hash = replay_hash(current)
    if current_hash != request["authorized_current_hash"]:
        raise FailClosedRuntimeError("filesystem rollback Worker current hash conflict")
    restore_content = _validate_plaintext(request["restore_content"])
    if replay_hash(restore_content) != request["expected_rollback_result_hash"]:
        raise FailClosedRuntimeError("filesystem rollback Worker restore content hash mismatch")
    target.write_text(restore_content, encoding="utf-8")
    final_content = _read_plaintext(target)
    final_hash = replay_hash(final_content)
    if final_hash != request["expected_rollback_result_hash"]:
        raise FailClosedRuntimeError("filesystem rollback Worker post rollback hash mismatch")
    return _execution_result(
        request=request,
        target=target,
        pre_rollback_hash=current_hash,
        post_rollback_hash=final_hash,
        target_exists_after=True,
        status=FILESYSTEM_ROLLBACK_WORKER_EXECUTED,
        failure_reason=None,
    )


def _execution_result(
    *,
    request: dict[str, Any],
    target: Path,
    pre_rollback_hash: str,
    post_rollback_hash: str,
    target_exists_after: bool,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": status,
        "runtime_version": FILESYSTEM_ROLLBACK_WORKER_VERSION,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_artifact_hash": _request_replay_artifact(request)["artifact_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "worker_id": FILESYSTEM_ROLLBACK_WORKER_ID,
        "rollback_action": request["rollback_action"],
        "target_path": str(target),
        "file_path": request["file_path"],
        "pre_rollback_hash": pre_rollback_hash,
        "post_rollback_hash": post_rollback_hash,
        "expected_rollback_result_hash": request["expected_rollback_result_hash"],
        "target_exists_after": target_exists_after,
        "worker_invoked": True,
        "rollback_executed": True,
        "mutated_file_count": 1,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(request)
    artifact["artifact_type"] = "AUTHORIZED_ROLLBACK_REQUEST_REPLAY_ARTIFACT_V1"
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    request_id = authorized_request.get("request_id") if isinstance(authorized_request, dict) else "INVALID_REQUEST"
    artifact = {
        "artifact_type": FILESYSTEM_ROLLBACK_WORKER_FAILED,
        "runtime_version": FILESYSTEM_ROLLBACK_WORKER_VERSION,
        "request_id": request_id if isinstance(request_id, str) else "INVALID_REQUEST",
        "failure_reason": failure_reason,
        "worker_invoked": False,
        "rollback_executed": False,
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": FILESYSTEM_ROLLBACK_WORKER_FAILED,
        "runtime_version": FILESYSTEM_ROLLBACK_WORKER_VERSION,
        "request_id": failure["request_id"],
        "request_hash": failure["artifact_hash"],
        "request_artifact_hash": failure["artifact_hash"],
        "worker_id": FILESYSTEM_ROLLBACK_WORKER_ID,
        "rollback_action": None,
        "target_path": None,
        "file_path": None,
        "pre_rollback_hash": None,
        "post_rollback_hash": None,
        "expected_rollback_result_hash": None,
        "target_exists_after": None,
        "worker_invoked": False,
        "rollback_executed": False,
        "mutated_file_count": 0,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "failure_reason": failure["failure_reason"],
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request_artifact: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "authorized_rollback_request": deepcopy(request_artifact),
        "filesystem_rollback_worker_execution": deepcopy(result),
    }


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("filesystem rollback Worker replay artifact already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("filesystem rollback Worker replay step mismatch")
    _verify_artifact_hash(artifact, "filesystem rollback Worker artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": FILESYSTEM_ROLLBACK_WORKER_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _resolve_target(*, base_dir: Path, file_path: str) -> Path:
    base = base_dir.resolve()
    target = (base / _validate_relative_path(file_path)).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise FailClosedRuntimeError("filesystem rollback Worker target escaped base dir") from exc
    return target


def _read_plaintext(target: Path) -> str:
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("filesystem rollback Worker target must be UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("filesystem rollback Worker target must be plaintext")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("filesystem rollback Worker target content too large")
    return content


def _validate_plaintext(value: Any) -> str:
    content = _require_string(value, "restore_content")
    if "\x00" in content:
        raise FailClosedRuntimeError("filesystem rollback Worker content must be plaintext")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("filesystem rollback Worker content too large")
    return content


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "file_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("filesystem rollback Worker path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("filesystem rollback Worker path must not contain traversal")
    return path.as_posix()


def _validate_action(value: Any) -> str:
    action = _require_string(value, "rollback_action")
    if action not in {ROLLBACK_DELETE_CREATED_FILE, ROLLBACK_RESTORE_ORIGINAL_CONTENT}:
        raise FailClosedRuntimeError("filesystem rollback Worker action is invalid")
    return action


def _validate_rollback_authorization(record: dict[str, Any]) -> dict[str, Any]:
    authorization = validate_authorization_record(record)
    if authorization.get("worker_id") != FILESYSTEM_ROLLBACK_WORKER_ID:
        raise FailClosedRuntimeError("rollback authorization Worker mismatch")
    if authorization.get("authorization_scope") != AUTHORIZED_ROLLBACK_SCOPE:
        raise FailClosedRuntimeError("rollback authorization scope mismatch")
    return authorization


def _require_json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"filesystem rollback Worker requires {field}")
    return deepcopy(value)


def _require_false(value: Any, field: str) -> None:
    if value is not False:
        raise FailClosedRuntimeError(f"filesystem rollback Worker requires {field} false")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("filesystem rollback Worker replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"filesystem rollback Worker requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__
