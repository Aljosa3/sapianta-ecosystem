"""Governed local Git commit Worker."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import os
import subprocess
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


GIT_COMMIT_WORKER_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GIT_COMMIT_WORKER_ID = "GOVERNED_LOCAL_GIT_COMMIT_WORKER"
AUTHORIZED_GIT_COMMIT_REQUEST_TYPE = "AUTHORIZED_GIT_COMMIT_REQUEST_V1"
AUTHORIZED_GIT_COMMIT_SCOPE = "CREATE_GOVERNED_LOCAL_GIT_COMMIT"
OPERATION_CREATE_LOCAL_GIT_COMMIT = "CREATE_LOCAL_GIT_COMMIT"
AUTHORIZED_GIT_COMMIT_REQUEST_CREATED = "AUTHORIZED_GIT_COMMIT_REQUEST_CREATED"
GIT_COMMIT_WORKER_PRE_STATE_RECORDED = "GIT_COMMIT_WORKER_PRE_STATE_RECORDED"
GIT_COMMIT_WORKER_STAGED = "GIT_COMMIT_WORKER_STAGED"
GIT_COMMIT_WORKER_EXECUTED = "GIT_COMMIT_WORKER_EXECUTED"
GIT_COMMIT_WORKER_FAILED = "GIT_COMMIT_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "authorized_git_commit_request",
    "git_commit_worker_pre_state",
    "git_commit_worker_staging",
    "git_commit_worker_execution",
)

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "push_request",
        "remote_request",
        "branch_request",
        "merge_request",
        "rebase_request",
        "checkout_request",
        "reset_request",
        "revert_request",
        "tag_request",
        "stash_request",
        "deployment_request",
        "provider_invocation_request",
        "shell_command",
        "raw_command",
        "raw_provider_output",
        "dispatch_request",
        "orchestration_request",
        "memory_mutation",
        "replay_mutation",
    }
)


def create_authorized_git_commit_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    candidate: dict[str, Any],
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the Worker-facing request for one governed local Git commit."""

    record = _validate_git_commit_authorization(authorization_record)
    request = {
        "request_type": AUTHORIZED_GIT_COMMIT_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_CREATE_LOCAL_GIT_COMMIT,
        "candidate_id": _require_string(candidate.get("candidate_id"), "candidate_id"),
        "candidate_hash": _require_string(candidate.get("artifact_hash"), "candidate_hash"),
        "repository_id": _require_string(candidate.get("repository_id"), "repository_id"),
        "branch_name": _require_string(candidate.get("branch_name"), "branch_name"),
        "expected_head": _require_string(candidate.get("expected_head"), "expected_head"),
        "staged_content_model": "EXPLICIT_FILE_SET_STAGED_BY_COMMIT_WORKER",
        "file_set": _require_json_list(candidate.get("file_set"), "file_set"),
        "file_set_hash": _require_string(candidate.get("file_set_hash"), "file_set_hash"),
        "commit_message": _require_json_object(candidate.get("commit_message"), "commit_message"),
        "commit_message_hash": _require_string(candidate.get("commit_message_hash"), "commit_message_hash"),
        "author": _require_json_object(candidate.get("author"), "author"),
        "author_hash": _require_string(candidate.get("author_hash"), "author_hash"),
        "validation_artifact_hash": _require_string(candidate.get("validation_artifact_hash"), "validation_artifact_hash"),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
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
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_git_commit_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a governed Git commit request without executing Git."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized Git commit request is required")
    _reject_forbidden_fields(request, "authorized Git commit request")
    if request.get("request_type") != AUTHORIZED_GIT_COMMIT_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized Git commit request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    if request.get("worker_id") != GIT_COMMIT_WORKER_ID:
        raise FailClosedRuntimeError("authorized Git commit request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_GIT_COMMIT_SCOPE:
        raise FailClosedRuntimeError("authorized Git commit request scope mismatch")
    if request.get("operation") != OPERATION_CREATE_LOCAL_GIT_COMMIT:
        raise FailClosedRuntimeError("authorized Git commit request operation mismatch")
    if request.get("file_set_hash") != replay_hash(_require_json_list(request.get("file_set"), "file_set")):
        raise FailClosedRuntimeError("authorized Git commit request file set hash mismatch")
    if request.get("commit_message_hash") != replay_hash(_require_json_object(request.get("commit_message"), "commit_message")):
        raise FailClosedRuntimeError("authorized Git commit request message hash mismatch")
    if request.get("author_hash") != replay_hash(_require_json_object(request.get("author"), "author")):
        raise FailClosedRuntimeError("authorized Git commit request author hash mismatch")
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
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
    ):
        if request.get(flag) is not False:
            raise FailClosedRuntimeError(f"authorized Git commit request {flag} must be false")
    if request.get("local_commit_only") is not True:
        raise FailClosedRuntimeError("authorized Git commit request must be local-only")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized Git commit request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorized Git commit request hash mismatch")
    if authorization_record is not None:
        record = _validate_git_commit_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized Git commit request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized Git commit request authorization hash mismatch")
    return deepcopy(request)


