"""Rollback metadata helpers for governed single-file patch mutation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PATCH_MUTATION_ROLLBACK_VERSION = "G9_04_SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTATION_V1"
PATCH_MUTATION_ROLLBACK_ARTIFACT_V1 = "PATCH_MUTATION_ROLLBACK_ARTIFACT_V1"


def patch_mutation_rollback_metadata_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    target: Path,
    pre_mutation: dict[str, Any],
    validation: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create hash-bound rollback metadata without performing rollback."""

    artifact = {
        "artifact_type": PATCH_MUTATION_ROLLBACK_ARTIFACT_V1,
        "runtime_version": PATCH_MUTATION_ROLLBACK_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_path": str(target),
        "target_relative_path": candidate["target_path"],
        "rollback_operation": "RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH",
        "original_content_hash": pre_mutation["target_content_hash_before"],
        "authorized_post_mutation_hash": validation["post_content_hash"],
        "inverse_patch_old_text_hash": candidate["new_text_hash"],
        "inverse_patch_new_text_hash": candidate["old_text_hash"],
        "complete_pre_mutation_artifact_required_for_execution": True,
        "complete_post_mutation_artifact_hash": validation["complete_resulting_content_hash"],
        "rollback_authorization_required": True,
        "automatic_rollback_allowed": False,
        "restore_if_current_hash_matches_authorized_post_hash": True,
        "delete_file_allowed": False,
        "delete_directories_allowed": False,
        "rollback_metadata_present": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"patch mutation requires {field}")
    return value
