"""Thin Human-authorized coordinator for one governed local repository commit."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any

from aigol.runtime.governed_git_commit_runtime import (
    GOVERNED_GIT_COMMIT_COMPLETED,
    execute_governed_git_commit,
    reconstruct_governed_git_commit_replay,
)
from aigol.runtime.governed_repository_mutation_runtime import (
    observe_repository_mutation_envelope,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_git_commit_candidate import (
    ADD_TEXT_FILE,
    REPLACE_TEXT_FILE,
    create_governed_git_commit_candidate,
)
from aigol.runtime.platform_core_git_commit_governance import (
    create_governed_git_commit_approval,
)
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
    reconstruct_validation_command_replay,
)
from runtime.governance.governance_conformance_engine import run_conformance_check


FINALIZATION_RUNTIME_VERSION = "G77_256FU_GOVERNED_REPOSITORY_FINALIZATION_V1"
FINALIZATION_CONTRACT_ARTIFACT_V1 = "GOVERNED_REPOSITORY_FINALIZATION_CONTRACT_V1"
FINALIZATION_RESULT_ARTIFACT_V1 = "GOVERNED_REPOSITORY_FINALIZATION_RESULT_V1"
FINALIZATION_COMPLETED = "GOVERNED_REPOSITORY_FINALIZATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
VALIDATION_PROFILE = "SAPIANTA_GOVERNED_FINALIZATION_V1"
HUMAN_INVOCATION = "FINALIZE_EXACT_CONTRACT"
REPLAY_STEPS = (
    "finalization_contract_recorded",
    "finalization_result_recorded",
)


def create_governed_repository_finalization_contract(
    *,
    contract_id: str,
    repository_root: str | Path,
    repository_id: str,
    expected_branch: str,
    expected_parent_head: str,
    expected_parent_tree: str,
    authorized_mutations: list[dict[str, Any]],
    commit_message: dict[str, str],
    author: dict[str, str],
    nested_authority: dict[str, str],
    authorized_by: str,
    authorized_at: str,
) -> dict[str, Any]:
    """Create the exact contract consumed by one explicit Human invocation."""

    artifact = {
        "artifact_type": FINALIZATION_CONTRACT_ARTIFACT_V1,
        "runtime_version": FINALIZATION_RUNTIME_VERSION,
        "contract_id": _validate_contract_id(contract_id),
        "repository_root": str(Path(repository_root).resolve()),
        "repository_id": _require_string(repository_id, "repository_id"),
        "expected_branch": _require_string(expected_branch, "expected_branch"),
        "expected_parent_head": _require_git_identity(expected_parent_head, "expected_parent_head"),
        "expected_parent_tree": _require_git_identity(expected_parent_tree, "expected_parent_tree"),
        "authorized_mutations": _validate_authorized_mutations(authorized_mutations),
        "commit_message": _validate_commit_message(commit_message),
        "author": _validate_author(author),
        "validation_profile": VALIDATION_PROFILE,
        "nested_authority": _validate_nested_authority(nested_authority),
        "human_authorization": {
            "decision": "APPROVED",
            "invocation": HUMAN_INVOCATION,
            "authorized_by": _require_string(authorized_by, "authorized_by"),
            "authorized_at": _require_string(authorized_at, "authorized_at"),
            "candidate_readiness_is_not_authority": True,
        },
        "commit_count_maximum": 1,
        "local_commit_only": True,
        "push_allowed": False,
        "remote_interaction_allowed": False,
        "branch_management_allowed": False,
        "hook_bypass_allowed": False,
        "human_invocation_required": True,
        "new_authority_truth_created": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_repository_finalization_contract(
    contract_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate the complete bounded Human finalization contract."""

    if not isinstance(contract_artifact, dict):
        raise FailClosedRuntimeError("finalization failed closed: contract artifact required")
    contract = deepcopy(contract_artifact)
    actual_hash = _require_hash(contract.get("artifact_hash"), "artifact_hash")
    expected = deepcopy(contract)
    expected.pop("artifact_hash")
    if replay_hash(expected) != actual_hash:
        raise FailClosedRuntimeError("finalization failed closed: contract hash mismatch")
    if contract.get("artifact_type") != FINALIZATION_CONTRACT_ARTIFACT_V1:
        raise FailClosedRuntimeError("finalization failed closed: contract artifact type mismatch")
    if contract.get("runtime_version") != FINALIZATION_RUNTIME_VERSION:
        raise FailClosedRuntimeError("finalization failed closed: contract runtime mismatch")
    _validate_contract_id(contract.get("contract_id"))
    root_text = _require_string(contract.get("repository_root"), "repository_root")
    if not Path(root_text).is_absolute() or str(Path(root_text).resolve()) != root_text:
        raise FailClosedRuntimeError("finalization failed closed: repository root must be canonical and absolute")
    _require_string(contract.get("repository_id"), "repository_id")
    _require_string(contract.get("expected_branch"), "expected_branch")
    _require_git_identity(contract.get("expected_parent_head"), "expected_parent_head")
    _require_git_identity(contract.get("expected_parent_tree"), "expected_parent_tree")
    mutations = _validate_authorized_mutations(contract.get("authorized_mutations"))
    if mutations != contract["authorized_mutations"]:
        raise FailClosedRuntimeError("finalization failed closed: mutation envelope is not canonical")
    if _validate_commit_message(contract.get("commit_message")) != contract["commit_message"]:
        raise FailClosedRuntimeError("finalization failed closed: commit message is not canonical")
    if _validate_author(contract.get("author")) != contract["author"]:
        raise FailClosedRuntimeError("finalization failed closed: author is not canonical")
    if contract.get("validation_profile") != VALIDATION_PROFILE:
        raise FailClosedRuntimeError("finalization failed closed: validation profile mismatch")
    if _validate_nested_authority(contract.get("nested_authority")) != contract["nested_authority"]:
        raise FailClosedRuntimeError("finalization failed closed: nested authority is not canonical")
    authorization = contract.get("human_authorization")
    if not isinstance(authorization, dict):
        raise FailClosedRuntimeError("finalization failed closed: Human authorization required")
    if authorization.get("decision") != "APPROVED" or authorization.get("invocation") != HUMAN_INVOCATION:
        raise FailClosedRuntimeError("finalization failed closed: explicit Human authorization required")
    _require_string(authorization.get("authorized_by"), "authorized_by")
    _require_string(authorization.get("authorized_at"), "authorized_at")
    if authorization.get("candidate_readiness_is_not_authority") is not True:
        raise FailClosedRuntimeError("finalization failed closed: Human authority separation missing")
    required_true = ("local_commit_only", "human_invocation_required", "replay_visible")
    required_false = (
        "push_allowed",
        "remote_interaction_allowed",
        "branch_management_allowed",
        "hook_bypass_allowed",
        "new_authority_truth_created",
    )
    if contract.get("commit_count_maximum") != 1:
        raise FailClosedRuntimeError("finalization failed closed: exactly one commit maximum required")
    if any(contract.get(field) is not True for field in required_true):
        raise FailClosedRuntimeError("finalization failed closed: required boundary missing")
    if any(contract.get(field) is not False for field in required_false):
        raise FailClosedRuntimeError("finalization failed closed: prohibited authority requested")
    return contract


