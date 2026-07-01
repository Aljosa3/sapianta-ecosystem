"""Governed validation command Worker with static allowlist execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_allowlist import (
    get_validation_command_spec,
    resolve_validation_working_directory,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


VALIDATION_COMMAND_WORKER_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
VALIDATION_COMMAND_WORKER_ID = "GOVERNED_VALIDATION_COMMAND_WORKER"
AUTHORIZED_VALIDATION_REQUEST_TYPE = "AUTHORIZED_VALIDATION_COMMAND_REQUEST_V1"
AUTHORIZED_VALIDATION_SCOPE = "RUN_ALLOWLISTED_VALIDATION_COMMAND"
OPERATION_RUN_VALIDATION_COMMAND = "RUN_VALIDATION_COMMAND"
AUTHORIZED_VALIDATION_REQUEST_CREATED = "AUTHORIZED_VALIDATION_REQUEST_CREATED"
VALIDATION_COMMAND_WORKER_EXECUTED = "VALIDATION_COMMAND_WORKER_EXECUTED"
VALIDATION_COMMAND_WORKER_FAILED = "VALIDATION_COMMAND_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorized_validation_request", "validation_command_worker_execution")

VALIDATION_PASSED = "VALIDATION_PASSED"
VALIDATION_FAILED = "VALIDATION_FAILED"
VALIDATION_TIMED_OUT = "VALIDATION_TIMED_OUT"
VALIDATION_BLOCKED = "VALIDATION_BLOCKED"

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_command",
        "shell",
        "shell_command",
        "raw_provider_output",
        "git_operation",
        "commit_request",
        "deployment_request",
        "package_install_request",
        "network_request",
        "dispatch_request",
        "orchestration_request",
        "memory_mutation",
        "replay_mutation",
    }
)


def create_authorized_validation_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    command_id: str,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the Worker-facing request for one allowlisted validation command."""

    record = _validate_validation_authorization(authorization_record)
    command_spec = get_validation_command_spec(command_id)
    request = {
        "request_type": AUTHORIZED_VALIDATION_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_RUN_VALIDATION_COMMAND,
        "command_id": command_spec["command_id"],
        "argv": deepcopy(command_spec["argv"]),
        "argv_hash": command_spec["argv_hash"],
        "command_spec_hash": command_spec["spec_hash"],
        "working_directory": command_spec["working_directory"],
        "timeout_seconds": command_spec["timeout_seconds"],
        "output_limit_bytes": command_spec["output_limit_bytes"],
        "expected_exit_code": command_spec["expected_exit_code"],
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "shell_allowed": False,
        "raw_command_string_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_validation_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a validation command request without executing it."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized validation request is required")
    _reject_forbidden_fields(request, "authorized validation request")
    if request.get("request_type") != AUTHORIZED_VALIDATION_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized validation request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    if request.get("worker_id") != VALIDATION_COMMAND_WORKER_ID:
        raise FailClosedRuntimeError("authorized validation request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_VALIDATION_SCOPE:
        raise FailClosedRuntimeError("authorized validation request scope mismatch")
    if request.get("operation") != OPERATION_RUN_VALIDATION_COMMAND:
        raise FailClosedRuntimeError("authorized validation request operation mismatch")
    command_spec = get_validation_command_spec(request.get("command_id"))
    if request.get("argv") != command_spec["argv"] or request.get("argv_hash") != command_spec["argv_hash"]:
        raise FailClosedRuntimeError("authorized validation request argv mismatch")
    if request.get("command_spec_hash") != command_spec["spec_hash"]:
        raise FailClosedRuntimeError("authorized validation request command spec mismatch")
    if request.get("working_directory") != command_spec["working_directory"]:
        raise FailClosedRuntimeError("authorized validation request working directory mismatch")
    if request.get("timeout_seconds") != command_spec["timeout_seconds"]:
        raise FailClosedRuntimeError("authorized validation request timeout mismatch")
    if request.get("output_limit_bytes") != command_spec["output_limit_bytes"]:
        raise FailClosedRuntimeError("authorized validation request output limit mismatch")
    if request.get("expected_exit_code") != command_spec["expected_exit_code"]:
        raise FailClosedRuntimeError("authorized validation request expected exit code mismatch")
    for flag in (
        "shell_allowed",
        "raw_command_string_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "package_install_allowed",
        "network_allowed",
        "repository_mutation_allowed",
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
    ):
        if request.get(flag) is not False:
            raise FailClosedRuntimeError(f"authorized validation request {flag} must be false")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized validation request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorized validation request hash mismatch")
    if authorization_record is not None:
        record = _validate_validation_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized validation request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized validation request authorization hash mismatch")
    return deepcopy(request)


def execute_validation_command_request(
    *,
    authorized_request: dict[str, Any],
    repository_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute exactly one allowlisted validation command with bounded output capture."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_validation_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        cwd = resolve_validation_working_directory(repository_root, request["working_directory"])
        result = _run_command(request=request, cwd=cwd)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(failure, result)


def reconstruct_validation_command_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker-side validation execution replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("validation command Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("validation command Worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "validation command Worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("validation command Worker replay request hash mismatch")
    return {
        "authorization_id": request_artifact["authorization_id"],
        "request_id": request_artifact["request_id"],
        "command_id": request_artifact["command_id"],
        "argv_hash": request_artifact["argv_hash"],
        "exit_code": result_artifact["exit_code"],
        "timed_out": result_artifact["timed_out"],
        "validation_status": result_artifact["validation_status"],
        "stdout_hash": result_artifact["stdout_hash"],
        "stderr_hash": result_artifact["stderr_hash"],
        "worker_invoked": result_artifact["worker_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _run_command(*, request: dict[str, Any], cwd: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            request["argv"],
            cwd=str(cwd),
            timeout=request["timeout_seconds"],
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        timed_out = False
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_timeout_output(exc.stdout)
        stderr = _decode_timeout_output(exc.stderr)
        timed_out = True
        exit_code = None
    validation_status = _validation_status(
        exit_code=exit_code,
        timed_out=timed_out,
        expected_exit_code=request["expected_exit_code"],
    )
    stdout_excerpt, stdout_truncated = _bounded_output(stdout, request["output_limit_bytes"])
    stderr_excerpt, stderr_truncated = _bounded_output(stderr, request["output_limit_bytes"])
    artifact = {
        "runtime_version": VALIDATION_COMMAND_WORKER_VERSION,
        "event_type": VALIDATION_COMMAND_WORKER_EXECUTED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": OPERATION_RUN_VALIDATION_COMMAND,
        "command_id": request["command_id"],
        "argv_hash": request["argv_hash"],
        "working_directory": request["working_directory"],
        "timeout_seconds": request["timeout_seconds"],
        "output_limit_bytes": request["output_limit_bytes"],
        "expected_exit_code": request["expected_exit_code"],
        "exit_code": exit_code,
        "timed_out": timed_out,
        "validation_status": validation_status,
        "stdout_hash": replay_hash(stdout),
        "stderr_hash": replay_hash(stderr),
        "stdout_excerpt": stdout_excerpt,
        "stderr_excerpt": stderr_excerpt,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "worker_invoked": True,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_intended": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_validation_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("validation authorization record must be authorized")
    if record["worker_id"] != VALIDATION_COMMAND_WORKER_ID:
        raise FailClosedRuntimeError("validation authorization Worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_VALIDATION_SCOPE:
        raise FailClosedRuntimeError("validation authorization scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": VALIDATION_COMMAND_WORKER_VERSION,
        "event_type": AUTHORIZED_VALIDATION_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "command_id": request["command_id"],
        "argv_hash": request["argv_hash"],
        "command_spec_hash": request["command_spec_hash"],
        "working_directory": request["working_directory"],
        "timeout_seconds": request["timeout_seconds"],
        "output_limit_bytes": request["output_limit_bytes"],
        "expected_exit_code": request["expected_exit_code"],
        "request_timestamp": request["request_timestamp"],
        "shell_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "worker_self_authorized": False,
        "worker_invoked": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": VALIDATION_COMMAND_WORKER_VERSION,
        "event_type": FAILED_CLOSED,
        "request_id": _safe_field(authorized_request, "request_id", "INVALID_REQUEST"),
        "request_hash": _safe_field(authorized_request, "request_hash", FAILED_CLOSED),
        "authorization_id": _safe_field(authorized_request, "authorization_id", "INVALID_AUTHORIZATION"),
        "authorization_hash": _safe_field(authorized_request, "authorization_hash", FAILED_CLOSED),
        "proposal_reference": _safe_object_field(authorized_request, "proposal_reference"),
        "worker_id": _safe_field(authorized_request, "worker_id", "INVALID_WORKER"),
        "authorized_scope": _safe_field(authorized_request, "authorized_scope", "INVALID_SCOPE"),
        "operation": _safe_field(authorized_request, "operation", "INVALID_OPERATION"),
        "command_id": _safe_field(authorized_request, "command_id", "INVALID_COMMAND"),
        "argv_hash": _safe_field(authorized_request, "argv_hash", FAILED_CLOSED),
        "command_spec_hash": _safe_field(authorized_request, "command_spec_hash", FAILED_CLOSED),
        "working_directory": _safe_field(authorized_request, "working_directory", "INVALID_WORKDIR"),
        "timeout_seconds": _safe_int_field(authorized_request, "timeout_seconds"),
        "output_limit_bytes": _safe_int_field(authorized_request, "output_limit_bytes"),
        "expected_exit_code": _safe_int_field(authorized_request, "expected_exit_code"),
        "request_timestamp": _safe_field(authorized_request, "request_timestamp", "INVALID_TIMESTAMP"),
        "shell_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "worker_self_authorized": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": VALIDATION_COMMAND_WORKER_VERSION,
        "event_type": VALIDATION_COMMAND_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "authorization_id": failure["authorization_id"],
        "worker_id": failure["worker_id"],
        "authorized_scope": failure["authorized_scope"],
        "operation": failure["operation"],
        "command_id": failure["command_id"],
        "argv_hash": failure["argv_hash"],
        "working_directory": failure["working_directory"],
        "exit_code": None,
        "timed_out": False,
        "validation_status": VALIDATION_BLOCKED,
        "stdout_hash": replay_hash(""),
        "stderr_hash": replay_hash(""),
        "stdout_excerpt": "",
        "stderr_excerpt": "",
        "stdout_truncated": False,
        "stderr_truncated": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_intended": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request_artifact: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "authorized_validation_request": deepcopy(request_artifact),
        "validation_command_worker_execution": deepcopy(result),
    }
    capture["validation_command_worker_capture_hash"] = replay_hash(capture)
    return capture


def _validation_status(*, exit_code: int | None, timed_out: bool, expected_exit_code: int) -> str:
    if timed_out:
        return VALIDATION_TIMED_OUT
    if exit_code == expected_exit_code:
        return VALIDATION_PASSED
    return VALIDATION_FAILED


def _bounded_output(value: str, limit: int) -> tuple[str, bool]:
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return value, False
    truncated = encoded[:limit].decode("utf-8", errors="replace")
    return truncated, True


def _decode_timeout_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return str(value)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only validation Worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("validation command Worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "validation command Worker artifact")
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
        raise FailClosedRuntimeError("validation command Worker replay hash mismatch")


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


def _safe_int_field(value: Any, field_name: str) -> int | None:
    if isinstance(value, dict) and isinstance(value.get(field_name), int):
        return value[field_name]
    return None


def _safe_object_field(value: Any, field_name: str) -> dict[str, Any]:
    if isinstance(value, dict) and isinstance(value.get(field_name), dict):
        return deepcopy(value[field_name])
    return {}


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "validation command Worker failed closed"
