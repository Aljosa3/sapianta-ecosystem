"""Replay-safe hardening evidence runtime for completed ACLI interactions."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_HARDENING_RUNTIME_VERSION = "ACLI_HARDENING_RUNTIME_V1"
ACLI_HARDENING_EVIDENCE_ARTIFACT_V1 = "ACLI_HARDENING_EVIDENCE_ARTIFACT_V1"
HARDENING_REPLAY_STEP = "acli_hardening_evidence_recorded"

PASS = "PASS"
PARTIAL_PASS = "PARTIAL PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_lifecycle_modification": False,
    "creates_approval": False,
}

SCENARIO_CATALOG = {
    "HUMAN_TO_GOVERNANCE_TRANSLATION": "Human -> Governance Translation",
    "GOVERNANCE_TO_HUMAN_TRANSLATION": "Governance -> Human Translation",
    "HIRR": "HIRR",
    "ROUTING": "Routing",
    "PROPOSAL_GENERATION": "Proposal Generation",
    "PROPOSAL_PREVIEW": "Proposal Preview",
    "APPROVAL": "Approval",
    "REJECT": "Reject",
    "REQUEST_MODIFICATION": "Request Modification",
    "REPLAY": "Replay",
    "RESUME": "Resume",
    "EXPLANATION": "Explanation",
    "LLM_ASSISTED_EXPLANATION": "LLM-assisted Explanation",
    "PROVIDER_ESCALATION": "Provider Escalation",
    "WORKER_DISPATCH": "Worker Dispatch",
    "VALIDATION": "Validation",
    "ERR": "ERR",
    "REPLAY_REVIEW": "Replay Review",
}

ISSUE_CATEGORIES = {
    "UX",
    "ROUTING",
    "REPLAY",
    "APPROVAL",
    "TRANSLATION",
    "WORKER",
    "PROVIDER",
    "PERFORMANCE",
    "SECURITY",
    "DOCUMENTATION",
    "ARCHITECTURE",
    "VALIDATION",
    "ERR",
}


def record_acli_hardening_interaction(
    *,
    hardening_id: str,
    interaction_id: str,
    completed_interaction: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    operator_feedback: dict[str, Any] | None = None,
    prior_hardening_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record hardening evidence for one completed ACLI interaction.

    The runtime is passive: it observes supplied lifecycle evidence, records
    hardening artifacts, and never authorizes execution, approval, or mutation.
    """

    replay_path = Path(replay_dir)
    interaction = _require_mapping(completed_interaction, "completed_interaction")
    feedback = _normalize_operator_feedback(operator_feedback)
    _ensure_replay_available(replay_path)

    source_replay_reference = _find_replay_reference(interaction)
    replay_hash_value = _find_replay_hash(interaction)
    exercised_components = _detect_components(interaction)
    workflows = _detect_workflows(interaction)
    operator_journey = _detect_operator_journey(interaction)
    scenarios = _detect_scenarios(interaction, exercised_components, operator_journey)
    invariants = _detect_architectural_invariants(interaction, scenarios)
    contracts = _detect_contracts(interaction, scenarios)
    issues = _detect_issues(interaction, feedback, source_replay_reference)
    result = _classify_result(interaction, issues, source_replay_reference)
    state = _next_hardening_state(
        prior_hardening_state=prior_hardening_state,
        result=result,
        scenarios=scenarios,
        workflows=workflows,
        contracts=contracts,
        source_replay_reference=source_replay_reference,
        issues=issues,
        feedback=feedback,
    )
    dashboards = _build_dashboards(state)

    artifact = {
        "artifact_type": ACLI_HARDENING_EVIDENCE_ARTIFACT_V1,
        "runtime_version": ACLI_HARDENING_RUNTIME_VERSION,
        "hardening_id": _require_string(hardening_id, "hardening_id"),
        "interaction_id": _require_string(interaction_id, "interaction_id"),
        "created_at": _require_string(created_at, "created_at"),
        "result": result,
        "completed_interaction_hash": replay_hash(interaction),
        "source_replay_reference": source_replay_reference,
        "source_replay_hash": replay_hash_value,
        "workflows_executed": workflows,
        "runtime_path": _normalize_string_list(interaction.get("runtime_path")),
        "operator_journey": operator_journey,
        "exercised_components": exercised_components,
        "exercised_contracts": contracts,
        "architectural_invariants": invariants,
        "hardening_scenarios": scenarios,
        "new_hardening_scenario": _is_new_scenario(prior_hardening_state, scenarios),
        "operator_feedback_prompt": {
            "question": "Was everything understandable?",
            "choices": ["Very Clear", "Mostly Clear", "Somewhat Confusing", "Confusing"],
            "optional_free_text": True,
        },
        "operator_feedback": feedback,
        "issues": issues,
        "hardening_statistics": state["statistics"],
        "scenario_coverage": state["coverage"],
        "discovered_issues": state["discovered_issues"],
        "unresolved_issues": state["unresolved_issues"],
        "regression_history": state["regression_history"],
        "dashboards": dashboards,
        "production_readiness": state["production_readiness"],
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_artifact(replay_path, artifact)
    return _capture(artifact, replay_path)


def reconstruct_acli_hardening_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct ACLI hardening evidence and verify replay integrity."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{HARDENING_REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != HARDENING_REPLAY_STEP:
        raise FailClosedRuntimeError("ACLI hardening replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "hardening_artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ACLI_HARDENING_EVIDENCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI hardening artifact type mismatch")
    _verify_authority_flags(artifact)
    return {
        "runtime_version": artifact["runtime_version"],
        "hardening_id": artifact["hardening_id"],
        "interaction_id": artifact["interaction_id"],
        "result": artifact["result"],
        "source_replay_reference": artifact["source_replay_reference"],
        "source_replay_hash": artifact["source_replay_hash"],
        "hardening_scenarios": deepcopy(artifact["hardening_scenarios"]),
        "issues": deepcopy(artifact["issues"]),
        "hardening_statistics": deepcopy(artifact["hardening_statistics"]),
        "scenario_coverage": deepcopy(artifact["scenario_coverage"]),
        "dashboards": deepcopy(artifact["dashboards"]),
        "production_readiness": deepcopy(artifact["production_readiness"]),
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": wrapper["replay_hash"],
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(artifact["authority_flags"]),
    }


def render_platform_hardening_progress(capture: dict[str, Any]) -> str:
    """Render a compact operator-facing hardening dashboard."""

    dashboards = capture.get("dashboards") or {}
    progress = dashboards.get("platform_hardening_progress") or {}
    blockers = dashboards.get("remaining_production_blockers") or {}
    lines = [
        "Platform Hardening Progress",
        f"Result: {capture.get('result', UNKNOWN)}",
        f"Platform Core Hardening Score: {progress.get('platform_core_hardening_score', 0)}",
        f"Operator Experience Score: {progress.get('operator_experience_score', 0)}",
        f"Production Readiness Score: {progress.get('production_readiness_score', 0)}",
        f"Open Critical Issues: {blockers.get('open_critical_issues', 0)}",
        f"Production Blockers: {blockers.get('production_blockers', 0)}",
    ]
    return "\n".join(lines)


def _detect_components(interaction: dict[str, Any]) -> list[str]:
    components: set[str] = set()
    text = _search_text(interaction)
    if _has_any_token(text, ("translation", "universal_translation", "normalized_intent")):
        components.add("Universal Translation Runtime")
    if _has_any_token(text, ("hirr", "intent_family", "intent resolution")):
        components.add("HIRR")
    if _has_any_token(text, ("workflow", "routing", "selected_workflow")):
        components.add("Workflow Routing")
    if _truthy_key(interaction, "proposal_presented") or _contains_key(interaction, "proposal_hash") or _contains_key(interaction, "target_paths"):
        components.add("Proposal Runtime")
    if _truthy_key(interaction, "approval_required") or _field_status(
        interaction, "approval_status", {"APPROVED", "REJECTED", "MODIFICATION_REQUESTED", "PENDING"}
    ):
        components.add("Approval Runtime")
    if _has_any_token(text, ("explanation", "operator summary", "human_readable")):
        components.add("Explanation Runtime")
    if _truthy_key(interaction, "provider_invoked") or _truthy_key(interaction, "llm_assisted_explanation") or _contains_key(
        interaction, "provider_explanation"
    ):
        components.add("Cognition Provider Runtime")
    if (
        _truthy_key(interaction, "worker_invoked")
        or _truthy_key(interaction, "worker_dispatched")
        or _truthy_key(interaction, "worker_assigned")
        or _truthy_key(interaction, "repository_mutation_performed")
        or _field_status(interaction, "worker_status", {"DISPATCHED", "INVOKED", "EXECUTED"})
    ):
        components.add("Worker Runtime")
    if _truthy_key(interaction, "validated") or _truthy_key(interaction, "validation_executed") or _field_status(
        interaction, "validation_status", {"PASSED", "VALIDATED", "FAILED"}
    ):
        components.add("Validation Runtime")
    if _has_any_token(text, ("replay", "reconstruction", "replay_hash")):
        components.add("Replay Runtime")
    if _has_any_token(text, ("err", "resource")):
        components.add("ERR")
    return sorted(components)


def _detect_workflows(interaction: dict[str, Any]) -> list[str]:
    candidates = _collect_values_for_keys(
        interaction,
        {
            "workflow",
            "selected_workflow",
            "workflow_id",
            "workflow_name",
            "workflow_candidate",
        },
    )
    return sorted(set(_normalize_string_list(candidates)))


def _detect_operator_journey(interaction: dict[str, Any]) -> dict[str, Any]:
    text = _search_text(interaction)
    prompt = _first_string(interaction, ("prompt", "operator_prompt", "human_request", "request"))
    journey = {
        "prompt": prompt,
        "proposal_presented": _truthy_key(interaction, "proposal_presented")
        or _contains_key(interaction, "proposal_hash")
        or _contains_key(interaction, "target_paths"),
        "approval_required": _truthy_key(interaction, "approval_required"),
        "approved": _status_present(text, ("approved", "approve this proposal")),
        "rejected": _status_present(text, ("rejected", "reject")),
        "modification_requested": _status_present(text, ("modification_requested", "request_modification")),
        "executed": _truthy_key(interaction, "executed")
        or _truthy_key(interaction, "execution_performed")
        or _field_status(interaction, "execution_status", {"EXECUTED", "PERFORMED", "COMPLETED"}),
        "validated": _truthy_key(interaction, "validated")
        or _field_status(interaction, "validation_status", {"PASSED", "VALIDATED"}),
        "replay_recorded": bool(_find_replay_reference(interaction)),
        "resumed": _truthy_key(interaction, "resumed") or _truthy_key(interaction, "proposal_restored"),
        "clarification_required": _truthy_key(interaction, "clarification_required")
        or _field_status(interaction, "response_status", {"CLARIFICATION_REQUIRED"}),
    }
    journey["completed"] = any(
        journey[key]
        for key in (
            "approved",
            "rejected",
            "modification_requested",
            "executed",
            "validated",
            "clarification_required",
        )
    )
    return journey


def _detect_scenarios(
    interaction: dict[str, Any],
    components: list[str],
    operator_journey: dict[str, Any],
) -> list[dict[str, Any]]:
    text = _search_text(interaction)
    scenarios: list[dict[str, Any]] = []

    def add(scenario_id: str) -> None:
        if scenario_id in SCENARIO_CATALOG:
            scenarios.append(
                {
                    "scenario_id": scenario_id,
                    "name": SCENARIO_CATALOG[scenario_id],
                }
            )

    if "Universal Translation Runtime" in components or "normalized_intent" in text:
        add("HUMAN_TO_GOVERNANCE_TRANSLATION")
    if _has_any_token(text, ("human_readable_payload", "operator explanation", "what i understood")):
        add("GOVERNANCE_TO_HUMAN_TRANSLATION")
    if "HIRR" in components:
        add("HIRR")
    if "Workflow Routing" in components:
        add("ROUTING")
    if operator_journey["proposal_presented"]:
        add("PROPOSAL_GENERATION")
    if _has_any_token(text, ("proposal_preview", "target_paths", "target path")):
        add("PROPOSAL_PREVIEW")
    if operator_journey["approved"]:
        add("APPROVAL")
    if operator_journey["rejected"]:
        add("REJECT")
    if operator_journey["modification_requested"]:
        add("REQUEST_MODIFICATION")
    if operator_journey["replay_recorded"]:
        add("REPLAY")
    if operator_journey["resumed"]:
        add("RESUME")
    if "Explanation Runtime" in components:
        add("EXPLANATION")
    if _has_any_token(text, ("llm_assisted", "provider_explanation", "explanation_provider")):
        add("LLM_ASSISTED_EXPLANATION")
    if _has_any_token(text, ("provider_escalation", "escalation_stage", "provider_tier")):
        add("PROVIDER_ESCALATION")
    if "Worker Runtime" in components:
        add("WORKER_DISPATCH")
    if "Validation Runtime" in components:
        add("VALIDATION")
    if "ERR" in components:
        add("ERR")
    if _has_any_token(text, ("replay review", "replay_review", "reconstruct")):
        add("REPLAY_REVIEW")

    if not scenarios:
        scenarios.append({"scenario_id": "UNKNOWN", "name": "Unknown hardening scenario"})
    return _dedupe_scenarios(scenarios)


def _detect_architectural_invariants(interaction: dict[str, Any], scenarios: list[dict[str, Any]]) -> list[str]:
    invariants = {
        "Human remains authority",
        "Replay remains source of truth",
        "Runtime hardening evidence is read-only",
    }
    text = _search_text(interaction)
    scenario_ids = {scenario["scenario_id"] for scenario in scenarios}
    if "LLM_ASSISTED_EXPLANATION" in scenario_ids or "PROVIDER_ESCALATION" in scenario_ids:
        invariants.add("Provider output remains non-authoritative")
    if "WORKER_DISPATCH" in scenario_ids:
        invariants.add("Worker executes only after governed authorization")
    if "APPROVAL" in scenario_ids or "REJECT" in scenario_ids or "REQUEST_MODIFICATION" in scenario_ids:
        invariants.add("Approval boundary is explicit")
    if _truthy_key(interaction, "fail_closed") or _field_status(interaction, "response_status", {"FAILED_CLOSED"}):
        invariants.add("Fail-closed behavior is preserved")
    if _has_any_token(text, ("translation", "normalized_intent")):
        invariants.add("Translation never authorizes execution")
    return sorted(invariants)


def _detect_contracts(interaction: dict[str, Any], scenarios: list[dict[str, Any]]) -> list[str]:
    contracts: set[str] = set()
    scenario_ids = {scenario["scenario_id"] for scenario in scenarios}
    mapping = {
        "HUMAN_TO_GOVERNANCE_TRANSLATION": "Human -> Governance Translation Contract",
        "GOVERNANCE_TO_HUMAN_TRANSLATION": "Governance -> Human Translation Contract",
        "HIRR": "Human Intent Resolution Contract",
        "ROUTING": "ACLI Workflow Routing Contract",
        "PROPOSAL_GENERATION": "Proposal Contract",
        "APPROVAL": "Approval Contract",
        "REJECT": "Approval Contract",
        "REQUEST_MODIFICATION": "Approval Contract",
        "REPLAY": "Replay Contract",
        "EXPLANATION": "Explanation Contract",
        "LLM_ASSISTED_EXPLANATION": "Explanation Provider Contract",
        "PROVIDER_ESCALATION": "Cognition Provider Contract",
        "WORKER_DISPATCH": "Worker Contract",
        "VALIDATION": "Validation Contract",
        "ERR": "ERR Evidence Contract",
    }
    for scenario_id, contract in mapping.items():
        if scenario_id in scenario_ids:
            contracts.add(contract)
    explicit = _collect_values_for_keys(interaction, {"contract", "contracts", "exercised_contracts"})
    contracts.update(_normalize_string_list(explicit))
    return sorted(contracts)


def _detect_issues(
    interaction: dict[str, Any],
    feedback: dict[str, Any],
    source_replay_reference: str | None,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    text = _search_text(interaction)
    executed = _truthy_key(interaction, "executed") or _truthy_key(interaction, "execution_performed")
    approval_required = _truthy_key(interaction, "approval_required") or "approval_required" in text
    approved = _status_present(text, ("approved", "approve this proposal"))

    if _truthy_key(interaction, "authority_violation") or _truthy_key(interaction, "provider_authority_claim"):
        issues.append(_issue("SECURITY", "P0", "authority_boundary_violation", source_replay_reference))
    if executed and approval_required and not approved:
        issues.append(_issue("APPROVAL", "P0", "execution_without_approval", source_replay_reference))
    if executed and not source_replay_reference:
        issues.append(_issue("REPLAY", "P0", "execution_missing_replay_reference", source_replay_reference))
    if _truthy_key(interaction, "approval_bypassed"):
        issues.append(_issue("APPROVAL", "P0", "approval_bypass_detected", source_replay_reference))
    if _truthy_key(interaction, "tampered") or _has_any_token(text, ("hash mismatch", "replay corruption")):
        issues.append(_issue("REPLAY", "P0", "replay_integrity_failure", source_replay_reference))

    if _truthy_key(interaction, "provider_unavailable") or _field_status(
        interaction, "provider_status", {"PROVIDER_UNAVAILABLE", "UNAVAILABLE"}
    ):
        issues.append(_issue("PROVIDER", "P1", "provider_unavailable", source_replay_reference))
    if _truthy_key(interaction, "worker_unavailable") or _field_status(
        interaction, "worker_status", {"WORKER_UNAVAILABLE", "UNAVAILABLE"}
    ):
        issues.append(_issue("WORKER", "P1", "worker_unavailable", source_replay_reference))
    if _truthy_key(interaction, "validation_failed") or _field_status(interaction, "validation_status", {"FAILED"}):
        issues.append(_issue("VALIDATION", "P1", "validation_failed", source_replay_reference))
    if (
        _truthy_key(interaction, "clarification_required")
        or _field_status(interaction, "response_status", {"CLARIFICATION_REQUIRED"})
        or _field_status(interaction, "intent_family", {"AMBIGUOUS_INTENT"})
    ):
        issues.append(_issue("ROUTING", "P1", "clarification_or_ambiguity_required", source_replay_reference))
    if _truthy_key(interaction, "fail_closed") or _field_status(interaction, "response_status", {"FAILED_CLOSED"}):
        issues.append(_issue("ARCHITECTURE", "P1", "fail_closed_path_exercised", source_replay_reference))

    clarity = str(feedback.get("clarity") or "").strip().lower()
    if clarity in {"somewhat confusing", "confusing"} or feedback.get("free_text"):
        issues.append(_issue("UX", "P2", "operator_feedback_requires_review", source_replay_reference))
    return _dedupe_issues(issues)


def _classify_result(interaction: dict[str, Any], issues: list[dict[str, Any]], source_replay_reference: str | None) -> str:
    if any(issue["severity"] == "P0" for issue in issues):
        return FAIL
    if any(issue["severity"] == "P1" for issue in issues):
        return PARTIAL_PASS
    if _status_present(_search_text(interaction), ("unknown", "incomplete")):
        return UNKNOWN
    if source_replay_reference or not issues:
        return PASS
    return UNKNOWN


def _next_hardening_state(
    *,
    prior_hardening_state: dict[str, Any] | None,
    result: str,
    scenarios: list[dict[str, Any]],
    workflows: list[str],
    contracts: list[str],
    source_replay_reference: str | None,
    issues: list[dict[str, Any]],
    feedback: dict[str, Any],
) -> dict[str, Any]:
    prior = _normalize_prior_state(prior_hardening_state)
    stats = deepcopy(prior["statistics"])
    stats["total_interactions"] += 1
    stats["result_counts"][result] = stats["result_counts"].get(result, 0) + 1
    if source_replay_reference:
        stats["interactions_with_replay"] += 1
    if feedback["feedback_provided"]:
        stats["operator_feedback_count"] += 1

    coverage = deepcopy(prior["coverage"])
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        if scenario_id != "UNKNOWN":
            coverage["covered_scenarios"][scenario_id] = coverage["covered_scenarios"].get(scenario_id, 0) + 1
    for workflow in workflows:
        coverage["covered_workflows"][workflow] = coverage["covered_workflows"].get(workflow, 0) + 1
    for contract in contracts:
        coverage["covered_contracts"][contract] = coverage["covered_contracts"].get(contract, 0) + 1
    _recalculate_coverage(coverage)

    discovered_issues = deepcopy(prior["discovered_issues"]) + deepcopy(issues)
    unresolved_issues = [issue for issue in discovered_issues if issue.get("fix_status") != "CLOSED"]
    regression_history = deepcopy(prior["regression_history"])
    for issue in issues:
        if issue["regression_status"] == "MISSING":
            regression_history.append(
                {
                    "issue_id": issue["issue_id"],
                    "regression_identifier": issue["regression_identifier"],
                    "regression_status": "REQUIRED",
                    "closure_blocked_without_regression_evidence": True,
                }
            )
    production_readiness = _production_readiness(stats, coverage, unresolved_issues)
    return {
        "statistics": stats,
        "coverage": coverage,
        "discovered_issues": discovered_issues,
        "unresolved_issues": unresolved_issues,
        "regression_history": regression_history,
        "production_readiness": production_readiness,
    }


def _build_dashboards(state: dict[str, Any]) -> dict[str, Any]:
    stats = state["statistics"]
    coverage = state["coverage"]
    readiness = state["production_readiness"]
    unresolved = state["unresolved_issues"]
    problems = Counter(issue["category"] for issue in unresolved)
    blockers = [issue for issue in unresolved if issue["severity"] in {"P0", "P1"}]
    return {
        "platform_hardening_progress": {
            "total_interactions": stats["total_interactions"],
            "pass_count": stats["result_counts"].get(PASS, 0),
            "partial_pass_count": stats["result_counts"].get(PARTIAL_PASS, 0),
            "fail_count": stats["result_counts"].get(FAIL, 0),
            "unknown_count": stats["result_counts"].get(UNKNOWN, 0),
            "platform_core_hardening_score": readiness["platform_core_hardening_score"],
            "operator_experience_score": readiness["operator_experience_score"],
            "production_readiness_score": readiness["production_readiness_score"],
        },
        "scenario_coverage": {
            "scenario_coverage_percent": coverage["scenario_coverage_percent"],
            "workflow_coverage_percent": coverage["workflow_coverage_percent"],
            "contract_coverage_percent": coverage["contract_coverage_percent"],
            "replay_coverage_percent": coverage["replay_coverage_percent"],
            "translation_coverage_percent": coverage["translation_coverage_percent"],
            "approval_coverage_percent": coverage["approval_coverage_percent"],
            "provider_coverage_percent": coverage["provider_coverage_percent"],
            "worker_coverage_percent": coverage["worker_coverage_percent"],
            "regression_coverage_percent": coverage["regression_coverage_percent"],
            "generation1_coverage_percent": coverage["generation1_coverage_percent"],
            "uncovered_scenarios": coverage["uncovered_scenarios"],
        },
        "most_frequent_operator_problems": [
            {"category": category, "count": count} for category, count in problems.most_common()
        ],
        "remaining_production_blockers": {
            "open_critical_issues": sum(1 for issue in unresolved if issue["severity"] == "P0"),
            "open_major_issues": sum(1 for issue in unresolved if issue["severity"] == "P1"),
            "open_minor_issues": sum(1 for issue in unresolved if issue["severity"] in {"P2", "P3"}),
            "production_blockers": len(blockers),
            "blocker_issue_ids": [issue["issue_id"] for issue in blockers],
        },
    }


def _production_readiness(
    stats: dict[str, Any],
    coverage: dict[str, Any],
    unresolved_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    p0 = sum(1 for issue in unresolved_issues if issue["severity"] == "P0")
    p1 = sum(1 for issue in unresolved_issues if issue["severity"] == "P1")
    p2 = sum(1 for issue in unresolved_issues if issue["severity"] in {"P2", "P3"})
    total = max(1, int(stats["total_interactions"]))
    pass_ratio = stats["result_counts"].get(PASS, 0) / total
    replay_ratio = stats["interactions_with_replay"] / total
    platform_score = _bounded_score((pass_ratio * 70) + (coverage["generation1_coverage_percent"] * 0.2) + (replay_ratio * 10))
    operator_score = _bounded_score(100 - (p2 * 5) - (p1 * 10) - (p0 * 30))
    readiness_score = _bounded_score(
        (platform_score * 0.45)
        + (operator_score * 0.25)
        + (coverage["generation1_coverage_percent"] * 0.30)
        - (p0 * 35)
        - (p1 * 10)
    )
    return {
        "platform_core_hardening_score": platform_score,
        "operator_experience_score": operator_score,
        "production_readiness_score": readiness_score,
        "open_critical_issues": p0,
        "open_major_issues": p1,
        "open_minor_issues": p2,
        "production_blockers": p0 + p1,
    }


def _normalize_prior_state(prior_hardening_state: dict[str, Any] | None) -> dict[str, Any]:
    if prior_hardening_state is not None and not isinstance(prior_hardening_state, dict):
        raise FailClosedRuntimeError("prior_hardening_state must be a JSON object")
    prior = deepcopy(prior_hardening_state or {})
    statistics = prior.get("hardening_statistics") or prior.get("statistics") or {}
    coverage = prior.get("scenario_coverage") or prior.get("coverage") or {}
    return {
        "statistics": {
            "total_interactions": int(statistics.get("total_interactions", 0)),
            "result_counts": dict(statistics.get("result_counts", {})),
            "interactions_with_replay": int(statistics.get("interactions_with_replay", 0)),
            "operator_feedback_count": int(statistics.get("operator_feedback_count", 0)),
        },
        "coverage": {
            "covered_scenarios": dict(coverage.get("covered_scenarios", {})),
            "covered_workflows": dict(coverage.get("covered_workflows", {})),
            "covered_contracts": dict(coverage.get("covered_contracts", {})),
            "uncovered_scenarios": list(coverage.get("uncovered_scenarios", sorted(SCENARIO_CATALOG))),
            "scenario_coverage_percent": int(coverage.get("scenario_coverage_percent", 0)),
            "workflow_coverage_percent": int(coverage.get("workflow_coverage_percent", 0)),
            "contract_coverage_percent": int(coverage.get("contract_coverage_percent", 0)),
            "replay_coverage_percent": int(coverage.get("replay_coverage_percent", 0)),
            "translation_coverage_percent": int(coverage.get("translation_coverage_percent", 0)),
            "approval_coverage_percent": int(coverage.get("approval_coverage_percent", 0)),
            "provider_coverage_percent": int(coverage.get("provider_coverage_percent", 0)),
            "worker_coverage_percent": int(coverage.get("worker_coverage_percent", 0)),
            "regression_coverage_percent": int(coverage.get("regression_coverage_percent", 0)),
            "generation1_coverage_percent": int(coverage.get("generation1_coverage_percent", 0)),
        },
        "discovered_issues": list(prior.get("discovered_issues", [])),
        "unresolved_issues": list(prior.get("unresolved_issues", [])),
        "regression_history": list(prior.get("regression_history", [])),
    }


def _recalculate_coverage(coverage: dict[str, Any]) -> None:
    covered_scenarios = set(coverage["covered_scenarios"])
    covered_contracts = set(coverage["covered_contracts"])
    coverage["uncovered_scenarios"] = sorted(set(SCENARIO_CATALOG) - covered_scenarios)
    coverage["scenario_coverage_percent"] = _percent(len(covered_scenarios), len(SCENARIO_CATALOG))
    coverage["workflow_coverage_percent"] = 100 if coverage["covered_workflows"] else 0
    coverage["contract_coverage_percent"] = _percent(len(covered_contracts), 9)
    coverage["replay_coverage_percent"] = 100 if "REPLAY" in covered_scenarios else 0
    coverage["translation_coverage_percent"] = _percent(
        len(covered_scenarios & {"HUMAN_TO_GOVERNANCE_TRANSLATION", "GOVERNANCE_TO_HUMAN_TRANSLATION"}),
        2,
    )
    coverage["approval_coverage_percent"] = _percent(
        len(covered_scenarios & {"APPROVAL", "REJECT", "REQUEST_MODIFICATION"}),
        3,
    )
    coverage["provider_coverage_percent"] = _percent(
        len(covered_scenarios & {"LLM_ASSISTED_EXPLANATION", "PROVIDER_ESCALATION"}),
        2,
    )
    coverage["worker_coverage_percent"] = 100 if "WORKER_DISPATCH" in covered_scenarios else 0
    coverage["regression_coverage_percent"] = 0
    component_scores = [
        coverage["scenario_coverage_percent"],
        coverage["workflow_coverage_percent"],
        coverage["contract_coverage_percent"],
        coverage["replay_coverage_percent"],
        coverage["translation_coverage_percent"],
        coverage["approval_coverage_percent"],
        coverage["provider_coverage_percent"],
        coverage["worker_coverage_percent"],
    ]
    coverage["generation1_coverage_percent"] = int(round(sum(component_scores) / len(component_scores)))


def _issue(category: str, severity: str, kind: str, replay_reference: str | None) -> dict[str, Any]:
    issue_id = f"HARDENING-{severity}-{category}-{replay_hash({'kind': kind, 'replay': replay_reference})[-12:]}"
    return {
        "issue_id": issue_id,
        "category": category,
        "severity": severity,
        "kind": kind,
        "replay_reference": replay_reference,
        "root_cause_status": "UNKNOWN",
        "fix_status": "OPEN",
        "regression_status": "MISSING",
        "regression_identifier": f"REGRESSION-{issue_id}",
        "closure_blocked_without_regression_evidence": True,
    }


def _dedupe_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for issue in issues:
        if issue["issue_id"] in seen:
            continue
        seen.add(issue["issue_id"])
        deduped.append(issue)
    return deduped


def _dedupe_scenarios(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for scenario in scenarios:
        if scenario["scenario_id"] in seen:
            continue
        seen.add(scenario["scenario_id"])
        deduped.append(scenario)
    return deduped


def _normalize_operator_feedback(operator_feedback: dict[str, Any] | None) -> dict[str, Any]:
    if operator_feedback is None:
        return {
            "feedback_requested": True,
            "feedback_provided": False,
            "clarity": None,
            "free_text": None,
        }
    feedback = _require_mapping(operator_feedback, "operator_feedback")
    clarity = feedback.get("clarity")
    if clarity is not None and str(clarity) not in {"Very Clear", "Mostly Clear", "Somewhat Confusing", "Confusing"}:
        raise FailClosedRuntimeError("operator feedback clarity choice is invalid")
    return {
        "feedback_requested": True,
        "feedback_provided": True,
        "clarity": clarity,
        "free_text": feedback.get("free_text"),
    }


def _find_replay_reference(value: Any) -> str | None:
    for key in (
        "replay_reference",
        "source_replay_reference",
        "conversational_cli_routing_replay_reference",
        "operator_summary_replay_reference",
        "approval_replay_reference",
        "execution_replay_reference",
    ):
        found = _first_string(value, (key,))
        if found:
            return found
    return None


def _find_replay_hash(value: Any) -> str | None:
    for key in ("replay_hash", "source_replay_hash", "artifact_hash"):
        found = _first_string(value, (key,))
        if found and found.startswith("sha256:"):
            return found
    return None


def _collect_values_for_keys(value: Any, keys: set[str]) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                if isinstance(item, list):
                    found.extend(item)
                else:
                    found.append(item)
            found.extend(_collect_values_for_keys(item, keys))
    elif isinstance(value, list):
        for item in value:
            found.extend(_collect_values_for_keys(item, keys))
    return found


def _first_string(value: Any, keys: tuple[str, ...]) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, str) and item.strip():
                return item.strip()
            found = _first_string(item, keys)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _first_string(item, keys)
            if found:
                return found
    return None


def _truthy_key(value: Any, key_name: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == key_name and item is True:
                return True
            if _truthy_key(item, key_name):
                return True
    elif isinstance(value, list):
        return any(_truthy_key(item, key_name) for item in value)
    return False


def _field_status(value: Any, key_name: str, statuses: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == key_name and isinstance(item, str) and item.strip().upper() in statuses:
                return True
            if _field_status(item, key_name, statuses):
                return True
    elif isinstance(value, list):
        return any(_field_status(item, key_name, statuses) for item in value)
    return False


def _contains_key(value: Any, key_name: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == key_name:
                return True
            if _contains_key(item, key_name):
                return True
    elif isinstance(value, list):
        return any(_contains_key(item, key_name) for item in value)
    return False


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result
    return []


def _search_text(value: Any) -> str:
    if isinstance(value, dict):
        parts: list[str] = []
        for key, item in value.items():
            parts.append(str(key))
            parts.append(_search_text(item))
        return " ".join(parts).lower()
    if isinstance(value, list):
        return " ".join(_search_text(item) for item in value).lower()
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, bool):
        return str(value).lower()
    return ""


def _has_any_token(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token.lower() in text for token in tokens)


def _status_present(text: str, statuses: tuple[str, ...]) -> bool:
    return any(status.lower() in text for status in statuses)


def _is_new_scenario(prior_hardening_state: dict[str, Any] | None, scenarios: list[dict[str, Any]]) -> bool:
    prior = _normalize_prior_state(prior_hardening_state)
    covered = set(prior["coverage"]["covered_scenarios"])
    return any(scenario["scenario_id"] not in covered and scenario["scenario_id"] != "UNKNOWN" for scenario in scenarios)


def _bounded_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _percent(count: int, total: int) -> int:
    if total <= 0:
        return 0
    return _bounded_score((count / total) * 100)


def _persist_artifact(replay_dir: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": HARDENING_REPLAY_STEP,
        "event_type": ACLI_HARDENING_RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"000_{HARDENING_REPLAY_STEP}.json", wrapper)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": ACLI_HARDENING_RUNTIME_VERSION,
        "hardening_id": artifact["hardening_id"],
        "interaction_id": artifact["interaction_id"],
        "result": artifact["result"],
        "source_replay_reference": artifact["source_replay_reference"],
        "source_replay_hash": artifact["source_replay_hash"],
        "hardening_scenarios": deepcopy(artifact["hardening_scenarios"]),
        "workflows_executed": deepcopy(artifact["workflows_executed"]),
        "operator_journey": deepcopy(artifact["operator_journey"]),
        "issues": deepcopy(artifact["issues"]),
        "hardening_statistics": deepcopy(artifact["hardening_statistics"]),
        "scenario_coverage": deepcopy(artifact["scenario_coverage"]),
        "discovered_issues": deepcopy(artifact["discovered_issues"]),
        "unresolved_issues": deepcopy(artifact["unresolved_issues"]),
        "regression_history": deepcopy(artifact["regression_history"]),
        "dashboards": deepcopy(artifact["dashboards"]),
        "production_readiness": deepcopy(artifact["production_readiness"]),
        "operator_feedback_prompt": deepcopy(artifact["operator_feedback_prompt"]),
        "operator_feedback": deepcopy(artifact["operator_feedback"]),
        "hardening_artifact": deepcopy(artifact),
        "hardening_replay_reference": str(replay_path),
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["hardening_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{HARDENING_REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("ACLI hardening replay artifact already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual:
        raise FailClosedRuntimeError("ACLI hardening artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("ACLI hardening artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual:
        raise FailClosedRuntimeError("ACLI hardening replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("ACLI hardening replay hash mismatch")


def _verify_authority_flags(artifact: dict[str, Any]) -> None:
    if artifact.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("ACLI hardening authority flags mismatch")
    for key in ("approval_created", "execution_authorized", "worker_invoked", "governance_mutated", "replay_mutated"):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError("ACLI hardening artifact attempted authority")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    replay_hash(value)
    return deepcopy(value)


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


__all__ = [
    "ACLI_HARDENING_EVIDENCE_ARTIFACT_V1",
    "ACLI_HARDENING_RUNTIME_VERSION",
    "FAIL",
    "HARDENING_REPLAY_STEP",
    "PARTIAL_PASS",
    "PASS",
    "UNKNOWN",
    "record_acli_hardening_interaction",
    "reconstruct_acli_hardening_replay",
    "render_platform_hardening_progress",
]
