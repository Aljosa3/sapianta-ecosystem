"""Pure read-only validator composition for AGOL Bridge continuity checks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .envelope_validator import canonical_hash

VALID = "VALID"
INVALID_COMPOSITION = "INVALID_COMPOSITION"
UNKNOWN_VALIDATOR = "UNKNOWN_VALIDATOR"
DUPLICATE_VALIDATOR = "DUPLICATE_VALIDATOR"
VALIDATOR_FAILED = "VALIDATOR_FAILED"
NON_DETERMINISTIC_REPORT = "NON_DETERMINISTIC_REPORT"
AUTHORITY_BOUNDARY_VIOLATION = "AUTHORITY_BOUNDARY_VIOLATION"

COMPOSITION_STATUSES = (
    VALID,
    INVALID_COMPOSITION,
    UNKNOWN_VALIDATOR,
    DUPLICATE_VALIDATOR,
    VALIDATOR_FAILED,
    NON_DETERMINISTIC_REPORT,
    AUTHORITY_BOUNDARY_VIOLATION,
)

COMPOSITION_STATUS_PRECEDENCE = (
    INVALID_COMPOSITION,
    UNKNOWN_VALIDATOR,
    DUPLICATE_VALIDATOR,
    NON_DETERMINISTIC_REPORT,
    AUTHORITY_BOUNDARY_VIOLATION,
    VALIDATOR_FAILED,
)


def _recommended_action(status: str) -> str:
    if status == VALID:
        return "Composition is valid for read-only validator aggregation."
    return "Block composition completion and review aggregate validation findings."


def _status_from_validator_report(report: Any) -> str:
    if not isinstance(report, dict):
        return VALIDATOR_FAILED
    status = report.get("status", VALIDATOR_FAILED)
    if status == VALID:
        return VALID
    if status == AUTHORITY_BOUNDARY_VIOLATION:
        return AUTHORITY_BOUNDARY_VIOLATION
    return VALIDATOR_FAILED


def _highest_precedence(statuses: list[str]) -> str:
    failures = [status for status in statuses if status != VALID]
    if not failures:
        return VALID
    return min(failures, key=COMPOSITION_STATUS_PRECEDENCE.index)


def _blank_report(
    *,
    envelope: Any,
    validator_ids: Any,
    aggregate_status: str = VALID,
    ordered_validator_reports: list[dict] | None = None,
    failures: list[dict] | None = None,
    authority_findings: list[dict] | None = None,
    determinism_findings: list[dict] | None = None,
) -> dict:
    reports = ordered_validator_reports if ordered_validator_reports is not None else []
    failure_items = failures if failures is not None else []
    authority_items = authority_findings if authority_findings is not None else []
    determinism_items = determinism_findings if determinism_findings is not None else []
    validator_order = list(validator_ids) if isinstance(validator_ids, list) else []
    composition_seed = {
        "aggregate_status": aggregate_status,
        "envelope_id": envelope.get("loop_id", "UNKNOWN") if isinstance(envelope, dict) else "UNKNOWN",
        "failures": failure_items,
        "validator_order": validator_order,
        "validator_reports": reports,
    }
    return {
        "composition_id": f"COMPOSITION-{canonical_hash(composition_seed)[7:31]}",
        "aggregate_status": aggregate_status,
        "validator_order": validator_order,
        "ordered_validator_reports": reports,
        "failures": failure_items,
        "authority_findings": authority_items,
        "determinism_findings": determinism_items,
        "recommended_action": _recommended_action(aggregate_status),
    }


def _invalid_report(*, envelope: Any, validator_ids: Any, status: str, failure: dict) -> dict:
    return _blank_report(
        envelope=envelope,
        validator_ids=validator_ids,
        aggregate_status=status,
        failures=[failure],
    )


def _duplicate_validator_ids(validator_ids: list[str]) -> list[str]:
    seen = set()
    duplicates = []
    for validator_id in validator_ids:
        if validator_id in seen and validator_id not in duplicates:
            duplicates.append(validator_id)
        seen.add(validator_id)
    return duplicates


def _validator_function(registry_entry: Any) -> Any:
    if callable(registry_entry):
        return registry_entry
    if isinstance(registry_entry, dict):
        return registry_entry.get("validator_function")
    return None


def compose_validators(
    *,
    envelope: Any,
    artifact_map: Any,
    validator_registry: Any,
    validator_ids: Any,
) -> dict:
    envelope_copy = deepcopy(envelope)
    artifact_map_copy = deepcopy(artifact_map)
    registry_copy = validator_registry
    validator_ids_copy = deepcopy(validator_ids)

    if not isinstance(registry_copy, dict) or not isinstance(validator_ids_copy, list):
        return _invalid_report(
            envelope=envelope_copy,
            validator_ids=validator_ids_copy,
            status=INVALID_COMPOSITION,
            failure={"status": INVALID_COMPOSITION, "error": "registry must be a dict and validator_ids must be a list"},
        )

    if not all(isinstance(validator_id, str) for validator_id in validator_ids_copy):
        return _invalid_report(
            envelope=envelope_copy,
            validator_ids=validator_ids_copy,
            status=INVALID_COMPOSITION,
            failure={"status": INVALID_COMPOSITION, "error": "validator ids must be strings"},
        )

    duplicates = _duplicate_validator_ids(validator_ids_copy)
    if duplicates:
        return _invalid_report(
            envelope=envelope_copy,
            validator_ids=validator_ids_copy,
            status=DUPLICATE_VALIDATOR,
            failure={"status": DUPLICATE_VALIDATOR, "validator_ids": duplicates},
        )

    unknown = [validator_id for validator_id in validator_ids_copy if validator_id not in registry_copy]
    if unknown:
        return _invalid_report(
            envelope=envelope_copy,
            validator_ids=validator_ids_copy,
            status=UNKNOWN_VALIDATOR,
            failure={"status": UNKNOWN_VALIDATOR, "validator_ids": unknown},
        )

    ordered_reports = []
    failures = []
    authority_findings = []
    determinism_findings = []
    statuses = []

    for validator_id in validator_ids_copy:
        validator = _validator_function(registry_copy[validator_id])
        if validator is None:
            statuses.append(INVALID_COMPOSITION)
            failures.append(
                {"status": INVALID_COMPOSITION, "validator_id": validator_id, "error": "validator is not callable"}
            )
            continue

        first_report = validator(deepcopy(envelope_copy), deepcopy(artifact_map_copy))
        second_report = validator(deepcopy(envelope_copy), deepcopy(artifact_map_copy))
        if first_report != second_report:
            report_copy = deepcopy(first_report)
            ordered_reports.append({"validator_id": validator_id, "report": report_copy})
            statuses.append(NON_DETERMINISTIC_REPORT)
            determinism_findings.append(
                {"validator_id": validator_id, "error": "validator returned non-deterministic reports"}
            )
            failures.append({"status": NON_DETERMINISTIC_REPORT, "validator_id": validator_id})
            continue

        report_copy = deepcopy(first_report)
        ordered_reports.append({"validator_id": validator_id, "report": report_copy})
        status = _status_from_validator_report(report_copy)
        statuses.append(status)
        if status != VALID:
            failures.append({"status": status, "validator_id": validator_id, "validator_status": report_copy.get("status")})
        if status == AUTHORITY_BOUNDARY_VIOLATION:
            authority_findings.append({"validator_id": validator_id, "status": AUTHORITY_BOUNDARY_VIOLATION})

    aggregate_status = _highest_precedence(statuses)
    return _blank_report(
        envelope=envelope_copy,
        validator_ids=validator_ids_copy,
        aggregate_status=aggregate_status,
        ordered_validator_reports=ordered_reports,
        failures=failures,
        authority_findings=authority_findings,
        determinism_findings=determinism_findings,
    )


__all__ = [
    "AUTHORITY_BOUNDARY_VIOLATION",
    "COMPOSITION_STATUSES",
    "DUPLICATE_VALIDATOR",
    "INVALID_COMPOSITION",
    "NON_DETERMINISTIC_REPORT",
    "UNKNOWN_VALIDATOR",
    "VALID",
    "VALIDATOR_FAILED",
    "compose_validators",
]
