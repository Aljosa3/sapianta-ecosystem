"""Deterministic Architectural Health advisory projection runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ARCHITECTURAL_HEALTH_ADVISORY_VERSION = "G9_07_ARCHITECTURAL_HEALTH_ADVISORY_IMPLEMENTATION_V1"
PLATFORM_DIGITAL_TWIN_EVIDENCE_BUNDLE_V1 = "PLATFORM_DIGITAL_TWIN_EVIDENCE_BUNDLE_V1"
ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1 = "ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1"
ARCHITECTURAL_HEALTH_ADVISORY_REPLAY_STEP = "architectural_health_advisory_projection_recorded"

NO_ADVISORY_FINDINGS = "NO_ADVISORY_FINDINGS"
ADVISORY_FINDINGS_PRESENT = "ADVISORY_FINDINGS_PRESENT"
GOVERNANCE_REVIEW_RECOMMENDED = "GOVERNANCE_REVIEW_RECOMMENDED"
ARCHITECTURE_REVIEW_REQUIRED = "ARCHITECTURE_REVIEW_REQUIRED"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

NON_AUTHORITY_STATEMENT = (
    "Architectural Health is deterministic advisory projection evidence only; "
    "it does not approve, reject, authorize, execute, mutate, repair, certify, "
    "replace Governance, or replace Replay."
)

FINDING_TYPES = {
    "responsibility_leakage",
    "ownership_inconsistency",
    "duplicated_responsibility",
    "architectural_boundary_violation",
    "certification_regression",
    "architectural_drift_indicator",
    "missing_replay_evidence",
    "missing_governance_evidence",
    "inconsistent_canonical_mapping",
    "known_gap_visibility",
}

CRITICAL_OWNERS = {"Governance", "Replay", "Human Authority"}


def create_platform_digital_twin_evidence_bundle(
    *,
    bundle_id: str,
    component_scope: str,
    evidence_records: list[dict[str, Any]],
    created_at: str,
    source_scope: list[str] | None = None,
) -> dict[str, Any]:
    """Create a deterministic Platform Digital Twin evidence bundle."""

    normalized_records = [_normalize_evidence_record(record) for record in _require_nonempty_list(evidence_records)]
    normalized_records.sort(
        key=lambda record: (
            record["source_path"],
            record["milestone_id"],
            record["evidence_type"],
            record["evidence_id"],
        )
    )
    if source_scope is None:
        normalized_source_scope = sorted({record["source_path"] for record in normalized_records})
    else:
        normalized_source_scope = sorted(_require_string(item, "source_scope item") for item in source_scope)
    bundle = {
        "artifact_type": PLATFORM_DIGITAL_TWIN_EVIDENCE_BUNDLE_V1,
        "runtime_version": ARCHITECTURAL_HEALTH_ADVISORY_VERSION,
        "bundle_id": _require_string(bundle_id, "bundle_id"),
        "component_scope": _require_string(component_scope, "component_scope"),
        "source_scope": normalized_source_scope,
        "evidence_records": normalized_records,
        "record_count": len(normalized_records),
        "created_at": _require_string(created_at, "created_at"),
        "deterministic_projection_input": True,
        "authority_bearing": False,
        "replay_visible": True,
    }
    bundle["artifact_hash"] = replay_hash(bundle)
    return bundle


def generate_architectural_health_advisory(
    *,
    projection_id: str,
    digital_twin_evidence: dict[str, Any],
    generated_at: str,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Generate an advisory-only Architectural Health projection."""

    _verify_artifact_hash(digital_twin_evidence, "Platform Digital Twin evidence")
    if digital_twin_evidence.get("artifact_type") != PLATFORM_DIGITAL_TWIN_EVIDENCE_BUNDLE_V1:
        raise FailClosedRuntimeError("architectural health requires Platform Digital Twin evidence bundle")
    records = digital_twin_evidence.get("evidence_records")
    if not isinstance(records, list) or not records:
        raise FailClosedRuntimeError("architectural health requires evidence records")

    normalized_records = [_normalize_evidence_record(record) for record in records]
    normalized_records.sort(
        key=lambda record: (
            record["source_path"],
            record["milestone_id"],
            record["evidence_type"],
            record["evidence_id"],
        )
    )
    findings = _derive_findings(normalized_records)
    report = {
        "artifact_type": ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1,
        "runtime_version": ARCHITECTURAL_HEALTH_ADVISORY_VERSION,
        "projection_id": _require_string(projection_id, "projection_id"),
        "projection_type": ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1,
        "projection_version": ARCHITECTURAL_HEALTH_ADVISORY_VERSION,
        "source_scope": deepcopy(digital_twin_evidence["source_scope"]),
        "component_scope": digital_twin_evidence["component_scope"],
        "generated_from": {
            "platform_digital_twin_bundle_id": digital_twin_evidence["bundle_id"],
            "platform_digital_twin_bundle_hash": digital_twin_evidence["artifact_hash"],
            "record_count": digital_twin_evidence["record_count"],
        },
        "finding_count": len(findings),
        "findings": findings,
        "overall_advisory_status": _overall_status(findings),
        "replay_references": _unique(record["replay_reference"] for record in normalized_records),
        "governance_references": _unique(record["governance_reference"] for record in normalized_records),
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "recommended_human_review": _recommended_human_review(findings),
        "deterministic": True,
        "advisory_only": True,
        "replay_visible": True,
        "approves_execution": False,
        "rejects_execution": False,
        "authorizes_execution": False,
        "modifies_implementation": False,
        "triggers_repairs": False,
        "moves_responsibilities": False,
        "certifies_artifacts": False,
        "replaces_governance": False,
        "replaces_replay": False,
        "generated_at": _require_string(generated_at, "generated_at"),
    }
    report["artifact_hash"] = replay_hash(report)
    if replay_dir is not None:
        persist_architectural_health_advisory_replay(replay_dir, report)
    return report


