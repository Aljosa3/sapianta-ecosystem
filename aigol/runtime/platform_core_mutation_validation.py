"""Platform Core validation helpers for the first governed mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import validate_mutation_target_filename
from aigol.runtime.transport.serialization import replay_hash


MUTATION_VALIDATION_SERVICE_VERSION = "G8_09B_PLATFORM_CORE_MUTATION_RUNTIME_REFACTORING_V1"
FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1"
FIRST_MUTATING_WORKER_VALIDATION_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_VALIDATION_ARTIFACT_V1"


def resolve_existing_repository_dir(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise FailClosedRuntimeError("first mutating Worker failed closed: repository_root must exist")
    return resolved


def resolve_allowlisted_workspace(*, root: Path, workspace: str | Path, expected: str) -> Path:
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


def mutation_target_path(*, workspace_path: Path, filename: str) -> Path:
    target = (workspace_path / validate_mutation_target_filename(filename)).resolve()
    if target.parent != workspace_path.resolve():
        raise FailClosedRuntimeError("first mutating Worker failed closed: target escaped workspace")
    return target


def pre_mutation_state_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    workspace_path: Path,
    target: Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_PRE_MUTATION_ARTIFACT_V1,
        "runtime_version": MUTATION_VALIDATION_SERVICE_VERSION,
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


def post_mutation_validation_artifact(
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
        "runtime_version": MUTATION_VALIDATION_SERVICE_VERSION,
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
