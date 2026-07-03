"""Thin conversational ACLI Next UX over certified runtime capabilities."""

from __future__ import annotations

import unicodedata
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.daily_dashboard import run_acli_next_daily_dashboard
from aigol.acli_next.execution_plan import run_acli_next_interactive_with_execution_plan
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION = (
    "G11_02_ACLI_NEXT_CONVERSATIONAL_DEVELOPMENT_SESSION_IMPLEMENTATION_V1"
)
ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_VERSION = (
    "G11_03_ACLI_NEXT_PERSISTENT_CONVERSATIONAL_SESSION_IMPLEMENTATION_V1"
)
ACLI_NEXT_MESSAGE_COMPOSER_VERSION = "G12_02_ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTATION_V1"
ACLI_NEXT_PERSISTENT_WORKSPACE_VERSION = "G14_05_PERSISTENT_DEVELOPMENT_WORKSPACE_AND_PROJECT_CONTINUITY_V1"
ACLI_NEXT_PROJECT_GUIDANCE_VERSION = "G14_06_PROJECT_GUIDANCE_AND_DEVELOPMENT_ASSISTANT_V1"
ACLI_NEXT_PROJECT_KNOWLEDGE_REUSE_VERSION = (
    "G14_08_PROJECT_KNOWLEDGE_REUSE_AND_CONTEXTUAL_TASK_MAPPING_V1"
)
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
        writer(_render_project_guidance(_project_guidance_from_workspace_state(workspace_state)))
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
                pending_summary = _guided_development_summary(
                    original_message=pending_clarification["original_message"],
                    clarification_response=message,
                    workspace_state=workspace_state,
                )
                composer_events["execution_summary_count"] += 1
                pending_clarification = None
                composer_buffer.clear()
                writer(_render_guided_development_summary(pending_summary))
                continue
            if guided_development_workflow and _guided_development_clarification_required(message):
                pending_clarification = _guided_development_clarification(message)
                composer_events["clarification_question_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_clarification(pending_clarification))
                continue
            if guided_development_workflow and _goal_oriented_request_detected(message):
                composer_events["goal_mapping_count"] += 1
                composer_events["knowledge_reuse_count"] += 1
                pending_summary = _guided_development_summary(
                    original_message=message,
                    clarification_response=None,
                    workspace_state=workspace_state,
                    goal_mapping=_goal_mapping_from_workspace(
                        message=message,
                        workspace_state=workspace_state,
                    ),
                )
                composer_events["execution_summary_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_summary(pending_summary))
                continue
            if guided_development_workflow and _guided_development_request_detected(message):
                pending_summary = _guided_development_summary(
                    original_message=message,
                    clarification_response=None,
                    workspace_state=workspace_state,
                )
                composer_events["execution_summary_count"] += 1
                composer_buffer.clear()
                writer(_render_guided_development_summary(pending_summary))
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
    workspace_snapshot = _persistent_workspace_state_artifact(
        conversation_id=conversation_id,
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


def _persistent_workspace_state_artifact(
    *,
    conversation_id: str,
    prior_state: dict[str, Any] | None,
    completion: dict[str, Any],
    turn_results: list[dict[str, Any]],
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    session_root: Path,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    prior_history = prior_state.get("implementation_history", []) if isinstance(prior_state, dict) else []
    if not isinstance(prior_history, list):
        prior_history = []
    new_history = [
        {
            "runtime_binding_status": result.get("runtime_binding_status"),
            "runtime_replay_reference": result.get("runtime_replay_reference") or result.get("replay_reference"),
            "latest_prompt_hash": replay_hash(result.get("latest_prompt", "")),
            "replay_certification_reached": result.get("replay_certification_reached") is True,
        }
        for result in turn_results
    ]
    implementation_history = [*deepcopy(prior_history), *new_history]
    active_objective = _active_development_objective(
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
        implementation_history=implementation_history,
    )
    pending_approval = pending_summary is not None
    pending_clarification_present = pending_clarification is not None
    guidance = _project_guidance_model(
        active_objective=active_objective,
        pending_clarification=pending_clarification_present,
        pending_approval=pending_approval,
        implementation_history_count=len(implementation_history),
        runtime_bound_count=sum(
            1 for result in turn_results if result.get("runtime_binding_status") == "AIGOL_NEXT_RUNTIME_BOUND"
        ),
    )
    knowledge_index = _project_knowledge_index_model(
        prior_state=prior_state,
        pending_summary=pending_summary,
        guidance=guidance,
        implementation_history=implementation_history,
    )
    artifact = {
        "artifact_type": "ACLI_NEXT_PERSISTENT_WORKSPACE_STATE_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_PERSISTENT_WORKSPACE_VERSION,
        "command": ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME,
        "session_id": conversation_id,
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "session_root": str(session_root),
        "completion_reference": completion.get("replay_reference"),
        "completion_hash": completion.get("artifact_hash"),
        "prior_workspace_state_reference": prior_state.get("replay_reference") if isinstance(prior_state, dict) else None,
        "active_development_objective": active_objective,
        "pending_clarification_request": deepcopy(pending_clarification),
        "pending_implementation_summary": deepcopy(pending_summary),
        "pending_approval": pending_approval,
        "pending_approval_kind": "IMPLEMENTATION_SUMMARY_APPROVAL" if pending_approval else None,
        "implementation_history": implementation_history,
        "implementation_history_count": len(implementation_history),
        "project_guidance": guidance,
        "project_knowledge_index": knowledge_index,
        "recent_governed_decisions": [
            {
                "decision": "HUMAN_CONFIRMATION_RECORDED",
                "runtime_binding_status": result.get("runtime_binding_status"),
                "replay_certification_reached": result.get("replay_certification_reached") is True,
            }
            for result in turn_results
            if result.get("runtime_binding_status")
        ],
        "resumable_conversational_context": True,
        "replay_visible": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
        "platform_core_runtime_delegated": True,
        "replay_reference": str(session_root / "workspace_state"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _active_development_objective(
    *,
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    implementation_history: list[dict[str, Any]],
) -> str | None:
    if isinstance(pending_summary, dict):
        return str(pending_summary.get("original_message") or pending_summary.get("refined_message") or "")
    if isinstance(pending_clarification, dict):
        return str(pending_clarification.get("original_message") or "")
    if implementation_history:
        return "recent governed development runtime completed"
    return None


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


def _project_guidance_from_workspace_state(workspace_state: dict[str, Any]) -> dict[str, Any]:
    existing = workspace_state.get("project_guidance")
    if isinstance(existing, dict):
        return deepcopy(existing)
    return _project_guidance_model(
        active_objective=workspace_state.get("active_development_objective"),
        pending_clarification=workspace_state.get("pending_clarification_request") is not None,
        pending_approval=workspace_state.get("pending_approval") is True,
        implementation_history_count=int(workspace_state.get("implementation_history_count") or 0),
        runtime_bound_count=sum(
            1
            for item in workspace_state.get("implementation_history", [])
            if isinstance(item, dict) and item.get("runtime_binding_status") == "AIGOL_NEXT_RUNTIME_BOUND"
        ),
    )


def _project_guidance_model(
    *,
    active_objective: Any,
    pending_clarification: bool,
    pending_approval: bool,
    implementation_history_count: int,
    runtime_bound_count: int,
) -> dict[str, Any]:
    objective = str(active_objective or "No active development objective")
    pending_work = _guidance_pending_work(
        active_objective=objective,
        pending_clarification=pending_clarification,
        pending_approval=pending_approval,
    )
    return {
        "guidance_version": ACLI_NEXT_PROJECT_GUIDANCE_VERSION,
        "guidance_source": "deterministic_workspace_state",
        "advisory_only": True,
        "active_generation": _guidance_generation(objective),
        "active_milestone": _guidance_milestone(objective),
        "active_development_objective": objective,
        "pending_implementation_work": pending_work,
        "pending_approvals": ["IMPLEMENTATION_SUMMARY_APPROVAL"] if pending_approval else [],
        "unresolved_clarification": pending_clarification,
        "implementation_history_count": int(implementation_history_count),
        "runtime_bound_count": int(runtime_bound_count),
        "recommended_next_governed_action": _guidance_next_action(
            pending_clarification=pending_clarification,
            pending_approval=pending_approval,
            implementation_history_count=implementation_history_count,
        ),
        "requires_explicit_human_approval": pending_approval,
        "acli_next_executes_recommendation": False,
    }


def _guidance_generation(objective: str) -> str:
    marker = _find_generation_marker(objective)
    return f"Generation {marker}" if marker else "Generation 14"


def _guidance_milestone(objective: str) -> str:
    for part in objective.replace("-", "_").split():
        normalized = part.strip(".,:;()[]{}")
        if "_V" in normalized and normalized.rsplit("_V", 1)[-1].isdigit():
            return normalized
    return "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"


def _find_generation_marker(value: str) -> str | None:
    for token in value.replace("-", "_").split("_"):
        if token.startswith("G") and token[1:].isdigit():
            return token[1:]
    for token in value.split():
        cleaned = token.strip(".,:;()[]{}")
        if cleaned.startswith("G") and cleaned[1:].isdigit():
            return cleaned[1:]
    return None


def _guidance_pending_work(
    *,
    active_objective: str,
    pending_clarification: bool,
    pending_approval: bool,
) -> list[str]:
    if pending_clarification:
        return [f"Answer clarification for: {active_objective}"]
    if pending_approval:
        return [f"Approve or cancel implementation summary for: {active_objective}"]
    if active_objective != "No active development objective":
        return [f"Continue next governed development task after: {active_objective}"]
    return ["Define the next governed development objective"]


def _guidance_next_action(
    *,
    pending_clarification: bool,
    pending_approval: bool,
    implementation_history_count: int,
) -> str:
    if pending_clarification:
        return "Answer the pending clarification, then type /send."
    if pending_approval:
        return "Review the pending implementation summary, then type /approve or /cancel."
    if implementation_history_count > 0:
        return "Choose the next governed development objective."
    return "Compose the first governed development request."


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


def _project_knowledge_index_model(
    *,
    prior_state: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    guidance: dict[str, Any],
    implementation_history: list[dict[str, Any]],
) -> dict[str, Any]:
    prior_index = (
        prior_state.get("project_knowledge_index")
        if isinstance(prior_state, dict) and isinstance(prior_state.get("project_knowledge_index"), dict)
        else {}
    )
    known_targets = _unique_strings(prior_index.get("known_goal_targets"))
    certified_artifacts = _copy_string_map(prior_index.get("certified_artifacts_by_target"))
    related_milestones = _copy_string_map(prior_index.get("related_milestones_by_target"))
    implementation_matches = _copy_string_map(prior_index.get("implementation_history_by_target"))
    target = None
    if isinstance(pending_summary, dict) and isinstance(pending_summary.get("goal_mapping"), dict):
        mapping = pending_summary["goal_mapping"]
        target = str(mapping.get("goal_target") or "").strip() or None
        if target:
            known_targets = _unique_strings([*known_targets, target])
            certified_artifacts[target] = _unique_strings(
                [
                    *certified_artifacts.get(target, []),
                    *_certified_artifacts_for_goal_target(target),
                ]
            )
            related_milestones[target] = _unique_strings(
                [
                    *related_milestones.get(target, []),
                    str(guidance.get("active_milestone") or "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"),
                ]
            )
            implementation_matches[target] = _unique_strings(
                [
                    *implementation_matches.get(target, []),
                    str(mapping.get("governed_request") or mapping.get("source_goal") or ""),
                ]
            )
    return {
        "knowledge_reuse_version": ACLI_NEXT_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "knowledge_source": "deterministic_workspace_state",
        "known_goal_targets": known_targets,
        "certified_artifacts_by_target": certified_artifacts,
        "related_milestones_by_target": related_milestones,
        "implementation_history_by_target": implementation_matches,
        "implementation_history_count": len(implementation_history),
        "latest_pending_goal_target": target,
        "conversation_history_is_authority": False,
        "requires_human_approval_before_execution": True,
        "acli_next_executes_recommendation": False,
    }


def _project_knowledge_context_from_workspace(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    goal_target: str,
    governed_request: str,
) -> dict[str, Any]:
    knowledge_index = (
        workspace_state.get("project_knowledge_index")
        if isinstance(workspace_state, dict) and isinstance(workspace_state.get("project_knowledge_index"), dict)
        else {}
    )
    known_targets = set(_unique_strings(knowledge_index.get("known_goal_targets")))
    known = goal_target in known_targets
    lowered = message.lower()
    already_requested = any(term in lowered for term in ("already", "done", "implemented", "satisfied"))
    modify_requested = any(term in lowered for term in ("improve", "change", "modify", "refine", "update"))
    continue_requested = any(term in lowered for term in ("continue", "extend", "add to", "build on"))
    if known and already_requested:
        classification = "ALREADY_SATISFIED"
        new_work_required = False
        reuse_recommended = True
        reason = "The deterministic workspace already records this goal target."
    elif known and modify_requested:
        classification = "MODIFIES_EXISTING_CAPABILITY"
        new_work_required = True
        reuse_recommended = True
        reason = "The goal modifies a capability already present in the deterministic workspace."
    elif known and continue_requested:
        classification = "EXTENDS_EXISTING_MILESTONE"
        new_work_required = True
        reuse_recommended = True
        reason = "The goal extends an existing workspace milestone instead of creating unrelated work."
    elif goal_target != "general_project_goal" and _certified_artifacts_for_goal_target(goal_target):
        classification = "RELATES_TO_CERTIFIED_CAPABILITY"
        new_work_required = True
        reuse_recommended = True
        reason = "Certified artifacts already describe the related capability family."
    else:
        classification = "NEW_GOVERNED_WORK"
        new_work_required = True
        reuse_recommended = False
        reason = "No deterministic workspace match was found for this goal target."
    artifacts_by_target = (
        knowledge_index.get("certified_artifacts_by_target")
        if isinstance(knowledge_index.get("certified_artifacts_by_target"), dict)
        else {}
    )
    artifacts = _unique_strings(
        [
            *artifacts_by_target.get(goal_target, []),
            *_certified_artifacts_for_goal_target(goal_target),
        ]
    )
    milestones = _unique_strings(
        knowledge_index.get("related_milestones_by_target", {}).get(goal_target, [])
        if isinstance(knowledge_index.get("related_milestones_by_target"), dict)
        else []
    )
    history_matches = _unique_strings(
        knowledge_index.get("implementation_history_by_target", {}).get(goal_target, [])
        if isinstance(knowledge_index.get("implementation_history_by_target"), dict)
        else []
    )
    return {
        "knowledge_reuse_version": ACLI_NEXT_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "workspace_inspected": True,
        "mapping_source": "deterministic_workspace_state",
        "classification": classification,
        "goal_target": goal_target,
        "governed_request": governed_request,
        "related_milestones": milestones,
        "relevant_certified_artifacts": artifacts,
        "implementation_history_matches": history_matches,
        "reuse_recommended": reuse_recommended,
        "reuse_reason": reason,
        "new_work_required": new_work_required,
        "duplicate_work_avoided": classification == "ALREADY_SATISFIED",
        "requires_human_approval": True,
        "acli_next_executes_recommendation": False,
    }


def _certified_artifacts_for_goal_target(goal_target: str) -> list[str]:
    artifacts = {
        "github_actions": [
            "docs/governance/G14_07_GOAL_ORIENTED_DEVELOPMENT_EXPERIENCE_V1.md",
        ],
        "deployment": [
            "docs/governance/G11_00_OPERATIONAL_EXPANSION_PRIORITIZATION_REVIEW_V1.md",
        ],
        "mobile_interface": [
            "docs/governance/G14_01_UNIFIED_HUMAN_INTERFACE_ARCHITECTURE_CERTIFICATION_V1.md",
        ],
        "active_objective": [
            "docs/governance/G14_05_PERSISTENT_DEVELOPMENT_WORKSPACE_AND_PROJECT_CONTINUITY_V1.md",
        ],
    }
    return artifacts.get(goal_target, [])


def _unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values if str(value).strip()})


def _copy_string_map(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key, values in value.items():
        result[str(key)] = _unique_strings(values)
    return result


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


def _guided_development_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(("add ", "build ", "create ", "implement ", "improve ", "fix "))


def _goal_oriented_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(("i want ", "i want aigol", "let's ", "lets ", "continue "))


def _goal_mapping_from_workspace(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
) -> dict[str, Any]:
    lowered = message.lower()
    active_objective = (
        workspace_state.get("active_development_objective")
        if isinstance(workspace_state, dict)
        else None
    )
    if "github actions" in lowered:
        governed_request = "Add GitHub Actions support."
        goal_type = "EXTENDS_PROJECT"
        target = "github_actions"
    elif "deployment" in lowered:
        governed_request = "Add governed deployment workflow support."
        goal_type = "EXTENDS_PROJECT"
        target = "deployment"
    elif "mobile" in lowered:
        governed_request = "Continue the governed mobile interface."
        goal_type = "CONTINUES_PROJECT"
        target = "mobile_interface"
    elif lowered.startswith(("continue ", "let's continue", "lets continue")):
        governed_request = str(active_objective or "Continue the active governed development objective.")
        goal_type = "CONTINUES_PROJECT"
        target = "active_objective"
    else:
        governed_request = message
        goal_type = "MODIFIES_PROJECT" if active_objective else "EXTENDS_PROJECT"
        target = "general_project_goal"
    mapping = {
        "goal_mapping_status": "GOAL_MAPPED_TO_GOVERNED_REQUEST",
        "goal_type": goal_type,
        "goal_target": target,
        "source_goal": message,
        "active_workspace_objective": active_objective,
        "governed_request": governed_request,
        "mapping_source": "deterministic_workspace_state",
        "requires_human_approval": True,
        "acli_next_executes_mapping": False,
    }
    mapping["contextual_task_mapping"] = _project_knowledge_context_from_workspace(
        message=message,
        workspace_state=workspace_state,
        goal_target=target,
        governed_request=governed_request,
    )
    return mapping


def _guided_development_clarification_required(message: str) -> bool:
    lowered = message.lower()
    if not _guided_development_request_detected(message):
        return False
    specificity_terms = (
        "support",
        "workflow",
        "runtime",
        "test",
        "validation",
        "validator",
        "parser",
        "github actions",
        "governed",
        "replay",
    )
    return not any(term in lowered for term in specificity_terms)


def _guided_development_clarification(message: str) -> dict[str, Any]:
    return {
        "original_message": message,
        "clarification_required": True,
        "clarification_questions": [
            "What specific capability should AiGOL implement?",
            "What constraints or boundaries should the implementation preserve?",
        ],
    }


def _render_guided_development_clarification(clarification: dict[str, Any]) -> str:
    lines = [
        "Clarification required before governed execution.",
        f"original_request: {clarification.get('original_message')}",
        "questions:",
    ]
    lines.extend(f"- {question}" for question in clarification.get("clarification_questions", []))
    lines.append("Compose your answer and type /send.")
    return "\n".join(lines)


def _guided_development_summary(
    *,
    original_message: str,
    clarification_response: str | None,
    workspace_state: dict[str, Any] | None = None,
    goal_mapping: dict[str, Any] | None = None,
) -> dict[str, Any]:
    refined_message = original_message
    if clarification_response:
        refined_message = f"{original_message}\n\nClarification:\n{clarification_response}"
    if isinstance(goal_mapping, dict):
        refined_message = str(goal_mapping.get("governed_request") or refined_message)
    return {
        "original_message": original_message,
        "clarification_response": clarification_response,
        "goal_mapping": deepcopy(goal_mapping),
        "workspace_state_reference": (
            workspace_state.get("replay_reference") if isinstance(workspace_state, dict) else None
        ),
        "refined_message": refined_message,
        "summary_status": "IMPLEMENTATION_SUMMARY_PRESENTED",
        "runtime_after_approval": "CERTIFIED_PLATFORM_CORE_RUNTIME",
        "requires_human_confirmation": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
    }


def _render_guided_development_summary(summary: dict[str, Any]) -> str:
    lines = [
        "Governed implementation summary",
        f"original_request: {summary.get('original_message')}",
    ]
    if summary.get("clarification_response"):
        lines.extend(["clarification:", str(summary["clarification_response"])])
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
            "runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME",
            "AiGOL Next will delegate to Platform Core; it will not authorize or execute.",
            "Type /approve to continue into the certified runtime, or /cancel to discard.",
        ]
    )
    return "\n".join(lines)


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
