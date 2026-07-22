"""Governed filesystem Worker for replacing one existing plaintext file."""

from __future__ import annotations

from base64 import b64decode
from copy import deepcopy
from hashlib import sha256
import os
from pathlib import Path
import stat
from subprocess import run as run_process
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.authorization.authorization_runtime import CANONICAL_AUTHORIZATION_ACTOR
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


FILESYSTEM_REPLACE_WORKER_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
FILESYSTEM_REPLACE_WORKER_ID = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
AUTHORIZED_REPLACE_REQUEST_TYPE = "AUTHORIZED_REPLACE_EXISTING_TEXT_FILE_REQUEST_V1"
AUTHORIZED_REPLACE_SCOPE = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE"
OPERATION_REPLACE_EXISTING_TEXT_FILE = "REPLACE_EXISTING_TEXT_FILE"
AUTHORIZED_REPLACE_REQUEST_CREATED = "AUTHORIZED_REPLACE_REQUEST_CREATED"
FILESYSTEM_REPLACE_WORKER_EXECUTED = "FILESYSTEM_REPLACE_WORKER_EXECUTED"
FILESYSTEM_REPLACE_WORKER_FAILED = "FILESYSTEM_REPLACE_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorized_replace_request", "filesystem_replace_worker_execution")
HARDENED_REPLACE_VERSION = "G31_24G_R04_R04_R02_EXISTING_REPLACE_HARDENED_V2"
AUTHENTICATED_REPLACE_REQUEST_TYPE_V2 = "AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2"
V2_EVENT_KEYS = ("request", "consumption", "journal", "started", "atomic", "result", "rollback", "recovery", "completion", "termination")

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
    }
)


