"""Provider-neutral external worker adapter runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    WORKER_EXECUTION_RESULT_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
    WORKER_EXECUTION_CANDIDATE_CREATED,
)


AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION = "AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_V1"
EXTERNAL_WORKER_TASK_PACKAGE_V1 = "EXTERNAL_WORKER_TASK_PACKAGE_V1"
EXTERNAL_WORKER_RESULT_PACKAGE_V1 = "EXTERNAL_WORKER_RESULT_PACKAGE_V1"
EXTERNAL_WORKER_TASK_PACKAGE_CREATED = "EXTERNAL_WORKER_TASK_PACKAGE_CREATED"
EXTERNAL_WORKER_RESULT_ACCEPTED = "EXTERNAL_WORKER_RESULT_ACCEPTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "external_worker_task_package_recorded",
    "external_worker_result_package_recorded",
    "external_worker_execution_result_recorded",
    "external_worker_adapter_returned",
)


def create_external_worker_task_package(
    *,
    task_id: str,
    execution_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    worker_capability_declaration: dict[str, Any],
) -> dict[str, Any]:
    """Create a provider-neutral task package from a governed execution candidate."""

    replay_path = Path(replay_dir)
    try:
        _ensure_task_replay_available(replay_path)
        candidate = deepcopy(execution_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        capability = deepcopy(worker_capability_declaration)
        _validate_execution_candidate(candidate)
        _validate_task_approval(approval, candidate)
        _validate_worker_capability_declaration(capability)
        task = _task_package_artifact(
            task_id=task_id,
            candidate=candidate,
            approval=approval,
            capability=capability,
            requested_by=requested_by,
            created_at=created_at,
            task_status=EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], task)
        return _task_capture(task, replay_path)
    except Exception as exc:
        task = _failed_task_package_artifact(
            task_id=task_id,
            execution_candidate_artifact=execution_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], task)
        return _task_capture(task, replay_path)


def accept_external_worker_result_package(
    *,
    result_package: dict[str, Any],
    task_package_artifact: dict[str, Any],
    accepted_by: str,
    accepted_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate a provider-neutral result package and emit a worker execution result."""

    replay_path = Path(replay_dir)
    try:
        _ensure_result_replay_available(replay_path)
        task = deepcopy(task_package_artifact)
        result_package_copy = deepcopy(result_package)
        _validate_task_package(task)
        _validate_result_package(result_package_copy, task)
        result = _worker_execution_result_artifact(
            task=task,
            result_package=result_package_copy,
            accepted_by=accepted_by,
            accepted_at=accepted_at,
            execution_status=WORKER_EXECUTION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(result)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result_package_copy)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], result)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _result_capture(result_package_copy, result, returned, replay_path)
    except Exception as exc:
        result = _failed_worker_execution_result_artifact(
            result_package=result_package,
            task_package_artifact=task_package_artifact,
            accepted_by=accepted_by,
            accepted_at=accepted_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(result)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], result)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _result_capture(None, result, returned, replay_path)


