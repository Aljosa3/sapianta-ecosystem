"""Pure read-only continuity report synthesis for AGOL Bridge."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .envelope_validator import canonical_hash

CONTINUITY_VALID = "CONTINUITY_VALID"
CONTINUITY_INCOMPLETE = "CONTINUITY_INCOMPLETE"
CONTINUITY_BOUNDARY_VIOLATION = "CONTINUITY_BOUNDARY_VIOLATION"
CONTINUITY_REPLAY_GAP = "CONTINUITY_REPLAY_GAP"
CONTINUITY_LIFECYCLE_GAP = "CONTINUITY_LIFECYCLE_GAP"
CONTINUITY_NON_DETERMINISTIC = "CONTINUITY_NON_DETERMINISTIC"
CONTINUITY_AUTHORITY_VIOLATION = "CONTINUITY_AUTHORITY_VIOLATION"

CONTINUITY_STATUSES = (
    CONTINUITY_VALID,
    CONTINUITY_INCOMPLETE,
    CONTINUITY_BOUNDARY_VIOLATION,
    CONTINUITY_REPLAY_GAP,
    CONTINUITY_LIFECYCLE_GAP,
    CONTINUITY_NON_DETERMINISTIC,
    CONTINUITY_AUTHORITY_VIOLATION,
)

CONTINUITY_STATUS_PRECEDENCE = (
    CONTINUITY_AUTHORITY_VIOLATION,
    CONTINUITY_BOUNDARY_VIOLATION,
    CONTINUITY_NON_DETERMINISTIC,
    CONTINUITY_REPLAY_GAP,
    CONTINUITY_LIFECYCLE_GAP,
    CONTINUITY_INCOMPLETE,
)

VALID_UPSTREAM_STATUSES = frozenset(
    {
        "VALID",
        "CONTINUITY_VALID",
    }
)

NON_DETERMINISTIC_UPSTREAM_STATUSES = frozenset(
    {
        "NON_DETERMINISTIC_REPORT",
        "CONTINUITY_NON_DETERMINISTIC",
    }
)

AUTHORITY_UPSTREAM_STATUSES = frozenset(
    {
        "AUTHORITY_BOUNDARY_VIOLATION",
        "CONTINUITY_AUTHORITY_VIOLATION",
    }
)


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return deepcopy(value)
    return [deepcopy(value)]


def _status_from_report(report: Any, field: str) -> str | None:
    if not isinstance(report, dict):
        return None
    status = report.get(field)
    return status if isinstance(status, str) else None


def _add_finding(findings: list[dict], *, status: str, field: str, detail: str) -> None:
    findings.append({"status": status, "field": field, "detail": detail})


def _highest_precedence(statuses: list[str]) -> str:
    failures = [status for status in statuses if status != CONTINUITY_VALID]
    if not failures:
        return CONTINUITY_VALID
    return min(failures, key=CONTINUITY_STATUS_PRECEDENCE.index)


def _recommended_action(status: str) -> str:
    if status == CONTINUITY_VALID:
        return "Continuity evidence is valid for read-only operational review."
    return "Block continuity closure and review report findings."


def _contains_forbidden_authority(statement: str) -> bool:
    lowered = statement.lower()
    forbidden = (
        "approval authority granted",
        "dispatch authority granted",
        "execution authority granted",
        "autonomous continuation authorized",
        "semantic authority granted",
    )
    return any(term in lowered for term in forbidden)


def _semantic_overclaim(statement: Any) -> bool:
    if isinstance(statement, dict):
        if statement.get("semantic_replay_determinism") is True:
            return True
        if statement.get("semantic_authority") is True:
            return True
    lowered = str(statement).lower()
    return "deterministic semantic replay" in lowered or "semantic authority granted" in lowered


def _summarize_replay(replay_references: Any, findings: list[dict], statuses: list[str]) -> dict:
    if replay_references is None:
        _add_finding(
            findings,
            status=CONTINUITY_INCOMPLETE,
            field="replay_references",
            detail="Replay references are missing.",
        )
        statuses.append(CONTINUITY_INCOMPLETE)
        return {"visible": False, "reference_count": 0, "gaps": ["missing replay references"]}

    refs = _as_list(replay_references)
    gaps = []
    for ref in refs:
        if not isinstance(ref, dict) or ref.get("reference_status") != "REFERENCED_NOT_MUTATED":
            gaps.append(deepcopy(ref))
    if not refs or gaps:
        _add_finding(
            findings,
            status=CONTINUITY_REPLAY_GAP,
            field="replay_references",
            detail="Replay references are absent or not marked as referenced without mutation.",
        )
        statuses.append(CONTINUITY_REPLAY_GAP)
    return {
        "visible": bool(refs) and not gaps,
        "reference_count": len(refs),
        "gaps": gaps,
        "mutated": False,
    }


def _summarize_lifecycle(lifecycle_references: Any, findings: list[dict], statuses: list[str]) -> dict:
    if lifecycle_references is None:
        _add_finding(
            findings,
            status=CONTINUITY_INCOMPLETE,
            field="lifecycle_references",
            detail="Lifecycle references are missing.",
        )
        statuses.append(CONTINUITY_INCOMPLETE)
        return {"visible": False, "reference_count": 0, "gaps": ["missing lifecycle references"]}

    refs = _as_list(lifecycle_references)
    gaps = []
    for ref in refs:
        if not isinstance(ref, dict) or ref.get("reference_status") != "VISIBLE_APPEND_ONLY_REFERENCE":
            gaps.append(deepcopy(ref))
    if not refs or gaps:
        _add_finding(
            findings,
            status=CONTINUITY_LIFECYCLE_GAP,
            field="lifecycle_references",
            detail="Lifecycle references are absent or not marked as append-only visibility references.",
        )
        statuses.append(CONTINUITY_LIFECYCLE_GAP)
    return {
        "visible": bool(refs) and not gaps,
        "reference_count": len(refs),
        "gaps": gaps,
        "mutated": False,
    }


def _summarize_authority(authority_boundary_statements: Any, findings: list[dict], statuses: list[str]) -> dict:
    if authority_boundary_statements is None:
        _add_finding(
            findings,
            status=CONTINUITY_INCOMPLETE,
            field="authority_boundary_statements",
            detail="Authority boundary statements are missing.",
        )
        statuses.append(CONTINUITY_INCOMPLETE)
        return {"visible": False, "violations": ["missing authority boundary statements"], "authority_created": False}

    statements = _as_list(authority_boundary_statements)
    violations = [statement for statement in statements if _contains_forbidden_authority(str(statement))]
    if violations:
        _add_finding(
            findings,
            status=CONTINUITY_AUTHORITY_VIOLATION,
            field="authority_boundary_statements",
            detail="Authority boundary statement implies forbidden authority.",
        )
        statuses.append(CONTINUITY_AUTHORITY_VIOLATION)
    return {
        "visible": bool(statements),
        "statement_count": len(statements),
        "violations": violations,
        "authority_created": False,
    }


def _summarize_semantic(semantic_boundary_statements: Any, findings: list[dict], statuses: list[str]) -> dict:
    if semantic_boundary_statements is None:
        _add_finding(
            findings,
            status=CONTINUITY_INCOMPLETE,
            field="semantic_boundary_statements",
            detail="Semantic boundary statements are missing.",
        )
        statuses.append(CONTINUITY_INCOMPLETE)
        return {"visible": False, "overclaims": ["missing semantic boundary statements"], "semantic_authority_created": False}

    statements = _as_list(semantic_boundary_statements)
    overclaims = [statement for statement in statements if _semantic_overclaim(statement)]
    if overclaims:
        _add_finding(
            findings,
            status=CONTINUITY_BOUNDARY_VIOLATION,
            field="semantic_boundary_statements",
            detail="Semantic boundary overclaims deterministic semantic replay or semantic authority.",
        )
        statuses.append(CONTINUITY_BOUNDARY_VIOLATION)
    return {
        "visible": bool(statements),
        "statement_count": len(statements),
        "overclaims": overclaims,
        "semantic_authority_created": False,
    }


def _summarize_lineage(lineage_references: Any, findings: list[dict], statuses: list[str]) -> dict:
    if lineage_references is None:
        _add_finding(
            findings,
            status=CONTINUITY_INCOMPLETE,
            field="lineage_references",
            detail="Lineage references are missing.",
        )
        statuses.append(CONTINUITY_INCOMPLETE)
        return {"visible": False, "reference_count": 0, "mutated": False}
    refs = _as_list(lineage_references)
    return {"visible": bool(refs), "reference_count": len(refs), "mutated": False}


def _summarize_report_statuses(
    envelope_validation_report: Any,
    validator_composition_report: Any,
    findings: list[dict],
    statuses: list[str],
) -> dict:
    envelope_status = _status_from_report(envelope_validation_report, "status")
    composition_status = _status_from_report(validator_composition_report, "aggregate_status")
    report_statuses = {
        "envelope_validation_status": envelope_status,
        "validator_composition_status": composition_status,
    }
    for field, status in report_statuses.items():
        if status is None:
            _add_finding(findings, status=CONTINUITY_INCOMPLETE, field=field, detail="Required report status is missing.")
            statuses.append(CONTINUITY_INCOMPLETE)
        elif status in VALID_UPSTREAM_STATUSES:
            continue
        elif status in NON_DETERMINISTIC_UPSTREAM_STATUSES:
            _add_finding(findings, status=CONTINUITY_NON_DETERMINISTIC, field=field, detail=f"{status} reported.")
            statuses.append(CONTINUITY_NON_DETERMINISTIC)
        elif status in AUTHORITY_UPSTREAM_STATUSES:
            _add_finding(findings, status=CONTINUITY_AUTHORITY_VIOLATION, field=field, detail=f"{status} reported.")
            statuses.append(CONTINUITY_AUTHORITY_VIOLATION)
        else:
            _add_finding(findings, status=CONTINUITY_BOUNDARY_VIOLATION, field=field, detail=f"Unknown status: {status}.")
            statuses.append(CONTINUITY_BOUNDARY_VIOLATION)
    return report_statuses


def synthesize_continuity_report(
    *,
    envelope_validation_report: Any = None,
    validator_composition_report: Any = None,
    replay_references: Any = None,
    lifecycle_references: Any = None,
    semantic_boundary_statements: Any = None,
    authority_boundary_statements: Any = None,
    lineage_references: Any = None,
    continuity_findings: Any = None,
    continuity_risks: Any = None,
) -> dict:
    envelope_report_copy = deepcopy(envelope_validation_report)
    composition_report_copy = deepcopy(validator_composition_report)
    findings = _as_list(continuity_findings)
    risks = _as_list(continuity_risks)
    statuses: list[str] = []

    report_statuses = _summarize_report_statuses(envelope_report_copy, composition_report_copy, findings, statuses)
    replay_summary = _summarize_replay(deepcopy(replay_references), findings, statuses)
    lifecycle_summary = _summarize_lifecycle(deepcopy(lifecycle_references), findings, statuses)
    authority_summary = _summarize_authority(deepcopy(authority_boundary_statements), findings, statuses)
    semantic_summary = _summarize_semantic(deepcopy(semantic_boundary_statements), findings, statuses)
    lineage_summary = _summarize_lineage(deepcopy(lineage_references), findings, statuses)

    for finding in findings:
        if isinstance(finding, dict) and finding.get("status") in CONTINUITY_STATUSES and finding["status"] != CONTINUITY_VALID:
            statuses.append(finding["status"])
    for risk in risks:
        if isinstance(risk, dict) and risk.get("status") in CONTINUITY_STATUSES and risk["status"] != CONTINUITY_VALID:
            statuses.append(risk["status"])

    aggregate_status = _highest_precedence(statuses)
    determinism_summary = {
        "deterministic_report_generation": True,
        "stable_status_precedence": True,
        "unknown_statuses_fail_closed": True,
        "source_statuses": report_statuses,
    }
    recommendations = [_recommended_action(aggregate_status)]
    report_seed = {
        "aggregate_governance_status": aggregate_status,
        "authority_boundary_summary": authority_summary,
        "continuity_findings": findings,
        "continuity_risks": risks,
        "determinism_summary": determinism_summary,
        "lifecycle_visibility_summary": lifecycle_summary,
        "lineage_summary": lineage_summary,
        "replay_visibility_summary": replay_summary,
        "semantic_boundary_summary": semantic_summary,
    }
    return {
        "continuity_report_id": f"CONTINUITY-{canonical_hash(report_seed)[7:31]}",
        "aggregate_governance_status": aggregate_status,
        "replay_visibility_summary": replay_summary,
        "lifecycle_visibility_summary": lifecycle_summary,
        "authority_boundary_summary": authority_summary,
        "semantic_boundary_summary": semantic_summary,
        "determinism_summary": determinism_summary,
        "continuity_findings": findings,
        "continuity_risks": risks,
        "continuity_recommendations": recommendations,
        "lineage_summary": lineage_summary,
    }


__all__ = [
    "CONTINUITY_AUTHORITY_VIOLATION",
    "CONTINUITY_BOUNDARY_VIOLATION",
    "CONTINUITY_INCOMPLETE",
    "CONTINUITY_LIFECYCLE_GAP",
    "CONTINUITY_NON_DETERMINISTIC",
    "CONTINUITY_REPLAY_GAP",
    "CONTINUITY_STATUSES",
    "CONTINUITY_VALID",
    "synthesize_continuity_report",
]
