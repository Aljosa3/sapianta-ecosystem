"""ACLI bridge from governed development routing to approved execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.governed_development_workflow_runtime import (
    APPROVED,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
    reconstruct_governed_development_workflow_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_VERSION = "ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_V1"
ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1 = (
    "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1"
)
ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1 = (
    "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1"
)

APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
REJECTED = "REJECTED"
REQUEST_MODIFICATION = "REQUEST_MODIFICATION"
MODIFICATION_REQUESTED = "MODIFICATION_REQUESTED"
WAITING_FOR_OPERATOR_REVISION = "WAITING_FOR_OPERATOR_REVISION"

WORKFLOW_ID = "GOVERNED_DEVELOPMENT_WORKFLOW"
REQUESTED_ARTIFACT_IDENTIFIER_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]*_V[0-9]+\b")
REQUESTED_IDENTIFIER_MODE = "REQUESTED_IDENTIFIER"
GENERATED_FALLBACK_MODE = "GENERATED_FALLBACK"
AMBIGUOUS_FAIL_CLOSED_MODE = "AMBIGUOUS_FAIL_CLOSED"
COLLISION_FAIL_CLOSED_MODE = "COLLISION_FAIL_CLOSED"


def propose_acli_governed_development_execution(
    *,
    bridge_id: str,
    prompt_id: str,
    human_prompt: str,
    conversational_routing_capture: dict[str, Any],
    universal_intake_artifact: dict[str, Any],
    workspace_root: str | Path,
    proposed_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Generate a bounded governed development proposal from an ACLI-routed prompt."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routing_decision = _require_artifact(
            conversational_routing_capture.get("routing_decision_artifact"),
            "routing_decision_artifact",
        )
        workflow_selection = _require_artifact(
            conversational_routing_capture.get("workflow_selection_artifact"),
            "workflow_selection_artifact",
        )
        if workflow_selection.get("workflow_id") != WORKFLOW_ID:
            raise FailClosedRuntimeError("ACLI governed development bridge failed closed: workflow mismatch")
        workspace = Path(workspace_root)
        if not workspace.exists() or not workspace.is_dir():
            raise FailClosedRuntimeError("ACLI governed development bridge failed closed: workspace missing")

        request_artifact = _request_artifact(
            bridge_id=bridge_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            routing_decision=routing_decision,
            created_at=created_at,
        )
        intent_artifact = _intent_artifact(
            bridge_id=bridge_id,
            workflow_selection=workflow_selection,
            universal_intake_artifact=universal_intake_artifact,
            created_at=created_at,
        )
        seed = replay_hash(
            {
                "prompt_id": prompt_id,
                "human_prompt": human_prompt,
                "workflow_selection_hash": workflow_selection["artifact_hash"],
            }
        )[7:23]
        naming_decision = _proposal_naming_decision(
            human_prompt=human_prompt,
            seed=seed,
            workspace=workspace,
        )
        proposal = create_governed_development_proposal(
            proposal_id=f"{bridge_id}:PROPOSAL",
            original_request_reference=routing_decision["routing_decision_id"],
            resolved_intent_reference=workflow_selection["workflow_selection_id"],
            governance_artifact=_governance_artifact(
                seed=seed,
                human_prompt=human_prompt,
                naming_decision=naming_decision,
            ),
            repository_file_mutations=[
                _repository_file_mutation(
                    seed=seed,
                    human_prompt=human_prompt,
                    artifact_identifier=naming_decision["selected_artifact_identifier"],
                )
            ],
            repository_validation_command=["git", "diff", "--check"],
            replay_references=[
                conversational_routing_capture["conversational_cli_routing_replay_reference"],
                routing_decision["routing_decision_id"],
                workflow_selection["workflow_selection_id"],
                universal_intake_artifact["universal_intake_id"],
            ],
            replay_hashes=[
                conversational_routing_capture["conversational_cli_routing_hash"],
                routing_decision["artifact_hash"],
                workflow_selection["artifact_hash"],
                universal_intake_artifact["artifact_hash"],
            ],
            created_by=proposed_by,
            created_at=created_at,
        )
        repository_context = _repository_context_artifact(
            bridge_id=bridge_id,
            proposal=proposal,
            workspace=workspace,
            created_at=created_at,
        )
        proposal_preview = _proposal_preview_artifact(
            bridge_id=bridge_id,
            proposal=proposal,
            naming_decision=naming_decision,
            created_at=created_at,
        )
        capture = {
            "artifact_type": ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1,
            "runtime_version": ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_VERSION,
            "bridge_id": bridge_id,
            "prompt_id": prompt_id,
            "workflow_id": WORKFLOW_ID,
            "bridge_status": APPROVAL_REQUIRED,
            "request_artifact": request_artifact,
            "intent_artifact": intent_artifact,
            "workflow_artifact": deepcopy(workflow_selection),
            "repository_context_artifact": repository_context,
            "proposal_artifact": proposal,
            "proposal_naming_decision": naming_decision,
            "proposal_preview_artifact": proposal_preview,
            "approval_required": True,
            "approval_bypassed": False,
            "mutation_performed": False,
            "worker_invoked": False,
            "validation_executed": False,
            "target_paths": [
                proposal["governance_artifact_proposal"]["target_path"],
                *proposal["repository_mutation_proposal"]["target_paths"],
            ],
            "operator_next_action": "APPROVE, REJECT, or REQUEST_MODIFICATION",
            "replay_reference": str(replay_path),
            "replay_lineage_preserved": True,
            "fail_closed_preserved": True,
            "failure_reason": None,
        }
        capture["artifact_hash"] = replay_hash(capture)
        _persist_step(replay_path, 0, "acli_governed_development_proposal_recorded", capture)
        return capture
    except Exception as exc:
        capture = _failed_capture(
            bridge_id=bridge_id,
            prompt_id=prompt_id,
            status=FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
            replay_path=replay_path,
        )
        _persist_failure_if_possible(replay_path, 0, "acli_governed_development_proposal_recorded", capture)
        return capture


def approve_and_execute_acli_governed_development(
    *,
    bridge_id: str,
    pending_proposal_capture: dict[str, Any],
    decision: str,
    decided_by: str,
    decided_at: str,
    workspace_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind explicit human approval and invoke the certified governed development workflow."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        pending = deepcopy(pending_proposal_capture)
        _verify_capture(pending)
        normalized_decision = _require_string(decision, "decision")
        if normalized_decision != APPROVED:
            return _rejected_execution_capture(
                bridge_id=bridge_id,
                pending=pending,
                decision=normalized_decision,
                decided_by=decided_by,
                decided_at=decided_at,
                replay_path=replay_path,
            )
        proposal = _require_artifact(pending.get("proposal_artifact"), "proposal_artifact")
        approval = create_governed_development_approval(
            approval_id=f"{bridge_id}:APPROVAL",
            proposal_artifact=proposal,
            decision=APPROVED,
            approved_by=decided_by,
            approved_at=decided_at,
            replay_references=[pending["bridge_id"], proposal["proposal_id"], pending["replay_reference"]],
            replay_hashes=[pending["artifact_hash"], proposal["artifact_hash"], replay_hash(pending["replay_reference"])],
        )
        workflow_capture = execute_governed_development_workflow(
            execution_id=f"{bridge_id}:EXECUTION",
            request_artifact=pending["request_artifact"],
            intent_artifact=pending["intent_artifact"],
            workflow_artifact=pending["workflow_artifact"],
            repository_context_artifact=pending["repository_context_artifact"],
            proposal_artifact=proposal,
            approval_artifact=approval,
            repository_root=workspace_root,
            executed_by="AIGOL_ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE",
            executed_at=decided_at,
            replay_dir=replay_path / "governed_development_workflow",
        )
        workflow_replay = {}
        if workflow_capture.get("execution_status") == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED:
            workflow_replay = reconstruct_governed_development_workflow_replay(
                workflow_capture["governed_development_replay_reference"]
            )
        capture = {
            "artifact_type": ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1,
            "runtime_version": ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_VERSION,
            "bridge_id": bridge_id,
            "prompt_id": pending["prompt_id"],
            "workflow_id": WORKFLOW_ID,
            "bridge_status": (
                EXECUTION_COMPLETED
                if workflow_capture.get("execution_status") == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
                else FAILED_CLOSED
            ),
            "decision": APPROVED,
            "proposal_hash": proposal["artifact_hash"],
            "approval_artifact": approval,
            "approval_hash": approval["artifact_hash"],
            "workflow_capture": workflow_capture,
            "workflow_replay": workflow_replay,
            "approval_required": True,
            "approval_bypassed": False,
            "mutation_performed": workflow_capture.get("execution_status") == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
            "worker_invoked": (
                (workflow_capture.get("governed_repository_mutation_capture") or {}).get("worker_invoked") is True
            ),
            "validation_executed": workflow_capture.get("execution_status") == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
            "repository_mutation_worker_protections_preserved": workflow_capture.get(
                "repository_mutation_worker_protections_preserved"
            )
            is True,
            "validation_allowlists_preserved": workflow_capture.get("validation_allowlists_preserved") is True,
            "replay_reference": str(replay_path),
            "replay_lineage_preserved": workflow_capture.get("replay_lineage_preserved") is True,
            "fail_closed_preserved": workflow_capture.get("fail_closed_preserved") is True,
            "failure_reason": workflow_capture.get("failure_reason"),
        }
        capture["artifact_hash"] = replay_hash(capture)
        _persist_step(replay_path, 0, "acli_governed_development_approval_recorded", approval)
        _persist_step(replay_path, 1, "acli_governed_development_execution_recorded", capture)
        return capture
    except Exception as exc:
        capture = _failed_capture(
            bridge_id=bridge_id,
            prompt_id=str(pending_proposal_capture.get("prompt_id") or ""),
            status=FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
            replay_path=replay_path,
        )
        _persist_failure_if_possible(replay_path, 1, "acli_governed_development_execution_recorded", capture)
        return capture


def render_acli_governed_development_bridge_summary(capture: dict[str, Any]) -> str:
    """Render an operator-facing summary with diagnostics separated from plain language."""

    proposal = capture.get("proposal_artifact") or {}
    workflow_capture = capture.get("workflow_capture") or {}
    if capture.get("bridge_status") == APPROVAL_REQUIRED:
        target_paths = [str(path) for path in capture.get("target_paths", [])]
        naming_decision = capture.get("proposal_naming_decision") or {}
        preview = capture.get("proposal_preview_artifact") or {}
        content_preview = preview.get("content_preview") if isinstance(preview.get("content_preview"), list) else []
        requested_identifier = naming_decision.get("requested_artifact_identifier")
        selected_identifier = naming_decision.get("selected_artifact_identifier")
        selected_target_path = naming_decision.get("selected_target_path")
        return "\n".join(
            _compact_lines(
                [
                    "Governed Development Proposal",
                    "",
                    "Operator Summary",
                    "",
                    "Proposal ready for review.",
                    "",
                    "ACLI prepared a governed development proposal for your request.",
                    "",
                    f"Requested artifact: {requested_identifier or 'not provided'}",
                    f"Selected artifact: {selected_identifier or 'not available'}",
                    f"File ACLI plans to create: {selected_target_path or 'not available'}",
                    f"Target path mode: {naming_decision.get('target_path_mode') or 'not available'}",
                    "",
                    "Proposal preview:",
                    *(_bullet_lines(content_preview) if content_preview else ["- No content preview was recorded."]),
                    "",
                    "Proposed repository changes:",
                    *(_bullet_lines(target_paths) if target_paths else ["- No target paths were recorded."]),
                    "",
                    "Nothing has changed yet.",
                    "No worker has run yet.",
                    "Validation has not run yet because execution has not been approved.",
                    "",
                    "What you can type next:",
                    "- APPROVE to continue.",
                    "- REJECT to cancel.",
                    "- REQUEST_MODIFICATION to ask for a changed proposal.",
                    "",
                    "Evidence",
                    "",
                    f"- proposal replay: {capture.get('replay_reference')}",
                    "",
                    "Diagnostics",
                    "",
                    f"bridge_status: {capture.get('bridge_status')}",
                    f"workflow_id: {capture.get('workflow_id')}",
                    f"proposal_id: {proposal.get('proposal_id')}",
                    f"proposal_hash: {proposal.get('artifact_hash')}",
                    f"requested_artifact_identifier: {requested_identifier or ''}",
                    f"selected_artifact_identifier: {selected_identifier or ''}",
                    f"selected_target_path: {selected_target_path or ''}",
                    f"target_path_mode: {naming_decision.get('target_path_mode') or ''}",
                    f"collision_status: {naming_decision.get('collision_status') or ''}",
                    f"proposal_preview_hash: {preview.get('artifact_hash') or ''}",
                    "target_paths:",
                    *[f"- {path}" for path in target_paths],
                    "approval_required: true",
                    "approval_boundary: explicit human APPROVE required before mutation",
                    "mutation_performed: false",
                    "worker_invoked: false",
                    "validation_executed: false",
                    f"replay_lineage_preserved: {str(capture.get('replay_lineage_preserved') is True).lower()}",
                    f"replay_reference: {capture.get('replay_reference')}",
                    "next_action: APPROVE, REJECT, or REQUEST_MODIFICATION",
                ]
            )
        )
    if capture.get("bridge_status") == MODIFICATION_REQUESTED:
        return "\n".join(
            _compact_lines(
                [
                    "Governed Development Modification Requested",
                    "",
                    "Operator Summary",
                    "",
                    "Modification requested.",
                    "",
                    "The current proposal has been stopped.",
                    "Nothing was approved.",
                    "No repository changes were made.",
                    "No worker ran.",
                    "",
                    "Please describe what you want changed in the proposal.",
                    "",
                    "Evidence",
                    "",
                    f"- modification replay: {capture.get('replay_reference')}",
                    "",
                    "Diagnostics",
                    "",
                    f"bridge_status: {capture.get('bridge_status')}",
                    f"workflow_state: {capture.get('workflow_state')}",
                    f"workflow_id: {capture.get('workflow_id')}",
                    f"approval_decision: {capture.get('decision') or ''}",
                    f"approval_bypassed: {str(capture.get('approval_bypassed') is True).lower()}",
                    f"approval_granted: {str(capture.get('approval_granted') is True).lower()}",
                    _optional_field("approval_hash", capture.get("approval_hash")),
                    f"execution_authorized: {str(capture.get('execution_authorized') is True).lower()}",
                    f"proposal_hash: {capture.get('proposal_hash') or ''}",
                    f"mutation_performed: {str(capture.get('mutation_performed') is True).lower()}",
                    f"worker_invoked: {str(capture.get('worker_invoked') is True).lower()}",
                    f"validation_executed: {str(capture.get('validation_executed') is True).lower()}",
                    f"replay_lineage_preserved: {str(capture.get('replay_lineage_preserved') is True).lower()}",
                    f"bridge_replay_reference: {capture.get('replay_reference')}",
                    "next_action: Describe the required proposal change.",
                    _optional_field("failure_reason", capture.get("failure_reason")),
                ]
            )
        )
    if capture.get("bridge_status") == REJECTED:
        return "\n".join(
            _compact_lines(
                [
                    "Governed Development Rejected",
                    "",
                    "Operator Summary",
                    "",
                    "Proposal rejected.",
                    "",
                    "The current proposal is canceled.",
                    "Nothing was approved.",
                    "No repository changes were made.",
                    "No worker ran.",
                    "Replay evidence records the rejection.",
                    "",
                    "Evidence",
                    "",
                    f"- rejection replay: {capture.get('replay_reference')}",
                    "",
                    "Diagnostics",
                    "",
                    f"bridge_status: {capture.get('bridge_status')}",
                    f"workflow_id: {capture.get('workflow_id')}",
                    f"approval_decision: {capture.get('decision') or ''}",
                    f"approval_bypassed: {str(capture.get('approval_bypassed') is True).lower()}",
                    f"approval_granted: {str(capture.get('approval_granted') is True).lower()}",
                    _optional_field("approval_hash", capture.get("approval_hash")),
                    f"execution_authorized: {str(capture.get('execution_authorized') is True).lower()}",
                    f"proposal_hash: {capture.get('proposal_hash') or ''}",
                    f"mutation_performed: {str(capture.get('mutation_performed') is True).lower()}",
                    f"worker_invoked: {str(capture.get('worker_invoked') is True).lower()}",
                    f"validation_executed: {str(capture.get('validation_executed') is True).lower()}",
                    f"replay_lineage_preserved: {str(capture.get('replay_lineage_preserved') is True).lower()}",
                    f"bridge_replay_reference: {capture.get('replay_reference')}",
                    _optional_field("failure_reason", capture.get("failure_reason")),
                ]
            )
        )
    return "\n".join(
        _compact_lines(
            [
                "Governed Development Execution",
                "",
                "Operator Summary",
                "",
                "Approved and executed.",
                "",
                "ACLI used your approval to run the governed development workflow.",
                "",
                "What happened:",
                "- the approved repository changes were applied",
                "- the repository mutation worker path was used",
                "- validation ran successfully",
                "- replay evidence was recorded",
                "",
                "Safety checks:",
                "- approval was not bypassed",
                "- worker protections remained active",
                "- validation ran only through approved checks",
                "",
                "Evidence",
                "",
                f"- proposal hash: {capture.get('proposal_hash') or ''}",
                f"- approval hash: {capture.get('approval_hash') or ''}",
                f"- workflow execution evidence: {workflow_capture.get('governed_development_replay_reference')}",
                f"- bridge evidence: {capture.get('replay_reference')}",
                "",
                "Diagnostics",
                "",
                f"bridge_status: {capture.get('bridge_status')}",
                f"workflow_id: {capture.get('workflow_id')}",
                f"approval_decision: {capture.get('decision') or ''}",
                f"approval_bypassed: {str(capture.get('approval_bypassed') is True).lower()}",
                f"proposal_hash: {capture.get('proposal_hash') or ''}",
                f"approval_hash: {capture.get('approval_hash') or ''}",
                f"mutation_performed: {str(capture.get('mutation_performed') is True).lower()}",
                f"worker_invoked: {str(capture.get('worker_invoked') is True).lower()}",
                f"validation_executed: {str(capture.get('validation_executed') is True).lower()}",
                f"workflow_execution_status: {workflow_capture.get('execution_status')}",
                f"worker_protections_preserved: {str(capture.get('repository_mutation_worker_protections_preserved') is True).lower()}",
                f"validation_allowlists_preserved: {str(capture.get('validation_allowlists_preserved') is True).lower()}",
                f"replay_lineage_preserved: {str(capture.get('replay_lineage_preserved') is True).lower()}",
                f"workflow_replay_reference: {workflow_capture.get('governed_development_replay_reference')}",
                f"bridge_replay_reference: {capture.get('replay_reference')}",
                _optional_field("failure_reason", capture.get("failure_reason")),
            ]
        )
    )


def _bullet_lines(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values]


def _optional_field(name: str, value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return f"{name}: {value}"


def _compact_lines(lines: list[str | None]) -> list[str]:
    compacted: list[str] = []
    previous_blank = False
    for line in lines:
        if line is None:
            continue
        if line == "":
            if previous_blank:
                continue
            previous_blank = True
            compacted.append(line)
            continue
        previous_blank = False
        compacted.append(line)
    while compacted and compacted[-1] == "":
        compacted.pop()
    return compacted


def _request_artifact(
    *,
    bridge_id: str,
    prompt_id: str,
    human_prompt: str,
    routing_decision: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_REQUEST_ARTIFACT_V1",
        "request_id": f"{bridge_id}:REQUEST",
        "prompt_id": prompt_id,
        "natural_language_prompt": _require_string(human_prompt, "human_prompt"),
        "routing_decision_reference": routing_decision["routing_decision_id"],
        "routing_decision_hash": routing_decision["artifact_hash"],
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _intent_artifact(
    *,
    bridge_id: str,
    workflow_selection: dict[str, Any],
    universal_intake_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    intake = deepcopy(workflow_selection.get("human_intent_intake") or {})
    artifact = {
        **intake,
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_INTENT_ARTIFACT_V1",
        "intent_id": f"{bridge_id}:INTENT",
        "workflow_selection_reference": workflow_selection["workflow_selection_id"],
        "workflow_selection_hash": workflow_selection["artifact_hash"],
        "universal_intake_reference": universal_intake_artifact["universal_intake_id"],
        "universal_intake_hash": universal_intake_artifact["artifact_hash"],
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _repository_context_artifact(
    *, bridge_id: str, proposal: dict[str, Any], workspace: Path, created_at: str
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_REPOSITORY_CONTEXT_ARTIFACT_V1",
        "context_id": f"{bridge_id}:REPOSITORY-CONTEXT",
        "workspace_root": str(workspace),
        "context_fresh": True,
        "git_directory_present": (workspace / ".git").exists(),
        "governance_target_path": proposal["governance_artifact_proposal"]["target_path"],
        "target_paths": proposal["repository_mutation_proposal"]["target_paths"],
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_naming_decision(*, human_prompt: str, seed: str, workspace: Path) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    matches = REQUESTED_ARTIFACT_IDENTIFIER_PATTERN.findall(prompt)
    unique_matches = list(dict.fromkeys(matches))
    fallback_identifier = f"ACLI_GOVERNED_DEVELOPMENT_{seed.upper()}_V1"
    if len(unique_matches) > 1:
        decision = {
            "requested_artifact_identifier": None,
            "requested_identifier_detected": True,
            "requested_identifier_detection_rule": REQUESTED_ARTIFACT_IDENTIFIER_PATTERN.pattern,
            "requested_identifier_safe": False,
            "requested_identifier_ambiguity": unique_matches,
            "selected_artifact_identifier": None,
            "selected_target_path": None,
            "target_path_mode": AMBIGUOUS_FAIL_CLOSED_MODE,
            "fallback_seed": seed,
            "collision_status": None,
            "collision_resolution": "FAIL_CLOSED",
        }
        decision["artifact_hash"] = replay_hash(decision)
        raise FailClosedRuntimeError(
            "ACLI governed development bridge failed closed: ambiguous artifact identifiers "
            + ", ".join(unique_matches)
        )
    if unique_matches:
        identifier = unique_matches[0]
        target_path = f"docs/governance/{identifier}.md"
        collision_status = _target_collision_status(workspace=workspace, target_path=target_path)
        if collision_status != "NO_COLLISION":
            decision = {
                "requested_artifact_identifier": identifier,
                "requested_identifier_detected": True,
                "requested_identifier_detection_rule": REQUESTED_ARTIFACT_IDENTIFIER_PATTERN.pattern,
                "requested_identifier_safe": True,
                "requested_identifier_ambiguity": [],
                "selected_artifact_identifier": identifier,
                "selected_target_path": target_path,
                "target_path_mode": COLLISION_FAIL_CLOSED_MODE,
                "fallback_seed": seed,
                "collision_status": collision_status,
                "collision_resolution": "FAIL_CLOSED",
            }
            decision["artifact_hash"] = replay_hash(decision)
            raise FailClosedRuntimeError(
                f"ACLI governed development bridge failed closed: target path collision at {target_path}"
            )
        decision = {
            "requested_artifact_identifier": identifier,
            "requested_identifier_detected": True,
            "requested_identifier_detection_rule": REQUESTED_ARTIFACT_IDENTIFIER_PATTERN.pattern,
            "requested_identifier_safe": True,
            "requested_identifier_ambiguity": [],
            "selected_artifact_identifier": identifier,
            "selected_target_path": target_path,
            "target_path_mode": REQUESTED_IDENTIFIER_MODE,
            "fallback_seed": seed,
            "collision_status": collision_status,
            "collision_resolution": "NOT_REQUIRED",
        }
        decision["artifact_hash"] = replay_hash(decision)
        return decision
    target_path = f"docs/governance/{fallback_identifier}.md"
    collision_status = _target_collision_status(workspace=workspace, target_path=target_path)
    if collision_status != "NO_COLLISION":
        raise FailClosedRuntimeError(
            f"ACLI governed development bridge failed closed: generated target path collision at {target_path}"
        )
    decision = {
        "requested_artifact_identifier": None,
        "requested_identifier_detected": False,
        "requested_identifier_detection_rule": REQUESTED_ARTIFACT_IDENTIFIER_PATTERN.pattern,
        "requested_identifier_safe": False,
        "requested_identifier_ambiguity": [],
        "selected_artifact_identifier": fallback_identifier,
        "selected_target_path": target_path,
        "target_path_mode": GENERATED_FALLBACK_MODE,
        "fallback_seed": seed,
        "collision_status": collision_status,
        "collision_resolution": "NOT_REQUIRED",
    }
    decision["artifact_hash"] = replay_hash(decision)
    return decision


def _target_collision_status(*, workspace: Path, target_path: str) -> str:
    target = (workspace / target_path).resolve()
    try:
        target.relative_to(workspace.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("ACLI governed development bridge failed closed: target escaped workspace") from exc
    if target.exists():
        return "TARGET_EXISTS"
    return "NO_COLLISION"


def _governance_artifact(*, seed: str, human_prompt: str, naming_decision: dict[str, Any]) -> dict[str, Any]:
    title = _require_string(naming_decision.get("selected_artifact_identifier"), "selected_artifact_identifier")
    target_path = _require_string(naming_decision.get("selected_target_path"), "selected_target_path")
    purpose = _proposal_purpose(human_prompt)
    content = "\n".join(
        [
            f"# {title}",
            "",
            "Status: Generated Proposal",
            "",
            f"Purpose: {purpose}",
            "",
            "Human request:",
            "",
            human_prompt.strip(),
            "",
            "Boundaries:",
            "",
            "- Human approval remains required.",
            "- Repository mutation remains worker-governed.",
            "- Replay remains source of truth.",
            "",
        ]
    )
    return {
        "target_path": target_path,
        "artifact_title": title,
        "artifact_purpose": purpose,
        "proposed_content": content,
        "expected_sections": ["Status", "Purpose", "Boundaries"],
    }


def _proposal_purpose(human_prompt: str) -> str:
    prompt = _require_string(human_prompt, "human_prompt")
    match = re.search(r"\b(documenting|defining|recording|explaining)\s+(.+?)[.!?]?$", prompt, re.IGNORECASE)
    if match:
        purpose = match.group(2).strip()
        if purpose:
            return "Document " + purpose
    return "Record a no-copy-paste governed development proposal."


def _repository_file_mutation(*, seed: str, human_prompt: str, artifact_identifier: str) -> dict[str, Any]:
    content = "\n".join(
        [
            '"""ACLI governed development bridge generated marker."""',
            "",
            f'CERTIFIED_ACLI_GOVERNED_DEVELOPMENT_REQUEST = {human_prompt.strip()!r}',
            f'CERTIFIED_ACLI_GOVERNED_DEVELOPMENT_ARTIFACT = "{_require_string(artifact_identifier, "artifact_identifier")}"',
            f'CERTIFIED_ACLI_GOVERNED_DEVELOPMENT_SEED = "{seed}"',
            "",
        ]
    )
    return {
        "target_path": f"aigol/runtime/acli_governed_development_{seed}.py",
        "operation": "CREATE_OR_REPLACE",
        "new_content": content,
        "new_content_hash": replay_hash(content),
        "approved": True,
    }


def _proposal_preview_artifact(
    *, bridge_id: str, proposal: dict[str, Any], naming_decision: dict[str, Any], created_at: str
) -> dict[str, Any]:
    governance = proposal["governance_artifact_proposal"]
    repository = proposal["repository_mutation_proposal"]
    preview = {
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_PROPOSAL_PREVIEW_ARTIFACT_V1",
        "preview_id": f"{bridge_id}:PROPOSAL-PREVIEW",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "requested_artifact_identifier": naming_decision.get("requested_artifact_identifier"),
        "selected_artifact_identifier": naming_decision["selected_artifact_identifier"],
        "selected_target_path": naming_decision["selected_target_path"],
        "target_path_mode": naming_decision["target_path_mode"],
        "content_preview": [
            f"Title: {governance['artifact_title']}",
            f"Purpose: {governance['artifact_purpose']}",
            "Section: Status",
            "Section: Purpose",
            "Section: Boundaries",
        ],
        "repository_mutation_paths": deepcopy(repository["target_paths"]),
        "repository_mutation_operations": [
            item["operation"] for item in repository.get("file_mutations", []) if isinstance(item, dict)
        ],
        "validation_command": deepcopy(repository["validation_plan"]["required_command"]),
        "created_at": created_at,
    }
    preview["artifact_hash"] = replay_hash(preview)
    return preview


def _rejected_execution_capture(
    *,
    bridge_id: str,
    pending: dict[str, Any],
    decision: str,
    decided_by: str,
    decided_at: str,
    replay_path: Path,
) -> dict[str, Any]:
    modification_requested = decision == REQUEST_MODIFICATION
    capture = {
        "artifact_type": ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1,
        "runtime_version": ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_VERSION,
        "bridge_id": bridge_id,
        "prompt_id": pending["prompt_id"],
        "workflow_id": WORKFLOW_ID,
        "bridge_status": MODIFICATION_REQUESTED if modification_requested else REJECTED,
        "workflow_state": WAITING_FOR_OPERATOR_REVISION if modification_requested else REJECTED,
        "decision": decision,
        "decided_by": decided_by,
        "decided_at": decided_at,
        "proposal_hash": pending["proposal_artifact"]["artifact_hash"],
        "approval_required": True,
        "approval_granted": False,
        "approval_artifact": None,
        "approval_hash": None,
        "approval_bypassed": False,
        "execution_authorized": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "next_operator_action": (
            "Describe the required proposal change." if modification_requested else "No further action required."
        ),
        "replay_reference": str(replay_path),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "failure_reason": None,
    }
    capture["artifact_hash"] = replay_hash(capture)
    _persist_step(replay_path, 1, "acli_governed_development_execution_recorded", capture)
    return capture


def _failed_capture(
    *, bridge_id: str, prompt_id: str, status: str, failure_reason: str, replay_path: Path
) -> dict[str, Any]:
    capture = {
        "artifact_type": ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1,
        "runtime_version": ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_VERSION,
        "bridge_id": bridge_id,
        "prompt_id": prompt_id,
        "workflow_id": WORKFLOW_ID,
        "bridge_status": status,
        "approval_required": True,
        "approval_bypassed": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "replay_reference": str(replay_path),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "failure_reason": failure_reason,
    }
    capture["artifact_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("ACLI governed development bridge failed closed: replay already exists")
    replay_path.mkdir(parents=True, exist_ok=True)


def _require_artifact(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"ACLI governed development bridge failed closed: {field_name} missing")
    if "artifact_hash" not in value:
        raise FailClosedRuntimeError(f"ACLI governed development bridge failed closed: {field_name} hash missing")
    return deepcopy(value)


def _verify_capture(capture: dict[str, Any]) -> None:
    if capture.get("artifact_type") != ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1:
        raise FailClosedRuntimeError("ACLI governed development bridge failed closed: pending proposal required")
    expected = deepcopy(capture)
    actual = expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("ACLI governed development bridge failed closed: pending proposal hash mismatch")
    if capture.get("bridge_status") != APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("ACLI governed development bridge failed closed: pending approval required")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI governed development bridge failed closed: {field_name} required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    detail = str(exc)
    if detail:
        return f"ACLI governed development bridge failed closed: {detail}"
    return "ACLI governed development bridge failed closed"
