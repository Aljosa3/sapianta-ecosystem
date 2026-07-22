"""Governance-owned approval and authorization for existing-file mutation."""

from __future__ import annotations

from base64 import b64encode
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.authorization.authorization_runtime import (
    CANONICAL_AUTHORIZATION_ACTOR, EXISTING_AUTHORIZATION_BINDING_VERSION,
    persist_existing_authorization_binding_replay, reconstruct_existing_authorization_binding_replay)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_mutation_candidate import (
    validate_g31_accepted_existing_file_mutation_candidate,
    validate_existing_file_mutation_candidate,
)
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED, WORKER_ROLE, default_resource_registry,
    reconstruct_unified_resource_selection_replay, select_unified_resource,
)
from aigol.runtime.worker_selection_certification_v1 import validate_worker_selection_certification_v1
from aigol.workers.filesystem_replace_worker import AUTHORIZED_REPLACE_SCOPE, FILESYSTEM_REPLACE_WORKER_ID
from aigol.workers.filesystem_replace_worker import (
    AUTHENTICATED_REPLACE_REQUEST_TYPE_V2, HARDENED_REPLACE_VERSION,
    _execute_authenticated_replace_v2, _recover_authenticated_replace_v2,
    g31_replace_destinations, reconstruct_authenticated_replace_replay_v2,
    validate_authenticated_replace_request_v2,
)


