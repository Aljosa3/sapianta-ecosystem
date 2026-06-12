"""OpenAI-backed external worker provider adapter.

This adapter is intentionally thin: it consumes the existing provider-neutral
external worker task package, invokes the existing OpenAI provider adapter, and
returns the existing external worker result package shape.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.external_worker_adapter_runtime import (
    EXTERNAL_WORKER_RESULT_PACKAGE_V1,
    EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
    EXTERNAL_WORKER_TASK_PACKAGE_V1,
    create_external_worker_result_package,
)
from aigol.runtime.governed_worker_execution_runtime import WORKER_EXECUTION_COMPLETED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.openai_provider_adapter import (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
    GOVERNED_RESULT_RETURNED,
    OpenAIClient,
    invoke_openai_provider_adapter,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION = "AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"
OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1 = "OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1"
OPENAI_EXTERNAL_WORKER_PROVIDER_RETURNED_ARTIFACT_V1 = "OPENAI_EXTERNAL_WORKER_PROVIDER_RETURNED_ARTIFACT_V1"
OPENAI_EXTERNAL_WORKER_COMPLETED = "OPENAI_EXTERNAL_WORKER_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "openai_external_worker_task_recorded",
    "openai_provider_adapter_recorded",
    "openai_external_worker_result_recorded",
    "openai_external_worker_returned",
)


def run_openai_external_worker_provider_adapter(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
    replay_dir: str | Path,
    openai_client: OpenAIClient | None = None,
    api_key: str | None = None,
    model: str = DEFAULT_OPENAI_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Consume EXTERNAL_WORKER_TASK_PACKAGE_V1 and return EXTERNAL_WORKER_RESULT_PACKAGE_V1."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        task = deepcopy(task_package_artifact)
        _validate_task_package(task)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], task)

        provider_capture = invoke_openai_provider_adapter(
            adapter_id=f"{task['task_id']}:OPENAI",
            human_request=_provider_prompt(task),
            created_at=completed_at,
            replay_dir=replay_path / "openai_provider_adapter",
            openai_client=openai_client,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
        provider_artifact = _provider_capture_artifact(
            task=task,
            provider_capture=provider_capture,
            captured_at=completed_at,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], provider_artifact)
        if provider_artifact["provider_status"] != "COMPLETED":
            raise FailClosedRuntimeError(provider_artifact["failure_reason"] or "OpenAI provider failed closed")

        result_package = create_external_worker_result_package(
            result_id=result_id,
            task_package_artifact=task,
            worker_result_payload=_worker_result_payload(task, provider_artifact),
            worker_evidence=_worker_evidence(task, provider_artifact),
            execution_logs=[
                "external worker task package consumed",
                "existing OpenAI provider adapter invoked",
                "OpenAI response captured as untrusted provider evidence",
                "external worker result package generated",
                "no repository mutation performed by provider adapter",
                "no command execution performed by provider adapter",
            ],
            completed_at=completed_at,
        )
        returned = _returned_artifact(result_package, provider_artifact, failure_reason=None)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], result_package)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(
            task=task,
            provider_artifact=provider_artifact,
            result_package=result_package,
            returned=returned,
            replay_path=replay_path,
        )
    except Exception as exc:
        result_package = _failed_result_package(
            result_id=result_id,
            task_package_artifact=task_package_artifact,
            completed_at=completed_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(result_package, None, failure_reason=result_package["failure_reason"])
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], result_package)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(
            task=task_package_artifact,
            provider_artifact=None,
            result_package=result_package,
            returned=returned,
            replay_path=replay_path,
        )


def reconstruct_openai_external_worker_provider_adapter_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate OpenAI external worker adapter replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OpenAI external worker adapter replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OpenAI external worker adapter replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    task = wrappers[0]["artifact"]
    provider = wrappers[1]["artifact"]
    result = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if provider.get("task_package_hash") != task["artifact_hash"]:
        raise FailClosedRuntimeError("OpenAI external worker provider task hash mismatch")
    if result.get("task_package_hash") != task["artifact_hash"]:
        raise FailClosedRuntimeError("OpenAI external worker result task hash mismatch")
    if returned.get("external_worker_result_package_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("OpenAI external worker returned result hash mismatch")
    return {
        "task_id": task["task_id"],
        "result_id": result["result_id"],
        "adapter_status": returned["adapter_status"],
        "provider_status": provider["provider_status"],
        "task_package_consumed": returned["task_package_consumed"],
        "openai_provider_connected": provider["provider_status"] == "COMPLETED",
        "result_package_generated": result["artifact_type"] == EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "replay_lineage_preserved": returned["replay_lineage_preserved"],
        "fail_closed_preserved": returned["fail_closed_preserved"],
        "provider_neutrality_above_adapter_preserved": returned["provider_neutrality_above_adapter_preserved"],
        "ready_for_external_worker_adapter_runtime": returned["ready_for_external_worker_adapter_runtime"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_task_package(task: dict[str, Any]) -> None:
    _verify_artifact_hash(task)
    if task.get("artifact_type") != EXTERNAL_WORKER_TASK_PACKAGE_V1:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: invalid task package type")
    if task.get("task_status") != EXTERNAL_WORKER_TASK_PACKAGE_CREATED:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: task package not ready")
    if task.get("provider_neutral") is not True or task.get("provider_specific_logic_used") is not False:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: task package neutrality invalid")
    authorization = task.get("worker_authorization")
    if not isinstance(authorization, dict) or authorization.get("authorized") is not True:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: worker authorization missing")
    capabilities = authorization.get("capabilities")
    if not isinstance(capabilities, list) or "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1" not in capabilities:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: worker task capability missing")
    if "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1" not in capabilities:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: worker result capability missing")
    scope = task.get("execution_scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("execution_objective"), str):
        raise FailClosedRuntimeError("OpenAI external worker failed closed: execution scope invalid")
    if scope.get("implementation_result_creation_allowed") is not False:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: implementation boundary invalid")
    if task.get("replay_lineage_preserved") is not True or task.get("certification_integrity_preserved") is not True:
        raise FailClosedRuntimeError("OpenAI external worker failed closed: lineage or certification invalid")


def _provider_prompt(task: dict[str, Any]) -> str:
    objective = " ".join(task["execution_scope"]["execution_objective"].split())
    return (
        "Return a concise proposal-only external worker result. "
        "Do not claim authority, do not execute commands, and do not modify files. "
        f"Task id: {task['task_id']}. Execution objective: {objective}"
    )


def _provider_capture_artifact(
    *,
    task: dict[str, Any],
    provider_capture: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    governed_result = provider_capture.get("governed_result") if isinstance(provider_capture, dict) else None
    raw_response = provider_capture.get("raw_provider_response") if isinstance(provider_capture, dict) else None
    if not isinstance(governed_result, dict):
        raise FailClosedRuntimeError("OpenAI external worker failed closed: OpenAI governed result missing")
    provider_status = governed_result.get("final_status")
    raw_text = raw_response.get("raw_provider_response") if isinstance(raw_response, dict) else None
    artifact = {
        "artifact_type": OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1,
        "runtime_version": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
        "task_id": task["task_id"],
        "task_package_hash": task["artifact_hash"],
        "provider_id": "openai",
        "provider_adapter_runtime": "OPENAI_PROVIDER_ADAPTER_V1",
        "provider_status": provider_status if isinstance(provider_status, str) else FAILED_CLOSED,
        "provider_governed_result_hash": governed_result.get("artifact_hash"),
        "raw_provider_response_hash": raw_response.get("artifact_hash") if isinstance(raw_response, dict) else None,
        "raw_provider_response_text_hash": replay_hash(raw_text) if isinstance(raw_text, str) else None,
        "raw_provider_response_text": raw_text if isinstance(raw_text, str) else "",
        "provider_capture": deepcopy(provider_capture),
        "provider_invoked_inside_adapter": True,
        "provider_authority": False,
        "provider_output_authoritative": False,
        "provider_neutrality_above_adapter_preserved": True,
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "captured_at": _require_string(captured_at, "captured_at"),
        "failure_reason": governed_result.get("failure_reason"),
    }
    if artifact["provider_status"] != "COMPLETED" and not artifact["failure_reason"]:
        artifact["failure_reason"] = "OpenAI provider failed closed"
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_result_payload(task: dict[str, Any], provider_artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "payload_type": "OPENAI_EXTERNAL_WORKER_PAYLOAD_V1",
        "task_id": task["task_id"],
        "source_execution_candidate": task["source_execution_candidate"],
        "proposal_authority": "PROPOSAL_ONLY",
        "execution_objective": task["execution_scope"]["execution_objective"],
        "provider_id": "openai",
        "provider_response_text": provider_artifact["raw_provider_response_text"],
        "provider_response_text_hash": provider_artifact["raw_provider_response_text_hash"],
        "provider_capture_hash": provider_artifact["artifact_hash"],
        "patch_proposals": [],
        "file_proposals": [],
        "test_proposals": [],
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "provider_output_authoritative": False,
        "provider_neutral_above_adapter": True,
        "certification_compatible": True,
        "replay_compatible": True,
    }


def _worker_evidence(task: dict[str, Any], provider_artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "worker_runtime": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
        "worker_id": "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1",
        "task_id": task["task_id"],
        "task_package_hash": task["artifact_hash"],
        "provider_id": "openai",
        "provider_adapter_runtime": provider_artifact["provider_adapter_runtime"],
        "provider_capture_hash": provider_artifact["artifact_hash"],
        "provider_governed_result_hash": provider_artifact["provider_governed_result_hash"],
        "raw_provider_response_hash": provider_artifact["raw_provider_response_hash"],
        "provider_invoked_inside_adapter": True,
        "provider_authority": False,
        "provider_output_authoritative": False,
        "provider_neutral_contract": True,
        "repository_mutation_performed": False,
        "command_execution_performed": False,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
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
        "runtime_version": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
        "result_id": result_id if isinstance(result_id, str) and result_id.strip() else "INVALID",
        "task_id": task_package_artifact.get("task_id") if isinstance(task_package_artifact, dict) else None,
        "task_package_hash": task_package_artifact.get("artifact_hash") if isinstance(task_package_artifact, dict) else None,
        "source_execution_candidate": task_package_artifact.get("source_execution_candidate")
        if isinstance(task_package_artifact, dict)
        else None,
        "source_execution_candidate_hash": task_package_artifact.get("source_execution_candidate_hash")
        if isinstance(task_package_artifact, dict)
        else None,
        "worker_interface": (
            task_package_artifact.get("worker_authorization", {}).get("worker_interface")
            if isinstance(task_package_artifact, dict)
            else None
        ),
        "execution_status": FAILED_CLOSED,
        "execution_outcome": FAILED_CLOSED,
        "worker_result_payload": {},
        "worker_result_payload_hash": replay_hash({}),
        "worker_evidence": {
            "worker_runtime": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
            "provider_id": "openai",
            "provider_authority": False,
            "repository_mutation_performed": False,
            "command_execution_performed": False,
        },
        "worker_evidence_hash": replay_hash(
            {
                "worker_runtime": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
                "provider_id": "openai",
                "provider_authority": False,
                "repository_mutation_performed": False,
                "command_execution_performed": False,
            }
        ),
        "execution_logs": ["OpenAI external worker provider adapter failed closed"],
        "completed_at": completed_at if isinstance(completed_at, str) else None,
        "provider_neutral": True,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(
    result_package: dict[str, Any],
    provider_artifact: dict[str, Any] | None,
    *,
    failure_reason: str | None,
) -> dict[str, Any]:
    completed = result_package.get("execution_status") == WORKER_EXECUTION_COMPLETED and failure_reason is None
    artifact = {
        "artifact_type": OPENAI_EXTERNAL_WORKER_PROVIDER_RETURNED_ARTIFACT_V1,
        "runtime_version": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
        "adapter_status": OPENAI_EXTERNAL_WORKER_COMPLETED if completed else FAILED_CLOSED,
        "external_worker_result_package": result_package.get("result_id"),
        "external_worker_result_package_hash": result_package.get("artifact_hash"),
        "provider_capture_hash": provider_artifact.get("artifact_hash") if isinstance(provider_artifact, dict) else None,
        "task_package_consumed": completed,
        "result_package_generated": result_package.get("artifact_type") == EXTERNAL_WORKER_RESULT_PACKAGE_V1,
        "openai_provider_connected": completed,
        "replay_lineage_preserved": completed,
        "fail_closed_preserved": True,
        "provider_neutrality_above_adapter_preserved": True,
        "ready_for_external_worker_adapter_runtime": completed,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    task: dict[str, Any],
    provider_artifact: dict[str, Any] | None,
    result_package: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_VERSION,
        "worker_status": returned["adapter_status"],
        "source_task_package": task.get("task_id") if isinstance(task, dict) else None,
        "openai_provider_capture_artifact": deepcopy(provider_artifact),
        "external_worker_result_package": deepcopy(result_package),
        "openai_external_worker_returned_artifact": deepcopy(returned),
        "openai_external_worker_replay_reference": str(replay_path),
        "openai_provider_connected": returned["openai_provider_connected"],
        "task_package_consumed": returned["task_package_consumed"],
        "result_package_generated": returned["result_package_generated"],
        "replay_lineage_preserved": returned["replay_lineage_preserved"],
        "fail_closed_preserved": returned["fail_closed_preserved"],
        "provider_neutrality_above_adapter_preserved": returned["provider_neutrality_above_adapter_preserved"],
        "ready_for_external_worker_adapter_runtime": returned["ready_for_external_worker_adapter_runtime"],
        "ready_for_first_real_openai_worker_execution": returned["ready_for_external_worker_adapter_runtime"],
        "failure_reason": returned["failure_reason"],
    }
    capture["openai_external_worker_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("OpenAI external worker failed closed: replay already exists")


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
        raise FailClosedRuntimeError("OpenAI external worker artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("OpenAI external worker artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("OpenAI external worker replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("OpenAI external worker replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"OpenAI external worker failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OpenAI external worker provider adapter failed closed"