def create_authorized_replace_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    file_path: str,
    expected_content_hash: str,
    replacement_content: str,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the bounded request accepted by the replace-existing-file Worker."""

    record = _validate_replace_authorization(authorization_record)
    path = _validate_relative_path(file_path)
    content = _validate_plaintext(replacement_content)
    replacement_hash = replay_hash(content)
    request = {
        "request_type": AUTHORIZED_REPLACE_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "proposal_reference": deepcopy(proposal_reference),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_REPLACE_EXISTING_TEXT_FILE,
        "file_path": path,
        "expected_content_hash": _require_string(expected_content_hash, "expected_content_hash"),
        "replacement_content": content,
        "replacement_content_hash": replacement_hash,
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
        "multi_step_execution": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_replace_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a replace request without executing it."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized replace request is required")
    _reject_forbidden_fields(request, "authorized replace request")
    if request.get("request_type") != AUTHORIZED_REPLACE_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized replace request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    if request.get("worker_id") != FILESYSTEM_REPLACE_WORKER_ID:
        raise FailClosedRuntimeError("authorized replace request worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_REPLACE_SCOPE:
        raise FailClosedRuntimeError("authorized replace request scope mismatch")
    if request.get("operation") != OPERATION_REPLACE_EXISTING_TEXT_FILE:
        raise FailClosedRuntimeError("authorized replace request operation is invalid")
    _validate_relative_path(request.get("file_path"))
    _require_string(request.get("expected_content_hash"), "expected_content_hash")
    content = _validate_plaintext(request.get("replacement_content"))
    if request.get("replacement_content_hash") != replay_hash(content):
        raise FailClosedRuntimeError("authorized replace request replacement hash mismatch")
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
        "multi_step_execution",
        "git_performed",
        "commit_created",
        "deployment_performed",
    ):
        _require_false(request.get(field), field)
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized replace request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorized replace request hash mismatch")
    if authorization_record is not None:
        record = _validate_replace_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized replace request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized replace request authorization hash mismatch")
    return deepcopy(request)


def execute_filesystem_replace_request(
    *,
    authorized_request: dict[str, Any],
    base_dir: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Replace exactly one existing plaintext file and record Worker replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_replace_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        target = _resolve_existing_target(base_dir=Path(base_dir), file_path=request["file_path"])
        old_content = target.read_text(encoding="utf-8")
        if "\x00" in old_content:
            raise FailClosedRuntimeError("filesystem replace worker target is not plaintext")
        old_hash = replay_hash(old_content)
        if old_hash != request["expected_content_hash"]:
            raise FailClosedRuntimeError("filesystem replace worker target hash conflict")
        target.write_text(request["replacement_content"], encoding="utf-8")
        new_content = target.read_text(encoding="utf-8")
        new_hash = replay_hash(new_content)
        if new_hash != request["replacement_content_hash"]:
            raise FailClosedRuntimeError("filesystem replace worker post-write hash mismatch")
        result = _execution_result(
            request=request,
            target=target,
            old_content_hash=old_hash,
            new_content_hash=new_hash,
            status=FILESYSTEM_REPLACE_WORKER_EXECUTED,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(failure, result)


def reconstruct_filesystem_replace_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the Worker-side replace operation."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("filesystem replace worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("filesystem replace worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "filesystem replace worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("filesystem replace worker replay request hash mismatch")
    if result_artifact.get("request_artifact_hash") != request_artifact.get("artifact_hash"):
        raise FailClosedRuntimeError("filesystem replace worker replay request artifact mismatch")
    return {
        "authorization_id": request_artifact["authorization_id"],
        "proposal_reference": deepcopy(request_artifact["proposal_reference"]),
        "request_id": request_artifact["request_id"],
        "worker_id": request_artifact["worker_id"],
        "authorized_scope": request_artifact["authorized_scope"],
        "operation": request_artifact["operation"],
        "file_path": request_artifact["file_path"],
        "old_content_hash": result_artifact["old_content_hash"],
        "new_content_hash": result_artifact["new_content_hash"],
        "execution_status": result_artifact["execution_status"],
        "execution_result": deepcopy(result_artifact["execution_result"]),
        "worker_invoked": result_artifact["worker_invoked"],
        "dispatch_performed": result_artifact["dispatch_performed"],
        "orchestration_performed": result_artifact["orchestration_performed"],
        "multi_step_execution": result_artifact["multi_step_execution"],
        "authority": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def g31_replace_destinations(session_root: str | Path, authorization_hash: str,
                             repository_root: str | Path, target_path: str) -> dict[str, str]:
    """Return the sole deterministic lifecycle and same-directory temporary paths."""
    identity = _require_string(authorization_hash, "authorization_hash"); digest = identity.removeprefix("sha256:")
    if identity != "sha256:" + digest or len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise FailClosedRuntimeError("hardened replace authorization hash is not canonical")
    root = Path(session_root).resolve()
    lifecycle = root / "G31_EXISTING_FILE_REPLACE_V2" / digest
    target = Path(repository_root).resolve() / _validate_relative_path(target_path)
    values = {key: str(lifecycle / f"{index:03d}_{key}.json")
              for index, key in enumerate(V2_EVENT_KEYS)}
    values["temporary_file"] = str(target.parent / f".aigol-{digest}.replace.tmp")
    values["restore_temporary_file"] = str(target.parent / f".aigol-{digest}.restore.tmp")
    return values
def validate_authenticated_replace_request_v2(request: dict[str, Any]) -> dict[str, Any]:
    """Validate the exact actor-bound V2 request without changing a repository."""
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authenticated replace request is required")
    value = deepcopy(request); actual = value.pop("request_hash", None)
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("authenticated replace request hash mismatch")
    record = _validate_replace_authorization(request.get("authorization_record"))
    required = ("request_id", "authorization_id", "authorization_hash", "authorization_replay_reference", "authorization_replay_hash", "actor_replay_binding_hash", "r02_authorization_binding_hash",
                "candidate_id", "candidate_hash", "candidate_replay_hash", "candidate_provenance_binding_hash", "mutation_decision_id", "mutation_decision_hash", "mutation_decision_outcome", "mutation_decision_scope", "mutation_decision_actor", "mutation_decision_replay_hash",
                "session_id", "session_root", "repository_identity", "repository_root", "repository_grounding_hash", "manifest_hash", "target_path", "preimage_sha256", "postimage_sha256", "source_content_hash", "replacement_content_hash", "preimage_bytes_b64", "replacement_bytes_b64", "source_mode", "replacement_mode")
    if any(not isinstance(request.get(field), str) or not request[field] for field in required):
        raise FailClosedRuntimeError("authenticated replace request lineage is incomplete")
    try:
        source = b64decode(request["preimage_bytes_b64"], validate=True)
        replacement = b64decode(request["replacement_bytes_b64"], validate=True)
        source_text, replacement_text = source.decode("utf-8"), replacement.decode("utf-8")
    except Exception as exc:
        raise FailClosedRuntimeError("authenticated replace request bytes are invalid") from exc
    if not all((request.get("request_type") == AUTHENTICATED_REPLACE_REQUEST_TYPE_V2,
                request.get("runtime_version") == HARDENED_REPLACE_VERSION,
                request.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR,
                request.get("authorization_record") == record,
                request.get("authorization_id") == record["authorization_id"],
                request.get("authorization_hash") == record["authorization_hash"],
                request.get("authorization_status") == record["authorization_status"],
                request.get("authorization_scope") == record["authorization_scope"],
                request.get("worker_id") == record["worker_id"], record["proposal_id"] == request.get("candidate_id"),
                request.get("mutation_decision_outcome") == "APPROVED",
                request.get("mutation_decision_scope") == "EXISTING_FILE_REPLACE_ONLY",
                request.get("operation") == "REPLACE_CONTENT",
                request.get("worker_operation") == OPERATION_REPLACE_EXISTING_TEXT_FILE,
                request["preimage_sha256"] == "sha256:" + sha256(source).hexdigest(),
                request["postimage_sha256"] == "sha256:" + sha256(replacement).hexdigest(),
                request["source_content_hash"] == replay_hash(source_text),
                request["replacement_content_hash"] == replay_hash(replacement_text),
                len(replacement) <= 64 * 1024, "\x00" not in source_text, "\x00" not in replacement_text,
                request.get("destinations") == g31_replace_destinations(
                    request["session_root"], record["authorization_hash"],
                    request["repository_root"], request["target_path"]),
                _mode(request["source_mode"]) >= 0, _mode(request["replacement_mode"]) >= 0,
                request.get("authorization_consumed") is False,
                request.get("replace_request_created") is True, request.get("worker_invoked") is False,
                request.get("provider_invoked") is False, request.get("command_executed") is False,
                request.get("repository_mutated") is False, request.get("main_repository_mutated") is False,
                request.get("replay_visible") is True)):
        raise FailClosedRuntimeError("authenticated replace request identity mismatch")
    root = Path(request["session_root"]).resolve()
    if root.name != request["session_id"] or str(root) != request["session_root"]:
        raise FailClosedRuntimeError("authenticated replace request session mismatch")
    return deepcopy(request)
def reconstruct_authenticated_replace_replay_v2(request: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct the exclusive V2 lifecycle by predecessor hashes, including recovery."""
    request = validate_authenticated_replace_request_v2(request)
    lifecycle = Path(request["destinations"]["request"]).parent
    allowed = {Path(request["destinations"][key]).name for key in V2_EVENT_KEYS}
    if lifecycle.exists() and any(item.name not in allowed for item in lifecycle.iterdir()):
        raise FailClosedRuntimeError("hardened replace Replay contains an unexpected artifact")
    wrappers = []
    for key in V2_EVENT_KEYS:
        path = Path(request["destinations"][key])
        if path.exists():
            wrapper = load_json(path); expected = deepcopy(wrapper); actual = expected.pop("replay_hash", None)
            artifact = wrapper.get("artifact") or {}; artifact_value = deepcopy(artifact)
            artifact_hash = artifact_value.pop("artifact_hash", None)
            if not all((actual == replay_hash(expected), artifact_hash == replay_hash(artifact_value),
                        wrapper.get("event_key") == key, artifact.get("request_hash") == request["request_hash"])):
                raise FailClosedRuntimeError("hardened replace Replay hash or identity mismatch")
            wrappers.append(wrapper)
    if not wrappers:
        raise FailClosedRuntimeError("hardened replace Replay is unavailable")
    ordered, previous = [], None
    remaining = list(wrappers)
    while remaining:
        matches = [item for item in remaining if item.get("previous_replay_hash") == previous]
        if len(matches) != 1:
            raise FailClosedRuntimeError("hardened replace Replay is reordered, duplicated, or branched")
        current = matches[0]; ordered.append(current); remaining.remove(current); previous = current["replay_hash"]
    latest = ordered[-1]["artifact"]
    return {"request_id": request["request_id"], "request_hash": request["request_hash"],
            "request_replay_reference": str(lifecycle),
            "authorization_id": request["authorization_id"],
            "event_keys": [item["event_key"] for item in ordered], "latest_event": latest["event_type"],
            "latest_artifact": deepcopy(latest), "replay_artifact_count": len(ordered),
            "replay_hash": replay_hash(ordered), "last_wrapper_hash": ordered[-1]["replay_hash"]}
