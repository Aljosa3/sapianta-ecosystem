"""Platform Core rollback metadata helpers for governed mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


MUTATION_ROLLBACK_SERVICE_VERSION = "G8_09B_PLATFORM_CORE_MUTATION_RUNTIME_REFACTORING_V1"
FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1"


def mutation_rollback_metadata_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    validation: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create hash-bound rollback metadata without performing rollback."""

    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_ROLLBACK_ARTIFACT_V1,
        "runtime_version": MUTATION_ROLLBACK_SERVICE_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_path": str(target),
        "target_filename": candidate["target_filename"],
        "rollback_operation": "DELETE_CREATED_FILE_IF_HASH_MATCHES",
        "content_hash": validation["content_hash"],
        "rollback_authorization_required": True,
        "automatic_rollback_allowed": False,
        "delete_directories_allowed": False,
        "delete_preexisting_file_allowed": False,
        "rollback_metadata_present": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first mutating Worker requires {field}")
    return value
