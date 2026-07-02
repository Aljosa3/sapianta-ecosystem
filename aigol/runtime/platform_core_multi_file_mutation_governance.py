"""Governance-owned approval and authorization for multi-file mutation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_multi_file_mutation_candidate import (
    MULTI_FILE_MUTATION_CANDIDATE_ARTIFACT_V1,
    validate_multi_file_mutation_candidate,
)
from aigol.runtime.transport.serialization import replay_hash


MULTI_FILE_MUTATION_GOVERNANCE_VERSION = "G9_11_GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTATION_V1"
MULTI_FILE_MUTATION_APPROVAL_ARTIFACT_V1 = "MULTI_FILE_MUTATION_APPROVAL_ARTIFACT_V1"
MULTI_FILE_MUTATION_AUTHORIZATION_ARTIFACT_V1 = "MULTI_FILE_MUTATION_AUTHORIZATION_ARTIFACT_V1"


def create_multi_file_mutation_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to the exact transaction candidate hash."""

    candidate = validate_multi_file_mutation_candidate(candidate_artifact)
    expected = f"confirm multi-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed = _require_string(confirmation_text, "confirmation_text").strip()
    if observed != expected:
        raise FailClosedRuntimeError("multi-file mutation failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": MULTI_FILE_MUTATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "operation_count": candidate["operation_count"],
        "target_paths": deepcopy(candidate["target_paths"]),
        "operation_hashes": [record["single_file_candidate_hash"] for record in candidate["operations"]],
        "confirmation_text": observed,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "transaction_scope_bound": True,
        "automatic_rollback_authorized": False,
        "git_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "dependency_installation_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_multi_file_mutation_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != MULTI_FILE_MUTATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval candidate mismatch")
    expected = f"confirm multi-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected:
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval confirmation mismatch")
    if artifact.get("target_paths") != candidate["target_paths"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: approval file-set mismatch")
    for field in (
        "approval_bypassed",
        "automatic_rollback_authorized",
        "git_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "dependency_installation_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"multi-file mutation failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("multi-file mutation failed closed: human authority invalid")
    return artifact


def create_multi_file_mutation_authorization_artifact(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create per-operation Worker authorization records from one approved transaction."""

    validated_candidate = validate_multi_file_mutation_candidate(candidate)
    validated_approval = validate_multi_file_mutation_approval(approval, validated_candidate)
    authorizations = []
    for record in validated_candidate["operations"]:
        authorization = create_authorization_record(
            authorization_id=f"{_require_string(authorization_id, 'authorization_id')}:{record['operation_id']}",
            proposal_id=validated_candidate["candidate_id"],
            worker_id=record["worker_id"],
            authorization_scope=record["worker_scope"],
            authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
        ).to_dict()
        authorizations.append(
            {
                "operation_id": record["operation_id"],
                "operation_index": record["operation_index"],
                "target_path": record["target_path"],
                "authorization_record": validate_authorization_record(authorization),
            }
        )
    artifact = {
        "artifact_type": MULTI_FILE_MUTATION_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_GOVERNANCE_VERSION,
        "authorization_id": _require_string(authorization_id, "authorization_id"),
        "candidate_id": validated_candidate["candidate_id"],
        "candidate_hash": validated_candidate["artifact_hash"],
        "approval_id": validated_approval["approval_id"],
        "approval_hash": validated_approval["artifact_hash"],
        "operation_count": validated_candidate["operation_count"],
        "authorizations": authorizations,
        "governance_authority": True,
        "execution_performed": False,
        "replay_reconstructed": False,
        "automatic_rollback_authorized": False,
        "git_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "dependency_installation_authorized": False,
        "authorization_timestamp": _require_string(authorization_timestamp, "authorization_timestamp"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_multi_file_mutation_authorization_artifact(
    artifact: dict[str, Any],
    candidate: dict[str, Any],
    approval: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("multi-file mutation authorization artifact required")
    authorization = deepcopy(artifact)
    _verify_artifact_hash(authorization)
    if authorization.get("artifact_type") != MULTI_FILE_MUTATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("multi-file mutation failed closed: authorization artifact type invalid")
    if authorization.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: authorization candidate mismatch")
    if authorization.get("approval_hash") != approval["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: authorization approval mismatch")
    if authorization.get("operation_count") != candidate["operation_count"]:
        raise FailClosedRuntimeError("multi-file mutation failed closed: authorization count mismatch")
    for expected, observed in zip(candidate["operations"], authorization["authorizations"]):
        if observed.get("operation_id") != expected["operation_id"] or observed.get("operation_index") != expected["operation_index"]:
            raise FailClosedRuntimeError("multi-file mutation failed closed: authorization operation mismatch")
        record = validate_authorization_record(observed["authorization_record"])
        if record["worker_id"] != expected["worker_id"] or record["authorization_scope"] != expected["worker_scope"]:
            raise FailClosedRuntimeError("multi-file mutation failed closed: authorization Worker mismatch")
    return authorization


def authorization_for_operation(authorization_artifact: dict[str, Any], operation_id: str) -> dict[str, Any]:
    for record in authorization_artifact["authorizations"]:
        if record["operation_id"] == operation_id:
            return deepcopy(record["authorization_record"])
    raise FailClosedRuntimeError("multi-file mutation failed closed: operation authorization missing")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("multi-file mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multi-file mutation requires {field}")
    return value