def execute_governed_repository_finalization(
    *,
    contract_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Authenticate, validate, commit once through the existing Worker, and verify."""

    contract: dict[str, Any] | None = None
    root: Path | None = None
    replay_path: Path | None = None
    commit_capture: dict[str, Any] | None = None
    validation_artifact: dict[str, Any] | None = None
    try:
        contract = validate_governed_repository_finalization_contract(contract_artifact)
        root = _authenticate_root_authority(contract)
        _authenticate_nested_authority(root, contract["nested_authority"])
        observed = observe_repository_mutation_envelope(root)
        _require_exact_mutation_envelope(observed, contract["authorized_mutations"])

        replay_path = _resolve_replay_path(root, contract["contract_id"])
        _ensure_replay_available(replay_path)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], contract)

        validation_artifact = _run_required_validation(
            root=root,
            contract=contract,
            replay_path=replay_path / "validation",
        )
        observed_after_validation = observe_repository_mutation_envelope(root)
        _require_exact_mutation_envelope(
            observed_after_validation,
            contract["authorized_mutations"],
        )

        candidate = create_governed_git_commit_candidate(
            candidate_id=f"{contract['contract_id']}:COMMIT-CANDIDATE",
            session_id=contract["contract_id"],
            repository_id=contract["repository_id"],
            branch_name=contract["expected_branch"],
            expected_head=contract["expected_parent_head"],
            file_set=deepcopy(contract["authorized_mutations"]),
            commit_message=deepcopy(contract["commit_message"]),
            author=deepcopy(contract["author"]),
            validation_artifact=validation_artifact,
            created_by="GOVERNED_REPOSITORY_FINALIZATION_COORDINATOR",
            created_at=contract["human_authorization"]["authorized_at"],
        )
        approval = create_governed_git_commit_approval(
            approval_id=f"{contract['contract_id']}:COMMIT-APPROVAL",
            candidate_artifact=candidate,
            confirmation_text=(
                f"confirm governed git commit {candidate['candidate_id']} {candidate['artifact_hash']}"
            ),
            approved_by=contract["human_authorization"]["authorized_by"],
            approved_at=contract["human_authorization"]["authorized_at"],
        )
        commit_capture = execute_governed_git_commit(
            execution_id=f"{contract['contract_id']}:COMMIT",
            candidate_artifact=candidate,
            approval_artifact=approval,
            validation_artifact=validation_artifact,
            repository_root=root,
            executed_by="GOVERNED_REPOSITORY_FINALIZATION_COORDINATOR",
            executed_at=contract["human_authorization"]["authorized_at"],
            replay_dir=replay_path / "governed_git_commit",
        )
        if commit_capture.get("execution_status") != GOVERNED_GIT_COMMIT_COMPLETED:
            reason = commit_capture.get("failure_reason") or "existing governed commit runtime failed"
            raise FailClosedRuntimeError(f"finalization failed closed: {reason}")

        post_commit = _verify_post_commit_state(root, contract, commit_capture)
        result = _result_artifact(
            contract=contract,
            status=FINALIZATION_COMPLETED,
            validation_artifact=validation_artifact,
            commit_capture=commit_capture,
            post_commit=post_commit,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(result, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        result = _failed_result_artifact(
            contract=contract,
            root=root,
            validation_artifact=validation_artifact,
            commit_capture=commit_capture,
            failure_reason=failure_reason,
        )
        if replay_path is not None:
            _persist_failure_if_possible(replay_path, result)
        return _capture(result, replay_path)


def reconstruct_governed_repository_finalization_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the integration result through the existing nested Replay owners."""

    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("finalization Replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("finalization Replay artifact missing")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    contract = validate_governed_repository_finalization_contract(wrappers[0]["artifact"])
    result = wrappers[1]["artifact"]
    if result.get("contract_id") != contract["contract_id"]:
        raise FailClosedRuntimeError("finalization Replay contract identity mismatch")
    if result.get("contract_hash") != contract["artifact_hash"]:
        raise FailClosedRuntimeError("finalization Replay contract hash mismatch")

    commit_replay = None
    validation_replay = None
    if result.get("finalization_status") == FINALIZATION_COMPLETED:
        validation_replay = reconstruct_validation_command_replay(
            replay_path / "validation" / "git_diff_check"
        )
        commit_replay = reconstruct_governed_git_commit_replay(
            replay_path / "governed_git_commit"
        )
        if validation_replay.get("command_status") != VALIDATION_COMMAND_COMPLETED:
            raise FailClosedRuntimeError("finalization Replay validation mismatch")
        if commit_replay.get("commit_hash") != result.get("committed_head"):
            raise FailClosedRuntimeError("finalization Replay commit identity mismatch")

    return {
        "contract_id": contract["contract_id"],
        "contract_hash": contract["artifact_hash"],
        "human_authorization": deepcopy(contract["human_authorization"]),
        "expected_parent_head": contract["expected_parent_head"],
        "authorized_mutations": deepcopy(contract["authorized_mutations"]),
        "validation_profile": contract["validation_profile"],
        "finalization_status": result["finalization_status"],
        "commit_effect_count": result["commit_effect_count"],
        "committed_head": result["committed_head"],
        "committed_tree": result["committed_tree"],
        "commit_subject": result["commit_subject"],
        "committed_path_set": deepcopy(result["committed_path_set"]),
        "post_commit_status": result["post_commit_status"],
        "nested_authority": deepcopy(result["nested_authority"]),
        "failure_reason": result["failure_reason"],
        "validation_replay_hash": validation_replay.get("replay_hash") if validation_replay else None,
        "commit_replay_hash": commit_replay.get("replay_hash") if commit_replay else None,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _authenticate_root_authority(contract: dict[str, Any]) -> Path:
    root = Path(contract["repository_root"])
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("finalization failed closed: repository root missing")
    if Path(_git_text(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise FailClosedRuntimeError("finalization failed closed: repository identity mismatch")
    if _git_text(root, "symbolic-ref", "--short", "HEAD") != contract["expected_branch"]:
        raise FailClosedRuntimeError("finalization failed closed: branch mismatch")
    if _git_text(root, "rev-parse", "HEAD") != contract["expected_parent_head"]:
        raise FailClosedRuntimeError("finalization failed closed: parent HEAD mismatch")
    if _git_text(root, "rev-parse", "HEAD^{tree}") != contract["expected_parent_tree"]:
        raise FailClosedRuntimeError("finalization failed closed: parent tree mismatch")
    return root


def _authenticate_nested_authority(root: Path, authority: dict[str, str]) -> dict[str, Any]:
    nested = (root / authority["path"]).resolve()
    try:
        nested.relative_to(root)
    except ValueError as exc:
        raise FailClosedRuntimeError("finalization failed closed: nested path escapes repository") from exc
    if not nested.exists() or not nested.is_dir():
        raise FailClosedRuntimeError("finalization failed closed: nested repository missing")
    if Path(_git_text(nested, "rev-parse", "--show-toplevel")).resolve() != nested:
        raise FailClosedRuntimeError("finalization failed closed: nested repository identity mismatch")
    head = _git_text(nested, "rev-parse", "HEAD")
    tree = _git_text(nested, "rev-parse", "HEAD^{tree}")
    if head != authority["commit"] or tree != authority["tree"]:
        raise FailClosedRuntimeError("finalization failed closed: nested pinned identity mismatch")
    symbolic = subprocess.run(
        ["git", "symbolic-ref", "-q", "HEAD"],
        cwd=nested,
        capture_output=True,
        shell=False,
        check=False,
    )
    if symbolic.returncode != 1:
        raise FailClosedRuntimeError("finalization failed closed: nested HEAD must be detached")
    if _git_bytes(nested, "status", "--porcelain=v1", "-z", "--untracked-files=all"):
        raise FailClosedRuntimeError("finalization failed closed: nested repository is dirty")
    return {"commit": head, "tree": tree, "status": "CLEAN__DETACHED_HEAD"}


def _require_exact_mutation_envelope(
    observed: dict[str, Any],
    authorized: list[dict[str, Any]],
) -> None:
    observed_entries = [
        {
            "path": item["path"],
            "change_type": item["change_type"],
            "content_hash": item["content_hash"],
        }
        for item in observed["mutations"]
    ]
    if observed_entries != authorized:
        raise FailClosedRuntimeError("finalization failed closed: observed mutation envelope mismatch")


def _run_required_validation(
    *,
    root: Path,
    contract: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    request = create_validation_command_request(
        request_id=f"{contract['contract_id']}:GIT-DIFF-CHECK",
        command=["git", "diff", "--check"],
        cwd=str(root),
        requested_by=contract["human_authorization"]["authorized_by"],
        requested_at=contract["human_authorization"]["authorized_at"],
        replay_references=[contract["contract_id"]],
        replay_hashes=[contract["artifact_hash"]],
        timeout_seconds=30,
    )
    diff_capture = execute_validation_command(
        request_artifact=request,
        executed_by="GOVERNED_REPOSITORY_FINALIZATION_COORDINATOR",
        executed_at=contract["human_authorization"]["authorized_at"],
        replay_dir=replay_path / "git_diff_check",
    )
    if diff_capture.get("command_status") != VALIDATION_COMMAND_COMPLETED:
        raise FailClosedRuntimeError("finalization failed closed: git diff --check failed")

    conformance = run_conformance_check(root)
    if conformance.get("status") != "CONFORMANT":
        raise FailClosedRuntimeError("finalization failed closed: governance conformance is not CONFORMANT")
    artifact = {
        "artifact_type": VALIDATION_RESULT_ARTIFACT_V1,
        "runtime_version": FINALIZATION_RUNTIME_VERSION,
        "execution_id": f"{contract['contract_id']}:VALIDATION",
        "validation_profile": VALIDATION_PROFILE,
        "validation_status": "VALIDATION_PASSED",
        "validation_passed": True,
        "git_diff_check_result_hash": diff_capture["validation_command_result_artifact"]["artifact_hash"],
        "git_diff_check_replay_reference": diff_capture["validation_command_replay_reference"],
        "governance_conformance_status": conformance["status"],
        "governance_conformance_report_hash": conformance["report_hash"],
        "pre_commit_governance_required": True,
        "nested_hook_enforcement_required": True,
        "repository_mutation_intended": False,
        "commit_created": False,
        "provider_invoked": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_post_commit_state(
    root: Path,
    contract: dict[str, Any],
    commit_capture: dict[str, Any],
) -> dict[str, Any]:
    head = _git_text(root, "rev-parse", "HEAD")
    parent = _git_text(root, "rev-parse", "HEAD^")
    branch = _git_text(root, "symbolic-ref", "--short", "HEAD")
    tree = _git_text(root, "rev-parse", "HEAD^{tree}")
    subject = _git_text(root, "show", "-s", "--format=%s", "HEAD")
    commit_count = int(_git_text(root, "rev-list", "--count", f"{contract['expected_parent_head']}..{head}"))
    if head != commit_capture.get("commit_hash") or parent != contract["expected_parent_head"]:
        raise FailClosedRuntimeError("finalization failed closed: committed parent or HEAD mismatch")
    if branch != contract["expected_branch"]:
        raise FailClosedRuntimeError("finalization failed closed: post-commit branch mismatch")
    if subject != contract["commit_message"]["subject"]:
        raise FailClosedRuntimeError("finalization failed closed: commit subject mismatch")
    if commit_count != 1:
        raise FailClosedRuntimeError("finalization failed closed: commit effect count mismatch")

    committed_paths = _nul_path_list(
        _git_bytes(root, "diff-tree", "--no-commit-id", "--name-only", "-z", "-r", "HEAD")
    )
    authorized_paths = [item["path"] for item in contract["authorized_mutations"]]
    if committed_paths != authorized_paths:
        raise FailClosedRuntimeError("finalization failed closed: committed path set mismatch")
    committed_blobs = _committed_blob_identities(root, head, contract["authorized_mutations"])

    index = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=root,
        capture_output=True,
        shell=False,
        check=False,
    )
    if index.returncode != 0:
        raise FailClosedRuntimeError("finalization failed closed: post-commit index is not empty")
    if _git_bytes(root, "status", "--porcelain=v1", "-z", "--untracked-files=all"):
        raise FailClosedRuntimeError("finalization failed closed: post-commit worktree is not clean")
    nested = _authenticate_nested_authority(root, contract["nested_authority"])
    return {
        "committed_head": head,
        "committed_tree": tree,
        "commit_subject": subject,
        "committed_path_set": committed_paths,
        "committed_blobs": committed_blobs,
        "commit_effect_count": commit_count,
        "index_empty": True,
        "root_worktree_clean": True,
        "nested_authority": nested,
        "post_commit_status": "CLEAN__VERIFIED",
    }


def _committed_blob_identities(
    root: Path,
    head: str,
    authorized: list[dict[str, Any]],
) -> list[dict[str, str]]:
    identities = []
    for entry in authorized:
        path = entry["path"]
        output = _git_bytes(root, "ls-tree", "-z", head, "--", path)
        records = [record for record in output.split(b"\0") if record]
        if len(records) != 1 or b"\t" not in records[0]:
            raise FailClosedRuntimeError("finalization failed closed: committed blob identity missing")
        metadata, raw_path = records[0].split(b"\t", 1)
        try:
            mode, object_type, blob_id = metadata.decode("ascii").split(" ")
            observed_path = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise FailClosedRuntimeError("finalization failed closed: committed blob identity ambiguous") from exc
        if object_type != "blob" or observed_path != path:
            raise FailClosedRuntimeError("finalization failed closed: committed blob identity mismatch")
        blob = _git_bytes(root, "cat-file", "blob", blob_id)
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError("finalization failed closed: committed blob is not UTF-8 text") from exc
        if "\x00" in text or replay_hash(text) != entry["content_hash"]:
            raise FailClosedRuntimeError("finalization failed closed: committed content identity mismatch")
        identities.append(
            {
                "path": path,
                "mode": mode,
                "blob_id": blob_id,
                "content_hash": entry["content_hash"],
            }
        )
    return identities


def _result_artifact(
    *,
    contract: dict[str, Any],
    status: str,
    validation_artifact: dict[str, Any],
    commit_capture: dict[str, Any],
    post_commit: dict[str, Any],
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FINALIZATION_RESULT_ARTIFACT_V1,
        "runtime_version": FINALIZATION_RUNTIME_VERSION,
        "contract_id": contract["contract_id"],
        "contract_hash": contract["artifact_hash"],
        "finalization_status": status,
        "human_authorization_observed": True,
        "validation_artifact_hash": validation_artifact["artifact_hash"],
        "governed_commit_capture_hash": commit_capture["capture_hash"],
        "existing_git_commit_worker_reused": True,
        "parallel_commit_system_created": False,
        "commit_effect_count": post_commit["commit_effect_count"],
        "committed_head": post_commit["committed_head"],
        "committed_tree": post_commit["committed_tree"],
        "commit_subject": post_commit["commit_subject"],
        "committed_path_set": deepcopy(post_commit["committed_path_set"]),
        "committed_blobs": deepcopy(post_commit["committed_blobs"]),
        "post_commit_status": post_commit["post_commit_status"],
        "root_worktree_clean": post_commit["root_worktree_clean"],
        "index_empty": post_commit["index_empty"],
        "nested_authority": deepcopy(post_commit["nested_authority"]),
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "hook_bypass_performed": False,
        "new_authority_truth_created": False,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result_artifact(
    *,
    contract: dict[str, Any] | None,
    root: Path | None,
    validation_artifact: dict[str, Any] | None,
    commit_capture: dict[str, Any] | None,
    failure_reason: str,
) -> dict[str, Any]:
    current_head = _try_git_text(root, "rev-parse", "HEAD")
    current_tree = _try_git_text(root, "rev-parse", "HEAD^{tree}")
    current_subject = _try_git_text(root, "show", "-s", "--format=%s", "HEAD")
    commit_created = bool(commit_capture and commit_capture.get("commit_created") is True)
    artifact = {
        "artifact_type": FINALIZATION_RESULT_ARTIFACT_V1,
        "runtime_version": FINALIZATION_RUNTIME_VERSION,
        "contract_id": contract.get("contract_id") if contract else None,
        "contract_hash": contract.get("artifact_hash") if contract else None,
        "finalization_status": FAILED_CLOSED,
        "human_authorization_observed": contract is not None,
        "validation_artifact_hash": validation_artifact.get("artifact_hash") if validation_artifact else None,
        "governed_commit_capture_hash": commit_capture.get("capture_hash") if commit_capture else None,
        "existing_git_commit_worker_reused": commit_capture is not None,
        "parallel_commit_system_created": False,
        "commit_effect_count": 1 if commit_created else 0,
        "committed_head": current_head if commit_created else None,
        "committed_tree": current_tree if commit_created else None,
        "commit_subject": current_subject if commit_created else None,
        "committed_path_set": [],
        "committed_blobs": [],
        "post_commit_status": "FAIL_CLOSED",
        "root_worktree_clean": False,
        "index_empty": False,
        "nested_authority": None,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "hook_bypass_performed": False,
        "new_authority_truth_created": False,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(result: dict[str, Any], replay_path: Path | None) -> dict[str, Any]:
    capture = {
        "runtime_version": FINALIZATION_RUNTIME_VERSION,
        "finalization_status": result["finalization_status"],
        "contract_id": result["contract_id"],
        "committed_head": result["committed_head"],
        "committed_tree": result["committed_tree"],
        "commit_subject": result["commit_subject"],
        "committed_path_set": deepcopy(result["committed_path_set"]),
        "post_commit_status": result["post_commit_status"],
        "commit_effect_count": result["commit_effect_count"],
        "push_performed": False,
        "remote_interaction_performed": False,
        "human_authorization_observed": result["human_authorization_observed"],
        "existing_git_commit_worker_reused": result["existing_git_commit_worker_reused"],
        "replay_reference": str(replay_path) if replay_path is not None else None,
        "finalization_result_artifact": deepcopy(result),
        "fail_closed": result["finalization_status"] == FAILED_CLOSED,
        "failure_reason": result["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _resolve_replay_path(root: Path, contract_id: str) -> Path:
    path = _git_text(
        root,
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        f"aigol-finalization/{contract_id}",
    )
    replay_path = Path(path)
    if not replay_path.is_absolute():
        raise FailClosedRuntimeError("finalization failed closed: Replay path resolution failed")
    return replay_path


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("finalization failed closed: Replay destination already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, result: dict[str, Any]) -> None:
    path = replay_path / f"001_{REPLAY_STEPS[1]}.json"
    if path.exists():
        return
    try:
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
    except Exception:
        return


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("finalization Replay wrapper hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("finalization Replay artifact hash mismatch")


def _validate_authorized_mutations(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("finalization failed closed: authorized mutations required")
    mutations = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("finalization failed closed: mutation entry must be an object")
        path = _validate_relative_path(item.get("path"))
        if path in seen:
            raise FailClosedRuntimeError("finalization failed closed: duplicate authorized path")
        change_type = _require_string(item.get("change_type"), "change_type")
        if change_type not in {ADD_TEXT_FILE, REPLACE_TEXT_FILE}:
            raise FailClosedRuntimeError("finalization failed closed: unsupported change type")
        mutations.append(
            {
                "path": path,
                "change_type": change_type,
                "content_hash": _require_hash(item.get("content_hash"), "content_hash"),
            }
        )
        seen.add(path)
    mutations.sort(key=lambda item: item["path"])
    return mutations


def _validate_nested_authority(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("finalization failed closed: nested authority required")
    return {
        "path": _validate_relative_path(value.get("path")),
        "commit": _require_git_identity(value.get("commit"), "nested commit"),
        "tree": _require_git_identity(value.get("tree"), "nested tree"),
        "required_status": _require_exact_string(
            value.get("required_status"),
            "CLEAN__DETACHED_HEAD",
            "nested required_status",
        ),
    }


def _validate_commit_message(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("finalization failed closed: commit message required")
    subject = _require_string(value.get("subject"), "commit subject").strip()
    body = value.get("body", "")
    if not isinstance(body, str) or "\x00" in subject or "\x00" in body or "\n" in subject:
        raise FailClosedRuntimeError("finalization failed closed: commit message invalid")
    if len((subject + "\n\n" + body).encode("utf-8")) > 4096:
        raise FailClosedRuntimeError("finalization failed closed: commit message too large")
    return {"subject": subject, "body": body}


def _validate_author(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("finalization failed closed: author required")
    name = _require_string(value.get("name"), "author.name")
    email = _require_string(value.get("email"), "author.email")
    if any(character in name + email for character in ("\n", "\r", "\x00")):
        raise FailClosedRuntimeError("finalization failed closed: author invalid")
    return {"name": name, "email": email}


def _validate_relative_path(value: Any) -> str:
    text = _require_string(value, "path")
    if any(character in text for character in ("\n", "\r", "\x00")):
        raise FailClosedRuntimeError("finalization failed closed: path invalid")
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("finalization failed closed: path invalid")
    return path.as_posix()


def _validate_contract_id(value: Any) -> str:
    text = _require_string(value, "contract_id")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", text) is None:
        raise FailClosedRuntimeError("finalization failed closed: contract_id invalid")
    return text


def _require_git_identity(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if re.fullmatch(r"[0-9a-f]{40}", text) is None:
        raise FailClosedRuntimeError(f"finalization failed closed: {field} invalid")
    return text


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if re.fullmatch(r"sha256:[0-9a-f]{64}", text) is None:
        raise FailClosedRuntimeError(f"finalization failed closed: {field} invalid")
    return text


def _require_exact_string(value: Any, expected: str, field: str) -> str:
    text = _require_string(value, field)
    if text != expected:
        raise FailClosedRuntimeError(f"finalization failed closed: {field} mismatch")
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"finalization failed closed: {field} required")
    return value


def _nul_path_list(output: bytes) -> list[str]:
    if not output:
        return []
    fields = output.split(b"\0")
    if fields[-1] != b"":
        raise FailClosedRuntimeError("finalization failed closed: ambiguous Git path output")
    try:
        paths = [field.decode("utf-8") for field in fields[:-1]]
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("finalization failed closed: ambiguous Git path output") from exc
    normalized = [_validate_relative_path(path) for path in paths]
    if len(normalized) != len(set(normalized)):
        raise FailClosedRuntimeError("finalization failed closed: duplicate committed path")
    return sorted(normalized)


def _git_text(root: Path, *args: str) -> str:
    output = _git_bytes(root, *args)
    try:
        return output.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("finalization failed closed: Git output is not UTF-8") from exc


def _git_bytes(root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        raise FailClosedRuntimeError("finalization failed closed: Git command failed")
    return completed.stdout


def _try_git_text(root: Path | None, *args: str) -> str | None:
    if root is None:
        return None
    try:
        return _git_text(root, *args)
    except Exception:
        return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "finalization failed closed: unexpected coordinator failure"
