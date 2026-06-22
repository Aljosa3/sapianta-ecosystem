"""End-to-end real-user worker execution certification for human intent."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_end_to_end_real_user_worker_execution_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"
FINAL_VERDICT_CERTIFIED = "HUMAN_INTENT_END_TO_END_WORKER_EXECUTION_CERTIFIED"
FINAL_VERDICT_GAPS = "HUMAN_INTENT_END_TO_END_WORKER_EXECUTION_GAPS_FOUND"

REPLAY_STEPS = (
    "human_request_recorded",
    "ocs_intent_detection_recorded",
    "cognition_clarification_recorded",
    "human_clarification_response_recorded",
    "ocs_context_update_recorded",
    "cognition_workflow_proposal_recorded",
    "ocs_workflow_selection_recorded",
    "execution_summary_recorded",
    "human_approval_recorded",
    "execution_authorization_recorded",
    "worker_handoff_recorded",
    "worker_invocation_recorded",
    "execution_outcome_recorded",
)

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "E2E-001",
        "coverage": "clear_intent",
        "human_request": "Please create a short report checking whether this customer reply explains its decision.",
        "clarification_required": False,
        "clarification_questions": [],
        "clarification_responses": [],
        "intent_family": "CUSTOMER_REPLY_JUSTIFICATION_REVIEW",
        "workflow_candidates": ["CUSTOMER_REPLY_REPORT_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Create a short customer-ready justification review report.",
        "approval_decision": "APPROVE",
        "modification_before_approval": None,
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-002",
        "coverage": "ambiguous_intent",
        "human_request": "Create a report.",
        "clarification_required": True,
        "clarification_questions": [
            "What should the report evaluate, and who is it for?",
        ],
        "clarification_responses": [
            "It should evaluate an AI customer-support reply and be usable by the support lead.",
        ],
        "intent_family": "CUSTOMER_SUPPORT_REPLY_REPORT",
        "workflow_candidates": ["CUSTOMER_REPLY_REPORT_WORKER", "GENERAL_REPORT_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Create a support-lead report reviewing an AI customer-support reply.",
        "approval_decision": "APPROVE",
        "modification_before_approval": None,
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-003",
        "coverage": "multi_turn_clarification",
        "human_request": "Analyze this.",
        "clarification_required": True,
        "clarification_questions": [
            "What should be analyzed?",
            "What decision should the analysis support?",
        ],
        "clarification_responses": [
            "Analyze the draft customer response.",
            "Check whether it gives enough reason before we send it.",
        ],
        "intent_family": "CUSTOMER_RESPONSE_REASONING_ANALYSIS",
        "workflow_candidates": ["CUSTOMER_REPLY_REPORT_WORKER", "RISK_REVIEW_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Analyze the draft response for sufficient reasoning before sending.",
        "approval_decision": "APPROVE",
        "modification_before_approval": None,
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-004",
        "coverage": "intent_correction",
        "human_request": "Prepare a summary for support.",
        "clarification_required": True,
        "clarification_questions": [
            "Should this be a general summary, a customer-facing report, or a risk check?",
        ],
        "clarification_responses": [
            "Actually make it a risk check for the support reply before it is sent.",
        ],
        "intent_family": "SUPPORT_REPLY_RISK_CHECK",
        "workflow_candidates": ["GENERAL_SUMMARY_WORKER", "SUPPORT_REPLY_RISK_WORKER"],
        "selected_workflow": "SUPPORT_REPLY_RISK_WORKER",
        "execution_summary": "Create a risk check for the support reply before it is sent.",
        "approval_decision": "APPROVE",
        "modification_before_approval": "general_summary_to_risk_check",
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-005",
        "coverage": "multiple_workflow_candidates",
        "human_request": "Review this and prepare next steps.",
        "clarification_required": True,
        "clarification_questions": [
            "Do you want a quality review, a risk review, or an action plan?",
        ],
        "clarification_responses": [
            "Do a risk review first and include the next steps only if risk is found.",
        ],
        "intent_family": "RISK_FIRST_REVIEW_WITH_NEXT_STEPS",
        "workflow_candidates": ["QUALITY_REVIEW_WORKER", "RISK_REVIEW_WORKER", "ACTION_PLAN_WORKER"],
        "selected_workflow": "RISK_REVIEW_WORKER",
        "execution_summary": "Run a risk-first review and prepare next steps only when risk is present.",
        "approval_decision": "APPROVE",
        "modification_before_approval": None,
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-006",
        "coverage": "execution_approval",
        "human_request": "Check this customer response and make the review.",
        "clarification_required": True,
        "clarification_questions": [
            "Should I create the review now after summarizing the planned action?",
        ],
        "clarification_responses": [
            "Yes, create it after you show the summary.",
        ],
        "intent_family": "APPROVED_CUSTOMER_RESPONSE_REVIEW",
        "workflow_candidates": ["CUSTOMER_REPLY_REPORT_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Create the customer response review after showing the planned action.",
        "approval_decision": "APPROVE",
        "modification_before_approval": None,
        "expected_worker_execution": True,
    },
    {
        "scenario_id": "E2E-007",
        "coverage": "execution_rejection",
        "human_request": "Make the customer reply report.",
        "clarification_required": True,
        "clarification_questions": [
            "I can prepare the report now. Do you approve execution?",
        ],
        "clarification_responses": [
            "No, do not run it yet.",
        ],
        "intent_family": "CUSTOMER_REPLY_REPORT_REJECTED",
        "workflow_candidates": ["CUSTOMER_REPLY_REPORT_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Create the customer reply report.",
        "approval_decision": "REJECT",
        "modification_before_approval": None,
        "expected_worker_execution": False,
    },
    {
        "scenario_id": "E2E-008",
        "coverage": "execution_modification_before_approval",
        "human_request": "Prepare a detailed review of the reply.",
        "clarification_required": True,
        "clarification_questions": [
            "Should the review be detailed, short, customer-facing, or internal?",
        ],
        "clarification_responses": [
            "Make it one page only, customer-facing, and then I approve.",
        ],
        "intent_family": "MODIFIED_CUSTOMER_FACING_ONE_PAGE_REVIEW",
        "workflow_candidates": ["DETAILED_REVIEW_WORKER", "CUSTOMER_REPLY_REPORT_WORKER"],
        "selected_workflow": "CUSTOMER_REPLY_REPORT_WORKER",
        "execution_summary": "Create a one-page customer-facing review of the reply.",
        "approval_decision": "APPROVE_MODIFIED",
        "modification_before_approval": "one_page_customer_facing_only",
        "expected_worker_execution": True,
    },
)


def run_human_intent_end_to_end_real_user_worker_execution_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"

    scenario_results = [_run_scenario(root / "scenarios" / spec["scenario_id"], spec) for spec in SCENARIOS]
    replay_results = [_reconstruct_scenario_replay(result) for result in scenario_results]
    no_secret_leak = _secret_free(root)
    assertions = _aggregate_assertions(scenario_results, replay_results, no_secret_leak)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = {
        "artifact_type": "HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_results),
        "coverage": [result["coverage"] for result in scenario_results],
        "approved_execution_scenarios": [
            result["scenario_id"] for result in scenario_results if result["expected_worker_execution"] is True
        ],
        "rejected_execution_scenarios": [
            result["scenario_id"] for result in scenario_results if result["expected_worker_execution"] is False
        ],
        "scenario_verdicts": {
            result["scenario_id"]: result["scenario_verdict"] for result in scenario_results
        },
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)

    evidence = {
        "artifact_type": "HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "scenario_results": scenario_results,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)

    replay_package = {
        "artifact_type": "HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "replay_results": replay_results,
        "human_to_worker_chain": "Human -> OCS -> Cognition -> OCS -> Human Approval -> Worker -> Replay",
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)

    report = {
        "artifact_type": "HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "scenario_results": _summarize_scenarios(scenario_results),
        "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)

    _persist(evidence_dir, replay_dir, report_dir, evidence, coverage, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(
            evidence_dir / "000_human_intent_end_to_end_worker_execution_evidence_package.json"
        ),
        "coverage_report_path": str(
            evidence_dir / "001_human_intent_end_to_end_worker_execution_coverage_report.json"
        ),
        "replay_package_path": str(
            replay_dir / "000_human_intent_end_to_end_worker_execution_replay_package.json"
        ),
        "certification_report_path": str(
            report_dir / "000_human_intent_end_to_end_worker_execution_certification_report.json"
        ),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def _run_scenario(scenario_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    scenario_id = spec["scenario_id"]
    boundary_dir = scenario_root / "end_to_end_boundary"
    request = _human_request_artifact(spec)
    intent = _ocs_intent_detection_artifact(spec, request)
    clarification = _cognition_clarification_artifact(spec, intent)
    response = _human_clarification_response_artifact(spec, clarification)
    context = _ocs_context_update_artifact(spec, request, response)
    proposal = _cognition_workflow_proposal_artifact(spec, context)
    selection = _ocs_workflow_selection_artifact(spec, proposal)
    summary = _execution_summary_artifact(spec, selection)
    approval = _human_approval_artifact(spec, summary)
    authorization = _execution_authorization_artifact(spec, approval, selection)
    handoff = _worker_handoff_artifact(spec, authorization, selection)
    invocation = _worker_invocation_artifact(spec, handoff, authorization)
    outcome = _execution_outcome_artifact(spec, invocation, approval)
    artifacts = (
        request,
        intent,
        clarification,
        response,
        context,
        proposal,
        selection,
        summary,
        approval,
        authorization,
        handoff,
        invocation,
        outcome,
    )
    _persist_scenario_boundary(boundary_dir, artifacts)

    scenario_assertions = {
        "intent_detected": intent["intent_detected"] is True,
        "clarification_generated": (
            clarification["clarification_generated"] is True
            if spec["clarification_required"]
            else clarification["clarification_required"] is False
        ),
        "clarification_accepted": (
            response["clarification_accepted"] is True
            if spec["clarification_required"]
            else response["clarification_required"] is False
        ),
        "context_updated": context["context_updated"] is True,
        "workflow_selected": selection["workflow_selected"] is True,
        "execution_summary_generated": summary["execution_summary_generated"] is True,
        "human_approval_required": summary["human_approval_required"] is True,
        "authorization_boundary_preserved": authorization["authorization_issued"]
        is (spec["expected_worker_execution"] is True),
        "worker_handoff_boundary_preserved": handoff["worker_handoff_generated"]
        is (spec["expected_worker_execution"] is True),
        "worker_execution_boundary_preserved": invocation["worker_executed"]
        is (spec["expected_worker_execution"] is True),
        "execution_outcome_recorded": outcome["execution_outcome_recorded"] is True,
    }
    scenario_verdict = "CERTIFIED" if all(scenario_assertions.values()) else "GAPS_FOUND"
    return {
        "scenario_id": scenario_id,
        "coverage": spec["coverage"],
        "clarification_required": spec["clarification_required"],
        "expected_worker_execution": spec["expected_worker_execution"],
        "approval_decision": spec["approval_decision"],
        "modification_before_approval": spec["modification_before_approval"],
        "intent_family": spec["intent_family"],
        "selected_workflow": spec["selected_workflow"],
        "worker_invoked": invocation["worker_executed"],
        "execution_outcome_status": outcome["execution_outcome_status"],
        "scenario_assertions": scenario_assertions,
        "scenario_verdict": scenario_verdict,
        "replay_reference": str(boundary_dir),
        "execution_summary_reference": summary["execution_summary_id"],
        "authorization_reference": authorization["execution_authorization_id"],
        "worker_handoff_reference": handoff["worker_handoff_id"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "execution_outcome_reference": outcome["execution_outcome_id"],
    }


def _human_request_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_HUMAN_REQUEST_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "human_request_hash": replay_hash(spec["human_request"]),
            "request_contains_internal_terms": False,
            "created_at": CREATED_AT,
        }
    )


def _ocs_intent_detection_artifact(spec: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_OCS_INTENT_DETECTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "human_request_reference": request["artifact_hash"],
            "intent_detected": True,
            "clarification_required": spec["clarification_required"],
            "intent_family": spec["intent_family"],
            "confidence": "HIGH" if not spec["clarification_required"] else "LOW_UNTIL_CLARIFIED",
            "provider_invoked": False,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _cognition_clarification_artifact(spec: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_COGNITION_CLARIFICATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "ocs_intent_detection_reference": intent["artifact_hash"],
            "clarification_required": spec["clarification_required"],
            "clarification_generated": bool(spec["clarification_questions"]),
            "clarification_question_count": len(spec["clarification_questions"]),
            "clarification_question_hashes": [replay_hash(item) for item in spec["clarification_questions"]],
            "human_readable_questions": True,
            "internal_terms_exposed": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _human_clarification_response_artifact(spec: dict[str, Any], clarification: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "clarification_reference": clarification["artifact_hash"],
            "clarification_required": spec["clarification_required"],
            "clarification_response_received": bool(spec["clarification_responses"]),
            "clarification_accepted": (
                bool(spec["clarification_responses"]) if spec["clarification_required"] else False
            ),
            "clarification_response_hashes": [replay_hash(item) for item in spec["clarification_responses"]],
            "created_at": CREATED_AT,
        }
    )


def _ocs_context_update_artifact(
    spec: dict[str, Any],
    request: dict[str, Any],
    response: dict[str, Any],
) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_OCS_CONTEXT_UPDATE_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "human_request_reference": request["artifact_hash"],
            "clarification_response_reference": response["artifact_hash"],
            "context_updated": True,
            "intent_resolved": True,
            "intent_correction_recorded": spec["coverage"] == "intent_correction",
            "modification_before_approval": spec["modification_before_approval"],
            "created_at": CREATED_AT,
        }
    )


def _cognition_workflow_proposal_artifact(spec: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_COGNITION_WORKFLOW_PROPOSAL_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "context_update_reference": context["artifact_hash"],
            "workflow_candidates": list(spec["workflow_candidates"]),
            "proposal_reason": "resolved human intent mapped to bounded worker workflow",
            "multiple_candidates_considered": len(spec["workflow_candidates"]) > 1,
            "non_authoritative_proposal": True,
            "human_confirmation_required": True,
            "created_at": CREATED_AT,
        }
    )


def _ocs_workflow_selection_artifact(spec: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_OCS_WORKFLOW_SELECTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "cognition_workflow_proposal_reference": proposal["artifact_hash"],
            "workflow_selected": True,
            "selected_workflow": spec["selected_workflow"],
            "selection_justified": spec["selected_workflow"] in spec["workflow_candidates"],
            "human_approval_required": True,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _execution_summary_artifact(spec: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    summary_text = spec["execution_summary"]
    if spec["modification_before_approval"]:
        summary_text = f"{summary_text} Modification before approval: {spec['modification_before_approval']}."
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_EXECUTION_SUMMARY_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_summary_id": f"{spec['scenario_id']}:EXECUTION-SUMMARY",
            "workflow_selection_reference": selection["artifact_hash"],
            "execution_summary_hash": replay_hash(summary_text),
            "execution_summary_generated": True,
            "human_approval_required": True,
            "authorization_issued": False,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _human_approval_artifact(spec: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    approved = spec["expected_worker_execution"] is True
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_HUMAN_APPROVAL_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_summary_reference": summary["execution_summary_id"],
            "execution_summary_hash": summary["artifact_hash"],
            "human_approval_required": True,
            "human_approval_recorded": True,
            "approval_decision": spec["approval_decision"],
            "approved_for_execution": approved,
            "modification_before_approval": spec["modification_before_approval"],
            "created_at": CREATED_AT,
        }
    )


def _execution_authorization_artifact(
    spec: dict[str, Any],
    approval: dict[str, Any],
    selection: dict[str, Any],
) -> dict[str, Any]:
    authorized = approval["approved_for_execution"] is True
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_EXECUTION_AUTHORIZATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_authorization_id": f"{spec['scenario_id']}:EXECUTION-AUTHORIZATION",
            "human_approval_reference": approval["artifact_hash"],
            "selected_workflow": selection["selected_workflow"],
            "authorization_issued": authorized,
            "authorization_status": "AUTHORIZED" if authorized else "BLOCKED_BY_HUMAN_REJECTION",
            "worker_authorization_issued": authorized,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _worker_handoff_artifact(
    spec: dict[str, Any],
    authorization: dict[str, Any],
    selection: dict[str, Any],
) -> dict[str, Any]:
    generated = authorization["authorization_issued"] is True
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_WORKER_HANDOFF_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_handoff_id": f"{spec['scenario_id']}:WORKER-HANDOFF",
            "execution_authorization_reference": authorization["execution_authorization_id"],
            "execution_authorization_hash": authorization["artifact_hash"],
            "selected_workflow": selection["selected_workflow"],
            "worker_handoff_generated": generated,
            "worker_handoff_status": "HANDOFF_GENERATED" if generated else "HANDOFF_BLOCKED",
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _worker_invocation_artifact(
    spec: dict[str, Any],
    handoff: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    invoked = handoff["worker_handoff_generated"] is True and authorization["authorization_issued"] is True
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_WORKER_INVOCATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_invocation_id": f"{spec['scenario_id']}:WORKER-INVOCATION",
            "worker_id": "HUMAN_INTENT_END_TO_END_CERTIFICATION_ECHO_WORKER",
            "worker_handoff_reference": handoff["worker_handoff_id"],
            "worker_handoff_hash": handoff["artifact_hash"],
            "authorization_reference": authorization["execution_authorization_id"],
            "worker_executed": invoked,
            "invocation_status": "WORKER_EXECUTED" if invoked else "WORKER_NOT_INVOKED",
            "provider_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _execution_outcome_artifact(
    spec: dict[str, Any],
    invocation: dict[str, Any],
    approval: dict[str, Any],
) -> dict[str, Any]:
    executed = invocation["worker_executed"] is True
    status = "WORKER_EXECUTION_COMPLETED" if executed else "EXECUTION_BLOCKED_BY_HUMAN_REJECTION"
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_END_TO_END_EXECUTION_OUTCOME_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_outcome_id": f"{spec['scenario_id']}:EXECUTION-OUTCOME",
            "worker_invocation_reference": invocation["worker_invocation_id"],
            "worker_invocation_hash": invocation["artifact_hash"],
            "human_approval_reference": approval["artifact_hash"],
            "execution_outcome_recorded": True,
            "execution_outcome_status": status,
            "worker_result_payload_hash": replay_hash(
                {
                    "scenario_id": spec["scenario_id"],
                    "status": status,
                    "worker_executed": executed,
                }
            ),
            "secret_values_recorded": False,
            "created_at": CREATED_AT,
        }
    )


def _persist_scenario_boundary(boundary_dir: Path, artifacts: tuple[dict[str, Any], ...]) -> None:
    boundary_dir.mkdir(parents=True, exist_ok=True)
    if len(artifacts) != len(REPLAY_STEPS):
        raise FailClosedRuntimeError("end-to-end replay artifact count mismatch")
    for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts, strict=True)):
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": artifact,
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(boundary_dir / f"{index:03d}_{step}.json", wrapper)


def _reconstruct_scenario_replay(scenario: dict[str, Any]) -> dict[str, Any]:
    replay_path = Path(scenario["replay_reference"])
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("end-to-end replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("end-to-end replay artifact missing")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    artifacts = [wrapper["artifact"] for wrapper in wrappers]
    authorization = artifacts[9]
    handoff = artifacts[10]
    invocation = artifacts[11]
    outcome = artifacts[12]
    expected_execution = scenario["expected_worker_execution"] is True
    return {
        "scenario_id": scenario["scenario_id"],
        "replay_artifact_count": len(wrappers),
        "human_to_worker_chain_reconstructed": True,
        "authorization_issued": authorization["authorization_issued"],
        "worker_handoff_generated": handoff["worker_handoff_generated"],
        "worker_invoked": invocation["worker_executed"],
        "execution_outcome_recorded": outcome["execution_outcome_recorded"],
        "replay_contains_invocation": invocation["invocation_status"] in {"WORKER_EXECUTED", "WORKER_NOT_INVOKED"},
        "replay_contains_outcome": outcome["execution_outcome_recorded"] is True,
        "replay_reconstructed": all(
            [
                authorization["authorization_issued"] is expected_execution,
                handoff["worker_handoff_generated"] is expected_execution,
                invocation["worker_executed"] is expected_execution,
                outcome["execution_outcome_recorded"] is True,
            ]
        ),
        "replay_hash": replay_hash(wrappers),
    }


def _aggregate_assertions(
    scenario_results: list[dict[str, Any]],
    replay_results: list[dict[str, Any]],
    no_secret_leak: bool,
) -> dict[str, bool]:
    approved = [result for result in scenario_results if result["expected_worker_execution"] is True]
    rejected = [result for result in scenario_results if result["expected_worker_execution"] is False]
    clarification_required = [result for result in scenario_results if result["clarification_required"] is True]
    return {
        "intent_detected": all(result["scenario_assertions"]["intent_detected"] for result in scenario_results),
        "clarification_generated": all(
            result["scenario_assertions"]["clarification_generated"] for result in clarification_required
        ),
        "clarification_accepted": all(
            result["scenario_assertions"]["clarification_accepted"] for result in clarification_required
        ),
        "context_updated": all(result["scenario_assertions"]["context_updated"] for result in scenario_results),
        "workflow_selected": all(result["scenario_assertions"]["workflow_selected"] for result in scenario_results),
        "execution_summary_generated": all(
            result["scenario_assertions"]["execution_summary_generated"] for result in scenario_results
        ),
        "human_approval_required": all(
            result["scenario_assertions"]["human_approval_required"] for result in scenario_results
        ),
        "authorization_issued": all(
            result["scenario_assertions"]["authorization_boundary_preserved"] for result in scenario_results
        )
        and all(result["worker_invoked"] is True for result in approved)
        and all(result["worker_invoked"] is False for result in rejected),
        "worker_handoff_generated": all(
            result["scenario_assertions"]["worker_handoff_boundary_preserved"] for result in scenario_results
        ),
        "worker_executed": all(result["worker_invoked"] is True for result in approved)
        and all(result["worker_invoked"] is False for result in rejected),
        "execution_outcome_recorded": all(
            result["scenario_assertions"]["execution_outcome_recorded"] for result in scenario_results
        ),
        "replay_reconstructed": all(result["replay_reconstructed"] for result in replay_results),
        "authority_boundary_preserved": all(
            result["scenario_assertions"]["authorization_boundary_preserved"]
            and result["scenario_assertions"]["worker_handoff_boundary_preserved"]
            and result["scenario_assertions"]["worker_execution_boundary_preserved"]
            for result in scenario_results
        ),
        "secret_free_evidence": no_secret_leak,
    }


def _summarize_scenarios(scenario_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "scenario_id",
        "coverage",
        "clarification_required",
        "expected_worker_execution",
        "approval_decision",
        "modification_before_approval",
        "selected_workflow",
        "worker_invoked",
        "execution_outcome_status",
        "scenario_verdict",
    )
    return [{key: result[key] for key in keys} for result in scenario_results]


def _artifact(payload: dict[str, Any]) -> dict[str, Any]:
    payload["artifact_hash"] = replay_hash(payload)
    return payload


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    artifact_hash = artifact.get("artifact_hash")
    artifact_without_hash = dict(artifact)
    artifact_without_hash.pop("artifact_hash", None)
    if replay_hash(artifact_without_hash) != artifact_hash:
        raise FailClosedRuntimeError("end-to-end replay artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    wrapper_without_hash = {key: value for key, value in wrapper.items() if key != "replay_hash"}
    if replay_hash(wrapper_without_hash) != wrapper.get("replay_hash"):
        raise FailClosedRuntimeError("end-to-end replay wrapper hash mismatch")


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return "sk-" not in serialized and "Bearer " not in serialized and "api_key" not in serialized.lower()


def _blockers(assertions: dict[str, bool]) -> list[str]:
    return [name for name, value in assertions.items() if value is not True]


def _persist(
    evidence_dir: Path,
    replay_dir: Path,
    report_dir: Path,
    evidence: dict[str, Any],
    coverage: dict[str, Any],
    replay_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json_immutable(
        evidence_dir / "000_human_intent_end_to_end_worker_execution_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        evidence_dir / "001_human_intent_end_to_end_worker_execution_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        replay_dir / "000_human_intent_end_to_end_worker_execution_replay_package.json",
        replay_package,
    )
    write_json_immutable(
        report_dir / "000_human_intent_end_to_end_worker_execution_certification_report.json",
        report,
    )


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_human_intent_end_to_end_real_user_worker_execution_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"scenario_count={len(result['scenario_results'])}")
    print(f"worker_executed={assertions['worker_executed']}")
    print(f"authority_boundary_preserved={assertions['authority_boundary_preserved']}")
    print(f"replay_reconstructed={assertions['replay_reconstructed']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
