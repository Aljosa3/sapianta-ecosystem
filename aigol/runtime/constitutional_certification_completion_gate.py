"""Fail-closed constitutional completion gate for governed development.

This adapter does not author G48 reports, assess Governance, issue
Certification, or decide promotion.  It validates and binds evidence produced
by those existing owners before emitting terminal workflow completion.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import re
from typing import Any

from aigol.runtime.constitutional_governance_certification import (
    ConstitutionalCertification,
    ConstitutionalCertificationStatus,
    validate_constitutional_certification,
)
from aigol.runtime.constitutional_replay_governance import (
    ConstitutionalGovernanceAssessment,
    ConstitutionalGovernanceStatus,
)
from aigol.runtime.governance_promotion_discipline import (
    ELIGIBLE,
    GovernancePromotionResult,
)
from aigol.runtime.governed_development_workflow_runtime import (
    AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
    reconstruct_governed_development_workflow_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION = (
    "CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_V1"
)
G48_COMPLETION_REPORT_EVIDENCE_V1 = "G48_COMPLETION_REPORT_EVIDENCE_V1"
CONSTITUTIONAL_COMPLETION_ARTIFACT_V1 = "CONSTITUTIONAL_COMPLETION_ARTIFACT_V1"
CONSTITUTIONAL_COMPLETION_FAILED_CLOSED = "CONSTITUTIONAL_COMPLETION_FAILED_CLOSED"

G48_HEADINGS = (
    "# 1. Implementation Summary",
    "# 2. Code Evidence",
    "# 3. Constitutional Self-Assessment",
    "# 4. Validation Matrix",
    "# 5. Repository Mutation Summary",
    "# 6. Certification Verdict",
)
NON_CERTIFYING_VERDICT_MARKERS = (
    "REQUIRES_REPAIR",
    "REQUIRES_REVISION",
    "FAILED",
    "INCOMPLETE",
    "PARTIALLY_CLOSED",
)
FINALIZATION_STEPS = (
    "pending_governed_development_recorded",
    "g48_completion_report_evidence_recorded",
    "constitutional_governance_assessment_recorded",
    "constitutional_certification_recorded",
    "governance_promotion_recorded",
    "constitutional_completion_recorded",
)


def create_g48_completion_report_evidence(
    *,
    report_path: str | Path,
    report_id: str,
    generation: str,
    certification_verdict: str,
    related_change_id: str,
    scope_binding_hash: str,
    governance_assessment_hash: str,
    constitutional_certification_hash: str,
    promotion_evidence_hash: str,
    created_at: str,
) -> dict[str, Any]:
    """Authenticate an external G48 report and bind it to one pending change."""

    path = Path(report_path)
    content = _read_report(path)
    _validate_g48_report(
        content,
        report_id=_require_string(report_id, "report_id"),
        generation=_require_string(generation, "generation"),
        certification_verdict=_require_string(
            certification_verdict, "certification_verdict"
        ),
    )
    artifact = {
        "artifact_type": G48_COMPLETION_REPORT_EVIDENCE_V1,
        "runtime_version": CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION,
        "report_id": report_id,
        "generation": generation,
        "report_path": str(path.resolve()),
        "report_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "certification_verdict": certification_verdict,
        "related_change_id": _require_string(related_change_id, "related_change_id"),
        "scope_binding_hash": _require_hash(scope_binding_hash, "scope_binding_hash"),
        "governance_assessment_hash": _require_hash(
            governance_assessment_hash, "governance_assessment_hash"
        ),
        "constitutional_certification_hash": _require_hash(
            constitutional_certification_hash, "constitutional_certification_hash"
        ),
        "promotion_evidence_hash": _require_hash(
            promotion_evidence_hash, "promotion_evidence_hash"
        ),
        "created_at": _require_string(created_at, "created_at"),
        "report_authored_by_workflow": False,
        "certification_created_by_workflow": False,
        "promotion_decided_by_workflow": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_g48_completion_report_evidence(
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Re-authenticate report bytes and immutable scope/evidence bindings."""

    _verify_artifact_hash(evidence)
    if evidence.get("artifact_type") != G48_COMPLETION_REPORT_EVIDENCE_V1:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_EVIDENCE_REQUIRED")
    path = Path(_require_string(evidence.get("report_path"), "report_path"))
    content = _read_report(path)
    if hashlib.sha256(content.encode("utf-8")).hexdigest() != evidence.get(
        "report_sha256"
    ):
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_TAMPERED")
    _validate_g48_report(
        content,
        report_id=evidence.get("report_id"),
        generation=evidence.get("generation"),
        certification_verdict=evidence.get("certification_verdict"),
    )
    for field in (
        "scope_binding_hash",
        "governance_assessment_hash",
        "constitutional_certification_hash",
        "promotion_evidence_hash",
    ):
        _require_hash(evidence.get(field), field)
    if any(
        evidence.get(field) is not False
        for field in (
            "report_authored_by_workflow",
            "certification_created_by_workflow",
            "promotion_decided_by_workflow",
        )
    ):
        raise FailClosedRuntimeError("FAIL_CLOSED_CERTIFICATION_OWNER_BOUNDARY")
    return deepcopy(evidence)