def record_authenticated_replace_request_v2(request: dict[str, Any]) -> dict[str, Any]:
    """Persist and reconstruct only the authenticated request-stage Replay event."""
    request = validate_authenticated_replace_request_v2(request)
    lifecycle = Path(request["destinations"]["request"]).parent
    if lifecycle.exists() and any(lifecycle.iterdir()):
        raise FailClosedRuntimeError(
            "authenticated replace request Replay already exists or conflicts"
        )
    _persist_v2_event(request, "request", "REQUEST_VALIDATED", {}, None)
    reconstruction = reconstruct_authenticated_replace_replay_v2(request)
    if not all((
        reconstruction.get("request_id") == request["request_id"],
        reconstruction.get("request_hash") == request["request_hash"],
        reconstruction.get("authorization_id") == request["authorization_id"],
        reconstruction.get("event_keys") == ["request"],
        reconstruction.get("latest_event") == "REQUEST_VALIDATED",
        reconstruction.get("replay_artifact_count") == 1,
    )):
        raise FailClosedRuntimeError(
            "authenticated replace request Replay reconstruction mismatch"
        )
    return reconstruction
def _execute_authenticated_replace_v2(request: dict[str, Any]) -> dict[str, Any]:
    """Execute one authenticated, consumed, journaled, atomic existing-file replacement."""
    request = validate_authenticated_replace_request_v2(request)
    if Path(request["destinations"]["consumption"]).exists():
        raise FailClosedRuntimeError("hardened replace authorization was already consumed")
    context = _open_v2_target(request, expected="preimage", require_clean=True)
    previous = None; consumed = replaced = restored = False; temporary_name = Path(request["destinations"]["temporary_file"]).name
    try:
        previous = _persist_v2_event(request, "request", "REQUEST_VALIDATED", {}, previous)
        previous = _persist_v2_event(request, "consumption", "AUTHORIZATION_CONSUMPTION_CLAIMED",
                                     {"consumption_identity": request["authorization_hash"]}, previous)
        consumed = True
        journal = {"original_bytes_b64": request["preimage_bytes_b64"], "original_mode": request["source_mode"],
                   "device": context["stat"].st_dev, "inode": context["stat"].st_ino,
                   "link_count": context["stat"].st_nlink, "preimage_sha256": request["preimage_sha256"]}
        previous = _persist_v2_event(request, "journal", "PRE_WRITE_JOURNAL_PERSISTED", journal, previous)
        previous = _persist_v2_event(request, "started", "REPLACEMENT_STARTED", {}, previous)
        _write_v2_temporary(context, temporary_name, b64decode(request["replacement_bytes_b64"]),
                            _mode(request["replacement_mode"]), restoration=False)
        _checkpoint("before_replace"); _revalidate_v2_preimage(context, request)
        os.replace(temporary_name, context["name"], src_dir_fd=context["parent_fd"], dst_dir_fd=context["parent_fd"])
        replaced = True; _checkpoint("after_replace"); _checkpoint("directory_fsync")
        os.fsync(context["parent_fd"]); _checkpoint("after_directory_fsync")
        previous = _persist_v2_event(request, "atomic", "ATOMIC_REPLACEMENT_COMPLETED", {}, previous)
        _verify_v2_named(context, b64decode(request["replacement_bytes_b64"]), _mode(request["replacement_mode"]))
        _checkpoint("post_write_verification")
        previous = _persist_v2_event(request, "result", "POST_WRITE_VALIDATION_SUCCEEDED",
                                     {"postimage_sha256": request["postimage_sha256"],
                                      "replacement_mode": request["replacement_mode"]}, previous)
        terminal = {"execution_status": "COMPLETED", "authorization_consumed": True,
                    "repository_mutated": True, "main_repository_mutated": True,
                    "restoration_performed": False, "recovery_required": False, "mutation_terminated": False}
        _persist_v2_event(request, "completion", "MUTATION_COMPLETED", terminal, previous)
        return _v2_capture(request, terminal)
    except Exception as exc:
        _unlink_v2_if_present(context, temporary_name)
        reason = _failure_reason(exc)
        if consumed and replaced:
            restored = _atomic_restore_v2(context, request, journal)
            previous = _safe_v2_event(request, "rollback", "ATOMIC_RESTORATION_COMPLETED" if restored else "ATOMIC_RESTORATION_FAILED",
                                      {"restoration_performed": restored}, previous)
        if not consumed:
            raise FailClosedRuntimeError(reason) from exc
        terminal = {"execution_status": "TERMINATED", "authorization_consumed": True,
                    "repository_mutated": bool(replaced and not restored),
                    "main_repository_mutated": bool(replaced and not restored),
                    "restoration_performed": restored, "recovery_required": bool(replaced and not restored),
                    "mutation_terminated": True, "failure_reason": reason}
        _safe_v2_event(request, "termination", "MUTATION_TERMINATED", terminal, previous)
        return _v2_capture(request, terminal)
    finally:
        _close_v2_context(context)
