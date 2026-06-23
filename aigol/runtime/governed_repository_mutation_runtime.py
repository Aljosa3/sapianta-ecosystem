"""Governed ACLI workflow bridge for approved repository mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.repository_mutation_worker_runtime import (
    REPOSITORY_MUTATION_COMPLETED,
    apply_repository_mutation,
    create_patch_proposal_artifact,
    reconstruct_repository_mutation_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
)


AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION = "AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_V1"
GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1 = "GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1"
GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1 = "GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1"
GOVERNED_REPOSITORY_MUTATION_OUTCOME_ARTIFACT_V1 = "GOVERNED_REPOSITORY_MUTATION_OUTCOME_ARTIFACT_V1"
GOVERNED_REPOSITORY_MUTATION_COMPLETED = "GOVERNED_REPOSITORY_MUTATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

APPROVED = "APPROVED"
REJECTED = "REJECTED"
NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"

WORKFLOW_ID = "GOVERNED_REPOSITORY_MUTATION"
DEFAULT_VALIDATION_COMMAND = ["git", "diff", "--check"]

FORBIDDEN_WORKFLOW_TARGET_PREFIXES = (
    ".git/",
    ".github/governance/",
    "runtime/finalization_evidence/",
    "docs/governance/",
)

REPLAY_STEPS = (
    "governed_repository_mutation_request_recorded",
    "governed_repository_mutation_intent_recorded",
    "governed_repository_mutation_workflow_recorded",
    "governed_repository_mutation_context_recorded",
    "governed_repository_mutation_proposal_recorded",
    "governed_repository_mutation_approval_recorded",
    "governed_repository_mutation_worker_recorded",
    "governed_repository_mutation_validation_recorded",
    "governed_repository_mutation_outcome_recorded",
)


def create_governed_repository_mutation_proposal(
    *,
    proposal_id: str,
    original_request_reference: str,
    resolved_intent_reference: str,
    file_mutations: list[dict[str, Any]],
    validation_command: list[str] | None,
    replay_references: list[str],
    replay_hashes: list[str],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a pre-approval proposal for bounded repository mutation."""

    mutations = _validate_file_mutations(file_mutations)
    command = _validate_validation_command(validation_command or DEFAULT_VALIDATION_COMMAND)
    artifact = {
        "artifact_type": GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION,
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "workflow_id": WORKFLOW_ID,
        "original_request_reference": _require_string(
            original_request_reference, "original_request_reference"
        ),
        "resolved_intent_reference": _require_string(resolved_intent_reference, "resolved_intent_reference"),
        "file_mutations": mutations,
        "file_mutation_count": len(mutations),
        "target_paths": [mutation["target_path"] for mutation in mutations],
        "validation_plan": {"required_command": command},
        "human_approval_required": True,
        "mutation_allowed_before_approval": False,
        "provider_authority_granted": False,
        "worker_execution_required": True,
        "repository_mutation_worker_required": True,
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_governed_repository_mutation_approval(
    *,
    approval_id: str,
    proposal_artifact: dict[str, Any],
    decision: str,
    approved_by: str,
    approved_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
) -> dict[str, Any]:
    """Create explicit approval bound to a governed repository mutation proposal."""

    proposal = deepcopy(proposal_artifact)
    _validate_proposal(proposal)
    normalized_decision = _require_string(decision, "decision")
    if normalized_decision not in {APPROVED, REJECTED, NEEDS_CLARIFICATION}:
        raise FailClosedRuntimeError("governed repository mutation approval failed closed: invalid decision")
    artifact = {
        "artifact_type": GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "decision": normalized_decision,
        "approved_target_paths": deepcopy(proposal["target_paths"]),
        "approved_file_mutation_count": proposal["file_mutation_count"],
        "approved_validation_plan": deepcopy(proposal["validation_plan"]),
        "approved_scope": "APPLY_APPROVED_FILE_MUTATIONS_ONLY",
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def execute_governed_repository_mutation(
    *,
    execution_id: str,
    request_artifact: dict[str, Any],
    intent_artifact: dict[str, Any],
    workflow_artifact: dict[str, Any],
    repository_context_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute approved repository mutation through the repository mutation worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(proposal_artifact)
        approval = deepcopy(approval_artifact)
        _validate_proposal(proposal)
        _validate_approval(approval, proposal)
        _validate_workflow_artifact(workflow_artifact)
        _validate_context_artifact(repository_context_artifact, proposal)
        worker_proposal = create_patch_proposal_artifact(
            proposal_id=f"PATCH-{proposal['proposal_id']}",
            file_mutations=deepcopy(proposal["file_mutations"]),
            replay_references=[*proposal["replay_references"], approval["approval_id"]],
            replay_hashes=[*proposal["replay_hashes"], approval["artifact_hash"]],
            authorization_references=[approval["approval_id"]],
            created_by=executed_by,
            created_at=executed_at,
        )
        worker_capture = apply_repository_mutation(
            mutation_id=f"{execution_id}:WORKER-MUTATION",
            source_artifact=worker_proposal,
            target_root=repository_root,
            mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
            mutated_at=executed_at,
            replay_dir=replay_path / "repository_mutation_worker",
        )
        if worker_capture["mutation_status"] != REPOSITORY_MUTATION_COMPLETED:
            raise FailClosedRuntimeError("FAIL_CLOSED_REPOSITORY_MUTATION_WORKER_FAILED")
        worker_replay = reconstruct_repository_mutation_replay(worker_capture["repository_mutation_replay_reference"])
        validation_capture = _run_validation(
            execution_id=execution_id,
            proposal=proposal,
            root=Path(repository_root),
            replay_path=replay_path / "validation_command",
            executed_by=executed_by,
            executed_at=executed_at,
            replay_references=[worker_capture["repository_mutation_replay_reference"]],
            replay_hashes=[worker_capture["repository_mutation_artifact"]["artifact_hash"]],
        )
        if validation_capture["validation_command_result_artifact"]["command_status"] != VALIDATION_COMMAND_COMPLETED:
            raise FailClosedRuntimeError("FAIL_CLOSED_VALIDATION_FAILED")
        outcome = _outcome_artifact(
            execution_id=execution_id,
            status=GOVERNED_REPOSITORY_MUTATION_COMPLETED,
            proposal=proposal,
            approval=approval,
            worker_capture=worker_capture,
            worker_replay=worker_replay,
            validation_capture=validation_capture,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        _persist_full_replay(
            replay_path=replay_path,
            artifacts=[
                request_artifact,
                intent_artifact,
                workflow_artifact,
                repository_context_artifact,
                proposal,
                approval,
                worker_capture["repository_mutation_artifact"],
                validation_capture["validation_command_result_artifact"],
                outcome,
            ],
        )
        return _capture(outcome, worker_capture, validation_capture, replay_path)
    except Exception as exc:
        outcome = _failed_outcome_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 8, REPLAY_STEPS[8], outcome)
        return _capture(outcome, None, None, replay_path)


def reconstruct_governed_repository_mutation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate governed repository mutation workflow replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed repository mutation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed repository mutation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    proposal = wrappers[4]["artifact"]
    approval = wrappers[5]["artifact"]
    worker_mutation = wrappers[6]["artifact"]
    validation = wrappers[7]["artifact"]
    outcome = wrappers[8]["artifact"]
    if approval["proposal_id"] != proposal["proposal_id"] or approval["proposal_hash"] != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("governed repository mutation approval proposal mismatch")
    if outcome["proposal_hash"] != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("governed repository mutation outcome proposal hash mismatch")
    if outcome["approval_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("governed repository mutation outcome approval hash mismatch")
    if outcome["worker_mutation_hash"] != worker_mutation["artifact_hash"]:
        raise FailClosedRuntimeError("governed repository mutation outcome worker hash mismatch")
    if outcome["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("governed repository mutation outcome validation hash mismatch")
    return {
        "execution_id": outcome["execution_id"],
        "execution_status": outcome["execution_status"],
        "target_paths": deepcopy(proposal["target_paths"]),
        "mutated_file_count": worker_mutation["mutated_file_count"],
        "validation_status": validation["command_status"],
        "repository_mutation_worker_used": outcome["repository_mutation_worker_used"],
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "human_authority_preserved": approval["human_authority_preserved"],
        "fail_closed_preserved": outcome["fail_closed_preserved"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _run_validation(
    *,
    execution_id: str,
    proposal: dict[str, Any],
    root: Path,
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
) -> dict[str, Any]:
    request = create_validation_command_request(
        request_id=f"{execution_id}:VALIDATION",
        command=proposal["validation_plan"]["required_command"],
        cwd=str(root),
        requested_by=executed_by,
        requested_at=executed_at,
        replay_references=replay_references,
        replay_hashes=replay_hashes,
    )
    return execute_validation_command(
        request_artifact=request,
        executed_by=executed_by,
        executed_at=executed_at,
        replay_dir=replay_path,
    )


def _outcome_artifact(
    *,
    execution_id: str,
    status: str,
    proposal: dict[str, Any],
    approval: dict[str, Any],
    worker_capture: dict[str, Any],
    worker_replay: dict[str, Any],
    validation_capture: dict[str, Any],
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    worker_mutation = worker_capture["repository_mutation_artifact"]
    validation = validation_capture["validation_command_result_artifact"]
    artifact = {
        "artifact_type": GOVERNED_REPOSITORY_MUTATION_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "workflow_id": WORKFLOW_ID,
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "worker_mutation_hash": worker_mutation["artifact_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "validation_hash": validation["artifact_hash"],
        "validation_status": validation["command_status"],
        "target_paths": deepcopy(proposal["target_paths"]),
        "mutated_file_count": worker_mutation["mutated_file_count"],
        "repository_mutation_worker_used": True,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "provider_invoked": False,
        "acli_governed_development_ready_claimed": False,
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_outcome_artifact(
    *,
    execution_id: str,
    executed_by: str,
    executed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_REPOSITORY_MUTATION_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else None,
        "execution_status": FAILED_CLOSED,
        "workflow_id": WORKFLOW_ID,
        "proposal_id": None,
        "proposal_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "worker_mutation_hash": None,
        "worker_replay_hash": None,
        "validation_hash": None,
        "validation_status": None,
        "target_paths": [],
        "mutated_file_count": 0,
        "repository_mutation_worker_used": False,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "provider_invoked": False,
        "acli_governed_development_ready_claimed": False,
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    outcome: dict[str, Any],
    worker_capture: dict[str, Any] | None,
    validation_capture: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_VERSION,
        "execution_id": outcome["execution_id"],
        "execution_status": outcome["execution_status"],
        "workflow_id": WORKFLOW_ID,
        "target_paths": deepcopy(outcome["target_paths"]),
        "worker_capture": deepcopy(worker_capture),
        "validation_capture": deepcopy(validation_capture),
        "governed_repository_mutation_outcome": deepcopy(outcome),
        "governed_repository_mutation_replay_reference": str(replay_path),
        "repository_mutation_worker_used": outcome["repository_mutation_worker_used"],
        "repository_mutation_performed": outcome["execution_status"] == GOVERNED_REPOSITORY_MUTATION_COMPLETED,
        "provider_invoked": False,
        "worker_invoked": outcome["repository_mutation_worker_used"],
        "approval_required": True,
        "approval_bypassed": False,
        "fail_closed": outcome["execution_status"] == FAILED_CLOSED,
        "failure_reason": outcome.get("failure_reason"),
        "fail_closed_preserved": True,
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "acli_governed_development_ready_claimed": False,
    }
    capture["governed_repository_mutation_capture_hash"] = replay_hash(capture)
    return capture


def _persist_full_replay(*, replay_path: Path, artifacts: list[dict[str, Any]]) -> None:
    for index, artifact in enumerate(artifacts):
        _persist_step(replay_path, index, REPLAY_STEPS[index], artifact)


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _validate_proposal(proposal: dict[str, Any]) -> None:
    _verify_artifact_hash(proposal)
    if proposal.get("artifact_type") != GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed repository mutation failed closed: proposal artifact required")
    if proposal.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("governed repository mutation failed closed: workflow mismatch")
    if proposal.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("governed repository mutation failed closed: human approval required")
    if proposal.get("mutation_allowed_before_approval") is not False:
        raise FailClosedRuntimeError("governed repository mutation failed closed: mutation before approval forbidden")
    _validate_file_mutations(proposal.get("file_mutations"))
    _validate_validation_command(proposal.get("validation_plan", {}).get("required_command"))


def _validate_approval(approval: dict[str, Any] | None, proposal: dict[str, Any]) -> None:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    _verify_artifact_hash(approval)
    if approval.get("artifact_type") != GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    if approval.get("decision") != APPROVED:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    if approval.get("proposal_id") != proposal["proposal_id"] or approval.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")
    if approval.get("approved_target_paths") != proposal["target_paths"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")
    if approval.get("approved_validation_plan") != proposal["validation_plan"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")


def _validate_workflow_artifact(workflow_artifact: dict[str, Any]) -> None:
    if not isinstance(workflow_artifact, dict) or workflow_artifact.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_WORKFLOW_SELECTION")


def _validate_context_artifact(context_artifact: dict[str, Any], proposal: dict[str, Any]) -> None:
    if not isinstance(context_artifact, dict):
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")
    if context_artifact.get("context_fresh") is False:
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")
    target_paths = context_artifact.get("target_paths")
    if target_paths is not None and target_paths != proposal["target_paths"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")


def _validate_file_mutations(file_mutations: Any) -> list[dict[str, Any]]:
    if not isinstance(file_mutations, list) or not file_mutations:
        raise FailClosedRuntimeError("governed repository mutation failed closed: file mutations required")
    mutations = []
    seen_paths: set[str] = set()
    for item in file_mutations:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("governed repository mutation failed closed: file mutation must be object")
        target_path = _normalize_target_path(item.get("target_path"))
        if target_path in seen_paths:
            raise FailClosedRuntimeError("governed repository mutation failed closed: duplicate target path")
        seen_paths.add(target_path)
        operation = _require_string(item.get("operation"), "operation")
        if operation not in {"CREATE_OR_REPLACE", "REPLACE_CONTENT"}:
            raise FailClosedRuntimeError("governed repository mutation failed closed: operation not authorized")
        new_content = _require_file_content(item.get("new_content"), "new_content")
        new_content_hash = _require_hash(item.get("new_content_hash"), "new_content_hash")
        if new_content_hash != replay_hash(new_content):
            raise FailClosedRuntimeError("governed repository mutation failed closed: new content hash mismatch")
        if item.get("approved") is not True:
            raise FailClosedRuntimeError("governed repository mutation failed closed: file mutation not approved")
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
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    if any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in FORBIDDEN_WORKFLOW_TARGET_PREFIXES):
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    return normalized


def _validate_validation_command(command: Any) -> list[str]:
    if not isinstance(command, list) or not command:
        raise FailClosedRuntimeError("governed repository mutation failed closed: validation command required")
    values = [_require_string(item, "validation_command") for item in command]
    if values != DEFAULT_VALIDATION_COMMAND and values[:3] != ["python", "-m", "py_compile"]:
        raise FailClosedRuntimeError("governed repository mutation failed closed: validation command not authorized")
    return values


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("FAIL_CLOSED_REPLAY_INCOMPLETE")
    replay_path.mkdir(parents=True, exist_ok=True)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        return
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash")
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governed repository mutation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("wrapper_hash", None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governed repository mutation replay wrapper hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_file_content(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} must be a non-empty list")
    return [_require_string(item, field_name) for item in value]


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a replay hash")
    return text


def _require_hash_list(value: Any, field_name: str) -> list[str]:
    values = _require_string_list(value, field_name)
    if any(not item.startswith("sha256:") for item in values):
        raise FailClosedRuntimeError(f"{field_name} must contain replay hashes")
    return values


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    detail = str(exc)
    if detail:
        return f"FAIL_CLOSED_GOVERNED_REPOSITORY_MUTATION_FAILED: {detail}"
    return "FAIL_CLOSED_GOVERNED_REPOSITORY_MUTATION_FAILED"
