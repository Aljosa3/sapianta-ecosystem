"""Final pre-mutation authorization gate for generated implementation bundles."""

from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any

from aigol.runtime.generated_content_acceptance_runtime import (
    GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1,
    GENERATED_CONTENT_ACCEPTED,
    verify_generated_content_acceptance_artifact,
)
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


AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_VERSION = (
    "AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_V1"
)
FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1 = "FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1"
AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_STATUS = "CERTIFIED"
FILESYSTEM_MUTATION_AUTHORIZED = "FILESYSTEM_MUTATION_AUTHORIZED"
FAILED_CLOSED = "FAILED_CLOSED"

AUTHORIZATION_DECISION = "AUTHORIZED"
AUTHORIZATION_SCOPE = "FILESYSTEM_MUTATION_AUTHORIZATION_ONLY"
AUTHORIZATION_STATEMENT = (
    "I authorize CREATE_ONLY filesystem mutation for the exact bound paths and content hashes."
)

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION_EXECUTION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "EXECUTION_AUTHORIZATION",
    "DISPATCH",
    "AUTOMATIC_AUTHORIZATION_INFERENCE",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
    "DELETE",
    "UPDATE_ONLY",
    "REPLACE_ONLY",
    "RENAME",
    "MOVE",
    "RECURSIVE_CREATE",
)

AUTHORITY_FLAGS = {
    "authorizes_filesystem_mutation": True,
    "performs_filesystem_mutation": False,
    "authorizes_provider_invocation": False,
    "authorizes_worker_invocation": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "infers_authorization_automatically": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
}