def create_external_worker_result_package(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    worker_result_payload: dict[str, Any],
    worker_evidence: dict[str, Any],
    execution_logs: list[str],
    completed_at: str,
) -> dict[str, Any]:
    """Create a neutral fixture result package that an external worker adapter can return."""

    task = deepcopy(task_package_artifact)
    _validate_task_package(task)
    _require_object(worker_result_payload, "worker_result_payload")
    _require_object(worker_evidence, "worker_evidence")
    logs = _require_string_list(execution_logs, "execution_logs")
    artifact = {
        "artifact_type": EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "result_id": _require_string(result_id, "result_id"),
        "task_id": task["task_id"],
        "task_package_hash": task["artifact_hash"],
        "source_execution_candidate": task["source_execution_candidate"],
        "source_execution_candidate_hash": task["source_execution_candidate_hash"],
        "worker_interface": deepcopy(task["worker_authorization"]["worker_interface"]),
        "execution_status": WORKER_EXECUTION_COMPLETED,
        "execution_outcome": "COMPLETED",
        "worker_result_payload": deepcopy(worker_result_payload),
        "worker_result_payload_hash": replay_hash(worker_result_payload),
        "worker_evidence": deepcopy(worker_evidence),
        "worker_evidence_hash": replay_hash(worker_evidence),
        "execution_logs": logs,
        "completed_at": _require_string(completed_at, "completed_at"),
        "provider_neutral": True,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_external_worker_adapter_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate the complete external worker adapter replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("external worker adapter replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("external worker adapter replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    task = wrappers[0]["artifact"]
    result_package = wrappers[1]["artifact"]
    result = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if result_package.get("task_package_hash") != task["artifact_hash"]:
        raise FailClosedRuntimeError("external worker adapter result task hash mismatch")
    if result.get("external_worker_task_package_hash") != task["artifact_hash"]:
        raise FailClosedRuntimeError("external worker adapter execution result task hash mismatch")
    if result.get("external_worker_result_package_hash") != result_package["artifact_hash"]:
        raise FailClosedRuntimeError("external worker adapter execution result package hash mismatch")
    if returned.get("worker_execution_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("external worker adapter returned result hash mismatch")
    return {
        "task_id": task["task_id"],
        "worker_execution_id": result["worker_execution_id"],
        "task_package_generated": task["artifact_type"] == EXTERNAL_WORKER_TASK_PACKAGE_V1,
        "result_package_accepted": result_package["artifact_type"] == EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "execution_result_generated": result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "provider_neutrality_preserved": result["provider_neutrality_preserved"],
        "ready_for_first_external_worker": result["ready_for_result_validation_runtime"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_execution_candidate(candidate: dict[str, Any]) -> None:
    _verify_artifact_hash(candidate)
    if candidate.get("artifact_type") != WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("external worker adapter failed closed: invalid artifact type")
    if candidate.get("candidate_status") != WORKER_EXECUTION_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("external worker adapter failed closed: certified execution candidate required")
    if candidate.get("certification_status") != "CERTIFIED_WORKER_INVOCATION_CANDIDATE_ACCEPTED":
        raise FailClosedRuntimeError("external worker adapter failed closed: certification integrity invalid")
    if candidate.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: replay lineage broken")
    if candidate.get("human_approval_required") is not True or candidate.get("human_approval_granted") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: human approval chain required")
    if candidate.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: human authority missing")
    if candidate.get("ready_for_governed_worker_execution") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: execution candidate not ready")
    for field in (
        "source_invocation_candidate",
        "source_dispatch_candidate",
        "source_worker_request",
        "source_implementation_request",
    ):
        _require_string(candidate.get(field), field)
        _require_hash(candidate.get(f"{field}_hash"), f"{field}_hash")
    if not _require_string_list(candidate.get("replay_references"), "replay_references"):
        raise FailClosedRuntimeError("external worker adapter failed closed: replay references required")
    if not _hash_list(candidate.get("replay_hashes")):
        raise FailClosedRuntimeError("external worker adapter failed closed: replay hashes required")
    for flag in (
        "worker_executed",
        "implementation_result_created",
        "code_modified",
        "governance_modified",
        "provider_invoked",
        "execution_requested",
    ):
        if candidate.get(flag) is not False:
            raise FailClosedRuntimeError(f"external worker adapter failed closed: candidate {flag} must be false")


def _validate_task_approval(approval: dict[str, Any], candidate: dict[str, Any]) -> None:
    _verify_artifact_hash(approval)
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("external worker adapter failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: explicit human approval required")
    if approval.get("source_execution_candidate") != candidate.get("execution_candidate_id"):
        raise FailClosedRuntimeError("external worker adapter failed closed: approval candidate mismatch")
    if approval.get("source_execution_candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("external worker adapter failed closed: approval candidate hash mismatch")
    if approval.get("approval_scope") != "CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY":
        raise FailClosedRuntimeError("external worker adapter failed closed: approval scope invalid")
    if approval.get("external_worker_task_allowed") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: external worker task approval required")
    if approval.get("implementation_result_creation_allowed") is not False:
        raise FailClosedRuntimeError("external worker adapter failed closed: approval scope exceeds adapter")
    _require_string(approval.get("approval_id"), "approval_id")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _validate_worker_capability_declaration(capability: dict[str, Any]) -> None:
    _require_object(capability, "worker_capability_declaration")
    _require_string(capability.get("worker_interface"), "worker_interface")
    _require_string(capability.get("worker_family"), "worker_family")
    capabilities = _require_string_list(capability.get("capabilities"), "capabilities")
    if "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1" not in capabilities:
        raise FailClosedRuntimeError("external worker adapter failed closed: worker capability missing")
    if capability.get("provider_neutral_contract") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: provider-neutral contract required")


def _validate_task_package(task: dict[str, Any]) -> None:
    _verify_artifact_hash(task)
    if task.get("artifact_type") != EXTERNAL_WORKER_TASK_PACKAGE_V1:
        raise FailClosedRuntimeError("external worker adapter failed closed: invalid task package type")
    if task.get("task_status") != EXTERNAL_WORKER_TASK_PACKAGE_CREATED:
        raise FailClosedRuntimeError("external worker adapter failed closed: task package not created")
    if task.get("provider_neutral") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: task package is not provider-neutral")
    _require_string(task.get("task_id"), "task_id")
    _require_hash(task.get("source_execution_candidate_hash"), "source_execution_candidate_hash")
    if not _hash_list(task.get("replay_hashes")):
        raise FailClosedRuntimeError("external worker adapter failed closed: task replay hashes required")
    authorization = _require_object(task.get("worker_authorization"), "worker_authorization")
    if authorization.get("authorized") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: task authorization missing")


def _validate_result_package(result_package: dict[str, Any], task: dict[str, Any]) -> None:
    _verify_artifact_hash(result_package)
    if result_package.get("artifact_type") != EXTERNAL_WORKER_RESULT_PACKAGE_V1:
        raise FailClosedRuntimeError("external worker adapter failed closed: invalid result package type")
    if result_package.get("task_id") != task.get("task_id"):
        raise FailClosedRuntimeError("external worker adapter failed closed: task integrity mismatch")
    if result_package.get("task_package_hash") != task.get("artifact_hash"):
        raise FailClosedRuntimeError("external worker adapter failed closed: task hash mismatch")
    if result_package.get("source_execution_candidate") != task.get("source_execution_candidate"):
        raise FailClosedRuntimeError("external worker adapter failed closed: execution candidate mismatch")
    if result_package.get("source_execution_candidate_hash") != task.get("source_execution_candidate_hash"):
        raise FailClosedRuntimeError("external worker adapter failed closed: execution candidate hash mismatch")
    if result_package.get("worker_interface") != task["worker_authorization"]["worker_interface"]:
        raise FailClosedRuntimeError("external worker adapter failed closed: worker interface mismatch")
    if result_package.get("execution_status") != WORKER_EXECUTION_COMPLETED:
        raise FailClosedRuntimeError("external worker adapter failed closed: worker execution incomplete")
    if result_package.get("provider_neutral") is not True:
        raise FailClosedRuntimeError("external worker adapter failed closed: result package is not provider-neutral")
    _require_object(result_package.get("worker_result_payload"), "worker_result_payload")
    _require_object(result_package.get("worker_evidence"), "worker_evidence")
    if result_package.get("worker_result_payload_hash") != replay_hash(result_package["worker_result_payload"]):
        raise FailClosedRuntimeError("external worker adapter failed closed: worker result payload hash mismatch")
    if result_package.get("worker_evidence_hash") != replay_hash(result_package["worker_evidence"]):
        raise FailClosedRuntimeError("external worker adapter failed closed: worker evidence hash mismatch")
    _require_string_list(result_package.get("execution_logs"), "execution_logs")


def _task_package_artifact(
    *,
    task_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    capability: dict[str, Any],
    requested_by: str,
    created_at: str,
    task_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXTERNAL_WORKER_TASK_PACKAGE_V1,
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "task_id": _require_string(task_id, "task_id"),
        "task_status": task_status,
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
        "execution_scope": {
            "execution_objective": candidate["execution_objective"],
            "execution_constraints": deepcopy(candidate["execution_constraints"]),
            "governance_constraints": deepcopy(candidate["governance_constraints"]),
            "implementation_result_creation_allowed": False,
        },
        "worker_authorization": {
            "authorized": True,
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "worker_interface": capability["worker_interface"],
            "worker_family": capability["worker_family"],
            "capabilities": deepcopy(capability["capabilities"]),
            "provider_neutral_contract": True,
        },
        "implementation_request_references": {
            "source_implementation_request": candidate["source_implementation_request"],
            "source_implementation_request_hash": candidate["source_implementation_request_hash"],
            "source_worker_request": candidate["source_worker_request"],
            "source_worker_request_hash": candidate["source_worker_request_hash"],
        },
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "provider_neutral": True,
        "provider_specific_logic_used": False,
        "replay_lineage_preserved": True,
        "certification_integrity_preserved": True,
        "fail_closed_preserved": True,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_execution_result_artifact(
    *,
    task: dict[str, Any],
    result_package: dict[str, Any],
    accepted_by: str,
    accepted_at: str,
    execution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    worker_execution_id = "EXTERNAL-WORKER-EXECUTION-" + result_package["result_id"]
    validation_inputs = {
        "artifact_type": "EXTERNAL_WORKER_VALIDATION_INPUTS_ARTIFACT_V1",
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "task_id": task["task_id"],
        "task_package_hash": task["artifact_hash"],
        "result_package_hash": result_package["artifact_hash"],
        "task_integrity_validated": True,
        "authorization_validated": True,
        "certification_integrity_validated": True,
        "provider_neutrality_validated": True,
        "validation_performed": True,
        "replay_visible": True,
    }
    validation_inputs["artifact_hash"] = replay_hash(validation_inputs)
    worker_evidence = {
        "worker_evidence_type": "EXTERNAL_WORKER_EVIDENCE",
        "external_worker_task_package_hash": task["artifact_hash"],
        "external_worker_result_package_hash": result_package["artifact_hash"],
        "worker_result_payload_hash": result_package["worker_result_payload_hash"],
        "worker_evidence_hash": result_package["worker_evidence_hash"],
        "governed_execution": True,
        "external_provider_invoked": False,
        "subprocess_invoked": False,
        "provider_neutral_contract": True,
    }
    artifact = {
        "artifact_type": WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "worker_execution_id": worker_execution_id,
        "execution_status": execution_status,
        "execution_outcome": result_package["execution_outcome"],
        "source_execution_candidate": task["source_execution_candidate"],
        "source_execution_candidate_hash": task["source_execution_candidate_hash"],
        "source_invocation_candidate": task["source_invocation_candidate"],
        "source_invocation_candidate_hash": task["source_invocation_candidate_hash"],
        "source_dispatch_candidate": task["source_dispatch_candidate"],
        "source_dispatch_candidate_hash": task["source_dispatch_candidate_hash"],
        "source_worker_request": task["source_worker_request"],
        "source_worker_request_hash": task["source_worker_request_hash"],
        "source_implementation_request": task["source_implementation_request"],
        "source_implementation_request_hash": task["source_implementation_request_hash"],
        "external_worker_task_package": task["task_id"],
        "external_worker_task_package_hash": task["artifact_hash"],
        "external_worker_result_package": result_package["result_id"],
        "external_worker_result_package_hash": result_package["artifact_hash"],
        "replay_references": deepcopy(task["replay_references"]),
        "replay_hashes": deepcopy(task["replay_hashes"]),
        "human_approval_reference": task["worker_authorization"]["human_approval_reference"],
        "human_approval_hash": task["worker_authorization"]["human_approval_hash"],
        "validation_inputs": validation_inputs,
        "validation_inputs_hash": validation_inputs["artifact_hash"],
        "execution_objective": task["execution_scope"]["execution_objective"],
        "worker_evidence": worker_evidence,
        "execution_logs": deepcopy(result_package["execution_logs"]),
        "worker_result_payload": deepcopy(result_package["worker_result_payload"]),
        "executed_by": result_package["worker_interface"],
        "executed_at": result_package["completed_at"],
        "accepted_by": _require_string(accepted_by, "accepted_by"),
        "accepted_at": _require_string(accepted_at, "accepted_at"),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "ready_for_result_validation_runtime": True,
        "worker_executed": True,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "provider_neutrality_preserved": True,
        "provider_specific_logic_used": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_task_package_artifact(
    *,
    task_id: str,
    execution_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXTERNAL_WORKER_TASK_PACKAGE_V1,
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "task_id": task_id if isinstance(task_id, str) else "INVALID",
        "task_status": FAILED_CLOSED,
        "source_execution_candidate": execution_candidate_artifact.get("execution_candidate_id")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_execution_candidate_hash": execution_candidate_artifact.get("artifact_hash")
        if isinstance(execution_candidate_artifact, dict)
        else None,
        "source_invocation_candidate": None,
        "source_dispatch_candidate": None,
        "source_worker_request": None,
        "source_implementation_request": None,
        "replay_references": [],
        "replay_hashes": [],
        "execution_scope": {},
        "worker_authorization": {
            "authorized": False,
            "human_approval_hash": human_approval_artifact.get("artifact_hash")
            if isinstance(human_approval_artifact, dict)
            else None,
        },
        "implementation_request_references": {},
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "provider_neutral": True,
        "provider_specific_logic_used": False,
        "replay_lineage_preserved": False,
        "certification_integrity_preserved": False,
        "fail_closed_preserved": True,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_worker_execution_result_artifact(
    *,
    result_package: dict[str, Any],
    task_package_artifact: dict[str, Any],
    accepted_by: str,
    accepted_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "worker_execution_id": "INVALID",
        "execution_status": FAILED_CLOSED,
        "execution_outcome": FAILED_CLOSED,
        "source_execution_candidate": task_package_artifact.get("source_execution_candidate")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_execution_candidate_hash": task_package_artifact.get("source_execution_candidate_hash")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_invocation_candidate": task_package_artifact.get("source_invocation_candidate")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_dispatch_candidate": task_package_artifact.get("source_dispatch_candidate")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_worker_request": task_package_artifact.get("source_worker_request")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_implementation_request": task_package_artifact.get("source_implementation_request")
        if isinstance(task_package_artifact, dict)
        else None,
        "external_worker_task_package": task_package_artifact.get("task_id")
        if isinstance(task_package_artifact, dict)
        else None,
        "external_worker_task_package_hash": task_package_artifact.get("artifact_hash")
        if isinstance(task_package_artifact, dict)
        else None,
        "external_worker_result_package": result_package.get("result_id") if isinstance(result_package, dict) else None,
        "external_worker_result_package_hash": result_package.get("artifact_hash")
        if isinstance(result_package, dict)
        else None,
        "replay_references": [],
        "replay_hashes": [],
        "human_approval_reference": None,
        "human_approval_hash": None,
        "validation_inputs": {},
        "validation_inputs_hash": None,
        "execution_objective": None,
        "worker_evidence": {},
        "execution_logs": [],
        "worker_result_payload": {},
        "executed_by": None,
        "executed_at": None,
        "accepted_by": accepted_by if isinstance(accepted_by, str) else None,
        "accepted_at": accepted_at if isinstance(accepted_at, str) else None,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "ready_for_result_validation_runtime": False,
        "worker_executed": False,
        "implementation_result_created": False,
        "code_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "provider_neutrality_preserved": True,
        "provider_specific_logic_used": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(result: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(result)
    artifact = {
        "event_type": "EXTERNAL_WORKER_ADAPTER_RETURNED",
        "worker_execution_reference": result["worker_execution_id"],
        "worker_execution_hash": result["artifact_hash"],
        "execution_status": result["execution_status"],
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "provider_neutrality_preserved": result["provider_neutrality_preserved"],
        "ready_for_result_validation_runtime": result["ready_for_result_validation_runtime"],
        "failure_reason": result["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _task_capture(task: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "task_status": task["task_status"],
        "external_worker_task_package": deepcopy(task),
        "external_worker_replay_reference": str(replay_path),
        "task_package_generated": task["artifact_type"] == EXTERNAL_WORKER_TASK_PACKAGE_V1
        and task["task_status"] == EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
        "replay_lineage_preserved": task["replay_lineage_preserved"],
        "provider_neutrality_preserved": task["provider_neutral"],
        "failure_reason": task["failure_reason"],
    }
    capture["external_worker_task_capture_hash"] = replay_hash(capture)
    return capture


def _result_capture(
    result_package: dict[str, Any] | None,
    result: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_VERSION,
        "execution_status": result["execution_status"],
        "external_worker_result_package": deepcopy(result_package),
        "worker_execution_result_artifact": deepcopy(result),
        "external_worker_adapter_returned_artifact": deepcopy(returned),
        "external_worker_replay_reference": str(replay_path),
        "result_package_accepted": result_package is not None,
        "execution_result_artifact_generated": result["artifact_type"] == WORKER_EXECUTION_RESULT_ARTIFACT_V1,
        "replay_lineage_preserved": result["replay_lineage_preserved"],
        "provider_neutrality_preserved": result["provider_neutrality_preserved"],
        "ready_for_first_external_worker": result["ready_for_result_validation_runtime"],
        "failure_reason": result["failure_reason"],
    }
    capture["external_worker_result_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_task_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEPS[0]}.json").exists():
        raise FailClosedRuntimeError("external worker adapter failed closed: task replay already exists")


def _ensure_result_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS[1:], start=1):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("external worker adapter failed closed: result replay already exists")


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
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("external worker adapter artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("external worker adapter artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("external worker adapter replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("external worker adapter replay hash mismatch")


def _require_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"external worker adapter failed closed: {field_name} must be object")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"external worker adapter failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"external worker adapter failed closed: {field_name} must be a replay hash")
    return text


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"external worker adapter failed closed: {field_name} must be a list")
    items = [_require_string(item, field_name) for item in value]
    if not items:
        raise FailClosedRuntimeError(f"external worker adapter failed closed: {field_name} requires at least one item")
    return items


def _hash_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.startswith("sha256:")]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "external worker adapter failed closed"
