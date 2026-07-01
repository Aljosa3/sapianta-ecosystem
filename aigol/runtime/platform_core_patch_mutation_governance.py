"""Governance-owned approval and authorization for single-file patch mutation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_patch_mutation_candidate import (
    validate_single_file_patch_mutation_candidate,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_patch_worker import AUTHORIZED_PATCH_SCOPE, FILESYSTEM_PATCH_WORKER_ID


PATCH_MUTATION_GOVERNANCE_VERSION = "G9_04_SINGLE_FILE_PATCH_LEVEL_MUTATION_IMPLEMENTATION_V1"
PATCH_MUTATION_APPROVAL_ARTIFACT_V1 = "PATCH_MUTATION_APPROVAL_ARTIFACT_V1"


def create_single_file_patch_mutation_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to a patch mutation candidate."""

    candidate = validate_single_file_patch_mutation_candidate(candidate_artifact)
    expected_confirmation = f"confirm single-file patch mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("patch mutation failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": PATCH_MUTATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": PATCH_MUTATION_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_path": candidate["target_path"],
        "pre_content_hash": candidate["pre_content_hash"],
        "old_text_hash": candidate["old_text_hash"],
        "new_text_hash": candidate["new_text_hash"],
        "expected_post_content_hash": candidate["expected_post_content_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "mutation_authorized_by_approval_only": False,
        "complete_resulting_file_is_canonical_artifact": True,
        "patch_is_intent_only": True,
        "git_authorized": False,
        "commit_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "additional_worker_dispatch_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_single_file_patch_mutation_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("patch mutation failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != PATCH_MUTATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("patch mutation failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("patch mutation failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("patch mutation failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm single-file patch mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("patch mutation failed closed: approval confirmation mismatch")
    for field in (
        "approval_bypassed",
        "mutation_authorized_by_approval_only",
        "git_authorized",
        "commit_authorized",
        "deployment_authorized",
        "provider_invocation_authorized",
        "additional_worker_dispatch_authorized",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"patch mutation failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("patch mutation failed closed: human authority evidence invalid")
    if artifact.get("complete_resulting_file_is_canonical_artifact") is not True:
        raise FailClosedRuntimeError("patch mutation failed closed: canonical artifact approval missing")
    return artifact


def create_single_file_patch_mutation_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate governed authorization for the patch Worker."""

    validated_candidate = validate_single_file_patch_mutation_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=FILESYSTEM_PATCH_WORKER_ID,
        authorization_scope=AUTHORIZED_PATCH_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("patch mutation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("patch mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"patch mutation requires {field}")
    return value
