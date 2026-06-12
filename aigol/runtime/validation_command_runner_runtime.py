"""Governed allowlisted validation command runner."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_VERSION = "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1"
VALIDATION_COMMAND_REQUEST_ARTIFACT_V1 = "VALIDATION_COMMAND_REQUEST_ARTIFACT_V1"
VALIDATION_COMMAND_RESULT_ARTIFACT_V1 = "VALIDATION_COMMAND_RESULT_ARTIFACT_V1"
VALIDATION_COMMAND_REQUEST_CERTIFIED = "CERTIFIED_VALIDATION_COMMAND_REQUEST"
VALIDATION_COMMAND_COMPLETED = "VALIDATION_COMMAND_COMPLETED"
VALIDATION_COMMAND_FAILED = "VALIDATION_COMMAND_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "validation_command_request_recorded",
    "validation_command_result_recorded",
    "validation_command_returned",
)

ALLOWLISTED_COMMAND_PREFIXES = (
    ("python", "-m", "pytest"),
    ("python", "-m", "py_compile"),
    ("python", "-m", "json.tool"),
    ("git", "diff", "--check"),
)


def create_validation_command_request(
    *,
    request_id: str,
    command: list[str],
    cwd: str,
    requested_by: str,
    requested_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Create a certified request for an allowlisted validation command."""

    command_argv = _validate_command_argv(command)
    _validate_allowlisted_command(command_argv)
    artifact = {
        "artifact_type": VALIDATION_COMMAND_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_VERSION,
        "request_id": _require_string(request_id, "request_id"),
        "certification_status": VALIDATION_COMMAND_REQUEST_CERTIFIED,
        "command": command_argv,
        "command_display": " ".join(command_argv),
        "cwd": _require_existing_directory(cwd),
        "requested_by": _require_string(requested_by, "requested_by"),
        "requested_at": _require_string(requested_at, "requested_at"),
        "timeout_seconds": _require_timeout(timeout_seconds),
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "governance_authority": {
            "human_authority_preserved": True,
            "validation_only": True,
            "repair_allowed": False,
            "arbitrary_shell_allowed": False,
            "repository_mutation_allowed": False,
        },
        "allowlist": [" ".join(prefix) for prefix in ALLOWLISTED_COMMAND_PREFIXES],
        "allowlist_enforced": True,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "arbitrary_execution_prevented": True,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def execute_validation_command(
    *,
    request_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute an allowlisted validation command with shell disabled and replay capture."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = deepcopy(request_artifact)
        _validate_request_artifact(request)
        result = _execute_request(
            request=request,
            executed_by=executed_by,
            executed_at=executed_at,
        )
        returned = _returned_artifact(result)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(result, returned, replay_path)
    except Exception as exc:
        result = _failed_result_artifact(
            request_artifact=request_artifact,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(result)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(result, returned, replay_path)


def reconstruct_validation_command_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate validation command replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("validation command replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("validation command replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    result = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if result.get("source_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("validation command source request hash mismatch")
    if returned.get("validation_command_result_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("validation command returned result hash mismatch")
    return {
        "request_id": result["source_request"],
        "result_id": result["result_id"],
        "command_status": result["command_status"],
        "exit_code": result["exit_code"],
        "allowlist_enforced": result["allowlist_enforced"],
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "fail_closed_preserved": result["fail_closed_preserved"],
        "arbitrary_execution_prevented": result["arbitrary_execution_prevented"],
        "ready_for_supervised_validation_automation": result["ready_for_supervised_validation_automation"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _execute_request(*, request: dict[str, Any], executed_by: str, executed_at: str) -> dict[str, Any]:
    completed = subprocess.run(
        request["command"],
        cwd=request["cwd"],
        capture_output=True,
        text=True,
        timeout=request["timeout_seconds"],
        shell=False,
        check=False,
    )
    status = VALIDATION_COMMAND_COMPLETED if completed.returncode == 0 else VALIDATION_COMMAND_FAILED
    artifact = {
        "artifact_type": VALIDATION_COMMAND_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_VERSION,
        "result_id": "VALIDATION-COMMAND-RESULT-" + request["request_id"],
        "command_status": status,
        "source_request": request["request_id"],
        "source_request_hash": request["artifact_hash"],
        "command": deepcopy(request["command"]),
        "command_display": request["command_display"],
        "cwd": request["cwd"],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "replay_references": deepcopy(request["replay_references"]),
        "replay_hashes": deepcopy(request["replay_hashes"]),
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "allowlist_enforced": True,
        "shell_execution_used": False,
        "arbitrary_execution_prevented": True,
        "repair_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_authority_preserved": True,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "ready_for_supervised_validation_automation": True,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result_artifact(
    *,
    request_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": VALIDATION_COMMAND_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_VERSION,
        "result_id": "VALIDATION-COMMAND-RESULT-INVALID",
        "command_status": FAILED_CLOSED,
        "source_request": request_artifact.get("request_id") if isinstance(request_artifact, dict) else None,
        "source_request_hash": request_artifact.get("artifact_hash") if isinstance(request_artifact, dict) else None,
        "command": request_artifact.get("command") if isinstance(request_artifact, dict) else None,
        "command_display": request_artifact.get("command_display") if isinstance(request_artifact, dict) else None,
        "cwd": request_artifact.get("cwd") if isinstance(request_artifact, dict) else None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "replay_references": [],
        "replay_hashes": [],
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "allowlist_enforced": True,
        "shell_execution_used": False,
        "arbitrary_execution_prevented": True,
        "repair_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_authority_preserved": True,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "ready_for_supervised_validation_automation": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_request_artifact(request: dict[str, Any]) -> None:
    _verify_artifact_hash(request)
    if request.get("artifact_type") != VALIDATION_COMMAND_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("validation command runner failed closed: invalid artifact type")
    if request.get("certification_status") != VALIDATION_COMMAND_REQUEST_CERTIFIED:
        raise FailClosedRuntimeError("validation command runner failed closed: certified request required")
    command = _validate_command_argv(request.get("command"))
    _validate_allowlisted_command(command)
    if request.get("command_display") != " ".join(command):
        raise FailClosedRuntimeError("validation command runner failed closed: command display mismatch")
    _require_existing_directory(request.get("cwd"))
    _require_timeout(request.get("timeout_seconds"))
    _require_string_list(request.get("replay_references"), "replay_references")
    _require_hash_list(request.get("replay_hashes"), "replay_hashes")
    authority = request.get("governance_authority")
    if not isinstance(authority, dict) or authority.get("validation_only") is not True:
        raise FailClosedRuntimeError("validation command runner failed closed: governance authority invalid")
    if authority.get("arbitrary_shell_allowed") is not False:
        raise FailClosedRuntimeError("validation command runner failed closed: arbitrary shell cannot be allowed")
    if request.get("allowlist_enforced") is not True or request.get("arbitrary_execution_prevented") is not True:
        raise FailClosedRuntimeError("validation command runner failed closed: allowlist evidence missing")


def _validate_command_argv(command: Any) -> list[str]:
    if not isinstance(command, list):
        raise FailClosedRuntimeError("validation command runner failed closed: command must be argv list")
    argv = [_require_string(part, "command") for part in command]
    if not argv:
        raise FailClosedRuntimeError("validation command runner failed closed: command is required")
    if any(part in {";", "&&", "||", "|", ">", ">>", "<"} for part in argv):
        raise FailClosedRuntimeError("validation command runner failed closed: shell operators are not allowed")
    return argv


def _validate_allowlisted_command(command: list[str]) -> None:
    if command[:3] == ["git", "diff", "--check"] and len(command) == 3:
        return
    if len(command) >= 3 and tuple(command[:3]) in ALLOWLISTED_COMMAND_PREFIXES[:3]:
        return
    raise FailClosedRuntimeError("validation command runner failed closed: command is not allowlisted")


def _returned_artifact(result: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(result)
    artifact = {
        "event_type": "VALIDATION_COMMAND_RETURNED",
        "validation_command_result": result["result_id"],
        "validation_command_result_hash": result["artifact_hash"],
        "command_status": result["command_status"],
        "exit_code": result["exit_code"],
        "allowlist_enforced": result["allowlist_enforced"],
        "arbitrary_execution_prevented": result["arbitrary_execution_prevented"],
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "fail_closed_preserved": result["fail_closed_preserved"],
        "ready_for_supervised_validation_automation": result["ready_for_supervised_validation_automation"],
        "failure_reason": result["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(result: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_VERSION,
        "command_status": result["command_status"],
        "validation_command_result_artifact": deepcopy(result),
        "validation_command_returned_artifact": deepcopy(returned),
        "validation_command_replay_reference": str(replay_path),
        "validation_command_runner_implemented": True,
        "allowlist_enforced": result["allowlist_enforced"],
        "replay_preserved": result["replay_lineage_preserved"],
        "arbitrary_execution_prevented": result["arbitrary_execution_prevented"],
        "ready_for_supervised_validation_automation": result["ready_for_supervised_validation_automation"],
        "failure_reason": result["failure_reason"],
    }
    capture["validation_command_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("validation command runner failed closed: replay already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash") if isinstance(artifact, dict) else None
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("validation command artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("validation command artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("validation command replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("validation command replay hash mismatch")


def _require_existing_directory(value: Any) -> str:
    path = Path(_require_string(value, "cwd")).resolve()
    if not path.exists() or not path.is_dir():
        raise FailClosedRuntimeError("validation command runner failed closed: cwd must exist")
    return str(path)


def _require_timeout(value: Any) -> int:
    if not isinstance(value, int) or value < 1 or value > 120:
        raise FailClosedRuntimeError("validation command runner failed closed: timeout must be 1..120 seconds")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"validation command runner failed closed: {field_name} is required")
    return value.strip()


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"validation command runner failed closed: {field_name} must be a list")
    items = [_require_string(item, field_name) for item in value]
    if not items:
        raise FailClosedRuntimeError(f"validation command runner failed closed: {field_name} requires at least one item")
    return items


def _require_hash_list(value: Any, field_name: str) -> list[str]:
    hashes = _require_string_list(value, field_name)
    if not all(item.startswith("sha256:") for item in hashes):
        raise FailClosedRuntimeError(f"validation command runner failed closed: {field_name} must contain hashes")
    return hashes


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    if isinstance(exc, subprocess.TimeoutExpired):
        return "validation command runner failed closed: command timed out"
    return "validation command runner failed closed"
