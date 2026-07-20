"""Governance-owned approval and authorization for existing-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_mutation_candidate import (
    validate_existing_file_mutation_candidate,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_replace_worker import AUTHORIZED_REPLACE_SCOPE, FILESYSTEM_REPLACE_WORKER_ID


EXISTING_FILE_GOVERNANCE_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1 = "EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1"
G31_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_VERSION = (
    "G31_24G_R04_R02_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_V2"
)


def create_existing_file_mutation_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    """Create explicit human approval bound to an existing-file mutation candidate."""

    candidate = validate_existing_file_mutation_candidate(candidate_artifact)
    expected_confirmation = f"confirm existing-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    observed_confirmation = _require_string(confirmation_text, "confirmation_text").strip()
    if observed_confirmation != expected_confirmation:
        raise FailClosedRuntimeError("existing-file mutation failed closed: confirmation does not bind candidate hash")
    artifact = {
        "artifact_type": EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_GOVERNANCE_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "target_path": candidate["target_path"],
        "expected_content_hash": candidate["expected_content_hash"],
        "replacement_content_hash": candidate["replacement_content_hash"],
        "confirmation_text": observed_confirmation,
        "decision": "APPROVED",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "mutation_authorized_by_approval_only": False,
        "git_authorized": False,
        "commit_authorized": False,
        "deployment_authorized": False,
        "provider_invocation_authorized": False,
        "additional_worker_dispatch_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_existing_file_mutation_approval(
    approval: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("existing-file mutation failed closed: approval required")
    artifact = deepcopy(approval)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("existing-file mutation failed closed: approval artifact required")
    if artifact.get("decision") != "APPROVED":
        raise FailClosedRuntimeError("existing-file mutation failed closed: approval required")
    if artifact.get("candidate_id") != candidate["candidate_id"] or artifact.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("existing-file mutation failed closed: approval candidate mismatch")
    expected_confirmation = f"confirm existing-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}"
    if artifact.get("confirmation_text") != expected_confirmation:
        raise FailClosedRuntimeError("existing-file mutation failed closed: approval confirmation mismatch")
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
            raise FailClosedRuntimeError(f"existing-file mutation failed closed: {field} must be false")
    if artifact.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("existing-file mutation failed closed: human authority evidence invalid")
    return artifact


def create_existing_file_mutation_authorization_record(
    *,
    authorization_id: str,
    candidate: dict[str, Any],
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create and validate the governed authorization for replace-existing-file Worker."""

    validated_candidate = validate_existing_file_mutation_candidate(candidate)
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=validated_candidate["candidate_id"],
        worker_id=FILESYSTEM_REPLACE_WORKER_ID,
        authorization_scope=AUTHORIZED_REPLACE_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def authorize_g31_approved_existing_file_mutation(
    *, authorization_id: str, candidate_capture: dict[str, Any],
    candidate_reconstruction: dict[str, Any], mutation_decision_capture: dict[str, Any],
    mutation_decision_reconstruction: dict[str, Any], acceptance_capture: dict[str, Any],
    content_decision_capture: dict[str, Any], binding_capture: dict[str, Any],
    repository_grounding_artifact: dict[str, Any], activation_capture: dict[str, Any],
    activation_binding: dict[str, Any], governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any], session_root: str | Path,
    workspace: str | Path, authorization_timestamp: str,
) -> dict[str, Any]:
    """Authorize one exact approved G31 V2 candidate without executing it."""

    subject = _g31_authorization_subject(
        candidate_capture=candidate_capture, candidate_reconstruction=candidate_reconstruction,
        mutation_decision_capture=mutation_decision_capture,
        mutation_decision_reconstruction=mutation_decision_reconstruction,
        acceptance_capture=acceptance_capture, content_decision_capture=content_decision_capture,
        binding_capture=binding_capture, repository_grounding_artifact=repository_grounding_artifact,
        activation_capture=activation_capture, activation_binding=activation_binding,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root, workspace=workspace,
    )
    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=subject["candidate_id"], worker_id=FILESYSTEM_REPLACE_WORKER_ID,
        authorization_scope=AUTHORIZED_REPLACE_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    authorization = validate_authorization_record(authorization)
    capture = {
        "runtime_version": G31_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_VERSION,
        "authorization_record": authorization, "authorization_evidence": subject,
        "authorization_evidence_hash": subject["binding_hash"],
        "mutation_authorization_id": authorization["authorization_id"],
        "mutation_authorization_hash": authorization["authorization_hash"],
        "mutation_authorized": True, "patch_created": False,
        "disposable_execution_performed": False, "worker_invoked": False,
        "provider_invoked": False, "command_executed": False,
        "repository_mutated": False, "main_repository_mutated": False,
    }
    capture["authorization_binding_hash"] = replay_hash(capture)
    return capture


