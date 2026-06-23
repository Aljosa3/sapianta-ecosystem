"""Certification for replay-derived improvement proposal governance."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_CREATED,
    create_governed_implementation_request,
    reconstruct_governed_implementation_request_replay,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    PPP_CANDIDATE_CREATED,
    bridge_improvement_intent_to_ppp_candidate,
    reconstruct_improvement_intent_to_ppp_bridge_replay,
)
from aigol.runtime.replay_gap_detection_runtime import (
    GAPS_DETECTED,
    detect_replay_gaps,
    reconstruct_replay_gap_detection_replay,
)
from aigol.runtime.replay_to_improvement_intent_runtime import (
    IMPROVEMENT_INTENT_CREATED,
    create_improvement_intent_from_replay_gap,
    reconstruct_replay_to_improvement_intent_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_REPLAY_DERIVED_IMPROVEMENT_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/replay_derived_improvement_certification_v1")
CREATED_AT = "2026-06-23T00:00:00Z"
FINAL_VERDICT_CERTIFIED = "REPLAY_DERIVED_IMPROVEMENT_CERTIFIED"
FINAL_VERDICT_GAPS = "REPLAY_DERIVED_IMPROVEMENT_GAPS_FOUND"

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


def run_replay_derived_improvement_certification_v1(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    """Execute replay-derived improvement proposal certification."""

    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    scenario = _execute_gap_to_proposal_scenario(cert_root)
    rejection = _execute_missing_approval_scenario(cert_root, scenario["ppp_candidate_artifact"])
    approved = _execute_approved_proposal_scenario(cert_root, scenario["ppp_candidate_artifact"])
    replay_reconstruction = _reconstruct_replay(cert_root)
    assertions = _assertions(
        scenario=scenario,
        rejection=rejection,
        approved=approved,
        replay_reconstruction=replay_reconstruction,
        cert_root=cert_root,
    )
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "coverage_dimensions": [
                "replay observation",
                "gap detection",
                "improvement intent creation",
                "PPP routing",
                "human approval requirement",
                "proposal-only behavior",
                "no autonomous modification",
                "no governance bypass",
                "no authority transfer",
                "replay closure",
                "secret-free evidence",
            ],
            "scenario_ids": ["RDI-001", "RDI-002", "RDI-003"],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "originating_replay": scenario["originating_replay_summary"],
            "gap_detection": _artifact_summary(scenario["gap_detection_artifact"]),
            "improvement_intent": _artifact_summary(scenario["improvement_intent_artifact"]),
            "ppp_routing": _artifact_summary(scenario["ppp_candidate_artifact"]),
            "approval_requirement": rejection["approval_requirement_summary"],
            "approved_proposal": approved["approved_proposal_summary"],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "originating_replay_reference": scenario["originating_replay_summary"]["source_replay_reference"],
            "originating_replay_hash": scenario["originating_replay_summary"]["source_replay_hash"],
            "reconstruction": replay_reconstruction,
            "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
            "replay_closure": {
                "improvement_linked_to_originating_replay": assertions[
                    "improvement_linked_to_originating_replay"
                ],
                "improvement_evidence_traceable": assertions["improvement_evidence_traceable"],
                "proposal_only_closure": assertions["proposal_only_behavior_verified"],
            },
            "final_verdict": final_verdict,
        }
    )
    proposal = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_PROPOSAL_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "proposal_status": "PROPOSAL_ONLY",
            "source_improvement_intent": scenario["improvement_intent_artifact"]["improvement_intent_id"],
            "source_improvement_intent_hash": scenario["improvement_intent_artifact"]["artifact_hash"],
            "source_gap_reference": scenario["gap_detection_artifact"]["detection_id"],
            "source_gap_hash": scenario["gap_detection_artifact"]["artifact_hash"],
            "source_replay_references": scenario["ppp_candidate_artifact"]["source_replay_references"],
            "source_replay_hashes": scenario["ppp_candidate_artifact"]["source_replay_hashes"],
            "human_approval_required": True,
            "implementation_request_created_after_approval": approved[
                "implementation_request_artifact"
            ]["request_status"]
            == IMPLEMENTATION_REQUEST_CREATED,
            "implementation_executed": False,
            "code_modified": False,
            "governance_modified": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "authority_transferred": False,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "REPLAY_DERIVED_IMPROVEMENT_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "improvement_proposal_package_hash": proposal["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "question_answer": (
                "YES: AiGOL can generate replay-derived improvement proposals while preserving "
                "governance authority and human control."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: replay-derived improvement governance gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, proposal, report):
        _assert_secret_safe(artifact)
    write_json_immutable(
        cert_root / "coverage_report" / "000_replay_derived_improvement_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        cert_root / "evidence_package" / "000_replay_derived_improvement_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        cert_root / "replay_package" / "000_replay_derived_improvement_replay_package.json",
        replay,
    )
    write_json_immutable(
        cert_root
        / "improvement_proposal_package"
        / "000_replay_derived_improvement_proposal_package.json",
        proposal,
    )
    write_json_immutable(
        cert_root
        / "certification_report"
        / "000_replay_derived_improvement_certification_report.json",
        report,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(
            cert_root / "coverage_report" / "000_replay_derived_improvement_coverage_report.json"
        ),
        "evidence_package_path": str(
            cert_root / "evidence_package" / "000_replay_derived_improvement_evidence_package.json"
        ),
        "replay_package_path": str(
            cert_root / "replay_package" / "000_replay_derived_improvement_replay_package.json"
        ),
        "improvement_proposal_package_path": str(
            cert_root
            / "improvement_proposal_package"
            / "000_replay_derived_improvement_proposal_package.json"
        ),
        "certification_report_path": str(
            cert_root
            / "certification_report"
            / "000_replay_derived_improvement_certification_report.json"
        ),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _execute_gap_to_proposal_scenario(cert_root: Path) -> dict[str, Any]:
    replay = _source_replay_artifact()
    gap = detect_replay_gaps(
        detection_id="GAP-REPLAY-DERIVED-IMPROVEMENT-CERTIFICATION-000001",
        replay_artifacts=[replay],
        created_at=CREATED_AT,
        replay_dir=cert_root / "scenarios" / "RDI-001" / "replay" / "gap_detection",
        domain_id="AIGOL_CORE",
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-REPLAY-DERIVED-CERTIFICATION-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id="CHAIN-REPLAY-DERIVED-IMPROVEMENT-CERTIFICATION-000001",
        created_at=CREATED_AT,
        replay_dir=cert_root / "scenarios" / "RDI-001" / "replay" / "improvement_intent",
        affected_layer="GOVERNANCE",
        affected_worker_family="REPLAY_DERIVED_IMPROVEMENT",
    )
    ppp = bridge_improvement_intent_to_ppp_candidate(
        bridge_id="PPP-CANDIDATE-REPLAY-DERIVED-CERTIFICATION-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        created_at=CREATED_AT,
        replay_dir=cert_root / "scenarios" / "RDI-001" / "replay" / "ppp_candidate",
        affected_lifecycle_stage="RESULT_VALIDATED",
    )
    return {
        "originating_replay_summary": {
            "source_replay_reference": replay["source_replay_reference"],
            "source_replay_hash": replay["source_replay_hash"],
            "observed_condition": replay["observed_condition"],
            "expected_condition": replay["expected_condition"],
        },
        "gap_detection_artifact": gap["gap_detection_artifact"],
        "gap_classification_artifact": gap["gap_classification_artifact"],
        "gap_evidence_artifact": gap["gap_evidence_artifact"],
        "improvement_intent_artifact": intent["improvement_intent_artifact"],
        "ppp_candidate_artifact": ppp["ppp_candidate_artifact"],
    }


def _execute_missing_approval_scenario(cert_root: Path, ppp_candidate: dict[str, Any]) -> dict[str, Any]:
    pending_approval = _human_approval(
        approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-PENDING-000001",
        source_ppp_candidate=ppp_candidate["ppp_candidate_id"],
        source_ppp_candidate_hash=ppp_candidate["artifact_hash"],
        approval_status="PENDING",
        approval_granted=False,
    )
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-REPLAY-DERIVED-NO-APPROVAL",
        ppp_candidate_artifact=ppp_candidate,
        human_approval_artifact=pending_approval,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=cert_root / "scenarios" / "RDI-002" / "replay" / "implementation_request",
    )
    return {
        "implementation_request_artifact": capture["implementation_request_artifact"],
        "approval_requirement_summary": {
            "approval_required": True,
            "approval_granted": False,
            "request_status": capture["request_status"],
            "implementation_prevented": capture["implementation_prevented"],
        },
    }


def _execute_approved_proposal_scenario(cert_root: Path, ppp_candidate: dict[str, Any]) -> dict[str, Any]:
    approval = _human_approval(
        approval_id="HUMAN-APPROVAL-REPLAY-DERIVED-IMPLEMENTATION-000001",
        source_ppp_candidate=ppp_candidate["ppp_candidate_id"],
        source_ppp_candidate_hash=ppp_candidate["artifact_hash"],
        approval_status=APPROVED,
        approval_granted=True,
    )
    capture = create_governed_implementation_request(
        request_id="IMPLEMENTATION-REQUEST-REPLAY-DERIVED-CERTIFICATION-000001",
        ppp_candidate_artifact=ppp_candidate,
        human_approval_artifact=approval,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=cert_root / "scenarios" / "RDI-003" / "replay" / "implementation_request",
    )
    request = capture["implementation_request_artifact"]
    return {
        "implementation_request_artifact": request,
        "approved_proposal_summary": {
            "approval_granted": request["human_approval_granted"],
            "request_status": request["request_status"],
            "ready_for_worker_request_generation": request["ready_for_worker_request_generation"],
            "implementation_executed": request["implementation_executed"],
            "code_modified": request["code_modified"],
            "governance_modified": request["governance_modified"],
            "worker_invoked": request["worker_invoked"],
            "provider_invoked": request["provider_invoked"],
        },
    }


def _reconstruct_replay(cert_root: Path) -> dict[str, Any]:
    reconstructed = {
        "gap_detection": reconstruct_replay_gap_detection_replay(
            cert_root / "scenarios" / "RDI-001" / "replay" / "gap_detection"
        ),
        "improvement_intent": reconstruct_replay_to_improvement_intent_replay(
            cert_root / "scenarios" / "RDI-001" / "replay" / "improvement_intent"
        ),
        "ppp_routing": reconstruct_improvement_intent_to_ppp_bridge_replay(
            cert_root / "scenarios" / "RDI-001" / "replay" / "ppp_candidate"
        ),
        "approval_required": reconstruct_governed_implementation_request_replay(
            cert_root / "scenarios" / "RDI-002" / "replay" / "implementation_request"
        ),
        "approved_proposal": reconstruct_governed_implementation_request_replay(
            cert_root / "scenarios" / "RDI-003" / "replay" / "implementation_request"
        ),
    }
    return {
        "replay_reconstructed": all(item.get("replay_visible") is True for item in reconstructed.values()),
        "reconstructed_paths": reconstructed,
        "reconstruction_hash": replay_hash(reconstructed),
    }


def _assertions(
    *,
    scenario: dict[str, Any],
    rejection: dict[str, Any],
    approved: dict[str, Any],
    replay_reconstruction: dict[str, Any],
    cert_root: Path,
) -> dict[str, bool]:
    gap = scenario["gap_detection_artifact"]
    intent = scenario["improvement_intent_artifact"]
    ppp = scenario["ppp_candidate_artifact"]
    rejected_request = rejection["implementation_request_artifact"]
    approved_request = approved["implementation_request_artifact"]
    return {
        "replay_observation_verified": bool(scenario["originating_replay_summary"]["source_replay_hash"]),
        "gap_detection_verified": gap["detection_status"] == GAPS_DETECTED and gap["gap_count"] > 0,
        "improvement_intent_created": intent["intent_status"] == IMPROVEMENT_INTENT_CREATED,
        "ppp_routing_verified": ppp["candidate_status"] == PPP_CANDIDATE_CREATED,
        "human_approval_required": ppp["human_approval_required"] is True
        and rejected_request["request_status"] == "FAILED_CLOSED",
        "proposal_only_behavior_verified": all(
            artifact.get("worker_invoked") is False
            and artifact.get("provider_invoked") is False
            and artifact.get("execution_requested") is False
            for artifact in (gap, intent, ppp, rejected_request, approved_request)
        ),
        "no_autonomous_modification": all(
            artifact.get(flag) is False
            for artifact in (ppp, rejected_request, approved_request)
            for flag in ("code_modified", "governance_modified")
            if flag in artifact
        ),
        "no_governance_bypass": ppp["human_approval_required"] is True
        and approved_request["human_approval_required"] is True,
        "no_authority_transfer": intent["self_modification_authority"] is False
        and approved_request["human_authority_preserved"] is True,
        "improvement_linked_to_originating_replay": ppp["source_replay_references"]
        == intent["source_replay_reference"],
        "improvement_evidence_traceable": ppp["source_gap_reference"] == intent["gap_reference"]
        and approved_request["source_gap_artifact"] == ppp["source_gap_reference"],
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"] is True,
        "replay_closure_verified": replay_reconstruction["reconstructed_paths"]["approved_proposal"][
            "replay_lineage_preserved"
        ]
        is True,
        "secret_free_evidence": _path_secret_free(cert_root),
    }


def _source_replay_artifact() -> dict[str, Any]:
    payload = {
        "execution_id": "EXECUTION-REPLAY-DERIVED-IMPROVEMENT-000001",
        "execution_status": "COMPLETED",
        "result_validation_status": "FAILED",
        "worker_execution_requested_by_replay_improvement": False,
        "provider_change_requested": False,
    }
    return {
        "evidence_id": "VALIDATION-FAIL-REPLAY-DERIVED-IMPROVEMENT-000001",
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": "replay/validation-fail-replay-derived-improvement-000001.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": "CHAIN-REPLAY-DERIVED-IMPROVEMENT-CERTIFICATION-000001",
        "observed_condition": "Replay records failed result validation.",
        "expected_condition": "Replay should record validated execution result.",
        "confidence": "DETERMINISTIC",
        "status": "FAILED",
    }


def _human_approval(
    *,
    approval_id: str,
    source_ppp_candidate: str,
    source_ppp_candidate_hash: str,
    approval_status: str,
    approval_granted: bool,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": approval_id,
        "approval_status": approval_status,
        "approval_granted": approval_granted,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "source_ppp_candidate": source_ppp_candidate,
        "source_ppp_candidate_hash": source_ppp_candidate_hash,
        "approval_scope": "CREATE_IMPLEMENTATION_REQUEST_ONLY",
        "implementation_execution_allowed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact.get("artifact_type"),
        "artifact_hash": artifact.get("artifact_hash"),
        "status": artifact.get("detection_status")
        or artifact.get("intent_status")
        or artifact.get("candidate_status")
        or artifact.get("request_status"),
        "human_approval_required": artifact.get("human_approval_required"),
        "worker_invoked": artifact.get("worker_invoked", False),
        "provider_invoked": artifact.get("provider_invoked", False),
        "execution_requested": artifact.get("execution_requested", False),
    }


def _blockers(assertions: dict[str, bool]) -> list[str]:
    return [key for key, value in assertions.items() if value is not True]


def _with_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(artifact)
    payload.pop("artifact_hash", None)
    payload["artifact_hash"] = replay_hash(payload)
    return payload


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
    leaked = [marker for marker in SECRET_MARKERS if marker in serialized]
    if leaked:
        raise ValueError("replay-derived improvement artifact contains secret marker")


def main() -> None:
    result = run_replay_derived_improvement_certification_v1()
    print("CERT_ROOT=" + result["cert_root"])
    print("FINAL_VERDICT=" + result["final_verdict"])


if __name__ == "__main__":
    main()