def finalize_governed_development_completion(
    *,
    finalization_id: str,
    governed_development_capture: dict[str, Any],
    g48_report_evidence: dict[str, Any],
    governance_assessment: ConstitutionalGovernanceAssessment,
    constitutional_certification: ConstitutionalCertification,
    promotion_evidence: GovernancePromotionResult | dict[str, Any],
    finalized_by: str,
    finalized_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Emit terminal completion only from exact external constitutional evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        pending = _validate_pending_capture(governed_development_capture)
        report = validate_g48_completion_report_evidence(g48_report_evidence)
        certification = validate_constitutional_certification(
            governance_assessment, constitutional_certification
        )
        promotion = (
            GovernancePromotionResult.from_dict(promotion_evidence)
            if isinstance(promotion_evidence, dict)
            else promotion_evidence
        )
        if not isinstance(promotion, GovernancePromotionResult):
            raise FailClosedRuntimeError("FAIL_CLOSED_PROMOTION_EVIDENCE_REQUIRED")
        change_id = pending["execution_id"]
        scope_hash = pending["reuse_proof_g47_scope_binding_hash"]
        if report.get("related_change_id") != change_id:
            raise FailClosedRuntimeError("FAIL_CLOSED_G48_CHANGE_ID_MISMATCH")
        if report.get("scope_binding_hash") != scope_hash:
            raise FailClosedRuntimeError("FAIL_CLOSED_G48_SCOPE_MISMATCH")
        if report.get("governance_assessment_hash") != governance_assessment.assessment_hash:
            raise FailClosedRuntimeError("FAIL_CLOSED_GOVERNANCE_ASSESSMENT_MISMATCH")
        if report.get("constitutional_certification_hash") != certification.certification_hash:
            raise FailClosedRuntimeError("FAIL_CLOSED_CERTIFICATION_MISMATCH")
        if report.get("promotion_evidence_hash") != promotion.evidence_hash:
            raise FailClosedRuntimeError("FAIL_CLOSED_PROMOTION_MISMATCH")
        if governance_assessment.constitutional_status is not ConstitutionalGovernanceStatus.COMPLIANT:
            raise FailClosedRuntimeError("FAIL_CLOSED_CONSTITUTIONAL_NON_COMPLIANCE")
        if certification.certification_status is not ConstitutionalCertificationStatus.COMPLIANCE_CERTIFIED:
            raise FailClosedRuntimeError("FAIL_CLOSED_CONSTITUTIONAL_NON_COMPLIANCE")
        if promotion.related_change_id != change_id or promotion.promotion_status != ELIGIBLE:
            raise FailClosedRuntimeError("FAIL_CLOSED_PROMOTION_NOT_ELIGIBLE")
        terminal = _terminal_artifact(
            finalization_id=finalization_id,
            pending=pending,
            report=report,
            governance_assessment=governance_assessment,
            certification=certification,
            promotion=promotion,
            finalized_by=finalized_by,
            finalized_at=finalized_at,
        )
        artifacts = [
            pending,
            report,
            governance_assessment.to_dict(),
            certification.to_dict(),
            promotion.to_dict(),
            terminal,
        ]
        for index, artifact in enumerate(artifacts):
            _persist_step(replay_path, index, FINALIZATION_STEPS[index], artifact)
        capture = {
            "runtime_version": CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION,
            "finalization_id": terminal["finalization_id"],
            "related_change_id": change_id,
            "completion_status": GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
            "constitutional_completion_reached": True,
            "promotion_eligible": True,
            "repository_mutated": False,
            "worker_invoked": False,
            "authorization_created": False,
            "constitutional_completion_artifact": terminal,
            "replay_reference": str(replay_path),
            "fail_closed": False,
            "failure_reason": None,
        }
        capture["capture_hash"] = replay_hash(capture)
        return capture
    except Exception as exc:
        failure = _failed_artifact(
            finalization_id=finalization_id,
            related_change_id=(governed_development_capture or {}).get("execution_id"),
            failure_reason=_failure_reason(exc),
            finalized_at=finalized_at,
        )
        _persist_failure_if_possible(replay_path, failure)
        capture = {
            "runtime_version": CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION,
            "finalization_id": failure["finalization_id"],
            "related_change_id": failure["related_change_id"],
            "completion_status": CONSTITUTIONAL_COMPLETION_FAILED_CLOSED,
            "constitutional_completion_reached": False,
            "promotion_eligible": False,
            "repository_mutated": False,
            "worker_invoked": False,
            "authorization_created": False,
            "constitutional_completion_artifact": failure,
            "replay_reference": str(replay_path),
            "fail_closed": True,
            "failure_reason": failure["failure_reason"],
        }
        capture["capture_hash"] = replay_hash(capture)
        return capture


def reconstruct_constitutional_completion_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(FINALIZATION_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        expected = deepcopy(wrapper)
        wrapper_hash = expected.pop("wrapper_hash", None)
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("constitutional completion replay ordering mismatch")
        if replay_hash(expected) != wrapper_hash:
            raise FailClosedRuntimeError("constitutional completion replay hash mismatch")
        wrappers.append(wrapper)
    terminal = wrappers[-1]["artifact"]
    _verify_artifact_hash(terminal)
    if terminal.get("completion_status") != GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED:
        raise FailClosedRuntimeError("constitutional completion terminal status missing")
    return {
        "finalization_id": terminal["finalization_id"],
        "related_change_id": terminal["related_change_id"],
        "completion_status": terminal["completion_status"],
        "constitutional_completion_reached": True,
        "promotion_eligible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_pending_capture(capture: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(capture, dict):
        raise FailClosedRuntimeError("FAIL_CLOSED_PENDING_WORKFLOW_REQUIRED")
    expected_capture = deepcopy(capture)
    actual_hash = expected_capture.pop("governed_development_capture_hash", None)
    if replay_hash(expected_capture) != actual_hash:
        raise FailClosedRuntimeError("FAIL_CLOSED_PENDING_WORKFLOW_TAMPERED")
    if capture.get("execution_status") != AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION:
        raise FailClosedRuntimeError("FAIL_CLOSED_PENDING_WORKFLOW_REQUIRED")
    replay = reconstruct_governed_development_workflow_replay(
        _require_string(
            capture.get("governed_development_replay_reference"),
            "governed_development_replay_reference",
        )
    )
    if replay.get("execution_status") != AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION:
        raise FailClosedRuntimeError("FAIL_CLOSED_PENDING_WORKFLOW_REQUIRED")
    outcome = deepcopy(capture.get("governed_development_outcome"))
    _verify_artifact_hash(outcome)
    return outcome


def _validate_g48_report(
    content: str,
    *,
    report_id: Any,
    generation: Any,
    certification_verdict: Any,
) -> None:
    headings = tuple(line.strip() for line in content.splitlines() if line.startswith("# "))
    if headings != G48_HEADINGS:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_STRUCTURE_INVALID")
    summary = content.split(G48_HEADINGS[1], 1)[0]
    required_summary = (
        f"Generation: {_require_string(generation, 'generation')}",
        "Report identity:",
        _require_string(report_id, "report_id"),
        "Reporting date:",
        "Constitutional baseline:",
        "Implementation contracts:",
    )
    if any(value not in summary for value in required_summary):
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_IDENTITY_INVALID")
    self_assessment = content.split(G48_HEADINGS[2], 1)[1].split(G48_HEADINGS[3], 1)[0]
    if "## Verified" not in self_assessment or "## Not Verified" not in self_assessment:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_SELF_ASSESSMENT_INVALID")
    validation = content.split(G48_HEADINGS[3], 1)[1].split(G48_HEADINGS[4], 1)[0]
    validation_results = re.findall(
        r"\|\s*`(PASS|FAIL|PARTIAL|NOT_RUN|BLOCKED|NOT_APPLICABLE)`\s*\|",
        validation,
    )
    if not validation_results:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_VALIDATION_MISSING")
    if any(
        result in {"FAIL", "PARTIAL", "NOT_RUN", "BLOCKED"}
        for result in validation_results
    ):
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_VALIDATION_INCOMPLETE")
    verdict_section = content.split(G48_HEADINGS[5], 1)[1].strip()
    verdict = _require_string(certification_verdict, "certification_verdict")
    if verdict_section != verdict:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_VERDICT_MISMATCH")
    if any(marker in verdict for marker in NON_CERTIFYING_VERDICT_MARKERS):
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_VERDICT_NOT_CERTIFIED")


def _terminal_artifact(**values: Any) -> dict[str, Any]:
    pending = values["pending"]
    report = values["report"]
    assessment = values["governance_assessment"]
    certification = values["certification"]
    promotion = values["promotion"]
    artifact = {
        "artifact_type": CONSTITUTIONAL_COMPLETION_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION,
        "finalization_id": _require_string(values["finalization_id"], "finalization_id"),
        "related_change_id": pending["execution_id"],
        "pending_outcome_hash": pending["artifact_hash"],
        "scope_binding_hash": pending["reuse_proof_g47_scope_binding_hash"],
        "g48_report_evidence_hash": report["artifact_hash"],
        "governance_assessment_hash": assessment.assessment_hash,
        "constitutional_certification_hash": certification.certification_hash,
        "promotion_evidence_hash": promotion.evidence_hash,
        "completion_status": GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
        "constitutional_completion_reached": True,
        "promotion_eligible": True,
        "report_authored_by_workflow": False,
        "certification_created_by_workflow": False,
        "promotion_decided_by_workflow": False,
        "repository_mutated": False,
        "worker_invoked": False,
        "authorization_created": False,
        "finalized_by": _require_string(values["finalized_by"], "finalized_by"),
        "finalized_at": _require_string(values["finalized_at"], "finalized_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(*, finalization_id: Any, related_change_id: Any, failure_reason: str, finalized_at: Any) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONSTITUTIONAL_COMPLETION_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION,
        "finalization_id": finalization_id if isinstance(finalization_id, str) else "FINALIZATION-INVALID",
        "related_change_id": related_change_id if isinstance(related_change_id, str) else None,
        "completion_status": CONSTITUTIONAL_COMPLETION_FAILED_CLOSED,
        "constitutional_completion_reached": False,
        "promotion_eligible": False,
        "repository_mutated": False,
        "worker_invoked": False,
        "authorization_created": False,
        "finalized_at": finalized_at if isinstance(finalized_at, str) else None,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _read_report(path: Path) -> str:
    try:
        if not path.is_file():
            raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_REQUIRED")
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FailClosedRuntimeError("FAIL_CLOSED_G48_REPORT_REQUIRED") from exc


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError("FAIL_CLOSED_DUPLICATE_FINALIZATION")
    path.mkdir(parents=True, exist_ok=True)


def _persist_step(path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(path: Path, failure: dict[str, Any]) -> None:
    try:
        _persist_step(path, len(FINALIZATION_STEPS) - 1, FINALIZATION_STEPS[-1], failure)
    except Exception:
        return


def _verify_artifact_hash(artifact: Any) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("constitutional completion artifact required")
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("constitutional completion artifact hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    normalized = _require_string(value, field_name)
    if not normalized.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a replay hash")
    return normalized


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"FAIL_CLOSED_CONSTITUTIONAL_COMPLETION: {exc}"


__all__ = [
    "AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION",
    "CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_VERSION",
    "CONSTITUTIONAL_COMPLETION_FAILED_CLOSED",
    "G48_COMPLETION_REPORT_EVIDENCE_V1",
    "create_g48_completion_report_evidence",
    "finalize_governed_development_completion",
    "reconstruct_constitutional_completion_replay",
    "validate_g48_completion_report_evidence",
]
