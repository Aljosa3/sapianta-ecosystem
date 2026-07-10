"""Universal Provider Runtime binding for external Worker provider execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.openai_external_worker_provider_adapter import run_openai_external_worker_provider_adapter
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_REQUIRED
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import (
    PROVIDER_ROLE,
    RESOURCE_SELECTION_SUCCEEDED,
    select_unified_resource,
)


UNIVERSAL_PROVIDER_WORKER_RUNTIME_VERSION = "G18_03_UNIVERSAL_PROVIDER_WORKER_RUNTIME_V1"
UNIVERSAL_PROVIDER_WORKER_INTERFACE = "UNIVERSAL_PROVIDER_WORKER_RUNTIME_V1"
UNIVERSAL_PROVIDER_WORKER_COMPLETED = "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
OPENAI_RESOURCE_ID = "OPENAI"

REPLAY_STEPS = (
    "universal_provider_worker_binding_recorded",
    "universal_provider_worker_result_recorded",
)


def run_universal_provider_worker_runtime(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
    replay_dir: str | Path,
    openai_client: Any | None = None,
    api_key: str | None = None,
    model: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Route external Worker provider execution through certified provider selection."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        task = deepcopy(task_package_artifact)
        selection_capture = select_unified_resource(
            selection_id=f"{_task_id(task)}:UNIVERSAL-PROVIDER-SELECTION",
            workflow_type="NATIVE_DEVELOPMENT",
            required_capability="PROPOSAL_GENERATION",
            requested_role_type=PROVIDER_ROLE,
            domain_id="NATIVE_DEVELOPMENT",
            provider_necessity_classification=PROVIDER_REQUIRED,
            min_trust_level="STANDARD",
            created_at=completed_at,
            replay_dir=replay_path / "universal_resource_selection",
            context_assembly_output={
                "external_worker_task_id": _task_id(task),
                "external_worker_task_hash": task.get("artifact_hash") if isinstance(task, dict) else None,
                "provider_consumer": UNIVERSAL_PROVIDER_WORKER_INTERFACE,
            },
        )
        selection = _selection_artifact(selection_capture)
        if selection.get("selection_status") != RESOURCE_SELECTION_SUCCEEDED:
            raise FailClosedRuntimeError(selection.get("failure_reason") or "universal provider selection failed closed")
        binding = _binding_artifact(
            task=task,
            selection=selection,
            completed_at=completed_at,
            replay_path=replay_path,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], binding)
        provider_capture = _invoke_selected_provider(
            selected_resource_id=str(selection.get("selected_resource_id") or ""),
            result_id=result_id,
            task_package_artifact=task,
            completed_at=completed_at,
            replay_path=replay_path,
            openai_client=openai_client,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
        result = _result_artifact(
            binding=binding,
            provider_capture=provider_capture,
            completed_at=completed_at,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(
            binding=binding,
            result=result,
            provider_capture=provider_capture,
            selection_capture=selection_capture,
            replay_path=replay_path,
        )
    except Exception as exc:
        result = _failed_result_artifact(
            result_id=result_id,
            task_package_artifact=task_package_artifact,
            completed_at=completed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(
            binding={},
            result=result,
            provider_capture={},
            selection_capture=locals().get("selection_capture", {}),
            replay_path=replay_path,
        )


def _selection_artifact(selection_capture: dict[str, Any]) -> dict[str, Any]:
    selection = selection_capture.get("resource_selection_artifact")
    if not isinstance(selection, dict):
        raise FailClosedRuntimeError("universal provider worker failed closed: resource selection missing")
    return selection


def _invoke_selected_provider(
    *,
    selected_resource_id: str,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
    replay_path: Path,
    openai_client: Any | None,
    api_key: str | None,
    model: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    if selected_resource_id == OPENAI_RESOURCE_ID:
        return run_openai_external_worker_provider_adapter(
            result_id=result_id,
            task_package_artifact=task_package_artifact,
            completed_at=completed_at,
            replay_dir=replay_path / "selected_provider_openai",
            openai_client=openai_client,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
    raise FailClosedRuntimeError(f"universal provider worker failed closed: selected provider {selected_resource_id} is not bound")


def _binding_artifact(
    *,
    task: dict[str, Any],
    selection: dict[str, Any],
    completed_at: str,
    replay_path: Path,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "UNIVERSAL_PROVIDER_WORKER_BINDING_ARTIFACT_V1",
        "runtime_version": UNIVERSAL_PROVIDER_WORKER_RUNTIME_VERSION,
        "binding_status": UNIVERSAL_PROVIDER_WORKER_COMPLETED if failure_reason is None else FAILED_CLOSED,
        "task_id": _task_id(task),
        "task_package_hash": task.get("artifact_hash") if isinstance(task, dict) else None,
        "selected_resource_id": selection.get("selected_resource_id"),
        "selected_resource_category": selection.get("selected_resource_category"),
        "selected_role_type": selection.get("selected_role_type"),
        "required_capability": selection.get("required_capability"),
        "selection_reference": selection.get("selection_id"),
        "selection_hash": selection.get("artifact_hash"),
        "selection_replay_reference": str(replay_path / "universal_resource_selection"),
        "smart_selection_executed": True,
        "universal_provider_runtime_reached": True,
        "provider_consumer": UNIVERSAL_PROVIDER_WORKER_INTERFACE,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authority": False,
        "replay_visible": True,
        "created_at": completed_at,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result_artifact(
    *,
    binding: dict[str, Any],
    provider_capture: dict[str, Any],
    completed_at: str,
) -> dict[str, Any]:
    completed = provider_capture.get("openai_provider_connected") is True
    artifact = {
        "artifact_type": "UNIVERSAL_PROVIDER_WORKER_RESULT_ARTIFACT_V1",
        "runtime_version": UNIVERSAL_PROVIDER_WORKER_RUNTIME_VERSION,
        "binding_hash": binding["artifact_hash"],
        "selected_resource_id": binding.get("selected_resource_id"),
        "provider_worker_status": provider_capture.get("worker_status"),
        "external_worker_result_package_hash": provider_capture.get("external_worker_result_package", {}).get("artifact_hash")
        if isinstance(provider_capture.get("external_worker_result_package"), dict)
        else None,
        "universal_provider_worker_status": UNIVERSAL_PROVIDER_WORKER_COMPLETED if completed else FAILED_CLOSED,
        "smart_selection_executed": True,
        "provider_invocation_delegated": True,
        "certified_provider_attachment_reused": True,
        "escalation_executed": False,
        "multi_provider_runtime_executed": False,
        "replay_lineage_preserved": provider_capture.get("replay_lineage_preserved") is True,
        "fail_closed_preserved": provider_capture.get("fail_closed_preserved") is True,
        "completed_at": completed_at,
        "failure_reason": None if completed else provider_capture.get("failure_reason"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result_artifact(
    *,
    result_id: str,
    task_package_artifact: dict[str, Any],
    completed_at: str,
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "UNIVERSAL_PROVIDER_WORKER_RESULT_ARTIFACT_V1",
        "runtime_version": UNIVERSAL_PROVIDER_WORKER_RUNTIME_VERSION,
        "result_id": result_id if isinstance(result_id, str) and result_id.strip() else "INVALID_RESULT_ID",
        "task_id": _task_id(task_package_artifact),
        "task_package_hash": task_package_artifact.get("artifact_hash") if isinstance(task_package_artifact, dict) else None,
        "universal_provider_worker_status": FAILED_CLOSED,
        "universal_provider_worker_replay_reference": str(replay_path),
        "smart_selection_executed": False,
        "provider_invocation_delegated": False,
        "certified_provider_attachment_reused": False,
        "escalation_executed": False,
        "multi_provider_runtime_executed": False,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "completed_at": completed_at,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    binding: dict[str, Any],
    result: dict[str, Any],
    provider_capture: dict[str, Any],
    selection_capture: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    worker_status = (
        provider_capture.get("worker_status")
        if isinstance(provider_capture, dict) and provider_capture.get("worker_status")
        else result.get("universal_provider_worker_status")
    )
    capture = {
        "runtime_version": UNIVERSAL_PROVIDER_WORKER_RUNTIME_VERSION,
        "worker_status": worker_status,
        "universal_provider_worker_status": result.get("universal_provider_worker_status"),
        "universal_provider_runtime_reached": True,
        "smart_selection_executed": bool(binding),
        "resource_selection": deepcopy(selection_capture),
        "resource_selection_replay_reference": str(replay_path / "universal_resource_selection") if selection_capture else None,
        "selected_resource_id": binding.get("selected_resource_id"),
        "universal_provider_worker_binding_artifact": deepcopy(binding),
        "universal_provider_worker_result_artifact": deepcopy(result),
        "universal_provider_worker_replay_reference": str(replay_path),
        "provider_worker_capture": deepcopy(provider_capture),
        "openai_external_worker_provider": deepcopy(provider_capture),
        "external_worker_result_package": deepcopy(provider_capture.get("external_worker_result_package", {}))
        if isinstance(provider_capture, dict)
        else {},
        "openai_external_worker_replay_reference": provider_capture.get("openai_external_worker_replay_reference")
        if isinstance(provider_capture, dict)
        else None,
        "openai_provider_connected": provider_capture.get("openai_provider_connected") is True
        if isinstance(provider_capture, dict)
        else False,
        "task_package_consumed": provider_capture.get("task_package_consumed") is True
        if isinstance(provider_capture, dict)
        else False,
        "result_package_generated": provider_capture.get("result_package_generated") is True
        if isinstance(provider_capture, dict)
        else False,
        "replay_lineage_preserved": provider_capture.get("replay_lineage_preserved") is True
        if isinstance(provider_capture, dict)
        else False,
        "fail_closed_preserved": True,
        "provider_neutrality_above_adapter_preserved": provider_capture.get("provider_neutrality_above_adapter_preserved") is True
        if isinstance(provider_capture, dict)
        else False,
        "ready_for_external_worker_adapter_runtime": provider_capture.get("ready_for_external_worker_adapter_runtime") is True
        if isinstance(provider_capture, dict)
        else False,
        "ready_for_first_real_openai_worker_execution": provider_capture.get("ready_for_first_real_openai_worker_execution") is True
        if isinstance(provider_capture, dict)
        else False,
        "failure_reason": result.get("failure_reason") or provider_capture.get("failure_reason")
        if isinstance(provider_capture, dict)
        else result.get("failure_reason"),
    }
    capture["universal_provider_worker_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("universal provider worker failed closed: replay already exists")


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


def _task_id(task: Any) -> str:
    if isinstance(task, dict) and isinstance(task.get("task_id"), str) and task["task_id"].strip():
        return task["task_id"].strip()
    return "UNIVERSAL-PROVIDER-WORKER-TASK-UNKNOWN"


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "universal provider worker failed closed"
