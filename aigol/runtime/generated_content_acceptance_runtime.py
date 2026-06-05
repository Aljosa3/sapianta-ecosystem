"""Human acceptance gate for validated generated implementation content."""

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


AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION = "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_V1"
GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1 = "GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1"
AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS = "CERTIFIED"
GENERATED_CONTENT_ACCEPTED = "GENERATED_CONTENT_ACCEPTED"
FAILED_CLOSED = "FAILED_CLOSED"

ACCEPTANCE_DECISION = "ACCEPTED"
ACCEPTANCE_SCOPE = "CONTENT_ACCEPTANCE_ONLY"
ACCEPTANCE_STATEMENT = (
    "I accept this generated content for the bound implementation manifest and validation evidence."
)

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "EXECUTION_AUTHORIZATION",
    "DISPATCH",
    "AUTOMATIC_APPROVAL_INFERENCE",
    "APPROVAL_CREATION",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
)

AUTHORITY_FLAGS = {
    "authorizes_filesystem_mutation": False,
    "authorizes_provider_invocation": False,
    "authorizes_worker_invocation": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "infers_approval_automatically": False,
    "creates_approval": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
}


def accept_generated_content(
    *,
    acceptance_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_content_validation_artifact: dict[str, Any],
    generated_test_validation_artifact: dict[str, Any],
    human_acceptance_evidence: dict[str, Any],
    created_at: str,
    prior_acceptance_lineage_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Create a non-authorizing human acceptance artifact for validated generated content."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        content_validation = _validate_content_validation(generated_content_validation_artifact, manifest)
        test_validation = _validate_test_validation(generated_test_validation_artifact, manifest)
        human = _validate_human_acceptance(human_acceptance_evidence)
        acceptance_lineage_key = _acceptance_lineage_key(manifest, content_validation, test_validation)
        if acceptance_lineage_key in _string_list(
            prior_acceptance_lineage_keys or [],
            "prior_acceptance_lineage_keys",
            allow_empty=True,
        ):
            raise FailClosedRuntimeError("generated content acceptance failed closed: acceptance lineage already used")
        checks = _validation_checks()
        status = GENERATED_CONTENT_ACCEPTED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        content_validation = _validation_stub(generated_content_validation_artifact, "generated_content_validation_hash")
        test_validation = _validation_stub(generated_test_validation_artifact, "generated_test_validation_hash")
        human = _human_stub(human_acceptance_evidence)
        acceptance_lineage_key = "UNKNOWN"
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1,
        "runtime_version": AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION,
        "acceptance_id": _safe_string(acceptance_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "acceptance_status": status,
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
        "operation_mode": manifest["operation_mode"],
        "acceptance_lineage_key": acceptance_lineage_key,
        "acceptance_reuse_prohibited": True,
        "acceptance_scope": human["acceptance_scope"],
        "human_actor_id": human["actor_id"],
        "human_decision": human["decision"],
        "human_accepted_at": human["accepted_at"],
        "human_acceptance_statement": human["acceptance_statement"],
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_approval_inferred": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["generated_content_acceptance_hash"] = _compute_acceptance_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "generated_content_acceptance_artifact": deepcopy(artifact),
        "generated_content_acceptance_hash": artifact["generated_content_acceptance_hash"],
        "acceptance_lineage_key": artifact["acceptance_lineage_key"],
        "acceptance_status": artifact["acceptance_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_approval_inferred": False,
        "fail_closed": artifact["acceptance_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS = "
            f"{AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS}"
        ),
    }


def verify_generated_content_acceptance_artifact(artifact: dict[str, Any]) -> None:
    """Verify a generated-content acceptance artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance artifact must be a JSON object")
    if artifact.get("artifact_type") != GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated content acceptance artifact type mismatch")
    actual_acceptance_hash = artifact.get("generated_content_acceptance_hash")
    if actual_acceptance_hash != _compute_acceptance_hash(artifact):
        raise FailClosedRuntimeError("generated content acceptance hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated content acceptance artifact hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest is not created")
    if manifest.get("operation_mode") != CREATE_ONLY:
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest must be CREATE_ONLY")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest hash mismatch")
    return manifest


def _validate_content_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: content validation missing")
    validation = deepcopy(artifact)
    verify_generated_content_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_CONTENT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid content validation artifact")
    if validation.get("validation_status") != GENERATED_CONTENT_VALIDATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: content validation not successful")
    _require_manifest_binding(validation, manifest, "content validation")
    return validation


def _validate_test_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: test validation missing")
    validation = deepcopy(artifact)
    verify_generated_test_validation_artifact(validation)
    if validation.get("artifact_type") != GENERATED_TEST_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid test validation artifact")
    if validation.get("validation_status") != GENERATED_TEST_VALIDATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: test validation not successful")
    _require_manifest_binding(validation, manifest, "test validation")
    return validation


def _require_manifest_binding(validation: dict[str, Any], manifest: dict[str, Any], label: str) -> None:
    if validation.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest reference mismatch")
    if validation.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest artifact hash mismatch")
    if validation.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest hash mismatch")
    if validation.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} chain mismatch")
    if validation.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} bundle mismatch")


def _validate_human_acceptance(evidence: dict[str, Any]) -> dict[str, str]:
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: human acceptance evidence missing")
    actor_id = _require_string(evidence.get("actor_id"), "actor_id")
    decision = _require_string(evidence.get("decision"), "decision")
    accepted_at = _require_string(evidence.get("accepted_at"), "accepted_at")
    acceptance_scope = _require_string(evidence.get("acceptance_scope"), "acceptance_scope")
    acceptance_statement = _require_string(evidence.get("acceptance_statement"), "acceptance_statement")
    if decision != ACCEPTANCE_DECISION:
        raise FailClosedRuntimeError("generated content acceptance failed closed: human acceptance decision required")
    if acceptance_scope != ACCEPTANCE_SCOPE:
        raise FailClosedRuntimeError("generated content acceptance failed closed: acceptance scope mismatch")
    if acceptance_statement != ACCEPTANCE_STATEMENT:
        raise FailClosedRuntimeError("generated content acceptance failed closed: explicit acceptance statement required")
    return {
        "actor_id": actor_id,
        "decision": decision,
        "accepted_at": accepted_at,
        "acceptance_scope": acceptance_scope,
        "acceptance_statement": acceptance_statement,
    }


def _acceptance_lineage_key(
    manifest: dict[str, Any],
    content_validation: dict[str, Any],
    test_validation: dict[str, Any],
) -> str:
    return replay_hash(
        {
            "implementation_manifest_hash": manifest["implementation_manifest_hash"],
            "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
            "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
        }
    )


def _validation_checks() -> dict[str, bool]:
    return {
        "manifest_binding_valid": True,
        "content_validation_binding_valid": True,
        "test_validation_binding_valid": True,
        "human_acceptance_explicit": True,
        "acceptance_reuse_prevented": True,
        "lineage_replay_visible": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_approval_inference_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "manifest_binding_valid": False,
        "content_validation_binding_valid": False,
        "test_validation_binding_valid": False,
        "human_acceptance_explicit": False,
        "acceptance_reuse_prevented": False,
        "lineage_replay_visible": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_approval_inference_absent": True,
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
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            hash_field: _safe_string(value.get(hash_field), "UNKNOWN"),
        }
    return {"validation_id": "UNKNOWN", "artifact_hash": "UNKNOWN", hash_field: "UNKNOWN"}


def _human_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "actor_id": _safe_string(value.get("actor_id"), "UNKNOWN"),
            "decision": _safe_string(value.get("decision"), "UNKNOWN"),
            "accepted_at": _safe_string(value.get("accepted_at"), "UNKNOWN"),
            "acceptance_scope": _safe_string(value.get("acceptance_scope"), "UNKNOWN"),
            "acceptance_statement": _safe_string(value.get("acceptance_statement"), "UNKNOWN"),
        }
    return {
        "actor_id": "UNKNOWN",
        "decision": "UNKNOWN",
        "accepted_at": "UNKNOWN",
        "acceptance_scope": "UNKNOWN",
        "acceptance_statement": "UNKNOWN",
    }


def _compute_acceptance_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("generated_content_acceptance_hash", None)
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
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} artifact hash mismatch")


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} missing")
    return value.strip()


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "generated content acceptance failed closed"


__all__ = [
    "ACCEPTANCE_DECISION",
    "ACCEPTANCE_SCOPE",
    "ACCEPTANCE_STATEMENT",
    "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS",
    "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1",
    "GENERATED_CONTENT_ACCEPTED",
    "accept_generated_content",
    "verify_generated_content_acceptance_artifact",
]
