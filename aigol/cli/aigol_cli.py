"""Canonical deterministic AiGOL governance CLI foundation."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
import select
import sys
import time
from pathlib import Path
from typing import Any

from aigol.cli.commands.approval import (
    approval_approved_command,
    approval_chain_command,
    approval_list_command,
    approval_pending_command,
    approval_rejected_command,
    approval_show_command,
    render_approval_summary,
)
from aigol.cli.commands.bridge import (
    bridge_approved_command,
    bridge_chain_command,
    bridge_execution_request_command,
    bridge_list_command,
    bridge_pending_command,
    bridge_rejected_command,
    bridge_show_command,
    render_bridge_summary,
)
from aigol.cli.commands.chain_inspection import (
    render_chain_inspection_summary,
    show_chain_command,
    show_chain_summary_command,
    show_execution_lifecycle_command,
    show_full_lineage_command,
    show_latest_chain_command,
    show_learning_lifecycle_command,
)
from aigol.cli.commands.cognition import (
    check_semantic_replay_continuity,
    inspect_authority,
    inspect_cognition,
    inspect_integrity,
    inspect_lifecycle,
    inspect_registry,
    inspect_semantic_boundary_propagation,
    inspect_semantic_context_audit_bundle,
    inspect_semantic_context_diff,
    inspect_semantic_context_state,
    inspect_semantic_relationship_index,
    inspect_topology,
)
from aigol.cli.commands.continuity import continuity_preview_summary
from aigol.cli.commands.dashboard import (
    dashboard_approvals_command,
    dashboard_bridges_command,
    dashboard_chains_command,
    dashboard_command,
    dashboard_execution_command,
    dashboard_learning_command,
    dashboard_summary_command,
    render_dashboard_summary,
)
from aigol.cli.commands.diagnostics import runtime_diagnostics
from aigol.cli.commands.dispatch import authorize_dispatch
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.governance import validate_governance_continuity
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cli.commands.implementation_epoch import (
    render_implementation_epoch_summary,
    run_implementation_generation_epoch,
)
from aigol.runtime.first_real_implementation_generation_epoch_runtime import (
    render_first_real_implementation_generation_epoch,
    run_first_real_implementation_generation_epoch,
)
from aigol.runtime.multi_provider_competitive_proposal_runtime import (
    render_multi_provider_competitive_review,
    run_multi_provider_competitive_proposal_runtime,
)
from aigol.runtime.native_provider_execution_runtime import (
    DEFAULT_OPENAI_MODEL,
    render_native_provider_execution_summary,
    run_native_provider_execution,
)
from aigol.runtime.provider_governance_runtime import (
    query_cognition_participation,
    query_provider_costs,
    query_provider_credentials,
    query_provider_failures,
    query_provider_status,
    query_provider_usage,
    render_provider_governance_query,
)
from aigol.runtime.provider_credential_vault import (
    DEFAULT_VAULT_PATH,
    add_provider_credential,
    delete_provider_credential,
    disable_provider_credential,
    provider_credential_diagnostic,
    provider_credential_history,
    retrieve_provider_credential,
    rotate_provider_credential,
    verify_provider_credential,
)
from aigol.cli.commands.moc import (
    append_ledger_command,
    approval_gate_command,
    correction_feedback_command,
    dispatch_authorize_command,
    dispatch_preview_command,
    dispatch_request_command,
    generate_contract_command,
    interpret_return_command,
    operational_lineage_command,
    persist_proposal_command,
    prepare_worker_command,
    provider_execution_gate_command,
    runtime_dispatch_command,
    validate_contract_command,
    validate_proposal_command,
)
from aigol.cli.commands.plan import (
    plan_approved_command,
    plan_bridge_command,
    plan_chain_command,
    plan_execution_request_command,
    plan_latest_command,
    plan_list_command,
    plan_show_command,
    render_plan_summary,
)
from aigol.cli.commands.replay import explain_operator_operation, ledger_summary, operator_operation_report, verify_replay
from aigol.cli.commands.return_flow import inspect_return
from aigol.cli.commands.run_governed import run_governed_operation_command, summarize_governed_operation_replay
from aigol.cli.commands.status import status_summary
from aigol.cognition.authority_propagation import render_authority_propagation_summary
from aigol.cognition.integrity_summary import render_cognition_integrity_summary
from aigol.cognition.lifecycle_model import render_cognition_lifecycle_summary
from aigol.cognition.registry import render_cognition_registry_summary
from aigol.cognition.semantic_boundary_propagation import render_semantic_boundary_summary
from aigol.cognition.semantic_context_audit_bundle import render_semantic_audit_bundle_summary
from aigol.cognition.semantic_context_diff import render_semantic_diff_summary
from aigol.cognition.semantic_context_state import render_semantic_context_summary
from aigol.cognition.semantic_relationship_index import render_semantic_relationship_summary
from aigol.cognition.semantic_replay import render_semantic_replay_report
from aigol.cognition.state_envelope import render_cognition_summary
from aigol.cognition.topology_report import render_cognition_topology_summary
from aigol.cli.render.status_renderer import render_status
from aigol.cli.render.terminal_cards import render_card
from aigol.moc.approval_gate import render_approval_gate_summary
from aigol.moc.advisory_contract_generation import render_advisory_contract_generation_summary
from aigol.moc.advisory_proposal_validation import render_advisory_proposal_validation_summary
from aigol.moc.contract_validation import render_contract_validation_summary
from aigol.moc.dispatch_authorization import render_worker_dispatch_authorization_summary
from aigol.moc.dispatch_authorization_preview import render_dispatch_authorization_preview_summary
from aigol.moc.dispatch_request import render_worker_dispatch_request_summary
from aigol.moc.governed_return_interpretation import render_governed_return_interpretation_summary
from aigol.moc.operational_lineage import render_operational_lineage_summary
from aigol.moc.proposal_correction_loop import render_proposal_correction_feedback_summary
from aigol.moc.provider_execution_gate import render_provider_execution_gate_summary
from aigol.moc.proposal_ledger import DEFAULT_LEDGER_PATH, render_proposal_ledger_summary
from aigol.moc.proposal_persistence import render_proposal_persistence_summary
from aigol.moc.runtime_dispatch import render_runtime_dispatch_summary
from aigol.moc.worker_preparation import render_worker_preparation_summary
from aigol.runtime.prompt_to_conversation_integration import submit_prompt_to_conversation
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.clarification_continuity_runtime import (
    detect_active_clarification,
    render_clarification_continuity_summary,
    run_clarification_continuity,
    should_bind_operator_reply_to_active_clarification,
)
from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    WORKER_BINDING_APPROVED as CLARIFIED_DOMAIN_WORKER_BINDING_APPROVED,
    render_clarified_domain_intent_handoff_review_summary,
    review_clarified_domain_intent,
)
from aigol.runtime.domain_handoff_review_approval_binding_runtime import (
    bind_domain_handoff_review_approval,
    detect_domain_approval_entry_intent,
    find_latest_domain_handoff_review,
    render_domain_handoff_review_approval_binding_summary,
)
from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    bridge_domain_approval_entry_to_execution_ready,
    detect_domain_execution_ready_entry_intent,
    find_latest_domain_approval_binding,
    render_domain_execution_ready_bridge_summary,
)
from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED as DOMAIN_PROPOSAL_APPROVED,
    REJECTED as DOMAIN_PROPOSAL_REJECTED,
    create_domain_proposal,
    review_domain_proposal,
)
from aigol.runtime.conversational_cli_runtime import (
    AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE as CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
    AI_DECISION_VALIDATOR_CAPABILITY_MODEL as CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
    AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION as CONVERSATIONAL_AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
    AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW as CONVERSATIONAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
    CAPABILITY_LIFECYCLE_GOVERNANCE as CONVERSATIONAL_CAPABILITY_LIFECYCLE_GOVERNANCE,
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION as CONVERSATIONAL_CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    CREATE_DOMAIN_MARKETING as CONVERSATIONAL_CREATE_DOMAIN_MARKETING,
    CREATE_DOMAIN_TRADING as CONVERSATIONAL_CREATE_DOMAIN_TRADING,
    DOMAIN_ADAPTATION_REFERENCE as CONVERSATIONAL_DOMAIN_ADAPTATION_REFERENCE,
    DOMAIN_EXECUTION_AUTHORIZATION as CONVERSATIONAL_DOMAIN_EXECUTION_AUTHORIZATION,
    DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE as CONVERSATIONAL_DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
    DOMAIN_LIFECYCLE_GOVERNANCE as CONVERSATIONAL_DOMAIN_LIFECYCLE_GOVERNANCE,
    DOMAIN_WORKER_ASSIGNMENT as CONVERSATIONAL_DOMAIN_WORKER_ASSIGNMENT,
    DOMAIN_WORKER_DISPATCH as CONVERSATIONAL_DOMAIN_WORKER_DISPATCH,
    DOMAIN_WORKER_EXECUTION as CONVERSATIONAL_DOMAIN_WORKER_EXECUTION,
    DOMAIN_GOVERNED_TERMINATION as CONVERSATIONAL_DOMAIN_GOVERNED_TERMINATION,
    DOMAIN_WORKER_INVOCATION as CONVERSATIONAL_DOMAIN_WORKER_INVOCATION,
    DOMAIN_POST_EXECUTION_REPLAY_REVIEW as CONVERSATIONAL_DOMAIN_POST_EXECUTION_REPLAY_REVIEW,
    DOMAIN_WORKER_RESULT_CAPTURE as CONVERSATIONAL_DOMAIN_WORKER_RESULT_CAPTURE,
    DOMAIN_WORKER_RESULT_VALIDATION as CONVERSATIONAL_DOMAIN_WORKER_RESULT_VALIDATION,
    DOMAIN_WORKER_REQUEST as CONVERSATIONAL_DOMAIN_WORKER_REQUEST,
    DEFAULT_PROVIDER_ASSISTED_CONVERSATION as CONVERSATIONAL_DEFAULT_PROVIDER_ASSISTED_CONVERSATION,
    FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH as CONVERSATIONAL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
    GOVERNED_DEVELOPMENT_WORKFLOW as CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW,
    IMPROVE_PROVIDER_LAYER as CONVERSATIONAL_IMPROVE_PROVIDER_LAYER,
    IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST as CONVERSATIONAL_IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
    IMPROVEMENT_PROPOSAL_RUNTIME as CONVERSATIONAL_IMPROVEMENT_PROPOSAL_RUNTIME,
    HUMAN_INTENT_CLARIFICATION_INTAKE as CONVERSATIONAL_HUMAN_INTENT_CLARIFICATION_INTAKE,
    NATIVE_DEVELOPMENT_INTENT_ROUTING as CONVERSATIONAL_NATIVE_DEVELOPMENT_INTENT_ROUTING,
    NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION as CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
    OCS_LLM_COGNITION as CONVERSATIONAL_OCS_LLM_COGNITION,
    OPERATOR_DECISION_SUPPORT as CONVERSATIONAL_OPERATOR_DECISION_SUPPORT,
    PROPOSAL_RUNTIME as CONVERSATIONAL_PROPOSAL_RUNTIME,
    REVIEW_LATEST_AUDIT as CONVERSATIONAL_REVIEW_LATEST_AUDIT,
    SHOW_DASHBOARD as CONVERSATIONAL_SHOW_DASHBOARD,
    SHOW_LATEST_REPLAY_CHAIN as CONVERSATIONAL_SHOW_LATEST_REPLAY_CHAIN,
    SHOW_STATUS as CONVERSATIONAL_SHOW_STATUS,
    is_ocs_llm_cognition_prompt,
    render_conversational_cli_routing_summary,
    route_conversational_cli_intent,
)
from aigol.runtime.conversation_native_development_intent_routing import (
    NATIVE_DEVELOPMENT_INTENT_ROUTED,
    is_conversation_native_development_intent,
    render_native_development_intent_routing_summary,
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.native_development_task_intake_runtime import is_plain_native_development_prompt
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    render_conversation_to_ppp_handoff_execution_summary,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.context_assembled_to_ppp_routing_continuation import (
    POST_CONTEXT_CONTINUATION_REACHED_PPP,
    continue_context_assembled_to_ppp_routing,
)
from aigol.runtime.post_entry_continuation_gate_runtime import (
    CLARIFICATION_REQUIRED as POST_ENTRY_CLARIFICATION_REQUIRED,
    CONTINUATION_ALLOWED as POST_ENTRY_CONTINUATION_ALLOWED,
    evaluate_post_entry_continuation_gate,
)
from aigol.runtime.ocs_end_to_end_runtime import run_ocs_end_to_end
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import continue_ocs_to_ppp_routing
from aigol.runtime.implementation_handoff_visibility import (
    create_implementation_handoff_visibility_summary,
    render_implementation_handoff_visibility_summary,
)
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    render_implementation_approval_resume_summary,
    resume_implementation_after_approval,
)
from aigol.runtime.human_decision_runtime import (
    APPROVE,
    REJECT,
    REQUEST_MODIFICATION,
    normalize_human_decision,
    record_human_decision,
    render_human_decision_summary,
)
from aigol.runtime.human_intent_clarification_continuity_runtime import (
    continue_human_intent_clarification_to_workflow,
    render_human_intent_clarification_continuity_summary,
)
from aigol.runtime.governed_implementation_dry_run import (
    prepare_governed_implementation_dry_run,
    render_governed_implementation_dry_run_summary,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.execution_authorization_runtime import (
    authorize_execution_ready,
    detect_domain_execution_authorization_entry_intent,
    find_latest_domain_execution_ready_bridge,
    render_execution_authorization_summary,
)
from aigol.runtime.execution_runtime import (
    detect_domain_worker_execution_entry_intent,
    find_latest_domain_worker_invocation_for_execution,
    start_execution as _record_execution_start,
)
from aigol.runtime.worker_invocation_request_runtime import (
    create_worker_invocation_request,
    detect_domain_worker_request_entry_intent,
    find_latest_domain_execution_authorization,
    render_worker_invocation_request_summary,
)
from aigol.runtime.worker_assignment_runtime import (
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    detect_domain_worker_assignment_entry_intent,
    find_latest_domain_worker_invocation_request,
    render_worker_assignment_summary,
)
from aigol.runtime.worker_dispatch_runtime import (
    detect_domain_worker_dispatch_entry_intent,
    dispatch_assigned_worker,
    find_latest_domain_worker_assignment,
    render_worker_dispatch_summary,
)
from aigol.runtime.worker_invocation_runtime import (
    detect_domain_worker_invocation_entry_intent,
    find_latest_domain_worker_dispatch,
    invoke_dispatched_worker,
    render_worker_invocation_summary,
)
from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import (
    APPROVAL_SCOPE as WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_APPROVAL_SCOPE,
    bridge_worker_invocation_to_execution_candidate,
)
from aigol.runtime.external_worker_adapter_runtime import (
    accept_external_worker_result_package,
    create_external_worker_task_package,
)
from aigol.runtime.openai_external_worker_provider_adapter import run_openai_external_worker_provider_adapter
from aigol.runtime.result_validation_runtime import validate_governed_execution_result
from aigol.runtime.replay_certification_runtime import certify_validated_replay
from aigol.runtime.worker_result_capture_runtime import (
    capture_worker_result,
    detect_domain_worker_result_capture_entry_intent,
    default_worker_output_for_invocation,
    find_latest_domain_execution_for_result_capture,
    render_worker_result_capture_summary,
)
from aigol.runtime.worker_result_validation_runtime import (
    detect_domain_worker_result_validation_entry_intent,
    find_latest_domain_result_capture_for_validation,
    render_worker_result_validation_summary,
    validate_worker_result,
)
from aigol.runtime.domain_bundle_registry_runtime import default_domain_bundle_registry
from aigol.runtime.executable_domain_bundle_runtime import (
    render_executable_domain_bundle_summary,
)
from aigol.runtime.generic_domain_factory_runtime import create_generic_executable_domain_bundle
from aigol.runtime.post_execution_replay_review_runtime import (
    detect_domain_post_execution_replay_review_entry_intent,
    find_latest_domain_result_validation_for_replay_review,
    render_post_execution_replay_review_summary,
    review_validated_worker_result,
)
from aigol.runtime.governed_termination_runtime import (
    detect_domain_governed_termination_entry_intent,
    find_latest_domain_replay_review_for_termination,
    render_governed_termination_summary,
    terminate_reviewed_operation,
)
from aigol.runtime.conversation_provider_unavailable_clarification_fallback import (
    HUMAN_CLARIFICATION_REQUIRED as PROVIDER_UNAVAILABLE_HUMAN_CLARIFICATION_REQUIRED,
    render_provider_unavailable_clarification_fallback,
    run_conversation_provider_unavailable_clarification_fallback,
)
from aigol.runtime.native_development_task_intake_runtime import (
    is_native_development_prompt,
)
from aigol.runtime.runtime_progress_visibility import (
    format_runtime_progress,
    format_runtime_status,
    load_runtime_progress,
    watch_runtime_progress,
)
from aigol.runtime.conversation_native_development_context_integration import (
    FAILED_CLOSED as NATIVE_DEVELOPMENT_CONTEXT_FAILED_CLOSED,
    reconstruct_conversation_native_development_context_integration_replay,
    render_conversation_native_development_context_summary,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.conversation_chain_continuity_runtime import reconstruct_conversation_chain_continuity_replay
from aigol.runtime.source_of_truth_router_runtime import route_source_of_truth
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unknown_domain_clarification_runtime import (
    CLARIFICATION_REQUIRED as UNKNOWN_DOMAIN_CLARIFICATION_REQUIRED,
    is_unknown_domain_clarification_eligible,
    render_unknown_domain_clarification_workflow,
    run_unknown_domain_clarification_workflow,
)
from aigol.runtime.semantic_similarity_domain_reference_runtime import (
    is_domain_reference_adaptation_prompt,
    render_domain_reference_resolution_summary,
    run_semantic_similarity_domain_reference_resolution,
)
from aigol.runtime.operator_decision_support_runtime import (
    is_operator_decision_support_prompt,
    render_operator_decision_support_summary,
    run_operator_decision_support,
)
from aigol.runtime.recommendation_approval_followup_runtime import (
    APPROVE as RECOMMENDATION_APPROVE,
    IGNORE as RECOMMENDATION_IGNORE,
    REJECT as RECOMMENDATION_REJECT,
    create_recommendation_continuity,
    create_recommendation_followup,
    is_recommendation_approval_prompt,
    is_recommendation_followup_prompt,
    is_recommendation_ignore_prompt,
    is_recommendation_rejection_prompt,
    record_recommendation_approval,
    render_recommendation_approval_summary,
    render_recommendation_continuity_summary,
    render_recommendation_followup_summary,
)
from aigol.runtime.conversational_progress_binding_runtime import (
    CLARIFICATION as CONVERSATIONAL_PROGRESS_CLARIFICATION,
    COGNITION as CONVERSATIONAL_PROGRESS_COGNITION,
    COMPARISON as CONVERSATIONAL_PROGRESS_COMPARISON,
    COMPLETED as CONVERSATIONAL_PROGRESS_COMPLETED,
    CONTINUITY as CONVERSATIONAL_PROGRESS_CONTINUITY,
    FAILED_CLOSED as CONVERSATIONAL_PROGRESS_FAILED_CLOSED,
    PROVIDER_INVOCATION as CONVERSATIONAL_PROGRESS_PROVIDER_INVOCATION,
    REPLAY as CONVERSATIONAL_PROGRESS_REPLAY,
    RESULT_ASSEMBLY as CONVERSATIONAL_PROGRESS_RESULT_ASSEMBLY,
    ROUTING as CONVERSATIONAL_PROGRESS_ROUTING,
    create_conversational_progress_binding,
    record_conversational_progress_checkpoint,
)
from aigol.runtime.conversational_turn_completion_runtime import (
    STATUS_COMPLETED as TURN_COMPLETION_COMPLETED,
    STATUS_FAILED_CLOSED as TURN_COMPLETION_FAILED_CLOSED,
    record_conversational_result_delivered,
    record_conversational_turn_completed,
)
from aigol.runtime.conversational_routing_visibility_runtime import (
    HIGH as ROUTING_VISIBILITY_HIGH,
    LOW as ROUTING_VISIBILITY_LOW,
    MEDIUM as ROUTING_VISIBILITY_MEDIUM,
    NO_CERTIFIED_WORKFLOW_MATCHED,
    ROUTING_FAILED_CLOSED,
    ROUTING_SELECTED,
    record_conversational_routing_visibility,
)
from aigol.runtime.universal_intake_layer_runtime import (
    record_universal_intake,
)
from aigol.runtime.multiline_prompt_support_runtime import (
    record_multiline_prompt_capture,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.provider_runtime import run_provider_attachment
from aigol.provider.providers.openai_provider import (
    DEFAULT_OPENAI_MODEL as OPENAI_PROVIDER_DEFAULT_MODEL,
    MAX_OPENAI_RESPONSE_CHARS,
    OPENAI_PROVIDER_ID,
    OpenAIProviderAdapter,
    openai_provider_metadata,
)
from aigol.runtime.llm_cognition_provider_runtime import create_default_openai_cognition_provider_contract
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    STATUS_COMPLETED as OCS_LLM_COGNITION_COMPLETED,
    render_operator_visible_ocs_llm_cognition,
    render_ocs_llm_cognition_end_to_end_summary,
    run_ocs_llm_cognition_end_to_end,
)
from aigol.runtime.acli_governed_development_execution_bridge import (
    ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1,
    ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1,
    APPROVAL_REQUIRED as ACLI_GOVERNED_DEVELOPMENT_APPROVAL_REQUIRED,
    EXECUTION_COMPLETED as ACLI_GOVERNED_DEVELOPMENT_EXECUTION_COMPLETED,
    MODIFICATION_REQUESTED as ACLI_GOVERNED_DEVELOPMENT_MODIFICATION_REQUESTED,
    approve_and_execute_acli_governed_development,
    propose_acli_governed_development_execution,
    render_acli_governed_development_bridge_summary,
)
from aigol.runtime.acli_human_friendly_explanation_runtime import (
    create_acli_human_friendly_explanation,
    render_acli_human_friendly_explanation,
)
from aigol.runtime.acli_llm_assisted_explanation_runtime import (
    authoritative_state_from_acli_proposal_capture,
    create_acli_llm_assisted_explanation,
    render_acli_llm_assisted_explanation,
)
from aigol.runtime.acli_hardening_integration_runtime import (
    record_completed_acli_interaction_hardening,
)


INTERACTIVE_CONVERSATION_CLI_VERSION = "INTERACTIVE_CONVERSATION_CLI_V1"
CONVERSATIONAL_OPENAI_OUTPUT_BUDGET_RUNTIME_VERSION = "AIGOL_CONVERSATIONAL_OPENAI_OUTPUT_BUDGET_RUNTIME_V1"
OPENAI_OUTPUT_BUDGET_ARTIFACT_V1 = "OPENAI_OUTPUT_BUDGET_ARTIFACT_V1"
DEFAULT_PROVIDER = "OPENAI"
CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS = 1200
CONVERSATIONAL_OCS_OPENAI_CHARS_PER_TOKEN_ESTIMATE = 5
CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET = (
    CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS * CONVERSATIONAL_OCS_OPENAI_CHARS_PER_TOKEN_ESTIMATE
)
INTERACTIVE_EXIT_COMMANDS = frozenset({"exit", "quit"})
MULTILINE_PROMPT_TERMINATOR = "."
INTERACTIVE_CONVERSATION_MULTILINE_BANNER = "\n".join(
    [
        "Multi-line mode enabled.",
        "Finish prompt with a single '.' on its own line.",
    ]
)
_CONVERSATIONAL_DEVELOPMENT_ENTRYPOINT_SELECTION_WORKFLOWS = frozenset(
    {
        CONVERSATIONAL_DOMAIN_LIFECYCLE_GOVERNANCE,
        CONVERSATIONAL_CAPABILITY_LIFECYCLE_GOVERNANCE,
        CONVERSATIONAL_PROPOSAL_RUNTIME,
        CONVERSATIONAL_IMPROVEMENT_PROPOSAL_RUNTIME,
        CONVERSATIONAL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
        CONVERSATIONAL_IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
        CONVERSATIONAL_AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
        CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
        CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
    }
)


def _bind_supported_executable_domain_bundle(
    *,
    prompt_id: str,
    validation_capture: dict[str, Any],
    workspace_root: str | Path,
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any] | None:
    validation = validation_capture["worker_result_validation_artifact"]
    produced_outputs = set(validation.get("produced_outputs", []))
    registry_entry = None
    for entry in default_domain_bundle_registry()["entries"]:
        if produced_outputs == set(entry["artifact_paths"]):
            registry_entry = entry
            break
    if registry_entry is None:
        return None
    return create_generic_executable_domain_bundle(
        generic_domain_factory_runtime_id=f"{prompt_id}:GENERIC-DOMAIN-FACTORY",
        domain_id=registry_entry["domain_id"],
        worker_result_validation_artifact=validation,
        worker_result_validation_replay_reference=validation_capture["worker_result_validation_replay_reference"],
        workspace_root=workspace_root,
        created_by="AIGOL_GOVERNANCE",
        created_at=created_at,
        replay_dir=replay_dir,
    )


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _replay_visible_context_source(
    *,
    artifact_id: str,
    artifact_type: str,
    summary: str,
    created_at: str,
    **extra: Any,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "summary": summary,
        "created_at": created_at,
        "replay_visible": True,
        "authority": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact.update(extra)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_ocs_cognition_source_context(
    *,
    prompt_id: str,
    human_prompt: str,
    router_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    source_artifact = router_capture.get("source_of_truth_router_artifact") or {}
    execution_hint = _conversation_ocs_execution_context_hint(
        prompt_id=prompt_id,
        human_prompt=human_prompt,
        created_at=created_at,
    )
    ppp_context = [execution_hint] if execution_hint else []
    registry_context = []
    if execution_hint:
        registry_context.append(execution_hint)
    return {
        "conversation_context": [
            _replay_visible_context_source(
                artifact_id=f"{prompt_id}:HUMAN-COGNITION-REQUEST",
                artifact_type="HUMAN_COGNITION_REQUEST_ARTIFACT_V1",
                summary=human_prompt,
                created_at=created_at,
                prompt_id=prompt_id,
                human_prompt_hash=replay_hash(human_prompt),
            )
        ],
        "replay_visible_operation_context": [
            _replay_visible_context_source(
                artifact_id=f"{prompt_id}:SOURCE-ROUTER-CONTEXT",
                artifact_type="CONVERSATIONAL_SOURCE_ROUTER_CONTEXT_V1",
                summary=source_artifact.get("selection_reason")
                or "Source router context for conversational OCS cognition.",
                created_at=created_at,
                selected_source=source_artifact.get("selected_source"),
                source_router_hash=source_artifact.get("artifact_hash"),
            ),
            _replay_visible_context_source(
                artifact_id=f"{prompt_id}:OCS-COGNITION-BINDING-CONTEXT",
                artifact_type="CONVERSATIONAL_OCS_COGNITION_BINDING_CONTEXT_V1",
                summary="Broad conversational cognition prompt routed to certified OCS LLM cognition end-to-end.",
                created_at=created_at,
                binding_milestone="AIGOL_CONVERSATIONAL_OCS_COGNITION_BINDING_V1",
                target_runtime="AIGOL_OCS_LLM_COGNITION_END_TO_END_V1",
            ),
        ],
        "ppp_context": ppp_context,
        "registry_context": registry_context,
    }


def _conversation_ocs_execution_context_hint(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
) -> dict[str, Any] | None:
    normalized_prompt = str(human_prompt or "").upper()
    if "TRADING" in normalized_prompt and "MARKET_EVIDENCE" in normalized_prompt:
        return _replay_visible_context_source(
            artifact_id=f"{prompt_id}:OCS-EXECUTION-HINT-TRADING-MARKET_EVIDENCE_NORMALIZATION",
            artifact_type="OCS_EXECUTION_REQUIRED_CONTEXT_HINT_V1",
            summary={
                "domain_id": "TRADING",
                "worker_family_id": "MARKET_EVIDENCE_NORMALIZATION",
                "provider_necessity_classification": "PROVIDER_REQUIRED",
            },
            created_at=created_at,
            domain_id="TRADING",
            worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        )
    if "AIGOL" in normalized_prompt and "CLAUDE_EXTERNAL" in normalized_prompt:
        return _replay_visible_context_source(
            artifact_id=f"{prompt_id}:OCS-EXECUTION-HINT-AIGOL-CLAUDE_EXTERNAL",
            artifact_type="OCS_EXECUTION_REQUIRED_CONTEXT_HINT_V1",
            summary={
                "domain_id": "AIGOL",
                "worker_family_id": "CLAUDE_EXTERNAL",
                "provider_necessity_classification": "PROVIDER_REQUIRED",
            },
            created_at=created_at,
            domain_id="AIGOL",
            worker_family_id="CLAUDE_EXTERNAL",
        )
    return None


def _conversation_ocs_cognition_provider_contracts(created_at: str) -> list[dict[str, Any]]:
    return [
        _conversation_openai_cognition_provider_contract(
            provider_id=OPENAI_PROVIDER_ID,
            provider_label="OpenAI Responses Provider",
            created_at=created_at,
        ),
        _conversation_openai_cognition_provider_contract(
            provider_id="openai-comparison",
            provider_label="OpenAI Comparison Responses Provider",
            created_at=created_at,
        ),
    ]


def _conversation_openai_cognition_provider_contract(
    *, provider_id: str, provider_label: str, created_at: str
) -> dict[str, Any]:
    artifact = create_default_openai_cognition_provider_contract(created_at=created_at)
    artifact["provider_id"] = provider_id
    artifact["provider_identity"]["provider_id"] = provider_id
    artifact["provider_identity"]["provider_label"] = provider_label
    artifact["single_provider_only"] = False
    artifact["multi_provider_cognition_scope"] = True
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_openai_provider_adapter() -> OpenAIProviderAdapter:
    return OpenAIProviderAdapter(max_output_tokens=CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS)


def _conversation_openai_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata())
    return registry


def _post_context_continuation_provider_registry() -> ProviderRegistry:
    return _conversation_openai_provider_registry()


def _post_context_continuation_provider_adapter() -> OpenAIProviderAdapter:
    return OpenAIProviderAdapter()


def _post_context_continuation_should_run(
    *,
    native_context_capture: dict[str, Any],
    auto_continue_enabled: bool,
    human_prompt: str,
) -> bool:
    if native_context_capture.get("fail_closed") is True:
        return False
    if native_context_capture.get("context_status") != "CONTEXT_ASSEMBLED":
        return False
    provider_necessity = str(native_context_capture.get("provider_necessity_classification") or "")
    if "PROVIDER_REQUIRED" not in provider_necessity:
        return False
    if auto_continue_enabled:
        return True
    normalized_prompt = " ".join(human_prompt.lower().split())
    return normalized_prompt == "continue" or ("continue" in normalized_prompt and "ppp" in normalized_prompt)


def _post_entry_continuation_clarification_matches(human_prompt: str) -> bool:
    normalized_prompt = " ".join(human_prompt.lower().split())
    return normalized_prompt == "continue" or ("continue" in normalized_prompt and "ppp" in normalized_prompt)


def _post_context_continuation_output(capture: dict[str, Any]) -> str:
    return "\n".join(
        [
            "",
            "Post-Context Continuation",
            "",
            f"continuation_status: {capture.get('continuation_status')}",
            f"ppp_route_status: {capture.get('ppp_route_status')}",
            f"domain_reference: {capture.get('domain_reference')}",
            f"worker_reference: {capture.get('worker_reference')}",
            f"implementation_handoff_reference: {capture.get('implementation_handoff_reference')}",
            f"replay_reference: {capture.get('post_context_continuation_replay_reference')}",
        ]
    )


def _worker_lifecycle_continuation_output(capture: dict[str, Any]) -> str:
    lifecycle = capture.get("worker_lifecycle_continuation")
    if not isinstance(lifecycle, dict):
        lifecycle = {}
    return "\n".join(
        [
            "",
            "Certified Worker Lifecycle Continuation",
            "",
            f"worker_request_reached: {str(capture.get('worker_request_reached') is True).lower()}",
            f"worker_assignment_reached: {str(lifecycle.get('worker_assignment_reached') is True).lower()}",
            f"worker_dispatch_reached: {str(lifecycle.get('worker_dispatch_reached') is True).lower()}",
            f"worker_invocation_reached: {str(lifecycle.get('worker_invocation_reached') is True).lower()}",
            f"execution_candidate_reached: {str(lifecycle.get('worker_execution_candidate_reached') is True).lower()}",
            f"external_task_package_reached: {str(lifecycle.get('external_task_package_reached') is True).lower()}",
            f"openai_provider_reached: {str(lifecycle.get('openai_provider_reached') is True).lower()}",
            f"result_validation_reached: {str(lifecycle.get('result_validation_reached') is True).lower()}",
            f"replay_certification_reached: {str(lifecycle.get('replay_certification_reached') is True).lower()}",
        ]
    )


def _explicit_ocs_execution_required(human_prompt: str) -> bool:
    normalized_prompt = " ".join(str(human_prompt or "").lower().split())
    execution_markers = (
        "enter governed execution",
        "continue to ppp",
        "continue into ppp",
        "execution required",
        "requires execution",
        "implement ",
    )
    return any(marker in normalized_prompt for marker in execution_markers)


def _external_worker_openai_client() -> Any:
    return None


def _scoped_invocation_bridge_approval(
    *,
    approval_id: str,
    invocation_artifact: dict[str, Any],
    approved_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": approval_id,
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_worker_invocation": invocation_artifact["worker_invocation_id"],
        "source_worker_invocation_hash": invocation_artifact["artifact_hash"],
        "approval_scope": WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_APPROVAL_SCOPE,
        "worker_execution_allowed": False,
        "provider_invocation_allowed": False,
        "implementation_result_creation_allowed": False,
        "approved_by": "AIGOL_CANONICAL_EXECUTION_AUTHORIZATION",
        "approved_at": approved_at,
        "authorization_boundary": "EXECUTION_AUTHORIZATION_ARTIFACT_V1_REQUIRED_UPSTREAM",
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _scoped_external_worker_task_approval(
    *,
    approval_id: str,
    execution_candidate_artifact: dict[str, Any],
    approved_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": approval_id,
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_execution_candidate": execution_candidate_artifact["execution_candidate_id"],
        "source_execution_candidate_hash": execution_candidate_artifact["artifact_hash"],
        "approval_scope": "CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY",
        "external_worker_task_allowed": True,
        "implementation_result_creation_allowed": False,
        "approved_by": "AIGOL_CANONICAL_EXECUTION_AUTHORIZATION",
        "approved_at": approved_at,
        "authorization_boundary": "EXECUTION_AUTHORIZATION_ARTIFACT_V1_REQUIRED_UPSTREAM",
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _external_worker_capability_declaration() -> dict[str, Any]:
    return {
        "worker_interface": "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1",
        "worker_family": "REAL_PROVIDER_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _continue_worker_request_to_replay_certification(
    *,
    prompt_id: str,
    worker_request_capture: dict[str, Any],
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    request_artifact = worker_request_capture.get("worker_invocation_request_artifact")
    request_replay_reference = worker_request_capture.get("worker_invocation_request_replay_reference")
    if not isinstance(request_artifact, dict):
        raise FailClosedRuntimeError("ACLI worker continuation failed closed: worker request artifact missing")
    if not isinstance(request_replay_reference, str) or not request_replay_reference:
        raise FailClosedRuntimeError("ACLI worker continuation failed closed: worker request replay missing")

    assignment_capture = assign_worker_from_invocation_request(
        worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
        worker_invocation_request_artifact=request_artifact,
        worker_invocation_request_replay_reference=request_replay_reference,
        worker_registry_artifacts=default_worker_registry_for_request(request_artifact, created_at=created_at),
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=created_at,
        replay_dir=replay_dir / "worker_assignment",
    )
    if assignment_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(assignment_capture.get("failure_reason") or "worker assignment failed")

    dispatch_capture = dispatch_assigned_worker(
        worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment_capture["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=created_at,
        replay_dir=replay_dir / "worker_dispatch",
    )
    if dispatch_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(dispatch_capture.get("failure_reason") or "worker dispatch failed")

    invocation_capture = invoke_dispatched_worker(
        worker_invocation_id=f"{prompt_id}:WORKER-INVOCATION",
        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch_capture["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=created_at,
        replay_dir=replay_dir / "worker_invocation",
    )
    if invocation_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(invocation_capture.get("failure_reason") or "worker invocation failed")

    invocation_artifact = invocation_capture["worker_invocation_artifact"]
    execution_candidate_capture = bridge_worker_invocation_to_execution_candidate(
        candidate_id=f"{prompt_id}:WORKER-EXECUTION-CANDIDATE",
        worker_invocation_artifact=invocation_artifact,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        human_approval_artifact=_scoped_invocation_bridge_approval(
            approval_id=f"{prompt_id}:WORKER-EXECUTION-CANDIDATE-APPROVAL",
            invocation_artifact=invocation_artifact,
            approved_at=created_at,
        ),
        requested_by="AIGOL_GOVERNANCE",
        created_at=created_at,
        replay_dir=replay_dir / "worker_execution_candidate",
    )
    if execution_candidate_capture.get("candidate_status") == "FAILED_CLOSED":
        raise FailClosedRuntimeError(
            execution_candidate_capture.get("failure_reason") or "worker execution candidate bridge failed"
        )

    execution_candidate = execution_candidate_capture["worker_execution_candidate_artifact"]
    external_task_capture = create_external_worker_task_package(
        task_id=f"{prompt_id}:EXTERNAL-WORKER-TASK",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_scoped_external_worker_task_approval(
            approval_id=f"{prompt_id}:EXTERNAL-WORKER-TASK-APPROVAL",
            execution_candidate_artifact=execution_candidate,
            approved_at=created_at,
        ),
        requested_by="AIGOL_GOVERNANCE",
        created_at=created_at,
        replay_dir=replay_dir / "external_worker_adapter",
        worker_capability_declaration=_external_worker_capability_declaration(),
    )
    if external_task_capture.get("task_package_generated") is not True:
        raise FailClosedRuntimeError(external_task_capture.get("failure_reason") or "external task package failed")

    openai_client = _external_worker_openai_client()
    openai_worker_capture = run_openai_external_worker_provider_adapter(
        result_id=f"{prompt_id}:OPENAI-EXTERNAL-WORKER-RESULT",
        task_package_artifact=external_task_capture["external_worker_task_package"],
        completed_at=created_at,
        replay_dir=replay_dir / "openai_external_worker_provider",
        openai_client=openai_client,
        api_key="test-openai-key" if openai_client is not None else None,
    )
    if openai_worker_capture.get("openai_provider_connected") is not True:
        raise FailClosedRuntimeError(openai_worker_capture.get("failure_reason") or "OpenAI worker failed")

    external_result_capture = accept_external_worker_result_package(
        result_package=openai_worker_capture["external_worker_result_package"],
        task_package_artifact=external_task_capture["external_worker_task_package"],
        accepted_by="AIGOL_GOVERNANCE",
        accepted_at=created_at,
        replay_dir=replay_dir / "external_worker_adapter",
    )
    if external_result_capture.get("execution_result_artifact_generated") is not True:
        raise FailClosedRuntimeError(external_result_capture.get("failure_reason") or "external result failed")

    result_validation_capture = validate_governed_execution_result(
        validation_id=f"{prompt_id}:RESULT-VALIDATION",
        worker_execution_result_artifact=external_result_capture["worker_execution_result_artifact"],
        validated_by="AIGOL_GOVERNANCE",
        validated_at=created_at,
        replay_dir=replay_dir / "result_validation",
    )
    if result_validation_capture.get("result_validation_completed") is not True:
        raise FailClosedRuntimeError(result_validation_capture.get("failure_reason") or "result validation failed")

    replay_certification_capture = certify_validated_replay(
        certification_id=f"{prompt_id}:REPLAY-CERTIFICATION",
        result_validation_artifact=result_validation_capture["result_validation_artifact"],
        certified_by="AIGOL_GOVERNANCE",
        certified_at=created_at,
        replay_dir=replay_dir / "replay_certification",
    )
    if replay_certification_capture.get("replay_certification_completed") is not True:
        raise FailClosedRuntimeError(
            replay_certification_capture.get("failure_reason") or "replay certification failed"
        )

    return {
        "worker_assignment": assignment_capture,
        "worker_dispatch": dispatch_capture,
        "worker_invocation": invocation_capture,
        "worker_execution_candidate": execution_candidate_capture,
        "external_worker_task_package": external_task_capture,
        "openai_external_worker_provider": openai_worker_capture,
        "external_worker_result": external_result_capture,
        "result_validation": result_validation_capture,
        "replay_certification": replay_certification_capture,
        "worker_assignment_reached": True,
        "worker_dispatch_reached": True,
        "worker_invocation_reached": True,
        "worker_execution_candidate_reached": True,
        "external_task_package_reached": True,
        "openai_provider_reached": True,
        "result_validation_reached": True,
        "replay_certification_reached": True,
        "authorization_boundary_preserved": True,
        "replay_lineage_preserved": all(
            capture.get("replay_lineage_preserved") is True
            for capture in (
                execution_candidate_capture,
                external_task_capture,
                openai_worker_capture,
                external_result_capture,
                result_validation_capture,
                replay_certification_capture,
            )
        ),
        "fail_closed": False,
        "failure_reason": None,
    }


def _continue_ppp_handoff_to_worker_request(
    *,
    prompt_id: str,
    post_context_continuation_capture: dict[str, Any],
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    ppp_capture = post_context_continuation_capture.get("conversation_ppp_routing")
    if not isinstance(ppp_capture, dict):
        raise FailClosedRuntimeError("ACLI continuation failed closed: PPP routing capture missing")
    if ppp_capture.get("route_status") != "CONVERSATION_PPP_HANDOFF_CREATED":
        raise FailClosedRuntimeError("ACLI continuation failed closed: implementation handoff not created")
    if ppp_capture.get("approval_required") is True:
        raise FailClosedRuntimeError("ACLI continuation failed closed: human approval required before worker request")
    ppp_replay_reference = ppp_capture.get("conversation_ppp_routing_replay_reference")
    if not isinstance(ppp_replay_reference, str) or not ppp_replay_reference:
        raise FailClosedRuntimeError("ACLI continuation failed closed: PPP replay reference missing")
    route_artifact = ppp_capture.get("conversation_ppp_routing_artifact")
    if not isinstance(route_artifact, dict):
        raise FailClosedRuntimeError("ACLI continuation failed closed: PPP route artifact missing")
    handoff_replay_reference = str(Path(ppp_replay_reference).parent / "final_implementation_handoff")
    visibility_capture = create_implementation_handoff_visibility_summary(
        visibility_id=f"{prompt_id}:IMPLEMENTATION-HANDOFF-VISIBILITY",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=ppp_capture.get("approval_status") or "APPROVAL_NOT_REQUIRED_FOR_HANDOFF",
        created_at=created_at,
        replay_dir=replay_dir / "implementation_handoff_visibility",
    )
    if visibility_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(visibility_capture.get("failure_reason") or "implementation handoff visibility failed")
    dry_run_capture = prepare_governed_implementation_dry_run(
        dry_run_id=f"{prompt_id}:GOVERNED-IMPLEMENTATION-DRY-RUN",
        handoff_replay_reference=handoff_replay_reference,
        handoff_visibility_artifact=visibility_capture["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=route_artifact,
        created_at=created_at,
        replay_dir=replay_dir / "governed_implementation_dry_run",
    )
    if dry_run_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(dry_run_capture.get("failure_reason") or "governed implementation dry run failed")
    authorization_capture = authorize_execution_ready(
        authorization_id=f"{prompt_id}:EXECUTION-AUTHORIZATION",
        execution_ready_replay_reference=dry_run_capture["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=created_at,
        replay_dir=replay_dir / "execution_authorization",
    )
    if authorization_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(authorization_capture.get("failure_reason") or "execution authorization failed")
    worker_request_capture = create_worker_invocation_request(
        invocation_request_id=f"{prompt_id}:WORKER-INVOCATION-REQUEST",
        execution_authorization_replay_reference=authorization_capture["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        requested_at=created_at,
        replay_dir=replay_dir / "worker_invocation_request",
    )
    if worker_request_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(worker_request_capture.get("failure_reason") or "worker request failed")
    worker_lifecycle_continuation = _continue_worker_request_to_replay_certification(
        prompt_id=prompt_id,
        worker_request_capture=worker_request_capture,
        created_at=created_at,
        replay_dir=replay_dir / "worker_lifecycle_continuation",
    )
    return {
        "implementation_handoff_visibility": visibility_capture,
        "governed_implementation_dry_run": dry_run_capture,
        "execution_authorization": authorization_capture,
        "worker_invocation_request": worker_request_capture,
        "worker_lifecycle_continuation": worker_lifecycle_continuation,
        "worker_request_reached": True,
        "worker_assignment_reached": worker_lifecycle_continuation["worker_assignment_reached"],
        "worker_dispatch_reached": worker_lifecycle_continuation["worker_dispatch_reached"],
        "worker_invocation_reached": worker_lifecycle_continuation["worker_invocation_reached"],
        "worker_execution_candidate_reached": worker_lifecycle_continuation["worker_execution_candidate_reached"],
        "external_task_package_reached": worker_lifecycle_continuation["external_task_package_reached"],
        "openai_provider_reached": worker_lifecycle_continuation["openai_provider_reached"],
        "result_validation_reached": worker_lifecycle_continuation["result_validation_reached"],
        "replay_certification_reached": worker_lifecycle_continuation["replay_certification_reached"],
        "worker_invoked": True,
        "execution_requested": True,
        "dispatch_requested": True,
        "fail_closed": False,
        "failure_reason": None,
    }


def _continue_ocs_cognition_to_ppp(
    *,
    prompt_id: str,
    human_prompt: str,
    router_capture: dict[str, Any],
    current_chain_id: str | None,
    created_at: str,
    replay_dir: Path,
    execution_required: bool,
    session_id: str,
    turn_id: str,
) -> dict[str, Any]:
    ocs_end_to_end_capture = run_ocs_end_to_end(
        ocs_run_id=f"{prompt_id}:OCS-END-TO-END",
        created_at=created_at,
        replay_dir=replay_dir / "ocs_end_to_end",
        source_context=_conversation_ocs_cognition_source_context(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            router_capture=router_capture,
            created_at=created_at,
        ),
        source_chain_id=current_chain_id or prompt_id,
        source_request_reference=prompt_id,
        failure_history=_ocs_execution_required_failure_history(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
        )
        if execution_required
        else None,
        validation_history=_ocs_execution_required_validation_history(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
        )
        if execution_required
        else None,
    )
    if ocs_end_to_end_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(ocs_end_to_end_capture.get("failure_reason") or "OCS end-to-end failed")
    handoff_artifact = _load_ocs_to_ppp_handoff_from_end_to_end_replay(ocs_end_to_end_capture)
    continuation_capture = continue_ocs_to_ppp_routing(
        continuation_id=f"{prompt_id}:OCS-TO-PPP-CONTINUATION",
        ocs_to_ppp_handoff_artifact=handoff_artifact,
        execution_required=execution_required,
        provider_id=OPENAI_PROVIDER_ID,
        created_at=created_at,
        replay_dir=replay_dir / "ocs_to_ppp_continuation",
        registry=_post_context_continuation_provider_registry(),
        adapter=_post_context_continuation_provider_adapter(),
        governance_root="governance",
        prompt_id=prompt_id,
        session_id=session_id,
        turn_id=turn_id,
        current_chain_id=current_chain_id or prompt_id,
        latest_chain_id=current_chain_id or prompt_id,
    )
    if continuation_capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(continuation_capture.get("failure_reason") or "OCS-to-PPP continuation failed")
    return {
        "ocs_end_to_end": ocs_end_to_end_capture,
        "ocs_to_ppp_handoff_artifact": handoff_artifact,
        "ocs_to_ppp_continuation": continuation_capture,
        "execution_required": execution_required,
        "ppp_route_status": continuation_capture.get("ppp_route_status"),
        "ppp_invoked": continuation_capture.get("ppp_invoked") is True,
        "fail_closed": False,
        "failure_reason": None,
    }


def _load_ocs_to_ppp_handoff_from_end_to_end_replay(ocs_end_to_end_capture: dict[str, Any]) -> dict[str, Any]:
    replay_reference = ocs_end_to_end_capture.get("ocs_end_to_end_replay_reference")
    if not isinstance(replay_reference, str) or not replay_reference:
        raise FailClosedRuntimeError("ACLI OCS continuation failed closed: OCS end-to-end replay reference missing")
    wrapper = load_json(Path(replay_reference) / "007_ocs_to_ppp_handoff" / "000_ocs_to_ppp_handoff_recorded.json")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI OCS continuation failed closed: OCS-to-PPP handoff artifact missing")
    return artifact


def _ocs_execution_required_failure_history(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
) -> list[dict[str, Any]]:
    return [
        _replay_visible_context_source(
            artifact_id=f"{prompt_id}:OCS-EXECUTION-FAILURE-{index:06d}",
            artifact_type="OCS_EXECUTION_REQUIRED_FAILURE_EVIDENCE_V1",
            summary=f"Execution-required OCS continuation evidence for: {human_prompt}",
            created_at=created_at,
            failure_reason="missing replay artifact",
        )
        for index in range(2)
    ]


def _ocs_execution_required_validation_history(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
) -> list[dict[str, Any]]:
    return [
        _replay_visible_context_source(
            artifact_id=f"{prompt_id}:OCS-EXECUTION-VALIDATION-{index:06d}",
            artifact_type="OCS_EXECUTION_REQUIRED_VALIDATION_EVIDENCE_V1",
            summary=f"Execution-required OCS validation evidence for: {human_prompt}",
            created_at=created_at,
            validation_status="FAILED",
            error_code="MISSING_HASH",
        )
        for index in range(2)
    ]


def _conversation_ocs_cognition_transports(*, created_at: str, replay_dir: Path) -> dict[str, Any]:
    def _transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        provider_id = str(metadata.get("provider_id") or payload.get("provider_id") or "")
        if provider_id not in {OPENAI_PROVIDER_ID, "openai-comparison"}:
            raise FailClosedRuntimeError("conversational OCS provider is not registered for real OpenAI attachment")
        provider_replay_dir = replay_dir / "real_openai_provider_attachment" / provider_id
        _record_conversational_openai_output_budget(
            provider_id=provider_id,
            model=OPENAI_PROVIDER_DEFAULT_MODEL,
            created_at=created_at,
            replay_dir=provider_replay_dir,
        )
        provider_capture = run_provider_attachment(
            provider_id=OPENAI_PROVIDER_ID,
            request={
                "prompt": payload["input"],
                "human_prompt": payload["input"],
                "provider_metadata": metadata,
                "stream": False,
                "tool_use": False,
                "function_calling": False,
            },
            proposal_id=f"{provider_id}:CONVERSATIONAL-OCS-COGNITION",
            timestamp=created_at,
            registry=_conversation_openai_provider_registry(),
            adapter=_conversation_openai_provider_adapter(),
            replay_dir=provider_replay_dir,
        )
        response = provider_capture["provider_proposal_envelope"]["response"]
        raw_response = response.get("raw_response")
        if not isinstance(raw_response, dict):
            raw_response = {}
        provider_response = {
            "output_text": response["response_text"],
            "model": response.get("model") or OPENAI_PROVIDER_DEFAULT_MODEL,
        }
        if isinstance(raw_response.get("usage"), dict):
            provider_response["usage"] = raw_response["usage"]
        return provider_response

    return {OPENAI_PROVIDER_ID: _transport, "openai-comparison": _transport}


def _record_conversational_openai_output_budget(
    *,
    provider_id: str,
    model: str,
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OPENAI_OUTPUT_BUDGET_ARTIFACT_V1,
        "runtime_version": CONVERSATIONAL_OPENAI_OUTPUT_BUDGET_RUNTIME_VERSION,
        "provider_id": provider_id,
        "model": model,
        "max_output_tokens": CONVERSATIONAL_OCS_OPENAI_MAX_OUTPUT_TOKENS,
        "estimated_char_budget": CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET,
        "max_provider_response_chars": MAX_OPENAI_RESPONSE_CHARS,
        "budget_status": "ACTIVE",
        "budget_deterministic": True,
        "provider_invocation_allowed": CONVERSATIONAL_OCS_OPENAI_ESTIMATED_CHAR_BUDGET <= MAX_OPENAI_RESPONSE_CHARS,
        "fail_closed": True,
        "replay_visible": True,
        "created_at": created_at,
    }
    if not artifact["provider_invocation_allowed"]:
        raise FailClosedRuntimeError("conversational OpenAI output budget exceeds provider response bound")
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "openai_output_budget_recorded",
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / "000_openai_output_budget_recorded.json", wrapper)
    return artifact


def _run_conversational_ocs_llm_cognition(
    *,
    prompt_id: str,
    human_prompt: str,
    router_capture: dict[str, Any],
    current_chain_id: str | None,
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    return run_ocs_llm_cognition_end_to_end(
        end_to_end_id=f"{prompt_id}:OCS-LLM-COGNITION-END-TO-END",
        human_question=human_prompt,
        source_context=_conversation_ocs_cognition_source_context(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            router_capture=router_capture,
            created_at=created_at,
        ),
        provider_contracts=_conversation_ocs_cognition_provider_contracts(created_at),
        transport_registry=_conversation_ocs_cognition_transports(created_at=created_at, replay_dir=replay_dir),
        created_at=created_at,
        replay_dir=replay_dir,
        source_chain_id=current_chain_id or prompt_id,
        source_request_reference=prompt_id,
        single_provider_primary_mode=False,
    )


def _ocs_cognition_provider_ids(ocs_cognition_capture: dict[str, Any]) -> list[str]:
    multi_capture = ocs_cognition_capture.get("stage_captures", {}).get("multi_provider_cognition", {})
    request_bundle = multi_capture.get("request_bundle") or {}
    provider_ids = request_bundle.get("deterministic_provider_order")
    if isinstance(provider_ids, list):
        return [str(provider_id) for provider_id in provider_ids]
    return []


def _real_llm_provider_used_by_ocs(ocs_cognition_capture: dict[str, Any]) -> bool:
    return any(provider_id == OPENAI_PROVIDER_ID or provider_id.startswith("openai-") for provider_id in _ocs_cognition_provider_ids(ocs_cognition_capture))


def _create_interactive_conversation_progress_binding(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    created_at: str,
    turn_root: Path,
) -> dict[str, Any]:
    return create_conversational_progress_binding(
        binding_id=f"{prompt_id}:CONVERSATIONAL-PROGRESS-BINDING",
        session_id=session_id,
        turn_id=turn_id,
        prompt_id=prompt_id,
        workflow_id="INTERACTIVE_CONVERSATION_TURN",
        created_at=created_at,
        replay_dir=turn_root / "conversational_progress",
    )


def _emit_interactive_conversation_progress(
    *,
    binding_capture: dict[str, Any],
    stage: str,
    activity: str,
    snapshot_at: str,
    output_writer: Any,
    runtime_status: str = "RUNNING",
) -> dict[str, Any]:
    capture = record_conversational_progress_checkpoint(
        binding_artifact=binding_capture["conversational_progress_binding_artifact"],
        stage=stage,
        activity=activity,
        snapshot_at=snapshot_at,
        runtime_status=runtime_status,
    )
    output_writer(capture["operator_progress_line"])
    return capture


def _emit_interactive_conversation_cognition_progress(
    *,
    binding_capture: dict[str, Any],
    snapshot_at: str,
    output_writer: Any,
) -> None:
    checkpoints = (
        (CONVERSATIONAL_PROGRESS_COGNITION, "Cognition visibility checkpoint recorded."),
        (CONVERSATIONAL_PROGRESS_PROVIDER_INVOCATION, "Provider invocation boundary checkpoint recorded."),
        (CONVERSATIONAL_PROGRESS_COMPARISON, "Comparison visibility checkpoint recorded."),
        (CONVERSATIONAL_PROGRESS_CONTINUITY, "Continuity visibility checkpoint recorded."),
        (CONVERSATIONAL_PROGRESS_CLARIFICATION, "Clarification visibility checkpoint recorded."),
    )
    for stage, activity in checkpoints:
        _emit_interactive_conversation_progress(
            binding_capture=binding_capture,
            stage=stage,
            activity=activity,
            snapshot_at=snapshot_at,
            output_writer=output_writer,
        )


def _record_interactive_turn_completion(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    turn_summary: dict[str, Any],
    progress_binding_capture: dict[str, Any],
    turn_root: Path,
    created_at: str,
    elapsed_seconds: int,
    delivered_output_line_count: int,
) -> dict[str, Any]:
    status = TURN_COMPLETION_FAILED_CLOSED if turn_summary.get("fail_closed") is True else TURN_COMPLETION_COMPLETED
    turn_completed = record_conversational_turn_completed(
        session_id=session_id,
        turn_id=turn_id,
        prompt_id=prompt_id,
        providers=_interactive_turn_providers(turn_summary),
        status=status,
        result_delivered=False,
        elapsed_seconds=elapsed_seconds,
        progress_replay_reference=progress_binding_capture["runtime_progress_replay_reference"],
        created_at=created_at,
        replay_dir=turn_root / "turn_completion",
    )
    delivery = record_conversational_result_delivered(
        turn_completed_artifact=turn_completed["turn_completed_artifact"],
        delivered_at=created_at,
        delivered_output_line_count=delivered_output_line_count,
    )
    turn_summary["turn_completed"] = True
    turn_summary["result_delivered"] = True
    turn_summary["turn_completion_replay_reference"] = delivery["turn_completion_replay_reference"]
    turn_summary["turn_completion_status"] = delivery["result_delivered_artifact"]["status"]
    turn_summary["turn_completion_artifact_type"] = turn_completed["turn_completed_artifact"]["artifact_type"]
    turn_summary["result_delivered_artifact_type"] = delivery["result_delivered_artifact"]["artifact_type"]
    turn_summary["elapsed_seconds"] = delivery["result_delivered_artifact"]["elapsed_seconds"]
    return delivery


def _record_interactive_hardening_capture(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    turn_summary: dict[str, Any],
    completion_capture: dict[str, Any],
    session_root: Path,
    turn_root: Path,
    created_at: str,
) -> dict[str, Any]:
    try:
        capture = record_completed_acli_interaction_hardening(
            session_id=session_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            turn_summary=turn_summary,
            completion_capture=completion_capture,
            session_root=session_root,
            turn_root=turn_root,
            created_at=created_at,
        )
        turn_summary["hardening_recorded"] = True
        turn_summary["hardening_result"] = capture["hardening_capture"]["result"]
        turn_summary["hardening_replay_reference"] = capture["hardening_replay_reference"]
        turn_summary["hardening_metrics_reference"] = capture["hardening_metrics_reference"]
        turn_summary["hardening_summary"] = capture["operator_summary"]
        turn_summary["hardening_authority_preserved"] = True
        return capture
    except Exception as exc:
        failure_reason = str(exc) or "ACLI hardening integration failed closed"
        turn_summary["hardening_recorded"] = False
        turn_summary["hardening_result"] = "FAILED_CLOSED"
        turn_summary["hardening_failure_reason"] = failure_reason
        turn_summary["hardening_authority_preserved"] = True
        return {
            "runtime_version": "ACLI_HARDENING_INTEGRATION_RUNTIME_V1",
            "integration_status": "HARDENING_CAPTURE_FAILED_CLOSED",
            "failure_reason": failure_reason,
            "operator_summary": "\n".join(
                [
                    "",
                    "Hardening",
                    "",
                    "Scenario: Not recorded",
                    "Coverage: Unchanged",
                    "Replay: Not recorded",
                    "Operator feedback: Optional",
                ]
            ),
            "read_only": True,
            "replay_visible": False,
            "authority_flags": {
                "authorizes_execution": False,
                "authorizes_dispatch": False,
                "authorizes_worker_invocation": False,
                "authorizes_provider_invocation": False,
                "authorizes_governance_mutation": False,
                "authorizes_replay_mutation": False,
                "authorizes_lifecycle_modification": False,
                "creates_approval": False,
                "creates_improvement_proposal": False,
            },
            "workflow_modified": False,
            "approval_created": False,
            "execution_authorized": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "governance_mutated": False,
            "replay_mutated": False,
        }


def _interactive_turn_elapsed_seconds(*, turn_started_monotonic: float, monotonic_now: Any) -> int:
    elapsed = float(monotonic_now()) - float(turn_started_monotonic)
    return max(0, int(elapsed))


def _interactive_turn_providers(turn_summary: dict[str, Any]) -> list[str]:
    provider_ids = turn_summary.get("provider_ids")
    if isinstance(provider_ids, list) and provider_ids:
        return [str(provider_id) for provider_id in provider_ids]
    if turn_summary.get("provider_invoked") is True:
        source = turn_summary.get("response_source")
        if isinstance(source, str) and source.strip():
            return [source.strip()]
        return ["PROVIDER_INVOKED"]
    return []


WORKFLOW_STATUS_WAITING_FOR_OPERATOR = "WAITING_FOR_OPERATOR"
WORKFLOW_STATUS_WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
WORKFLOW_STATUS_CONTINUATION_AVAILABLE = "CONTINUATION_AVAILABLE"
WORKFLOW_STATUS_COMPLETED = "COMPLETED"
WORKFLOW_STATUS_FAILED_CLOSED = "FAILED_CLOSED"

WORKFLOW_LIFECYCLE_STAGES = (
    "CLARIFICATION",
    "APPROVAL",
    "EXECUTION_READY",
    "EXECUTION_AUTHORIZED",
    "WORKER_REQUESTED",
    "WORKER_ASSIGNED",
    "WORKER_DISPATCHED",
    "WORKER_INVOKED",
    "EXECUTING",
    "RESULT_CREATED",
    "RESULT_VALIDATED",
    "REPLAY_REVIEWED",
    "REPLAY_CERTIFIED",
    "TERMINATED",
)


def _attach_interactive_workflow_status(turn_summary: dict[str, Any]) -> dict[str, Any]:
    status = _interactive_workflow_status(turn_summary)
    turn_summary["workflow_status"] = status
    return status


def _interactive_workflow_status(turn_summary: dict[str, Any]) -> dict[str, Any]:
    current_stage = _interactive_current_lifecycle_stage(turn_summary)
    workflow_state = _interactive_workflow_state(turn_summary, current_stage)
    current_stage_completed = workflow_state not in {
        WORKFLOW_STATUS_WAITING_FOR_OPERATOR,
        WORKFLOW_STATUS_WAITING_FOR_APPROVAL,
    }
    completed_stages = _interactive_completed_lifecycle_stages(current_stage, current_stage_completed)
    remaining_stages = _interactive_remaining_lifecycle_stages(current_stage, current_stage_completed)
    workflow_complete = workflow_state == WORKFLOW_STATUS_COMPLETED
    next_expected_action = _interactive_next_expected_action(
        turn_summary=turn_summary,
        workflow_state=workflow_state,
        current_stage=current_stage,
    )
    return {
        "workflow_name": _interactive_workflow_name(turn_summary),
        "workflow_state": workflow_state,
        "current_lifecycle_stage": current_stage,
        "next_expected_action": next_expected_action,
        "workflow_complete": workflow_complete,
        "required_input": _interactive_required_input(turn_summary),
        "completed_stages": completed_stages,
        "current_stage": current_stage,
        "remaining_stages": remaining_stages,
    }


def _render_interactive_workflow_status(status: dict[str, Any]) -> str:
    completed = status.get("completed_stages")
    if not isinstance(completed, list):
        completed = []
    remaining = status.get("remaining_stages")
    if not isinstance(remaining, list):
        remaining = []
    lines = [
        "Workflow Name: " + _workflow_status_value(status.get("workflow_name")),
        "Workflow State: " + _workflow_status_value(status.get("workflow_state")),
        "Current Lifecycle Stage: " + _workflow_status_value(status.get("current_lifecycle_stage")),
        "Next Expected Action: " + _workflow_status_value(status.get("next_expected_action")),
        "WORKFLOW COMPLETE: " + ("TRUE" if status.get("workflow_complete") is True else "FALSE"),
        "Lifecycle Progress:",
        "Completed Stages: " + _workflow_stage_list(completed),
        "Current Stage: " + _workflow_status_value(status.get("current_stage")),
        "Remaining Stages: " + _workflow_stage_list(remaining),
    ]
    if status.get("workflow_state") == WORKFLOW_STATUS_WAITING_FOR_OPERATOR:
        lines.extend(_render_waiting_for_operator_banner(status))
    return "\n".join(lines)


def _interactive_workflow_name(turn_summary: dict[str, Any]) -> str:
    for key in ("conversational_workflow_id", "originating_workflow_id", "response_source", "selected_source"):
        value = turn_summary.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "UNKNOWN_WORKFLOW"


def _interactive_current_lifecycle_stage(turn_summary: dict[str, Any]) -> str:
    if turn_summary.get("fail_closed") is True:
        return WORKFLOW_STATUS_FAILED_CLOSED
    if turn_summary.get("operator_revision_requested") is True:
        return "MODIFICATION_REQUESTED"
    if (
        turn_summary.get("handoff_review_next_certified_stage")
        == CONVERSATIONAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
    ):
        return "APPROVAL"
    if turn_summary.get("replay_certification_reached") is True:
        return "REPLAY_CERTIFIED"
    if turn_summary.get("clarification_resolved") is True and turn_summary.get("workflow_resumed") is True:
        return "APPROVAL"
    if turn_summary.get("execution_ready_continuation_status") == "EXECUTION_READY_CONTINUATION_CREATED":
        return "EXECUTION_READY"
    ordered_flags = (
        ("terminated", "TERMINATED"),
        ("post_execution_replay_reviewed", "REPLAY_REVIEWED"),
        ("worker_result_validated", "RESULT_VALIDATED"),
        ("worker_result_captured", "RESULT_CREATED"),
        ("execution_started", "EXECUTING"),
        ("worker_invoked", "WORKER_INVOKED"),
        ("worker_dispatched", "WORKER_DISPATCHED"),
        ("worker_assigned", "WORKER_ASSIGNED"),
        ("worker_request_created", "WORKER_REQUESTED"),
        ("authorization_created", "EXECUTION_AUTHORIZED"),
    )
    for flag, stage in ordered_flags:
        if turn_summary.get(flag) is True:
            return stage
    response_source = str(turn_summary.get("response_source") or "")
    if response_source == "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE":
        return "EXECUTION_READY"
    if turn_summary.get("approval_created") is True or "APPROVAL" in response_source:
        return "APPROVAL"
    if _interactive_waiting_for_clarification(turn_summary):
        return "CLARIFICATION"
    if turn_summary.get("domain_created") is True:
        return "APPROVAL"
    return str(turn_summary.get("response_status") or "TURN_COMPLETED")


def _interactive_workflow_state(turn_summary: dict[str, Any], current_stage: str) -> str:
    if turn_summary.get("fail_closed") is True:
        return WORKFLOW_STATUS_FAILED_CLOSED
    if turn_summary.get("operator_revision_requested") is True:
        return WORKFLOW_STATUS_WAITING_FOR_OPERATOR
    if _interactive_waiting_for_clarification(turn_summary):
        return WORKFLOW_STATUS_WAITING_FOR_OPERATOR
    response_status = str(turn_summary.get("response_status") or "")
    if "APPROVAL_REQUIRED" in response_status or turn_summary.get("approval_required") is True:
        return WORKFLOW_STATUS_WAITING_FOR_APPROVAL
    if current_stage in {"TERMINATED", "REPLAY_CERTIFIED"}:
        return WORKFLOW_STATUS_COMPLETED
    if current_stage in WORKFLOW_LIFECYCLE_STAGES:
        return WORKFLOW_STATUS_CONTINUATION_AVAILABLE
    return WORKFLOW_STATUS_COMPLETED


def _interactive_next_expected_action(
    *,
    turn_summary: dict[str, Any],
    workflow_state: str,
    current_stage: str,
) -> str:
    if workflow_state == WORKFLOW_STATUS_FAILED_CLOSED:
        reason = turn_summary.get("failure_reason")
        if isinstance(reason, str) and reason.strip():
            return f"Informational only: inspect fail-closed reason: {reason.strip()}"
        return "Informational only: inspect fail-closed replay evidence before continuing."
    if workflow_state == WORKFLOW_STATUS_WAITING_FOR_OPERATOR:
        if turn_summary.get("operator_revision_requested") is True:
            return "Informational only: describe the required proposal change."
        return "Informational only: provide the requested operator clarification."
    if workflow_state == WORKFLOW_STATUS_WAITING_FOR_APPROVAL:
        return "Informational only: provide an explicit operator approval or rejection decision."

    domain = _interactive_workflow_domain_text(turn_summary)
    if turn_summary.get("execution_ready_continuation_status") == "EXECUTION_READY_CONTINUATION_CREATED":
        return f"Create execution-ready authorization packet for {domain}."
    actions = {
        "CLARIFICATION": f"Authorize {domain} domain artifact request.",
        "APPROVAL": f"Authorize {domain} domain artifact request.",
        "EXECUTION_READY": f"Authorize execution-ready packet for {domain}.",
        "EXECUTION_AUTHORIZED": f"Create worker request for {domain}.",
        "WORKER_REQUESTED": f"Assign worker for {domain}.",
        "WORKER_ASSIGNED": f"Dispatch worker for {domain}.",
        "WORKER_DISPATCHED": f"Invoke worker for {domain}.",
        "WORKER_INVOKED": f"Execute worker for {domain}.",
        "EXECUTING": f"Capture worker result for {domain}.",
        "RESULT_CREATED": f"Validate worker result for {domain}.",
        "RESULT_VALIDATED": f"Review post-execution replay for {domain}.",
        "REPLAY_REVIEWED": f"Terminate reviewed operation for {domain}.",
        "REPLAY_CERTIFIED": "Informational only: no further operator action required.",
        "TERMINATED": "Informational only: no further operator action required.",
    }
    if workflow_state == WORKFLOW_STATUS_COMPLETED:
        return "Informational only: no further operator action required."
    return actions.get(current_stage, "Informational only: no governed continuation is currently available.")


def _interactive_workflow_domain_text(turn_summary: dict[str, Any]) -> str:
    for key in ("approved_domain", "proposed_domain", "requested_domain", "domain_name"):
        value = turn_summary.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "the active domain"


def _certified_auto_continuation_action(status: dict[str, Any]) -> str | None:
    if status.get("workflow_state") != WORKFLOW_STATUS_CONTINUATION_AVAILABLE:
        return None
    action = status.get("next_expected_action")
    stage = status.get("current_lifecycle_stage")
    if not isinstance(action, str) or not action.strip():
        return None
    action = action.strip()
    if action.startswith("Informational only:"):
        return None
    if "the active domain" in action:
        return None
    if not isinstance(stage, str) or stage not in WORKFLOW_LIFECYCLE_STAGES:
        return None
    certified_prefixes = {
        "CLARIFICATION": ("Authorize ",),
        "APPROVAL": ("Authorize ",),
        "EXECUTION_READY": (
            "Create execution-ready authorization packet for ",
            "Authorize execution-ready packet for ",
        ),
        "EXECUTION_AUTHORIZED": ("Create worker request for ",),
        "WORKER_REQUESTED": ("Assign worker for ",),
        "WORKER_ASSIGNED": ("Dispatch worker for ",),
        "WORKER_DISPATCHED": ("Invoke worker for ",),
        "WORKER_INVOKED": ("Execute worker for ",),
        "EXECUTING": ("Capture worker result for ",),
        "RESULT_CREATED": ("Validate worker result for ",),
        "RESULT_VALIDATED": ("Review post-execution replay for ",),
        "REPLAY_REVIEWED": ("Terminate reviewed operation for ",),
    }
    prefixes = certified_prefixes.get(stage)
    if prefixes is None:
        return None
    if not action.endswith("."):
        return None
    if not any(action.startswith(prefix) for prefix in prefixes):
        return None
    return action


def _auto_continue_stop_reason(status: dict[str, Any]) -> str:
    workflow_state = status.get("workflow_state")
    if workflow_state == WORKFLOW_STATUS_COMPLETED:
        return "WORKFLOW_COMPLETE"
    if workflow_state == WORKFLOW_STATUS_FAILED_CLOSED:
        return "FAILED_CLOSED"
    if workflow_state == WORKFLOW_STATUS_WAITING_FOR_OPERATOR:
        return "WAITING_FOR_OPERATOR"
    if workflow_state == WORKFLOW_STATUS_WAITING_FOR_APPROVAL:
        return "WAITING_FOR_APPROVAL"
    action = status.get("next_expected_action")
    if not isinstance(action, str) or not action.strip():
        return "MISSING_CONTINUATION"
    if action.startswith("Informational only:"):
        return "MISSING_CONTINUATION"
    return "AMBIGUOUS_CONTINUATION"


def _interactive_required_input(turn_summary: dict[str, Any]) -> list[str]:
    if turn_summary.get("operator_revision_requested") is True:
        return ["proposal revision description"]
    missing_information = turn_summary.get("missing_information")
    if isinstance(missing_information, list) and missing_information:
        return [str(item) for item in missing_information]
    if _interactive_waiting_for_clarification(turn_summary):
        return ["operator clarification"]
    return []


def _interactive_waiting_for_clarification(turn_summary: dict[str, Any]) -> bool:
    if turn_summary.get("clarification_resolved") is True or turn_summary.get("workflow_resumed") is True:
        return False
    return turn_summary.get("clarification_required") is True or turn_summary.get("open_clarification_detected") is True


def _interactive_prompt_label(workflow_status: dict[str, Any] | None) -> str:
    if not isinstance(workflow_status, dict):
        return f"AiGOL [{WORKFLOW_STATUS_COMPLETED}] > "
    workflow_state = _workflow_status_value(workflow_status.get("workflow_state"))
    current_stage = _workflow_status_value(workflow_status.get("current_lifecycle_stage"))
    if workflow_state in {WORKFLOW_STATUS_FAILED_CLOSED, WORKFLOW_STATUS_COMPLETED}:
        return f"AiGOL [{workflow_state}] > "
    if current_stage != "UNKNOWN":
        return f"AiGOL [{workflow_state}: {current_stage}] > "
    return f"AiGOL [{workflow_state}] > "


def _interactive_completed_lifecycle_stages(current_stage: str, current_stage_completed: bool) -> list[str]:
    if current_stage == WORKFLOW_STATUS_FAILED_CLOSED:
        return []
    if current_stage not in WORKFLOW_LIFECYCLE_STAGES:
        return []
    offset = 1 if current_stage_completed else 0
    return list(WORKFLOW_LIFECYCLE_STAGES[: WORKFLOW_LIFECYCLE_STAGES.index(current_stage) + offset])


def _interactive_remaining_lifecycle_stages(current_stage: str, current_stage_completed: bool) -> list[str]:
    if current_stage not in WORKFLOW_LIFECYCLE_STAGES:
        return []
    offset = 1 if current_stage_completed else 0
    return list(WORKFLOW_LIFECYCLE_STAGES[WORKFLOW_LIFECYCLE_STAGES.index(current_stage) + offset :])


def _render_waiting_for_operator_banner(status: dict[str, Any]) -> list[str]:
    required_input = status.get("required_input")
    if not isinstance(required_input, list) or not required_input:
        required_input = ["operator clarification"]
    return [
        "WAITING FOR OPERATOR INPUT",
        "Required input:",
        *[f"- {item}" for item in required_input],
    ]


def _workflow_stage_list(stages: list[Any]) -> str:
    return ", ".join(str(stage) for stage in stages) if stages else "NONE"


def _workflow_status_value(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "UNKNOWN"


def _interactive_live_progress_lines() -> list[str]:
    return [
        "Routing ...",
        "Cognition ...",
        "Provider Invocation ...",
        "Replay ...",
    ]


def _render_execution_runtime_summary(execution_capture: dict[str, Any]) -> str:
    execution = execution_capture.get("execution_artifact")
    if not isinstance(execution, dict):
        return "Execution Runtime\n\nExecution Status: UNAVAILABLE"
    return "\n".join(
        [
            "Execution Runtime",
            "",
            f"Execution Status: {execution.get('execution_status')}",
            f"Execution Reference: {execution.get('execution_id')}",
            f"Worker Invocation Reference: {execution.get('worker_invocation_reference')}",
            f"Replay Reference: {execution.get('replay_reference')}",
            "",
            "No completion recorded.",
            "No result certification recorded.",
            "No repair or reattempt started.",
        ]
    )


def _record_authorized_worker_execution_start(
    *,
    execution_id: str,
    invocation_artifact: dict[str, Any],
    invocation_replay: dict[str, Any],
    dispatch_artifact: dict[str, Any],
    worker_assignment_artifact: dict[str, Any],
    canonical_chain_id: str,
    worker_reference: str,
    worker_role: str,
    started_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    """Bridge ACLI continuation to the certified execution-start runtime."""

    return _record_execution_start(
        execution_id=execution_id,
        invocation_artifact=invocation_artifact,
        invocation_replay=invocation_replay,
        dispatch_artifact=dispatch_artifact,
        worker_assignment_artifact=worker_assignment_artifact,
        canonical_chain_id=canonical_chain_id,
        execution_metadata={
            "execution_mode": "START_ONLY",
            "runtime_boundary": "WORKER_INVOKED_TO_EXECUTING",
            "result_handling": "RESULT_CAPTURE_BOUNDARY_ONLY",
        },
        execution_context={
            "worker_reference": worker_reference,
            "request_type": "WORKER_INVOCATION_REQUEST",
            "capability_id": worker_role,
            "allowed_effects": ["RECORD_EXECUTION_START"],
        },
        started_by="AIGOL",
        started_at=started_at,
        replay_reference=str(replay_dir),
        replay_dir=replay_dir,
    )


def _delivered_output_line_count(*chunks: str) -> int:
    count = 0
    for chunk in chunks:
        if chunk:
            count += len(chunk.splitlines())
    return count


def _attach_interactive_multiline_prompt_capture(
    *,
    turn_summary: dict[str, Any],
    multiline_prompt_capture: dict[str, Any],
) -> None:
    artifact = multiline_prompt_capture["multiline_prompt_capture_artifact"]
    turn_summary["turn_started"] = multiline_prompt_capture["turn_started"]
    turn_summary["multiline_prompt_capture_replay_reference"] = multiline_prompt_capture[
        "multiline_prompt_capture_replay_reference"
    ]
    turn_summary["multiline_prompt_capture_artifact_type"] = artifact["artifact_type"]
    turn_summary["multiline_input_mode"] = artifact["input_mode"]
    turn_summary["multiline_line_count"] = artifact["line_count"]
    turn_summary["multiline_character_count"] = artifact["character_count"]
    turn_summary["assembled_prompt_hash"] = artifact["assembled_prompt_hash"]
    turn_summary["fragment_turns_created"] = artifact["fragment_turns_created"]
    turn_summary["partial_routing_allowed"] = artifact["partial_routing_allowed"]


def _attach_interactive_routing_visibility(
    *,
    turn_summary: dict[str, Any],
    routing_visibility_capture: dict[str, Any],
) -> None:
    artifact = routing_visibility_capture["conversational_routing_visibility_artifact"]
    turn_summary["routing_visibility_replay_reference"] = routing_visibility_capture[
        "conversational_routing_visibility_replay_reference"
    ]
    turn_summary["routing_visibility_artifact_type"] = artifact["artifact_type"]
    turn_summary["routing_visibility_workflow_id"] = artifact["workflow_id"]
    turn_summary["routing_visibility_status"] = artifact["routing_status"]
    turn_summary["routing_confidence"] = artifact["routing_confidence"]
    turn_summary["matched_signals"] = artifact["matched_signals"]
    turn_summary["competing_signals"] = artifact["competing_signals"]
    turn_summary["routing_reason"] = artifact["routing_reason"]


def _attach_interactive_universal_intake(
    *,
    turn_summary: dict[str, Any],
    universal_intake_capture: dict[str, Any] | None,
) -> None:
    if not isinstance(universal_intake_capture, dict):
        return
    artifact = universal_intake_capture.get("universal_intake_artifact")
    if not isinstance(artifact, dict):
        return
    turn_summary["universal_intake_replay_reference"] = universal_intake_capture[
        "universal_intake_replay_reference"
    ]
    turn_summary["universal_intake_artifact_type"] = artifact.get("artifact_type")
    turn_summary["universal_intake_status"] = artifact.get("intake_status")
    turn_summary["universal_intake_classification"] = artifact.get("intake_classification")
    turn_summary["universal_intake_cognition_required"] = artifact.get("cognition_required")
    turn_summary["universal_intake_provider_necessity"] = artifact.get("provider_necessity")
    turn_summary["universal_intake_domain_reference"] = artifact.get("domain_reference")
    turn_summary["universal_intake_worker_family_reference"] = artifact.get("worker_family_reference")
    turn_summary["universal_intake_approval_status"] = artifact.get("approval_status")
    turn_summary["universal_intake_next_backbone_target"] = artifact.get("next_backbone_target")
    turn_summary["universal_intake_source_workflow_id"] = artifact.get("source_workflow_id")
    turn_summary["universal_intake_provider_invoked"] = artifact.get("provider_invoked") is True
    turn_summary["universal_intake_worker_invoked"] = artifact.get("worker_invoked") is True
    turn_summary["universal_intake_approval_created"] = artifact.get("approval_created") is True
    turn_summary["universal_intake_ppp_artifact_mutated"] = artifact.get("ppp_artifact_mutated") is True
    turn_summary["universal_intake_governance_mutated"] = artifact.get("governance_mutated") is True
    turn_summary["universal_intake_fail_closed"] = artifact.get("fail_closed") is True


def _attach_interactive_human_friendly_explanation(
    *,
    turn_summary: dict[str, Any],
    explanation_capture: dict[str, Any],
) -> None:
    artifact = explanation_capture["human_friendly_explanation_artifact"]
    turn_summary["human_friendly_explanation_replay_reference"] = explanation_capture[
        "human_friendly_explanation_replay_reference"
    ]
    turn_summary["human_friendly_explanation_artifact_type"] = artifact["artifact_type"]
    turn_summary["human_friendly_explanation_workflow_id"] = artifact["workflow_id"]
    turn_summary["human_friendly_explanation_visibility_only"] = artifact["visibility_only"] is True
    turn_summary["human_friendly_explanation_authority_granted"] = artifact["authority_granted"] is True
    turn_summary["human_friendly_explanation_rendered_hash"] = artifact["rendered_explanation_hash"]


def _attach_interactive_llm_assisted_explanation(
    *,
    turn_summary: dict[str, Any],
    explanation_capture: dict[str, Any],
) -> None:
    artifact = explanation_capture["llm_assisted_explanation_artifact"]
    turn_summary["llm_assisted_explanation_replay_reference"] = explanation_capture[
        "llm_assisted_explanation_replay_reference"
    ]
    turn_summary["llm_assisted_explanation_artifact_type"] = artifact["artifact_type"]
    turn_summary["llm_assisted_explanation_status"] = artifact["explanation_status"]
    turn_summary["llm_assisted_explanation_provider_id"] = artifact["provider_id"]
    turn_summary["llm_assisted_explanation_provider_invoked"] = artifact["provider_invoked"] is True
    turn_summary["llm_assisted_explanation_provider_used"] = artifact["provider_explanation_used"] is True
    turn_summary["llm_assisted_explanation_deterministic_fallback_used"] = (
        artifact["deterministic_fallback_used"] is True
    )
    turn_summary["llm_assisted_explanation_advisory_only"] = artifact["advisory_only"] is True
    turn_summary["llm_assisted_explanation_authority_granted"] = artifact["authority_granted"] is True
    turn_summary["llm_assisted_explanation_rendered_hash"] = artifact["rendered_explanation_hash"]


def _record_interactive_routing_visibility(
    *,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    pending_approval_required: dict[str, Any] | None,
    recommendation_continuity_artifact: dict[str, Any] | None,
    recommendation_approval_artifact: dict[str, Any] | None,
    created_at: str,
    turn_root: Path,
    domain_approval_entry_intent: dict[str, Any] | None = None,
    conversational_routing_capture: dict[str, Any] | None = None,
    pending_governed_development_bridge: dict[str, Any] | None = None,
    pending_post_entry_continuation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if conversational_routing_capture is None:
        analysis = _interactive_routing_visibility_analysis(
            human_prompt=human_prompt,
            pending_approval_required=pending_approval_required,
            recommendation_continuity_artifact=recommendation_continuity_artifact,
            recommendation_approval_artifact=recommendation_approval_artifact,
            domain_approval_entry_intent=domain_approval_entry_intent,
            pending_governed_development_bridge=pending_governed_development_bridge,
            pending_post_entry_continuation=pending_post_entry_continuation,
        )
    else:
        analysis = _authoritative_routing_visibility_analysis(conversational_routing_capture)
    return record_conversational_routing_visibility(
        turn_id=turn_id,
        prompt_id=prompt_id,
        human_prompt=human_prompt,
        workflow_id=analysis["workflow_id"],
        routing_status=analysis["routing_status"],
        routing_confidence=analysis["routing_confidence"],
        matched_signals=analysis["matched_signals"],
        competing_signals=analysis["competing_signals"],
        routing_reason=analysis["routing_reason"],
        routing_timestamp=created_at,
        replay_dir=turn_root / "routing_visibility",
    )


def _authoritative_routing_visibility_analysis(conversational_routing_capture: dict[str, Any]) -> dict[str, Any]:
    decision = conversational_routing_capture.get("routing_decision_artifact")
    if not isinstance(decision, dict):
        decision = {}
    selection = conversational_routing_capture.get("workflow_selection_artifact")
    if not isinstance(selection, dict):
        selection = {}
    if conversational_routing_capture.get("fail_closed") is True:
        return {
            "workflow_id": NO_CERTIFIED_WORKFLOW_MATCHED,
            "routing_status": ROUTING_FAILED_CLOSED,
            "routing_confidence": ROUTING_VISIBILITY_LOW,
            "matched_signals": [],
            "competing_signals": [],
            "routing_reason": conversational_routing_capture.get("failure_reason") or "No certified workflow matched.",
        }
    confidence = str(decision.get("confidence") or ROUTING_VISIBILITY_LOW)
    if confidence not in {ROUTING_VISIBILITY_HIGH, ROUTING_VISIBILITY_MEDIUM, ROUTING_VISIBILITY_LOW}:
        confidence = ROUTING_VISIBILITY_LOW
    matched_terms = decision.get("matched_terms")
    if not isinstance(matched_terms, list):
        matched_terms = []
    return {
        "workflow_id": selection.get("workflow_id") or conversational_routing_capture.get("workflow_id"),
        "routing_status": ROUTING_SELECTED,
        "routing_confidence": confidence,
        "matched_signals": [str(term) for term in matched_terms],
        "competing_signals": [],
        "routing_reason": selection.get("operator_summary") or "Authoritative workflow selection recorded.",
    }


def _interactive_routing_visibility_analysis(
    *,
    human_prompt: str,
    pending_approval_required: dict[str, Any] | None,
    recommendation_continuity_artifact: dict[str, Any] | None,
    recommendation_approval_artifact: dict[str, Any] | None,
    domain_approval_entry_intent: dict[str, Any] | None = None,
    pending_governed_development_bridge: dict[str, Any] | None = None,
    pending_post_entry_continuation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    human_decision = normalize_human_decision(human_prompt)
    if (
        pending_post_entry_continuation is not None
        and _is_lifecycle_command_prompt(human_prompt)
    ):
        matched = (
            "continue ppp"
            if _post_entry_continuation_clarification_matches(human_prompt)
            else "lifecycle-command"
        )
        return _routing_visibility_selected(
            workflow_id=CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=["native-context-pending-continuation", matched],
            competing_signals=[],
            routing_reason=(
                "Stateful native development continuation detected; "
                "continuing the active workflow without rerouting."
            ),
        )
    if (
        pending_governed_development_bridge is not None
        and (
            human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
            or _is_explicit_governed_development_resume_approval(
                human_prompt,
                pending_governed_development_bridge,
            )
        )
    ):
        decision_signal = (
            APPROVE
            if _is_explicit_governed_development_resume_approval(
                human_prompt,
                pending_governed_development_bridge,
            )
            else human_decision
        )
        return _routing_visibility_selected(
            workflow_id=CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW,
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=["governed-development-pending-approval", decision_signal],
            competing_signals=[],
            routing_reason=(
                "Stateful governed development approval decision detected; "
                "continuing the pending proposal without rerouting."
            ),
        )
    if domain_approval_entry_intent and domain_approval_entry_intent.get("approval_entry_intent_detected") is True:
        return _routing_visibility_selected(
            workflow_id=CONVERSATIONAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=[
                "authorized_domain_artifact_request_review",
                str(domain_approval_entry_intent.get("domain_name") or ""),
                str(domain_approval_entry_intent.get("approval_action") or ""),
            ],
            competing_signals=[],
            routing_reason="Domain handoff review approval entry intent detected.",
        )
    if pending_approval_required is not None and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}:
        return _routing_visibility_selected(
            workflow_id=(
                "IMPLEMENTATION_APPROVAL_RESUME"
                if human_decision == APPROVE
                else "HUMAN_DECISION_RUNTIME"
            ),
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=[human_decision],
            competing_signals=[],
            routing_reason="Pending human approval context and explicit operator decision detected.",
        )
    if recommendation_continuity_artifact is not None and _is_recommendation_decision_prompt(human_prompt):
        return _routing_visibility_selected(
            workflow_id="RECOMMENDATION_APPROVAL",
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=[_recommendation_decision_from_prompt(human_prompt)],
            competing_signals=[],
            routing_reason="Pending recommendation continuity and explicit recommendation decision detected.",
        )
    if (
        recommendation_continuity_artifact is not None
        and recommendation_approval_artifact is not None
        and is_recommendation_followup_prompt(human_prompt)
    ):
        return _routing_visibility_selected(
            workflow_id="RECOMMENDATION_FOLLOWUP",
            routing_confidence=ROUTING_VISIBILITY_HIGH,
            matched_signals=_matched_terms(human_prompt, ("prepare", "proposal", "implementation", "candidate")),
            competing_signals=[],
            routing_reason="Approved recommendation context and follow-up preparation request detected.",
        )

    candidates = _interactive_routing_visibility_candidates(human_prompt)
    selected = _selected_routing_visibility_candidate(human_prompt, candidates)
    if selected is None:
        return {
            "workflow_id": NO_CERTIFIED_WORKFLOW_MATCHED,
            "routing_status": ROUTING_FAILED_CLOSED,
            "routing_confidence": ROUTING_VISIBILITY_LOW,
            "matched_signals": [],
            "competing_signals": [],
            "routing_reason": "No certified workflow matched.",
        }
    competing = [candidate["workflow_id"] for candidate in candidates if candidate["workflow_id"] != selected["workflow_id"]]
    confidence = selected["routing_confidence"]
    if competing and confidence == ROUTING_VISIBILITY_HIGH:
        confidence = ROUTING_VISIBILITY_MEDIUM
    return _routing_visibility_selected(
        workflow_id=selected["workflow_id"],
        routing_confidence=confidence,
        matched_signals=selected["matched_signals"],
        competing_signals=competing,
        routing_reason=selected["routing_reason"],
    )


def _interactive_routing_visibility_candidates(human_prompt: str) -> list[dict[str, Any]]:
    prompt = str(human_prompt or "")
    normalized = prompt.lower()
    candidates: list[dict[str, Any]] = []
    if _is_conversational_cli_readonly_candidate(prompt):
        if "latest" in normalized and ("replay chain" in normalized or "chain" in normalized):
            candidates.append(
                _candidate(
                    CONVERSATIONAL_SHOW_LATEST_REPLAY_CHAIN,
                    ROUTING_VISIBILITY_HIGH,
                    _matched_terms(prompt, ("latest", "replay", "chain")),
                    "Replay chain inspection request detected.",
                )
            )
        if "review" in normalized and "audit" in normalized:
            candidates.append(
                _candidate(
                    CONVERSATIONAL_REVIEW_LATEST_AUDIT,
                    ROUTING_VISIBILITY_HIGH,
                    _matched_terms(prompt, ("review", "audit")),
                    "Audit review request detected.",
                )
            )
        if "improve" in normalized and "provider" in normalized and "layer" in normalized:
            candidates.append(
                _candidate(
                    CONVERSATIONAL_IMPROVE_PROVIDER_LAYER,
                    ROUTING_VISIBILITY_MEDIUM,
                    _matched_terms(prompt, ("improve", "provider", "layer")),
                    "Provider-layer improvement guidance request detected.",
                )
            )
    if is_domain_reference_adaptation_prompt(prompt):
        candidates.append(
            _candidate(
                CONVERSATIONAL_DOMAIN_ADAPTATION_REFERENCE,
                ROUTING_VISIBILITY_HIGH,
                _matched_terms(prompt, ("similar", "based", "derived", "adaptation", "trading", "marketing", "domain")),
                "Domain adaptation reference signals detected.",
            )
        )
    if is_operator_decision_support_prompt(prompt):
        candidates.append(
            _candidate(
                CONVERSATIONAL_OPERATOR_DECISION_SUPPORT,
                ROUTING_VISIBILITY_HIGH,
                _matched_terms(prompt, ("first real", "product domain", "which", "capability", "provider", "roadmap", "priority")),
                "Operator decision-support request detected.",
            )
        )
    if is_unknown_domain_clarification_eligible(prompt):
        candidates.append(
            _candidate(
                CONVERSATIONAL_CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
                ROUTING_VISIBILITY_HIGH,
                _matched_terms(prompt, ("create", "domain", "compliance", "regulatory")),
                "Unknown-domain clarification route detected.",
            )
        )
    if _is_plain_domain_proposal_prompt(prompt):
        candidates.append(
            _candidate(
                CONVERSATIONAL_CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
                ROUTING_VISIBILITY_HIGH,
                _matched_terms(prompt, ("create", "new", "domain", "hr", "evaluation")),
                "Plain domain proposal request detected.",
            )
        )
    if is_conversation_native_development_intent(prompt):
        candidates.append(_native_development_visibility_candidate(prompt))
    if is_native_development_prompt(prompt):
        candidates.append(
            _candidate(
                "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
                ROUTING_VISIBILITY_HIGH,
                ["native_development_milestone"],
                "Native development milestone prompt detected.",
            )
        )
    if is_plain_native_development_prompt(prompt):
        candidates.append(
            _candidate(
                "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
                ROUTING_VISIBILITY_HIGH,
                _matched_terms(prompt, ("implement", "build", "add", "create", "function", "runtime")),
                "Plain native development prompt detected.",
            )
        )
    if is_ocs_llm_cognition_prompt(prompt):
        ocs_signals = _matched_terms(
            prompt,
            (
                "first real aigol product",
                "commercialization",
                "managed services",
                "license the platform",
                "sell domains",
                "should sapianta",
                "continue",
                "help me decide",
                "what should",
                "sapianta",
                "product",
            ),
        )
        candidates.append(
            _candidate(
                CONVERSATIONAL_OCS_LLM_COGNITION,
                ROUTING_VISIBILITY_HIGH if len(ocs_signals) >= 2 else ROUTING_VISIBILITY_MEDIUM,
                ocs_signals or ["ocs_cognition_marker"],
                "Prompt requests comparative strategic analysis.",
            )
        )
        if any(
            term in normalized
            for term in ("which", "should", "primarily", "recommend", "priority", "prioritize", "roadmap", "first")
        ):
            candidates.append(
                _candidate(
                    CONVERSATIONAL_OPERATOR_DECISION_SUPPORT,
                    ROUTING_VISIBILITY_LOW,
                    _matched_terms(
                        prompt,
                        ("which", "should", "primarily", "recommend", "priority", "prioritize", "roadmap", "first"),
                    ),
                    "Partial operator decision-support signals also detected.",
                )
            )
    return candidates


def _selected_routing_visibility_candidate(
    human_prompt: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    prompt = str(human_prompt or "")
    order = (
        CONVERSATIONAL_SHOW_LATEST_REPLAY_CHAIN,
        CONVERSATIONAL_REVIEW_LATEST_AUDIT,
        CONVERSATIONAL_IMPROVE_PROVIDER_LAYER,
        CONVERSATIONAL_DOMAIN_ADAPTATION_REFERENCE,
        CONVERSATIONAL_OPERATOR_DECISION_SUPPORT,
        CONVERSATIONAL_CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        CONVERSATIONAL_CREATE_DOMAIN_TRADING,
        CONVERSATIONAL_CREATE_DOMAIN_MARKETING,
        "NATIVE_DEVELOPMENT_INTENT_ROUTING",
        "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
        CONVERSATIONAL_OCS_LLM_COGNITION,
    )
    if is_ocs_llm_cognition_prompt(prompt):
        order = tuple(item for item in order if item != CONVERSATIONAL_OPERATOR_DECISION_SUPPORT) + (
            CONVERSATIONAL_OPERATOR_DECISION_SUPPORT,
        )
    by_workflow = {candidate["workflow_id"]: candidate for candidate in candidates}
    for workflow_id in order:
        if workflow_id in by_workflow:
            return by_workflow[workflow_id]
    return None


def _native_development_visibility_candidate(human_prompt: str) -> dict[str, Any]:
    normalized = str(human_prompt or "").lower()
    if "trading" in normalized and "domain" in normalized:
        workflow_id = CONVERSATIONAL_CREATE_DOMAIN_TRADING
    elif "marketing" in normalized and "domain" in normalized:
        workflow_id = CONVERSATIONAL_CREATE_DOMAIN_MARKETING
    else:
        workflow_id = "NATIVE_DEVELOPMENT_INTENT_ROUTING"
    return _candidate(
        workflow_id,
        ROUTING_VISIBILITY_HIGH,
        _matched_terms(
            human_prompt,
            (
                "create",
                "add",
                "improve",
                "domain",
                "worker",
                "provider",
                "trading",
                "marketing",
                "filesystem",
                "monitoring",
            ),
        ),
        "Native development intent signals detected.",
    )


def _is_plain_domain_proposal_prompt(human_prompt: str) -> bool:
    normalized = " ".join(str(human_prompt or "").lower().split())
    return (
        "domain" in normalized
        and ("create" in normalized or "need" in normalized or "want" in normalized or "prepare" in normalized)
        and "governed" not in normalized
        and "called" not in normalized
        and "named" not in normalized
        and any(
            term in normalized
            for term in (
                "new",
                "hr",
                "evaluation",
                "code auditing",
                "supplier",
                "ai decision validator",
                "foundation",
            )
        )
    )


def _is_plain_ocs_approval_prompt(human_prompt: str) -> bool:
    normalized = " ".join(str(human_prompt or "").lower().split())
    return (
        ("deploy" in normalized and "production" in normalized)
        or "modify production customer data" in normalized
        or "production customer data" in normalized
        or "external users" in normalized
        or "production rollout" in normalized
    )


def _plain_domain_proposal_name(human_prompt: str) -> str:
    normalized = " ".join(str(human_prompt or "").lower().split())
    if "ai decision validator" in normalized:
        return "AIDecisionValidator"
    if "hr" in normalized and "evaluation" in normalized:
        return "HREvaluation"
    if "hr" in normalized:
        return "HR"
    return "ProposedDomain"


def _routing_visibility_selected(
    *,
    workflow_id: str,
    routing_confidence: str,
    matched_signals: list[str],
    competing_signals: list[str],
    routing_reason: str,
) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "routing_status": ROUTING_SELECTED,
        "routing_confidence": routing_confidence,
        "matched_signals": matched_signals,
        "competing_signals": list(dict.fromkeys(competing_signals)),
        "routing_reason": routing_reason,
    }


def _candidate(
    workflow_id: str,
    routing_confidence: str,
    matched_signals: list[str],
    routing_reason: str,
) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "routing_confidence": routing_confidence,
        "matched_signals": matched_signals,
        "routing_reason": routing_reason,
    }


def _matched_terms(human_prompt: str, terms: tuple[str, ...]) -> list[str]:
    normalized = str(human_prompt or "").lower()
    return [term for term in terms if term in normalized]


def _read_interactive_prompt_capture(*, input_reader: Any, workflow_status: dict[str, Any] | None = None) -> dict[str, Any]:
    raw_prompt = input_reader(_interactive_prompt_label(workflow_status))
    if not _has_buffered_multiline_input(input_reader):
        return {
            "human_prompt": raw_prompt.strip(),
            "prompt_lines": [raw_prompt.strip()] if raw_prompt.strip() else [],
            "line_count": 1 if raw_prompt.strip() else 0,
            "input_mode": "SINGLE_LINE",
            "terminator": MULTILINE_PROMPT_TERMINATOR,
            "terminator_seen": False,
        }

    lines = [raw_prompt]
    terminator_seen = False
    while True:
        try:
            continuation = input_reader("... ")
        except EOFError:
            break
        if continuation.strip() == MULTILINE_PROMPT_TERMINATOR:
            terminator_seen = True
            break
        lines.append(continuation)
    assembled = "\n".join(lines)
    return {
        "human_prompt": assembled,
        "prompt_lines": lines,
        "line_count": len(lines),
        "input_mode": "MULTILINE_SENTINEL",
        "terminator": MULTILINE_PROMPT_TERMINATOR,
        "terminator_seen": terminator_seen,
    }


def _has_buffered_multiline_input(input_reader: Any) -> bool:
    has_pending = getattr(input_reader, "has_pending_input", None)
    if callable(has_pending):
        return bool(has_pending())
    if input_reader is not input:
        return False
    try:
        readable, _, _ = select.select([sys.stdin], [], [], 0)
    except Exception:
        return False
    return bool(readable)


def _artifact_from_args(args: argparse.Namespace) -> dict:
    if getattr(args, "artifact_json", ""):
        loaded = json.loads(args.artifact_json)
        if not isinstance(loaded, dict):
            raise ValueError("artifact JSON must be an object")
        return loaded
    return generate_ingress_artifact(
        human_request=getattr(args, "human_request", ""),
        semantic_intent=getattr(args, "semantic_intent", ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aigol", description="Deterministic AiGOL governance CLI substrate")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("status")

    runtime_status = subcommands.add_parser("runtime-status")
    runtime_status.add_argument("runtime_id")
    runtime_status.add_argument("--replay-root", default=".aigol_runtime_progress")
    runtime_status.add_argument("--json", action="store_true")

    runtime_progress = subcommands.add_parser("runtime-progress")
    runtime_progress.add_argument("runtime_id")
    runtime_progress.add_argument("--replay-root", default=".aigol_runtime_progress")
    runtime_progress.add_argument("--json", action="store_true")

    runtime_watch = subcommands.add_parser("runtime-watch")
    runtime_watch.add_argument("runtime_id")
    runtime_watch.add_argument("--replay-root", default=".aigol_runtime_progress")
    runtime_watch.add_argument("--interval-seconds", type=float, default=2.0)
    runtime_watch.add_argument("--iterations", type=int, default=0)
    runtime_watch.add_argument("--json", action="store_true")

    ingress = subcommands.add_parser("ingress")
    ingress_sub = ingress.add_subparsers(dest="ingress_command", required=True)
    ingress_generate = ingress_sub.add_parser("generate")
    ingress_generate.add_argument("--human-request", required=True)
    ingress_generate.add_argument("--semantic-intent", required=True)

    governance = subcommands.add_parser("governance")
    governance_sub = governance.add_subparsers(dest="governance_command", required=True)
    governance_validate = governance_sub.add_parser("validate")
    governance_validate.add_argument("--artifact-json", default="")
    governance_validate.add_argument("--human-request", default="Validate governed CLI continuity.")
    governance_validate.add_argument("--semantic-intent", default="Deterministic governance validation")

    approval = subcommands.add_parser("approval")
    approval_sub = approval.add_subparsers(dest="approval_command", required=True)
    approval_list = approval_sub.add_parser("list")
    approval_list.add_argument("--replay-root", default=".")
    approval_list.add_argument("--json", action="store_true")
    approval_show = approval_sub.add_parser("show")
    approval_show.add_argument("approval_id")
    approval_show.add_argument("--replay-root", default=".")
    approval_show.add_argument("--json", action="store_true")
    approval_pending = approval_sub.add_parser("pending")
    approval_pending.add_argument("--replay-root", default=".")
    approval_pending.add_argument("--json", action="store_true")
    approval_approved = approval_sub.add_parser("approved")
    approval_approved.add_argument("--replay-root", default=".")
    approval_approved.add_argument("--json", action="store_true")
    approval_rejected = approval_sub.add_parser("rejected")
    approval_rejected.add_argument("--replay-root", default=".")
    approval_rejected.add_argument("--json", action="store_true")
    approval_chain = approval_sub.add_parser("chain")
    approval_chain.add_argument("canonical_chain_id")
    approval_chain.add_argument("--replay-root", default=".")
    approval_chain.add_argument("--json", action="store_true")

    continuity = subcommands.add_parser("continuity")
    continuity_sub = continuity.add_subparsers(dest="continuity_command", required=True)
    continuity_preview = continuity_sub.add_parser("preview")
    continuity_preview.add_argument("--artifact-json", default="")
    continuity_preview.add_argument("--human-request", default="Preview governed execution continuity.")
    continuity_preview.add_argument("--semantic-intent", default="Deterministic continuity preview")

    dispatch = subcommands.add_parser("dispatch")
    dispatch_sub = dispatch.add_subparsers(dest="dispatch_command", required=True)
    dispatch_authorize = dispatch_sub.add_parser("authorize")
    dispatch_authorize.add_argument("--artifact-json", default="")
    dispatch_authorize.add_argument("--human-request", default="Authorize governed dispatch continuity.")
    dispatch_authorize.add_argument("--semantic-intent", default="Deterministic dispatch authorization")

    bridge = subcommands.add_parser("bridge")
    bridge_sub = bridge.add_subparsers(dest="bridge_command", required=True)
    bridge_list = bridge_sub.add_parser("list")
    bridge_list.add_argument("--replay-root", default=".")
    bridge_list.add_argument("--json", action="store_true")
    bridge_show = bridge_sub.add_parser("show")
    bridge_show.add_argument("bridge_id")
    bridge_show.add_argument("--replay-root", default=".")
    bridge_show.add_argument("--json", action="store_true")
    bridge_pending = bridge_sub.add_parser("pending")
    bridge_pending.add_argument("--replay-root", default=".")
    bridge_pending.add_argument("--json", action="store_true")
    bridge_approved = bridge_sub.add_parser("approved")
    bridge_approved.add_argument("--replay-root", default=".")
    bridge_approved.add_argument("--json", action="store_true")
    bridge_rejected = bridge_sub.add_parser("rejected")
    bridge_rejected.add_argument("--replay-root", default=".")
    bridge_rejected.add_argument("--json", action="store_true")
    bridge_chain = bridge_sub.add_parser("chain")
    bridge_chain.add_argument("canonical_chain_id")
    bridge_chain.add_argument("--replay-root", default=".")
    bridge_chain.add_argument("--json", action="store_true")
    bridge_execution_request = bridge_sub.add_parser("execution-request")
    bridge_execution_request.add_argument("execution_request_id")
    bridge_execution_request.add_argument("--replay-root", default=".")
    bridge_execution_request.add_argument("--json", action="store_true")

    plan = subcommands.add_parser("plan")
    plan_sub = plan.add_subparsers(dest="plan_command", required=True)
    plan_list = plan_sub.add_parser("list")
    plan_list.add_argument("--replay-root", default=".")
    plan_list.add_argument("--json", action="store_true")
    plan_show = plan_sub.add_parser("show")
    plan_show.add_argument("implementation_plan_id")
    plan_show.add_argument("--replay-root", default=".")
    plan_show.add_argument("--json", action="store_true")
    plan_approved = plan_sub.add_parser("approved")
    plan_approved.add_argument("--replay-root", default=".")
    plan_approved.add_argument("--json", action="store_true")
    plan_chain = plan_sub.add_parser("chain")
    plan_chain.add_argument("canonical_chain_id")
    plan_chain.add_argument("--replay-root", default=".")
    plan_chain.add_argument("--json", action="store_true")
    plan_bridge = plan_sub.add_parser("bridge")
    plan_bridge.add_argument("bridge_id")
    plan_bridge.add_argument("--replay-root", default=".")
    plan_bridge.add_argument("--json", action="store_true")
    plan_execution_request = plan_sub.add_parser("execution-request")
    plan_execution_request.add_argument("execution_request_id")
    plan_execution_request.add_argument("--replay-root", default=".")
    plan_execution_request.add_argument("--json", action="store_true")
    plan_latest = plan_sub.add_parser("latest")
    plan_latest.add_argument("--replay-root", default=".")
    plan_latest.add_argument("--json", action="store_true")

    dashboard = subcommands.add_parser("dashboard")
    dashboard.add_argument("--replay-root", default=".")
    dashboard.add_argument("--limit", type=int, default=10)
    dashboard.add_argument("--json", action="store_true")
    dashboard_sub = dashboard.add_subparsers(dest="dashboard_command")
    dashboard_summary = dashboard_sub.add_parser("summary")
    dashboard_summary.add_argument("--replay-root", default=".")
    dashboard_summary.add_argument("--limit", type=int, default=10)
    dashboard_summary.add_argument("--json", action="store_true")
    dashboard_approvals = dashboard_sub.add_parser("approvals")
    dashboard_approvals.add_argument("--replay-root", default=".")
    dashboard_approvals.add_argument("--limit", type=int, default=10)
    dashboard_approvals.add_argument("--json", action="store_true")
    dashboard_bridges = dashboard_sub.add_parser("bridges")
    dashboard_bridges.add_argument("--replay-root", default=".")
    dashboard_bridges.add_argument("--limit", type=int, default=10)
    dashboard_bridges.add_argument("--json", action="store_true")
    dashboard_chains = dashboard_sub.add_parser("chains")
    dashboard_chains.add_argument("--replay-root", default=".")
    dashboard_chains.add_argument("--limit", type=int, default=10)
    dashboard_chains.add_argument("--json", action="store_true")
    dashboard_learning = dashboard_sub.add_parser("learning")
    dashboard_learning.add_argument("--replay-root", default=".")
    dashboard_learning.add_argument("--limit", type=int, default=10)
    dashboard_learning.add_argument("--json", action="store_true")
    dashboard_execution = dashboard_sub.add_parser("execution")
    dashboard_execution.add_argument("--replay-root", default=".")
    dashboard_execution.add_argument("--limit", type=int, default=10)
    dashboard_execution.add_argument("--json", action="store_true")

    execution = subcommands.add_parser("execution")
    execution_sub = execution.add_subparsers(dest="execution_command", required=True)
    execution_handoff = execution_sub.add_parser("handoff")
    execution_handoff.add_argument("--artifact-json", default="")
    execution_handoff.add_argument("--human-request", default="Run governed execution handoff.")
    execution_handoff.add_argument("--semantic-intent", default="Deterministic execution handoff")
    execution_handoff.add_argument("--workspace-path", default="")
    execution_handoff.add_argument("--timeout-seconds", type=int, default=600)
    execution_handoff.add_argument("--full-codex-exec", action="store_true")
    execution_handoff.add_argument("--runtime-root", default="")

    implementation = subcommands.add_parser("implementation")
    implementation_sub = implementation.add_subparsers(dest="implementation_command", required=True)
    implementation_epoch = implementation_sub.add_parser("epoch")
    implementation_epoch.add_argument("--request", required=True)
    implementation_epoch.add_argument("--runtime-root", default=".aigol_implementation_generation_epoch")
    implementation_epoch.add_argument("--workspace", default=".aigol_implementation_generation_workspace")
    implementation_epoch.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    implementation_epoch.add_argument("--actor-id", default="human.operator")
    implementation_real_epoch = implementation_sub.add_parser("real-epoch")
    implementation_real_epoch.add_argument("--request", required=True)
    implementation_real_epoch.add_argument("--runtime-root", default=".aigol_real_implementation_generation_epoch")
    implementation_real_epoch.add_argument("--workspace", default=".aigol_real_implementation_generation_workspace")
    implementation_real_epoch.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    implementation_real_epoch.add_argument("--actor-id", default="human.operator")
    implementation_real_epoch.add_argument("--decision", default="")
    implementation_real_epoch.add_argument("--decision-reason", default="")
    implementation_compete = implementation_sub.add_parser("compete")
    implementation_compete.add_argument("--request", required=True)
    implementation_compete.add_argument("--runtime-root", default=".aigol_multi_provider_competition")
    implementation_compete.add_argument("--workspace", default=".aigol_multi_provider_competition_workspace")
    implementation_compete.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    implementation_compete.add_argument("--actor-id", default="human.operator")
    implementation_compete.add_argument("--selection", default="ABORT")
    implementation_compete.add_argument("--decision-reason", default="")

    provider = subcommands.add_parser("provider")
    provider_sub = provider.add_subparsers(dest="provider_command", required=True)
    provider_invoke = provider_sub.add_parser("invoke")
    provider_invoke.add_argument("--request", required=True)
    provider_invoke.add_argument("--execution-id", default="AIGOL-NATIVE-PROVIDER-EXECUTION-000001")
    provider_invoke.add_argument("--provider-id", default="openai")
    provider_invoke.add_argument("--model", default=DEFAULT_OPENAI_MODEL)
    provider_invoke.add_argument("--credential-env", default="AIGOL_OPENAI_API_KEY")
    provider_invoke.add_argument("--runtime-root", default=".aigol_native_provider_execution_runtime")
    provider_invoke.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    provider_invoke.add_argument("--approved-by", default="human.operator")
    provider_invoke.add_argument("--human-approved", action="store_true")
    provider_invoke.add_argument("--timeout-seconds", type=int, default=20)
    provider_invoke.add_argument("--json", action="store_true")
    provider_governance = provider_sub.add_parser("governance")
    provider_governance_sub = provider_governance.add_subparsers(dest="provider_governance_command", required=True)
    for governance_query in ("status", "credentials", "usage", "failures", "costs", "participation"):
        provider_governance_query = provider_governance_sub.add_parser(governance_query)
        provider_governance_query.add_argument("--replay-root", default=".")
        provider_governance_query.add_argument("--json", action="store_true")
    provider_credential = provider_sub.add_parser("credential")
    provider_credential_sub = provider_credential.add_subparsers(dest="provider_credential_command", required=True)
    for credential_command in ("add", "rotate"):
        provider_credential_mutation = provider_credential_sub.add_parser(credential_command)
        provider_credential_mutation.add_argument("provider_id")
        provider_credential_mutation.add_argument("--credential-env", default="AIGOL_PROVIDER_CREDENTIAL_INPUT")
        provider_credential_mutation.add_argument("--vault-path", default=str(DEFAULT_VAULT_PATH))
        provider_credential_mutation.add_argument("--replay-root", default=".aigol_provider_credential_vault")
        provider_credential_mutation.add_argument("--created-at", default="2026-06-21T00:00:00Z")
        provider_credential_mutation.add_argument("--human-approved", action="store_true")
        provider_credential_mutation.add_argument("--approved-by", default="human.operator")
        provider_credential_mutation.add_argument("--json", action="store_true")
    for credential_command in ("verify", "disable", "delete", "history", "status"):
        provider_credential_query = provider_credential_sub.add_parser(credential_command)
        provider_credential_query.add_argument("provider_id")
        provider_credential_query.add_argument("--vault-path", default=str(DEFAULT_VAULT_PATH))
        provider_credential_query.add_argument("--replay-root", default=".aigol_provider_credential_vault")
        provider_credential_query.add_argument("--created-at", default="2026-06-21T00:00:00Z")
        provider_credential_query.add_argument("--human-approved", action="store_true")
        provider_credential_query.add_argument("--approved-by", default="human.operator")
        provider_credential_query.add_argument("--json", action="store_true")

    return_cmd = subcommands.add_parser("return")
    return_sub = return_cmd.add_subparsers(dest="return_command", required=True)
    return_inspect = return_sub.add_parser("inspect")
    return_inspect.add_argument("--replay-identity", required=True)
    return_inspect.add_argument("--runtime-root", default="")

    replay = subcommands.add_parser("replay")
    replay_sub = replay.add_subparsers(dest="replay_command", required=True)
    replay_ledger = replay_sub.add_parser("ledger")
    replay_ledger.add_argument("--runtime-root", default="")
    replay_ledger.add_argument("--limit", type=int, default=10)
    replay_verify = replay_sub.add_parser("verify")
    replay_verify.add_argument("--replay-identity", required=True)
    replay_verify.add_argument("--runtime-root", default="")
    replay_operation = replay_sub.add_parser("operation")
    replay_operation.add_argument("--operation-id", required=True)
    replay_operation.add_argument("--runtime-root", default=".aigol_operator_runtime")
    replay_report = replay_sub.add_parser("report")
    replay_report.add_argument("--runtime-root", default=".aigol_operator_runtime")
    replay_report.add_argument("--limit", type=int, default=100)
    replay_explain = replay_sub.add_parser("explain")
    replay_explain.add_argument("--operation-id", required=True)
    replay_explain.add_argument("--runtime-root", default=".aigol_operator_runtime")

    diagnostics = subcommands.add_parser("diagnostics")
    diagnostics_sub = diagnostics.add_subparsers(dest="diagnostics_command", required=True)
    diagnostics_runtime = diagnostics_sub.add_parser("runtime")
    diagnostics_runtime.add_argument("--extension-id", default="")

    prompt = subcommands.add_parser("prompt")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)
    prompt_submit = prompt_sub.add_parser("submit")
    prompt_submit.add_argument("--prompt", required=True)
    prompt_submit.add_argument("--prompt-id", default="AIGOL-HUMAN-PROMPT-000001")
    prompt_submit.add_argument("--created-at", default="2026-06-01T00:00:00Z")
    prompt_submit.add_argument("--runtime-root", default=".aigol_prompt_runtime")
    prompt_submit.add_argument("--operator-context", default="operator_cli")

    conversational = subcommands.add_parser("conversational")
    conversational_sub = conversational.add_subparsers(dest="conversational_command", required=True)
    conversational_route = conversational_sub.add_parser("route")
    conversational_route.add_argument("--prompt", required=True)
    conversational_route.add_argument("--prompt-id", default="AIGOL-CONVERSATIONAL-PROMPT-000001")
    conversational_route.add_argument("--routing-id", default="AIGOL-CONVERSATIONAL-ROUTING-000001")
    conversational_route.add_argument("--canonical-chain-id", default="AIGOL-CONVERSATIONAL-CHAIN-000001")
    conversational_route.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    conversational_route.add_argument("--runtime-root", default=".aigol_conversational_cli_runtime")
    conversational_route.add_argument("--json", action="store_true")

    clarification = subcommands.add_parser("clarification")
    clarification_sub = clarification.add_subparsers(dest="clarification_command", required=True)
    clarification_unknown = clarification_sub.add_parser("unknown-domain")
    clarification_unknown.add_argument("--prompt", required=True)
    clarification_unknown.add_argument("--prompt-id", default="AIGOL-UNKNOWN-DOMAIN-PROMPT-000001")
    clarification_unknown.add_argument("--clarification-id", default="AIGOL-UNKNOWN-DOMAIN-CLARIFICATION-000001")
    clarification_unknown.add_argument("--canonical-chain-id", default="AIGOL-UNKNOWN-DOMAIN-CHAIN-000001")
    clarification_unknown.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    clarification_unknown.add_argument("--runtime-root", default=".aigol_unknown_domain_clarification_runtime")
    clarification_unknown.add_argument("--json", action="store_true")

    domain_reference = subcommands.add_parser("domain-reference")
    domain_reference_sub = domain_reference.add_subparsers(dest="domain_reference_command", required=True)
    domain_reference_resolve = domain_reference_sub.add_parser("resolve")
    domain_reference_resolve.add_argument("--prompt", required=True)
    domain_reference_resolve.add_argument("--prompt-id", default="AIGOL-DOMAIN-REFERENCE-PROMPT-000001")
    domain_reference_resolve.add_argument("--resolution-id", default="AIGOL-DOMAIN-REFERENCE-RESOLUTION-000001")
    domain_reference_resolve.add_argument("--canonical-chain-id", default="AIGOL-DOMAIN-REFERENCE-CHAIN-000001")
    domain_reference_resolve.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    domain_reference_resolve.add_argument("--runtime-root", default=".aigol_domain_reference_runtime")
    domain_reference_resolve.add_argument("--json", action="store_true")

    decision_support = subcommands.add_parser("decision-support")
    decision_support_sub = decision_support.add_subparsers(dest="decision_support_command", required=True)
    decision_support_recommend = decision_support_sub.add_parser("recommend")
    decision_support_recommend.add_argument("--prompt", required=True)
    decision_support_recommend.add_argument("--prompt-id", default="AIGOL-DECISION-SUPPORT-PROMPT-000001")
    decision_support_recommend.add_argument("--recommendation-id", default="AIGOL-DECISION-SUPPORT-RECOMMENDATION-000001")
    decision_support_recommend.add_argument("--canonical-chain-id", default="AIGOL-DECISION-SUPPORT-CHAIN-000001")
    decision_support_recommend.add_argument("--created-at", default="2026-06-05T00:00:00Z")
    decision_support_recommend.add_argument("--runtime-root", default=".aigol_operator_decision_support_runtime")
    decision_support_recommend.add_argument("--json", action="store_true")

    conversation = subcommands.add_parser("conversation")
    conversation.add_argument("--session-id", default="AIGOL-INTERACTIVE-CONVERSATION-000001")
    conversation.add_argument("--created-at", default="2026-06-01T00:00:00Z")
    conversation.add_argument("--runtime-root", default=".aigol_conversation_runtime")
    conversation.add_argument("--operator-context", default="interactive_conversation_cli")
    conversation.add_argument("--workspace", default=".")
    conversation.add_argument("--auto-continue", action="store_true")
    conversation.add_argument("--enable-llm-assisted-explanation", action="store_true")
    conversation.add_argument("--llm-explanation-provider-id", default="UNSPECIFIED_EXPLANATION_PROVIDER")

    show_latest_chain = subcommands.add_parser("show-latest-chain")
    show_latest_chain.add_argument("--replay-root", default=".")
    show_latest_chain.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_latest_chain.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_latest_chain.add_argument("--json", action="store_true")

    show_chain = subcommands.add_parser("show-chain")
    show_chain.add_argument("canonical_chain_id")
    show_chain.add_argument("--replay-root", default=".")
    show_chain.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_chain.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_chain.add_argument("--json", action="store_true")

    show_execution_lifecycle = subcommands.add_parser("show-execution-lifecycle")
    show_execution_lifecycle.add_argument("canonical_chain_id")
    show_execution_lifecycle.add_argument("--replay-root", default=".")
    show_execution_lifecycle.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_execution_lifecycle.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_execution_lifecycle.add_argument("--json", action="store_true")

    show_learning_lifecycle = subcommands.add_parser("show-learning-lifecycle")
    show_learning_lifecycle.add_argument("canonical_chain_id")
    show_learning_lifecycle.add_argument("--replay-root", default=".")
    show_learning_lifecycle.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_learning_lifecycle.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_learning_lifecycle.add_argument("--json", action="store_true")

    show_full_lineage = subcommands.add_parser("show-full-lineage")
    show_full_lineage.add_argument("canonical_chain_id")
    show_full_lineage.add_argument("--replay-root", default=".")
    show_full_lineage.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_full_lineage.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_full_lineage.add_argument("--json", action="store_true")

    show_chain_summary = subcommands.add_parser("show-chain-summary")
    show_chain_summary.add_argument("canonical_chain_id")
    show_chain_summary.add_argument("--replay-root", default=".")
    show_chain_summary.add_argument("--report-root", default=".aigol_chain_inspection_runtime")
    show_chain_summary.add_argument("--created-at", default="2026-06-02T00:00:00Z")
    show_chain_summary.add_argument("--json", action="store_true")

    run_governed = subcommands.add_parser("run-governed")
    run_governed.add_argument("--worker", required=True)
    run_governed.add_argument("--operation", required=True)
    run_governed.add_argument("--target", required=True)
    run_governed.add_argument("--content", default="FIRST_END_TO_END_GOVERNED_OPERATION_V1")
    run_governed.add_argument("--operation-id", default="AIGOL-RUN-GOVERNED-000001")
    run_governed.add_argument("--created-at", default="2026-05-31T00:00:00Z")
    run_governed.add_argument("--runtime-root", default=".aigol_operator_runtime")
    run_governed.add_argument("--workspace", default=".")

    moc = subcommands.add_parser("moc")
    moc_sub = moc.add_subparsers(dest="moc_command", required=True)
    moc_validate_contract = moc_sub.add_parser("validate-contract")
    moc_validate_contract.add_argument("--input", required=True)
    moc_validate_contract.add_argument("--json", action="store_true")
    moc_validate_contract.add_argument("--output", default="")
    moc_generate_contract = moc_sub.add_parser("generate-contract")
    moc_generate_contract.add_argument("--input", required=True)
    moc_generate_contract.add_argument("--json", action="store_true")
    moc_generate_contract.add_argument("--output", default="")
    moc_validate_proposal = moc_sub.add_parser("validate-proposal")
    moc_validate_proposal.add_argument("--proposal", required=True)
    moc_validate_proposal.add_argument("--contract", required=True)
    moc_validate_proposal.add_argument("--json", action="store_true")
    moc_validate_proposal.add_argument("--output", default="")
    moc_correction_feedback = moc_sub.add_parser("correction-feedback")
    moc_correction_feedback.add_argument("--validation-result", required=True)
    moc_correction_feedback.add_argument("--attempt", type=int, required=True)
    moc_correction_feedback.add_argument("--max-attempts", type=int, required=True)
    moc_correction_feedback.add_argument("--json", action="store_true")
    moc_correction_feedback.add_argument("--output", default="")
    moc_persist_proposal = moc_sub.add_parser("persist-proposal")
    moc_persist_proposal.add_argument("--proposal", required=True)
    moc_persist_proposal.add_argument("--state", required=True)
    moc_persist_proposal.add_argument("--previous-state", required=True)
    moc_persist_proposal.add_argument("--json", action="store_true")
    moc_persist_proposal.add_argument("--output", default="")
    moc_append_ledger = moc_sub.add_parser("append-ledger")
    moc_append_ledger.add_argument("--persistence-record", required=True)
    moc_append_ledger.add_argument("--ledger-path", default=DEFAULT_LEDGER_PATH)
    moc_append_ledger.add_argument("--json", action="store_true")
    moc_append_ledger.add_argument("--output", default="")
    moc_approval_gate = moc_sub.add_parser("approval-gate")
    moc_approval_gate.add_argument("--proposal", required=True)
    moc_approval_gate.add_argument("--ledger-entry", required=True)
    moc_approval_gate.add_argument("--approval-evidence", required=True)
    moc_approval_gate.add_argument("--json", action="store_true")
    moc_approval_gate.add_argument("--output", default="")
    moc_prepare_worker = moc_sub.add_parser("prepare-worker")
    moc_prepare_worker.add_argument("--proposal", required=True)
    moc_prepare_worker.add_argument("--approval-gate", required=True)
    moc_prepare_worker.add_argument("--json", action="store_true")
    moc_prepare_worker.add_argument("--output", default="")
    moc_dispatch_preview = moc_sub.add_parser("dispatch-preview")
    moc_dispatch_preview.add_argument("--worker-package", required=True)
    moc_dispatch_preview.add_argument("--json", action="store_true")
    moc_dispatch_preview.add_argument("--output", default="")
    moc_dispatch_request = moc_sub.add_parser("dispatch-request")
    moc_dispatch_request.add_argument("--dispatch-preview", required=True)
    moc_dispatch_request.add_argument("--request-evidence", required=True)
    moc_dispatch_request.add_argument("--json", action="store_true")
    moc_dispatch_request.add_argument("--output", default="")
    moc_dispatch_authorize = moc_sub.add_parser("dispatch-authorize")
    moc_dispatch_authorize.add_argument("--dispatch-request", required=True)
    moc_dispatch_authorize.add_argument("--json", action="store_true")
    moc_dispatch_authorize.add_argument("--output", default="")
    moc_runtime_dispatch = moc_sub.add_parser("runtime-dispatch")
    moc_runtime_dispatch.add_argument("--dispatch-authorization", required=True)
    moc_runtime_dispatch.add_argument("--json", action="store_true")
    moc_runtime_dispatch.add_argument("--output", default="")
    moc_provider_execution_gate = moc_sub.add_parser("provider-execution-gate")
    moc_provider_execution_gate.add_argument("--runtime-dispatch", required=True)
    moc_provider_execution_gate.add_argument("--json", action="store_true")
    moc_provider_execution_gate.add_argument("--output", default="")
    moc_interpret_return = moc_sub.add_parser("interpret-return")
    moc_interpret_return.add_argument("--runtime-dispatch", required=True)
    moc_interpret_return.add_argument("--provider-gate", default="")
    moc_interpret_return.add_argument("--return-evidence", default="")
    moc_interpret_return.add_argument("--json", action="store_true")
    moc_interpret_return.add_argument("--output", default="")
    moc_operational_lineage = moc_sub.add_parser("operational-lineage")
    moc_operational_lineage.add_argument("--contract", required=True)
    moc_operational_lineage.add_argument("--proposal", required=True)
    moc_operational_lineage.add_argument("--approval", required=True)
    moc_operational_lineage.add_argument("--runtime-dispatch", required=True)
    moc_operational_lineage.add_argument("--governed-return", required=True)
    moc_operational_lineage.add_argument("--provider-gate", default="")
    moc_operational_lineage.add_argument("--json", action="store_true")
    moc_operational_lineage.add_argument("--output", default="")

    cognition = subcommands.add_parser("cognition")
    cognition_sub = cognition.add_subparsers(dest="cognition_command", required=True)
    cognition_inspect = cognition_sub.add_parser("inspect")
    cognition_inspect.add_argument("--input", default="")
    cognition_inspect.add_argument("--json", action="store_true")
    cognition_inspect.add_argument("--output", default="")
    cognition_continuity = cognition_sub.add_parser("continuity-check")
    cognition_continuity.add_argument("--input", default="")
    cognition_continuity.add_argument("--json", action="store_true")
    cognition_continuity.add_argument("--output", default="")
    cognition_registry = cognition_sub.add_parser("registry")
    cognition_registry.add_argument("--input", default="")
    cognition_registry.add_argument("--json", action="store_true")
    cognition_registry.add_argument("--output", default="")
    cognition_topology = cognition_sub.add_parser("topology")
    cognition_topology.add_argument("--input", default="")
    cognition_topology.add_argument("--json", action="store_true")
    cognition_topology.add_argument("--output", default="")
    cognition_lifecycle = cognition_sub.add_parser("lifecycle")
    cognition_lifecycle.add_argument("--json", action="store_true")
    cognition_lifecycle.add_argument("--output", default="")
    cognition_lifecycle.add_argument("--validate", action="store_true")
    cognition_integrity = cognition_sub.add_parser("integrity")
    cognition_integrity.add_argument("--input", default="")
    cognition_integrity.add_argument("--json", action="store_true")
    cognition_integrity.add_argument("--output", default="")
    cognition_integrity.add_argument("--validate", action="store_true")
    cognition_authority = cognition_sub.add_parser("authority")
    cognition_authority.add_argument("--input", default="")
    cognition_authority.add_argument("--json", action="store_true")
    cognition_authority.add_argument("--output", default="")
    cognition_authority.add_argument("--validate", action="store_true")
    cognition_semantic_context = cognition_sub.add_parser("semantic-context")
    cognition_semantic_context.add_argument("--input", default="")
    cognition_semantic_context.add_argument("--json", action="store_true")
    cognition_semantic_context.add_argument("--output", default="")
    cognition_semantic_context.add_argument("--validate", action="store_true")
    cognition_semantic_relationships = cognition_sub.add_parser("semantic-relationships")
    cognition_semantic_relationships.add_argument("--input", default="")
    cognition_semantic_relationships.add_argument("--json", action="store_true")
    cognition_semantic_relationships.add_argument("--output", default="")
    cognition_semantic_relationships.add_argument("--validate", action="store_true")
    cognition_semantic_boundaries = cognition_sub.add_parser("semantic-boundaries")
    cognition_semantic_boundaries.add_argument("--input", default="")
    cognition_semantic_boundaries.add_argument("--json", action="store_true")
    cognition_semantic_boundaries.add_argument("--output", default="")
    cognition_semantic_boundaries.add_argument("--validate", action="store_true")
    cognition_semantic_diff = cognition_sub.add_parser("semantic-diff")
    cognition_semantic_diff.add_argument("--source", default="")
    cognition_semantic_diff.add_argument("--target", default="")
    cognition_semantic_diff.add_argument("--json", action="store_true")
    cognition_semantic_diff.add_argument("--output", default="")
    cognition_semantic_diff.add_argument("--validate", action="store_true")
    cognition_semantic_audit_bundle = cognition_sub.add_parser("semantic-audit-bundle")
    cognition_semantic_audit_bundle.add_argument("--input", default="")
    cognition_semantic_audit_bundle.add_argument("--json", action="store_true")
    cognition_semantic_audit_bundle.add_argument("--output", default="")
    cognition_semantic_audit_bundle.add_argument("--validate", action="store_true")

    return parser


def run_interactive_conversation(
    args: argparse.Namespace,
    *,
    input_func: Any | None = None,
    output_func: Any | None = None,
    monotonic_func: Any | None = None,
    llm_explanation_provider: Any | None = None,
) -> dict[str, Any]:
    input_reader = input if input_func is None else input_func
    output_writer = print if output_func is None else output_func
    terminal_output_writer = output_writer
    monotonic_now = time.monotonic if monotonic_func is None else monotonic_func
    session_id = _require_cli_string(args.session_id, "session_id")
    created_at = _require_cli_string(args.created_at, "created_at")
    runtime_root = Path(args.runtime_root)
    session_root = runtime_root / session_id
    turns: list[dict[str, Any]] = []
    turn_count = 0
    failed_turns = 0
    exit_reason = "EXIT_COMMAND"
    current_chain_id: str | None = None
    latest_chain_id: str | None = None
    pending_approval_required: dict[str, Any] | None = None
    pending_domain_proposal: dict[str, Any] | None = None
    pending_domain_review: dict[str, Any] | None = None
    initial_resume = resume_conversation_session(session_id=session_id, runtime_root=runtime_root, created_at=created_at)
    recommendation_continuity_artifact, recommendation_approval_artifact = _latest_recommendation_state(session_root)
    latest_workflow_status: dict[str, Any] | None = None
    pending_governed_development_bridge: dict[str, Any] | None = None
    pending_governed_development_bridge_restored = False
    pending_governed_development_resume_presented = False
    auto_continue_enabled = bool(getattr(args, "auto_continue", False))
    llm_assisted_explanation_enabled = bool(
        getattr(args, "enable_llm_assisted_explanation", False)
        or llm_explanation_provider is not None
    )
    llm_explanation_provider_id = str(
        getattr(args, "llm_explanation_provider_id", "UNSPECIFIED_EXPLANATION_PROVIDER")
        or "UNSPECIFIED_EXPLANATION_PROVIDER"
    )
    pending_auto_continuation: str | None = None
    pending_post_entry_continuation: dict[str, Any] | None = None
    auto_continue_turns = 0
    auto_continue_stop_reason: str | None = None
    if input_func is None and output_func is None:
        output_writer(INTERACTIVE_CONVERSATION_MULTILINE_BANNER)

    while True:
        auto_continuation_prompt = pending_auto_continuation
        pending_auto_continuation = None
        if auto_continuation_prompt is not None:
            prompt_capture = {
                "human_prompt": auto_continuation_prompt,
                "prompt_lines": [auto_continuation_prompt],
                "line_count": 1,
                "input_mode": "AUTO_CONTINUE",
                "terminator": MULTILINE_PROMPT_TERMINATOR,
                "terminator_seen": False,
            }
        else:
            try:
                prompt_capture = _read_interactive_prompt_capture(
                    input_reader=input_reader,
                    workflow_status=latest_workflow_status,
                )
            except EOFError:
                exit_reason = "EOF"
                break

        human_prompt = prompt_capture["human_prompt"]
        if not human_prompt:
            continue
        if prompt_capture["input_mode"] == "SINGLE_LINE" and human_prompt.lower() in INTERACTIVE_EXIT_COMMANDS:
            break

        turn_started_monotonic = float(monotonic_now())
        turn_count += 1
        turn_id = "TURN-UNALLOCATED"
        prompt_id = f"{session_id}:{turn_id}"
        turn_root = session_root / turn_id
        progress_binding_capture: dict[str, Any] | None = None
        universal_intake_capture: dict[str, Any] | None = None
        human_friendly_explanation_capture: dict[str, Any] | None = None
        llm_assisted_explanation_capture: dict[str, Any] | None = None
        turn_progress_buffer: list[str] = []
        turn_output_buffer: list[str] = []
        try:
            resume_state = resume_conversation_session(
                session_id=session_id,
                runtime_root=runtime_root,
                created_at=created_at,
            )
            turn_id = resume_state["next_turn_id"]
            prompt_id = f"{session_id}:{turn_id}"
            turn_root = session_root / turn_id
            multiline_prompt_capture = record_multiline_prompt_capture(
                session_id=session_id,
                turn_id=turn_id,
                prompt_id=prompt_id,
                prompt_lines=prompt_capture["prompt_lines"],
                assembled_prompt=human_prompt,
                terminator=prompt_capture["terminator"],
                created_at=created_at,
                replay_dir=turn_root / "multiline_prompt_capture",
            )
            progress_binding_capture = _create_interactive_conversation_progress_binding(
                session_id=session_id,
                turn_id=turn_id,
                prompt_id=prompt_id,
                created_at=created_at,
                turn_root=turn_root,
            )
            human_decision = normalize_human_decision(human_prompt)
            domain_proposal_decision = _domain_proposal_review_decision(human_prompt, human_decision)
            lifecycle_command_detected = _is_lifecycle_command_prompt(human_prompt)
            native_development_prompt_detected = is_native_development_prompt(human_prompt)
            if (
                pending_post_entry_continuation is None
                and _post_entry_continuation_clarification_matches(human_prompt)
            ):
                pending_post_entry_continuation = _restore_pending_post_entry_continuation_from_replay(
                    session_root=session_root,
                    turn_root=turn_root,
                    created_at=created_at,
                )
            if (
                pending_governed_development_bridge is None
                and _is_governed_development_resume_decision_prompt(human_prompt)
            ):
                pending_governed_development_bridge = _restore_pending_governed_development_bridge_from_replay(
                    session_root=session_root,
                    turn_root=turn_root,
                    created_at=created_at,
                )
                pending_governed_development_bridge_restored = pending_governed_development_bridge is not None
                pending_governed_development_resume_presented = False
            if (
                pending_governed_development_bridge is not None
                and _is_explicit_governed_development_resume_approval(
                    human_prompt,
                    pending_governed_development_bridge,
                )
            ):
                human_decision = APPROVE
            active_clarification_capture = detect_active_clarification(session_root=session_root)
            active_clarification_detected = active_clarification_capture.get("open_clarification_detected") is True
            clarification_reply_gate_capture = (
                should_bind_operator_reply_to_active_clarification(
                    session_root=session_root,
                    human_prompt=human_prompt,
                )
                if active_clarification_detected
                else {"should_bind_reply": False}
            )
            active_clarification_reply_detected = (
                clarification_reply_gate_capture.get("should_bind_reply") is True
                and not native_development_prompt_detected
            )
            active_clarification_reply_mismatch_detected = (
                active_clarification_detected
                and not native_development_prompt_detected
                and clarification_reply_gate_capture.get("binding_decision_reason")
                == "REPLY_DOES_NOT_MATCH_ACTIVE_CLARIFICATION_SCOPE"
            )
            domain_approval_entry_intent = detect_domain_approval_entry_intent(human_prompt)
            domain_approval_entry_detected = (
                domain_approval_entry_intent.get("approval_entry_intent_detected") is True
            )
            stateful_pre_routing_gate = (
                active_clarification_reply_detected
                or active_clarification_reply_mismatch_detected
                or domain_approval_entry_detected
                or (
                    pending_domain_proposal is not None
                    and domain_proposal_decision is not None
                )
                or (
                    pending_domain_review is not None
                    and _is_domain_candidate_continuation_prompt(human_prompt)
                )
                or (
                    pending_approval_required is not None
                    and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
                )
                or (
                    pending_governed_development_bridge is not None
                    and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
                )
                or (
                    recommendation_continuity_artifact is not None
                    and _is_recommendation_decision_prompt(human_prompt)
                )
                or (
                    recommendation_continuity_artifact is not None
                    and recommendation_approval_artifact is not None
                    and is_recommendation_followup_prompt(human_prompt)
                )
                or (
                    pending_post_entry_continuation is not None
                    and _post_entry_continuation_clarification_matches(human_prompt)
                )
                or (
                    lifecycle_command_detected
                    and (
                        pending_governed_development_bridge is not None
                        or pending_post_entry_continuation is not None
                    )
                )
            )
            conversational_routing_capture: dict[str, Any] | None = None
            if not stateful_pre_routing_gate:
                conversational_routing_capture = route_conversational_cli_intent(
                    routing_id=f"{prompt_id}:CONVERSATIONAL-CLI-ROUTING",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    canonical_chain_id=current_chain_id or prompt_id,
                    created_at=created_at,
                    replay_dir=turn_root / "conversational_cli_routing",
                )
            authoritative_workflow_id = (
                (conversational_routing_capture or {}).get("workflow_selection_artifact", {}).get("workflow_id")
            )
            if _interactive_deterministic_conversation_submit_override_active():
                authoritative_workflow_id = CONVERSATIONAL_DEFAULT_PROVIDER_ASSISTED_CONVERSATION
            stateful_governed_development_decision = (
                pending_governed_development_bridge is not None
                and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
            )
            if stateful_governed_development_decision:
                authoritative_workflow_id = CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW
            routing_visibility_capture = _record_interactive_routing_visibility(
                turn_id=turn_id,
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                pending_approval_required=pending_approval_required,
                recommendation_continuity_artifact=recommendation_continuity_artifact,
                recommendation_approval_artifact=recommendation_approval_artifact,
                domain_approval_entry_intent=domain_approval_entry_intent,
                conversational_routing_capture=conversational_routing_capture,
                pending_governed_development_bridge=pending_governed_development_bridge,
                pending_post_entry_continuation=pending_post_entry_continuation,
                created_at=created_at,
                turn_root=turn_root,
            )
            turn_progress_buffer.append(routing_visibility_capture["operator_routing_summary"])
            turn_progress_buffer.extend(_interactive_live_progress_lines())
            _emit_interactive_conversation_progress(
                binding_capture=progress_binding_capture,
                stage=CONVERSATIONAL_PROGRESS_ROUTING,
                activity="Prompt received; routing started.",
                snapshot_at=created_at,
                output_writer=turn_progress_buffer.append,
            )
            output_writer = turn_output_buffer.append
            router_capture = route_source_of_truth(
                router_id=f"{prompt_id}:SOURCE_ROUTER",
                human_prompt_reference=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                replay_dir=turn_root / "source_router",
            )
            universal_intake_capture = record_universal_intake(
                intake_id=f"{prompt_id}:UNIVERSAL-INTAKE",
                turn_id=turn_id,
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                chain_id=current_chain_id or prompt_id,
                workflow_id=authoritative_workflow_id or NO_CERTIFIED_WORKFLOW_MATCHED,
                routing_visibility_artifact=routing_visibility_capture[
                    "conversational_routing_visibility_artifact"
                ],
                routing_visibility_replay_reference=routing_visibility_capture[
                    "conversational_routing_visibility_replay_reference"
                ],
                source_router_replay_reference=str(turn_root / "source_router"),
                created_at=created_at,
                replay_dir=turn_root / "universal_intake",
            )
            if universal_intake_capture.get("fail_closed") is True:
                raise FailClosedRuntimeError(
                    universal_intake_capture.get("failure_reason") or "universal intake failed closed"
                )
            _emit_interactive_conversation_cognition_progress(
                binding_capture=progress_binding_capture,
                snapshot_at=created_at,
                output_writer=turn_progress_buffer.append,
            )
            if (
                pending_governed_development_bridge is not None
                and pending_governed_development_bridge_restored
                and human_decision == APPROVE
                and not _is_explicit_governed_development_resume_approval(
                    human_prompt,
                    pending_governed_development_bridge,
                )
            ):
                safe_resume_capture = _record_safe_governed_development_resume_presentation(
                    turn_root=turn_root,
                    pending_proposal_capture=pending_governed_development_bridge,
                    human_prompt=human_prompt,
                    created_at=created_at,
                )
                pending_governed_development_resume_presented = True
                output_writer(_render_safe_governed_development_resume_summary(safe_resume_capture))
                turns.append(
                    _interactive_acli_governed_development_bridge_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        bridge_capture=pending_governed_development_bridge,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif pending_governed_development_bridge is not None and human_decision in {
                APPROVE,
                REJECT,
                REQUEST_MODIFICATION,
            }:
                if pending_governed_development_bridge_restored and human_decision == APPROVE:
                    if not (
                        pending_governed_development_resume_presented
                        or _is_explicit_governed_development_resume_approval(
                            human_prompt,
                            pending_governed_development_bridge,
                        )
                    ):
                        raise FailClosedRuntimeError(
                            "ACLI safe approval resume failed closed: restored proposal must be re-presented "
                            "before execution approval"
                        )
                bridge_decision = "APPROVED" if human_decision == APPROVE else human_decision
                bridge_capture = approve_and_execute_acli_governed_development(
                    bridge_id=f"{prompt_id}:ACLI-GOVERNED-DEVELOPMENT-BRIDGE",
                    pending_proposal_capture=pending_governed_development_bridge,
                    decision=bridge_decision,
                    decided_by=args.operator_context or "HUMAN_OPERATOR",
                    decided_at=created_at,
                    workspace_root=args.workspace,
                    replay_dir=turn_root / "acli_governed_development_execution_bridge",
                )
                if bridge_capture.get("bridge_status") == ACLI_GOVERNED_DEVELOPMENT_EXECUTION_COMPLETED:
                    pending_governed_development_bridge = None
                    pending_governed_development_bridge_restored = False
                    pending_governed_development_resume_presented = False
                    output_writer(render_acli_governed_development_bridge_summary(bridge_capture))
                elif bridge_capture.get("bridge_status") in {
                    "REJECTED",
                    ACLI_GOVERNED_DEVELOPMENT_MODIFICATION_REQUESTED,
                }:
                    pending_governed_development_bridge = None
                    pending_governed_development_bridge_restored = False
                    pending_governed_development_resume_presented = False
                    output_writer(render_acli_governed_development_bridge_summary(bridge_capture))
                else:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {bridge_capture.get('failure_reason')}")
                turns.append(
                    _interactive_acli_governed_development_bridge_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        bridge_capture=bridge_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif (
                pending_post_entry_continuation is not None
                and _post_entry_continuation_clarification_matches(human_prompt)
            ):
                pending_native_context = pending_post_entry_continuation["native_context_capture"]
                current_chain_id = pending_post_entry_continuation.get("current_chain_id") or current_chain_id
                latest_chain_id = pending_post_entry_continuation.get("latest_chain_id") or current_chain_id
                native_context_capture = deepcopy(pending_native_context)
                native_context_capture["post_entry_clarification_resolved"] = True
                native_context_capture["clarification_required"] = False
                native_context_capture["open_clarification_detected"] = False
                native_context_capture["current_chain_id"] = current_chain_id
                native_context_capture["latest_chain_id"] = latest_chain_id
                native_output = render_conversation_native_development_context_summary(native_context_capture)
                post_entry_gate_capture = evaluate_post_entry_continuation_gate(
                    gate_id=f"{prompt_id}:POST-ENTRY-CONTINUATION-GATE",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    workflow_id=CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
                    lifecycle_entry_status=str(native_context_capture.get("context_status") or ""),
                    provider_necessity_classification=native_context_capture.get(
                        "provider_necessity_classification"
                    ),
                    auto_continue_enabled=False,
                    created_at=created_at,
                    replay_dir=turn_root / "post_entry_continuation_gate",
                    lifecycle_replay_reference=native_context_capture.get("conversation_replay_reference"),
                )
                native_context_capture["post_entry_continuation_gate"] = post_entry_gate_capture
                native_context_capture["post_entry_continuation_gate_status"] = post_entry_gate_capture.get(
                    "gate_status"
                )
                native_context_capture["post_entry_continuation_gate_replay_reference"] = (
                    post_entry_gate_capture.get("post_entry_continuation_gate_replay_reference")
                )
                if post_entry_gate_capture.get("fail_closed") is True:
                    native_context_capture["fail_closed"] = True
                    native_context_capture["failure_reason"] = post_entry_gate_capture.get("failure_reason")
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                elif (
                    post_entry_gate_capture.get("gate_status") == POST_ENTRY_CONTINUATION_ALLOWED
                    and _post_context_continuation_should_run(
                        native_context_capture=native_context_capture,
                        auto_continue_enabled=False,
                        human_prompt=human_prompt,
                    )
                ):
                    post_context_continuation_capture = continue_context_assembled_to_ppp_routing(
                        continuation_id=f"{prompt_id}:POST-CONTEXT-CONTINUATION",
                        prompt_id=prompt_id,
                        human_prompt=pending_post_entry_continuation["original_human_prompt"],
                        provider_id=OPENAI_PROVIDER_ID,
                        created_at=created_at,
                        replay_dir=turn_root / "post_context_continuation",
                        registry=_post_context_continuation_provider_registry(),
                        adapter=_post_context_continuation_provider_adapter(),
                        governance_root="governance",
                        session_id=session_id,
                        turn_id=turn_id,
                        current_chain_id=current_chain_id,
                        latest_chain_id=latest_chain_id,
                        restored_native_context_capture=native_context_capture,
                    )
                    native_context_capture["post_context_continuation"] = post_context_continuation_capture
                    native_context_capture["ppp_route_status"] = post_context_continuation_capture.get(
                        "ppp_route_status"
                    )
                    native_context_capture["post_context_continuation_replay_reference"] = (
                        post_context_continuation_capture.get("post_context_continuation_replay_reference")
                    )
                    if post_context_continuation_capture.get("fail_closed") is True:
                        native_context_capture["fail_closed"] = True
                        native_context_capture["failure_reason"] = post_context_continuation_capture.get(
                            "failure_reason"
                        )
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                    else:
                        try:
                            worker_request_continuation = _continue_ppp_handoff_to_worker_request(
                                prompt_id=prompt_id,
                                post_context_continuation_capture=post_context_continuation_capture,
                                created_at=created_at,
                                replay_dir=turn_root / "certified_development_continuation",
                            )
                            native_context_capture["certified_development_continuation"] = (
                                worker_request_continuation
                            )
                        except FailClosedRuntimeError as exc:
                            native_context_capture["fail_closed"] = True
                            native_context_capture["failure_reason"] = str(exc)
                            failed_turns += 1
                            output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                        else:
                            pending_post_entry_continuation = None
                            native_output += "\n" + _post_context_continuation_output(
                                post_context_continuation_capture
                            )
                            native_output += "\n" + _worker_lifecycle_continuation_output(
                                worker_request_continuation
                            )
                if native_context_capture.get("fail_closed") is not True:
                    output_writer(native_output)
                turns.append(
                    _interactive_native_development_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        native_context_capture=native_context_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif active_clarification_reply_mismatch_detected:
                failed_turns += 1
                failure_reason = (
                    "clarification continuity failed closed: reply does not match active clarification scope"
                )
                output_writer(f"FAILED_CLOSED: {failure_reason}")
                turns.append(
                    _interactive_failed_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        failure_reason=failure_reason,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif active_clarification_reply_detected:
                active_state = clarification_reply_gate_capture.get("active_clarification") or {}
                if active_state.get("originating_workflow_id") == CONVERSATIONAL_HUMAN_INTENT_CLARIFICATION_INTAKE:
                    human_intent_continuity_capture = continue_human_intent_clarification_to_workflow(
                        continuity_id=f"{prompt_id}:HUMAN-INTENT-CLARIFICATION-CONTINUITY",
                        session_root=session_root,
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        clarification_response=human_prompt,
                        current_chain_id=current_chain_id,
                        created_at=created_at,
                        replay_dir=turn_root / "human_intent_clarification_continuity",
                    )
                    current_chain_id = human_intent_continuity_capture.get("current_chain_id") or current_chain_id
                    latest_chain_id = human_intent_continuity_capture.get("latest_chain_id") or current_chain_id
                    if human_intent_continuity_capture.get("fail_closed") is True:
                        failed_turns += 1
                        output_writer(
                            f"FAILED_CLOSED: {human_intent_continuity_capture.get('failure_reason')}"
                        )
                    else:
                        if human_intent_continuity_capture.get("workflow_id") == CONVERSATIONAL_OCS_LLM_COGNITION:
                            human_intent_continuity_capture["post_clarification_ocs_execution_deferred"] = True
                            human_intent_continuity_capture["post_clarification_ocs_replay_reference"] = None
                            human_intent_continuity_capture["post_clarification_ocs_llm_cognition"] = {}
                            human_intent_continuity_capture["provider_invoked"] = False
                            human_intent_continuity_capture["provider_ids"] = []
                            human_intent_continuity_capture["real_llm_provider_used_by_ocs"] = False
                            human_intent_continuity_capture["live_provider_response_received"] = False
                        output_writer(
                            render_human_intent_clarification_continuity_summary(
                                human_intent_continuity_capture
                            )
                        )
                    turns.append(
                        _interactive_human_intent_clarification_continuity_turn_summary(
                            turn_id=turn_id,
                            prompt_id=prompt_id,
                            router_capture=router_capture,
                            continuity_capture=human_intent_continuity_capture,
                            source_router_replay_reference=str(turn_root / "source_router"),
                        )
                    )
                else:
                    clarification_continuity_capture = run_clarification_continuity(
                        continuity_id=f"{prompt_id}:CLARIFICATION-CONTINUITY",
                        session_root=session_root,
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        operator_reply=human_prompt,
                        current_chain_id=current_chain_id,
                        created_at=created_at,
                        replay_dir=turn_root / "clarification_continuity",
                    )
                    current_chain_id = clarification_continuity_capture.get("current_chain_id") or current_chain_id
                    latest_chain_id = clarification_continuity_capture.get("latest_chain_id") or current_chain_id
                    if clarification_continuity_capture.get("fail_closed") is True:
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {clarification_continuity_capture.get('failure_reason')}")
                    else:
                        handoff_review_capture = review_clarified_domain_intent(
                            review_id=f"{prompt_id}:CLARIFIED-DOMAIN-HANDOFF-REVIEW",
                            clarification_continuity_replay_reference=clarification_continuity_capture[
                                "clarification_continuity_replay_reference"
                            ],
                            review_decision=CLARIFIED_DOMAIN_WORKER_BINDING_APPROVED,
                            reviewed_by="AIGOL_GOVERNANCE_REVIEW",
                            created_at=created_at,
                            replay_dir=turn_root / "clarified_domain_handoff_review",
                        )
                        clarification_continuity_capture["handoff_review"] = handoff_review_capture
                        if handoff_review_capture.get("fail_closed") is True:
                            failed_turns += 1
                            clarification_continuity_capture["fail_closed"] = True
                            clarification_continuity_capture["failure_reason"] = handoff_review_capture.get(
                                "failure_reason"
                            )
                            output_writer(f"FAILED_CLOSED: {clarification_continuity_capture.get('failure_reason')}")
                        else:
                            output_writer(
                                "\n\n".join(
                                    [
                                        render_clarification_continuity_summary(clarification_continuity_capture),
                                        render_clarified_domain_intent_handoff_review_summary(handoff_review_capture),
                                    ]
                                )
                            )
                    turns.append(
                        _interactive_clarification_continuity_turn_summary(
                            turn_id=turn_id,
                            prompt_id=prompt_id,
                            router_capture=router_capture,
                            clarification_continuity_capture=clarification_continuity_capture,
                            source_router_replay_reference=str(turn_root / "source_router"),
                        )
                    )
            elif domain_approval_entry_detected:
                try:
                    latest_review = find_latest_domain_handoff_review(
                        session_root=session_root,
                        domain_name=domain_approval_entry_intent["domain_name"],
                    )
                    domain_approval_capture = bind_domain_handoff_review_approval(
                        approval_entry_id=f"{prompt_id}:DOMAIN-APPROVAL-BINDING",
                        handoff_review_replay_reference=latest_review["handoff_review_replay_reference"],
                        operator_prompt=human_prompt,
                        approved_domain=domain_approval_entry_intent["domain_name"],
                        approving_actor=args.operator_context or "HUMAN_OPERATOR",
                        approved_at=created_at,
                        replay_dir=turn_root / "domain_approval_binding",
                        latest_handoff_review_replay_reference=latest_review["handoff_review_replay_reference"],
                    )
                except Exception:
                    domain_approval_capture = bind_domain_handoff_review_approval(
                        approval_entry_id=f"{prompt_id}:DOMAIN-APPROVAL-BINDING",
                        handoff_review_replay_reference="MISSING_HANDOFF_REVIEW",
                        operator_prompt=human_prompt,
                        approved_domain=domain_approval_entry_intent.get("domain_name") or "UNKNOWN_DOMAIN",
                        approving_actor=args.operator_context or "HUMAN_OPERATOR",
                        approved_at=created_at,
                        replay_dir=turn_root / "domain_approval_binding",
                    )
                current_chain_id = domain_approval_capture.get("canonical_chain_id") or current_chain_id
                latest_chain_id = current_chain_id
                if domain_approval_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {domain_approval_capture.get('failure_reason')}")
                else:
                    output_writer(render_domain_handoff_review_approval_binding_summary(domain_approval_capture))
                turns.append(
                    _interactive_domain_approval_binding_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        domain_approval_capture=domain_approval_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif pending_domain_proposal is not None and domain_proposal_decision is not None:
                domain_review_capture = review_domain_proposal(
                    review_id=f"{prompt_id}:DOMAIN-PROPOSAL-REVIEW",
                    domain_proposal_artifact=pending_domain_proposal["domain_proposal_artifact"],
                    decision=domain_proposal_decision,
                    decision_reason=f"Operator selected {domain_proposal_decision}.",
                    reviewed_by=args.operator_context or "HUMAN_OPERATOR",
                    reviewed_at=created_at,
                    human_approval_reference=prompt_id,
                    replay_dir=turn_root / "domain_proposal_review",
                )
                if domain_review_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {domain_review_capture.get('failure_reason')}")
                else:
                    review = domain_review_capture.get("domain_review_decision_artifact")
                    if isinstance(review, dict):
                        current_chain_id = review.get("canonical_chain_id") or current_chain_id
                        latest_chain_id = current_chain_id
                    pending_domain_proposal = None
                    pending_domain_review = (
                        domain_review_capture
                        if domain_review_capture.get("domain_candidate_created") is True
                        else None
                    )
                    output_writer(_render_domain_proposal_review_summary(domain_review_capture))
                turns.append(
                    _interactive_domain_proposal_review_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        domain_review_capture=domain_review_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif pending_domain_review is not None and _is_domain_candidate_continuation_prompt(human_prompt):
                continuation_capture = _record_domain_candidate_continuation_boundary(
                    boundary_id=f"{prompt_id}:DOMAIN-CANDIDATE-CONTINUATION-BOUNDARY",
                    domain_review_capture=pending_domain_review,
                    operator_prompt=human_prompt,
                    created_at=created_at,
                    replay_dir=turn_root / "domain_candidate_continuation_boundary",
                )
                current_chain_id = (
                    continuation_capture.get("domain_candidate_continuation_boundary_artifact", {}).get(
                        "canonical_chain_id"
                    )
                    or current_chain_id
                )
                latest_chain_id = current_chain_id
                pending_domain_review = None
                output_writer(_render_domain_candidate_continuation_boundary_summary(continuation_capture))
                turns.append(
                    _interactive_domain_candidate_continuation_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        continuation_capture=continuation_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif pending_approval_required is not None and human_decision in {REJECT, REQUEST_MODIFICATION}:
                human_decision_capture = record_human_decision(
                    human_decision_id=f"{prompt_id}:HUMAN-DECISION",
                    approval_required_artifact=pending_approval_required[
                        "conversation_to_ppp_handoff_execution_artifact"
                    ],
                    decision=human_decision,
                    decision_reason=f"Operator selected {human_decision}.",
                    decided_by=args.operator_context or "HUMAN_OPERATOR",
                    decided_at=created_at,
                    replay_dir=turn_root / "human_decision",
                )
                if human_decision_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {human_decision_capture.get('failure_reason')}")
                else:
                    current_chain_id = human_decision_capture.get("chain_id") or current_chain_id
                    latest_chain_id = current_chain_id
                    pending_approval_required = None
                    output_writer(render_human_decision_summary(human_decision_capture))
                turns.append(
                    _interactive_human_decision_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        human_decision_capture=human_decision_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif human_decision == APPROVE and pending_approval_required is not None:
                human_decision_capture = record_human_decision(
                    human_decision_id=f"{prompt_id}:HUMAN-DECISION",
                    approval_required_artifact=pending_approval_required[
                        "conversation_to_ppp_handoff_execution_artifact"
                    ],
                    decision=human_decision,
                    decision_reason="Operator selected APPROVE.",
                    decided_by=args.operator_context or "HUMAN_OPERATOR",
                    decided_at=created_at,
                    replay_dir=turn_root / "human_decision",
                )
                if human_decision_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {human_decision_capture.get('failure_reason')}")
                    turns.append(
                        _interactive_human_decision_turn_summary(
                            turn_id=turn_id,
                            prompt_id=prompt_id,
                            router_capture=router_capture,
                            human_decision_capture=human_decision_capture,
                            source_router_replay_reference=str(turn_root / "source_router"),
                        )
                    )
                    continue
                approval_request = pending_approval_required["conversation_to_ppp_handoff_execution_artifact"][
                    "approval_resume_packet"
                ]["approval_request_artifact"]
                human_approval = create_human_implementation_approval(
                    approval_id=f"{prompt_id}:HUMAN-APPROVAL",
                    approval_request_artifact=approval_request,
                    approving_actor=args.operator_context or "HUMAN_OPERATOR",
                    approval_timestamp=created_at,
                )
                approval_resume_capture = resume_implementation_after_approval(
                    resume_id=f"{prompt_id}:IMPLEMENTATION-APPROVAL-RESUME",
                    approval_required_replay_reference=pending_approval_required[
                        "conversation_to_ppp_handoff_execution_replay_reference"
                    ],
                    human_approval_artifact=human_approval,
                    created_at=created_at,
                    replay_dir=turn_root / "implementation_approval_resume",
                )
                fail_closed = approval_resume_capture.get("fail_closed") is True
                if fail_closed:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {approval_resume_capture.get('failure_reason')}")
                else:
                    current_chain_id = approval_resume_capture.get("chain_id") or current_chain_id
                    latest_chain_id = current_chain_id
                    handoff_visibility_capture = create_implementation_handoff_visibility_summary(
                        visibility_id=f"{prompt_id}:IMPLEMENTATION-HANDOFF-VISIBILITY",
                        handoff_replay_reference=approval_resume_capture["implementation_handoff_replay_reference"],
                        approval_status="APPROVED",
                        created_at=created_at,
                        replay_dir=turn_root / "implementation_handoff_visibility",
                    )
                    if handoff_visibility_capture.get("fail_closed") is True:
                        failed_turns += 1
                        approval_resume_capture["fail_closed"] = True
                        approval_resume_capture["failure_reason"] = handoff_visibility_capture.get("failure_reason")
                        output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                    else:
                        approval_resume_capture["implementation_handoff_visibility"] = handoff_visibility_capture
                        dry_run_capture = prepare_governed_implementation_dry_run(
                            dry_run_id=f"{prompt_id}:GOVERNED-IMPLEMENTATION-DRY-RUN",
                            handoff_replay_reference=approval_resume_capture["implementation_handoff_replay_reference"],
                            handoff_visibility_artifact=handoff_visibility_capture[
                                "implementation_handoff_visibility_artifact"
                            ],
                            upstream_lineage_artifact=approval_resume_capture[
                                "implementation_approval_resume_artifact"
                            ],
                            created_at=created_at,
                            replay_dir=turn_root / "governed_implementation_dry_run",
                        )
                        approval_resume_capture["governed_implementation_dry_run"] = dry_run_capture
                        if dry_run_capture.get("fail_closed") is True:
                            failed_turns += 1
                            approval_resume_capture["fail_closed"] = True
                            approval_resume_capture["failure_reason"] = dry_run_capture.get("failure_reason")
                            output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                        else:
                            authorization_capture = authorize_execution_ready(
                                authorization_id=f"{prompt_id}:EXECUTION-AUTHORIZATION",
                                execution_ready_replay_reference=dry_run_capture[
                                    "governed_implementation_dry_run_replay_reference"
                                ],
                                authorizing_actor="AIGOL_GOVERNANCE",
                                authorized_at=created_at,
                                replay_dir=turn_root / "execution_authorization",
                            )
                            approval_resume_capture["execution_authorization"] = authorization_capture
                            if authorization_capture.get("fail_closed") is True:
                                failed_turns += 1
                                approval_resume_capture["fail_closed"] = True
                                approval_resume_capture["failure_reason"] = authorization_capture.get("failure_reason")
                                output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                            else:
                                invocation_request_capture = create_worker_invocation_request(
                                    invocation_request_id=f"{prompt_id}:WORKER-INVOCATION-REQUEST",
                                    execution_authorization_replay_reference=authorization_capture[
                                        "execution_authorization_replay_reference"
                                    ],
                                    requested_by="AIGOL_GOVERNANCE",
                                    requested_at=created_at,
                                    replay_dir=turn_root / "worker_invocation_request",
                                )
                                approval_resume_capture["worker_invocation_request"] = invocation_request_capture
                                if invocation_request_capture.get("fail_closed") is True:
                                    failed_turns += 1
                                    approval_resume_capture["fail_closed"] = True
                                    approval_resume_capture["failure_reason"] = invocation_request_capture.get(
                                        "failure_reason"
                                    )
                                    output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                else:
                                    assignment_capture = assign_worker_from_invocation_request(
                                        worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
                                        worker_invocation_request_artifact=invocation_request_capture[
                                            "worker_invocation_request_artifact"
                                        ],
                                        worker_invocation_request_replay_reference=invocation_request_capture[
                                            "worker_invocation_request_replay_reference"
                                        ],
                                        worker_registry_artifacts=default_worker_registry_for_request(
                                            invocation_request_capture["worker_invocation_request_artifact"],
                                            created_at=created_at,
                                        ),
                                        assigned_by="AIGOL_GOVERNANCE",
                                        assigned_at=created_at,
                                        replay_dir=turn_root / "worker_assignment",
                                    )
                                    approval_resume_capture["worker_assignment"] = assignment_capture
                                    if assignment_capture.get("fail_closed") is True:
                                        failed_turns += 1
                                        approval_resume_capture["fail_closed"] = True
                                        approval_resume_capture["failure_reason"] = assignment_capture.get(
                                            "failure_reason"
                                        )
                                        output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                    else:
                                        dispatch_capture = dispatch_assigned_worker(
                                            worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
                                            worker_assignment_artifact=assignment_capture[
                                                "worker_assignment_artifact"
                                            ],
                                            worker_assignment_replay_reference=assignment_capture[
                                                "worker_assignment_replay_reference"
                                            ],
                                            dispatched_by="AIGOL_GOVERNANCE",
                                            dispatched_at=created_at,
                                            replay_dir=turn_root / "worker_dispatch",
                                        )
                                        approval_resume_capture["worker_dispatch"] = dispatch_capture
                                        if dispatch_capture.get("fail_closed") is True:
                                            failed_turns += 1
                                            approval_resume_capture["fail_closed"] = True
                                            approval_resume_capture["failure_reason"] = dispatch_capture.get(
                                                "failure_reason"
                                            )
                                            output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                        else:
                                            invocation_capture = invoke_dispatched_worker(
                                                worker_invocation_id=f"{prompt_id}:WORKER-INVOCATION",
                                                worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
                                                worker_dispatch_replay_reference=dispatch_capture[
                                                    "worker_dispatch_replay_reference"
                                                ],
                                                invoked_by="AIGOL_GOVERNANCE",
                                                invoked_at=created_at,
                                                replay_dir=turn_root / "worker_invocation",
                                            )
                                            approval_resume_capture["worker_invocation"] = invocation_capture
                                            if invocation_capture.get("fail_closed") is True:
                                                failed_turns += 1
                                                approval_resume_capture["fail_closed"] = True
                                                approval_resume_capture["failure_reason"] = invocation_capture.get(
                                                    "failure_reason"
                                                )
                                                output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                            else:
                                                execution_capture = _record_authorized_worker_execution_start(
                                                    execution_id=f"{prompt_id}:EXECUTION",
                                                    invocation_artifact=invocation_capture[
                                                        "worker_invocation_artifact"
                                                    ],
                                                    invocation_replay=invocation_capture["invocation_result_artifact"],
                                                    dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
                                                    worker_assignment_artifact=assignment_capture[
                                                        "worker_assignment_artifact"
                                                    ],
                                                    canonical_chain_id=invocation_capture[
                                                        "worker_invocation_artifact"
                                                    ]["chain_id"],
                                                    worker_reference=invocation_capture["worker_id"],
                                                    worker_role=invocation_capture["worker_role"],
                                                    started_at=created_at,
                                                    replay_dir=turn_root / "execution_runtime",
                                                )
                                                approval_resume_capture["execution_runtime"] = execution_capture
                                                result_capture = capture_worker_result(
                                                    worker_result_capture_id=f"{prompt_id}:WORKER-RESULT-CAPTURE",
                                                    worker_invocation_artifact=invocation_capture[
                                                        "worker_invocation_artifact"
                                                    ],
                                                    worker_invocation_replay_reference=invocation_capture[
                                                        "worker_invocation_replay_reference"
                                                    ],
                                                    worker_output=default_worker_output_for_invocation(
                                                        invocation_capture["worker_invocation_artifact"],
                                                        captured_at=created_at,
                                                    ),
                                                    captured_by="AIGOL_GOVERNANCE",
                                                    captured_at=created_at,
                                                    replay_dir=turn_root / "worker_result_capture",
                                                    execution_artifact=execution_capture["execution_artifact"],
                                                    execution_replay=execution_capture["execution_replay"],
                                                    execution_replay_reference=str(turn_root / "execution_runtime"),
                                                )
                                                approval_resume_capture["worker_result_capture"] = result_capture
                                                if result_capture.get("fail_closed") is True:
                                                    failed_turns += 1
                                                    approval_resume_capture["fail_closed"] = True
                                                    approval_resume_capture["failure_reason"] = result_capture.get(
                                                        "failure_reason"
                                                    )
                                                    output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                                else:
                                                    validation_capture = validate_worker_result(
                                                        worker_result_validation_id=f"{prompt_id}:WORKER-RESULT-VALIDATION",
                                                        worker_result_capture_artifact=result_capture[
                                                            "worker_result_capture_artifact"
                                                        ],
                                                        worker_result_capture_replay_reference=result_capture[
                                                            "worker_result_capture_replay_reference"
                                                        ],
                                                        validated_by="AIGOL_GOVERNANCE",
                                                        validated_at=created_at,
                                                        replay_dir=turn_root / "worker_result_validation",
                                                    )
                                                    approval_resume_capture["worker_result_validation"] = validation_capture
                                                    if validation_capture.get("fail_closed") is True:
                                                        failed_turns += 1
                                                        approval_resume_capture["fail_closed"] = True
                                                        approval_resume_capture["failure_reason"] = validation_capture.get(
                                                            "failure_reason"
                                                        )
                                                        output_writer(f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}")
                                                    else:
                                                        executable_bundle_capture = _bind_supported_executable_domain_bundle(
                                                            prompt_id=prompt_id,
                                                            validation_capture=validation_capture,
                                                            workspace_root=args.workspace,
                                                            created_at=created_at,
                                                            replay_dir=turn_root / "executable_domain_bundle",
                                                        )
                                                        if executable_bundle_capture is not None:
                                                            approval_resume_capture["executable_bundle"] = executable_bundle_capture
                                                        if executable_bundle_capture is not None and executable_bundle_capture.get(
                                                            "fail_closed"
                                                        ) is True:
                                                            failed_turns += 1
                                                            approval_resume_capture["fail_closed"] = True
                                                            approval_resume_capture["failure_reason"] = executable_bundle_capture.get(
                                                                "failure_reason"
                                                            )
                                                            output_writer(
                                                                f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}"
                                                            )
                                                        if not (
                                                            executable_bundle_capture is not None
                                                            and executable_bundle_capture.get("fail_closed") is True
                                                        ):
                                                            review_capture = review_validated_worker_result(
                                                                post_execution_replay_review_id=f"{prompt_id}:POST-EXECUTION-REPLAY-REVIEW",
                                                                worker_result_validation_artifact=validation_capture[
                                                                    "worker_result_validation_artifact"
                                                                ],
                                                                worker_result_validation_replay_reference=validation_capture[
                                                                    "worker_result_validation_replay_reference"
                                                                ],
                                                                executable_bundle_artifact=(
                                                                    executable_bundle_capture["executable_domain_bundle_artifact"]
                                                                    if executable_bundle_capture
                                                                    else None
                                                                ),
                                                                executable_bundle_replay_reference=(
                                                                    executable_bundle_capture["executable_bundle_replay_reference"]
                                                                    if executable_bundle_capture
                                                                    else None
                                                                ),
                                                                reviewed_by="AIGOL_GOVERNANCE",
                                                                reviewed_at=created_at,
                                                                replay_dir=turn_root / "post_execution_replay_review",
                                                            )
                                                            approval_resume_capture["post_execution_replay_review"] = review_capture
                                                            if review_capture.get("fail_closed") is True:
                                                                failed_turns += 1
                                                                approval_resume_capture["fail_closed"] = True
                                                                approval_resume_capture["failure_reason"] = review_capture.get(
                                                                    "failure_reason"
                                                                )
                                                                output_writer(
                                                                    f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}"
                                                                )
                                                            else:
                                                                termination_capture = terminate_reviewed_operation(
                                                                    governed_termination_id=f"{prompt_id}:GOVERNED-TERMINATION",
                                                                    post_execution_replay_review_artifact=review_capture[
                                                                        "post_execution_replay_review_artifact"
                                                                    ],
                                                                    post_execution_replay_review_replay_reference=review_capture[
                                                                        "post_execution_replay_review_replay_reference"
                                                                    ],
                                                                    terminated_by="AIGOL_GOVERNANCE",
                                                                    terminated_at=created_at,
                                                                    replay_dir=turn_root / "governed_termination",
                                                                )
                                                                approval_resume_capture["governed_termination"] = termination_capture
                                                                if termination_capture.get("fail_closed") is True:
                                                                    failed_turns += 1
                                                                    approval_resume_capture["fail_closed"] = True
                                                                    approval_resume_capture["failure_reason"] = termination_capture.get(
                                                                        "failure_reason"
                                                                    )
                                                                    output_writer(
                                                                        f"FAILED_CLOSED: {approval_resume_capture['failure_reason']}"
                                                                    )
                                                                else:
                                                                    pending_approval_required = None
                                                                    output_writer(
                                                                        render_implementation_approval_resume_summary(approval_resume_capture)
                                                                        + "\n"
                                                                        + render_implementation_handoff_visibility_summary(handoff_visibility_capture)
                                                                        + "\n"
                                                                        + render_governed_implementation_dry_run_summary(dry_run_capture)
                                                                        + "\n"
                                                                        + render_execution_authorization_summary(authorization_capture)
                                                                        + "\n"
                                                                        + render_worker_invocation_request_summary(invocation_request_capture)
                                                                        + "\n"
                                                                        + render_worker_assignment_summary(assignment_capture)
                                                                        + "\n"
                                                                        + render_worker_dispatch_summary(dispatch_capture)
                                                                        + "\n"
                                                                        + render_worker_invocation_summary(invocation_capture)
                                                                        + "\n"
                                                                        + _render_execution_runtime_summary(execution_capture)
                                                                        + "\n"
                                                                        + render_worker_result_capture_summary(result_capture)
                                                                        + "\n"
                                                                        + render_worker_result_validation_summary(validation_capture)
                                                                        + "\n"
                                                                        + (
                                                                            render_executable_domain_bundle_summary(executable_bundle_capture)
                                                                            + "\n"
                                                                            if executable_bundle_capture
                                                                            else ""
                                                                        )
                                                                        + render_post_execution_replay_review_summary(review_capture)
                                                                        + "\n"
                                                                        + render_governed_termination_summary(termination_capture)
                                                                    )
                turns.append(
                    _interactive_approval_resume_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        approval_resume_capture=approval_resume_capture,
                        human_decision_capture=human_decision_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif recommendation_continuity_artifact is not None and _is_recommendation_decision_prompt(human_prompt):
                recommendation_decision = _recommendation_decision_from_prompt(human_prompt)
                recommendation_approval_capture = record_recommendation_approval(
                    approval_id=f"{prompt_id}:RECOMMENDATION-APPROVAL",
                    recommendation_continuity_artifact=recommendation_continuity_artifact,
                    operator_decision=recommendation_decision,
                    approval_timestamp=created_at,
                    replay_dir=turn_root / "recommendation_approval",
                )
                if recommendation_approval_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {recommendation_approval_capture.get('failure_reason')}")
                else:
                    recommendation_approval_artifact = recommendation_approval_capture[
                        "recommendation_approval_artifact"
                    ]
                    output_writer(render_recommendation_approval_summary(recommendation_approval_capture))
                    if recommendation_decision in {RECOMMENDATION_REJECT, RECOMMENDATION_IGNORE}:
                        recommendation_continuity_artifact = None
                        recommendation_approval_artifact = None
                turns.append(
                    _interactive_recommendation_approval_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        recommendation_approval_capture=recommendation_approval_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif (
                recommendation_continuity_artifact is not None
                and recommendation_approval_artifact is not None
                and is_recommendation_followup_prompt(human_prompt)
            ):
                recommendation_followup_capture = create_recommendation_followup(
                    followup_id=f"{prompt_id}:RECOMMENDATION-FOLLOWUP",
                    recommendation_continuity_artifact=recommendation_continuity_artifact,
                    recommendation_approval_artifact=recommendation_approval_artifact,
                    human_prompt=human_prompt,
                    created_at=created_at,
                    replay_dir=turn_root / "recommendation_followup",
                )
                if recommendation_followup_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {recommendation_followup_capture.get('failure_reason')}")
                else:
                    output_writer(render_recommendation_followup_summary(recommendation_followup_capture))
                turns.append(
                    _interactive_recommendation_followup_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        recommendation_followup_capture=recommendation_followup_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif conversational_routing_capture is not None and conversational_routing_capture.get("fail_closed") is True:
                failed_turns += 1
                workflow_capture = _conversational_workflow_capture(
                    prompt_id=prompt_id,
                    workflow_id=NO_CERTIFIED_WORKFLOW_MATCHED,
                    response_text="",
                    existing_result={},
                    response_status="FAILED_CLOSED",
                    fail_closed=True,
                    failure_reason=conversational_routing_capture.get("failure_reason")
                    or "conversational routing failed closed",
                )
                output_writer(f"FAILED_CLOSED: {workflow_capture.get('failure_reason')}")
                turns.append(
                    _interactive_conversational_cli_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        workflow_capture=workflow_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id in {
                CONVERSATIONAL_SHOW_LATEST_REPLAY_CHAIN,
                CONVERSATIONAL_REVIEW_LATEST_AUDIT,
                CONVERSATIONAL_IMPROVE_PROVIDER_LAYER,
                CONVERSATIONAL_SHOW_STATUS,
                CONVERSATIONAL_SHOW_DASHBOARD,
                CONVERSATIONAL_DOMAIN_LIFECYCLE_GOVERNANCE,
                CONVERSATIONAL_CAPABILITY_LIFECYCLE_GOVERNANCE,
                CONVERSATIONAL_PROPOSAL_RUNTIME,
                CONVERSATIONAL_IMPROVEMENT_PROPOSAL_RUNTIME,
                CONVERSATIONAL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
                CONVERSATIONAL_IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
                CONVERSATIONAL_AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
                CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
                CONVERSATIONAL_AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
                CONVERSATIONAL_HUMAN_INTENT_CLARIFICATION_INTAKE,
            }:
                workflow_capture = _run_conversational_cli_selected_readonly_workflow(
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    routing_capture=conversational_routing_capture,
                    runtime_root=args.runtime_root,
                    turn_root=turn_root,
                    created_at=created_at,
                )
                if workflow_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {workflow_capture.get('failure_reason')}")
                else:
                    output_writer(workflow_capture.get("response_text", ""))
                turns.append(
                    _interactive_conversational_cli_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        workflow_capture=workflow_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE:
                execution_ready_entry_intent = detect_domain_execution_ready_entry_intent(human_prompt)
                try:
                    latest_approval_binding = find_latest_domain_approval_binding(
                        session_root=session_root,
                        domain_name=execution_ready_entry_intent["domain_name"],
                    )
                    execution_ready_bridge_capture = bridge_domain_approval_entry_to_execution_ready(
                        bridge_id=f"{prompt_id}:DOMAIN-EXECUTION-READY-BRIDGE",
                        domain_approval_binding_replay_reference=latest_approval_binding[
                            "domain_approval_binding_replay_reference"
                        ],
                        approved_domain=execution_ready_entry_intent["domain_name"],
                        created_at=created_at,
                        replay_dir=turn_root / "domain_execution_ready_bridge",
                    )
                except Exception:
                    execution_ready_bridge_capture = bridge_domain_approval_entry_to_execution_ready(
                        bridge_id=f"{prompt_id}:DOMAIN-EXECUTION-READY-BRIDGE",
                        domain_approval_binding_replay_reference="MISSING_DOMAIN_APPROVAL_BINDING",
                        approved_domain=execution_ready_entry_intent.get("domain_name") or "UNKNOWN_DOMAIN",
                        created_at=created_at,
                        replay_dir=turn_root / "domain_execution_ready_bridge",
                    )
                if execution_ready_bridge_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {execution_ready_bridge_capture.get('failure_reason')}")
                else:
                    output_writer(render_domain_execution_ready_bridge_summary(execution_ready_bridge_capture))
                turns.append(
                    _interactive_domain_execution_ready_bridge_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        execution_ready_bridge_capture=execution_ready_bridge_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_EXECUTION_AUTHORIZATION:
                execution_authorization_entry_intent = detect_domain_execution_authorization_entry_intent(human_prompt)
                try:
                    latest_execution_ready_bridge = find_latest_domain_execution_ready_bridge(
                        session_root=session_root,
                        domain_name=execution_authorization_entry_intent["domain_name"],
                    )
                    execution_authorization_capture = authorize_execution_ready(
                        authorization_id=f"{prompt_id}:EXECUTION-AUTHORIZATION",
                        execution_ready_replay_reference=latest_execution_ready_bridge[
                            "execution_ready_replay_reference"
                        ],
                        authorizing_actor=args.operator_context or "HUMAN_OPERATOR",
                        authorized_at=created_at,
                        replay_dir=turn_root / "execution_authorization",
                    )
                except Exception:
                    execution_authorization_capture = authorize_execution_ready(
                        authorization_id=f"{prompt_id}:EXECUTION-AUTHORIZATION",
                        execution_ready_replay_reference="MISSING_EXECUTION_READY_REPLAY",
                        authorizing_actor=args.operator_context or "HUMAN_OPERATOR",
                        authorized_at=created_at,
                        replay_dir=turn_root / "execution_authorization",
                    )
                if execution_authorization_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {execution_authorization_capture.get('failure_reason')}")
                else:
                    output_writer(render_execution_authorization_summary(execution_authorization_capture))
                turns.append(
                    _interactive_domain_execution_authorization_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        execution_authorization_capture=execution_authorization_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_REQUEST:
                worker_request_entry_intent = detect_domain_worker_request_entry_intent(human_prompt)
                try:
                    latest_execution_authorization = find_latest_domain_execution_authorization(
                        session_root=session_root,
                        domain_name=worker_request_entry_intent["domain_name"],
                    )
                    worker_request_capture = create_worker_invocation_request(
                        invocation_request_id=f"{prompt_id}:WORKER-INVOCATION-REQUEST",
                        execution_authorization_replay_reference=latest_execution_authorization[
                            "execution_authorization_replay_reference"
                        ],
                        requested_by=args.operator_context or "HUMAN_OPERATOR",
                        requested_at=created_at,
                        replay_dir=turn_root / "worker_invocation_request",
                    )
                except Exception:
                    worker_request_capture = create_worker_invocation_request(
                        invocation_request_id=f"{prompt_id}:WORKER-INVOCATION-REQUEST",
                        execution_authorization_replay_reference="MISSING_EXECUTION_AUTHORIZATION_REPLAY",
                        requested_by=args.operator_context or "HUMAN_OPERATOR",
                        requested_at=created_at,
                        replay_dir=turn_root / "worker_invocation_request",
                    )
                if worker_request_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {worker_request_capture.get('failure_reason')}")
                else:
                    output_writer(render_worker_invocation_request_summary(worker_request_capture))
                turns.append(
                    _interactive_domain_worker_request_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        worker_request_capture=worker_request_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_ASSIGNMENT:
                worker_assignment_entry_intent = detect_domain_worker_assignment_entry_intent(human_prompt)
                try:
                    latest_worker_request = find_latest_domain_worker_invocation_request(
                        session_root=session_root,
                        domain_name=worker_assignment_entry_intent["domain_name"],
                    )
                    worker_assignment_capture = assign_worker_from_invocation_request(
                        worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
                        worker_invocation_request_artifact=latest_worker_request[
                            "worker_invocation_request_artifact"
                        ],
                        worker_invocation_request_replay_reference=latest_worker_request[
                            "worker_invocation_request_replay_reference"
                        ],
                        worker_registry_artifacts=default_worker_registry_for_request(
                            latest_worker_request["worker_invocation_request_artifact"],
                            created_at=created_at,
                        ),
                        assigned_by=args.operator_context or "HUMAN_OPERATOR",
                        assigned_at=created_at,
                        replay_dir=turn_root / "worker_assignment",
                    )
                except Exception:
                    worker_assignment_capture = assign_worker_from_invocation_request(
                        worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
                        worker_invocation_request_artifact={},
                        worker_invocation_request_replay_reference="MISSING_WORKER_INVOCATION_REQUEST_REPLAY",
                        worker_registry_artifacts=[],
                        assigned_by=args.operator_context or "HUMAN_OPERATOR",
                        assigned_at=created_at,
                        replay_dir=turn_root / "worker_assignment",
                    )
                if worker_assignment_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {worker_assignment_capture.get('failure_reason')}")
                else:
                    output_writer(render_worker_assignment_summary(worker_assignment_capture))
                turns.append(
                    _interactive_domain_worker_assignment_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        worker_assignment_capture=worker_assignment_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_DISPATCH:
                worker_dispatch_entry_intent = detect_domain_worker_dispatch_entry_intent(human_prompt)
                try:
                    latest_worker_assignment = find_latest_domain_worker_assignment(
                        session_root=session_root,
                        domain_name=worker_dispatch_entry_intent["domain_name"],
                    )
                    worker_dispatch_capture = dispatch_assigned_worker(
                        worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
                        worker_assignment_artifact=latest_worker_assignment["worker_assignment_artifact"],
                        worker_assignment_replay_reference=latest_worker_assignment[
                            "worker_assignment_replay_reference"
                        ],
                        dispatched_by=args.operator_context or "HUMAN_OPERATOR",
                        dispatched_at=created_at,
                        replay_dir=turn_root / "worker_dispatch",
                    )
                except Exception:
                    worker_dispatch_capture = dispatch_assigned_worker(
                        worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
                        worker_assignment_artifact={},
                        worker_assignment_replay_reference="MISSING_WORKER_ASSIGNMENT_REPLAY",
                        dispatched_by=args.operator_context or "HUMAN_OPERATOR",
                        dispatched_at=created_at,
                        replay_dir=turn_root / "worker_dispatch",
                    )
                if worker_dispatch_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {worker_dispatch_capture.get('failure_reason')}")
                else:
                    output_writer(render_worker_dispatch_summary(worker_dispatch_capture))
                turns.append(
                    _interactive_domain_worker_dispatch_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        worker_dispatch_capture=worker_dispatch_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_INVOCATION:
                worker_invocation_entry_intent = detect_domain_worker_invocation_entry_intent(human_prompt)
                worker_assignment_capture: dict[str, Any] | None = None
                worker_dispatch_capture: dict[str, Any] | None = None
                try:
                    try:
                        latest_worker_dispatch = find_latest_domain_worker_dispatch(
                            session_root=session_root,
                            domain_name=worker_invocation_entry_intent["domain_name"],
                        )
                    except Exception:
                        try:
                            latest_worker_assignment = find_latest_domain_worker_assignment(
                                session_root=session_root,
                                domain_name=worker_invocation_entry_intent["domain_name"],
                            )
                        except Exception:
                            latest_worker_request = find_latest_domain_worker_invocation_request(
                                session_root=session_root,
                                domain_name=worker_invocation_entry_intent["domain_name"],
                            )
                            worker_assignment_capture = assign_worker_from_invocation_request(
                                worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
                                worker_invocation_request_artifact=latest_worker_request[
                                    "worker_invocation_request_artifact"
                                ],
                                worker_invocation_request_replay_reference=latest_worker_request[
                                    "worker_invocation_request_replay_reference"
                                ],
                                worker_registry_artifacts=default_worker_registry_for_request(
                                    latest_worker_request["worker_invocation_request_artifact"],
                                    created_at=created_at,
                                ),
                                assigned_by=args.operator_context or "HUMAN_OPERATOR",
                                assigned_at=created_at,
                                replay_dir=turn_root / "worker_assignment",
                            )
                            if worker_assignment_capture.get("fail_closed") is True:
                                raise FailClosedRuntimeError(
                                    worker_assignment_capture.get("failure_reason")
                                    or "worker assignment failed closed"
                                )
                            latest_worker_assignment = {
                                "worker_assignment_artifact": worker_assignment_capture[
                                    "worker_assignment_artifact"
                                ],
                                "worker_assignment_replay_reference": worker_assignment_capture[
                                    "worker_assignment_replay_reference"
                                ],
                            }
                        worker_dispatch_capture = dispatch_assigned_worker(
                            worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
                            worker_assignment_artifact=latest_worker_assignment["worker_assignment_artifact"],
                            worker_assignment_replay_reference=latest_worker_assignment[
                                "worker_assignment_replay_reference"
                            ],
                            dispatched_by=args.operator_context or "HUMAN_OPERATOR",
                            dispatched_at=created_at,
                            replay_dir=turn_root / "worker_dispatch",
                        )
                        if worker_dispatch_capture.get("fail_closed") is True:
                            raise FailClosedRuntimeError(
                                worker_dispatch_capture.get("failure_reason")
                                or "worker dispatch failed closed"
                            )
                        latest_worker_dispatch = {
                            "worker_dispatch_artifact": worker_dispatch_capture["worker_dispatch_artifact"],
                            "worker_dispatch_replay_reference": worker_dispatch_capture[
                                "worker_dispatch_replay_reference"
                            ],
                        }
                    worker_invocation_capture = invoke_dispatched_worker(
                        worker_invocation_id=f"{prompt_id}:WORKER-INVOCATION",
                        worker_dispatch_artifact=latest_worker_dispatch["worker_dispatch_artifact"],
                        worker_dispatch_replay_reference=latest_worker_dispatch["worker_dispatch_replay_reference"],
                        invoked_by="AIGOL_GOVERNANCE",
                        invoked_at=created_at,
                        replay_dir=turn_root / "worker_invocation",
                    )
                except Exception:
                    worker_invocation_capture = invoke_dispatched_worker(
                        worker_invocation_id=f"{prompt_id}:WORKER-INVOCATION",
                        worker_dispatch_artifact={},
                        worker_dispatch_replay_reference="MISSING_WORKER_DISPATCH_REPLAY",
                        invoked_by="AIGOL_GOVERNANCE",
                        invoked_at=created_at,
                        replay_dir=turn_root / "worker_invocation",
                    )
                if worker_invocation_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {worker_invocation_capture.get('failure_reason')}")
                else:
                    rendered_summaries = []
                    if worker_assignment_capture is not None:
                        rendered_summaries.append(render_worker_assignment_summary(worker_assignment_capture))
                    if worker_dispatch_capture is not None:
                        rendered_summaries.append(render_worker_dispatch_summary(worker_dispatch_capture))
                    rendered_summaries.append(render_worker_invocation_summary(worker_invocation_capture))
                    output_writer("\n".join(rendered_summaries))
                turns.append(
                    _interactive_domain_worker_invocation_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        worker_invocation_capture=worker_invocation_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_EXECUTION:
                worker_execution_entry_intent = detect_domain_worker_execution_entry_intent(human_prompt)
                try:
                    latest_worker_invocation = find_latest_domain_worker_invocation_for_execution(
                        session_root=session_root,
                        domain_name=worker_execution_entry_intent["domain_name"],
                    )
                    execution_capture = _record_authorized_worker_execution_start(
                        execution_id=f"{prompt_id}:EXECUTION",
                        invocation_artifact=latest_worker_invocation["worker_invocation_artifact"],
                        invocation_replay=latest_worker_invocation["invocation_result_artifact"],
                        dispatch_artifact=latest_worker_invocation["worker_dispatch_artifact"],
                        worker_assignment_artifact=latest_worker_invocation["worker_assignment_artifact"],
                        canonical_chain_id=latest_worker_invocation["chain_id"],
                        worker_reference=latest_worker_invocation["worker_id"],
                        worker_role=latest_worker_invocation["worker_role"],
                        started_at=created_at,
                        replay_dir=turn_root / "execution_runtime",
                    )
                    output_writer(_render_execution_runtime_summary(execution_capture))
                except Exception as exc:
                    failed_turns += 1
                    execution_capture = {
                        "execution_artifact": None,
                        "execution_replay": None,
                        "fail_closed": True,
                        "failure_reason": str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "execution failed closed",
                    }
                    output_writer(f"FAILED_CLOSED: {execution_capture['failure_reason']}")
                execution_capture["domain_name"] = worker_execution_entry_intent.get("domain_name")
                turns.append(
                    _interactive_domain_worker_execution_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        execution_capture=execution_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_RESULT_CAPTURE:
                worker_result_capture_entry_intent = detect_domain_worker_result_capture_entry_intent(human_prompt)
                try:
                    latest_execution = find_latest_domain_execution_for_result_capture(
                        session_root=session_root,
                        domain_name=worker_result_capture_entry_intent["domain_name"],
                    )
                    result_capture = capture_worker_result(
                        worker_result_capture_id=f"{prompt_id}:WORKER-RESULT-CAPTURE",
                        worker_invocation_artifact=latest_execution["worker_invocation_artifact"],
                        worker_invocation_replay_reference=latest_execution[
                            "worker_invocation_replay_reference"
                        ],
                        worker_output=default_worker_output_for_invocation(
                            latest_execution["worker_invocation_artifact"],
                            captured_at=created_at,
                        ),
                        captured_by="AIGOL_GOVERNANCE",
                        captured_at=created_at,
                        replay_dir=turn_root / "worker_result_capture",
                        execution_artifact=latest_execution["execution_artifact"],
                        execution_replay=latest_execution["execution_replay"],
                        execution_replay_reference=latest_execution["execution_replay_reference"],
                    )
                    if result_capture.get("fail_closed") is True:
                        raise FailClosedRuntimeError(
                            result_capture.get("failure_reason")
                            or "worker result capture failed closed"
                        )
                    output_writer(render_worker_result_capture_summary(result_capture))
                except Exception as exc:
                    failed_turns += 1
                    result_capture = {
                        "worker_result_capture_artifact": None,
                        "result_capture_result_artifact": None,
                        "fail_closed": True,
                        "failure_reason": str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "worker result capture failed closed",
                    }
                    output_writer(f"FAILED_CLOSED: {result_capture['failure_reason']}")
                result_capture["domain_name"] = worker_result_capture_entry_intent.get("domain_name")
                turns.append(
                    _interactive_domain_worker_result_capture_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        result_capture=result_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_WORKER_RESULT_VALIDATION:
                worker_result_validation_entry_intent = detect_domain_worker_result_validation_entry_intent(human_prompt)
                try:
                    latest_result_capture = find_latest_domain_result_capture_for_validation(
                        session_root=session_root,
                        domain_name=worker_result_validation_entry_intent["domain_name"],
                    )
                    validation_capture = validate_worker_result(
                        worker_result_validation_id=f"{prompt_id}:WORKER-RESULT-VALIDATION",
                        worker_result_capture_artifact=latest_result_capture["worker_result_capture_artifact"],
                        worker_result_capture_replay_reference=latest_result_capture[
                            "worker_result_capture_replay_reference"
                        ],
                        validated_by="AIGOL_GOVERNANCE",
                        validated_at=created_at,
                        replay_dir=turn_root / "worker_result_validation",
                    )
                    if validation_capture.get("fail_closed") is True:
                        raise FailClosedRuntimeError(
                            validation_capture.get("failure_reason")
                            or "worker result validation failed closed"
                        )
                    output_writer(render_worker_result_validation_summary(validation_capture))
                except Exception as exc:
                    failed_turns += 1
                    validation_capture = {
                        "worker_result_validation_artifact": None,
                        "validation_result_artifact": None,
                        "fail_closed": True,
                        "failure_reason": str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "worker result validation failed closed",
                    }
                    output_writer(f"FAILED_CLOSED: {validation_capture['failure_reason']}")
                validation_capture["domain_name"] = worker_result_validation_entry_intent.get("domain_name")
                turns.append(
                    _interactive_domain_worker_result_validation_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        validation_capture=validation_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_POST_EXECUTION_REPLAY_REVIEW:
                replay_review_entry_intent = detect_domain_post_execution_replay_review_entry_intent(human_prompt)
                try:
                    latest_validation = find_latest_domain_result_validation_for_replay_review(
                        session_root=session_root,
                        domain_name=replay_review_entry_intent["domain_name"],
                    )
                    review_capture = review_validated_worker_result(
                        post_execution_replay_review_id=f"{prompt_id}:POST-EXECUTION-REPLAY-REVIEW",
                        worker_result_validation_artifact=latest_validation[
                            "worker_result_validation_artifact"
                        ],
                        worker_result_validation_replay_reference=latest_validation[
                            "worker_result_validation_replay_reference"
                        ],
                        reviewed_by="AIGOL_GOVERNANCE",
                        reviewed_at=created_at,
                        replay_dir=turn_root / "post_execution_replay_review",
                    )
                    if review_capture.get("fail_closed") is True:
                        raise FailClosedRuntimeError(
                            review_capture.get("failure_reason")
                            or "post-execution replay review failed closed"
                        )
                    output_writer(render_post_execution_replay_review_summary(review_capture))
                except Exception as exc:
                    failed_turns += 1
                    review_capture = {
                        "post_execution_replay_review_artifact": None,
                        "review_result_artifact": None,
                        "fail_closed": True,
                        "failure_reason": str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "post-execution replay review failed closed",
                    }
                    output_writer(f"FAILED_CLOSED: {review_capture['failure_reason']}")
                review_capture["domain_name"] = replay_review_entry_intent.get("domain_name")
                turns.append(
                    _interactive_domain_post_execution_replay_review_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        review_capture=review_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_GOVERNED_TERMINATION:
                governed_termination_entry_intent = detect_domain_governed_termination_entry_intent(human_prompt)
                try:
                    latest_review = find_latest_domain_replay_review_for_termination(
                        session_root=session_root,
                        domain_name=governed_termination_entry_intent["domain_name"],
                    )
                    termination_capture = terminate_reviewed_operation(
                        governed_termination_id=f"{prompt_id}:GOVERNED-TERMINATION",
                        post_execution_replay_review_artifact=latest_review[
                            "post_execution_replay_review_artifact"
                        ],
                        post_execution_replay_review_replay_reference=latest_review[
                            "post_execution_replay_review_replay_reference"
                        ],
                        terminated_by="AIGOL_GOVERNANCE",
                        terminated_at=created_at,
                        replay_dir=turn_root / "governed_termination",
                    )
                    if termination_capture.get("fail_closed") is True:
                        raise FailClosedRuntimeError(
                            termination_capture.get("failure_reason")
                            or "governed termination failed closed"
                        )
                    output_writer(render_governed_termination_summary(termination_capture))
                except Exception as exc:
                    failed_turns += 1
                    termination_capture = {
                        "governed_termination_artifact": None,
                        "termination_result_artifact": None,
                        "fail_closed": True,
                        "failure_reason": str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "governed termination failed closed",
                    }
                    output_writer(f"FAILED_CLOSED: {termination_capture['failure_reason']}")
                termination_capture["domain_name"] = governed_termination_entry_intent.get("domain_name")
                turns.append(
                    _interactive_domain_governed_termination_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        termination_capture=termination_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DOMAIN_ADAPTATION_REFERENCE:
                domain_reference_capture = run_semantic_similarity_domain_reference_resolution(
                    resolution_id=f"{prompt_id}:SEMANTIC-SIMILARITY-DOMAIN-REFERENCE",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    canonical_chain_id=current_chain_id or prompt_id,
                    created_at=created_at,
                    replay_dir=turn_root / "semantic_similarity_domain_reference",
                )
                current_chain_id = domain_reference_capture.get("current_chain_id") or current_chain_id
                latest_chain_id = domain_reference_capture.get("latest_chain_id") or current_chain_id
                if domain_reference_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {domain_reference_capture.get('failure_reason')}")
                else:
                    output_writer(render_domain_reference_resolution_summary(domain_reference_capture))
                turns.append(
                    _interactive_domain_reference_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        domain_reference_capture=domain_reference_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_OPERATOR_DECISION_SUPPORT:
                decision_support_capture = run_operator_decision_support(
                    recommendation_id=f"{prompt_id}:OPERATOR-DECISION-SUPPORT",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    canonical_chain_id=current_chain_id or prompt_id,
                    created_at=created_at,
                    replay_dir=turn_root / "operator_decision_support",
                )
                current_chain_id = decision_support_capture.get("current_chain_id") or current_chain_id
                latest_chain_id = decision_support_capture.get("latest_chain_id") or current_chain_id
                if decision_support_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {decision_support_capture.get('failure_reason')}")
                else:
                    recommendation_continuity_capture = create_recommendation_continuity(
                        continuity_id=f"{prompt_id}:RECOMMENDATION-CONTINUITY",
                        recommendation_artifact=decision_support_capture["operator_decision_support_artifact"],
                        conversation_reference=prompt_id,
                        created_at=created_at,
                        replay_dir=turn_root / "recommendation_continuity",
                    )
                    decision_support_capture["recommendation_continuity"] = recommendation_continuity_capture
                    if recommendation_continuity_capture.get("fail_closed") is True:
                        failed_turns += 1
                        decision_support_capture["fail_closed"] = True
                        decision_support_capture["failure_reason"] = recommendation_continuity_capture.get(
                            "failure_reason"
                        )
                        output_writer(f"FAILED_CLOSED: {decision_support_capture['failure_reason']}")
                    else:
                        recommendation_continuity_artifact = recommendation_continuity_capture[
                            "recommendation_continuity_artifact"
                        ]
                        recommendation_approval_artifact = None
                        output_writer(
                            render_operator_decision_support_summary(decision_support_capture)
                            + "\n"
                            + render_recommendation_continuity_summary(recommendation_continuity_capture)
                        )
                turns.append(
                    _interactive_operator_decision_support_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        decision_support_capture=decision_support_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_CREATE_DOMAIN_COMPLIANCE_CLARIFICATION:
                if _is_plain_domain_proposal_prompt(human_prompt):
                    domain_proposal_capture = create_domain_proposal(
                        proposal_id=f"{prompt_id}:DOMAIN-PROPOSAL",
                        source_type="HUMAN_REQUEST",
                        proposed_domain=_plain_domain_proposal_name(human_prompt),
                        need_summary=human_prompt,
                        requested_by=args.operator_context or "HUMAN_OPERATOR",
                        canonical_chain_id=current_chain_id or prompt_id,
                        created_at=created_at,
                        replay_dir=turn_root / "domain_proposal",
                    )
                    current_chain_id = domain_proposal_capture.get("canonical_chain_id") or current_chain_id
                    latest_chain_id = current_chain_id
                    if domain_proposal_capture.get("fail_closed") is True:
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {domain_proposal_capture.get('failure_reason')}")
                    else:
                        pending_domain_proposal = domain_proposal_capture
                        pending_domain_review = None
                        output_writer(_render_domain_proposal_acceptance_summary(domain_proposal_capture))
                    turns.append(
                        _interactive_domain_proposal_turn_summary(
                            turn_id=turn_id,
                            prompt_id=prompt_id,
                            router_capture=router_capture,
                            domain_proposal_capture=domain_proposal_capture,
                            conversational_routing_capture=conversational_routing_capture,
                            source_router_replay_reference=str(turn_root / "source_router"),
                        )
                    )
                else:
                    clarification_capture = run_unknown_domain_clarification_workflow(
                        clarification_id=f"{prompt_id}:UNKNOWN-DOMAIN-CLARIFICATION",
                        prompt_id=prompt_id,
                        human_prompt=human_prompt,
                        canonical_chain_id=current_chain_id or prompt_id,
                        created_at=created_at,
                        replay_dir=turn_root / "unknown_domain_clarification",
                    )
                    current_chain_id = clarification_capture.get("current_chain_id") or current_chain_id
                    latest_chain_id = clarification_capture.get("latest_chain_id") or current_chain_id
                    if clarification_capture.get("fail_closed") is True:
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {clarification_capture.get('failure_reason')}")
                    else:
                        output_writer(render_unknown_domain_clarification_workflow(clarification_capture))
                    turns.append(
                        _interactive_unknown_domain_clarification_turn_summary(
                            turn_id=turn_id,
                            prompt_id=prompt_id,
                            router_capture=router_capture,
                            clarification_capture=clarification_capture,
                            conversational_routing_capture=conversational_routing_capture,
                            source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW:
                bridge_capture = propose_acli_governed_development_execution(
                    bridge_id=f"{prompt_id}:ACLI-GOVERNED-DEVELOPMENT-BRIDGE",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    conversational_routing_capture=conversational_routing_capture or {},
                    universal_intake_artifact=universal_intake_capture["universal_intake_artifact"],
                    workspace_root=args.workspace,
                    proposed_by=args.operator_context or "HUMAN_OPERATOR",
                    created_at=created_at,
                    replay_dir=turn_root / "acli_governed_development_execution_bridge",
                )
                if bridge_capture.get("bridge_status") == ACLI_GOVERNED_DEVELOPMENT_APPROVAL_REQUIRED:
                    pending_governed_development_bridge = bridge_capture
                    human_friendly_explanation_capture = create_acli_human_friendly_explanation(
                        explanation_id=f"{prompt_id}:HUMAN-FRIENDLY-EXPLANATION",
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        human_prompt=human_prompt,
                        workflow_id=CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW,
                        routing_visibility_artifact=routing_visibility_capture[
                            "conversational_routing_visibility_artifact"
                        ],
                        universal_intake_artifact=universal_intake_capture["universal_intake_artifact"],
                        proposal_capture=bridge_capture,
                        replay_dir=turn_root / "human_friendly_explanation",
                        created_at=created_at,
                    )
                    output_writer(render_acli_human_friendly_explanation(human_friendly_explanation_capture))
                    if llm_assisted_explanation_enabled:
                        authoritative_state = authoritative_state_from_acli_proposal_capture(
                            state_id=f"{prompt_id}:LLM-ASSISTED-EXPLANATION-STATE",
                            proposal_capture=bridge_capture,
                            approval_state="APPROVAL_REQUIRED",
                            replay_references=[
                                str(turn_root / "conversational_cli_routing"),
                                str(turn_root / "routing_visibility"),
                                str(turn_root / "universal_intake"),
                                human_friendly_explanation_capture[
                                    "human_friendly_explanation_replay_reference"
                                ],
                            ],
                            created_at=created_at,
                        )
                        llm_assisted_explanation_capture = create_acli_llm_assisted_explanation(
                            explanation_id=f"{prompt_id}:LLM-ASSISTED-EXPLANATION",
                            authoritative_state=authoritative_state,
                            deterministic_explanation=human_friendly_explanation_capture[
                                "operator_explanation"
                            ],
                            provider=llm_explanation_provider,
                            provider_id=llm_explanation_provider_id,
                            replay_dir=turn_root / "llm_assisted_explanation",
                            created_at=created_at,
                        )
                        llm_assisted_artifact = llm_assisted_explanation_capture[
                            "llm_assisted_explanation_artifact"
                        ]
                        if llm_assisted_artifact.get("provider_explanation_used") is True:
                            output_writer("PROVIDER-ASSISTED EXPLANATION")
                            output_writer(
                                render_acli_llm_assisted_explanation(llm_assisted_explanation_capture)
                            )
                    output_writer(render_acli_governed_development_bridge_summary(bridge_capture))
                else:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {bridge_capture.get('failure_reason')}")
                turns.append(
                    _interactive_acli_governed_development_bridge_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        bridge_capture=bridge_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id in {
                CONVERSATIONAL_CREATE_DOMAIN_TRADING,
                CONVERSATIONAL_CREATE_DOMAIN_MARKETING,
                CONVERSATIONAL_NATIVE_DEVELOPMENT_INTENT_ROUTING,
            }:
                routing_capture = run_conversation_native_development_intent_routing(
                    routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    canonical_chain_id=current_chain_id or prompt_id,
                    turn_allocation_evidence=resume_state,
                    created_at=created_at,
                    replay_dir=turn_root / "native_development_intent_routing",
                )
                current_chain_id = routing_capture.get("current_chain_id") or current_chain_id
                latest_chain_id = routing_capture.get("latest_chain_id") or current_chain_id
                fail_closed = routing_capture.get("fail_closed") is True
                if fail_closed:
                    failed_turns += 1
                    failure_reason = routing_capture.get("failure_reason") or "native development intent routing failed closed"
                    output_writer(f"FAILED_CLOSED: {failure_reason}")
                else:
                    ppp_capture = run_conversation_to_ppp_handoff_execution(
                        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
                        native_development_intent_routed_artifact=routing_capture[
                            "native_development_intent_routed_artifact"
                        ],
                        created_at=created_at,
                        replay_dir=turn_root / "conversation_to_ppp_handoff_execution",
                    )
                    routing_capture["conversation_to_ppp_handoff_execution"] = ppp_capture
                    routing_capture["response_status"] = ppp_capture.get("terminal_status")
                    routing_capture["response_source"] = "CONVERSATION_TO_PPP_HANDOFF_EXECUTION"
                    routing_capture["fail_closed"] = ppp_capture.get("fail_closed") is True
                    routing_capture["failure_reason"] = ppp_capture.get("failure_reason")
                    if ppp_capture.get("terminal_status") == "HUMAN_APPROVAL_REQUIRED":
                        pending_approval_required = ppp_capture
                    if routing_capture["fail_closed"]:
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                    else:
                        handoff_visibility_capture = None
                        if (
                            ppp_capture.get("terminal_status") == "IMPLEMENTATION_HANDOFF_CREATED"
                            and ppp_capture.get("handoff_replay_reference")
                        ):
                            handoff_visibility_capture = create_implementation_handoff_visibility_summary(
                                visibility_id=f"{prompt_id}:IMPLEMENTATION-HANDOFF-VISIBILITY",
                                handoff_replay_reference=ppp_capture["handoff_replay_reference"],
                                approval_status=ppp_capture.get("approval_status") or "",
                                created_at=created_at,
                                replay_dir=turn_root / "implementation_handoff_visibility",
                            )
                            routing_capture["implementation_handoff_visibility"] = handoff_visibility_capture
                            if handoff_visibility_capture.get("fail_closed") is True:
                                routing_capture["fail_closed"] = True
                                routing_capture["failure_reason"] = handoff_visibility_capture.get("failure_reason")
                                failed_turns += 1
                                output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                            else:
                                dry_run_capture = prepare_governed_implementation_dry_run(
                                    dry_run_id=f"{prompt_id}:GOVERNED-IMPLEMENTATION-DRY-RUN",
                                    handoff_replay_reference=ppp_capture["handoff_replay_reference"],
                                    handoff_visibility_artifact=handoff_visibility_capture[
                                        "implementation_handoff_visibility_artifact"
                                    ],
                                    upstream_lineage_artifact=ppp_capture[
                                        "conversation_to_ppp_handoff_execution_artifact"
                                    ],
                                    created_at=created_at,
                                    replay_dir=turn_root / "governed_implementation_dry_run",
                                )
                                routing_capture["governed_implementation_dry_run"] = dry_run_capture
                                if dry_run_capture.get("fail_closed") is True:
                                    routing_capture["fail_closed"] = True
                                    routing_capture["failure_reason"] = dry_run_capture.get("failure_reason")
                                    failed_turns += 1
                                    output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                else:
                                    authorization_capture = authorize_execution_ready(
                                        authorization_id=f"{prompt_id}:EXECUTION-AUTHORIZATION",
                                        execution_ready_replay_reference=dry_run_capture[
                                            "governed_implementation_dry_run_replay_reference"
                                        ],
                                        authorizing_actor="AIGOL_GOVERNANCE",
                                        authorized_at=created_at,
                                        replay_dir=turn_root / "execution_authorization",
                                    )
                                    routing_capture["execution_authorization"] = authorization_capture
                                    if authorization_capture.get("fail_closed") is True:
                                        routing_capture["fail_closed"] = True
                                        routing_capture["failure_reason"] = authorization_capture.get("failure_reason")
                                        failed_turns += 1
                                        output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                    else:
                                        invocation_request_capture = create_worker_invocation_request(
                                            invocation_request_id=f"{prompt_id}:WORKER-INVOCATION-REQUEST",
                                            execution_authorization_replay_reference=authorization_capture[
                                                "execution_authorization_replay_reference"
                                            ],
                                            requested_by="AIGOL_GOVERNANCE",
                                            requested_at=created_at,
                                            replay_dir=turn_root / "worker_invocation_request",
                                        )
                                        routing_capture["worker_invocation_request"] = invocation_request_capture
                                        if invocation_request_capture.get("fail_closed") is True:
                                            routing_capture["fail_closed"] = True
                                            routing_capture["failure_reason"] = invocation_request_capture.get(
                                                "failure_reason"
                                            )
                                            failed_turns += 1
                                            output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                        else:
                                            assignment_capture = assign_worker_from_invocation_request(
                                                worker_assignment_id=f"{prompt_id}:WORKER-ASSIGNMENT",
                                                worker_invocation_request_artifact=invocation_request_capture[
                                                    "worker_invocation_request_artifact"
                                                ],
                                                worker_invocation_request_replay_reference=invocation_request_capture[
                                                    "worker_invocation_request_replay_reference"
                                                ],
                                                worker_registry_artifacts=default_worker_registry_for_request(
                                                    invocation_request_capture["worker_invocation_request_artifact"],
                                                    created_at=created_at,
                                                ),
                                                assigned_by="AIGOL_GOVERNANCE",
                                                assigned_at=created_at,
                                                replay_dir=turn_root / "worker_assignment",
                                            )
                                            routing_capture["worker_assignment"] = assignment_capture
                                            if assignment_capture.get("fail_closed") is True:
                                                routing_capture["fail_closed"] = True
                                                routing_capture["failure_reason"] = assignment_capture.get(
                                                    "failure_reason"
                                                )
                                                failed_turns += 1
                                                output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                            else:
                                                dispatch_capture = dispatch_assigned_worker(
                                                    worker_dispatch_id=f"{prompt_id}:WORKER-DISPATCH",
                                                    worker_assignment_artifact=assignment_capture[
                                                        "worker_assignment_artifact"
                                                    ],
                                                    worker_assignment_replay_reference=assignment_capture[
                                                        "worker_assignment_replay_reference"
                                                    ],
                                                    dispatched_by="AIGOL_GOVERNANCE",
                                                    dispatched_at=created_at,
                                                    replay_dir=turn_root / "worker_dispatch",
                                                )
                                                routing_capture["worker_dispatch"] = dispatch_capture
                                                if dispatch_capture.get("fail_closed") is True:
                                                    routing_capture["fail_closed"] = True
                                                    routing_capture["failure_reason"] = dispatch_capture.get(
                                                        "failure_reason"
                                                    )
                                                    failed_turns += 1
                                                    output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                                else:
                                                    invocation_capture = invoke_dispatched_worker(
                                                        worker_invocation_id=f"{prompt_id}:WORKER-INVOCATION",
                                                        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
                                                        worker_dispatch_replay_reference=dispatch_capture[
                                                            "worker_dispatch_replay_reference"
                                                        ],
                                                        invoked_by="AIGOL_GOVERNANCE",
                                                        invoked_at=created_at,
                                                        replay_dir=turn_root / "worker_invocation",
                                                    )
                                                    routing_capture["worker_invocation"] = invocation_capture
                                                    if invocation_capture.get("fail_closed") is True:
                                                        routing_capture["fail_closed"] = True
                                                        routing_capture["failure_reason"] = invocation_capture.get(
                                                            "failure_reason"
                                                        )
                                                        failed_turns += 1
                                                        output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                                    else:
                                                        execution_capture = _record_authorized_worker_execution_start(
                                                            execution_id=f"{prompt_id}:EXECUTION",
                                                            invocation_artifact=invocation_capture[
                                                                "worker_invocation_artifact"
                                                            ],
                                                            invocation_replay=invocation_capture[
                                                                "invocation_result_artifact"
                                                            ],
                                                            dispatch_artifact=dispatch_capture[
                                                                "worker_dispatch_artifact"
                                                            ],
                                                            worker_assignment_artifact=assignment_capture[
                                                                "worker_assignment_artifact"
                                                            ],
                                                            canonical_chain_id=invocation_capture[
                                                                "worker_invocation_artifact"
                                                            ]["chain_id"],
                                                            worker_reference=invocation_capture["worker_id"],
                                                            worker_role=invocation_capture["worker_role"],
                                                            started_at=created_at,
                                                            replay_dir=turn_root / "execution_runtime",
                                                        )
                                                        routing_capture["execution_runtime"] = execution_capture
                                                        result_capture = capture_worker_result(
                                                            worker_result_capture_id=f"{prompt_id}:WORKER-RESULT-CAPTURE",
                                                            worker_invocation_artifact=invocation_capture[
                                                                "worker_invocation_artifact"
                                                            ],
                                                            worker_invocation_replay_reference=invocation_capture[
                                                                "worker_invocation_replay_reference"
                                                            ],
                                                            worker_output=default_worker_output_for_invocation(
                                                                invocation_capture["worker_invocation_artifact"],
                                                                captured_at=created_at,
                                                            ),
                                                            captured_by="AIGOL_GOVERNANCE",
                                                            captured_at=created_at,
                                                            replay_dir=turn_root / "worker_result_capture",
                                                            execution_artifact=execution_capture["execution_artifact"],
                                                            execution_replay=execution_capture["execution_replay"],
                                                            execution_replay_reference=str(turn_root / "execution_runtime"),
                                                        )
                                                        routing_capture["worker_result_capture"] = result_capture
                                                        if result_capture.get("fail_closed") is True:
                                                            routing_capture["fail_closed"] = True
                                                            routing_capture["failure_reason"] = result_capture.get(
                                                                "failure_reason"
                                                            )
                                                            failed_turns += 1
                                                            output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                                        else:
                                                            validation_capture = validate_worker_result(
                                                                worker_result_validation_id=f"{prompt_id}:WORKER-RESULT-VALIDATION",
                                                                worker_result_capture_artifact=result_capture[
                                                                    "worker_result_capture_artifact"
                                                                ],
                                                                worker_result_capture_replay_reference=result_capture[
                                                                    "worker_result_capture_replay_reference"
                                                                ],
                                                                validated_by="AIGOL_GOVERNANCE",
                                                                validated_at=created_at,
                                                                replay_dir=turn_root / "worker_result_validation",
                                                            )
                                                            routing_capture["worker_result_validation"] = validation_capture
                                                            if validation_capture.get("fail_closed") is True:
                                                                routing_capture["fail_closed"] = True
                                                                routing_capture["failure_reason"] = validation_capture.get(
                                                                    "failure_reason"
                                                                )
                                                                failed_turns += 1
                                                                output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                                                            else:
                                                                executable_bundle_capture = _bind_supported_executable_domain_bundle(
                                                                    prompt_id=prompt_id,
                                                                    validation_capture=validation_capture,
                                                                    workspace_root=args.workspace,
                                                                    created_at=created_at,
                                                                    replay_dir=turn_root / "executable_domain_bundle",
                                                                )
                                                                if executable_bundle_capture is not None:
                                                                    routing_capture["executable_bundle"] = executable_bundle_capture
                                                                if executable_bundle_capture is not None and executable_bundle_capture.get(
                                                                    "fail_closed"
                                                                ) is True:
                                                                    routing_capture["fail_closed"] = True
                                                                    routing_capture["failure_reason"] = executable_bundle_capture.get(
                                                                        "failure_reason"
                                                                    )
                                                                    failed_turns += 1
                                                                    output_writer(
                                                                        f"FAILED_CLOSED: {routing_capture['failure_reason']}"
                                                                    )
                                                                if not (
                                                                    executable_bundle_capture is not None
                                                                    and executable_bundle_capture.get("fail_closed") is True
                                                                ):
                                                                    review_capture = review_validated_worker_result(
                                                                        post_execution_replay_review_id=f"{prompt_id}:POST-EXECUTION-REPLAY-REVIEW",
                                                                        worker_result_validation_artifact=validation_capture[
                                                                            "worker_result_validation_artifact"
                                                                        ],
                                                                        worker_result_validation_replay_reference=validation_capture[
                                                                            "worker_result_validation_replay_reference"
                                                                        ],
                                                                        executable_bundle_artifact=(
                                                                            executable_bundle_capture["executable_domain_bundle_artifact"]
                                                                            if executable_bundle_capture
                                                                            else None
                                                                        ),
                                                                        executable_bundle_replay_reference=(
                                                                            executable_bundle_capture["executable_bundle_replay_reference"]
                                                                            if executable_bundle_capture
                                                                            else None
                                                                        ),
                                                                        reviewed_by="AIGOL_GOVERNANCE",
                                                                        reviewed_at=created_at,
                                                                        replay_dir=turn_root / "post_execution_replay_review",
                                                                    )
                                                                    routing_capture["post_execution_replay_review"] = review_capture
                                                                    if review_capture.get("fail_closed") is True:
                                                                        routing_capture["fail_closed"] = True
                                                                        routing_capture["failure_reason"] = review_capture.get(
                                                                            "failure_reason"
                                                                        )
                                                                        failed_turns += 1
                                                                        output_writer(
                                                                            f"FAILED_CLOSED: {routing_capture['failure_reason']}"
                                                                        )
                                                                    else:
                                                                        termination_capture = terminate_reviewed_operation(
                                                                            governed_termination_id=f"{prompt_id}:GOVERNED-TERMINATION",
                                                                            post_execution_replay_review_artifact=review_capture[
                                                                                "post_execution_replay_review_artifact"
                                                                            ],
                                                                            post_execution_replay_review_replay_reference=review_capture[
                                                                                "post_execution_replay_review_replay_reference"
                                                                            ],
                                                                            terminated_by="AIGOL_GOVERNANCE",
                                                                            terminated_at=created_at,
                                                                            replay_dir=turn_root / "governed_termination",
                                                                        )
                                                                        routing_capture["governed_termination"] = termination_capture
                                                                        if termination_capture.get("fail_closed") is True:
                                                                            routing_capture["fail_closed"] = True
                                                                            routing_capture["failure_reason"] = termination_capture.get(
                                                                                "failure_reason"
                                                                            )
                                                                            failed_turns += 1
                                                                            output_writer(
                                                                                f"FAILED_CLOSED: {routing_capture['failure_reason']}"
                                                                            )
                                                                        else:
                                                                            output_writer(
                                                                                render_conversation_to_ppp_handoff_execution_summary(ppp_capture)
                                                                                + "\n"
                                                                                + render_implementation_handoff_visibility_summary(handoff_visibility_capture)
                                                                                + "\n"
                                                                                + render_governed_implementation_dry_run_summary(dry_run_capture)
                                                                                + "\n"
                                                                                + render_execution_authorization_summary(authorization_capture)
                                                                                + "\n"
                                                                                + render_worker_invocation_request_summary(invocation_request_capture)
                                                                                + "\n"
                                                                                + render_worker_assignment_summary(assignment_capture)
                                                                                + "\n"
                                                                                + render_worker_dispatch_summary(dispatch_capture)
                                                                                + "\n"
                                                                                + render_worker_invocation_summary(invocation_capture)
                                                                                + "\n"
                                                                                + _render_execution_runtime_summary(execution_capture)
                                                                                + "\n"
                                                                                + render_worker_result_capture_summary(result_capture)
                                                                                + "\n"
                                                                                + render_worker_result_validation_summary(validation_capture)
                                                                                + "\n"
                                                                                + (
                                                                                    render_executable_domain_bundle_summary(
                                                                                        executable_bundle_capture
                                                                                    )
                                                                                    + "\n"
                                                                                    if executable_bundle_capture
                                                                                    else ""
                                                                                )
                                                                                + render_post_execution_replay_review_summary(review_capture)
                                                                                + "\n"
                                                                                + render_governed_termination_summary(termination_capture)
                                                                            )
                        else:
                            summary = render_conversation_to_ppp_handoff_execution_summary(ppp_capture)
                            if ppp_capture.get("terminal_status") == "HUMAN_APPROVAL_REQUIRED":
                                summary += "\n\nHuman Decision Required\n\nChoices:\n* APPROVE\n* REJECT\n* REQUEST_MODIFICATION"
                            output_writer(summary)
                turns.append(
                    _interactive_native_development_intent_routing_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        routing_capture=routing_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION:
                native_context_capture = run_conversation_native_development_context_integration(
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    created_at=created_at,
                    replay_dir=turn_root,
                    governance_root="governance",
                    session_id=session_id,
                    turn_id=turn_id,
                    current_chain_id=current_chain_id,
                    latest_chain_id=latest_chain_id,
                )
                current_chain_id = native_context_capture.get("current_chain_id") or current_chain_id
                latest_chain_id = native_context_capture.get("latest_chain_id") or current_chain_id
                fail_closed = native_context_capture.get("fail_closed") is True
                if fail_closed:
                    failed_turns += 1
                    failure_reason = (
                        native_context_capture.get("failure_reason")
                        or "native development context integration failed closed"
                    )
                    output_writer(f"FAILED_CLOSED: {failure_reason}")
                else:
                    native_output = render_conversation_native_development_context_summary(native_context_capture)
                    post_entry_gate_capture = evaluate_post_entry_continuation_gate(
                        gate_id=f"{prompt_id}:POST-ENTRY-CONTINUATION-GATE",
                        prompt_id=prompt_id,
                        human_prompt=human_prompt,
                        workflow_id=CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
                        lifecycle_entry_status=str(native_context_capture.get("context_status") or ""),
                        provider_necessity_classification=native_context_capture.get(
                            "provider_necessity_classification"
                        ),
                        auto_continue_enabled=auto_continue_enabled,
                        created_at=created_at,
                        replay_dir=turn_root / "post_entry_continuation_gate",
                        lifecycle_replay_reference=native_context_capture.get("conversation_replay_reference"),
                    )
                    native_context_capture["post_entry_continuation_gate"] = post_entry_gate_capture
                    native_context_capture["post_entry_continuation_gate_status"] = post_entry_gate_capture.get(
                        "gate_status"
                    )
                    native_context_capture["post_entry_continuation_gate_replay_reference"] = (
                        post_entry_gate_capture.get("post_entry_continuation_gate_replay_reference")
                    )
                    if post_entry_gate_capture.get("fail_closed") is True:
                        native_context_capture["fail_closed"] = True
                        native_context_capture["failure_reason"] = post_entry_gate_capture.get("failure_reason")
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                    elif post_entry_gate_capture.get("gate_status") == POST_ENTRY_CLARIFICATION_REQUIRED:
                        native_context_capture["clarification_required"] = True
                        native_context_capture["open_clarification_detected"] = True
                        native_context_capture["missing_information"] = [
                            "explicit post-entry continuation confirmation: continue ppp"
                        ]
                        native_context_capture["post_entry_clarification_pending"] = True
                        pending_post_entry_continuation = {
                            "native_context_capture": deepcopy(native_context_capture),
                            "original_human_prompt": human_prompt,
                            "current_chain_id": current_chain_id,
                            "latest_chain_id": latest_chain_id,
                        }
                    elif (
                        post_entry_gate_capture.get("gate_status") == POST_ENTRY_CONTINUATION_ALLOWED
                        and _post_context_continuation_should_run(
                            native_context_capture=native_context_capture,
                            auto_continue_enabled=auto_continue_enabled,
                            human_prompt=human_prompt,
                        )
                    ):
                        post_context_continuation_capture = continue_context_assembled_to_ppp_routing(
                            continuation_id=f"{prompt_id}:POST-CONTEXT-CONTINUATION",
                            prompt_id=prompt_id,
                            human_prompt=human_prompt,
                            provider_id=OPENAI_PROVIDER_ID,
                            created_at=created_at,
                            replay_dir=turn_root / "post_context_continuation",
                            registry=_post_context_continuation_provider_registry(),
                            adapter=_post_context_continuation_provider_adapter(),
                            governance_root="governance",
                            session_id=session_id,
                            turn_id=turn_id,
                            current_chain_id=current_chain_id,
                            latest_chain_id=latest_chain_id,
                            restored_native_context_capture=native_context_capture,
                        )
                        native_context_capture["post_context_continuation"] = post_context_continuation_capture
                        native_context_capture["ppp_route_status"] = post_context_continuation_capture.get(
                            "ppp_route_status"
                        )
                        native_context_capture["post_context_continuation_replay_reference"] = (
                            post_context_continuation_capture.get("post_context_continuation_replay_reference")
                        )
                        if post_context_continuation_capture.get("fail_closed") is True:
                            native_context_capture["fail_closed"] = True
                            native_context_capture["failure_reason"] = post_context_continuation_capture.get(
                                "failure_reason"
                            )
                            failed_turns += 1
                            output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                        else:
                            try:
                                worker_request_continuation = _continue_ppp_handoff_to_worker_request(
                                    prompt_id=prompt_id,
                                    post_context_continuation_capture=post_context_continuation_capture,
                                    created_at=created_at,
                                    replay_dir=turn_root / "certified_development_continuation",
                                )
                                native_context_capture["certified_development_continuation"] = (
                                    worker_request_continuation
                                )
                            except FailClosedRuntimeError as exc:
                                native_context_capture["fail_closed"] = True
                                native_context_capture["failure_reason"] = str(exc)
                                failed_turns += 1
                                output_writer(f"FAILED_CLOSED: {native_context_capture['failure_reason']}")
                            else:
                                native_output += "\n" + _post_context_continuation_output(
                                    post_context_continuation_capture
                                )
                                native_output += "\n" + _worker_lifecycle_continuation_output(
                                    worker_request_continuation
                                )
                    if native_context_capture.get("fail_closed") is not True:
                        output_writer(native_output)
                turns.append(
                    _interactive_native_development_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        native_context_capture=native_context_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_OCS_LLM_COGNITION:
                ocs_cognition_capture = _run_conversational_ocs_llm_cognition(
                    prompt_id=prompt_id,
                    human_prompt=human_prompt,
                    router_capture=router_capture,
                    current_chain_id=current_chain_id,
                    created_at=created_at,
                    replay_dir=turn_root / "ocs_llm_cognition_end_to_end",
                )
                current_chain_id = current_chain_id or prompt_id
                latest_chain_id = current_chain_id
                if ocs_cognition_capture.get("fail_closed") is True:
                    failed_turns += 1
                    output_writer(f"FAILED_CLOSED: {ocs_cognition_capture.get('failure_reason')}")
                else:
                    ocs_continuation_output = ""
                    if _explicit_ocs_execution_required(human_prompt):
                        try:
                            ocs_to_ppp_capture = _continue_ocs_cognition_to_ppp(
                                prompt_id=prompt_id,
                                human_prompt=human_prompt,
                                router_capture=router_capture,
                                current_chain_id=current_chain_id,
                                created_at=created_at,
                                replay_dir=turn_root / "ocs_certified_continuation",
                                execution_required=True,
                                session_id=session_id,
                                turn_id=turn_id,
                            )
                            ocs_cognition_capture["ocs_certified_continuation"] = ocs_to_ppp_capture
                            ocs_cognition_capture["ppp_route_status"] = ocs_to_ppp_capture.get("ppp_route_status")
                            ocs_worker_continuation = _continue_ppp_handoff_to_worker_request(
                                prompt_id=prompt_id,
                                post_context_continuation_capture=ocs_to_ppp_capture["ocs_to_ppp_continuation"],
                                created_at=created_at,
                                replay_dir=turn_root / "ocs_certified_worker_continuation",
                            )
                            ocs_cognition_capture["certified_worker_continuation"] = ocs_worker_continuation
                            ocs_continuation_output = "\n".join(
                                [
                                    "",
                                    "OCS-to-PPP Continuation",
                                    "",
                                    f"continuation_status: {ocs_to_ppp_capture.get('ocs_to_ppp_continuation', {}).get('continuation_status')}",
                                    f"ppp_route_status: {ocs_to_ppp_capture.get('ppp_route_status')}",
                                    f"replay_reference: {ocs_to_ppp_capture.get('ocs_to_ppp_continuation', {}).get('ocs_to_ppp_continuation_replay_reference')}",
                                    _worker_lifecycle_continuation_output(ocs_worker_continuation),
                                ]
                            )
                        except FailClosedRuntimeError as exc:
                            ocs_cognition_capture["fail_closed"] = True
                            ocs_cognition_capture["failure_reason"] = str(exc)
                            failed_turns += 1
                            output_writer(f"FAILED_CLOSED: {ocs_cognition_capture['failure_reason']}")
                    else:
                        ocs_cognition_capture["ocs_proposal_only_preserved"] = True
                        ocs_cognition_capture["ppp_route_status"] = None
                        if _is_plain_ocs_approval_prompt(human_prompt):
                            ocs_cognition_capture["approval_status"] = "APPROVAL_REQUIRED"
                            ocs_cognition_capture["approval_required"] = True
                            ocs_cognition_capture["clarification_required"] = False
                    output_writer(
                        "\n".join(
                            [
                                render_operator_visible_ocs_llm_cognition(ocs_cognition_capture),
                                render_ocs_llm_cognition_end_to_end_summary(ocs_cognition_capture),
                                "REAL_LLM_PROVIDER_USED_BY_OCS = "
                                f"{str(_real_llm_provider_used_by_ocs(ocs_cognition_capture)).lower()}",
                                ocs_continuation_output,
                            ]
                        )
                    )
                turns.append(
                    _interactive_ocs_llm_cognition_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        ocs_cognition_capture=ocs_cognition_capture,
                        conversational_routing_capture=conversational_routing_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif authoritative_workflow_id == CONVERSATIONAL_DEFAULT_PROVIDER_ASSISTED_CONVERSATION:
                conversation_capture = submit_prompt_to_conversation(
                    human_prompt=human_prompt,
                    prompt_id=prompt_id,
                    created_at=created_at,
                    replay_dir=session_root / "prompt_runtime",
                    operator_context=args.operator_context,
                    session_id=session_id,
                    current_chain_id=current_chain_id,
                    latest_chain_id=latest_chain_id,
                )
                current_chain_id = conversation_capture.get("current_chain_id") or current_chain_id
                latest_chain_id = conversation_capture.get("latest_chain_id") or current_chain_id
                fail_closed = conversation_capture.get("fail_closed") is True
                if fail_closed:
                    fallback_capture = run_conversation_provider_unavailable_clarification_fallback(
                        fallback_id=f"{prompt_id}:PROVIDER-UNAVAILABLE-CLARIFICATION-FALLBACK",
                        prompt_id=prompt_id,
                        human_prompt=human_prompt,
                        provider_failure_capture=conversation_capture,
                        canonical_chain_id=conversation_capture.get("canonical_chain_id") or current_chain_id or prompt_id,
                        created_at=created_at,
                        replay_dir=turn_root / "provider_unavailable_clarification_fallback",
                    )
                    if fallback_capture.get("response_status") == PROVIDER_UNAVAILABLE_HUMAN_CLARIFICATION_REQUIRED:
                        conversation_capture = fallback_capture
                        fail_closed = False
                        output_writer(render_provider_unavailable_clarification_fallback(fallback_capture))
                    else:
                        failed_turns += 1
                        failure_reason = (
                            fallback_capture.get("failure_reason")
                            or conversation_capture.get("failure_reason")
                            or "conversation failed closed"
                        )
                        conversation_capture = fallback_capture
                        output_writer(f"FAILED_CLOSED: {failure_reason}")
                else:
                    output_writer(conversation_capture.get("response_text", ""))
                turns.append(
                    _interactive_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        conversation_capture=conversation_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                        failure_reason=conversation_capture.get("failure_reason"),
                    )
                )
            else:
                failed_turns += 1
                failure_reason = f"unsupported conversational workflow selection: {authoritative_workflow_id}"
                output_writer(f"FAILED_CLOSED: {failure_reason}")
                turns.append(
                    _interactive_failed_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        source_router_replay_reference=str(turn_root / "source_router"),
                        failure_reason=failure_reason,
                    )
                )
            _attach_interactive_multiline_prompt_capture(
                turn_summary=turns[-1],
                multiline_prompt_capture=multiline_prompt_capture,
            )
            turns[-1]["operator_prompt"] = human_prompt
            turns[-1]["operator_prompt_lines"] = list(prompt_capture["prompt_lines"])
            _attach_interactive_routing_visibility(
                turn_summary=turns[-1],
                routing_visibility_capture=routing_visibility_capture,
            )
            _attach_interactive_universal_intake(
                turn_summary=turns[-1],
                universal_intake_capture=universal_intake_capture,
            )
            if human_friendly_explanation_capture is not None:
                _attach_interactive_human_friendly_explanation(
                    turn_summary=turns[-1],
                    explanation_capture=human_friendly_explanation_capture,
                )
            if llm_assisted_explanation_capture is not None:
                _attach_interactive_llm_assisted_explanation(
                    turn_summary=turns[-1],
                    explanation_capture=llm_assisted_explanation_capture,
                )
            workflow_status = _attach_interactive_workflow_status(turns[-1])
            if auto_continuation_prompt is not None:
                turns[-1]["auto_continued"] = True
                turns[-1]["auto_continued_from_next_expected_action"] = auto_continuation_prompt
                auto_continue_turns += 1
            _ensure_interactive_chain_inspection_commands(turns[-1])
            latest_workflow_status = workflow_status
            workflow_status_output = _render_interactive_workflow_status(workflow_status)
            _emit_interactive_conversation_progress(
                binding_capture=progress_binding_capture,
                stage=CONVERSATIONAL_PROGRESS_RESULT_ASSEMBLY,
                activity="Human-facing conversation result assembled.",
                snapshot_at=created_at,
                output_writer=turn_progress_buffer.append,
            )
            _emit_interactive_conversation_progress(
                binding_capture=progress_binding_capture,
                stage=CONVERSATIONAL_PROGRESS_REPLAY,
                activity="Conversation progress replay recorded.",
                snapshot_at=created_at,
                output_writer=turn_progress_buffer.append,
                runtime_status=CONVERSATIONAL_PROGRESS_COMPLETED,
            )
            failure_output = [line for line in turn_output_buffer if line.startswith("FAILED_CLOSED:")]
            normal_output = [line for line in turn_output_buffer if not line.startswith("FAILED_CLOSED:")]
            completion_capture = _record_interactive_turn_completion(
                session_id=session_id,
                turn_id=turn_id,
                prompt_id=prompt_id,
                turn_summary=turns[-1],
                progress_binding_capture=progress_binding_capture,
                turn_root=turn_root,
                created_at=created_at,
                elapsed_seconds=_interactive_turn_elapsed_seconds(
                    turn_started_monotonic=turn_started_monotonic,
                    monotonic_now=monotonic_now,
                ),
                delivered_output_line_count=_delivered_output_line_count(
                    "\n".join(turn_progress_buffer + normal_output + failure_output + [workflow_status_output]),
                ),
            )
            hardening_capture = _record_interactive_hardening_capture(
                session_id=session_id,
                turn_id=turn_id,
                prompt_id=prompt_id,
                turn_summary=turns[-1],
                completion_capture=completion_capture,
                session_root=session_root,
                turn_root=turn_root,
                created_at=created_at,
            )
            if turns[-1].get("fail_closed") is not True:
                normal_output.append(hardening_capture["operator_summary"])
                normal_output.append(completion_capture["operator_completion_summary"])
                normal_output.append(workflow_status_output)
            rendered_normal_output = "\n".join(turn_progress_buffer + normal_output)
            terminal_output_writer(rendered_normal_output)
            if turns[-1].get("fail_closed") is True:
                terminal_output_writer(hardening_capture["operator_summary"])
                terminal_output_writer(completion_capture["operator_completion_summary"])
                for failure_line in failure_output:
                    terminal_output_writer(failure_line)
                terminal_output_writer(workflow_status_output)
            else:
                for failure_line in failure_output:
                    terminal_output_writer(failure_line)
            output_writer = terminal_output_writer
            if auto_continue_enabled:
                certified_action = _certified_auto_continuation_action(workflow_status)
                if certified_action is not None:
                    pending_auto_continuation = certified_action
                else:
                    auto_continue_stop_reason = _auto_continue_stop_reason(workflow_status)
        except Exception as exc:
            output_writer = terminal_output_writer
            failed_turns += 1
            failure_reason = str(exc) or "interactive conversation failed closed"
            if progress_binding_capture is not None:
                try:
                    _emit_interactive_conversation_progress(
                        binding_capture=progress_binding_capture,
                        stage=CONVERSATIONAL_PROGRESS_REPLAY,
                        activity=f"Conversation failed closed: {failure_reason}",
                        snapshot_at=created_at,
                        output_writer=turn_progress_buffer.append,
                        runtime_status=CONVERSATIONAL_PROGRESS_FAILED_CLOSED,
                    )
                except Exception:
                    pass
            if turn_progress_buffer:
                output_writer("\n".join(turn_progress_buffer))
            failed_summary = _interactive_failed_turn_summary(
                turn_id=turn_id,
                prompt_id=prompt_id,
                source_router_replay_reference=str(turn_root / "source_router"),
                failure_reason=failure_reason,
            )
            _attach_interactive_universal_intake(
                turn_summary=failed_summary,
                universal_intake_capture=universal_intake_capture,
            )
            failed_summary["operator_prompt"] = human_prompt
            failed_summary["operator_prompt_lines"] = list(prompt_capture["prompt_lines"])
            failed_workflow_status = _attach_interactive_workflow_status(failed_summary)
            _ensure_interactive_chain_inspection_commands(failed_summary)
            latest_workflow_status = failed_workflow_status
            if progress_binding_capture is not None:
                try:
                    completion_capture = _record_interactive_turn_completion(
                        session_id=session_id,
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        turn_summary=failed_summary,
                        progress_binding_capture=progress_binding_capture,
                        turn_root=turn_root,
                        created_at=created_at,
                        elapsed_seconds=_interactive_turn_elapsed_seconds(
                            turn_started_monotonic=turn_started_monotonic,
                            monotonic_now=monotonic_now,
                        ),
                        delivered_output_line_count=_delivered_output_line_count(
                            "\n".join(turn_progress_buffer + [f"FAILED_CLOSED: {failure_reason}"])
                        ),
                    )
                    hardening_capture = _record_interactive_hardening_capture(
                        session_id=session_id,
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        turn_summary=failed_summary,
                        completion_capture=completion_capture,
                        session_root=session_root,
                        turn_root=turn_root,
                        created_at=created_at,
                    )
                    output_writer(hardening_capture["operator_summary"])
                    output_writer(completion_capture["operator_completion_summary"])
                except Exception:
                    pass
            output_writer(f"FAILED_CLOSED: {failure_reason}")
            output_writer(_render_interactive_workflow_status(failed_workflow_status))
            turns.append(failed_summary)

    return {
        "command": "aigol conversation",
        "interactive_conversation_cli_version": INTERACTIVE_CONVERSATION_CLI_VERSION,
        "session_id": session_id,
        "turn_count": turn_count,
        "failed_turns": failed_turns,
        "exit_reason": exit_reason,
        "runtime_root": str(session_root),
        "session_resumed": initial_resume["session_resumed"],
        "existing_turn_count": initial_resume["existing_turn_count"],
        "next_turn_id_at_start": initial_resume["next_turn_id"],
        "auto_continue_enabled": auto_continue_enabled,
        "auto_continue_turns": auto_continue_turns,
        "auto_continue_stop_reason": auto_continue_stop_reason,
        "current_chain_id": current_chain_id,
        "latest_chain_id": latest_chain_id,
        "replay_visible": True,
        "worker_assigned": any(turn.get("worker_assigned") is True for turn in turns),
        "worker_dispatched": any(turn.get("worker_dispatched") is True for turn in turns),
        "worker_invoked": any(turn.get("worker_invoked") is True for turn in turns),
        "execution_started": any(turn.get("execution_started") is True for turn in turns),
        "worker_result_captured": any(turn.get("worker_result_captured") is True for turn in turns),
        "worker_result_validated": any(turn.get("worker_result_validated") is True for turn in turns),
        "output_bound": any(turn.get("output_bound") is True for turn in turns),
        "artifact_created": any(turn.get("artifact_created") is True for turn in turns),
        "artifact_verified": any(turn.get("artifact_verified") is True for turn in turns),
        "bundle_authorized": any(turn.get("bundle_authorized") is True for turn in turns),
        "artifacts_created": any(turn.get("artifacts_created") is True for turn in turns),
        "bundle_verified": any(turn.get("bundle_verified") is True for turn in turns),
        "executable_bundle_authorized": any(turn.get("executable_bundle_authorized") is True for turn in turns),
        "executable_bundle_verified": any(turn.get("executable_bundle_verified") is True for turn in turns),
        "post_execution_replay_reviewed": any(
            turn.get("post_execution_replay_reviewed") is True for turn in turns
        ),
        "terminated": any(turn.get("terminated") is True for turn in turns),
        "hardening_recorded": any(turn.get("hardening_recorded") is True for turn in turns),
        "hardening_event_count": sum(1 for turn in turns if turn.get("hardening_recorded") is True),
        "hardening_metrics_reference": next(
            (turn.get("hardening_metrics_reference") for turn in reversed(turns) if turn.get("hardening_metrics_reference")),
            None,
        ),
        "execution_requested": any(turn.get("execution_started") is True for turn in turns),
        "dispatch_requested": any(turn.get("dispatch_requested") is True for turn in turns),
        "invocation_requested": any(turn.get("invocation_requested") is True for turn in turns),
        "turns": turns,
    }


def _interactive_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversation_capture: dict[str, Any],
    source_router_replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": conversation_capture.get("response_status"),
        "response_source": conversation_capture.get("response_source"),
        "fail_closed": conversation_capture.get("fail_closed") is True,
        "failure_reason": failure_reason,
        "replay_reference": conversation_capture.get("replay_reference"),
        "conversation_replay_reference": conversation_capture.get("conversation_replay_reference"),
        "canonical_chain_id": conversation_capture.get("canonical_chain_id"),
        "current_chain_id": conversation_capture.get("current_chain_id"),
        "latest_chain_id": conversation_capture.get("latest_chain_id"),
        "related_chain_id": conversation_capture.get("related_chain_id"),
        "suggested_inspection_commands": conversation_capture.get("suggested_inspection_commands", []),
        "conversation_chain_continuity_replay_reference": conversation_capture.get(
            "conversation_chain_continuity_replay_reference"
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }


def _interactive_deterministic_conversation_submit_override_active() -> bool:
    """Return whether the deterministic conversation test seam is active."""

    if getattr(submit_prompt_to_conversation, "__module__", "") == (
        "aigol.runtime.prompt_to_conversation_integration"
    ):
        return False
    return getattr(submit_prompt_to_conversation, "__name__", "") == "deterministic_conversation"


def _ensure_interactive_chain_inspection_commands(turn_summary: dict[str, Any]) -> None:
    """Attach replay inspection hints to summaries that carry a canonical chain."""

    if "suggested_inspection_commands" in turn_summary:
        return
    chain_id = turn_summary.get("canonical_chain_id") or turn_summary.get("current_chain_id")
    if not isinstance(chain_id, str) or not chain_id.strip():
        turn_summary["suggested_inspection_commands"] = []
        return
    normalized = chain_id.strip()
    turn_summary["suggested_inspection_commands"] = [
        f"show-chain {normalized}",
        f"show-full-lineage {normalized}",
        f"show-learning-lifecycle {normalized}",
    ]


def _interactive_failed_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    source_router_replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": "FAILED_CLOSED",
        "selection_reason": "Interactive conversation failed closed before a complete turn could be returned.",
        "response_status": "FAILED_CLOSED",
        "response_source": "UNAVAILABLE",
        "fail_closed": True,
        "failure_reason": failure_reason,
        "replay_reference": None,
        "conversation_replay_reference": None,
        "canonical_chain_id": None,
        "current_chain_id": None,
        "latest_chain_id": None,
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }


def _interactive_unknown_domain_clarification_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    clarification_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    unknown = clarification_capture.get("unknown_domain_artifact")
    if not isinstance(unknown, dict):
        unknown = {}
    request = clarification_capture.get("clarification_request_artifact")
    if not isinstance(request, dict):
        request = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": clarification_capture.get("response_status"),
        "response_source": clarification_capture.get("response_source"),
        "fail_closed": clarification_capture.get("fail_closed") is True,
        "failure_reason": clarification_capture.get("failure_reason"),
        "replay_reference": clarification_capture.get("unknown_domain_replay_reference"),
        "conversation_replay_reference": clarification_capture.get("conversation_replay_reference"),
        "canonical_chain_id": clarification_capture.get("canonical_chain_id"),
        "current_chain_id": clarification_capture.get("current_chain_id"),
        "latest_chain_id": clarification_capture.get("latest_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "unknown_domain_status": unknown.get("unknown_domain_status"),
        "originating_intent": request.get("originating_intent") or unknown.get("originating_intent"),
        "proposed_domain": request.get("proposed_domain") or unknown.get("proposed_domain"),
        "requested_domain": unknown.get("requested_domain"),
        "missing_information": request.get("missing_information", []),
        "clarification_required": clarification_capture.get("response_status")
        == UNKNOWN_DOMAIN_CLARIFICATION_REQUIRED,
        "unknown_domain_artifact_type": unknown.get("artifact_type"),
        "clarification_request_artifact_type": request.get("artifact_type"),
        "conversational_workflow_id": (conversational_routing_capture or {}).get("workflow_id"),
        "conversational_cli_routing_replay_reference": (conversational_routing_capture or {}).get(
            "conversational_cli_routing_replay_reference"
        ),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _render_domain_proposal_acceptance_summary(domain_proposal_capture: dict[str, Any]) -> str:
    proposal = domain_proposal_capture.get("domain_proposal_artifact")
    if not isinstance(proposal, dict):
        proposal = {}
    return "\n".join(
        [
            "Domain Proposal",
            "",
            f"proposal_status: {domain_proposal_capture.get('proposal_status')}",
            f"proposed_domain: {proposal.get('proposed_domain')}",
            f"approval_required: {str(proposal.get('approval_required') is True).lower()}",
            f"domain_created: {str(proposal.get('domain_created') is True).lower()}",
            f"worker_invoked: {str(proposal.get('worker_invoked') is True).lower()}",
            f"replay_reference: {domain_proposal_capture.get('domain_proposal_replay_reference')}",
        ]
    )


def _render_domain_proposal_review_summary(domain_review_capture: dict[str, Any]) -> str:
    review = domain_review_capture.get("domain_review_decision_artifact")
    if not isinstance(review, dict):
        review = {}
    outcome = domain_review_capture.get("domain_review_outcome_artifact")
    if not isinstance(outcome, dict):
        outcome = {}
    return "\n".join(
        [
            "Domain Proposal Review",
            "",
            f"review_status: {domain_review_capture.get('review_status')}",
            f"proposed_domain: {review.get('proposed_domain') or outcome.get('proposed_domain')}",
            f"domain_candidate_created: {str(domain_review_capture.get('domain_candidate_created') is True).lower()}",
            f"domain_created: {str(domain_review_capture.get('domain_created') is True).lower()}",
            f"worker_invoked: {str(outcome.get('worker_invoked') is True).lower()}",
            f"required_next_step: {outcome.get('required_next_step')}",
            f"replay_reference: {domain_review_capture.get('domain_review_replay_reference')}",
        ]
    )


def _is_domain_candidate_continuation_prompt(human_prompt: str) -> bool:
    normalized = " ".join(human_prompt.lower().split())
    if "continue" not in normalized:
        return False
    return any(
        marker in normalized
        for marker in (
            "next governed step",
            "next step",
            "governed step",
            "continue with",
            "continue the",
        )
    )


def _domain_proposal_review_decision(human_prompt: str, human_decision: str) -> str | None:
    if human_decision == APPROVE:
        return DOMAIN_PROPOSAL_APPROVED
    if human_decision in {REJECT, REQUEST_MODIFICATION}:
        return DOMAIN_PROPOSAL_REJECTED
    normalized = " ".join(human_prompt.lower().split())
    if any(marker in normalized for marker in ("reject", "do not approve", "decline")) and "proposal" in normalized:
        return DOMAIN_PROPOSAL_REJECTED
    if "approve" in normalized and "proposal" in normalized:
        return DOMAIN_PROPOSAL_APPROVED
    return None


def _record_domain_candidate_continuation_boundary(
    *,
    boundary_id: str,
    domain_review_capture: dict[str, Any],
    operator_prompt: str,
    created_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    review = domain_review_capture.get("domain_review_decision_artifact")
    if not isinstance(review, dict):
        review = {}
    outcome = domain_review_capture.get("domain_review_outcome_artifact")
    if not isinstance(outcome, dict):
        outcome = {}
    artifact = {
        "artifact_type": "DOMAIN_CANDIDATE_CONTINUATION_BOUNDARY_ARTIFACT_V1",
        "boundary_id": boundary_id,
        "response_status": "WAITING_FOR_SEPARATE_DOMAIN_CREATION_AUTHORIZATION",
        "operator_prompt": operator_prompt,
        "domain_review_reference": outcome.get("domain_review_reference") or review.get("domain_review_id"),
        "domain_review_hash": outcome.get("domain_review_hash") or review.get("artifact_hash"),
        "domain_candidate_reference": outcome.get("domain_candidate_id"),
        "domain_candidate_hash": outcome.get("artifact_hash"),
        "proposed_domain": outcome.get("proposed_domain") or review.get("proposed_domain"),
        "canonical_chain_id": outcome.get("canonical_chain_id") or review.get("canonical_chain_id"),
        "required_next_step": "SEPARATE_DOMAIN_CREATION_AUTHORIZATION",
        "conversation_state_preserved": True,
        "replay_lineage_preserved": domain_review_capture.get("replay_lineage_preserved") is True,
        "authorization_boundary_preserved": True,
        "manual_routing_used": False,
        "manual_artifact_lookup_used": False,
        "domain_created": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    replay_dir.mkdir(parents=True, exist_ok=True)
    wrapper = {
        "step": "domain_candidate_continuation_boundary_recorded",
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / "000_domain_candidate_continuation_boundary_recorded.json", wrapper)
    capture = {
        "response_source": "DOMAIN_CANDIDATE_CONTINUATION_BOUNDARY",
        "response_status": artifact["response_status"],
        "domain_candidate_continuation_boundary_artifact": artifact,
        "domain_candidate_continuation_replay_reference": str(replay_dir),
        "conversation_state_preserved": True,
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "authorization_boundary_preserved": True,
        "fail_closed": False,
        "failure_reason": None,
    }
    capture["domain_candidate_continuation_capture_hash"] = replay_hash(capture)
    return capture


def _render_domain_candidate_continuation_boundary_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("domain_candidate_continuation_boundary_artifact")
    if not isinstance(artifact, dict):
        artifact = {}
    return "\n".join(
        [
            "Domain Candidate Continuation",
            "",
            f"response_status: {capture.get('response_status')}",
            f"proposed_domain: {artifact.get('proposed_domain')}",
            f"required_next_step: {artifact.get('required_next_step')}",
            f"authorization_boundary_preserved: {str(artifact.get('authorization_boundary_preserved') is True).lower()}",
            f"domain_created: {str(artifact.get('domain_created') is True).lower()}",
            f"worker_invoked: {str(artifact.get('worker_invoked') is True).lower()}",
            f"replay_reference: {capture.get('domain_candidate_continuation_replay_reference')}",
        ]
    )


def _interactive_domain_proposal_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    domain_proposal_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    proposal = domain_proposal_capture.get("domain_proposal_artifact")
    if not isinstance(proposal, dict):
        proposal = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": domain_proposal_capture.get("proposal_status"),
        "response_source": "DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME",
        "fail_closed": domain_proposal_capture.get("fail_closed") is True,
        "failure_reason": domain_proposal_capture.get("failure_reason"),
        "replay_reference": domain_proposal_capture.get("domain_proposal_replay_reference"),
        "conversation_replay_reference": domain_proposal_capture.get("domain_proposal_replay_reference"),
        "canonical_chain_id": proposal.get("canonical_chain_id"),
        "current_chain_id": proposal.get("canonical_chain_id"),
        "latest_chain_id": proposal.get("canonical_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "domain_proposal_status": domain_proposal_capture.get("proposal_status"),
        "domain_proposal_artifact_type": proposal.get("artifact_type"),
        "domain_proposal_replay_reference": domain_proposal_capture.get("domain_proposal_replay_reference"),
        "proposed_domain": proposal.get("proposed_domain"),
        "domain_candidate_created": False,
        "approval_required": proposal.get("approval_required") is True,
        "approval_created": False,
        "approval_bypassed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "conversational_workflow_id": (conversational_routing_capture or {}).get("workflow_id"),
        "conversational_cli_routing_replay_reference": (conversational_routing_capture or {}).get(
            "conversational_cli_routing_replay_reference"
        ),
    }


def _interactive_domain_proposal_review_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    domain_review_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    review = domain_review_capture.get("domain_review_decision_artifact")
    if not isinstance(review, dict):
        review = {}
    outcome = domain_review_capture.get("domain_review_outcome_artifact")
    if not isinstance(outcome, dict):
        outcome = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": domain_review_capture.get("review_status"),
        "response_source": "DOMAIN_PROPOSAL_REVIEW_RUNTIME",
        "fail_closed": domain_review_capture.get("fail_closed") is True,
        "failure_reason": domain_review_capture.get("failure_reason"),
        "replay_reference": domain_review_capture.get("domain_review_replay_reference"),
        "conversation_replay_reference": domain_review_capture.get("domain_review_replay_reference"),
        "canonical_chain_id": outcome.get("canonical_chain_id") or review.get("canonical_chain_id"),
        "current_chain_id": outcome.get("canonical_chain_id") or review.get("canonical_chain_id"),
        "latest_chain_id": outcome.get("canonical_chain_id") or review.get("canonical_chain_id"),
        "related_chain_id": review.get("domain_proposal_reference"),
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": domain_review_capture.get("domain_review_replay_reference"),
        "source_router_replay_reference": source_router_replay_reference,
        "domain_review_status": domain_review_capture.get("review_status"),
        "domain_review_replay_reference": domain_review_capture.get("domain_review_replay_reference"),
        "domain_candidate_artifact_type": outcome.get("artifact_type"),
        "domain_candidate_created": domain_review_capture.get("domain_candidate_created") is True,
        "domain_candidate_reference": outcome.get("domain_candidate_id"),
        "proposed_domain": outcome.get("proposed_domain") or review.get("proposed_domain"),
        "approval_required": False,
        "approval_created": True,
        "approval_bypassed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_lineage_preserved": domain_review_capture.get("replay_lineage_preserved") is True,
    }


def _interactive_domain_candidate_continuation_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    continuation_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    artifact = continuation_capture.get("domain_candidate_continuation_boundary_artifact")
    if not isinstance(artifact, dict):
        artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": continuation_capture.get("response_status"),
        "response_source": continuation_capture.get("response_source"),
        "fail_closed": continuation_capture.get("fail_closed") is True,
        "failure_reason": continuation_capture.get("failure_reason"),
        "replay_reference": continuation_capture.get("domain_candidate_continuation_replay_reference"),
        "conversation_replay_reference": continuation_capture.get("domain_candidate_continuation_replay_reference"),
        "canonical_chain_id": artifact.get("canonical_chain_id"),
        "current_chain_id": artifact.get("canonical_chain_id"),
        "latest_chain_id": artifact.get("canonical_chain_id"),
        "related_chain_id": artifact.get("domain_review_reference"),
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": continuation_capture.get(
            "domain_candidate_continuation_replay_reference"
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "conversation_state_preserved": continuation_capture.get("conversation_state_preserved") is True,
        "replay_lineage_preserved": continuation_capture.get("replay_lineage_preserved") is True,
        "authorization_boundary_preserved": continuation_capture.get("authorization_boundary_preserved") is True,
        "domain_candidate_reference": artifact.get("domain_candidate_reference"),
        "proposed_domain": artifact.get("proposed_domain"),
        "required_next_step": artifact.get("required_next_step"),
        "approval_required": False,
        "approval_created": False,
        "approval_bypassed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_clarification_continuity_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    clarification_continuity_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    resume = clarification_continuity_capture.get("clarification_workflow_resume_artifact")
    if not isinstance(resume, dict):
        resume = {}
    handoff_review = clarification_continuity_capture.get("handoff_review")
    if not isinstance(handoff_review, dict):
        handoff_review = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": clarification_continuity_capture.get("response_status"),
        "response_source": clarification_continuity_capture.get("response_source"),
        "fail_closed": clarification_continuity_capture.get("fail_closed") is True,
        "failure_reason": clarification_continuity_capture.get("failure_reason"),
        "replay_reference": clarification_continuity_capture.get("clarification_continuity_replay_reference"),
        "conversation_replay_reference": clarification_continuity_capture.get("conversation_replay_reference"),
        "canonical_chain_id": clarification_continuity_capture.get("canonical_chain_id"),
        "current_chain_id": clarification_continuity_capture.get("current_chain_id"),
        "latest_chain_id": clarification_continuity_capture.get("latest_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "open_clarification_detected": clarification_continuity_capture.get("open_clarification_detected") is True,
        "operator_reply_bound": clarification_continuity_capture.get("operator_reply_bound") is True,
        "clarification_resolved": clarification_continuity_capture.get("clarification_resolved") is True,
        "workflow_resumed": clarification_continuity_capture.get("workflow_resumed") is True,
        "originating_workflow_id": clarification_continuity_capture.get("originating_workflow_id")
        or resume.get("originating_workflow_id"),
        "originating_intent": clarification_continuity_capture.get("originating_intent")
        or resume.get("originating_intent"),
        "proposed_domain": clarification_continuity_capture.get("proposed_domain") or resume.get("proposed_domain"),
        "handoff_review_decision": handoff_review.get("review_decision"),
        "handoff_review_reference": handoff_review.get("review_reference"),
        "handoff_review_replay_reference": handoff_review.get("handoff_review_replay_reference"),
        "handoff_review_next_certified_stage": handoff_review.get("next_certified_stage"),
        "clarification_continuity_artifact_type": (
            clarification_continuity_capture.get("clarification_reply_binding_artifact") or {}
        ).get("artifact_type"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_human_intent_clarification_continuity_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    continuity_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    post_clarification_ocs = continuity_capture.get("post_clarification_ocs_llm_cognition")
    if not isinstance(post_clarification_ocs, dict):
        post_clarification_ocs = {}
    provider_ids = continuity_capture.get("provider_ids")
    if not isinstance(provider_ids, list):
        provider_ids = []
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": continuity_capture.get("response_status"),
        "response_source": continuity_capture.get("response_source"),
        "response_text": continuity_capture.get("response_text"),
        "fail_closed": continuity_capture.get("fail_closed") is True,
        "failure_reason": continuity_capture.get("failure_reason"),
        "replay_reference": continuity_capture.get("human_intent_clarification_continuity_replay_reference"),
        "conversation_replay_reference": continuity_capture.get("conversation_replay_reference"),
        "canonical_chain_id": continuity_capture.get("canonical_chain_id"),
        "current_chain_id": continuity_capture.get("current_chain_id"),
        "latest_chain_id": continuity_capture.get("latest_chain_id"),
        "source_router_replay_reference": source_router_replay_reference,
        "open_clarification_detected": True,
        "operator_reply_bound": continuity_capture.get("clarification_response_bound") is True,
        "clarification_resolved": continuity_capture.get("intent_resolution_after_clarification") is True,
        "workflow_resumed": continuity_capture.get("workflow_selection_after_clarification") is True,
        "originating_workflow_id": continuity_capture.get("originating_workflow_id"),
        "intent_family": continuity_capture.get("intent_family"),
        "conversational_workflow_id": continuity_capture.get("workflow_id"),
        "workflow_id": continuity_capture.get("workflow_id"),
        "routing_status": continuity_capture.get("routing_status"),
        "ambiguity_escalation_reason": continuity_capture.get("ambiguity_escalation_reason"),
        "unresolved_ambiguity_classification": continuity_capture.get("unresolved_ambiguity_classification"),
        "proposal_only_cognition_routing": continuity_capture.get("proposal_only_cognition_routing") is True,
        "post_clarification_ocs_replay_reference": continuity_capture.get(
            "post_clarification_ocs_replay_reference"
        ),
        "provider_ids": provider_ids,
        "real_llm_provider_used_by_ocs": continuity_capture.get("real_llm_provider_used_by_ocs") is True,
        "live_provider_response_received": continuity_capture.get("live_provider_response_received") is True,
        "human_confirmation_required": continuity_capture.get("human_confirmation_required") is True,
        "future_deterministic_rule_candidate_status": continuity_capture.get(
            "future_deterministic_rule_candidate_status"
        ),
        "provider_invoked": continuity_capture.get("provider_invoked") is True,
        "ocs_llm_cognition_final_status": post_clarification_ocs.get("final_status"),
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_approval_binding_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    domain_approval_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": domain_approval_capture.get("approval_status"),
        "response_source": "DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY",
        "fail_closed": domain_approval_capture.get("fail_closed") is True,
        "failure_reason": domain_approval_capture.get("failure_reason"),
        "replay_reference": domain_approval_capture.get("domain_approval_binding_replay_reference"),
        "canonical_chain_id": domain_approval_capture.get("canonical_chain_id"),
        "current_chain_id": domain_approval_capture.get("canonical_chain_id"),
        "latest_chain_id": domain_approval_capture.get("canonical_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "source_router_replay_reference": source_router_replay_reference,
        "approval_status": domain_approval_capture.get("approval_status"),
        "approval_reference": domain_approval_capture.get("approval_reference"),
        "approved_domain": domain_approval_capture.get("approved_domain"),
        "authorization_entry_status": domain_approval_capture.get("authorization_entry_status"),
        "authorization_entry_reference": domain_approval_capture.get("authorization_entry_reference"),
        "execution_ready_continuation_status": domain_approval_capture.get(
            "execution_ready_continuation_status"
        ),
        "execution_ready_continuation_reference": domain_approval_capture.get(
            "execution_ready_continuation_reference"
        ),
        "next_runtime": domain_approval_capture.get("next_runtime"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "worker_request_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_execution_ready_bridge_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    execution_ready_bridge_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": execution_ready_bridge_capture.get("bridge_status"),
        "response_source": "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE",
        "fail_closed": execution_ready_bridge_capture.get("fail_closed") is True,
        "failure_reason": execution_ready_bridge_capture.get("failure_reason"),
        "replay_reference": execution_ready_bridge_capture.get("domain_execution_ready_bridge_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "approved_domain": execution_ready_bridge_capture.get("approved_domain"),
        "bridge_status": execution_ready_bridge_capture.get("bridge_status"),
        "execution_status": execution_ready_bridge_capture.get("execution_status"),
        "execution_ready_replay_reference": execution_ready_bridge_capture.get("execution_ready_replay_reference"),
        "execution_ready_replay_hash": execution_ready_bridge_capture.get("execution_ready_replay_hash"),
        "authorization_runtime_compatible": execution_ready_bridge_capture.get("authorization_runtime_compatible"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "worker_request_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_execution_authorization_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    execution_authorization_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": execution_authorization_capture.get("authorization_status"),
        "response_source": "DOMAIN_EXECUTION_AUTHORIZATION",
        "fail_closed": execution_authorization_capture.get("fail_closed") is True,
        "failure_reason": execution_authorization_capture.get("failure_reason"),
        "replay_reference": execution_authorization_capture.get("execution_authorization_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "execution_authorization_status": execution_authorization_capture.get("authorization_status"),
        "execution_authorization_replay_reference": execution_authorization_capture.get(
            "execution_authorization_replay_reference"
        ),
        "approved_domain": execution_authorization_capture.get("approved_domain"),
        "authorization_reference": execution_authorization_capture.get("authorization_reference"),
        "approval_status": execution_authorization_capture.get("approval_status"),
        "approval_reference": execution_authorization_capture.get("approval_reference"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": execution_authorization_capture.get("fail_closed") is not True,
        "worker_request_created": False,
        "execution_requested": False,
        "execution_started": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_request_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    worker_request_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": worker_request_capture.get("request_status"),
        "response_source": "DOMAIN_WORKER_REQUEST",
        "fail_closed": worker_request_capture.get("fail_closed") is True,
        "failure_reason": worker_request_capture.get("failure_reason"),
        "replay_reference": worker_request_capture.get("worker_invocation_request_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_invocation_request_status": worker_request_capture.get("request_status"),
        "worker_invocation_request_replay_reference": worker_request_capture.get(
            "worker_invocation_request_replay_reference"
        ),
        "worker_invocation_request_reference": worker_request_capture.get("worker_invocation_request_reference"),
        "approved_domain": worker_request_capture.get("approved_domain"),
        "authorization_reference": worker_request_capture.get("authorization_reference"),
        "execution_packet_reference": worker_request_capture.get("execution_packet_reference"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "worker_request_created": worker_request_capture.get("fail_closed") is not True,
        "worker_assigned": False,
        "worker_dispatched": False,
        "execution_requested": False,
        "execution_started": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_assignment_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    worker_assignment_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": worker_assignment_capture.get("assignment_status"),
        "response_source": "DOMAIN_WORKER_ASSIGNMENT",
        "fail_closed": worker_assignment_capture.get("fail_closed") is True,
        "failure_reason": worker_assignment_capture.get("failure_reason"),
        "replay_reference": worker_assignment_capture.get("worker_assignment_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_assignment_status": worker_assignment_capture.get("assignment_status"),
        "worker_assignment_replay_reference": worker_assignment_capture.get("worker_assignment_replay_reference"),
        "worker_assignment_reference": worker_assignment_capture.get("worker_assignment_reference"),
        "approved_domain": worker_assignment_capture.get("approved_domain"),
        "worker_id": worker_assignment_capture.get("worker_id"),
        "worker_family": worker_assignment_capture.get("worker_family"),
        "worker_role": worker_assignment_capture.get("worker_role"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": worker_assignment_capture.get("fail_closed") is not True,
        "worker_dispatched": False,
        "execution_requested": False,
        "execution_started": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_dispatch_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    worker_dispatch_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": worker_dispatch_capture.get("dispatch_status"),
        "response_source": "DOMAIN_WORKER_DISPATCH",
        "fail_closed": worker_dispatch_capture.get("fail_closed") is True,
        "failure_reason": worker_dispatch_capture.get("failure_reason"),
        "replay_reference": worker_dispatch_capture.get("worker_dispatch_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_dispatch_status": worker_dispatch_capture.get("dispatch_status"),
        "worker_dispatch_replay_reference": worker_dispatch_capture.get("worker_dispatch_replay_reference"),
        "worker_dispatch_reference": worker_dispatch_capture.get("worker_dispatch_reference"),
        "worker_assignment_reference": worker_dispatch_capture.get("worker_assignment_reference"),
        "approved_domain": worker_dispatch_capture.get("approved_domain"),
        "worker_id": worker_dispatch_capture.get("worker_id"),
        "worker_family": worker_dispatch_capture.get("worker_family"),
        "worker_role": worker_dispatch_capture.get("worker_role"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": worker_dispatch_capture.get("fail_closed") is not True,
        "worker_dispatched": worker_dispatch_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_invocation_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    worker_invocation_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": worker_invocation_capture.get("invocation_status"),
        "response_source": "DOMAIN_WORKER_INVOCATION",
        "fail_closed": worker_invocation_capture.get("fail_closed") is True,
        "failure_reason": worker_invocation_capture.get("failure_reason"),
        "replay_reference": worker_invocation_capture.get("worker_invocation_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_invocation_status": worker_invocation_capture.get("invocation_status"),
        "worker_invocation_replay_reference": worker_invocation_capture.get("worker_invocation_replay_reference"),
        "worker_invocation_reference": worker_invocation_capture.get("worker_invocation_reference"),
        "worker_dispatch_reference": worker_invocation_capture.get("worker_dispatch_reference"),
        "worker_assignment_reference": worker_invocation_capture.get("worker_assignment_reference"),
        "approved_domain": worker_invocation_capture.get("approved_domain"),
        "worker_id": worker_invocation_capture.get("worker_id"),
        "worker_family": worker_invocation_capture.get("worker_family"),
        "worker_role": worker_invocation_capture.get("worker_role"),
        "provider_invoked": False,
        "worker_invoked": worker_invocation_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": worker_invocation_capture.get("fail_closed") is not True,
        "worker_dispatched": worker_invocation_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_execution_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    execution_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    execution_artifact = execution_capture.get("execution_artifact")
    if not isinstance(execution_artifact, dict):
        execution_artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": execution_artifact.get("execution_status"),
        "response_source": "DOMAIN_WORKER_EXECUTION",
        "fail_closed": execution_capture.get("fail_closed") is True,
        "failure_reason": execution_capture.get("failure_reason"),
        "replay_reference": execution_artifact.get("replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "execution_runtime_status": execution_artifact.get("execution_status"),
        "execution_runtime_replay_reference": execution_artifact.get("replay_reference"),
        "execution_reference": execution_artifact.get("execution_id"),
        "execution_hash": execution_artifact.get("artifact_hash"),
        "domain_name": execution_capture.get("domain_name"),
        "worker_invocation_reference": execution_artifact.get("worker_invocation_reference"),
        "worker_dispatch_reference": execution_artifact.get("dispatch_reference"),
        "worker_assignment_reference": execution_artifact.get("worker_assignment_reference"),
        "worker_id": execution_artifact.get("worker_reference"),
        "provider_invoked": False,
        "worker_invoked": execution_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": execution_capture.get("fail_closed") is not True,
        "worker_dispatched": execution_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": execution_artifact.get("execution_started") is True,
        "domain_created": False,
        "worker_result_captured": False,
        "worker_result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_result_capture_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    result_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    capture_artifact = result_capture.get("worker_result_capture_artifact")
    if not isinstance(capture_artifact, dict):
        capture_artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": capture_artifact.get("result_capture_status"),
        "response_source": "DOMAIN_WORKER_RESULT_CAPTURE",
        "fail_closed": result_capture.get("fail_closed") is True,
        "failure_reason": result_capture.get("failure_reason"),
        "replay_reference": result_capture.get("worker_result_capture_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_result_capture_status": capture_artifact.get("result_capture_status"),
        "worker_result_capture_replay_reference": result_capture.get("worker_result_capture_replay_reference"),
        "worker_result_capture_reference": capture_artifact.get("worker_result_capture_id"),
        "domain_name": result_capture.get("domain_name"),
        "execution_reference": capture_artifact.get("execution_reference"),
        "execution_hash": capture_artifact.get("execution_hash"),
        "worker_invocation_reference": capture_artifact.get("worker_invocation_reference"),
        "worker_dispatch_reference": capture_artifact.get("worker_dispatch_reference"),
        "worker_id": capture_artifact.get("worker_id"),
        "provider_invoked": False,
        "worker_invoked": result_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": result_capture.get("fail_closed") is not True,
        "worker_dispatched": result_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": capture_artifact.get("execution_started") is True,
        "domain_created": False,
        "worker_result_captured": capture_artifact.get("result_capture_status") == "WORKER_RESULT_CAPTURED",
        "worker_result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_worker_result_validation_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    validation_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    validation_artifact = validation_capture.get("worker_result_validation_artifact")
    if not isinstance(validation_artifact, dict):
        validation_artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": validation_capture.get("validation_status"),
        "response_source": "DOMAIN_WORKER_RESULT_VALIDATION",
        "fail_closed": validation_capture.get("fail_closed") is True,
        "failure_reason": validation_capture.get("failure_reason"),
        "replay_reference": validation_capture.get("worker_result_validation_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "worker_result_validation_status": validation_capture.get("validation_status"),
        "worker_result_validation_replay_reference": validation_capture.get(
            "worker_result_validation_replay_reference"
        ),
        "worker_result_validation_reference": validation_capture.get("worker_result_validation_reference"),
        "worker_result_capture_reference": validation_capture.get("worker_result_capture_reference"),
        "domain_name": validation_capture.get("domain_name"),
        "execution_reference": validation_capture.get("execution_reference"),
        "execution_hash": validation_capture.get("execution_hash"),
        "worker_id": validation_capture.get("worker_id"),
        "provider_invoked": False,
        "worker_invoked": validation_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": validation_capture.get("fail_closed") is not True,
        "worker_dispatched": validation_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": validation_artifact.get("execution_started") is True,
        "domain_created": False,
        "worker_result_captured": validation_capture.get("fail_closed") is not True,
        "worker_result_validated": validation_capture.get("validation_status") == "RESULT_VALIDATED",
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_post_execution_replay_review_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    review_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    review_artifact = review_capture.get("post_execution_replay_review_artifact")
    if not isinstance(review_artifact, dict):
        review_artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": review_capture.get("review_status"),
        "response_source": "DOMAIN_POST_EXECUTION_REPLAY_REVIEW",
        "fail_closed": review_capture.get("fail_closed") is True,
        "failure_reason": review_capture.get("failure_reason"),
        "replay_reference": review_capture.get("post_execution_replay_review_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "post_execution_replay_review_status": review_capture.get("review_status"),
        "post_execution_replay_review_replay_reference": review_capture.get(
            "post_execution_replay_review_replay_reference"
        ),
        "post_execution_replay_review_reference": review_capture.get("post_execution_replay_review_reference"),
        "worker_result_validation_reference": review_capture.get("worker_result_validation_reference"),
        "domain_name": review_capture.get("domain_name"),
        "execution_reference": review_capture.get("execution_reference"),
        "execution_hash": review_capture.get("execution_hash"),
        "worker_id": review_capture.get("worker_id"),
        "provider_invoked": False,
        "worker_invoked": review_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": review_capture.get("fail_closed") is not True,
        "worker_dispatched": review_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": review_artifact.get("execution_started") is True,
        "domain_created": False,
        "worker_result_captured": review_capture.get("fail_closed") is not True,
        "worker_result_validated": review_capture.get("fail_closed") is not True,
        "post_execution_replay_reviewed": review_capture.get("review_status") == "REVIEW_COMPLETED",
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_governed_termination_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None,
    termination_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_selection = (conversational_routing_capture or {}).get("workflow_selection_artifact", {})
    termination_artifact = termination_capture.get("governed_termination_artifact")
    if not isinstance(termination_artifact, dict):
        termination_artifact = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": termination_capture.get("termination_status"),
        "response_source": "DOMAIN_GOVERNED_TERMINATION",
        "fail_closed": termination_capture.get("fail_closed") is True,
        "failure_reason": termination_capture.get("failure_reason"),
        "replay_reference": termination_capture.get("governed_termination_replay_reference"),
        "conversational_workflow_id": workflow_selection.get("workflow_id"),
        "conversational_routing_replay_reference": (
            (conversational_routing_capture or {}).get("conversational_cli_routing_replay_reference")
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "governed_termination_status": termination_capture.get("termination_status"),
        "governed_termination_replay_reference": termination_capture.get("governed_termination_replay_reference"),
        "governed_termination_reference": termination_capture.get("governed_termination_reference"),
        "post_execution_replay_review_reference": termination_capture.get("post_execution_replay_review_reference"),
        "domain_name": termination_capture.get("domain_name"),
        "execution_reference": termination_capture.get("execution_reference"),
        "execution_hash": termination_capture.get("execution_hash"),
        "worker_id": termination_capture.get("worker_id"),
        "provider_invoked": False,
        "worker_invoked": termination_capture.get("fail_closed") is not True,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": termination_capture.get("fail_closed") is not True,
        "worker_dispatched": termination_capture.get("fail_closed") is not True,
        "execution_requested": False,
        "execution_started": termination_artifact.get("execution_started") is True,
        "domain_created": False,
        "worker_result_captured": termination_capture.get("fail_closed") is not True,
        "worker_result_validated": termination_capture.get("fail_closed") is not True,
        "post_execution_replay_reviewed": termination_capture.get("fail_closed") is not True,
        "terminated": termination_capture.get("termination_status") == "TERMINATED",
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_domain_reference_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    domain_reference_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    reference = domain_reference_capture.get("domain_reference_artifact")
    if not isinstance(reference, dict):
        reference = {}
    similarity = domain_reference_capture.get("semantic_similarity_artifact")
    if not isinstance(similarity, dict):
        similarity = {}
    candidate = domain_reference_capture.get("domain_adaptation_candidate_artifact")
    if not isinstance(candidate, dict):
        candidate = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": domain_reference_capture.get("response_status"),
        "response_source": domain_reference_capture.get("response_source"),
        "fail_closed": domain_reference_capture.get("fail_closed") is True,
        "failure_reason": domain_reference_capture.get("failure_reason"),
        "replay_reference": domain_reference_capture.get("semantic_similarity_domain_reference_replay_reference"),
        "conversation_replay_reference": domain_reference_capture.get("conversation_replay_reference"),
        "canonical_chain_id": domain_reference_capture.get("canonical_chain_id"),
        "current_chain_id": domain_reference_capture.get("current_chain_id"),
        "latest_chain_id": domain_reference_capture.get("latest_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "conversational_workflow_id": (conversational_routing_capture or {}).get("workflow_id"),
        "conversational_cli_routing_replay_reference": (conversational_routing_capture or {}).get(
            "conversational_cli_routing_replay_reference"
        ),
        "domain_reference_artifact_type": reference.get("artifact_type"),
        "semantic_similarity_artifact_type": similarity.get("artifact_type"),
        "domain_adaptation_candidate_artifact_type": candidate.get("artifact_type"),
        "reference_status": reference.get("reference_status"),
        "candidate_status": candidate.get("candidate_status"),
        "source_domain": candidate.get("source_domain"),
        "target_domain": candidate.get("target_domain"),
        "operation": candidate.get("operation"),
        "missing_information": candidate.get("missing_information", []),
        "clarification_required": candidate.get("clarification_required") is True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_operator_decision_support_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    decision_support_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    recommendation = decision_support_capture.get("operator_decision_support_artifact")
    if not isinstance(recommendation, dict):
        recommendation = {}
    continuity_capture = decision_support_capture.get("recommendation_continuity")
    if not isinstance(continuity_capture, dict):
        continuity_capture = {}
    continuity = continuity_capture.get("recommendation_continuity_artifact")
    if not isinstance(continuity, dict):
        continuity = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": decision_support_capture.get("response_status"),
        "response_source": decision_support_capture.get("response_source"),
        "fail_closed": decision_support_capture.get("fail_closed") is True,
        "failure_reason": decision_support_capture.get("failure_reason"),
        "replay_reference": decision_support_capture.get("operator_decision_support_replay_reference"),
        "conversation_replay_reference": decision_support_capture.get("conversation_replay_reference"),
        "canonical_chain_id": decision_support_capture.get("canonical_chain_id"),
        "current_chain_id": decision_support_capture.get("current_chain_id"),
        "latest_chain_id": decision_support_capture.get("latest_chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "conversational_workflow_id": (conversational_routing_capture or {}).get("workflow_id"),
        "conversational_cli_routing_replay_reference": (conversational_routing_capture or {}).get(
            "conversational_cli_routing_replay_reference"
        ),
        "operator_decision_support_artifact_type": recommendation.get("artifact_type"),
        "recommendation_status": recommendation.get("recommendation_status"),
        "recommendation_category": recommendation.get("category"),
        "recommendation": recommendation.get("recommendation"),
        "alternatives": recommendation.get("alternatives", []),
        "risks": recommendation.get("risks", []),
        "confidence": recommendation.get("confidence"),
        "human_authority": recommendation.get("human_authority"),
        "recommendation_continuity_status": continuity.get("continuity_status"),
        "recommendation_continuity_reference": continuity.get("continuity_id"),
        "recommendation_continuity_replay_reference": continuity_capture.get(
            "recommendation_continuity_replay_reference"
        ),
        "followup_candidates": continuity.get("followup_candidates", []),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_recommendation_approval_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    recommendation_approval_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    approval = recommendation_approval_capture.get("recommendation_approval_artifact")
    if not isinstance(approval, dict):
        approval = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": recommendation_approval_capture.get("response_status"),
        "response_source": recommendation_approval_capture.get("response_source"),
        "fail_closed": recommendation_approval_capture.get("fail_closed") is True,
        "failure_reason": recommendation_approval_capture.get("failure_reason"),
        "replay_reference": recommendation_approval_capture.get("recommendation_approval_replay_reference"),
        "conversation_replay_reference": recommendation_approval_capture.get("conversation_replay_reference"),
        "source_router_replay_reference": source_router_replay_reference,
        "recommendation_reference": approval.get("recommendation_reference"),
        "continuity_reference": approval.get("continuity_reference"),
        "operator_decision": approval.get("operator_decision"),
        "approval_status": approval.get("approval_status"),
        "available_next_actions": approval.get("available_next_actions", []),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "implementation_authorized": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_recommendation_followup_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    recommendation_followup_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    followup = recommendation_followup_capture.get("recommendation_followup_artifact")
    if not isinstance(followup, dict):
        followup = {}
    candidate = followup.get("candidate")
    if not isinstance(candidate, dict):
        candidate = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": recommendation_followup_capture.get("response_status"),
        "response_source": recommendation_followup_capture.get("response_source"),
        "fail_closed": recommendation_followup_capture.get("fail_closed") is True,
        "failure_reason": recommendation_followup_capture.get("failure_reason"),
        "replay_reference": recommendation_followup_capture.get("recommendation_followup_replay_reference"),
        "conversation_replay_reference": recommendation_followup_capture.get("conversation_replay_reference"),
        "source_router_replay_reference": source_router_replay_reference,
        "recommendation_reference": followup.get("recommendation_reference"),
        "continuity_reference": followup.get("continuity_reference"),
        "approval_reference": followup.get("approval_reference"),
        "followup_action": followup.get("followup_action"),
        "candidate_status": followup.get("candidate_status"),
        "candidate_title": candidate.get("title"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "implementation_authorized": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_conversational_cli_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any],
    workflow_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": workflow_capture.get("response_status"),
        "response_source": workflow_capture.get("response_source"),
        "response_text": workflow_capture.get("response_text"),
        "fail_closed": workflow_capture.get("fail_closed") is True,
        "failure_reason": workflow_capture.get("failure_reason"),
        "replay_reference": conversational_routing_capture.get("conversational_cli_routing_replay_reference"),
        "conversation_replay_reference": conversational_routing_capture.get("conversational_cli_routing_replay_reference"),
        "canonical_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "current_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "latest_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "conversational_workflow_id": conversational_routing_capture.get("workflow_id"),
        "conversational_cli_routing_replay_reference": conversational_routing_capture.get(
            "conversational_cli_routing_replay_reference"
        ),
        "existing_runtime": conversational_routing_capture.get("workflow_selection_artifact", {}).get(
            "existing_runtime"
        ),
        "existing_cli_command": conversational_routing_capture.get("workflow_selection_artifact", {}).get(
            "existing_cli_command"
        ),
        "coverage": conversational_routing_capture.get("coverage"),
        "clarification_required": workflow_capture.get("existing_result", {}).get("clarification_required") is True,
        "open_clarification_detected": workflow_capture.get("existing_result", {}).get("clarification_required") is True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_acli_governed_development_bridge_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    bridge_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    workflow_capture = bridge_capture.get("workflow_capture") or {}
    bridge_status = bridge_capture.get("bridge_status")
    completed = bridge_status == ACLI_GOVERNED_DEVELOPMENT_EXECUTION_COMPLETED
    modification_requested = bridge_status == ACLI_GOVERNED_DEVELOPMENT_MODIFICATION_REQUESTED
    rejected = bridge_status == "REJECTED"
    authorization_created = (
        bridge_capture.get("approval_granted") is True
        and bridge_capture.get("execution_authorized", completed) is not False
    )
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": bridge_status,
        "response_source": "ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE",
        "response_text": render_acli_governed_development_bridge_summary(bridge_capture),
        "fail_closed": bridge_status == "FAILED_CLOSED",
        "failure_reason": bridge_capture.get("failure_reason"),
        "replay_reference": bridge_capture.get("replay_reference"),
        "conversation_replay_reference": bridge_capture.get("replay_reference"),
        "canonical_chain_id": prompt_id,
        "current_chain_id": prompt_id,
        "latest_chain_id": prompt_id,
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "conversational_workflow_id": bridge_capture.get("workflow_id"),
        "existing_runtime": "acli_governed_development_execution_bridge",
        "existing_cli_command": "aigol conversation",
        "coverage": None,
        "clarification_required": False,
        "open_clarification_detected": False,
        "provider_invoked": False,
        "worker_invoked": bridge_capture.get("worker_invoked") is True,
        "worker_assigned": False,
        "worker_dispatched": False,
        "authorization_created": authorization_created,
        "approval_required": (
            bridge_capture.get("approval_required") is True
            and not completed
            and not modification_requested
            and not rejected
        ),
        "operator_revision_requested": modification_requested,
        "execution_requested": completed,
        "execution_started": completed,
        "dispatch_requested": False,
        "invocation_requested": bridge_capture.get("worker_invoked") is True,
        "approval_bypassed": bridge_capture.get("approval_bypassed") is True,
        "governance_mutated": completed,
        "repository_mutation_performed": bridge_capture.get("mutation_performed") is True,
        "validation_executed": bridge_capture.get("validation_executed") is True,
        "replay_mutated": False,
        "governed_development_replay_reference": workflow_capture.get("governed_development_replay_reference"),
    }


def _interactive_ocs_llm_cognition_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    ocs_cognition_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    artifact = ocs_cognition_capture.get("ocs_llm_cognition_end_to_end_artifact")
    if not isinstance(artifact, dict):
        artifact = {}
    human_result = artifact.get("human_facing_cognition_result")
    if not isinstance(human_result, dict):
        human_result = {}
    stage_captures = ocs_cognition_capture.get("stage_captures")
    if not isinstance(stage_captures, dict):
        stage_captures = {}
    multi_provider_capture = stage_captures.get("multi_provider_cognition")
    if not isinstance(multi_provider_capture, dict):
        multi_provider_capture = {}
    request_bundle = multi_provider_capture.get("request_bundle")
    if not isinstance(request_bundle, dict):
        request_bundle = {}
    ocs_continuation = ocs_cognition_capture.get("ocs_certified_continuation")
    if not isinstance(ocs_continuation, dict):
        ocs_continuation = {}
    ocs_to_ppp = ocs_continuation.get("ocs_to_ppp_continuation")
    if not isinstance(ocs_to_ppp, dict):
        ocs_to_ppp = {}
    certified_worker_continuation = ocs_cognition_capture.get("certified_worker_continuation")
    if not isinstance(certified_worker_continuation, dict):
        certified_worker_continuation = {}
    worker_lifecycle = certified_worker_continuation.get("worker_lifecycle_continuation")
    if not isinstance(worker_lifecycle, dict):
        worker_lifecycle = {}
    worker_request = certified_worker_continuation.get("worker_invocation_request")
    if not isinstance(worker_request, dict):
        worker_request = {}
    worker_assignment = worker_lifecycle.get("worker_assignment")
    if not isinstance(worker_assignment, dict):
        worker_assignment = {}
    worker_dispatch = worker_lifecycle.get("worker_dispatch")
    if not isinstance(worker_dispatch, dict):
        worker_dispatch = {}
    worker_invocation = worker_lifecycle.get("worker_invocation")
    if not isinstance(worker_invocation, dict):
        worker_invocation = {}
    execution_candidate = worker_lifecycle.get("worker_execution_candidate")
    if not isinstance(execution_candidate, dict):
        execution_candidate = {}
    external_task = worker_lifecycle.get("external_worker_task_package")
    if not isinstance(external_task, dict):
        external_task = {}
    openai_worker = worker_lifecycle.get("openai_external_worker_provider")
    if not isinstance(openai_worker, dict):
        openai_worker = {}
    result_validation = worker_lifecycle.get("result_validation")
    if not isinstance(result_validation, dict):
        result_validation = {}
    replay_certification = worker_lifecycle.get("replay_certification")
    if not isinstance(replay_certification, dict):
        replay_certification = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": ocs_cognition_capture.get("final_status"),
        "response_source": "OCS_LLM_COGNITION_END_TO_END",
        "fail_closed": ocs_cognition_capture.get("fail_closed") is True,
        "failure_reason": ocs_cognition_capture.get("failure_reason"),
        "replay_reference": ocs_cognition_capture.get("replay_reference"),
        "conversation_replay_reference": ocs_cognition_capture.get("replay_reference"),
        "canonical_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "current_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "latest_chain_id": conversational_routing_capture.get("routing_decision_artifact", {}).get(
            "canonical_chain_id"
        ),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "conversational_workflow_id": conversational_routing_capture.get("workflow_id"),
        "conversational_cli_routing_replay_reference": conversational_routing_capture.get(
            "conversational_cli_routing_replay_reference"
        ),
        "existing_runtime": conversational_routing_capture.get("workflow_selection_artifact", {}).get(
            "existing_runtime"
        ),
        "existing_cli_command": conversational_routing_capture.get("workflow_selection_artifact", {}).get(
            "existing_cli_command"
        ),
        "ocs_proposal_only_preserved": ocs_cognition_capture.get("ocs_proposal_only_preserved") is True,
        "ocs_to_ppp_continuation_status": ocs_to_ppp.get("continuation_status"),
        "ocs_to_ppp_continuation_replay_reference": ocs_to_ppp.get("ocs_to_ppp_continuation_replay_reference"),
        "ppp_route_status": ocs_continuation.get("ppp_route_status"),
        "ppp_invoked": ocs_continuation.get("ppp_invoked") is True,
        "execution_authorization_status": certified_worker_continuation.get("execution_authorization", {}).get(
            "authorization_status"
        )
        if isinstance(certified_worker_continuation.get("execution_authorization"), dict)
        else None,
        "worker_invocation_request_status": worker_request.get("request_status"),
        "worker_invocation_request_replay_reference": worker_request.get(
            "worker_invocation_request_replay_reference"
        ),
        "worker_assignment_status": worker_assignment.get("assignment_status"),
        "worker_assignment_replay_reference": worker_assignment.get("worker_assignment_replay_reference"),
        "worker_dispatch_status": worker_dispatch.get("dispatch_status"),
        "worker_dispatch_replay_reference": worker_dispatch.get("worker_dispatch_replay_reference"),
        "worker_invocation_status": worker_invocation.get("invocation_status"),
        "worker_invocation_replay_reference": worker_invocation.get("worker_invocation_replay_reference"),
        "worker_execution_candidate_status": execution_candidate.get("candidate_status"),
        "worker_execution_candidate_replay_reference": execution_candidate.get(
            "worker_execution_candidate_replay_reference"
        ),
        "external_worker_task_status": external_task.get("task_status"),
        "external_worker_task_replay_reference": external_task.get("external_worker_replay_reference"),
        "openai_external_worker_status": openai_worker.get("worker_status"),
        "openai_external_worker_replay_reference": openai_worker.get("openai_external_worker_replay_reference"),
        "result_validation_status": result_validation.get("validation_status"),
        "result_validation_replay_reference": result_validation.get("result_validation_replay_reference"),
        "replay_certification_status": replay_certification.get("certification_status"),
        "replay_certification_replay_reference": replay_certification.get("replay_certification_replay_reference"),
        "worker_request_reached": certified_worker_continuation.get("worker_request_reached") is True,
        "worker_assignment_reached": worker_lifecycle.get("worker_assignment_reached") is True,
        "worker_dispatch_reached": worker_lifecycle.get("worker_dispatch_reached") is True,
        "worker_invocation_reached": worker_lifecycle.get("worker_invocation_reached") is True,
        "worker_execution_candidate_reached": worker_lifecycle.get("worker_execution_candidate_reached") is True,
        "external_task_package_reached": worker_lifecycle.get("external_task_package_reached") is True,
        "openai_provider_reached": worker_lifecycle.get("openai_provider_reached") is True,
        "result_validation_reached": worker_lifecycle.get("result_validation_reached") is True,
        "replay_certification_reached": worker_lifecycle.get("replay_certification_reached") is True,
        "replay_lineage_preserved": worker_lifecycle.get("replay_lineage_preserved") is True,
        "ocs_llm_cognition_artifact_type": artifact.get("artifact_type"),
        "context_hash": artifact.get("context_hash"),
        "provider_count": artifact.get("provider_count"),
        "successful_provider_count": artifact.get("successful_provider_count"),
        "provider_ids": request_bundle.get("deterministic_provider_order", []),
        "real_llm_provider_used_by_ocs": _real_llm_provider_used_by_ocs(ocs_cognition_capture),
        "cognition_artifact_count": len(artifact.get("cognition_artifact_hashes", [])),
        "single_provider_primary_mode": artifact.get("single_provider_primary_mode") is True,
        "comparison_required": artifact.get("comparison_required") is True,
        "comparison_performed": artifact.get("comparison_performed") is True,
        "comparison_artifact_hash": artifact.get("comparison_artifact_hash"),
        "continuity_artifact_hash": artifact.get("continuity_artifact_hash"),
        "clarification_artifact_hash": artifact.get("clarification_artifact_hash"),
        "comparison_confidence": human_result.get("comparison_confidence"),
        "clarification_required": ocs_cognition_capture.get(
            "clarification_required",
            human_result.get("clarification_required"),
        ),
        "clarification_candidate_count": human_result.get("clarification_candidate_count"),
        "approval_status": ocs_cognition_capture.get("approval_status"),
        "approval_required": ocs_cognition_capture.get("approval_required") is True,
        "stage_captures_present": sorted(stage_captures),
        "provider_invoked": ocs_cognition_capture.get("final_status") == OCS_LLM_COGNITION_COMPLETED,
        "worker_invoked": worker_lifecycle.get("worker_invocation_reached") is True,
        "authorization_created": certified_worker_continuation.get("execution_authorization", {}).get(
            "authorization_status"
        )
        is not None
        if isinstance(certified_worker_continuation.get("execution_authorization"), dict)
        else False,
        "execution_requested": worker_lifecycle.get("openai_provider_reached") is True,
        "approval_created": False,
        "approval_bypassed": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _interactive_native_development_intent_routing_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    routing_capture: dict[str, Any],
    conversational_routing_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    ppp_capture = routing_capture.get("conversation_to_ppp_handoff_execution")
    if not isinstance(ppp_capture, dict):
        ppp_capture = {}
    handoff_visibility = routing_capture.get("implementation_handoff_visibility")
    if not isinstance(handoff_visibility, dict):
        handoff_visibility = {}
    dry_run_capture = routing_capture.get("governed_implementation_dry_run")
    if not isinstance(dry_run_capture, dict):
        dry_run_capture = {}
    authorization_capture = routing_capture.get("execution_authorization")
    if not isinstance(authorization_capture, dict):
        authorization_capture = {}
    invocation_request_capture = routing_capture.get("worker_invocation_request")
    if not isinstance(invocation_request_capture, dict):
        invocation_request_capture = {}
    assignment_capture = routing_capture.get("worker_assignment")
    if not isinstance(assignment_capture, dict):
        assignment_capture = {}
    dispatch_capture = routing_capture.get("worker_dispatch")
    if not isinstance(dispatch_capture, dict):
        dispatch_capture = {}
    invocation_capture = routing_capture.get("worker_invocation")
    if not isinstance(invocation_capture, dict):
        invocation_capture = {}
    execution_capture = routing_capture.get("execution_runtime")
    if not isinstance(execution_capture, dict):
        execution_capture = {}
    execution_artifact = execution_capture.get("execution_artifact")
    if not isinstance(execution_artifact, dict):
        execution_artifact = {}
    result_capture = routing_capture.get("worker_result_capture")
    if not isinstance(result_capture, dict):
        result_capture = {}
    validation_capture = routing_capture.get("worker_result_validation")
    if not isinstance(validation_capture, dict):
        validation_capture = {}
    executable_bundle_capture = routing_capture.get("executable_bundle")
    if not isinstance(executable_bundle_capture, dict):
        executable_bundle_capture = {}
    review_capture = routing_capture.get("post_execution_replay_review")
    if not isinstance(review_capture, dict):
        review_capture = {}
    termination_capture = routing_capture.get("governed_termination")
    if not isinstance(termination_capture, dict):
        termination_capture = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": routing_capture.get("response_status"),
        "response_source": routing_capture.get("response_source"),
        "fail_closed": routing_capture.get("fail_closed") is True,
        "failure_reason": routing_capture.get("failure_reason"),
        "replay_reference": routing_capture.get("native_development_intent_routing_replay_reference"),
        "conversation_replay_reference": routing_capture.get("native_development_intent_routing_replay_reference"),
        "canonical_chain_id": routing_capture.get("canonical_chain_id"),
        "current_chain_id": routing_capture.get("current_chain_id"),
        "latest_chain_id": routing_capture.get("latest_chain_id"),
        "related_chain_id": routing_capture.get("related_chain_id"),
        "suggested_inspection_commands": routing_capture.get("suggested_inspection_commands", []),
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "native_development_intent_routing_replay_reference": routing_capture.get(
            "native_development_intent_routing_replay_reference"
        ),
        "conversational_workflow_id": (conversational_routing_capture or {}).get("workflow_id"),
        "conversational_cli_routing_replay_reference": (conversational_routing_capture or {}).get(
            "conversational_cli_routing_replay_reference"
        ),
        "intent_class": routing_capture.get("intent_class"),
        "target_domain": routing_capture.get("target_domain"),
        "target_resource": routing_capture.get("target_resource"),
        "target_provider": routing_capture.get("target_provider"),
        "target_worker_family": routing_capture.get("target_worker_family"),
        "target_milestone": routing_capture.get("target_milestone"),
        "next_pipeline_stage": routing_capture.get("next_pipeline_stage"),
        "conversation_to_ppp_terminal_status": ppp_capture.get("terminal_status"),
        "handoff_status": ppp_capture.get("handoff_status"),
        "handoff_reference": ppp_capture.get("handoff_reference"),
        "approval_status": ppp_capture.get("approval_status"),
        "proposal_validation_status": ppp_capture.get("proposal_validation_status"),
        "conversation_to_ppp_handoff_execution_replay_reference": ppp_capture.get(
            "conversation_to_ppp_handoff_execution_replay_reference"
        ),
        "implementation_handoff_visibility_replay_reference": handoff_visibility.get(
            "implementation_handoff_visibility_replay_reference"
        ),
        "implementation_handoff_summary_hash": handoff_visibility.get("summary_hash"),
        "execution_preparation_status": dry_run_capture.get("execution_status"),
        "governed_implementation_dry_run_replay_reference": dry_run_capture.get(
            "governed_implementation_dry_run_replay_reference"
        ),
        "execution_authorization_status": authorization_capture.get("authorization_status"),
        "execution_authorization_replay_reference": authorization_capture.get(
            "execution_authorization_replay_reference"
        ),
        "worker_invocation_request_status": invocation_request_capture.get("request_status"),
        "worker_invocation_request_replay_reference": invocation_request_capture.get(
            "worker_invocation_request_replay_reference"
        ),
        "worker_assignment_status": assignment_capture.get("assignment_status"),
        "worker_assignment_replay_reference": assignment_capture.get("worker_assignment_replay_reference"),
        "worker_dispatch_status": dispatch_capture.get("dispatch_status"),
        "worker_dispatch_replay_reference": dispatch_capture.get("worker_dispatch_replay_reference"),
        "worker_invocation_status": invocation_capture.get("invocation_status"),
        "worker_invocation_replay_reference": invocation_capture.get("worker_invocation_replay_reference"),
        "execution_runtime_status": execution_artifact.get("execution_status"),
        "execution_runtime_replay_reference": execution_artifact.get("replay_reference"),
        "execution_reference": execution_artifact.get("execution_id"),
        "execution_hash": execution_artifact.get("artifact_hash"),
        "worker_result_capture_status": result_capture.get("result_capture_status"),
        "worker_result_capture_replay_reference": result_capture.get("worker_result_capture_replay_reference"),
        "worker_result_validation_status": validation_capture.get("validation_status"),
        "worker_result_validation_replay_reference": validation_capture.get(
            "worker_result_validation_replay_reference"
        ),
        "executable_bundle_status": executable_bundle_capture.get("executable_bundle_verification_status"),
        "executable_bundle_replay_reference": executable_bundle_capture.get("executable_bundle_replay_reference"),
        "post_execution_replay_review_status": review_capture.get("review_status"),
        "post_execution_replay_review_replay_reference": review_capture.get(
            "post_execution_replay_review_replay_reference"
        ),
        "governed_termination_status": termination_capture.get("termination_status"),
        "governed_termination_replay_reference": termination_capture.get("governed_termination_replay_reference"),
        "recognized_development_task": routing_capture.get("routing_status") == NATIVE_DEVELOPMENT_INTENT_ROUTED,
        "worker_assigned": assignment_capture.get("assignment_status") == "WORKER_ASSIGNED",
        "worker_dispatched": dispatch_capture.get("dispatch_status") == "WORKER_DISPATCHED",
        "worker_invoked": invocation_capture.get("invocation_status") == "WORKER_INVOKED",
        "execution_started": execution_artifact.get("execution_started") is True,
        "worker_result_captured": result_capture.get("result_capture_status") == "WORKER_RESULT_CAPTURED",
        "worker_result_validated": validation_capture.get("validation_status") == "RESULT_VALIDATED",
        "executable_bundle_authorized": executable_bundle_capture.get("executable_bundle_authorization_status")
        == "EXECUTABLE_BUNDLE_AUTHORIZED",
        "artifacts_created": executable_bundle_capture.get("artifact_creation_status") == "ARTIFACTS_CREATED",
        "executable_bundle_verified": executable_bundle_capture.get("executable_bundle_verification_status")
        == "EXECUTABLE_BUNDLE_VERIFIED",
        "post_execution_replay_reviewed": review_capture.get("review_status") == "REVIEW_COMPLETED",
        "terminated": termination_capture.get("termination_status") == "TERMINATED",
        "execution_requested": False,
        "dispatch_requested": dispatch_capture.get("dispatch_status") == "WORKER_DISPATCHED",
        "invocation_requested": invocation_request_capture.get("request_status")
        == "WORKER_INVOCATION_REQUEST_CREATED",
    }


def _interactive_approval_resume_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    approval_resume_capture: dict[str, Any],
    human_decision_capture: dict[str, Any] | None = None,
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    if not isinstance(human_decision_capture, dict):
        human_decision_capture = {}
    handoff_visibility = approval_resume_capture.get("implementation_handoff_visibility")
    if not isinstance(handoff_visibility, dict):
        handoff_visibility = {}
    dry_run_capture = approval_resume_capture.get("governed_implementation_dry_run")
    if not isinstance(dry_run_capture, dict):
        dry_run_capture = {}
    authorization_capture = approval_resume_capture.get("execution_authorization")
    if not isinstance(authorization_capture, dict):
        authorization_capture = {}
    invocation_request_capture = approval_resume_capture.get("worker_invocation_request")
    if not isinstance(invocation_request_capture, dict):
        invocation_request_capture = {}
    assignment_capture = approval_resume_capture.get("worker_assignment")
    if not isinstance(assignment_capture, dict):
        assignment_capture = {}
    dispatch_capture = approval_resume_capture.get("worker_dispatch")
    if not isinstance(dispatch_capture, dict):
        dispatch_capture = {}
    invocation_capture = approval_resume_capture.get("worker_invocation")
    if not isinstance(invocation_capture, dict):
        invocation_capture = {}
    execution_capture = approval_resume_capture.get("execution_runtime")
    if not isinstance(execution_capture, dict):
        execution_capture = {}
    execution_artifact = execution_capture.get("execution_artifact")
    if not isinstance(execution_artifact, dict):
        execution_artifact = {}
    result_capture = approval_resume_capture.get("worker_result_capture")
    if not isinstance(result_capture, dict):
        result_capture = {}
    validation_capture = approval_resume_capture.get("worker_result_validation")
    if not isinstance(validation_capture, dict):
        validation_capture = {}
    executable_bundle_capture = approval_resume_capture.get("executable_bundle")
    if not isinstance(executable_bundle_capture, dict):
        executable_bundle_capture = {}
    review_capture = approval_resume_capture.get("post_execution_replay_review")
    if not isinstance(review_capture, dict):
        review_capture = {}
    termination_capture = approval_resume_capture.get("governed_termination")
    if not isinstance(termination_capture, dict):
        termination_capture = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": approval_resume_capture.get("handoff_status"),
        "response_source": "IMPLEMENTATION_APPROVAL_RESUME",
        "fail_closed": approval_resume_capture.get("fail_closed") is True,
        "failure_reason": approval_resume_capture.get("failure_reason"),
        "replay_reference": approval_resume_capture.get("implementation_approval_resume_replay_reference"),
        "conversation_replay_reference": approval_resume_capture.get("implementation_approval_resume_replay_reference"),
        "canonical_chain_id": approval_resume_capture.get("chain_id"),
        "current_chain_id": approval_resume_capture.get("chain_id"),
        "latest_chain_id": approval_resume_capture.get("chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "approval_resume_status": approval_resume_capture.get("resume_status"),
        "human_decision_status": human_decision_capture.get("decision_status"),
        "human_decision": human_decision_capture.get("decision"),
        "human_decision_replay_reference": human_decision_capture.get("human_decision_replay_reference"),
        "approval_id": approval_resume_capture.get("approval_id"),
        "approval_scope": approval_resume_capture.get("approval_scope"),
        "handoff_status": approval_resume_capture.get("handoff_status"),
        "handoff_reference": approval_resume_capture.get("handoff_reference"),
        "implementation_approval_resume_replay_reference": approval_resume_capture.get(
            "implementation_approval_resume_replay_reference"
        ),
        "implementation_handoff_visibility_replay_reference": handoff_visibility.get(
            "implementation_handoff_visibility_replay_reference"
        ),
        "execution_preparation_status": dry_run_capture.get("execution_status"),
        "governed_implementation_dry_run_replay_reference": dry_run_capture.get(
            "governed_implementation_dry_run_replay_reference"
        ),
        "execution_authorization_status": authorization_capture.get("authorization_status"),
        "execution_authorization_replay_reference": authorization_capture.get(
            "execution_authorization_replay_reference"
        ),
        "worker_invocation_request_status": invocation_request_capture.get("request_status"),
        "worker_invocation_request_replay_reference": invocation_request_capture.get(
            "worker_invocation_request_replay_reference"
        ),
        "worker_assignment_status": assignment_capture.get("assignment_status"),
        "worker_assignment_replay_reference": assignment_capture.get("worker_assignment_replay_reference"),
        "worker_dispatch_status": dispatch_capture.get("dispatch_status"),
        "worker_dispatch_replay_reference": dispatch_capture.get("worker_dispatch_replay_reference"),
        "worker_invocation_status": invocation_capture.get("invocation_status"),
        "worker_invocation_replay_reference": invocation_capture.get("worker_invocation_replay_reference"),
        "execution_runtime_status": execution_artifact.get("execution_status"),
        "execution_runtime_replay_reference": execution_artifact.get("replay_reference"),
        "execution_reference": execution_artifact.get("execution_id"),
        "execution_hash": execution_artifact.get("artifact_hash"),
        "worker_result_capture_status": result_capture.get("result_capture_status"),
        "worker_result_capture_replay_reference": result_capture.get("worker_result_capture_replay_reference"),
        "worker_result_validation_status": validation_capture.get("validation_status"),
        "worker_result_validation_replay_reference": validation_capture.get(
            "worker_result_validation_replay_reference"
        ),
        "executable_bundle_status": executable_bundle_capture.get("executable_bundle_verification_status"),
        "executable_bundle_replay_reference": executable_bundle_capture.get("executable_bundle_replay_reference"),
        "post_execution_replay_review_status": review_capture.get("review_status"),
        "post_execution_replay_review_replay_reference": review_capture.get(
            "post_execution_replay_review_replay_reference"
        ),
        "governed_termination_status": termination_capture.get("termination_status"),
        "governed_termination_replay_reference": termination_capture.get("governed_termination_replay_reference"),
        "worker_assigned": assignment_capture.get("assignment_status") == "WORKER_ASSIGNED",
        "worker_dispatched": dispatch_capture.get("dispatch_status") == "WORKER_DISPATCHED",
        "worker_invoked": invocation_capture.get("invocation_status") == "WORKER_INVOKED",
        "execution_started": execution_artifact.get("execution_started") is True,
        "worker_result_captured": result_capture.get("result_capture_status") == "WORKER_RESULT_CAPTURED",
        "worker_result_validated": validation_capture.get("validation_status") == "RESULT_VALIDATED",
        "executable_bundle_authorized": executable_bundle_capture.get("executable_bundle_authorization_status")
        == "EXECUTABLE_BUNDLE_AUTHORIZED",
        "artifacts_created": executable_bundle_capture.get("artifact_creation_status") == "ARTIFACTS_CREATED",
        "executable_bundle_verified": executable_bundle_capture.get("executable_bundle_verification_status")
        == "EXECUTABLE_BUNDLE_VERIFIED",
        "post_execution_replay_reviewed": review_capture.get("review_status") == "REVIEW_COMPLETED",
        "terminated": termination_capture.get("termination_status") == "TERMINATED",
        "execution_requested": False,
        "dispatch_requested": dispatch_capture.get("dispatch_status") == "WORKER_DISPATCHED",
        "invocation_requested": invocation_request_capture.get("request_status")
        == "WORKER_INVOCATION_REQUEST_CREATED",
    }


def _interactive_human_decision_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    human_decision_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": human_decision_capture.get("terminal_status"),
        "response_source": "HUMAN_DECISION_RUNTIME",
        "fail_closed": human_decision_capture.get("fail_closed") is True,
        "failure_reason": human_decision_capture.get("failure_reason"),
        "replay_reference": human_decision_capture.get("human_decision_replay_reference"),
        "conversation_replay_reference": human_decision_capture.get("human_decision_replay_reference"),
        "canonical_chain_id": human_decision_capture.get("chain_id"),
        "current_chain_id": human_decision_capture.get("chain_id"),
        "latest_chain_id": human_decision_capture.get("chain_id"),
        "related_chain_id": None,
        "suggested_inspection_commands": [],
        "conversation_chain_continuity_replay_reference": None,
        "source_router_replay_reference": source_router_replay_reference,
        "human_decision_status": human_decision_capture.get("decision_status"),
        "human_decision": human_decision_capture.get("decision"),
        "human_decision_replay_reference": human_decision_capture.get("human_decision_replay_reference"),
        "approval_scope": human_decision_capture.get("approval_scope"),
        "clarification_required": human_decision_capture.get("clarification_required") is True,
        "implementation_authorized": human_decision_capture.get("implementation_authorized") is True,
        "implementation_rejected": human_decision_capture.get("implementation_rejected") is True,
        "modification_requested": human_decision_capture.get("modification_requested") is True,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
    }


def _interactive_native_development_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    native_context_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    post_context_continuation = native_context_capture.get("post_context_continuation")
    if not isinstance(post_context_continuation, dict):
        post_context_continuation = {}
    post_entry_gate = native_context_capture.get("post_entry_continuation_gate")
    if not isinstance(post_entry_gate, dict):
        post_entry_gate = {}
    conversation_ppp_routing = post_context_continuation.get("conversation_ppp_routing")
    if not isinstance(conversation_ppp_routing, dict):
        conversation_ppp_routing = {}
    certified_continuation = native_context_capture.get("certified_development_continuation")
    if not isinstance(certified_continuation, dict):
        certified_continuation = {}
    handoff_visibility = certified_continuation.get("implementation_handoff_visibility")
    if not isinstance(handoff_visibility, dict):
        handoff_visibility = {}
    dry_run = certified_continuation.get("governed_implementation_dry_run")
    if not isinstance(dry_run, dict):
        dry_run = {}
    authorization = certified_continuation.get("execution_authorization")
    if not isinstance(authorization, dict):
        authorization = {}
    worker_request = certified_continuation.get("worker_invocation_request")
    if not isinstance(worker_request, dict):
        worker_request = {}
    worker_lifecycle = certified_continuation.get("worker_lifecycle_continuation")
    if not isinstance(worker_lifecycle, dict):
        worker_lifecycle = {}
    worker_assignment = worker_lifecycle.get("worker_assignment")
    if not isinstance(worker_assignment, dict):
        worker_assignment = {}
    worker_dispatch = worker_lifecycle.get("worker_dispatch")
    if not isinstance(worker_dispatch, dict):
        worker_dispatch = {}
    worker_invocation = worker_lifecycle.get("worker_invocation")
    if not isinstance(worker_invocation, dict):
        worker_invocation = {}
    execution_candidate = worker_lifecycle.get("worker_execution_candidate")
    if not isinstance(execution_candidate, dict):
        execution_candidate = {}
    external_task = worker_lifecycle.get("external_worker_task_package")
    if not isinstance(external_task, dict):
        external_task = {}
    openai_worker = worker_lifecycle.get("openai_external_worker_provider")
    if not isinstance(openai_worker, dict):
        openai_worker = {}
    result_validation = worker_lifecycle.get("result_validation")
    if not isinstance(result_validation, dict):
        result_validation = {}
    replay_certification = worker_lifecycle.get("replay_certification")
    if not isinstance(replay_certification, dict):
        replay_certification = {}
    return {
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "selected_source": source_artifact["selected_source"],
        "selection_reason": source_artifact["selection_reason"],
        "response_status": native_context_capture.get("response_status"),
        "response_source": native_context_capture.get("response_source"),
        "fail_closed": native_context_capture.get("fail_closed") is True,
        "failure_reason": native_context_capture.get("failure_reason"),
        "replay_reference": native_context_capture.get("replay_reference"),
        "conversation_replay_reference": native_context_capture.get("conversation_replay_reference"),
        "canonical_chain_id": native_context_capture.get("canonical_chain_id"),
        "current_chain_id": native_context_capture.get("current_chain_id"),
        "latest_chain_id": native_context_capture.get("latest_chain_id"),
        "related_chain_id": native_context_capture.get("related_chain_id"),
        "suggested_inspection_commands": native_context_capture.get("suggested_inspection_commands", []),
        "conversation_chain_continuity_replay_reference": native_context_capture.get(
            "conversation_chain_continuity_replay_reference"
        ),
        "source_router_replay_reference": source_router_replay_reference,
        "native_development_task_intake_replay_reference": native_context_capture.get(
            "native_development_task_intake", {}
        ).get("native_development_task_intake_replay_reference")
        if isinstance(native_context_capture.get("native_development_task_intake"), dict)
        else None,
        "development_context_assembly_replay_reference": native_context_capture.get(
            "development_context_assembly", {}
        ).get("development_context_assembly_replay_reference")
        if isinstance(native_context_capture.get("development_context_assembly"), dict)
        else None,
        "conversation_native_development_context_replay_reference": native_context_capture.get(
            "conversation_replay_reference"
        ),
        "recognized_development_task": native_context_capture.get("response_status")
        != NATIVE_DEVELOPMENT_CONTEXT_FAILED_CLOSED,
        "task_intake_reference": native_context_capture.get("task_intake_reference"),
        "context_assembly_reference": native_context_capture.get("context_assembly_reference"),
        "context_status": native_context_capture.get("context_status"),
        "requested_domain": native_context_capture.get("development_context_assembly", {}).get("requested_domain")
        if isinstance(native_context_capture.get("development_context_assembly"), dict)
        else None,
        "context_hash": native_context_capture.get("context_hash"),
        "missing_context": native_context_capture.get("missing_context", []),
        "ambiguous_context": native_context_capture.get("ambiguous_context", []),
        "provider_necessity_classification": native_context_capture.get("provider_necessity_classification"),
        "suggested_next_actions": native_context_capture.get("suggested_next_actions", []),
        "post_entry_continuation_gate_status": post_entry_gate.get("gate_status"),
        "post_entry_continuation_allowed": post_entry_gate.get("continuation_allowed") is True,
        "post_entry_continuation_gate_replay_reference": post_entry_gate.get(
            "post_entry_continuation_gate_replay_reference"
        ),
        "clarification_required": native_context_capture.get("clarification_required") is True,
        "open_clarification_detected": native_context_capture.get("open_clarification_detected") is True,
        "missing_information": native_context_capture.get("missing_information", []),
        "post_entry_clarification_pending": native_context_capture.get("post_entry_clarification_pending") is True,
        "post_entry_clarification_resolved": native_context_capture.get("post_entry_clarification_resolved") is True,
        "post_entry_execution_summary_required": post_entry_gate.get("execution_summary_required") is True,
        "post_entry_human_confirmation_required": post_entry_gate.get("human_confirmation_required") is True,
        "post_entry_authorization_required": post_entry_gate.get("authorization_required") is True,
        "post_context_continuation_status": post_context_continuation.get("continuation_status"),
        "post_context_continuation_replay_reference": post_context_continuation.get(
            "post_context_continuation_replay_reference"
        ),
        "ppp_route_status": post_context_continuation.get("ppp_route_status"),
        "ppp_routing_replay_reference": conversation_ppp_routing.get("conversation_ppp_routing_replay_reference"),
        "implementation_handoff_reference": post_context_continuation.get("implementation_handoff_reference"),
        "implementation_handoff_visibility_status": handoff_visibility.get("summary_status"),
        "execution_preparation_status": dry_run.get("execution_status"),
        "execution_authorization_status": authorization.get("authorization_status"),
        "execution_summary_reference": authorization.get("execution_summary_reference"),
        "execution_summary_hash": authorization.get("execution_summary_hash"),
        "human_confirmation_reference": authorization.get("human_confirmation_reference"),
        "human_confirmation_hash": authorization.get("human_confirmation_hash"),
        "execution_authorization_replay_reference": authorization.get("execution_authorization_replay_reference"),
        "worker_invocation_request_status": worker_request.get("request_status"),
        "worker_invocation_request_replay_reference": worker_request.get(
            "worker_invocation_request_replay_reference"
        ),
        "worker_request_reached": certified_continuation.get("worker_request_reached") is True,
        "worker_assignment_status": worker_assignment.get("assignment_status"),
        "worker_assignment_replay_reference": worker_assignment.get("worker_assignment_replay_reference"),
        "worker_dispatch_status": worker_dispatch.get("dispatch_status"),
        "worker_dispatch_replay_reference": worker_dispatch.get("worker_dispatch_replay_reference"),
        "worker_invocation_status": worker_invocation.get("invocation_status"),
        "worker_invocation_replay_reference": worker_invocation.get("worker_invocation_replay_reference"),
        "worker_execution_candidate_status": execution_candidate.get("candidate_status"),
        "worker_execution_candidate_replay_reference": execution_candidate.get(
            "worker_execution_candidate_replay_reference"
        ),
        "external_worker_task_status": external_task.get("task_status"),
        "external_worker_task_replay_reference": external_task.get("external_worker_replay_reference"),
        "openai_external_worker_status": openai_worker.get("worker_status"),
        "openai_external_worker_replay_reference": openai_worker.get("openai_external_worker_replay_reference"),
        "result_validation_status": result_validation.get("validation_status"),
        "result_validation_replay_reference": result_validation.get("result_validation_replay_reference"),
        "replay_certification_status": replay_certification.get("certification_status"),
        "replay_certification_replay_reference": replay_certification.get("replay_certification_replay_reference"),
        "worker_assignment_reached": worker_lifecycle.get("worker_assignment_reached") is True,
        "worker_dispatch_reached": worker_lifecycle.get("worker_dispatch_reached") is True,
        "worker_invocation_reached": worker_lifecycle.get("worker_invocation_reached") is True,
        "worker_execution_candidate_reached": worker_lifecycle.get("worker_execution_candidate_reached") is True,
        "external_task_package_reached": worker_lifecycle.get("external_task_package_reached") is True,
        "openai_provider_reached": worker_lifecycle.get("openai_provider_reached") is True,
        "result_validation_reached": worker_lifecycle.get("result_validation_reached") is True,
        "replay_certification_reached": worker_lifecycle.get("replay_certification_reached") is True,
        "replay_lineage_preserved": worker_lifecycle.get("replay_lineage_preserved") is True,
        "worker_invoked": worker_lifecycle.get("worker_invocation_reached") is True,
        "execution_requested": worker_lifecycle.get("openai_provider_reached") is True,
        "dispatch_requested": worker_lifecycle.get("worker_dispatch_reached") is True,
        "invocation_requested": worker_request.get("request_status") == "WORKER_INVOCATION_REQUEST_CREATED",
    }


def _require_cli_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _is_governed_development_resume_decision_prompt(human_prompt: str) -> bool:
    human_decision = normalize_human_decision(human_prompt)
    if human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}:
        return True
    normalized = str(human_prompt or "").strip().upper().replace("-", "_")
    return normalized == "APPROVE THIS PROPOSAL" or normalized.startswith("APPROVE ")


def _is_lifecycle_command_prompt(human_prompt: str) -> bool:
    normalized = " ".join(str(human_prompt or "").strip().lower().replace("_", " ").split())
    if not normalized:
        return False
    if _post_entry_continuation_clarification_matches(human_prompt):
        return True
    if normalize_human_decision(human_prompt) in {APPROVE, REJECT, REQUEST_MODIFICATION}:
        return True
    return normalized in {"continue", "resume", "cancel", "retry", "clarify"}


def _restore_pending_post_entry_continuation_from_replay(
    *,
    session_root: Path,
    turn_root: Path,
    created_at: str,
) -> dict[str, Any] | None:
    if not session_root.exists():
        return None
    gate_paths = sorted(
        session_root.glob("TURN-*/post_entry_continuation_gate/000_post_entry_continuation_gate_recorded.json")
    )
    for gate_path in reversed(gate_paths):
        if _path_belongs_to_turn(gate_path, turn_root):
            continue
        gate_artifact = _load_verified_post_entry_gate_artifact(gate_path)
        if gate_artifact.get("workflow_id") != CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION:
            continue
        if gate_artifact.get("gate_status") != POST_ENTRY_CLARIFICATION_REQUIRED:
            continue
        source_turn_root = gate_path.parents[1]
        if (source_turn_root / "post_context_continuation").exists():
            continue
        native_context_capture = _load_verified_pending_native_context_capture(source_turn_root)
        native_context_capture["post_entry_continuation_gate"] = deepcopy(gate_artifact)
        native_context_capture["post_entry_continuation_gate_status"] = gate_artifact.get("gate_status")
        native_context_capture["post_entry_continuation_gate_replay_reference"] = str(gate_path.parent)
        native_context_capture["clarification_required"] = True
        native_context_capture["open_clarification_detected"] = True
        native_context_capture["post_entry_clarification_pending"] = True
        _record_pending_post_entry_continuation_restore(
            turn_root=turn_root,
            gate_path=gate_path,
            native_context_capture=native_context_capture,
            created_at=created_at,
        )
        return {
            "native_context_capture": native_context_capture,
            "original_human_prompt": _restored_native_context_original_prompt(native_context_capture),
            "current_chain_id": native_context_capture.get("current_chain_id"),
            "latest_chain_id": native_context_capture.get("latest_chain_id"),
            "restored_from_replay": True,
        }
    return None


def _path_belongs_to_turn(path: Path, turn_root: Path) -> bool:
    try:
        path.relative_to(turn_root)
    except ValueError:
        return False
    return True


def _load_verified_post_entry_gate_artifact(gate_path: Path) -> dict[str, Any]:
    wrapper = load_json(gate_path)
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("post-entry continuation restore failed closed: gate replay wrapper missing")
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("post-entry continuation restore failed closed: gate replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("post-entry continuation restore failed closed: gate artifact missing")
    _verify_replay_hashed_artifact(
        artifact,
        failure_reason="post-entry continuation restore failed closed: gate artifact hash mismatch",
    )
    return artifact


def _load_verified_pending_native_context_capture(source_turn_root: Path) -> dict[str, Any]:
    native_context_capture = reconstruct_conversation_native_development_context_integration_replay(source_turn_root)
    if native_context_capture.get("context_status") != "CONTEXT_ASSEMBLED":
        raise FailClosedRuntimeError("post-entry continuation restore failed closed: context is not assembled")
    provider_necessity = str(native_context_capture.get("provider_necessity_classification") or "")
    if "PROVIDER_REQUIRED" not in provider_necessity:
        raise FailClosedRuntimeError("post-entry continuation restore failed closed: provider-backed proposal not required")
    native_context_capture["response_status"] = "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED"
    native_context_capture["response_source"] = "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    native_context_capture["response_text"] = ""
    native_context_capture["fail_closed"] = False
    native_context_capture["failure_reason"] = None
    native_context_capture["replay_reference"] = str(source_turn_root)
    native_context_capture["conversation_replay_reference"] = str(
        source_turn_root / "native_development_context_integration"
    )
    native_context_capture["native_development_task_intake"] = native_context_capture.get("intake_replay")
    native_context_capture["development_context_assembly"] = native_context_capture.get("context_replay")
    if (source_turn_root / "chain_continuity").exists():
        continuity = reconstruct_conversation_chain_continuity_replay(source_turn_root / "chain_continuity")
        native_context_capture["canonical_chain_id"] = continuity.get("canonical_chain_id")
        native_context_capture["current_chain_id"] = continuity.get("current_chain_id")
        native_context_capture["latest_chain_id"] = continuity.get("latest_chain_id")
        native_context_capture["related_chain_id"] = continuity.get("related_chain_id")
        native_context_capture["suggested_inspection_commands"] = deepcopy(
            continuity.get("suggested_inspection_commands", [])
        )
        native_context_capture["conversation_chain_continuity_replay_reference"] = str(
            source_turn_root / "chain_continuity"
        )
    return native_context_capture


def _restored_native_context_original_prompt(native_context_capture: dict[str, Any]) -> str:
    intake = native_context_capture.get("intake_replay")
    if isinstance(intake, dict):
        artifact = intake.get("native_development_task_intake_artifact")
        if isinstance(artifact, dict):
            prompt = artifact.get("human_prompt")
            if isinstance(prompt, str) and prompt.strip():
                return prompt.strip()
        milestone = intake.get("requested_milestone_id")
        if isinstance(milestone, str) and milestone.strip():
            return (
                f"Continue restored native development context for {milestone.strip()}. "
                "Reuse existing governance, replay, validation, mutation, and worker lifecycle infrastructure."
            )
    prompt_id = native_context_capture.get("prompt_id")
    if isinstance(prompt_id, str) and prompt_id.strip():
        return (
            f"Continue restored native development context for {prompt_id.strip()}. "
            "Reuse existing governance, replay, validation, mutation, and worker lifecycle infrastructure."
        )
    raise FailClosedRuntimeError("post-entry continuation restore failed closed: original prompt missing")


def _record_pending_post_entry_continuation_restore(
    *,
    turn_root: Path,
    gate_path: Path,
    native_context_capture: dict[str, Any],
    created_at: str,
) -> None:
    artifact = {
        "artifact_type": "ACLI_PENDING_POST_ENTRY_CONTINUATION_RESTORED_V1",
        "restore_status": "PENDING_POST_ENTRY_CONTINUATION_RESTORED",
        "source_replay_reference": str(gate_path),
        "workflow_id": CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        "context_status": native_context_capture.get("context_status"),
        "context_hash": native_context_capture.get("context_hash"),
        "canonical_chain_id": native_context_capture.get("canonical_chain_id"),
        "approval_granted": False,
        "execution_authorized": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "replay_visible": True,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "pending_post_entry_continuation_restored",
        "artifact": artifact,
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(
        turn_root
        / "pending_post_entry_continuation_restore"
        / "000_pending_post_entry_continuation_restored.json",
        wrapper,
    )


def _is_explicit_governed_development_resume_approval(
    human_prompt: str,
    pending_proposal_capture: dict[str, Any],
) -> bool:
    normalized = " ".join(str(human_prompt or "").strip().upper().replace("-", "_").split())
    if normalized == "APPROVE THIS PROPOSAL":
        return True
    identifier = _governed_development_proposal_identifier(pending_proposal_capture)
    if not identifier:
        return False
    return normalized == f"APPROVE {identifier.upper()}"


def _governed_development_proposal_identifier(pending_proposal_capture: dict[str, Any]) -> str | None:
    naming = pending_proposal_capture.get("proposal_naming_decision")
    if isinstance(naming, dict):
        identifier = naming.get("selected_artifact_identifier") or naming.get("requested_artifact_identifier")
        if isinstance(identifier, str) and identifier.strip():
            return identifier.strip()
    proposal = pending_proposal_capture.get("proposal_artifact")
    if isinstance(proposal, dict):
        artifact = proposal.get("governance_artifact_proposal")
        if isinstance(artifact, dict):
            title = artifact.get("artifact_title")
            if isinstance(title, str) and title.strip():
                return title.strip()
    return None


def _record_safe_governed_development_resume_presentation(
    *,
    turn_root: Path,
    pending_proposal_capture: dict[str, Any],
    human_prompt: str,
    created_at: str,
) -> dict[str, Any]:
    proposal = pending_proposal_capture.get("proposal_artifact")
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("ACLI safe approval resume failed closed: proposal artifact missing")
    proposal_hash = proposal.get("artifact_hash")
    if not isinstance(proposal_hash, str) or not proposal_hash:
        raise FailClosedRuntimeError("ACLI safe approval resume failed closed: proposal hash missing")
    artifact = {
        "artifact_type": "ACLI_SAFE_APPROVAL_RESUME_PRESENTATION_V1",
        "presentation_status": "RESTORED_PROPOSAL_PRESENTED",
        "operator_prompt": human_prompt,
        "artifact_identifier": _governed_development_proposal_identifier(pending_proposal_capture),
        "target_paths": [str(path) for path in pending_proposal_capture.get("target_paths", [])],
        "proposal_hash": proposal_hash,
        "proposal_replay_reference": pending_proposal_capture.get("replay_reference"),
        "approval_granted": False,
        "execution_authorized": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "next_allowed_approval_commands": _safe_governed_development_resume_approval_commands(
            pending_proposal_capture
        ),
        "replay_visible": True,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "acli_safe_approval_resume_presentation_recorded",
        "artifact": artifact,
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    replay_path = (
        turn_root
        / "acli_safe_approval_resume"
        / "000_acli_safe_approval_resume_presentation_recorded.json"
    )
    write_json_immutable(replay_path, wrapper)
    return {
        "safe_resume_presentation_artifact": artifact,
        "safe_resume_presentation_replay_reference": str(replay_path.parent),
    }


def _safe_governed_development_resume_approval_commands(
    pending_proposal_capture: dict[str, Any],
) -> list[str]:
    commands = ["APPROVE THIS PROPOSAL"]
    identifier = _governed_development_proposal_identifier(pending_proposal_capture)
    if identifier:
        commands.append(f"APPROVE {identifier}")
    return commands


def _render_safe_governed_development_resume_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("safe_resume_presentation_artifact") or {}
    identifier = artifact.get("artifact_identifier") or "not available"
    target_paths = artifact.get("target_paths") if isinstance(artifact.get("target_paths"), list) else []
    commands = artifact.get("next_allowed_approval_commands")
    if not isinstance(commands, list) or not commands:
        commands = ["APPROVE THIS PROPOSAL"]
    lines = [
        "Restored Governed Development Proposal",
        "",
        "Operator Summary",
        "",
        f"ACLI restored a pending governed development proposal for: {identifier}",
        "The proposal exists because a prior ACLI session prepared repository changes and stopped before approval.",
        "",
        "If approved:",
        "- ACLI will use the restored proposal",
        "- repository artifacts may be created or modified",
        "- validation will run",
        "- replay evidence will be recorded",
        "",
        "What will not happen:",
        "- no worker has executed yet",
        "- no repository mutation has occurred yet",
        "- this summary does not approve execution",
        "- bare APPROVE will not execute a restored proposal",
        "",
        "Nothing has executed yet.",
        "",
        "To approve this restored proposal, type exactly one of:",
        *[f"- {command}" for command in commands],
        "",
        "To cancel, type:",
        "- REJECT",
        "",
        "To request changes, type:",
        "- REQUEST_MODIFICATION",
        "",
        "Technical Evidence",
        "",
        f"artifact_identifier: {identifier}",
        "target_paths:",
        *([f"- {path}" for path in target_paths] if target_paths else ["- none recorded"]),
        f"proposal_hash: {artifact.get('proposal_hash') or ''}",
        f"proposal_replay_reference: {artifact.get('proposal_replay_reference') or ''}",
        f"presentation_replay_reference: {capture.get('safe_resume_presentation_replay_reference') or ''}",
        "approval_granted: false",
        "execution_authorized: false",
        "mutation_performed: false",
    ]
    return "\n".join(lines)


def _restore_pending_governed_development_bridge_from_replay(
    *,
    session_root: Path,
    turn_root: Path,
    created_at: str,
) -> dict[str, Any] | None:
    if not session_root.exists():
        return None
    proposal_paths = sorted(
        session_root.glob(
            "TURN-*/acli_governed_development_execution_bridge/"
            "000_acli_governed_development_proposal_recorded.json"
        )
    )
    for proposal_path in reversed(proposal_paths):
        if _governed_development_proposal_belongs_to_turn(proposal_path, turn_root):
            continue
        proposal_capture = _load_verified_governed_development_proposal_capture(proposal_path)
        proposal_hash = _governed_development_pending_proposal_hash(proposal_capture)
        if _governed_development_proposal_is_consumed(session_root=session_root, proposal_hash=proposal_hash):
            continue
        _record_governed_development_pending_proposal_restore(
            turn_root=turn_root,
            proposal_path=proposal_path,
            proposal_hash=proposal_hash,
            created_at=created_at,
        )
        return proposal_capture
    return None


def _governed_development_proposal_belongs_to_turn(proposal_path: Path, turn_root: Path) -> bool:
    try:
        proposal_path.relative_to(turn_root)
    except ValueError:
        return False
    return True


def _load_verified_governed_development_proposal_capture(proposal_path: Path) -> dict[str, Any]:
    wrapper = _load_verified_replay_wrapper(proposal_path)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: proposal replay artifact missing")
    if artifact.get("artifact_type") != ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1:
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: unexpected proposal artifact type")
    _verify_replay_hashed_artifact(
        artifact,
        failure_reason="ACLI approval continuation failed closed: pending proposal hash mismatch",
    )
    if artifact.get("bridge_status") != ACLI_GOVERNED_DEVELOPMENT_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: pending proposal approval required")
    required_false_fields = (
        "approval_bypassed",
        "mutation_performed",
        "worker_invoked",
        "validation_executed",
    )
    if artifact.get("approval_required") is not True or any(artifact.get(field) is True for field in required_false_fields):
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: invalid pending proposal state")
    return artifact


def _load_verified_replay_wrapper(path: Path) -> dict[str, Any]:
    try:
        wrapper = load_json(path)
    except Exception as exc:
        raise FailClosedRuntimeError(f"ACLI approval continuation failed closed: unreadable replay {path}") from exc
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: replay wrapper missing")
    wrapper_hash = wrapper.get("wrapper_hash")
    if wrapper_hash is not None:
        expected = deepcopy(wrapper)
        actual = expected.pop("wrapper_hash", None)
        if not isinstance(actual, str) or replay_hash(expected) != actual:
            raise FailClosedRuntimeError("ACLI approval continuation failed closed: replay wrapper hash mismatch")
    return wrapper


def _verify_replay_hashed_artifact(artifact: dict[str, Any], *, failure_reason: str) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError(failure_reason)


def _governed_development_pending_proposal_hash(proposal_capture: dict[str, Any]) -> str:
    proposal = proposal_capture.get("proposal_artifact")
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: proposal artifact missing")
    proposal_hash = proposal.get("artifact_hash")
    if not isinstance(proposal_hash, str) or not proposal_hash:
        raise FailClosedRuntimeError("ACLI approval continuation failed closed: proposal artifact hash missing")
    return proposal_hash


def _governed_development_proposal_is_consumed(*, session_root: Path, proposal_hash: str) -> bool:
    execution_paths = sorted(
        session_root.glob(
            "TURN-*/acli_governed_development_execution_bridge/"
            "001_acli_governed_development_execution_recorded.json"
        )
    )
    for execution_path in execution_paths:
        wrapper = _load_verified_replay_wrapper(execution_path)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            continue
        if artifact.get("artifact_type") != ACLI_GOVERNED_DEVELOPMENT_BRIDGE_EXECUTION_CAPTURE_V1:
            continue
        if artifact.get("proposal_hash") == proposal_hash:
            return True
    return False


def _record_governed_development_pending_proposal_restore(
    *,
    turn_root: Path,
    proposal_path: Path,
    proposal_hash: str,
    created_at: str,
) -> None:
    artifact = {
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_PENDING_PROPOSAL_RESTORED_V1",
        "restore_status": "PENDING_PROPOSAL_RESTORED",
        "source_replay_reference": str(proposal_path),
        "proposal_hash": proposal_hash,
        "restored_for": "EXPLICIT_OPERATOR_DECISION",
        "approval_granted": False,
        "execution_authorized": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "replay_visible": True,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "acli_governed_development_pending_proposal_restored",
        "artifact": artifact,
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(
        turn_root
        / "acli_governed_development_pending_proposal_restore"
        / "000_acli_governed_development_pending_proposal_restored.json",
        wrapper,
    )


def _latest_recommendation_state(session_root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    continuity_artifact: dict[str, Any] | None = None
    approval_artifact: dict[str, Any] | None = None
    if not session_root.exists():
        return None, None
    for turn_root in sorted((path for path in session_root.iterdir() if path.is_dir()), key=lambda path: path.name):
        continuity = _load_turn_artifact(
            turn_root / "recommendation_continuity" / "000_recommendation_continuity_recorded.json"
        )
        if continuity and continuity.get("approval_status") == "APPROVAL_REQUIRED":
            continuity_artifact = continuity
            approval_artifact = None
        approval = _load_turn_artifact(
            turn_root / "recommendation_approval" / "000_recommendation_approval_recorded.json"
        )
        if (
            approval
            and continuity_artifact
            and approval.get("continuity_hash") == continuity_artifact.get("artifact_hash")
            and approval.get("operator_decision") == RECOMMENDATION_APPROVE
        ):
            approval_artifact = approval
    return continuity_artifact, approval_artifact


def _load_turn_artifact(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        wrapper = load_json(path)
    except Exception:
        return None
    artifact = wrapper.get("artifact")
    return artifact if isinstance(artifact, dict) else None


def _is_recommendation_decision_prompt(human_prompt: str) -> bool:
    return (
        is_recommendation_approval_prompt(human_prompt)
        or is_recommendation_rejection_prompt(human_prompt)
        or is_recommendation_ignore_prompt(human_prompt)
    )


def _recommendation_decision_from_prompt(human_prompt: str) -> str:
    if is_recommendation_approval_prompt(human_prompt):
        return RECOMMENDATION_APPROVE
    if is_recommendation_rejection_prompt(human_prompt):
        return RECOMMENDATION_REJECT
    if is_recommendation_ignore_prompt(human_prompt):
        return RECOMMENDATION_IGNORE
    raise ValueError("unsupported recommendation decision prompt")


def _is_conversational_cli_readonly_candidate(human_prompt: str) -> bool:
    prompt = str(human_prompt or "").lower()
    return (
        ("latest" in prompt and ("replay chain" in prompt or "chain" in prompt))
        or ("review" in prompt and "audit" in prompt)
        or ("improve" in prompt and "provider" in prompt and "layer" in prompt)
    )


def _run_conversational_cli_selected_readonly_workflow(
    *,
    prompt_id: str,
    human_prompt: str,
    routing_capture: dict[str, Any],
    runtime_root: str | Path,
    turn_root: Path,
    created_at: str,
) -> dict[str, Any]:
    workflow_id = routing_capture.get("workflow_id")
    try:
        if routing_capture.get("fail_closed") is True:
            raise ValueError(routing_capture.get("failure_reason") or "conversational route failed closed")
        if workflow_id == CONVERSATIONAL_SHOW_LATEST_REPLAY_CHAIN:
            result = show_latest_chain_command(
                replay_root=runtime_root,
                report_root=turn_root / "conversational_chain_inspection",
                created_at=created_at,
            )
            response_text = render_chain_inspection_summary(result)
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=response_text,
                existing_result=result,
                response_status=result.get("status", "READY"),
                fail_closed=result.get("fail_closed") is True,
                failure_reason=result.get("failure_reason"),
            )
        if workflow_id == CONVERSATIONAL_REVIEW_LATEST_AUDIT:
            audit_path = Path("governance") / "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1.md"
            if not audit_path.exists():
                raise ValueError("latest audit summary artifact is missing")
            lines = audit_path.read_text(encoding="utf-8").splitlines()
            preview = "\n".join(line for line in lines[:18] if line.strip())
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text="LATEST AUDIT REVIEW\n" + preview,
                existing_result={"audit_summary_path": str(audit_path), "read_only": True},
            )
        if workflow_id == CONVERSATIONAL_IMPROVE_PROVIDER_LAYER:
            response_text = "\n".join(
                [
                    "PROVIDER LAYER IMPROVEMENT REVIEW",
                    "Workflow Selected: IMPROVE_PROVIDER_LAYER",
                    "Existing Runtime: provider-layer review guidance",
                    "Safe next step: create a bounded provider-layer improvement proposal with human approval.",
                    "No provider invoked.",
                    "No worker invoked.",
                    "No execution requested.",
                ]
            )
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=response_text,
                existing_result={"read_only": True, "proposal_created": False},
            )
        if workflow_id == CONVERSATIONAL_SHOW_STATUS:
            result = status_summary()
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=render_status(result),
                existing_result=result,
                response_status=result.get("status", "READY"),
                fail_closed=result.get("fail_closed") is True,
                failure_reason=result.get("failure_reason"),
            )
        if workflow_id == CONVERSATIONAL_SHOW_DASHBOARD:
            result = dashboard_summary_command(replay_root=runtime_root)
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=render_dashboard_summary(result),
                existing_result=result,
                response_status=result.get("status", "READY"),
                fail_closed=result.get("fail_closed") is True,
                failure_reason=result.get("failure_reason"),
            )
        if workflow_id in _CONVERSATIONAL_DEVELOPMENT_ENTRYPOINT_SELECTION_WORKFLOWS:
            selection = routing_capture.get("workflow_selection_artifact") or {}
            response_text = "\n".join(
                [
                    "DEVELOPMENT ENTRYPOINT SELECTED",
                    f"Workflow Selected: {workflow_id}",
                    f"Existing Runtime: {selection.get('existing_runtime')}",
                    f"Operator Summary: {selection.get('operator_summary')}",
                    "No provider invoked.",
                    "No worker invoked.",
                    "No execution requested.",
                    "Authorization boundary preserved.",
                ]
            )
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=response_text,
                existing_result={
                    "read_only": True,
                    "selection_only": True,
                    "existing_runtime": selection.get("existing_runtime"),
                },
            )
        if workflow_id == CONVERSATIONAL_HUMAN_INTENT_CLARIFICATION_INTAKE:
            selection = routing_capture.get("workflow_selection_artifact") or {}
            questions = selection.get("clarification_questions") or []
            response_text = "\n".join(
                [
                    "HUMAN INTENT CLARIFICATION REQUIRED",
                    f"Intent Family: {selection.get('intent_family')}",
                    "Clarification Questions:",
                    *(f"- {question}" for question in questions),
                    "No provider invoked.",
                    "No worker invoked.",
                    "No execution requested.",
                    "Authorization boundary preserved.",
                ]
            )
            return _conversational_workflow_capture(
                prompt_id=prompt_id,
                workflow_id=workflow_id,
                response_text=response_text,
                existing_result={
                    "clarification_required": True,
                    "intent_family": selection.get("intent_family"),
                    "clarification_questions": questions,
                },
                response_status="CLARIFICATION_REQUIRED",
            )
        raise ValueError(f"unsupported conversational read-only workflow: {workflow_id}")
    except Exception as exc:
        return _conversational_workflow_capture(
            prompt_id=prompt_id,
            workflow_id=workflow_id,
            response_text="",
            existing_result={},
            response_status="FAILED_CLOSED",
            fail_closed=True,
            failure_reason=str(exc),
        )


def _conversational_workflow_capture(
    *,
    prompt_id: str,
    workflow_id: str | None,
    response_text: str,
    existing_result: dict[str, Any],
    response_status: str = "READY",
    fail_closed: bool = False,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "prompt_id": prompt_id,
        "workflow_id": workflow_id,
        "response_status": response_status,
        "response_source": "CONVERSATIONAL_CLI_WORKFLOW",
        "response_text": response_text,
        "existing_result": existing_result,
        "fail_closed": fail_closed,
        "failure_reason": failure_reason,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "workflow_capture_hash": replay_hash(
            {"prompt_id": prompt_id, "workflow_id": workflow_id, "response_status": response_status}
        ),
    }


def _provider_credential_value_from_env(env_name: str) -> str:
    name = _require_cli_string(env_name, "credential_env")
    value = os.environ.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required for provider credential command")
    return value.strip()


def _provider_credential_approval_artifact(args: argparse.Namespace) -> dict[str, Any]:
    artifact = {
        "artifact_type": "PROVIDER_CREDENTIAL_ACLI_HUMAN_APPROVAL_ARTIFACT_V1",
        "operation": args.provider_credential_command.upper(),
        "provider_id": args.provider_id,
        "approval_status": "APPROVED",
        "approved_by": args.approved_by,
        "created_at": args.created_at,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "authorization_header_recorded": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_credential_command_result(args: argparse.Namespace, artifact: dict[str, Any], replay_dir: Path) -> dict:
    return {
        "command": f"aigol provider credential {args.provider_credential_command}",
        "operation": args.provider_credential_command.upper(),
        "provider_id": args.provider_id,
        "vault_path": args.vault_path,
        "replay_reference": str(replay_dir),
        "artifact": artifact,
        "replay_visible": True,
    }


def run_command(args: argparse.Namespace) -> dict:
    if args.command == "status":
        return status_summary()
    if args.command == "runtime-status":
        progress = load_runtime_progress(args.runtime_id, replay_root=args.replay_root)
        progress["command"] = "aigol runtime-status"
        return progress
    if args.command == "runtime-progress":
        progress = load_runtime_progress(args.runtime_id, replay_root=args.replay_root)
        progress["command"] = "aigol runtime-progress"
        return progress
    if args.command == "runtime-watch":
        max_iterations = args.iterations if args.iterations > 0 else None
        outputs = watch_runtime_progress(
            runtime_id=args.runtime_id,
            replay_root=args.replay_root,
            interval_seconds=args.interval_seconds,
            max_iterations=max_iterations,
        )
        latest = load_runtime_progress(args.runtime_id, replay_root=args.replay_root)
        latest["command"] = "aigol runtime-watch"
        latest["watch_outputs"] = outputs
        latest["watch_iteration_count"] = len(outputs)
        return latest
    if args.command == "ingress" and args.ingress_command == "generate":
        return {
            "command": "aigol ingress generate",
            "ingress_artifact": generate_ingress_artifact(
                human_request=args.human_request,
                semantic_intent=args.semantic_intent,
            ),
        }
    if args.command == "governance" and args.governance_command == "validate":
        return validate_governance_continuity(ingress_artifact=_artifact_from_args(args))
    if args.command == "approval" and args.approval_command == "list":
        return approval_list_command(replay_root=args.replay_root)
    if args.command == "approval" and args.approval_command == "show":
        return approval_show_command(approval_id=args.approval_id, replay_root=args.replay_root)
    if args.command == "approval" and args.approval_command == "pending":
        return approval_pending_command(replay_root=args.replay_root)
    if args.command == "approval" and args.approval_command == "approved":
        return approval_approved_command(replay_root=args.replay_root)
    if args.command == "approval" and args.approval_command == "rejected":
        return approval_rejected_command(replay_root=args.replay_root)
    if args.command == "approval" and args.approval_command == "chain":
        return approval_chain_command(canonical_chain_id=args.canonical_chain_id, replay_root=args.replay_root)
    if args.command == "continuity" and args.continuity_command == "preview":
        return continuity_preview_summary(ingress_artifact=_artifact_from_args(args))
    if args.command == "dispatch" and args.dispatch_command == "authorize":
        return authorize_dispatch(ingress_artifact=_artifact_from_args(args))
    if args.command == "bridge" and args.bridge_command == "list":
        return bridge_list_command(replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "show":
        return bridge_show_command(bridge_id=args.bridge_id, replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "pending":
        return bridge_pending_command(replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "approved":
        return bridge_approved_command(replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "rejected":
        return bridge_rejected_command(replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "chain":
        return bridge_chain_command(canonical_chain_id=args.canonical_chain_id, replay_root=args.replay_root)
    if args.command == "bridge" and args.bridge_command == "execution-request":
        return bridge_execution_request_command(
            execution_request_id=args.execution_request_id,
            replay_root=args.replay_root,
        )
    if args.command == "plan" and args.plan_command == "list":
        return plan_list_command(replay_root=args.replay_root)
    if args.command == "plan" and args.plan_command == "show":
        return plan_show_command(implementation_plan_id=args.implementation_plan_id, replay_root=args.replay_root)
    if args.command == "plan" and args.plan_command == "approved":
        return plan_approved_command(replay_root=args.replay_root)
    if args.command == "plan" and args.plan_command == "chain":
        return plan_chain_command(canonical_chain_id=args.canonical_chain_id, replay_root=args.replay_root)
    if args.command == "plan" and args.plan_command == "bridge":
        return plan_bridge_command(bridge_id=args.bridge_id, replay_root=args.replay_root)
    if args.command == "plan" and args.plan_command == "execution-request":
        return plan_execution_request_command(
            execution_request_id=args.execution_request_id,
            replay_root=args.replay_root,
        )
    if args.command == "plan" and args.plan_command == "latest":
        return plan_latest_command(replay_root=args.replay_root)
    if args.command == "dashboard":
        dashboard_subcommand = getattr(args, "dashboard_command", None)
        if dashboard_subcommand is None:
            return dashboard_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "summary":
            return dashboard_summary_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "approvals":
            return dashboard_approvals_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "bridges":
            return dashboard_bridges_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "chains":
            return dashboard_chains_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "learning":
            return dashboard_learning_command(replay_root=args.replay_root, limit=args.limit)
        if dashboard_subcommand == "execution":
            return dashboard_execution_command(replay_root=args.replay_root, limit=args.limit)
    if args.command == "execution" and args.execution_command == "handoff":
        return run_execution_handoff(
            ingress_artifact=_artifact_from_args(args),
            workspace_path=args.workspace_path or None,
            timeout_seconds=args.timeout_seconds,
            provider_success_proof=not args.full_codex_exec,
            runtime_root=args.runtime_root or None,
        )
    if args.command == "implementation" and args.implementation_command == "epoch":
        return run_implementation_generation_epoch(
            request=args.request,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            created_at=args.created_at,
            actor_id=args.actor_id,
        )
    if args.command == "implementation" and args.implementation_command == "real-epoch":
        return run_first_real_implementation_generation_epoch(
            human_request=args.request,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            created_at=args.created_at,
            actor_id=args.actor_id,
            operator_decision=args.decision or None,
            decision_reason=args.decision_reason or None,
        )
    if args.command == "implementation" and args.implementation_command == "compete":
        return run_multi_provider_competitive_proposal_runtime(
            human_request=args.request,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            created_at=args.created_at,
            actor_id=args.actor_id,
            selection=args.selection,
            decision_reason=args.decision_reason or None,
        )
    if args.command == "provider" and args.provider_command == "invoke":
        result = run_native_provider_execution(
            execution_id=args.execution_id,
            human_request=args.request,
            provider_id=args.provider_id,
            model=args.model,
            created_at=args.created_at,
            replay_dir=Path(args.runtime_root) / args.execution_id,
            human_approved=args.human_approved,
            approved_by=args.approved_by,
            credential_env=args.credential_env,
            timeout_seconds=args.timeout_seconds,
        )
        result["replay_reference"] = str(Path(args.runtime_root) / args.execution_id)
        return result
    if args.command == "provider" and args.provider_command == "governance":
        query_name = args.provider_governance_command
        query_handlers = {
            "status": query_provider_status,
            "credentials": query_provider_credentials,
            "usage": query_provider_usage,
            "failures": query_provider_failures,
            "costs": query_provider_costs,
            "participation": query_cognition_participation,
        }
        rows = query_handlers[query_name](args.replay_root)
        return {
            "command": f"aigol provider governance {query_name}",
            "query": query_name,
            "replay_root": args.replay_root,
            "rows": rows,
            "replay_visible": True,
        }
    if args.command == "provider" and args.provider_command == "credential":
        credential_command = args.provider_credential_command
        replay_dir = Path(args.replay_root) / args.provider_id / credential_command
        approval = _provider_credential_approval_artifact(args) if args.human_approved else None
        if credential_command == "add":
            event = add_provider_credential(
                provider_id=args.provider_id,
                credential_value=_provider_credential_value_from_env(args.credential_env),
                created_at=args.created_at,
                vault_path=args.vault_path,
                replay_dir=replay_dir,
                human_approval_artifact=approval,
            )
            return _provider_credential_command_result(args, event, replay_dir)
        if credential_command == "rotate":
            event = rotate_provider_credential(
                provider_id=args.provider_id,
                credential_value=_provider_credential_value_from_env(args.credential_env),
                created_at=args.created_at,
                vault_path=args.vault_path,
                replay_dir=replay_dir,
                human_approval_artifact=approval,
            )
            return _provider_credential_command_result(args, event, replay_dir)
        if credential_command == "verify":
            event = verify_provider_credential(
                provider_id=args.provider_id,
                created_at=args.created_at,
                vault_path=args.vault_path,
                replay_dir=replay_dir,
            )
            return _provider_credential_command_result(args, event, replay_dir)
        if credential_command == "disable":
            event = disable_provider_credential(
                provider_id=args.provider_id,
                created_at=args.created_at,
                human_approval_artifact=approval,
                vault_path=args.vault_path,
                replay_dir=replay_dir,
            )
            return _provider_credential_command_result(args, event, replay_dir)
        if credential_command == "delete":
            event = delete_provider_credential(
                provider_id=args.provider_id,
                created_at=args.created_at,
                human_approval_artifact=approval,
                vault_path=args.vault_path,
                replay_dir=replay_dir,
            )
            return _provider_credential_command_result(args, event, replay_dir)
        if credential_command == "history":
            history = provider_credential_history(provider_id=args.provider_id, vault_path=args.vault_path)
            return _provider_credential_command_result(args, history, replay_dir)
        if credential_command == "status":
            diagnostic = provider_credential_diagnostic(provider_id=args.provider_id, vault_path=args.vault_path)
            return _provider_credential_command_result(args, diagnostic, replay_dir)
    if args.command == "return" and args.return_command == "inspect":
        return inspect_return(replay_identity=args.replay_identity, runtime_root=args.runtime_root or None)
    if args.command == "replay" and args.replay_command == "ledger":
        return ledger_summary(runtime_root=args.runtime_root or None, limit=args.limit)
    if args.command == "replay" and args.replay_command == "verify":
        return verify_replay(replay_identity=args.replay_identity, runtime_root=args.runtime_root or None)
    if args.command == "replay" and args.replay_command == "operation":
        return summarize_governed_operation_replay(
            operation_id=args.operation_id,
            runtime_root=args.runtime_root,
        )
    if args.command == "replay" and args.replay_command == "report":
        return operator_operation_report(runtime_root=args.runtime_root, limit=args.limit)
    if args.command == "replay" and args.replay_command == "explain":
        return explain_operator_operation(operation_id=args.operation_id, runtime_root=args.runtime_root)
    if args.command == "diagnostics" and args.diagnostics_command == "runtime":
        return runtime_diagnostics(extension_id=args.extension_id)
    if args.command == "prompt" and args.prompt_command == "submit":
        return submit_prompt_to_conversation(
            human_prompt=args.prompt,
            prompt_id=args.prompt_id,
            created_at=args.created_at,
            replay_dir=args.runtime_root,
            operator_context=args.operator_context,
        )
    if args.command == "conversational" and args.conversational_command == "route":
        return route_conversational_cli_intent(
            routing_id=args.routing_id,
            prompt_id=args.prompt_id,
            human_prompt=args.prompt,
            canonical_chain_id=args.canonical_chain_id,
            created_at=args.created_at,
            replay_dir=Path(args.runtime_root) / args.routing_id,
        )
    if args.command == "clarification" and args.clarification_command == "unknown-domain":
        result = run_unknown_domain_clarification_workflow(
            clarification_id=args.clarification_id,
            prompt_id=args.prompt_id,
            human_prompt=args.prompt,
            canonical_chain_id=args.canonical_chain_id,
            created_at=args.created_at,
            replay_dir=Path(args.runtime_root) / args.clarification_id,
        )
        result["command"] = "aigol clarification unknown-domain"
        return result
    if args.command == "domain-reference" and args.domain_reference_command == "resolve":
        result = run_semantic_similarity_domain_reference_resolution(
            resolution_id=args.resolution_id,
            prompt_id=args.prompt_id,
            human_prompt=args.prompt,
            canonical_chain_id=args.canonical_chain_id,
            created_at=args.created_at,
            replay_dir=Path(args.runtime_root) / args.resolution_id,
        )
        result["command"] = "aigol domain-reference resolve"
        return result
    if args.command == "decision-support" and args.decision_support_command == "recommend":
        result = run_operator_decision_support(
            recommendation_id=args.recommendation_id,
            prompt_id=args.prompt_id,
            human_prompt=args.prompt,
            canonical_chain_id=args.canonical_chain_id,
            created_at=args.created_at,
            replay_dir=Path(args.runtime_root) / args.recommendation_id,
        )
        result["command"] = "aigol decision-support recommend"
        return result
    if args.command == "conversation":
        return {
            "command": "aigol conversation",
            "interactive_conversation_cli_version": INTERACTIVE_CONVERSATION_CLI_VERSION,
            "session_id": args.session_id,
            "runtime_root": str(Path(args.runtime_root) / args.session_id),
            "replay_visible": True,
            "worker_assigned": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_requested": False,
            "dispatch_requested": False,
            "invocation_requested": False,
        }
    if args.command == "show-latest-chain":
        return show_latest_chain_command(
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "show-chain":
        return show_chain_command(
            canonical_chain_id=args.canonical_chain_id,
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "show-execution-lifecycle":
        return show_execution_lifecycle_command(
            canonical_chain_id=args.canonical_chain_id,
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "show-learning-lifecycle":
        return show_learning_lifecycle_command(
            canonical_chain_id=args.canonical_chain_id,
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "show-full-lineage":
        return show_full_lineage_command(
            canonical_chain_id=args.canonical_chain_id,
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "show-chain-summary":
        return show_chain_summary_command(
            canonical_chain_id=args.canonical_chain_id,
            replay_root=args.replay_root,
            report_root=args.report_root,
            created_at=args.created_at,
        )
    if args.command == "run-governed":
        return run_governed_operation_command(
            worker=args.worker,
            operation=args.operation,
            target=args.target,
            content=args.content,
            operation_id=args.operation_id,
            created_at=args.created_at,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
        )
    if args.command == "moc" and args.moc_command == "validate-contract":
        return validate_contract_command(
            input_path=args.input,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "generate-contract":
        return generate_contract_command(
            input_path=args.input,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "validate-proposal":
        return validate_proposal_command(
            proposal_path=args.proposal,
            contract_path=args.contract,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "correction-feedback":
        return correction_feedback_command(
            validation_result_path=args.validation_result,
            attempt_number=args.attempt,
            max_attempts=args.max_attempts,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "persist-proposal":
        return persist_proposal_command(
            proposal_path=args.proposal,
            proposal_state=args.state,
            previous_state=args.previous_state,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "append-ledger":
        return append_ledger_command(
            persistence_record_path=args.persistence_record,
            ledger_path=args.ledger_path,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "approval-gate":
        return approval_gate_command(
            proposal_path=args.proposal,
            ledger_entry_path=args.ledger_entry,
            approval_evidence_path=args.approval_evidence,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "prepare-worker":
        return prepare_worker_command(
            proposal_path=args.proposal,
            approval_gate_path=args.approval_gate,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "dispatch-preview":
        return dispatch_preview_command(
            worker_package_path=args.worker_package,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "dispatch-request":
        return dispatch_request_command(
            dispatch_preview_path=args.dispatch_preview,
            request_evidence_path=args.request_evidence,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "dispatch-authorize":
        return dispatch_authorize_command(
            dispatch_request_path=args.dispatch_request,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "runtime-dispatch":
        return runtime_dispatch_command(
            dispatch_authorization_path=args.dispatch_authorization,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "provider-execution-gate":
        return provider_execution_gate_command(
            runtime_dispatch_path=args.runtime_dispatch,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "interpret-return":
        return interpret_return_command(
            runtime_dispatch_path=args.runtime_dispatch,
            provider_gate_path=args.provider_gate or None,
            return_evidence_path=args.return_evidence or None,
            output_path=args.output or None,
        )
    if args.command == "moc" and args.moc_command == "operational-lineage":
        return operational_lineage_command(
            contract_path=args.contract,
            proposal_path=args.proposal,
            approval_path=args.approval,
            runtime_dispatch_path=args.runtime_dispatch,
            governed_return_path=args.governed_return,
            provider_gate_path=args.provider_gate or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "inspect":
        return inspect_cognition(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "continuity-check":
        return check_semantic_replay_continuity(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "registry":
        return inspect_registry(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "topology":
        return inspect_topology(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "lifecycle":
        return inspect_lifecycle(
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "integrity":
        return inspect_integrity(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "authority":
        return inspect_authority(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "semantic-context":
        return inspect_semantic_context_state(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "semantic-relationships":
        return inspect_semantic_relationship_index(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "semantic-boundaries":
        return inspect_semantic_boundary_propagation(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "semantic-diff":
        return inspect_semantic_context_diff(
            source_path=args.source or None,
            target_path=args.target or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "semantic-audit-bundle":
        return inspect_semantic_context_audit_bundle(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    raise ValueError("unsupported command")


def render_command_result(result: dict) -> str:
    command = result.get("command", "")
    if command == "aigol status":
        return render_status(result)
    if command == "aigol runtime-status":
        return format_runtime_status(result)
    if command == "aigol runtime-progress":
        return format_runtime_progress(result)
    if command == "aigol runtime-watch":
        outputs = result.get("watch_outputs", [])
        if isinstance(outputs, list) and outputs:
            return "\n\n".join(str(output) for output in outputs)
        return format_runtime_progress(result)
    if command == "aigol ingress generate":
        artifact = result["ingress_artifact"]
        return render_card(
            "AIGOL INGRESS GENERATE",
            [
                f"artifact_type: {artifact.get('artifact_type')}",
                f"validation_status: {artifact.get('validation_status')}",
                f"replay_identity: {artifact.get('replay_identity')}",
                f"artifact_hash: {artifact.get('hashes', {}).get('artifact_hash')}",
                "execution_authority: false",
            ],
        )
    if command == "aigol governance validate":
        return render_card(
            "AIGOL GOVERNANCE VALIDATE",
            [
                f"governance_status: {result.get('governance_status')}",
                f"validation_status: {result.get('validation', {}).get('status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"hash_continuity: {_json(result.get('hash_continuity', {}))}",
            ],
        )
    if command == "aigol continuity preview":
        return render_card(
            "AIGOL CONTINUITY PREVIEW",
            [
                f"continuity_status: {result.get('continuity_status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"hash_continuity: {_json(result.get('hash_continuity', {}))}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"native_messaging_called: {result.get('native_messaging_called')}",
            ],
        )
    if command == "aigol implementation epoch":
        return render_implementation_epoch_summary(result)
    if command == "aigol implementation real-epoch":
        return render_first_real_implementation_generation_epoch(result)
    if command == "aigol implementation compete":
        return render_multi_provider_competitive_review(result)
    if command == "aigol provider invoke":
        return render_card(
            "AIGOL NATIVE PROVIDER EXECUTION",
            render_native_provider_execution_summary(result).splitlines()[1:],
        )
    if command.startswith("aigol provider governance "):
        return render_card(
            "AIGOL PROVIDER GOVERNANCE",
            render_provider_governance_query(result.get("query", "status"), result.get("rows", [])).splitlines(),
        )
    if command.startswith("aigol provider credential "):
        artifact = result.get("artifact", {})
        return render_card(
            "AIGOL PROVIDER CREDENTIAL",
            [
                f"operation: {result.get('operation')}",
                f"provider_id: {result.get('provider_id')}",
                f"credential_reference: {artifact.get('credential_reference')}",
                f"credential_present: {artifact.get('credential_present')}",
                f"credential_enabled: {artifact.get('credential_enabled')}",
                f"display_identifier: {artifact.get('display_identifier')}",
                f"credential_value_recorded: {artifact.get('credential_value_recorded')}",
                f"credential_hash_recorded: {artifact.get('credential_hash_recorded')}",
                f"replay_reference: {result.get('replay_reference')}",
            ],
        )
    if command in {
        "aigol approval list",
        "aigol approval show",
        "aigol approval pending",
        "aigol approval approved",
        "aigol approval rejected",
        "aigol approval chain",
    }:
        return render_card(
            "AIGOL APPROVAL",
            render_approval_summary(result).splitlines(),
        )
    if command in {
        "aigol bridge list",
        "aigol bridge show",
        "aigol bridge pending",
        "aigol bridge approved",
        "aigol bridge rejected",
        "aigol bridge chain",
        "aigol bridge execution-request",
    }:
        return render_card(
            "AIGOL BRIDGE",
            render_bridge_summary(result).splitlines(),
        )
    if command in {
        "aigol plan list",
        "aigol plan show",
        "aigol plan approved",
        "aigol plan chain",
        "aigol plan bridge",
        "aigol plan execution-request",
        "aigol plan latest",
    }:
        return render_card(
            "AIGOL PLAN",
            render_plan_summary(result).splitlines(),
        )
    if command in {
        "aigol dashboard",
        "aigol dashboard summary",
        "aigol dashboard approvals",
        "aigol dashboard bridges",
        "aigol dashboard chains",
        "aigol dashboard learning",
        "aigol dashboard execution",
    }:
        return render_card(
            "AIGOL DASHBOARD",
            render_dashboard_summary(result).splitlines(),
        )
    if command == "aigol dispatch authorize":
        return render_card(
            "AIGOL DISPATCH AUTHORIZE",
            [
                f"dispatch_status: {result.get('dispatch_status')}",
                f"dispatch_authorized: {result.get('dispatch_authorized')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"dispatch_authorization_hash: {result.get('dispatch_authorization_hash')}",
                "execution_performed: false",
            ],
        )
    if command == "aigol execution handoff":
        diagnostics = result.get("diagnostic_evidence", {})
        provider_state = "INVOKED" if result.get("provider_invoked") else "NOT_INVOKED"
        return_state = "GENERATED" if result.get("governed_return_hash") else "NOT_GENERATED"
        continuity_state = "VERIFIED" if result.get("continuity_verified") else "NOT_VERIFIED"
        return render_card(
            "AIGOL EXECUTION RESULT",
            [
                "Execution:",
                f"  {result.get('execution_status')}",
                "Provider:",
                f"  {provider_state}",
                "Command:",
                f"  {diagnostics.get('provider_command')}",
                "Replay:",
                f"  {result.get('replay_identity')}",
                "Governed Return:",
                f"  {return_state}",
                "Return Hash:",
                f"  {result.get('governed_return_hash')}",
                "Exit Code:",
                f"  {result.get('provider_exit_code')}",
                "Continuity:",
                f"  {continuity_state}",
                "Diagnostics:",
                f"  provider_executable_found: {diagnostics.get('provider_executable_found')}",
                f"  failure_stage: {diagnostics.get('failure_stage')}",
                f"  fail_closed: {result.get('fail_closed')}",
                f"  persistence: {result.get('persistence', {}).get('status')}",
            ],
        )
    if command == "aigol return inspect":
        return render_card(
            "AIGOL RETURN INSPECT",
            [
                f"status: {result.get('status')}",
                f"execution_status: {result.get('execution_status')}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"governed_return_hash: {result.get('governed_return_hash')}",
                f"continuity_verified: {result.get('continuity_verified')}",
                f"fail_closed: {result.get('fail_closed')}",
                f"evidence_path: {result.get('evidence_path', '')}",
            ],
        )
    if command == "aigol replay ledger":
        lines = []
        for entry in result.get("entries", []):
            lines.append(
                f"{entry.get('replay_identity')} | {entry.get('execution_status')} | {entry.get('governed_return_hash')}"
            )
        return render_card("AIGOL REPLAY LEDGER", lines or ["NO GOVERNED RETURNS"])
    if command == "aigol replay verify":
        return render_card(
            "AIGOL REPLAY VERIFY",
            [
                f"status: {result.get('status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"governed_return_hash_valid: {result.get('governed_return_hash_valid')}",
                f"execution_result_hash_present: {result.get('execution_result_hash_present')}",
                f"evidence_files_exist: {result.get('evidence_files_exist')}",
                f"ledger_entry_exists: {result.get('ledger_entry_exists')}",
                f"lineage_continuity_exists: {result.get('lineage_continuity_exists')}",
                f"fail_closed: {result.get('fail_closed')}",
            ],
        )
    if command == "aigol replay operation":
        return render_card(
            "AIGOL REPLAY OPERATION",
            [
                f"status: {result.get('status')}",
                f"operator_status: {result.get('operator_status')}",
                f"execution_status: {result.get('execution_status')}",
                f"operation_id: {result.get('operation_id')}",
                f"proposal_id: {result.get('proposal_id')}",
                f"authorization_id: {result.get('authorization_id')}",
                f"worker_id: {result.get('worker_id')}",
                f"worker_result: {_json(result.get('worker_result', {}))}",
                f"replay_id: {result.get('replay_id')}",
                f"replay_reference: {result.get('replay_reference')}",
                f"replay_summary: {_json(result.get('replay_summary', {}))}",
                f"fail_closed: {result.get('fail_closed')}",
                f"failure_reason: {result.get('failure_reason', '')}",
            ],
        )
    if command == "aigol replay report":
        stats = result.get("statistics", {})
        lines = [
            f"status: {result.get('status')}",
            f"runtime_root: {result.get('runtime_root')}",
            f"operation_count: {result.get('operation_count')}",
            f"total_operations: {stats.get('total_operations')}",
            f"successful_operations: {stats.get('successful_operations')}",
            f"fail_closed_operations: {stats.get('fail_closed_operations')}",
            f"verification_failures: {stats.get('verification_failures')}",
            f"success_rate: {stats.get('success_rate')}",
            f"fail_closed_rate: {stats.get('fail_closed_rate')}",
            f"worker_usage: {_json(stats.get('worker_usage', {}))}",
            f"operation_type_usage: {_json(stats.get('operation_type_usage', {}))}",
            f"weekly_usage_summary: {result.get('weekly_usage_summary')}",
            f"replay_backed: {result.get('replay_backed')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason', '')}",
        ]
        for entry in result.get("entries", []):
            lines.append(
                "operation: "
                f"{entry.get('operation_id')} | "
                f"{entry.get('status')} | "
                f"{entry.get('worker')} | "
                f"{entry.get('operation')} | "
                f"{entry.get('replay_status')}"
            )
        return render_card("AIGOL REPLAY REPORT", lines)
    if command == "aigol replay explain":
        return render_card(
            "AIGOL REPLAY EXPLAIN",
            [
                f"status: {result.get('status')}",
                f"operation_id: {result.get('operation_id')}",
                f"explanation_type: {result.get('explanation_type')}",
                f"what_happened: {result.get('what_happened')}",
                f"why_it_happened: {result.get('why_it_happened')}",
                f"why_authorized: {result.get('why_authorized')}",
                f"trust_explanation: {result.get('trust_explanation')}",
                f"replay_backed: {result.get('replay_backed')}",
                f"fail_closed: {result.get('fail_closed')}",
                f"failure_reason: {result.get('failure_reason', '')}",
            ],
        )
    if command == "aigol diagnostics runtime":
        diagnostics = result.get("runtime_diagnostics", {})
        return render_card(
            "AIGOL DIAGNOSTICS RUNTIME",
            [
                f"native_host_launch_ready: {diagnostics.get('native_host_launch_ready')}",
                f"chrome_runtime_launch_allowed: {diagnostics.get('chrome_runtime_launch_allowed')}",
                f"failure_stage: {result.get('failure_stage')}",
            ],
        )
    if command == "aigol prompt submit":
        return render_card(
            "AIGOL PROMPT SUBMIT",
            [
                f"prompt_id: {result.get('prompt_id')}",
                f"prompt_status: {result.get('prompt_status')}",
                f"classification_destination: {result.get('classification_destination')}",
                f"routing_destination: {result.get('routing_destination')}",
                f"cognition_path_entered: {result.get('cognition_path_entered')}",
                f"response_status: {result.get('response_status')}",
                f"response_source: {result.get('response_source')}",
                f"response_text: {result.get('response_text')}",
                f"canonical_chain_id: {result.get('canonical_chain_id')}",
                f"current_chain_id: {result.get('current_chain_id')}",
                f"latest_chain_id: {result.get('latest_chain_id')}",
                f"suggested_inspection_commands: {_json({'commands': result.get('suggested_inspection_commands', [])})}",
                f"replay_reference: {result.get('replay_reference')}",
                f"conversation_replay_reference: {result.get('conversation_replay_reference')}",
                f"provider_used: {result.get('provider_used')}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"worker_invoked: {result.get('worker_invoked')}",
                f"execution_requested: {result.get('execution_requested')}",
                f"fail_closed: {result.get('fail_closed')}",
                f"failure_reason: {result.get('failure_reason') or ''}",
            ],
        )
    if command == "aigol conversational route":
        return render_card(
            "AIGOL CONVERSATIONAL ROUTING",
            render_conversational_cli_routing_summary(result).splitlines(),
        )
    if command == "aigol clarification unknown-domain":
        return render_card(
            "AIGOL UNKNOWN DOMAIN CLARIFICATION",
            render_unknown_domain_clarification_workflow(result).splitlines(),
        )
    if command == "aigol domain-reference resolve":
        return render_card(
            "AIGOL DOMAIN REFERENCE RESOLUTION",
            render_domain_reference_resolution_summary(result).splitlines(),
        )
    if command == "aigol decision-support recommend":
        return render_card(
            "AIGOL OPERATOR DECISION SUPPORT",
            render_operator_decision_support_summary(result).splitlines(),
        )
    if command == "aigol conversation":
        return render_card(
            "AIGOL CONVERSATION",
            [
                f"session_id: {result.get('session_id')}",
                f"runtime_root: {result.get('runtime_root')}",
                f"session_resumed: {result.get('session_resumed')}",
                f"existing_turn_count: {result.get('existing_turn_count')}",
                f"next_turn_id_at_start: {result.get('next_turn_id_at_start')}",
                f"current_chain_id: {result.get('current_chain_id')}",
                f"latest_chain_id: {result.get('latest_chain_id')}",
                f"turn_count: {result.get('turn_count', 0)}",
                f"failed_turns: {result.get('failed_turns', 0)}",
                f"exit_reason: {result.get('exit_reason', '')}",
                f"replay_visible: {result.get('replay_visible')}",
                f"worker_assigned: {result.get('worker_assigned')}",
                f"worker_dispatched: {result.get('worker_dispatched')}",
                f"worker_invoked: {result.get('worker_invoked')}",
                f"execution_requested: {result.get('execution_requested')}",
                f"dispatch_requested: {result.get('dispatch_requested')}",
                f"invocation_requested: {result.get('invocation_requested')}",
            ],
        )
    if command in {
        "aigol show-latest-chain",
        "aigol show-chain",
        "aigol show-execution-lifecycle",
        "aigol show-learning-lifecycle",
        "aigol show-full-lineage",
        "aigol show-chain-summary",
    }:
        return render_card(
            "AIGOL CHAIN INSPECTION",
            render_chain_inspection_summary(result).splitlines(),
        )
    if command == "aigol run-governed":
        return render_card(
            "AIGOL RUN GOVERNED",
            [
                f"status: {result.get('status')}",
                f"operator_status: {result.get('operator_status')}",
                f"execution_status: {result.get('execution_status')}",
                f"proposal_id: {result.get('proposal_id')}",
                f"authorization_id: {result.get('authorization_id')}",
                f"worker_id: {result.get('worker_id')}",
                f"worker_result: {_json(result.get('worker_result', {}))}",
                f"replay_id: {result.get('replay_id')}",
                f"replay_reference: {result.get('replay_reference')}",
                f"replay_summary: {_json(result.get('replay_summary', {}))}",
                f"target: {result.get('target')}",
                f"fail_closed: {result.get('fail_closed')}",
                f"failure_reason: {result.get('failure_reason', '')}",
            ],
        )
    if command == "aigol moc validate-contract":
        validation = result.get("contract_validation_result", {})
        return render_card(
            "AIGOL MOC VALIDATE CONTRACT",
            render_contract_validation_summary(validation).splitlines(),
        )
    if command == "aigol moc generate-contract":
        generation = result.get("advisory_contract_generation_result", {})
        return render_card(
            "AIGOL MOC GENERATE CONTRACT",
            render_advisory_contract_generation_summary(generation).splitlines(),
        )
    if command == "aigol moc validate-proposal":
        validation = result.get("advisory_proposal_validation_result", {})
        return render_card(
            "AIGOL MOC VALIDATE PROPOSAL",
            render_advisory_proposal_validation_summary(validation).splitlines(),
        )
    if command == "aigol moc correction-feedback":
        feedback = result.get("proposal_correction_feedback", {})
        return render_card(
            "AIGOL MOC CORRECTION FEEDBACK",
            render_proposal_correction_feedback_summary(feedback).splitlines(),
        )
    if command == "aigol moc persist-proposal":
        record = result.get("proposal_persistence_record", {})
        return render_card(
            "AIGOL MOC PERSIST PROPOSAL",
            render_proposal_persistence_summary(record).splitlines(),
        )
    if command == "aigol moc append-ledger":
        entry = result.get("proposal_ledger_entry", {})
        return render_card(
            "AIGOL MOC APPEND LEDGER",
            render_proposal_ledger_summary(entry).splitlines(),
        )
    if command == "aigol moc approval-gate":
        approval = result.get("approval_gate_result", {})
        return render_card(
            "AIGOL MOC APPROVAL GATE",
            render_approval_gate_summary(approval).splitlines(),
        )
    if command == "aigol moc prepare-worker":
        package = result.get("worker_preparation_package", {})
        return render_card(
            "AIGOL MOC PREPARE WORKER",
            render_worker_preparation_summary(package).splitlines(),
        )
    if command == "aigol moc dispatch-preview":
        preview = result.get("dispatch_authorization_preview", {})
        return render_card(
            "AIGOL MOC DISPATCH PREVIEW",
            render_dispatch_authorization_preview_summary(preview).splitlines(),
        )
    if command == "aigol moc dispatch-request":
        request = result.get("worker_dispatch_request", {})
        return render_card(
            "AIGOL MOC DISPATCH REQUEST",
            render_worker_dispatch_request_summary(request).splitlines(),
        )
    if command == "aigol moc dispatch-authorize":
        authorization = result.get("worker_dispatch_authorization", {})
        return render_card(
            "AIGOL MOC DISPATCH AUTHORIZE",
            render_worker_dispatch_authorization_summary(authorization).splitlines(),
        )
    if command == "aigol moc runtime-dispatch":
        dispatch_event = result.get("runtime_dispatch_event", {})
        return render_card(
            "AIGOL MOC RUNTIME DISPATCH",
            render_runtime_dispatch_summary(dispatch_event).splitlines(),
        )
    if command == "aigol moc provider-execution-gate":
        gate = result.get("provider_execution_gate", {})
        return render_card(
            "AIGOL MOC PROVIDER EXECUTION GATE",
            render_provider_execution_gate_summary(gate).splitlines(),
        )
    if command == "aigol moc interpret-return":
        interpretation = result.get("governed_return_interpretation", {})
        return render_card(
            "AIGOL MOC INTERPRET RETURN",
            render_governed_return_interpretation_summary(interpretation).splitlines(),
        )
    if command == "aigol moc operational-lineage":
        lineage = result.get("operational_lineage", {})
        return render_card(
            "AIGOL MOC OPERATIONAL LINEAGE",
            render_operational_lineage_summary(lineage).splitlines(),
        )
    if command == "aigol cognition inspect":
        envelope = result.get("cognition_state_envelope", {})
        return render_card(
            "AIGOL COGNITION INSPECT",
            render_cognition_summary(envelope).splitlines(),
        )
    if command == "aigol cognition continuity-check":
        check = result.get("semantic_replay_continuity_check", {})
        return render_card(
            "AIGOL COGNITION CONTINUITY CHECK",
            render_semantic_replay_report(check).splitlines(),
        )
    if command == "aigol cognition registry":
        registry = result.get("cognition_registry", {})
        validation = result.get("registry_validation", {})
        return render_card(
            "AIGOL COGNITION REGISTRY",
            render_cognition_registry_summary(registry, validation).splitlines(),
        )
    if command == "aigol cognition topology":
        report = result.get("cognition_topology_report", {})
        return render_card(
            "AIGOL COGNITION TOPOLOGY",
            render_cognition_topology_summary(report).splitlines(),
        )
    if command == "aigol cognition lifecycle":
        model = result.get("cognition_lifecycle_model", {})
        return render_card(
            "AIGOL COGNITION LIFECYCLE",
            render_cognition_lifecycle_summary(model).splitlines(),
        )
    if command == "aigol cognition integrity":
        summary = result.get("cognition_integrity_summary", {})
        return render_card(
            "AIGOL COGNITION INTEGRITY",
            render_cognition_integrity_summary(summary).splitlines(),
        )
    if command == "aigol cognition authority":
        artifact = result.get("authority_propagation_verifier", {})
        return render_card(
            "AIGOL COGNITION AUTHORITY",
            render_authority_propagation_summary(artifact).splitlines(),
        )
    if command == "aigol cognition semantic-context":
        state = result.get("semantic_context_state", {})
        return render_card(
            "AIGOL COGNITION SEMANTIC CONTEXT",
            render_semantic_context_summary(state).splitlines(),
        )
    if command == "aigol cognition semantic-relationships":
        index = result.get("semantic_relationship_index", {})
        return render_card(
            "AIGOL COGNITION SEMANTIC RELATIONSHIPS",
            render_semantic_relationship_summary(index).splitlines(),
        )
    if command == "aigol cognition semantic-boundaries":
        propagation = result.get("semantic_boundary_propagation", {})
        return render_card(
            "AIGOL COGNITION SEMANTIC BOUNDARIES",
            render_semantic_boundary_summary(propagation).splitlines(),
        )
    if command == "aigol cognition semantic-diff":
        diff = result.get("semantic_context_diff", {})
        return render_card(
            "AIGOL COGNITION SEMANTIC DIFF",
            render_semantic_diff_summary(diff).splitlines(),
        )
    if command == "aigol cognition semantic-audit-bundle":
        bundle = result.get("semantic_context_audit_bundle", {})
        return render_card(
            "AIGOL COGNITION SEMANTIC AUDIT BUNDLE",
            render_semantic_audit_bundle_summary(bundle).splitlines(),
        )
    return render_card("AIGOL", [_json(result)])


def _interactive_real_epoch_decision_callback(checkpoint: dict[str, Any]) -> dict[str, str]:
    print(
        render_card(
            "AIGOL INTERACTIVE ACCEPTANCE CHECKPOINT",
            [
                f"request: {checkpoint.get('request_summary')}",
                f"purpose: {checkpoint.get('generated_implementation_summary', {}).get('purpose')}",
                "planned_functionality: "
                + _json(checkpoint.get("generated_implementation_summary", {}).get("planned_functionality", [])),
                "manifest: " + _json(checkpoint.get("manifest_summary", {})),
                "affected_paths:",
                *[f"  {path}" for path in checkpoint.get("affected_paths", [])],
                "choices: APPROVE | REJECT | ABORT",
            ],
        )
    )
    decision = input("Decision [APPROVE/REJECT/ABORT]: ").strip()
    reason = input("Decision reason: ").strip()
    return {
        "decision": decision,
        "decision_reason": reason or f"Operator selected {decision}.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "conversation":
        result = run_interactive_conversation(args)
        if getattr(args, "json", False):
            print(_json(result))
        return 0
    if (
        args.command == "implementation"
        and args.implementation_command == "real-epoch"
        and not args.decision
    ):
        result = run_first_real_implementation_generation_epoch(
            human_request=args.request,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            created_at=args.created_at,
            actor_id=args.actor_id,
            decision_reason=args.decision_reason or None,
            operator_decision_callback=_interactive_real_epoch_decision_callback,
        )
        if getattr(args, "json", False):
            print(_json(result))
        else:
            print(render_command_result(result))
        return 0
    result = run_command(args)
    if getattr(args, "json", False):
        print(_json(result))
    else:
        print(render_command_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
