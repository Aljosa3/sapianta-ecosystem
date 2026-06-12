"""First provider-neutral proposal-only external LLM worker."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.external_worker_adapter_runtime import (
    EXTERNAL_WORKER_RESULT_PACKAGE_V1,
    EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
    EXTERNAL_WORKER_TASK_PACKAGE_V1,
    create_external_worker_result_package,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION = "AIGOL_FIRST_EXTERNAL_LLM_WORKER_V1"
FIRST_EXTERNAL_LLM_WORKER_ID = "PROVIDER_NEUTRAL_PROPOSAL_WORKER_V1"
FAILED_CLOSED = "FAILED_CLOSED"


def run_first_external_llm_worker(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
) -> dict[str, Any]:
    """Consume a task package and return proposal-only external worker result data."""

    try:
        task = deepcopy(task_package_artifact)
        _validate_task_package(task)
        proposals = _proposal_payload(task)
        evidence = _worker_evidence(task, proposals)
        result_package = create_external_worker_result_package(
            result_id=result_id,
            task_package_artifact=task,
            worker_result_payload=proposals,
            worker_evidence=evidence,
            execution_logs=[
                "external worker task package consumed",
                "proposal-only patch proposal generated",
                "proposal-only file proposal generated",
                "proposal-only test proposal generated",
                "no repository mutation performed",
                "no command execution performed",
            ],
            completed_at=completed_at,
        )
        return _capture(result_package, task, failure_reason=None)
    except Exception as exc:
        result_package = _failed_result_package(
            result_id=result_id,
            task_package_artifact=task_package_artifact,
            completed_at=completed_at,
            failure_reason=_failure_reason(exc),
        )
        return _capture(result_package, task_package_artifact, failure_reason=result_package["failure_reason"])


def _validate_task_package(task: dict[str, Any]) -> None:
    _verify_artifact_hash(task)
    if task.get("artifact_type") != EXTERNAL_WORKER_TASK_PACKAGE_V1:
        raise FailClosedRuntimeError("first external worker failed closed: invalid task package type")
    if task.get("task_status") != EXTERNAL_WORKER_TASK_PACKAGE_CREATED:
        raise FailClosedRuntimeError("first external worker failed closed: task package not ready")
    if task.get("provider_neutral") is not True or task.get("provider_specific_logic_used") is not False:
        raise FailClosedRuntimeError("first external worker failed closed: provider neutrality invalid")
    authorization = task.get("worker_authorization")
    if not isinstance(authorization, dict) or authorization.get("authorized") is not True:
        raise FailClosedRuntimeError("first external worker failed closed: worker authorization missing")
    capabilities = authorization.get("capabilities")
    if not isinstance(capabilities, list) or "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1" not in capabilities:
        raise FailClosedRuntimeError("first external worker failed closed: worker capability missing")
    if "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1" not in capabilities:
        raise FailClosedRuntimeError("first external worker failed closed: result package capability missing")
    scope = task.get("execution_scope")
    if not isinstance(scope, dict):
        raise FailClosedRuntimeError("first external worker failed closed: execution scope invalid")
    if scope.get("implementation_result_creation_allowed") is not False:
        raise FailClosedRuntimeError("first external worker failed closed: proposal-only boundary invalid")
    if task.get("replay_lineage_preserved") is not True or task.get("certification_integrity_preserved") is not True:
        raise FailClosedRuntimeError("first external worker failed closed: lineage or certification invalid")


def _proposal_payload(task: dict[str, Any]) -> dict[str, Any]:
    objective = task["execution_scope"]["execution_objective"]
    target_path = _target_path(task)
    return {
        "payload_type": "PROPOSAL_ONLY_EXTERNAL_WORKER_PAYLOAD_V1",
        "task_id": task["task_id"],
        "source_execution_candidate": task["source_execution_candidate"],
        "proposal_authority": "PROPOSAL_ONLY",
        "execution_objective": objective,
        "patch_proposals": [
            {
                "proposal_id": f"{task['task_id']}-PATCH-001",
                "target_path": target_path,
                "patch_intent": "Add bounded implementation matching the execution objective.",
                "diff_preview": [
                    {
                        "operation": "PROPOSE_UPDATE",
                        "path": target_path,
                        "summary": objective,
                    }
                ],
                "applied": False,
            }
        ],
        "file_proposals": [
            {
                "proposal_id": f"{task['task_id']}-FILE-001",
                "target_path": target_path,
                "content_summary": "Provider-neutral worker proposal; no file written by this worker.",
                "content_hash": replay_hash({"objective": objective, "target_path": target_path}),
                "created": False,
            }
        ],
        "test_proposals": [
            {
                "proposal_id": f"{task['task_id']}-TEST-001",
                "target_path": _test_path(target_path),
                "test_intent": "Validate the proposed implementation under existing governance constraints.",
                "created": False,
                "executed": False,
            }
        ],
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "provider_neutral": True,
        "certification_compatible": True,
        "replay_compatible": True,
    }


def _worker_evidence(task: dict[str, Any], proposals: dict[str, Any]) -> dict[str, Any]:
    return {
        "worker_runtime": AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
        "worker_id": FIRST_EXTERNAL_LLM_WORKER_ID,
        "task_id": task["task_id"],
        "task_package_hash": task["artifact_hash"],
        "proposal_payload_hash": replay_hash(proposals),
        "patch_proposal_generated": True,
        "file_proposal_generated": True,
        "test_proposal_generated": True,
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "provider_neutral": True,
        "replay_compatible": True,
        "certification_compatible": True,
    }


def _failed_result_package(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "runtime_version": AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
        "result_id": result_id if isinstance(result_id, str) else "INVALID",
        "task_id": task_package_artifact.get("task_id") if isinstance(task_package_artifact, dict) else None,
        "task_package_hash": task_package_artifact.get("artifact_hash") if isinstance(task_package_artifact, dict) else None,
        "source_execution_candidate": task_package_artifact.get("source_execution_candidate")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_execution_candidate_hash": task_package_artifact.get("source_execution_candidate_hash")
        if isinstance(task_package_artifact, dict)
        else None,
        "worker_interface": None,
        "execution_status": FAILED_CLOSED,
        "execution_outcome": FAILED_CLOSED,
        "worker_result_payload": {},
        "worker_result_payload_hash": replay_hash({}),
        "worker_evidence": {
            "worker_runtime": AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
            "repository_mutation_performed": False,
            "command_execution_performed": False,
        },
        "worker_evidence_hash": replay_hash(
            {
                "worker_runtime": AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
                "repository_mutation_performed": False,
                "command_execution_performed": False,
            }
        ),
        "execution_logs": ["first external worker failed closed before proposal generation"],
        "completed_at": completed_at if isinstance(completed_at, str) else None,
        "provider_neutral": True,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(result_package: dict[str, Any], task: dict[str, Any], failure_reason: str | None) -> dict[str, Any]:
    payload = result_package.get("worker_result_payload") if isinstance(result_package, dict) else {}
    capture = {
        "runtime_version": AIGOL_FIRST_EXTERNAL_LLM_WORKER_RUNTIME_VERSION,
        "worker_status": result_package["execution_status"],
        "external_worker_result_package": deepcopy(result_package),
        "source_task_package": task.get("task_id") if isinstance(task, dict) else None,
        "task_package_consumed": failure_reason is None,
        "result_package_generated": result_package.get("artifact_type") == EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "patch_proposal_generated": bool(payload.get("patch_proposals")) if isinstance(payload, dict) else False,
        "file_proposal_generated": bool(payload.get("file_proposals")) if isinstance(payload, dict) else False,
        "test_proposal_generated": bool(payload.get("test_proposals")) if isinstance(payload, dict) else False,
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "replay_compatibility_confirmed": failure_reason is None,
        "provider_neutrality_confirmed": result_package.get("provider_neutral") is True,
        "ready_for_real_worker_evaluation": failure_reason is None,
        "failure_reason": failure_reason,
    }
    capture["first_external_worker_capture_hash"] = replay_hash(capture)
    return capture


def _target_path(task: dict[str, Any]) -> str:
    source = str(task.get("source_implementation_request") or "implementation")
    suffix = source.lower().replace("_", "-").replace(" ", "-")
    return f"proposals/{suffix}.proposal.md"


def _test_path(target_path: str) -> str:
    stem = target_path.rsplit("/", 1)[-1].replace(".proposal.md", "")
    return f"tests/test_{stem.replace('-', '_')}_proposal.py"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("first external worker artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("first external worker artifact hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "first external worker failed closed"
