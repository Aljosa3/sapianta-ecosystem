"""Reference Unified Human Interface CLI for AiGOL.

The module is intentionally small: it captures terminal input, renders
Platform Core decisions, collects approval, and delegates execution to the
certified runtime path.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.platform_core_project_services import (
    guided_development_clarification,
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
)


REFERENCE_UHI_RUNTIME_VERSION = "G14_22_REFERENCE_UNIFIED_HUMAN_INTERFACE_IMPLEMENTATION_V1"
REFERENCE_UHI_BOUND = "REFERENCE_UHI_RUNTIME_BOUND"
REFERENCE_UHI_PARTIALLY_BOUND = "REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND"
REFERENCE_UHI_NOT_REQUIRED = "REFERENCE_UHI_RUNTIME_NOT_REQUIRED"
DEFAULT_CREATED_AT = "2026-07-04T00:00:00Z"
DEFAULT_RUNTIME_ROOT = ".runtime/aicli"


RuntimeRunner = Callable[..., dict[str, Any]]


def run_reference_uhi_session(
    *,
    session_id: str,
    created_at: str = DEFAULT_CREATED_AT,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    workspace: str | Path = ".",
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
    runtime_runner: RuntimeRunner | None = None,
) -> dict[str, Any]:
    """Run the reference UHI session.

    Local state is limited to interface interaction state: pending approval,
    message count, and rendered summaries. All semantic decisions are read from
    Platform Core service artifacts.
    """

    session = _require_string(session_id, "session_id")
    created = _require_string(created_at, "created_at")
    root = Path(runtime_root)
    workspace_path = str(Path(workspace))
    runner = runtime_runner or _run_certified_runtime
    output_writer("aicli reference UHI session started. Type a request, /approve, /cancel, or /exit.")

    pending_summary: dict[str, Any] | None = None
    submitted_messages = 0
    clarification_count = 0
    approval_count = 0
    runtime_result: dict[str, Any] | None = None
    runtime_status = REFERENCE_UHI_NOT_REQUIRED
    last_resolution: dict[str, Any] | None = None
    last_project_context: dict[str, Any] | None = None
    pending_clarification: dict[str, Any] | None = None
    transcript: list[dict[str, Any]] = []

    while True:
        try:
            line = input_reader("aicli> ")
        except EOFError:
            exit_reason = "EOF"
            break
        message = str(line).strip()
        if not message:
            continue
        normalized = message.lower()
        if normalized in {"/exit", "exit", "quit"}:
            exit_reason = "EXIT_COMMAND"
            break
        if normalized == "/help":
            output_writer(_render_help())
            continue
        if normalized == "/cancel":
            pending_summary = None
            pending_clarification = None
            output_writer("Pending request canceled.")
            transcript.append({"event": "cancel"})
            continue
        if normalized == "/approve":
            if pending_summary is None:
                output_writer("No governed implementation summary is pending approval.")
                transcript.append({"event": "approval_without_summary"})
                continue
            approval_count += 1
            prompt = _require_string(pending_summary["canonical_runtime_prompt"], "canonical_runtime_prompt")
            output_writer("Human approval recorded. Delegating to certified Platform Core runtime.")
            runtime_result = runner(
                session_id=session,
                prompt=prompt,
                created_at=created,
                runtime_root=root,
                workspace=workspace_path,
            )
            runtime_status = _reference_runtime_status(runtime_result)
            output_writer(_render_runtime_result(runtime_result, runtime_status))
            pending_summary = None
            pending_clarification = None
            transcript.append({"event": "approved", "runtime_status": runtime_status})
            continue

        submitted_messages += 1
        project_context = prepare_unified_human_interface_project_context(
            interface_name="aicli",
            session_id=session,
            message=message,
            runtime_root=root,
            workspace=workspace_path,
            created_at=created,
        )
        last_project_context = project_context
        output_writer(_render_project_context(project_context))
        resolution = project_context["development_intent_resolution"]
        last_resolution = resolution
        transcript.append(
            {
                "event": "message",
                "summary_admissible": resolution.get("summary_admissible"),
                "clarification_required": resolution.get("clarification_required"),
                "project_context_reference": project_context.get("replay_reference"),
            }
        )
        if resolution.get("clarification_required") is True:
            clarification_count += 1
            clarification = guided_development_clarification(message)
            pending_clarification = clarification
            output_writer(_render_clarification(clarification))
            continue
        if resolution.get("summary_admissible") is True:
            pending_summary = _summary_from_resolution(resolution)
            pending_clarification = None
            output_writer(_render_summary(pending_summary))
            continue
        output_writer(_render_non_development_resolution(resolution))

    result = {
        "command": "aicli",
        "runtime_version": REFERENCE_UHI_RUNTIME_VERSION,
        "session_id": session,
        "created_at": created,
        "runtime_root": str(root),
        "workspace": workspace_path,
        "session_status": "REFERENCE_UHI_SESSION_COMPLETED",
        "exit_reason": exit_reason,
        "submitted_message_count": submitted_messages,
        "clarification_question_count": clarification_count,
        "approval_count": approval_count,
        "pending_approval": pending_summary is not None,
        "runtime_status": runtime_status,
        "runtime_entered": runtime_result is not None,
        "runtime_result": runtime_result,
        "development_intent_resolution": last_resolution,
        "transcript": transcript,
        "aicli_authorizes": False,
        "aicli_executes": False,
        "aicli_owns_replay": False,
        "aicli_owns_workspace": False,
        "aicli_owns_goal_mapping": False,
        "aicli_owns_provider_selection": False,
        "platform_core_services_delegated": True,
        "platform_core_project_services_context": last_project_context,
        "provider_platform_preserved": True,
        "worker_platform_preserved": True,
        "replay_authority_preserved": True,
    }
    workspace_state = record_unified_human_interface_workspace_state(
        interface_name="aicli",
        session_id=session,
        runtime_root=root,
        workspace=workspace_path,
        created_at=created,
        completion=result,
        turn_results=[runtime_result] if isinstance(runtime_result, dict) else [],
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
    )
    result["project_workspace_replay_reference"] = workspace_state["replay_reference"]
    result["project_workspace_hash"] = workspace_state["artifact_hash"]
    output_writer(_render_session_result(result))
    return result


def _run_certified_runtime(
    *,
    session_id: str,
    prompt: str,
    created_at: str,
    runtime_root: str | Path,
    workspace: str,
) -> dict[str, Any]:
    conversation_args = argparse.Namespace(
        session_id=session_id,
        created_at=created_at,
        runtime_root=str(runtime_root),
        workspace=workspace,
        operator_context="REFERENCE_UHI_RUNTIME",
        auto_continue=True,
        enable_llm_assisted_explanation=False,
        llm_explanation_provider_id="UNSPECIFIED_EXPLANATION_PROVIDER",
    )
    output: list[str] = []
    conversation_result = run_interactive_conversation(
        conversation_args,
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )
    latest_turn = _latest_turn(conversation_result)
    binding_status = _runtime_binding_status(conversation_result, latest_turn)
    return {
        "runtime_binding_status": binding_status,
        "runtime_entered": True,
        "runtime_command": conversation_result.get("command"),
        "runtime_root": conversation_result.get("runtime_root"),
        "runtime_turn_count": conversation_result.get("turn_count"),
        "runtime_failed_turns": conversation_result.get("failed_turns"),
        "runtime_exit_reason": conversation_result.get("exit_reason"),
        "governance_authorization_reached": latest_turn.get("execution_authorization_status") == "EXECUTION_AUTHORIZED",
        "provider_invocation_reached": latest_turn.get("openai_provider_reached") is True
        or latest_turn.get("provider_invoked") is True,
        "worker_execution_reached": latest_turn.get("worker_invoked") is True,
        "replay_certification_reached": latest_turn.get("replay_certification_reached") is True,
        "execution_plan_status": latest_turn.get("execution_preparation_status"),
        "worker_assignment_status": latest_turn.get("worker_assignment_status"),
        "worker_dispatch_status": latest_turn.get("worker_dispatch_status"),
        "worker_invocation_status": latest_turn.get("worker_invocation_status"),
        "result_validation_status": latest_turn.get("result_validation_status"),
        "replay_certification_status": latest_turn.get("replay_certification_status"),
        "runtime_replay_reference": latest_turn.get("replay_reference") or latest_turn.get("conversation_replay_reference"),
        "conversation_output_tail": output[-12:],
        "platform_core_runtime_delegated": True,
        "governance_authority_preserved": True,
        "provider_platform_preserved": True,
        "worker_execution_authority_preserved": True,
        "replay_authority_preserved": True,
    }


def _reference_runtime_status(runtime_result: dict[str, Any]) -> str:
    if runtime_result.get("runtime_binding_status") == REFERENCE_UHI_BOUND:
        return REFERENCE_UHI_BOUND
    return REFERENCE_UHI_PARTIALLY_BOUND


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


def _runtime_binding_status(conversation_result: dict[str, Any], turn: dict[str, Any]) -> str:
    if (
        conversation_result.get("failed_turns") == 0
        and turn.get("worker_invoked") is True
        and turn.get("replay_certification_reached") is True
    ):
        return REFERENCE_UHI_BOUND
    return REFERENCE_UHI_PARTIALLY_BOUND


def _summary_from_resolution(resolution: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_type": "GOVERNED_IMPLEMENTATION_SUMMARY",
        "summary_authority": "PLATFORM_CORE",
        "original_request": resolution["raw_prompt"],
        "canonical_runtime_prompt": resolution["canonical_runtime_prompt"],
        "goal_mapping": resolution.get("goal_mapping"),
        "requires_human_approval": resolution.get("requires_human_approval") is True,
        "runtime_after_approval": "CERTIFIED_PLATFORM_CORE_RUNTIME",
        "aicli_authorizes": False,
        "aicli_executes": False,
    }


def _render_project_context(project_context: dict[str, Any]) -> str:
    guidance = (
        project_context.get("project_guidance")
        if isinstance(project_context.get("project_guidance"), dict)
        else {}
    )
    knowledge = (
        project_context.get("knowledge_reuse")
        if isinstance(project_context.get("knowledge_reuse"), dict)
        else {}
    )
    return "\n".join(
        [
            "Platform Core project context",
            f"project_workspace_restored: {project_context.get('project_workspace_restored')}",
            f"project_workspace_authority: {project_context.get('project_workspace_authority')}",
            f"project_guidance_authority: {project_context.get('project_guidance_authority')}",
            f"project_knowledge_reuse_authority: {project_context.get('project_knowledge_reuse_authority')}",
            f"recommended_next_governed_action: {guidance.get('recommended_next_governed_action')}",
            f"knowledge_reuse_classification: {knowledge.get('classification')}",
            f"reuse_recommended: {knowledge.get('reuse_recommended')}",
        ]
    )


def _render_summary(summary: dict[str, Any]) -> str:
    lines = [
        "Governed implementation summary",
        f"original_request: {summary.get('original_request')}",
        f"runtime_after_approval: {summary.get('runtime_after_approval')}",
        "aicli will delegate to Platform Core; it will not authorize or execute.",
        "Type /approve to continue, or /cancel to discard.",
    ]
    return "\n".join(lines)


def _render_clarification(clarification: dict[str, Any]) -> str:
    lines = [
        "Clarification required before governed execution.",
        f"original_request: {clarification.get('original_message')}",
        "questions:",
    ]
    for question in clarification.get("clarification_questions", []):
        lines.append(f"- {question}")
    return "\n".join(lines)


def _render_non_development_resolution(resolution: dict[str, Any]) -> str:
    return "\n".join(
        [
            "No governed implementation summary was produced.",
            f"reason: {resolution.get('clarification_reason')}",
            "aicli performed no routing or execution.",
        ]
    )


def _render_runtime_result(runtime_result: dict[str, Any], runtime_status: str) -> str:
    return "\n".join(
        [
            "Certified runtime result",
            f"runtime_status: {runtime_status}",
            f"governance_authorization_reached: {runtime_result.get('governance_authorization_reached')}",
            f"provider_invocation_reached: {runtime_result.get('provider_invocation_reached')}",
            f"worker_execution_reached: {runtime_result.get('worker_execution_reached')}",
            f"replay_certification_reached: {runtime_result.get('replay_certification_reached')}",
            f"runtime_replay_reference: {runtime_result.get('runtime_replay_reference')}",
        ]
    )


def _render_session_result(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "aicli session closed.",
            f"session_id: {result.get('session_id')}",
            f"runtime_status: {result.get('runtime_status')}",
            f"submitted_message_count: {result.get('submitted_message_count')}",
            f"approval_count: {result.get('approval_count')}",
            f"aicli_authorizes: {result.get('aicli_authorizes')}",
            f"aicli_executes: {result.get('aicli_executes')}",
            f"aicli_owns_replay: {result.get('aicli_owns_replay')}",
        ]
    )


def _render_help() -> str:
    return "\n".join(
        [
            "Commands:",
            "/approve - approve the pending governed implementation summary",
            "/cancel - discard the pending summary",
            "/exit - close the reference UHI session",
        ]
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aicli", description="Reference AiGOL Unified Human Interface")
    parser.add_argument("--session-id", default="AICLI-REFERENCE-SESSION")
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--runtime-root", default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--workspace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_reference_uhi_session(
        session_id=args.session_id,
        created_at=args.created_at,
        runtime_root=args.runtime_root,
        workspace=args.workspace,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
