"""OCS-owned candidate helpers for governed existing-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.workers.filesystem_replace_worker import (
    AUTHORIZED_REPLACE_SCOPE,
    FILESYSTEM_REPLACE_WORKER_ID,
    OPERATION_REPLACE_EXISTING_TEXT_FILE,
)


EXISTING_FILE_MUTATION_CANDIDATE_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1 = "EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1"
EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2 = "EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2"
G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION = "G31_24G_R01_EXISTING_FILE_MUTATION_CANDIDATE_V2"
G31_CANDIDATE_REPLAY_STEPS = (
    "existing_file_mutation_candidate_request_recorded",
    "existing_file_mutation_candidate_recorded",
    "existing_file_mutation_candidate_returned",
)
REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE = (
    "REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE"
)
MAX_CONTENT_BYTES = 64 * 1024


def create_existing_file_mutation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    target_path: str,
    expected_content_hash: str,
    replacement_content: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    """Create the OCS candidate for replacing one existing plaintext file."""

    relative_path = validate_existing_file_target_path(target_path)
    content = validate_plaintext_replacement_content(replacement_content)
    artifact = {
        "artifact_type": EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE,
        "worker_id": FILESYSTEM_REPLACE_WORKER_ID,
        "worker_scope": AUTHORIZED_REPLACE_SCOPE,
        "worker_operation": OPERATION_REPLACE_EXISTING_TEXT_FILE,
        "allowlisted_workspace": _require_string(workspace, "workspace"),
        "target_path": relative_path,
        "expected_content_hash": _require_string(expected_content_hash, "expected_content_hash"),
        "replacement_content": content,
        "replacement_content_hash": replay_hash(content),
        "file_count": 1,
        "plaintext_utf8_only": True,
        "existing_file_required": True,
        "full_file_replacement_only": True,
        "new_file_creation_allowed": False,
        "multi_file_mutation_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "additional_worker_dispatch_allowed": False,
        "human_approval_required": True,
        "governance_authorization_required": True,
        "rollback_required": True,
        "validation_required": True,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_existing_file_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate an OCS existing-file mutation candidate without executing it."""

    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("existing-file mutation failed closed: candidate artifact required")
    if artifact.get("operation") != REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: operation not authorized")
    if artifact.get("worker_id") != FILESYSTEM_REPLACE_WORKER_ID:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_REPLACE_SCOPE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_REPLACE_EXISTING_TEXT_FILE:
        raise FailClosedRuntimeError("existing-file mutation failed closed: Worker operation mismatch")
    if artifact.get("file_count") != 1:
        raise FailClosedRuntimeError("existing-file mutation failed closed: exactly one file required")
    if artifact.get("existing_file_required") is not True or artifact.get("full_file_replacement_only") is not True:
        raise FailClosedRuntimeError("existing-file mutation failed closed: full replacement of existing file required")
    for flag in (
        "new_file_creation_allowed",
        "multi_file_mutation_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "additional_worker_dispatch_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"existing-file mutation failed closed: {flag} must be false")
    validate_existing_file_target_path(artifact.get("target_path"))
    content = validate_plaintext_replacement_content(artifact.get("replacement_content"))
    if artifact.get("replacement_content_hash") != replay_hash(content):
        raise FailClosedRuntimeError("existing-file mutation failed closed: replacement content hash mismatch")
    _require_string(artifact.get("expected_content_hash"), "expected_content_hash")
    return artifact