def authorize_filesystem_mutation(
    *,
    authorization_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_content_validation_artifact: dict[str, Any],
    generated_test_validation_artifact: dict[str, Any],
    generated_content_acceptance_artifact: dict[str, Any],
    human_authorization_evidence: dict[str, Any],
    created_at: str,
    prior_authorization_lineage_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Authorize exact CREATE_ONLY filesystem mutation without performing it."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        content_validation = _validate_content_validation(generated_content_validation_artifact, manifest)
        test_validation = _validate_test_validation(generated_test_validation_artifact, manifest)
        acceptance = _validate_acceptance(
            generated_content_acceptance_artifact,
            manifest,
            content_validation,
            test_validation,
        )
        human = _validate_human_authorization(human_authorization_evidence)
        authorized_permissions = _authorized_permissions(manifest)
        authorization_lineage_key = _authorization_lineage_key(
            manifest,
            content_validation,
            test_validation,
            acceptance,
        )
        if authorization_lineage_key in _string_list(
            prior_authorization_lineage_keys or [],
            "prior_authorization_lineage_keys",
            allow_empty=True,
        ):
            raise FailClosedRuntimeError(
                "filesystem mutation authorization failed closed: authorization lineage already used"
            )
        checks = _validation_checks()
        status = FILESYSTEM_MUTATION_AUTHORIZED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        content_validation = _validation_stub(generated_content_validation_artifact, "generated_content_validation_hash")
        test_validation = _validation_stub(generated_test_validation_artifact, "generated_test_validation_hash")
        acceptance = _validation_stub(generated_content_acceptance_artifact, "generated_content_acceptance_hash")
        human = _human_stub(human_authorization_evidence)
        authorized_permissions = []
        authorization_lineage_key = "UNKNOWN"
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_id": _safe_string(authorization_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "authorization_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "generated_content_validation_reference": content_validation["validation_id"],
        "generated_content_validation_artifact_hash": content_validation["artifact_hash"],
        "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
        "generated_test_validation_reference": test_validation["validation_id"],
        "generated_test_validation_artifact_hash": test_validation["artifact_hash"],
        "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
        "generated_content_acceptance_reference": acceptance["acceptance_id"],
        "generated_content_acceptance_artifact_hash": acceptance["artifact_hash"],
        "generated_content_acceptance_hash": acceptance["generated_content_acceptance_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "authorized_permissions": authorized_permissions,
        "authorized_permission_count": len(authorized_permissions),
        "authorization_lineage_key": authorization_lineage_key,
        "authorization_reuse_prohibited": True,
        "authorization_scope": human["authorization_scope"],
        "human_actor_id": human["actor_id"],
        "human_decision": human["decision"],
        "human_authorized_at": human["authorized_at"],
        "human_authorization_statement": human["authorization_statement"],
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutation_authorized": status == FILESYSTEM_MUTATION_AUTHORIZED,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_authorization_inferred": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    if status != FILESYSTEM_MUTATION_AUTHORIZED:
        artifact["authority_flags"]["authorizes_filesystem_mutation"] = False
    artifact["filesystem_mutation_authorization_hash"] = _compute_authorization_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "filesystem_mutation_authorization_artifact": deepcopy(artifact),
        "filesystem_mutation_authorization_hash": artifact["filesystem_mutation_authorization_hash"],
        "authorization_lineage_key": artifact["authorization_lineage_key"],
        "authorization_status": artifact["authorization_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "authorized_permissions": deepcopy(artifact["authorized_permissions"]),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutation_authorized": artifact["filesystem_mutation_authorized"],
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_authorization_inferred": False,
        "fail_closed": artifact["authorization_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_STATUS = "
            f"{AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_STATUS}"
        ),
    }


def verify_filesystem_mutation_authorization_artifact(artifact: dict[str, Any]) -> None:
    """Verify a filesystem mutation authorization artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization artifact must be a JSON object")
    if artifact.get("artifact_type") != FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation authorization artifact type mismatch")
    actual_authorization_hash = artifact.get("filesystem_mutation_authorization_hash")
    if actual_authorization_hash != _compute_authorization_hash(artifact):
        raise FailClosedRuntimeError("filesystem mutation authorization hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("filesystem mutation authorization artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: manifest must be CREATE_ONLY")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: manifest hash mismatch")
    if not isinstance(manifest.get("file_entries"), list) or not manifest["file_entries"]:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: implementation files are required")
    if not isinstance(manifest.get("test_entries"), list):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: test entries must be a list")
    return manifest


def _validate_content_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: content validation missing")
    validation = deepcopy(artifact)
    verify_generated_content_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_CONTENT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid content validation artifact")
    if validation.get("validation_status") != GENERATED_CONTENT_VALIDATED:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: content validation not successful")
    _require_manifest_binding(validation, manifest, "content validation")
    return validation


def _validate_test_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: test validation missing")
    validation = deepcopy(artifact)
    verify_generated_test_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_TEST_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid test validation artifact")
    if validation.get("validation_status") != GENERATED_TEST_VALIDATED:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: test validation not successful")
    _require_manifest_binding(validation, manifest, "test validation")
    return validation


def _validate_acceptance(
    artifact: dict[str, Any],
    manifest: dict[str, Any],
    content_validation: dict[str, Any],
    test_validation: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: acceptance missing")
    acceptance = deepcopy(artifact)
    verify_generated_content_acceptance_artifact(acceptance)
    if acceptance.get("artifact_type") != GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid acceptance artifact")
    if acceptance.get("acceptance_status") != GENERATED_CONTENT_ACCEPTED:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: content acceptance not successful")
    _require_manifest_binding(acceptance, manifest, "acceptance")
    if acceptance.get("generated_content_validation_hash") != content_validation["generated_content_validation_hash"]:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: acceptance content validation mismatch")
    if acceptance.get("generated_content_validation_artifact_hash") != content_validation["artifact_hash"]:
        raise FailClosedRuntimeError(
            "filesystem mutation authorization failed closed: acceptance content validation artifact mismatch"
        )
    if acceptance.get("generated_test_validation_hash") != test_validation["generated_test_validation_hash"]:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: acceptance test validation mismatch")
    if acceptance.get("generated_test_validation_artifact_hash") != test_validation["artifact_hash"]:
        raise FailClosedRuntimeError(
            "filesystem mutation authorization failed closed: acceptance test validation artifact mismatch"
        )
    return acceptance


def _require_manifest_binding(artifact: dict[str, Any], manifest: dict[str, Any], label: str) -> None:
    if artifact.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError(
            f"filesystem mutation authorization failed closed: {label} manifest reference mismatch"
        )
    if artifact.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(
            f"filesystem mutation authorization failed closed: {label} manifest artifact hash mismatch"
        )
    if artifact.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError(
            f"filesystem mutation authorization failed closed: {label} manifest hash mismatch"
        )
    if artifact.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} chain mismatch")
    if artifact.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} bundle mismatch")


def _validate_human_authorization(evidence: dict[str, Any]) -> dict[str, str]:
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: human authorization evidence missing")
    actor_id = _require_string(evidence.get("actor_id"), "actor_id")
    decision = _require_string(evidence.get("decision"), "decision")
    authorized_at = _require_string(evidence.get("authorized_at"), "authorized_at")
    authorization_scope = _require_string(evidence.get("authorization_scope"), "authorization_scope")
    authorization_statement = _require_string(evidence.get("authorization_statement"), "authorization_statement")
    if decision != AUTHORIZATION_DECISION:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: human authorization decision required")
    if authorization_scope != AUTHORIZATION_SCOPE:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: authorization scope mismatch")
    if authorization_statement != AUTHORIZATION_STATEMENT:
        raise FailClosedRuntimeError(
            "filesystem mutation authorization failed closed: explicit authorization statement required"
        )
    return {
        "actor_id": actor_id,
        "decision": decision,
        "authorized_at": authorized_at,
        "authorization_scope": authorization_scope,
        "authorization_statement": authorization_statement,
    }


def _authorized_permissions(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    seen_paths: set[str] = set()
    for entry in manifest["file_entries"]:
        entries.append(_permission_from_file_entry(entry, seen_paths))
    for entry in manifest["test_entries"]:
        entries.append(_permission_from_test_entry(entry, seen_paths))
    return sorted(entries, key=lambda item: item["target_path"])


def _permission_from_file_entry(entry: dict[str, Any], seen_paths: set[str]) -> dict[str, Any]:
    path = _normalize_target_path(entry.get("target_path"))
    _require_unique_path(path, seen_paths)
    if entry.get("operation") != CREATE_ONLY:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: file operation must be CREATE_ONLY")
    if entry.get("preflight_target_state") != "MUST_NOT_EXIST":
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: CREATE_ONLY target must not exist")
    content_hash = _require_hash(entry.get("content_hash"), "content_hash")
    if entry.get("content_hash") != replay_hash(_require_content(entry.get("content"))):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: file content hash mismatch")
    return {
        "entry_kind": "IMPLEMENTATION_FILE",
        "entry_id": _require_string(entry.get("file_entry_id"), "file_entry_id"),
        "target_path": path,
        "artifact_type": _require_string(entry.get("artifact_type"), "artifact_type"),
        "operation": CREATE_ONLY,
        "content_hash": content_hash,
        "content_size_bytes": entry.get("content_size_bytes"),
        "required_preflight_target_state": "MUST_NOT_EXIST",
    }


def _permission_from_test_entry(entry: dict[str, Any], seen_paths: set[str]) -> dict[str, Any]:
    path = _normalize_target_path(entry.get("target_path"))
    _require_unique_path(path, seen_paths)
    if entry.get("operation") != CREATE_ONLY:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: test operation must be CREATE_ONLY")
    content_hash = _require_hash(entry.get("content_hash"), "content_hash")
    if entry.get("content_hash") != replay_hash(_require_content(entry.get("content"))):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: test content hash mismatch")
    return {
        "entry_kind": "GENERATED_TEST",
        "entry_id": _require_string(entry.get("test_entry_id"), "test_entry_id"),
        "target_path": path,
        "artifact_type": _require_string(entry.get("artifact_type"), "artifact_type"),
        "operation": CREATE_ONLY,
        "content_hash": content_hash,
        "content_size_bytes": entry.get("content_size_bytes"),
        "required_preflight_target_state": "MUST_NOT_EXIST",
    }


def _authorization_lineage_key(
    manifest: dict[str, Any],
    content_validation: dict[str, Any],
    test_validation: dict[str, Any],
    acceptance: dict[str, Any],
) -> str:
    return replay_hash(
        {
            "implementation_manifest_hash": manifest["implementation_manifest_hash"],
            "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
            "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
            "generated_content_acceptance_hash": acceptance["generated_content_acceptance_hash"],
        }
    )


def _validation_checks() -> dict[str, bool]:
    return {
        "accepted_bundle_binding_valid": True,
        "manifest_binding_valid": True,
        "content_validation_binding_valid": True,
        "test_validation_binding_valid": True,
        "acceptance_binding_valid": True,
        "create_only_permissions_valid": True,
        "exact_paths_valid": True,
        "exact_content_hashes_valid": True,
        "authorization_reuse_prevented": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_authorization_inference_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "accepted_bundle_binding_valid": False,
        "manifest_binding_valid": False,
        "content_validation_binding_valid": False,
        "test_validation_binding_valid": False,
        "acceptance_binding_valid": False,
        "create_only_permissions_valid": False,
        "exact_paths_valid": False,
        "exact_content_hashes_valid": False,
        "authorization_reuse_prevented": False,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_authorization_inference_absent": True,
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


def _validation_stub(value: Any, hash_field: str) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "validation_id": _safe_string(value.get("validation_id"), "UNKNOWN"),
            "acceptance_id": _safe_string(value.get("acceptance_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            hash_field: _safe_string(value.get(hash_field), "UNKNOWN"),
        }
    return {
        "validation_id": "UNKNOWN",
        "acceptance_id": "UNKNOWN",
        "artifact_hash": "UNKNOWN",
        hash_field: "UNKNOWN",
    }


def _human_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "actor_id": _safe_string(value.get("actor_id"), "UNKNOWN"),
            "decision": _safe_string(value.get("decision"), "UNKNOWN"),
            "authorized_at": _safe_string(value.get("authorized_at"), "UNKNOWN"),
            "authorization_scope": _safe_string(value.get("authorization_scope"), "UNKNOWN"),
            "authorization_statement": _safe_string(value.get("authorization_statement"), "UNKNOWN"),
        }
    return {
        "actor_id": "UNKNOWN",
        "decision": "UNKNOWN",
        "authorized_at": "UNKNOWN",
        "authorization_scope": "UNKNOWN",
        "authorization_statement": "UNKNOWN",
    }


def _compute_authorization_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("filesystem_mutation_authorization_hash", None)
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
        raise FailClosedRuntimeError(
            f"filesystem mutation authorization failed closed: {label} artifact hash mismatch"
        )


def _normalize_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    if path_text.startswith("/") or "\\" in path_text:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid target path")
    path = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: invalid target path")
    return path.as_posix()


def _require_unique_path(path: str, seen_paths: set[str]) -> None:
    if path in seen_paths:
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: duplicate target path")
    seen_paths.add(path)


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_hash(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} must be a sha256 hash")
    return text


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"filesystem mutation authorization failed closed: {label} missing")
    return value.strip()


def _require_content(value: Any) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError("filesystem mutation authorization failed closed: content missing")
    return value


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "filesystem mutation authorization failed closed"


__all__ = [
    "AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_STATUS",
    "AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_VERSION",
    "AUTHORIZATION_DECISION",
    "AUTHORIZATION_SCOPE",
    "AUTHORIZATION_STATEMENT",
    "FAILED_CLOSED",
    "FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1",
    "FILESYSTEM_MUTATION_AUTHORIZED",
    "authorize_filesystem_mutation",
    "verify_filesystem_mutation_authorization_artifact",
]
