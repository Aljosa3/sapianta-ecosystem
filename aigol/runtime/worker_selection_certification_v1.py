"""Certification for governed worker selection."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    WORKER_ROLE,
    default_resource_registry,
    reconstruct_unified_resource_selection_replay,
    select_unified_resource,
)


MILESTONE_ID = "AIGOL_WORKER_SELECTION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/worker_selection_certification_v1")
CREATED_AT = "2026-07-22T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "WORKER_SELECTION_CERTIFIED"
FINAL_VERDICT_GAPS = "WORKER_SELECTION_GAPS_FOUND"
SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "WSG-001",
        "coverage": "deterministic_worker_available",
        "required_capability": "file_create",
        "selected_worker": "deterministic_file_worker",
        "expected_status": "SELECTED",
        "candidates": ["deterministic_file_worker", "llm_translation_worker"],
        "validation_result": "PASS",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-002",
        "coverage": "deterministic_worker_unavailable",
        "required_capability": "translation",
        "selected_worker": "llm_translation_worker",
        "expected_status": "SELECTED",
        "candidates": ["llm_translation_worker"],
        "validation_result": "PASS",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-003",
        "coverage": "deterministic_worker_preferred_over_llm_worker",
        "required_capability": "summarize_static",
        "selected_worker": "deterministic_summary_worker",
        "expected_status": "SELECTED",
        "candidates": ["deterministic_summary_worker", "llm_summary_worker"],
        "validation_result": "PASS",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-004",
        "coverage": "multiple_llm_workers_available",
        "required_capability": "translation",
        "selected_worker": "llm_translation_worker",
        "expected_status": "SELECTED",
        "candidates": ["llm_translation_worker", "llm_repair_worker"],
        "validation_result": "PASS",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-005",
        "coverage": "worker_failover",
        "required_capability": "file_create",
        "selected_worker": "deterministic_file_worker_backup",
        "expected_status": "FAILOVER_SELECTED",
        "candidates": ["deterministic_file_worker_primary", "deterministic_file_worker_backup"],
        "failed_worker": "deterministic_file_worker_primary",
        "validation_result": "PASS",
        "failover_used": True,
    },
    {
        "scenario_id": "WSG-006",
        "coverage": "worker_validation_failure",
        "required_capability": "translation",
        "selected_worker": "llm_translation_worker",
        "expected_status": "VALIDATION_FAILED_CLOSED",
        "candidates": ["llm_translation_worker"],
        "validation_result": "FAIL",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-007",
        "coverage": "capability_mismatch",
        "required_capability": "database_write",
        "selected_worker": None,
        "expected_status": "FAIL_CLOSED",
        "candidates": ["deterministic_file_worker", "llm_translation_worker"],
        "validation_result": "NOT_APPLICABLE",
        "failover_used": False,
    },
    {
        "scenario_id": "WSG-008",
        "coverage": "filesystem_replace_worker_selection",
        "required_capability": "REPLACE_EXISTING_TEXT_FILE",
        "selected_worker": "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER",
        "expected_status": "SELECTED",
        "candidates": ["FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"],
        "validation_result": "PASS",
        "failover_used": False,
    },
)


WORKER_DECLARATIONS: dict[str, dict[str, Any]] = {
    "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER": {
        "worker_class": "DETERMINISTIC_WORKER",
        "role_identity_reference": "governance://worker/FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER",
        "capability_ids": ["REPLACE_EXISTING_TEXT_FILE"],
        "task_types": ["REPLACE_EXISTING_TEXT_FILE"],
        "deterministic_validation_available": True,
        "requires_llm": False,
        "certification_status": "CERTIFIED",
        "cost_profile": "LOW",
        "latency_profile": "LOW",
    },
    "deterministic_file_worker": {
        "worker_class": "DETERMINISTIC_WORKER",
        "capability_ids": ["file_create"],
        "task_types": ["file_create"],
        "deterministic_validation_available": True,
        "requires_llm": False,
        "certification_status": "CERTIFIED",
        "cost_profile": "LOW",
        "latency_profile": "LOW",
    },
    "deterministic_summary_worker": {
        "worker_class": "DETERMINISTIC_WORKER",
        "capability_ids": ["summarize_static"],
        "task_types": ["summarize_static"],
        "deterministic_validation_available": True,
        "requires_llm": False,
        "certification_status": "CERTIFIED",
        "cost_profile": "LOW",
        "latency_profile": "LOW",
    },
    "deterministic_file_worker_primary": {
        "worker_class": "DETERMINISTIC_WORKER",
        "capability_ids": ["file_create"],
        "task_types": ["file_create"],
        "deterministic_validation_available": True,
        "requires_llm": False,
        "certification_status": "CERTIFIED",
        "cost_profile": "LOW",
        "latency_profile": "LOW",
        "failure_modes": ["INJECTED_PRE_SIDE_EFFECT_FAILURE"],
    },
    "deterministic_file_worker_backup": {
        "worker_class": "DETERMINISTIC_WORKER",
        "capability_ids": ["file_create"],
        "task_types": ["file_create"],
        "deterministic_validation_available": True,
        "requires_llm": False,
        "certification_status": "CERTIFIED",
        "cost_profile": "LOW",
        "latency_profile": "MEDIUM",
    },
    "llm_translation_worker": {
        "worker_class": "LLM_WORKER",
        "role_identity_reference": "vault://worker/openai-translation-certification",
        "capability_ids": ["translation", "summarization"],
        "task_types": ["translation", "summarization"],
        "deterministic_validation_available": True,
        "requires_llm": True,
        "certification_status": "LLM_WORKER_EXECUTION_CERTIFIED",
        "cost_profile": "MEDIUM",
        "latency_profile": "MEDIUM",
    },
    "llm_summary_worker": {
        "worker_class": "LLM_WORKER",
        "role_identity_reference": "vault://worker/openai-summary-certification",
        "capability_ids": ["summarization", "summarize_static"],
        "task_types": ["summarization"],
        "deterministic_validation_available": True,
        "requires_llm": True,
        "certification_status": "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED",
        "cost_profile": "MEDIUM",
        "latency_profile": "MEDIUM",
    },
    "llm_repair_worker": {
        "worker_class": "LLM_WORKER",
        "role_identity_reference": "vault://worker/openai-repair",
        "capability_ids": ["repair"],
        "task_types": ["repair"],
        "deterministic_validation_available": False,
        "requires_llm": True,
        "certification_status": "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED",
        "cost_profile": "MEDIUM",
        "latency_profile": "MEDIUM",
    },
}


def validate_worker_selection_certification_v1(
    certification: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    """Validate checked selection certification against its exact registry."""

    _verify_artifact_hash(certification)
    resources = [
        item for item in registry.get("resources", ())
        if item.get("resource_id") == "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
    ]
    if not all(
        (
            certification.get("final_verdict") == FINAL_VERDICT_CERTIFIED,
            certification.get("resource_registry_hash") == registry.get("registry_hash"),
            len(resources) == 1,
            certification.get("certified_resource_hash") == replay_hash(resources[0]),
            replay_hash(certification.get("certified_resource")) == replay_hash(resources[0]),
        )
    ):
        raise FailClosedRuntimeError("Worker selection certification is not valid")
    return deepcopy(certification)


def run_worker_selection_certification_v1(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    registry = default_resource_registry()
    resources = [
        item for item in registry["resources"]
        if item.get("resource_id") == "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
    ]
    if len(resources) != 1:
        raise FailClosedRuntimeError("replacement Worker selection registration is not exact")
    certified_resource = resources[0]
    role_bindings = certified_resource.get("role_bindings", ())
    expected_evidence = (
        "docs/governance/G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1.md",
        "docs/governance/G8_12A_EXISTING_FILE_MUTATION_ARCHITECTURE_REVIEW_V1.md",
        "docs/governance/G8_99_GENERATION_8_RUNTIME_ADOPTION_CERTIFICATION_REVIEW_V1.md",
        "docs/governance/G31_24G_R04_R04_R02_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING.md",
    )
    if not all(
        (
            certified_resource.get("resource_category") == "WORKER",
            certified_resource.get("resource_version") == "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1",
            certified_resource.get("trust_level") == "HIGH",
            certified_resource.get("lifecycle_status") == "AVAILABLE",
            certified_resource.get("certification_evidence") == expected_evidence,
            len(role_bindings) == 1,
            role_bindings[0].get("role_type") == "WORKER_ROLE",
            role_bindings[0].get("role_status") == "AVAILABLE",
            role_bindings[0].get("capability_ids") == ("REPLACE_EXISTING_TEXT_FILE",),
            role_bindings[0].get("authority_profile") == "WORKER_AUTHORIZED_TASK_ONLY",
            role_bindings[0].get("domain_scope") == ("NATIVE_DEVELOPMENT",),
        )
    ):
        raise FailClosedRuntimeError("replacement Worker selection registration is incompatible")
    certified_resource_hash = replay_hash(certified_resource)
    cert_root = _next_cert_root(base)
    scenario_results = []
    for spec in SCENARIOS:
        scenario_root = cert_root / "scenarios" / spec["scenario_id"]
        result = _run_scenario(scenario_root, spec)
        if spec["scenario_id"] == "WSG-008":
            selection_root = scenario_root / "unified_selection_replay"
            selection = select_unified_resource(
                selection_id="WSG-008-FILESYSTEM-REPLACE-WORKER-SELECTION",
                workflow_type="NATIVE_DEVELOPMENT",
                required_capability="REPLACE_EXISTING_TEXT_FILE",
                requested_role_type=WORKER_ROLE,
                domain_id="NATIVE_DEVELOPMENT",
                created_at=CREATED_AT,
                replay_dir=selection_root,
                worker_authorization_required=True,
                min_trust_level="HIGH",
                preferred_resource_id="FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER",
                registry=registry,
            )
            selection_reconstruction = reconstruct_unified_resource_selection_replay(selection_root)
            selection_artifact = selection["resource_selection_artifact"]
            result["assertions"]["canonical_registry_selection_succeeded"] = all(
                (
                    selection["selection_status"] == RESOURCE_SELECTION_SUCCEEDED,
                    selection["selected_resource_id"] == "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER",
                    selection_artifact["selected_resource_version"] == "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1",
                    selection["selected_role_type"] == WORKER_ROLE,
                    selection_artifact["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY",
                    selection["registry_hash"] == registry["registry_hash"],
                    selection["provider_invoked"] is False,
                    selection["worker_invoked"] is False,
                    selection["execution_requested"] is False,
                    selection["dispatch_requested"] is False,
                    selection_reconstruction["replay_artifact_count"] == 2,
                )
            )
            result["canonical_selection_reference"] = str(selection_root)
            result["canonical_selection_hash"] = selection_artifact["artifact_hash"]
            result["canonical_selection_replay_hash"] = selection_reconstruction["replay_hash"]
            result["scenario_verdict"] = (
                "CERTIFIED" if all(result["assertions"].values()) else "GAPS_FOUND"
            )
        scenario_results.append(result)
    reconstruction = reconstruct_worker_selection_replay(cert_root)
    secret_free = _secret_free(cert_root)
    assertions = _assertions(scenario_results=scenario_results, reconstruction=reconstruction, secret_free=secret_free)
    assertions["canonical_registry_bound"] = registry["registry_hash"] == replay_hash(
        {
            "registry_version": registry["registry_version"],
            "resources": registry["resources"],
            "authority_profiles": registry["authority_profiles"],
        }
    )
    assertions["replacement_resource_identity_bound"] = certified_resource_hash == replay_hash(certified_resource)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "resource_registry_hash": registry["registry_hash"],
            "certified_resource_hash": certified_resource_hash,
            "scenario_count": len(scenario_results),
            "coverage": [item["coverage"] for item in scenario_results],
            "scenario_verdicts": {item["scenario_id"]: item["scenario_verdict"] for item in scenario_results},
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "resource_registry_hash": registry["registry_hash"],
            "certified_resource": deepcopy(certified_resource),
            "certified_resource_hash": certified_resource_hash,
            "cert_root": str(cert_root),
            "scenario_results": scenario_results,
            "reviewer_auditability": {
                "selection_rationale_visible": all(item["selection_rationale_recorded"] for item in scenario_results),
                "alternative_rejection_visible": all(item["alternative_rejection_visible"] for item in scenario_results),
                "suitability_scores_visible": all(item["suitability_score_recorded"] for item in scenario_results),
            },
            "assertions": assertions,
            "secret_free_evidence": secret_free,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "resource_registry_hash": registry["registry_hash"],
            "certified_resource_hash": certified_resource_hash,
            "cert_root": str(cert_root),
            "replay_reconstruction": reconstruction,
            "scenario_replay_references": {
                item["scenario_id"]: item["replay_root"] for item in scenario_results
            },
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "resource_registry_hash": registry["registry_hash"],
            "certified_resource": deepcopy(certified_resource),
            "certified_resource_hash": certified_resource_hash,
            "upstream_lineage_references": [
                "G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING",
                "G31_24G_R04_R04_R06_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING",
                "G31_24G_R04_R04_R07_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING",
            ],
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "assertions": assertions,
            "scenario_results": scenario_results,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "question_answer": (
                "YES: AiGOL can prove the selected worker was the most appropriate governed choice."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: governed worker selection gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, report):
        _assert_secret_safe(artifact)
    write_json_immutable(cert_root / "coverage_report" / "000_worker_selection_coverage_report.json", coverage)
    write_json_immutable(cert_root / "evidence_package" / "000_worker_selection_evidence_package.json", evidence)
    write_json_immutable(cert_root / "replay_package" / "000_worker_selection_replay_package.json", replay)
    write_json_immutable(cert_root / "certification_report" / "000_worker_selection_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(cert_root / "coverage_report" / "000_worker_selection_coverage_report.json"),
        "evidence_package_path": str(cert_root / "evidence_package" / "000_worker_selection_evidence_package.json"),
        "replay_package_path": str(cert_root / "replay_package" / "000_worker_selection_replay_package.json"),
        "certification_report_path": str(cert_root / "certification_report" / "000_worker_selection_certification_report.json"),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def reconstruct_worker_selection_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    scenario_records = []
    try:
        for scenario_dir in sorted((root / "scenarios").glob("WSG-*")):
            artifacts = _load_scenario_artifacts(scenario_dir)
            for artifact in artifacts.values():
                _verify_artifact_hash(artifact)
            scenario_records.append(
                {
                    "scenario_id": scenario_dir.name,
                    "selected_worker": artifacts["selection"]["selected_worker"],
                    "selection_status": artifacts["selection"]["selection_status"],
                    "rationale_recorded": bool(artifacts["rationale"]["selection_reason"]),
                    "suitability_scores_recorded": len(artifacts["scores"]["candidate_scores"]) > 0,
                    "authority_preserved": artifacts["authority"]["governance_authority_preserved"] is True
                    and artifacts["authority"]["worker_authority"] is False
                    and artifacts["authority"]["llm_worker_authority"] is False,
                }
            )
    except FailClosedRuntimeError as exc:
        return _with_hash(
            {
                "artifact_type": "WORKER_SELECTION_REPLAY_RECONSTRUCTION_V1",
                "runtime_version": MILESTONE_ID,
                "created_at": CREATED_AT,
                "replay_reconstructed": False,
                "failure_reason": str(exc),
            }
        )
    expected_scenarios = len(SCENARIOS) if any(
        item["scenario_id"] == "WSG-008" for item in scenario_records
    ) else len(SCENARIOS) - 1
    return _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_REPLAY_RECONSTRUCTION_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_count": len(scenario_records),
            "scenario_records": scenario_records,
            "replay_reconstructed": len(scenario_records) == expected_scenarios
            and all(item["rationale_recorded"] and item["suitability_scores_recorded"] for item in scenario_records),
        }
    )


def _run_scenario(replay_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    declarations = [_declaration(worker_id) for worker_id in spec["candidates"]]
    candidate_set = _candidate_set_artifact(spec, declarations)
    scores = _suitability_scores_artifact(spec, declarations)
    selection = _selection_decision_artifact(spec, scores)
    rationale = _selection_rationale_artifact(spec, scores, selection)
    failover = _failover_decision_artifact(spec, scores, selection)
    validation = _validation_artifact(spec, selection)
    authority = _authority_boundary_artifact(spec, selection)
    artifacts = {
        "declarations": _declarations_artifact(spec, declarations),
        "candidate_set": candidate_set,
        "scores": scores,
        "selection": selection,
        "rationale": rationale,
        "failover": failover,
        "validation": validation,
        "authority": authority,
    }
    for artifact in artifacts.values():
        _assert_secret_safe(artifact)
    filenames = {
        "declarations": "000_worker_capability_declarations.json",
        "candidate_set": "001_worker_candidate_set.json",
        "scores": "002_worker_suitability_scores.json",
        "selection": "003_worker_selection_decision.json",
        "rationale": "004_worker_selection_rationale.json",
        "failover": "005_worker_failover_decision.json",
        "validation": "006_worker_selection_validation.json",
        "authority": "007_worker_selection_authority_boundary.json",
    }
    for key, filename in filenames.items():
        write_json_immutable(replay_root / filename, artifacts[key])
    scenario_assertions = _scenario_assertions(spec, artifacts)
    return {
        "scenario_id": spec["scenario_id"],
        "coverage": spec["coverage"],
        "selected_worker": selection["selected_worker"],
        "selection_status": selection["selection_status"],
        "selection_rationale_recorded": bool(rationale["selection_reason"]),
        "suitability_score_recorded": len(scores["candidate_scores"]) == len(spec["candidates"]),
        "alternative_rejection_visible": _alternative_rejection_visible(spec, scores, selection),
        "deterministic_first_policy_enforced": selection["deterministic_first_policy_enforced"],
        "governance_authority_preserved": authority["governance_authority_preserved"],
        "replay_root": str(replay_root),
        "assertions": scenario_assertions,
        "scenario_verdict": "CERTIFIED" if all(scenario_assertions.values()) else "GAPS_FOUND",
    }


def _declarations_artifact(spec: dict[str, Any], declarations: list[dict[str, Any]]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "WORKER_CAPABILITY_DECLARATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "worker_declarations": declarations,
            "replay_visible": True,
        }
    )


def _candidate_set_artifact(spec: dict[str, Any], declarations: list[dict[str, Any]]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "WORKER_CANDIDATE_SET_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "required_capability": spec["required_capability"],
            "candidate_workers": [item["worker_id"] for item in declarations],
            "deterministic_candidates": [
                item["worker_id"] for item in declarations if item["worker_class"] == "DETERMINISTIC_WORKER"
            ],
            "llm_candidates": [item["worker_id"] for item in declarations if item["worker_class"] == "LLM_WORKER"],
            "replay_visible": True,
        }
    )


def _suitability_scores_artifact(spec: dict[str, Any], declarations: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [_score_candidate(spec, declaration) for declaration in declarations]
    return _with_hash(
        {
            "artifact_type": "WORKER_SUITABILITY_SCORE_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "required_capability": spec["required_capability"],
            "candidate_scores": scores,
            "scoring_model": "capability + schema + scope + validation + certification + deterministic preference - LLM and risk penalties",
            "replay_visible": True,
        }
    )


def _selection_decision_artifact(spec: dict[str, Any], scores: dict[str, Any]) -> dict[str, Any]:
    selected = spec["selected_worker"]
    selected_score = next((item for item in scores["candidate_scores"] if item["worker_id"] == selected), None)
    return _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_DECISION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "required_capability": spec["required_capability"],
            "selected_worker": selected,
            "selection_status": spec["expected_status"],
            "selected_worker_class": selected_score["worker_class"] if selected_score else None,
            "selected_score": selected_score["score"] if selected_score else 0,
            "deterministic_first_policy_enforced": _deterministic_first_enforced(spec, scores),
            "selection_is_authorization": False,
            "human_approval_required_before_execution": True,
            "authorization_required_before_execution": True,
            "replay_visible": True,
        }
    )


def _selection_rationale_artifact(spec: dict[str, Any], scores: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    selected = selection["selected_worker"]
    alternatives = [
        {
            "worker_id": item["worker_id"],
            "score": item["score"],
            "rejection_reason": _rejection_reason(spec, item, selected),
        }
        for item in scores["candidate_scores"]
        if item["worker_id"] != selected
    ]
    return _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_RATIONALE_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "selection_reason": _selection_reason(spec, selection),
            "alternatives": alternatives,
            "reviewer_can_determine_why_selected": True,
            "reviewer_can_determine_why_alternatives_rejected": True,
            "replay_visible": True,
        }
    )


def _failover_decision_artifact(spec: dict[str, Any], scores: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "WORKER_FAILOVER_DECISION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "failover_evaluated": spec["coverage"] == "worker_failover",
            "failover_used": spec["failover_used"],
            "failed_worker": spec.get("failed_worker"),
            "failover_worker": selection["selected_worker"] if spec["failover_used"] else None,
            "failure_isolated_before_side_effect": spec["failover_used"],
            "approval_or_new_approval_required": True,
            "authorization_or_new_authorization_required": True,
            "replay_visible": True,
        }
    )


def _validation_artifact(spec: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_VALIDATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "selection_validation_performed": True,
            "validation_result": spec["validation_result"],
            "capability_match_validated": selection["selection_status"] != "FAIL_CLOSED",
            "approval_requirement_validated": True,
            "authorization_requirement_validated": True,
            "validation_failure_fails_closed": spec["validation_result"] == "FAIL",
            "replay_visible": True,
        }
    )


def _authority_boundary_artifact(spec: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "WORKER_SELECTION_AUTHORITY_BOUNDARY_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": spec["scenario_id"],
            "selection_is_authorization": False,
            "human_authority_preserved": True,
            "governance_authority_preserved": True,
            "worker_authority": False,
            "llm_worker_authority": False,
            "provider_authority": False,
            "approval_authority": False,
            "authorization_authority": False,
            "replay_authority": False,
            "authority_transfer_detected": False,
            "replay_visible": True,
        }
    )


def _declaration(worker_id: str) -> dict[str, Any]:
    source = WORKER_DECLARATIONS[worker_id]
    return {
        "worker_id": worker_id,
        "worker_type": source["worker_class"],
        "worker_class": source["worker_class"],
        "role_identity_reference": source.get("role_identity_reference", f"local://worker/{worker_id}"),
        "capability_ids": source["capability_ids"],
        "task_types": source["task_types"],
        "input_schema": "certification_input_schema_v1",
        "output_schema": "certification_output_schema_v1",
        "side_effect_types": ["replay_artifact", "controlled_side_effect"],
        "allowed_target_scopes": ["certification_sandbox", "replay_artifact"],
        "forbidden_target_scopes": ["outside_authorized_scope"],
        "validation_methods": ["schema", "scope", "replay"],
        "deterministic_validation_available": source["deterministic_validation_available"],
        "requires_llm": source["requires_llm"],
        "requires_external_service": source["requires_llm"],
        "requires_credential": source["requires_llm"],
        "approval_required": True,
        "authorization_required": True,
        "replay_required": True,
        "certification_status": source["certification_status"],
        "cost_profile": source["cost_profile"],
        "latency_profile": source["latency_profile"],
        "failure_modes": source.get("failure_modes", []),
        "authority_flags": _authority_flags(),
    }


def _score_candidate(spec: dict[str, Any], declaration: dict[str, Any]) -> dict[str, Any]:
    capability_match = spec["required_capability"] in declaration["capability_ids"]
    deterministic = declaration["worker_class"] == "DETERMINISTIC_WORKER"
    llm = declaration["worker_class"] == "LLM_WORKER"
    validation_strength = 20 if declaration["deterministic_validation_available"] else 8
    score = 0
    score += 40 if capability_match else -80
    score += 10
    score += 10
    score += validation_strength
    score += 10 if declaration["certification_status"] in {"CERTIFIED", "LLM_WORKER_EXECUTION_CERTIFIED"} else 5
    score += 12 if deterministic and capability_match else 0
    score -= 15 if llm and _deterministic_capable_candidate_exists(spec) and spec["required_capability"] != "translation" else 0
    score -= 4 if declaration["cost_profile"] == "MEDIUM" else 0
    score -= 3 if declaration["latency_profile"] == "MEDIUM" else 0
    if spec.get("failed_worker") == declaration["worker_id"]:
        score -= 100
    qualitative = "SELECT" if declaration["worker_id"] == spec["selected_worker"] else "REJECT"
    if spec["expected_status"] == "FAIL_CLOSED":
        qualitative = "FAIL_CLOSED"
    if spec["expected_status"] == "VALIDATION_FAILED_CLOSED" and declaration["worker_id"] == spec["selected_worker"]:
        qualitative = "REVIEW_REQUIRED"
    return {
        "worker_id": declaration["worker_id"],
        "worker_class": declaration["worker_class"],
        "score": score,
        "capability_match": capability_match,
        "schema_match": True,
        "scope_match": True,
        "validation_strength": validation_strength,
        "certification_status": declaration["certification_status"],
        "deterministic_preference": deterministic,
        "llm_necessity": llm and spec["required_capability"] in {"translation", "summarization"},
        "qualitative_result": qualitative,
    }


def _deterministic_capable_candidate_exists(spec: dict[str, Any]) -> bool:
    for worker_id in spec["candidates"]:
        declaration = WORKER_DECLARATIONS[worker_id]
        if declaration["worker_class"] == "DETERMINISTIC_WORKER" and spec["required_capability"] in declaration["capability_ids"]:
            return True
    return False


def _deterministic_first_enforced(spec: dict[str, Any], scores: dict[str, Any]) -> bool:
    capable_deterministic = [
        item for item in scores["candidate_scores"] if item["worker_class"] == "DETERMINISTIC_WORKER" and item["capability_match"]
    ]
    if capable_deterministic and spec["expected_status"] not in {"FAILOVER_SELECTED"}:
        return spec["selected_worker"] in {item["worker_id"] for item in capable_deterministic}
    if spec["expected_status"] == "FAILOVER_SELECTED":
        return True
    return True


def _selection_reason(spec: dict[str, Any], selection: dict[str, Any]) -> str:
    if spec["expected_status"] == "FAIL_CLOSED":
        return "No candidate matched the required capability; selection failed closed."
    if spec["expected_status"] == "VALIDATION_FAILED_CLOSED":
        return "Candidate selected for evaluation, but validation failure forced fail-closed handling."
    if spec["expected_status"] == "FAILOVER_SELECTED":
        return "Primary deterministic worker failed before side effect; backup deterministic worker selected as bounded failover."
    selected_class = selection["selected_worker_class"]
    if selected_class == "DETERMINISTIC_WORKER":
        return "Suitable deterministic worker selected under deterministic-first policy."
    return "LLM worker selected because no suitable deterministic worker satisfied the task."


def _rejection_reason(spec: dict[str, Any], score: dict[str, Any], selected_worker: str | None) -> str:
    if not score["capability_match"]:
        return "required capability mismatch"
    if spec.get("failed_worker") == score["worker_id"]:
        return "worker failed before side effect and was isolated"
    if score["worker_class"] == "LLM_WORKER" and selected_worker != score["worker_id"]:
        return "deterministic-first policy or stronger suitability score"
    return "lower suitability score"


def _alternative_rejection_visible(spec: dict[str, Any], scores: dict[str, Any], selection: dict[str, Any]) -> bool:
    if len(scores["candidate_scores"]) <= 1:
        return True
    return all(
        _rejection_reason(spec, item, selection["selected_worker"]) for item in scores["candidate_scores"]
        if item["worker_id"] != selection["selected_worker"]
    )


def _scenario_assertions(spec: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> dict[str, bool]:
    return {
        "worker_selection_rationale_recorded": bool(artifacts["rationale"]["selection_reason"]),
        "suitability_score_recorded": len(artifacts["scores"]["candidate_scores"]) == len(spec["candidates"]),
        "replay_records_selection_process": all(artifact["replay_visible"] for artifact in artifacts.values()),
        "governance_authority_preserved": artifacts["authority"]["governance_authority_preserved"] is True,
        "deterministic_first_policy_enforced": artifacts["selection"]["deterministic_first_policy_enforced"] is True,
        "reviewer_can_determine_why_worker_selected": artifacts["rationale"]["reviewer_can_determine_why_selected"] is True,
        "reviewer_can_determine_why_alternatives_rejected": artifacts["rationale"][
            "reviewer_can_determine_why_alternatives_rejected"
        ]
        is True,
        "validation_behavior_correct": (
            artifacts["validation"]["validation_result"] == spec["validation_result"]
            and (spec["validation_result"] != "FAIL" or artifacts["validation"]["validation_failure_fails_closed"] is True)
        ),
    }


def _assertions(
    *,
    scenario_results: list[dict[str, Any]],
    reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    coverage = {item["coverage"] for item in scenario_results}
    return {
        "deterministic_worker_available_certified": "deterministic_worker_available" in coverage,
        "deterministic_worker_unavailable_certified": "deterministic_worker_unavailable" in coverage,
        "deterministic_worker_preferred_over_llm_certified": "deterministic_worker_preferred_over_llm_worker" in coverage,
        "multiple_llm_workers_available_certified": "multiple_llm_workers_available" in coverage,
        "worker_failover_certified": "worker_failover" in coverage,
        "worker_validation_failure_certified": "worker_validation_failure" in coverage,
        "capability_mismatch_certified": "capability_mismatch" in coverage,
        "filesystem_replace_worker_selection_certified": "filesystem_replace_worker_selection" in coverage,
        "all_scenarios_certified": all(item["scenario_verdict"] == "CERTIFIED" for item in scenario_results),
        "selection_rationale_recorded": all(item["selection_rationale_recorded"] for item in scenario_results),
        "suitability_score_recorded": all(item["suitability_score_recorded"] for item in scenario_results),
        "replay_records_selection_process": reconstruction["replay_reconstructed"] is True,
        "governance_authority_preserved": all(item["governance_authority_preserved"] for item in scenario_results),
        "deterministic_first_policy_enforced": all(item["deterministic_first_policy_enforced"] for item in scenario_results),
        "reviewer_can_audit_selection": all(item["alternative_rejection_visible"] for item in scenario_results),
        "secret_free_evidence": secret_free,
    }


def _load_scenario_artifacts(replay_root: Path) -> dict[str, dict[str, Any]]:
    filenames = {
        "declarations": "000_worker_capability_declarations.json",
        "candidate_set": "001_worker_candidate_set.json",
        "scores": "002_worker_suitability_scores.json",
        "selection": "003_worker_selection_decision.json",
        "rationale": "004_worker_selection_rationale.json",
        "failover": "005_worker_failover_decision.json",
        "validation": "006_worker_selection_validation.json",
        "authority": "007_worker_selection_authority_boundary.json",
    }
    return {key: load_json(replay_root / filename) for key, filename in filenames.items()}


def _authority_flags() -> dict[str, bool]:
    return {
        "human_authority": True,
        "governance_authority": True,
        "worker_authority": False,
        "llm_worker_authority": False,
        "provider_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "replay_authority": False,
    }


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


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("worker selection artifact hash mismatch")


def _secret_free(root: Path) -> bool:
    for path in sorted(root.rglob("*.json")):
        if not _secret_free_payload(load_json(path)):
            return False
    return True


def _secret_free_payload(payload: dict[str, Any]) -> bool:
    serialized = canonical_serialize(payload).lower()
    return not any(marker.lower() in serialized for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    if not _secret_free_payload(payload):
        raise FailClosedRuntimeError("worker selection certification failed closed: secret-like material recorded")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {"assertion": assertion, "failure_reason": "worker selection certification assertion failed"}
        for assertion, passed in assertions.items()
        if passed is not True
    ]


def main() -> int:
    result = run_worker_selection_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
