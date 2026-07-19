"""Reference Unified Human Interface CLI for AiGOL.

The module is intentionally small: it captures terminal input, renders
Platform Core decisions, collects approval, and delegates execution to the
certified runtime path.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
    run_human_interface_runtime_entry,
)
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_APPROVED,
    EXECUTION_DECISION_REJECTED,
    bind_distinct_human_execution_decision,
    render_distinct_human_execution_decision,
)
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    authorize_confirmed_grounded_execution_decision,
    render_authorized_grounded_worker_selection,
    select_authorized_grounded_worker,
)
from aigol.runtime.execution_authorization_runtime import render_execution_authorization_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import worker_assignment_runtime as worker_assignment
from aigol.runtime import worker_dispatch_runtime as worker_dispatch
from aigol.runtime import worker_invocation_runtime as worker_invocation
from aigol.runtime import worker_invocation_to_execution_candidate_bridge_runtime as worker_candidate
from aigol.runtime import governed_worker_execution_runtime as governed_execution
from aigol.runtime import codex_worker_activation_binding_runtime as worker_activation
from aigol.runtime import codex_transport_to_worker_result_capture_binding_runtime as codex_result
from aigol.runtime import codex_worker_result_to_semantic_validation_binding_runtime as codex_validation
from aigol.runtime import codex_task_outcome_human_review_runtime as codex_task_review
from aigol.runtime import codex_satisfied_outcome_disposable_validation_binding_runtime as disposable_validation
from aigol.runtime import codex_replacement_acceptance_prerequisite_binding_runtime as replacement_prerequisites
from aigol.runtime import human_decision_runtime as human_decision
from aigol.runtime import worker_invocation_request_runtime as worker_request
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
    worker_process_runner: Callable[..., Any] | None = None,
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
        "/approve, /satisfied, /unsatisfied, /rework, /cancel, or /exit."
    )

    pending_summary: dict[str, Any] | None = None
    pending_execution_review: dict[str, Any] | None = None
    pending_activation_review: dict[str, Any] | None = None
    pending_task_outcome_review: dict[str, Any] | None = None
    pending_disposable_patch_validation_review: dict[str, Any] | None = None
    pending_content_acceptance_context: dict[str, Any] | None = None
    submitted_messages = 0
    clarification_count = 0
    approval_count = 0
    human_task_outcome_decision_count = 0
    runtime_result: dict[str, Any] | None = None
    runtime_status = REFERENCE_UHI_NOT_REQUIRED
    session_status = "REFERENCE_UHI_SESSION_ACTIVE"
    last_resolution: dict[str, Any] | None = None
    last_project_context: dict[str, Any] | None = None
    synthesis_preflight_capture: dict[str, Any] | None = None
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
                        synthesis_preflight_capture,
                    ) = _submit_composed_request(
                        compose_buffer=compose_buffer,
                        session=session,
                        root=root,
                        workspace_path=workspace_path,
                        created=created,
                        output_writer=output_writer,
                        transcript=transcript,
                        artifact_references=artifact_references,
                        codex_activation_preflight_required=runtime_runner is None,
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
                if pending_content_acceptance_context is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_CONTENT_ACCEPTANCE_DECISION"
                    exit_reason = "EOF_AWAITING_CONTENT_ACCEPTANCE_DECISION"
                    output_writer("Validated content is awaiting /accept or /reject.")
                    transcript.append({"event": "eof_awaiting_content_acceptance_decision"})
                    break
                if pending_disposable_patch_validation_review is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_DISPOSABLE_PATCH_VALIDATION_DECISION"
                    exit_reason = "EOF_AWAITING_DISPOSABLE_PATCH_VALIDATION_DECISION"
                    output_writer(
                        "Platform Core is waiting for the disposable patch-validation decision. "
                        "Use /approve or /cancel."
                    )
                    transcript.append({"event": "eof_awaiting_disposable_patch_validation_decision"})
                    break
                if pending_task_outcome_review is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_TASK_OUTCOME_DECISION"
                    exit_reason = "EOF_AWAITING_TASK_OUTCOME_DECISION"
                    output_writer(
                        "Platform Core is waiting for the task-outcome human decision. "
                        "Use /satisfied, /unsatisfied, or /rework."
                    )
                    transcript.append({"event": "eof_awaiting_task_outcome_decision"})
                    break
                if pending_activation_review is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_WORKER_ACTIVATION_DECISION"
                    exit_reason = "EOF_AWAITING_WORKER_ACTIVATION_DECISION"
                    output_writer(
                        "Platform Core is waiting for the bounded Worker activation decision. "
                        "Use /approve or /cancel."
                    )
                    transcript.append({"event": "eof_awaiting_worker_activation_decision"})
                    break
                if pending_execution_review is not None:
                    session_status = "REFERENCE_UHI_SESSION_AWAITING_EXECUTION_DECISION"
                    exit_reason = "EOF_AWAITING_EXECUTION_DECISION"
                    output_writer(
                        "Platform Core is waiting for the distinct execution decision. "
                        "Use /approve or /cancel."
                    )
                    transcript.append({"event": "eof_awaiting_execution_decision"})
                    break
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
        if pending_content_acceptance_context is not None:
            if normalized not in {"/accept", "/reject"}:
                output_writer("Content-acceptance context accepts only /accept or /reject.")
                transcript.append({"event": "invalid_content_acceptance_response"})
                continue
            outcome = human_decision.ACCEPTED if normalized == "/accept" else human_decision.REJECTED
            capture = human_decision.record_content_acceptance_decision(
                context_capture=pending_content_acceptance_context,
                binding_capture=runtime_result["codex_replacement_acceptance_prerequisite_binding_capture"],
                decision_outcome=outcome, decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=created,
                session_root=root / session,
            )
            reconstruction = human_decision.reconstruct_content_acceptance_decision_replay(
                decision_capture=capture,
                binding_capture=runtime_result["codex_replacement_acceptance_prerequisite_binding_capture"],
                session_root=root / session,
            )
            runtime_result.update({"human_content_acceptance_decision_capture": capture,
                "human_content_acceptance_decision_reconstruction": reconstruction,
                "result_accepted": False, "mutation_authorized": False, "main_repository_mutated": False})
            output_writer(human_decision.render_content_acceptance_decision(capture))
            pending_content_acceptance_context = None
            transcript.append({"event": "human_content_acceptance_decision_recorded", "outcome": outcome})
            session_status = "REFERENCE_UHI_SESSION_COMPLETED"
            exit_reason = "HUMAN_CONTENT_ACCEPTANCE_DECISION_RECORDED"
            break
        if normalized in {"/exit", "exit", "quit"}:
            if pending_disposable_patch_validation_review is not None:
                output_writer(
                    "Platform Core is waiting for the disposable patch-validation decision. "
                    "Use /approve or /cancel."
                )
                continue
            if pending_task_outcome_review is not None:
                output_writer(
                    "Platform Core is waiting for the task-outcome human decision. "
                    "Use /satisfied, /unsatisfied, or /rework."
                )
                continue
            if pending_activation_review is not None:
                output_writer(
                    "Platform Core is waiting for the bounded Worker activation decision. "
                    "Use /approve or /cancel."
                )
                continue
            if pending_execution_review is not None:
                output_writer(
                    "Platform Core is waiting for the distinct execution decision. "
                    "Use /approve or /cancel."
                )
                continue
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
            if pending_task_outcome_review is not None:
                output_writer(
                    "Task-outcome review is pending. Use /unsatisfied or /rework to "
                    "record an explicit human outcome; /cancel records no decision."
                )
                transcript.append({"event": "task_outcome_cancel_rejected"})
                continue
            if pending_disposable_patch_validation_review is not None:
                runtime_result = _record_contextual_disposable_patch_validation_decision(
                    pending_review=pending_disposable_patch_validation_review,
                    decision=human_decision.REJECT,
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=runtime_result,
                )
                output_writer(human_decision.render_human_decision_summary(
                    runtime_result["disposable_patch_validation_human_decision_capture"]
                ))
                pending_disposable_patch_validation_review = None
                transcript.append({"event": "disposable_patch_validation_decision_rejected"})
                session_status = "REFERENCE_UHI_SESSION_COMPLETED"
                exit_reason = "DISPOSABLE_PATCH_VALIDATION_HUMAN_DECISION_RECORDED"
                break
            if pending_activation_review is not None:
                runtime_result = dict(runtime_result or {})
                runtime_result.update({
                    "worker_activation_decision_rejected": True,
                    "third_human_decision_recorded": True,
                    "worker_process_activation_allowed": False,
                    "worker_process_started": False,
                    "provider_invoked": False,
                    "semantic_worker_result_captured": False,
                    "repository_mutated": False,
                })
                pending_activation_review = None
                output_writer("Bounded CODEX Worker process activation rejected; no process started.")
                transcript.append({"event": "worker_activation_decision_rejected"})
                continue
            if pending_execution_review is not None:
                runtime_result = _record_contextual_execution_decision(
                    pending_execution_review=pending_execution_review,
                    decision="REJECT",
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=runtime_result,
                )
                output_writer(render_distinct_human_execution_decision(
                    runtime_result["execution_human_decision_result"]
                ))
                pending_execution_review = None
                transcript.append({"event": "execution_decision_rejected"})
                continue
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
                    synthesis_preflight_capture,
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
                    codex_activation_preflight_required=runtime_runner is None,
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
                synthesis_preflight_capture,
            ) = _submit_composed_request(
                compose_buffer=compose_buffer,
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                output_writer=output_writer,
                transcript=transcript,
                artifact_references=artifact_references,
                codex_activation_preflight_required=runtime_runner is None,
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
        if normalized in {"/satisfied", "/unsatisfied", "/rework"}:
            if pending_task_outcome_review is None:
                output_writer("No captured Worker task outcome is pending human review.")
                transcript.append({"event": "task_outcome_decision_without_review"})
                continue
            outcome = {
                "/satisfied": codex_task_review.TASK_OUTCOME_SATISFIED,
                "/unsatisfied": codex_task_review.TASK_OUTCOME_UNSATISFIED,
                "/rework": codex_task_review.REWORK_REQUESTED,
            }[normalized]
            runtime_result = _record_contextual_task_outcome_decision(
                pending_task_outcome_review=pending_task_outcome_review,
                task_outcome_decision=outcome,
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=runtime_result,
            )
            output_writer(codex_task_review.render_codex_task_outcome_decision(
                runtime_result["codex_task_outcome_human_decision_capture"]
            ))
            pending_task_outcome_review = None
            human_task_outcome_decision_count += 1
            transcript.append({
                "event": "task_outcome_human_decision_recorded",
                "task_outcome_decision": outcome,
            })
            if outcome == codex_task_review.TASK_OUTCOME_SATISFIED:
                try:
                    runtime_result = _prepare_contextual_disposable_patch_validation_review(
                        session=session,
                        root=root,
                        workspace_path=workspace_path,
                        created=created,
                        runtime_result=runtime_result,
                    )
                except FailClosedRuntimeError as exc:
                    runtime_result["disposable_patch_validation_review_blocked"] = True
                    runtime_result["disposable_patch_validation_review_blocker"] = str(exc)
                    output_writer(f"Disposable patch-validation review failed closed: {exc}")
                    session_status = "REFERENCE_UHI_SESSION_COMPLETED"
                    exit_reason = "TASK_OUTCOME_HUMAN_DECISION_RECORDED"
                    break
                pending_disposable_patch_validation_review = runtime_result[
                    "disposable_patch_validation_review_capture"
                ]
                output_writer(disposable_validation.render_disposable_patch_validation_review(
                    pending_disposable_patch_validation_review,
                    runtime_result["codex_task_outcome_review_capture"],
                ))
                output_writer(
                    "Disposable-only validation decision pending. Use /approve to record "
                    "APPROVE or /cancel to record REJECT. No patch or test has run."
                )
                transcript.append({"event": "disposable_patch_validation_review_prepared"})
                continue
            session_status = "REFERENCE_UHI_SESSION_COMPLETED"
            exit_reason = "TASK_OUTCOME_HUMAN_DECISION_RECORDED"
            break
        if normalized == "/approve":
            if pending_disposable_patch_validation_review is not None:
                runtime_result = _record_contextual_disposable_patch_validation_decision(
                    pending_review=pending_disposable_patch_validation_review,
                    decision=human_decision.APPROVE,
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=runtime_result,
                )
                output_writer(human_decision.render_human_decision_summary(
                    runtime_result["disposable_patch_validation_human_decision_capture"]
                ))
                pending_disposable_patch_validation_review = None
                approval_count += 1
                transcript.append({"event": "disposable_patch_validation_decision_approved"})
                runtime_result = _execute_contextual_disposable_patch_validation(
                    session=session, root=root, workspace_path=workspace_path,
                    created=created, runtime_result=runtime_result,
                )
                output_writer(disposable_validation.render_disposable_patch_validation_outcome(
                    runtime_result["disposable_patch_validation_outcome_capture"]
                ))
                transcript.append({"event": "disposable_patch_validation_outcome_recorded"})
                outcome_artifact = runtime_result[
                    "disposable_patch_validation_outcome_capture"
                ]["outcome_artifact"]
                if outcome_artifact["execution_status"] == disposable_validation.COMPLETED:
                    runtime_result = _bind_contextual_replacement_acceptance_prerequisites(
                        session=session, root=root, workspace_path=workspace_path,
                        created=created, runtime_result=runtime_result,
                    )
                    output_writer(
                        replacement_prerequisites.render_codex_replacement_acceptance_prerequisites(
                            runtime_result["codex_replacement_acceptance_prerequisite_binding_capture"],
                            runtime_result["codex_replacement_acceptance_prerequisite_binding_reconstruction"],
                        )
                    )
                    transcript.append({"event": "replacement_acceptance_prerequisites_bound"})
                    binding = runtime_result["codex_replacement_acceptance_prerequisite_binding_capture"]["binding_artifact"]
                    pending_content_acceptance_context = human_decision.prepare_content_acceptance_decision_context(
                        context_id=f"G31-CONTENT-ACCEPTANCE-{binding['artifact_hash'][-16:]}",
                        binding_capture=runtime_result["codex_replacement_acceptance_prerequisite_binding_capture"],
                        human_actor_id="HUMAN_OPERATOR_VIA_AICLI", presented_at=created,
                        session_root=root / session,
                        replay_dir=root / session / f"CONTENT-ACCEPTANCE-DECISION-{binding['artifact_hash'][-16:]}",
                    )
                    runtime_result["human_content_acceptance_context_capture"] = pending_content_acceptance_context
                    output_writer(human_decision.render_content_acceptance_decision_context(pending_content_acceptance_context))
                    transcript.append({"event": "human_content_acceptance_context_presented"})
                    continue
                else:
                    exit_reason = "DISPOSABLE_PATCH_VALIDATION_OUTCOME_RECORDED"
                session_status = "REFERENCE_UHI_SESSION_COMPLETED"
                break
            if pending_activation_review is not None:
                approval_count += 1
                runtime_result = _record_contextual_worker_activation_decision(
                    pending_activation_review=pending_activation_review,
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=runtime_result,
                    runner=worker_process_runner,
                )
                output_writer(worker_activation.render_codex_worker_activation_result(
                    runtime_result["codex_worker_activation_capture"]
                ))
                output_writer(codex_result.render_codex_worker_result_capture(
                    runtime_result["codex_worker_result_capture_binding_capture"]
                ))
                output_writer(codex_validation.render_codex_worker_semantic_validation(
                    runtime_result["codex_worker_semantic_validation_binding_capture"]
                ))
                validation = runtime_result[
                    "codex_worker_semantic_validation_binding_capture"
                ]
                if validation.get("g31_semantic_validation_status") == (
                    codex_validation.SUCCESS
                ):
                    try:
                        runtime_result = _prepare_contextual_task_outcome_review(
                            session=session,
                            root=root,
                            workspace_path=workspace_path,
                            created=created,
                            runtime_result=runtime_result,
                        )
                    except FailClosedRuntimeError as exc:
                        runtime_result["task_outcome_review_blocked"] = True
                        runtime_result["task_outcome_review_blocker"] = str(exc)
                        output_writer(
                            "Exact-byte task-outcome review failed closed: "
                            f"{exc}"
                        )
                    else:
                        pending_task_outcome_review = runtime_result[
                            "codex_task_outcome_review_capture"
                        ]
                        output_writer(codex_task_review.render_codex_task_outcome_review(
                            pending_task_outcome_review
                        ))
                        output_writer(_render_task_outcome_review_lineage(
                            pending_task_outcome_review
                        ))
                        output_writer(
                            "Exact-byte task-outcome decision pending. Use /satisfied, "
                            "/unsatisfied, or /rework. No decision accepts or applies the patch."
                        )
                else:
                    runtime_result["task_outcome_review_blocked"] = True
                    runtime_result["task_outcome_review_blocker"] = (
                        "G31 governance validation did not return RESULT_VALIDATED"
                    )
                    output_writer(
                        "Task-outcome review was not requested because G31 governance "
                        "validation did not return RESULT_VALIDATED."
                    )
                pending_activation_review = None
                transcript.append({"event": "worker_activation_decision_approved"})
                continue
            if pending_execution_review is not None:
                approval_count += 1
                runtime_result = _record_contextual_execution_decision(
                    pending_execution_review=pending_execution_review,
                    decision="APPROVE",
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=runtime_result,
                )
                output_writer(render_distinct_human_execution_decision(
                    runtime_result["execution_human_decision_result"]
                ))
                output_writer(render_execution_authorization_summary(
                    runtime_result["execution_authorization_capture"]
                ))
                output_writer(render_authorized_grounded_worker_selection(
                    runtime_result["authorized_worker_selection_capture"]))
                if runtime_result.get("worker_invocation_request_capture"):
                    output_writer(worker_request.render_worker_invocation_request_summary(runtime_result["worker_invocation_request_capture"]))
                if runtime_result.get("worker_assignment_capture"):
                    output_writer(worker_assignment.render_worker_assignment_summary(runtime_result["worker_assignment_capture"]))
                if runtime_result.get("worker_dispatch_capture"):
                    output_writer(worker_dispatch.render_worker_dispatch_summary(runtime_result["worker_dispatch_capture"]))
                if runtime_result.get("worker_invocation_capture"):
                    output_writer(worker_invocation.render_worker_invocation_summary(runtime_result["worker_invocation_capture"]))
                if runtime_result.get("worker_execution_candidate_capture"):
                    output_writer(worker_candidate.render_worker_execution_candidate_summary(
                        runtime_result["worker_execution_candidate_capture"]
                    ))
                if runtime_result.get("governed_worker_execution_capture"):
                    output_writer(governed_execution.render_governed_worker_execution_summary(
                        runtime_result["governed_worker_execution_capture"]
                    ))
                    pending_activation_review = worker_activation.prepare_codex_worker_activation_review(
                        governed_execution_capture=runtime_result["governed_worker_execution_capture"],
                        execution_candidate_capture=runtime_result["worker_execution_candidate_capture"],
                        session_root=root / session,
                        workspace=workspace_path,
                        created_at=created,
                        synthesis_preflight_capture=runtime_result.get(
                            "codex_synthesis_preflight_capture"
                        ),
                    )
                    runtime_result["codex_worker_activation_review_capture"] = pending_activation_review
                    runtime_result["codex_worker_activation_synthesis_preflight_capture"] = deepcopy(
                        pending_activation_review["synthesis_preflight_capture"]
                    )
                    output_writer(worker_activation.render_codex_worker_activation_review(
                        pending_activation_review
                    ))
                pending_execution_review = None
                transcript.append({"event": "execution_decision_approved"})
                continue
            if pending_summary is None and compose_buffer:
                (
                    pending_summary,
                    pending_clarification,
                    last_resolution,
                    last_project_context,
                    submitted_requests,
                    multiline_requests,
                    synthesis_preflight_capture,
                ) = _submit_composed_request(
                    compose_buffer=compose_buffer,
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    output_writer=output_writer,
                    transcript=transcript,
                    artifact_references=artifact_references,
                    codex_activation_preflight_required=runtime_runner is None,
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
                    approved_implementation_turn_binding=pending_summary.get(
                        "canonical_implementation_turn_binding"
                    ),
                    approved_development_composition_plan_hash=pending_summary.get(
                        "development_composition_plan_hash"
                    ),
                    approved_durable_governed_work_hash=pending_summary.get(
                        "durable_governed_work_hash"
                    ),
                    approved_proposal_preview_hash=pending_summary.get(
                        "proposal_preview_hash"
                    ),
                    approved_approval_request_hash=pending_summary.get(
                        "approval_request_hash"
                    ),
                )
            else:
                runtime_result = runtime_runner(
                    session_id=session,
                    prompt=prompt,
                    created_at=created,
                    runtime_root=root,
                    workspace=workspace_path,
                )
            if synthesis_preflight_capture is not None:
                runtime_result["codex_synthesis_preflight_capture"] = deepcopy(
                    synthesis_preflight_capture
                )
            runtime_status = _reference_runtime_status(runtime_result)
            output_writer(_render_runtime_result(runtime_result, runtime_status))
            review = runtime_result.get("authorization_review_artifact")
            if isinstance(review, dict) and review.get(
                "authorization_review_status"
            ) == "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED":
                pending_execution_review = review
                output_writer(
                    "Development proposal approval is complete. A distinct execution "
                    "decision is now pending. Type /approve to approve proceeding toward "
                    "execution, or /cancel to reject it. No execution is authorized yet."
                )
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

        if pending_disposable_patch_validation_review is not None:
            output_writer(
                "Disposable patch-validation decision pending. Use exact /approve or /cancel; "
                "other text does not apply a patch or run a test."
            )
            transcript.append({"event": "ambiguous_disposable_patch_validation_decision_rejected"})
            continue
        if pending_task_outcome_review is not None:
            output_writer(
                "Task-outcome human decision pending. Use exact /satisfied, "
                "/unsatisfied, or /rework."
            )
            transcript.append({"event": "ambiguous_task_outcome_decision_rejected"})
            continue
        if pending_activation_review is not None:
            output_writer(
                "Worker activation decision pending. Use exact /approve or /cancel; "
                "other text does not activate CODEX."
            )
            transcript.append({"event": "ambiguous_worker_activation_decision_rejected"})
            continue
        if pending_execution_review is not None:
            output_writer(
                "Execution decision pending. Use exact /approve or /cancel; "
                "other text does not confirm execution."
            )
            transcript.append({"event": "ambiguous_execution_decision_rejected"})
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
        "pending_approval": (
            pending_summary is not None or pending_execution_review is not None
            or pending_activation_review is not None
            or pending_task_outcome_review is not None
            or pending_disposable_patch_validation_review is not None
        ),
        "pending_execution_decision": pending_execution_review is not None,
        "pending_worker_activation_decision": pending_activation_review is not None,
        "pending_task_outcome_decision": pending_task_outcome_review is not None,
        "pending_disposable_patch_validation_decision": (
            pending_disposable_patch_validation_review is not None
        ),
        "human_execution_decision_count": approval_count,
        "human_task_outcome_decision_count": human_task_outcome_decision_count,
        "total_human_decision_count": (
            approval_count + human_task_outcome_decision_count
        ),
        "runtime_status": runtime_status,
        "runtime_entered": runtime_result is not None,
        "runtime_result": runtime_result,
        "synthesis_preflight_capture": synthesis_preflight_capture,
        **(
            {
                field: synthesis_preflight_capture[field]
                for field in (
                    "synthesis_preflight_performed", "synthesis_within_bound",
                    "raw_character_count", "prefix_character_count",
                    "final_character_count", "maximum_character_count",
                    "human_decision_count", "process_start_count",
                )
            }
            if synthesis_preflight_capture is not None
            else {
                "synthesis_preflight_performed": False,
                "synthesis_within_bound": False,
                "human_decision_count": approval_count,
                "process_start_count": 0,
            }
        ),
        "development_intent_resolution": last_resolution,
        "transcript": transcript,
        "aicli_authorizes": False,
        "aicli_executes": False,
        "aicli_owns_replay": False,
        "aicli_validates": False,
        "aicli_accepts_result": False,
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
    synthesis_preflight_capture: dict[str, Any] | None = None
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
            synthesis_preflight_capture,
        ) = _submit_composed_request(
            compose_buffer=request.split("\n"),
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            output_writer=output_writer,
            transcript=transcript,
            artifact_references=artifact_references,
            codex_activation_preflight_required=runtime_runner is None,
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
                synthesis_preflight_capture,
            ) = _submit_composed_request(
                compose_buffer=reply_text.split("\n"),
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                output_writer=output_writer,
                transcript=transcript,
                artifact_references=artifact_references,
                codex_activation_preflight_required=runtime_runner is None,
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
                approved_implementation_turn_binding=pending_summary.get(
                    "canonical_implementation_turn_binding"
                ),
                approved_development_composition_plan_hash=pending_summary.get(
                    "development_composition_plan_hash"
                ),
                approved_durable_governed_work_hash=pending_summary.get(
                    "durable_governed_work_hash"
                ),
                approved_proposal_preview_hash=pending_summary.get(
                    "proposal_preview_hash"
                ),
                approved_approval_request_hash=pending_summary.get(
                    "approval_request_hash"
                ),
            )
        else:
            runtime_result = runtime_runner(
                session_id=session,
                prompt=prompt,
                created_at=created,
                runtime_root=root,
                workspace=workspace_path,
            )
        if synthesis_preflight_capture is not None:
            runtime_result["codex_synthesis_preflight_capture"] = deepcopy(
                synthesis_preflight_capture
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
        "synthesis_preflight_capture": synthesis_preflight_capture,
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


def _record_contextual_execution_decision(
    *,
    pending_execution_review: dict[str, Any],
    decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """Transport one contextual decision to its Platform Core binding owner."""

    review_hash = _require_string(pending_execution_review.get("artifact_hash"),
                                  "authorization_review_hash")
    result = bind_distinct_human_execution_decision(
        authorization_review_artifact=pending_execution_review,
        human_decision=decision,
        session_id=session,
        decided_by="HUMAN_OPERATOR_VIA_AICLI",
        decided_at=created,
        workspace=workspace_path,
        session_root=root / session,
        replay_dir=root / session / f"EXECUTION-DECISION-{review_hash[-16:]}",
    )
    confirmation = result.get("human_confirmation_artifact") or {}
    merged = dict(runtime_result or {})
    merged.update({
        "execution_human_decision_result": result,
        "execution_human_decision_status": result.get("decision_status"),
        "execution_human_decision_hash": result.get("artifact_hash"),
        "execution_summary_human_confirmation": result.get("execution_summary_human_confirmation") is True,
        "execution_decision_rejected": result.get("decision_status") == EXECUTION_DECISION_REJECTED,
        "human_confirmation_reference": confirmation.get("confirmation_id"),
        "human_confirmation_hash": result.get("human_confirmation_hash"),
        "runtime_replay_reference": result.get("replay_reference"),
        "execution_authorized": False,
        "worker_selected": False,
        "authorization_dispatch_blocked": True,
    })
    if result.get("decision_status") == EXECUTION_DECISION_APPROVED:
        authorization = authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=result,
            workspace=workspace_path,
            session_root=root / session,
            replay_dir=root / session / f"EXECUTION-AUTHORIZATION-{result['artifact_hash'][-16:]}",
        )
        merged.update({
            "execution_authorization_capture": authorization,
            "execution_authorization_status": authorization.get("authorization_status"),
            "execution_authorized": authorization.get("execution_authorized") is True,
            "authorization_dispatch_blocked": True,
            "runtime_replay_reference": authorization.get(
                "execution_authorization_replay_reference"
            ),
        })
        if authorization.get("execution_authorized") is True:
            selection = select_authorized_grounded_worker(
                execution_authorization_capture=authorization,
                session_root=root / session,
                replay_dir=root / session / f"WORKER-SELECTION-{authorization['execution_authorization_artifact']['artifact_hash'][-16:]}",
            )
            merged.update({
                "authorized_worker_selection_capture": selection,
                "worker_selection_status": selection.get("selection_status"),
                "selected_resource_id": selection.get("selected_resource_id"),
                "selected_role_type": selection.get("selected_role_type"),
                "worker_selected": selection.get("worker_selected") is True,
                "worker_assigned": False, "worker_dispatched": False,
                "runtime_replay_reference": selection.get(
                    "resource_selection_replay_reference"),
            })
            if selection.get("worker_selected") is True:
                selection_artifact = selection["resource_selection_artifact"]
                invocation_request = worker_request.create_worker_invocation_request(
                    invocation_request_id=f"{selection_artifact['selection_id']}:INVOCATION-REQUEST",
                    execution_authorization_replay_reference=authorization[
                        "execution_authorization_replay_reference"
                    ],
                    resource_selection_replay_reference=selection[
                        "resource_selection_replay_reference"
                    ],
                    requested_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
                    requested_at=created,
                    replay_dir=root / session / f"WORKER-REQUEST-{selection_artifact['artifact_hash'][-16:]}",
                )
                merged.update({
                    "worker_invocation_request_capture": invocation_request,
                    "worker_invocation_request_status": invocation_request.get("request_status"),
                    "worker_invocation_request_created": (
                        invocation_request.get("request_status") == worker_request.WORKER_INVOCATION_REQUEST_CREATED
                    ),
                    "runtime_replay_reference": invocation_request.get(
                        "worker_invocation_request_replay_reference"
                    ),
                })
                if invocation_request.get("request_status") == worker_request.WORKER_INVOCATION_REQUEST_CREATED:
                    request_artifact = invocation_request["worker_invocation_request_artifact"]
                    assignment = worker_assignment.assign_worker_from_invocation_request(
                        worker_assignment_id=f"{selection_artifact['selection_id']}:ASSIGNMENT",
                        worker_invocation_request_artifact=request_artifact,
                        worker_invocation_request_replay_reference=invocation_request[
                            "worker_invocation_request_replay_reference"
                        ],
                        worker_registry_artifacts=worker_assignment.default_worker_registry_for_request(
                            request_artifact,
                            created_at=created,
                        ),
                        assigned_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
                        assigned_at=created,
                        replay_dir=root / session / f"WORKER-ASSIGNMENT-{request_artifact['artifact_hash'][-16:]}",
                    )
                    merged.update({
                        "worker_assignment_capture": assignment,
                        "worker_assignment_status": assignment.get("assignment_status"),
                        "worker_assigned": assignment.get("assignment_status") == worker_assignment.WORKER_ASSIGNED,
                        "worker_dispatched": False,
                        "provider_invoked": False,
                        "worker_invoked": False,
                        "command_executed": False,
                        "repository_mutated": False,
                        "runtime_replay_reference": assignment.get(
                            "worker_assignment_replay_reference"
                        ),
                    })
                    if assignment.get("assignment_status") == worker_assignment.WORKER_ASSIGNED:
                        assignment_artifact = assignment["worker_assignment_artifact"]
                        dispatch = worker_dispatch.dispatch_assigned_worker(
                            worker_dispatch_id=f"{assignment_artifact['worker_assignment_id']}:DISPATCH",
                            worker_assignment_artifact=assignment_artifact,
                            worker_assignment_replay_reference=assignment[
                                "worker_assignment_replay_reference"
                            ],
                            dispatched_by="AIGOL_GOVERNANCE",
                            dispatched_at=created,
                            replay_dir=root / session / f"WORKER-DISPATCH-{assignment_artifact['artifact_hash'][-16:]}",
                        )
                        merged.update({
                            "worker_dispatch_capture": dispatch,
                            "worker_dispatch_status": dispatch.get("dispatch_status"),
                            "worker_dispatched": (
                                dispatch.get("dispatch_status") == worker_dispatch.WORKER_DISPATCHED
                            ),
                            "authorization_dispatch_blocked": (
                                dispatch.get("dispatch_status") != worker_dispatch.WORKER_DISPATCHED
                            ),
                            "provider_invoked": False,
                            "worker_invoked": False,
                            "command_executed": False,
                            "repository_mutated": False,
                            "runtime_replay_reference": dispatch.get(
                                "worker_dispatch_replay_reference"
                            ),
                        })
                        if dispatch.get("dispatch_status") == worker_dispatch.WORKER_DISPATCHED:
                            dispatch_artifact = dispatch["worker_dispatch_artifact"]
                            invocation = worker_invocation.invoke_dispatched_worker(
                                worker_invocation_id=f"{dispatch_artifact['worker_dispatch_id']}:INVOCATION",
                                worker_dispatch_artifact=dispatch_artifact,
                                worker_dispatch_replay_reference=dispatch[
                                    "worker_dispatch_replay_reference"
                                ],
                                invoked_by="AIGOL_GOVERNANCE",
                                invoked_at=created,
                                replay_dir=root / session / f"WORKER-INVOCATION-{dispatch_artifact['artifact_hash'][-16:]}",
                            )
                            merged.update({
                                "worker_invocation_capture": invocation,
                                "worker_invocation_status": invocation.get("invocation_status"),
                                "worker_invoked": (
                                    invocation.get("invocation_status") == worker_invocation.WORKER_INVOKED
                                ),
                                "provider_invoked": False,
                                "execution_started": False,
                                "command_executed": False,
                                "result_created": False,
                                "repository_mutated": False,
                                "runtime_replay_reference": invocation.get(
                                    "worker_invocation_replay_reference"
                                ),
                            })
                            if invocation.get("invocation_status") == worker_invocation.WORKER_INVOKED:
                                invocation_artifact = invocation["worker_invocation_artifact"]
                                candidate = worker_candidate.project_g31_invocation_to_execution_candidate(
                                    worker_invocation_artifact=invocation_artifact,
                                    worker_invocation_replay_reference=invocation[
                                        "worker_invocation_replay_reference"
                                    ],
                                    session_root=root / session,
                                    requested_by="PLATFORM_CORE_G31_CANDIDATE_BINDING",
                                    created_at=created,
                                    replay_dir=root / session / (
                                        f"WORKER-EXECUTION-CANDIDATE-{invocation_artifact['artifact_hash'][-16:]}"
                                    ),
                                )
                                merged.update({
                                    "worker_execution_candidate_capture": candidate,
                                    "execution_candidate_created": candidate.get(
                                        "worker_execution_candidate_generated"
                                    ) is True,
                                    "provider_invoked": False,
                                    "worker_process_started": False,
                                    "execution_started": False,
                                    "command_executed": False,
                                    "result_created": False,
                                    "repository_mutated": False,
                                    "runtime_replay_reference": candidate.get(
                                        "worker_execution_candidate_replay_reference"
                                    ),
                                })
                                if candidate.get("worker_execution_candidate_generated") is True:
                                    execution = governed_execution.project_g31_candidate_to_governed_execution(
                                        execution_candidate_capture=candidate,
                                        session_root=root / session,
                                        executed_by="PLATFORM_CORE_G31_GOVERNED_EXECUTION_BINDING",
                                        executed_at=created,
                                        replay_dir=root / session / (
                                            "GOVERNED-WORKER-EXECUTION-"
                                            f"{candidate['worker_execution_candidate_artifact']['artifact_hash'][-16:]}"
                                        ),
                                    )
                                    merged.update({
                                        "governed_worker_execution_capture": execution,
                                        "governed_execution_evidence_created": execution.get(
                                            "worker_execution_completed"
                                        ) is True,
                                        "provider_invoked": False,
                                        "worker_process_started": False,
                                        "execution_started": False,
                                        "command_executed": False,
                                        "worker_output_created": False,
                                        "result_created": False,
                                        "repository_mutated": False,
                                        "runtime_replay_reference": execution.get(
                                            "worker_execution_replay_reference"
                                        ),
                                    })
    return merged


def _record_contextual_worker_activation_decision(
    *,
    pending_activation_review: dict[str, Any],
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any] | None,
    runner: Callable[..., Any] | None,
) -> dict[str, Any]:
    """Transport the third decision to the Worker-owned activation binding."""

    merged = dict(runtime_result or {})
    review = pending_activation_review["activation_review_artifact"]
    capture = worker_activation.activate_bounded_codex_worker(
        activation_review_artifact=review,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        human_decision="APPROVE",
        decided_by="HUMAN_OPERATOR_VIA_AICLI",
        decided_at=created,
        session_root=root / session,
        workspace=workspace_path,
        replay_dir=root / session / f"CODEX-WORKER-ACTIVATION-{review['artifact_hash'][-16:]}",
        runner=runner,
    )
    merged.update({
        "codex_worker_activation_capture": capture,
        "runtime_replay_reference": capture["activation_replay_reference"],
        **{
            field: capture[field]
            for field in worker_activation.ACTIVATION_TRUTH_FIELDS
        },
    })
    result = codex_result.capture_successful_codex_worker_result(
        activation_capture=capture,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        captured_at=created,
        replay_dir=root / session / f"CODEX-WORKER-RESULT-CAPTURE-{capture['codex_transport_receipt']['receipt_id'][-16:]}",
    )
    merged["codex_worker_result_capture_binding_capture"] = result
    merged.update({field: result[field] for field in codex_result.RESULT_TRUTH_FIELDS})
    validation = codex_validation.validate_captured_codex_worker_result(
        result_capture_binding_capture=result,
        activation_capture=capture,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        validated_at=created,
        replay_dir=(
            root / session /
            f"CODEX-WORKER-RESULT-VALIDATION-{result.get('worker_output_hash', '')[-16:]}"
        ),
    )
    merged["codex_worker_semantic_validation_binding_capture"] = validation
    merged.update({field: validation[field] for field in codex_validation.VALIDATION_TRUTH_FIELDS})
    return merged


def _prepare_contextual_task_outcome_review(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Bind exact in-memory output to one review-only human continuation."""

    merged = dict(runtime_result)
    validation = merged["codex_worker_semantic_validation_binding_capture"]
    validation_artifact = validation.get("worker_result_validation_artifact") or {}
    review = codex_task_review.prepare_codex_task_outcome_review(
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=validation,
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        prepared_at=created,
        replay_dir=(
            root / session / "CODEX-TASK-OUTCOME-REVIEW-"
            f"{validation_artifact.get('artifact_hash', '')[-16:]}"
        ),
    )
    reconstruction = codex_task_review.reconstruct_codex_task_outcome_review(
        review_capture=review,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=validation,
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    merged.update({
        "codex_task_outcome_review_capture": review,
        "codex_task_outcome_review_reconstruction": reconstruction,
        "task_outcome_review_status": review["review_status"],
        "task_outcome_review_replay_created": True,
        "task_outcome_review_count": 1,
        "human_task_outcome_decision_recorded": False,
    })
    return merged


def _record_contextual_task_outcome_decision(
    *,
    pending_task_outcome_review: dict[str, Any],
    task_outcome_decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """Record one explicit review outcome without acceptance or execution."""

    merged = dict(runtime_result or {})
    review_packet = pending_task_outcome_review["task_outcome_review_packet_artifact"]
    decision = codex_task_review.record_codex_task_outcome_human_decision(
        review_capture=pending_task_outcome_review,
        task_outcome_decision=task_outcome_decision,
        decision_reason=(
            "Human operator selected the explicit task-outcome decision after "
            "AiCLI displayed the exact captured Worker output and bound lineage."
        ),
        decided_by="HUMAN_OPERATOR_VIA_AICLI",
        decided_at=created,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        human_decision_replay_dir=(
            root / session / "CODEX-TASK-OUTCOME-HUMAN-DECISION-"
            f"{review_packet['artifact_hash'][-16:]}"
        ),
    )
    reconstruction = codex_task_review.reconstruct_codex_task_outcome_human_decision(
        decision_capture=decision,
        review_capture=pending_task_outcome_review,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    merged.update({
        "codex_task_outcome_human_decision_capture": decision,
        "codex_task_outcome_human_decision_reconstruction": reconstruction,
        "task_outcome_review_status": task_outcome_decision,
        "task_outcome_review_replay_created": True,
        "task_outcome_review_count": 1,
        "human_task_outcome_decision_recorded": True,
        **{
            field: decision[field]
            for field in (
                "task_outcome_satisfaction_evaluated",
                "task_outcome_satisfied",
                "rework_requested",
                "result_accepted",
                "repository_mutation_authorized",
                "repository_mutated",
                "automatic_retry_performed",
                "additional_worker_process_started",
                "commit_created",
                "deployed",
                "released",
            )
        },
    })
    return merged


def _prepare_contextual_disposable_patch_validation_review(
    *, session: str, root: Path, workspace_path: str, created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(runtime_result)
    decision = merged["codex_task_outcome_human_decision_capture"]
    identity = decision["human_decision_capture"]["human_decision_artifact"]["artifact_hash"][-16:]
    lineage = dict(task_outcome_decision_capture=decision, review_capture=merged["codex_task_outcome_review_capture"], result_capture_binding_capture=merged["codex_worker_result_capture_binding_capture"], validation_binding_capture=merged["codex_worker_semantic_validation_binding_capture"], activation_capture=merged["codex_worker_activation_capture"], governed_execution_capture=merged["governed_worker_execution_capture"], execution_candidate_capture=merged["worker_execution_candidate_capture"], session_root=root / session, source_workspace=workspace_path)
    review = disposable_validation.prepare_disposable_patch_validation_review(
        disposable_workspace=root / session / f"DISPOSABLE-PATCH-VALIDATION-{identity}",
        prepared_at=created,
        replay_dir=root / session / f"DISPOSABLE-PATCH-VALIDATION-REVIEW-{identity}",
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_review(
        review_binding_capture=review, **lineage,
    )
    merged.update({"disposable_patch_validation_review_capture": review, "disposable_patch_validation_review_reconstruction": reconstruction,
        "disposable_patch_validation_review_pending": True, "disposable_patch_validation_decision_recorded": False,
        "disposable_patch_validation_executed": False, "ready_for_acceptance": False, "result_accepted": False,
        "mutation_authorized": False, "main_repository_mutated": False})
    return merged


def _record_contextual_disposable_patch_validation_decision(
    *, pending_review: dict[str, Any], decision: str, session: str, root: Path,
    workspace_path: str, created: str, runtime_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """Record and reconstruct one existing disposable-only decision; never execute it."""

    merged = dict(runtime_result or {})
    plan = pending_review["disposable_patch_validation_plan_artifact"]
    lineage = dict(task_outcome_decision_capture=merged["codex_task_outcome_human_decision_capture"], review_capture=merged["codex_task_outcome_review_capture"], result_capture_binding_capture=merged["codex_worker_result_capture_binding_capture"], validation_binding_capture=merged["codex_worker_semantic_validation_binding_capture"], activation_capture=merged["codex_worker_activation_capture"], governed_execution_capture=merged["governed_worker_execution_capture"], execution_candidate_capture=merged["worker_execution_candidate_capture"], session_root=root / session, source_workspace=workspace_path)
    capture = disposable_validation.record_disposable_patch_validation_human_decision(
        review_binding_capture=pending_review, decision=decision,
        decision_reason="Human operator selected the explicit disposable validation decision in AiCLI.",
        decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=created,
        human_decision_replay_dir=root / session / f"DISPOSABLE-PATCH-VALIDATION-HUMAN-DECISION-{plan['artifact_hash'][-16:]}",
        **lineage,
    )
    merged.update({"disposable_patch_validation_human_decision_capture": capture,
        "disposable_patch_validation_human_decision_reconstruction": human_decision.reconstruct_human_decision_replay(capture["human_decision_replay_reference"]),
        "disposable_patch_validation_review_pending": False, "disposable_patch_validation_decision_recorded": True,
        "disposable_patch_validation_executed": False, "ready_for_acceptance": False, "result_accepted": False,
        "mutation_authorized": False, "main_repository_mutated": False})
    return merged


def _execute_contextual_disposable_patch_validation(
    *, session: str, root: Path, workspace_path: str, created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Call and reconstruct exactly one existing G31-23A disposable execution."""

    merged = dict(runtime_result)
    review = merged["disposable_patch_validation_review_capture"]
    plan = review["disposable_patch_validation_plan_artifact"]
    lineage = dict(task_outcome_decision_capture=merged["codex_task_outcome_human_decision_capture"], review_capture=merged["codex_task_outcome_review_capture"], result_capture_binding_capture=merged["codex_worker_result_capture_binding_capture"], validation_binding_capture=merged["codex_worker_semantic_validation_binding_capture"], activation_capture=merged["codex_worker_activation_capture"], governed_execution_capture=merged["governed_worker_execution_capture"], execution_candidate_capture=merged["worker_execution_candidate_capture"], session_root=root / session, source_workspace=workspace_path)
    outcome = disposable_validation.execute_disposable_patch_validation(
        review_binding_capture=review,
        application_decision_capture=merged["disposable_patch_validation_human_decision_capture"],
        executed_by="HUMAN_OPERATOR_VIA_AICLI", executed_at=created,
        replay_dir=root / session / f"DISPOSABLE-PATCH-VALIDATION-OUTCOME-{plan['artifact_hash'][-16:]}",
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_outcome(
        outcome_capture=outcome, review_binding_capture=review,
        application_decision_capture=merged["disposable_patch_validation_human_decision_capture"],
        **lineage,
    )
    artifact = outcome["outcome_artifact"]
    merged.update({"disposable_patch_validation_outcome_capture": outcome,
        "disposable_patch_validation_outcome_reconstruction": reconstruction,
        "disposable_patch_validation_approved": True,
        "disposable_patch_validation_executed": artifact["disposable_patch_application_attempted"],
        "disposable_patch_application_succeeded": artifact["disposable_patch_applied"] and artifact["content_validation_passed"],
        "focused_validation_executed": artifact["grounded_test_execution_performed"],
        "focused_validation_succeeded": artifact["grounded_test_validation_passed"],
        "ready_for_acceptance": False, "result_accepted": False,
        "mutation_authorized": False, "main_repository_mutated": False})
    merged.update({key: outcome[key] for key in (
        "disposable_patch_applied", "content_validation_performed", "content_validation_passed",
        "grounded_test_execution_performed", "grounded_test_validation_passed",
        "ready_for_generated_content_acceptance", "repository_mutation_authorized",
        "failure_reason")})
    return merged


def _bind_contextual_replacement_acceptance_prerequisites(
    *, session: str, root: Path, workspace_path: str, created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Bind one exact successful R03 outcome through the existing G31-23B owner."""

    merged = dict(runtime_result)
    outcome = merged["disposable_patch_validation_outcome_capture"]
    outcome_hash = outcome["outcome_artifact"]["artifact_hash"]
    capture = replacement_prerequisites.bind_codex_replacement_acceptance_prerequisites(
        disposable_validation_outcome_capture=outcome,
        disposable_validation_review_capture=merged["disposable_patch_validation_review_capture"],
        application_decision_capture=merged["disposable_patch_validation_human_decision_capture"],
        task_outcome_decision_capture=merged["codex_task_outcome_human_decision_capture"],
        task_outcome_review_capture=merged["codex_task_outcome_review_capture"],
        result_capture_binding_capture=merged["codex_worker_result_capture_binding_capture"],
        governance_validation_binding_capture=merged["codex_worker_semantic_validation_binding_capture"],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session, source_workspace=workspace_path, created_at=created,
        replay_dir=root / session / f"G31-REPLACEMENT-ACCEPTANCE-PREREQUISITES-{outcome_hash[-16:]}",
    )
    reconstruction = (
        replacement_prerequisites.reconstruct_codex_replacement_acceptance_prerequisite_binding(
            binding_capture=capture, session_root=root / session,
        )
    )
    merged["codex_replacement_acceptance_prerequisite_binding_capture"] = capture
    merged["codex_replacement_acceptance_prerequisite_binding_reconstruction"] = reconstruction
    merged.update({key: capture[key] for key in (
        "replacement_manifest_created", "acceptance_prerequisites_satisfied",
        "ready_for_acceptance", "result_accepted", "mutation_authorized",
        "main_repository_mutated",
    )})
    return merged


def _render_task_outcome_review_lineage(review: dict[str, Any]) -> str:
    """Render identities required for a human decision; acquire no authority."""

    packet = review["task_outcome_review_packet_artifact"]
    capture = packet["capture_binding"]
    capture_artifact = capture["artifact"]
    validation = packet["governance_validation_binding"]
    validation_artifact = validation["artifact"]
    return "\n".join((
        "Exact Task-Outcome Review Lineage",
        f"Capture Identity: {capture_artifact['worker_result_capture_id']}",
        f"Capture Artifact Hash: {capture_artifact['artifact_hash']}",
        f"Capture Replay Hash: {capture['replay_hash']}",
        f"Governance Validation Identity: {validation_artifact['worker_result_validation_id']}",
        f"Governance Validation Artifact Hash: {validation_artifact['artifact_hash']}",
        f"Governance Validation Status: {validation['status']}",
        f"Governance Validation Meaning: {validation['canonical_meaning']}",
        f"Patch Applied: {packet['patch_applied']}",
        "Tests Run Against Applied Patch: "
        f"{packet['tests_run_against_applied_patch']}",
    ))


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
    codex_activation_preflight_required: bool = True,
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any],
    dict[str, Any],
    int,
    int,
    dict[str, Any] | None,
]:
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
        return None, clarification, resolution, project_context, 1, multiline_requests, None
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
        return None, clarification, resolution, project_context, 1, multiline_requests, None
    if resolution.get("summary_admissible") is True:
        summary = _summary_from_conversation(conversation)
        if not codex_activation_preflight_required:
            output_writer(_render_summary(summary))
            return summary, None, resolution, project_context, 1, multiline_requests, None
        preflight = worker_activation.preflight_codex_worker_synthesis(
            _require_string(summary["canonical_runtime_prompt"], "canonical_runtime_prompt")
        )
        output_writer(worker_activation.render_codex_worker_synthesis_preflight(preflight))
        if preflight["synthesis_preflight_status"] != "SYNTHESIS_PREFLIGHT_READY":
            output_writer(
                "Canonical CODEX synthesis preflight failed closed before human approval."
            )
            transcript.append({"event": "codex_synthesis_preflight_failed_closed"})
            return None, None, resolution, project_context, 1, multiline_requests, preflight
        output_writer(_render_summary(summary))
        return summary, None, resolution, project_context, 1, multiline_requests, preflight
    if conversation.get("response_mode") == "READ_ONLY_RESULT":
        output_writer(_render_read_only_result(conversation))
        return None, None, resolution, project_context, 1, multiline_requests, None
    output_writer(_render_non_development_response(conversation))
    return None, None, resolution, project_context, 1, multiline_requests, None


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
    ]
    preview = summary.get("canonical_proposal_preview")
    if isinstance(preview, dict):
        lines.extend(
            [
                "Canonical durable governed-work proposal",
                f"canonical_project_objective: {preview.get('canonical_project_objective')}",
                f"knowledge_reuse_classification: {preview.get('knowledge_reuse_classification')}",
                f"knowledge_reuse_recommended: {preview.get('knowledge_reuse_recommended')}",
                f"repository_scope_status: {preview.get('repository_scope_status')}",
                f"repository_scope_explanation: {preview.get('repository_scope_explanation')}",
                f"bounded_work_scope: {preview.get('bounded_work_scope')}",
                f"ordered_implementation_sequence: {preview.get('ordered_implementation_sequence')}",
                f"focused_tests: {preview.get('focused_tests')}",
                f"validation_requirements: {preview.get('validation_requirements')}",
                f"development_composition_plan_hash: {summary.get('development_composition_plan_hash')}",
                f"durable_governed_work_id: {summary.get('durable_governed_work_id')}",
                f"durable_governed_work_hash: {summary.get('durable_governed_work_hash')}",
                f"proposal_preview_hash: {summary.get('proposal_preview_hash')}",
                f"approval_request_id: {summary.get('approval_request_id')}",
                f"approval_request_hash: {summary.get('approval_request_hash')}",
                "approval_is_execution_authorization: False",
            ]
        )
    lines.extend(
        [
            str(summary.get("approval_explanation")),
            "Type /approve to continue, or /cancel to discard.",
        ]
    )
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
    lines = [
        "Certified runtime result",
        f"runtime_status: {runtime_status}",
        f"governance_authorization_reached: {runtime_result.get('governance_authorization_reached')}",
        f"provider_invocation_reached: {runtime_result.get('provider_invocation_reached')}",
        f"worker_execution_reached: {runtime_result.get('worker_execution_reached')}",
        f"replay_certification_reached: {runtime_result.get('replay_certification_reached')}",
        f"runtime_replay_reference: {runtime_result.get('runtime_replay_reference')}",
    ]
    if runtime_result.get("approved_worker_payload_binding_hash"):
        approved_binding = runtime_result.get("approved_implementation_turn_binding")
        if not isinstance(approved_binding, dict):
            approved_binding = {}
        lines.extend(
            [
                "Approved durable governed work Worker payload",
                f"binding_status: {runtime_result.get('approved_worker_payload_binding_status')}",
                f"development_composition_plan_hash: {approved_binding.get('development_composition_plan_hash')}",
                f"durable_governed_work_hash: {approved_binding.get('durable_governed_work_hash')}",
                f"proposal_preview_hash: {approved_binding.get('proposal_preview_hash')}",
                f"approval_request_hash: {approved_binding.get('approval_request_hash')}",
                f"approval_consumption_hash: {runtime_result.get('approved_identity_consumption_hash')}",
                f"ppp_task_package_hash: {runtime_result.get('approved_ppp_task_package_hash')}",
                f"implementation_request_hash: {runtime_result.get('approved_implementation_request_hash')}",
                f"worker_implementation_payload_hash: {runtime_result.get('approved_worker_implementation_payload_hash')}",
                f"dispatch_blocked: {runtime_result.get('approved_worker_payload_dispatch_blocked')}",
                f"failure_reason: {runtime_result.get('approved_worker_payload_failure_reason')}",
                "Canonical repository-scope grounding",
                f"grounding_status: {runtime_result.get('repository_scope_grounding_status')}",
                f"repository_scope_grounding_hash: {runtime_result.get('repository_scope_grounding_hash')}",
                f"repository_cognition_snapshot_hash: {runtime_result.get('repository_cognition_snapshot_hash')}",
                f"grounded_repository_targets: {runtime_result.get('grounded_repository_targets')}",
                f"grounded_focused_test_targets: {runtime_result.get('grounded_focused_test_targets')}",
                f"grounded_worker_request_hash: {runtime_result.get('grounded_worker_request_hash')}",
                f"repository_scope_dispatch_blocked: {runtime_result.get('repository_scope_dispatch_blocked')}",
                "Grounded Worker request execution-authorization review",
                f"authorization_review_status: {runtime_result.get('authorization_review_status')}",
                f"authorization_review_hash: {runtime_result.get('authorization_review_hash')}",
                f"authorization_scope_hash: {runtime_result.get('authorization_scope_hash')}",
                f"execution_summary_hash: {runtime_result.get('execution_summary_hash')}",
                f"distinct_human_execution_authorization_required: {runtime_result.get('distinct_human_execution_authorization_required')}",
                f"proposal_approval_is_execution_authorization: {runtime_result.get('proposal_approval_is_execution_authorization')}",
                f"execution_authorized: {runtime_result.get('execution_authorized')}",
                f"worker_selected: {runtime_result.get('worker_selected')}",
                f"authorization_dispatch_blocked: {runtime_result.get('authorization_dispatch_blocked')}",
            ]
        )
    return "\n".join(lines)


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
            "/approve - approve the pending proposal or distinct execution decision",
            "/satisfied - record that the captured Worker output satisfies its task",
            "/unsatisfied - record that the captured Worker output does not satisfy its task",
            "/rework - request future governed rework without starting another Worker",
            "/cancel - clear pending input or reject the distinct execution decision",
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
