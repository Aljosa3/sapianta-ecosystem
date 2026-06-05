"""Final replay-visible certification for materialized implementation bundles."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.filesystem_mutation_authorization_runtime import (
    FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1,
    FILESYSTEM_MUTATION_AUTHORIZED,
    verify_filesystem_mutation_authorization_artifact,
)
from aigol.runtime.filesystem_mutation_runtime import (
    FILESYSTEM_MUTATION_ARTIFACT_V1,
    FILESYSTEM_MUTATION_COMPLETED,
    verify_filesystem_mutation_artifact,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1,
    GENERATED_CONTENT_ACCEPTED,
    verify_generated_content_acceptance_artifact,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_VERSION = "AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_V1"
IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1 = "IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1"
AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_STATUS = "CERTIFIED"
IMPLEMENTATION_CERTIFIED = "IMPLEMENTATION_CERTIFIED"
FAILED_CLOSED = "FAILED_CLOSED"

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "EXECUTION_AUTHORIZATION",
    "GOVERNANCE_MUTATION",
)

AUTHORITY_FLAGS = {
    "performs_filesystem_mutation": False,
    "invokes_provider": False,
    "invokes_worker": False,
    "authorizes_execution": False,
    "mutates_governance": False,
    "mutates_replay": False,
}


def certify_implementation(
    *,
    certification_id: str,
    implementation_manifest_artifact: dict[str, Any],
    filesystem_mutation_authorization_artifact: dict[str, Any],
    generated_content_acceptance_artifact: dict[str, Any],
    filesystem_mutation_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Certify post-materialization continuity without further mutation."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        authorization = _validate_authorization(filesystem_mutation_authorization_artifact, manifest)
        acceptance = _validate_acceptance(generated_content_acceptance_artifact, manifest, authorization)
        mutation = _validate_mutation(filesystem_mutation_artifact, manifest, authorization)
        certified_paths = _certified_paths(manifest, authorization, mutation)
        checks = _validation_checks()
        status = IMPLEMENTATION_CERTIFIED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        authorization = _authorization_stub(filesystem_mutation_authorization_artifact)
        acceptance = _acceptance_stub(generated_content_acceptance_artifact)
        mutation = _mutation_stub(filesystem_mutation_artifact)
        certified_paths = []
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_VERSION,
        "certification_id": _safe_string(certification_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "certification_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "filesystem_mutation_authorization_reference": authorization["authorization_id"],
        "filesystem_mutation_authorization_artifact_hash": authorization["artifact_hash"],
        "filesystem_mutation_authorization_hash": authorization["filesystem_mutation_authorization_hash"],
        "generated_content_acceptance_reference": acceptance["acceptance_id"],
        "generated_content_acceptance_artifact_hash": acceptance["artifact_hash"],
        "generated_content_acceptance_hash": acceptance["generated_content_acceptance_hash"],
        "filesystem_mutation_reference": mutation["mutation_id"],
        "filesystem_mutation_artifact_hash": mutation["artifact_hash"],
        "filesystem_mutation_hash": mutation["filesystem_mutation_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "certified_paths": certified_paths,
        "certified_path_count": len(certified_paths),
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "governance_mutated": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["implementation_certification_hash"] = _compute_certification_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "implementation_certification_artifact": deepcopy(artifact),
        "implementation_certification_hash": artifact["implementation_certification_hash"],
        "certification_status": artifact["certification_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "certified_path_count": artifact["certified_path_count"],
        "certified_paths": deepcopy(artifact["certified_paths"]),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "governance_mutated": False,
        "fail_closed": artifact["certification_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_STATUS = "
            f"{AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_STATUS}"
        ),
    }


def verify_implementation_certification_artifact(artifact: dict[str, Any]) -> None:
    """Verify an implementation certification artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation certification artifact must be a JSON object")
    if artifact.get("artifact_type") != IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation certification artifact type mismatch")
    actual_certification_hash = artifact.get("implementation_certification_hash")
    if actual_certification_hash != _compute_certification_hash(artifact):
        raise FailClosedRuntimeError("implementation certification hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation certification artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("implementation certification failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation certification failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("implementation certification failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("implementation certification failed closed: manifest must be CREATE_ONLY")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("implementation certification failed closed: manifest hash mismatch")
    return manifest


def _validate_authorization(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation certification failed closed: authorization must be a JSON object")
    authorization = deepcopy(artifact)
    verify_filesystem_mutation_authorization_artifact(authorization)
    if authorization.get("artifact_type") != FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation certification failed closed: invalid authorization artifact")
    if authorization.get("authorization_status") != FILESYSTEM_MUTATION_AUTHORIZED:
        raise FailClosedRuntimeError("implementation certification failed closed: authorization not successful")
    _require_manifest_binding(authorization, manifest, "authorization")
    return authorization


def _validate_acceptance(
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation certification failed closed: acceptance must be a JSON object")
    acceptance = deepcopy(artifact)
    verify_generated_content_acceptance_artifact(acceptance)
    if acceptance.get("artifact_type") != GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation certification failed closed: invalid acceptance artifact")
    if acceptance.get("acceptance_status") != GENERATED_CONTENT_ACCEPTED:
        raise FailClosedRuntimeError("implementation certification failed closed: acceptance not successful")
    _require_manifest_binding(acceptance, manifest, "acceptance")
    if acceptance.get("generated_content_acceptance_hash") != authorization.get("generated_content_acceptance_hash"):
        raise FailClosedRuntimeError("implementation certification failed closed: authorization acceptance hash mismatch")
    if acceptance.get("artifact_hash") != authorization.get("generated_content_acceptance_artifact_hash"):
        raise FailClosedRuntimeError("implementation certification failed closed: authorization acceptance artifact mismatch")
    return acceptance


def _validate_mutation(
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation certification failed closed: mutation must be a JSON object")
    mutation = deepcopy(artifact)
    verify_filesystem_mutation_artifact(mutation)
    if mutation.get("artifact_type") != FILESYSTEM_MUTATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation certification failed closed: invalid mutation artifact")
    if mutation.get("mutation_status") != FILESYSTEM_MUTATION_COMPLETED:
        raise FailClosedRuntimeError("implementation certification failed closed: mutation not completed")
    _require_manifest_binding(mutation, manifest, "mutation")
    if mutation.get("filesystem_mutation_authorization_hash") != authorization["filesystem_mutation_authorization_hash"]:
        raise FailClosedRuntimeError("implementation certification failed closed: mutation authorization hash mismatch")
    if mutation.get("filesystem_mutation_authorization_artifact_hash") != authorization["artifact_hash"]:
        raise FailClosedRuntimeError("implementation certification failed closed: mutation authorization artifact mismatch")
    return mutation


def _require_manifest_binding(artifact: dict[str, Any], manifest: dict[str, Any], label: str) -> None:
    if artifact.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError(
            f"implementation certification failed closed: {label} manifest reference mismatch"
        )
    if artifact.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(
            f"implementation certification failed closed: {label} manifest artifact hash mismatch"
        )
    if artifact.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError(f"implementation certification failed closed: {label} manifest hash mismatch")
    if artifact.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError(f"implementation certification failed closed: {label} chain mismatch")
    if artifact.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError(f"implementation certification failed closed: {label} bundle mismatch")


def _certified_paths(
    manifest: dict[str, Any],
    authorization: dict[str, Any],
    mutation: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest_paths = _manifest_path_map(manifest)
    authorization_paths = _authorization_path_map(authorization)
    mutation_paths = _mutation_path_map(mutation)
    if set(manifest_paths) != set(authorization_paths):
        raise FailClosedRuntimeError("implementation certification failed closed: authorization path continuity mismatch")
    if set(manifest_paths) != set(mutation_paths):
        raise FailClosedRuntimeError("implementation certification failed closed: materialization path continuity mismatch")

    certified = []
    for path in sorted(manifest_paths):
        manifest_entry = manifest_paths[path]
        authorization_entry = authorization_paths[path]
        mutation_entry = mutation_paths[path]
        if authorization_entry["operation"] != CREATE_ONLY or mutation_entry["operation"] != CREATE_ONLY:
            raise FailClosedRuntimeError("implementation certification failed closed: CREATE_ONLY continuity mismatch")
        if manifest_entry["content_hash"] != authorization_entry["content_hash"]:
            raise FailClosedRuntimeError("implementation certification failed closed: authorization content hash mismatch")
        if manifest_entry["content_hash"] != mutation_entry["content_hash"]:
            raise FailClosedRuntimeError("implementation certification failed closed: mutation content hash mismatch")
        if mutation_entry["content_hash"] != mutation_entry["materialized_content_hash"]:
            raise FailClosedRuntimeError("implementation certification failed closed: materialized content hash mismatch")
        if mutation_entry.get("created") is not True:
            raise FailClosedRuntimeError("implementation certification failed closed: materialization not created")
        certified.append(
            {
                "target_path": path,
                "operation": CREATE_ONLY,
                "content_hash": manifest_entry["content_hash"],
                "materialized_content_hash": mutation_entry["materialized_content_hash"],
                "manifest_entry_kind": manifest_entry["entry_kind"],
                "authorization_entry_kind": authorization_entry["entry_kind"],
                "mutation_entry_kind": mutation_entry["entry_kind"],
            }
        )
    return certified


def _manifest_path_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for entry in manifest.get("file_entries", []):
        _add_path_entry(entries, entry, "IMPLEMENTATION_FILE")
    for entry in manifest.get("test_entries", []):
        _add_path_entry(entries, entry, "GENERATED_TEST")
    if not entries:
        raise FailClosedRuntimeError("implementation certification failed closed: manifest paths are required")
    return entries


def _add_path_entry(entries: dict[str, dict[str, Any]], entry: dict[str, Any], entry_kind: str) -> None:
    path = _require_string(entry.get("target_path"), "target_path")
    if path in entries:
        raise FailClosedRuntimeError("implementation certification failed closed: duplicate manifest path")
    entries[path] = {
        "entry_kind": entry_kind,
        "operation": _require_string(entry.get("operation"), "operation"),
        "content_hash": _require_string(entry.get("content_hash"), "content_hash"),
    }


def _authorization_path_map(authorization: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = {}
    for entry in authorization.get("authorized_permissions", []):
        path = _require_string(entry.get("target_path"), "target_path")
        if path in entries:
            raise FailClosedRuntimeError("implementation certification failed closed: duplicate authorization path")
        entries[path] = {
            "entry_kind": _require_string(entry.get("entry_kind"), "entry_kind"),
            "operation": _require_string(entry.get("operation"), "operation"),
            "content_hash": _require_string(entry.get("content_hash"), "content_hash"),
        }
    return entries


def _mutation_path_map(mutation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = {}
    for entry in mutation.get("mutation_results", []):
        path = _require_string(entry.get("target_path"), "target_path")
        if path in entries:
            raise FailClosedRuntimeError("implementation certification failed closed: duplicate mutation path")
        entries[path] = {
            "entry_kind": _require_string(entry.get("entry_kind"), "entry_kind"),
            "operation": _require_string(entry.get("operation"), "operation"),
            "content_hash": _require_string(entry.get("content_hash"), "content_hash"),
            "materialized_content_hash": _require_string(
                entry.get("materialized_content_hash"),
                "materialized_content_hash",
            ),
            "created": entry.get("created"),
        }
    return entries


def _validation_checks() -> dict[str, bool]:
    return {
        "filesystem_mutation_artifact_consumed": True,
        "filesystem_mutation_authorization_artifact_consumed": True,
        "generated_content_acceptance_artifact_consumed": True,
        "implementation_manifest_artifact_consumed": True,
        "path_continuity_valid": True,
        "content_hash_continuity_valid": True,
        "authorization_continuity_valid": True,
        "materialization_continuity_valid": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "governance_mutation_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "filesystem_mutation_artifact_consumed": False,
        "filesystem_mutation_authorization_artifact_consumed": False,
        "generated_content_acceptance_artifact_consumed": False,
        "implementation_manifest_artifact_consumed": False,
        "path_continuity_valid": False,
        "content_hash_continuity_valid": False,
        "authorization_continuity_valid": False,
        "materialization_continuity_valid": False,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "governance_mutation_absent": True,
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


def _acceptance_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "acceptance_id": _safe_string(value.get("acceptance_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "generated_content_acceptance_hash": _safe_string(
                value.get("generated_content_acceptance_hash"),
                "UNKNOWN",
            ),
        }
    return {"acceptance_id": "UNKNOWN", "artifact_hash": "UNKNOWN", "generated_content_acceptance_hash": "UNKNOWN"}


def _mutation_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "mutation_id": _safe_string(value.get("mutation_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "filesystem_mutation_hash": _safe_string(value.get("filesystem_mutation_hash"), "UNKNOWN"),
        }
    return {"mutation_id": "UNKNOWN", "artifact_hash": "UNKNOWN", "filesystem_mutation_hash": "UNKNOWN"}


def _compute_certification_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("implementation_certification_hash", None)
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
        raise FailClosedRuntimeError(f"implementation certification failed closed: {label} artifact hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation certification failed closed: {label} missing")
    return value.strip()


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "implementation certification failed closed"


__all__ = [
    "AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_STATUS",
    "AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1",
    "IMPLEMENTATION_CERTIFIED",
    "certify_implementation",
    "verify_implementation_certification_artifact",
]
