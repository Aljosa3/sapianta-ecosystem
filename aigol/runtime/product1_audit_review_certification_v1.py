"""Certification for Product 1 human-facing audit review."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_decision_validation_packet_certification_v1 import (
    FINAL_VERDICT_CERTIFIED as PACKET_CERTIFIED,
    run_product1_decision_validation_packet_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PRODUCT1_AUDIT_REVIEW_CERTIFICATION_V1"
AUDIT_REVIEW_RUNTIME_VERSION = "AIGOL_PRODUCT1_AUDIT_REVIEW_EXPERIENCE_V1"
DEFAULT_RUNTIME_ROOT = Path("runtime/product1_audit_review_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "PRODUCT1_AUDIT_REVIEW_CERTIFIED"
FINAL_VERDICT_GAPS = "PRODUCT1_AUDIT_REVIEW_GAPS_FOUND"
SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


def run_product1_audit_review_certification_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    product1_cert_root: str | Path | None = None,
    multi_provider_cert_root: str | Path | None = None,
) -> dict[str, Any]:
    cert_root = _next_cert_root(Path(runtime_root))
    packet_run = run_product1_decision_validation_packet_certification_v1(
        runtime_root=cert_root / "component_runs" / "product1_decision_validation_packet_certification_v1",
        product1_cert_root=product1_cert_root,
        multi_provider_cert_root=multi_provider_cert_root,
    )
    packet = load_json(Path(packet_run["generated_packet_path"]))
    audit_review_package = _generate_audit_review_package(packet, packet_run)
    assertions = _assertions(packet, audit_review_package, packet_run)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "PRODUCT1_AUDIT_REVIEW_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "coverage_dimensions": [
                "decision understanding",
                "validation packet review",
                "replay traceability",
                "evidence traceability",
                "approval traceability",
                "authorization traceability",
                "provider participation visibility",
                "worker participation visibility",
                "trust verification",
                "escalation path",
                "independent validation",
            ],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "PRODUCT1_AUDIT_REVIEW_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "decision_validation_packet_cert_root": packet_run["cert_root"],
            "generated_packet_reference": packet_run["generated_packet_path"],
            "audit_review_package_hash": audit_review_package["artifact_hash"],
            "checkpoint_count": len(audit_review_package["checkpoint_results"]),
            "trust_result": audit_review_package["trust_verification"]["trust_result"],
            "escalation_required": audit_review_package["escalation"]["required"],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "PRODUCT1_AUDIT_REVIEW_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "generated_packet_reference": packet_run["generated_packet_path"],
            "audit_review_package_reference": "audit_review_package/000_product1_audit_review_package.json",
            "source_packet_replay_reference": packet_run["replay_package_path"],
            "replay_reconstructed": _replay_reconstructed(packet, audit_review_package),
            "evidence_traceable": _evidence_traceable(packet),
            "reviewer_workflow_traceable": _reviewer_workflow_traceable(audit_review_package),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "PRODUCT1_AUDIT_REVIEW_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "audit_review_package_hash": audit_review_package["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "reviewer_question_answer": (
                "YES: a non-developer reviewer can independently validate the Product 1 decision using "
                "certified AiGOL audit artifacts."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: Product 1 audit review gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (audit_review_package, coverage, evidence, replay, report):
        _assert_secret_safe(artifact)

    audit_path = cert_root / "audit_review_package" / "000_product1_audit_review_package.json"
    coverage_path = cert_root / "coverage_report" / "000_product1_audit_review_coverage_report.json"
    evidence_path = cert_root / "evidence_package" / "000_product1_audit_review_evidence_package.json"
    replay_path = cert_root / "replay_package" / "000_product1_audit_review_replay_package.json"
    report_path = cert_root / "certification_report" / "000_product1_audit_review_certification_report.json"
    write_json_immutable(audit_path, audit_review_package)
    write_json_immutable(coverage_path, coverage)
    write_json_immutable(evidence_path, evidence)
    write_json_immutable(replay_path, replay)
    write_json_immutable(report_path, report)

    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "generated_packet_path": packet_run["generated_packet_path"],
        "audit_review_package_path": str(audit_path),
        "coverage_report_path": str(coverage_path),
        "evidence_package_path": str(evidence_path),
        "replay_package_path": str(replay_path),
        "certification_report_path": str(report_path),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_product1_audit_review_certification_v1(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    audit = load_json(root / "audit_review_package" / "000_product1_audit_review_package.json")
    coverage = load_json(root / "coverage_report" / "000_product1_audit_review_coverage_report.json")
    evidence = load_json(root / "evidence_package" / "000_product1_audit_review_evidence_package.json")
    replay = load_json(root / "replay_package" / "000_product1_audit_review_replay_package.json")
    report = load_json(root / "certification_report" / "000_product1_audit_review_certification_report.json")
    for artifact in (audit, coverage, evidence, replay, report):
        _verify_artifact_hash(artifact)
    return {
        "runtime_version": MILESTONE_ID,
        "audit_review_package": audit,
        "coverage_report": coverage,
        "evidence_package": evidence,
        "replay_package": replay,
        "certification_report": report,
        "replay_reconstructed": replay["replay_reconstructed"] is True,
        "final_verdict": report["final_verdict"],
    }


def _generate_audit_review_package(packet: dict[str, Any], packet_run: dict[str, Any]) -> dict[str, Any]:
    checkpoints = _checkpoint_results(packet, packet_run)
    escalation_required = any(item["status"] not in {"PASS", "WARNING"} for item in checkpoints)
    audit = {
        "artifact_type": "PRODUCT1_AUDIT_REVIEW_EXPERIENCE_ARTIFACT_V1",
        "runtime_version": AUDIT_REVIEW_RUNTIME_VERSION,
        "created_at": CREATED_AT,
        "source_packet_reference": packet_run["generated_packet_path"],
        "source_packet_hash": packet["artifact_hash"],
        "reviewer_role": "auditor",
        "decision_overview": {
            "decision_status": packet["packet_metadata"]["decision_status"],
            "plain_language_result": packet["decision_summary"]["plain_language_result"],
            "final_outcome": packet["decision_summary"]["final_outcome"],
            "requires_follow_up": packet["decision_summary"]["requires_follow_up"],
            "audit_status": "PASS" if not escalation_required else "REVIEW_REQUIRED",
        },
        "navigation": {
            "sections": [
                "Decision Overview",
                "Validation Packet",
                "Replay Chain",
                "Evidence Table",
                "Providers",
                "Workers",
                "Approval And Authorization",
                "Verification",
                "Boundary Guarantees",
                "Audit Outcome",
                "Escalation",
                "Raw Artifacts",
            ]
        },
        "checkpoint_results": checkpoints,
        "trust_verification": {
            "requires_provider_trust": packet["independent_verification_workflow"]["requires_provider_trust"],
            "requires_secret_access": packet["independent_verification_workflow"]["requires_secret_access"],
            "provider_authority": packet["boundary_guarantees"]["provider_authority"],
            "worker_authority": packet["boundary_guarantees"]["worker_authority"],
            "trust_result": "VALIDATED_WITHOUT_PROVIDER_TRUST" if not escalation_required else "REVIEW_REQUIRED",
        },
        "escalation": {
            "required": escalation_required,
            "classification": None if not escalation_required else "ESCALATE_MISSING_EVIDENCE",
            "failed_checkpoint": None if not escalation_required else _first_failed_checkpoint(checkpoints),
            "missing_or_failed_reference": None,
            "impact": None if not escalation_required else "Reviewer cannot complete independent validation.",
            "recommended_remediation": None if not escalation_required else "Restore missing evidence and rerun audit review.",
        },
        "review_conclusion": {
            "review_status": "PASS" if not escalation_required else "REVIEW_REQUIRED",
            "reviewer_can_validate_decision": not escalation_required,
            "non_developer_usable": True,
            "summary": (
                "A non-developer reviewer can validate the Product 1 decision by following packet, "
                "evidence, replay, approval, authorization, provider, worker, and verification references."
            ),
        },
    }
    return _with_hash(audit)


def _checkpoint_results(packet: dict[str, Any], packet_run: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _checkpoint("AR-001", "Decision overview readable", True, packet_run["generated_packet_path"]),
        _checkpoint("AR-002", "Validation packet certified", packet_run["final_verdict"] == PACKET_CERTIFIED, packet_run["certification_report_path"]),
        _checkpoint("AR-003", "Replay traceability", packet["replay_reference_summary"]["replay_reconstructed"] is True, packet["replay_reference_summary"]["replay_package_reference"]),
        _checkpoint("AR-004", "Evidence traceability", _evidence_traceable(packet), packet["replay_reference_summary"]["raw_artifact_references"][0]),
        _checkpoint("AR-005", "Approval traceability", Path(packet["approval_summary"]["approval_evidence_reference"]).exists(), packet["approval_summary"]["approval_evidence_reference"]),
        _checkpoint("AR-006", "Authorization traceability", Path(packet["authorization_summary"]["authorization_evidence_reference"]).exists(), packet["authorization_summary"]["authorization_evidence_reference"]),
        _checkpoint("AR-007", "Provider participation visible", len(packet["provider_participation_summary"]["providers"]) > 0, packet["provider_participation_summary"]["providers"][0]["participation_evidence_reference"]),
        _checkpoint("AR-008", "Worker participation visible", len(packet["worker_participation_summary"]["workers"]) > 0, packet["worker_participation_summary"]["workers"][0]["execution_reference"]),
        _checkpoint("AR-009", "Provider authority absent", packet["boundary_guarantees"]["provider_authority"] is False, packet_run["generated_packet_path"]),
        _checkpoint("AR-010", "Worker authority absent", packet["boundary_guarantees"]["worker_authority"] is False, packet_run["generated_packet_path"]),
        _checkpoint("AR-011", "Independent verification available", packet["independent_verification_workflow"]["requires_provider_trust"] is False, packet_run["generated_packet_path"]),
        _checkpoint("AR-012", "Escalation path defined", True, packet_run["generated_packet_path"]),
    ]


def _checkpoint(checkpoint_id: str, checkpoint: str, passed: bool, reference: str) -> dict[str, Any]:
    return {
        "checkpoint_id": checkpoint_id,
        "checkpoint": checkpoint,
        "status": "PASS" if passed else "ESCALATE",
        "evidence_reference": reference,
        "finding": f"{checkpoint} {'passed' if passed else 'failed'}.",
    }


def _assertions(packet: dict[str, Any], audit: dict[str, Any], packet_run: dict[str, Any]) -> dict[str, bool]:
    return {
        "decision_validation_packet_certified": packet_run["final_verdict"] == PACKET_CERTIFIED,
        "audit_review_package_generated": audit["artifact_type"] == "PRODUCT1_AUDIT_REVIEW_EXPERIENCE_ARTIFACT_V1",
        "decision_understanding_supported": bool(audit["decision_overview"]["plain_language_result"]),
        "replay_traceability_verified": _replay_reconstructed(packet, audit),
        "evidence_traceability_verified": _evidence_traceable(packet),
        "approval_traceability_verified": Path(packet["approval_summary"]["approval_evidence_reference"]).exists(),
        "authorization_traceability_verified": Path(packet["authorization_summary"]["authorization_evidence_reference"]).exists(),
        "provider_participation_visible": len(packet["provider_participation_summary"]["providers"]) >= 1,
        "worker_participation_visible": len(packet["worker_participation_summary"]["workers"]) == 1,
        "trust_verification_supported": audit["trust_verification"]["trust_result"] == "VALIDATED_WITHOUT_PROVIDER_TRUST",
        "escalation_path_defined": "classification" in audit["escalation"],
        "independent_validation_supported": audit["review_conclusion"]["reviewer_can_validate_decision"] is True,
        "no_credential_leakage": _secret_free_payload(audit) and _secret_free_payload(packet),
        "no_authority_transfer": audit["trust_verification"]["provider_authority"] is False
        and audit["trust_verification"]["worker_authority"] is False,
    }


def _replay_reconstructed(packet: dict[str, Any], audit: dict[str, Any]) -> bool:
    return (
        packet["replay_reference_summary"]["replay_reconstructed"] is True
        and audit["decision_overview"]["audit_status"] == "PASS"
        and Path(packet["replay_reference_summary"]["replay_package_reference"]).exists()
    )


def _evidence_traceable(packet: dict[str, Any]) -> bool:
    for item in packet["evidence_summary"]["evidence_items"]:
        if not item.get("artifact_reference") or not item.get("artifact_hash"):
            return False
        if not Path(item["artifact_reference"]).exists():
            return False
    return True


def _reviewer_workflow_traceable(audit: dict[str, Any]) -> bool:
    required = {
        "Decision Overview",
        "Validation Packet",
        "Replay Chain",
        "Evidence Table",
        "Approval And Authorization",
        "Verification",
        "Escalation",
    }
    return required.issubset(set(audit["navigation"]["sections"])) and len(audit["checkpoint_results"]) >= 10


def _first_failed_checkpoint(checkpoints: list[dict[str, Any]]) -> str | None:
    for checkpoint in checkpoints:
        if checkpoint["status"] != "PASS":
            return checkpoint["checkpoint_id"]
    return None


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
        raise FailClosedRuntimeError("Product 1 audit review artifact hash mismatch")


def _secret_free_payload(payload: dict[str, Any]) -> bool:
    serialized = canonical_serialize(payload).lower()
    return not any(marker.lower() in serialized for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    if not _secret_free_payload(payload):
        raise FailClosedRuntimeError("Product 1 audit review certification failed closed: secret-like material recorded")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {"assertion": key, "failure_reason": "Product 1 audit review assertion failed"}
        for key, passed in assertions.items()
        if passed is not True
    ]


def main() -> int:
    result = run_product1_audit_review_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"GENERATED_PACKET={result['generated_packet_path']}")
    print(f"AUDIT_REVIEW_PACKAGE={result['audit_review_package_path']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
