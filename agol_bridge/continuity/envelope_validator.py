"""Pure read-only operational loop envelope validator."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

VALID = "VALID"
INVALID_SCHEMA = "INVALID_SCHEMA"
MISSING_REFERENCE = "MISSING_REFERENCE"
HASH_MISMATCH = "HASH_MISMATCH"
AUTHORITY_BOUNDARY_VIOLATION = "AUTHORITY_BOUNDARY_VIOLATION"
REPLAY_REFERENCE_INVALID = "REPLAY_REFERENCE_INVALID"
LIFECYCLE_REFERENCE_INVALID = "LIFECYCLE_REFERENCE_INVALID"
SEMANTIC_REPLAY_OVERCLAIM = "SEMANTIC_REPLAY_OVERCLAIM"
NEXT_STEP_APPROVAL_CONFUSION = "NEXT_STEP_APPROVAL_CONFUSION"
PROVIDER_BOUNDARY_VIOLATION = "PROVIDER_BOUNDARY_VIOLATION"

VALIDATION_STATUSES = (
    VALID,
    INVALID_SCHEMA,
    MISSING_REFERENCE,
    HASH_MISMATCH,
    AUTHORITY_BOUNDARY_VIOLATION,
    REPLAY_REFERENCE_INVALID,
    LIFECYCLE_REFERENCE_INVALID,
    SEMANTIC_REPLAY_OVERCLAIM,
    NEXT_STEP_APPROVAL_CONFUSION,
    PROVIDER_BOUNDARY_VIOLATION,
)

REQUIRED_ENVELOPE_FIELDS = (
    "loop_id",
    "originating_human_request_ref",
    "semantic_context_ref",
    "task_package_ref",
    "result_package_ref",
    "lineage_id",
    "execution_provider_ref",
    "governance_state_ref",
    "replay_refs",
    "lifecycle_refs",
    "semantic_interpretation_boundary",
    "next_step_ref",
    "authority_boundary_statement",
    "created_at",
    "envelope_hash",
)

STATUS_PRECEDENCE = (
    INVALID_SCHEMA,
    MISSING_REFERENCE,
    HASH_MISMATCH,
    AUTHORITY_BOUNDARY_VIOLATION,
    REPLAY_REFERENCE_INVALID,
    LIFECYCLE_REFERENCE_INVALID,
    SEMANTIC_REPLAY_OVERCLAIM,
    NEXT_STEP_APPROVAL_CONFUSION,
    PROVIDER_BOUNDARY_VIOLATION,
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(value: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()}"


def _hashable_envelope(envelope: dict) -> dict:
    value = deepcopy(envelope)
    value.pop("envelope_hash", None)
    return value


def canonical_envelope_hash(envelope: dict) -> str:
    return canonical_hash(_hashable_envelope(envelope))


def _blank_report(envelope_id: str) -> dict:
    return {
        "validation_id": f"VALIDATION-{canonical_hash({'envelope_id': envelope_id})[7:31]}",
        "envelope_id": envelope_id,
        "status": VALID,
        "checks": [],
        "missing_references": [],
        "hash_mismatches": [],
        "authority_findings": [],
        "replay_findings": [],
        "lifecycle_findings": [],
        "semantic_findings": [],
        "provider_findings": [],
        "recommended_action": "Envelope is valid for read-only continuity planning.",
    }


def _add_check(report: dict, name: str, status: str, detail: str) -> None:
    report["checks"].append({"name": name, "status": status, "detail": detail})


def _set_failure(report: dict, status: str) -> None:
    current = report["status"]
    if current == VALID or STATUS_PRECEDENCE.index(status) < STATUS_PRECEDENCE.index(current):
        report["status"] = status


def _artifact(artifact_map: dict, collection: str, identifier: str) -> Any:
    value = artifact_map.get(collection, {})
    if isinstance(value, dict):
        return value.get(identifier)
    return None


def _validate_schema(envelope: Any, report: dict) -> bool:
    if not isinstance(envelope, dict):
        _set_failure(report, INVALID_SCHEMA)
        _add_check(report, "required envelope fields", INVALID_SCHEMA, "Envelope must be a JSON object.")
        return False
    missing = [field for field in REQUIRED_ENVELOPE_FIELDS if field not in envelope]
    if missing:
        _set_failure(report, INVALID_SCHEMA)
        _add_check(report, "required envelope fields", INVALID_SCHEMA, f"Missing fields: {', '.join(missing)}")
        return False
    typed_checks = {
        "task_package_ref": dict,
        "result_package_ref": dict,
        "execution_provider_ref": dict,
        "governance_state_ref": dict,
        "replay_refs": list,
        "lifecycle_refs": list,
        "semantic_interpretation_boundary": dict,
        "next_step_ref": dict,
        "authority_boundary_statement": str,
    }
    type_errors = [
        field for field, expected_type in typed_checks.items() if not isinstance(envelope.get(field), expected_type)
    ]
    if type_errors:
        _set_failure(report, INVALID_SCHEMA)
        _add_check(report, "required envelope fields", INVALID_SCHEMA, f"Invalid field types: {', '.join(type_errors)}")
        return False
    _add_check(report, "required envelope fields", VALID, "Required envelope fields are present.")
    return True


def _validate_envelope_hash(envelope: dict, report: dict) -> None:
    expected = canonical_envelope_hash(envelope)
    actual = envelope["envelope_hash"]
    if actual != expected:
        _set_failure(report, HASH_MISMATCH)
        report["hash_mismatches"].append({"field": "envelope_hash", "expected": expected, "actual": actual})
        _add_check(report, "deterministic envelope hash", HASH_MISMATCH, "Envelope hash mismatch.")
        return
    _add_check(report, "deterministic envelope hash", VALID, "Envelope hash matches canonical content.")


def _validate_package_reference(
    *,
    envelope: dict,
    artifact_map: dict,
    report: dict,
    ref_field: str,
    collection: str,
    id_field: str,
    hash_field: str,
    check_name: str,
) -> None:
    ref = envelope[ref_field]
    identifier = ref.get(id_field)
    package = _artifact(artifact_map, collection, identifier)
    if package is None:
        _set_failure(report, MISSING_REFERENCE)
        report["missing_references"].append({"type": collection, "id": identifier})
        _add_check(report, check_name, MISSING_REFERENCE, f"Missing {collection} reference: {identifier}")
        return
    expected_hash = ref.get(hash_field)
    actual_hash = canonical_hash(package)
    if expected_hash != actual_hash:
        _set_failure(report, HASH_MISMATCH)
        report["hash_mismatches"].append(
            {"field": f"{ref_field}.{hash_field}", "expected": actual_hash, "actual": expected_hash}
        )
        _add_check(report, check_name, HASH_MISMATCH, f"{collection} hash mismatch.")
        return
    _add_check(report, check_name, VALID, f"{collection} reference exists and hash matches.")


def _validate_replay_refs(envelope: dict, artifact_map: dict, report: dict) -> None:
    valid = True
    for ref in envelope["replay_refs"]:
        replay_id = ref.get("replay_id")
        record = _artifact(artifact_map, "replay_records", replay_id)
        if record is None:
            valid = False
            _set_failure(report, MISSING_REFERENCE)
            report["missing_references"].append({"type": "replay_records", "id": replay_id})
            continue
        if ref.get("reference_status") != "REFERENCED_NOT_MUTATED":
            valid = False
            _set_failure(report, REPLAY_REFERENCE_INVALID)
            report["replay_findings"].append({"replay_id": replay_id, "error": "replay reference is not read-only"})
    if valid:
        _add_check(report, "replay references", VALID, "Replay references exist and are read-only.")
    else:
        _add_check(report, "replay references", report["status"], "Replay reference validation failed.")


def _validate_lifecycle_refs(envelope: dict, artifact_map: dict, report: dict) -> None:
    valid = True
    lifecycle_records = artifact_map.get("lifecycle_records", [])
    for ref in envelope["lifecycle_refs"]:
        match = any(
            record.get("previous_state") == ref.get("previous_state")
            and record.get("next_state") == ref.get("next_state")
            for record in lifecycle_records
        )
        if not match:
            valid = False
            _set_failure(report, LIFECYCLE_REFERENCE_INVALID)
            report["lifecycle_findings"].append({"reference": deepcopy(ref), "error": "lifecycle reference missing"})
        if ref.get("reference_status") != "VISIBLE_APPEND_ONLY_REFERENCE":
            valid = False
            _set_failure(report, LIFECYCLE_REFERENCE_INVALID)
            report["lifecycle_findings"].append({"reference": deepcopy(ref), "error": "lifecycle reference not append-only"})
    if valid:
        _add_check(report, "lifecycle references", VALID, "Lifecycle references are consistent.")
    else:
        _add_check(report, "lifecycle references", LIFECYCLE_REFERENCE_INVALID, "Lifecycle reference validation failed.")


def _validate_authority_boundary(envelope: dict, report: dict) -> None:
    statement = envelope["authority_boundary_statement"].lower()
    required_terms = ("chatgpt", "aigol", "agol", "codex", "sidepanel", "observe")
    if not all(term in statement for term in required_terms):
        _set_failure(report, AUTHORITY_BOUNDARY_VIOLATION)
        report["authority_findings"].append({"field": "authority_boundary_statement", "error": "missing role boundary"})
        _add_check(report, "authority boundary statement", AUTHORITY_BOUNDARY_VIOLATION, "Authority boundary incomplete.")
        return
    _add_check(report, "authority boundary statement", VALID, "Authority boundary preserves role separation.")


def _validate_semantic_boundary(envelope: dict, report: dict) -> None:
    boundary = envelope["semantic_interpretation_boundary"]
    deterministic = boundary.get("semantic_replay_determinism")
    status = boundary.get("interpretation_status")
    if deterministic is not False:
        _set_failure(report, SEMANTIC_REPLAY_OVERCLAIM)
        report["semantic_findings"].append({"field": "semantic_replay_determinism", "error": "semantic replay overclaim"})
        _add_check(report, "semantic replay limitation", SEMANTIC_REPLAY_OVERCLAIM, "Semantic replay overclaim detected.")
        return
    if status != "NON_AUTHORITATIVE":
        _set_failure(report, AUTHORITY_BOUNDARY_VIOLATION)
        report["semantic_findings"].append({"field": "interpretation_status", "error": "semantic interpretation is authoritative"})
        _add_check(report, "semantic replay limitation", AUTHORITY_BOUNDARY_VIOLATION, "Semantic boundary is authoritative.")
        return
    _add_check(report, "semantic replay limitation", VALID, "Semantic reasoning is non-deterministic and non-authoritative.")


def _validate_next_step(envelope: dict, report: dict) -> None:
    next_step = envelope["next_step_ref"]
    if next_step.get("approval_granted") is not False or next_step.get("status") != "PROPOSED_NOT_APPROVED":
        _set_failure(report, NEXT_STEP_APPROVAL_CONFUSION)
        report["authority_findings"].append({"field": "next_step_ref", "error": "next step appears approved"})
        _add_check(report, "next-step synthesis is not approval", NEXT_STEP_APPROVAL_CONFUSION, "Next-step approval confusion.")
        return
    _add_check(report, "next-step synthesis is not approval", VALID, "Next step is proposed, not approved.")


def _validate_provider_boundary(envelope: dict, report: dict) -> None:
    provider = envelope["execution_provider_ref"]
    violations = []
    for field in ("governance_authority", "approval_authority", "replay_mutation_authority"):
        if provider.get(field) is not False:
            violations.append(field)
    if provider.get("provider_role") != "EXECUTION_ONLY":
        violations.append("provider_role")
    if "governed transport" not in str(provider.get("transport_requirement", "")).lower():
        violations.append("transport_requirement")
    if violations:
        _set_failure(report, PROVIDER_BOUNDARY_VIOLATION)
        report["provider_findings"].append({"fields": violations, "error": "provider boundary violation"})
        _add_check(report, "provider boundary consistency", PROVIDER_BOUNDARY_VIOLATION, "Provider boundary violation.")
        return
    _add_check(report, "provider boundary consistency", VALID, "Provider boundary is execution-only.")


def _recommended_action(status: str) -> str:
    if status == VALID:
        return "Envelope is valid for read-only continuity planning."
    return "Block envelope completion and review validation findings."


def validate_envelope(envelope: Any, artifact_map: dict) -> dict:
    envelope_copy = deepcopy(envelope)
    artifact_map_copy = deepcopy(artifact_map)
    envelope_id = envelope_copy.get("loop_id", "UNKNOWN") if isinstance(envelope_copy, dict) else "UNKNOWN"
    report = _blank_report(envelope_id)
    if not _validate_schema(envelope_copy, report):
        report["recommended_action"] = _recommended_action(report["status"])
        return report
    _validate_envelope_hash(envelope_copy, report)
    _validate_package_reference(
        envelope=envelope_copy,
        artifact_map=artifact_map_copy,
        report=report,
        ref_field="task_package_ref",
        collection="task_packages",
        id_field="task_id",
        hash_field="package_hash",
        check_name="referenced task package metadata",
    )
    _validate_package_reference(
        envelope=envelope_copy,
        artifact_map=artifact_map_copy,
        report=report,
        ref_field="result_package_ref",
        collection="result_packages",
        id_field="result_id",
        hash_field="package_hash",
        check_name="referenced result package metadata",
    )
    _validate_replay_refs(envelope_copy, artifact_map_copy, report)
    _validate_lifecycle_refs(envelope_copy, artifact_map_copy, report)
    _validate_authority_boundary(envelope_copy, report)
    _validate_semantic_boundary(envelope_copy, report)
    _validate_next_step(envelope_copy, report)
    _validate_provider_boundary(envelope_copy, report)
    report["recommended_action"] = _recommended_action(report["status"])
    return report
