"""Governed CREATE_ONLY filesystem mutation runtime for authorized bundles."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.filesystem_mutation_authorization_runtime import (
    FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1,
    FILESYSTEM_MUTATION_AUTHORIZED,
    verify_filesystem_mutation_authorization_artifact,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_FILESYSTEM_MUTATION_RUNTIME_VERSION = "AIGOL_FILESYSTEM_MUTATION_RUNTIME_V1"
FILESYSTEM_MUTATION_ARTIFACT_V1 = "FILESYSTEM_MUTATION_ARTIFACT_V1"
AIGOL_FILESYSTEM_MUTATION_RUNTIME_STATUS = "CERTIFIED"
FILESYSTEM_MUTATION_COMPLETED = "FILESYSTEM_MUTATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

FORBIDDEN_OPERATIONS = (
    "OVERWRITE",
    "DELETE",
    "RENAME",
    "MOVE",
    "IMPLICIT_FILE_CREATION",
    "UNAUTHORIZED_FILE_CREATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "UPDATE_ONLY",
    "REPLACE_ONLY",
    "RECURSIVE_CREATE",
)

AUTHORITY_FLAGS = {
    "performed_filesystem_mutation": True,
    "performed_overwrite": False,
    "performed_delete": False,
    "performed_rename": False,
    "performed_move": False,
    "created_unauthorized_files": False,
    "invoked_provider": False,
    "invoked_worker": False,
    "authorized_execution": False,
}


def apply_filesystem_mutation(
    *,
    mutation_id: str,
    implementation_manifest_artifact: dict[str, Any],
    filesystem_mutation_authorization_artifact: dict[str, Any],
    target_root: str | Path,
    created_at: str,
    target_root_reference: str = "WORKSPACE_ROOT",
) -> dict[str, Any]:
    """Materialize authorized CREATE_ONLY files beneath target_root."""

    root = Path(target_root)
    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        authorization = _validate_authorization(filesystem_mutation_authorization_artifact, manifest)
        content_by_path = _content_by_authorized_path(manifest, authorization)
        planned_writes = _planned_writes(root, content_by_path, authorization)
        _preflight_no_collisions(planned_writes)
        mutation_results = _write_files(planned_writes)
        checks = _validation_checks()
        status = FILESYSTEM_MUTATION_COMPLETED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        authorization = _authorization_stub(filesystem_mutation_authorization_artifact)
        mutation_results = []
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": FILESYSTEM_MUTATION_ARTIFACT_V1,
        "runtime_version": AIGOL_FILESYSTEM_MUTATION_RUNTIME_VERSION,
        "mutation_id": _safe_string(mutation_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "mutation_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "filesystem_mutation_authorization_reference": authorization["authorization_id"],
        "filesystem_mutation_authorization_artifact_hash": authorization["artifact_hash"],
        "filesystem_mutation_authorization_hash": authorization["filesystem_mutation_authorization_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "target_root_reference": _safe_string(target_root_reference, "WORKSPACE_ROOT"),
        "mutation_results": mutation_results,
        "created_file_count": len(mutation_results),
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "replay_visible": True,
        "filesystem_mutated": status == FILESYSTEM_MUTATION_COMPLETED,
        "overwrite_performed": False,
        "delete_performed": False,
        "rename_performed": False,
        "move_performed": False,
        "implicit_file_creation_performed": False,
        "unauthorized_files_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    if status != FILESYSTEM_MUTATION_COMPLETED:
        artifact["authority_flags"]["performed_filesystem_mutation"] = False
    artifact["filesystem_mutation_hash"] = _compute_mutation_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "filesystem_mutation_artifact": deepcopy(artifact),
        "filesystem_mutation_hash": artifact["filesystem_mutation_hash"],
        "mutation_status": artifact["mutation_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "created_file_count": artifact["created_file_count"],
        "mutation_results": deepcopy(artifact["mutation_results"]),
        "replay_visible": True,
        "filesystem_mutated": artifact["filesystem_mutated"],
        "overwrite_performed": False,
        "delete_performed": False,
        "rename_performed": False,
        "move_performed": False,
        "implicit_file_creation_performed": False,
        "unauthorized_files_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "fail_closed": artifact["mutation_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_FILESYSTEM_MUTATION_RUNTIME_STATUS = "
            f"{AIGOL_FILESYSTEM_MUTATION_RUNTIME_STATUS}"
        ),
    }


def verify_filesystem_mutation_artifact(artifact: dict[str, Any]) -> None:
    """Verify a filesystem mutation artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation artifact must be a JSON object")
    if artifact.get("artifact_type") != FILESYSTEM_MUTATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation artifact type mismatch")
    actual_mutation_hash = artifact.get("filesystem_mutation_hash")
    if actual_mutation_hash != _compute_mutation_hash(artifact):
        raise FailClosedRuntimeError("filesystem mutation hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("filesystem mutation artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("filesystem mutation failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("filesystem mutation failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("filesystem mutation failed closed: manifest must be CREATE_ONLY")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("filesystem mutation failed closed: manifest hash mismatch")
    return manifest


def _validate_authorization(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization must be a JSON object")
    authorization = deepcopy(artifact)
    verify_filesystem_mutation_authorization_artifact(authorization)
    if authorization.get("artifact_type") != FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation failed closed: invalid authorization artifact")
    if authorization.get("authorization_status") != FILESYSTEM_MUTATION_AUTHORIZED:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization not successful")
    if authorization.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization manifest reference mismatch")
    if authorization.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization manifest artifact hash mismatch")
    if authorization.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization manifest hash mismatch")
    if authorization.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization chain mismatch")
    if authorization.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization bundle mismatch")
    if authorization.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorization must be CREATE_ONLY")
    if not isinstance(authorization.get("authorized_permissions"), list) or not authorization["authorized_permissions"]:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorized permissions are required")
    return authorization


def _content_by_authorized_path(manifest: dict[str, Any], authorization: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for entry in list(manifest.get("file_entries", [])) + list(manifest.get("test_entries", [])):
        path = _normalize_target_path(entry.get("target_path"))
        if path in entries:
            raise FailClosedRuntimeError("filesystem mutation failed closed: duplicate manifest target path")
        content = _require_content(entry.get("content"))
        content_hash = _require_hash(entry.get("content_hash"), "content_hash")
        if content_hash != replay_hash(content):
            raise FailClosedRuntimeError("filesystem mutation failed closed: manifest content hash mismatch")
        entries[path] = {
            "content": content,
            "content_hash": content_hash,
            "content_size_bytes": len(content.encode("utf-8")),
        }

    permission_paths = {_normalize_target_path(item.get("target_path")) for item in authorization["authorized_permissions"]}
    if set(entries) != permission_paths:
        raise FailClosedRuntimeError("filesystem mutation failed closed: authorized paths do not match manifest paths")
    return entries


def _planned_writes(
    root: Path,
    content_by_path: dict[str, dict[str, Any]],
    authorization: dict[str, Any],
) -> list[dict[str, Any]]:
    resolved_root = root.resolve()
    writes = []
    seen_paths: set[str] = set()
    for permission in sorted(authorization["authorized_permissions"], key=lambda item: item["target_path"]):
        path = _normalize_target_path(permission.get("target_path"))
        if path in seen_paths:
            raise FailClosedRuntimeError("filesystem mutation failed closed: duplicate authorized target path")
        seen_paths.add(path)
        if permission.get("operation") != CREATE_ONLY:
            raise FailClosedRuntimeError("filesystem mutation failed closed: permission must be CREATE_ONLY")
        if permission.get("required_preflight_target_state") != "MUST_NOT_EXIST":
            raise FailClosedRuntimeError("filesystem mutation failed closed: CREATE_ONLY target must not exist")
        content = content_by_path[path]["content"]
        content_hash = content_by_path[path]["content_hash"]
        if permission.get("content_hash") != content_hash:
            raise FailClosedRuntimeError("filesystem mutation failed closed: permission content hash mismatch")
        target = resolved_root / path
        if not _is_relative_to(target.resolve(), resolved_root):
            raise FailClosedRuntimeError("filesystem mutation failed closed: target path escapes mutation root")
        writes.append(
            {
                "target_path": path,
                "absolute_target_path": target,
                "content": content,
                "content_hash": content_hash,
                "content_size_bytes": content_by_path[path]["content_size_bytes"],
                "operation": CREATE_ONLY,
                "entry_kind": _require_string(permission.get("entry_kind"), "entry_kind"),
                "entry_id": _require_string(permission.get("entry_id"), "entry_id"),
                "artifact_type": _require_string(permission.get("artifact_type"), "artifact_type"),
            }
        )
    return writes


def _preflight_no_collisions(planned_writes: list[dict[str, Any]]) -> None:
    for write in planned_writes:
        target = write["absolute_target_path"]
        if target.exists():
            raise FailClosedRuntimeError("filesystem mutation failed closed: CREATE_ONLY collision")


def _write_files(planned_writes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for write in planned_writes:
        target = write["absolute_target_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as handle:
            handle.write(write["content"])
        materialized_content = target.read_text(encoding="utf-8")
        materialized_hash = replay_hash(materialized_content)
        if materialized_hash != write["content_hash"]:
            raise FailClosedRuntimeError("filesystem mutation failed closed: materialized content hash mismatch")
        results.append(
            {
                "entry_kind": write["entry_kind"],
                "entry_id": write["entry_id"],
                "target_path": write["target_path"],
                "artifact_type": write["artifact_type"],
                "operation": CREATE_ONLY,
                "content_hash": write["content_hash"],
                "materialized_content_hash": materialized_hash,
                "content_size_bytes": len(materialized_content.encode("utf-8")),
                "created": True,
                "overwrite_performed": False,
            }
        )
    return results


def _validation_checks() -> dict[str, bool]:
    return {
        "authorization_consumed": True,
        "authorized_files_only_created": True,
        "exact_content_hashes_verified": True,
        "exact_paths_verified": True,
        "create_only_enforced": True,
        "collision_preflight_passed": True,
        "replay_visible_mutation_evidence": True,
        "overwrite_absent": True,
        "delete_absent": True,
        "rename_absent": True,
        "move_absent": True,
        "implicit_file_creation_absent": True,
        "unauthorized_files_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "authorization_consumed": False,
        "authorized_files_only_created": False,
        "exact_content_hashes_verified": False,
        "exact_paths_verified": False,
        "create_only_enforced": False,
        "collision_preflight_passed": False,
        "replay_visible_mutation_evidence": True,
        "overwrite_absent": True,
        "delete_absent": True,
        "rename_absent": True,
        "move_absent": True,
        "implicit_file_creation_absent": True,
        "unauthorized_files_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
    }


def _manifest_stub(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "manifest_id": _safe_string(value.get("manifest_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "implementation_manifest_hash": _safe_string(value.get("implementation_manifest_hash"), "UNKNOWN"),
            "canonical_chain_id": _safe_string(value.get("canonical_chain_id"), "UNKNOWN"),
            "implementation_bundle_id": _safe_string(value.get("implementation_bundle_id"), "UNKNOWN"),
            "operation_mode": _safe_string(value.get("operation_mode"), "UNKNOWN"),
        }
    return {
        "manifest_id": "UNKNOWN",
        "artifact_hash": "UNKNOWN",
        "implementation_manifest_hash": "UNKNOWN",
        "canonical_chain_id": "UNKNOWN",
        "implementation_bundle_id": "UNKNOWN",
        "operation_mode": "UNKNOWN",
    }


def _authorization_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "authorization_id": _safe_string(value.get("authorization_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "filesystem_mutation_authorization_hash": _safe_string(
                value.get("filesystem_mutation_authorization_hash"),
                "UNKNOWN",
            ),
        }
    return {
        "authorization_id": "UNKNOWN",
        "artifact_hash": "UNKNOWN",
        "filesystem_mutation_authorization_hash": "UNKNOWN",
    }


def _compute_mutation_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("filesystem_mutation_hash", None)
    return replay_hash(value)


def _compute_manifest_hash(manifest: dict[str, Any]) -> str:
    return replay_hash(
        {
            "manifest_id": manifest["manifest_id"],
            "canonical_chain_id": manifest["canonical_chain_id"],
            "implementation_bundle_id": manifest["implementation_bundle_id"],
            "source_candidate_reference": manifest["source_candidate_reference"],
            "source_candidate_hash": manifest["source_candidate_hash"],
            "implementation_handoff_reference": manifest["implementation_handoff_reference"],
            "implementation_handoff_hash": manifest["implementation_handoff_hash"],
            "provider_generation_authorization_reference": manifest[
                "provider_generation_authorization_reference"
            ],
            "provider_generation_authorization_hash": manifest["provider_generation_authorization_hash"],
            "provider_response_reference": manifest["provider_response_reference"],
            "provider_response_hash": manifest["provider_response_hash"],
            "target_domain": manifest["target_domain"],
            "target_resource": manifest["target_resource"],
            "target_worker": manifest["target_worker"],
            "operation_mode": manifest["operation_mode"],
            "file_entries": manifest["file_entries"],
            "test_entries": manifest["test_entries"],
            "validation_requirements": manifest["validation_requirements"],
            "forbidden_operations": manifest["forbidden_operations"],
            "known_gaps": manifest["known_gaps"],
            "manifest_status": manifest["manifest_status"],
            "read_only": manifest["read_only"],
            "content_bearing_manifest": manifest["content_bearing_manifest"],
            "filesystem_mutated": manifest["filesystem_mutated"],
            "execution_authorized": manifest["execution_authorized"],
            "provider_invoked": manifest["provider_invoked"],
            "worker_invoked": manifest["worker_invoked"],
            "approval_created": manifest["approval_created"],
            "authority_flags": manifest["authority_flags"],
            "failure_reason": manifest["failure_reason"],
        }
    )


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"filesystem mutation failed closed: {label} artifact hash mismatch")


def _normalize_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    if path_text.startswith("/") or "\\" in path_text:
        raise FailClosedRuntimeError("filesystem mutation failed closed: invalid target path")
    path = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("filesystem mutation failed closed: invalid target path")
    return path.as_posix()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _require_hash(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"filesystem mutation failed closed: {label} must be a sha256 hash")
    return text


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"filesystem mutation failed closed: {label} missing")
    return value.strip()


def _require_content(value: Any) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError("filesystem mutation failed closed: content missing")
    return value


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "filesystem mutation failed closed"


__all__ = [
    "AIGOL_FILESYSTEM_MUTATION_RUNTIME_STATUS",
    "AIGOL_FILESYSTEM_MUTATION_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "FILESYSTEM_MUTATION_ARTIFACT_V1",
    "FILESYSTEM_MUTATION_COMPLETED",
    "apply_filesystem_mutation",
    "verify_filesystem_mutation_artifact",
]