EXISTING_FILE_GOVERNANCE_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1 = "EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1"
G31_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_VERSION = (
    "G31_24G_R04_R02_EXISTING_FILE_MUTATION_AUTHORIZATION_BINDING_V2"
)
R08B_REGISTRY_HASH = "sha256:74357af9a2ba666d73241381e5a4c24ac7687e41b67efe6746cb86d3ac6e7d64"
R08B_CERTIFICATION_HASH = "sha256:03cbf0fc4e8ae562ffe25235aff1c7a6fbd559c23fc8c4fad48e15a1c56b1b45"
R08B_CERTIFICATION_PATH = Path(__file__).resolve().parents[2] / (
    "runtime/worker_selection_certification_v1/CERT-000002/certification_report/000_worker_selection_certification_report.json"
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


def bind_g31_mutation_authorization_actor_and_replay(
    *, authorization_capture: dict[str, Any], candidate_capture: dict[str, Any],
    candidate_reconstruction: dict[str, Any], mutation_decision_capture: dict[str, Any],
    mutation_decision_reconstruction: dict[str, Any], acceptance_capture: dict[str, Any],
    content_decision_capture: dict[str, Any], binding_capture: dict[str, Any],
    repository_grounding_artifact: dict[str, Any], activation_capture: dict[str, Any],
    activation_binding: dict[str, Any], governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any], session_root: str | Path, workspace: str | Path,
) -> dict[str, Any]:
    """Bind the canonical Governance actor and Replay to an existing R02 record."""

    root = Path(session_root).resolve()
    reconstructed = reconstruct_g31_existing_file_mutation_authorization_binding(
        authorization_capture=authorization_capture, candidate_capture=candidate_capture,
        candidate_reconstruction=candidate_reconstruction, mutation_decision_capture=mutation_decision_capture,
        mutation_decision_reconstruction=mutation_decision_reconstruction, acceptance_capture=acceptance_capture,
        content_decision_capture=content_decision_capture, binding_capture=binding_capture,
        repository_grounding_artifact=repository_grounding_artifact, activation_capture=activation_capture,
        activation_binding=activation_binding, governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture, session_root=root, workspace=workspace)
    subject = _g31_authorization_subject(
        candidate_capture=candidate_capture, candidate_reconstruction=candidate_reconstruction,
        mutation_decision_capture=mutation_decision_capture,
        mutation_decision_reconstruction=mutation_decision_reconstruction,
        acceptance_capture=acceptance_capture, content_decision_capture=content_decision_capture,
        binding_capture=binding_capture, repository_grounding_artifact=repository_grounding_artifact,
        activation_capture=activation_capture, activation_binding=activation_binding,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture, session_root=root, workspace=workspace)
    record = validate_authorization_record(authorization_capture.get("authorization_record"))
    decision = mutation_decision_capture.get("human_mutation_decision_artifact") or {}
    replay_path = root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1"
    if any(authorization_capture.get(field) is True for field in (
        "authorization_consumed", "replace_request_created", "patch_created", "worker_invoked",
        "provider_invoked", "command_executed", "repository_mutated", "main_repository_mutated", "rollback_performed", "recovery_required", "mutation_completed", "mutation_terminated")):
        raise FailClosedRuntimeError("authorization actor binding requires an unconsumed stop state")
    artifact = {
        "artifact_type": "EXISTING_MUTATION_AUTHORIZATION_ACTOR_BINDING_V1",
        "runtime_version": EXISTING_AUTHORIZATION_BINDING_VERSION,
        "canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR,
        "authorization_record": deepcopy(record), "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"], "authorization_status": record["authorization_status"],
        "authorization_scope": record["authorization_scope"], "worker_id": record["worker_id"],
        "r02_authorization_binding_hash": authorization_capture["authorization_binding_hash"],
        "session_id": subject["session_id"], "activation_id": activation_binding["activation_approval_artifact"]["approval_id"], "activation_hash": activation_binding["activation_approval_artifact"]["artifact_hash"], "activation_replay_reference": subject["activation_replay_reference"],
        "activation_replay_hash": subject["activation_replay_hash"], "candidate_id": subject["candidate_id"],
        "candidate_hash": subject["candidate_hash"], "candidate_replay_hash": subject["candidate_replay_hash"],
        "candidate_provenance_binding_hash": subject["candidate_provenance_binding_hash"],
        "mutation_decision_id": subject["mutation_decision_id"],
        "mutation_decision_hash": subject["mutation_decision_hash"],
        "mutation_decision_outcome": subject["decision_outcome"],
        "mutation_decision_scope": decision.get("decision_scope"),
        "mutation_decision_actor": decision.get("decided_by"),
        "mutation_decision_replay_hash": subject["mutation_decision_replay_hash"],
        "target_path": subject["target_path"], "expected_source_sha256": subject["expected_source_sha256"],
        "authorization_replay_reference": str(replay_path), "authorization_consumed": False,
        "replace_request_created": False, "worker_invoked": False, "provider_invoked": False,
        "command_executed": False, "repository_mutated": False, "main_repository_mutated": False,
        "replay_visible": True,
    }
    if reconstructed["mutation_authorized"] is not True or not all(
            isinstance(artifact.get(field), str) and artifact[field] for field in (
                "mutation_decision_scope", "mutation_decision_actor")):
        raise FailClosedRuntimeError("authorization actor binding lineage is incomplete")
    artifact["artifact_hash"] = replay_hash(artifact)
    replay = persist_existing_authorization_binding_replay(
        binding=artifact, replay_dir=replay_path, session_root=root)
    capture = {"runtime_version": EXISTING_AUTHORIZATION_BINDING_VERSION,
               "authorization_binding_artifact": deepcopy(artifact),
               "authorization_replay_reference": replay["authorization_replay_reference"],
               "authorization_replay_hash": replay["authorization_replay_hash"],
               "authorization_actor_bound": True, "authorization_replay_recorded": True,
               "mutation_authorized": True, "authorization_consumed": False,
               "replace_request_created": False, "worker_invoked": False, "provider_invoked": False,
               "command_executed": False, "repository_mutated": False, "main_repository_mutated": False}
    capture["actor_replay_binding_hash"] = replay_hash(capture)
    return capture