def reconstruct_g31_existing_file_mutation_authorization_binding(
    *, authorization_capture: dict[str, Any], candidate_capture: dict[str, Any],
    candidate_reconstruction: dict[str, Any], mutation_decision_capture: dict[str, Any],
    mutation_decision_reconstruction: dict[str, Any], acceptance_capture: dict[str, Any],
    content_decision_capture: dict[str, Any], binding_capture: dict[str, Any],
    repository_grounding_artifact: dict[str, Any], activation_capture: dict[str, Any],
    activation_binding: dict[str, Any], governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any], session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Reconstruct an evidence-only G31 mutation authorization binding."""

    capture = deepcopy(authorization_capture)
    actual_hash = capture.pop("authorization_binding_hash", None)
    if actual_hash != replay_hash(capture):
        raise FailClosedRuntimeError("G31 mutation authorization binding hash mismatch")
    subject = _g31_authorization_subject(
        candidate_capture=candidate_capture, candidate_reconstruction=candidate_reconstruction,
        mutation_decision_capture=mutation_decision_capture,
        mutation_decision_reconstruction=mutation_decision_reconstruction,
        acceptance_capture=acceptance_capture, content_decision_capture=content_decision_capture,
        binding_capture=binding_capture, repository_grounding_artifact=repository_grounding_artifact,
        activation_capture=activation_capture, activation_binding=activation_binding,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root, workspace=workspace,
    )
    authorization = validate_authorization_record(capture.get("authorization_record"))
    checks = (
        capture.get("runtime_version") == G31_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_VERSION,
        capture.get("authorization_evidence") == subject,
        capture.get("authorization_evidence_hash") == subject["binding_hash"],
        authorization.get("proposal_id") == subject["candidate_id"],
        authorization.get("worker_id") == FILESYSTEM_REPLACE_WORKER_ID,
        authorization.get("authorization_scope") == AUTHORIZED_REPLACE_SCOPE,
        capture.get("mutation_authorization_id") == authorization["authorization_id"],
        capture.get("mutation_authorization_hash") == authorization["authorization_hash"],
        capture.get("mutation_authorized") is True,
        capture.get("patch_created") is False,
        capture.get("disposable_execution_performed") is False,
        capture.get("worker_invoked") is False, capture.get("provider_invoked") is False,
        capture.get("command_executed") is False, capture.get("repository_mutated") is False,
        capture.get("main_repository_mutated") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError("G31 mutation authorization binding identity mismatch")
    return {
        "mutation_authorization_id": authorization["authorization_id"],
        "mutation_authorization_hash": authorization["authorization_hash"],
        "candidate_id": subject["candidate_id"], "candidate_hash": subject["candidate_hash"],
        "mutation_decision_id": subject["mutation_decision_id"],
        "mutation_decision_hash": subject["mutation_decision_hash"],
        "mutation_authorized": True, "patch_created": False,
        "worker_invoked": False, "provider_invoked": False,
        "repository_mutated": False, "main_repository_mutated": False,
        "authorization_binding_hash": actual_hash,
    }


def _g31_authorization_subject(
    *, candidate_capture: dict[str, Any], candidate_reconstruction: dict[str, Any],
    mutation_decision_capture: dict[str, Any], mutation_decision_reconstruction: dict[str, Any],
    acceptance_capture: dict[str, Any], content_decision_capture: dict[str, Any],
    binding_capture: dict[str, Any], repository_grounding_artifact: dict[str, Any],
    activation_capture: dict[str, Any], activation_binding: dict[str, Any],
    governed_execution_capture: dict[str, Any], execution_candidate_capture: dict[str, Any],
    session_root: str | Path, workspace: str | Path,
) -> dict[str, Any]:
    from aigol.runtime.codex_worker_activation_binding_runtime import reconstruct_codex_worker_activation_binding
    from aigol.runtime.human_decision_runtime import (
        HUMAN_DECISION_ARTIFACT_V3, MUTATION_APPROVED,
        reconstruct_existing_file_mutation_decision_replay,
    )
    from aigol.runtime.platform_core_existing_file_mutation_candidate import (
        G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        reconstruct_g31_accepted_existing_file_mutation_candidate_replay,
        validate_g31_accepted_existing_file_mutation_candidate,
    )

    root = Path(session_root).resolve()
    reconstructed_activation = reconstruct_codex_worker_activation_binding(
        activation_capture=activation_capture, governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture, session_root=root, workspace=workspace)
    if activation_binding != reconstructed_activation or not isinstance(activation_binding.get("lineage"), dict):
        raise FailClosedRuntimeError("G31 mutation authorization requires reconstructed activation lineage")
    grounding = activation_binding["lineage"].get("grounding")
    if grounding != repository_grounding_artifact:
        raise FailClosedRuntimeError("G31 mutation authorization grounding lineage mismatch")
    reconstructed_candidate = reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
        candidate_capture=candidate_capture, acceptance_capture=acceptance_capture,
        decision_capture=content_decision_capture, binding_capture=binding_capture,
        repository_grounding_artifact=grounding, session_root=root)
    if candidate_reconstruction != reconstructed_candidate:
        raise FailClosedRuntimeError("G31 mutation authorization requires reconstructed V2 candidate")
    candidate = validate_g31_accepted_existing_file_mutation_candidate(
        candidate_capture.get("existing_file_mutation_candidate_artifact") or {})
    if candidate.get("runtime_version") != G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION:
        raise FailClosedRuntimeError("G31 mutation authorization candidate generation mismatch")
    reconstructed_decision = reconstruct_existing_file_mutation_decision_replay(
        decision_capture=mutation_decision_capture, candidate_capture=candidate_capture,
        acceptance_capture=acceptance_capture, content_decision_capture=content_decision_capture,
        binding_capture=binding_capture, repository_grounding_artifact=grounding, session_root=root)
    if mutation_decision_reconstruction != reconstructed_decision:
        raise FailClosedRuntimeError("G31 mutation authorization requires reconstructed V3 decision")
    decision = mutation_decision_capture.get("human_mutation_decision_artifact") or {}
    provenance = candidate["candidate_provenance"]
    if not all((decision.get("artifact_type") == HUMAN_DECISION_ARTIFACT_V3,
                decision.get("decision_outcome") == MUTATION_APPROVED,
                reconstructed_decision.get("mutation_decision_approved") is True,
                reconstructed_decision.get("mutation_authorized") is False,
                decision.get("candidate_id") == candidate["candidate_id"],
                decision.get("candidate_hash") == candidate["artifact_hash"],
                decision.get("candidate_replay_hash") == reconstructed_candidate["replay_hash"],
                decision.get("candidate_provenance_binding_hash") == candidate["candidate_provenance_binding_hash"],
                provenance.get("repository_root") == str(Path(workspace).resolve()),
                provenance.get("repository_grounding_hash") == grounding.get("grounding_evidence_hash"))):
        raise FailClosedRuntimeError("G31 mutation authorization decision or candidate lineage mismatch")
    subject = {
        "session_id": candidate["session_id"],
        "activation_replay_reference": activation_binding["activation_replay_reference"],
        "activation_replay_hash": activation_binding["activation_replay_hash"],
        "repository_grounding_hash": provenance["repository_grounding_hash"],
        "candidate_id": candidate["candidate_id"], "candidate_hash": candidate["artifact_hash"],
        "candidate_replay_reference": candidate_capture["candidate_replay_reference"],
        "candidate_replay_hash": reconstructed_candidate["replay_hash"],
        "candidate_provenance_binding_hash": candidate["candidate_provenance_binding_hash"],
        "mutation_decision_id": decision["human_decision_id"],
        "mutation_decision_hash": decision["artifact_hash"],
        "mutation_decision_replay_reference": mutation_decision_capture["human_mutation_decision_replay_reference"],
        "mutation_decision_replay_hash": reconstructed_decision["replay_hash"],
        "decision_outcome": MUTATION_APPROVED, "operation": candidate["operation"],
        "target_path": candidate["target_path"], "expected_source_sha256": provenance["preimage_sha256"],
        "expected_postimage_sha256": provenance["postimage_sha256"],
    }
    subject["binding_hash"] = replay_hash(subject)
    return subject


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("existing-file mutation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("existing-file mutation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"existing-file mutation requires {field}")
    return value
