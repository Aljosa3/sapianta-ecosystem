"""Static allowlist for governed validation command execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


VALIDATION_ALLOWLIST_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"

VALIDATION_COMMAND_ALLOWLIST: dict[str, dict[str, Any]] = {
    "PY_COMPILE_G8_VALIDATION_TARGETS": {
        "argv": [
            "python",
            "-m",
            "py_compile",
            "aigol/workers/validation_command_worker.py",
            "aigol/runtime/governed_validation_runtime.py",
            "aigol/runtime/platform_core_validation_allowlist.py",
        ],
        "working_directory": ".",
        "timeout_seconds": 30,
        "output_limit_bytes": 8192,
        "expected_exit_code": 0,
        "network_allowed": False,
        "repository_mutation_allowed": False,
    },
    "PYTHON_VALIDATION_FAILS_FOR_TEST": {
        "argv": ["python", "-c", "import sys; print('validation failed'); sys.exit(2)"],
        "working_directory": ".",
        "timeout_seconds": 5,
        "output_limit_bytes": 8192,
        "expected_exit_code": 0,
        "network_allowed": False,
        "repository_mutation_allowed": False,
    },
    "PYTHON_VALIDATION_TIMEOUT_FOR_TEST": {
        "argv": ["python", "-c", "import time; time.sleep(2)"],
        "working_directory": ".",
        "timeout_seconds": 1,
        "output_limit_bytes": 8192,
        "expected_exit_code": 0,
        "network_allowed": False,
        "repository_mutation_allowed": False,
    },
}


def get_validation_command_spec(command_id: str) -> dict[str, Any]:
    """Return a validated static allowlist entry."""

    normalized_id = _require_string(command_id, "command_id")
    spec = VALIDATION_COMMAND_ALLOWLIST.get(normalized_id)
    if not isinstance(spec, dict):
        raise FailClosedRuntimeError("governed validation failed closed: command is not allowlisted")
    return validate_validation_command_spec(normalized_id, spec)


def validate_validation_command_spec(command_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise FailClosedRuntimeError("governed validation command spec must be a JSON object")
    argv = spec.get("argv")
    if not isinstance(argv, list) or not argv:
        raise FailClosedRuntimeError("governed validation argv must be a non-empty list")
    normalized_argv = [_require_string(item, "argv") for item in argv]
    _reject_shell(normalized_argv)
    working_directory = _validate_working_directory(spec.get("working_directory"))
    timeout_seconds = _validate_positive_int(spec.get("timeout_seconds"), "timeout_seconds", maximum=60)
    output_limit_bytes = _validate_positive_int(spec.get("output_limit_bytes"), "output_limit_bytes", maximum=65536)
    expected_exit_code = _validate_nonnegative_int(spec.get("expected_exit_code"), "expected_exit_code", maximum=255)
    if spec.get("network_allowed") is not False:
        raise FailClosedRuntimeError("governed validation network access must be false")
    if spec.get("repository_mutation_allowed") is not False:
        raise FailClosedRuntimeError("governed validation repository mutation must be false")
    normalized = {
        "allowlist_version": VALIDATION_ALLOWLIST_VERSION,
        "command_id": _require_string(command_id, "command_id"),
        "argv": normalized_argv,
        "argv_hash": replay_hash(normalized_argv),
        "working_directory": working_directory,
        "timeout_seconds": timeout_seconds,
        "output_limit_bytes": output_limit_bytes,
        "expected_exit_code": expected_exit_code,
        "shell_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
    }
    normalized["spec_hash"] = replay_hash(normalized)
    return normalized


def resolve_validation_working_directory(repository_root: str | Path, working_directory: str) -> Path:
    root = Path(repository_root).resolve()
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("governed validation failed closed: repository root must exist")
    relative = Path(_validate_working_directory(working_directory))
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise FailClosedRuntimeError("governed validation failed closed: working directory escaped repository") from exc
    if not resolved.exists() or not resolved.is_dir():
        raise FailClosedRuntimeError("governed validation failed closed: working directory must exist")
    return resolved


def _reject_shell(argv: list[str]) -> None:
    shell_names = {"sh", "bash", "zsh", "cmd", "cmd.exe", "powershell", "pwsh"}
    executable = Path(argv[0]).name.lower()
    if executable in shell_names:
        raise FailClosedRuntimeError("governed validation shell execution is prohibited")


def _validate_working_directory(value: Any) -> str:
    text = _require_string(value, "working_directory")
    path = Path(text)
    if path.is_absolute() or any(part in {"..", ""} for part in path.parts):
        raise FailClosedRuntimeError("governed validation working directory must be relative")
    return path.as_posix()


def _validate_positive_int(value: Any, field: str, *, maximum: int) -> int:
    if not isinstance(value, int) or value <= 0 or value > maximum:
        raise FailClosedRuntimeError(f"governed validation {field} is out of bounds")
    return value


def _validate_nonnegative_int(value: Any, field: str, *, maximum: int) -> int:
    if not isinstance(value, int) or value < 0 or value > maximum:
        raise FailClosedRuntimeError(f"governed validation {field} is out of bounds")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value


def command_spec_public_fields(spec: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a command spec for embedding in candidate artifacts."""

    return deepcopy(spec)
