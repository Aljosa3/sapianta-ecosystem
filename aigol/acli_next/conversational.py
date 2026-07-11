"""Thin conversational ACLI Next UX over certified runtime capabilities."""

from __future__ import annotations

import unicodedata
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.daily_dashboard import run_acli_next_daily_dashboard
from aigol.acli_next.execution_plan import run_acli_next_interactive_with_execution_plan
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_PERSISTENT_WORKSPACE_VERSION,
    PLATFORM_CORE_PROJECT_GUIDANCE_VERSION,
    PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
    build_persistent_workspace_state_artifact,
    guided_development_clarification,
    human_conversation_experience_from_resolution,
    project_guidance_from_workspace_state,
    resolve_development_intent,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION = (
    "G11_02_ACLI_NEXT_CONVERSATIONAL_DEVELOPMENT_SESSION_IMPLEMENTATION_V1"
)
ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_VERSION = (
    "G11_03_ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_IMPLEMENTATION_V1"
)
ACLI_NEXT_MESSAGE_COMPOSER_VERSION = "G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1"
ACLI_NEXT_PERSISTENT_WORKSPACE_VERSION = PLATFORM_CORE_PERSISTENT_WORKSPACE_VERSION
ACLI_NEXT_PROJECT_GUIDANCE_VERSION = PLATFORM_CORE_PROJECT_GUIDANCE_VERSION
ACLI_NEXT_PROJECT_KNOWLEDGE_REUSE_VERSION = PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION
ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME = "aigol next"
ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED = "ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED"
ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETED = (
    "ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETED"
)
ACLI_NEXT_PERSISTENT_EXIT_COMMANDS = {"exit", "quit", "close session"}
ACLI_NEXT_MESSAGE_COMPOSER_SEND_COMMAND = "/send"
ACLI_NEXT_MESSAGE_COMPOSER_PREVIEW_COMMAND = "/preview"
ACLI_NEXT_MESSAGE_COMPOSER_CLEAR_COMMAND = "/clear"
ACLI_NEXT_MESSAGE_COMPOSER_CANCEL_COMMAND = "/cancel"
ACLI_NEXT_MESSAGE_COMPOSER_HELP_COMMAND = "/help"
ACLI_NEXT_MESSAGE_COMPOSER_APPROVE_COMMAND = "/approve"
ACLI_NEXT_MESSAGE_COMPOSER_EXIT_COMMANDS = {"/exit", "/quit", "exit", "quit", "close session"}
ACLI_NEXT_MESSAGE_COMPOSER_PROMPT_PREFIXES = ("aigol compose>", "aigol>")