def reconstruct_g31_mutation_authorization_actor_and_replay(
    *, actor_replay_capture: dict[str, Any], **evidence: Any) -> dict[str, Any]:
    """Reconstruct the actor-bound Replay without issuing authorization."""

    capture = deepcopy(actor_replay_capture); actual = capture.pop("actor_replay_binding_hash", None)
    if actual != replay_hash(capture):
        raise FailClosedRuntimeError("authorization actor Replay capture hash mismatch")
    root = Path(evidence["session_root"]).resolve()
    replay = reconstruct_existing_authorization_binding_replay(
        capture.get("authorization_replay_reference", ""), session_root=root)
    artifact = capture.get("authorization_binding_artifact") or {}
    record = validate_authorization_record((evidence["authorization_capture"] or {}).get("authorization_record"))
    r02 = reconstruct_g31_existing_file_mutation_authorization_binding(**evidence)
    subject = _g31_authorization_subject(**{key: evidence[key] for key in (
        "candidate_capture", "candidate_reconstruction", "mutation_decision_capture",
        "mutation_decision_reconstruction", "acceptance_capture", "content_decision_capture",
        "binding_capture", "repository_grounding_artifact", "activation_capture", "activation_binding",
        "governed_execution_capture", "execution_candidate_capture", "session_root", "workspace")})
    decision = evidence["mutation_decision_capture"].get("human_mutation_decision_artifact") or {}
    checks = (replay.get("authorization_binding_artifact") == artifact, capture.get("authorization_replay_hash") == replay.get("authorization_replay_hash"),
        artifact.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR, artifact.get("runtime_version") == EXISTING_AUTHORIZATION_BINDING_VERSION, artifact.get("artifact_type") == "EXISTING_MUTATION_AUTHORIZATION_ACTOR_BINDING_V1", artifact.get("authorization_record") == record,
        artifact.get("authorization_hash") == record["authorization_hash"], artifact.get("r02_authorization_binding_hash") == evidence["authorization_capture"].get("authorization_binding_hash"),
        artifact.get("session_id") == root.name == subject["session_id"], artifact.get("activation_id") == evidence["activation_binding"]["activation_approval_artifact"]["approval_id"], artifact.get("activation_hash") == evidence["activation_binding"]["activation_approval_artifact"]["artifact_hash"], artifact.get("candidate_hash") == subject["candidate_hash"], artifact.get("mutation_decision_hash") == subject["mutation_decision_hash"],
        artifact.get("mutation_decision_actor") == decision.get("decided_by"), artifact.get("mutation_decision_scope") == decision.get("decision_scope"),
        artifact.get("target_path") == subject["target_path"], artifact.get("expected_source_sha256") == subject["expected_source_sha256"],
        r02.get("mutation_authorized") is True, capture.get("authorization_actor_bound") is True, capture.get("authorization_replay_recorded") is True, capture.get("mutation_authorized") is True, all(artifact.get(field) is False for field in ("authorization_consumed", "replace_request_created", "worker_invoked", "provider_invoked", "command_executed", "repository_mutated", "main_repository_mutated")), all(capture.get(field) is False for field in (
            "authorization_consumed", "replace_request_created", "worker_invoked", "provider_invoked",
            "command_executed", "repository_mutated", "main_repository_mutated")))
    if not all(checks):
        raise FailClosedRuntimeError("authorization actor Replay reconstruction mismatch")
    return {"canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR, "authorization_replay_reference": replay["authorization_replay_reference"],
            "authorization_replay_hash": replay["authorization_replay_hash"], "authorization_record": deepcopy(record), "authorization_id": record["authorization_id"], "authorization_hash": record["authorization_hash"],
            "authorization_status": record["authorization_status"], "authorization_scope": record["authorization_scope"], "worker_id": record["worker_id"], "r02_authorization_binding_hash": artifact["r02_authorization_binding_hash"],
            "session_id": artifact["session_id"], "activation_id": artifact["activation_id"], "activation_hash": artifact["activation_hash"], "activation_replay_reference": artifact["activation_replay_reference"], "activation_replay_hash": artifact["activation_replay_hash"], "candidate_id": artifact["candidate_id"], "candidate_hash": artifact["candidate_hash"], "candidate_replay_hash": artifact["candidate_replay_hash"], "candidate_provenance_binding_hash": artifact["candidate_provenance_binding_hash"],
            "mutation_decision_id": artifact["mutation_decision_id"], "mutation_decision_hash": artifact["mutation_decision_hash"], "mutation_decision_outcome": artifact["mutation_decision_outcome"], "mutation_decision_scope": artifact["mutation_decision_scope"], "mutation_decision_actor": artifact["mutation_decision_actor"], "mutation_decision_replay_hash": artifact["mutation_decision_replay_hash"], "target_path": artifact["target_path"], "expected_source_sha256": artifact["expected_source_sha256"],
            "authorization_actor_bound": True, "authorization_replay_recorded": True, "mutation_authorized": True,
            "authorization_consumed": False, "replace_request_created": False, "worker_invoked": False,
            "provider_invoked": False, "command_executed": False, "repository_mutated": False,
            "main_repository_mutated": False, "actor_replay_binding_hash": actual}


