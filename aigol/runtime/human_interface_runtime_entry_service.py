"""Canonical Human Interface Runtime Entry Service.

The service is the shared Platform Core entry boundary for human interfaces.
Interfaces collect human input and approval, then delegate the composed request
here. The service restores Platform Core project context, resolves development
intent, and enters the certified governed conversation runtime through an
injected runner supplied by the embedding interface.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
)


CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_VERSION = (
    "G14_30_CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_V1"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED"
)


GovernedRuntimeRunner = Callable[..., dict[str, Any]]


def run_human_interface_runtime_entry(
    *,
    interface_name: str,
    session_id: str,
    human_requests: list[str],
    created_at: str,
    runtime_root: str | Path,
    workspace: str | Path,
    governed_runtime_runner: GovernedRuntimeRunner,
    presentation: dict[str, Any] | None = None,
    operator_context: str = "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
) -> dict[str, Any]:
    """Enter the certified runtime from any Unified Human Interface."""

    interface = _require_string(interface_name, "interface_name")
    session = _require_string(session_id, "session_id")
    created = _require_string(created_at, "created_at")
    root = Path(runtime_root)
    workspace_text = str(Path(workspace))
    requests = [_require_string(request, "human_request") for request in human_requests]

    result = deepcopy(presentation) if isinstance(presentation, dict) else {}
    project_contexts = [
        prepare_unified_human_interface_project_context(
            interface_name=interface,
            session_id=session,
            message=request,
            runtime_root=root,
            workspace=workspace_text,
            created_at=created,
        )
        for request in requests
    ]
    intent_resolutions = [
        context["development_intent_resolution"]
        for context in project_contexts
        if isinstance(context.get("development_intent_resolution"), dict)
    ]
    runtime_prompts = [
        str(resolution.get("canonical_runtime_prompt") or request)
        for request, resolution in zip(requests, intent_resolutions)
        if resolution.get("runtime_binding_admissible") is True
    ]
    read_only_work_results = [
        context.get("governed_read_only_work_result")
        for context in project_contexts
        if isinstance(context.get("governed_read_only_work_result"), dict)
    ]

    result.update(
        {
            "canonical_runtime_entry_service_version": (
                CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_VERSION
            ),
            "canonical_runtime_entry_interface": interface,
            "canonical_runtime_entry_session_id": session,
            "canonical_runtime_entry_workspace": workspace_text,
            "platform_core_project_services_contexts": project_contexts,
            "platform_core_project_services_context": project_contexts[-1] if project_contexts else None,
            "development_intent_resolutions": intent_resolutions,
            "development_intent_resolution": intent_resolutions[-1] if intent_resolutions else None,
            "runtime_prompts": runtime_prompts,
            "read_only_work_results": read_only_work_results,
            "governed_read_only_work_result": (
                read_only_work_results[-1] if read_only_work_results else None
            ),
            "read_only_runtime_entered": bool(read_only_work_results),
            "read_only_work_binding_status": (
                read_only_work_results[-1].get("binding_status")
                if read_only_work_results
                else None
            ),
            "human_interface_runtime_entry_service_used": True,
            "human_interface_runtime_entry_orchestrates": False,
            "platform_core_project_services_delegated": True,
            "platform_core_runtime_delegated": True,
            "manual_chatgpt_codex_transfer_required": False,
        }
    )

    if not runtime_prompts:
        result.update(
            {
                "canonical_runtime_entry_status": (
                    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED
                ),
                "runtime_binding_status": CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
                "runtime_entered": False,
                "runtime_turn_count": 0,
                "runtime_failed_turns": 0,
                "governance_authorization_reached": None,
                "provider_invocation_reached": None,
                "worker_execution_reached": None,
                "replay_certification_reached": None,
            }
        )
        workspace_state = record_unified_human_interface_workspace_state(
            interface_name=interface,
            session_id=session,
            runtime_root=root,
            workspace=workspace_text,
            created_at=created,
            completion=result,
            turn_results=[],
            pending_clarification=None,
            pending_summary=None,
        )
        result["project_workspace_replay_reference"] = workspace_state["replay_reference"]
        result["project_workspace_hash"] = workspace_state["artifact_hash"]
        return result

    conversation_args = argparse.Namespace(
        session_id=session,
        created_at=created,
        runtime_root=str(root),
        workspace=workspace_text,
        operator_context=operator_context,
        auto_continue=True,
        enable_llm_assisted_explanation=False,
        llm_explanation_provider_id="UNSPECIFIED_EXPLANATION_PROVIDER",
    )
    conversation_output: list[str] = []
    conversation_result = governed_runtime_runner(
        conversation_args,
        input_func=_input_sequence([*runtime_prompts, "exit"]),
        output_func=conversation_output.append,
    )
    latest_turn = _latest_turn(conversation_result)
    runtime_projection = _runtime_status_projection(conversation_result, latest_turn)
    runtime_bound = _runtime_bound(conversation_result, runtime_projection)
    canonical_status = (
        CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
        if runtime_bound
        else CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND
    )
    result.update(
        {
            "canonical_runtime_entry_status": canonical_status,
            "runtime_binding_status": canonical_status,
            "runtime_entered": True,
            "runtime_command": conversation_result.get("command"),
            "runtime_root": conversation_result.get("runtime_root"),
            "runtime_turn_count": conversation_result.get("turn_count"),
            "runtime_failed_turns": conversation_result.get("failed_turns"),
            "runtime_exit_reason": conversation_result.get("exit_reason"),
            "runtime_response_source": latest_turn.get("response_source"),
            "runtime_response_status": latest_turn.get("response_status"),
            "auto_continue_enabled": conversation_result.get("auto_continue_enabled") is True,
            "auto_continue_stop_reason": conversation_result.get("auto_continue_stop_reason"),
            "manual_chatgpt_codex_transfer_required": not runtime_bound,
            "execution_summary_presented": bool(latest_turn.get("execution_summary_reference")),
            "human_confirmation_presented": bool(latest_turn.get("human_confirmation_reference")),
            "governance_authorization_reached": latest_turn.get("execution_authorization_status")
            == "EXECUTION_AUTHORIZED",
            "provider_invocation_reached": runtime_projection["provider_invocation_reached"],
            "worker_execution_reached": runtime_projection["worker_execution_reached"],
            "replay_certification_reached": runtime_projection["replay_certification_reached"],
            "runtime_status_projection_source": runtime_projection["projection_source"],
            "runtime_status_projection_evidence": runtime_projection["projection_evidence"],
            "execution_plan_generated": latest_turn.get("execution_preparation_status") == "EXECUTION_READY",
            "execution_plan_status": latest_turn.get("execution_preparation_status"),
            "worker_assignment_status": latest_turn.get("worker_assignment_status"),
            "worker_dispatch_status": latest_turn.get("worker_dispatch_status"),
            "worker_invocation_status": latest_turn.get("worker_invocation_status"),
            "worker_execution_candidate_reached": latest_turn.get("worker_execution_candidate_reached") is True,
            "external_task_package_reached": latest_turn.get("external_task_package_reached") is True,
            "openai_provider_reached": latest_turn.get("openai_provider_reached") is True,
            "universal_provider_runtime_reached": runtime_projection["universal_provider_runtime_reached"],
            "smart_provider_selection_reached": runtime_projection["smart_provider_selection_reached"],
            "universal_provider_worker_status": latest_turn.get("universal_provider_worker_status"),
            "universal_provider_worker_replay_reference": latest_turn.get(
                "universal_provider_worker_replay_reference"
            ),
            "selected_provider_resource_id": latest_turn.get("selected_provider_resource_id"),
            "smart_provider_selection_executed": latest_turn.get("smart_provider_selection_executed"),
            "result_validation_status": latest_turn.get("result_validation_status"),
            "replay_certification_status": latest_turn.get("replay_certification_status"),
            "replay_certification_replay_reference": latest_turn.get("replay_certification_replay_reference"),
            "execution_summary_reference": latest_turn.get("execution_summary_reference"),
            "human_confirmation_reference": latest_turn.get("human_confirmation_reference"),
            "runtime_replay_reference": latest_turn.get("replay_reference")
            or latest_turn.get("conversation_replay_reference"),
            "conversation_output_tail": conversation_output[-12:],
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }
    )
    workspace_state = record_unified_human_interface_workspace_state(
        interface_name=interface,
        session_id=session,
        runtime_root=root,
        workspace=workspace_text,
        created_at=created,
        completion=result,
        turn_results=[result],
        pending_clarification=None,
        pending_summary=None,
    )
    result["project_workspace_replay_reference"] = workspace_state["replay_reference"]
    result["project_workspace_hash"] = workspace_state["artifact_hash"]
    return result


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        try:
            return next(iterator)
        except StopIteration:
            return "exit"

    return read


def _latest_turn(conversation_result: dict[str, Any]) -> dict[str, Any]:
    turns = conversation_result.get("turns")
    if not isinstance(turns, list):
        return {}
    for turn in reversed(turns):
        if isinstance(turn, dict):
            return turn
    return {}


def _runtime_bound(conversation_result: dict[str, Any], projection: dict[str, Any]) -> bool:
    return (
        conversation_result.get("failed_turns") == 0
        and projection.get("provider_invocation_reached") is True
        and projection.get("worker_execution_reached") is True
        and projection.get("replay_certification_reached") is True
    )


def _runtime_status_projection(
    conversation_result: dict[str, Any],
    latest_turn: dict[str, Any],
) -> dict[str, Any]:
    """Project certified runtime status from latest-turn fields and replay evidence."""

    turn_replay_root = _discover_turn_replay_root(latest_turn)
    worker_lifecycle_root = (
        turn_replay_root
        / "governed_bridge_certified_development_continuation"
        / "worker_lifecycle_continuation"
        if turn_replay_root is not None
        else None
    )
    worker_invocation_artifact = _read_replay_artifact_path(
        worker_lifecycle_root / "worker_invocation" / "003_invocation_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    universal_worker_binding_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "000_universal_provider_worker_binding_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    universal_worker_artifact = _read_replay_artifact(
        latest_turn.get("universal_provider_worker_replay_reference"),
        "001_universal_provider_worker_result_recorded.json",
    ) or _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "001_universal_provider_worker_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    resource_selection_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "universal_resource_selection"
        / "001_resource_selection_returned.json"
        if worker_lifecycle_root is not None
        else None
    )
    selected_provider_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "001_openai_provider_adapter_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    openai_worker_result_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "002_openai_external_worker_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    certified_provider_attachment_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "certified_provider_attachment"
        / "002_certified_provider_attachment_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    replay_certification_artifact = _read_replay_artifact(
        latest_turn.get("replay_certification_replay_reference"),
        "000_replay_certification_artifact_recorded.json",
    ) or _read_replay_artifact_path(
        worker_lifecycle_root / "replay_certification" / "000_replay_certification_artifact_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )

    universal_provider_completed = (
        latest_turn.get("universal_provider_worker_status") == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
        or universal_worker_artifact.get("universal_provider_worker_status")
        == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
        or universal_worker_binding_artifact.get("binding_status") == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
    )
    smart_selection_reached = (
        latest_turn.get("smart_provider_selection_executed") is True
        or latest_turn.get("smart_provider_selection_reached") is True
        or universal_worker_artifact.get("smart_selection_executed") is True
        or universal_worker_binding_artifact.get("smart_selection_executed") is True
        or resource_selection_artifact.get("selection_status") == "RESOURCE_SELECTION_SUCCEEDED"
    )
    universal_provider_reached = (
        latest_turn.get("universal_provider_runtime_reached") is True
        or universal_provider_completed
        or bool(universal_worker_artifact)
        or bool(universal_worker_binding_artifact)
        or bool(resource_selection_artifact)
        or bool(selected_provider_artifact)
    )
    provider_invocation_reached = (
        latest_turn.get("openai_provider_reached") is True
        or latest_turn.get("provider_invoked") is True
        or latest_turn.get("provider_invocation_reached") is True
        or universal_provider_reached
        or universal_worker_artifact.get("provider_invocation_delegated") is True
        or universal_worker_artifact.get("certified_provider_attachment_reused") is True
        or selected_provider_artifact.get("provider_invoked_inside_adapter") is True
        or bool(openai_worker_result_artifact)
        or bool(certified_provider_attachment_artifact)
    )
    worker_execution_reached = (
        latest_turn.get("worker_invoked") is True
        or latest_turn.get("worker_invocation_reached") is True
        or latest_turn.get("worker_execution_candidate_reached") is True
        or latest_turn.get("external_task_package_reached") is True
        or latest_turn.get("worker_invocation_status") == "WORKER_INVOKED"
        or worker_invocation_artifact.get("worker_invoked") is True
        or worker_invocation_artifact.get("invocation_status") == "WORKER_INVOKED"
        or universal_provider_completed
    )
    replay_certification_reached = (
        latest_turn.get("replay_certification_reached") is True
        or latest_turn.get("replay_certification_status") == "REPLAY_CERTIFICATION_COMPLETED"
        or replay_certification_artifact.get("certification_status") == "REPLAY_CERTIFICATION_COMPLETED"
    )
    projection_evidence = {
        "latest_turn_used": bool(latest_turn),
        "turn_replay_discovery_used": turn_replay_root is not None,
        "turn_replay_root": str(turn_replay_root) if turn_replay_root is not None else None,
        "worker_lifecycle_replay_root": (
            str(worker_lifecycle_root) if worker_lifecycle_root is not None else None
        ),
        "worker_invocation_replay_inspected": bool(worker_invocation_artifact),
        "universal_provider_worker_binding_replay_inspected": bool(universal_worker_binding_artifact),
        "universal_provider_worker_replay_inspected": bool(universal_worker_artifact),
        "resource_selection_replay_inspected": bool(resource_selection_artifact),
        "selected_provider_replay_inspected": bool(selected_provider_artifact),
        "openai_worker_result_replay_inspected": bool(openai_worker_result_artifact),
        "certified_provider_attachment_replay_inspected": bool(certified_provider_attachment_artifact),
        "replay_certification_replay_inspected": bool(replay_certification_artifact),
        "conversation_failed_turns": conversation_result.get("failed_turns"),
        "worker_invocation_status": (
            latest_turn.get("worker_invocation_status")
            or worker_invocation_artifact.get("invocation_status")
        ),
        "universal_provider_worker_binding_status": universal_worker_binding_artifact.get("binding_status"),
        "universal_provider_worker_status": (
            latest_turn.get("universal_provider_worker_status")
            or universal_worker_artifact.get("universal_provider_worker_status")
        ),
        "selected_provider_resource_id": (
            latest_turn.get("selected_provider_resource_id")
            or universal_worker_artifact.get("selected_resource_id")
            or universal_worker_binding_artifact.get("selected_resource_id")
            or resource_selection_artifact.get("selected_resource_id")
        ),
        "resource_selection_status": resource_selection_artifact.get("selection_status"),
        "selected_provider_status": selected_provider_artifact.get("provider_status"),
        "certified_provider_attachment_status": certified_provider_attachment_artifact.get("provider_status"),
        "replay_certification_status": (
            latest_turn.get("replay_certification_status")
            or replay_certification_artifact.get("certification_status")
        ),
    }
    return {
        "provider_invocation_reached": provider_invocation_reached,
        "worker_execution_reached": worker_execution_reached,
        "replay_certification_reached": replay_certification_reached,
        "universal_provider_runtime_reached": universal_provider_reached,
        "smart_provider_selection_reached": smart_selection_reached,
        "projection_source": "LATEST_TURN_AND_REPLAY_EVIDENCE",
        "projection_evidence": projection_evidence,
    }


def _read_replay_artifact(replay_reference: Any, filename: str) -> dict[str, Any]:
    if not isinstance(replay_reference, str) or not replay_reference.strip():
        return {}
    return _read_replay_artifact_path(Path(replay_reference) / filename)


def _read_replay_artifact_path(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists() or not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            wrapper = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    artifact = wrapper.get("artifact") if isinstance(wrapper, dict) else None
    return deepcopy(artifact) if isinstance(artifact, dict) else {}


def _discover_turn_replay_root(latest_turn: dict[str, Any]) -> Path | None:
    for candidate in _turn_replay_candidates(latest_turn):
        discovered = _nearest_turn_replay_root(candidate)
        if discovered is not None:
            return discovered
    return None


def _turn_replay_candidates(latest_turn: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    for field_name in (
        "replay_reference",
        "conversation_replay_reference",
        "runtime_replay_reference",
        "universal_provider_worker_replay_reference",
        "replay_certification_replay_reference",
        "execution_summary_reference",
        "human_confirmation_reference",
    ):
        value = latest_turn.get(field_name)
        if isinstance(value, str) and value.strip():
            candidates.append(Path(value))
    return candidates


def _nearest_turn_replay_root(path: Path) -> Path | None:
    current = path if path.suffix == "" else path.parent
    search_path = [current, *current.parents]
    for candidate in search_path:
        if candidate.name.startswith("TURN-"):
            return candidate
        if _looks_like_turn_replay_root(candidate):
            return candidate
    return None


def _looks_like_turn_replay_root(path: Path) -> bool:
    return (
        path.exists()
        and path.is_dir()
        and (
            (path / "governed_bridge_certified_development_continuation").exists()
            or (path / "source_router").exists()
            or (path / "turn_completion").exists()
        )
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()
