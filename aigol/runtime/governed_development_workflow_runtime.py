"""Governed ACLI development workflow orchestration runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governance_artifact_creation_runtime import (
    APPROVED,
    GOVERNANCE_ARTIFACT_CREATION_COMPLETED,
    create_governance_artifact,
    create_governance_artifact_approval,
    create_governance_artifact_proposal,
    reconstruct_governance_artifact_creation_replay,
)
from aigol.runtime.governed_repository_mutation_runtime import (
    GOVERNED_REPOSITORY_MUTATION_COMPLETED,
    create_governed_repository_mutation_approval,
    create_governed_repository_mutation_proposal,
    execute_governed_repository_mutation,
    reconstruct_governed_repository_mutation_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION = "AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_V1"
GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1 = "GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1"
GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1 = "GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1"
GOVERNED_DEVELOPMENT_OUTCOME_ARTIFACT_V1 = "GOVERNED_DEVELOPMENT_OUTCOME_ARTIFACT_V1"
GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED = "GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

WORKFLOW_ID = "GOVERNED_DEVELOPMENT_WORKFLOW"
REJECTED = "REJECTED"
NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"

REPLAY_STEPS = (
    "governed_development_request_recorded",
    "governed_development_intent_recorded",
    "governed_development_workflow_recorded",
    "governed_development_context_recorded",
    "governed_development_proposal_recorded",
    "governed_development_approval_recorded",
    "governance_artifact_creation_component_recorded",
    "governed_repository_mutation_component_recorded",
    "governed_development_outcome_recorded",
)


def create_governed_development_proposal(
    *,
    proposal_id: str,
    original_request_reference: str,
    resolved_intent_reference: str,
    governance_artifact: dict[str, Any],
    repository_file_mutations: list[dict[str, Any]],
    repository_validation_command: list[str] | None,
    replay_references: list[str],
    replay_hashes: list[str],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a top-level governed development proposal with component proposals."""

    refs = _require_string_list(replay_references, "replay_references")
    hashes = _require_hash_list(replay_hashes, "replay_hashes")
    proposal_id_value = _require_string(proposal_id, "proposal_id")
    original_ref = _require_string(original_request_reference, "original_request_reference")
    intent_ref = _require_string(resolved_intent_reference, "resolved_intent_reference")
    governance_proposal = create_governance_artifact_proposal(
        proposal_id=f"{proposal_id_value}:GOVERNANCE-ARTIFACT",
        original_request_reference=original_ref,
        resolved_intent_reference=intent_ref,
        target_path=_require_string(governance_artifact.get("target_path"), "governance_artifact.target_path"),
        artifact_title=_require_string(governance_artifact.get("artifact_title"), "governance_artifact.artifact_title"),
        artifact_purpose=_require_string(
            governance_artifact.get("artifact_purpose"), "governance_artifact.artifact_purpose"
        ),
        proposed_content=_require_string(
            governance_artifact.get("proposed_content"), "governance_artifact.proposed_content"
        ),
        expected_sections=_require_string_list(
            governance_artifact.get("expected_sections"), "governance_artifact.expected_sections"
        ),
        replay_references=refs,
        replay_hashes=hashes,
        created_by=created_by,
        created_at=created_at,
    )
    repository_proposal = create_governed_repository_mutation_proposal(
        proposal_id=f"{proposal_id_value}:REPOSITORY-MUTATION",
        original_request_reference=original_ref,
        resolved_intent_reference=intent_ref,
        file_mutations=repository_file_mutations,
        validation_command=repository_validation_command,
        replay_references=[*refs, governance_proposal["proposal_id"]],
        replay_hashes=[*hashes, governance_proposal["artifact_hash"]],
        created_by=created_by,
        created_at=created_at,
    )
    artifact = {
        "artifact_type": GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION,
        "proposal_id": proposal_id_value,
        "workflow_id": WORKFLOW_ID,
        "original_request_reference": original_ref,
        "resolved_intent_reference": intent_ref,
        "governance_artifact_proposal": deepcopy(governance_proposal),
        "repository_mutation_proposal": deepcopy(repository_proposal),
        "component_order": ["GOVERNANCE_ARTIFACT_CREATION", "GOVERNED_REPOSITORY_MUTATION"],
        "human_approval_required": True,
        "mutation_allowed_before_approval": False,
        "proposal_hash_binding_required": True,
        "validation_allowlists_preserved": True,
        "repository_mutation_worker_protections_preserved": True,
        "replay_references": refs,
        "replay_hashes": hashes,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "fail_closed_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_governed_development_approval(
    *,
    approval_id: str,
    proposal_artifact: dict[str, Any],
    decision: str,
    approved_by: str,
    approved_at: str,
    replay_references: list[str],
    replay_hashes: list[str],
) -> dict[str, Any]:
    """Create one explicit approval bound to the top-level development proposal."""

    proposal = deepcopy(proposal_artifact)
    _validate_proposal(proposal)
    normalized_decision = _require_string(decision, "decision")
    if normalized_decision not in {APPROVED, REJECTED, NEEDS_CLARIFICATION}:
        raise FailClosedRuntimeError("governed development approval failed closed: invalid decision")
    artifact = {
        "artifact_type": GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "decision": normalized_decision,
        "approved_component_order": deepcopy(proposal["component_order"]),
        "approved_governance_artifact_proposal_hash": proposal["governance_artifact_proposal"]["artifact_hash"],
        "approved_repository_mutation_proposal_hash": proposal["repository_mutation_proposal"]["artifact_hash"],
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


def execute_governed_development_workflow(
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
    """Execute governed development by composing governed component workflows."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(proposal_artifact)
        approval = deepcopy(approval_artifact)
        _validate_proposal(proposal)
        _validate_approval(approval, proposal)
        _validate_workflow_artifact(workflow_artifact)
        governance_approval = create_governance_artifact_approval(
            approval_id=f"{approval['approval_id']}:GOVERNANCE-ARTIFACT",
            proposal_artifact=proposal["governance_artifact_proposal"],
            decision=APPROVED,
            approved_by=approval["approved_by"],
            approved_at=approval["approved_at"],
            replay_references=[approval["approval_id"], proposal["proposal_id"]],
            replay_hashes=[approval["artifact_hash"], proposal["artifact_hash"]],
        )
        governance_capture = create_governance_artifact(
            creation_id=f"{execution_id}:GOVERNANCE-ARTIFACT",
            request_artifact=request_artifact,
            intent_artifact=intent_artifact,
            workflow_artifact={"workflow_id": "GOVERNANCE_ARTIFACT_CREATION"},
            repository_context_artifact={
                "target_path": proposal["governance_artifact_proposal"]["target_path"],
                "context_fresh": repository_context_artifact.get("context_fresh", True),
            },
            proposal_artifact=proposal["governance_artifact_proposal"],
            approval_artifact=governance_approval,
            repository_root=repository_root,
            created_by=executed_by,
            created_at=executed_at,
            replay_dir=replay_path / "governance_artifact_creation",
        )
        if governance_capture["creation_status"] != GOVERNANCE_ARTIFACT_CREATION_COMPLETED:
            raise FailClosedRuntimeError("FAIL_CLOSED_GOVERNANCE_ARTIFACT_CREATION_FAILED")
        governance_replay = reconstruct_governance_artifact_creation_replay(
            governance_capture["governance_artifact_creation_replay_reference"]
        )
        repository_approval = create_governed_repository_mutation_approval(
            approval_id=f"{approval['approval_id']}:REPOSITORY-MUTATION",
            proposal_artifact=proposal["repository_mutation_proposal"],
            decision=APPROVED,
            approved_by=approval["approved_by"],
            approved_at=approval["approved_at"],
            replay_references=[
                approval["approval_id"],
                proposal["proposal_id"],
                governance_capture["governance_artifact_creation_replay_reference"],
            ],
            replay_hashes=[
                approval["artifact_hash"],
                proposal["artifact_hash"],
                governance_capture["governance_artifact_creation_outcome"]["artifact_hash"],
            ],
        )
        repository_capture = execute_governed_repository_mutation(
            execution_id=f"{execution_id}:REPOSITORY-MUTATION",
            request_artifact=request_artifact,
            intent_artifact=intent_artifact,
            workflow_artifact={"workflow_id": "GOVERNED_REPOSITORY_MUTATION"},
            repository_context_artifact={
                "target_paths": proposal["repository_mutation_proposal"]["target_paths"],
                "context_fresh": repository_context_artifact.get("context_fresh", True),
            },
            proposal_artifact=proposal["repository_mutation_proposal"],
            approval_artifact=repository_approval,
            repository_root=repository_root,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_dir=replay_path / "governed_repository_mutation",
        )
        if repository_capture["execution_status"] != GOVERNED_REPOSITORY_MUTATION_COMPLETED:
            raise FailClosedRuntimeError("FAIL_CLOSED_GOVERNED_REPOSITORY_MUTATION_FAILED")
        repository_replay = reconstruct_governed_repository_mutation_replay(
            repository_capture["governed_repository_mutation_replay_reference"]
        )
        outcome = _outcome_artifact(
            execution_id=execution_id,
            status=GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
            proposal=proposal,
            approval=approval,
            governance_capture=governance_capture,
            governance_replay=governance_replay,
            repository_capture=repository_capture,
            repository_replay=repository_replay,
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
                governance_capture["governance_artifact_creation_outcome"],
                repository_capture["governed_repository_mutation_outcome"],
                outcome,
            ],
        )
        return _capture(outcome, governance_capture, repository_capture, replay_path)
    except Exception as exc:
        outcome = _failed_outcome_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 8, REPLAY_STEPS[8], outcome)
        return _capture(outcome, None, None, replay_path)


def reconstruct_governed_development_workflow_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate governed development orchestration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed development workflow replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed development workflow replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    proposal = wrappers[4]["artifact"]
    approval = wrappers[5]["artifact"]
    governance_outcome = wrappers[6]["artifact"]
    repository_outcome = wrappers[7]["artifact"]
    outcome = wrappers[8]["artifact"]
    if approval["proposal_hash"] != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("governed development approval proposal hash mismatch")
    if outcome["proposal_hash"] != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("governed development outcome proposal hash mismatch")
    if outcome["approval_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("governed development outcome approval hash mismatch")
    if outcome["governance_artifact_creation_hash"] != governance_outcome["artifact_hash"]:
        raise FailClosedRuntimeError("governed development governance component hash mismatch")
    if outcome["governed_repository_mutation_hash"] != repository_outcome["artifact_hash"]:
        raise FailClosedRuntimeError("governed development repository component hash mismatch")
    return {
        "execution_id": outcome["execution_id"],
        "execution_status": outcome["execution_status"],
        "workflow_id": WORKFLOW_ID,
        "governance_artifact_creation_status": governance_outcome["creation_status"],
        "governed_repository_mutation_status": repository_outcome["execution_status"],
        "component_order": deepcopy(proposal["component_order"]),
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "human_authority_preserved": approval["human_authority_preserved"],
        "repository_mutation_worker_protections_preserved": outcome[
            "repository_mutation_worker_protections_preserved"
        ],
        "validation_allowlists_preserved": outcome["validation_allowlists_preserved"],
        "fail_closed_preserved": outcome["fail_closed_preserved"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _outcome_artifact(
    *,
    execution_id: str,
    status: str,
    proposal: dict[str, Any],
    approval: dict[str, Any],
    governance_capture: dict[str, Any],
    governance_replay: dict[str, Any],
    repository_capture: dict[str, Any],
    repository_replay: dict[str, Any],
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    governance_outcome = governance_capture["governance_artifact_creation_outcome"]
    repository_outcome = repository_capture["governed_repository_mutation_outcome"]
    artifact = {
        "artifact_type": GOVERNED_DEVELOPMENT_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "workflow_id": WORKFLOW_ID,
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "governance_artifact_creation_hash": governance_outcome["artifact_hash"],
        "governance_artifact_creation_replay_hash": governance_replay["replay_hash"],
        "governed_repository_mutation_hash": repository_outcome["artifact_hash"],
        "governed_repository_mutation_replay_hash": repository_replay["replay_hash"],
        "component_order": deepcopy(proposal["component_order"]),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "validation_allowlists_preserved": True,
        "repository_mutation_worker_protections_preserved": True,
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
        "artifact_type": GOVERNED_DEVELOPMENT_OUTCOME_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else None,
        "execution_status": FAILED_CLOSED,
        "workflow_id": WORKFLOW_ID,
        "proposal_id": None,
        "proposal_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "governance_artifact_creation_hash": None,
        "governance_artifact_creation_replay_hash": None,
        "governed_repository_mutation_hash": None,
        "governed_repository_mutation_replay_hash": None,
        "component_order": [],
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "human_authority_preserved": True,
        "approval_bypassed": False,
        "validation_allowlists_preserved": True,
        "repository_mutation_worker_protections_preserved": True,
        "acli_governed_development_ready_claimed": False,
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    outcome: dict[str, Any],
    governance_capture: dict[str, Any] | None,
    repository_capture: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_VERSION,
        "execution_id": outcome["execution_id"],
        "execution_status": outcome["execution_status"],
        "workflow_id": WORKFLOW_ID,
        "governance_artifact_creation_capture": deepcopy(governance_capture),
        "governed_repository_mutation_capture": deepcopy(repository_capture),
        "governed_development_outcome": deepcopy(outcome),
        "governed_development_replay_reference": str(replay_path),
        "approval_required": True,
        "approval_bypassed": False,
        "repository_mutation_worker_protections_preserved": outcome[
            "repository_mutation_worker_protections_preserved"
        ],
        "validation_allowlists_preserved": outcome["validation_allowlists_preserved"],
        "fail_closed": outcome["execution_status"] == FAILED_CLOSED,
        "failure_reason": outcome.get("failure_reason"),
        "replay_lineage_preserved": outcome["replay_lineage_preserved"],
        "fail_closed_preserved": outcome["fail_closed_preserved"],
        "acli_governed_development_ready_claimed": False,
    }
    capture["governed_development_capture_hash"] = replay_hash(capture)
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
    if proposal.get("artifact_type") != GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed development failed closed: proposal artifact required")
    if proposal.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("governed development failed closed: workflow mismatch")
    if proposal.get("component_order") != ["GOVERNANCE_ARTIFACT_CREATION", "GOVERNED_REPOSITORY_MUTATION"]:
        raise FailClosedRuntimeError("governed development failed closed: component order mismatch")
    _verify_artifact_hash(proposal.get("governance_artifact_proposal"))
    _verify_artifact_hash(proposal.get("repository_mutation_proposal"))


def _validate_approval(approval: dict[str, Any] | None, proposal: dict[str, Any]) -> None:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    _verify_artifact_hash(approval)
    if approval.get("artifact_type") != GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    if approval.get("decision") != APPROVED:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_APPROVAL")
    if approval.get("proposal_id") != proposal["proposal_id"] or approval.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")
    if approval.get("approved_governance_artifact_proposal_hash") != proposal["governance_artifact_proposal"]["artifact_hash"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")
    if approval.get("approved_repository_mutation_proposal_hash") != proposal["repository_mutation_proposal"]["artifact_hash"]:
        raise FailClosedRuntimeError("FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH")


def _validate_workflow_artifact(workflow_artifact: dict[str, Any]) -> None:
    if not isinstance(workflow_artifact, dict) or workflow_artifact.get("workflow_id") != WORKFLOW_ID:
        raise FailClosedRuntimeError("FAIL_CLOSED_NO_WORKFLOW_SELECTION")


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("FAIL_CLOSED_REPLAY_INCOMPLETE")
    replay_path.mkdir(parents=True, exist_ok=True)


def _verify_artifact_hash(artifact: Any) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("governed development artifact hash required")
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash")
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governed development artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("wrapper_hash", None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governed development replay wrapper hash mismatch")


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


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    detail = str(exc)
    if detail:
        return f"FAIL_CLOSED_GOVERNED_DEVELOPMENT_WORKFLOW_FAILED: {detail}"
    return "FAIL_CLOSED_GOVERNED_DEVELOPMENT_WORKFLOW_FAILED"
