"""Conversational CLI workflow routing for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.canonical_semantic_artifact_runtime import create_canonical_semantic_artifact_from_translation
from aigol.runtime.human_execution_intent_detection import (
    GENERIC_GOVERNED_ARTIFACT_CREATION,
    GENERIC_GOVERNED_DOMAIN_CREATION,
    GENERIC_GOVERNED_EXECUTION_REQUEST,
    detect_human_execution_intent,
)
from aigol.runtime.human_intent_clarification_intake_runtime import (
    HUMAN_INTENT_CLARIFICATION_INTAKE,
    classify_development_intent_for_governed_routing,
    classify_human_intent_for_clarification_from_canonical_semantic_artifact,
    classify_human_intent_for_clarification,
)
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance
from aigol.runtime.domain_handoff_review_approval_binding_runtime import detect_domain_approval_entry_intent
from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    detect_domain_execution_ready_entry_intent,
)
from aigol.runtime.execution_authorization_runtime import detect_domain_execution_authorization_entry_intent
from aigol.runtime.execution_runtime import detect_domain_worker_execution_entry_intent
from aigol.runtime.worker_result_capture_runtime import detect_domain_worker_result_capture_entry_intent
from aigol.runtime.worker_result_validation_runtime import detect_domain_worker_result_validation_entry_intent
from aigol.runtime.post_execution_replay_review_runtime import detect_domain_post_execution_replay_review_entry_intent
from aigol.runtime.governed_termination_runtime import detect_domain_governed_termination_entry_intent
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_cognition_result_integration_runtime import (
    integrate_ocs_cognition_result_into_canonical_semantic_artifact,
)
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import (
    orchestrate_ubtr_semantic_cognition,
)
from aigol.runtime.ubtr_ocs_cognition_handoff_runtime import run_ubtr_ocs_cognition_handoff
from aigol.runtime.worker_assignment_runtime import detect_domain_worker_assignment_entry_intent
from aigol.runtime.worker_dispatch_runtime import detect_domain_worker_dispatch_entry_intent
from aigol.runtime.worker_invocation_runtime import detect_domain_worker_invocation_entry_intent
from aigol.runtime.worker_invocation_request_runtime import detect_domain_worker_request_entry_intent
from aigol.runtime.conversation_native_development_intent_routing import is_conversation_native_development_intent
from aigol.runtime.native_development_task_intake_runtime import is_plain_native_development_prompt


MILESTONE_ID = "AIGOL_CONVERSATIONAL_CLI_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_CONVERSATIONAL_CLI_RUNTIME_STATUS"

CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1 = "CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1"
CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1 = "CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1"
SEMANTIC_REPLAY_COMPARISON_ARTIFACT_V1 = "SEMANTIC_REPLAY_COMPARISON_ARTIFACT_V1"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_01_REPLAY_COMPARISON_SUBSTRATE_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_01_REPLAY_COMPARISON_SUBSTRATE_V1"
)
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_PROPOSAL_ONLY_OCS_ROUTING_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_PROPOSAL_ONLY_OCS_ROUTING_V1"
)

WORKFLOW_SELECTED = "WORKFLOW_SELECTED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

CREATE_DOMAIN_TRADING = "CREATE_DOMAIN_TRADING"
CREATE_DOMAIN_MARKETING = "CREATE_DOMAIN_MARKETING"
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
DOMAIN_ADAPTATION_REFERENCE = "DOMAIN_ADAPTATION_REFERENCE"
OPERATOR_DECISION_SUPPORT = "OPERATOR_DECISION_SUPPORT"
SHOW_LATEST_REPLAY_CHAIN = "SHOW_LATEST_REPLAY_CHAIN"
REVIEW_LATEST_AUDIT = "REVIEW_LATEST_AUDIT"
IMPROVE_PROVIDER_LAYER = "IMPROVE_PROVIDER_LAYER"
SHOW_STATUS = "SHOW_STATUS"
SHOW_DASHBOARD = "SHOW_DASHBOARD"
OCS_LLM_COGNITION = "OCS_LLM_COGNITION"
BOUNDED_FILE_WRITE_WORKER_USER_SESSION = "BOUNDED_FILE_WRITE_WORKER_USER_SESSION"
NATIVE_DEVELOPMENT_INTENT_ROUTING = "NATIVE_DEVELOPMENT_INTENT_ROUTING"
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION = "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
DOMAIN_LIFECYCLE_GOVERNANCE = "DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME"
CAPABILITY_LIFECYCLE_GOVERNANCE = "CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME"
PROPOSAL_RUNTIME = "PROPOSAL_RUNTIME"
IMPROVEMENT_PROPOSAL_RUNTIME = "IMPROVEMENT_PROPOSAL_RUNTIME"
FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH = "FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH"
IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST = "IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME"
AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION = "AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION"
AI_DECISION_VALIDATOR_CAPABILITY_MODEL = "AI_DECISION_VALIDATOR_CAPABILITY_MODEL"
AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE = "AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE"
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW = "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW"
DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE = "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE"
DOMAIN_EXECUTION_AUTHORIZATION = "DOMAIN_EXECUTION_AUTHORIZATION"
DOMAIN_WORKER_REQUEST = "DOMAIN_WORKER_REQUEST"
DOMAIN_WORKER_ASSIGNMENT = "DOMAIN_WORKER_ASSIGNMENT"
DOMAIN_WORKER_DISPATCH = "DOMAIN_WORKER_DISPATCH"
DOMAIN_WORKER_INVOCATION = "DOMAIN_WORKER_INVOCATION"
DOMAIN_WORKER_EXECUTION = "DOMAIN_WORKER_EXECUTION"
DOMAIN_WORKER_RESULT_CAPTURE = "DOMAIN_WORKER_RESULT_CAPTURE"
DOMAIN_WORKER_RESULT_VALIDATION = "DOMAIN_WORKER_RESULT_VALIDATION"
DOMAIN_POST_EXECUTION_REPLAY_REVIEW = "DOMAIN_POST_EXECUTION_REPLAY_REVIEW"
DOMAIN_GOVERNED_TERMINATION = "DOMAIN_GOVERNED_TERMINATION"
GOVERNANCE_ARTIFACT_CREATION = "GOVERNANCE_ARTIFACT_CREATION"
GOVERNED_REPOSITORY_MUTATION = "GOVERNED_REPOSITORY_MUTATION"
GOVERNED_DEVELOPMENT_WORKFLOW = "GOVERNED_DEVELOPMENT_WORKFLOW"
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = "DEFAULT_PROVIDER_ASSISTED_CONVERSATION"
PROVIDER_ONBOARDING_DOMAIN = "PROVIDER_ONBOARDING_DOMAIN"

REPLAY_STEPS = (
    "conversational_routing_decision_recorded",
    "conversational_workflow_selection_recorded",
    "conversational_routing_returned",
)


def route_conversational_cli_intent(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Route natural language to an existing certified workflow selection."""

    replay_path = Path(replay_dir)
    universal_translation_capture: dict[str, Any] | None = None
    canonical_semantic_capture: dict[str, Any] | None = None
    ubtr_cognition_orchestration_capture: dict[str, Any] | None = None
    ubtr_ocs_cognition_handoff_capture: dict[str, Any] | None = None
    ubtr_cognition_result_integration_capture: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        universal_translation_capture = translate_human_to_governance(
            translation_request_id=f"{routing_id}:UNIVERSAL-TRANSLATION",
            human_request=human_prompt,
            created_at=created_at,
            replay_dir=replay_path / "universal_translation" / "human_to_governance",
            session_context={"canonical_chain_id": canonical_chain_id, "prompt_id": prompt_id},
            available_workflows=[entry["workflow_id"] for entry in workflow_registry()],
        )
        canonical_semantic_capture = create_canonical_semantic_artifact_from_translation(
            semantic_artifact_id=f"{routing_id}:CANONICAL-SEMANTIC",
            translation_artifact=universal_translation_capture["translation_artifact"],
            conversation_id=canonical_chain_id,
            workflow_id=None,
            created_at=created_at,
            replay_dir=replay_path / "canonical_semantic_artifact",
        )
        ubtr_cognition_orchestration_capture = orchestrate_ubtr_semantic_cognition(
            orchestration_id=f"{routing_id}:UBTR-SEMANTIC-COGNITION",
            canonical_semantic_artifact=canonical_semantic_capture["semantic_artifact"],
            created_at=created_at,
            replay_dir=replay_path / "ubtr_semantic_cognition_orchestration",
        )
        if ubtr_cognition_orchestration_capture.get("ocs_cognition_request_hash"):
            ubtr_ocs_cognition_handoff_capture = run_ubtr_ocs_cognition_handoff(
                handoff_id=f"{routing_id}:UBTR-OCS-COGNITION-HANDOFF",
                ubtr_orchestration_artifact=ubtr_cognition_orchestration_capture["orchestration_artifact"],
                created_at=created_at,
                replay_dir=replay_path / "ubtr_ocs_cognition_handoff",
            )
            if ubtr_ocs_cognition_handoff_capture.get("fail_closed") is not True:
                ubtr_cognition_result_integration_capture = (
                    integrate_ocs_cognition_result_into_canonical_semantic_artifact(
                        integration_id=f"{routing_id}:UBTR-COGNITION-INTEGRATED-SEMANTIC",
                        prior_canonical_semantic_artifact=canonical_semantic_capture["semantic_artifact"],
                        ubtr_ocs_cognition_handoff_artifact=ubtr_ocs_cognition_handoff_capture["handoff_artifact"],
                        created_at=created_at,
                        replay_dir=replay_path / "ubtr_cognition_result_integration",
                    )
                )
        compatibility_route_evidence = _compatibility_route_evidence(human_prompt)
        csa_analysis = _classify_workflow_from_canonical_semantic_artifact(
            canonical_semantic_capture,
            compatibility_route_evidence=compatibility_route_evidence,
        )
        if not csa_analysis:
            csa_analysis = _classify_hirr_from_canonical_semantic_artifact(
                canonical_semantic_capture,
                compatibility_route_evidence=compatibility_route_evidence,
            )
        if not csa_analysis:
            csa_analysis = _classify_proposal_only_ocs_from_canonical_semantic_artifact(
                canonical_semantic_capture,
                compatibility_route_evidence=compatibility_route_evidence,
            )
        semantic_comparison_artifact = _semantic_replay_comparison_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            canonical_semantic_capture=canonical_semantic_capture,
            compatibility_route_evidence=compatibility_route_evidence,
        )
        if not csa_analysis:
            compatibility_route_evidence = None
        analysis = csa_analysis or _classify_workflow(human_prompt)
        decision = _routing_decision_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            analysis=analysis,
            universal_translation_capture=universal_translation_capture,
            canonical_semantic_capture=canonical_semantic_capture,
            ubtr_cognition_orchestration_capture=ubtr_cognition_orchestration_capture,
            ubtr_ocs_cognition_handoff_capture=ubtr_ocs_cognition_handoff_capture,
            ubtr_cognition_result_integration_capture=ubtr_cognition_result_integration_capture,
            compatibility_route_evidence=compatibility_route_evidence,
            semantic_comparison_artifact=semantic_comparison_artifact,
            failure_reason=None,
        )
        selection = _workflow_selection_artifact(
            routing_id=routing_id,
            decision=decision,
            analysis=analysis,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        returned = _returned_artifact(decision, selection)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], selection)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(decision, selection, returned, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "conversational CLI routing failed closed"
        decision = _failed_decision_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        selection = _failed_selection_artifact(
            routing_id=routing_id,
            decision=decision,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(decision, selection)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], selection)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(decision, selection, returned, replay_path)