def create_g31_authenticated_replace_request(*, actor_replay_capture: dict[str, Any], **evidence: Any) -> dict[str, Any]:
    """Project only reconstructed actor-bound authorization into the hardened owner."""
    authorization = reconstruct_g31_mutation_authorization_actor_and_replay(actor_replay_capture=actor_replay_capture, **evidence)
    candidate = validate_g31_accepted_existing_file_mutation_candidate(evidence["candidate_capture"].get("existing_file_mutation_candidate_artifact") or {})
    provenance = candidate["candidate_provenance"]
    manifest = ((evidence["binding_capture"].get("implementation_manifest_capture") or {}).get("implementation_manifest_artifact") or {})
    entries = manifest.get("file_entries")
    entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else {}
    source = entry.get("preimage_content")
    replacement = entry.get("postimage_content")
    if not isinstance(source, str) or not isinstance(replacement, str):
        raise FailClosedRuntimeError("authenticated replace requires reconstructed manifest bytes")
    source_bytes, replacement_bytes = source.encode("utf-8"), replacement.encode("utf-8")
    raw_source = "sha256:" + sha256(source_bytes).hexdigest()
    raw_replacement = "sha256:" + sha256(replacement_bytes).hexdigest()
    checks = (
        authorization["candidate_id"] == candidate["candidate_id"], authorization["candidate_hash"] == candidate["artifact_hash"], authorization["candidate_provenance_binding_hash"] == provenance["binding_hash"],
        authorization["target_path"] == candidate["target_path"] == provenance["target_path"] == entry.get("target_path"),
        authorization["expected_source_sha256"] == provenance["preimage_sha256"] == entry.get("preimage_sha256") == raw_source,
        provenance["postimage_sha256"] == entry.get("postimage_sha256") == raw_replacement, provenance["manifest_hash"] == manifest.get("artifact_hash"), provenance["repository_root"] == str(Path(evidence["workspace"]).resolve()),
        provenance["repository_grounding_hash"] == evidence["repository_grounding_artifact"].get("grounding_evidence_hash"), provenance["source_mode"] == str(entry.get("file_mode")), provenance["replacement_mode"] == str(entry.get("postimage_file_mode")),
        not provenance.get("source_content_hash") or provenance["source_content_hash"] == replay_hash(source),
        not provenance.get("replacement_content_hash") or provenance["replacement_content_hash"] == replay_hash(replacement),
        candidate["operation"] == provenance["operation"] == entry.get("operation") == "REPLACE_CONTENT",
    )
    if not all(checks):
        raise FailClosedRuntimeError("authenticated replace manifest or authorization lineage mismatch")
    destinations = g31_replace_destinations(evidence["session_root"], authorization["authorization_hash"], provenance["repository_root"], provenance["target_path"])
    request = {
        "request_type": AUTHENTICATED_REPLACE_REQUEST_TYPE_V2, "runtime_version": HARDENED_REPLACE_VERSION,
        "request_id": f"{authorization['authorization_id']}:HARDENED-REPLACE-V2",
        "canonical_authorization_actor": authorization["canonical_authorization_actor"],
        "authorization_record": deepcopy(authorization["authorization_record"]),
        "authorization_id": authorization["authorization_id"], "authorization_hash": authorization["authorization_hash"],
        "authorization_status": authorization["authorization_status"], "authorization_scope": authorization["authorization_scope"],
        "worker_id": authorization["worker_id"], "authorization_replay_reference": authorization["authorization_replay_reference"],
        "authorization_replay_hash": authorization["authorization_replay_hash"], "actor_replay_binding_hash": authorization["actor_replay_binding_hash"], "r02_authorization_binding_hash": authorization["r02_authorization_binding_hash"],
        "candidate_id": authorization["candidate_id"], "candidate_hash": authorization["candidate_hash"],
        "candidate_replay_hash": authorization["candidate_replay_hash"], "candidate_provenance_binding_hash": authorization["candidate_provenance_binding_hash"],
        "mutation_decision_id": authorization["mutation_decision_id"], "mutation_decision_hash": authorization["mutation_decision_hash"], "mutation_decision_outcome": authorization["mutation_decision_outcome"],
        "mutation_decision_scope": authorization["mutation_decision_scope"], "mutation_decision_actor": authorization["mutation_decision_actor"], "mutation_decision_replay_hash": authorization["mutation_decision_replay_hash"],
        "session_id": authorization["session_id"], "session_root": str(Path(evidence["session_root"]).resolve()),
        "repository_identity": provenance["repository_identity"], "repository_root": provenance["repository_root"],
        "repository_grounding_hash": provenance["repository_grounding_hash"], "manifest_hash": provenance["manifest_hash"],
        "operation": "REPLACE_CONTENT", "worker_operation": "REPLACE_EXISTING_TEXT_FILE",
        "target_path": provenance["target_path"], "preimage_sha256": raw_source, "postimage_sha256": raw_replacement,
        "source_content_hash": replay_hash(source), "replacement_content_hash": replay_hash(replacement),
        "preimage_bytes_b64": b64encode(source_bytes).decode("ascii"), "replacement_bytes_b64": b64encode(replacement_bytes).decode("ascii"),
        "source_mode": provenance["source_mode"], "replacement_mode": provenance["replacement_mode"],
        "destinations": destinations, "authorization_consumed": False, "replace_request_created": True,
        "worker_invoked": False, "provider_invoked": False, "command_executed": False, "repository_mutated": False, "main_repository_mutated": False, "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return validate_authenticated_replace_request_v2(request)


def bind_consumed_g31_authenticated_replace_worker_selection(
    *,
    authenticated_request: dict[str, Any],
    authorization_reconstruction: dict[str, Any],
    consumption_reconstruction: dict[str, Any],
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Project exact consumed R07 evidence into the certified selector and stop."""

    request = validate_authenticated_replace_request_v2(authenticated_request)
    if not isinstance(authorization_reconstruction, dict) or not isinstance(
        consumption_reconstruction, dict
    ):
        raise FailClosedRuntimeError("consumed replacement selection evidence is incomplete")
    parent = reconstruct_authenticated_replace_replay_v2(request)
    request_wrapper = load_json(Path(request["destinations"]["request"]))
    request_stage_hash = replay_hash([request_wrapper])
    authorization = authorization_reconstruction
    consumption = consumption_reconstruction
    if not all(
        (
            authorization.get("authorization_id") == request["authorization_id"],
            authorization.get("authorization_hash") == request["authorization_hash"],
            authorization.get("authorization_status") == request["authorization_status"] == "AUTHORIZED",
            authorization.get("authorization_replay_hash") == request["authorization_replay_hash"],
            authorization.get("canonical_authorization_actor") == request["canonical_authorization_actor"],
            authorization.get("worker_id") == request["worker_id"] == FILESYSTEM_REPLACE_WORKER_ID,
            authorization.get("session_id") == request["session_id"],
            authorization.get("candidate_id") == request["candidate_id"],
            authorization.get("candidate_hash") == request["candidate_hash"],
            authorization.get("mutation_decision_id") == request["mutation_decision_id"],
            authorization.get("mutation_decision_hash") == request["mutation_decision_hash"],
            authorization.get("target_path") == request["target_path"],
            authorization.get("expected_source_sha256") == request["preimage_sha256"],
            parent.get("event_keys") == ["request", "consumption"],
            parent.get("latest_event") == "AUTHORIZATION_CONSUMPTION_CLAIMED",
            parent.get("replay_artifact_count") == 2,
            parent.get("request_id") == request["request_id"],
            parent.get("request_hash") == request["request_hash"],
            parent.get("authorization_id") == request["authorization_id"],
            consumption.get("request_id") == parent["request_id"],
            consumption.get("request_hash") == parent["request_hash"],
            consumption.get("authorization_id") == parent["authorization_id"],
            consumption.get("authorization_hash") == request["authorization_hash"],
            consumption.get("consumption_identity") == request["authorization_hash"],
            consumption.get("request_stage_replay_hash") == request_stage_hash,
            consumption.get("request_replay_reference") == parent["request_replay_reference"],
            consumption.get("replay_hash") == parent["replay_hash"],
            consumption.get("authorization_consumed") is True,
            consumption.get("worker_selected") is False,
            consumption.get("worker_dispatched") is False,
            consumption.get("worker_invoked") is False,
            consumption.get("provider_invoked") is False,
            consumption.get("command_executed") is False,
            consumption.get("repository_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError("consumed replacement selection lineage mismatch")

    registry = default_resource_registry()
    try:
        checked_certification = load_json(R08B_CERTIFICATION_PATH)
    except (OSError, ValueError, TypeError) as exc:
        raise FailClosedRuntimeError(
            "consumed replacement selection certification is unavailable"
        ) from exc
    certification = validate_worker_selection_certification_v1(
        checked_certification, registry
    )
    resources = [
        value for value in registry["resources"]
        if value.get("resource_id") == FILESYSTEM_REPLACE_WORKER_ID
    ]
    resource = resources[0] if len(resources) == 1 else {}
    bindings = resource.get("role_bindings") or ()
    role = bindings[0] if len(bindings) == 1 else {}
    if not all(
        (
            registry["registry_hash"] == R08B_REGISTRY_HASH,
            certification["artifact_hash"] == R08B_CERTIFICATION_HASH,
            resource.get("resource_version") == EXISTING_FILE_GOVERNANCE_VERSION,
            resource.get("resource_category") == "WORKER",
            resource.get("lifecycle_status") == "AVAILABLE",
            role.get("role_type") == WORKER_ROLE,
            role.get("capability_ids") == ("REPLACE_EXISTING_TEXT_FILE",),
            role.get("authority_profile") == "WORKER_AUTHORIZED_TASK_ONLY",
            role.get("domain_scope") == ("NATIVE_DEVELOPMENT",),
        )
    ):
        raise FailClosedRuntimeError("consumed replacement selection certification mismatch")

    context_identity = (
        f"{request['request_id']}:R07-CONSUMED-REPLACEMENT-SELECTION-CONTEXT"
    )
    context = {
        "context_type": "R07_CONSUMED_REPLACEMENT_SELECTION_CONTEXT_V1",
        "context_identity": context_identity,
        "worker_id": request["worker_id"],
        "worker_version": resource["resource_version"],
        "operation": request["worker_operation"],
        "role_type": role["role_type"],
        "authority_profile": role["authority_profile"],
        "domain_id": "NATIVE_DEVELOPMENT",
        "worker_authorization_required": True,
        "repository_identity": request["repository_identity"],
        "session_identity": request["session_id"],
        "decision_identity": request["mutation_decision_id"],
        "decision_hash": request["mutation_decision_hash"],
        "authorization_identity": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "authenticated_request_identity": request["request_id"],
        "authenticated_request_hash": request["request_hash"],
        "consumption_identity": consumption["consumption_identity"],
        "consumption_hash": parent["last_wrapper_hash"],
        "consumption_replay_hash": parent["replay_hash"],
        "target_identity": {
            "target_path": request["target_path"],
            "preimage_sha256": request["preimage_sha256"],
            "postimage_sha256": request["postimage_sha256"],
            "source_content_hash": request["source_content_hash"],
            "replacement_content_hash": request["replacement_content_hash"],
            "source_mode": request["source_mode"],
            "replacement_mode": request["replacement_mode"],
        },
        "predecessor_ordering": ["request", "consumption"],
        "parent_replay_reference": parent["request_replay_reference"],
        "parent_replay_hash": parent["replay_hash"],
        "certified_registry_hash": registry["registry_hash"],
        "certification_report_hash": certification["artifact_hash"],
    }
    context_hash = replay_hash(context)
    selection = select_unified_resource(
        selection_id=f"{request['request_id']}:CERTIFIED-WORKER-SELECTION",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability=request["worker_operation"],
        requested_role_type=WORKER_ROLE,
        domain_id="NATIVE_DEVELOPMENT",
        created_at=authorization["authorization_record"]["authorization_timestamp"],
        replay_dir=replay_dir,
        worker_authorization_required=True,
        min_trust_level="HIGH",
        preferred_resource_id=request["worker_id"],
        context_assembly_output={
            "context_reference": context_identity,
            "context_hash": context_hash,
        },
        registry=registry,
    )
    artifact = selection["resource_selection_artifact"]
    reconstructed = reconstruct_unified_resource_selection_replay(replay_dir)
    if not all(
        (
            selection["selection_status"] == RESOURCE_SELECTION_SUCCEEDED,
            selection["selected_resource_id"] == FILESYSTEM_REPLACE_WORKER_ID,
            selection["selected_role_type"] == WORKER_ROLE,
            artifact.get("selected_resource_version") == EXISTING_FILE_GOVERNANCE_VERSION,
            artifact.get("selected_authority_profile") == "WORKER_AUTHORIZED_TASK_ONLY",
            artifact.get("required_capability") == request["worker_operation"],
            artifact.get("registry_hash") == R08B_REGISTRY_HASH,
            artifact.get("context_reference") == context_identity,
            artifact.get("context_hash") == context_hash,
            reconstructed.get("selection_status") == RESOURCE_SELECTION_SUCCEEDED,
            reconstructed.get("selected_resource_id") == FILESYSTEM_REPLACE_WORKER_ID,
            reconstructed.get("required_capability") == request["worker_operation"],
            reconstructed.get("registry_hash") == R08B_REGISTRY_HASH,
            selection.get("provider_invoked") is False,
            selection.get("worker_invoked") is False,
            selection.get("dispatch_requested") is False,
            selection.get("execution_requested") is False,
        )
    ):
        raise FailClosedRuntimeError("consumed replacement Worker selection mismatch")
    selection.update(
        {
            "consumed_replacement_selection_context": context,
            "consumed_replacement_selection_context_hash": context_hash,
            "parent_request_consumption_reconstruction": parent,
            "certified_selection_reconstruction": reconstructed,
            "worker_selected": True,
            "worker_assigned": False,
            "worker_dispatched": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "command_executed": False,
            "target_opened": False,
            "repository_mutated": False,
            "restoration_started": False,
            "rollback_started": False,
            "recovery_started": False,
        }
    )
    return selection


def execute_g31_authenticated_replace(*, actor_replay_capture: dict[str, Any], **evidence: Any) -> dict[str, Any]:
    """Non-live hardened entry point; reconstructs authorization before any write."""
    return _execute_authenticated_replace_v2(create_g31_authenticated_replace_request(
        actor_replay_capture=actor_replay_capture, **evidence))
def recover_g31_authenticated_replace(*, actor_replay_capture: dict[str, Any], **evidence: Any) -> dict[str, Any]:
    """Recover an interrupted hardened replacement from its authenticated journal."""
    return _recover_authenticated_replace_v2(create_g31_authenticated_replace_request(
        actor_replay_capture=actor_replay_capture, **evidence))


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
