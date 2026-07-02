"""Governed Git remote Worker.

This Worker executes only exact authorized Git remote operations. It does not
orchestrate workflows, authorize execution, validate suites, or own Replay.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any

from aigol.authorization.authorization_record import validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


GIT_REMOTE_WORKER_VERSION = "G11_08_GOVERNED_GIT_REMOTE_WORKFLOW_IMPLEMENTATION_V1"
GIT_REMOTE_WORKER_ID = "GOVERNED_GIT_REMOTE_WORKER"
AUTHORIZED_GIT_REMOTE_REQUEST_TYPE = "AUTHORIZED_GIT_REMOTE_REQUEST_V1"
AUTHORIZED_GIT_REMOTE_SCOPE = "BOUNDED_GIT_REMOTE_OPERATION"

OPERATION_REMOTE_INSPECTION = "REMOTE_INSPECTION"
OPERATION_FETCH = "FETCH"
OPERATION_PULL = "PULL"
OPERATION_PUSH = "PUSH"
AUTHORIZED_OPERATIONS = {
    OPERATION_REMOTE_INSPECTION,
    OPERATION_FETCH,
    OPERATION_PULL,
    OPERATION_PUSH,
}

GIT_REMOTE_REQUEST_CREATED = "GIT_REMOTE_REQUEST_CREATED"
GIT_REMOTE_PRE_STATE_RECORDED = "GIT_REMOTE_PRE_STATE_RECORDED"
GIT_REMOTE_WORKER_EXECUTED = "GIT_REMOTE_WORKER_EXECUTED"
GIT_REMOTE_WORKER_FAILED = "GIT_REMOTE_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "authorized_git_remote_request",
    "git_remote_worker_pre_state",
    "git_remote_worker_execution",
)

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_command",
        "shell_command",
        "shell",
        "merge_request",
        "rebase_request",
        "force_push_request",
        "tag_request",
        "deployment_request",
        "provider_invocation_request",
        "dispatch_request",
        "orchestration_request",
        "memory_mutation",
        "replay_mutation",
    }
)


def create_authorized_git_remote_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    operation: str,
    repository_id: str,
    remote_name: str,
    remote_url: str,
    local_branch: str,
    remote_branch: str,
    expected_local_head: str,
    expected_remote_head: str | None,
    protected_branch: bool,
    protected_branch_authorized: bool,
    credential_reference: str,
    validation_artifact_hash: str,
    rollback_reference: str,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the Worker-facing request for one governed Git remote operation."""

    record = _validate_git_remote_authorization(authorization_record)
    normalized_operation = _operation(operation)
    protected = bool(protected_branch)
    protected_authorized = bool(protected_branch_authorized)
    if protected and not protected_authorized:
        raise FailClosedRuntimeError("governed Git remote failed closed: protected branch authorization required")
    request = {
        "request_type": AUTHORIZED_GIT_REMOTE_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": normalized_operation,
        "repository_id": _require_string(repository_id, "repository_id"),
        "remote_name": _normalize_remote_name(remote_name),
        "remote_url": _require_string(remote_url, "remote_url"),
        "remote_url_fingerprint": replay_hash(_require_string(remote_url, "remote_url")),
        "local_branch": _require_string(local_branch, "local_branch"),
        "remote_branch": _require_string(remote_branch, "remote_branch"),
        "expected_local_head": _require_string(expected_local_head, "expected_local_head"),
        "expected_remote_head": _optional_string(expected_remote_head),
        "protected_branch": protected,
        "protected_branch_authorized": protected_authorized,
        "credential_reference": _require_string(credential_reference, "credential_reference"),
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "validation_artifact_hash": _require_string(validation_artifact_hash, "validation_artifact_hash"),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "shell_allowed": False,
        "raw_command_allowed": False,
        "merge_allowed": False,
        "rebase_allowed": False,
        "force_push_allowed": False,
        "tag_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_git_remote_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a governed Git remote request without executing Git."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized Git remote request is required")
    _reject_forbidden_fields(request, "authorized Git remote request")
    if request.get("request_type") != AUTHORIZED_GIT_REMOTE_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized Git remote request type is invalid")
    if request.get("worker_id") != GIT_REMOTE_WORKER_ID:
        raise FailClosedRuntimeError("authorized Git remote request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_GIT_REMOTE_SCOPE:
        raise FailClosedRuntimeError("authorized Git remote request scope mismatch")
    _operation(request.get("operation"))
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    _require_string(request.get("repository_id"), "repository_id")
    _normalize_remote_name(request.get("remote_name"))
    remote_url = _require_string(request.get("remote_url"), "remote_url")
    if request.get("remote_url_fingerprint") != replay_hash(remote_url):
        raise FailClosedRuntimeError("authorized Git remote request URL fingerprint mismatch")
    _require_string(request.get("local_branch"), "local_branch")
    _require_string(request.get("remote_branch"), "remote_branch")
    _require_string(request.get("expected_local_head"), "expected_local_head")
    _optional_string(request.get("expected_remote_head"))
    if request.get("protected_branch") is True and request.get("protected_branch_authorized") is not True:
        raise FailClosedRuntimeError("authorized Git remote request protected branch authorization missing")
    for field in (
        "credential_value_recorded",
        "credential_hash_recorded",
        "shell_allowed",
        "raw_command_allowed",
        "merge_allowed",
        "rebase_allowed",
        "force_push_allowed",
        "tag_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError(f"authorized Git remote request {field} must be false")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized Git remote request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected = deepcopy(request)
    expected.pop("request_hash")
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("authorized Git remote request hash mismatch")
    if authorization_record is not None:
        record = _validate_git_remote_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized Git remote request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized Git remote request authorization hash mismatch")
    return deepcopy(request)


def execute_git_remote_request(
    *,
    authorized_request: dict[str, Any],
    repository_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute exactly one authorized Git remote operation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_git_remote_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        root = _resolve_git_repository(repository_root)
        pre_state = _pre_state_artifact(request=request, root=root)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], pre_state)
        result = _execute_operation(request=request, root=root, pre_state=pre_state)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], result)
        return _capture(failure, result)


