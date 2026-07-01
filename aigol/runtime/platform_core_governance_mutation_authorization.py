"""Governance-owned approval and authorization helpers for governed mutation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import validate_mutation_candidate
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE as FILESYSTEM_CREATE_FILE_SCOPE,
    FILESYSTEM_WORKER_ID,
)


GOVERNANCE_MUTATION_AUTHORIZATION_VERSION = "G8_09B_PLATFORM_CORE_MUTATION_RUNTIME_REFACTORING_V1"
FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1 = "FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1"


def create_first_mutating_worker_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to the exact OCS candidate hash."""

    candidate = validate_mutation_candidate(candidate_artifact)
    expected_confirmation = f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("first mutating Worker failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1,
        "runtime_version": GOVERNANCE_MUTATION_AUTHORIZATION_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "mutation_authorized_by_approval_only": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_mutation_approval(approval: dict[str, Any] | None, candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate human approval evidence without authorizing execution by itself."""

    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != FIRST_MUTATING_WORKER_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("first mutating Worker failed closed: approval confirmation mismatch")
    if artifact.get("approval_bypassed") is not False or artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("first mutating Worker failed closed: human authority evidence invalid")
    return artifact


def create_mutation_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate the governed Worker authorization record."""

    validated_candidate = validate_mutation_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=FILESYSTEM_WORKER_ID,
        authorization_scope=FILESYSTEM_CREATE_FILE_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first mutating Worker artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first mutating Worker requires {field}")
    return value
