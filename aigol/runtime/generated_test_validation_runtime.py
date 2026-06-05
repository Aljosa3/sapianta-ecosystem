"""Pure generated-test validation runtime for implementation manifests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_VERSION = "AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_V1"
GENERATED_TEST_VALIDATION_ARTIFACT_V1 = "GENERATED_TEST_VALIDATION_ARTIFACT_V1"
AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_STATUS = "CERTIFIED"
GENERATED_TEST_VALIDATED = "GENERATED_TEST_VALIDATED"
FAILED_CLOSED = "FAILED_CLOSED"

ALLOWED_TEST_ARTIFACT_TYPES = ("PYTEST_TEST",)
ALLOWED_TEST_TARGET_PREFIXES = ("tests/",)

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


def validate_generated_tests(
    *,
    validation_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_test_bundle: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    """Validate generated test artifacts without acceptance, execution, or mutation authority."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        manifest_tests = _manifest_tests_by_id(manifest)
        implementation_files = _implementation_files_by_id(manifest)
        bundle = _validate_test_bundle(generated_test_bundle, manifest_tests)
        test_results = [
            _validate_test_artifact(test, manifest_tests[test["test_entry_id"]], implementation_files)
            for test in bundle
        ]
        checks = _validation_checks(manifest, test_results)
        status = GENERATED_TEST_VALIDATED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        test_results = []
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": GENERATED_TEST_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_VERSION,
        "validation_id": _safe_string(validation_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "validation_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "test_validation_results": test_results,
        "test_count": len(test_results),
        "validation_checks": checks,
        "allowed_test_artifact_types": list(ALLOWED_TEST_ARTIFACT_TYPES),
        "allowed_test_target_prefixes": list(ALLOWED_TEST_TARGET_PREFIXES),
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
    artifact["generated_test_validation_hash"] = _compute_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "generated_test_validation_artifact": deepcopy(artifact),
        "generated_test_validation_hash": artifact["generated_test_validation_hash"],
        "validation_status": artifact["validation_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
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
            "AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_STATUS = "
            f"{AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_STATUS}"
        ),
    }


