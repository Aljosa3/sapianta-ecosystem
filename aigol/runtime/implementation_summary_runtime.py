"""Operator-facing summary runtime for validated implementation candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.generated_content_validation_runtime import (
    GENERATED_CONTENT_VALIDATED,
    GENERATED_CONTENT_VALIDATION_ARTIFACT_V1,
    verify_generated_content_validation_artifact,
)
from aigol.runtime.generated_test_validation_runtime import (
    GENERATED_TEST_VALIDATED,
    GENERATED_TEST_VALIDATION_ARTIFACT_V1,
    verify_generated_test_validation_artifact,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_VERSION = "AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_V1"
IMPLEMENTATION_SUMMARY_ARTIFACT_V1 = "IMPLEMENTATION_SUMMARY_ARTIFACT_V1"
AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_STATUS = "CERTIFIED"
IMPLEMENTATION_SUMMARY_CREATED = "IMPLEMENTATION_SUMMARY_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "APPROVAL_CREATION",
    "EXECUTION_AUTHORIZATION",
    "AUTOMATIC_ACCEPTANCE",
    "DISPATCH",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
)

AUTHORITY_FLAGS = {
    "authorizes_filesystem_mutation": False,
    "authorizes_provider_invocation": False,
    "authorizes_worker_invocation": False,
    "creates_approval": False,
    "authorizes_execution": False,
    "accepts_content_automatically": False,
    "authorizes_dispatch": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
}


def create_implementation_summary(
    *,
    summary_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_content_validation_artifact: dict[str, Any],
    generated_test_validation_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create a deterministic human-readable summary before acceptance."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        content_validation = _validate_content_validation(generated_content_validation_artifact, manifest)
        test_validation = _validate_test_validation(generated_test_validation_artifact, manifest)
        purpose = _summarize_purpose(manifest)
        functionality = _summarize_functionality(manifest)
        implementation_files = _summarize_files(manifest["file_entries"])
        generated_tests = _summarize_tests(manifest["test_entries"])
        validation_outcomes = _summarize_validation_outcomes(content_validation, test_validation)
        checks = _validation_checks()
        status = IMPLEMENTATION_SUMMARY_CREATED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        content_validation = _validation_stub(generated_content_validation_artifact, "generated_content_validation_hash")
        test_validation = _validation_stub(generated_test_validation_artifact, "generated_test_validation_hash")
        purpose = "Summary unavailable because lineage validation failed."
        functionality = []
        implementation_files = []
        generated_tests = []
        validation_outcomes = []
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": IMPLEMENTATION_SUMMARY_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_VERSION,
        "summary_id": _safe_string(summary_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "summary_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "generated_content_validation_reference": content_validation["validation_id"],
        "generated_content_validation_artifact_hash": content_validation["artifact_hash"],
        "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
        "generated_test_validation_reference": test_validation["validation_id"],
        "generated_test_validation_artifact_hash": test_validation["artifact_hash"],
        "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "target_domain": manifest["target_domain"],
        "target_resource": manifest["target_resource"],
        "target_worker": manifest["target_worker"],
        "operation_mode": manifest["operation_mode"],
        "implementation_purpose": purpose,
        "planned_functionality": functionality,
        "implementation_files": implementation_files,
        "generated_tests": generated_tests,
        "validation_outcomes": validation_outcomes,
        "known_gaps": deepcopy(manifest["known_gaps"]),
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "operator_review_only": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_authorized": False,
        "automatic_acceptance_created": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["implementation_summary_hash"] = _compute_summary_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "implementation_summary_artifact": deepcopy(artifact),
        "implementation_summary_hash": artifact["implementation_summary_hash"],
        "summary_status": artifact["summary_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "read_only": True,
        "replay_visible": True,
        "operator_review_only": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_authorized": False,
        "automatic_acceptance_created": False,
        "fail_closed": artifact["summary_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_STATUS = "
            f"{AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_STATUS}"
        ),
    }


def render_implementation_summary(capture: dict[str, Any]) -> str:
    """Render the implementation summary for operator review."""

    artifact = capture.get("implementation_summary_artifact", capture)
    lines = [
        "",
        "Implementation Summary",
        "",
        str(artifact.get("implementation_purpose") or "Summary unavailable."),
        "",
        "Planned Functionality",
    ]
    lines.extend(f"- {item}" for item in artifact.get("planned_functionality", []))
    lines.extend(["", "Implementation Files"])
    lines.extend(
        f"- {item['target_path']} ({item['artifact_type']}, {item['content_hash']})"
        for item in artifact.get("implementation_files", [])
    )
    lines.extend(["", "Generated Tests"])
    lines.extend(
        f"- {item['target_path']} covers {item['expected_coverage_target']} ({item['content_hash']})"
        for item in artifact.get("generated_tests", [])
    )
    lines.extend(["", "Validation Outcomes"])
    lines.extend(f"- {item}" for item in artifact.get("validation_outcomes", []))
    if artifact.get("failure_reason"):
        lines.extend(["", f"failure_reason: {artifact['failure_reason']}"])
    return "\n".join(lines)


def verify_implementation_summary_artifact(artifact: dict[str, Any]) -> None:
    """Verify an implementation summary artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation summary artifact must be a JSON object")
    if artifact.get("artifact_type") != IMPLEMENTATION_SUMMARY_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation summary artifact type mismatch")
    actual_summary_hash = artifact.get("implementation_summary_hash")
    if actual_summary_hash != _compute_summary_hash(artifact):
        raise FailClosedRuntimeError("implementation summary hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation summary artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("implementation summary failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation summary failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("implementation summary failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("implementation summary failed closed: manifest must be CREATE_ONLY")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("implementation summary failed closed: manifest hash mismatch")
    if not isinstance(manifest.get("file_entries"), list) or not manifest["file_entries"]:
        raise FailClosedRuntimeError("implementation summary failed closed: implementation files are required")
    if not isinstance(manifest.get("test_entries"), list):
        raise FailClosedRuntimeError("implementation summary failed closed: test entries must be a list")
    return manifest


def _validate_content_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation summary failed closed: content validation missing")
    validation = deepcopy(artifact)
    verify_generated_content_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_CONTENT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation summary failed closed: invalid content validation artifact")
    if validation.get("validation_status") != GENERATED_CONTENT_VALIDATED:
        raise FailClosedRuntimeError("implementation summary failed closed: content validation not successful")
    _require_manifest_binding(validation, manifest, "content validation")
    return validation


def _validate_test_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation summary failed closed: test validation missing")
    validation = deepcopy(artifact)
    verify_generated_test_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_TEST_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation summary failed closed: invalid test validation artifact")
    if validation.get("validation_status") != GENERATED_TEST_VALIDATED:
        raise FailClosedRuntimeError("implementation summary failed closed: test validation not successful")
    _require_manifest_binding(validation, manifest, "test validation")
    return validation


def _require_manifest_binding(validation: dict[str, Any], manifest: dict[str, Any], label: str) -> None:
    if validation.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} manifest reference mismatch")
    if validation.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} manifest artifact hash mismatch")
    if validation.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} manifest hash mismatch")
    if validation.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} chain mismatch")
    if validation.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} bundle mismatch")


