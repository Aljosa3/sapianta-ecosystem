"""Governance-owned approval and authorization for validation execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_candidate import validate_governed_validation_candidate
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.validation_command_worker import AUTHORIZED_VALIDATION_SCOPE, VALIDATION_COMMAND_WORKER_ID


VALIDATION_GOVERNANCE_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
VALIDATION_APPROVAL_ARTIFACT_V1 = "VALIDATION_APPROVAL_ARTIFACT_V1"


def create_governed_validation_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create human approval bound to a validation candidate hash."""

    candidate = validate_governed_validation_candidate(candidate_artifact)
    expected_confirmation = f"confirm validation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("governed validation failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": VALIDATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": VALIDATION_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "command_id": candidate["command_id"],
        "argv_hash": candidate["argv_hash"],
        "command_spec_hash": candidate["command_spec_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "validation_authorized_by_approval_only": False,
        "git_authorized": False,
        "commit_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "package_install_authorized": False,
        "network_authorized": False,
        "additional_worker_dispatch_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_validation_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("governed validation failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != VALIDATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed validation failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("governed validation failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm validation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("governed validation failed closed: approval confirmation mismatch")
    for field in (
        "approval_bypassed",
        "validation_authorized_by_approval_only",
        "git_authorized",
        "commit_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "package_install_authorized",
        "network_authorized",
        "additional_worker_dispatch_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"governed validation failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("governed validation failed closed: human authority evidence invalid")
    return artifact


def create_governed_validation_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate authorization for the validation command Worker."""

    validated_candidate = validate_governed_validation_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=VALIDATION_COMMAND_WORKER_ID,
        authorization_scope=AUTHORIZED_VALIDATION_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed validation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value
