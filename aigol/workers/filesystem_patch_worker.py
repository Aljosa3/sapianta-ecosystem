"""Governed filesystem Worker for one context-bound plaintext patch."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


FILESYSTEM_PATCH_WORKER_VERSION = "G9_04_SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTATION_V1"
FILESYSTEM_PATCH_WORKER_ID = "FILESYSTEM_SINGLE_FILE_CONTEXT_PATCH_WORKER"
AUTHORIZED_PATCH_REQUEST_TYPE = "AUTHORIZED_SINGLE_FILE_CONTEXT_PATCH_REQUEST_V1"
AUTHORIZED_PATCH_SCOPE = "FILESYSTEM_SINGLE_FILE_CONTEXT_PATCH"
OPERATION_APPLY_CONTEXT_PATCH = "APPLY_SINGLE_CONTEXT_BOUND_PATCH"
AUTHORIZED_PATCH_REQUEST_CREATED = "AUTHORIZED_PATCH_REQUEST_CREATED"
FILESYSTEM_PATCH_WORKER_EXECUTED = "FILESYSTEM_PATCH_WORKER_EXECUTED"
FILESYSTEM_PATCH_WORKER_FAILED = "FILESYSTEM_PATCH_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorized_patch_request", "filesystem_patch_worker_execution")
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
        "regex",
        "glob",
        "search_replace",
    }
)


def create_authorized_patch_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    file_path: str,
    pre_content_hash: str,
    old_text: str,
    new_text: str,
    expected_post_content_hash: str,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the bounded request accepted by the single-file patch Worker."""

    record = _validate_patch_authorization(authorization_record)
    old = _validate_plaintext(old_text, "old_text")
    new = _validate_plaintext(new_text, "new_text")
    request = {
        "request_type": AUTHORIZED_PATCH_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "proposal_reference": deepcopy(proposal_reference),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_APPLY_CONTEXT_PATCH,
        "file_path": _validate_relative_path(file_path),
        "pre_content_hash": _require_string(pre_content_hash, "pre_content_hash"),
        "old_text": old,
        "old_text_hash": replay_hash(old),
        "new_text": new,
        "new_text_hash": replay_hash(new),
        "occurrence_policy": "exactly_once",
        "expected_post_content_hash": _require_string(
            expected_post_content_hash,
            "expected_post_content_hash",
        ),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "authorization_hash": record["authorization_hash"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "canonical_artifact_model": "complete_resulting_file",
        "patch_is_intent_only": True,
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
        "multi_file_mutation": False,
        "arbitrary_search_replace": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_patch_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a patch request without executing it."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized patch request is required")
    _reject_forbidden_fields(request, "authorized patch request")
    if request.get("request_type") != AUTHORIZED_PATCH_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized patch request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    if request.get("worker_id") != FILESYSTEM_PATCH_WORKER_ID:
        raise FailClosedRuntimeError("authorized patch request worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_PATCH_SCOPE:
        raise FailClosedRuntimeError("authorized patch request scope mismatch")
    if request.get("operation") != OPERATION_APPLY_CONTEXT_PATCH:
        raise FailClosedRuntimeError("authorized patch request operation is invalid")
    _validate_relative_path(request.get("file_path"))
    _require_string(request.get("pre_content_hash"), "pre_content_hash")
    old = _validate_plaintext(request.get("old_text"), "old_text")
    new = _validate_plaintext(request.get("new_text"), "new_text")
    if request.get("old_text_hash") != replay_hash(old):
        raise FailClosedRuntimeError("authorized patch request old text hash mismatch")
    if request.get("new_text_hash") != replay_hash(new):
        raise FailClosedRuntimeError("authorized patch request new text hash mismatch")
    if request.get("occurrence_policy") != "exactly_once":
        raise FailClosedRuntimeError("authorized patch request occurrence policy mismatch")
    _require_string(request.get("expected_post_content_hash"), "expected_post_content_hash")
    _require_string(request.get("request_timestamp"), "request_timestamp")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_string(request.get("replay_reference"), "replay_reference")
    if request.get("canonical_artifact_model") != "complete_resulting_file":
        raise FailClosedRuntimeError("authorized patch request must preserve complete artifact model")
    if request.get("patch_is_intent_only") is not True:
        raise FailClosedRuntimeError("authorized patch request must keep patch intent-only")
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
        "multi_file_mutation",
        "arbitrary_search_replace",
        "git_performed",
        "commit_created",
        "deployment_performed",
    ):
        _require_false(request.get(field), field)
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized patch request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorized patch request hash mismatch")
    if authorization_record is not None:
        record = _validate_patch_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized patch request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized patch request authorization hash mismatch")
    return deepcopy(request)


def execute_filesystem_patch_request(
    *,
    authorized_request: dict[str, Any],
    base_dir: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Apply exactly one context-bound patch and record Worker replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_patch_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        target = _resolve_existing_target(base_dir=Path(base_dir), file_path=request["file_path"])
        old_content = _read_plaintext(target)
        old_hash = replay_hash(old_content)
        if old_hash != request["pre_content_hash"]:
            raise FailClosedRuntimeError("filesystem patch worker target hash conflict")
        occurrences = old_content.count(request["old_text"])
        if occurrences == 0:
            raise FailClosedRuntimeError("filesystem patch worker old text missing")
        if occurrences > 1:
            raise FailClosedRuntimeError("filesystem patch worker old text ambiguous")
        resulting_content = old_content.replace(request["old_text"], request["new_text"], 1)
        resulting_hash = replay_hash(resulting_content)
        if resulting_hash != request["expected_post_content_hash"]:
            raise FailClosedRuntimeError("filesystem patch worker constructed post hash mismatch")
        target.write_text(resulting_content, encoding="utf-8")
        final_content = _read_plaintext(target)
        final_hash = replay_hash(final_content)
        if final_hash != request["expected_post_content_hash"]:
            raise FailClosedRuntimeError("filesystem patch worker post-write hash mismatch")
        result = _execution_result(
            request=request,
            target=target,
            pre_content_hash=old_hash,
            post_content_hash=final_hash,
            complete_resulting_content=final_content,
            status=FILESYSTEM_PATCH_WORKER_EXECUTED,
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


def reconstruct_filesystem_patch_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the Worker-side patch operation."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("filesystem patch worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("filesystem patch worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "filesystem patch worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("filesystem patch worker replay request hash mismatch")
    if result_artifact.get("request_artifact_hash") != request_artifact.get("artifact_hash"):
        raise FailClosedRuntimeError("filesystem patch worker replay request artifact mismatch")
    return {
        "authorization_id": request_artifact["authorization_id"],
        "proposal_reference": deepcopy(request_artifact["proposal_reference"]),
        "request_id": request_artifact["request_id"],
        "worker_id": request_artifact["worker_id"],
        "authorized_scope": request_artifact["authorized_scope"],
        "operation": request_artifact["operation"],
        "file_path": request_artifact["file_path"],
        "pre_content_hash": result_artifact["pre_content_hash"],
        "post_content_hash": result_artifact["post_content_hash"],
        "complete_resulting_content_hash": result_artifact["complete_resulting_content_hash"],
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


def _validate_patch_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("authorization record must be authorized")
    if record["worker_id"] != FILESYSTEM_PATCH_WORKER_ID:
        raise FailClosedRuntimeError("authorization record worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_PATCH_SCOPE:
        raise FailClosedRuntimeError("authorization record scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": FILESYSTEM_PATCH_WORKER_VERSION,
        "event_type": AUTHORIZED_PATCH_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "file_path": request["file_path"],
        "pre_content_hash": request["pre_content_hash"],
        "old_text_hash": request["old_text_hash"],
        "new_text_hash": request["new_text_hash"],
        "expected_post_content_hash": request["expected_post_content_hash"],
        "canonical_artifact_model": request["canonical_artifact_model"],
        "patch_is_intent_only": request["patch_is_intent_only"],
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
    pre_content_hash: str,
    post_content_hash: str,
    complete_resulting_content: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    request_artifact = _request_replay_artifact(request)
    artifact = {
        "runtime_version": FILESYSTEM_PATCH_WORKER_VERSION,
        "event_type": status,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_artifact_hash": request_artifact["artifact_hash"],
        "authorization_id": request["authorization_id"],
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": OPERATION_APPLY_CONTEXT_PATCH,
        "file_path": request["file_path"],
        "pre_content_hash": pre_content_hash,
        "old_text_hash": request["old_text_hash"],
        "new_text_hash": request["new_text_hash"],
        "post_content_hash": post_content_hash,
        "complete_resulting_content": complete_resulting_content,
        "complete_resulting_content_hash": replay_hash(complete_resulting_content),
        "canonical_execution_artifact": "complete_resulting_file",
        "patch_persisted_as_execution_artifact": False,
        "execution_status": "SUCCEEDED",
        "execution_result": {
            "patched": True,
            "path": str(target),
            "pre_content_hash": pre_content_hash,
            "post_content_hash": post_content_hash,
            "complete_resulting_content_hash": replay_hash(complete_resulting_content),
        },
        "worker_invoked": True,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "multi_file_mutation": False,
        "arbitrary_search_replace": False,
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
        "runtime_version": FILESYSTEM_PATCH_WORKER_VERSION,
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
        "pre_content_hash": _safe_field(authorized_request, "pre_content_hash", FAILED_CLOSED),
        "old_text_hash": _safe_field(authorized_request, "old_text_hash", FAILED_CLOSED),
        "new_text_hash": _safe_field(authorized_request, "new_text_hash", FAILED_CLOSED),
        "expected_post_content_hash": _safe_field(authorized_request, "expected_post_content_hash", FAILED_CLOSED),
        "request_timestamp": _safe_field(authorized_request, "request_timestamp", "INVALID_TIMESTAMP"),
        "canonical_artifact_model": "complete_resulting_file",
        "patch_is_intent_only": True,
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
        "runtime_version": FILESYSTEM_PATCH_WORKER_VERSION,
        "event_type": FILESYSTEM_PATCH_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "request_artifact_hash": failure["artifact_hash"],
        "authorization_id": failure["authorization_id"],
        "worker_id": failure["worker_id"],
        "authorized_scope": failure["authorized_scope"],
        "operation": failure["operation"],
        "file_path": failure["file_path"],
        "pre_content_hash": FAILED_CLOSED,
        "post_content_hash": FAILED_CLOSED,
        "complete_resulting_content_hash": FAILED_CLOSED,
        "execution_status": FAILED_CLOSED,
        "execution_result": {
            "patched": False,
            "path": None,
            "pre_content_hash": FAILED_CLOSED,
            "post_content_hash": FAILED_CLOSED,
        },
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "multi_file_mutation": False,
        "arbitrary_search_replace": False,
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
        "authorized_patch_request": deepcopy(request_artifact),
        "filesystem_patch_worker_execution": deepcopy(result),
    }
    capture["filesystem_patch_worker_capture_hash"] = replay_hash(capture)
    return capture


def _resolve_existing_target(*, base_dir: Path, file_path: str) -> Path:
    if not base_dir.exists() or not base_dir.is_dir():
        raise FailClosedRuntimeError("filesystem patch worker base directory is invalid")
    relative_path = Path(_validate_relative_path(file_path))
    target = (base_dir / relative_path).resolve()
    base_resolved = base_dir.resolve()
    try:
        target.relative_to(base_resolved)
    except ValueError as exc:
        raise FailClosedRuntimeError("filesystem patch worker target escaped base directory") from exc
    if target.is_symlink() or not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("filesystem patch worker target must be an existing regular file")
    return target


def _validate_relative_path(value: Any) -> str:
    path_text = _require_string(value, "file_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("file_path must be a relative path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("file_path must not contain traversal")
    return path.as_posix()


def _validate_plaintext(value: Any, field_name: str) -> str:
    content = _require_string(value, field_name)
    content.encode("utf-8")
    if "\x00" in content:
        raise FailClosedRuntimeError(f"{field_name} must be plaintext")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError(f"{field_name} is too large")
    return content


def _read_plaintext(target: Path) -> str:
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("filesystem patch worker target is not UTF-8 plaintext") from exc
    if "\x00" in content:
        raise FailClosedRuntimeError("filesystem patch worker target is not plaintext")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("filesystem patch worker target is too large")
    return content


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only patch worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("filesystem patch worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "filesystem patch worker artifact")
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
        raise FailClosedRuntimeError("filesystem patch worker replay hash mismatch")


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
    return "filesystem patch worker failed closed"