def verify_generated_test_validation_artifact(artifact: dict[str, Any]) -> None:
    """Verify a generated-test validation artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated test validation artifact must be a JSON object")
    if artifact.get("artifact_type") != GENERATED_TEST_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated test validation artifact type mismatch")
    actual_validation_hash = artifact.get("generated_test_validation_hash")
    if actual_validation_hash != _compute_validation_hash(artifact):
        raise FailClosedRuntimeError("generated test validation hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated test validation artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated test validation failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated test validation failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("generated test validation failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("generated test validation failed closed: manifest must be CREATE_ONLY")
    _verify_manifest_artifact_hash(manifest)
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("generated test validation failed closed: manifest hash mismatch")
    if not isinstance(manifest.get("file_entries"), list) or not manifest["file_entries"]:
        raise FailClosedRuntimeError("generated test validation failed closed: implementation files are required")
    if not isinstance(manifest.get("test_entries"), list) or not manifest["test_entries"]:
        raise FailClosedRuntimeError("generated test validation failed closed: test artifacts are required")
    if manifest.get("test_count") != len(manifest["test_entries"]):
        raise FailClosedRuntimeError("generated test validation failed closed: manifest test count mismatch")
    return manifest


def _manifest_tests_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tests: dict[str, dict[str, Any]] = {}
    for entry in manifest["test_entries"]:
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError("generated test validation failed closed: manifest test must be a JSON object")
        test_id = _require_string(entry.get("test_entry_id"), "test_entry_id")
        if test_id in tests:
            raise FailClosedRuntimeError("generated test validation failed closed: duplicate test artifact id")
        tests[test_id] = entry
    return tests


def _implementation_files_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for entry in manifest["file_entries"]:
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError("generated test validation failed closed: implementation file must be a JSON object")
        file_id = _require_string(entry.get("file_entry_id"), "file_entry_id")
        if file_id in files:
            raise FailClosedRuntimeError("generated test validation failed closed: duplicate implementation file id")
        files[file_id] = entry
    return files


def _validate_test_bundle(
    generated_test_bundle: list[dict[str, Any]],
    manifest_tests: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(generated_test_bundle, list) or not generated_test_bundle:
        raise FailClosedRuntimeError("generated test validation failed closed: generated test bundle is required")
    bundle = deepcopy(generated_test_bundle)
    bundle_ids: list[str] = []
    for entry in bundle:
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError("generated test validation failed closed: test artifact must be a JSON object")
        bundle_ids.append(_require_string(entry.get("test_entry_id"), "test_entry_id"))
    if len(bundle_ids) != len(set(bundle_ids)):
        raise FailClosedRuntimeError("generated test validation failed closed: duplicate test artifact id")
    if set(bundle_ids) != set(manifest_tests):
        raise FailClosedRuntimeError("generated test validation failed closed: manifest-to-test consistency mismatch")
    return sorted(bundle, key=lambda item: item["test_entry_id"])


def _validate_test_artifact(
    test: dict[str, Any],
    manifest_test: dict[str, Any],
    implementation_files: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if test != manifest_test:
        raise FailClosedRuntimeError("generated test validation failed closed: test artifact does not match manifest")
    target_path = _normalize_test_path(test.get("target_path"))
    artifact_type = _require_allowed_test_artifact_type(test.get("artifact_type"))
    if test.get("operation") != CREATE_ONLY:
        raise FailClosedRuntimeError("generated test validation failed closed: test operation must be CREATE_ONLY")
    content = _require_content(test.get("content"))
    expected_hash = replay_hash(content)
    if test.get("content_hash") != expected_hash:
        raise FailClosedRuntimeError("generated test validation failed closed: test content hash mismatch")
    if test.get("content_size_bytes") != len(content.encode("utf-8")):
        raise FailClosedRuntimeError("generated test validation failed closed: test content size mismatch")
    if test.get("test_entry_hash") != replay_hash(_without_hash(test, "test_entry_hash")):
        raise FailClosedRuntimeError("generated test validation failed closed: test entry hash mismatch")
    linked_file_ids = _string_list(test.get("tests_file_entries"), "tests_file_entries", allow_empty=False)
    linked_targets = []
    for file_id in linked_file_ids:
        implementation_file = implementation_files.get(file_id)
        if implementation_file is None:
            raise FailClosedRuntimeError(
                "generated test validation failed closed: test references unknown implementation file"
            )
        linked_targets.append(implementation_file["target_path"])
    coverage_target = _require_string(test.get("expected_coverage_target"), "expected_coverage_target")
    if coverage_target not in linked_targets:
        raise FailClosedRuntimeError(
            "generated test validation failed closed: expected coverage target is not linked"
        )
    _require_string(test.get("validation_command"), "validation_command")
    _require_string(test.get("negative_case_requirement"), "negative_case_requirement")
    if "fixture_references" in test:
        _string_list(test["fixture_references"], "fixture_references", allow_empty=True)
    _require_false_authority_flags(test.get("authority_flags"))
    return {
        "test_entry_id": test["test_entry_id"],
        "target_path": target_path,
        "artifact_type": artifact_type,
        "operation": CREATE_ONLY,
        "content_hash": expected_hash,
        "test_entry_hash": test["test_entry_hash"],
        "tests_file_entries": linked_file_ids,
        "linked_implementation_targets": sorted(linked_targets),
        "expected_coverage_target": coverage_target,
        "test_artifact_present": True,
        "test_hash_valid": True,
        "test_path_valid": True,
        "test_artifact_type_valid": True,
        "manifest_to_test_consistency_valid": True,
        "implementation_to_test_linkage_valid": True,
        "authority_preserved": True,
    }


def _validation_checks(manifest: dict[str, Any], test_results: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        "test_artifact_presence_valid": len(test_results) == manifest["test_count"],
        "test_artifact_hashes_valid": all(result["test_hash_valid"] for result in test_results),
        "test_artifact_paths_valid": all(result["test_path_valid"] for result in test_results),
        "test_artifact_types_valid": all(result["test_artifact_type_valid"] for result in test_results),
        "manifest_to_test_consistency_valid": all(
            result["manifest_to_test_consistency_valid"] for result in test_results
        ),
        "implementation_to_test_linkage_valid": all(
            result["implementation_to_test_linkage_valid"] for result in test_results
        ),
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "approval_creation_absent": True,
        "execution_authorization_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "test_artifact_presence_valid": False,
        "test_artifact_hashes_valid": False,
        "test_artifact_paths_valid": False,
        "test_artifact_types_valid": False,
        "manifest_to_test_consistency_valid": False,
        "implementation_to_test_linkage_valid": False,
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
    value.pop("generated_test_validation_hash", None)
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


def _verify_manifest_artifact_hash(manifest: dict[str, Any]) -> None:
    actual = manifest.get("artifact_hash")
    expected_input = deepcopy(manifest)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated test validation failed closed: manifest artifact hash mismatch")


def _without_hash(entry: dict[str, Any], field_name: str) -> dict[str, Any]:
    value = deepcopy(entry)
    value.pop(field_name, None)
    return value


def _normalize_test_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    if path_text.startswith("/") or "\\" in path_text:
        raise FailClosedRuntimeError("generated test validation failed closed: invalid test path")
    path = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("generated test validation failed closed: invalid test path")
    normalized = path.as_posix()
    if not any(normalized.startswith(prefix) for prefix in ALLOWED_TEST_TARGET_PREFIXES):
        raise FailClosedRuntimeError("generated test validation failed closed: test path is not allowed")
    return normalized


def _require_allowed_test_artifact_type(value: Any) -> str:
    artifact_type = _require_string(value, "artifact_type")
    if artifact_type not in ALLOWED_TEST_ARTIFACT_TYPES:
        raise FailClosedRuntimeError("generated test validation failed closed: test artifact type is not allowed")
    return artifact_type


def _require_false_authority_flags(value: Any) -> None:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated test validation failed closed: authority flags missing")
    if any(flag_value is not False for flag_value in value.values()):
        raise FailClosedRuntimeError("generated test validation failed closed: authority flag must be false")


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"generated test validation failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"generated test validation failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"generated test validation failed closed: {label} missing")
    return value.strip()


def _require_content(value: Any) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError("generated test validation failed closed: test content missing")
    return value


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "generated test validation failed closed"


__all__ = [
    "AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_STATUS",
    "AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "GENERATED_TEST_VALIDATED",
    "GENERATED_TEST_VALIDATION_ARTIFACT_V1",
    "validate_generated_tests",
    "verify_generated_test_validation_artifact",
]