def _summarize_purpose(manifest: dict[str, Any]) -> str:
    worker = manifest.get("target_worker") or "unspecified worker"
    return (
        f"Review generated CREATE_ONLY implementation bundle {manifest['implementation_bundle_id']} "
        f"for {manifest['target_domain']} {manifest['target_resource']} target {worker}."
    )


def _summarize_functionality(manifest: dict[str, Any]) -> list[str]:
    file_count = len(manifest["file_entries"])
    test_count = len(manifest["test_entries"])
    validation_count = len(manifest["validation_requirements"])
    return [
        f"Plans {file_count} implementation file(s) and {test_count} generated test file(s).",
        "Restricts all planned artifact operations to CREATE_ONLY.",
        f"Carries {validation_count} validation requirement(s) for operator review.",
        "Preserves known gaps without authorizing implementation.",
    ]


def _summarize_files(file_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "file_entry_id": _require_string(entry.get("file_entry_id"), "file_entry_id"),
            "target_path": _require_string(entry.get("target_path"), "target_path"),
            "artifact_type": _require_string(entry.get("artifact_type"), "artifact_type"),
            "operation": _require_string(entry.get("operation"), "operation"),
            "content_hash": _require_string(entry.get("content_hash"), "content_hash"),
            "content_size_bytes": entry.get("content_size_bytes"),
            "validation_requirements": _string_list(
                entry.get("validation_requirements", []),
                "validation_requirements",
                allow_empty=True,
            ),
        }
        for entry in sorted(file_entries, key=lambda item: item["target_path"])
    ]


