"""Governance-owned approval and authorization for rollback execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_rollback_candidate import validate_governed_rollback_candidate
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_rollback_worker import AUTHORIZED_ROLLBACK_SCOPE, FILESYSTEM_ROLLBACK_WORKER_ID


ROLLBACK_GOVERNANCE_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
ROLLBACK_APPROVAL_ARTIFACT_V1 = "ROLLBACK_APPROVAL_ARTIFACT_V1"


def create_governed_rollback_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to a rollback candidate."""

    candidate = validate_governed_rollback_candidate(candidate_artifact)
    expected = f"confirm governed rollback execution {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed = _require_string(confirmation_text, "confirmation_text").strip()
    if observed != expected:
        raise FailClosedRuntimeError("governed rollback failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": ROLLBACK_APPROVAL_ARTIFACT_V1,
        "runtime_version": ROLLBACK_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "prior_execution_id": candidate["prior_execution_id"],
        "prior_replay_reference": candidate["prior_replay_reference"],
        "rollback_metadata_hash": candidate["rollback_metadata_hash"],
        "target_path": candidate["target_path"],
        "rollback_action": candidate["rollback_action"],
        "authorized_current_hash": candidate["authorized_current_hash"],
        "expected_rollback_result_hash": candidate["expected_rollback_result_hash"],
        "confirmation_text": observed,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "rollback_authorized_by_approval_only": False,
        "multi_file_rollback_authorized": False,
        "automatic_rollback_authorized": False,
        "git_authorized": False,
        "branch_manipulation_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "dependency_rollback_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_rollback_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("governed rollback failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ROLLBACK_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed rollback failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("governed rollback failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback failed closed: approval candidate mismatch")
    expected = f"confirm governed rollback execution {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected:
        raise FailClosedRuntimeError("governed rollback failed closed: approval confirmation mismatch")
    for field in (
        "approval_bypassed",
        "rollback_authorized_by_approval_only",
        "multi_file_rollback_authorized",
        "automatic_rollback_authorized",
        "git_authorized",
        "branch_manipulation_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "dependency_rollback_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"governed rollback failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("governed rollback failed closed: human authority invalid")
    return artifact


def create_governed_rollback_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate the governed authorization for rollback Worker execution."""

    validated_candidate = validate_governed_rollback_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=FILESYSTEM_ROLLBACK_WORKER_ID,
        authorization_scope=AUTHORIZED_ROLLBACK_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed rollback artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed rollback requires {field}")
    return value
