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

from aigol.runtime import codex_replacement_acceptance_prerequisite_binding_runtime as replacement_prerequisites
from aigol.runtime import codex_satisfied_outcome_disposable_validation_binding_runtime as disposable_validation
from aigol.runtime import codex_task_outcome_human_review_runtime as codex_task_review
from aigol.runtime import codex_transport_to_worker_result_capture_binding_runtime as codex_result
from aigol.runtime import codex_worker_activation_binding_runtime as worker_activation
from aigol.runtime import codex_worker_result_to_semantic_validation_binding_runtime as codex_validation
from aigol.runtime import generated_content_acceptance_runtime as generated_acceptance
from aigol.runtime import governed_worker_execution_runtime as governed_execution
from aigol.runtime import human_decision_runtime as human_decision
from aigol.runtime import platform_core_existing_file_governance as existing_file_governance
from aigol.runtime import platform_core_existing_file_mutation_candidate as existing_file_candidate
from aigol.runtime import worker_assignment_runtime as worker_assignment
from aigol.runtime import worker_dispatch_runtime as worker_dispatch
from aigol.runtime import worker_invocation_request_runtime as worker_request
from aigol.runtime import worker_invocation_runtime as worker_invocation
from aigol.runtime import worker_invocation_to_execution_candidate_bridge_runtime as worker_candidate
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    authorize_confirmed_grounded_execution_decision,
    render_authorized_grounded_worker_selection,
    select_authorized_grounded_worker,
)
from aigol.runtime.execution_authorization_runtime import render_execution_authorization_summary
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_APPROVED,
    EXECUTION_DECISION_REJECTED,
    bind_distinct_human_execution_decision,
    render_distinct_human_execution_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
)
from aigol.workers import filesystem_replace_worker


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
G31_APPLICATION_TRANSITION_VERSION = (
    "G31_COMMON_HUMAN_INTERFACE_APPLICATION_TRANSITION_V1"
)
G31_EXECUTION_DECISION = "G31_EXECUTION_DECISION"
G31_WORKER_ACTIVATION_DECISION = "G31_WORKER_ACTIVATION_DECISION"
G31_TASK_OUTCOME_DECISION = "G31_TASK_OUTCOME_DECISION"
G31_DISPOSABLE_VALIDATION_DECISION = "G31_DISPOSABLE_VALIDATION_DECISION"
G31_CONTENT_ACCEPTANCE_DECISION = "G31_CONTENT_ACCEPTANCE_DECISION"
G31_MUTATION_DECISION = "G31_MUTATION_DECISION"
G31_APPROVE = "APPROVE"
G31_REJECT = "REJECT"
G31_TASK_OUTCOME_SATISFIED = "TASK_OUTCOME_SATISFIED"
G31_TASK_OUTCOME_UNSATISFIED = "TASK_OUTCOME_UNSATISFIED"
G31_REWORK_REQUESTED = "REWORK_REQUESTED"
G31_CONTENT_ACCEPTED = "ACCEPTED"
G31_CONTENT_REJECTED = "REJECTED"
G31_MUTATION_APPROVED = "APPROVED"
G31_MUTATION_REJECTED = "REJECTED"


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
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
    approved_implementation_turn_binding: dict[str, Any] | None = None,
    approved_development_composition_plan_hash: str | None = None,
    approved_durable_governed_work_hash: str | None = None,
    approved_proposal_preview_hash: str | None = None,
    approved_approval_request_hash: str | None = None,
    g31_application_state: dict[str, Any] | None = None,
    g31_human_action: str | None = None,
    g31_human_actor_id: str = "HUMAN_OPERATOR",
    g31_worker_process_runner: Callable[..., Any] | None = None,
    g31_synthesis_preflight_prompt: str | None = None,
) -> dict[str, Any]:
    """Enter the certified runtime from any Unified Human Interface."""

    interface = _require_string(interface_name, "interface_name")
    session = _require_string(session_id, "session_id")
    created = _require_string(created_at, "created_at")
    root = Path(runtime_root)
    workspace_text = str(Path(workspace))
    if g31_synthesis_preflight_prompt is not None:
        preflight = worker_activation.preflight_codex_worker_synthesis(
            _require_string(
                g31_synthesis_preflight_prompt, "g31_synthesis_preflight_prompt"
            )
        )
        return _g31_application_result(
            {"codex_synthesis_preflight_capture": preflight},
            interface_name=interface,
            presentations=(
                worker_activation.render_codex_worker_synthesis_preflight(preflight),
            ),
        )
    if g31_application_state is not None:
        return _continue_g31_application_transition(
            interface_name=interface,
            session=session,
            root=root,
            workspace_path=workspace_text,
            created=created,
            application_state=g31_application_state,
            human_action=g31_human_action,
            human_actor_id=g31_human_actor_id,
            worker_process_runner=g31_worker_process_runner,
        )
    requests = [_require_string(request, "human_request") for request in human_requests]

    result = deepcopy(presentation) if isinstance(presentation, dict) else {}
    approved_identity_consumption = None
    if approved_implementation_turn_binding is not None:
        from aigol.runtime.platform_implementation_turn_durable_work_binding import (
            consume_approved_implementation_turn_binding,
        )

        approved_identity_consumption = consume_approved_implementation_turn_binding(
            binding_artifact=approved_implementation_turn_binding,
            development_composition_plan_hash=_require_string(
                approved_development_composition_plan_hash,
                "approved_development_composition_plan_hash",
            ),
            durable_governed_work_hash=_require_string(
                approved_durable_governed_work_hash,
                "approved_durable_governed_work_hash",
            ),
            proposal_preview_hash=_require_string(
                approved_proposal_preview_hash,
                "approved_proposal_preview_hash",
            ),
            approval_request_hash=_require_string(
                approved_approval_request_hash,
                "approved_approval_request_hash",
            ),
            created_at=created,
            replay_dir=_require_string(
                approved_implementation_turn_binding.get("replay_reference"),
                "approved_implementation_turn_replay_reference",
            ),
        )
        project_contexts = []
        intent_resolutions = [
            {
                "runtime_binding_admissible": True,
                "canonical_runtime_prompt": requests[0],
                "work_type": "IMPLEMENTATION",
                "canonical_implementation_turn_binding": deepcopy(
                    approved_implementation_turn_binding
                ),
                "canonical_implementation_turn_binding_hash": (
                    approved_implementation_turn_binding.get("artifact_hash")
                ),
                "approved_identity_consumption": deepcopy(
                    approved_identity_consumption
                ),
            }
        ]
    else:
        project_contexts = [
            prepare_unified_human_interface_project_context(
                interface_name=interface,
                session_id=session,
                message=request,
                runtime_root=root,
                workspace=workspace_text,
                created_at=created,
                explicit_canonical_artifacts=explicit_canonical_artifacts,
                explicit_canonical_artifact_references=(
                    explicit_canonical_artifact_references
                ),
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
            "approved_implementation_turn_binding": deepcopy(
                approved_implementation_turn_binding
            ),
            "approved_identity_consumption": deepcopy(approved_identity_consumption),
            "approved_identity_consumption_hash": (
                approved_identity_consumption.get("artifact_hash")
                if isinstance(approved_identity_consumption, dict)
                else None
            ),
            "approved_durable_work_identity_consumed": isinstance(
                approved_identity_consumption, dict
            ),
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
            "human_interface_resolves_artifacts": False,
            "human_interface_validates_artifacts": False,
            "human_interface_selects_artifacts": False,
            "human_interface_influences_semantic_selection": False,
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
        approved_implementation_turn_binding_hash=(
            approved_implementation_turn_binding.get("artifact_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_identity_consumption_hash=(
            approved_identity_consumption.get("artifact_hash")
            if isinstance(approved_identity_consumption, dict)
            else None
        ),
        approved_durable_governed_work_id=(
            approved_implementation_turn_binding.get("durable_governed_work_id")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_durable_governed_work_hash=(
            approved_implementation_turn_binding.get("durable_governed_work_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_proposal_preview_hash=(
            approved_implementation_turn_binding.get("proposal_preview_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_approval_request_hash=(
            approved_implementation_turn_binding.get("approval_request_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_implementation_turn_binding=deepcopy(
            approved_implementation_turn_binding
        ),
        approved_identity_consumption=deepcopy(approved_identity_consumption),
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
            "approved_identity_transport_to_canonical_continuation": isinstance(
                approved_identity_consumption, dict
            ),
            "auto_continue_stop_reason": conversation_result.get("auto_continue_stop_reason"),
            "manual_chatgpt_codex_transfer_required": not runtime_bound,
            "execution_summary_presented": bool(latest_turn.get("execution_summary_reference")),
            "human_confirmation_presented": bool(latest_turn.get("human_confirmation_reference")),
            "governance_authorization_reached": runtime_projection[
                "governance_authorization_reached"
            ],
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
            "approved_worker_payload_binding_status": latest_turn.get(
                "approved_worker_payload_binding_status"
            ),
            "approved_worker_payload_binding_hash": latest_turn.get(
                "approved_worker_payload_binding_hash"
            ),
            "approved_ppp_task_package_hash": latest_turn.get(
                "approved_ppp_task_package_hash"
            ),
            "approved_implementation_request_hash": latest_turn.get(
                "approved_implementation_request_hash"
            ),
            "approved_worker_implementation_payload_hash": latest_turn.get(
                "approved_worker_implementation_payload_hash"
            ),
            "approved_worker_payload_dispatch_blocked": latest_turn.get(
                "approved_worker_payload_dispatch_blocked"
            )
            is True,
            "approved_worker_payload_failure_reason": latest_turn.get(
                "approved_worker_payload_failure_reason"
            )
            if latest_turn.get("approved_worker_payload_binding_hash")
            else None,
            "repository_scope_grounding_status": latest_turn.get(
                "repository_scope_grounding_status"
            ),
            "repository_scope_grounding_hash": latest_turn.get(
                "repository_scope_grounding_hash"
            ),
            "repository_cognition_snapshot_hash": latest_turn.get(
                "repository_cognition_snapshot_hash"
            ),
            "grounded_repository_targets": deepcopy(
                latest_turn.get("grounded_repository_targets") or []
            ),
            "grounded_focused_test_targets": deepcopy(
                latest_turn.get("grounded_focused_test_targets") or []
            ),
            "grounded_worker_request_hash": latest_turn.get(
                "grounded_worker_request_hash"
            ),
            "repository_scope_dispatch_blocked": latest_turn.get(
                "repository_scope_dispatch_blocked"
            )
            is True,
            "authorization_review_status": latest_turn.get(
                "authorization_review_status"
            ),
            "authorization_review_hash": latest_turn.get(
                "authorization_review_hash"
            ),
            "authorization_review_artifact": deepcopy(
                latest_turn.get("authorization_review_artifact")
            )
            if isinstance(latest_turn.get("authorization_review_artifact"), dict)
            else None,
            "authorization_scope_hash": latest_turn.get(
                "authorization_scope_hash"
            ),
            "execution_summary_hash": latest_turn.get(
                "execution_summary_hash"
            ),
            "distinct_human_execution_authorization_required": latest_turn.get(
                "distinct_human_execution_authorization_required"
            )
            is True,
            "human_confirmation_required": latest_turn.get(
                "human_confirmation_required"
            )
            is True,
            "execution_authorization_required": latest_turn.get(
                "execution_authorization_required"
            )
            is True,
            "proposal_approval_is_execution_authorization": latest_turn.get(
                "proposal_approval_is_execution_authorization"
            )
            is True,
            "execution_authorized": latest_turn.get("execution_authorized") is True,
            "worker_selected": latest_turn.get("worker_selected") is True,
            "authorization_dispatch_blocked": latest_turn.get(
                "authorization_dispatch_blocked"
            )
            is True,
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
    review = result.get("authorization_review_artifact")
    if isinstance(review, dict) and review.get("authorization_review_status") == (
        "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
    ):
        return _g31_application_result(
            result,
            interface_name=interface,
            pending_action=_pending_action(
                G31_EXECUTION_DECISION,
                ("APPROVE", "REJECT"),
                review,
            ),
            presentations=(
                "Development proposal approval is complete. A distinct execution "
                "decision is now pending. No execution is authorized yet.",
            ),
        )
    return _g31_application_result(result, interface_name=interface)


def _continue_g31_application_transition(
    *,
    interface_name: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    application_state: dict[str, Any],
    human_action: str | None,
    human_actor_id: str,
    worker_process_runner: Callable[..., Any] | None,
) -> dict[str, Any]:
    """Continue one G31 application action through canonical low-level owners."""

    if not isinstance(application_state, dict):
        raise FailClosedRuntimeError("G31 application state must be a dict")
    pending = application_state.get("g31_pending_action")
    if human_action is None and not isinstance(pending, dict):
        review = application_state.get("authorization_review_artifact")
        if not isinstance(review, dict) or review.get("authorization_review_status") != (
            "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
        ):
            raise FailClosedRuntimeError(
                "G31 application initialization requires the canonical execution review"
            )
        return _g31_application_result(
            application_state,
            interface_name=interface_name,
            pending_action=_pending_action(
                G31_EXECUTION_DECISION, (G31_APPROVE, G31_REJECT), review
            ),
            presentations=(
                "Development proposal approval is complete. A distinct execution "
                "decision is now pending. No execution is authorized yet.",
            ),
        )
    actor = _require_string(human_actor_id, "g31_human_actor_id")
    action = _require_string(human_action, "g31_human_action")
    if not isinstance(pending, dict):
        raise FailClosedRuntimeError("G31 canonical pending action is required")
    action_type = _require_string(pending.get("action_type"), "g31_pending_action_type")
    valid_values = pending.get("valid_values")
    if not isinstance(valid_values, list) or action not in valid_values:
        raise FailClosedRuntimeError(
            f"G31 action {action!r} is invalid for {action_type}"
        )
    context = pending.get("context")
    if not isinstance(context, dict):
        raise FailClosedRuntimeError("G31 canonical pending context is required")

    state = deepcopy(application_state)
    presentations: list[str] = []
    next_pending: dict[str, Any] | None = None

    if action_type == G31_EXECUTION_DECISION:
        state = _record_g31_execution_decision(
            pending_execution_review=context,
            decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            render_distinct_human_execution_decision(
                state["execution_human_decision_result"]
            )
        )
        if action == "APPROVE" and state.get("governed_worker_execution_capture"):
            presentations.extend(_render_g31_execution_progress(state))
            review = worker_activation.prepare_codex_worker_activation_review(
                governed_execution_capture=state["governed_worker_execution_capture"],
                execution_candidate_capture=state["worker_execution_candidate_capture"],
                session_root=root / session,
                workspace=workspace_path,
                created_at=created,
                synthesis_preflight_capture=state.get("codex_synthesis_preflight_capture"),
            )
            state["codex_worker_activation_review_capture"] = review
            state["codex_worker_activation_synthesis_preflight_capture"] = deepcopy(
                review["synthesis_preflight_capture"]
            )
            presentations.append(worker_activation.render_codex_worker_activation_review(review))
            next_pending = _pending_action(
                G31_WORKER_ACTIVATION_DECISION, ("APPROVE", "REJECT"), review
            )

    elif action_type == G31_WORKER_ACTIVATION_DECISION:
        if action == "REJECT":
            state.update(
                {
                    "worker_activation_decision_rejected": True,
                    "third_human_decision_recorded": True,
                    "worker_process_activation_allowed": False,
                    "worker_process_started": False,
                    "provider_invoked": False,
                    "semantic_worker_result_captured": False,
                    "repository_mutated": False,
                }
            )
            presentations.append(
                "Bounded CODEX Worker process activation rejected; no process started."
            )
        else:
            state = _record_g31_worker_activation_decision(
                pending_activation_review=context,
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
                runner=worker_process_runner,
                actor=actor,
            )
            presentations.extend(
                (
                    worker_activation.render_codex_worker_activation_result(
                        state["codex_worker_activation_capture"]
                    ),
                    codex_result.render_codex_worker_result_capture(
                        state["codex_worker_result_capture_binding_capture"]
                    ),
                    codex_validation.render_codex_worker_semantic_validation(
                        state["codex_worker_semantic_validation_binding_capture"]
                    ),
                )
            )
            validation = state["codex_worker_semantic_validation_binding_capture"]
            if validation.get("g31_semantic_validation_status") == codex_validation.SUCCESS:
                state = _prepare_g31_task_outcome_review(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
                review = state["codex_task_outcome_review_capture"]
                presentations.extend(
                    (
                        codex_task_review.render_codex_task_outcome_review(review),
                        _render_task_outcome_review_lineage(review),
                        "Exact-byte task-outcome decision pending. No decision accepts "
                        "or applies the patch.",
                    )
                )
                next_pending = _pending_action(
                    G31_TASK_OUTCOME_DECISION,
                    (
                        codex_task_review.TASK_OUTCOME_SATISFIED,
                        codex_task_review.TASK_OUTCOME_UNSATISFIED,
                        codex_task_review.REWORK_REQUESTED,
                    ),
                    review,
                )
            else:
                state["task_outcome_review_blocked"] = True
                state["task_outcome_review_blocker"] = (
                    "G31 governance validation did not return RESULT_VALIDATED"
                )
                presentations.append(
                    "Task-outcome review was not requested because G31 governance "
                    "validation did not return RESULT_VALIDATED."
                )

    elif action_type == G31_TASK_OUTCOME_DECISION:
        state = _record_g31_task_outcome_decision(
            pending_task_outcome_review=context,
            task_outcome_decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            codex_task_review.render_codex_task_outcome_decision(
                state["codex_task_outcome_human_decision_capture"]
            )
        )
        if action == codex_task_review.TASK_OUTCOME_SATISFIED:
            try:
                state = _prepare_g31_disposable_patch_validation_review(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
            except FailClosedRuntimeError as exc:
                state["disposable_patch_validation_review_blocked"] = True
                state["disposable_patch_validation_review_blocker"] = str(exc)
                presentations.append(
                    f"Disposable patch-validation review failed closed: {exc}"
                )
            else:
                review = state["disposable_patch_validation_review_capture"]
                presentations.extend(
                    (
                        disposable_validation.render_disposable_patch_validation_review(
                            review, state["codex_task_outcome_review_capture"]
                        ),
                        "Disposable-only validation decision pending. No patch or test has run.",
                    )
                )
                next_pending = _pending_action(
                    G31_DISPOSABLE_VALIDATION_DECISION,
                    (human_decision.APPROVE, human_decision.REJECT),
                    review,
                )

    elif action_type == G31_DISPOSABLE_VALIDATION_DECISION:
        state = _record_g31_disposable_patch_validation_decision(
            pending_review=context,
            decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            human_decision.render_human_decision_summary(
                state["disposable_patch_validation_human_decision_capture"]
            )
        )
        if action == human_decision.APPROVE:
            state = _execute_g31_disposable_patch_validation(
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
                actor=actor,
            )
            outcome = state["disposable_patch_validation_outcome_capture"]
            presentations.append(
                disposable_validation.render_disposable_patch_validation_outcome(outcome)
            )
            if outcome["outcome_artifact"]["execution_status"] == disposable_validation.COMPLETED:
                state = _bind_g31_replacement_acceptance_prerequisites(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
                presentations.append(
                    replacement_prerequisites.render_codex_replacement_acceptance_prerequisites(
                        state["codex_replacement_acceptance_prerequisite_binding_capture"],
                        state["codex_replacement_acceptance_prerequisite_binding_reconstruction"],
                    )
                )
                binding = state[
                    "codex_replacement_acceptance_prerequisite_binding_capture"
                ]["binding_artifact"]
                content_context = human_decision.prepare_content_acceptance_decision_context(
                    context_id=f"G31-CONTENT-ACCEPTANCE-{binding['artifact_hash'][-16:]}",
                    binding_capture=state[
                        "codex_replacement_acceptance_prerequisite_binding_capture"
                    ],
                    human_actor_id=actor,
                    presented_at=created,
                    session_root=root / session,
                    replay_dir=root / session
                    / f"CONTENT-ACCEPTANCE-DECISION-{binding['artifact_hash'][-16:]}",
                )
                state["human_content_acceptance_context_capture"] = content_context
                presentations.append(
                    human_decision.render_content_acceptance_decision_context(content_context)
                )
                next_pending = _pending_action(
                    G31_CONTENT_ACCEPTANCE_DECISION,
                    (human_decision.ACCEPTED, human_decision.REJECTED),
                    content_context,
                )

    elif action_type == G31_CONTENT_ACCEPTANCE_DECISION:
        state, next_pending, content_presentations = _record_g31_content_decision(
            context_capture=context,
            outcome=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.extend(content_presentations)

    elif action_type == G31_MUTATION_DECISION:
        state = _record_g31_mutation_decision(
            context_capture=context,
            outcome=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            human_decision.render_existing_file_mutation_decision(
                state["human_mutation_decision_capture"]
            )
        )
        if action == human_decision.MUTATION_APPROVED:
            state = _authorize_g31_mutation_decision(
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
            )
            authorization = state[
                "mutation_authorization_actor_replay_reconstruction"
            ]
            request = state["authenticated_replacement_request"]
            request_replay = state[
                "authenticated_replacement_request_reconstruction"
            ]
            consumption = state["authorization_consumption_reconstruction"]
            presentations.append(
                "\n".join(
                    (
                        "Canonical Existing-File Mutation Authorization",
                        f"Authorization ID: {authorization['authorization_id']}",
                        f"Authorization Status: {authorization['authorization_status']}",
                        "Canonical Authorization Actor: "
                        f"{authorization['canonical_authorization_actor']}",
                        f"Target Path: {authorization['target_path']}",
                        "Authorization Replay Recorded: True",
                        "Authorization Consumed: True",
                        "Authenticated Replacement Request",
                        f"Request ID: {request['request_id']}",
                        f"Request Hash: {request['request_hash']}",
                        f"Request Replay Hash: {request_replay['replay_hash']}",
                        "Replacement Request Created: True",
                        "Single-Use Consumption Identity: "
                        f"{consumption['consumption_identity']}",
                        "Authorization Consumption Reached: True",
                        "Worker Selection Reached: True",
                        "Worker Invocation Request Created: "
                        f"{state['worker_invocation_request_created']}",
                        "Worker Assignment Reached: False",
                        "Repository Mutated: False",
                    )
                )
            )
            presentations.append(
                render_authorized_grounded_worker_selection(
                    state["consumed_replacement_worker_selection_capture"]
                )
            )
            presentations.append(
                worker_request.render_worker_invocation_request_summary(
                    state["worker_invocation_request_capture"]
                )
            )
    else:
        raise FailClosedRuntimeError(f"unsupported G31 pending action: {action_type}")

    return _g31_application_result(
        state,
        interface_name=interface_name,
        pending_action=next_pending,
        presentations=presentations,
    )


def _pending_action(
    action_type: str,
    valid_values: tuple[str, ...],
    context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "valid_values": list(valid_values),
        "context": deepcopy(context),
    }


def _g31_application_result(
    state: dict[str, Any],
    *,
    interface_name: str,
    pending_action: dict[str, Any] | None = None,
    presentations: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    result = deepcopy(state)
    result.update(
        {
            "g31_application_transition_version": G31_APPLICATION_TRANSITION_VERSION,
            "g31_application_state_authority": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "g31_application_sequenced_by_common_entry": True,
            "g31_application_interface_transport": interface_name,
            "g31_pending_action": deepcopy(pending_action),
            "g31_canonical_presentations": list(presentations),
        }
    )
    return result


def _render_g31_execution_progress(state: dict[str, Any]) -> list[str]:
    lines = [render_execution_authorization_summary(state["execution_authorization_capture"])]
    lines.append(
        render_authorized_grounded_worker_selection(
            state["authorized_worker_selection_capture"]
        )
    )
    renderers = (
        ("worker_invocation_request_capture", worker_request.render_worker_invocation_request_summary),
        ("worker_assignment_capture", worker_assignment.render_worker_assignment_summary),
        ("worker_dispatch_capture", worker_dispatch.render_worker_dispatch_summary),
        ("worker_invocation_capture", worker_invocation.render_worker_invocation_summary),
        ("worker_execution_candidate_capture", worker_candidate.render_worker_execution_candidate_summary),
        ("governed_worker_execution_capture", governed_execution.render_governed_worker_execution_summary),
    )
    for field, renderer in renderers:
        if state.get(field):
            lines.append(renderer(state[field]))
    return lines


def _record_g31_execution_decision(
    *,
    pending_execution_review: dict[str, Any],
    decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    review_hash = _require_string(
        pending_execution_review.get("artifact_hash"), "authorization_review_hash"
    )
    decision_result = bind_distinct_human_execution_decision(
        authorization_review_artifact=pending_execution_review,
        human_decision=decision,
        session_id=session,
        decided_by=actor,
        decided_at=created,
        workspace=workspace_path,
        session_root=root / session,
        replay_dir=root / session / f"EXECUTION-DECISION-{review_hash[-16:]}",
    )
    confirmation = decision_result.get("human_confirmation_artifact") or {}
    merged = deepcopy(runtime_result)
    merged.update(
        {
            "execution_human_decision_result": decision_result,
            "execution_human_decision_status": decision_result.get("decision_status"),
            "execution_human_decision_hash": decision_result.get("artifact_hash"),
            "execution_summary_human_confirmation": decision_result.get(
                "execution_summary_human_confirmation"
            )
            is True,
            "execution_decision_rejected": decision_result.get("decision_status")
            == EXECUTION_DECISION_REJECTED,
            "human_confirmation_reference": confirmation.get("confirmation_id"),
            "human_confirmation_hash": decision_result.get("human_confirmation_hash"),
            "runtime_replay_reference": decision_result.get("replay_reference"),
            "execution_authorized": False,
            "worker_selected": False,
            "authorization_dispatch_blocked": True,
        }
    )
    if decision_result.get("decision_status") != EXECUTION_DECISION_APPROVED:
        return merged

    authorization = authorize_confirmed_grounded_execution_decision(
        human_execution_decision_artifact=decision_result,
        workspace=workspace_path,
        session_root=root / session,
        replay_dir=root
        / session
        / f"EXECUTION-AUTHORIZATION-{decision_result['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "execution_authorization_capture": authorization,
            "execution_authorization_status": authorization.get("authorization_status"),
            "execution_authorized": authorization.get("execution_authorized") is True,
            "authorization_dispatch_blocked": True,
            "runtime_replay_reference": authorization.get(
                "execution_authorization_replay_reference"
            ),
        }
    )
    if authorization.get("execution_authorized") is not True:
        return merged

    selection = select_authorized_grounded_worker(
        execution_authorization_capture=authorization,
        session_root=root / session,
        replay_dir=root
        / session
        / (
            "WORKER-SELECTION-"
            f"{authorization['execution_authorization_artifact']['artifact_hash'][-16:]}"
        ),
    )
    merged.update(
        {
            "authorized_worker_selection_capture": selection,
            "worker_selection_status": selection.get("selection_status"),
            "selected_resource_id": selection.get("selected_resource_id"),
            "selected_role_type": selection.get("selected_role_type"),
            "worker_selected": selection.get("worker_selected") is True,
            "worker_assigned": False,
            "worker_dispatched": False,
            "runtime_replay_reference": selection.get(
                "resource_selection_replay_reference"
            ),
        }
    )
    if selection.get("worker_selected") is not True:
        return merged

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
        replay_dir=root
        / session
        / f"WORKER-REQUEST-{selection_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_invocation_request_capture": invocation_request,
            "worker_invocation_request_status": invocation_request.get("request_status"),
            "worker_invocation_request_created": invocation_request.get("request_status")
            == worker_request.WORKER_INVOCATION_REQUEST_CREATED,
            "runtime_replay_reference": invocation_request.get(
                "worker_invocation_request_replay_reference"
            ),
        }
    )
    if invocation_request.get("request_status") != worker_request.WORKER_INVOCATION_REQUEST_CREATED:
        return merged

    request_artifact = invocation_request["worker_invocation_request_artifact"]
    assignment = worker_assignment.assign_worker_from_invocation_request(
        worker_assignment_id=f"{selection_artifact['selection_id']}:ASSIGNMENT",
        worker_invocation_request_artifact=request_artifact,
        worker_invocation_request_replay_reference=invocation_request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=worker_assignment.default_worker_registry_for_request(
            request_artifact, created_at=created
        ),
        assigned_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
        assigned_at=created,
        replay_dir=root
        / session
        / f"WORKER-ASSIGNMENT-{request_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_assignment_capture": assignment,
            "worker_assignment_status": assignment.get("assignment_status"),
            "worker_assigned": assignment.get("assignment_status")
            == worker_assignment.WORKER_ASSIGNED,
            "worker_dispatched": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "runtime_replay_reference": assignment.get(
                "worker_assignment_replay_reference"
            ),
        }
    )
    if assignment.get("assignment_status") != worker_assignment.WORKER_ASSIGNED:
        return merged

    assignment_artifact = assignment["worker_assignment_artifact"]
    dispatch = worker_dispatch.dispatch_assigned_worker(
        worker_dispatch_id=f"{assignment_artifact['worker_assignment_id']}:DISPATCH",
        worker_assignment_artifact=assignment_artifact,
        worker_assignment_replay_reference=assignment[
            "worker_assignment_replay_reference"
        ],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=created,
        replay_dir=root
        / session
        / f"WORKER-DISPATCH-{assignment_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_dispatch_capture": dispatch,
            "worker_dispatch_status": dispatch.get("dispatch_status"),
            "worker_dispatched": dispatch.get("dispatch_status")
            == worker_dispatch.WORKER_DISPATCHED,
            "authorization_dispatch_blocked": dispatch.get("dispatch_status")
            != worker_dispatch.WORKER_DISPATCHED,
            "provider_invoked": False,
            "worker_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "runtime_replay_reference": dispatch.get(
                "worker_dispatch_replay_reference"
            ),
        }
    )
    if dispatch.get("dispatch_status") != worker_dispatch.WORKER_DISPATCHED:
        return merged

    dispatch_artifact = dispatch["worker_dispatch_artifact"]
    invocation = worker_invocation.invoke_dispatched_worker(
        worker_invocation_id=f"{dispatch_artifact['worker_dispatch_id']}:INVOCATION",
        worker_dispatch_artifact=dispatch_artifact,
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=created,
        replay_dir=root
        / session
        / f"WORKER-INVOCATION-{dispatch_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_invocation_capture": invocation,
            "worker_invocation_status": invocation.get("invocation_status"),
            "worker_invoked": invocation.get("invocation_status")
            == worker_invocation.WORKER_INVOKED,
            "provider_invoked": False,
            "execution_started": False,
            "command_executed": False,
            "result_created": False,
            "repository_mutated": False,
            "runtime_replay_reference": invocation.get(
                "worker_invocation_replay_reference"
            ),
        }
    )
    if invocation.get("invocation_status") != worker_invocation.WORKER_INVOKED:
        return merged

    invocation_artifact = invocation["worker_invocation_artifact"]
    candidate = worker_candidate.project_g31_invocation_to_execution_candidate(
        worker_invocation_artifact=invocation_artifact,
        worker_invocation_replay_reference=invocation[
            "worker_invocation_replay_reference"
        ],
        session_root=root / session,
        requested_by="PLATFORM_CORE_G31_CANDIDATE_BINDING",
        created_at=created,
        replay_dir=root
        / session
        / f"WORKER-EXECUTION-CANDIDATE-{invocation_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_execution_candidate_capture": candidate,
            "execution_candidate_created": candidate.get(
                "worker_execution_candidate_generated"
            )
            is True,
            "provider_invoked": False,
            "worker_process_started": False,
            "execution_started": False,
            "command_executed": False,
            "result_created": False,
            "repository_mutated": False,
            "runtime_replay_reference": candidate.get(
                "worker_execution_candidate_replay_reference"
            ),
        }
    )
    if candidate.get("worker_execution_candidate_generated") is not True:
        return merged

    execution = governed_execution.project_g31_candidate_to_governed_execution(
        execution_candidate_capture=candidate,
        session_root=root / session,
        executed_by="PLATFORM_CORE_G31_GOVERNED_EXECUTION_BINDING",
        executed_at=created,
        replay_dir=root
        / session
        / (
            "GOVERNED-WORKER-EXECUTION-"
            f"{candidate['worker_execution_candidate_artifact']['artifact_hash'][-16:]}"
        ),
    )
    merged.update(
        {
            "governed_worker_execution_capture": execution,
            "governed_execution_evidence_created": execution.get(
                "worker_execution_completed"
            )
            is True,
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
        }
    )
    return merged


def _record_g31_worker_activation_decision(
    *,
    pending_activation_review: dict[str, Any],
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    runner: Callable[..., Any] | None,
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review = pending_activation_review["activation_review_artifact"]
    capture = worker_activation.activate_bounded_codex_worker(
        activation_review_artifact=review,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        human_decision="APPROVE",
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
        workspace=workspace_path,
        replay_dir=root
        / session
        / f"CODEX-WORKER-ACTIVATION-{review['artifact_hash'][-16:]}",
        runner=runner,
    )
    merged.update(
        {
            "codex_worker_activation_capture": capture,
            "runtime_replay_reference": capture["activation_replay_reference"],
            **{
                field: capture[field]
                for field in worker_activation.ACTIVATION_TRUTH_FIELDS
            },
        }
    )
    result = codex_result.capture_successful_codex_worker_result(
        activation_capture=capture,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        captured_at=created,
        replay_dir=root
        / session
        / (
            "CODEX-WORKER-RESULT-CAPTURE-"
            f"{capture['codex_transport_receipt']['receipt_id'][-16:]}"
        ),
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
        replay_dir=root
        / session
        / f"CODEX-WORKER-RESULT-VALIDATION-{result.get('worker_output_hash', '')[-16:]}",
    )
    merged["codex_worker_semantic_validation_binding_capture"] = validation
    merged.update(
        {field: validation[field] for field in codex_validation.VALIDATION_TRUTH_FIELDS}
    )
    return merged


def _prepare_g31_task_outcome_review(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
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
        replay_dir=root
        / session
        / (
            "CODEX-TASK-OUTCOME-REVIEW-"
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
    merged.update(
        {
            "codex_task_outcome_review_capture": review,
            "codex_task_outcome_review_reconstruction": reconstruction,
            "task_outcome_review_status": review["review_status"],
            "task_outcome_review_replay_created": True,
            "task_outcome_review_count": 1,
            "human_task_outcome_decision_recorded": False,
        }
    )
    return merged


def _record_g31_task_outcome_decision(
    *,
    pending_task_outcome_review: dict[str, Any],
    task_outcome_decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review_packet = pending_task_outcome_review["task_outcome_review_packet_artifact"]
    decision = codex_task_review.record_codex_task_outcome_human_decision(
        review_capture=pending_task_outcome_review,
        task_outcome_decision=task_outcome_decision,
        decision_reason=(
            "Human operator selected the explicit task-outcome decision after "
            "canonical presentation of the exact captured Worker output and lineage."
        ),
        decided_by=actor,
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
        human_decision_replay_dir=root
        / session
        / (
            "CODEX-TASK-OUTCOME-HUMAN-DECISION-"
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
    merged.update(
        {
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
        }
    )
    return merged


def _g31_disposable_lineage(
    state: dict[str, Any], *, session_root: Path, workspace_path: str
) -> dict[str, Any]:
    return {
        "task_outcome_decision_capture": state[
            "codex_task_outcome_human_decision_capture"
        ],
        "review_capture": state["codex_task_outcome_review_capture"],
        "result_capture_binding_capture": state[
            "codex_worker_result_capture_binding_capture"
        ],
        "validation_binding_capture": state[
            "codex_worker_semantic_validation_binding_capture"
        ],
        "activation_capture": state["codex_worker_activation_capture"],
        "governed_execution_capture": state["governed_worker_execution_capture"],
        "execution_candidate_capture": state["worker_execution_candidate_capture"],
        "session_root": session_root,
        "source_workspace": workspace_path,
    }


def _prepare_g31_disposable_patch_validation_review(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    decision = merged["codex_task_outcome_human_decision_capture"]
    identity = decision["human_decision_capture"]["human_decision_artifact"][
        "artifact_hash"
    ][-16:]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    review = disposable_validation.prepare_disposable_patch_validation_review(
        disposable_workspace=root / session / f"DISPOSABLE-PATCH-VALIDATION-{identity}",
        prepared_at=created,
        replay_dir=root
        / session
        / f"DISPOSABLE-PATCH-VALIDATION-REVIEW-{identity}",
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_review(
        review_binding_capture=review, **lineage
    )
    merged.update(
        {
            "disposable_patch_validation_review_capture": review,
            "disposable_patch_validation_review_reconstruction": reconstruction,
            "disposable_patch_validation_review_pending": True,
            "disposable_patch_validation_decision_recorded": False,
            "disposable_patch_validation_executed": False,
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _record_g31_disposable_patch_validation_decision(
    *,
    pending_review: dict[str, Any],
    decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    plan = pending_review["disposable_patch_validation_plan_artifact"]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    capture = disposable_validation.record_disposable_patch_validation_human_decision(
        review_binding_capture=pending_review,
        decision=decision,
        decision_reason=(
            "Human operator selected the explicit disposable validation decision "
            "through the canonical Human Interface application entry."
        ),
        decided_by=actor,
        decided_at=created,
        human_decision_replay_dir=root
        / session
        / (
            "DISPOSABLE-PATCH-VALIDATION-HUMAN-DECISION-"
            f"{plan['artifact_hash'][-16:]}"
        ),
        **lineage,
    )
    merged.update(
        {
            "disposable_patch_validation_human_decision_capture": capture,
            "disposable_patch_validation_human_decision_reconstruction": (
                human_decision.reconstruct_human_decision_replay(
                    capture["human_decision_replay_reference"]
                )
            ),
            "disposable_patch_validation_review_pending": False,
            "disposable_patch_validation_decision_recorded": True,
            "disposable_patch_validation_executed": False,
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _execute_g31_disposable_patch_validation(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review = merged["disposable_patch_validation_review_capture"]
    plan = review["disposable_patch_validation_plan_artifact"]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    outcome = disposable_validation.execute_disposable_patch_validation(
        review_binding_capture=review,
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        executed_by=actor,
        executed_at=created,
        replay_dir=root
        / session
        / f"DISPOSABLE-PATCH-VALIDATION-OUTCOME-{plan['artifact_hash'][-16:]}",
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_outcome(
        outcome_capture=outcome,
        review_binding_capture=review,
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        **lineage,
    )
    artifact = outcome["outcome_artifact"]
    merged.update(
        {
            "disposable_patch_validation_outcome_capture": outcome,
            "disposable_patch_validation_outcome_reconstruction": reconstruction,
            "disposable_patch_validation_approved": True,
            "disposable_patch_validation_executed": artifact[
                "disposable_patch_application_attempted"
            ],
            "disposable_patch_application_succeeded": artifact[
                "disposable_patch_applied"
            ]
            and artifact["content_validation_passed"],
            "focused_validation_executed": artifact[
                "grounded_test_execution_performed"
            ],
            "focused_validation_succeeded": artifact[
                "grounded_test_validation_passed"
            ],
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    merged.update(
        {
            key: outcome[key]
            for key in (
                "disposable_patch_applied",
                "content_validation_performed",
                "content_validation_passed",
                "grounded_test_execution_performed",
                "grounded_test_validation_passed",
                "ready_for_generated_content_acceptance",
                "repository_mutation_authorized",
                "failure_reason",
            )
        }
    )
    return merged


def _bind_g31_replacement_acceptance_prerequisites(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    outcome = merged["disposable_patch_validation_outcome_capture"]
    outcome_hash = outcome["outcome_artifact"]["artifact_hash"]
    capture = replacement_prerequisites.bind_codex_replacement_acceptance_prerequisites(
        disposable_validation_outcome_capture=outcome,
        disposable_validation_review_capture=merged[
            "disposable_patch_validation_review_capture"
        ],
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        task_outcome_decision_capture=merged[
            "codex_task_outcome_human_decision_capture"
        ],
        task_outcome_review_capture=merged["codex_task_outcome_review_capture"],
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        governance_validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        source_workspace=workspace_path,
        created_at=created,
        replay_dir=root
        / session
        / f"G31-REPLACEMENT-ACCEPTANCE-PREREQUISITES-{outcome_hash[-16:]}",
    )
    reconstruction = replacement_prerequisites.reconstruct_codex_replacement_acceptance_prerequisite_binding(
        binding_capture=capture, session_root=root / session
    )
    merged["codex_replacement_acceptance_prerequisite_binding_capture"] = capture
    merged[
        "codex_replacement_acceptance_prerequisite_binding_reconstruction"
    ] = reconstruction
    merged.update(
        {
            key: capture[key]
            for key in (
                "replacement_manifest_created",
                "acceptance_prerequisites_satisfied",
                "ready_for_acceptance",
                "result_accepted",
                "mutation_authorized",
                "main_repository_mutated",
            )
        }
    )
    return merged


def _record_g31_content_decision(
    *,
    context_capture: dict[str, Any],
    outcome: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, list[str]]:
    merged = deepcopy(runtime_result)
    binding = merged["codex_replacement_acceptance_prerequisite_binding_capture"]
    capture = human_decision.record_content_acceptance_decision(
        context_capture=context_capture,
        binding_capture=binding,
        decision_outcome=outcome,
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
    )
    reconstruction = human_decision.reconstruct_content_acceptance_decision_replay(
        decision_capture=capture,
        binding_capture=binding,
        session_root=root / session,
    )
    merged.update(
        {
            "human_content_acceptance_decision_capture": capture,
            "human_content_acceptance_decision_reconstruction": reconstruction,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    presentations = [human_decision.render_content_acceptance_decision(capture)]
    if outcome != human_decision.ACCEPTED:
        return merged, None, presentations

    artifact = capture["human_decision_artifact"]
    suffix = artifact["artifact_hash"][-16:]
    accepted = generated_acceptance.accept_generated_content_from_content_acceptance_decision(
        acceptance_id=f"G31-GENERATED-CONTENT-ACCEPTANCE-{suffix}",
        decision_capture=capture,
        binding_capture=binding,
        created_at=created,
        session_root=root / session,
        replay_dir=root / session / f"GENERATED-CONTENT-ACCEPTANCE-{suffix}",
    )
    accepted_reconstruction = generated_acceptance.reconstruct_generated_content_acceptance_from_decision_replay(
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        session_root=root / session,
    )
    activation_binding = worker_activation.reconstruct_codex_worker_activation_binding(
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    grounding = activation_binding["lineage"]["grounding"]
    candidate = existing_file_candidate.create_g31_accepted_existing_file_mutation_candidate(
        candidate_id=f"G31-EXISTING-FILE-CANDIDATE-{suffix}",
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=root / session,
        created_by=actor,
        created_at=created,
        replay_dir=root / session / f"EXISTING-FILE-CANDIDATE-{suffix}",
    )
    candidate_reconstruction = existing_file_candidate.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
        candidate_capture=candidate,
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=root / session,
    )
    candidate_hash = candidate["existing_file_mutation_candidate_artifact"]["artifact_hash"]
    mutation_context = human_decision.prepare_existing_file_mutation_decision_context(
        context_id=f"G31-MUTATION-DECISION-{candidate_hash[-16:]}",
        candidate_capture=candidate,
        acceptance_capture=accepted,
        content_decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        human_actor_id=actor,
        presented_at=created,
        session_root=root / session,
        replay_dir=root / session / f"G31-MUTATION-DECISION-{candidate_hash[-16:]}",
    )
    merged.update(
        {
            "generated_content_acceptance_capture": accepted,
            "generated_content_acceptance_reconstruction": accepted_reconstruction,
            "existing_file_mutation_candidate_capture": candidate,
            "existing_file_mutation_candidate_reconstruction": candidate_reconstruction,
            "existing_file_mutation_candidate_created": True,
            "human_mutation_decision_context_capture": mutation_context,
            "codex_worker_activation_binding_reconstruction": activation_binding,
            "repository_grounding_artifact": deepcopy(grounding),
            "human_mutation_decision_actor": actor,
            "human_mutation_decision_recorded": False,
            "result_accepted": True,
            "mutation_authorized": False,
            "authorization_actor_bound": False,
            "authorization_replay_recorded": False,
            "authorization_consumed": False,
            "replace_request_created": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "main_repository_mutated": False,
        }
    )
    presentations.extend(
        (
            generated_acceptance.render_generated_content_acceptance_from_decision(
                accepted, binding
            ),
            existing_file_candidate.render_g31_accepted_existing_file_mutation_candidate(
                candidate
            ),
            human_decision.render_existing_file_mutation_decision_context(mutation_context),
            "Enter exact APPROVED or REJECTED.",
        )
    )
    return (
        merged,
        _pending_action(
            G31_MUTATION_DECISION,
            (human_decision.MUTATION_APPROVED, human_decision.REJECTED),
            mutation_context,
        ),
        presentations,
    )


def _record_g31_mutation_decision(
    *,
    context_capture: dict[str, Any],
    outcome: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    grounding = merged.get("repository_grounding_artifact")
    if not isinstance(grounding, dict):
        raise FailClosedRuntimeError("canonical repository grounding is required")
    capture = human_decision.record_existing_file_mutation_decision(
        context_capture=context_capture,
        candidate_capture=merged["existing_file_mutation_candidate_capture"],
        acceptance_capture=merged["generated_content_acceptance_capture"],
        content_decision_capture=merged["human_content_acceptance_decision_capture"],
        binding_capture=merged["codex_replacement_acceptance_prerequisite_binding_capture"],
        repository_grounding_artifact=grounding,
        decision_outcome=outcome,
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
    )
    reconstruction = human_decision.reconstruct_existing_file_mutation_decision_replay(
        decision_capture=capture,
        candidate_capture=merged["existing_file_mutation_candidate_capture"],
        acceptance_capture=merged["generated_content_acceptance_capture"],
        content_decision_capture=merged["human_content_acceptance_decision_capture"],
        binding_capture=merged["codex_replacement_acceptance_prerequisite_binding_capture"],
        repository_grounding_artifact=grounding,
        session_root=root / session,
    )
    merged.update(
        {
            "human_mutation_decision_context_capture": context_capture,
            "human_mutation_decision_capture": capture,
            "human_mutation_decision_reconstruction": reconstruction,
            "repository_grounding_artifact": deepcopy(grounding),
            "human_mutation_decision_actor": actor,
            "human_mutation_decision_recorded": True,
            "mutation_decision_recorded": True,
            "mutation_decision_approved": outcome == human_decision.MUTATION_APPROVED,
            "mutation_authorized": False,
            "authorization_actor_bound": False,
            "authorization_replay_recorded": False,
            "authorization_consumed": False,
            "replace_request_created": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _authorize_g31_mutation_decision(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Sequence exact reconstructed APPROVED V3 evidence through existing owners."""

    merged = deepcopy(runtime_result)
    decision = merged.get("human_mutation_decision_capture") or {}
    artifact = decision.get("human_mutation_decision_artifact") or {}
    session_root = root / session
    evidence = {
        "candidate_capture": merged["existing_file_mutation_candidate_capture"],
        "candidate_reconstruction": merged[
            "existing_file_mutation_candidate_reconstruction"
        ],
        "mutation_decision_capture": decision,
        "mutation_decision_reconstruction": merged[
            "human_mutation_decision_reconstruction"
        ],
        "acceptance_capture": merged["generated_content_acceptance_capture"],
        "content_decision_capture": merged[
            "human_content_acceptance_decision_capture"
        ],
        "binding_capture": merged[
            "codex_replacement_acceptance_prerequisite_binding_capture"
        ],
        "repository_grounding_artifact": merged["repository_grounding_artifact"],
        "activation_capture": merged["codex_worker_activation_capture"],
        "activation_binding": merged[
            "codex_worker_activation_binding_reconstruction"
        ],
        "governed_execution_capture": merged["governed_worker_execution_capture"],
        "execution_candidate_capture": merged["worker_execution_candidate_capture"],
        "session_root": session_root,
        "workspace": workspace_path,
    }
    authorization = existing_file_governance.authorize_g31_approved_existing_file_mutation(
        authorization_id=(
            "G31-MUTATION-AUTHORIZATION-" + artifact["artifact_hash"][-16:]
        ),
        authorization_timestamp=created,
        **evidence,
    )
    authorization_reconstruction = (
        existing_file_governance.reconstruct_g31_existing_file_mutation_authorization_binding(
            authorization_capture=authorization,
            **evidence,
        )
    )
    actor_replay = existing_file_governance.bind_g31_mutation_authorization_actor_and_replay(
        authorization_capture=authorization,
        **evidence,
    )
    actor_replay_reconstruction = (
        existing_file_governance.reconstruct_g31_mutation_authorization_actor_and_replay(
            actor_replay_capture=actor_replay,
            authorization_capture=authorization,
            **evidence,
        )
    )
    request = existing_file_governance.create_g31_authenticated_replace_request(
        actor_replay_capture=actor_replay,
        authorization_capture=authorization,
        **evidence,
    )
    request_reconstruction = (
        filesystem_replace_worker.record_authenticated_replace_request_v2(request)
    )
    consumption_reconstruction = (
        filesystem_replace_worker.consume_authenticated_replace_authorization_v2(
            request
        )
    )
    selection = existing_file_governance.bind_consumed_g31_authenticated_replace_worker_selection(
        authenticated_request=request,
        authorization_reconstruction=actor_replay_reconstruction,
        consumption_reconstruction=consumption_reconstruction,
        replay_dir=session_root
        / f"FILESYSTEM-REPLACE-WORKER-SELECTION-{request['request_hash'][-16:]}",
    )
    selection_artifact = selection["resource_selection_artifact"]
    invocation_request = (
        worker_request.create_authenticated_replacement_worker_invocation_request(
            invocation_request_id=(
                f"{selection_artifact['selection_id']}:INVOCATION-REQUEST"
            ),
            authenticated_request=request,
            consumption_reconstruction=consumption_reconstruction,
            resource_selection_capture=selection,
            worker_selection_certification_reference=str(
                existing_file_governance.R08B_CERTIFICATION_PATH
            ),
            requested_by="PLATFORM_CORE_G31_INVOCATION_REQUEST_COMPATIBILITY",
            requested_at=created,
            replay_dir=session_root
            / f"WORKER-REQUEST-{selection_artifact['artifact_hash'][-16:]}",
        )
    )
    merged.update(
        {
            "mutation_authorization_capture": authorization,
            "mutation_authorization_reconstruction": authorization_reconstruction,
            "mutation_authorization_actor_replay_capture": actor_replay,
            "mutation_authorization_actor_replay_reconstruction": (
                actor_replay_reconstruction
            ),
            "mutation_authorization_id": actor_replay_reconstruction[
                "authorization_id"
            ],
            "mutation_authorization_hash": actor_replay_reconstruction[
                "authorization_hash"
            ],
            "authenticated_replacement_request": request,
            "authenticated_replacement_request_reconstruction": (
                request_reconstruction
            ),
            "authenticated_replacement_request_id": request["request_id"],
            "authenticated_replacement_request_hash": request["request_hash"],
            "authenticated_replacement_request_replay_reference": (
                request_reconstruction["request_replay_reference"]
            ),
            "authenticated_replacement_request_replay_hash": (
                request_reconstruction["replay_hash"]
            ),
            "authorization_consumption_reconstruction": consumption_reconstruction,
            "authorization_consumption_identity": consumption_reconstruction[
                "consumption_identity"
            ],
            "authorization_consumption_replay_reference": (
                consumption_reconstruction["request_replay_reference"]
            ),
            "authorization_consumption_replay_hash": consumption_reconstruction[
                "replay_hash"
            ],
            "consumed_replacement_worker_selection_capture": selection,
            "consumed_replacement_worker_selection_reconstruction": selection[
                "certified_selection_reconstruction"
            ],
            "consumed_replacement_selection_context": selection[
                "consumed_replacement_selection_context"
            ],
            "consumed_replacement_selection_context_hash": selection[
                "consumed_replacement_selection_context_hash"
            ],
            "worker_selection_status": selection["selection_status"],
            "selected_resource_id": selection["selected_resource_id"],
            "selected_role_type": selection["selected_role_type"],
            "worker_selected": selection["worker_selected"],
            "worker_invocation_request_capture": invocation_request,
            "worker_invocation_request_status": invocation_request[
                "request_status"
            ],
            "worker_invocation_request_created": invocation_request[
                "request_status"
            ] == worker_request.WORKER_INVOCATION_REQUEST_CREATED,
            "worker_assigned": False,
            "worker_dispatched": False,
            "runtime_replay_reference": invocation_request[
                "worker_invocation_request_replay_reference"
            ],
        }
    )
    for field in (
        "mutation_authorized",
        "authorization_actor_bound",
        "authorization_replay_recorded",
        "authorization_consumed",
        "replace_request_created",
        "worker_invoked",
        "provider_invoked",
        "command_executed",
        "repository_mutated",
        "main_repository_mutated",
    ):
        merged[field] = actor_replay_reconstruction[field]
    merged["replace_request_created"] = True
    merged["authorization_consumed"] = True
    return merged


def _render_task_outcome_review_lineage(review: dict[str, Any]) -> str:
    """Render exact review identities without acquiring authority."""

    packet = review["task_outcome_review_packet_artifact"]
    capture = packet["capture_binding"]
    capture_artifact = capture["artifact"]
    validation = packet["governance_validation_binding"]
    validation_artifact = validation["artifact"]
    return "\n".join(
        (
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
        )
    )


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
    execution_authorization_artifact = _read_replay_artifact_path(
        turn_replay_root
        / "governed_bridge_certified_development_continuation"
        / "execution_authorization"
        / "002_authorization_artifact_recorded.json"
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
    latest_turn_authorization_status = latest_turn.get("execution_authorization_status")
    execution_authorization_artifact_recognized = (
        execution_authorization_artifact.get("artifact_type")
        == "EXECUTION_AUTHORIZATION_ARTIFACT_V1"
    )
    authorization_status = (
        latest_turn_authorization_status
        if latest_turn_authorization_status is not None
        else (
            execution_authorization_artifact.get("authorization_status")
            if execution_authorization_artifact_recognized
            else None
        )
    )
    governance_authorization_reached = authorization_status == "EXECUTION_AUTHORIZED"
    projection_evidence = {
        "latest_turn_used": bool(latest_turn),
        "turn_replay_discovery_used": turn_replay_root is not None,
        "turn_replay_root": str(turn_replay_root) if turn_replay_root is not None else None,
        "worker_lifecycle_replay_root": (
            str(worker_lifecycle_root) if worker_lifecycle_root is not None else None
        ),
        "execution_authorization_replay_inspected": bool(execution_authorization_artifact),
        "execution_authorization_artifact_recognized": (
            execution_authorization_artifact_recognized
        ),
        "execution_authorization_status": authorization_status,
        "execution_authorization_status_source": (
            "LATEST_TURN"
            if latest_turn_authorization_status is not None
            else (
                "EXECUTION_AUTHORIZATION_REPLAY"
                if execution_authorization_artifact_recognized
                else "NOT_AVAILABLE"
            )
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
        "governance_authorization_reached": governance_authorization_reached,
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