def _recover_authenticated_replace_v2(request: dict[str, Any]) -> dict[str, Any]:
    """Use the durable authenticated journal to restore an interrupted V2 replacement."""
    request = validate_authenticated_replace_request_v2(request)
    replay = reconstruct_authenticated_replace_replay_v2(request)
    if "consumption" not in replay["event_keys"] or "journal" not in replay["event_keys"]:
        raise FailClosedRuntimeError("hardened replace recovery requires consumption and journal evidence")
    if "completion" in replay["event_keys"] or "recovery" in replay["event_keys"]:
        raise FailClosedRuntimeError("hardened replace recovery is not available for this terminal state")
    journal = _load_v2_event(request, "journal")["artifact"]["payload"]
    context = _open_v2_target(request, expected=None, require_clean=False)
    _unlink_v2_if_present(context, Path(request["destinations"]["temporary_file"]).name); _unlink_v2_if_present(context, Path(request["destinations"]["restore_temporary_file"]).name)
    try:
        current = _read_v2_fd(context["target_fd"])
        original = b64decode(journal["original_bytes_b64"])
        original_mode = _mode(journal["original_mode"])
        if current == original and stat.S_IMODE(context["stat"].st_mode) == original_mode:
            restored = True
        else:
            restored = _atomic_restore_v2(context, request, journal)
        latest = reconstruct_authenticated_replace_replay_v2(request)
        terminal = {"execution_status": "RECOVERED" if restored else "RECOVERY_REQUIRED",
                    "authorization_consumed": True, "repository_mutated": not restored,
                    "main_repository_mutated": not restored, "restoration_performed": restored,
                    "recovery_required": not restored, "mutation_terminated": True}
        _persist_v2_event(request, "recovery", "RECOVERY_COMPLETED" if restored else "RECOVERY_REQUIRED",
                          terminal, latest["last_wrapper_hash"])
        return _v2_capture(request, terminal)
    finally:
        _close_v2_context(context)
