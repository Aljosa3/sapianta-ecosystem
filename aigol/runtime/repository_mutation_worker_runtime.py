"""Governed repository mutation worker for certified patch proposals."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.governed_worker_execution_runtime import WORKER_EXECUTION_RESULT_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_VERSION = "AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1"
PATCH_PROPOSAL_ARTIFACT_V1 = "PATCH_PROPOSAL_ARTIFACT_V1"
REPOSITORY_MUTATION_ARTIFACT_V1 = "REPOSITORY_MUTATION_ARTIFACT_V1"
REPOSITORY_MUTATION_COMPLETED = "REPOSITORY_MUTATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

CERTIFIED_PATCH_PROPOSAL = "CERTIFIED_PATCH_PROPOSAL"
CERTIFIED_WORKER_EXECUTION_RESULT = "CERTIFIED_WORKER_EXECUTION_RESULT"

REPLAY_STEPS = (
    "repository_mutation_source_recorded",
    "repository_mutation_artifact_recorded",
    "repository_mutation_returned",
)

FORBIDDEN_TARGET_PREFIXES = (
    ".git/",
    ".github/governance/",
    "runtime/finalization_evidence/",
)

ALLOWED_OPERATIONS = ("CREATE_OR_REPLACE", "REPLACE_CONTENT")


def create_patch_proposal_artifact(
    *,
    proposal_id: str,
    file_mutations: list[dict[str, Any]],
    replay_references: list[str],
    replay_hashes: list[str],
    authorization_references: list[str],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a certified patch proposal artifact for governed repository mutation."""

    mutations = _validate_file_mutations(file_mutations)
    target_paths = [mutation["target_path"] for mutation in mutations]
    artifact = {
        "artifact_type": PATCH_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_VERSION,
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "certification_status": CERTIFIED_PATCH_PROPOSAL,
        "authorization_scope": "APPLY_APPROVED_FILE_MUTATIONS_ONLY",
        "human_approval_required": True,
        "human_approval_granted": True,
        "repository_mutation_scope": {
            "allowed_operations": list(ALLOWED_OPERATIONS),
            "allowed_target_paths": target_paths,
            "forbidden_target_prefixes": list(FORBIDDEN_TARGET_PREFIXES),
            "governance_artifact_mutation_allowed": False,
            "replay_artifact_mutation_allowed": False,
        },
        "file_mutations": mutations,
        "file_mutation_count": len(mutations),
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "authorization_references": _require_string_list(authorization_references, "authorization_references"),
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "provider_invocation_allowed": False,
        "command_execution_allowed": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def apply_repository_mutation(
    *,
    mutation_id: str,
    source_artifact: dict[str, Any],
    target_root: str | Path,
    mutated_by: str,
    mutated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Apply approved file mutations and persist replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        source = deepcopy(source_artifact)
        proposal = _proposal_from_source(source)
        planned = _planned_mutations(proposal, target_root)
        mutation_results = _apply_planned_mutations(planned)
        artifact = _mutation_artifact(
            mutation_id=mutation_id,
            source=proposal,
            mutation_results=mutation_results,
            mutated_by=mutated_by,
            mutated_at=mutated_at,
            mutation_status=REPOSITORY_MUTATION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], proposal)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], artifact)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_mutation_artifact(
            mutation_id=mutation_id,
            source_artifact=source_artifact,
            mutated_by=mutated_by,
            mutated_at=mutated_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], artifact)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_repository_mutation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate a repository mutation replay."""

    replay_path = Path(replay_dir)
    result_wrapper = load_json(replay_path / "001_repository_mutation_artifact_recorded.json")
    returned_wrapper = load_json(replay_path / "002_repository_mutation_returned.json")
    _verify_wrapper_hash(result_wrapper)
    _verify_wrapper_hash(returned_wrapper)
    artifact = result_wrapper.get("artifact")
    returned = returned_wrapper.get("artifact")
    if not isinstance(artifact, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("repository mutation replay artifact must be a JSON object")
    _verify_artifact_hash(artifact)
    _verify_artifact_hash(returned)
    replay_artifact_count = 2
    if artifact.get("mutation_status") == REPOSITORY_MUTATION_COMPLETED:
        source_wrapper = load_json(replay_path / "000_repository_mutation_source_recorded.json")
        if source_wrapper.get("replay_index") != 0 or source_wrapper.get("replay_step") != REPLAY_STEPS[0]:
            raise FailClosedRuntimeError("repository mutation replay ordering mismatch")
        _verify_wrapper_hash(source_wrapper)
        source = source_wrapper.get("artifact")
        if not isinstance(source, dict):
            raise FailClosedRuntimeError("repository mutation source artifact must be a JSON object")
        _verify_artifact_hash(source)
        if artifact.get("source_artifact_hash") != source["artifact_hash"]:
            raise FailClosedRuntimeError("repository mutation source hash mismatch")
        replay_artifact_count = 3
    if returned.get("repository_mutation_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("repository mutation returned hash mismatch")
    return {
        "mutation_id": artifact["mutation_id"],
        "mutation_status": artifact["mutation_status"],
        "mutated_file_count": artifact["mutated_file_count"],
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "unauthorized_mutation_prevented": artifact["unauthorized_mutation_prevented"],
        "fail_closed_preserved": artifact["fail_closed_preserved"],
        "ready_for_governed_repository_changes": artifact["ready_for_governed_repository_changes"],
        "replay_artifact_count": replay_artifact_count,
        "replay_hash": replay_hash([result_wrapper, returned_wrapper]),
    }


def _proposal_from_source(source: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(source)
    if source.get("artifact_type") == PATCH_PROPOSAL_ARTIFACT_V1:
        _validate_patch_proposal(source)
        return source
    if source.get("artifact_type") == WORKER_EXECUTION_RESULT_ARTIFACT_V1:
        return _patch_proposal_from_worker_result(source)
    raise FailClosedRuntimeError("repository mutation failed closed: invalid source artifact type")


def _validate_patch_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("certification_status") != CERTIFIED_PATCH_PROPOSAL:
        raise FailClosedRuntimeError("repository mutation failed closed: certified patch proposal required")
    if proposal.get("human_approval_required") is not True or proposal.get("human_approval_granted") is not True:
        raise FailClosedRuntimeError("repository mutation failed closed: human approval required")
    if proposal.get("authorization_scope") != "APPLY_APPROVED_FILE_MUTATIONS_ONLY":
        raise FailClosedRuntimeError("repository mutation failed closed: authorization scope invalid")
    if proposal.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("repository mutation failed closed: replay lineage broken")
    if proposal.get("provider_invocation_allowed") is not False or proposal.get("command_execution_allowed") is not False:
        raise FailClosedRuntimeError("repository mutation failed closed: forbidden authority allowed")
    scope = proposal.get("repository_mutation_scope")
    if not isinstance(scope, dict):
        raise FailClosedRuntimeError("repository mutation failed closed: repository mutation scope invalid")
    if scope.get("governance_artifact_mutation_allowed") is not False:
        raise FailClosedRuntimeError("repository mutation failed closed: governance mutation cannot be allowed")
    if scope.get("replay_artifact_mutation_allowed") is not False:
        raise FailClosedRuntimeError("repository mutation failed closed: replay mutation cannot be allowed")
    mutations = _validate_file_mutations(proposal.get("file_mutations"))
    allowed_paths = scope.get("allowed_target_paths")
    if not isinstance(allowed_paths, list) or sorted(allowed_paths) != sorted(m["target_path"] for m in mutations):
        raise FailClosedRuntimeError("repository mutation failed closed: target file authorization mismatch")
    _require_string_list(proposal.get("authorization_references"), "authorization_references")
    _require_string_list(proposal.get("replay_references"), "replay_references")
    _require_hash_list(proposal.get("replay_hashes"), "replay_hashes")


def _patch_proposal_from_worker_result(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("certification_status") != CERTIFIED_WORKER_EXECUTION_RESULT:
        raise FailClosedRuntimeError("repository mutation failed closed: certified worker execution result required")
    payload = result.get("worker_result_payload")
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("repository mutation failed closed: worker result payload invalid")
    mutations = payload.get("approved_file_mutations")
    if not isinstance(mutations, list) or not mutations:
        raise FailClosedRuntimeError("repository mutation failed closed: approved file mutations required")
    proposal = create_patch_proposal_artifact(
        proposal_id="PATCH-PROPOSAL-FROM-" + _require_string(result.get("worker_execution_id"), "worker_execution_id"),
        file_mutations=mutations,
        replay_references=_require_string_list(result.get("replay_references"), "replay_references"),
        replay_hashes=_require_hash_list(result.get("replay_hashes"), "replay_hashes"),
        authorization_references=[result["worker_execution_id"]],
        created_by=_require_string(result.get("executed_by"), "executed_by"),
        created_at=_require_string(result.get("executed_at"), "executed_at"),
    )
    return proposal


def _planned_mutations(proposal: dict[str, Any], target_root: str | Path) -> list[dict[str, Any]]:
    root = Path(target_root).resolve()
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("repository mutation failed closed: target root must exist")
    planned = []
    for mutation in proposal["file_mutations"]:
        target_path = mutation["target_path"]
        target = (root / target_path).resolve()
        if not _is_relative_to(target, root):
            raise FailClosedRuntimeError("repository mutation failed closed: target path escapes root")
        before_content = target.read_text(encoding="utf-8") if target.exists() else None
        before_hash = replay_hash(before_content) if before_content is not None else None
        planned.append(
            {
                "target_path": target_path,
                "absolute_target_path": target,
                "operation": mutation["operation"],
                "new_content": mutation["new_content"],
                "new_content_hash": mutation["new_content_hash"],
                "before_content_snapshot": before_content,
                "before_hash": before_hash,
            }
        )
    return planned


def _apply_planned_mutations(planned: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for item in planned:
        target = item["absolute_target_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["new_content"], encoding="utf-8")
        after_content = target.read_text(encoding="utf-8")
        after_hash = replay_hash(after_content)
        if after_hash != item["new_content_hash"]:
            raise FailClosedRuntimeError("repository mutation failed closed: after hash mismatch")
        results.append(
            {
                "target_path": item["target_path"],
                "operation": item["operation"],
                "before_hash": item["before_hash"],
                "after_hash": after_hash,
                "before_content_snapshot": item["before_content_snapshot"],
                "after_content_snapshot": after_content,
                "mutation_applied": True,
            }
        )
    return results


def _mutation_artifact(
    *,
    mutation_id: str,
    source: dict[str, Any],
    mutation_results: list[dict[str, Any]],
    mutated_by: str,
    mutated_at: str,
    mutation_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REPOSITORY_MUTATION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_VERSION,
        "mutation_id": _require_string(mutation_id, "mutation_id"),
        "mutation_status": mutation_status,
        "source_artifact_id": source["proposal_id"],
        "source_artifact_type": source["artifact_type"],
        "source_artifact_hash": source["artifact_hash"],
        "mutated_files": [result["target_path"] for result in mutation_results],
        "mutated_file_count": len(mutation_results),
        "before_hashes": {result["target_path"]: result["before_hash"] for result in mutation_results},
        "after_hashes": {result["target_path"]: result["after_hash"] for result in mutation_results},
        "mutation_results": deepcopy(mutation_results),
        "mutation_summary": f"Applied {len(mutation_results)} approved file mutation(s).",
        "replay_references": deepcopy(source["replay_references"]),
        "replay_hashes": deepcopy(source["replay_hashes"]),
        "authorization_references": deepcopy(source["authorization_references"]),
        "mutated_by": _require_string(mutated_by, "mutated_by"),
        "mutated_at": _require_string(mutated_at, "mutated_at"),
        "governance_artifacts_modified": False,
        "replay_artifacts_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "arbitrary_shell_executed": False,
        "unauthorized_mutation_prevented": True,
        "replay_lineage_preserved": True,
        "human_authority_preserved": True,
        "authorization_boundaries_preserved": True,
        "fail_closed_preserved": True,
        "ready_for_governed_repository_changes": True,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_mutation_artifact(
    *,
    mutation_id: str,
    source_artifact: dict[str, Any],
    mutated_by: str,
    mutated_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REPOSITORY_MUTATION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_VERSION,
        "mutation_id": mutation_id if isinstance(mutation_id, str) else "INVALID",
        "mutation_status": FAILED_CLOSED,
        "source_artifact_id": source_artifact.get("proposal_id")
        if isinstance(source_artifact, dict)
        else None,
        "source_artifact_type": source_artifact.get("artifact_type")
        if isinstance(source_artifact, dict)
        else None,
        "source_artifact_hash": source_artifact.get("artifact_hash")
        if isinstance(source_artifact, dict)
        else None,
        "mutated_files": [],
        "mutated_file_count": 0,
        "before_hashes": {},
        "after_hashes": {},
        "mutation_results": [],
        "mutation_summary": "Repository mutation failed closed before applying approved file mutations.",
        "replay_references": [],
        "replay_hashes": [],
        "authorization_references": [],
        "mutated_by": mutated_by if isinstance(mutated_by, str) else None,
        "mutated_at": mutated_at if isinstance(mutated_at, str) else None,
        "governance_artifacts_modified": False,
        "replay_artifacts_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "arbitrary_shell_executed": False,
        "unauthorized_mutation_prevented": True,
        "replay_lineage_preserved": False,
        "human_authority_preserved": True,
        "authorization_boundaries_preserved": True,
        "fail_closed_preserved": True,
        "ready_for_governed_repository_changes": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    returned = {
        "event_type": "REPOSITORY_MUTATION_RETURNED",
        "repository_mutation": artifact["mutation_id"],
        "repository_mutation_hash": artifact["artifact_hash"],
        "mutation_status": artifact["mutation_status"],
        "mutated_file_count": artifact["mutated_file_count"],
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "unauthorized_mutation_prevented": artifact["unauthorized_mutation_prevented"],
        "fail_closed_preserved": artifact["fail_closed_preserved"],
        "ready_for_governed_repository_changes": artifact["ready_for_governed_repository_changes"],
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_VERSION,
        "mutation_status": artifact["mutation_status"],
        "repository_mutation_artifact": deepcopy(artifact),
        "repository_mutation_returned_artifact": deepcopy(returned),
        "repository_mutation_replay_reference": str(replay_path),
        "repository_mutation_worker_implemented": True,
        "repository_mutation_artifact_generated": artifact["artifact_type"] == REPOSITORY_MUTATION_ARTIFACT_V1,
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "unauthorized_mutation_prevented": artifact["unauthorized_mutation_prevented"],
        "fail_closed_preserved": artifact["fail_closed_preserved"],
        "ready_for_governed_repository_changes": artifact["ready_for_governed_repository_changes"],
        "failure_reason": artifact["failure_reason"],
    }
    capture["repository_mutation_capture_hash"] = replay_hash(capture)
    return capture


def _validate_file_mutations(file_mutations: Any) -> list[dict[str, Any]]:
    if not isinstance(file_mutations, list) or not file_mutations:
        raise FailClosedRuntimeError("repository mutation failed closed: file mutations required")
    mutations = []
    seen_paths: set[str] = set()
    for item in file_mutations:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("repository mutation failed closed: file mutation must be object")
        target_path = _normalize_target_path(item.get("target_path"))
        if target_path in seen_paths:
            raise FailClosedRuntimeError("repository mutation failed closed: duplicate target path")
        seen_paths.add(target_path)
        if _is_forbidden_target(target_path):
            raise FailClosedRuntimeError("repository mutation failed closed: target path is not authorized")
        operation = _require_string(item.get("operation"), "operation")
        if operation not in ALLOWED_OPERATIONS:
            raise FailClosedRuntimeError("repository mutation failed closed: mutation operation not authorized")
        new_content = _require_file_content(item.get("new_content"), "new_content")
        new_content_hash = _require_hash(item.get("new_content_hash"), "new_content_hash")
        if new_content_hash != replay_hash(new_content):
            raise FailClosedRuntimeError("repository mutation failed closed: new content hash mismatch")
        if item.get("approved") is not True:
            raise FailClosedRuntimeError("repository mutation failed closed: file mutation not approved")
        mutations.append(
            {
                "target_path": target_path,
                "operation": operation,
                "new_content": new_content,
                "new_content_hash": new_content_hash,
                "approved": True,
            }
        )
    return mutations


def _normalize_target_path(value: Any) -> str:
    text = _require_string(value, "target_path")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts:
        raise FailClosedRuntimeError("repository mutation failed closed: target path is outside approved scope")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise FailClosedRuntimeError("repository mutation failed closed: target path is required")
    return normalized


def _is_forbidden_target(path: str) -> bool:
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FORBIDDEN_TARGET_PREFIXES)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("repository mutation failed closed: replay already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash") if isinstance(artifact, dict) else None
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("repository mutation artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("repository mutation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("repository mutation replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("repository mutation replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} is required")
    return value.strip()


def _require_file_content(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} must be text")
    return value


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} must be list")
    values = [_require_string(item, field_name) for item in value]
    if not values:
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} requires entries")
    return values


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} must be a replay hash")
    return text


def _require_hash_list(value: Any, field_name: str) -> list[str]:
    hashes = _require_string_list(value, field_name)
    if not all(item.startswith("sha256:") for item in hashes):
        raise FailClosedRuntimeError(f"repository mutation failed closed: {field_name} must contain hashes")
    return hashes


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "repository mutation failed closed"