def reconstruct_conversational_cli_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversational CLI routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversational CLI routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversational CLI routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    selection = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if selection.get("routing_decision_reference") != decision["routing_decision_id"]:
        raise FailClosedRuntimeError("conversational CLI routing decision reference mismatch")
    if selection.get("routing_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("conversational CLI routing decision hash mismatch")
    if returned.get("workflow_selection_reference") != selection["workflow_selection_id"]:
        raise FailClosedRuntimeError("conversational CLI routing returned reference mismatch")
    comparison_artifact = decision.get("semantic_comparison_artifact")
    if isinstance(comparison_artifact, dict):
        _verify_artifact_hash(comparison_artifact)
        if decision.get("semantic_comparison_hash") != comparison_artifact["artifact_hash"]:
            raise FailClosedRuntimeError("conversational CLI semantic comparison hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "routing_status": returned["routing_status"],
        "workflow_id": returned["workflow_id"],
        "existing_runtime": selection.get("existing_runtime"),
        "existing_cli_command": selection.get("existing_cli_command"),
        "coverage": deepcopy(selection["coverage"]),
        "replay_visible": True,
        "universal_translation_reference": decision.get("universal_translation_reference"),
        "universal_translation_hash": decision.get("universal_translation_hash"),
        "canonical_semantic_artifact_reference": decision.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": decision.get("canonical_semantic_artifact_hash"),
        "ubtr_semantic_cognition_orchestration_reference": decision.get(
            "ubtr_semantic_cognition_orchestration_reference"
        ),
        "ubtr_semantic_cognition_decision": decision.get("ubtr_semantic_cognition_decision"),
        "ubtr_semantic_cognition_reasons": deepcopy(decision.get("ubtr_semantic_cognition_reasons", [])),
        "ubtr_ocs_cognition_request_hash": decision.get("ubtr_ocs_cognition_request_hash"),
        "ubtr_ocs_cognition_handoff_reference": decision.get("ubtr_ocs_cognition_handoff_reference"),
        "ubtr_ocs_cognition_handoff_status": decision.get("ubtr_ocs_cognition_handoff_status"),
        "ubtr_ocs_context_hash": decision.get("ubtr_ocs_context_hash"),
        "ubtr_ocs_cognition_hash": decision.get("ubtr_ocs_cognition_hash"),
        "ubtr_ocs_provider_necessity": deepcopy(decision.get("ubtr_ocs_provider_necessity")),
        "ubtr_cognition_result_integration_reference": decision.get(
            "ubtr_cognition_result_integration_reference"
        ),
        "ubtr_cognition_result_integration_status": decision.get("ubtr_cognition_result_integration_status"),
        "ubtr_cognition_integrated_semantic_artifact_hash": decision.get(
            "ubtr_cognition_integrated_semantic_artifact_hash"
        ),
        "semantic_routing_source": decision.get("semantic_routing_source"),
        "migration_batch_id": decision.get("migration_batch_id"),
        "previous_routing_source": decision.get("previous_routing_source"),
        "previous_compatibility_workflow_id": decision.get("previous_compatibility_workflow_id"),
        "previous_compatibility_routing_status": decision.get("previous_compatibility_routing_status"),
        "previous_compatibility_confidence": decision.get("previous_compatibility_confidence"),
        "previous_compatibility_matched_terms": deepcopy(
            decision.get("previous_compatibility_matched_terms", [])
        ),
        "previous_compatibility_interpretation": deepcopy(
            decision.get("previous_compatibility_interpretation")
        ),
        "semantic_parity_evidence": deepcopy(decision.get("semantic_parity_evidence")),
        "semantic_comparison_artifact": deepcopy(decision.get("semantic_comparison_artifact")),
        "semantic_comparison_hash": decision.get("semantic_comparison_hash"),
        "semantic_equivalence_result": decision.get("semantic_equivalence_result"),
        "semantic_comparison_parity_status": decision.get("semantic_comparison_parity_status"),
        "semantic_comparison_non_authoritative": decision.get("semantic_comparison_non_authoritative"),
        "new_csa_routing_source": decision.get("new_csa_routing_source"),
        "ocs_escalation_reason": decision.get("ocs_escalation_reason"),
        "ocs_escalation_confidence": decision.get("ocs_escalation_confidence"),
        "ocs_provider_selection": decision.get("ocs_provider_selection"),
        "proposal_only_classification": decision.get("proposal_only_classification") is True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_conversational_cli_routing_summary(capture: dict[str, Any]) -> str:
    selection = capture.get("workflow_selection_artifact") or {}
    coverage = selection.get("coverage", {})
    lines = [
        f"routing_status: {capture.get('routing_status')}",
        f"workflow_id: {capture.get('workflow_id')}",
        f"existing_runtime: {selection.get('existing_runtime')}",
        f"existing_cli_command: {selection.get('existing_cli_command')}",
        f"operator_summary: {selection.get('operator_summary')}",
        f"coverage: {coverage.get('conversationally_accessible_workflows')}/{coverage.get('registered_workflows')}",
        f"replay_reference: {capture.get('conversational_cli_routing_replay_reference')}",
        f"provider_invoked: {capture.get('provider_invoked')}",
        f"worker_invoked: {capture.get('worker_invoked')}",
        f"execution_requested: {capture.get('execution_requested')}",
        f"fail_closed: {capture.get('fail_closed')}",
        f"failure_reason: {capture.get('failure_reason') or ''}",
    ]
    return "\n".join(lines)


def workflow_registry() -> tuple[dict[str, Any], ...]:
    """Return the deterministic conversational workflow registry."""

    return (
        _workflow(CREATE_DOMAIN_TRADING, "aigol conversation", "conversation_native_development_intent_routing"),
        _workflow(CREATE_DOMAIN_MARKETING, "aigol conversation", "conversation_native_development_intent_routing"),
        _workflow(
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
            "aigol conversation",
            "unknown_domain_clarification_runtime",
            clarification=True,
        ),
        _workflow(
            DOMAIN_ADAPTATION_REFERENCE,
            "aigol domain-reference resolve",
            "semantic_similarity_domain_reference_runtime",
        ),
        _workflow(
            OPERATOR_DECISION_SUPPORT,
            "aigol decision-support recommend",
            "operator_decision_support_runtime",
        ),
        _workflow(SHOW_LATEST_REPLAY_CHAIN, "aigol show-latest-chain", "cli_chain_inspection_runtime"),
        _workflow(REVIEW_LATEST_AUDIT, "aigol conversational route", "capability_audit_artifact_review"),
        _workflow(IMPROVE_PROVIDER_LAYER, "aigol conversational route", "provider_layer_review_guidance"),
        _workflow(SHOW_STATUS, "aigol status", "status_summary"),
        _workflow(SHOW_DASHBOARD, "aigol dashboard", "session_dashboard_runtime"),
        _workflow(
            NATIVE_DEVELOPMENT_INTENT_ROUTING,
            "aigol conversation",
            "conversation_native_development_intent_routing",
        ),
        _workflow(
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
            "aigol conversation",
            "conversation_native_development_context_integration",
        ),
        _workflow(
            DOMAIN_LIFECYCLE_GOVERNANCE,
            "aigol conversation",
            "domain_lifecycle_governance_runtime",
        ),
        _workflow(
            CAPABILITY_LIFECYCLE_GOVERNANCE,
            "aigol conversation",
            "capability_lifecycle_governance_runtime",
        ),
        _workflow(PROPOSAL_RUNTIME, "aigol conversation", "proposal_runtime"),
        _workflow(
            IMPROVEMENT_PROPOSAL_RUNTIME,
            "aigol conversation",
            "improvement_proposal_runtime",
        ),
        _workflow(
            FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
            "aigol conversation",
            "first_real_implementation_generation_epoch_runtime",
        ),
        _workflow(
            IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
            "aigol conversation",
            "implementation_plan_to_execution_request_runtime",
        ),
        _workflow(
            AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
            "aigol conversation",
            "AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION_V1.md",
        ),
        _workflow(
            AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
            "aigol conversation",
            "AI_DECISION_VALIDATOR_CAPABILITY_MODEL_V1.md",
        ),
        _workflow(
            AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
            "aigol conversation",
            "AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE_V1.md",
        ),
        _workflow(OCS_LLM_COGNITION, "aigol conversation", "ocs_llm_cognition_end_to_end_runtime"),
        _workflow(
            BOUNDED_FILE_WRITE_WORKER_USER_SESSION,
            "aigol conversation",
            "file_write_worker_certified_path",
            clarification=True,
        ),
        _workflow(
            AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
            "aigol conversation",
            "domain_handoff_review_approval_binding_runtime",
        ),
        _workflow(
            DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
            "aigol conversation",
            "domain_approval_entry_to_execution_ready_authorization_bridge_runtime",
        ),
        _workflow(
            DOMAIN_EXECUTION_AUTHORIZATION,
            "aigol conversation",
            "execution_authorization_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_REQUEST,
            "aigol conversation",
            "worker_invocation_request_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_ASSIGNMENT,
            "aigol conversation",
            "worker_assignment_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_DISPATCH,
            "aigol conversation",
            "worker_dispatch_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_INVOCATION,
            "aigol conversation",
            "worker_invocation_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_EXECUTION,
            "aigol conversation",
            "execution_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_RESULT_CAPTURE,
            "aigol conversation",
            "worker_result_capture_runtime",
        ),
        _workflow(
            DOMAIN_WORKER_RESULT_VALIDATION,
            "aigol conversation",
            "worker_result_validation_runtime",
        ),
        _workflow(
            DOMAIN_POST_EXECUTION_REPLAY_REVIEW,
            "aigol conversation",
            "post_execution_replay_review_runtime",
        ),
        _workflow(
            DOMAIN_GOVERNED_TERMINATION,
            "aigol conversation",
            "governed_termination_runtime",
        ),
        _workflow(
            GOVERNANCE_ARTIFACT_CREATION,
            "aigol conversation",
            "governance_artifact_creation_runtime",
        ),
        _workflow(
            GOVERNED_REPOSITORY_MUTATION,
            "aigol conversation",
            "governed_repository_mutation_runtime",
        ),
        _workflow(
            GOVERNED_DEVELOPMENT_WORKFLOW,
            "aigol conversation",
            "governed_development_workflow_runtime",
        ),
        _workflow(
            HUMAN_INTENT_CLARIFICATION_INTAKE,
            "aigol conversation",
            "human_intent_clarification_intake_runtime",
            clarification=True,
        ),
        _workflow(
            PROVIDER_ONBOARDING_DOMAIN,
            "aigol conversation",
            "provider_onboarding_domain_certification_v1",
        ),
        _workflow(
            DEFAULT_PROVIDER_ASSISTED_CONVERSATION,
            "aigol conversation",
            "prompt_to_conversation_integration",
        ),
    )


def _classify_workflow(human_prompt: str) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized_with_punctuation = prompt.lower().strip()
    normalized = normalized_with_punctuation.rstrip(".?!")
    if "unrestricted" in normalized and "autonomous agent" in normalized:
        raise FailClosedRuntimeError("conversational CLI routing failed closed: no certified workflow mapping")
    if _is_domain_adaptation_reference_prompt(normalized):
        return _analysis(DOMAIN_ADAPTATION_REFERENCE, "HIGH", ["domain", "reference", "adaptation"])
    governed_termination_entry_intent = detect_domain_governed_termination_entry_intent(prompt)
    if governed_termination_entry_intent.get("governed_termination_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_GOVERNED_TERMINATION,
            "HIGH",
            ["governed-termination", str(governed_termination_entry_intent.get("domain_name") or "")],
        )
    replay_review_entry_intent = detect_domain_post_execution_replay_review_entry_intent(prompt)
    if replay_review_entry_intent.get("post_execution_replay_review_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_POST_EXECUTION_REPLAY_REVIEW,
            "HIGH",
            ["post-execution-replay-review", str(replay_review_entry_intent.get("domain_name") or "")],
        )
    worker_result_validation_entry_intent = detect_domain_worker_result_validation_entry_intent(prompt)
    if worker_result_validation_entry_intent.get("worker_result_validation_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_RESULT_VALIDATION,
            "HIGH",
            ["worker-result-validation", str(worker_result_validation_entry_intent.get("domain_name") or "")],
        )
    worker_execution_entry_intent = detect_domain_worker_execution_entry_intent(prompt)
    if worker_execution_entry_intent.get("worker_execution_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_EXECUTION,
            "HIGH",
            [
                "worker-execution",
                "worker-invocation",
                str(worker_execution_entry_intent.get("domain_name") or ""),
            ],
        )
    worker_result_capture_entry_intent = detect_domain_worker_result_capture_entry_intent(prompt)
    if worker_result_capture_entry_intent.get("worker_result_capture_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_RESULT_CAPTURE,
            "HIGH",
            [
                "worker-result-capture",
                "worker-execution",
                str(worker_result_capture_entry_intent.get("domain_name") or ""),
            ],
        )
    worker_invocation_entry_intent = detect_domain_worker_invocation_entry_intent(prompt)
    if worker_invocation_entry_intent.get("worker_invocation_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_INVOCATION,
            "HIGH",
            [
                "worker-invocation",
                "worker-dispatch",
                str(worker_invocation_entry_intent.get("domain_name") or ""),
            ],
        )
    worker_dispatch_entry_intent = detect_domain_worker_dispatch_entry_intent(prompt)
    if worker_dispatch_entry_intent.get("worker_dispatch_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_DISPATCH,
            "HIGH",
            [
                "worker-dispatch",
                "worker-assignment",
                str(worker_dispatch_entry_intent.get("domain_name") or ""),
            ],
        )
    worker_assignment_entry_intent = detect_domain_worker_assignment_entry_intent(prompt)
    if worker_assignment_entry_intent.get("worker_assignment_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_ASSIGNMENT,
            "HIGH",
            [
                "worker-assignment",
                "worker-request",
                str(worker_assignment_entry_intent.get("domain_name") or ""),
            ],
        )
    worker_request_entry_intent = detect_domain_worker_request_entry_intent(prompt)
    if worker_request_entry_intent.get("worker_request_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_WORKER_REQUEST,
            "HIGH",
            [
                "worker-request",
                "authorized",
                str(worker_request_entry_intent.get("domain_name") or ""),
            ],
        )
    execution_authorization_entry_intent = detect_domain_execution_authorization_entry_intent(prompt)
    if execution_authorization_entry_intent.get("execution_authorization_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_EXECUTION_AUTHORIZATION,
            "HIGH",
            [
                "execution",
                "authorization",
                "authorized",
                str(execution_authorization_entry_intent.get("domain_name") or ""),
            ],
        )
    execution_ready_entry_intent = detect_domain_execution_ready_entry_intent(prompt)
    if execution_ready_entry_intent.get("execution_ready_entry_intent_detected") is True:
        return _analysis(
            DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
            "HIGH",
            [
                "execution-ready",
                "authorization",
                "packet",
                str(execution_ready_entry_intent.get("domain_name") or ""),
            ],
        )
    approval_entry_intent = detect_domain_approval_entry_intent(prompt)
    if approval_entry_intent.get("approval_entry_intent_detected") is True:
        return _analysis(
            AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
            "HIGH",
            [
                "authorized",
                "domain",
                "artifact",
                "request",
                str(approval_entry_intent.get("domain_name") or ""),
            ],
        )
    if _is_provider_onboarding_domain_prompt(normalized):
        return _analysis(
            PROVIDER_ONBOARDING_DOMAIN,
            "HIGH",
            ["provider-onboarding", *_provider_onboarding_matched_terms(normalized)],
        )
    early_human_intent = classify_human_intent_for_clarification(prompt, include_unknown=False)
    if early_human_intent.get("intake_matched") is True:
        return _human_intent_analysis(early_human_intent)
    if _is_freeform_clarification_prompt(normalized):
        return _analysis(OCS_LLM_COGNITION, "HIGH", ["freeform", "clarification", "ocs"])
    if _is_freeform_ambiguous_prompt(normalized):
        return _analysis(OCS_LLM_COGNITION, "HIGH", ["freeform", "ambiguous", "ocs"])
    if "create" in normalized and "trading" in normalized and "domain" in normalized:
        return _analysis(CREATE_DOMAIN_TRADING, "HIGH", ["create", "trading", "domain"])
    if "create" in normalized and "marketing" in normalized and "domain" in normalized:
        return _analysis(CREATE_DOMAIN_MARKETING, "HIGH", ["create", "marketing", "domain"])
    proposal_only_ocs_escalation = _proposal_only_ocs_escalation(normalized)
    if proposal_only_ocs_escalation:
        return _analysis(
            OCS_LLM_COGNITION,
            proposal_only_ocs_escalation["confidence"],
            proposal_only_ocs_escalation["matched_terms"],
            ocs_escalation=proposal_only_ocs_escalation,
        )
    if _is_improvement_proposal_runtime_prompt(normalized):
        return _analysis(IMPROVEMENT_PROPOSAL_RUNTIME, "HIGH", ["improvement", "proposal", "governance"])
    if _is_proposal_runtime_prompt(normalized):
        return _analysis(PROPOSAL_RUNTIME, "HIGH", ["proposal", "artifact", "governance"])
    if _is_governance_artifact_creation_prompt(normalized):
        return _analysis(
            GOVERNED_DEVELOPMENT_WORKFLOW,
            "HIGH",
            ["create", "governance", "artifact", "governed-development"],
        )
    if _is_governed_repository_mutation_prompt(normalized):
        return _analysis(
            GOVERNED_REPOSITORY_MUTATION,
            "HIGH",
            ["governed", "repository", "mutation"],
        )
    if _is_governed_development_workflow_prompt(normalized):
        return _analysis(
            GOVERNED_DEVELOPMENT_WORKFLOW,
            "HIGH",
            ["governed", "development", "workflow"],
        )
    if _is_task_completion_native_development_prompt(normalized):
        return _analysis(
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
            "HIGH",
            ["task-completion", "native", "development"],
        )
    development_intent = classify_development_intent_for_governed_routing(prompt)
    if development_intent.get("intake_matched") is True:
        return _analysis(
            GOVERNED_DEVELOPMENT_WORKFLOW,
            str(development_intent.get("intent_confidence") or "HIGH"),
            list(development_intent.get("intent_signals") or ["development", "intent"]),
            human_intent_intake=development_intent,
        )
    if is_conversation_native_development_intent(prompt):
        return _analysis(
            NATIVE_DEVELOPMENT_INTENT_ROUTING,
            "HIGH",
            ["native", "development", "intent"],
        )
    if _is_product_1_domain_foundation_prompt(normalized):
        return _analysis(
            AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
            "HIGH",
            ["product-1", "ai-decision-validator", "domain-foundation"],
        )
    if _is_product_1_capability_lifecycle_prompt(normalized):
        return _analysis(
            AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
            "HIGH",
            ["product-1", "ai-decision-validator", "capability-lifecycle"],
        )
    if _is_product_1_capability_model_prompt(normalized):
        return _analysis(
            AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
            "HIGH",
            ["product-1", "ai-decision-validator", "capability-model"],
        )
    if _is_domain_lifecycle_governance_prompt(normalized):
        return _analysis(DOMAIN_LIFECYCLE_GOVERNANCE, "HIGH", ["domain", "lifecycle", "governance"])
    if _is_capability_lifecycle_governance_prompt(normalized):
        return _analysis(CAPABILITY_LIFECYCLE_GOVERNANCE, "HIGH", ["capability", "lifecycle", "governance"])
    if _is_improvement_proposal_runtime_prompt(normalized):
        return _analysis(IMPROVEMENT_PROPOSAL_RUNTIME, "HIGH", ["improvement", "proposal", "governance"])
    if _is_proposal_runtime_prompt(normalized):
        return _analysis(PROPOSAL_RUNTIME, "HIGH", ["proposal", "artifact", "governance"])
    if _is_first_real_implementation_generation_prompt(normalized):
        return _analysis(
            FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
            "HIGH",
            ["first-real", "implementation", "generation"],
        )
    if _is_implementation_plan_to_execution_request_prompt(normalized):
        return _analysis(
            IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
            "HIGH",
            ["implementation-plan", "execution-request"],
        )
    if _is_task_completion_domain_prompt(normalized):
        return _analysis(CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, "HIGH", ["domain", "proposal", "product"])
    if _is_task_completion_provider_prompt(normalized):
        return _analysis(IMPROVE_PROVIDER_LAYER, "HIGH", ["provider", "boundary", "improvement"])
    if _is_task_completion_product_foundation_prompt(normalized):
        return _analysis(OPERATOR_DECISION_SUPPORT, "HIGH", ["product", "evidence", "decision-support"])
    if _is_task_completion_domain_continuation_prompt(normalized):
        return _analysis(
            AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
            "HIGH",
            ["approved", "domain", "proposal", "continuation"],
        )
    if _is_task_completion_native_development_prompt(normalized):
        return _analysis(
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
            "HIGH",
            ["task-completion", "native", "development"],
        )
    early_human_intent = classify_human_intent_for_clarification(prompt, include_unknown=False)
    if early_human_intent.get("intake_matched") is True:
        return _human_intent_analysis(early_human_intent)
    if _is_ocs_llm_cognition_prompt(
        normalized,
        ends_with_question=normalized_with_punctuation.endswith("?"),
    ):
        return _analysis(OCS_LLM_COGNITION, "MEDIUM", ["ocs", "llm", "cognition"])
    if _is_plain_domain_proposal_prompt(normalized):
        return _analysis(CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, "HIGH", ["create", "new", "domain"])
    if _is_plain_ocs_intake_prompt(normalized):
        return _analysis(OCS_LLM_COGNITION, "HIGH", ["plain", "ocs", "cognition"])
    if is_plain_native_development_prompt(prompt):
        return _analysis(NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION, "HIGH", ["plain", "native", "development"])
    if _is_operator_decision_support_prompt(normalized):
        return _analysis(OPERATOR_DECISION_SUPPORT, "HIGH", ["operator", "decision", "support"])
    if "create" in normalized and "domain" in normalized and (
        "compliance" in normalized or "regulatory" in normalized
    ):
        return _analysis(CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, "HIGH", ["create", "compliance", "domain"])
    execution_intent = detect_human_execution_intent(prompt)
    if execution_intent["intent_class"] == GENERIC_GOVERNED_DOMAIN_CREATION:
        return _analysis(
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
            execution_intent["confidence"],
            execution_intent["matched_terms"] or ["create", "governed", "domain"],
        )
    if execution_intent["intent_class"] == GENERIC_GOVERNED_ARTIFACT_CREATION:
        return _analysis(
            GOVERNANCE_ARTIFACT_CREATION,
            execution_intent["confidence"],
            execution_intent["matched_terms"] or ["create", "governed", "artifact"],
        )
    if execution_intent["intent_class"] == GENERIC_GOVERNED_EXECUTION_REQUEST:
        raise FailClosedRuntimeError(
            "conversational CLI routing failed closed: generic governed execution intent requires a certified workflow mapping"
        )
    if "latest" in normalized and ("replay chain" in normalized or "chain" in normalized):
        return _analysis(SHOW_LATEST_REPLAY_CHAIN, "HIGH", ["latest", "replay", "chain"])
    if "review" in normalized and "audit" in normalized:
        return _analysis(REVIEW_LATEST_AUDIT, "HIGH", ["review", "audit"])
    if "improve" in normalized and "provider" in normalized and "layer" in normalized:
        return _analysis(IMPROVE_PROVIDER_LAYER, "MEDIUM", ["improve", "provider", "layer"])
    if normalized in {"status", "show status", "what is status"}:
        return _analysis(SHOW_STATUS, "HIGH", ["status"])
    if "dashboard" in normalized:
        return _analysis(SHOW_DASHBOARD, "HIGH", ["dashboard"])
    if _is_native_development_context_prompt(prompt):
        return _analysis(NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION, "HIGH", ["native", "development", "context"])
    human_intent = classify_human_intent_for_clarification(prompt, include_unknown=True)
    if human_intent.get("intake_matched") is True:
        return _human_intent_analysis(human_intent)
    return _analysis(DEFAULT_PROVIDER_ASSISTED_CONVERSATION, "LOW", ["provider", "conversation", "fallback"])


def _classify_workflow_from_canonical_semantic_artifact(
    canonical_semantic_capture: dict[str, Any] | None,
    *,
    compatibility_route_evidence: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Use UBTR semantic artifact as first-class routing input when decisive."""

    if not isinstance(canonical_semantic_capture, dict):
        return None
    if not _compatibility_route_supports_csa_migration(compatibility_route_evidence):
        return None
    artifact = canonical_semantic_capture.get("semantic_artifact")
    if not isinstance(artifact, dict):
        return None
    workflow_identity = artifact.get("workflow_identity")
    semantic_identity = artifact.get("semantic_identity")
    ambiguity = artifact.get("ambiguity")
    if not isinstance(workflow_identity, dict) or not isinstance(semantic_identity, dict):
        return None
    if isinstance(ambiguity, dict) and ambiguity.get("clarification_required") is True:
        return None
    workflow_id = workflow_identity.get("workflow_id")
    if workflow_id != GOVERNED_DEVELOPMENT_WORKFLOW:
        return None
    domain = semantic_identity.get("domain")
    actions = semantic_identity.get("requested_actions")
    action_set = {action for action in actions if isinstance(action, str)} if isinstance(actions, list) else set()
    if not action_set.intersection({"CREATE", "UPDATE", "IMPLEMENT"}):
        return None
    confidence = str(artifact.get("confidence", {}).get("semantic_confidence") or "LOW")
    if domain == "DEVELOPMENT":
        if confidence != "HIGH":
            return None
        matched_terms = ["ubtr", "canonical-semantic-artifact", "governed-development", "development"]
        matched_terms.extend(sorted(action.lower() for action in action_set))
        return _analysis(
            GOVERNED_DEVELOPMENT_WORKFLOW,
            confidence,
            matched_terms,
            human_intent_intake=_csa_development_intent_intake(
                artifact=artifact,
                confidence=confidence,
                matched_terms=matched_terms,
            ),
        )
    if domain != "GOVERNANCE":
        return None
    technical_projection = artifact.get("technical_projection")
    normalized_intent = (
        technical_projection.get("normalized_intent")
        if isinstance(technical_projection, dict)
        else {}
    )
    normalized_text = (
        normalized_intent.get("normalized_text")
        if isinstance(normalized_intent, dict)
        else None
    )
    if not isinstance(normalized_text, str) or not _is_governance_artifact_creation_prompt(normalized_text):
        return None
    matched_terms = ["ubtr", "canonical-semantic-artifact", "governed-development"]
    matched_terms.append(str(domain).lower())
    matched_terms.extend(sorted(action.lower() for action in action_set))
    return _analysis(
        GOVERNED_DEVELOPMENT_WORKFLOW,
        confidence,
        matched_terms,
    )


def _classify_hirr_from_canonical_semantic_artifact(
    canonical_semantic_capture: dict[str, Any] | None,
    *,
    compatibility_route_evidence: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(canonical_semantic_capture, dict) or not isinstance(compatibility_route_evidence, dict):
        return None
    semantic_artifact = canonical_semantic_capture.get("semantic_artifact")
    compatibility_intake = compatibility_route_evidence.get("compatibility_human_intent_intake")
    if not isinstance(semantic_artifact, dict) or not isinstance(compatibility_intake, dict):
        return None
    intake = classify_human_intent_for_clarification_from_canonical_semantic_artifact(
        canonical_semantic_artifact=semantic_artifact,
        previous_compatibility_intake=compatibility_intake,
    )
    if intake.get("intake_matched") is not True:
        return None
    return _human_intent_analysis(intake)


def _classify_proposal_only_ocs_from_canonical_semantic_artifact(
    canonical_semantic_capture: dict[str, Any] | None,
    *,
    compatibility_route_evidence: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(canonical_semantic_capture, dict) or not isinstance(compatibility_route_evidence, dict):
        return None
    semantic_artifact = canonical_semantic_capture.get("semantic_artifact")
    if not isinstance(semantic_artifact, dict):
        return None
    compatibility_ocs = compatibility_route_evidence.get("compatibility_ocs_escalation")
    if not _compatibility_supports_proposal_only_ocs(compatibility_route_evidence, compatibility_ocs):
        return None
    if not _csa_supports_proposal_only_ocs(semantic_artifact, compatibility_ocs):
        return None
    matched_terms = ["ubtr", "canonical-semantic-artifact", "proposal-only", "ocs-cognition"]
    escalation = {
        "escalation_reason": compatibility_ocs["escalation_reason"],
        "confidence": compatibility_ocs["confidence"],
        "matched_terms": matched_terms,
        "proposal_only_classification": True,
        "provider_selection": compatibility_ocs["provider_selection"],
    }
    analysis = _analysis(
        OCS_LLM_COGNITION,
        compatibility_ocs["confidence"],
        matched_terms,
        ocs_escalation=escalation,
    )
    analysis.update(
        {
            "semantic_routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
            "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_PROPOSAL_ONLY_OCS_ROUTING_V1,
            "previous_compatibility_interpretation": _compatibility_proposal_only_ocs_interpretation(
                compatibility_route_evidence,
                compatibility_ocs,
            ),
            "semantic_parity_evidence": _proposal_only_ocs_parity_evidence(
                artifact=semantic_artifact,
                compatibility_route_evidence=compatibility_route_evidence,
                compatibility_ocs=compatibility_ocs,
            ),
        }
    )
    return analysis


def _compatibility_supports_proposal_only_ocs(
    route_evidence: dict[str, Any],
    compatibility_ocs: Any,
) -> bool:
    return (
        route_evidence.get("compatibility_source") == "LOCAL_COMPATIBILITY_MARKERS"
        and route_evidence.get("compatibility_workflow_id") == OCS_LLM_COGNITION
        and route_evidence.get("compatibility_routing_status") == WORKFLOW_SELECTED
        and isinstance(compatibility_ocs, dict)
        and compatibility_ocs.get("proposal_only_classification") is True
        and compatibility_ocs.get("provider_selection") == "OCS_PROVIDER_REGISTRY_DETERMINISTIC_ORDER"
        and compatibility_ocs.get("escalation_reason")
        in {
            "PROPOSAL_ONLY_GOVERNANCE_DOCUMENT_COGNITION",
            "PROPOSAL_ONLY_IMPLEMENTATION_PROPOSAL_COGNITION",
            "PROPOSAL_ONLY_EXPLANATION_OR_ANALYSIS_COGNITION",
        }
    )


def _csa_supports_proposal_only_ocs(artifact: dict[str, Any], compatibility_ocs: dict[str, Any]) -> bool:
    workflow_identity = artifact.get("workflow_identity") or {}
    semantic_identity = artifact.get("semantic_identity") or {}
    confidence = artifact.get("confidence") or {}
    ambiguity = artifact.get("ambiguity") or {}
    approval_state = artifact.get("approval_state") or {}
    execution_intent = artifact.get("execution_intent") or {}
    provider_projection = artifact.get("provider_projection") or {}
    worker_projection = artifact.get("worker_projection") or {}
    technical_projection = artifact.get("technical_projection") or {}
    payload = technical_projection.get("translated_governance_payload") if isinstance(technical_projection, dict) else {}
    return (
        workflow_identity.get("workflow_id") == OCS_LLM_COGNITION
        and semantic_identity.get("intent_family") == "OCS_PROPOSAL_ONLY_INTENT"
        and semantic_identity.get("domain") == "GOVERNANCE"
        and semantic_identity.get("requested_actions") == ["REVIEW"]
        and confidence.get("semantic_confidence") == compatibility_ocs.get("confidence")
        and ambiguity.get("clarification_required") is False
        and approval_state.get("approval_required") is False
        and execution_intent.get("execution_requested") is False
        and provider_projection.get("provider_relevance") == "PROVIDER_REQUIRED"
        and provider_projection.get("provider_invoked") is False
        and worker_projection.get("worker_relevance") == "NONE"
        and worker_projection.get("worker_invoked") is False
        and isinstance(payload, dict)
        and payload.get("proposal_only") is True
        and payload.get("proposal_only_reason") == compatibility_ocs.get("escalation_reason")
    )


def _compatibility_proposal_only_ocs_interpretation(
    route_evidence: dict[str, Any],
    compatibility_ocs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source": "LOCAL_PROPOSAL_ONLY_OCS_COMPATIBILITY_MARKERS",
        "workflow_id": route_evidence.get("compatibility_workflow_id"),
        "routing_status": route_evidence.get("compatibility_routing_status"),
        "confidence": route_evidence.get("compatibility_confidence"),
        "matched_terms": deepcopy(route_evidence.get("compatibility_matched_terms", [])),
        "escalation_reason": compatibility_ocs.get("escalation_reason"),
        "proposal_only_classification": compatibility_ocs.get("proposal_only_classification") is True,
        "provider_selection": compatibility_ocs.get("provider_selection"),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_bypassed": False,
    }


def _proposal_only_ocs_parity_evidence(
    *,
    artifact: dict[str, Any],
    compatibility_route_evidence: dict[str, Any],
    compatibility_ocs: dict[str, Any],
) -> dict[str, Any]:
    evidence = {
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_PROPOSAL_ONLY_OCS_ROUTING_V1,
        "parity_status": "CSA_COMPATIBILITY_PARITY_PROVEN",
        "parity_scope": "PROPOSAL_ONLY_OCS_ROUTING",
        "csa_workflow_id": artifact["workflow_identity"]["workflow_id"],
        "csa_intent_family": artifact["semantic_identity"]["intent_family"],
        "csa_requested_actions": list(artifact["semantic_identity"]["requested_actions"]),
        "csa_semantic_confidence": artifact["confidence"]["semantic_confidence"],
        "csa_execution_requested": artifact["execution_intent"]["execution_requested"] is True,
        "csa_provider_relevance": artifact["provider_projection"]["provider_relevance"],
        "csa_worker_relevance": artifact["worker_projection"]["worker_relevance"],
        "compatibility_workflow_id": compatibility_route_evidence.get("compatibility_workflow_id"),
        "compatibility_confidence": compatibility_route_evidence.get("compatibility_confidence"),
        "compatibility_escalation_reason": compatibility_ocs.get("escalation_reason"),
        "compatibility_provider_selection": compatibility_ocs.get("provider_selection"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
    }
    evidence["parity_hash"] = replay_hash(evidence)
    return evidence


def _human_intent_analysis(intake: dict[str, Any]) -> dict[str, Any]:
    return _analysis(
        HUMAN_INTENT_CLARIFICATION_INTAKE,
        str(intake.get("intent_confidence") or "LOW"),
        list(intake.get("intent_signals") or []),
        human_intent_intake=intake,
    )


def _csa_development_intent_intake(
    *,
    artifact: dict[str, Any],
    confidence: str,
    matched_terms: list[str],
) -> dict[str, Any]:
    return {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1",
        "intake_matched": True,
        "workflow_id": GOVERNED_DEVELOPMENT_WORKFLOW,
        "intent_family": "DEVELOPMENT_INTENT",
        "intent_confidence": confidence,
        "intent_signals": list(matched_terms),
        "clarification_required": False,
        "clarification_questions": [],
        "expected_workflow_targets": [GOVERNED_DEVELOPMENT_WORKFLOW],
        "routing_decision": "DEVELOPMENT_INTENT_RESOLVED_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
        "routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
        "canonical_semantic_artifact_hash": artifact.get("artifact_hash"),
        "semantic_authority": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }


def _compatibility_route_evidence(prompt: str) -> dict[str, Any]:
    try:
        analysis = _classify_workflow(prompt)
        return {
            "compatibility_source": "LOCAL_COMPATIBILITY_MARKERS",
            "compatibility_workflow_id": analysis["workflow_id"],
            "compatibility_routing_status": analysis["routing_status"],
            "compatibility_confidence": analysis["confidence"],
            "compatibility_matched_terms": deepcopy(analysis["matched_terms"]),
            "compatibility_human_intent_intake": deepcopy(analysis.get("human_intent_intake")),
            "compatibility_intent_family": analysis.get("intent_family"),
            "compatibility_clarification_questions": deepcopy(analysis.get("clarification_questions", [])),
            "compatibility_expected_workflow_targets": deepcopy(
                analysis.get("expected_workflow_targets", [])
            ),
            "compatibility_ocs_escalation": deepcopy(analysis.get("ocs_escalation")),
            "compatibility_failure_reason": None,
        }
    except Exception as exc:
        return {
            "compatibility_source": "LOCAL_COMPATIBILITY_MARKERS",
            "compatibility_workflow_id": None,
            "compatibility_routing_status": FAILED_CLOSED,
            "compatibility_confidence": "NONE",
            "compatibility_matched_terms": [],
            "compatibility_human_intent_intake": None,
            "compatibility_intent_family": None,
            "compatibility_clarification_questions": [],
            "compatibility_expected_workflow_targets": [],
            "compatibility_ocs_escalation": None,
            "compatibility_failure_reason": str(exc)
            if isinstance(exc, FailClosedRuntimeError)
            else "compatibility routing evidence failed closed",
        }


def _compatibility_route_supports_csa_migration(route_evidence: dict[str, Any] | None) -> bool:
    if not isinstance(route_evidence, dict):
        return False
    return (
        route_evidence.get("compatibility_source") == "LOCAL_COMPATIBILITY_MARKERS"
        and route_evidence.get("compatibility_workflow_id") == GOVERNED_DEVELOPMENT_WORKFLOW
        and route_evidence.get("compatibility_routing_status") == WORKFLOW_SELECTED
    )


def _semantic_replay_comparison_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    canonical_semantic_capture: dict[str, Any] | None,
    compatibility_route_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    csa_interpretation = _csa_semantic_interpretation(canonical_semantic_capture)
    compatibility_interpretation = _compatibility_semantic_interpretation(compatibility_route_evidence)
    differences = _semantic_interpretation_differences(
        csa_interpretation=csa_interpretation,
        compatibility_interpretation=compatibility_interpretation,
    )
    if csa_interpretation["available"] is not True:
        parity_status = "CSA_UNAVAILABLE"
        equivalence_result = "NOT_EVALUATED"
    elif compatibility_interpretation["available"] is not True:
        parity_status = "COMPATIBILITY_UNAVAILABLE"
        equivalence_result = "NOT_EQUIVALENT"
    elif differences:
        parity_status = "CSA_COMPATIBILITY_DIVERGENT"
        equivalence_result = "NOT_EQUIVALENT"
    else:
        parity_status = "CSA_COMPATIBILITY_EQUIVALENT"
        equivalence_result = "EQUIVALENT"
    confidence_comparison = {
        "csa_confidence": csa_interpretation.get("semantic_confidence"),
        "compatibility_confidence": compatibility_interpretation.get("confidence"),
        "confidence_equivalent": csa_interpretation.get("semantic_confidence")
        == compatibility_interpretation.get("confidence"),
    }
    artifact = {
        "artifact_type": SEMANTIC_REPLAY_COMPARISON_ARTIFACT_V1,
        "comparison_id": f"{_require_string(routing_id, 'routing_id')}:SEMANTIC-COMPARISON",
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_01_REPLAY_COMPARISON_SUBSTRATE_V1,
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "comparison_mode": "OBSERVATIONAL_ONLY",
        "authoritative_source": "COMPATIBILITY_ROUTING_UNLESS_CERTIFIED_MIGRATION_ALREADY_SELECTED",
        "canonical_semantic_artifact_reference": csa_interpretation.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": csa_interpretation.get("canonical_semantic_artifact_hash"),
        "compatibility_source": compatibility_interpretation.get("source"),
        "compatibility_interpretation_hash": replay_hash(compatibility_interpretation),
        "csa_interpretation_hash": replay_hash(csa_interpretation),
        "compatibility_semantic_interpretation": compatibility_interpretation,
        "csa_semantic_interpretation": csa_interpretation,
        "semantic_equivalence_result": equivalence_result,
        "semantic_differences": differences,
        "confidence_comparison": confidence_comparison,
        "parity_status": parity_status,
        "replay_lineage": {
            "routing_replay_reference": _require_string(replay_reference, "replay_reference"),
            "canonical_chain_id": canonical_chain_id,
            "prompt_id": prompt_id,
            "comparison_source": "CSA_VS_LOCAL_COMPATIBILITY_MARKERS",
        },
        "non_authoritative": True,
        "routing_influence": False,
        "governance_influence": False,
        "approval_influence": False,
        "provider_selection_influence": False,
        "execution_influence": False,
        "worker_influence": False,
        "lifecycle_influence": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _csa_semantic_interpretation(canonical_semantic_capture: dict[str, Any] | None) -> dict[str, Any]:
    semantic_artifact = (
        canonical_semantic_capture.get("semantic_artifact")
        if isinstance(canonical_semantic_capture, dict)
        else None
    )
    if not isinstance(semantic_artifact, dict):
        return {
            "source": "CANONICAL_SEMANTIC_ARTIFACT",
            "available": False,
            "canonical_semantic_artifact_reference": None,
            "canonical_semantic_artifact_hash": None,
            "workflow_id": None,
            "intent_family": None,
            "domain": None,
            "requested_actions": [],
            "semantic_confidence": None,
            "ambiguity_status": None,
            "clarification_required": None,
            "approval_required": None,
            "execution_requested": None,
            "provider_invoked": None,
            "worker_invoked": None,
        }
    semantic_identity = semantic_artifact.get("semantic_identity") or {}
    workflow_identity = semantic_artifact.get("workflow_identity") or {}
    confidence = semantic_artifact.get("confidence") or {}
    ambiguity = semantic_artifact.get("ambiguity") or {}
    clarification_state = semantic_artifact.get("clarification_state") or {}
    approval_state = semantic_artifact.get("approval_state") or {}
    execution_intent = semantic_artifact.get("execution_intent") or {}
    provider_projection = semantic_artifact.get("provider_projection") or {}
    worker_projection = semantic_artifact.get("worker_projection") or {}
    return {
        "source": "CANONICAL_SEMANTIC_ARTIFACT",
        "available": True,
        "canonical_semantic_artifact_reference": (
            canonical_semantic_capture.get("semantic_replay_reference")
            if isinstance(canonical_semantic_capture, dict)
            else None
        ),
        "canonical_semantic_artifact_hash": semantic_artifact.get("artifact_hash"),
        "workflow_id": workflow_identity.get("workflow_id"),
        "intent_family": semantic_identity.get("intent_family"),
        "domain": semantic_identity.get("domain"),
        "requested_actions": list(semantic_identity.get("requested_actions") or []),
        "semantic_confidence": confidence.get("semantic_confidence"),
        "ambiguity_status": ambiguity.get("ambiguity_status"),
        "clarification_required": clarification_state.get("clarification_required"),
        "approval_required": approval_state.get("approval_required"),
        "execution_requested": execution_intent.get("execution_requested"),
        "provider_invoked": provider_projection.get("provider_invoked"),
        "worker_invoked": worker_projection.get("worker_invoked"),
    }


def _compatibility_semantic_interpretation(route_evidence: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(route_evidence, dict):
        return {
            "source": "LOCAL_COMPATIBILITY_MARKERS",
            "available": False,
            "workflow_id": None,
            "routing_status": None,
            "confidence": None,
            "matched_terms": [],
            "intent_family": None,
            "clarification_required": None,
            "expected_workflow_targets": [],
            "ocs_escalation": None,
            "proposal_only_classification": False,
            "failure_reason": None,
        }
    compatibility_intake = route_evidence.get("compatibility_human_intent_intake")
    compatibility_ocs = route_evidence.get("compatibility_ocs_escalation")
    return {
        "source": route_evidence.get("compatibility_source"),
        "available": route_evidence.get("compatibility_failure_reason") is None,
        "workflow_id": route_evidence.get("compatibility_workflow_id"),
        "routing_status": route_evidence.get("compatibility_routing_status"),
        "confidence": route_evidence.get("compatibility_confidence"),
        "matched_terms": deepcopy(route_evidence.get("compatibility_matched_terms", [])),
        "intent_family": route_evidence.get("compatibility_intent_family"),
        "clarification_required": (
            compatibility_intake.get("clarification_required")
            if isinstance(compatibility_intake, dict)
            else route_evidence.get("compatibility_routing_status") == CLARIFICATION_REQUIRED
        ),
        "expected_workflow_targets": deepcopy(route_evidence.get("compatibility_expected_workflow_targets", [])),
        "ocs_escalation": deepcopy(compatibility_ocs) if isinstance(compatibility_ocs, dict) else None,
        "proposal_only_classification": (
            compatibility_ocs.get("proposal_only_classification") is True
            if isinstance(compatibility_ocs, dict)
            else False
        ),
        "failure_reason": route_evidence.get("compatibility_failure_reason"),
    }


def _semantic_interpretation_differences(
    *,
    csa_interpretation: dict[str, Any],
    compatibility_interpretation: dict[str, Any],
) -> list[dict[str, Any]]:
    if csa_interpretation.get("available") is not True or compatibility_interpretation.get("available") is not True:
        return []
    comparisons = (
        ("workflow_id", "workflow_id"),
        ("semantic_confidence", "confidence"),
        ("clarification_required", "clarification_required"),
    )
    differences: list[dict[str, Any]] = []
    for csa_field, compatibility_field in comparisons:
        csa_value = csa_interpretation.get(csa_field)
        compatibility_value = compatibility_interpretation.get(compatibility_field)
        if csa_value != compatibility_value:
            differences.append(
                {
                    "field": csa_field,
                    "csa_value": csa_value,
                    "compatibility_field": compatibility_field,
                    "compatibility_value": compatibility_value,
                }
            )
    return differences


def _analysis(
    workflow_id: str,
    confidence: str,
    matched_terms: list[str],
    *,
    human_intent_intake: dict[str, Any] | None = None,
    ocs_escalation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = _workflow_by_id(workflow_id)
    return {
        "workflow_id": workflow_id,
        "routing_status": CLARIFICATION_REQUIRED if entry.get("clarification_required") else WORKFLOW_SELECTED,
        "confidence": confidence,
        "matched_terms": list(matched_terms),
        "existing_runtime": entry["existing_runtime"],
        "existing_cli_command": entry["existing_cli_command"],
        "operator_summary": _operator_summary(workflow_id),
        "human_intent_intake": deepcopy(human_intent_intake) if human_intent_intake else None,
        "intent_family": human_intent_intake.get("intent_family") if human_intent_intake else None,
        "clarification_questions": deepcopy(human_intent_intake.get("clarification_questions", []))
        if human_intent_intake
        else [],
        "expected_workflow_targets": deepcopy(human_intent_intake.get("expected_workflow_targets", []))
        if human_intent_intake
        else [],
        "semantic_routing_source": human_intent_intake.get("semantic_routing_source") if human_intent_intake else None,
        "migration_batch_id": human_intent_intake.get("migration_batch_id") if human_intent_intake else None,
        "previous_compatibility_interpretation": deepcopy(
            human_intent_intake.get("previous_compatibility_interpretation")
        )
        if human_intent_intake
        else None,
        "semantic_parity_evidence": deepcopy(human_intent_intake.get("semantic_parity_evidence"))
        if human_intent_intake
        else None,
        "ocs_escalation": deepcopy(ocs_escalation) if ocs_escalation else None,
    }


def _is_domain_adaptation_reference_prompt(normalized: str) -> bool:
    markers = (
        "similar to",
        "based on",
        "derived from",
        "version of",
        "adaptation of",
        "same as but",
        "as a basis",
    )
    domains = ("trading", "marketing", "compliance", "healthcare", "public services", "server management")
    return any(marker in normalized for marker in markers) and any(domain in normalized for domain in domains)


def _is_operator_decision_support_prompt(normalized: str) -> bool:
    return (
        ("first real" in normalized and ("product domain" in normalized or "aigol product domain" in normalized))
        or "which capability" in normalized
        or ("capability" in normalized and "next" in normalized)
        or "which provider" in normalized
        or ("provider" in normalized and "first" in normalized)
        or "which worker" in normalized
        or ("worker" in normalized and "compare" in normalized)
        or "roadmap" in normalized
        or "prioritize" in normalized
        or "priority" in normalized
        or "sequencing" in normalized
    )


def _is_provider_onboarding_domain_prompt(normalized: str) -> bool:
    return bool(_provider_onboarding_matched_terms(normalized))


def _provider_onboarding_matched_terms(normalized: str) -> list[str]:
    normalized_ascii = _normalize_slovenian(normalized)
    tokens = set(_tokenize_provider_onboarding_prompt(normalized_ascii))
    provider_terms = {"claude", "anthropic", "gemini", "mistral"}
    onboarding_terms = {"dodaj", "add", "uporabljati", "use"}
    management_terms = {"onemogoci", "disable", "izklopi"}
    if not provider_terms.intersection(tokens):
        return []
    if onboarding_terms.intersection(tokens):
        return ["provider", "onboarding"]
    if management_terms.intersection(tokens):
        return ["provider", "management"]
    return []


def _normalize_slovenian(value: str) -> str:
    return value.translate(str.maketrans({"č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "d"}))


def _proposal_only_ocs_escalation(normalized: str) -> dict[str, Any] | None:
    normalized_ascii = _normalize_slovenian(normalized)
    no_execution_markers = (
        "proposal-only",
        "proposal only",
        "advisory only",
        "conversation only",
        "discussion only",
        "no execution",
        "do not execute",
        "do not invoke workers",
        "no workers",
        "without workers",
        "without worker",
        "without writing files",
        "do not write files",
        "no file writes",
        "no repository mutation",
        "no mutation",
        "samo pogovor",
        "samo pri pogovoru",
        "samo pripraviti",
        "brez izvajanja",
        "brez izvajanja workerjev",
        "ne zelim izvajanja workerjev",
        "brez zapisovanja datotek",
        "ne zelim zapisovanja datotek",
    )
    has_no_execution_marker = any(marker in normalized_ascii for marker in no_execution_markers)
    execution_markers = (
        "enter governed execution",
        "continue to ppp",
        "continue into ppp",
        "execution required",
        "requires execution",
        "run worker",
        "invoke worker",
        "write file",
        "write files",
        "modify repository",
        "mutate repository",
        "commit ",
    )
    if any(marker in normalized_ascii for marker in execution_markers) and not has_no_execution_marker:
        return None

    governance_document_markers = (
        "create governance document",
        "create a governance document",
        "draft governance document",
        "draft a governance document",
        "prepare governance document",
        "prepare a governance document",
        "generate governance document",
        "generate a governance document",
        "pripraviti governance dokument",
        "pripravi governance dokument",
    )
    explicit_governance_artifact_with_no_execution = (
        has_no_execution_marker
        and any(term in normalized_ascii for term in ("governance artifact", "governance artefakt"))
    )
    if any(marker in normalized_ascii for marker in governance_document_markers) or explicit_governance_artifact_with_no_execution:
        return {
            "escalation_reason": "PROPOSAL_ONLY_GOVERNANCE_DOCUMENT_COGNITION",
            "confidence": "HIGH",
            "matched_terms": ["proposal-only", "governance", "document", "ocs-cognition"],
            "proposal_only_classification": True,
            "provider_selection": "OCS_PROVIDER_REGISTRY_DETERMINISTIC_ORDER",
        }

    implementation_proposal_markers = (
        "generate implementation proposal",
        "create implementation proposal",
        "draft implementation proposal",
        "prepare implementation proposal",
        "implementation proposal",
    )
    if any(marker in normalized_ascii for marker in implementation_proposal_markers):
        return {
            "escalation_reason": "PROPOSAL_ONLY_IMPLEMENTATION_PROPOSAL_COGNITION",
            "confidence": "HIGH",
            "matched_terms": ["proposal-only", "implementation-proposal", "ocs-cognition"],
            "proposal_only_classification": True,
            "provider_selection": "OCS_PROVIDER_REGISTRY_DETERMINISTIC_ORDER",
        }

    proposal_actions = (
        "summarize",
        "explain",
        "compare",
        "brainstorm",
        "povzemi",
        "razlozi",
        "primerjaj",
    )
    governed_subjects = (
        "governance",
        "approval",
        "replay",
        "validation",
        "execution",
        "acli",
        "ocs",
        "ppp",
        "sapianta",
        "aigol",
        "provider",
        "workflow",
        "worker",
    )
    if any(action in normalized_ascii for action in proposal_actions) and any(
        subject in normalized_ascii for subject in governed_subjects
    ):
        return {
            "escalation_reason": "PROPOSAL_ONLY_EXPLANATION_OR_ANALYSIS_COGNITION",
            "confidence": "MEDIUM",
            "matched_terms": ["proposal-only", "analysis", "ocs-cognition"],
            "proposal_only_classification": True,
            "provider_selection": "OCS_PROVIDER_REGISTRY_DETERMINISTIC_ORDER",
        }
    return None


def _tokenize_provider_onboarding_prompt(value: str) -> list[str]:
    separators = ",.;:!?()[]{}\"'"
    normalized = value
    for separator in separators:
        normalized = normalized.replace(separator, " ")
    return [token for token in normalized.split() if token]


def is_ocs_llm_cognition_prompt(human_prompt: str) -> bool:
    """Return whether a prompt should enter broad OCS LLM cognition."""

    try:
        normalized_with_punctuation = _require_string(human_prompt, "human_prompt").lower().strip()
    except FailClosedRuntimeError:
        return False
    normalized = normalized_with_punctuation.rstrip(".?!")
    return _is_ocs_llm_cognition_prompt(
        normalized,
        ends_with_question=normalized_with_punctuation.endswith("?"),
    )


def _is_ocs_llm_cognition_prompt(normalized: str, *, ends_with_question: bool = False) -> bool:
    if "unrestricted" in normalized and "autonomous agent" in normalized:
        return False
    if "product domain" in normalized and "product domains" not in normalized:
        return False
    cognition_markers = (
        "first real aigol product",
        "commercialization",
        "managed services",
        "license the platform",
        "sell domains",
        "first real commercial sapianta product",
        "first real sapianta product",
        "commercial sapianta product",
        "sapianta product opportunity",
        "cognition output only",
        "should sapianta",
        "continue the aigol",
        "continue ",
        "help me decide",
        "what should",
    )
    has_cognition_marker = any(marker in normalized for marker in cognition_markers)
    if (
        not has_cognition_marker
        and "domain" in normalized
        and any(term in normalized for term in ("create", "new", "add"))
    ):
        return False
    question_starts = (
        "should ",
        "what should ",
        "how should ",
        "why should ",
        "can you analyze",
    )
    if has_cognition_marker:
        return True
    has_governed_cognition_subject = any(marker in normalized for marker in ("sapianta", "aigol"))
    has_cognition_scope = any(
        marker in normalized
        for marker in ("commercialization", "commercial", "architecture", "governance", "cognition")
    )
    has_analysis_intent = any(
        marker in normalized
        for marker in ("first real", "product", "opportunity", "analyze", "analysis", "evaluate", "decide")
    )
    if has_governed_cognition_subject and has_cognition_scope and has_analysis_intent:
        return True
    if _is_plain_ocs_intake_prompt(normalized):
        return True
    return ends_with_question and normalized.startswith(question_starts)


def _is_plain_ocs_intake_prompt(normalized: str) -> bool:
    return (
        "suitable for my business" in normalized
        or "external users" in normalized
        or "modify production customer data" in normalized
        or "production customer data" in normalized
        or "production rollout" in normalized
        or "evaluate employees" in normalized
        or "hiring process" in normalized
        or "ai compliance system" in normalized
        or ("deploy" in normalized and "production" in normalized)
        or ("reporting system" in normalized and "business" in normalized)
    )


def _is_plain_domain_proposal_prompt(normalized: str) -> bool:
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
                "evaluation",
                "hr",
                "code auditing",
                "supplier",
                "ai decision validator",
                "foundation",
            )
        )
    )


def _is_product_1_prompt(normalized: str) -> bool:
    return "product 1" in normalized and "ai decision validator" in normalized


def _is_governance_artifact_creation_prompt(normalized: str) -> bool:
    explicit_phrases = (
        "create a governance artifact",
        "create the governance artifact",
        "create governance artifact",
        "define a governance artifact",
        "define the governance artifact",
        "define governance artifact",
        "add a governance artifact",
        "prepare a governance artifact",
        "create a governed artifact",
        "create the governed artifact",
        "create governed artifact",
        "create a certification artifact",
        "create a governance workflow artifact",
        "create a governance analysis artifact",
    )
    if any(phrase in normalized for phrase in explicit_phrases):
        return True
    creation_verbs = ("create", "add", "define", "draft", "prepare", "write", "generate")
    governance_subjects = ("governance", "governed", "certification")
    artifact_terms = ("artifact", "doc", "document", "markdown", "specification")
    return (
        any(_contains_term(normalized, verb) for verb in creation_verbs)
        and any(_contains_term(normalized, subject) for subject in governance_subjects)
        and any(_contains_term(normalized, artifact) for artifact in artifact_terms)
    )


def _is_governed_repository_mutation_prompt(normalized: str) -> bool:
    explicit_phrases = (
        "governed repository mutation",
        "approved repository mutation",
        "bounded repository mutation",
        "run repository mutation worker",
        "invoke repository mutation worker",
        "apply approved file mutation",
        "apply approved repository mutation",
    )
    return any(phrase in normalized for phrase in explicit_phrases)


def _is_governed_development_workflow_prompt(normalized: str) -> bool:
    explicit_phrases = (
        "governed development workflow",
        "run governed development",
        "execute governed development",
        "start governed development workflow",
        "orchestrate governed development",
    )
    return any(phrase in normalized for phrase in explicit_phrases)


def _is_product_1_domain_foundation_prompt(normalized: str) -> bool:
    return (
        _is_product_1_prompt(normalized)
        and "domain" in normalized
        and "foundation" in normalized
        and any(term in normalized for term in ("define", "extend", "create", "add"))
    )


def _is_product_1_capability_model_prompt(normalized: str) -> bool:
    return (
        _is_product_1_prompt(normalized)
        and any(term in normalized for term in ("capability model", "decision model", "validation model"))
        and any(term in normalized for term in ("define", "extend", "create", "add"))
    )


def _is_product_1_capability_lifecycle_prompt(normalized: str) -> bool:
    return (
        _is_product_1_prompt(normalized)
        and "capability" in normalized
        and "lifecycle" in normalized
        and any(term in normalized for term in ("define", "extend", "create", "add"))
    )


def _is_domain_lifecycle_governance_prompt(normalized: str) -> bool:
    if "domain" not in normalized:
        return False
    lifecycle_terms = (
        "domain lifecycle",
        "domain activation candidate",
        "activate domain",
        "retire domain",
        "domain retirement",
    )
    return any(term in normalized for term in lifecycle_terms) and any(
        term in normalized for term in ("create", "define", "add", "prepare")
    )


def _is_capability_lifecycle_governance_prompt(normalized: str) -> bool:
    if "capability" not in normalized:
        return False
    lifecycle_terms = (
        "capability lifecycle",
        "capability activation candidate",
        "activate capability",
        "retire capability",
        "capability retirement",
    )
    return any(term in normalized for term in lifecycle_terms) and any(
        term in normalized for term in ("create", "define", "add", "prepare")
    )


def _is_proposal_runtime_prompt(normalized: str) -> bool:
    return (
        "proposal" in normalized
        and "artifact" in normalized
        and any(term in normalized for term in ("governed", "governance", "certified"))
        and any(term in normalized for term in ("create", "define", "prepare"))
    )


def _is_improvement_proposal_runtime_prompt(normalized: str) -> bool:
    return (
        "improvement proposal" in normalized
        and any(term in normalized for term in ("create", "define", "prepare"))
    )


def _is_first_real_implementation_generation_prompt(normalized: str) -> bool:
    return (
        "first real implementation generation" in normalized
        and any(term in normalized for term in ("run", "create", "start", "prepare"))
    )


def _is_implementation_plan_to_execution_request_prompt(normalized: str) -> bool:
    return (
        "implementation plan" in normalized
        and "execution request" in normalized
        and any(term in normalized for term in ("convert", "create", "prepare", "turn"))
    )


def _is_task_completion_domain_prompt(normalized: str) -> bool:
    return (
        "domain" in normalized
        and any(term in normalized for term in ("proposal", "foundation", "demo preparation", "product 1"))
        and any(term in normalized for term in ("create", "prepare", "add"))
    )


def _is_task_completion_provider_prompt(normalized: str) -> bool:
    return (
        "provider" in normalized
        and any(term in normalized for term in ("improve", "boundary", "abstraction", "identity", "authority"))
    )


def _is_task_completion_product_foundation_prompt(normalized: str) -> bool:
    return (
        ("ai decision validator" in normalized or "product 1" in normalized)
        and any(term in normalized for term in ("evidence", "presentation", "demo", "eu ai act", "approach"))
    )


def _is_task_completion_domain_continuation_prompt(normalized: str) -> bool:
    return (
        "continue" in normalized
        and "approved" in normalized
        and "domain" in normalized
        and any(term in normalized for term in ("proposal", "next governed boundary", "governed boundary"))
    )


def _is_task_completion_native_development_prompt(normalized: str) -> bool:
    action_terms = ("prepare", "improve", "identify", "add", "create", "implement")
    if normalized.startswith(("what should ", "should ", "how should ", "can you analyze ")):
        return False
    if not any(term in normalized for term in action_terms):
        return False
    if any(term in normalized for term in ("production customer data", "unrestricted", "autonomous agent")):
        return False
    development_subjects = (
        "governance validation report",
        "governance failures",
        "governance improvement",
        "replay lineage",
        "replay-derived",
        "replay improvement",
        "execution summary boundary",
        "capability candidate",
        "document validation",
        "operator experience",
        "acli adoption",
        "task completion",
        "external worker",
        "worker lifecycle",
        "provider adapter",
    )
    return any(subject in normalized for subject in development_subjects)


def _is_freeform_clarification_prompt(normalized: str) -> bool:
    return normalized in {
        "help me improve the system",
        "build something useful for my company",
        "make the platform better",
    }


def _is_freeform_ambiguous_prompt(normalized: str) -> bool:
    return normalized in {
        "i want an ai system for my business",
        "help automate company operations",
        "create an intelligent management solution",
    }


def _is_native_development_context_prompt(prompt: str) -> bool:
    normalized = prompt.lower()
    has_milestone = "aigol_" in normalized or "v1" in normalized
    has_development_marker = any(
        marker in normalized for marker in ("implement", "create", "open", "foundation", "runtime", "worker", "domain")
    )
    return has_milestone and has_development_marker


def _routing_decision_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    analysis: dict[str, Any],
    universal_translation_capture: dict[str, Any] | None,
    canonical_semantic_capture: dict[str, Any] | None,
    ubtr_cognition_orchestration_capture: dict[str, Any] | None,
    ubtr_ocs_cognition_handoff_capture: dict[str, Any] | None,
    ubtr_cognition_result_integration_capture: dict[str, Any] | None,
    compatibility_route_evidence: dict[str, Any] | None,
    semantic_comparison_artifact: dict[str, Any] | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    translation_artifact = (
        universal_translation_capture.get("translation_artifact")
        if isinstance(universal_translation_capture, dict)
        else None
    )
    semantic_artifact = (
        canonical_semantic_capture.get("semantic_artifact") if isinstance(canonical_semantic_capture, dict) else None
    )
    semantic_routing_source = analysis.get("semantic_routing_source") or (
        "CANONICAL_SEMANTIC_ARTIFACT"
        if isinstance(semantic_artifact, dict)
        and analysis["matched_terms"][:2] == ["ubtr", "canonical-semantic-artifact"]
        else "COMPATIBILITY_FALLBACK"
    )
    migration_batch_id = analysis.get("migration_batch_id") or (
        "UBTR_CONSUMER_MIGRATION_BATCH_01_ACLI_ROUTING_V1"
        if isinstance(compatibility_route_evidence, dict)
        and semantic_routing_source == "CANONICAL_SEMANTIC_ARTIFACT"
        else None
    )
    artifact = {
        "artifact_type": CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "routing_decision_id": f"{_require_string(routing_id, 'routing_id')}:DECISION",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "workflow_id": analysis["workflow_id"],
        "routing_status": analysis["routing_status"],
        "confidence": analysis["confidence"],
        "matched_terms": deepcopy(analysis["matched_terms"]),
        "human_intent_intake": deepcopy(analysis.get("human_intent_intake")),
        "intent_family": analysis.get("intent_family"),
        "clarification_questions": deepcopy(analysis.get("clarification_questions", [])),
        "expected_workflow_targets": deepcopy(analysis.get("expected_workflow_targets", [])),
        "ocs_escalation_reason": (analysis.get("ocs_escalation") or {}).get("escalation_reason"),
        "ocs_escalation_confidence": (analysis.get("ocs_escalation") or {}).get("confidence"),
        "ocs_provider_selection": (analysis.get("ocs_escalation") or {}).get("provider_selection"),
        "proposal_only_classification": (analysis.get("ocs_escalation") or {}).get(
            "proposal_only_classification"
        )
        is True,
        "universal_translation_reference": (
            universal_translation_capture.get("translation_replay_reference")
            if isinstance(universal_translation_capture, dict)
            else None
        ),
        "universal_translation_hash": (
            translation_artifact.get("artifact_hash") if isinstance(translation_artifact, dict) else None
        ),
        "universal_translation_direction": (
            translation_artifact.get("source_direction") if isinstance(translation_artifact, dict) else None
        ),
        "universal_translation_confidence": (
            translation_artifact.get("confidence") if isinstance(translation_artifact, dict) else None
        ),
        "canonical_semantic_artifact_reference": (
            canonical_semantic_capture.get("semantic_replay_reference")
            if isinstance(canonical_semantic_capture, dict)
            else None
        ),
        "canonical_semantic_artifact_hash": (
            semantic_artifact.get("artifact_hash") if isinstance(semantic_artifact, dict) else None
        ),
        "canonical_semantic_artifact_type": (
            semantic_artifact.get("artifact_type") if isinstance(semantic_artifact, dict) else None
        ),
        "semantic_routing_source": semantic_routing_source,
        "migration_batch_id": migration_batch_id,
        "previous_routing_source": (
            compatibility_route_evidence.get("compatibility_source")
            if isinstance(compatibility_route_evidence, dict)
            else None
        ),
        "previous_compatibility_workflow_id": (
            compatibility_route_evidence.get("compatibility_workflow_id")
            if isinstance(compatibility_route_evidence, dict)
            else None
        ),
        "previous_compatibility_routing_status": (
            compatibility_route_evidence.get("compatibility_routing_status")
            if isinstance(compatibility_route_evidence, dict)
            else None
        ),
        "previous_compatibility_confidence": (
            compatibility_route_evidence.get("compatibility_confidence")
            if isinstance(compatibility_route_evidence, dict)
            else None
        ),
        "previous_compatibility_matched_terms": (
            deepcopy(compatibility_route_evidence.get("compatibility_matched_terms", []))
            if isinstance(compatibility_route_evidence, dict)
            else []
        ),
        "previous_compatibility_interpretation": deepcopy(
            analysis.get("previous_compatibility_interpretation")
        ),
        "semantic_parity_evidence": deepcopy(analysis.get("semantic_parity_evidence")),
        "semantic_comparison_artifact": (
            deepcopy(semantic_comparison_artifact)
            if isinstance(semantic_comparison_artifact, dict)
            else None
        ),
        "semantic_comparison_hash": (
            semantic_comparison_artifact.get("artifact_hash")
            if isinstance(semantic_comparison_artifact, dict)
            else None
        ),
        "semantic_equivalence_result": (
            semantic_comparison_artifact.get("semantic_equivalence_result")
            if isinstance(semantic_comparison_artifact, dict)
            else None
        ),
        "semantic_comparison_parity_status": (
            semantic_comparison_artifact.get("parity_status")
            if isinstance(semantic_comparison_artifact, dict)
            else None
        ),
        "semantic_comparison_non_authoritative": (
            semantic_comparison_artifact.get("non_authoritative") is True
            if isinstance(semantic_comparison_artifact, dict)
            else None
        ),
        "new_csa_routing_source": (
            "CANONICAL_SEMANTIC_ARTIFACT"
            if isinstance(compatibility_route_evidence, dict)
            and semantic_routing_source == "CANONICAL_SEMANTIC_ARTIFACT"
            else None
        ),
        "ubtr_semantic_cognition_orchestration_reference": (
            ubtr_cognition_orchestration_capture.get("orchestration_replay_reference")
            if isinstance(ubtr_cognition_orchestration_capture, dict)
            else None
        ),
        "ubtr_semantic_cognition_decision": (
            ubtr_cognition_orchestration_capture.get("semantic_decision")
            if isinstance(ubtr_cognition_orchestration_capture, dict)
            else None
        ),
        "ubtr_semantic_cognition_reasons": (
            list(ubtr_cognition_orchestration_capture.get("decision_reasons") or [])
            if isinstance(ubtr_cognition_orchestration_capture, dict)
            else []
        ),
        "ubtr_ocs_cognition_request_hash": (
            ubtr_cognition_orchestration_capture.get("ocs_cognition_request_hash")
            if isinstance(ubtr_cognition_orchestration_capture, dict)
            else None
        ),
        "ubtr_ocs_cognition_handoff_reference": (
            ubtr_ocs_cognition_handoff_capture.get("handoff_replay_reference")
            if isinstance(ubtr_ocs_cognition_handoff_capture, dict)
            else None
        ),
        "ubtr_ocs_cognition_handoff_status": (
            ubtr_ocs_cognition_handoff_capture.get("handoff_status")
            if isinstance(ubtr_ocs_cognition_handoff_capture, dict)
            else None
        ),
        "ubtr_ocs_context_hash": (
            ubtr_ocs_cognition_handoff_capture.get("ocs_context_hash")
            if isinstance(ubtr_ocs_cognition_handoff_capture, dict)
            else None
        ),
        "ubtr_ocs_cognition_hash": (
            ubtr_ocs_cognition_handoff_capture.get("ocs_cognition_hash")
            if isinstance(ubtr_ocs_cognition_handoff_capture, dict)
            else None
        ),
        "ubtr_ocs_provider_necessity": (
            deepcopy(ubtr_ocs_cognition_handoff_capture.get("ocs_provider_necessity"))
            if isinstance(ubtr_ocs_cognition_handoff_capture, dict)
            else None
        ),
        "ubtr_cognition_result_integration_reference": (
            ubtr_cognition_result_integration_capture.get("integration_replay_reference")
            if isinstance(ubtr_cognition_result_integration_capture, dict)
            else None
        ),
        "ubtr_cognition_result_integration_status": (
            ubtr_cognition_result_integration_capture.get("integration_status")
            if isinstance(ubtr_cognition_result_integration_capture, dict)
            else None
        ),
        "ubtr_cognition_integrated_semantic_artifact_hash": (
            ubtr_cognition_result_integration_capture.get("integrated_canonical_semantic_artifact_hash")
            if isinstance(ubtr_cognition_result_integration_capture, dict)
            else None
        ),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _workflow_selection_artifact(
    *,
    routing_id: str,
    decision: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(decision)
    artifact = {
        "artifact_type": CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "workflow_selection_id": f"{_require_string(routing_id, 'routing_id')}:WORKFLOW-SELECTION",
        "routing_decision_reference": decision["routing_decision_id"],
        "routing_decision_hash": decision["artifact_hash"],
        "canonical_chain_id": decision["canonical_chain_id"],
        "workflow_id": analysis["workflow_id"],
        "routing_status": analysis["routing_status"],
        "existing_runtime": analysis["existing_runtime"],
        "existing_cli_command": analysis["existing_cli_command"],
        "operator_summary": analysis["operator_summary"],
        "human_intent_intake": deepcopy(analysis.get("human_intent_intake")),
        "intent_family": analysis.get("intent_family"),
        "clarification_questions": deepcopy(analysis.get("clarification_questions", [])),
        "expected_workflow_targets": deepcopy(analysis.get("expected_workflow_targets", [])),
        "ocs_escalation_reason": decision.get("ocs_escalation_reason"),
        "ocs_escalation_confidence": decision.get("ocs_escalation_confidence"),
        "ocs_provider_selection": decision.get("ocs_provider_selection"),
        "proposal_only_classification": decision.get("proposal_only_classification") is True,
        "universal_translation_reference": decision.get("universal_translation_reference"),
        "universal_translation_hash": decision.get("universal_translation_hash"),
        "universal_translation_direction": decision.get("universal_translation_direction"),
        "universal_translation_confidence": decision.get("universal_translation_confidence"),
        "canonical_semantic_artifact_reference": decision.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": decision.get("canonical_semantic_artifact_hash"),
        "canonical_semantic_artifact_type": decision.get("canonical_semantic_artifact_type"),
        "semantic_routing_source": decision.get("semantic_routing_source"),
        "migration_batch_id": decision.get("migration_batch_id"),
        "previous_routing_source": decision.get("previous_routing_source"),
        "previous_compatibility_workflow_id": decision.get("previous_compatibility_workflow_id"),
        "previous_compatibility_routing_status": decision.get("previous_compatibility_routing_status"),
        "previous_compatibility_confidence": decision.get("previous_compatibility_confidence"),
        "previous_compatibility_matched_terms": deepcopy(
            decision.get("previous_compatibility_matched_terms", [])
        ),
        "previous_compatibility_interpretation": deepcopy(
            decision.get("previous_compatibility_interpretation")
        ),
        "semantic_parity_evidence": deepcopy(decision.get("semantic_parity_evidence")),
        "semantic_comparison_artifact": deepcopy(decision.get("semantic_comparison_artifact")),
        "semantic_comparison_hash": decision.get("semantic_comparison_hash"),
        "semantic_equivalence_result": decision.get("semantic_equivalence_result"),
        "semantic_comparison_parity_status": decision.get("semantic_comparison_parity_status"),
        "semantic_comparison_non_authoritative": decision.get("semantic_comparison_non_authoritative"),
        "new_csa_routing_source": decision.get("new_csa_routing_source"),
        "ubtr_semantic_cognition_orchestration_reference": decision.get(
            "ubtr_semantic_cognition_orchestration_reference"
        ),
        "ubtr_semantic_cognition_decision": decision.get("ubtr_semantic_cognition_decision"),
        "ubtr_semantic_cognition_reasons": deepcopy(decision.get("ubtr_semantic_cognition_reasons", [])),
        "ubtr_ocs_cognition_request_hash": decision.get("ubtr_ocs_cognition_request_hash"),
        "ubtr_ocs_cognition_handoff_reference": decision.get("ubtr_ocs_cognition_handoff_reference"),
        "ubtr_ocs_cognition_handoff_status": decision.get("ubtr_ocs_cognition_handoff_status"),
        "ubtr_ocs_context_hash": decision.get("ubtr_ocs_context_hash"),
        "ubtr_ocs_cognition_hash": decision.get("ubtr_ocs_cognition_hash"),
        "ubtr_ocs_provider_necessity": deepcopy(decision.get("ubtr_ocs_provider_necessity")),
        "ubtr_cognition_result_integration_reference": decision.get(
            "ubtr_cognition_result_integration_reference"
        ),
        "ubtr_cognition_result_integration_status": decision.get("ubtr_cognition_result_integration_status"),
        "ubtr_cognition_integrated_semantic_artifact_hash": decision.get(
            "ubtr_cognition_integrated_semantic_artifact_hash"
        ),
        "coverage": _coverage(),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "approval_required_if_downstream_requires_approval": True,
        "authorization_required_if_downstream_requires_authorization": True,
        "provider_controls_preserved": True,
        "worker_controls_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(decision: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(decision)
    _verify_artifact_hash(selection)
    artifact = {
        "event_type": "CONVERSATIONAL_CLI_ROUTING_RETURNED",
        "milestone_id": MILESTONE_ID,
        "routing_decision_reference": decision["routing_decision_id"],
        "routing_decision_hash": decision["artifact_hash"],
        "workflow_selection_reference": selection["workflow_selection_id"],
        "workflow_selection_hash": selection["artifact_hash"],
        "routing_status": selection["routing_status"],
        "workflow_id": selection["workflow_id"],
        "universal_translation_reference": decision.get("universal_translation_reference"),
        "universal_translation_hash": decision.get("universal_translation_hash"),
        "canonical_semantic_artifact_reference": decision.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": decision.get("canonical_semantic_artifact_hash"),
        "semantic_routing_source": decision.get("semantic_routing_source"),
        "migration_batch_id": decision.get("migration_batch_id"),
        "previous_routing_source": decision.get("previous_routing_source"),
        "previous_compatibility_workflow_id": decision.get("previous_compatibility_workflow_id"),
        "previous_compatibility_routing_status": decision.get("previous_compatibility_routing_status"),
        "previous_compatibility_confidence": decision.get("previous_compatibility_confidence"),
        "previous_compatibility_matched_terms": deepcopy(
            decision.get("previous_compatibility_matched_terms", [])
        ),
        "previous_compatibility_interpretation": deepcopy(
            decision.get("previous_compatibility_interpretation")
        ),
        "semantic_parity_evidence": deepcopy(decision.get("semantic_parity_evidence")),
        "semantic_comparison_artifact": deepcopy(decision.get("semantic_comparison_artifact")),
        "semantic_comparison_hash": decision.get("semantic_comparison_hash"),
        "semantic_equivalence_result": decision.get("semantic_equivalence_result"),
        "semantic_comparison_parity_status": decision.get("semantic_comparison_parity_status"),
        "semantic_comparison_non_authoritative": decision.get("semantic_comparison_non_authoritative"),
        "new_csa_routing_source": decision.get("new_csa_routing_source"),
        "ubtr_semantic_cognition_orchestration_reference": decision.get(
            "ubtr_semantic_cognition_orchestration_reference"
        ),
        "ubtr_semantic_cognition_decision": decision.get("ubtr_semantic_cognition_decision"),
        "ubtr_semantic_cognition_reasons": deepcopy(decision.get("ubtr_semantic_cognition_reasons", [])),
        "ubtr_ocs_cognition_request_hash": decision.get("ubtr_ocs_cognition_request_hash"),
        "ubtr_ocs_cognition_handoff_reference": decision.get("ubtr_ocs_cognition_handoff_reference"),
        "ubtr_ocs_cognition_handoff_status": decision.get("ubtr_ocs_cognition_handoff_status"),
        "ubtr_ocs_context_hash": decision.get("ubtr_ocs_context_hash"),
        "ubtr_ocs_cognition_hash": decision.get("ubtr_ocs_cognition_hash"),
        "ubtr_ocs_provider_necessity": deepcopy(decision.get("ubtr_ocs_provider_necessity")),
        "ubtr_cognition_result_integration_reference": decision.get(
            "ubtr_cognition_result_integration_reference"
        ),
        "ubtr_cognition_result_integration_status": decision.get("ubtr_cognition_result_integration_status"),
        "ubtr_cognition_integrated_semantic_artifact_hash": decision.get(
            "ubtr_cognition_integrated_semantic_artifact_hash"
        ),
        "ocs_escalation_reason": decision.get("ocs_escalation_reason"),
        "ocs_escalation_confidence": decision.get("ocs_escalation_confidence"),
        "ocs_provider_selection": decision.get("ocs_provider_selection"),
        "proposal_only_classification": decision.get("proposal_only_classification") is True,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": selection["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_decision_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: Any,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "routing_decision_id": f"{routing_id}:DECISION",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "human_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "workflow_id": None,
        "routing_status": FAILED_CLOSED,
        "confidence": "NONE",
        "matched_terms": [],
        "human_intent_intake": None,
        "intent_family": None,
        "clarification_questions": [],
        "expected_workflow_targets": [],
        "universal_translation_reference": None,
        "universal_translation_hash": None,
        "universal_translation_direction": None,
        "universal_translation_confidence": None,
        "canonical_semantic_artifact_reference": None,
        "canonical_semantic_artifact_hash": None,
        "canonical_semantic_artifact_type": None,
        "semantic_routing_source": None,
        "migration_batch_id": None,
        "previous_routing_source": None,
        "previous_compatibility_workflow_id": None,
        "previous_compatibility_routing_status": None,
        "previous_compatibility_confidence": None,
        "previous_compatibility_matched_terms": [],
        "previous_compatibility_interpretation": None,
        "semantic_parity_evidence": None,
        "semantic_comparison_artifact": None,
        "semantic_comparison_hash": None,
        "semantic_equivalence_result": None,
        "semantic_comparison_parity_status": None,
        "semantic_comparison_non_authoritative": None,
        "new_csa_routing_source": None,
        "ubtr_semantic_cognition_orchestration_reference": None,
        "ubtr_semantic_cognition_decision": None,
        "ubtr_semantic_cognition_reasons": [],
        "ubtr_ocs_cognition_request_hash": None,
        "ubtr_ocs_cognition_handoff_reference": None,
        "ubtr_ocs_cognition_handoff_status": None,
        "ubtr_ocs_context_hash": None,
        "ubtr_ocs_cognition_hash": None,
        "ubtr_ocs_provider_necessity": None,
        "ubtr_cognition_result_integration_reference": None,
        "ubtr_cognition_result_integration_status": None,
        "ubtr_cognition_integrated_semantic_artifact_hash": None,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_selection_artifact(
    *,
    routing_id: str,
    decision: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _workflow_selection_artifact(
        routing_id=routing_id,
        decision=decision,
        analysis={
            "workflow_id": None,
            "routing_status": FAILED_CLOSED,
            "existing_runtime": None,
            "existing_cli_command": None,
            "operator_summary": "",
            "human_intent_intake": None,
            "intent_family": None,
            "clarification_questions": [],
            "expected_workflow_targets": [],
        },
        created_at=created_at,
        replay_reference=replay_reference,
        failure_reason=failure_reason,
    )


def _capture(decision: dict[str, Any], selection: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "command": "aigol conversational route",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "routing_status": returned["routing_status"],
        "workflow_id": returned["workflow_id"],
        "routing_decision_artifact": deepcopy(decision),
        "workflow_selection_artifact": deepcopy(selection),
        "conversational_routing_returned": deepcopy(returned),
        "conversational_cli_routing_replay_reference": str(replay_path),
        "universal_translation_reference": decision.get("universal_translation_reference"),
        "universal_translation_hash": decision.get("universal_translation_hash"),
        "canonical_semantic_artifact_reference": decision.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": decision.get("canonical_semantic_artifact_hash"),
        "semantic_routing_source": decision.get("semantic_routing_source"),
        "migration_batch_id": decision.get("migration_batch_id"),
        "previous_routing_source": decision.get("previous_routing_source"),
        "previous_compatibility_workflow_id": decision.get("previous_compatibility_workflow_id"),
        "previous_compatibility_routing_status": decision.get("previous_compatibility_routing_status"),
        "previous_compatibility_confidence": decision.get("previous_compatibility_confidence"),
        "previous_compatibility_matched_terms": deepcopy(
            decision.get("previous_compatibility_matched_terms", [])
        ),
        "previous_compatibility_interpretation": deepcopy(
            decision.get("previous_compatibility_interpretation")
        ),
        "semantic_parity_evidence": deepcopy(decision.get("semantic_parity_evidence")),
        "semantic_comparison_artifact": deepcopy(decision.get("semantic_comparison_artifact")),
        "semantic_comparison_hash": decision.get("semantic_comparison_hash"),
        "semantic_equivalence_result": decision.get("semantic_equivalence_result"),
        "semantic_comparison_parity_status": decision.get("semantic_comparison_parity_status"),
        "semantic_comparison_non_authoritative": decision.get("semantic_comparison_non_authoritative"),
        "new_csa_routing_source": decision.get("new_csa_routing_source"),
        "ubtr_semantic_cognition_orchestration_reference": decision.get(
            "ubtr_semantic_cognition_orchestration_reference"
        ),
        "ubtr_semantic_cognition_decision": decision.get("ubtr_semantic_cognition_decision"),
        "ubtr_semantic_cognition_reasons": deepcopy(decision.get("ubtr_semantic_cognition_reasons", [])),
        "ubtr_ocs_cognition_request_hash": decision.get("ubtr_ocs_cognition_request_hash"),
        "ubtr_ocs_cognition_handoff_reference": decision.get("ubtr_ocs_cognition_handoff_reference"),
        "ubtr_ocs_cognition_handoff_status": decision.get("ubtr_ocs_cognition_handoff_status"),
        "ubtr_ocs_context_hash": decision.get("ubtr_ocs_context_hash"),
        "ubtr_ocs_cognition_hash": decision.get("ubtr_ocs_cognition_hash"),
        "ubtr_ocs_provider_necessity": deepcopy(decision.get("ubtr_ocs_provider_necessity")),
        "ubtr_cognition_result_integration_reference": decision.get(
            "ubtr_cognition_result_integration_reference"
        ),
        "ubtr_cognition_result_integration_status": decision.get("ubtr_cognition_result_integration_status"),
        "ubtr_cognition_integrated_semantic_artifact_hash": decision.get(
            "ubtr_cognition_integrated_semantic_artifact_hash"
        ),
        "ocs_escalation_reason": decision.get("ocs_escalation_reason"),
        "ocs_escalation_confidence": decision.get("ocs_escalation_confidence"),
        "ocs_provider_selection": decision.get("ocs_provider_selection"),
        "proposal_only_classification": decision.get("proposal_only_classification") is True,
        "coverage": deepcopy(selection.get("coverage", _coverage())),
        "fail_closed": returned["routing_status"] == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["conversational_cli_routing_hash"] = replay_hash(capture)
    return capture


def _workflow(workflow_id: str, cli_command: str, runtime: str, *, clarification: bool = False) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "existing_cli_command": cli_command,
        "existing_runtime": runtime,
        "conversationally_accessible": True,
        "clarification_required": clarification,
    }


def _workflow_by_id(workflow_id: str) -> dict[str, Any]:
    for entry in workflow_registry():
        if entry["workflow_id"] == workflow_id:
            return entry
    raise FailClosedRuntimeError("conversational CLI routing failed closed: workflow is not registered")


def _coverage() -> dict[str, Any]:
    registry = workflow_registry()
    accessible = [entry for entry in registry if entry["conversationally_accessible"] is True]
    return {
        "registered_workflows": len(registry),
        "conversationally_accessible_workflows": len(accessible),
        "coverage_ratio": f"{len(accessible)}/{len(registry)}",
        "workflow_ids": [entry["workflow_id"] for entry in registry],
    }


def _operator_summary(workflow_id: str) -> str:
    summaries = {
        CREATE_DOMAIN_TRADING: "Route to existing native-development domain workflow.",
        CREATE_DOMAIN_MARKETING: "Route to existing native-development domain workflow.",
        CREATE_DOMAIN_COMPLIANCE_CLARIFICATION: "Use certified unknown-domain clarification workflow.",
        DOMAIN_ADAPTATION_REFERENCE: "Resolve semantic domain references into a governed adaptation candidate.",
        OPERATOR_DECISION_SUPPORT: "Generate a governed non-authoritative recommendation for human review.",
        SHOW_LATEST_REPLAY_CHAIN: "Show latest replay chain through read-only chain inspection.",
        REVIEW_LATEST_AUDIT: "Review existing capability audit artifacts without regenerating them.",
        IMPROVE_PROVIDER_LAYER: "Route to provider-layer improvement review guidance without execution.",
        SHOW_STATUS: "Show AiGOL status.",
        SHOW_DASHBOARD: "Show read-only operator dashboard.",
        NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION: "Assemble native development context without provider or execution.",
        DOMAIN_LIFECYCLE_GOVERNANCE: "Select certified domain lifecycle governance entrypoint without execution.",
        CAPABILITY_LIFECYCLE_GOVERNANCE: (
            "Select certified capability lifecycle governance entrypoint without execution."
        ),
        PROPOSAL_RUNTIME: "Select certified proposal runtime entrypoint without execution.",
        IMPROVEMENT_PROPOSAL_RUNTIME: "Select certified improvement proposal runtime entrypoint without execution.",
        FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH: (
            "Select certified first real implementation generation entrypoint without execution."
        ),
        IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST: (
            "Select certified implementation-plan-to-execution-request entrypoint without execution."
        ),
        AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION: (
            "Select Product 1 AI Decision Validator domain foundation entrypoint without execution."
        ),
        AI_DECISION_VALIDATOR_CAPABILITY_MODEL: (
            "Select Product 1 AI Decision Validator capability model entrypoint without execution."
        ),
        AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE: (
            "Select Product 1 AI Decision Validator capability lifecycle entrypoint without execution."
        ),
        OCS_LLM_COGNITION: "Run certified OCS LLM cognition end-to-end for human-facing guidance.",
        PROVIDER_ONBOARDING_DOMAIN: "Route provider add/use/disable requests into certified provider onboarding domain.",
        BOUNDED_FILE_WRITE_WORKER_USER_SESSION: (
            "Select bounded certified FILE_WRITE worker session after clarification and approval."
        ),
        AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW: (
            "Route reviewed domain approval prompts to the authorization-entry binding path without execution."
        ),
        DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE: (
            "Convert approved domain authorization-entry evidence into an execution-ready packet without execution."
        ),
        DOMAIN_EXECUTION_AUTHORIZATION: "Authorize the latest execution-ready domain packet without worker invocation.",
        DOMAIN_WORKER_REQUEST: "Create a worker invocation request from the latest execution authorization only.",
        DOMAIN_WORKER_ASSIGNMENT: "Assign a compatible worker from the latest worker request without dispatch.",
        DOMAIN_WORKER_DISPATCH: "Dispatch the latest assigned worker without invocation.",
        DOMAIN_WORKER_INVOCATION: "Invoke the latest dispatched worker without execution or result validation.",
        DOMAIN_WORKER_EXECUTION: "Start execution from the latest invoked worker without completion or result validation.",
        DOMAIN_WORKER_RESULT_CAPTURE: "Capture output from the latest execution without validation or replay review.",
        DOMAIN_WORKER_RESULT_VALIDATION: "Validate the latest captured worker result without replay review.",
        DOMAIN_POST_EXECUTION_REPLAY_REVIEW: "Review the latest validated worker result replay without termination.",
        DOMAIN_GOVERNED_TERMINATION: "Terminate the latest reviewed operation without new work.",
        GOVERNANCE_ARTIFACT_CREATION: (
            "Select the certified governance artifact creation workflow without mutation or approval bypass."
        ),
        GOVERNED_REPOSITORY_MUTATION: (
            "Select the governed repository mutation workflow without mutation or approval bypass."
        ),
        GOVERNED_DEVELOPMENT_WORKFLOW: (
            "Select the governed development orchestration workflow without mutation or approval bypass."
        ),
        HUMAN_INTENT_CLARIFICATION_INTAKE: (
            "Ask deterministic clarification questions for normal human intent before provider fallback."
        ),
        DEFAULT_PROVIDER_ASSISTED_CONVERSATION: "Use provider-assisted conversation integration with fail-closed fallback.",
    }
    return summaries.get(workflow_id, "")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversational CLI routing replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("conversational CLI routing failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("conversational CLI routing artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversational CLI routing artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("conversational CLI routing replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversational CLI routing replay hash mismatch")


def _contains_term(normalized: str, term: str) -> bool:
    return term in normalized if " " in term else re.search(rf"\b{re.escape(term)}\b", normalized) is not None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