def _summarize_tests(test_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "test_entry_id": _require_string(entry.get("test_entry_id"), "test_entry_id"),
            "target_path": _require_string(entry.get("target_path"), "target_path"),
            "artifact_type": _require_string(entry.get("artifact_type"), "artifact_type"),
            "operation": _require_string(entry.get("operation"), "operation"),
            "content_hash": _require_string(entry.get("content_hash"), "content_hash"),
            "tests_file_entries": _string_list(entry.get("tests_file_entries"), "tests_file_entries", allow_empty=False),
            "validation_command": _require_string(entry.get("validation_command"), "validation_command"),
            "expected_coverage_target": _require_string(
                entry.get("expected_coverage_target"),
                "expected_coverage_target",
            ),
            "negative_case_requirement": _require_string(
                entry.get("negative_case_requirement"),
                "negative_case_requirement",
            ),
        }
        for entry in sorted(test_entries, key=lambda item: item["target_path"])
    ]


def _summarize_validation_outcomes(content_validation: dict[str, Any], test_validation: dict[str, Any]) -> list[str]:
    content_checks = content_validation.get("validation_checks", {})
    test_checks = test_validation.get("validation_checks", {})
    return [
        f"Generated content validation status: {content_validation['validation_status']}.",
        f"Generated test validation status: {test_validation['validation_status']}.",
        f"Content validation checks passed: {sum(1 for value in content_checks.values() if value is True)} of {len(content_checks)}.",
        f"Test validation checks passed: {sum(1 for value in test_checks.values() if value is True)} of {len(test_checks)}.",
        "Summary creates no acceptance, approval, execution, or filesystem mutation authority.",
    ]


def _validation_checks() -> dict[str, bool]:
    return {
        "manifest_lineage_valid": True,
        "content_validation_lineage_valid": True,
        "test_validation_lineage_valid": True,
        "summary_hash_deterministic": True,
        "operator_review_only": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "approval_creation_absent": True,
        "execution_authorization_absent": True,
        "automatic_acceptance_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "manifest_lineage_valid": False,
        "content_validation_lineage_valid": False,
        "test_validation_lineage_valid": False,
        "summary_hash_deterministic": False,
        "operator_review_only": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "approval_creation_absent": True,
        "execution_authorization_absent": True,
        "automatic_acceptance_absent": True,
    }


def _manifest_stub(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "manifest_id": _safe_string(value.get("manifest_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "implementation_manifest_hash": _safe_string(value.get("implementation_manifest_hash"), "UNKNOWN"),
            "canonical_chain_id": _safe_string(value.get("canonical_chain_id"), "UNKNOWN"),
            "implementation_bundle_id": _safe_string(value.get("implementation_bundle_id"), "UNKNOWN"),
            "target_domain": _safe_string(value.get("target_domain"), "UNKNOWN"),
            "target_resource": _safe_string(value.get("target_resource"), "UNKNOWN"),
            "target_worker": value.get("target_worker") if isinstance(value.get("target_worker"), str) else None,
            "operation_mode": _safe_string(value.get("operation_mode"), "UNKNOWN"),
            "known_gaps": value.get("known_gaps") if isinstance(value.get("known_gaps"), list) else [],
        }
    return {
        "manifest_id": "UNKNOWN",
        "artifact_hash": "UNKNOWN",
        "implementation_manifest_hash": "UNKNOWN",
        "canonical_chain_id": "UNKNOWN",
        "implementation_bundle_id": "UNKNOWN",
        "target_domain": "UNKNOWN",
        "target_resource": "UNKNOWN",
        "target_worker": None,
        "operation_mode": "UNKNOWN",
        "known_gaps": [],
    }


def _validation_stub(value: Any, hash_field: str) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "validation_id": _safe_string(value.get("validation_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            hash_field: _safe_string(value.get(hash_field), "UNKNOWN"),
        }
    return {"validation_id": "UNKNOWN", "artifact_hash": "UNKNOWN", hash_field: "UNKNOWN"}


def _compute_summary_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("implementation_summary_hash", None)
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
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} artifact hash mismatch")


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation summary failed closed: {label} missing")
    return value.strip()


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "implementation summary failed closed"


__all__ = [
    "AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_STATUS",
    "AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "IMPLEMENTATION_SUMMARY_ARTIFACT_V1",
    "IMPLEMENTATION_SUMMARY_CREATED",
    "create_implementation_summary",
    "render_implementation_summary",
    "verify_implementation_summary_artifact",
]
