"""Canonical Human Interface Runtime Entry Service.

The service is the shared Platform Core entry boundary for human interfaces.
Interfaces collect human input and approval, then delegate the composed request
here. The service restores Platform Core project context, resolves development
intent, and enters the certified governed conversation runtime through an
injected runner supplied by the embedding interface.
"""

from __future__ import annotations

import argparse
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
    runtime_bound = _runtime_bound(conversation_result, latest_turn)
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
            "provider_invocation_reached": latest_turn.get("openai_provider_reached") is True
            or latest_turn.get("provider_invoked") is True,
            "worker_execution_reached": latest_turn.get("worker_invoked") is True,
            "replay_certification_reached": latest_turn.get("replay_certification_reached") is True,
            "execution_plan_generated": latest_turn.get("execution_preparation_status") == "EXECUTION_READY",
            "execution_plan_status": latest_turn.get("execution_preparation_status"),
            "worker_assignment_status": latest_turn.get("worker_assignment_status"),
            "worker_dispatch_status": latest_turn.get("worker_dispatch_status"),
            "worker_invocation_status": latest_turn.get("worker_invocation_status"),
            "worker_execution_candidate_reached": latest_turn.get("worker_execution_candidate_reached") is True,
            "external_task_package_reached": latest_turn.get("external_task_package_reached") is True,
            "openai_provider_reached": latest_turn.get("openai_provider_reached") is True,
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


def _runtime_bound(conversation_result: dict[str, Any], turn: dict[str, Any]) -> bool:
    return (
        conversation_result.get("failed_turns") == 0
        and turn.get("worker_invoked") is True
        and turn.get("replay_certification_reached") is True
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()