def create_g31_accepted_existing_file_mutation_candidate(
    *, candidate_id: str, acceptance_capture: dict[str, Any], decision_capture: dict[str, Any],
    binding_capture: dict[str, Any], repository_grounding_artifact: dict[str, Any],
    session_root: str | Path, created_by: str, created_at: str, replay_dir: str | Path,
) -> dict[str, Any]:
    """Project one exact accepted G31 V2 replacement into a replayed V2 candidate."""
    root, path = Path(session_root).resolve(), Path(replay_dir).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("G31 existing-file candidate Replay is cross-session")
    subject = _g31_candidate_subject(acceptance_capture, decision_capture, binding_capture,
                                     repository_grounding_artifact, root)
    _ensure_g31_candidate_destination(root, path, subject["binding_hash"])
    artifact = {
        "artifact_type": EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2,
        "runtime_version": G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": subject["session_id"], "operation": "REPLACE_CONTENT",
        "target_path": subject["target_path"], "file_count": 1,
        "candidate_provenance": subject, "candidate_provenance_binding_hash": subject["binding_hash"],
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "human_mutation_decision_recorded": False, "mutation_authorized": False,
        "main_repository_mutated": False, "provider_invoked": False, "worker_invoked": False,
        "command_executed": False, "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    validate_g31_accepted_existing_file_mutation_candidate(artifact)
    request = {"artifact_type": "EXISTING_FILE_MUTATION_CANDIDATE_REQUEST_V2",
               "candidate_id": artifact["candidate_id"], "candidate_provenance_binding_hash": subject["binding_hash"],
               "created_at": artifact["created_at"]}
    request["artifact_hash"] = replay_hash(request)
    returned = {"artifact_type": "EXISTING_FILE_MUTATION_CANDIDATE_RETURNED_V2",
                "candidate_id": artifact["candidate_id"], "candidate_hash": artifact["artifact_hash"],
                "candidate_provenance_binding_hash": subject["binding_hash"], "mutation_authorized": False,
                "main_repository_mutated": False}
    returned["artifact_hash"] = replay_hash(returned)
    for index, value in enumerate((request, artifact, returned)):
        _persist_g31_candidate_step(path, index, value)
    return {"existing_file_mutation_candidate_artifact": deepcopy(artifact),
            "candidate_replay_reference": str(path), "candidate_replay_hash": replay_hash([
                _load_g31_wrapper(path, index) for index in range(3)]),
            "existing_file_mutation_candidate_created": True, "result_accepted": True,
            "human_mutation_decision_recorded": False, "mutation_authorized": False,
            "main_repository_mutated": False}


def reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
    *, candidate_capture: dict[str, Any], acceptance_capture: dict[str, Any], decision_capture: dict[str, Any],
    binding_capture: dict[str, Any], repository_grounding_artifact: dict[str, Any], session_root: str | Path,
) -> dict[str, Any]:
    """Reconstruct one exact G31 V2 candidate Replay and its accepted lineage."""
    root, path = Path(session_root).resolve(), Path(candidate_capture.get("candidate_replay_reference", "")).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("G31 existing-file candidate Replay is cross-session")
    wrappers = [_load_g31_wrapper(path, index) for index in range(3)]
    request, candidate, returned = [item["artifact"] for item in wrappers]
    validate_g31_accepted_existing_file_mutation_candidate(candidate)
    subject = _g31_candidate_subject(acceptance_capture, decision_capture, binding_capture,
                                     repository_grounding_artifact, root)
    if not all((candidate_capture.get("existing_file_mutation_candidate_artifact") == candidate,
                candidate.get("candidate_provenance") == subject,
                request.get("candidate_id") == candidate.get("candidate_id"),
                request.get("candidate_provenance_binding_hash") == subject["binding_hash"],
                returned.get("candidate_hash") == candidate.get("artifact_hash"),
                returned.get("candidate_provenance_binding_hash") == subject["binding_hash"],
                returned.get("mutation_authorized") is False, returned.get("main_repository_mutated") is False)):
        raise FailClosedRuntimeError("G31 existing-file candidate Replay identity mismatch")
    return {"candidate_id": candidate["candidate_id"], "candidate_hash": candidate["artifact_hash"],
            "candidate_provenance_binding_hash": subject["binding_hash"], "replay_artifact_count": 3,
            "replay_hash": replay_hash(wrappers), "result_accepted": True,
            "human_mutation_decision_recorded": False, "mutation_authorized": False,
            "main_repository_mutated": False}


def render_g31_accepted_existing_file_mutation_candidate(candidate_capture: dict[str, Any]) -> str:
    """Render a truthful pre-authorization candidate review."""
    candidate = candidate_capture.get("existing_file_mutation_candidate_artifact") or {}
    validate_g31_accepted_existing_file_mutation_candidate(candidate)
    subject = candidate["candidate_provenance"]
    return "\n".join(("Existing-File Mutation Candidate", f"Candidate: {candidate['candidate_id']}",
        f"Target: {subject['target_path']}", f"Operation: {subject['operation']}",
        f"Preimage: {subject['preimage_sha256']}", f"Postimage: {subject['postimage_sha256']}",
        f"Replay: {candidate_capture['candidate_replay_reference']}", "Content is accepted.",
        "No human mutation decision has been recorded.", "Mutation Authorized: False",
        "Main Repository Mutated: False"))


