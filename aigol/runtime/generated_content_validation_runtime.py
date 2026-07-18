"""Pure generated-content validation runtime for implementation manifests."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Any

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V2,
    IMPLEMENTATION_MANIFEST_CREATED,
    REPLACE_CONTENT,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION = "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_V1"
AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION_V2 = "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_V2"
GENERATED_CONTENT_VALIDATION_ARTIFACT_V1 = "GENERATED_CONTENT_VALIDATION_ARTIFACT_V1"
GENERATED_CONTENT_VALIDATION_ARTIFACT_V2 = "GENERATED_CONTENT_VALIDATION_ARTIFACT_V2"
AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_STATUS = "CERTIFIED"
GENERATED_CONTENT_VALIDATED = "GENERATED_CONTENT_VALIDATED"
FAILED_CLOSED = "FAILED_CLOSED"

ALLOWED_ARTIFACT_TYPES = (
    "GOVERNANCE_DOCUMENT_MARKDOWN",
    "JSON_GOVERNANCE_ARTIFACT",
    "JSON_SCHEMA",
    "PYTEST_TEST",
    "PYTHON_RUNTIME_MODULE",
)

ALLOWED_TARGET_PREFIXES = (
    "aigol/runtime/",
    "docs/",
    "governance/",
    "schemas/",
    "tests/",
)

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "APPROVAL_CREATION",
    "EXECUTION_AUTHORIZATION",
    "DISPATCH",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
    "DEPENDENCY_INSTALL",
    "DELETE",
    "RENAME",
    "MOVE",
    "RECURSIVE_CREATE",
)

AUTHORITY_FLAGS = {
    "authorizes_filesystem_mutation": False,
    "authorizes_provider_invocation": False,
    "authorizes_worker_invocation": False,
    "authorizes_approval_creation": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_automatic_implementation": False,
}


def validate_generated_content(
    *,
    validation_id: str,
    implementation_manifest_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Validate generated implementation content without file, provider, or worker authority."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        file_results = [_validate_file_entry(entry) for entry in manifest["file_entries"]]
        test_results = (
            [] if manifest["operation_mode"] == REPLACE_CONTENT
            else [_validate_test_entry(entry, file_results) for entry in manifest["test_entries"]]
        )
        _validate_bundle_consistency(manifest, file_results, test_results)
        checks = _validation_checks(manifest, file_results, test_results)
        status = GENERATED_CONTENT_VALIDATED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        file_results = []
        test_results = []
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": (
            GENERATED_CONTENT_VALIDATION_ARTIFACT_V2
            if manifest["operation_mode"] == REPLACE_CONTENT
            else GENERATED_CONTENT_VALIDATION_ARTIFACT_V1
        ),
        "runtime_version": (
            AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION_V2
            if manifest["operation_mode"] == REPLACE_CONTENT
            else AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION
        ),
        "validation_id": _safe_string(validation_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "validation_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "file_validation_results": file_results,
        "test_validation_results": test_results,
        "file_count": len(file_results),
        "test_count": len(test_results),
        "validation_checks": checks,
        "allowed_artifact_types": list(ALLOWED_ARTIFACT_TYPES),
        "allowed_target_prefixes": list(ALLOWED_TARGET_PREFIXES),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_authorized": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["generated_content_validation_hash"] = _compute_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "generated_content_validation_artifact": deepcopy(artifact),
        "generated_content_validation_hash": artifact["generated_content_validation_hash"],
        "validation_status": artifact["validation_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "file_count": artifact["file_count"],
        "test_count": artifact["test_count"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_authorized": False,
        "fail_closed": artifact["validation_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_STATUS = "
            f"{AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_STATUS}"
        ),
    }


def verify_generated_content_validation_artifact(artifact: dict[str, Any]) -> None:
    """Verify a generated-content validation artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content validation artifact must be a JSON object")
    if artifact.get("artifact_type") not in {
        GENERATED_CONTENT_VALIDATION_ARTIFACT_V1,
        GENERATED_CONTENT_VALIDATION_ARTIFACT_V2,
    }:
        raise FailClosedRuntimeError("generated content validation artifact type mismatch")
    actual_validation_hash = artifact.get("generated_content_validation_hash")
    if actual_validation_hash != _compute_validation_hash(artifact):
        raise FailClosedRuntimeError("generated content validation hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated content validation artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated content validation failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    artifact_type = manifest.get("artifact_type")
    if artifact_type not in {IMPLEMENTATION_MANIFEST_ARTIFACT_V1, IMPLEMENTATION_MANIFEST_ARTIFACT_V2}:
        raise FailClosedRuntimeError("generated content validation failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("generated content validation failed closed: manifest is not created")
    expected_operation = CREATE_ONLY if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1 else REPLACE_CONTENT
    if manifest.get("operation_mode") != expected_operation:
        if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
            raise FailClosedRuntimeError("generated content validation failed closed: manifest must be CREATE_ONLY")
        raise FailClosedRuntimeError("generated content validation failed closed: manifest must be REPLACE_CONTENT")
    _verify_manifest_artifact_hash(manifest)
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("generated content validation failed closed: manifest hash mismatch")
    if not isinstance(manifest.get("file_entries"), list) or not manifest["file_entries"]:
        raise FailClosedRuntimeError("generated content validation failed closed: file entries are required")
    if not isinstance(manifest.get("test_entries"), list):
        raise FailClosedRuntimeError("generated content validation failed closed: test entries must be a list")
    if expected_operation == REPLACE_CONTENT:
        patch = _require_content(manifest.get("exact_patch"))
        if _exact_sha256(manifest.get("patch_sha256"), "patch_sha256") != _byte_sha256(patch):
            raise FailClosedRuntimeError("generated content validation failed closed: patch hash mismatch")
    return manifest


def _validate_file_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("generated content validation failed closed: file entry must be a JSON object")
    normalized_path = _normalize_target_path(entry.get("target_path"))
    artifact_type = _require_allowed_artifact_type(entry.get("artifact_type"))
    if entry.get("operation") == REPLACE_CONTENT:
        return _validate_replacement_file_entry(entry, normalized_path, artifact_type)
    if entry.get("operation") != CREATE_ONLY:
        raise FailClosedRuntimeError("generated content validation failed closed: file operation must be CREATE_ONLY")
    if entry.get("preflight_target_state") != "MUST_NOT_EXIST":
        raise FailClosedRuntimeError("generated content validation failed closed: CREATE_ONLY target must not exist")
    content = _require_content(entry.get("content"))
    expected_hash = replay_hash(content)
    if entry.get("content_hash") != expected_hash:
        raise FailClosedRuntimeError("generated content validation failed closed: file content hash mismatch")
    if entry.get("content_size_bytes") != len(content.encode("utf-8")):
        raise FailClosedRuntimeError("generated content validation failed closed: file content size mismatch")
    if entry.get("file_entry_hash") != replay_hash(_without_hash(entry, "file_entry_hash")):
        raise FailClosedRuntimeError("generated content validation failed closed: file entry hash mismatch")
    _require_false_authority_flags(entry.get("authority_flags"))
    return {
        "entry_id": _require_string(entry.get("file_entry_id"), "file_entry_id"),
        "target_path": normalized_path,
        "artifact_type": artifact_type,
        "operation": CREATE_ONLY,
        "content_hash": expected_hash,
        "entry_hash": entry["file_entry_hash"],
        "content_size_bytes": entry["content_size_bytes"],
        "path_allowed": True,
        "artifact_type_allowed": True,
        "create_only_valid": True,
        "content_hash_valid": True,
        "authority_preserved": True,
    }


def _validate_replacement_file_entry(
    entry: dict[str, Any], normalized_path: str, artifact_type: str,
) -> dict[str, Any]:
    if entry.get("existing_target") is not True or entry.get("preflight_target_state") != "MUST_EXIST_REGULAR_FILE":
        raise FailClosedRuntimeError("generated content validation failed closed: replacement existing target required")
    if entry.get("original_target_path") != normalized_path or entry.get("resulting_target_path") != normalized_path:
        raise FailClosedRuntimeError("generated content validation failed closed: replacement path identity changed")
    preimage = _require_text(entry.get("preimage_content"), "preimage_content")
    postimage = _require_text(entry.get("postimage_content"), "postimage_content")
    preimage_hash = _exact_sha256(entry.get("preimage_sha256"), "preimage_sha256")
    postimage_hash = _exact_sha256(entry.get("postimage_sha256"), "postimage_sha256")
    if preimage_hash != _byte_sha256(preimage) or postimage_hash != _byte_sha256(postimage):
        raise FailClosedRuntimeError("generated content validation failed closed: replacement byte hash mismatch")
    _exact_sha256(entry.get("patch_sha256"), "patch_sha256")
    if entry.get("expected_postimage_size_bytes") != len(postimage.encode("utf-8")):
        raise FailClosedRuntimeError("generated content validation failed closed: replacement postimage size mismatch")
    if not all((
        entry.get("path_identity_unchanged") is True,
        entry.get("file_type") == "REGULAR_FILE",
        entry.get("postimage_file_type") == "REGULAR_FILE",
        entry.get("file_mode") == entry.get("postimage_file_mode"),
        isinstance(entry.get("file_mode"), int),
    )):
        raise FailClosedRuntimeError("generated content validation failed closed: replacement type or mode changed")
    for flag in (
        "create_allowed", "delete_allowed", "rename_allowed", "binary_patch_allowed",
        "symlink_allowed", "submodule_allowed", "path_traversal_allowed",
    ):
        if entry.get(flag) is not False:
            raise FailClosedRuntimeError(f"generated content validation failed closed: {flag} must be false")
    if entry.get("file_entry_hash") != replay_hash(_without_hash(entry, "file_entry_hash")):
        raise FailClosedRuntimeError("generated content validation failed closed: file entry hash mismatch")
    _require_false_authority_flags(entry.get("authority_flags"))
    return {
        "entry_id": _require_string(entry.get("file_entry_id"), "file_entry_id"),
        "target_path": normalized_path,
        "artifact_type": artifact_type,
        "operation": REPLACE_CONTENT,
        "preimage_sha256": preimage_hash,
        "postimage_sha256": postimage_hash,
        "patch_sha256": entry["patch_sha256"],
        "entry_hash": entry["file_entry_hash"],
        "expected_postimage_size_bytes": entry["expected_postimage_size_bytes"],
        "path_allowed": True,
        "artifact_type_allowed": True,
        "replacement_constraints_valid": True,
        "content_hash_valid": True,
        "authority_preserved": True,
    }


def _validate_test_entry(entry: dict[str, Any], file_results: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("generated content validation failed closed: test entry must be a JSON object")
    normalized_path = _normalize_target_path(entry.get("target_path"))
    artifact_type = _require_allowed_artifact_type(entry.get("artifact_type"))
    if entry.get("operation") != CREATE_ONLY:
        raise FailClosedRuntimeError("generated content validation failed closed: test operation must be CREATE_ONLY")
    content = _require_content(entry.get("content"))
    expected_hash = replay_hash(content)
    if entry.get("content_hash") != expected_hash:
        raise FailClosedRuntimeError("generated content validation failed closed: test content hash mismatch")
    if entry.get("content_size_bytes") != len(content.encode("utf-8")):
        raise FailClosedRuntimeError("generated content validation failed closed: test content size mismatch")
    if entry.get("test_entry_hash") != replay_hash(_without_hash(entry, "test_entry_hash")):
        raise FailClosedRuntimeError("generated content validation failed closed: test entry hash mismatch")
    file_ids = {result["entry_id"] for result in file_results}
    tested_entries = _string_list(entry.get("tests_file_entries"), "tests_file_entries", allow_empty=False)
    if any(entry_id not in file_ids for entry_id in tested_entries):
        raise FailClosedRuntimeError("generated content validation failed closed: test references unknown file entry")
    _require_string(entry.get("validation_command"), "validation_command")
    _require_string(entry.get("expected_coverage_target"), "expected_coverage_target")
    _require_string(entry.get("negative_case_requirement"), "negative_case_requirement")
    _require_false_authority_flags(entry.get("authority_flags"))
    return {
        "entry_id": _require_string(entry.get("test_entry_id"), "test_entry_id"),
        "target_path": normalized_path,
        "artifact_type": artifact_type,
        "operation": CREATE_ONLY,
        "content_hash": expected_hash,
        "entry_hash": entry["test_entry_hash"],
        "content_size_bytes": entry["content_size_bytes"],
        "tests_file_entries": tested_entries,
        "path_allowed": True,
        "artifact_type_allowed": True,
        "create_only_valid": True,
        "content_hash_valid": True,
        "bundle_reference_valid": True,
        "authority_preserved": True,
    }


def _validate_bundle_consistency(
    manifest: dict[str, Any],
    file_results: list[dict[str, Any]],
    test_results: list[dict[str, Any]],
) -> None:
    if manifest.get("file_count") != len(file_results):
        raise FailClosedRuntimeError("generated content validation failed closed: file count mismatch")
    if manifest.get("operation_mode") == CREATE_ONLY and manifest.get("test_count") != len(test_results):
        raise FailClosedRuntimeError("generated content validation failed closed: test count mismatch")
    paths = [result["target_path"] for result in file_results + test_results]
    if len(paths) != len(set(paths)):
        raise FailClosedRuntimeError("generated content validation failed closed: duplicate target path")
    if not _string_list(manifest.get("validation_requirements"), "validation_requirements", allow_empty=False):
        raise FailClosedRuntimeError("generated content validation failed closed: validation requirements missing")
    if manifest.get("operation_mode") == REPLACE_CONTENT and any(
        result.get("patch_sha256") != manifest.get("patch_sha256") for result in file_results
    ):
        raise FailClosedRuntimeError("generated content validation failed closed: replacement patch binding mismatch")
    _require_false_authority_flags(manifest.get("authority_flags"))
    if any(operation not in manifest.get("forbidden_operations", []) for operation in FORBIDDEN_OPERATIONS):
        raise FailClosedRuntimeError("generated content validation failed closed: forbidden operations incomplete")


def _validation_checks(
    manifest: dict[str, Any],
    file_results: list[dict[str, Any]],
    test_results: list[dict[str, Any]],
) -> dict[str, bool]:
    checks = {
        "manifest_consistency_valid": manifest["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
        "manifest_hash_valid": manifest["implementation_manifest_hash"] == _compute_manifest_hash(manifest),
        "file_content_hashes_valid": all(result["content_hash_valid"] for result in file_results),
        "test_content_hashes_valid": all(result["content_hash_valid"] for result in test_results),
        "artifact_types_valid": all(result["artifact_type_allowed"] for result in file_results + test_results),
        "allowed_paths_valid": all(result["path_allowed"] for result in file_results + test_results),
        "bundle_consistency_valid": manifest["file_count"] == len(file_results)
        and (
            manifest["operation_mode"] == REPLACE_CONTENT
            or manifest["test_count"] == len(test_results)
        ),
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "approval_creation_absent": True,
        "execution_authorization_absent": True,
    }
    if manifest["operation_mode"] == REPLACE_CONTENT:
        checks["manifest_consistency_valid"] = manifest["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V2
        checks["replacement_constraints_valid"] = all(
            result["replacement_constraints_valid"] for result in file_results
        )
    else:
        checks["create_only_constraints_valid"] = all(
            result["create_only_valid"] for result in file_results + test_results
        )
    return checks


def _failed_checks() -> dict[str, bool]:
    return {
        "manifest_consistency_valid": False,
        "manifest_hash_valid": False,
        "file_content_hashes_valid": False,
        "test_content_hashes_valid": False,
        "artifact_types_valid": False,
        "allowed_paths_valid": False,
        "create_only_constraints_valid": False,
        "bundle_consistency_valid": False,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "approval_creation_absent": True,
        "execution_authorization_absent": True,
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


def _compute_validation_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("generated_content_validation_hash", None)
    return replay_hash(value)


def _compute_manifest_hash(manifest: dict[str, Any]) -> str:
    if manifest.get("artifact_type") == IMPLEMENTATION_MANIFEST_ARTIFACT_V2:
        value = deepcopy(manifest)
        value.pop("implementation_manifest_hash", None)
        value.pop("artifact_hash", None)
        return replay_hash(value)
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


def _verify_manifest_artifact_hash(manifest: dict[str, Any]) -> None:
    actual = manifest.get("artifact_hash")
    expected_input = deepcopy(manifest)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated content validation failed closed: manifest artifact hash mismatch")


def _without_hash(entry: dict[str, Any], field_name: str) -> dict[str, Any]:
    value = deepcopy(entry)
    value.pop(field_name, None)
    return value


def _normalize_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    if path_text.startswith("/") or "\\" in path_text:
        raise FailClosedRuntimeError("generated content validation failed closed: invalid target path")
    path = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("generated content validation failed closed: invalid target path")
    normalized = path.as_posix()
    if not any(normalized.startswith(prefix) for prefix in ALLOWED_TARGET_PREFIXES):
        raise FailClosedRuntimeError("generated content validation failed closed: target path is not allowed")
    return normalized


def _require_allowed_artifact_type(value: Any) -> str:
    artifact_type = _require_string(value, "artifact_type")
    if artifact_type not in ALLOWED_ARTIFACT_TYPES:
        raise FailClosedRuntimeError("generated content validation failed closed: artifact type is not allowed")
    return artifact_type


def _require_false_authority_flags(value: Any) -> None:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated content validation failed closed: authority flags missing")
    if any(flag_value is not False for flag_value in value.values()):
        raise FailClosedRuntimeError("generated content validation failed closed: authority flag must be false")


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"generated content validation failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"generated content validation failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"generated content validation failed closed: {label} missing")
    return value.strip()


def _require_content(value: Any) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError("generated content validation failed closed: content missing")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise FailClosedRuntimeError(f"generated content validation failed closed: {label} missing")
    return value


def _exact_sha256(value: Any, label: str) -> str:
    text = _require_string(value, label)
    digest = text.removeprefix("sha256:")
    if not text.startswith("sha256:") or len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise FailClosedRuntimeError(f"generated content validation failed closed: {label} invalid")
    return text


def _byte_sha256(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "generated content validation failed closed"


__all__ = [
    "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_STATUS",
    "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION",
    "AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_VERSION_V2",
    "FAILED_CLOSED",
    "GENERATED_CONTENT_VALIDATED",
    "GENERATED_CONTENT_VALIDATION_ARTIFACT_V1",
    "GENERATED_CONTENT_VALIDATION_ARTIFACT_V2",
    "validate_generated_content",
    "verify_generated_content_validation_artifact",
]
