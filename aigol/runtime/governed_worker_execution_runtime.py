"""Governed deterministic worker execution runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.execution_summary_runtime import (
    create_execution_summary,
    create_execution_summary_confirmation,
    verify_execution_summary_confirmation,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, verify_replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
    WORKER_EXECUTION_CANDIDATE_CREATED,
)


AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_VERSION = "AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_V1"
WORKER_EXECUTION_RESULT_ARTIFACT_V1 = "WORKER_EXECUTION_RESULT_ARTIFACT_V1"
WORKER_EXECUTION_COMPLETED = "WORKER_EXECUTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "worker_execution_validation_inputs_recorded",
    "worker_execution_result_recorded",
    "worker_execution_returned",
)
EXECUTION_APPROVAL_SCOPE = "RUN_GOVERNED_WORKER_EXECUTION_ONLY"


def project_g31_candidate_to_governed_execution(
    *,
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Project the original G31 execution decision into evidence-only execution."""

    from aigol.runtime.approved_durable_work_repository_scope_grounding import validate_approved_durable_work_repository_scope_grounding
    from aigol.runtime.confirmed_grounded_execution_authorization_binding import reconstruct_confirmed_grounded_execution_ready_replay
    from aigol.runtime.execution_authorization_runtime import EXECUTION_AUTHORIZED, reconstruct_execution_authorization_replay
    from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
        EXECUTION_DECISION_APPROVED, reconstruct_distinct_human_execution_decision,
        validate_distinct_human_execution_decision,
    )
    from aigol.runtime.worker_invocation_runtime import reconstruct_worker_invocation_replay
    from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import (
        APPROVAL_SCOPE as CANDIDATE_APPROVAL_SCOPE,
        reconstruct_worker_invocation_to_execution_candidate_bridge_replay,
    )

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    candidate_replay = Path(execution_candidate_capture.get(
        "worker_execution_candidate_replay_reference", ""
    )).resolve()
    if not destination.is_relative_to(root) or not candidate_replay.is_relative_to(root):
        raise FailClosedRuntimeError("G31 governed execution path is cross-session")
    reconstructed_candidate = reconstruct_worker_invocation_to_execution_candidate_bridge_replay(
        candidate_replay
    )
    wrapper = load_json(candidate_replay / "001_worker_invocation_execution_candidate_recorded.json")
    verify_replay_hash(wrapper, hash_field="replay_hash")
    candidate = wrapper.get("artifact")
    _validate_execution_candidate(candidate)
    supplied = execution_candidate_capture.get("worker_execution_candidate_artifact")
    if not isinstance(supplied, dict) or supplied.get("artifact_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("G31 execution candidate capture mismatch")
    if reconstructed_candidate["execution_candidate_id"] != candidate["execution_candidate_id"]:
        raise FailClosedRuntimeError("G31 execution candidate Replay mismatch")
    candidate_approval = execution_candidate_capture.get("candidate_only_human_approval_artifact")
    _validate_artifact(candidate_approval)
    if not all((
        candidate_approval.get("approval_scope") == CANDIDATE_APPROVAL_SCOPE,
        candidate_approval.get("worker_execution_allowed") is False,
        candidate_approval.get("artifact_hash") == candidate.get("human_approval_hash"),
    )):
        raise FailClosedRuntimeError("G31 candidate-only approval integrity mismatch")

    references = [Path(value).resolve() for value in candidate["replay_references"]]
    if any(not value.is_relative_to(root) for value in references):
        raise FailClosedRuntimeError("G31 governed execution lineage is cross-session")
    invocation_paths = [value for value in references if (value / "002_invocation_artifact_recorded.json").is_file()]
    authorization_paths = [value for value in references if (value / "002_authorization_artifact_recorded.json").is_file()]
    ready_paths = [value for value in references if (value / "000_execution_candidate_recorded.json").is_file()]
    if not all(len(paths) == 1 for paths in (invocation_paths, authorization_paths, ready_paths)):
        raise FailClosedRuntimeError("G31 governed execution lineage references are incomplete")
    invocation = reconstruct_worker_invocation_replay(invocation_paths[0])
    authorization = reconstruct_execution_authorization_replay(authorization_paths[0])
    ready = reconstruct_confirmed_grounded_execution_ready_replay(ready_paths[0])
    authorization_wrapper = load_json(authorization_paths[0] / "002_authorization_artifact_recorded.json")
    verify_replay_hash(authorization_wrapper, hash_field="replay_hash")
    authorization_artifact = authorization_wrapper.get("artifact")
    _validate_artifact(authorization_artifact)
    if not all((
        invocation["worker_invocation_id"] == candidate["source_worker_invocation"],
        authorization["authorization_status"] == EXECUTION_AUTHORIZED,
        authorization_artifact.get("authorization_revoked") is False,
        authorization_artifact.get("authorized_scope") == ready["authorization_scope"],
    )):
        raise FailClosedRuntimeError("G31 invocation or authorization lineage mismatch")

    ready_wrapper = load_json(ready_paths[0] / "000_execution_candidate_recorded.json")
    verify_replay_hash(ready_wrapper, hash_field="replay_hash")
    ready_candidate = ready_wrapper.get("artifact")
    _validate_artifact(ready_candidate)
    decision = validate_distinct_human_execution_decision(
        ready_candidate.get("source_human_execution_decision_artifact"),
        workspace=ready["authorization_scope"]["workspace_root"], session_root=root,
    )
    reconstructed_decision = reconstruct_distinct_human_execution_decision(
        decision["replay_reference"], workspace=ready["authorization_scope"]["workspace_root"],
        session_root=root,
    )
    grounding = validate_approved_durable_work_repository_scope_grounding(
        decision["source_authorization_review_artifact"]["source_repository_scope_grounding_artifact"],
        workspace=ready["authorization_scope"]["workspace_root"],
    )
    ppp = grounding["source_worker_payload_binding_artifact"]["ppp_task_package_artifact"]
    if not all((
        decision["decision_status"] == EXECUTION_DECISION_APPROVED,
        reconstructed_decision["artifact_hash"] == decision["artifact_hash"],
        authorization_artifact["human_confirmation_hash"] == decision["human_confirmation_hash"],
        candidate["source_ppp_candidate"] == ppp["ppp_candidate_id"],
        candidate["source_ppp_candidate_hash"] == ppp["artifact_hash"],
    )):
        raise FailClosedRuntimeError("G31 decision, confirmation, or PPP lineage mismatch")

    approval = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": f"{candidate['execution_candidate_id']}:EXECUTION-APPROVAL",
        "approval_status": APPROVED, "approval_granted": True,
        "source_execution_candidate": candidate["execution_candidate_id"],
        "source_execution_candidate_hash": candidate["artifact_hash"],
        "approval_scope": EXECUTION_APPROVAL_SCOPE, "worker_execution_allowed": True,
        "implementation_result_creation_allowed": False, "worker_process_activation_allowed": False,
        "provider_invocation_allowed": False, "command_execution_allowed": False,
        "worker_output_creation_allowed": False, "result_capture_allowed": False,
        "repository_mutation_allowed": False, "derived_compatibility_projection": True,
        "source_human_execution_decision": decision["artifact_hash"],
        "source_human_confirmation": decision["human_confirmation_hash"],
        "source_execution_authorization": authorization_artifact["authorization_id"],
        "source_execution_authorization_hash": authorization_artifact["artifact_hash"],
        "third_human_decision_recorded": False,
        "approved_by": decision["decided_by"], "approved_at": decision["decided_at"],
    }
    approval["artifact_hash"] = replay_hash(approval)
    capture = run_governed_worker_execution(
        execution_id=f"{candidate['execution_candidate_id']}:GOVERNED-EXECUTION",
        execution_candidate_artifact=candidate, human_approval_artifact=approval,
        executed_by=executed_by, executed_at=executed_at, replay_dir=destination,
        execution_summary_artifact=decision["source_authorization_review_artifact"]["execution_summary_artifact"],
        human_confirmation_artifact=decision["human_confirmation_artifact"],
    )
    capture["execution_scoped_human_approval_artifact"] = deepcopy(approval)
    capture["source_human_decision_count"] = 2
    return capture