def validate_g31_accepted_existing_file_mutation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate the V2 candidate shape without authorizing or mutating."""
    if not isinstance(candidate, dict) or candidate.get("artifact_type") != EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2:
        raise FailClosedRuntimeError("G31 existing-file candidate artifact required")
    value = deepcopy(candidate); actual = value.pop("artifact_hash", None)
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("G31 existing-file candidate hash mismatch")
    subject = candidate.get("candidate_provenance")
    required = ("session_id", "repository_identity", "repository_root", "repository_grounding_hash",
                "accepted_result_hash", "acceptance_hash", "content_decision_hash", "prerequisite_hash",
                "manifest_hash", "target_path", "preimage_sha256", "postimage_sha256", "source_mode",
                "replacement_mode", "content_validation_hash", "test_validation_hash", "disposable_validation_hash", "binding_hash")
    if not isinstance(subject, dict) or any(not isinstance(subject.get(key), str) or not subject[key] for key in required):
        raise FailClosedRuntimeError("G31 existing-file candidate provenance incomplete")
    if not all((candidate.get("session_id") == subject["session_id"], candidate.get("operation") == "REPLACE_CONTENT",
                subject.get("operation") == "REPLACE_CONTENT", candidate.get("target_path") == subject["target_path"],
                candidate.get("candidate_provenance_binding_hash") == subject["binding_hash"], candidate.get("file_count") == 1,
                candidate.get("human_mutation_decision_recorded") is False, candidate.get("mutation_authorized") is False,
                candidate.get("main_repository_mutated") is False, candidate.get("provider_invoked") is False,
                candidate.get("worker_invoked") is False, candidate.get("command_executed") is False)):
        raise FailClosedRuntimeError("G31 existing-file candidate authority or provenance mismatch")
    return deepcopy(candidate)


def _g31_candidate_subject(acceptance_capture: dict[str, Any], decision_capture: dict[str, Any],
                           binding_capture: dict[str, Any], grounding_artifact: dict[str, Any], root: Path) -> dict[str, str]:
    from aigol.runtime.approved_durable_work_repository_scope_grounding import (
        reconstruct_approved_durable_work_repository_scope_grounding,
        validate_approved_durable_work_repository_scope_grounding,
    )
    from aigol.runtime.codex_replacement_acceptance_prerequisite_binding_runtime import (
        reconstruct_codex_replacement_acceptance_prerequisite_binding,
    )
    from aigol.runtime.generated_content_acceptance_runtime import (
        reconstruct_generated_content_acceptance_from_decision_replay,
        verify_generated_content_acceptance_artifact,
    )
    from aigol.runtime.human_decision_runtime import reconstruct_content_acceptance_decision_replay
    from aigol.runtime.implementation_manifest_runtime import REPLACE_CONTENT, reconstruct_implementation_manifest_replay
    accepted = reconstruct_generated_content_acceptance_from_decision_replay(
        acceptance_capture=acceptance_capture, decision_capture=decision_capture,
        binding_capture=binding_capture, session_root=root)
    decision = reconstruct_content_acceptance_decision_replay(
        decision_capture=decision_capture, binding_capture=binding_capture, session_root=root)
    bound = reconstruct_codex_replacement_acceptance_prerequisite_binding(
        binding_capture=binding_capture, session_root=root)
    acceptance = acceptance_capture.get("generated_content_acceptance_artifact") or {}
    manifest_capture = binding_capture.get("implementation_manifest_capture") or {}
    manifest = manifest_capture.get("implementation_manifest_artifact") or {}
    content = (binding_capture.get("generated_content_validation_capture") or {}).get("generated_content_validation_artifact") or {}
    tests = (binding_capture.get("generated_test_validation_capture") or {}).get("generated_test_validation_artifact") or {}
    prerequisite = (binding_capture.get("acceptance_prerequisite_capture") or {}).get("acceptance_prerequisite_artifact") or {}
    verify_generated_content_acceptance_artifact(acceptance)
    manifest_replay = reconstruct_implementation_manifest_replay(manifest_capture.get("implementation_manifest_replay_reference", ""))
    grounding = validate_approved_durable_work_repository_scope_grounding(grounding_artifact, workspace=manifest.get("source_workspace"))
    reconstructed_grounding = reconstruct_approved_durable_work_repository_scope_grounding(
        grounding["replay_reference"], workspace=manifest["source_workspace"])
    files = manifest.get("file_entries")
    if not all((accepted.get("result_accepted") is True, accepted.get("mutation_authorized") is False,
                decision.get("decision_outcome") == "ACCEPTED", bound.get("ready_for_acceptance") is True,
                manifest.get("operation_mode") == REPLACE_CONTENT, manifest.get("canonical_session_id") == root.name,
                isinstance(files, list) and len(files) == 1, manifest_replay.get("manifest_id") == manifest.get("manifest_id"),
                reconstructed_grounding.get("artifact_hash") == grounding.get("artifact_hash"))):
        raise FailClosedRuntimeError("G31 existing-file candidate requires exact accepted replacement evidence")
    entry = files[0]
    if not all((entry.get("operation") == REPLACE_CONTENT, entry.get("file_type") == "REGULAR_FILE",
                entry.get("postimage_file_type") == "REGULAR_FILE", entry.get("file_mode") == entry.get("postimage_file_mode"),
                entry.get("target_path") in grounding.get("grounded_repository_targets", []))):
        raise FailClosedRuntimeError("G31 existing-file candidate target or mode lineage mismatch")
    subject = {
        "session_id": manifest["canonical_session_id"], "repository_identity": grounding["grounding_identity"],
        "repository_root": grounding["workspace_root"], "repository_grounding_hash": grounding["grounding_evidence_hash"],
        "repository_grounding_replay_reference": grounding["replay_reference"], "repository_grounding_replay_hash": replay_hash([grounding]), "accepted_result_id": acceptance["acceptance_id"],
        "accepted_result_hash": acceptance["artifact_hash"], "accepted_result_replay_hash": accepted["replay_hash"],
        "accepted_result_replay_reference": acceptance_capture["acceptance_replay_reference"],
        "acceptance_id": acceptance["acceptance_id"], "acceptance_hash": acceptance["artifact_hash"],
        "acceptance_replay_hash": accepted["replay_hash"], "content_decision_id": decision["human_decision_id"],
        "content_decision_hash": decision_capture["human_decision_artifact"]["artifact_hash"],
        "content_decision_replay_reference": decision_capture["human_decision_replay_reference"], "content_decision_replay_hash": decision["replay_hash"], "prerequisite_id": prerequisite["prerequisite_id"],
        "prerequisite_hash": prerequisite["prerequisite_hash"], "prerequisite_replay_reference": binding_capture["binding_replay_reference"], "prerequisite_replay_hash": bound["replay_hash"],
        "manifest_id": manifest["manifest_id"], "manifest_hash": manifest["artifact_hash"],
        "manifest_replay_reference": manifest_capture["implementation_manifest_replay_reference"], "manifest_replay_hash": manifest_replay["replay_hash"], "operation": REPLACE_CONTENT,
        "target_path": entry["target_path"], "preimage_sha256": entry["preimage_sha256"],
        "postimage_sha256": entry["postimage_sha256"], "source_content_hash": replay_hash(entry["preimage_content"]),
        "replacement_content_hash": replay_hash(entry["postimage_content"]), "source_mode": str(entry["file_mode"]),
        "replacement_mode": str(entry["postimage_file_mode"]), "content_validation_id": content["validation_id"], "content_validation_hash": content["artifact_hash"],
        "test_validation_id": tests["validation_id"], "test_validation_hash": tests["artifact_hash"], "disposable_validation_hash": bound["binding_hash"],
    }
    subject["binding_hash"] = replay_hash(subject)
    return subject


def _ensure_g31_candidate_destination(root: Path, path: Path, binding_hash: str) -> None:
    if any((path / f"{index:03d}_{step}.json").exists() for index, step in enumerate(G31_CANDIDATE_REPLAY_STEPS)):
        raise FailClosedRuntimeError("G31 existing-file candidate destination already exists")
    for existing in root.rglob(f"001_{G31_CANDIDATE_REPLAY_STEPS[1]}.json"):
        wrapper = _load_g31_wrapper(existing.parent, 1)
        provenance = (wrapper.get("artifact") or {}).get("candidate_provenance") or {}
        if provenance.get("binding_hash") == binding_hash:
            raise FailClosedRuntimeError("G31 existing-file candidate accepted result already consumed")


def _persist_g31_candidate_step(path: Path, index: int, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": G31_CANDIDATE_REPLAY_STEPS[index],
               "event_type": G31_CANDIDATE_REPLAY_STEPS[index].upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{G31_CANDIDATE_REPLAY_STEPS[index]}.json", wrapper)


def _load_g31_wrapper(path: Path, index: int) -> dict[str, Any]:
    wrapper = load_json(path / f"{index:03d}_{G31_CANDIDATE_REPLAY_STEPS[index]}.json")
    expected = deepcopy(wrapper); actual = expected.pop("replay_hash", None)
    if not all((wrapper.get("replay_index") == index, wrapper.get("replay_step") == G31_CANDIDATE_REPLAY_STEPS[index],
                actual == replay_hash(expected), isinstance(wrapper.get("artifact"), dict))):
        raise FailClosedRuntimeError("G31 existing-file candidate Replay ordering or hash mismatch")
    return wrapper


def validate_existing_file_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    path = Path(path_text)
    if path.is_absolute() or path_text in {".", ".."}:
        raise FailClosedRuntimeError("existing-file mutation failed closed: target path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("existing-file mutation failed closed: target path must not contain traversal")
    return path.as_posix()


def validate_plaintext_replacement_content(value: Any) -> str:
    content = _require_string(value, "replacement_content")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_CONTENT_BYTES:
        raise FailClosedRuntimeError("existing-file mutation failed closed: replacement content too large")
    if "\x00" in content:
        raise FailClosedRuntimeError("existing-file mutation failed closed: binary content not allowed")
    return content


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
