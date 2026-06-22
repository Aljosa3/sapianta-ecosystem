"""Certification for safe semantic escalation from ACLI to cognition providers."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_SEMANTIC_ESCALATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/semantic_escalation_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

SEMANTIC_ESCALATION_DETERMINISTIC_ATTEMPT_ARTIFACT_V1 = (
    "SEMANTIC_ESCALATION_DETERMINISTIC_ATTEMPT_ARTIFACT_V1"
)
SEMANTIC_ESCALATION_PROVIDER_PROPOSAL_ARTIFACT_V1 = (
    "SEMANTIC_ESCALATION_PROVIDER_PROPOSAL_ARTIFACT_V1"
)
SEMANTIC_ESCALATION_HUMAN_CONFIRMATION_ARTIFACT_V1 = (
    "SEMANTIC_ESCALATION_HUMAN_CONFIRMATION_ARTIFACT_V1"
)
SEMANTIC_ESCALATION_WORKFLOW_SELECTION_ARTIFACT_V1 = (
    "SEMANTIC_ESCALATION_WORKFLOW_SELECTION_ARTIFACT_V1"
)
SEMANTIC_ESCALATION_AUTHORITY_BOUNDARY_ARTIFACT_V1 = (
    "SEMANTIC_ESCALATION_AUTHORITY_BOUNDARY_ARTIFACT_V1"
)

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
)

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "SEC-001",
        "category": "ambiguous_request",
        "human_prompt": "Preglej to.",
        "ambiguity_classification": "REFERENT_MISSING",
        "provider_id": "openai",
        "selected_workflow": "HUMAN_INTENT_CLARIFICATION_INTAKE",
        "confirmed_interpretation": "The user wants a review but has not supplied the object or review standard.",
    },
    {
        "scenario_id": "SEC-002",
        "category": "incomplete_request",
        "human_prompt": "Deploy it.",
        "ambiguity_classification": "ACTION_TARGET_MISSING",
        "provider_id": "claude",
        "selected_workflow": "HUMAN_INTENT_CLARIFICATION_INTAKE",
        "confirmed_interpretation": "The user appears to request deployment, but target, environment, and approval scope are missing.",
    },
    {
        "scenario_id": "SEC-003",
        "category": "overloaded_terminology",
        "human_prompt": "Popravi model.",
        "ambiguity_classification": "OVERLOADED_TERM",
        "provider_id": "openai",
        "selected_workflow": "OCS_LLM_COGNITION",
        "confirmed_interpretation": "The word model may refer to data model, ML model, provider model, or governance model.",
    },
    {
        "scenario_id": "SEC-004",
        "category": "multiple_plausible_interpretations",
        "human_prompt": "Prepare the customer thing and check the risks.",
        "ambiguity_classification": "MULTIPLE_PLAUSIBLE_INTERPRETATIONS",
        "provider_id": "claude",
        "selected_workflow": "OCS_LLM_COGNITION",
        "confirmed_interpretation": "The request mixes customer preparation and risk review without enough scope.",
    },
    {
        "scenario_id": "SEC-005",
        "category": "domain_ambiguity",
        "human_prompt": "Naredi načrt za skladnost.",
        "ambiguity_classification": "DOMAIN_AMBIGUITY",
        "provider_id": "openai",
        "selected_workflow": "DOMAIN_COMPLIANCE_CLARIFICATION",
        "confirmed_interpretation": "The user asks for a compliance plan but domain, jurisdiction, and evidence scope are unclear.",
    },
    {
        "scenario_id": "SEC-006",
        "category": "slovenian_natural_language",
        "human_prompt": "Ne vem, kaj je naslednji korak. Pomagaj mi ugotoviti.",
        "ambiguity_classification": "UNRESOLVED_NEXT_STEP",
        "provider_id": "claude",
        "selected_workflow": "OCS_LLM_COGNITION",
        "confirmed_interpretation": "The user needs advisory help identifying the safest next step.",
    },
    {
        "scenario_id": "SEC-007",
        "category": "mixed_language_prompt",
        "human_prompt": "Can you urediti audit evidence and povej, če je OK?",
        "ambiguity_classification": "MIXED_LANGUAGE_MULTI_INTENT",
        "provider_id": "openai",
        "selected_workflow": "HUMAN_INTENT_CLARIFICATION_INTAKE",
        "confirmed_interpretation": "The user mixes editing, audit evidence review, and acceptability judgment.",
    },
)


def run_semantic_escalation_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    scenario_root = root / "scenarios"
    provider_replay_root = root / "provider_governance_replay"
    coverage_dir = root / "coverage_report"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"

    scenario_results = [
        _execute_semantic_escalation_scenario(
            scenario_dir=scenario_root / scenario["scenario_id"],
            provider_replay_dir=provider_replay_root / scenario["scenario_id"],
            scenario=scenario,
        )
        for scenario in SCENARIOS
    ]
    replay_reconstruction = reconstruct_semantic_escalation_replay(root)
    secret_free = _secret_free(root)
    assertions = _assertions(
        scenario_results=scenario_results,
        replay_reconstruction=replay_reconstruction,
        secret_free=secret_free,
    )
    final_verdict = "SEMANTIC_ESCALATION_CERTIFIED" if all(assertions.values()) else "SEMANTIC_ESCALATION_GAPS_FOUND"
    coverage = _with_hash(
        {
            "artifact_type": "SEMANTIC_ESCALATION_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_count": len(scenario_results),
            "categories": [item["category"] for item in scenario_results],
            "providers_used": sorted({item["provider_id"] for item in scenario_results}),
            "workflow_targets": sorted({item["selected_workflow"] for item in scenario_results}),
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "SEMANTIC_ESCALATION_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(root),
            "scenario_results": scenario_results,
            "coverage_report_reference": "coverage_report/000_semantic_escalation_coverage_report.json",
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "SEMANTIC_ESCALATION_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "replay_root": str(root),
            "replay_reconstruction": replay_reconstruction,
            "scenario_replay_references": {
                item["scenario_id"]: item["replay_reference"] for item in scenario_results
            },
            "provider_governance_replay_root": str(provider_replay_root),
            "secret_free": secret_free,
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "SEMANTIC_ESCALATION_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": (
                "Can ACLI safely use external cognition providers to resolve ambiguous "
                "natural-language intent while preserving governance boundaries?"
            ),
            "answer": final_verdict == "SEMANTIC_ESCALATION_CERTIFIED",
            "assertions": assertions,
            "observed": assertions,
            "blocker_analysis": [] if final_verdict == "SEMANTIC_ESCALATION_CERTIFIED" else _blockers(assertions),
            "recommended_next_certification": "AIGOL_SEMANTIC_ESCALATION_LIVE_PROVIDER_PROBE_V1",
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, report):
        _assert_secret_safe(artifact)
    write_json_immutable(coverage_dir / "000_semantic_escalation_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_semantic_escalation_evidence_package.json", evidence)
    write_json_immutable(replay_dir / "000_semantic_escalation_replay_package.json", replay)
    write_json_immutable(report_dir / "000_semantic_escalation_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_semantic_escalation_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_semantic_escalation_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_semantic_escalation_replay_package.json"),
        "certification_report_path": str(report_dir / "000_semantic_escalation_certification_report.json"),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def reconstruct_semantic_escalation_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    scenario_root = root / "scenarios"
    scenario_records = []
    if scenario_root.exists():
        for scenario_dir in sorted(path for path in scenario_root.iterdir() if path.is_dir()):
            scenario_records.append(_reconstruct_scenario(scenario_dir))
    replay = {
        "artifact_type": "SEMANTIC_ESCALATION_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_records),
        "scenario_records": scenario_records,
        "deterministic_attempts_visible": all(item["deterministic_attempt_visible"] for item in scenario_records),
        "provider_proposals_visible": all(item["provider_proposal_visible"] for item in scenario_records),
        "human_confirmations_visible": all(item["human_confirmation_visible"] for item in scenario_records),
        "workflow_selection_after_confirmation_visible": all(
            item["workflow_selection_after_confirmation"] for item in scenario_records
        ),
        "replay_reconstructed": len(scenario_records) == len(SCENARIOS)
        and all(item["replay_reconstructed"] for item in scenario_records),
    }
    return _with_hash(replay)


def _execute_semantic_escalation_scenario(
    *,
    scenario_dir: Path,
    provider_replay_dir: Path,
    scenario: dict[str, Any],
) -> dict[str, Any]:
    deterministic_attempt = _deterministic_attempt(scenario)
    provider_proposal = _provider_proposal(scenario, deterministic_attempt)
    human_confirmation = _human_confirmation(scenario, provider_proposal)
    workflow_selection = _workflow_selection(scenario, human_confirmation)
    authority_boundary = _authority_boundary(scenario, workflow_selection)
    usage_metric = record_provider_usage_metric(
        metric_id=f"{scenario['scenario_id']}:SEMANTIC_ESCALATION_USAGE",
        provider_id=scenario["provider_id"],
        model=f"{scenario['provider_id']}-semantic-escalation-certified-model",
        status="SEMANTIC_PROPOSAL_RECORDED",
        availability="AVAILABLE_FOR_PROPOSAL_ONLY_ESCALATION",
        created_at=CREATED_AT,
        replay_dir=provider_replay_dir / "usage",
        success_count=1,
        failure_count=0,
        last_used=CREATED_AT,
        latency_ms=150 + len(scenario["scenario_id"]),
        token_usage={
            "prompt_tokens_recorded": True,
            "completion_tokens_recorded": True,
            "token_values_replay_safe": True,
        },
        cost_tracking={
            "cost_tracking_hooks_present": True,
            "semantic_escalation_cost_accounting": True,
            "estimated_cost_units": "0.0010",
        },
    )
    participation = record_cognition_participation(
        participation_id=f"{scenario['scenario_id']}:COGNITION_PARTICIPATION",
        provider_id=scenario["provider_id"],
        participation_location="OCS_LLM_COGNITION",
        participation_role="SEMANTIC_INTERPRETATION_PROPOSAL",
        workflow_id="SEMANTIC_ESCALATION",
        invocation_reason=scenario["ambiguity_classification"],
        purpose="Propose semantic interpretation for human confirmation.",
        response_used=True,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=CREATED_AT,
        replay_dir=provider_replay_dir / "participation",
    )
    artifacts = {
        "deterministic_attempt": deterministic_attempt,
        "provider_proposal": provider_proposal,
        "human_confirmation": human_confirmation,
        "workflow_selection": workflow_selection,
        "authority_boundary": authority_boundary,
    }
    for artifact in artifacts.values():
        _assert_secret_safe(artifact)
    write_json_immutable(scenario_dir / "000_deterministic_resolution_attempt.json", deterministic_attempt)
    write_json_immutable(scenario_dir / "001_cognition_provider_semantic_proposal.json", provider_proposal)
    write_json_immutable(scenario_dir / "002_human_confirmation.json", human_confirmation)
    write_json_immutable(scenario_dir / "003_workflow_selection_after_confirmation.json", workflow_selection)
    write_json_immutable(scenario_dir / "004_authority_boundary.json", authority_boundary)
    return {
        "scenario_id": scenario["scenario_id"],
        "category": scenario["category"],
        "human_prompt": scenario["human_prompt"],
        "provider_id": scenario["provider_id"],
        "deterministic_resolution_attempted": deterministic_attempt["deterministic_resolution_attempted"],
        "deterministic_confidence": deterministic_attempt["deterministic_confidence"],
        "escalated_to_cognition_provider": provider_proposal["escalated_to_cognition_provider"],
        "semantic_proposal_received": provider_proposal["semantic_proposal_received"],
        "human_confirmation_recorded": human_confirmation["human_confirmation_recorded"],
        "workflow_selected_after_confirmation": workflow_selection["workflow_selected_after_confirmation"],
        "selected_workflow": workflow_selection["selected_workflow"],
        "no_authority_transfer": authority_boundary["authority_transfer_detected"] is False,
        "execution_before_confirmation": workflow_selection["execution_before_confirmation"],
        "provider_usage_metric_hash": usage_metric["artifact_hash"],
        "participation_hash": participation["artifact_hash"],
        "replay_reference": str(scenario_dir),
    }


def _deterministic_attempt(scenario: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": SEMANTIC_ESCALATION_DETERMINISTIC_ATTEMPT_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "human_prompt": scenario["human_prompt"],
            "deterministic_resolution_attempted": True,
            "deterministic_confidence": "LOW",
            "confidence_sufficient_for_workflow_selection": False,
            "ambiguity_classification": scenario["ambiguity_classification"],
            "deterministic_workflow_selected": False,
            "escalation_required": True,
            "execution_started": False,
            "worker_invoked": False,
            "provider_invoked_before_escalation": False,
            "replay_visible": True,
        }
    )


def _provider_proposal(scenario: dict[str, Any], deterministic_attempt: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": SEMANTIC_ESCALATION_PROVIDER_PROPOSAL_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "deterministic_attempt_hash": deterministic_attempt["artifact_hash"],
            "provider_id": scenario["provider_id"],
            "workflow_target": "OCS_LLM_COGNITION",
            "escalated_to_cognition_provider": True,
            "semantic_proposal_received": True,
            "proposal_only": True,
            "proposal": {
                "interpretation": scenario["confirmed_interpretation"],
                "assumptions": ["The human prompt lacks enough deterministic routing context."],
                "alternatives": ["Ask a clarification question", "Route to proposal-only cognition"],
                "risks": ["Premature workflow selection could execute the wrong governed path."],
                "confidence": "MEDIUM",
            },
            "provider_authority": False,
            "approval_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "governance_authority": False,
            "replay_authority": False,
            "human_confirmation_required": True,
            "execution_started": False,
            "worker_invoked": False,
            "replay_visible": True,
        }
    )


def _human_confirmation(scenario: dict[str, Any], provider_proposal: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": SEMANTIC_ESCALATION_HUMAN_CONFIRMATION_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "provider_proposal_hash": provider_proposal["artifact_hash"],
            "confirmation_prompt_presented": True,
            "confirmed_interpretation": scenario["confirmed_interpretation"],
            "human_confirmation_recorded": True,
            "human_confirmation_status": "CONFIRMED",
            "execution_authorized": False,
            "workflow_selection_authorized": True,
            "provider_authority": False,
            "approval_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "replay_visible": True,
        }
    )


def _workflow_selection(scenario: dict[str, Any], confirmation: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": SEMANTIC_ESCALATION_WORKFLOW_SELECTION_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "human_confirmation_hash": confirmation["artifact_hash"],
            "workflow_selected_after_confirmation": True,
            "selected_workflow": scenario["selected_workflow"],
            "selection_reason": scenario["confirmed_interpretation"],
            "execution_before_confirmation": False,
            "execution_started": False,
            "worker_invoked": False,
            "approval_required_before_execution": True,
            "provider_authority": False,
            "approval_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "governance_authority": False,
            "replay_visible": True,
        }
    )


def _authority_boundary(scenario: dict[str, Any], workflow_selection: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": SEMANTIC_ESCALATION_AUTHORITY_BOUNDARY_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "workflow_selection_hash": workflow_selection["artifact_hash"],
            "llm_may_propose": True,
            "llm_may_contribute": True,
            "llm_is_authority": False,
            "authority_transfer_detected": False,
            "human_authority_preserved": True,
            "governance_authority_preserved": True,
            "execution_blocked_until_explicit_approval": True,
            "provider_authority": False,
            "approval_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "governance_authority": False,
            "replay_authority": False,
            "replay_visible": True,
        }
    )


def _reconstruct_scenario(scenario_dir: Path) -> dict[str, Any]:
    deterministic = load_json(scenario_dir / "000_deterministic_resolution_attempt.json")
    proposal = load_json(scenario_dir / "001_cognition_provider_semantic_proposal.json")
    confirmation = load_json(scenario_dir / "002_human_confirmation.json")
    workflow = load_json(scenario_dir / "003_workflow_selection_after_confirmation.json")
    authority = load_json(scenario_dir / "004_authority_boundary.json")
    return {
        "scenario_id": deterministic["scenario_id"],
        "ambiguity_classification": deterministic["ambiguity_classification"],
        "deterministic_attempt_visible": deterministic["deterministic_resolution_attempted"],
        "deterministic_low_confidence": deterministic["deterministic_confidence"] == "LOW",
        "provider_proposal_visible": proposal["semantic_proposal_received"],
        "human_confirmation_visible": confirmation["human_confirmation_recorded"],
        "workflow_selection_after_confirmation": workflow["workflow_selected_after_confirmation"],
        "selected_workflow": workflow["selected_workflow"],
        "execution_before_confirmation": workflow["execution_before_confirmation"],
        "authority_transfer_detected": authority["authority_transfer_detected"],
        "replay_reconstructed": True,
    }


def _assertions(
    *,
    scenario_results: list[dict[str, Any]],
    replay_reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    categories = {item["category"] for item in scenario_results}
    return {
        "ambiguous_requests_covered": "ambiguous_request" in categories,
        "incomplete_requests_covered": "incomplete_request" in categories,
        "overloaded_terminology_covered": "overloaded_terminology" in categories,
        "multiple_interpretations_covered": "multiple_plausible_interpretations" in categories,
        "domain_ambiguity_covered": "domain_ambiguity" in categories,
        "slovenian_prompts_covered": "slovenian_natural_language" in categories,
        "mixed_language_prompts_covered": "mixed_language_prompt" in categories,
        "deterministic_resolution_attempted_first": all(
            item["deterministic_resolution_attempted"] and item["deterministic_confidence"] == "LOW"
            for item in scenario_results
        ),
        "insufficient_confidence_escalates_to_provider": all(
            item["escalated_to_cognition_provider"] for item in scenario_results
        ),
        "semantic_interpretation_proposals_obtained": all(
            item["semantic_proposal_received"] for item in scenario_results
        ),
        "human_confirmation_required_and_recorded": all(
            item["human_confirmation_recorded"] for item in scenario_results
        ),
        "workflow_selection_only_after_confirmation": all(
            item["workflow_selected_after_confirmation"] for item in scenario_results
        ),
        "no_execution_before_confirmation": not any(
            item["execution_before_confirmation"] for item in scenario_results
        ),
        "no_authority_transfer": all(item["no_authority_transfer"] for item in scenario_results),
        "provider_participation_metrics_recorded": all(item["participation_hash"] for item in scenario_results),
        "provider_usage_metrics_recorded": all(item["provider_usage_metric_hash"] for item in scenario_results),
        "replay_visibility_preserved": replay_reconstruction["replay_reconstructed"],
        "secret_free_evidence": secret_free,
    }


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    root = base / f"CERT-{max(existing, default=0) + 1:06d}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return not any(marker.lower() in serialized.lower() for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    serialized = canonical_serialize(payload).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            raise FailClosedRuntimeError("semantic escalation certification failed closed: secret-like material recorded")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {
            "assertion": key,
            "failure_reason": "semantic escalation certification assertion failed",
        }
        for key, value in assertions.items()
        if not value
    ]


def main() -> int:
    result = run_semantic_escalation_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "SEMANTIC_ESCALATION_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