def _open_v2_target(request: dict[str, Any], *, expected: str | None, require_clean: bool) -> dict[str, Any]:
    root = Path(request["repository_root"])
    if not root.is_absolute() or str(root.resolve()) != str(root) or not root.is_dir():
        raise FailClosedRuntimeError("hardened replace repository root is not canonical")
    relative = Path(_validate_relative_path(request["target_path"]))
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        try:
            state = os.lstat(current)
        except OSError as exc:
            raise FailClosedRuntimeError("hardened replace path component is unavailable") from exc
        if stat.S_ISLNK(state.st_mode) or not stat.S_ISDIR(state.st_mode):
            raise FailClosedRuntimeError("hardened replace path component is not a stable directory")
        if os.path.lexists(current / ".git"):
            raise FailClosedRuntimeError("hardened replace target is inside a nested repository")
    top = run_process(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True)
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise FailClosedRuntimeError("hardened replace repository identity cannot be proved")
    if require_clean:
        status_result = run_process(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                                    cwd=root, capture_output=True, text=True)
        if status_result.returncode != 0 or status_result.stdout:
            raise FailClosedRuntimeError("hardened replace requires a clean target worktree")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    parent_fd = os.open(current, flags)
    try:
        target_fd = os.open(relative.name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
    except Exception as exc:
        os.close(parent_fd); raise FailClosedRuntimeError("hardened replace target cannot be opened without following links") from exc
    state = os.fstat(target_fd)
    named = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISREG(state.st_mode) or state.st_nlink != 1:
        os.close(target_fd); os.close(parent_fd)
        raise FailClosedRuntimeError("hardened replace target must be a single-link regular file")
    if (state.st_dev, state.st_ino, state.st_mode, state.st_nlink) != (named.st_dev, named.st_ino, named.st_mode, named.st_nlink):
        os.close(target_fd); os.close(parent_fd)
        raise FailClosedRuntimeError("hardened replace target descriptor identity mismatch")
    context = {"root": root, "parent": current, "name": relative.name, "parent_fd": parent_fd,
               "target_fd": target_fd, "stat": state}
    if expected is not None:
        data = b64decode(request["preimage_bytes_b64"] if expected == "preimage" else request["replacement_bytes_b64"])
        mode = _mode(request["source_mode"] if expected == "preimage" else request["replacement_mode"])
        observed = _read_v2_fd(target_fd)
        digest = "sha256:" + sha256(observed).hexdigest()
        wanted = request["preimage_sha256"] if expected == "preimage" else request["postimage_sha256"]
        if observed != data or digest != wanted or stat.S_IMODE(state.st_mode) != mode:
            _close_v2_context(context)
            raise FailClosedRuntimeError("hardened replace target bytes or mode drifted")
    return context
def _revalidate_v2_preimage(context: dict[str, Any], request: dict[str, Any]) -> None:
    descriptor = os.fstat(context["target_fd"])
    named = os.stat(context["name"], dir_fd=context["parent_fd"], follow_symlinks=False)
    original = context["stat"]
    identity = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_nlink, value.st_size)
    if identity(descriptor) != identity(original) or identity(named) != identity(original):
        raise FailClosedRuntimeError("hardened replace target identity drifted before atomic replace")
    observed = _read_v2_fd(context["target_fd"])
    if observed != b64decode(request["preimage_bytes_b64"]) or "sha256:" + sha256(observed).hexdigest() != request["preimage_sha256"]:
        raise FailClosedRuntimeError("hardened replace preimage drifted before atomic replace")
