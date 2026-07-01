"""Platform Core validation result evidence helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_allowlist import resolve_validation_working_directory
from aigol.runtime.transport.serialization import replay_hash


VALIDATION_RESULT_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
VALIDATION_PRE_EXECUTION_ARTIFACT_V1 = "VALIDATION_PRE_EXECUTION_ARTIFACT_V1"
VALIDATION_RESULT_ARTIFACT_V1 = "VALIDATION_RESULT_ARTIFACT_V1"


def validation_pre_execution_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    repository_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    command_spec = candidate["command_spec"]
    working_directory = resolve_validation_working_directory(repository_root, command_spec["working_directory"])
    artifact = {
        "artifact_type": VALIDATION_PRE_EXECUTION_ARTIFACT_V1,
        "runtime_version": VALIDATION_RESULT_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "command_id": candidate["command_id"],
        "argv_hash": candidate["argv_hash"],
        "command_spec_hash": candidate["command_spec_hash"],
        "repository_root": str(Path(repository_root).resolve()),
        "working_directory": str(working_directory),
        "timeout_seconds": command_spec["timeout_seconds"],
        "output_limit_bytes": command_spec["output_limit_bytes"],
        "allowlist_match": True,
        "shell_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validation_result_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    worker_result: dict[str, Any],
    worker_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if worker_result.get("command_id") != candidate["command_id"]:
        raise FailClosedRuntimeError("governed validation result command mismatch")
    if worker_result.get("argv_hash") != candidate["argv_hash"]:
        raise FailClosedRuntimeError("governed validation result argv mismatch")
    artifact = {
        "artifact_type": VALIDATION_RESULT_ARTIFACT_V1,
        "runtime_version": VALIDATION_RESULT_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "command_id": candidate["command_id"],
        "argv_hash": candidate["argv_hash"],
        "command_spec_hash": candidate["command_spec_hash"],
        "exit_code": worker_result["exit_code"],
        "timed_out": worker_result["timed_out"],
        "validation_status": worker_result["validation_status"],
        "stdout_hash": worker_result["stdout_hash"],
        "stderr_hash": worker_result["stderr_hash"],
        "stdout_excerpt": worker_result["stdout_excerpt"],
        "stderr_excerpt": worker_result["stderr_excerpt"],
        "stdout_truncated": worker_result["stdout_truncated"],
        "stderr_truncated": worker_result["stderr_truncated"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_intended": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value
