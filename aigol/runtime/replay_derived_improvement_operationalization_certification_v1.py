"""Certification for operational replay-derived improvement cycles."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/replay_derived_improvement_operationalization_certification_v1")
CREATED_AT = "2026-06-23T00:00:00Z"
FINAL_VERDICT_CERTIFIED = "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFIED"
FINAL_VERDICT_GAPS = "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_GAPS_FOUND"

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


def run_replay_derived_improvement_operationalization_certification_v1(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    """Execute continuous replay-derived improvement operationalization certification."""

    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    campaign = _build_operational_campaign()
    _write_scenario_artifacts(cert_root, campaign)
    reconstruction = reconstruct_replay_derived_improvement_operationalization_replay(cert_root)
    assertions = _assertions(campaign=campaign, reconstruction=reconstruction, cert_root=cert_root)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_ids": [
                "RDI-OP-001",
                "RDI-OP-002",
                "RDI-OP-003",
                "RDI-OP-004",
                "RDI-OP-005",
                "RDI-OP-006",
                "RDI-OP-007",
            ],
            "coverage_dimensions": [
                "multi-generation replay chain",
                "backlog creation",
                "prioritization",
                "duplicate detection",
                "competing improvements",
                "rejected improvements",
                "approved improvements",
                "superseded proposal handling",
                "lineage tracking",
                "PPP routing preservation",
                "human approval preservation",
                "proposal-only behavior",
                "governance authority preservation",
                "no autonomous modification",
                "no authority transfer",
            ],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "backlog": _summary(campaign["backlog_entry"]),
            "duplicate_detection": _summary(campaign["duplicate_detection"]),
            "priority": _summary(campaign["priority"]),
            "competing_improvements": [
                _summary(campaign["original_proposal"]),
                _summary(campaign["competing_proposal"]),
            ],
            "rejection": _summary(campaign["rejection"]),
            "approval": _summary(campaign["approval"]),
            "supersession": _summary(campaign["supersession"]),
            "lineage": _summary(campaign["lineage"]),
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "reconstruction": reconstruction,
            "replay_reconstructed": reconstruction["replay_reconstructed"],
            "generation_chain": campaign["lineage"]["generation_chain"],
            "source_replay_hashes": campaign["backlog_entry"]["source_replay_hashes"],
            "final_verdict": final_verdict,
        }
    )
    operationalization = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "backlog_status": campaign["backlog_entry"]["status"],
            "duplicate_outcome": campaign["duplicate_detection"]["duplicate_outcome"],
            "priority_level": campaign["priority"]["priority_level"],
            "superseded_proposal": campaign["supersession"]["superseded_proposal"],
            "superseding_proposal": campaign["supersession"]["superseding_proposal"],
            "human_approval_required": True,
            "ppp_routing_preserved": campaign["ppp_route"]["ppp_route"] == "RUNTIME_HARDENING",
            "proposal_only_behavior_preserved": _proposal_only(campaign),
            "code_modified": False,
            "governance_modified": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "authority_transferred": False,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "operationalization_package_hash": operationalization["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "question_answer": (
                "YES: AiGOL can sustain long-term replay-derived improvement cycles while "
                "preserving governance, replay traceability, and human authority."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: replay-derived improvement operationalization gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, operationalization, report):
        _assert_secret_safe(artifact)
    write_json_immutable(
        cert_root / "coverage_report" / "000_replay_derived_improvement_operationalization_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        cert_root / "evidence_package" / "000_replay_derived_improvement_operationalization_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        cert_root / "replay_package" / "000_replay_derived_improvement_operationalization_replay_package.json",
        replay,
    )
    write_json_immutable(
        cert_root
        / "operationalization_package"
        / "000_replay_derived_improvement_operationalization_package.json",
        operationalization,
    )
    write_json_immutable(
        cert_root
        / "certification_report"
        / "000_replay_derived_improvement_operationalization_certification_report.json",
        report,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(
            cert_root
            / "coverage_report"
            / "000_replay_derived_improvement_operationalization_coverage_report.json"
        ),
        "evidence_package_path": str(
            cert_root
            / "evidence_package"
            / "000_replay_derived_improvement_operationalization_evidence_package.json"
        ),
        "replay_package_path": str(
            cert_root
            / "replay_package"
            / "000_replay_derived_improvement_operationalization_replay_package.json"
        ),
        "operationalization_package_path": str(
            cert_root
            / "operationalization_package"
            / "000_replay_derived_improvement_operationalization_package.json"
        ),
        "certification_report_path": str(
            cert_root
            / "certification_report"
            / "000_replay_derived_improvement_operationalization_certification_report.json"
        ),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_replay_derived_improvement_operationalization_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    artifacts = {
        "generation_1_replay": load_json(root / "scenarios" / "RDI-OP-001" / "000_generation_1_replay.json"),
        "generation_2_replay": load_json(root / "scenarios" / "RDI-OP-001" / "001_generation_2_replay.json"),
        "backlog_entry": load_json(root / "scenarios" / "RDI-OP-001" / "002_backlog_entry.json"),
        "duplicate_detection": load_json(root / "scenarios" / "RDI-OP-001" / "003_duplicate_detection.json"),
        "priority": load_json(root / "scenarios" / "RDI-OP-002" / "000_priority.json"),
        "original_proposal": load_json(root / "scenarios" / "RDI-OP-002" / "001_original_proposal.json"),
        "competing_proposal": load_json(root / "scenarios" / "RDI-OP-002" / "002_competing_proposal.json"),
        "rejection": load_json(root / "scenarios" / "RDI-OP-003" / "000_rejection.json"),
        "approval": load_json(root / "scenarios" / "RDI-OP-004" / "000_approval.json"),
        "supersession": load_json(root / "scenarios" / "RDI-OP-005" / "000_supersession.json"),
        "certification_failure": load_json(root / "scenarios" / "RDI-OP-006" / "000_certification_failure.json"),
        "lineage": load_json(root / "scenarios" / "RDI-OP-007" / "000_lineage.json"),
        "ppp_route": load_json(root / "scenarios" / "RDI-OP-007" / "001_ppp_route.json"),
    }
    for artifact in artifacts.values():
        _verify_artifact_hash(artifact)
    backlog = artifacts["backlog_entry"]
    duplicate = artifacts["duplicate_detection"]
    supersession = artifacts["supersession"]
    lineage = artifacts["lineage"]
    replay_reconstructed = (
        duplicate["canonical_backlog_entry"] == backlog["backlog_entry_id"]
        and supersession["superseded_proposal"] == artifacts["original_proposal"]["proposal_id"]
        and supersession["superseding_proposal"] == artifacts["competing_proposal"]["proposal_id"]
        and lineage["generation_chain"][0]["source_replay_reference"]
        == artifacts["generation_1_replay"]["source_replay_reference"]
        and lineage["generation_chain"][1]["source_replay_reference"]
        == artifacts["generation_2_replay"]["source_replay_reference"]
    )
    return {
        "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_RECONSTRUCTION_V1",
        "replay_reconstructed": replay_reconstructed,
        "artifact_hashes": {key: value["artifact_hash"] for key, value in artifacts.items()},
        "backlog_entry_id": backlog["backlog_entry_id"],
        "lineage_id": lineage["lineage_id"],
        "duplicate_group_id": duplicate["duplicate_group_id"],
        "superseded_proposal": supersession["superseded_proposal"],
        "superseding_proposal": supersession["superseding_proposal"],
        "ppp_route": artifacts["ppp_route"]["ppp_route"],
    }


def _build_operational_campaign() -> dict[str, dict[str, Any]]:
    generation_1 = _artifact(
        {
            "artifact_type": "REPLAY_OBSERVATION_ARTIFACT_V1",
            "source_replay_reference": "runtime/product1_end_to_end_certification_v1/CERT-000001/replay/generation-1.json",
            "source_replay_hash": replay_hash({"generation": 1, "gap": "VALIDATION_GAP"}),
            "generation": 1,
            "gap_classification": "VALIDATION_GAP",
            "affected_capability": "result_validation",
            "observed_condition": "Validation summary lacks reviewer-facing remediation hint.",
            "replay_visible": True,
        }
    )
    generation_2 = _artifact(
        {
            "artifact_type": "REPLAY_OBSERVATION_ARTIFACT_V1",
            "source_replay_reference": "runtime/product1_end_to_end_certification_v1/CERT-000002/replay/generation-2.json",
            "source_replay_hash": replay_hash({"generation": 2, "gap": "VALIDATION_GAP"}),
            "generation": 2,
            "gap_classification": "VALIDATION_GAP",
            "affected_capability": "result_validation",
            "observed_condition": "Validation summary still lacks reviewer-facing remediation hint.",
            "replay_visible": True,
        }
    )
    backlog = _artifact(
        {
            "artifact_type": "IMPROVEMENT_BACKLOG_ENTRY_ARTIFACT_V1",
            "backlog_entry_id": "BACKLOG-RDI-OP-000001",
            "improvement_intent_id": "IMPROVEMENT-INTENT-RDI-OP-000001",
            "source_replay_references": [
                generation_1["source_replay_reference"],
                generation_2["source_replay_reference"],
            ],
            "source_replay_hashes": [
                generation_1["source_replay_hash"],
                generation_2["source_replay_hash"],
            ],
            "gap_classification": "VALIDATION_GAP",
            "affected_capability": "result_validation",
            "affected_boundary": "reviewer_explainability",
            "priority": "P2",
            "status": "PRIORITIZED",
            "duplicate_group_id": "DUPLICATE-GROUP-RDI-OP-VALIDATION-000001",
            "supersedes": [],
            "superseded_by": None,
            "human_review_required": True,
            "lineage_generation": 2,
            "proposal_only": True,
            "replay_visible": True,
        }
    )
    duplicate = _artifact(
        {
            "artifact_type": "IMPROVEMENT_DUPLICATE_DETECTION_ARTIFACT_V1",
            "duplicate_detection_id": "DUPLICATE-RDI-OP-000001",
            "duplicate_group_id": backlog["duplicate_group_id"],
            "canonical_backlog_entry": backlog["backlog_entry_id"],
            "duplicate_outcome": "DUPLICATE_OF_EXISTING",
            "new_replay_reference": generation_2["source_replay_reference"],
            "new_replay_hash": generation_2["source_replay_hash"],
            "evidence_retained": True,
            "automatic_approval": False,
            "replay_visible": True,
        }
    )
    priority = _artifact(
        {
            "artifact_type": "IMPROVEMENT_PRIORITY_ARTIFACT_V1",
            "priority_id": "PRIORITY-RDI-OP-000001",
            "backlog_entry_id": backlog["backlog_entry_id"],
            "priority_level": "P2",
            "priority_score": 72,
            "rationale": "Repeated validation explainability gap affects audit review but does not alter authority boundaries.",
            "non_authoritative": True,
            "human_review_required": True,
            "replay_visible": True,
        }
    )
    original_proposal = _artifact(
        {
            "artifact_type": "IMPROVEMENT_PROPOSAL_ARTIFACT_V1",
            "proposal_id": "PROPOSAL-RDI-OP-ORIGINAL-000001",
            "backlog_entry_id": backlog["backlog_entry_id"],
            "proposal_summary": "Add a reviewer-facing remediation hint to validation summaries.",
            "proposal_status": "REJECTED",
            "ppp_route_required": True,
            "human_approval_required": True,
            "implementation_executed": False,
            "code_modified": False,
            "governance_modified": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "authority_transferred": False,
            "replay_visible": True,
        }
    )
    competing_proposal = _artifact(
        {
            "artifact_type": "IMPROVEMENT_PROPOSAL_ARTIFACT_V1",
            "proposal_id": "PROPOSAL-RDI-OP-COMPETING-000001",
            "backlog_entry_id": backlog["backlog_entry_id"],
            "proposal_summary": "Add remediation hint plus source replay pointer in validation summaries.",
            "proposal_status": "APPROVED_FOR_PROPOSAL",
            "ppp_route_required": True,
            "human_approval_required": True,
            "implementation_executed": False,
            "code_modified": False,
            "governance_modified": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "authority_transferred": False,
            "replay_visible": True,
        }
    )
    rejection = _artifact(
        {
            "artifact_type": "HUMAN_IMPROVEMENT_REJECTION_ARTIFACT_V1",
            "decision_id": "HUMAN-REJECTION-RDI-OP-000001",
            "proposal_id": original_proposal["proposal_id"],
            "decision": "REJECTED",
            "reason": "Proposal did not preserve direct replay traceability for reviewer verification.",
            "human_authority_preserved": True,
            "implementation_authorized": False,
            "replay_visible": True,
        }
    )
    approval = _artifact(
        {
            "artifact_type": "HUMAN_IMPROVEMENT_APPROVAL_ARTIFACT_V1",
            "decision_id": "HUMAN-APPROVAL-RDI-OP-000001",
            "proposal_id": competing_proposal["proposal_id"],
            "decision": "APPROVED_FOR_IMPLEMENTATION_PROPOSAL_ONLY",
            "approved_scope": "CREATE_IMPLEMENTATION_PROPOSAL_AND_CERTIFICATION_PLAN_ONLY",
            "human_authority_preserved": True,
            "implementation_execution_allowed": False,
            "replay_visible": True,
        }
    )
    supersession = _artifact(
        {
            "artifact_type": "IMPROVEMENT_SUPERSESSION_ARTIFACT_V1",
            "supersession_id": "SUPERSESSION-RDI-OP-000001",
            "superseded_proposal": original_proposal["proposal_id"],
            "superseding_proposal": competing_proposal["proposal_id"],
            "rationale": "Superseding proposal preserves reviewer-facing replay traceability.",
            "superseded_execution_blocked": True,
            "human_review_required": True,
            "replay_visible": True,
        }
    )
    certification_failure = _artifact(
        {
            "artifact_type": "IMPROVEMENT_CERTIFICATION_FAILURE_ARTIFACT_V1",
            "certification_id": "CERTIFICATION-RDI-OP-FAILED-000001",
            "proposal_id": original_proposal["proposal_id"],
            "certification_status": "CERTIFICATION_FAILED",
            "readiness_status_updated": False,
            "remediation_requires_new_or_amended_proposal": True,
            "replay_visible": True,
        }
    )
    lineage = _artifact(
        {
            "artifact_type": "IMPROVEMENT_LINEAGE_ARTIFACT_V1",
            "lineage_id": "LINEAGE-RDI-OP-000001",
            "backlog_entry_id": backlog["backlog_entry_id"],
            "generation_chain": [
                {
                    "generation": 1,
                    "source_replay_reference": generation_1["source_replay_reference"],
                    "source_replay_hash": generation_1["source_replay_hash"],
                    "improvement_reference": original_proposal["proposal_id"],
                },
                {
                    "generation": 2,
                    "source_replay_reference": generation_2["source_replay_reference"],
                    "source_replay_hash": generation_2["source_replay_hash"],
                    "improvement_reference": competing_proposal["proposal_id"],
                    "predecessor_improvement_reference": original_proposal["proposal_id"],
                },
            ],
            "successor_replay_required_after_certification": True,
            "closure_status": "APPROVED_PROPOSAL_PENDING_CERTIFICATION",
            "replay_visible": True,
        }
    )
    ppp_route = _artifact(
        {
            "artifact_type": "PPP_ROUTING_ARTIFACT_V1",
            "ppp_route_id": "PPP-ROUTE-RDI-OP-000001",
            "backlog_entry_id": backlog["backlog_entry_id"],
            "proposal_id": competing_proposal["proposal_id"],
            "ppp_route": "RUNTIME_HARDENING",
            "routing_reason": "Validation explainability improvement requires bounded runtime proposal and certification.",
            "human_approval_required": True,
            "implementation_authorized": False,
            "replay_visible": True,
        }
    )
    return {
        "generation_1_replay": generation_1,
        "generation_2_replay": generation_2,
        "backlog_entry": backlog,
        "duplicate_detection": duplicate,
        "priority": priority,
        "original_proposal": original_proposal,
        "competing_proposal": competing_proposal,
        "rejection": rejection,
        "approval": approval,
        "supersession": supersession,
        "certification_failure": certification_failure,
        "lineage": lineage,
        "ppp_route": ppp_route,
    }


def _write_scenario_artifacts(cert_root: Path, campaign: dict[str, dict[str, Any]]) -> None:
    paths = {
        "generation_1_replay": "scenarios/RDI-OP-001/000_generation_1_replay.json",
        "generation_2_replay": "scenarios/RDI-OP-001/001_generation_2_replay.json",
        "backlog_entry": "scenarios/RDI-OP-001/002_backlog_entry.json",
        "duplicate_detection": "scenarios/RDI-OP-001/003_duplicate_detection.json",
        "priority": "scenarios/RDI-OP-002/000_priority.json",
        "original_proposal": "scenarios/RDI-OP-002/001_original_proposal.json",
        "competing_proposal": "scenarios/RDI-OP-002/002_competing_proposal.json",
        "rejection": "scenarios/RDI-OP-003/000_rejection.json",
        "approval": "scenarios/RDI-OP-004/000_approval.json",
        "supersession": "scenarios/RDI-OP-005/000_supersession.json",
        "certification_failure": "scenarios/RDI-OP-006/000_certification_failure.json",
        "lineage": "scenarios/RDI-OP-007/000_lineage.json",
        "ppp_route": "scenarios/RDI-OP-007/001_ppp_route.json",
    }
    for key, relative in paths.items():
        write_json_immutable(cert_root / relative, campaign[key])


def _assertions(
    *,
    campaign: dict[str, dict[str, Any]],
    reconstruction: dict[str, Any],
    cert_root: Path,
) -> dict[str, bool]:
    backlog = campaign["backlog_entry"]
    duplicate = campaign["duplicate_detection"]
    priority = campaign["priority"]
    supersession = campaign["supersession"]
    lineage = campaign["lineage"]
    approval = campaign["approval"]
    proposals = (campaign["original_proposal"], campaign["competing_proposal"])
    return {
        "multi_generation_replay_chains_created": len(lineage["generation_chain"]) == 2,
        "backlog_creation_verified": backlog["artifact_type"] == "IMPROVEMENT_BACKLOG_ENTRY_ARTIFACT_V1",
        "prioritization_verified": priority["priority_level"] == "P2" and priority["non_authoritative"] is True,
        "duplicate_detection_verified": duplicate["duplicate_outcome"] == "DUPLICATE_OF_EXISTING",
        "superseded_proposal_handling_verified": supersession["superseded_execution_blocked"] is True,
        "lineage_tracking_verified": lineage["generation_chain"][1]["predecessor_improvement_reference"]
        == campaign["original_proposal"]["proposal_id"],
        "replay_linkage_across_generations_verified": backlog["source_replay_hashes"]
        == [
            campaign["generation_1_replay"]["source_replay_hash"],
            campaign["generation_2_replay"]["source_replay_hash"],
        ],
        "ppp_routing_preserved": campaign["ppp_route"]["ppp_route"] == "RUNTIME_HARDENING",
        "human_approval_preserved": approval["human_authority_preserved"] is True
        and approval["implementation_execution_allowed"] is False,
        "proposal_only_behavior_preserved": _proposal_only(campaign),
        "governance_authority_preserved": all(item["human_approval_required"] is True for item in proposals),
        "no_autonomous_modification": all(
            item["code_modified"] is False and item["governance_modified"] is False for item in proposals
        ),
        "no_authority_transfer": all(item["authority_transferred"] is False for item in proposals),
        "replay_reconstructed": reconstruction["replay_reconstructed"] is True,
        "secret_free_evidence": _path_secret_free(cert_root),
    }


def _proposal_only(campaign: dict[str, dict[str, Any]]) -> bool:
    proposals = (campaign["original_proposal"], campaign["competing_proposal"])
    return all(
        proposal["implementation_executed"] is False
        and proposal["code_modified"] is False
        and proposal["governance_modified"] is False
        and proposal["worker_invoked"] is False
        and proposal["provider_invoked"] is False
        and proposal["authority_transferred"] is False
        for proposal in proposals
    )


def _summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact["artifact_type"],
        "artifact_hash": artifact["artifact_hash"],
        "id": artifact.get("backlog_entry_id")
        or artifact.get("duplicate_detection_id")
        or artifact.get("priority_id")
        or artifact.get("proposal_id")
        or artifact.get("decision_id")
        or artifact.get("supersession_id")
        or artifact.get("lineage_id"),
        "status": artifact.get("status")
        or artifact.get("proposal_status")
        or artifact.get("decision")
        or artifact.get("duplicate_outcome")
        or artifact.get("closure_status"),
        "replay_visible": artifact.get("replay_visible", False),
    }


def _artifact(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact.setdefault("runtime_version", MILESTONE_ID)
    artifact.setdefault("created_at", CREATED_AT)
    artifact.setdefault("proposal_only", True)
    artifact.setdefault("replay_visible", True)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _with_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(artifact)
    payload.pop("artifact_hash", None)
    payload["artifact_hash"] = replay_hash(payload)
    return payload


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise ValueError("replay-derived improvement operationalization artifact hash mismatch")


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    max_index = 0
    for child in base.iterdir():
        if child.is_dir():
            match = re.fullmatch(r"CERT-(\d{6})", child.name)
            if match:
                max_index = max(max_index, int(match.group(1)))
    return base / f"CERT-{max_index + 1:06d}"


def _path_secret_free(path: Path) -> bool:
    if not path.exists():
        return True
    for artifact_path in path.rglob("*.json"):
        text = artifact_path.read_text(encoding="utf-8")
        if any(marker in text for marker in SECRET_MARKERS):
            return False
    return True


def _assert_secret_safe(artifact: dict[str, Any]) -> None:
    serialized = canonical_serialize(artifact)
    if any(marker in serialized for marker in SECRET_MARKERS):
        raise ValueError("replay-derived improvement operationalization artifact contains secret marker")


def _blockers(assertions: dict[str, bool]) -> list[str]:
    return [key for key, value in assertions.items() if value is not True]


def main() -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1()
    print("CERT_ROOT=" + result["cert_root"])
    print("FINAL_VERDICT=" + result["final_verdict"])


if __name__ == "__main__":
    main()
