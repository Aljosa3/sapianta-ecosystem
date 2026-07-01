"""Governance-owned approval and authorization for governed Git commits."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_git_commit_candidate import validate_governed_git_commit_candidate
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.git_commit_worker import AUTHORIZED_GIT_COMMIT_SCOPE, GIT_COMMIT_WORKER_ID


GIT_COMMIT_GOVERNANCE_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GIT_COMMIT_APPROVAL_ARTIFACT_V1 = "GIT_COMMIT_APPROVAL_ARTIFACT_V1"


def create_governed_git_commit_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to a Git commit candidate hash."""

    candidate = validate_governed_git_commit_candidate(candidate_artifact)
    expected_confirmation = f"confirm governed git commit {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("governed Git commit failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": GIT_COMMIT_APPROVAL_ARTIFACT_V1,
        "runtime_version": GIT_COMMIT_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "expected_head": candidate["expected_head"],
        "file_set_hash": candidate["file_set_hash"],
        "commit_message_hash": candidate["commit_message_hash"],
        "author_hash": candidate["author_hash"],
        "validation_artifact_hash": candidate["validation_artifact_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "commit_authorized_by_approval_only": False,
        "push_authorized": False,
        "remote_interaction_authorized": False,
        "branch_management_authorized": False,
        "merge_authorized": False,
        "rebase_authorized": False,
        "checkout_authorized": False,
        "reset_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "additional_worker_dispatch_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_git_commit_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("governed Git commit failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != GIT_COMMIT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed Git commit failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("governed Git commit failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm governed git commit {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("governed Git commit failed closed: approval confirmation mismatch")
    for field in (
        "approval_bypassed",
        "commit_authorized_by_approval_only",
        "push_authorized",
        "remote_interaction_authorized",
        "branch_management_authorized",
        "merge_authorized",
        "rebase_authorized",
        "checkout_authorized",
        "reset_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "additional_worker_dispatch_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"governed Git commit failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("governed Git commit failed closed: human authority evidence invalid")
    return artifact


def create_governed_git_commit_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate the governed authorization for the local Git commit Worker."""

    validated_candidate = validate_governed_git_commit_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=GIT_COMMIT_WORKER_ID,
        authorization_scope=AUTHORIZED_GIT_COMMIT_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed Git commit artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed Git commit artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git commit requires {field}")
    return value
