"""Canonical deterministic AiGOL governance CLI foundation."""

from __future__ import annotations

import argparse
import json
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
from aigol.runtime.conversation_native_development_intent_routing import (
    NATIVE_DEVELOPMENT_INTENT_ROUTED,
    is_conversation_native_development_intent,
    render_native_development_intent_routing_summary,
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    render_conversation_to_ppp_handoff_execution_summary,
    run_conversation_to_ppp_handoff_execution,
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
    render_conversation_native_development_context_summary,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.source_of_truth_router_runtime import route_source_of_truth


INTERACTIVE_CONVERSATION_CLI_VERSION = "INTERACTIVE_CONVERSATION_CLI_V1"
INTERACTIVE_EXIT_COMMANDS = frozenset({"exit", "quit"})


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


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

    conversation = subcommands.add_parser("conversation")
    conversation.add_argument("--session-id", default="AIGOL-INTERACTIVE-CONVERSATION-000001")
    conversation.add_argument("--created-at", default="2026-06-01T00:00:00Z")
    conversation.add_argument("--runtime-root", default=".aigol_conversation_runtime")
    conversation.add_argument("--operator-context", default="interactive_conversation_cli")

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
) -> dict[str, Any]:
    input_reader = input if input_func is None else input_func
    output_writer = print if output_func is None else output_func
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
    initial_resume = resume_conversation_session(session_id=session_id, runtime_root=runtime_root, created_at=created_at)

    while True:
        try:
            raw_prompt = input_reader("AiGOL > ")
        except EOFError:
            exit_reason = "EOF"
            break

        human_prompt = raw_prompt.strip()
        if not human_prompt:
            continue
        if human_prompt.lower() in INTERACTIVE_EXIT_COMMANDS:
            break

        turn_count += 1
        turn_id = "TURN-UNALLOCATED"
        prompt_id = f"{session_id}:{turn_id}"
        turn_root = session_root / turn_id
        try:
            resume_state = resume_conversation_session(
                session_id=session_id,
                runtime_root=runtime_root,
                created_at=created_at,
            )
            turn_id = resume_state["next_turn_id"]
            prompt_id = f"{session_id}:{turn_id}"
            turn_root = session_root / turn_id
            router_capture = route_source_of_truth(
                router_id=f"{prompt_id}:SOURCE_ROUTER",
                human_prompt_reference=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                replay_dir=turn_root / "source_router",
            )
            if is_conversation_native_development_intent(human_prompt):
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
                    if routing_capture["fail_closed"]:
                        failed_turns += 1
                        output_writer(f"FAILED_CLOSED: {routing_capture['failure_reason']}")
                    else:
                        output_writer(render_conversation_to_ppp_handoff_execution_summary(ppp_capture))
                turns.append(
                    _interactive_native_development_intent_routing_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        routing_capture=routing_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            elif is_native_development_prompt(human_prompt):
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
                    output_writer(render_conversation_native_development_context_summary(native_context_capture))
                turns.append(
                    _interactive_native_development_turn_summary(
                        turn_id=turn_id,
                        prompt_id=prompt_id,
                        router_capture=router_capture,
                        native_context_capture=native_context_capture,
                        source_router_replay_reference=str(turn_root / "source_router"),
                    )
                )
            else:
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
        except Exception as exc:
            failed_turns += 1
            failure_reason = str(exc) or "interactive conversation failed closed"
            output_writer(f"FAILED_CLOSED: {failure_reason}")
            turns.append(
                _interactive_failed_turn_summary(
                    turn_id=turn_id,
                    prompt_id=prompt_id,
                    source_router_replay_reference=str(turn_root / "source_router"),
                    failure_reason=failure_reason,
                )
            )

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
        "current_chain_id": current_chain_id,
        "latest_chain_id": latest_chain_id,
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
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
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }


def _interactive_native_development_intent_routing_turn_summary(
    *,
    turn_id: str,
    prompt_id: str,
    router_capture: dict[str, Any],
    routing_capture: dict[str, Any],
    source_router_replay_reference: str,
) -> dict[str, Any]:
    source_artifact = router_capture["source_of_truth_router_artifact"]
    ppp_capture = routing_capture.get("conversation_to_ppp_handoff_execution")
    if not isinstance(ppp_capture, dict):
        ppp_capture = {}
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
        "recognized_development_task": routing_capture.get("routing_status") == NATIVE_DEVELOPMENT_INTENT_ROUTED,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
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
        "context_hash": native_context_capture.get("context_hash"),
        "missing_context": native_context_capture.get("missing_context", []),
        "ambiguous_context": native_context_capture.get("ambiguous_context", []),
        "provider_necessity_classification": native_context_capture.get("provider_necessity_classification"),
        "suggested_next_actions": native_context_capture.get("suggested_next_actions", []),
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }


def _require_cli_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


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
    if args.command == "conversation":
        return {
            "command": "aigol conversation",
            "interactive_conversation_cli_version": INTERACTIVE_CONVERSATION_CLI_VERSION,
            "session_id": args.session_id,
            "runtime_root": str(Path(args.runtime_root) / args.session_id),
            "replay_visible": True,
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "conversation":
        result = run_interactive_conversation(args)
        if getattr(args, "json", False):
            print(_json(result))
        return 0
    result = run_command(args)
    if getattr(args, "json", False):
        print(_json(result))
    else:
        print(render_command_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