def run_acli_next_conversational_session(
    *,
    prompts: list[str],
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None = None,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run a natural ACLI Next conversational turn set using existing certified components."""

    normalized_prompts = _require_prompts(prompts)
    conversation_id = session_id or _derived_session_id(normalized_prompts, created_at)
    session_root = Path(replay_dir) / conversation_id
    run_index = _next_run_index(session_root)
    run_id = f"RUN-{run_index:06d}"
    run_root = session_root / run_id
    runtime_session_id = f"{conversation_id}:{run_id}"
    turns = [
        {
            "operator_request": prompt,
            "operator_response": _operator_response_for_prompt(prompt, index, len(normalized_prompts)),
        }
        for index, prompt in enumerate(normalized_prompts, start=1)
    ]

    execution_plan = run_acli_next_interactive_with_execution_plan(
        session_id=runtime_session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=run_root / "execution_plan",
        workspace=workspace,
        worker_sequence=["Platform Core", "Governed Development Workflow"],
        requested_capabilities=_requested_capabilities(normalized_prompts),
        expected_artifacts=[
            "workflow_stage_summary",
            "execution_plan_preview",
            "dashboard_snapshot",
            "replay_reference",
        ],
        potential_repository_impacts=["none_from_conversational_layer"],
    )
    _require_non_authoritative_execution_plan(execution_plan)

    dashboard = run_acli_next_daily_dashboard(
        dashboard_id=f"{conversation_id}:{run_id}:DASHBOARD",
        platform_core_state=_platform_core_state(
            conversation_id=conversation_id,
            run_id=run_id,
            prompts=normalized_prompts,
            execution_plan=execution_plan,
        ),
        created_at=created_at,
        replay_dir=run_root / "dashboard",
    )
    _require_non_authoritative_dashboard(dashboard)

    artifact = _conversational_artifact(
        conversation_id=conversation_id,
        run_id=run_id,
        run_index=run_index,
        prompts=normalized_prompts,
        execution_plan=execution_plan,
        dashboard=dashboard,
        session_root=session_root,
        run_root=run_root,
        created_at=created_at,
        workspace=workspace,
    )
    write_json_immutable(run_root / "000_acli_next_conversational_session_presented.json", artifact)
    result = deepcopy(artifact)
    result["replay_hash"] = artifact["artifact_hash"]
    return result


def run_acli_next_persistent_conversational_session(
    *,
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None = None,
    workspace: str | Path = ".",
    input_reader: Any | None = None,
    output_writer: Any | None = None,
    turn_runner: Any | None = None,
    guided_development_workflow: bool = False,
) -> dict[str, Any]:
    """Run a persistent ACLI Next conversational REPL over the single-turn adapter."""

    reader = input if input_reader is None else input_reader
    writer = print if output_writer is None else output_writer
    submit_turn = run_acli_next_conversational_session if turn_runner is None else turn_runner
    conversation_id = session_id or _derived_persistent_session_id(created_at, workspace)
    session_root = Path(replay_dir) / conversation_id
    workspace_state = _latest_persistent_workspace_state(session_root)
    turn_results: list[dict[str, Any]] = []
    composer_buffer: list[str] = []
    pending_clarification = _restored_pending_clarification(workspace_state)
    pending_summary = _restored_pending_summary(workspace_state)
    composer_events = {
        "preview_count": 0,
        "clear_count": 0,
        "cancel_count": 0,
        "empty_send_count": 0,
        "submitted_message_count": 0,
        "clarification_question_count": 0,
        "clarification_response_count": 0,
        "execution_summary_count": 0,
        "approval_count": 0,
        "goal_mapping_count": 0,
        "knowledge_reuse_count": 0,
    }
    exit_reason = "EXIT_COMMAND"
    writer(
        "AiGOL conversational session started. Compose a message, then type /send. "
        "Use /preview, /clear, /cancel, or /help."
    )
    if workspace_state is not None:
        writer(_render_persistent_workspace_resume(workspace_state))
        writer(_render_project_guidance(project_guidance_from_workspace_state(workspace_state)))
    while True:
        try:
            prompt = reader("" if composer_buffer else "AiGOL> ")
        except EOFError:
            exit_reason = "EOF"
            break
        if not isinstance(prompt, str):
            raise FailClosedRuntimeError("ACLI Next persistent session requires string input")
        line = prompt.rstrip("\r\n")
        normalized = line.strip()
        command = _normalized_message_composer_command(line)
        if not normalized and not composer_buffer:
            continue
        if not command and not composer_buffer:
            continue
        if command in ACLI_NEXT_MESSAGE_COMPOSER_EXIT_COMMANDS:
            if composer_buffer:
                writer("Composed message is not empty. Use /send, /clear, or /cancel before exiting.")
                continue
            break
        if command == ACLI_NEXT_MESSAGE_COMPOSER_HELP_COMMAND:
            writer(_render_message_composer_help())
            continue
        if command == ACLI_NEXT_MESSAGE_COMPOSER_APPROVE_COMMAND:
            if not pending_summary:
                writer("No implementation summary is awaiting approval.")
                continue
            composer_events["approval_count"] += 1
            writer("Human confirmation recorded. Entering certified runtime.")
            turn_result = submit_turn(
                session_id=conversation_id,
                prompts=[pending_summary["refined_message"]],
                created_at=created_at,
                replay_dir=replay_dir,
                workspace=workspace,
            )
            turn_results.append(turn_result)
            pending_summary = None
            pending_clarification = None
            composer_buffer.clear()
            writer(render_acli_next_conversational_session(turn_result))
            continue
        if command == ACLI_NEXT_MESSAGE_COMPOSER_PREVIEW_COMMAND:
            composer_events["preview_count"] += 1
            writer(_render_message_composer_preview(composer_buffer))
            continue
        if command == ACLI_NEXT_MESSAGE_COMPOSER_CLEAR_COMMAND:
            composer_events["clear_count"] += 1
            composer_buffer.clear()
            writer("Message buffer cleared.")
            continue
        if command == ACLI_NEXT_MESSAGE_COMPOSER_CANCEL_COMMAND:
            composer_events["cancel_count"] += 1
            composer_buffer.clear()
            pending_clarification = None
            pending_summary = None
            writer("Message composition canceled.")
            continue
        if command == ACLI_NEXT_MESSAGE_COMPOSER_SEND_COMMAND:
            message = _composed_message(composer_buffer)
            if not message:
                composer_events["empty_send_count"] += 1
                writer("Message buffer is empty. Add content before /send.")
                continue
            if guided_development_workflow and pending_clarification is not None:
                composer_events["clarification_response_count"] += 1
                clarified_message = f"{pending_clarification['original_message']}\n\nClarification:\n{message}"
                intent_resolution = resolve_development_intent(
                    message=clarified_message,
                    workspace_state=workspace_state,
                )
                if intent_resolution.get("summary_admissible") is not True:
                    pending_clarification = guided_development_clarification(pending_clarification["original_message"])
                    composer_events["clarification_question_count"] += 1
                    composer_buffer.clear()
                    writer(_render_guided_development_clarification(pending_clarification))
                    continue
                conversation_experience = _human_conversation_experience(
                    message=clarified_message,
                    intent_resolution=intent_resolution,
                    workspace_state=workspace_state,
                )
                pending_summary = _guided_development_summary(conversation_experience=conversation_experience)
                composer_events["execution_summary_count"] += 1
                pending_clarification = None
                composer_buffer.clear()
                writer(_render_guided_development_summary(pending_summary))
                continue
            intent_resolution = (
                resolve_development_intent(message=message, workspace_state=workspace_state)
                if guided_development_workflow
                else None
            )
            conversation_experience = (
                _human_conversation_experience(
                    message=message,
                    intent_resolution=intent_resolution,
                    workspace_state=workspace_state,
                )
                if guided_development_workflow and isinstance(intent_resolution, dict)
                else {}
            )
            if guided_development_workflow and isinstance(intent_resolution, dict) and intent_resolution.get(
                "clarification_required"
            ) is True:
                pending_clarification = _clarification_from_conversation(message, conversation_experience)
                composer_events["clarification_question_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_clarification(pending_clarification))
                continue
            if (
                guided_development_workflow
                and isinstance(intent_resolution, dict)
                and conversation_experience.get("response_mode") == "CLARIFICATION"
            ):
                pending_clarification = _clarification_from_conversation(message, conversation_experience)
                composer_events["clarification_question_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_clarification(pending_clarification))
                continue
            if guided_development_workflow and isinstance(intent_resolution, dict) and intent_resolution.get(
                "summary_admissible"
            ) is True:
                goal_mapping = (
                    intent_resolution.get("goal_mapping")
                    if isinstance(intent_resolution.get("goal_mapping"), dict)
                    else None
                )
                if goal_mapping is not None:
                    composer_events["goal_mapping_count"] += 1
                    composer_events["knowledge_reuse_count"] += 1
                pending_summary = _guided_development_summary(conversation_experience=conversation_experience)
                composer_events["execution_summary_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_summary(pending_summary))
                continue
            if guided_development_workflow and isinstance(intent_resolution, dict) and _should_render_fail_closed_response(
                conversation_experience
            ):
                composer_buffer.clear()
                writer(_render_fail_closed_response(conversation_experience))
                continue
            composer_events["submitted_message_count"] += 1
            turn_result = submit_turn(
                session_id=conversation_id,
                prompts=[message],
                created_at=created_at,
                replay_dir=replay_dir,
                workspace=workspace,
            )
            turn_results.append(turn_result)
            composer_buffer.clear()
            writer(render_acli_next_conversational_session(turn_result))
            continue
        composer_buffer.append(line)

    if composer_buffer:
        exit_reason = "EOF_WITH_UNSUBMITTED_MESSAGE" if exit_reason == "EOF" else "EXIT_WITH_UNSUBMITTED_MESSAGE"

    completion = _persistent_completion_artifact(
        conversation_id=conversation_id,
        turn_results=turn_results,
        composer_events=composer_events,
        unsubmitted_buffer_line_count=len(composer_buffer),
        guided_development_workflow=guided_development_workflow,
        session_resumed=workspace_state is not None,
        restored_workspace_state_reference=workspace_state.get("replay_reference") if workspace_state else None,
        restored_implementation_history_count=len(workspace_state.get("implementation_history", []))
        if workspace_state
        else 0,
        pending_clarification=pending_clarification is not None,
        pending_summary=pending_summary is not None,
        session_root=session_root,
        exit_reason=exit_reason,
        created_at=created_at,
        workspace=workspace,
    )
    write_json_immutable(
        session_root
        / f"{_next_persistent_completion_index(session_root):03d}_acli_next_persistent_session_completed.json",
        completion,
    )
    workspace_snapshot = build_persistent_workspace_state_artifact(
        conversation_id=conversation_id,
        command_name=ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME,
        prior_state=workspace_state,
        completion=completion,
        turn_results=turn_results,
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
        session_root=session_root,
        created_at=created_at,
        workspace=workspace,
    )
    write_json_immutable(
        session_root
        / "workspace_state"
        / f"{_next_workspace_state_index(session_root):03d}_acli_next_workspace_state_recorded.json",
        workspace_snapshot,
    )
    writer("AiGOL conversational session closed.")
    result = deepcopy(completion)
    result["workspace_state_replay_reference"] = workspace_snapshot["replay_reference"]
    result["workspace_state_hash"] = workspace_snapshot["artifact_hash"]
    result["replay_hash"] = completion["artifact_hash"]
    return result


def render_acli_next_conversational_session(result: dict[str, Any]) -> str:
    """Render the conversational ACLI Next session summary."""

    dashboard = result.get("dashboard_summary") if isinstance(result.get("dashboard_summary"), dict) else {}
    hybrid = dashboard.get("hybrid_operation") if isinstance(dashboard.get("hybrid_operation"), dict) else {}
    governance = dashboard.get("governance") if isinstance(dashboard.get("governance"), dict) else {}
    replay = dashboard.get("replay") if isinstance(dashboard.get("replay"), dict) else {}
    health = (
        dashboard.get("architectural_health")
        if isinstance(dashboard.get("architectural_health"), dict)
        else {}
    )
    lines = [
        f"command: {result.get('command')}",
        f"runtime_version: {result.get('runtime_version')}",
        f"session_id: {result.get('session_id')}",
        f"run_id: {result.get('run_id')}",
        f"session_resumed: {result.get('session_resumed')}",
        f"turn_count: {result.get('turn_count')}",
        f"session_status: {result.get('session_status')}",
        f"prompt: {result.get('latest_prompt')}",
        f"current_stage: {dashboard.get('workflow', {}).get('current_stage')}",
        f"next_expected_operation: {dashboard.get('workflow', {}).get('next_expected_operation')}",
        f"approval_state: {governance.get('approval_state')}",
        f"authorization_state: {governance.get('authorization_state')}",
        f"latest_replay_record: {replay.get('latest_replay_record')}",
        f"architectural_health_status: {health.get('health_status')}",
        f"hybrid_status: {hybrid.get('hybrid_status')}",
        f"hybrid_reason: {hybrid.get('reason')}",
        f"execution_plan_replay_reference: {result.get('execution_plan_replay_reference')}",
        f"dashboard_replay_reference: {result.get('dashboard_replay_reference')}",
        f"replay_reference: {result.get('replay_reference')}",
        f"acli_next_authorizes: {result.get('acli_next_authorizes')}",
        f"acli_next_executes: {result.get('acli_next_executes')}",
        f"acli_next_records_replay_evidence: {result.get('acli_next_records_replay_evidence')}",
    ]
    if result.get("runtime_binding_status"):
        lines.extend(
            [
                f"runtime_binding_status: {result.get('runtime_binding_status')}",
                f"runtime_entered: {result.get('runtime_entered')}",
                f"governance_authorization_reached: {result.get('governance_authorization_reached')}",
                f"provider_invocation_reached: {result.get('provider_invocation_reached')}",
                f"worker_execution_reached: {result.get('worker_execution_reached')}",
                f"replay_certification_reached: {result.get('replay_certification_reached')}",
                f"manual_chatgpt_codex_transfer_required: {result.get('manual_chatgpt_codex_transfer_required')}",
            ]
        )
    return "\n".join(lines)


def render_acli_next_persistent_conversational_session(result: dict[str, Any]) -> str:
    """Render the persistent conversational ACLI Next session summary."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"session_status: {result.get('session_status')}",
            f"turn_count: {result.get('turn_count')}",
            f"message_composer_enabled: {result.get('message_composer_enabled')}",
            f"persistent_development_workspace_enabled: {result.get('persistent_development_workspace_enabled')}",
            f"session_resumed: {result.get('session_resumed')}",
            f"restored_implementation_history_count: {result.get('restored_implementation_history_count')}",
            f"guided_development_workflow_enabled: {result.get('guided_development_workflow_enabled')}",
            f"submitted_message_count: {result.get('submitted_message_count')}",
            f"clarification_question_count: {result.get('clarification_question_count')}",
            f"clarification_response_count: {result.get('clarification_response_count')}",
            f"execution_summary_count: {result.get('execution_summary_count')}",
            f"approval_count: {result.get('approval_count')}",
            f"goal_mapping_count: {result.get('goal_mapping_count')}",
            f"knowledge_reuse_count: {result.get('knowledge_reuse_count')}",
            f"runtime_bound_count: {result.get('runtime_bound_count')}",
            f"pending_clarification: {result.get('pending_clarification')}",
            f"pending_execution_summary: {result.get('pending_execution_summary')}",
            f"exit_reason: {result.get('exit_reason')}",
            f"workspace_state_replay_reference: {result.get('workspace_state_replay_reference')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"acli_next_authorizes: {result.get('acli_next_authorizes')}",
            f"acli_next_executes: {result.get('acli_next_executes')}",
            f"acli_next_records_replay_evidence: {result.get('acli_next_records_replay_evidence')}",
        ]
    )