def persist_architectural_health_advisory_replay(replay_dir: str | Path, report: dict[str, Any]) -> dict[str, Any]:
    """Persist a replay-visible advisory projection wrapper."""

    verify_architectural_health_advisory_report(report)
    replay_path = Path(replay_dir)
    artifact_path = replay_path / f"000_{ARCHITECTURAL_HEALTH_ADVISORY_REPLAY_STEP}.json"
    if artifact_path.exists():
        raise FailClosedRuntimeError("architectural health advisory replay artifact already exists")
    wrapper = {
        "replay_index": 0,
        "replay_step": ARCHITECTURAL_HEALTH_ADVISORY_REPLAY_STEP,
        "artifact": deepcopy(report),
        "replay_service_version": ARCHITECTURAL_HEALTH_ADVISORY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(artifact_path, wrapper)
    return wrapper


def reconstruct_architectural_health_advisory_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the advisory replay summary from the persisted wrapper."""

    wrapper = load_json(Path(replay_dir) / f"000_{ARCHITECTURAL_HEALTH_ADVISORY_REPLAY_STEP}.json")
    _verify_wrapper_hash(wrapper)
    if wrapper.get("replay_index") != 0:
        raise FailClosedRuntimeError("architectural health advisory replay index mismatch")
    if wrapper.get("replay_step") != ARCHITECTURAL_HEALTH_ADVISORY_REPLAY_STEP:
        raise FailClosedRuntimeError("architectural health advisory replay step mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("architectural health advisory replay artifact must be an object")
    verify_architectural_health_advisory_report(artifact)
    return {
        "projection_id": artifact["projection_id"],
        "projection_type": artifact["projection_type"],
        "component_scope": artifact["component_scope"],
        "finding_count": artifact["finding_count"],
        "overall_advisory_status": artifact["overall_advisory_status"],
        "advisory_only": artifact["advisory_only"],
        "approves_execution": artifact["approves_execution"],
        "authorizes_execution": artifact["authorizes_execution"],
        "modifies_implementation": artifact["modifies_implementation"],
        "replaces_governance": artifact["replaces_governance"],
        "replaces_replay": artifact["replaces_replay"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_artifact_count": 1,
        "replay_hash": replay_hash([wrapper]),
    }


def verify_architectural_health_advisory_report(report: dict[str, Any]) -> None:
    """Verify advisory report hash and non-authority invariants."""

    _verify_artifact_hash(report, "Architectural Health advisory report")
    if report.get("artifact_type") != ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1:
        raise FailClosedRuntimeError("architectural health advisory report type mismatch")
    if report.get("projection_type") != ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1:
        raise FailClosedRuntimeError("architectural health advisory projection type mismatch")
    for field in (
        "approves_execution",
        "rejects_execution",
        "authorizes_execution",
        "modifies_implementation",
        "triggers_repairs",
        "moves_responsibilities",
        "certifies_artifacts",
        "replaces_governance",
        "replaces_replay",
    ):
        if report.get(field) is not False:
            raise FailClosedRuntimeError(f"architectural health advisory must not set {field}")
    if report.get("advisory_only") is not True or report.get("deterministic") is not True:
        raise FailClosedRuntimeError("architectural health advisory non-authority flags missing")


def _derive_findings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pending: list[dict[str, Any]] = []
    for record in records:
        if record["responsibility_status"] in {"leaked", "leakage_detected"}:
            pending.append(_finding(record, "responsibility_leakage"))
        if _owners_conflict(record):
            pending.append(_finding(record, "ownership_inconsistency"))
        if record["duplication_status"] in {"duplicated", "duplicate_detected"}:
            pending.append(_finding(record, "duplicated_responsibility"))
        if record["boundary_status"] in {"violated", "weakened", "bypassed"}:
            pending.append(_finding(record, "architectural_boundary_violation"))
        if record["certification_status"] in {"regression", "conflicting"}:
            pending.append(_finding(record, "certification_regression"))
        if record["implementation_scope_status"] in {"drift", "scope_expanded"}:
            pending.append(_finding(record, "architectural_drift_indicator"))
        if record["replay_status"] in {"missing", "stale", "partial", "conflicting"}:
            pending.append(_finding(record, "missing_replay_evidence"))
        if record["governance_status"] in {"missing", "stale", "partial", "conflicting"}:
            pending.append(_finding(record, "missing_governance_evidence"))
        if record["canonical_mapping_status"] in {"missing", "stale", "inconsistent", "conflicting"}:
            pending.append(_finding(record, "inconsistent_canonical_mapping"))
        if record["known_gap_status"] in {"hidden", "reframed", "missing"}:
            pending.append(_finding(record, "known_gap_visibility"))

    findings: list[dict[str, Any]] = []
    for index, finding in enumerate(pending, start=1):
        stable_input = {
            "finding_type": finding["finding_type"],
            "source_path": finding["evidence"]["source_path"],
            "milestone_id": finding["evidence"]["milestone_id"],
            "evidence_id": finding["evidence"]["evidence_id"],
        }
        finding["finding_id"] = f"AH-FINDING-{index:03d}-{replay_hash(stable_input)[7:19]}"
        findings.append(finding)
    return findings


def _finding(record: dict[str, Any], finding_type: str) -> dict[str, Any]:
    severity = _severity(finding_type, record)
    owner = _affected_owner(record)
    return {
        "finding_id": "PENDING",
        "finding_type": finding_type,
        "severity": severity,
        "affected_owner": owner,
        "affected_component": record["component_scope"],
        "evidence": {
            "evidence_id": record["evidence_id"],
            "source_path": record["source_path"],
            "source_title": record["source_title"],
            "milestone_id": record["milestone_id"],
            "source_class": record["source_class"],
            "final_verdict": record["final_verdict"],
            "evidence_type": record["evidence_type"],
        },
        "replay_references": _single_or_empty(record["replay_reference"]),
        "governance_references": _single_or_empty(record["governance_reference"]),
        "canonical_mapping_references": _single_or_empty(record["canonical_mapping_reference"]),
        "explanation": _explanation(finding_type, record),
        "recommended_human_review": _finding_review(severity, finding_type),
        "authority_boundary_statement": "This finding is advisory only and does not certify or authorize.",
    }


def _severity(finding_type: str, record: dict[str, Any]) -> str:
    if finding_type == "architectural_boundary_violation" and _affected_owner(record) in CRITICAL_OWNERS:
        return "critical"
    if finding_type in {
        "responsibility_leakage",
        "architectural_boundary_violation",
        "certification_regression",
        "missing_replay_evidence",
        "missing_governance_evidence",
    }:
        return "high"
    if finding_type in {
        "ownership_inconsistency",
        "duplicated_responsibility",
        "architectural_drift_indicator",
        "inconsistent_canonical_mapping",
    }:
        return "medium"
    return "low"


def _overall_status(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return NO_ADVISORY_FINDINGS
    severities = {finding["severity"] for finding in findings}
    types = {finding["finding_type"] for finding in findings}
    if "critical" in severities:
        return ARCHITECTURE_REVIEW_REQUIRED
    if {"missing_replay_evidence", "missing_governance_evidence"} & types:
        return INSUFFICIENT_EVIDENCE
    if "high" in severities:
        return GOVERNANCE_REVIEW_RECOMMENDED
    return ADVISORY_FINDINGS_PRESENT


def _recommended_human_review(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "No advisory findings were produced; proceed to normal architecture review."
    status = _overall_status(findings)
    if status == ARCHITECTURE_REVIEW_REQUIRED:
        return "Human review should request formal architecture review before certification."
    if status == INSUFFICIENT_EVIDENCE:
        return "Human review should request missing Governance or Replay evidence before certification."
    if status == GOVERNANCE_REVIEW_RECOMMENDED:
        return "Human review should route high-severity findings to Governance-visible architecture review."
    return "Human review should acknowledge advisory findings during architecture review."


def _finding_review(severity: str, finding_type: str) -> str:
    if severity == "critical":
        return f"Review {finding_type} with Governance before certification."
    if severity == "high":
        return f"Review {finding_type} in formal architecture review before certification."
    if severity == "medium":
        return f"Evaluate {finding_type} during architecture review."
    return f"Acknowledge {finding_type} if relevant to the milestone."


def _explanation(finding_type: str, record: dict[str, Any]) -> str:
    return (
        f"{finding_type} detected for {record['component_scope']} from "
        f"{record['source_path']} with expected owner {record['expected_owner']} "
        f"and observed owner {record['observed_owner']}."
    )


def _normalize_evidence_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("architectural health evidence record must be an object")
    normalized = {
        "evidence_id": _string_field(record, "evidence_id"),
        "source_path": _string_field(record, "source_path"),
        "source_title": _optional_string(record, "source_title", "UNKNOWN_SOURCE_TITLE"),
        "milestone_id": _string_field(record, "milestone_id"),
        "source_class": _optional_string(record, "source_class", "unknown"),
        "status": _optional_string(record, "status", "unknown"),
        "final_verdict": _optional_string(record, "final_verdict", "unknown"),
        "component_scope": _string_field(record, "component_scope"),
        "expected_owner": _optional_string(record, "expected_owner", "unknown"),
        "observed_owner": _optional_string(record, "observed_owner", "unknown"),
        "affected_owner": _optional_string(record, "affected_owner", ""),
        "affected_component": _optional_string(record, "affected_component", ""),
        "evidence_type": _string_field(record, "evidence_type"),
        "boundary": _optional_string(record, "boundary", "unknown"),
        "boundary_status": _optional_string(record, "boundary_status", "preserved"),
        "responsibility_status": _optional_string(record, "responsibility_status", "preserved"),
        "duplication_status": _optional_string(record, "duplication_status", "none"),
        "certification_status": _optional_string(record, "certification_status", "confirmed"),
        "replay_status": _optional_string(record, "replay_status", "present"),
        "governance_status": _optional_string(record, "governance_status", "present"),
        "canonical_mapping_status": _optional_string(record, "canonical_mapping_status", "consistent"),
        "implementation_scope_status": _optional_string(record, "implementation_scope_status", "within_scope"),
        "known_gap_status": _optional_string(record, "known_gap_status", "visible"),
        "replay_reference": _optional_string(record, "replay_reference", ""),
        "governance_reference": _optional_string(record, "governance_reference", ""),
        "canonical_mapping_reference": _optional_string(record, "canonical_mapping_reference", ""),
        "validation_evidence": _json_value(record.get("validation_evidence", {}), "validation_evidence"),
        "known_gaps": _json_value(record.get("known_gaps", []), "known_gaps"),
    }
    return normalized


def _owners_conflict(record: dict[str, Any]) -> bool:
    expected = record["expected_owner"]
    observed = record["observed_owner"]
    return expected not in {"", "unknown"} and observed not in {"", "unknown"} and expected != observed


def _affected_owner(record: dict[str, Any]) -> str:
    if record["affected_owner"]:
        return record["affected_owner"]
    if record["expected_owner"] != "unknown":
        return record["expected_owner"]
    return "Platform Core"


def _unique(values: Any) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value.strip()})


def _single_or_empty(value: str) -> list[str]:
    if value:
        return [value]
    return []


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be an object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("architectural health advisory replay hash mismatch")


def _require_nonempty_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("architectural health requires non-empty evidence records")
    return value


def _string_field(record: dict[str, Any], field: str) -> str:
    return _require_string(record.get(field), field)


def _optional_string(record: dict[str, Any], field: str, default: str) -> str:
    value = record.get(field, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise FailClosedRuntimeError(f"architectural health requires {field}")
    if not value.strip():
        return default
    return value.strip()


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"architectural health requires {field}")
    return value.strip()


def _json_value(value: Any, field: str) -> Any:
    try:
        replay_hash(value)
    except Exception as exc:
        raise FailClosedRuntimeError(f"architectural health requires serializable {field}") from exc
    return deepcopy(value)
