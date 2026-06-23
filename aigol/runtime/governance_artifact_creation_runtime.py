"""Governed ACLI workflow for approved governance artifact creation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
)


AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION = "AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1"
GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1 = "GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1"
GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1 = "GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1"
GOVERNANCE_ARTIFACT_CREATION_ARTIFACT_V1 = "GOVERNANCE_ARTIFACT_CREATION_ARTIFACT_V1"
GOVERNANCE_ARTIFACT_CREATION_OUTCOME_ARTIFACT_V1 = "GOVERNANCE_ARTIFACT_CREATION_OUTCOME_ARTIFACT_V1"
GOVERNANCE_ARTIFACT_CREATION_COMPLETED = "GOVERNANCE_ARTIFACT_CREATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

APPROVED = "APPROVED"
REJECTED = "REJECTED"
NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"

WORKFLOW_ID = "GOVERNANCE_ARTIFACT_CREATION"
VALIDATION_COMMAND = ["git", "diff", "--check"]

REPLAY_STEPS = (
    "governance_artifact_creation_request_recorded",
    "governance_artifact_creation_intent_recorded",
    "governance_artifact_creation_workflow_recorded",
    "governance_artifact_creation_context_recorded",
    "governance_artifact_creation_proposal_recorded",
    "governance_artifact_creation_approval_recorded",
    "governance_artifact_creation_mutation_recorded",
    "governance_artifact_creation_validation_recorded",
    "governance_artifact_creation_outcome_recorded",
)

FAIL_CLOSED_NO_APPROVAL = "FAIL_CLOSED_NO_APPROVAL"
FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH = "FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH"
FAIL_CLOSED_SCOPE_VIOLATION = "FAIL_CLOSED_SCOPE_VIOLATION"
FAIL_CLOSED_MUTATION_FAILED = "FAIL_CLOSED_MUTATION_FAILED"
FAIL_CLOSED_VALIDATION_FAILED = "FAIL_CLOSED_VALIDATION_FAILED"


def create_governance_artifact_proposal(
    *,
    proposal_id: str,
    original_request_reference: str,
    resolved_intent_reference: str,
    target_path: str,
    artifact_title: str,
    artifact_purpose: str,
    proposed_content: str,
    expected_sections: list[str],
    replay_references: list[str],
    replay_hashes: list[str],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create the pre-approval proposal for one governance artifact."""

    normalized_target = _validate_target_path(target_path)
    content = _require_string(proposed_content, "proposed_content")
    artifact = {
        "artifact_type": GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "workflow_id": WORKFLOW_ID,
        "original_request_reference": _require_string(
            original_request_reference, "original_request_reference"
        ),
        "resolved_intent_reference": _require_string(resolved_intent_reference, "resolved_intent_reference"),
        "target_path": normalized_target,
        "artifact_title": _require_string(artifact_title, "artifact_title"),
        "artifact_purpose": _require_string(artifact_purpose, "artifact_purpose"),
        "proposed_content": content,
        "proposed_content_hash": replay_hash(content),
        "expected_sections": _require_string_list(expected_sections, "expected_sections"),
        "mutation_summary": f"Create one approved governance artifact at {normalized_target}.",
        "validation_plan": {"required_commands": [list(VALIDATION_COMMAND)]},
        "human_approval_required": True,
        "mutation_allowed_before_approval": False,
        "provider_authority_granted": False,
        "repository_mutation_scope": {
            "allowed_operation": "CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT",
            "allowed_target_path": normalized_target,
            "allowed_file_count": 1,
            "runtime_code_mutation_allowed": False,
            "test_mutation_allowed": False,
            "replay_history_mutation_allowed": False,
        },
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_governance_artifact_approval(
    *,
    approval_id: str,
    proposal_artifact: dict[str, Any],
    decision: str,
    approved_by: str,
    approved_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
) -> dict[str, Any]:
    """Create an approval artifact bound to a governance artifact proposal."""

    proposal = deepcopy(proposal_artifact)
    _validate_proposal(proposal)
    normalized_decision = _require_string(decision, "decision")
    if normalized_decision not in {APPROVED, REJECTED, NEEDS_CLARIFICATION}:
        raise FailClosedRuntimeError("governance artifact approval failed closed: invalid decision")
    artifact = {
        "artifact_type": GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "decision": normalized_decision,
        "approved_target_path": proposal["target_path"],
        "approved_scope": "CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT",
        "approved_mutation_limits": {
            "allowed_file_count": 1,
            "allowed_operation": "CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT",
        },
        "approved_validation_plan": deepcopy(proposal["validation_plan"]),
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(approved_at, "approved_at"),
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "replay_hashes": _require_hash_list(replay_hashes, "replay_hashes"),
        "human_authority_preserved": True,
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_governance_artifact(
    *,
    creation_id: str,
    request_artifact: dict[str, Any],
    intent_artifact: dict[str, Any],
    workflow_artifact: dict[str, Any],
    repository_context_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create one approved governance artifact, validate it, and persist replay."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(proposal_artifact)
        approval = deepcopy(approval_artifact)
        _validate_proposal(proposal)
        _validate_approval(approval, proposal)
        _validate_workflow_artifact(workflow_artifact)
        _validate_context_artifact(repository_context_artifact, proposal)
        mutation = _write_approved_artifact(
            creation_id=creation_id,
            proposal=proposal,
            approval=approval,
            root=Path(repository_root),
            created_by=created_by,
            created_at=created_at,
        )
        validation_capture = _run_validation(
            creation_id=creation_id,
            root=Path(repository_root),
            replay_path=replay_path / "validation_command",
            created_by=created_by,
            created_at=created_at,
            replay_references=[str(replay_path), mutation["artifact_hash"]],
            replay_hashes=[replay_hash({"governance_artifact_creation": creation_id}), mutation["artifact_hash"]],
        )
        if validation_capture["validation_command_result_artifact"]["command_status"] != VALIDATION_COMMAND_COMPLETED:
            raise FailClosedRuntimeError("FAIL_CLOSED_VALIDATION_FAILED")
        outcome = _outcome_artifact(
            creation_id=creation_id,
            status=GOVERNANCE_ARTIFACT_CREATION_COMPLETED,
            mutation=mutation,
            validation_capture=validation_capture,
            created_by=created_by,
            created_at=created_at,
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
                mutation,
                validation_capture["validation_command_result_artifact"],
                outcome,
            ],
        )
        return _capture(outcome, mutation, validation_capture, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        outcome = _failed_outcome_artifact(
            creation_id=creation_id,
            created_by=created_by,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        _persist_failure_if_possible(replay_path, 8, REPLAY_STEPS[8], outcome)
        return _capture(outcome, None, None, replay_path)


def reconstruct_governance_artifact_creation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate governance artifact creation replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governance artifact creation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governance artifact creation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    proposal = wrappers[4]["artifact"]
    approval = wrappers[5]["artifact"]
    mutation = wrappers[6]["artifact"]
    validation = wrappers[7]["artifact"]
    outcome = wrappers[8]["artifact"]
    if approval["proposal_id"] != proposal["proposal_id"] or approval["proposal_hash"] != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("governance artifact creation approval proposal mismatch")
    if mutation["proposal_id"] != proposal["proposal_id"] or mutation["approval_id"] != approval["approval_id"]:
        raise FailClosedRuntimeError("governance artifact creation mutation authorization mismatch")
    if outcome["mutation_hash"] != mutation["artifact_hash"]:
        raise FailClosedRuntimeError("governance artifact creation outcome mutation hash mismatch")
    if outcome["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("governance artifact creation outcome validation hash mismatch")
    return {
        "creation_id": outcome["creation_id"],
        "creation_status": outcome["creation_status"],
        "target_path": mutation["target_path"],
        "mutated_file_count": mutation["mutated_file_count"],
        "validation_status": validation["command_status"],
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "fail_closed_preserved": outcome["fail_closed_preserved"],
        "human_authority_preserved": approval["human_authority_preserved"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _write_approved_artifact(
    *,
    creation_id: str,
    proposal: dict[str, Any],
    approval: dict[str, Any],
    root: Path,
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    target_path = proposal["target_path"]
    root_path = root.resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    target = (root_path / target_path).resolve()
    if not _is_relative_to(target, root_path):
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    if target.exists():
        raise FailClosedRuntimeError("FAIL_CLOSED_SCOPE_VIOLATION")
    before_hash = None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(proposal["proposed_content"], encoding="utf-8")
    after_content = target.read_text(encoding="utf-8")
    artifact = {
        "artifact_type": GOVERNANCE_ARTIFACT_CREATION_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "creation_id": _require_string(creation_id, "creation_id"),
        "proposal_id": proposal["proposal_id"],
        "approval_id": approval["approval_id"],
        "target_path": target_path,
        "operation": "CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT",
        "mutated_files": [target_path],
        "mutated_file_count": 1,
        "before_hash": before_hash,
        "after_hash": replay_hash(after_content),
        "after_content_snapshot": after_content,
        "governance_artifact_created": True,
        "runtime_code_modified": False,
        "tests_modified": False,
        "replay_history_modified": False,
        "provider_invoked": False,
        "arbitrary_shell_executed": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _run_validation(
    *,
    creation_id: str,
    root: Path,
    replay_path: Path,
    created_by: str,
    created_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
) -> dict[str, Any]:
    request = create_validation_command_request(
        request_id=f"{creation_id}:VALIDATION",
        command=list(VALIDATION_COMMAND),
        cwd=str(root),
        requested_by=created_by,
        requested_at=created_at,
        replay_references=replay_references,
        replay_hashes=replay_hashes,
    )
    return execute_validation_command(
        request_artifact=request,
        executed_by=created_by,
        executed_at=created_at,
        replay_dir=replay_path,
    )


def _outcome_artifact(
    *,
    creation_id: str,
    status: str,
    mutation: dict[str, Any],
    validation_capture: dict[str, Any],
    created_by: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    validation = validation_capture["validation_command_result_artifact"]
    artifact = {
        "artifact_type": GOVERNANCE_ARTIFACT_CREATION_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "creation_id": _require_string(creation_id, "creation_id"),
        "creation_status": status,
        "target_path": mutation["target_path"],
        "mutation_hash": mutation["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
        "validation_status": validation["command_status"],
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "acli_governed_development_ready_claimed": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_outcome_artifact(
    *,
    creation_id: str,
    created_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNANCE_ARTIFACT_CREATION_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "creation_id": creation_id if isinstance(creation_id, str) else None,
        "creation_status": FAILED_CLOSED,
        "target_path": None,
        "mutation_hash": None,
        "validation_hash": None,
        "validation_status": None,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "acli_governed_development_ready_claimed": False,
        "created_by": created_by if isinstance(created_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    outcome: dict[str, Any],
    mutation: dict[str, Any] | None,
    validation_capture: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION,
        "creation_id": outcome["creation_id"],
        "creation_status": outcome["creation_status"],
        "target_path": outcome.get("target_path"),
        "governance_artifact_creation_artifact": deepcopy(mutation),
        "validation_capture": deepcopy(validation_capture),
        "governance_artifact_creation_outcome": deepcopy(outcome),
        "governance_artifact_creation_replay_reference": str(replay_path),
        "workflow_id": WORKFLOW_ID,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_required": True,
        "approval_bypassed": False,
        "repository_mutation_performed": outcome["creation_status"] == GOVERNANCE_ARTIFACT_CREATION_COMPLETED,
        "fail_closed": outcome["creation_status"] == FAILED_CLOSED,
        "failure_reason": outcome.get("failure_reason"),
        "fail_closed_preserved": True,
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "acli_governed_development_ready_claimed": False,
    }
    capture["governance_artifact_creation_capture_hash"] = replay_hash(capture)
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
    if proposal.get("artifact_type") != GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governance artifact creation failed closed: proposal artifact required")
    if proposal.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("governance artifact creation failed closed: workflow mismatch")
    _validate_target_path(proposal.get("target_path"))
    if proposal.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("governance artifact creation failed closed: human approval required")
    if proposal.get("mutation_allowed_before_approval") is not False:
        raise FailClosedRuntimeError("governance artifact creation failed closed: mutation before approval forbidden")
    if proposal.get("validation_plan", {}).get("required_commands") != [list(VALIDATION_COMMAND)]:
        raise FailClosedRuntimeError("governance artifact creation failed closed: validation plan mismatch")
    if proposal.get("proposed_content_hash") != replay_hash(_require_string(proposal.get("proposed_content"), "proposed_content")):
        raise FailClosedRuntimeError("governance artifact creation failed closed: proposed content hash mismatch")


def _validate_approval(approval: dict[str, Any] | None, proposal: dict[str, Any]) -> None:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError(FAIL_CLOSED_NO_APPROVAL)
    _verify_artifact_hash(approval)
    if approval.get("artifact_type") != GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError(FAIL_CLOSED_NO_APPROVAL)
    if approval.get("decision") != APPROVED:
        raise FailClosedRuntimeError(FAIL_CLOSED_NO_APPROVAL)
    if approval.get("proposal_id") != proposal["proposal_id"] or approval.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError(FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH)
    if approval.get("approved_target_path") != proposal["target_path"]:
        raise FailClosedRuntimeError(FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH)
    if approval.get("approved_validation_plan") != proposal["validation_plan"]:
        raise FailClosedRuntimeError(FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH)


def _validate_workflow_artifact(workflow_artifact: dict[str, Any]) -> None:
    if not isinstance(workflow_artifact, dict) or workflow_artifact.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_WORKFLOW_SELECTION")


def _validate_context_artifact(context_artifact: dict[str, Any], proposal: dict[str, Any]) -> None:
    if not isinstance(context_artifact, dict):
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")
    target = context_artifact.get("target_path")
    if target is not None and target != proposal["target_path"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")
    if context_artifact.get("context_fresh") is False:
        raise FailClosedRuntimeError("FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT")


def _validate_target_path(value: Any) -> str:
    raw = _require_string(value, "target_path")
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts:
        raise FailClosedRuntimeError(FAIL_CLOSED_SCOPE_VIOLATION)
    normalized = path.as_posix()
    if not normalized.startswith("docs/governance/") or not normalized.endswith(".md"):
        raise FailClosedRuntimeError(FAIL_CLOSED_SCOPE_VIOLATION)
    if normalized == "docs/governance/.md":
        raise FailClosedRuntimeError(FAIL_CLOSED_SCOPE_VIOLATION)
    return normalized


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
        raise FailClosedRuntimeError("governance artifact creation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("wrapper_hash", None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governance artifact creation replay wrapper hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} must be a non-empty list")
    return [_require_string(item, field_name) for item in value]


def _require_hash_list(value: Any, field_name: str) -> list[str]:
    values = _require_string_list(value, field_name)
    if any(not item.startswith("sha256:") for item in values):
        raise FailClosedRuntimeError(f"{field_name} must contain replay hashes")
    return values


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    detail = str(exc)
    if detail:
        return f"{FAIL_CLOSED_MUTATION_FAILED}: {detail}"
    return FAIL_CLOSED_MUTATION_FAILED