def _write_v2_temporary(context: dict[str, Any], name: str, data: bytes, mode: int, *, restoration: bool) -> None:
    descriptor = None
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                             mode, dir_fd=context["parent_fd"])
        if not restoration: _checkpoint("temporary_created")
        offset = 0
        while offset < len(data):
            written = os.write(descriptor, data[offset:])
            if written <= 0: raise OSError("temporary write made no progress")
            offset += written
        if not restoration: _checkpoint("temporary_written")
        os.fchmod(descriptor, mode); os.fsync(descriptor)
        if not restoration: _checkpoint("temporary_fsynced")
    except Exception:
        if descriptor is not None: os.close(descriptor)
        _unlink_v2_if_present(context, name)
        raise
    else:
        os.close(descriptor)
def _verify_v2_named(context: dict[str, Any], expected: bytes, mode: int) -> None:
    descriptor = os.open(context["name"], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                         dir_fd=context["parent_fd"])
    try:
        state = os.fstat(descriptor); observed = _read_v2_fd(descriptor)
        if not stat.S_ISREG(state.st_mode) or state.st_nlink != 1 or stat.S_IMODE(state.st_mode) != mode or observed != expected:
            raise FailClosedRuntimeError("hardened replace post-write bytes, mode, or type mismatch")
    finally:
        os.close(descriptor)
def _atomic_restore_v2(context: dict[str, Any], request: dict[str, Any], journal: dict[str, Any]) -> bool:
    name = Path(request["destinations"]["restore_temporary_file"]).name
    try:
        _verify_v2_named(context, b64decode(request["replacement_bytes_b64"]), _mode(request["replacement_mode"]))
        _write_v2_temporary(context, name, b64decode(journal["original_bytes_b64"]),
                            _mode(journal["original_mode"]), restoration=True)
        os.replace(name, context["name"], src_dir_fd=context["parent_fd"], dst_dir_fd=context["parent_fd"])
        os.fsync(context["parent_fd"])
        _verify_v2_named(context, b64decode(journal["original_bytes_b64"]), _mode(journal["original_mode"]))
        return True
    except Exception:
        _unlink_v2_if_present(context, name)
        return False
