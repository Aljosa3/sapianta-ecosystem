"""Fail-closed validator for SAPIANTA bridge protocol artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .hashing import is_valid_sha256, verify_hash
from .lifecycle import LIFECYCLE_STATES
from .lineage import validate_lineage
from .schemas import (
    ANALYSIS_CONTEXT_REQUIRED_FIELDS,
    PROPOSAL_TYPES,
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    REQUIRED_FIELDS_BY_ARTIFACT,
    RESULT_REQUIRED_FIELDS,
    RESULT_STATUSES,
    RISK_LEVELS,
    SUPPORTED_ARTIFACTS,
    TASK_REQUIRED_FIELDS,
    TASK_TYPES,
)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors)}


def _error(field: str, reason: str) -> dict[str, str]:
    return {"field": field, "reason": reason}


def _missing_required_errors(artifact: dict[str, Any], required_fields: tuple[str, ...]) -> list[dict[str, str]]:
    return [
        _error(field, "missing required field")
        for field in required_fields
        if field not in artifact
    ]


def _non_empty_string(artifact: dict[str, Any], field: str, errors: list[dict[str, str]]) -> None:
    if field in artifact and (not isinstance(artifact[field], str) or not artifact[field].strip()):
        errors.append(_error(field, "id must be non-empty"))


def _list_field(artifact: dict[str, Any], field: str, errors: list[dict[str, str]]) -> None:
    if field in artifact and not isinstance(artifact[field], list):
        errors.append(_error(field, "must be a list"))


def _dict_field(artifact: dict[str, Any], field: str, errors: list[dict[str, str]]) -> None:
    if field in artifact and not isinstance(artifact[field], dict):
        errors.append(_error(field, "must be an object"))


def _enum_field(
    artifact: dict[str, Any],
    field: str,
    allowed: tuple[str, ...],
    errors: list[dict[str, str]],
) -> None:
    if field in artifact and artifact[field] not in allowed:
        errors.append(_error(field, "invalid enum value"))


def _protocol_version(artifact: dict[str, Any], errors: list[dict[str, str]]) -> None:
    if artifact.get("protocol_version") != PROTOCOL_VERSION:
        errors.append(_error("protocol_version", "invalid protocol version"))


def _validate_hash_field(
    artifact: dict[str, Any],
    artifact_hashes: dict[str, Any],
    field: str,
    errors: list[dict[str, str]],
    *,
    verify_self_hash: bool = False,
) -> None:
    value = artifact_hashes.get(field)
    if not is_valid_sha256(value):
        errors.append(_error(f"artifact_hashes.{field}", "invalid sha256 hash"))
        return
    if verify_self_hash and not verify_hash(artifact, value, omit_hash_fields={field}):
        errors.append(_error(f"artifact_hashes.{field}", "hash mismatch"))


def _validate_task(artifact: dict[str, Any]) -> list[dict[str, str]]:
    errors = _missing_required_errors(artifact, TASK_REQUIRED_FIELDS)
    _protocol_version(artifact, errors)

    for field in ("task_id", "milestone_id", "objective"):
        _non_empty_string(artifact, field, errors)
    for field in (
        "target_paths",
        "allowed_operations",
        "forbidden_operations",
        "constraints",
        "expected_outputs",
    ):
        _list_field(artifact, field, errors)

    _enum_field(artifact, "task_type", TASK_TYPES, errors)
    _enum_field(artifact, "risk_level", RISK_LEVELS, errors)

    validation_required = artifact.get("validation_required")
    if isinstance(validation_required, dict):
        for field in ("pytest", "py_compile", "git_diff_check"):
            if field not in validation_required:
                errors.append(_error(f"validation_required.{field}", "missing required field"))
            elif not isinstance(validation_required[field], bool):
                errors.append(_error(f"validation_required.{field}", "must be boolean"))
    elif "validation_required" in artifact:
        errors.append(_error("validation_required", "must be an object"))

    if "human_approval_required" in artifact and not isinstance(artifact["human_approval_required"], bool):
        errors.append(_error("human_approval_required", "must be boolean"))

    lineage = validate_lineage(
        artifact.get("lineage"),
        required_fields=("parent_task_id", "source_result_id", "source_reflection_id"),
        nullable_fields=("parent_task_id", "source_result_id", "source_reflection_id"),
    )
    errors.extend(lineage.errors)
    return errors


def _validate_result(artifact: dict[str, Any]) -> list[dict[str, str]]:
    errors = _missing_required_errors(artifact, RESULT_REQUIRED_FIELDS)
    _protocol_version(artifact, errors)

    for field in ("task_id", "result_id", "execution_summary"):
        _non_empty_string(artifact, field, errors)
    for field in ("files_created", "files_modified", "files_deleted", "errors", "warnings"):
        _list_field(artifact, field, errors)
    for field in ("tests", "artifact_hashes"):
        _dict_field(artifact, field, errors)

    _enum_field(artifact, "status", RESULT_STATUSES, errors)

    tests = artifact.get("tests")
    if isinstance(tests, dict):
        for field in ("pytest", "py_compile", "git_diff_check"):
            if field not in tests:
                errors.append(_error(f"tests.{field}", "missing required field"))
            elif not isinstance(tests[field], dict):
                errors.append(_error(f"tests.{field}", "must be an object"))

    if artifact.get("status") in {"FAIL", "BLOCKED", "ESCALATED"}:
        if not artifact.get("errors") and not artifact.get("warnings"):
            errors.append(_error("errors", "failure status requires evidence"))

    artifact_hashes = artifact.get("artifact_hashes")
    if isinstance(artifact_hashes, dict):
        _validate_hash_field(artifact, artifact_hashes, "result_sha256", errors, verify_self_hash=True)
        _validate_hash_field(artifact, artifact_hashes, "task_sha256", errors)

    lineage = validate_lineage(
        artifact.get("lineage"),
        required_fields=("source_task_id", "parent_result_id"),
        nullable_fields=("parent_result_id",),
    )
    errors.extend(lineage.errors)
    return errors


def _validate_impact(
    artifact: dict[str, Any],
    field: str,
    errors: list[dict[str, str]],
) -> None:
    value = artifact.get(field)
    if not isinstance(value, dict):
        if field in artifact:
            errors.append(_error(field, "must be an object"))
        return
    if value.get("level") not in RISK_LEVELS:
        errors.append(_error(f"{field}.level", "invalid enum value"))
    if not isinstance(value.get("summary"), str) or not value.get("summary", "").strip():
        errors.append(_error(f"{field}.summary", "missing required field"))


def _validate_analysis_context(artifact: dict[str, Any]) -> list[dict[str, str]]:
    errors = _missing_required_errors(artifact, ANALYSIS_CONTEXT_REQUIRED_FIELDS)
    _protocol_version(artifact, errors)

    for field in ("task_id", "analysis_context_id"):
        _non_empty_string(artifact, field, errors)
    for field in ("risk_analysis", "opportunities"):
        _list_field(artifact, field, errors)
    for field in (
        "architectural_impact",
        "governance_impact",
        "recommended_next_milestone",
        "artifact_hashes",
    ):
        _dict_field(artifact, field, errors)

    if "interpretation_ready" in artifact and not isinstance(artifact["interpretation_ready"], bool):
        errors.append(_error("interpretation_ready", "must be boolean"))

    _validate_impact(artifact, "architectural_impact", errors)
    _validate_impact(artifact, "governance_impact", errors)

    next_milestone = artifact.get("recommended_next_milestone")
    if isinstance(next_milestone, dict):
        for field in ("milestone_id", "reason"):
            if not isinstance(next_milestone.get(field), str) or not next_milestone.get(field, "").strip():
                errors.append(_error(f"recommended_next_milestone.{field}", "missing required field"))

    artifact_hashes = artifact.get("artifact_hashes")
    if isinstance(artifact_hashes, dict):
        _validate_hash_field(
            artifact,
            artifact_hashes,
            "analysis_context_sha256",
            errors,
            verify_self_hash=True,
        )
        _validate_hash_field(artifact, artifact_hashes, "source_result_sha256", errors)

    lineage = validate_lineage(
        artifact.get("lineage"),
        required_fields=("source_task_id", "source_result_id"),
    )
    errors.extend(lineage.errors)
    return errors


def _validate_next_task_proposal(artifact: dict[str, Any]) -> list[dict[str, str]]:
    errors = _missing_required_errors(artifact, REQUIRED_FIELDS_BY_ARTIFACT["next_task_proposal.json"])
    _protocol_version(artifact, errors)

    for field in ("proposal_id", "recommended_action", "rationale"):
        _non_empty_string(artifact, field, errors)
    _enum_field(artifact, "proposal_type", PROPOSAL_TYPES, errors)

    if "approval_required" in artifact and artifact.get("approval_required") is not True:
        errors.append(_error("approval_required", "approval must be required"))
    if "allowed_to_execute_automatically" in artifact and artifact.get("allowed_to_execute_automatically") is not False:
        errors.append(
            _error(
                "allowed_to_execute_automatically",
                "automatic execution is forbidden in protocol v0.1",
            )
        )

    lineage = validate_lineage(
        artifact.get("lineage"),
        required_fields=("source_task_id", "source_result_id", "source_analysis_context_id"),
    )
    errors.extend(lineage.errors)
    return errors


def validate_artifact(artifact: Any, artifact_type: str) -> ValidationResult:
    if artifact_type not in SUPPORTED_ARTIFACTS:
        return ValidationResult(False, (_error("artifact_type", "unsupported artifact type"),))
    if not isinstance(artifact, dict):
        return ValidationResult(False, (_error("artifact", "malformed artifact"),))

    if "state" in artifact and artifact["state"] not in LIFECYCLE_STATES:
        return ValidationResult(False, (_error("state", "unknown lifecycle state"),))
    if "lifecycle_state" in artifact and artifact["lifecycle_state"] not in LIFECYCLE_STATES:
        return ValidationResult(False, (_error("lifecycle_state", "unknown lifecycle state"),))

    validators = {
        "task.json": _validate_task,
        "result.json": _validate_result,
        "analysis_context.json": _validate_analysis_context,
        "next_task_proposal.json": _validate_next_task_proposal,
    }
    errors = validators[artifact_type](artifact)
    return ValidationResult(not errors, tuple(errors))


def validate_json_text(raw_json: str, artifact_type: str) -> ValidationResult:
    try:
        artifact = json.loads(raw_json)
    except json.JSONDecodeError:
        return ValidationResult(False, (_error("json", "invalid JSON"),))
    return validate_artifact(artifact, artifact_type)


def validate_protocol_manifest(manifest: Any) -> ValidationResult:
    errors: list[dict[str, str]] = []
    if not isinstance(manifest, dict):
        return ValidationResult(False, (_error("manifest", "malformed manifest"),))
    if manifest.get("protocol_name") != PROTOCOL_NAME:
        errors.append(_error("protocol_name", "invalid protocol name"))
    if manifest.get("protocol_version") != PROTOCOL_VERSION:
        errors.append(_error("protocol_version", "invalid protocol version"))
    for field in ("fail_closed", "replay_required", "lineage_required"):
        if manifest.get(field) is not True:
            errors.append(_error(field, "must be true"))
    if tuple(manifest.get("supported_artifacts", ())) != SUPPORTED_ARTIFACTS:
        errors.append(_error("supported_artifacts", "unsupported artifact set"))
    if tuple(manifest.get("lifecycle_states", ())) != LIFECYCLE_STATES:
        errors.append(_error("lifecycle_states", "unsupported lifecycle state set"))
    return ValidationResult(not errors, tuple(errors))

