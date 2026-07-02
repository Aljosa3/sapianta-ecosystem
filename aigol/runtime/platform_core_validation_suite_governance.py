"""Governance-owned approval and authorization for validation suites."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_governance import create_governed_validation_authorization_record
from aigol.runtime.platform_core_validation_suite_candidate import validate_governed_validation_suite_candidate
from aigol.runtime.transport.serialization import replay_hash


VALIDATION_SUITE_GOVERNANCE_VERSION = "G9_13_BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTATION_V1"
VALIDATION_SUITE_APPROVAL_ARTIFACT_V1 = "VALIDATION_SUITE_APPROVAL_ARTIFACT_V1"
VALIDATION_SUITE_AUTHORIZATION_ARTIFACT_V1 = "VALIDATION_SUITE_AUTHORIZATION_ARTIFACT_V1"


def create_governed_validation_suite_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create human approval bound to a validation suite candidate hash."""

    candidate = validate_governed_validation_suite_candidate(candidate_artifact)
    expected_confirmation = f"confirm validation suite {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError(
            "governed validation suite failed closed: confirmation does not bind candidate hash"
        )
    artifact = {
        "artifact_type": VALIDATION_SUITE_APPROVAL_ARTIFACT_V1,
        "runtime_version": VALIDATION_SUITE_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "command_count": candidate["command_count"],
        "command_order": deepcopy(candidate["command_order"]),
        "command_ids": deepcopy(candidate["command_ids"]),
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "approval_executes_validation": False,
        "governance_authorization_required": True,
        "git_authorized": False,
        "commit_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "package_install_authorized": False,
        "network_authorized": False,
        "repository_mutation_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_validation_suite_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("governed validation suite failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact, "governed validation suite approval")
    if artifact.get("artifact_type") != VALIDATION_SUITE_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed validation suite failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("governed validation suite failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm validation suite {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("governed validation suite failed closed: approval confirmation mismatch")
    if artifact.get("command_order") != candidate["command_order"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: approval command order mismatch")
    for field in (
        "approval_bypassed",
        "approval_executes_validation",
        "git_authorized",
        "commit_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "package_install_authorized",
        "network_authorized",
        "repository_mutation_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"governed validation suite failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("governed validation suite failed closed: human authority evidence invalid")
    return artifact


def create_governed_validation_suite_authorization_artifact(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create Governance authorization for each Worker-facing validation command."""

    validated_candidate = validate_governed_validation_suite_candidate(candidate)
    validated_approval = validate_governed_validation_suite_approval(approval, validated_candidate)
    command_authorizations = []
    for record in validated_candidate["commands"]:
        single_candidate = record["single_command_candidate"]
        command_authorizations.append(
            {
                "command_record_id": record["command_record_id"],
                "command_index": record["command_index"],
                "command_id": record["command_id"],
                "single_command_candidate_id": single_candidate["candidate_id"],
                "single_command_candidate_hash": single_candidate["artifact_hash"],
                "authorization_record": create_governed_validation_authorization_record(
                    authorization_id=f"{authorization_id}:{record['command_record_id']}",
                    candidate=single_candidate,
                    authorization_timestamp=authorization_timestamp,
                ),
            }
        )
    artifact = {
        "artifact_type": VALIDATION_SUITE_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": VALIDATION_SUITE_GOVERNANCE_VERSION,
        "authorization_id": _require_string(authorization_id, "authorization_id"),
        "candidate_id": validated_candidate["candidate_id"],
        "candidate_hash": validated_candidate["artifact_hash"],
        "approval_id": validated_approval["approval_id"],
        "approval_hash": validated_approval["artifact_hash"],
        "command_count": validated_candidate["command_count"],
        "command_authorizations": command_authorizations,
        "governance_authorizes_only": True,
        "worker_execution_not_performed": True,
        "replay_mutation_not_performed": True,
        "git_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "authorization_timestamp": _require_string(authorization_timestamp, "authorization_timestamp"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_validation_suite_authorization_artifact(
    authorization: dict[str, Any],
    candidate: dict[str, Any],
    approval: dict[str, Any],
) -> dict[str, Any]:
    artifact = deepcopy(authorization)
    validated_candidate = validate_governed_validation_suite_candidate(candidate)
    validated_approval = validate_governed_validation_suite_approval(approval, validated_candidate)
    _verify_artifact_hash(artifact, "governed validation suite authorization")
    if artifact.get("artifact_type") != VALIDATION_SUITE_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed validation suite failed closed: authorization artifact required")
    if artifact.get("candidate_hash") != validated_candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: authorization candidate mismatch")
    if artifact.get("approval_hash") != validated_approval["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: authorization approval mismatch")
    command_authorizations = artifact.get("command_authorizations")
    if not isinstance(command_authorizations, list) or len(command_authorizations) != validated_candidate["command_count"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: authorization count mismatch")
    for expected, observed in zip(validated_candidate["commands"], command_authorizations):
        if observed.get("command_record_id") != expected["command_record_id"]:
            raise FailClosedRuntimeError("governed validation suite failed closed: authorization order mismatch")
        if observed.get("single_command_candidate_hash") != expected["single_command_candidate_hash"]:
            raise FailClosedRuntimeError("governed validation suite failed closed: authorization command hash mismatch")
        record = observed.get("authorization_record")
        if not isinstance(record, dict):
            raise FailClosedRuntimeError("governed validation suite failed closed: authorization record missing")
        if record.get("proposal_id") != expected["single_command_candidate"]["candidate_id"]:
            raise FailClosedRuntimeError("governed validation suite failed closed: authorization proposal mismatch")
    for field in ("git_authorized", "deployment_authorized", "provider_invocation_authorized"):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"governed validation suite failed closed: {field} must be false")
    return artifact


def authorization_for_command(authorization: dict[str, Any], command_record_id: str) -> dict[str, Any]:
    for record in authorization["command_authorizations"]:
        if record["command_record_id"] == command_record_id:
            return deepcopy(record["authorization_record"])
    raise FailClosedRuntimeError("governed validation suite failed closed: command authorization missing")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation suite requires {field}")
    return value