def execute_git_commit_request(
    *,
    authorized_request: dict[str, Any],
    repository_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create exactly one local Git commit from the authorized file set."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_git_commit_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        root = _resolve_git_repository(repository_root)
        pre_state = _pre_state_artifact(request=request, root=root)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], pre_state)
        staging = _stage_authorized_files(request=request, root=root, pre_state=pre_state)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], staging)
        result = _create_commit(request=request, root=root, staging=staging)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(failure, result)


def reconstruct_git_commit_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker-side governed Git commit replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("Git commit Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("Git commit Worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "Git commit Worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[3]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("Git commit Worker replay request hash mismatch")
    return {
        "authorization_id": request_artifact["authorization_id"],
        "request_id": request_artifact["request_id"],
        "candidate_id": request_artifact["candidate_id"],
        "candidate_hash": request_artifact["candidate_hash"],
        "repository_id": request_artifact["repository_id"],
        "branch_name": result_artifact["branch_name"],
        "parent_head": result_artifact["parent_head"],
        "commit_hash": result_artifact["commit_hash"],
        "post_commit_head": result_artifact["post_commit_head"],
        "file_set_hash": result_artifact["file_set_hash"],
        "git_performed": result_artifact["git_performed"],
        "commit_created": result_artifact["commit_created"],
        "worker_invoked": result_artifact["worker_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _pre_state_artifact(*, request: dict[str, Any], root: Path) -> dict[str, Any]:
    branch = _git_stdout(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git_stdout(root, ["rev-parse", "HEAD"])
    if branch != request["branch_name"]:
        raise FailClosedRuntimeError("governed Git commit failed closed: branch mismatch")
    if head != request["expected_head"]:
        raise FailClosedRuntimeError("governed Git commit failed closed: HEAD mismatch")
    staged_paths = _staged_paths(root)
    if staged_paths:
        raise FailClosedRuntimeError("governed Git commit failed closed: unexpected staged content")
    file_hashes = _verify_file_set(root=root, file_set=request["file_set"])
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": GIT_COMMIT_WORKER_PRE_STATE_RECORDED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "repository_id": request["repository_id"],
        "branch_name": branch,
        "expected_head": request["expected_head"],
        "observed_head": head,
        "index_clean_before_staging": True,
        "staged_paths_before": staged_paths,
        "authorized_file_hashes": file_hashes,
        "file_set_hash": request["file_set_hash"],
        "git_performed": True,
        "commit_created": False,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "worker_invoked": True,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _stage_authorized_files(*, request: dict[str, Any], root: Path, pre_state: dict[str, Any]) -> dict[str, Any]:
    paths = [entry["path"] for entry in request["file_set"]]
    if not paths:
        raise FailClosedRuntimeError("governed Git commit requires authorized paths")
    _run_git(root, ["add", "--", *paths])
    staged_paths = _staged_paths(root)
    if staged_paths != sorted(paths):
        raise FailClosedRuntimeError("governed Git commit failed closed: staged path mismatch")
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": GIT_COMMIT_WORKER_STAGED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "candidate_hash": request["candidate_hash"],
        "parent_head": pre_state["observed_head"],
        "staged_paths": staged_paths,
        "staged_paths_hash": replay_hash(staged_paths),
        "file_set_hash": request["file_set_hash"],
        "staged_file_count": len(staged_paths),
        "git_performed": True,
        "commit_created": False,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "worker_invoked": True,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _create_commit(*, request: dict[str, Any], root: Path, staging: dict[str, Any]) -> dict[str, Any]:
    message = request["commit_message"]
    author = request["author"]
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": author["name"],
            "GIT_AUTHOR_EMAIL": author["email"],
            "GIT_COMMITTER_NAME": author["name"],
            "GIT_COMMITTER_EMAIL": author["email"],
        }
    )
    args = ["commit", "--no-gpg-sign", "-m", message["subject"]]
    if message.get("body"):
        args.extend(["-m", message["body"]])
    completed = _run_git(root, args, env=env)
    commit_hash = _git_stdout(root, ["rev-parse", "HEAD"])
    if commit_hash == request["expected_head"]:
        raise FailClosedRuntimeError("governed Git commit failed closed: commit did not advance HEAD")
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": GIT_COMMIT_WORKER_EXECUTED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "candidate_id": request["candidate_id"],
        "candidate_hash": request["candidate_hash"],
        "repository_id": request["repository_id"],
        "branch_name": request["branch_name"],
        "parent_head": request["expected_head"],
        "commit_hash": commit_hash,
        "post_commit_head": commit_hash,
        "file_set_hash": request["file_set_hash"],
        "staged_paths_hash": staging["staged_paths_hash"],
        "commit_message_hash": request["commit_message_hash"],
        "author_hash": request["author_hash"],
        "git_stdout_hash": replay_hash(completed.stdout or ""),
        "git_stderr_hash": replay_hash(completed.stderr or ""),
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
        "worker_invoked": True,
        "authority": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_file_set(*, root: Path, file_set: list[dict[str, Any]]) -> list[dict[str, str]]:
    observed: list[dict[str, str]] = []
    for entry in file_set:
        path = _validate_relative_path(entry.get("path"))
        target = (root / path).resolve()
        if not _is_relative_to(target, root):
            raise FailClosedRuntimeError("governed Git commit failed closed: path escapes repository")
        if not target.is_file():
            raise FailClosedRuntimeError("governed Git commit failed closed: authorized file missing")
        content = target.read_text(encoding="utf-8")
        if "\x00" in content:
            raise FailClosedRuntimeError("governed Git commit failed closed: binary file not allowed")
        content_hash = replay_hash(content)
        if content_hash != entry.get("content_hash"):
            raise FailClosedRuntimeError("governed Git commit failed closed: authorized file hash mismatch")
        tracked = _is_tracked(root, path)
        change_type = entry.get("change_type")
        if change_type == "ADD_TEXT_FILE" and tracked:
            raise FailClosedRuntimeError("governed Git commit failed closed: add target already tracked")
        if change_type == "REPLACE_TEXT_FILE" and not tracked:
            raise FailClosedRuntimeError("governed Git commit failed closed: replace target is not tracked")
        observed.append({"path": path, "change_type": change_type, "content_hash": content_hash})
    return observed


def _validate_git_commit_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("Git commit authorization record must be authorized")
    if record["worker_id"] != GIT_COMMIT_WORKER_ID:
        raise FailClosedRuntimeError("Git commit authorization Worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_GIT_COMMIT_SCOPE:
        raise FailClosedRuntimeError("Git commit authorization scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": AUTHORIZED_GIT_COMMIT_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "candidate_id": request["candidate_id"],
        "candidate_hash": request["candidate_hash"],
        "repository_id": request["repository_id"],
        "branch_name": request["branch_name"],
        "expected_head": request["expected_head"],
        "file_set_hash": request["file_set_hash"],
        "commit_message_hash": request["commit_message_hash"],
        "author_hash": request["author_hash"],
        "validation_artifact_hash": request["validation_artifact_hash"],
        "request_timestamp": request["request_timestamp"],
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
        "worker_self_authorized": False,
        "worker_invoked": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": FAILED_CLOSED,
        "request_id": _safe_field(authorized_request, "request_id", "INVALID_REQUEST"),
        "request_hash": _safe_field(authorized_request, "request_hash", FAILED_CLOSED),
        "authorization_id": _safe_field(authorized_request, "authorization_id", "INVALID_AUTHORIZATION"),
        "authorization_hash": _safe_field(authorized_request, "authorization_hash", FAILED_CLOSED),
        "proposal_reference": _safe_object_field(authorized_request, "proposal_reference"),
        "worker_id": _safe_field(authorized_request, "worker_id", "INVALID_WORKER"),
        "authorized_scope": _safe_field(authorized_request, "authorized_scope", "INVALID_SCOPE"),
        "operation": _safe_field(authorized_request, "operation", "INVALID_OPERATION"),
        "candidate_id": _safe_field(authorized_request, "candidate_id", "INVALID_CANDIDATE"),
        "candidate_hash": _safe_field(authorized_request, "candidate_hash", FAILED_CLOSED),
        "repository_id": _safe_field(authorized_request, "repository_id", "INVALID_REPOSITORY"),
        "branch_name": _safe_field(authorized_request, "branch_name", "INVALID_BRANCH"),
        "expected_head": _safe_field(authorized_request, "expected_head", FAILED_CLOSED),
        "file_set_hash": _safe_field(authorized_request, "file_set_hash", FAILED_CLOSED),
        "commit_message_hash": _safe_field(authorized_request, "commit_message_hash", FAILED_CLOSED),
        "author_hash": _safe_field(authorized_request, "author_hash", FAILED_CLOSED),
        "validation_artifact_hash": _safe_field(authorized_request, "validation_artifact_hash", FAILED_CLOSED),
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
        "worker_self_authorized": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": GIT_COMMIT_WORKER_VERSION,
        "event_type": GIT_COMMIT_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "authorization_id": failure["authorization_id"],
        "candidate_id": failure["candidate_id"],
        "candidate_hash": failure["candidate_hash"],
        "repository_id": failure["repository_id"],
        "branch_name": failure["branch_name"],
        "parent_head": failure["expected_head"],
        "commit_hash": None,
        "post_commit_head": None,
        "file_set_hash": failure["file_set_hash"],
        "staged_paths_hash": replay_hash([]),
        "commit_message_hash": failure["commit_message_hash"],
        "author_hash": failure["author_hash"],
        "git_performed": False,
        "commit_created": False,
        "commit_count": 0,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request_artifact: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "authorized_git_commit_request": deepcopy(request_artifact),
        "git_commit_worker_execution": deepcopy(result),
    }
    capture["git_commit_worker_capture_hash"] = replay_hash(capture)
    return capture


def _resolve_git_repository(repository_root: str | Path) -> Path:
    root = Path(repository_root).resolve()
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("governed Git commit repository root missing")
    observed = _git_stdout(root, ["rev-parse", "--show-toplevel"])
    observed_path = Path(observed).resolve()
    if observed_path != root:
        raise FailClosedRuntimeError("governed Git commit repository root mismatch")
    return root


def _staged_paths(root: Path) -> list[str]:
    output = _git_stdout(root, ["diff", "--cached", "--name-only"])
    return sorted(line.strip() for line in output.splitlines() if line.strip())


def _is_tracked(root: Path, path: str) -> bool:
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", path],
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return completed.returncode == 0


def _git_stdout(root: Path, args: list[str]) -> str:
    return (_run_git(root, args).stdout or "").strip()


def _run_git(root: Path, args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    _validate_git_args(args)
    completed = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
        check=False,
        env=env,
    )
    if completed.returncode != 0:
        raise FailClosedRuntimeError("governed Git commit failed closed: Git command failed")
    return completed


def _validate_git_args(args: list[str]) -> None:
    if not args:
        raise FailClosedRuntimeError("governed Git commit requires Git operation")
    allowed = {"rev-parse", "diff", "ls-files", "add", "commit"}
    operation = args[0]
    if operation not in allowed:
        raise FailClosedRuntimeError("governed Git commit failed closed: Git operation not allowlisted")
    prohibited = {
        "push",
        "fetch",
        "pull",
        "clone",
        "remote",
        "branch",
        "checkout",
        "switch",
        "merge",
        "rebase",
        "reset",
        "revert",
        "tag",
        "stash",
        "cherry-pick",
        "clean",
        "submodule",
        "worktree",
        "config",
    }
    if any(token in prohibited for token in args):
        raise FailClosedRuntimeError("governed Git commit failed closed: prohibited Git operation requested")


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "path")
    if "\n" in path_text or "\x00" in path_text:
        raise FailClosedRuntimeError("governed Git commit path invalid")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("governed Git commit path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("governed Git commit path must not contain traversal")
    return path.as_posix()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only Git commit Worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("Git commit Worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "Git commit Worker artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
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
        raise FailClosedRuntimeError("Git commit Worker replay hash mismatch")


def _reject_forbidden_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_REQUEST_FIELDS.intersection(value):
            raise FailClosedRuntimeError(f"{label} contains forbidden field")
        for nested in value.values():
            _reject_forbidden_fields(nested, label)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_fields(nested, label)


def _require_json_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    replay_hash(value)
    return deepcopy(value)


def _require_json_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON list")
    replay_hash(value)
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _safe_field(value: Any, field_name: str, default: str) -> str:
    if isinstance(value, dict):
        field = value.get(field_name)
        if isinstance(field, str) and field.strip():
            return field
    return default


def _safe_object_field(value: Any, field_name: str) -> dict[str, Any]:
    if isinstance(value, dict) and isinstance(value.get(field_name), dict):
        return deepcopy(value[field_name])
    return {}


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "Git commit Worker failed closed"