def run_governed_worker_execution(
    *,
    execution_id: str,
    execution_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
    validation_inputs: dict[str, Any] | None = None,
    execution_summary_artifact: dict[str, Any] | None = None,
    human_confirmation_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a deterministic governed worker execution and persist replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        candidate = deepcopy(execution_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_execution_candidate(candidate)
        _validate_human_approval(approval, candidate)
        summary = execution_summary_artifact or _default_execution_summary(
            execution_id=execution_id,
            candidate=candidate,
            approval=approval,
            executed_by=executed_by,
            executed_at=executed_at,
        )
        confirmation = human_confirmation_artifact or create_execution_summary_confirmation(
            confirmation_id=f"{execution_id}:EXECUTION-SUMMARY-CONFIRMATION",
            execution_summary_artifact=summary,
            decision="APPROVE",
            confirmed_by=approval["approved_by"],
            confirmed_at=approval["approved_at"],
        )
        verify_execution_summary_confirmation(summary, confirmation)
        inputs = _validation_inputs(
            execution_id=execution_id,
            candidate=candidate,
            approval=approval,
            execution_summary_artifact=summary,
            human_confirmation_artifact=confirmation,
            executed_by=executed_by,
            executed_at=executed_at,
            validation_inputs=validation_inputs,
        )
        result = _execution_result_artifact(
            execution_id=execution_id,
            candidate=candidate,
            approval=approval,
            validation_inputs_artifact=inputs,
            execution_summary_artifact=summary,
            human_confirmation_artifact=confirmation,
            executed_by=executed_by,
            executed_at=executed_at,
            execution_status=WORKER_EXECUTION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(result)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], inputs)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(inputs, result, returned, replay_path)
    except Exception as exc:
        result = _failed_execution_result_artifact(
            execution_id=execution_id,
            execution_candidate_artifact=execution_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(result)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(None, result, returned, replay_path)


def reconstruct_governed_worker_execution_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate governed worker execution replay."""

    replay_path = Path(replay_dir)
    result_wrapper = load_json(replay_path / "001_worker_execution_result_recorded.json")
    returned_wrapper = load_json(replay_path / "002_worker_execution_returned.json")
    _verify_wrapper_hash(result_wrapper)
    _verify_wrapper_hash(returned_wrapper)
    result = result_wrapper.get("artifact")
    returned = returned_wrapper.get("artifact")
    if not isinstance(result, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("governed worker execution replay artifact must be a JSON object")
    _verify_artifact_hash(result)
    _verify_artifact_hash(returned)
    if result.get("execution_status") == WORKER_EXECUTION_COMPLETED:
        inputs_wrapper = load_json(replay_path / "000_worker_execution_validation_inputs_recorded.json")
        if inputs_wrapper.get("replay_index") != 0 or inputs_wrapper.get("replay_step") != REPLAY_STEPS[0]:
            raise FailClosedRuntimeError("governed worker execution replay ordering mismatch")
        _verify_wrapper_hash(inputs_wrapper)
        inputs = inputs_wrapper.get("artifact")
        if not isinstance(inputs, dict):
            raise FailClosedRuntimeError("governed worker execution validation inputs must be a JSON object")
        _verify_artifact_hash(inputs)
        if result.get("validation_inputs_hash") != inputs["artifact_hash"]:
            raise FailClosedRuntimeError("governed worker execution validation input hash mismatch")
        if result.get("execution_summary_hash") != inputs.get("execution_summary_hash"):
            raise FailClosedRuntimeError("governed worker execution summary lineage mismatch")
        if result.get("human_confirmation_hash") != inputs.get("human_confirmation_hash"):
            raise FailClosedRuntimeError("governed worker execution confirmation lineage mismatch")
        replay_artifact_count = 3
    else:
        replay_artifact_count = 2
    if result_wrapper.get("replay_index") != 1 or result_wrapper.get("replay_step") != REPLAY_STEPS[1]:
        raise FailClosedRuntimeError("governed worker execution replay ordering mismatch")
    if returned_wrapper.get("replay_index") != 2 or returned_wrapper.get("replay_step") != REPLAY_STEPS[2]:
        raise FailClosedRuntimeError("governed worker execution replay ordering mismatch")
    if returned.get("worker_execution_reference") != result["worker_execution_id"]:
        raise FailClosedRuntimeError("governed worker execution returned reference mismatch")
    if returned.get("worker_execution_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("governed worker execution returned hash mismatch")
    return {
        "worker_execution_id": result["worker_execution_id"],
        "execution_status": result["execution_status"],
        "source_execution_candidate": result["source_execution_candidate"],
        "source_invocation_candidate": result["source_invocation_candidate"],
        "source_dispatch_candidate": result["source_dispatch_candidate"],
        "source_worker_request": result["source_worker_request"],
        "source_implementation_request": result["source_implementation_request"],
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "fail_closed_preserved": result["fail_closed_preserved"],
        "ready_for_result_validation_runtime": result["ready_for_result_validation_runtime"],
        "implementation_result_created": result["implementation_result_created"],
        "code_modified": result["code_modified"],
        "governance_modified": result["governance_modified"],
        "provider_invoked": result["provider_invoked"],
        "replay_visible": True,
        "replay_artifact_count": replay_artifact_count,
        "replay_hash": replay_hash([result_wrapper, returned_wrapper]),
    }


def render_governed_worker_execution_summary(capture: dict[str, Any]) -> str:
    """Render governed-execution evidence without implying process activation."""

    result = capture.get("worker_execution_result_artifact") or {}
    return "\n".join((
        "Governed Worker Execution Evidence",
        f"Evidence Status: {result.get('execution_status')}",
        f"Evidence Reference: {result.get('worker_execution_id')}",
        "Deterministic governed-execution evidence was recorded; CODEX did not start.",
        "No adapter, Provider, subprocess, command, Worker output, result capture, or mutation occurred.",
        "A later governed transition is required before actual Worker activation.",
    ))


def _validate_execution_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate)
    if candidate.get("artifact_type") != WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed worker execution failed closed: invalid artifact type")
    if candidate.get("candidate_status") != WORKER_EXECUTION_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("governed worker execution failed closed: certified execution candidate required")
    if candidate.get("certification_status") != "CERTIFIED_WORKER_INVOCATION_CANDIDATE_ACCEPTED":
        raise FailClosedRuntimeError("governed worker execution failed closed: certification validation failed")
    if candidate.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: replay lineage broken")
    if candidate.get("human_approval_required") is not True or candidate.get("human_approval_granted") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: human approval chain required")
    if candidate.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: human authority missing")
    if candidate.get("ready_for_governed_worker_execution") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: candidate is not ready")
    _require_string(candidate.get("source_invocation_candidate"), "source_invocation_candidate")
    _require_hash(candidate.get("source_invocation_candidate_hash"), "source_invocation_candidate_hash")
    _require_string(candidate.get("source_dispatch_candidate"), "source_dispatch_candidate")
    _require_hash(candidate.get("source_dispatch_candidate_hash"), "source_dispatch_candidate_hash")
    _require_string(candidate.get("source_worker_request"), "source_worker_request")
    _require_hash(candidate.get("source_worker_request_hash"), "source_worker_request_hash")
    _require_string(candidate.get("source_implementation_request"), "source_implementation_request")
    _require_hash(candidate.get("source_implementation_request_hash"), "source_implementation_request_hash")
    if not _string_list(candidate.get("replay_references")):
        raise FailClosedRuntimeError("governed worker execution failed closed: replay references required")
    if not _hash_list(candidate.get("replay_hashes")):
        raise FailClosedRuntimeError("governed worker execution failed closed: replay hashes required")
    constraints = candidate.get("execution_constraints")
    if not isinstance(constraints, dict):
        raise FailClosedRuntimeError("governed worker execution failed closed: execution constraints invalid")
    if constraints.get("implementation_result_creation_allowed") is not False:
        raise FailClosedRuntimeError("governed worker execution failed closed: result creation constraints invalid")
    governance = candidate.get("governance_constraints")
    if not isinstance(governance, dict) or governance.get("worker_execution_requires_separate_governance") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: governance constraints invalid")
    for flag in (
        "worker_executed",
        "implementation_result_created",
        "code_modified",
        "governance_modified",
        "provider_invoked",
        "execution_requested",
    ):
        if candidate.get(flag) is not False:
            raise FailClosedRuntimeError(f"governed worker execution failed closed: candidate {flag} must be false")


def _validate_human_approval(approval: dict[str, Any], candidate: dict[str, Any]) -> None:
    _validate_artifact(approval)
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed worker execution failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: explicit human approval required")
    if approval.get("source_execution_candidate") != candidate.get("execution_candidate_id"):
        raise FailClosedRuntimeError("governed worker execution failed closed: approval candidate mismatch")
    if approval.get("source_execution_candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("governed worker execution failed closed: approval candidate hash mismatch")
    if approval.get("approval_scope") != "RUN_GOVERNED_WORKER_EXECUTION_ONLY":
        raise FailClosedRuntimeError("governed worker execution failed closed: approval scope invalid")
    if approval.get("worker_execution_allowed") is not True:
        raise FailClosedRuntimeError("governed worker execution failed closed: execution approval required")
    if approval.get("implementation_result_creation_allowed") is not False:
        raise FailClosedRuntimeError("governed worker execution failed closed: approval scope exceeds execution")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _validation_inputs(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    execution_summary_artifact: dict[str, Any],
    human_confirmation_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    validation_inputs: dict[str, Any] | None,
) -> dict[str, Any]:
    if validation_inputs is not None and not isinstance(validation_inputs, dict):
        raise FailClosedRuntimeError("governed worker execution failed closed: validation inputs invalid")
    artifact = {
        "artifact_type": "WORKER_EXECUTION_VALIDATION_INPUTS_ARTIFACT_V1",
        "runtime_version": AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_VERSION,
        "worker_execution_id": _require_string(execution_id, "execution_id"),
        "source_execution_candidate": candidate["execution_candidate_id"],
        "source_execution_candidate_hash": candidate["artifact_hash"],
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "execution_summary_reference": execution_summary_artifact["summary_id"],
        "execution_summary_hash": execution_summary_artifact["artifact_hash"],
        "human_confirmation_reference": human_confirmation_artifact["confirmation_id"],
        "human_confirmation_hash": human_confirmation_artifact["artifact_hash"],
        "execution_objective": candidate["execution_objective"],
        "execution_constraints": deepcopy(candidate["execution_constraints"]),
        "governance_constraints": deepcopy(candidate["governance_constraints"]),
        "provided_validation_inputs": deepcopy(validation_inputs or {}),
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "replay_visible": True,
        "validation_performed": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_result_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    validation_inputs_artifact: dict[str, Any],
    execution_summary_artifact: dict[str, Any],
    human_confirmation_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    execution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    execution_logs = [
        "execution candidate artifact hash verified",
        "explicit human approval verified",
        "replay lineage verified",
        "deterministic governed worker execution completed",
        "implementation result creation withheld",
    ]
    worker_evidence = {
        "worker_evidence_type": "DETERMINISTIC_GOVERNED_WORKER_EVIDENCE",
        "execution_objective_hash": replay_hash(candidate["execution_objective"]),
        "source_execution_candidate_hash": candidate["artifact_hash"],
        "governed_execution": True,
        "external_provider_invoked": False,
        "subprocess_invoked": False,
    }
    artifact = {
        "artifact_type": WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_VERSION,
        "worker_execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": execution_status,
        "execution_outcome": "COMPLETED",
        "source_execution_candidate": candidate["execution_candidate_id"],
        "source_execution_candidate_hash": candidate["artifact_hash"],
        "source_invocation_candidate": candidate["source_invocation_candidate"],
        "source_invocation_candidate_hash": candidate["source_invocation_candidate_hash"],
        "source_dispatch_candidate": candidate["source_dispatch_candidate"],
        "source_dispatch_candidate_hash": candidate["source_dispatch_candidate_hash"],
        "source_worker_request": candidate["source_worker_request"],
        "source_worker_request_hash": candidate["source_worker_request_hash"],
        "source_implementation_request": candidate["source_implementation_request"],
        "source_implementation_request_hash": candidate["source_implementation_request_hash"],
        "replay_references": deepcopy(candidate["replay_references"]),
        "replay_hashes": deepcopy(candidate["replay_hashes"]),
        "human_approval_reference": approval["approval_id"],
        "human_approval_hash": approval["artifact_hash"],
        "execution_summary_reference": execution_summary_artifact["summary_id"],
        "execution_summary_hash": execution_summary_artifact["artifact_hash"],
        "human_confirmation_reference": human_confirmation_artifact["confirmation_id"],
        "human_confirmation_hash": human_confirmation_artifact["artifact_hash"],
        "validation_inputs": deepcopy(validation_inputs_artifact),
        "validation_inputs_hash": validation_inputs_artifact["artifact_hash"],
        "execution_objective": candidate["execution_objective"],
        "worker_evidence": worker_evidence,
        "execution_logs": execution_logs,
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "ready_for_result_validation_runtime": True,
        "worker_executed": True,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_execution_result_artifact(
    *,
    execution_id: str,
    execution_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    executed_by: str,
    executed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_VERSION,
        "worker_execution_id": execution_id if isinstance(execution_id, str) else "INVALID",
        "execution_status": FAILED_CLOSED,
        "execution_outcome": "FAILED_CLOSED",
        "source_execution_candidate": execution_candidate_artifact.get("execution_candidate_id")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_execution_candidate_hash": execution_candidate_artifact.get("artifact_hash")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_invocation_candidate": execution_candidate_artifact.get("source_invocation_candidate")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_dispatch_candidate": execution_candidate_artifact.get("source_dispatch_candidate")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_worker_request": execution_candidate_artifact.get("source_worker_request")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_implementation_request": execution_candidate_artifact.get("source_implementation_request")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "replay_references": [],
        "replay_hashes": [],
        "human_approval_reference": human_approval_artifact.get("approval_id")
        if isinstance(human_approval_artifact, dict)
        else None,
        "human_approval_hash": human_approval_artifact.get("artifact_hash")
        if isinstance(human_approval_artifact, dict)
        else None,
        "execution_summary_reference": None,
        "execution_summary_hash": None,
        "human_confirmation_reference": None,
        "human_confirmation_hash": None,
        "validation_inputs": {},
        "validation_inputs_hash": None,
        "execution_objective": None,
        "worker_evidence": {},
        "execution_logs": [],
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "ready_for_result_validation_runtime": False,
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(result: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(result)
    artifact = {
        "event_type": "WORKER_EXECUTION_RETURNED",
        "worker_execution_reference": result["worker_execution_id"],
        "worker_execution_hash": result["artifact_hash"],
        "execution_status": result["execution_status"],
        "execution_outcome": result["execution_outcome"],
        "source_execution_candidate": result["source_execution_candidate"],
        "execution_summary_reference": result.get("execution_summary_reference"),
        "execution_summary_hash": result.get("execution_summary_hash"),
        "human_confirmation_reference": result.get("human_confirmation_reference"),
        "human_confirmation_hash": result.get("human_confirmation_hash"),
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "fail_closed_preserved": result["fail_closed_preserved"],
        "ready_for_result_validation_runtime": result["ready_for_result_validation_runtime"],
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": result["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    validation_inputs_artifact: dict[str, Any] | None,
    result: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_GOVERNED_WORKER_EXECUTION_RUNTIME_VERSION,
        "execution_status": result["execution_status"],
        "validation_inputs_artifact": deepcopy(validation_inputs_artifact),
        "worker_execution_result_artifact": deepcopy(result),
        "worker_execution_returned_artifact": deepcopy(returned),
        "worker_execution_replay_reference": str(replay_path),
        "worker_execution_completed": result["execution_status"] == WORKER_EXECUTION_COMPLETED,
        "execution_result_artifact_generated": result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "fail_closed_preserved": result["fail_closed_preserved"],
        "ready_for_result_validation_runtime": result["ready_for_result_validation_runtime"],
        "execution_summary_reference": result.get("execution_summary_reference"),
        "execution_summary_hash": result.get("execution_summary_hash"),
        "human_confirmation_reference": result.get("human_confirmation_reference"),
        "human_confirmation_hash": result.get("human_confirmation_hash"),
        "failure_reason": result["failure_reason"],
    }
    capture["governed_worker_execution_capture_hash"] = replay_hash(capture)
    return capture


def _default_execution_summary(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    executed_by: str,
    executed_at: str,
) -> dict[str, Any]:
    return create_execution_summary(
        summary_id=f"{_require_string(execution_id, 'execution_id')}:EXECUTION-SUMMARY",
        original_request=str(candidate.get("source_implementation_request") or candidate["execution_candidate_id"]),
        interpreted_intent={
            "intent_type": "RUN_GOVERNED_WORKER_EXECUTION",
            "execution_candidate_reference": candidate["execution_candidate_id"],
            "execution_objective": candidate["execution_objective"],
        },
        selected_route={
            "route_type": "GOVERNED_WORKER_EXECUTION_RUNTIME",
            "source_execution_candidate": candidate["execution_candidate_id"],
        },
        planned_actions=[
            {
                "action": "RUN_GOVERNED_WORKER_EXECUTION",
                "execution_candidate_reference": candidate["execution_candidate_id"],
            }
        ],
        expected_outputs=[
            {
                "artifact_type": WORKER_EXECUTION_RESULT_ARTIFACT_V1,
                "status": WORKER_EXECUTION_COMPLETED,
            }
        ],
        assumptions=["Human execution approval has been validated against the execution candidate."],
        constraints=[
            "Implementation result creation remains withheld.",
            "Provider invocation, code modification, and governance mutation remain prohibited.",
        ],
        risk_classification={
            "risk_level": "GOVERNED_WORKER_EXECUTION",
            "reason": "The transition performs bounded worker execution.",
        },
        execution_scope={
            "execution_constraints": deepcopy(candidate["execution_constraints"]),
            "governance_constraints": deepcopy(candidate["governance_constraints"]),
            "approval_scope": approval["approval_scope"],
        },
        replay_references=deepcopy(candidate["replay_references"]),
        created_by=_require_string(executed_by, "executed_by"),
        created_at=_require_string(executed_at, "executed_at"),
    )


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


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("governed worker execution failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed worker execution failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("governed worker execution artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("governed worker execution artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("governed worker execution replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("governed worker execution replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed worker execution failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"governed worker execution failed closed: {field_name} must be a replay hash")
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _hash_list(value: Any) -> list[str]:
    return [item for item in _string_list(value) if item.startswith("sha256:")]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed worker execution failed closed"