def reconstruct_git_remote_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker-side governed Git remote replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("Git remote Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("Git remote Worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "Git remote Worker replay artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    result = wrappers[2]["artifact"]
    if result.get("request_hash") != request.get("request_hash"):
        raise FailClosedRuntimeError("Git remote Worker replay request hash mismatch")
    return {
        "request_id": request["request_id"],
        "authorization_id": request["authorization_id"],
        "operation": request["operation"],
        "repository_id": request["repository_id"],
        "remote_name": request["remote_name"],
        "remote_branch": request["remote_branch"],
        "local_branch": request["local_branch"],
        "execution_status": result["execution_status"],
        "exit_code": result["exit_code"],
        "git_remote_performed": result["git_remote_performed"],
        "remote_state_changed": result["remote_state_changed"],
        "worker_invoked": result["worker_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _pre_state_artifact(*, request: dict[str, Any], root: Path) -> dict[str, Any]:
    branch = _git_stdout(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git_stdout(root, ["rev-parse", "HEAD"])
    if branch != request["local_branch"]:
        raise FailClosedRuntimeError("governed Git remote failed closed: branch mismatch")
    if head != request["expected_local_head"]:
        raise FailClosedRuntimeError("governed Git remote failed closed: local HEAD mismatch")
    remote_url = _git_stdout(root, ["remote", "get-url", request["remote_name"]])
    if replay_hash(remote_url) != request["remote_url_fingerprint"]:
        raise FailClosedRuntimeError("governed Git remote failed closed: remote URL fingerprint mismatch")
    dirty = _git_stdout(root, ["status", "--porcelain"])
    if request["operation"] in {OPERATION_PULL, OPERATION_PUSH} and dirty:
        raise FailClosedRuntimeError("governed Git remote failed closed: working tree not clean")
    remote_head = _remote_head(root, request["remote_name"], request["remote_branch"])
    expected_remote = request.get("expected_remote_head") or None
    if expected_remote is not None and remote_head != expected_remote:
        raise FailClosedRuntimeError("governed Git remote failed closed: remote HEAD mismatch")
    artifact = {
        "runtime_version": GIT_REMOTE_WORKER_VERSION,
        "event_type": GIT_REMOTE_PRE_STATE_RECORDED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": request["operation"],
        "repository_id": request["repository_id"],
        "local_branch": branch,
        "local_head": head,
        "remote_name": request["remote_name"],
        "remote_url_fingerprint": request["remote_url_fingerprint"],
        "remote_branch": request["remote_branch"],
        "remote_head": remote_head,
        "working_tree_clean": not bool(dirty),
        "protected_branch": request["protected_branch"],
        "protected_branch_authorized": request["protected_branch_authorized"],
        "credential_reference": request["credential_reference"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_operation(*, request: dict[str, Any], root: Path, pre_state: dict[str, Any]) -> dict[str, Any]:
    operation = request["operation"]
    if operation == OPERATION_REMOTE_INSPECTION:
        argv = ["remote", "-v"]
        completed = _git_completed(root, argv)
        remote_state_changed = False
    elif operation == OPERATION_FETCH:
        argv = ["fetch", request["remote_name"], request["remote_branch"]]
        completed = _git_completed(root, argv)
        remote_state_changed = False
    elif operation == OPERATION_PULL:
        argv = ["pull", "--ff-only", request["remote_name"], request["remote_branch"]]
        completed = _git_completed(root, argv)
        remote_state_changed = False
    elif operation == OPERATION_PUSH:
        argv = ["push", request["remote_name"], f"{request['local_branch']}:{request['remote_branch']}"]
        completed = _git_completed(root, argv)
        remote_state_changed = completed.returncode == 0
    else:
        raise FailClosedRuntimeError("governed Git remote failed closed: unsupported operation")
    post_local_head = _git_stdout(root, ["rev-parse", "HEAD"])
    post_remote_head = _remote_head(root, request["remote_name"], request["remote_branch"])
    status = "GIT_REMOTE_OPERATION_COMPLETED" if completed.returncode == 0 else FAILED_CLOSED
    artifact = {
        "runtime_version": GIT_REMOTE_WORKER_VERSION,
        "event_type": GIT_REMOTE_WORKER_EXECUTED if completed.returncode == 0 else GIT_REMOTE_WORKER_FAILED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": operation,
        "repository_id": request["repository_id"],
        "remote_name": request["remote_name"],
        "remote_branch": request["remote_branch"],
        "local_branch": request["local_branch"],
        "pre_local_head": pre_state["local_head"],
        "post_local_head": post_local_head,
        "pre_remote_head": pre_state["remote_head"],
        "post_remote_head": post_remote_head,
        "argv": ["git", *argv],
        "argv_hash": replay_hash(["git", *argv]),
        "exit_code": completed.returncode,
        "stdout": _bounded_output(completed.stdout),
        "stderr": _bounded_output(completed.stderr),
        "execution_status": status,
        "git_remote_performed": completed.returncode == 0,
        "remote_state_changed": remote_state_changed,
        "worker_invoked": True,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(request)
    artifact["runtime_version"] = GIT_REMOTE_WORKER_VERSION
    artifact["event_type"] = GIT_REMOTE_REQUEST_CREATED
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    request_id = authorized_request.get("request_id") if isinstance(authorized_request, dict) else None
    request_hash = authorized_request.get("request_hash") if isinstance(authorized_request, dict) else None
    artifact = {
        "runtime_version": GIT_REMOTE_WORKER_VERSION,
        "event_type": GIT_REMOTE_WORKER_FAILED,
        "request_id": request_id,
        "request_hash": request_hash,
        "execution_status": FAILED_CLOSED,
        "failure_reason": _bounded_output(failure_reason),
        "git_remote_performed": False,
        "remote_state_changed": False,
        "worker_invoked": False,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(failure)


def _capture(request_artifact: dict[str, Any], result_artifact: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "worker_id": GIT_REMOTE_WORKER_ID,
        "request_id": request_artifact.get("request_id"),
        "request_hash": request_artifact.get("request_hash"),
        "operation": request_artifact.get("operation"),
        "execution_status": result_artifact["execution_status"],
        "git_remote_performed": result_artifact["git_remote_performed"],
        "remote_state_changed": result_artifact["remote_state_changed"],
        "worker_invoked": result_artifact["worker_invoked"],
        "failure_reason": result_artifact.get("failure_reason"),
        "result_hash": result_artifact["artifact_hash"],
        "replay_visible": True,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _validate_git_remote_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record.get("worker_id") != GIT_REMOTE_WORKER_ID:
        raise FailClosedRuntimeError("Git remote authorization Worker mismatch")
    if record.get("authorization_scope") != AUTHORIZED_GIT_REMOTE_SCOPE:
        raise FailClosedRuntimeError("Git remote authorization scope mismatch")
    return record


def _resolve_git_repository(repository_root: str | Path) -> Path:
    root = Path(repository_root).resolve()
    if not (root / ".git").exists():
        raise FailClosedRuntimeError("governed Git remote failed closed: repository root is not Git repository")
    return root


def _remote_head(root: Path, remote_name: str, remote_branch: str) -> str | None:
    completed = _git_completed(root, ["ls-remote", remote_name, f"refs/heads/{remote_branch}"])
    if completed.returncode != 0:
        raise FailClosedRuntimeError("governed Git remote failed closed: remote head unavailable")
    output = (completed.stdout or "").strip()
    if not output:
        return None
    return output.split()[0]


def _git_stdout(root: Path, args: list[str]) -> str:
    completed = _git_completed(root, args)
    if completed.returncode != 0:
        raise FailClosedRuntimeError(_bounded_output(completed.stderr) or "git command failed")
    return (completed.stdout or "").strip()


def _git_completed(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
    )


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only Git remote replay artifact already exists: {path.name}")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "Git remote artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if path.exists():
        return
    _persist_step(replay_path, index, step, artifact)


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("Git remote Worker replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _reject_forbidden_fields(request: dict[str, Any], label: str) -> None:
    present = FORBIDDEN_REQUEST_FIELDS.intersection(request)
    if present:
        raise FailClosedRuntimeError(f"{label} contains forbidden field {sorted(present)[0]}")


def _operation(value: Any) -> str:
    operation = _require_string(value, "operation").strip().upper().replace("-", "_").replace(" ", "_")
    if operation not in AUTHORIZED_OPERATIONS:
        raise FailClosedRuntimeError("governed Git remote failed closed: unsupported operation")
    return operation


def _normalize_remote_name(value: Any) -> str:
    remote = _require_string(value, "remote_name").strip()
    if remote.startswith("-") or any(char.isspace() for char in remote):
        raise FailClosedRuntimeError("governed Git remote failed closed: invalid remote name")
    return remote


def _require_json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"governed Git remote requires {field}")
    return deepcopy(value)


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FailClosedRuntimeError("governed Git remote optional string is invalid")
    return value.strip() or None


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git remote requires {field}")
    return value.strip()


def _bounded_output(value: Any, limit: int = 4000) -> str:
    text = "" if value is None else str(value)
    return text[:limit]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed Git remote failed closed"
