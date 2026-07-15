"""Reference Unified Human Interface CLI for AiGOL.

The module is intentionally small: it captures terminal input, renders
Platform Core decisions, collects approval, and delegates execution to the
certified runtime path.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
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
AICLI_SEND_COMMANDS = {"/send", "."}


RuntimeRunner = Callable[..., dict[str, Any]]
StdinReader = Callable[[], str]


def run_reference_uhi_session(
    *,
    session_id: str,
    created_at: str = DEFAULT_CREATED_AT,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    workspace: str | Path = ".",
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
    runtime_runner: RuntimeRunner | None = None,
    artifact_references: list[Any] | tuple[Any, ...] = (),
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
    output_writer(
        "aicli reference UHI session started. Type a request, /attach <reference>, "
        "/approve, /cancel, or /exit."
    )

    pending_summary: dict[str, Any] | None = None
    submitted_messages = 0
    clarification_count = 0
    approval_count = 0
    runtime_result: dict[str, Any] | None = None
    runtime_status = REFERENCE_UHI_NOT_REQUIRED
    session_status = "REFERENCE_UHI_SESSION_ACTIVE"
    last_resolution: dict[str, Any] | None = None
    last_project_context: dict[str, Any] | None = None
    pending_clarification: dict[str, Any] | None = None
    compose_buffer: list[str] = []
    pending_input_lines: list[str] = []
    submitted_request_count = 0
    multiline_request_count = 0
    canceled_compose_count = 0
    transcript: list[dict[str, Any]] = []
    output_writer("Compose a request. Finish with /send or a single '.' line. Use /cancel to clear.")

    while True:
        if pending_input_lines:
            line = pending_input_lines.pop(0)
        else:
            try:
                line = input_reader("" if compose_buffer else "aicli> ")
            except (EOFError, StopIteration):
                if compose_buffer:
                    (
                        pending_summary,
                        pending_clarification,
                        last_resolution,
                        last_project_context,
                        submitted_requests,
                        multiline_requests,
                    ) = _submit_composed_request(
                        compose_buffer=compose_buffer,
                        session=session,
                        root=root,
                        workspace_path=workspace_path,
                        created=created,
                        output_writer=output_writer,
                        transcript=transcript,
                        artifact_references=artifact_references,
                    )
                    submitted_messages += submitted_requests
                    submitted_request_count += submitted_requests
                    clarification_count += 1 if pending_clarification is not None else 0
                    multiline_request_count += multiline_requests
                    compose_buffer.clear()
                    _record_reference_workspace_state(
                        command_name="aicli",
                        session=session,
                        root=root,
                        workspace_path=workspace_path,
                        created=created,
                        session_status=session_status,
                        exit_reason="AWAITING_PLATFORM_CORE_INPUT",
                        submitted_messages=submitted_messages,
                        submitted_request_count=submitted_request_count,
                        multiline_request_count=multiline_request_count,
                        canceled_compose_count=canceled_compose_count,
                        clarification_count=clarification_count,
                        approval_count=approval_count,
                        runtime_status=runtime_status,
                        runtime_result=runtime_result,
                        last_resolution=last_resolution,
                        last_project_context=last_project_context,
                        transcript=transcript,
                        pending_clarification=pending_clarification,
                        pending_summary=pending_summary,
                    )
                if pending_summary is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_HUMAN_APPROVAL"
                    exit_reason = "EOF_AWAITING_APPROVAL"
                    output_writer("Platform Core is waiting for approval. Use /approve or /cancel.")
                    transcript.append({"event": "eof_awaiting_approval"})
                    break
                if pending_clarification is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_HUMAN_CLARIFICATION"
                    exit_reason = "EOF_AWAITING_CLARIFICATION"
                    output_writer("Platform Core is waiting for clarification. Use /send or /cancel.")
                    transcript.append({"event": "eof_awaiting_clarification"})
                    break
                session_status = "REFERENCE_UHI_SESSION_COMPLETED"
                exit_reason = "EOF"
                break
            except KeyboardInterrupt:
                if compose_buffer:
                    canceled_compose_count += 1
                    compose_buffer.clear()
                pending_summary = None
                pending_clarification = None
                output_writer("Session interrupted. Pending compose buffer canceled.")
                transcript.append({"event": "keyboard_interrupt"})
                session_status = "REFERENCE_UHI_SESSION_INTERRUPTED"
                exit_reason = "KEYBOARD_INTERRUPT"
                break
            pending_input_lines.extend(_split_input_chunk(line))
            if not pending_input_lines:
                continue
            line = pending_input_lines.pop(0)
        line_text = str(line).rstrip("\r\n")
        normalized = line_text.strip().lower()
        if not normalized and not compose_buffer:
            continue
        if normalized in {"/exit", "exit", "quit"}:
            if compose_buffer:
                output_writer("Composed request is not empty. Use /send, '.', or /cancel before exiting.")
                continue
            session_status = "REFERENCE_UHI_SESSION_COMPLETED"
            exit_reason = "EXIT_COMMAND"
            break
        if normalized == "/help":
            output_writer(_render_help())
            continue
        if normalized == "/cancel":
            if compose_buffer:
                canceled_compose_count += 1
                compose_buffer.clear()
            pending_summary = None
            pending_clarification = None
            _record_reference_workspace_state(
                command_name="aicli",
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                session_status=session_status,
                exit_reason="CANCEL_COMMAND",
                submitted_messages=submitted_messages,
                submitted_request_count=submitted_request_count,
                multiline_request_count=multiline_request_count,
                canceled_compose_count=canceled_compose_count,
                clarification_count=clarification_count,
                approval_count=approval_count,
                runtime_status=runtime_status,
                runtime_result=runtime_result,
                last_resolution=last_resolution,
                last_project_context=last_project_context,
                transcript=transcript,
                pending_clarification=pending_clarification,
                pending_summary=pending_summary,
            )
            output_writer("Pending request canceled.")
            transcript.append({"event": "cancel"})
            continue
        if normalized == "/attach" or normalized.startswith("/attach "):
            reference = line_text.strip()[len("/attach") :].strip()
            if not reference:
                output_writer("Usage: /attach <opaque-canonical-artifact-reference>")
                transcript.append({"event": "attachment_reference_missing"})
                continue
            if compose_buffer:
                output_writer(
                    "Composed request is not empty. Use /send or /cancel before attaching."
                )
                transcript.append({"event": "attachment_with_compose_buffer_rejected"})
                continue
            if pending_clarification is None:
                output_writer(
                    "No active Platform Core clarification accepts an artifact attachment."
                )
                transcript.append({"event": "attachment_without_clarification_rejected"})
                continue
            if not isinstance(
                pending_clarification.get("operational_clarification_envelope"),
                dict,
            ):
                output_writer(
                    "The active Platform Core clarification does not accept an artifact attachment."
                )
                transcript.append({"event": "attachment_for_generic_clarification_rejected"})
                continue
            output_writer(
                "Opaque artifact reference attached to the active Platform Core clarification."
            )
            try:
                (
                    pending_summary,
                    pending_clarification,
                    last_resolution,
                    last_project_context,
                    submitted_requests,
                    multiline_requests,
                ) = _submit_composed_request(
                    compose_buffer=[
                        "Opaque canonical artifact reference attached for the active "
                        "Platform Core clarification."
                    ],
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    output_writer=output_writer,
                    transcript=transcript,
                    artifact_references=(reference,),
                )
            except FailClosedRuntimeError as exc:
                output_writer(f"Platform Core rejected the artifact attachment: {exc}")
                transcript.append({"event": "attachment_failed_closed"})
                continue
            submitted_messages += submitted_requests
            submitted_request_count += submitted_requests
            clarification_count += 1 if pending_clarification is not None else 0
            multiline_request_count += multiline_requests
            transcript.append({"event": "opaque_artifact_attachment_submitted"})
            _record_reference_workspace_state(
                command_name="aicli",
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                session_status=session_status,
                exit_reason="ARTIFACT_ATTACHMENT_SUBMITTED",
                submitted_messages=submitted_messages,
                submitted_request_count=submitted_request_count,
                multiline_request_count=multiline_request_count,
                canceled_compose_count=canceled_compose_count,
                clarification_count=clarification_count,
                approval_count=approval_count,
                runtime_status=runtime_status,
                runtime_result=runtime_result,
                last_resolution=last_resolution,
                last_project_context=last_project_context,
                transcript=transcript,
                pending_clarification=pending_clarification,
                pending_summary=pending_summary,
            )
            continue
        if normalized in AICLI_SEND_COMMANDS:
            if not compose_buffer:
                output_writer("Compose buffer is empty. Add a request before submitting.")
                continue
            (
                pending_summary,
                pending_clarification,
                last_resolution,
                last_project_context,
                submitted_requests,
                multiline_requests,
            ) = _submit_composed_request(
                compose_buffer=compose_buffer,
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                output_writer=output_writer,
                transcript=transcript,
                artifact_references=artifact_references,
            )
            submitted_messages += submitted_requests
            submitted_request_count += submitted_requests
            clarification_count += 1 if pending_clarification is not None else 0
            multiline_request_count += multiline_requests
            compose_buffer.clear()
            _record_reference_workspace_state(
                command_name="aicli",
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                session_status=session_status,
                exit_reason="AWAITING_PLATFORM_CORE_INPUT",
                submitted_messages=submitted_messages,
                submitted_request_count=submitted_request_count,
                multiline_request_count=multiline_request_count,
                canceled_compose_count=canceled_compose_count,
                clarification_count=clarification_count,
                approval_count=approval_count,
                runtime_status=runtime_status,
                runtime_result=runtime_result,
                last_resolution=last_resolution,
                last_project_context=last_project_context,
                transcript=transcript,
                pending_clarification=pending_clarification,
                pending_summary=pending_summary,
            )
            continue
        if normalized == "/approve":
            if pending_summary is None and compose_buffer:
                (
                    pending_summary,
                    pending_clarification,
                    last_resolution,
                    last_project_context,
                    submitted_requests,
                    multiline_requests,
                ) = _submit_composed_request(
                    compose_buffer=compose_buffer,
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    output_writer=output_writer,
                    transcript=transcript,
                    artifact_references=artifact_references,
                )
                submitted_messages += submitted_requests
                submitted_request_count += submitted_requests
                clarification_count += 1 if pending_clarification is not None else 0
                multiline_request_count += multiline_requests
                compose_buffer.clear()
                _record_reference_workspace_state(
                    command_name="aicli",
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    session_status=session_status,
                    exit_reason="AWAITING_PLATFORM_CORE_INPUT",
                    submitted_messages=submitted_messages,
                    submitted_request_count=submitted_request_count,
                    multiline_request_count=multiline_request_count,
                    canceled_compose_count=canceled_compose_count,
                    clarification_count=clarification_count,
                    approval_count=approval_count,
                    runtime_status=runtime_status,
                    runtime_result=runtime_result,
                    last_resolution=last_resolution,
                    last_project_context=last_project_context,
                    transcript=transcript,
                    pending_clarification=pending_clarification,
                    pending_summary=pending_summary,
                )
            if pending_summary is None:
                output_writer("No governed implementation summary is pending approval.")
                transcript.append({"event": "approval_without_summary"})
                continue
            approval_count += 1
            prompt = _require_string(pending_summary["canonical_runtime_prompt"], "canonical_runtime_prompt")
            output_writer("Human approval recorded. Delegating to certified Platform Core runtime.")
            if runtime_runner is None:
                runtime_result = run_human_interface_runtime_entry(
                    interface_name="aicli",
                    session_id=session,
                    human_requests=[prompt],
                    created_at=created,
                    runtime_root=root,
                    workspace=workspace_path,
                    governed_runtime_runner=run_interactive_conversation,
                    operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
                    explicit_canonical_artifact_references=artifact_references,
                )
            else:
                runtime_result = runtime_runner(
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
            _record_reference_workspace_state(
                command_name="aicli",
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                session_status=session_status,
                exit_reason="RUNTIME_COMPLETED",
                submitted_messages=submitted_messages,
                submitted_request_count=submitted_request_count,
                multiline_request_count=multiline_request_count,
                canceled_compose_count=canceled_compose_count,
                clarification_count=clarification_count,
                approval_count=approval_count,
                runtime_status=runtime_status,
                runtime_result=runtime_result,
                last_resolution=last_resolution,
                last_project_context=last_project_context,
                transcript=transcript,
                pending_clarification=pending_clarification,
                pending_summary=pending_summary,
            )
            continue

        compose_buffer.append(line_text)

    result = {
        "command": "aicli",
        "runtime_version": REFERENCE_UHI_RUNTIME_VERSION,
        "session_id": session,
        "created_at": created,
        "runtime_root": str(root),
        "workspace": workspace_path,
        "session_status": session_status,
        "exit_reason": exit_reason,
        "submitted_message_count": submitted_messages,
        "submitted_request_count": submitted_request_count,
        "multiline_request_count": multiline_request_count,
        "unsubmitted_compose_line_count": len(compose_buffer),
        "canceled_compose_count": canceled_compose_count,
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
        "aicli_owns_artifact_resolution": False,
        "aicli_owns_artifact_validation": False,
        "aicli_owns_artifact_selection": False,
        "aicli_owns_provider_selection": False,
        "platform_core_services_delegated": True,
        "platform_core_project_services_context": last_project_context,
        "provider_platform_preserved": True,
        "worker_platform_preserved": True,
        "replay_authority_preserved": True,
    }
    if isinstance(runtime_result, dict) and runtime_result.get("project_workspace_replay_reference"):
        result["project_workspace_replay_reference"] = runtime_result["project_workspace_replay_reference"]
        result["project_workspace_hash"] = runtime_result.get("project_workspace_hash")
    else:
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


def run_reference_uhi_submit_session(
    *,
    session_id: str,
    created_at: str = DEFAULT_CREATED_AT,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    workspace: str | Path = ".",
    stdin_reader: StdinReader | None = None,
    input_reader: Callable[[str], str] | None = None,
    output_writer: Callable[[str], None] = print,
    runtime_runner: RuntimeRunner | None = None,
    artifact_references: list[Any] | tuple[Any, ...] = (),
) -> dict[str, Any]:
    """Run stdin submission and continue while Platform Core needs input."""

    session = _require_string(session_id, "session_id")
    created = _require_string(created_at, "created_at")
    root = Path(runtime_root)
    workspace_path = str(Path(workspace))
    reader = sys.stdin.read if stdin_reader is None else stdin_reader
    output_writer("Paste request below.")
    output_writer("Finish with Ctrl+D.")

    request = _normalize_submit_request(reader())
    pending_summary: dict[str, Any] | None = None
    pending_clarification: dict[str, Any] | None = None
    last_resolution: dict[str, Any] | None = None
    last_project_context: dict[str, Any] | None = None
    transcript: list[dict[str, Any]] = []
    submitted_messages = 0
    submitted_request_count = 0
    multiline_request_count = 0
    clarification_count = 0
    approval_count = 0
    canceled_compose_count = 0
    runtime_result: dict[str, Any] | None = None
    runtime_status = REFERENCE_UHI_NOT_REQUIRED
    session_status = "REFERENCE_UHI_SUBMIT_COMPLETED"
    exit_reason = "SUBMITTED"

    if request:
        (
            pending_summary,
            pending_clarification,
            last_resolution,
            last_project_context,
            submitted_requests,
            multiline_requests,
        ) = _submit_composed_request(
            compose_buffer=request.split("\n"),
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            output_writer=output_writer,
            transcript=transcript,
            artifact_references=artifact_references,
        )
        submitted_messages += submitted_requests
        submitted_request_count += submitted_requests
        clarification_count += 1 if pending_clarification is not None else 0
        multiline_request_count += multiline_requests
        _record_submit_workspace_state(
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            session_status="REFERENCE_UHI_SUBMIT_CONVERSATION_ACTIVE",
            exit_reason="AWAITING_PLATFORM_CORE_INPUT",
            submitted_messages=submitted_messages,
            submitted_request_count=submitted_request_count,
            multiline_request_count=multiline_request_count,
            canceled_compose_count=canceled_compose_count,
            clarification_count=clarification_count,
            approval_count=approval_count,
            runtime_status=runtime_status,
            runtime_result=runtime_result,
            last_resolution=last_resolution,
            last_project_context=last_project_context,
            transcript=transcript,
            pending_clarification=pending_clarification,
            pending_summary=pending_summary,
        )
    else:
        output_writer("No request submitted. Submit mode received empty input.")
        session_status = "REFERENCE_UHI_SUBMIT_REJECTED_EMPTY_INPUT"
        exit_reason = "EMPTY_INPUT"
        transcript.append({"event": "empty_submit_rejected"})

    while request and (pending_clarification is not None or pending_summary is not None):
        if input_reader is None:
            session_status = "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
            exit_reason = "AWAITING_HUMAN_INPUT"
            break
        if pending_clarification is not None:
            reply_text, reply_status = _read_clarification_reply(
                input_reader=input_reader,
            )
            if reply_status == "EOF":
                session_status = "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
                exit_reason = "EOF_AWAITING_CLARIFICATION"
                break
            if reply_status == "EMPTY":
                continue
            normalized_reply = reply_text.strip().lower()
            if normalized_reply == "/cancel":
                pending_clarification = None
                canceled_compose_count += 1
                session_status = "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
                exit_reason = "CANCEL_COMMAND"
                output_writer("Pending request canceled.")
                transcript.append({"event": "cancel"})
                break
            if normalized_reply in {"/exit", "exit", "quit"}:
                output_writer("Platform Core is waiting for clarification. Use /cancel to discard the request.")
                continue
            (
                pending_summary,
                pending_clarification,
                last_resolution,
                last_project_context,
                submitted_requests,
                multiline_requests,
            ) = _submit_composed_request(
                compose_buffer=reply_text.split("\n"),
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                output_writer=output_writer,
                transcript=transcript,
                artifact_references=artifact_references,
            )
            submitted_messages += submitted_requests
            submitted_request_count += submitted_requests
            clarification_count += 1 if pending_clarification is not None else 0
            multiline_request_count += multiline_requests
            _record_submit_workspace_state(
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                session_status="REFERENCE_UHI_SUBMIT_CONVERSATION_ACTIVE",
                exit_reason="AWAITING_PLATFORM_CORE_INPUT",
                submitted_messages=submitted_messages,
                submitted_request_count=submitted_request_count,
                multiline_request_count=multiline_request_count,
                canceled_compose_count=canceled_compose_count,
                clarification_count=clarification_count,
                approval_count=approval_count,
                runtime_status=runtime_status,
                runtime_result=runtime_result,
                last_resolution=last_resolution,
                last_project_context=last_project_context,
                transcript=transcript,
                pending_clarification=pending_clarification,
                pending_summary=pending_summary,
            )
            continue
        try:
            approval = input_reader("aicli approval> ")
        except (EOFError, StopIteration):
            session_status = "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
            exit_reason = "EOF_AWAITING_APPROVAL"
            break
        approval_text = str(approval).strip().lower()
        if approval_text == "/cancel":
            pending_summary = None
            canceled_compose_count += 1
            session_status = "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
            exit_reason = "CANCEL_COMMAND"
            output_writer("Pending request canceled.")
            transcript.append({"event": "cancel"})
            break
        if approval_text in {"/exit", "exit", "quit"}:
            output_writer("Platform Core is waiting for approval. Use /approve or /cancel.")
            continue
        if approval_text != "/approve":
            output_writer("Type /approve to continue, or /cancel to discard.")
            continue
        approval_count += 1
        prompt = _require_string(pending_summary["canonical_runtime_prompt"], "canonical_runtime_prompt")
        output_writer("Human approval recorded. Delegating to certified Platform Core runtime.")
        if runtime_runner is None:
            runtime_result = run_human_interface_runtime_entry(
                interface_name="aicli",
                session_id=session,
                human_requests=[prompt],
                created_at=created,
                runtime_root=root,
                workspace=workspace_path,
                governed_runtime_runner=run_interactive_conversation,
                operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
                explicit_canonical_artifact_references=artifact_references,
            )
        else:
            runtime_result = runtime_runner(
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
        session_status = "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
        exit_reason = "RUNTIME_COMPLETED"
        transcript.append({"event": "approved", "runtime_status": runtime_status})
        break

    result = {
        "command": "aicli submit",
        "runtime_version": REFERENCE_UHI_RUNTIME_VERSION,
        "session_id": session,
        "created_at": created,
        "runtime_root": str(root),
        "workspace": workspace_path,
        "session_status": session_status,
        "exit_reason": exit_reason,
        "submitted_message_count": submitted_messages,
        "submitted_request_count": submitted_request_count,
        "multiline_request_count": multiline_request_count,
        "unsubmitted_compose_line_count": 0,
        "canceled_compose_count": canceled_compose_count,
        "canceled_conversation_count": canceled_compose_count,
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
        "aicli_owns_artifact_resolution": False,
        "aicli_owns_artifact_validation": False,
        "aicli_owns_artifact_selection": False,
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


def _reference_runtime_status(runtime_result: dict[str, Any]) -> str:
    if runtime_result.get("runtime_binding_status") == REFERENCE_UHI_BOUND:
        return REFERENCE_UHI_BOUND
    if runtime_result.get("canonical_runtime_entry_status") == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND:
        return REFERENCE_UHI_BOUND
    if runtime_result.get("canonical_runtime_entry_status") == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED:
        return REFERENCE_UHI_NOT_REQUIRED
    return REFERENCE_UHI_PARTIALLY_BOUND


def _read_clarification_reply(
    *,
    input_reader: Callable[[str], str],
) -> tuple[str, str]:
    """Read one composed clarification reply from terminal input."""

    reply_buffer: list[str] = []
    pending_lines: list[str] = []
    while True:
        if pending_lines:
            line = pending_lines.pop(0)
        else:
            try:
                line = input_reader("aicli clarification> " if not reply_buffer else "")
            except (EOFError, StopIteration):
                return "", "EOF"
            pending_lines.extend(_split_input_chunk(line))
            if not pending_lines:
                continue
            line = pending_lines.pop(0)
        line_text = str(line).rstrip("\r\n")
        normalized = line_text.strip().lower()
        if not normalized and not reply_buffer:
            continue
        if normalized == "/cancel":
            if not reply_buffer:
                return "/cancel", "CANCEL"
            reply_buffer.clear()
            return "/cancel", "CANCEL"
        if normalized in {"/exit", "exit", "quit"}:
            return normalized, "EXIT"
        if normalized in AICLI_SEND_COMMANDS:
            if not reply_buffer:
                return "", "EMPTY"
            return "\n".join(reply_buffer), "SUBMITTED"
        reply_buffer.append(line_text)


def _record_submit_workspace_state(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    session_status: str,
    exit_reason: str,
    submitted_messages: int,
    submitted_request_count: int,
    multiline_request_count: int,
    canceled_compose_count: int,
    clarification_count: int,
    approval_count: int,
    runtime_status: str,
    runtime_result: dict[str, Any] | None,
    last_resolution: dict[str, Any] | None,
    last_project_context: dict[str, Any] | None,
    transcript: list[dict[str, Any]],
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    return _record_reference_workspace_state(
        command_name="aicli submit",
        session=session,
        root=root,
        workspace_path=workspace_path,
        created=created,
        session_status=session_status,
        exit_reason=exit_reason,
        submitted_messages=submitted_messages,
        submitted_request_count=submitted_request_count,
        multiline_request_count=multiline_request_count,
        canceled_compose_count=canceled_compose_count,
        clarification_count=clarification_count,
        approval_count=approval_count,
        runtime_status=runtime_status,
        runtime_result=runtime_result,
        last_resolution=last_resolution,
        last_project_context=last_project_context,
        transcript=transcript,
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
    )


def _record_reference_workspace_state(
    *,
    command_name: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    session_status: str,
    exit_reason: str,
    submitted_messages: int,
    submitted_request_count: int,
    multiline_request_count: int,
    canceled_compose_count: int,
    clarification_count: int,
    approval_count: int,
    runtime_status: str,
    runtime_result: dict[str, Any] | None,
    last_resolution: dict[str, Any] | None,
    last_project_context: dict[str, Any] | None,
    transcript: list[dict[str, Any]],
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    completion = {
        "command": command_name,
        "runtime_version": REFERENCE_UHI_RUNTIME_VERSION,
        "session_id": session,
        "created_at": created,
        "runtime_root": str(root),
        "workspace": workspace_path,
        "session_status": session_status,
        "exit_reason": exit_reason,
        "submitted_message_count": submitted_messages,
        "submitted_request_count": submitted_request_count,
        "multiline_request_count": multiline_request_count,
        "unsubmitted_compose_line_count": 0,
        "canceled_compose_count": canceled_compose_count,
        "canceled_conversation_count": canceled_compose_count,
        "clarification_question_count": clarification_count,
        "approval_count": approval_count,
        "pending_approval": pending_summary is not None,
        "runtime_status": runtime_status,
        "runtime_entered": runtime_result is not None,
        "runtime_result": runtime_result,
        "development_intent_resolution": last_resolution,
        "transcript": list(transcript),
        "aicli_authorizes": False,
        "aicli_executes": False,
        "aicli_owns_replay": False,
        "aicli_owns_workspace": False,
        "aicli_owns_goal_mapping": False,
        "aicli_owns_artifact_resolution": False,
        "aicli_owns_artifact_validation": False,
        "aicli_owns_artifact_selection": False,
        "aicli_owns_provider_selection": False,
        "platform_core_services_delegated": True,
        "platform_core_project_services_context": last_project_context,
        "provider_platform_preserved": True,
        "worker_platform_preserved": True,
        "replay_authority_preserved": True,
    }
    return record_unified_human_interface_workspace_state(
        interface_name="aicli",
        session_id=session,
        runtime_root=root,
        workspace=workspace_path,
        created_at=created,
        completion=completion,
        turn_results=[runtime_result] if isinstance(runtime_result, dict) else [],
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
    )


def _split_input_chunk(line: Any) -> list[str]:
    text = str(line)
    if "\n" not in text and "\r" not in text:
        return [text]
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _normalize_submit_request(raw_request: Any) -> str:
    text = str(raw_request).replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def _submit_composed_request(
    *,
    compose_buffer: list[str],
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    output_writer: Callable[[str], None],
    transcript: list[dict[str, Any]],
    artifact_references: list[Any] | tuple[Any, ...] = (),
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any], dict[str, Any], int, int]:
    message = "\n".join(compose_buffer)
    project_context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session,
        message=message,
        runtime_root=root,
        workspace=workspace_path,
        created_at=created,
        explicit_canonical_artifact_references=artifact_references,
    )
    output_writer("Request submitted to Platform Core.")
    output_writer(_render_project_context(project_context))
    resolution = project_context["development_intent_resolution"]
    conversation = (
        project_context.get("human_conversation_experience")
        if isinstance(project_context.get("human_conversation_experience"), dict)
        else {}
    )
    transcript.append(
        {
            "event": "message",
            "line_count": len(compose_buffer),
            "summary_admissible": resolution.get("summary_admissible"),
            "clarification_required": resolution.get("clarification_required"),
            "conversation_response_mode": conversation.get("response_mode"),
            "project_context_reference": project_context.get("replay_reference"),
        }
    )
    multiline_requests = 1 if len(compose_buffer) > 1 else 0
    if conversation.get("artifact_attachment_retry_eligible") is True:
        output_writer(_render_read_only_result(conversation))
        clarification = _clarification_from_conversation(
            str(
                conversation.get("artifact_attachment_retry_original_message")
                or message
            ),
            conversation,
        )
        output_writer(_render_clarification(clarification))
        return None, clarification, resolution, project_context, 1, multiline_requests
    if resolution.get("clarification_required") is True or conversation.get("response_mode") == "CLARIFICATION":
        operational_envelope = conversation.get(
            "operational_clarification_envelope"
        )
        original_message = (
            operational_envelope.get("original_message")
            if isinstance(operational_envelope, dict)
            and isinstance(operational_envelope.get("original_message"), str)
            else message
        )
        clarification = _clarification_from_conversation(
            original_message,
            conversation,
        )
        output_writer(_render_clarification(clarification))
        return None, clarification, resolution, project_context, 1, multiline_requests
    if resolution.get("summary_admissible") is True:
        summary = _summary_from_conversation(conversation)
        output_writer(_render_summary(summary))
        return summary, None, resolution, project_context, 1, multiline_requests
    if conversation.get("response_mode") == "READ_ONLY_RESULT":
        output_writer(_render_read_only_result(conversation))
        return None, None, resolution, project_context, 1, multiline_requests
    output_writer(_render_non_development_response(conversation))
    return None, None, resolution, project_context, 1, multiline_requests


def _summary_from_conversation(conversation: dict[str, Any]) -> dict[str, Any]:
    summary = conversation.get("approval_summary")
    if not isinstance(summary, dict):
        raise ValueError("Platform Core approval_summary is required")
    return dict(summary)


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
    conversation = (
        project_context.get("human_conversation_experience")
        if isinstance(project_context.get("human_conversation_experience"), dict)
        else {}
    )
    turn = (
        project_context.get("operational_turn_binding")
        if isinstance(project_context.get("operational_turn_binding"), dict)
        else {}
    )
    lines = [
            "Platform Core project context",
            f"status: {conversation.get('user_headline')}",
            f"next_step: {conversation.get('recommended_next_user_action')}",
            f"project_workspace_restored: {project_context.get('project_workspace_restored')}",
            f"project_workspace_authority: {project_context.get('project_workspace_authority')}",
            f"project_guidance_authority: {project_context.get('project_guidance_authority')}",
            f"project_knowledge_reuse_authority: {project_context.get('project_knowledge_reuse_authority')}",
            f"recommended_next_governed_action: {guidance.get('recommended_next_governed_action')}",
    ]
    if turn.get("turn_kind") == "OPERATIONAL_PLATFORM_QUERY":
        lines.extend(
            [
                "operational_turn_classification: PLATFORM_QUERY",
                f"selected_query_class: {turn.get('selected_query_class')}",
                f"selected_service: {turn.get('selected_service')}",
            ]
        )
    else:
        lines.extend(
            [
                f"knowledge_reuse_classification: {knowledge.get('classification')}",
                f"reuse_recommended: {knowledge.get('reuse_recommended')}",
            ]
        )
    return "\n".join(lines)


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
        "operational_clarification_envelope": (
            dict(conversation["operational_clarification_envelope"])
            if isinstance(conversation.get("operational_clarification_envelope"), dict)
            else None
        ),
        "artifact_attachment_retry_state": (
            dict(conversation["artifact_attachment_retry_state"])
            if isinstance(conversation.get("artifact_attachment_retry_state"), dict)
            else None
        ),
    }


def _render_summary(summary: dict[str, Any]) -> str:
    lines = [
        str(summary.get("summary_title") or "Governed implementation summary"),
        f"original_request: {summary.get('original_request')}",
        f"runtime_after_approval: {summary.get('runtime_after_approval')}",
        str(summary.get("approval_explanation")),
        "Type /approve to continue, or /cancel to discard.",
    ]
    return "\n".join(lines)


def _render_clarification(clarification: dict[str, Any]) -> str:
    lines = [
        "Clarification required before governed execution.",
        f"original_request: {clarification.get('original_message')}",
    ]
    if clarification.get("user_headline"):
        lines.append(str(clarification["user_headline"]))
    if clarification.get("user_explanation"):
        lines.append(str(clarification["user_explanation"]))
    retry_state = clarification.get("artifact_attachment_retry_state")
    if isinstance(retry_state, dict) and retry_state.get("retry_eligible") is True:
        lines.append(
            "The artifact attachment failed closed. The original Platform Core "
            "clarification remains active for another /attach attempt."
        )
        lines.append(f"attachment_attempt: {retry_state.get('attempt_number')}")
    lines.append("questions:")
    for question in clarification.get("clarification_questions", []):
        lines.append(f"- {question}")
    lines.append("Finish with /send or a single '.' line. Use /cancel to discard.")
    return "\n".join(lines)


def _render_non_development_response(conversation: dict[str, Any]) -> str:
    response = conversation.get("fail_closed_response")
    if not isinstance(response, dict):
        raise ValueError("Platform Core fail_closed_response is required")
    return "\n".join(
        [
            str(response.get("response_title") or "No governed implementation summary was produced."),
            f"reason: {response.get('reason')}",
            str(response.get("fail_closed_explanation")),
            f"next_step: {response.get('recommended_next_user_action')}",
        ]
    )


def _render_read_only_result(conversation: dict[str, Any]) -> str:
    result = conversation.get("governed_read_only_work_result")
    if not isinstance(result, dict):
        raise ValueError("Platform Core governed_read_only_work_result is required")
    return "\n".join(
        [
            "Governed read-only result",
            f"work_type: {result.get('work_type')}",
            f"binding_status: {result.get('binding_status')}",
            f"selected_service: {result.get('selected_read_only_service')}",
            f"presentation_status: {result.get('presentation_status')}",
            str(result.get("presentation_summary")),
            f"provider_invoked: {result.get('provider_invoked')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"result_hash: {result.get('artifact_hash')}",
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
    title = (
        "aicli session awaiting human input."
        if "_AWAITING_" in str(result.get("session_status"))
        else "aicli session closed."
    )
    return "\n".join(
        [
            title,
            f"session_id: {result.get('session_id')}",
            f"session_status: {result.get('session_status')}",
            f"exit_reason: {result.get('exit_reason')}",
            f"pending_approval: {result.get('pending_approval')}",
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
            "/send - submit the composed request",
            ". - submit the composed request",
            "/attach <reference> - attach one opaque artifact to the active clarification",
            "/approve - approve the pending governed implementation summary",
            "/cancel - clear the compose buffer or discard the pending summary",
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
    parser.add_argument(
        "--artifact-reference",
        action="append",
        default=[],
        help="Transport one opaque canonical Replay wrapper reference to Platform Core.",
    )
    parser.add_argument("mode", nargs="?", choices=("submit",), help="Use stdin one-shot submission mode.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "submit":
        run_reference_uhi_submit_session(
            session_id=args.session_id,
            created_at=args.created_at,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            input_reader=input,
            artifact_references=args.artifact_reference,
        )
        return 0
    run_reference_uhi_session(
        session_id=args.session_id,
        created_at=args.created_at,
        runtime_root=args.runtime_root,
        workspace=args.workspace,
        artifact_references=args.artifact_reference,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