def _persist_v2_event(request: dict[str, Any], key: str, event_type: str,
                      payload: dict[str, Any], previous: str | None) -> str:
    if key not in V2_EVENT_KEYS:
        raise FailClosedRuntimeError("hardened replace Replay event is invalid")
    _checkpoint(f"replay_{key}")
    artifact = {"artifact_type": "FILESYSTEM_REPLACE_WORKER_EVENT_V2", "runtime_version": HARDENED_REPLACE_VERSION,
                "event_type": event_type, "request_hash": request["request_hash"],
                "authorization_id": request["authorization_id"], "authorization_hash": request["authorization_hash"],
                "authorization_actor": request["canonical_authorization_actor"],
                "authorization_replay_hash": request["authorization_replay_hash"],
                "candidate_hash": request["candidate_hash"], "decision_hash": request["mutation_decision_hash"],
                "repository_identity": request["repository_identity"], "repository_grounding_hash": request["repository_grounding_hash"],
                "target_path": request["target_path"], "preimage_sha256": request["preimage_sha256"],
                "postimage_sha256": request["postimage_sha256"], "source_mode": request["source_mode"],
                "replacement_mode": request["replacement_mode"], "payload": deepcopy(payload)}
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {"event_key": key, "previous_replay_hash": previous, "artifact": artifact}
    wrapper["replay_hash"] = replay_hash(wrapper)
    destination = Path(request["destinations"][key]); destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        data = (canonical_serialize(wrapper) + "\n").encode("utf-8"); offset = 0
        while offset < len(data): offset += os.write(descriptor, data[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory = os.open(destination.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try: os.fsync(directory)
    finally: os.close(directory)
    return wrapper["replay_hash"]
def _safe_v2_event(request: dict[str, Any], key: str, event_type: str,
                   payload: dict[str, Any], previous: str | None) -> str | None:
    try: return _persist_v2_event(request, key, event_type, payload, previous)
    except Exception: return previous
def _load_v2_event(request: dict[str, Any], key: str) -> dict[str, Any]:
    wrapper = load_json(Path(request["destinations"][key])); expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None); artifact = wrapper.get("artifact") or {}
    value = deepcopy(artifact); artifact_hash = value.pop("artifact_hash", None)
    if not all((actual == replay_hash(expected), artifact_hash == replay_hash(value),
                wrapper.get("event_key") == key, artifact.get("request_hash") == request["request_hash"])):
        raise FailClosedRuntimeError("hardened replace Replay artifact is invalid")
    return wrapper
def _v2_capture(request: dict[str, Any], terminal: dict[str, Any]) -> dict[str, Any]:
    capture = {"runtime_version": HARDENED_REPLACE_VERSION, "request_id": request["request_id"],
               "request_hash": request["request_hash"], "authorization_id": request["authorization_id"],
               "authorization_hash": request["authorization_hash"], **deepcopy(terminal),
               "worker_invoked": True, "provider_invoked": False, "command_executed": False,
               "git_performed": False, "replay_visible": True}
    try:
        replay = reconstruct_authenticated_replace_replay_v2(request)
        capture["replay_hash"] = replay["replay_hash"]; capture["replay_artifact_count"] = replay["replay_artifact_count"]
    except Exception:
        capture["replay_hash"] = "INCOMPLETE"; capture["replay_artifact_count"] = 0
    capture["capture_hash"] = replay_hash(capture)
    return capture
def _read_v2_fd(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET); chunks = []
    while True:
        chunk = os.read(descriptor, 64 * 1024)
        if not chunk: break
        chunks.append(chunk)
    os.lseek(descriptor, 0, os.SEEK_SET)
    return b"".join(chunks)
def _unlink_v2_if_present(context: dict[str, Any], name: str) -> None:
    try: os.unlink(name, dir_fd=context["parent_fd"])
    except FileNotFoundError: pass
def _close_v2_context(context: dict[str, Any]) -> None:
    for key in ("target_fd", "parent_fd"):
        try: os.close(context[key])
        except OSError: pass
def _mode(value: str) -> int:
    try: parsed = int(value, 0) if value.startswith("0") else int(value)
    except (TypeError, ValueError) as exc: raise FailClosedRuntimeError("hardened replace mode is invalid") from exc
    if parsed < 0 or (parsed > 0o7777 and not stat.S_ISREG(parsed)):
        raise FailClosedRuntimeError("hardened replace mode is not a regular-file mode")
    return stat.S_IMODE(parsed)
def _checkpoint(_name: str) -> None:
    """Private deterministic failure-injection seam used only by isolated tests."""


def _validate_replace_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("authorization record must be authorized")
    if record["worker_id"] != FILESYSTEM_REPLACE_WORKER_ID:
        raise FailClosedRuntimeError("authorization record worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_REPLACE_SCOPE:
        raise FailClosedRuntimeError("authorization record scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": FILESYSTEM_REPLACE_WORKER_VERSION,
        "event_type": AUTHORIZED_REPLACE_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "file_path": request["file_path"],
        "expected_content_hash": request["expected_content_hash"],
        "replacement_content_hash": request["replacement_content_hash"],
        "request_timestamp": request["request_timestamp"],
        "provider_authority": False,
        "proposal_authority": False,
        "governance_authority": False,
        "authorization_authority": False,
        "worker_self_authorized": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_result(
    *,
    request: dict[str, Any],
    target: Path,
    old_content_hash: str,
    new_content_hash: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    request_artifact = _request_replay_artifact(request)
    artifact = {
        "runtime_version": FILESYSTEM_REPLACE_WORKER_VERSION,
        "event_type": status,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_artifact_hash": request_artifact["artifact_hash"],
        "authorization_id": request["authorization_id"],
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": OPERATION_REPLACE_EXISTING_TEXT_FILE,
        "file_path": request["file_path"],
        "old_content_hash": old_content_hash,
        "new_content_hash": new_content_hash,
        "execution_status": "SUCCEEDED",
        "execution_result": {
            "replaced": True,
            "path": str(target),
            "old_content_hash": old_content_hash,
            "new_content_hash": new_content_hash,
        },
        "worker_invoked": True,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": FILESYSTEM_REPLACE_WORKER_VERSION,
        "event_type": FAILED_CLOSED,
        "request_id": _safe_field(authorized_request, "request_id", "INVALID_REQUEST"),
        "request_hash": _safe_field(authorized_request, "request_hash", FAILED_CLOSED),
        "authorization_id": _safe_field(authorized_request, "authorization_id", "INVALID_AUTHORIZATION"),
        "authorization_hash": _safe_field(authorized_request, "authorization_hash", FAILED_CLOSED),
        "proposal_reference": _safe_object_field(authorized_request, "proposal_reference"),
        "worker_id": _safe_field(authorized_request, "worker_id", "INVALID_WORKER"),
        "authorized_scope": _safe_field(authorized_request, "authorized_scope", "INVALID_SCOPE"),
        "operation": _safe_field(authorized_request, "operation", "INVALID_OPERATION"),
        "file_path": _safe_field(authorized_request, "file_path", "INVALID_FILE_PATH"),
        "expected_content_hash": _safe_field(authorized_request, "expected_content_hash", FAILED_CLOSED),
        "replacement_content_hash": _safe_field(authorized_request, "replacement_content_hash", FAILED_CLOSED),
        "request_timestamp": _safe_field(authorized_request, "request_timestamp", "INVALID_TIMESTAMP"),
        "provider_authority": False,
        "proposal_authority": False,
        "governance_authority": False,
        "authorization_authority": False,
        "worker_self_authorized": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": FILESYSTEM_REPLACE_WORKER_VERSION,
        "event_type": FILESYSTEM_REPLACE_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "request_artifact_hash": failure["artifact_hash"],
        "authorization_id": failure["authorization_id"],
        "worker_id": failure["worker_id"],
        "authorized_scope": failure["authorized_scope"],
        "operation": failure["operation"],
        "file_path": failure["file_path"],
        "old_content_hash": FAILED_CLOSED,
        "new_content_hash": FAILED_CLOSED,
        "execution_status": FAILED_CLOSED,
        "execution_result": {
            "replaced": False,
            "path": None,
            "old_content_hash": FAILED_CLOSED,
            "new_content_hash": FAILED_CLOSED,
        },
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request_artifact: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "authorized_replace_request": deepcopy(request_artifact),
        "filesystem_replace_worker_execution": deepcopy(result),
    }
    capture["filesystem_replace_worker_capture_hash"] = replay_hash(capture)
    return capture


def _resolve_existing_target(*, base_dir: Path, file_path: str) -> Path:
    if not base_dir.exists() or not base_dir.is_dir():
        raise FailClosedRuntimeError("filesystem replace worker base directory is invalid")
    relative_path = Path(_validate_relative_path(file_path))
    target = (base_dir / relative_path).resolve()
    base_resolved = base_dir.resolve()
    try:
        target.relative_to(base_resolved)
    except ValueError as exc:
        raise FailClosedRuntimeError("filesystem replace worker target escaped base directory") from exc
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("filesystem replace worker target must be an existing regular file")
    return target


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "file_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("file_path must be a relative path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("file_path must not contain traversal")
    return path.as_posix()


def _validate_plaintext(value: Any) -> str:
    content = _require_string(value, "replacement_content")
    content.encode("utf-8")
    if "\x00" in content:
        raise FailClosedRuntimeError("replacement content must be plaintext")
    if len(content.encode("utf-8")) > 64 * 1024:
        raise FailClosedRuntimeError("replacement content is too large")
    return content


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only replace worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("filesystem replace worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "filesystem replace worker artifact")
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
        raise FailClosedRuntimeError("filesystem replace worker replay hash mismatch")


def _reject_forbidden_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_REQUEST_FIELDS.intersection(value):
            raise FailClosedRuntimeError(f"{label} contains forbidden authority field")
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


def _require_false(value: Any, field_name: str) -> None:
    if value is not False:
        raise FailClosedRuntimeError(f"{field_name} must be false")


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
    return "filesystem replace worker failed closed"