def _conversational_artifact(
    *,
    conversation_id: str,
    run_id: str,
    run_index: int,
    prompts: list[str],
    execution_plan: dict[str, Any],
    dashboard: dict[str, Any],
    session_root: Path,
    run_root: Path,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    dashboard_snapshot = dashboard.get("platform_core_snapshot", {})
    artifact = {
        "artifact_type": "ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTATION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION,
        "command": ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME,
        "session_id": conversation_id,
        "run_id": run_id,
        "run_index": run_index,
        "session_resumed": run_index > 1,
        "session_status": ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED,
        "turn_count": len(prompts),
        "latest_prompt": prompts[-1],
        "prompt_hashes": [replay_hash(prompt) for prompt in prompts],
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "execution_plan_hash": execution_plan["replay_hash"],
        "execution_plan_replay_reference": execution_plan.get("replay_reference"),
        "dashboard_hash": dashboard["replay_hash"],
        "dashboard_replay_reference": dashboard.get("replay_reference"),
        "dashboard_summary": deepcopy(dashboard_snapshot),
        "replay_reference": str(run_root),
        "session_root": str(session_root),
        "show_guide_delegate_only": True,
        "minimal_ux_extension_only": True,
        "platform_core_coordinates": True,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "worker_execution_authority_preserved": True,
        "architectural_health_advisory_only": True,
        "platform_digital_twin_evidence_source_preserved": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
        "acli_next_records_replay_evidence": False,
        "acli_next_repairs_architecture": False,
        "acli_next_certifies": False,
        "external_operation_performed": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "dependency_operation_performed": False,
        "git_remote_operation_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _latest_persistent_workspace_state(session_root: Path) -> dict[str, Any] | None:
    state_root = session_root / "workspace_state"
    if not state_root.exists():
        return None
    candidates = sorted(state_root.glob("*_acli_next_workspace_state_recorded.json"))
    for path in reversed(candidates):
        try:
            artifact = load_json(path)
        except FailClosedRuntimeError:
            continue
        if artifact.get("artifact_type") == "ACLI_NEXT_PERSISTENT_WORKSPACE_STATE_ARTIFACT_V1":
            return artifact
    return None


def _restored_pending_clarification(workspace_state: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(workspace_state, dict):
        return None
    pending = workspace_state.get("pending_clarification_request")
    return deepcopy(pending) if isinstance(pending, dict) else None


def _restored_pending_summary(workspace_state: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(workspace_state, dict):
        return None
    pending = workspace_state.get("pending_implementation_summary")
    return deepcopy(pending) if isinstance(pending, dict) else None


def _next_workspace_state_index(session_root: Path) -> int:
    state_root = session_root / "workspace_state"
    existing: list[int] = []
    if state_root.exists():
        for path in state_root.glob("*_acli_next_workspace_state_recorded.json"):
            prefix = path.name.split("_", 1)[0]
            if prefix.isdigit():
                existing.append(int(prefix))
    return max(existing, default=0) + 1


def _next_persistent_completion_index(session_root: Path) -> int:
    existing: list[int] = []
    if session_root.exists():
        for path in session_root.glob("*_acli_next_persistent_session_completed.json"):
            prefix = path.name.split("_", 1)[0]
            if prefix.isdigit():
                existing.append(int(prefix))
    return max(existing, default=0) + 1


def _render_persistent_workspace_resume(workspace_state: dict[str, Any]) -> str:
    lines = [
        "Persistent development workspace restored.",
        f"active_development_objective: {workspace_state.get('active_development_objective')}",
        f"pending_clarification: {workspace_state.get('pending_clarification_request') is not None}",
        f"pending_approval: {workspace_state.get('pending_approval') is True}",
        f"implementation_history_count: {workspace_state.get('implementation_history_count')}",
    ]
    if workspace_state.get("pending_clarification_request") is not None:
        lines.append("Continue by answering the pending clarification and type /send.")
    elif workspace_state.get("pending_implementation_summary") is not None:
        lines.append("Continue by typing /approve, or /cancel to discard the pending summary.")
    else:
        lines.append("Continue by composing the next development request.")
    return "\n".join(lines)


def _render_project_guidance(guidance: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Project guidance",
            f"guidance_source: {guidance.get('guidance_source')}",
            f"active_generation: {guidance.get('active_generation')}",
            f"active_milestone: {guidance.get('active_milestone')}",
            f"pending_implementation_work: {', '.join(guidance.get('pending_implementation_work') or [])}",
            f"pending_approvals: {', '.join(guidance.get('pending_approvals') or []) or 'NONE'}",
            f"unresolved_clarification: {guidance.get('unresolved_clarification')}",
            f"recommended_next_governed_action: {guidance.get('recommended_next_governed_action')}",
            f"acli_next_executes_recommendation: {guidance.get('acli_next_executes_recommendation')}",
        ]
    )


def _persistent_completion_artifact(
    *,
    conversation_id: str,
    turn_results: list[dict[str, Any]],
    composer_events: dict[str, int],
    unsubmitted_buffer_line_count: int,
    guided_development_workflow: bool,
    session_resumed: bool,
    restored_workspace_state_reference: str | None,
    restored_implementation_history_count: int,
    pending_clarification: bool,
    pending_summary: bool,
    session_root: Path,
    exit_reason: str,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_MESSAGE_COMPOSER_VERSION,
        "persistent_session_runtime_version": ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_VERSION,
        "command": ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME,
        "session_id": conversation_id,
        "session_status": ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_COMPLETED,
        "turn_count": len(turn_results),
        "turn_hashes": [turn["artifact_hash"] for turn in turn_results],
        "turn_replay_references": [turn["replay_reference"] for turn in turn_results],
        "message_composer_enabled": True,
        "persistent_development_workspace_enabled": True,
        "persistent_workspace_runtime_version": ACLI_NEXT_PERSISTENT_WORKSPACE_VERSION,
        "session_resumed": bool(session_resumed),
        "restored_workspace_state_reference": restored_workspace_state_reference,
        "restored_implementation_history_count": int(restored_implementation_history_count),
        "guided_development_workflow_enabled": bool(guided_development_workflow),
        "message_composer_version": ACLI_NEXT_MESSAGE_COMPOSER_VERSION,
        "message_composer_commands": [
            ACLI_NEXT_MESSAGE_COMPOSER_SEND_COMMAND,
            ACLI_NEXT_MESSAGE_COMPOSER_PREVIEW_COMMAND,
            ACLI_NEXT_MESSAGE_COMPOSER_CLEAR_COMMAND,
            ACLI_NEXT_MESSAGE_COMPOSER_CANCEL_COMMAND,
            ACLI_NEXT_MESSAGE_COMPOSER_APPROVE_COMMAND,
        ],
        "submitted_message_count": int(composer_events.get("submitted_message_count", 0)),
        "clarification_question_count": int(composer_events.get("clarification_question_count", 0)),
        "clarification_response_count": int(composer_events.get("clarification_response_count", 0)),
        "execution_summary_count": int(composer_events.get("execution_summary_count", 0)),
        "approval_count": int(composer_events.get("approval_count", 0)),
        "goal_mapping_count": int(composer_events.get("goal_mapping_count", 0)),
        "knowledge_reuse_count": int(composer_events.get("knowledge_reuse_count", 0)),
        "runtime_bound_count": sum(
            1 for result in turn_results if result.get("runtime_binding_status") == "AIGOL_NEXT_RUNTIME_BOUND"
        ),
        "pending_clarification": bool(pending_clarification),
        "pending_execution_summary": bool(pending_summary),
        "preview_count": int(composer_events.get("preview_count", 0)),
        "clear_count": int(composer_events.get("clear_count", 0)),
        "cancel_count": int(composer_events.get("cancel_count", 0)),
        "empty_send_count": int(composer_events.get("empty_send_count", 0)),
        "unsubmitted_buffer_line_count": int(unsubmitted_buffer_line_count),
        "composer_creates_turn_before_send": False,
        "composer_creates_replay_before_send": False,
        "one_submitted_message_per_turn": True,
        "exit_reason": _require_string(exit_reason, "exit_reason"),
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(session_root),
        "persistent_repl": True,
        "show_guide_delegate_only": True,
        "minimal_ux_extension_only": True,
        "platform_core_coordinates": True,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "worker_execution_authority_preserved": True,
        "architectural_health_advisory_only": True,
        "platform_digital_twin_evidence_source_preserved": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
        "acli_next_records_replay_evidence": False,
        "acli_next_repairs_architecture": False,
        "acli_next_certifies": False,
        "external_operation_performed": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "dependency_operation_performed": False,
        "git_remote_operation_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _composed_message(buffer: list[str]) -> str:
    return "\n".join(buffer).strip()


def _normalized_message_composer_command(line: str) -> str:
    """Normalize only command detection; preserve buffered message content unchanged."""

    candidate = line.strip()
    normalized = "".join(ch for ch in candidate if unicodedata.category(ch) != "Cf").lower().strip()
    for prefix in ACLI_NEXT_MESSAGE_COMPOSER_PROMPT_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            break
    return normalized


def _render_message_composer_preview(buffer: list[str]) -> str:
    message = _composed_message(buffer)
    if not message:
        return "Message buffer is empty."
    return "\n".join(["Message buffer preview:", message])


def _render_message_composer_help() -> str:
    return "\n".join(
        [
            "Message composer commands:",
            "/send - submit the composed message as one governed conversational turn",
            "/preview - show the current buffer without execution",
            "/clear - empty the current buffer",
            "/cancel - discard the current message",
            "/approve - confirm the presented implementation summary and enter the certified runtime",
            "/exit or /quit - close the session when the buffer is empty",
        ]
    )


def _render_guided_development_clarification(clarification: dict[str, Any]) -> str:
    lines = [
        "Clarification required before governed execution.",
        f"original_request: {clarification.get('original_message')}",
    ]
    if clarification.get("user_headline"):
        lines.append(str(clarification["user_headline"]))
    if clarification.get("user_explanation"):
        lines.append(str(clarification["user_explanation"]))
    lines.append("questions:")
    lines.extend(f"- {question}" for question in clarification.get("clarification_questions", []))
    lines.append("Compose your answer and type /send.")
    return "\n".join(lines)


def _human_conversation_experience(
    *,
    message: str,
    intent_resolution: dict[str, Any] | None,
    workspace_state: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(intent_resolution, dict):
        return {}
    guidance = (
        project_guidance_from_workspace_state(workspace_state)
        if isinstance(workspace_state, dict)
        else {}
    )
    goal_mapping = (
        intent_resolution.get("goal_mapping")
        if isinstance(intent_resolution.get("goal_mapping"), dict)
        else {}
    )
    knowledge = (
        goal_mapping.get("contextual_task_mapping")
        if isinstance(goal_mapping.get("contextual_task_mapping"), dict)
        else {}
    )
    return human_conversation_experience_from_resolution(
        message=message,
        guidance=guidance,
        knowledge_reuse=knowledge,
        development_intent=intent_resolution,
    )


def _clarification_from_conversation(message: str, conversation: dict[str, Any]) -> dict[str, Any]:
    questions = conversation.get("clarification_questions")
    if not isinstance(questions, list) or not questions:
        return guided_development_clarification(message)
    return {
        "original_message": message,
        "clarification_required": True,
        "clarification_authority": "PLATFORM_CORE",
        "conversation_response_mode": conversation.get("response_mode"),
        "user_headline": conversation.get("user_headline"),
        "user_explanation": conversation.get("user_explanation"),
        "requested_work_type": conversation.get("requested_work_type"),
        "work_type": conversation.get("work_type"),
        "prepared_work_type": conversation.get("prepared_work_type"),
        "work_type_source": conversation.get("work_type_source"),
        "work_type_source_text": conversation.get("work_type_source_text"),
        "mutation_allowed": conversation.get("mutation_allowed"),
        "runtime_implementation": conversation.get("runtime_implementation"),
        "work_type_change_allowed": conversation.get("work_type_change_allowed"),
        "work_type_conflict_detected": conversation.get("work_type_conflict_detected"),
        "work_type_conflict_reason": conversation.get("work_type_conflict_reason"),
        "clarification_questions": [str(question) for question in questions],
    }


def _guided_development_summary(*, conversation_experience: dict[str, Any]) -> dict[str, Any]:
    summary = conversation_experience.get("approval_summary")
    if not isinstance(summary, dict):
        raise FailClosedRuntimeError("Platform Core approval_summary is required")
    return dict(summary)


def _render_guided_development_summary(summary: dict[str, Any]) -> str:
    lines = [
        str(summary.get("summary_title") or "Governed implementation summary"),
        f"original_request: {summary.get('original_request')}",
    ]
    if isinstance(summary.get("goal_mapping"), dict):
        mapping = summary["goal_mapping"]
        lines.extend(
            [
                "goal_mapping:",
                f"goal_type: {mapping.get('goal_type')}",
                f"goal_target: {mapping.get('goal_target')}",
                f"governed_request: {mapping.get('governed_request')}",
                f"mapping_source: {mapping.get('mapping_source')}",
            ]
        )
        if isinstance(mapping.get("contextual_task_mapping"), dict):
            context = mapping["contextual_task_mapping"]
            lines.extend(
                [
                    "contextual_task_mapping:",
                    f"classification: {context.get('classification')}",
                    f"workspace_inspected: {context.get('workspace_inspected')}",
                    f"reuse_recommended: {context.get('reuse_recommended')}",
                    f"new_work_required: {context.get('new_work_required')}",
                    f"duplicate_work_avoided: {context.get('duplicate_work_avoided')}",
                    f"related_milestones: {', '.join(context.get('related_milestones') or []) or 'NONE'}",
                    "relevant_certified_artifacts: "
                    f"{', '.join(context.get('relevant_certified_artifacts') or []) or 'NONE'}",
                    "implementation_history_matches: "
                    f"{', '.join(context.get('implementation_history_matches') or []) or 'NONE'}",
                ]
            )
    lines.extend(
        [
            f"runtime_after_approval: {summary.get('runtime_after_approval')}",
            str(summary.get("approval_explanation")),
            "Type /approve to continue into the certified runtime, or /cancel to discard.",
        ]
    )
    return "\n".join(lines)


def _render_fail_closed_response(conversation_experience: dict[str, Any]) -> str:
    response = conversation_experience.get("fail_closed_response")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("Platform Core fail_closed_response is required")
    return "\n".join(
        [
            str(response.get("response_title") or "No governed implementation summary was produced."),
            f"reason: {response.get('reason')}",
            str(response.get("fail_closed_explanation")),
            f"next_step: {response.get('recommended_next_user_action')}",
            "Compose a revised request and type /send.",
        ]
    )


def _should_render_fail_closed_response(conversation_experience: dict[str, Any]) -> bool:
    response = conversation_experience.get("fail_closed_response")
    if not isinstance(response, dict) or response.get("conversation_state") != "FAIL_CLOSED":
        return False
    return response.get("interface_render_recommended") is True


def _platform_core_state(
    *,
    conversation_id: str,
    run_id: str,
    prompts: list[str],
    execution_plan: dict[str, Any],
) -> dict[str, Any]:
    requested_operation = _requested_operation(prompts)
    hybrid_required = requested_operation in {
        "git_remote",
        "dependency_management",
        "deployment",
        "exceptional_environment",
    }
    return {
        "workflow": {
            "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
            "current_stage": "Classify Capability Coverage",
            "completed_stages": ["Capture Intent"],
            "current_operation": "present conversational governed development state",
            "next_expected_operation": "Existing Capability Audit",
        },
        "active_task": {
            "task_id": conversation_id,
            "task_objective": prompts[-1],
            "current_milestone": "G11_02",
            "current_generation": "Generation 11",
            "governance_state": "governed",
            "requested_operation": requested_operation,
        },
        "governance": {
            "approval_state": "not_required_for_conversational_presentation",
            "authorization_state": "not_required_for_conversational_presentation",
            "pending_approvals": [],
            "completed_authorizations": [],
        },
        "validation": {
            "latest_validation": "not_run",
            "validation_suite_status": "not_run",
            "validation_summary": "conversational presentation only; no execution validation required",
            "validation_outcome": "not_applicable",
        },
        "replay": {
            "latest_replay_record": str(execution_plan.get("replay_reference")),
            "replay_summary": f"conversational run {run_id} delegated to existing ACLI Next execution plan runtime",
            "reconstruction_available": True,
            "evidence_available": True,
        },
        "architectural_health": {
            "health_status": "advisory_review_required_before_certification",
            "highest_severity": "none",
            "findings": [],
            "recommendations": [
                "verify ACLI Next remains show-guide-delegate only",
                "verify Platform Core remains the orchestration authority",
            ],
        },
        "hybrid": {
            "operation_type": requested_operation,
            "hybrid_required": hybrid_required,
        },
    }


def _requested_capabilities(prompts: list[str]) -> list[str]:
    capabilities = [
        "acli_next_conversational_presentation",
        "governed_development_workflow_visibility",
        "platform_core_execution_plan_preview",
        "daily_operational_dashboard",
    ]
    requested = _requested_operation(prompts)
    if requested != "governed_development":
        capabilities.append(f"hybrid_guidance_for_{requested}")
    return capabilities


def _requested_operation(prompts: list[str]) -> str:
    text = " ".join(prompts).lower()
    if "git remote" in text or "push" in text or "pull request" in text or "remote branch" in text:
        return "git_remote"
    if "dependency" in text or "package" in text or "lockfile" in text:
        return "dependency_management"
    if "deploy" in text or "deployment" in text:
        return "deployment"
    if "environment" in text or "credential" in text or "infrastructure" in text:
        return "exceptional_environment"
    return "governed_development"


def _operator_response_for_prompt(prompt: str, index: int, total: int) -> str:
    if index < total:
        return "please clarify"
    return "confirm"


def _next_run_index(session_root: Path) -> int:
    if not session_root.exists():
        return 1
    existing = []
    for path in session_root.iterdir():
        if not path.is_dir() or not path.name.startswith("RUN-"):
            continue
        suffix = path.name.removeprefix("RUN-")
        if suffix.isdigit():
            existing.append(int(suffix))
    return max(existing, default=0) + 1


def _derived_session_id(prompts: list[str], created_at: str) -> str:
    digest = replay_hash({"prompts": prompts, "created_at": created_at})[7:23].upper()
    return f"ACLI-NEXT-CONVERSATIONAL-{digest}"


def _derived_persistent_session_id(created_at: str, workspace: str | Path) -> str:
    digest = replay_hash({"created_at": created_at, "workspace": str(Path(workspace)), "mode": "persistent"})[
        7:23
    ].upper()
    return f"ACLI-NEXT-PERSISTENT-{digest}"


def _require_prompts(prompts: list[str]) -> list[str]:
    if not isinstance(prompts, list) or not prompts:
        raise FailClosedRuntimeError("ACLI Next conversational session requires at least one prompt")
    return [_require_string(prompt, "prompt").strip() for prompt in prompts]


def _require_non_authoritative_execution_plan(execution_plan: dict[str, Any]) -> None:
    for key in (
        "execution_authorized",
        "worker_invoked",
        "provider_invoked",
        "repository_mutated",
        "deployment_performed",
    ):
        if execution_plan.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next conversational session failed closed: execution plan {key}")


def _require_non_authoritative_dashboard(dashboard: dict[str, Any]) -> None:
    for key in (
        "acli_next_authorizes",
        "acli_next_executes",
        "acli_next_records_replay_evidence",
        "external_operation_performed",
        "repository_mutated",
        "deployment_performed",
        "dependency_operation_performed",
        "git_remote_operation_performed",
    ):
        if dashboard.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next conversational session failed closed: dashboard {key}")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next conversational session requires {field}")
    return value
