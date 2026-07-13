"""Deterministic, non-authoritative Platform Core change normalization."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.governed_repository_mutation_runtime import (
    GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
)
from aigol.runtime.implementation_manifest_runtime import (
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_CHANGE_NORMALIZATION_RUNTIME_VERSION = "G27_04_PLATFORM_CHANGE_NORMALIZATION_RUNTIME_V1"
NORMALIZED_CHANGE_ARTIFACT_V1 = "NORMALIZED_CHANGE_ARTIFACT_V1"
CHANGE_NORMALIZED = "CHANGE_NORMALIZED"
CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS = "CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "normalized_change_recorded"

ALLOWLISTED_SOURCE_ARTIFACT_TYPES = (
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_filesystem_mutation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_certification": False,
    "performs_impact_analysis": False,
    "plans_validation": False,
    "executes_validation": False,
}

OPERATION_TYPES = {
    "CREATE_ONLY": "CREATE",
    "CREATE_OR_REPLACE": "UPSERT",
    "REPLACE_CONTENT": "UPDATE",
}


def normalize_platform_change(
    *,
    normalization_id: str,
    source_artifact: dict[str, Any],
    source_reference: str,
    source_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Normalize one allowlisted change artifact without downstream analysis."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        normalized_id = _require_string(normalization_id, "normalization_id")
        normalized_reference = _require_string(source_reference, "source_reference")
        normalized_hash = _require_hash(source_hash, "source_hash")
        source = _validated_source(source_artifact, normalized_reference, normalized_hash)
        entries = _normalize_source_entries(source)
        unresolved = sorted(
            (deepcopy(item) for entry in entries for item in entry["unresolved_mappings"]),
            key=lambda item: (item["target_path"], item["field"], item["reason"]),
        )
        status = CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS if unresolved else CHANGE_NORMALIZED
        artifact = _normalized_change_artifact(
            normalization_id=normalized_id,
            source_reference=normalized_reference,
            source_hash=normalized_hash,
            source_artifact_type=source["artifact_type"],
            entries=entries,
            unresolved_mappings=unresolved,
            normalization_status=status,
            created_at=_require_string(created_at, "created_at"),
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            normalization_id=normalization_id,
            source_artifact=source_artifact,
            source_reference=source_reference,
            source_hash=source_hash,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def reconstruct_platform_change_normalization_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify normalized change replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("change normalization replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "change normalization replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("change normalization replay artifact must be a JSON object")
    _verify_normalized_artifact(artifact)
    return {
        "normalization_id": artifact["normalization_id"],
        "normalization_status": artifact["normalization_status"],
        "source_artifact_type": artifact["source_artifact_type"],
        "source_reference": artifact["source_reference"],
        "source_hash": artifact["source_hash"],
        "change_entries": deepcopy(artifact["change_entries"]),
        "change_entry_count": artifact["change_entry_count"],
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "unresolved_mapping_count": artifact["unresolved_mapping_count"],
        "normalized_change_hash": artifact["normalized_change_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["normalization_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def _validated_source(source_artifact: Any, source_reference: str, source_hash: str) -> dict[str, Any]:
    if not isinstance(source_artifact, dict):
        raise FailClosedRuntimeError("change normalization failed closed: source artifact must be a JSON object")
    source = deepcopy(source_artifact)
    artifact_type = _require_string(source.get("artifact_type"), "source artifact_type")
    if artifact_type not in ALLOWLISTED_SOURCE_ARTIFACT_TYPES:
        raise FailClosedRuntimeError("change normalization failed closed: unsupported source artifact type")
    _verify_hash(source, "artifact_hash", "change normalization failed closed: source artifact hash mismatch")
    if source["artifact_hash"] != source_hash:
        raise FailClosedRuntimeError("change normalization failed closed: source hash does not match source artifact")
    expected_reference = source.get("manifest_id") if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1 else source.get("proposal_id")
    if _require_string(expected_reference, "source artifact reference") != source_reference:
        raise FailClosedRuntimeError("change normalization failed closed: source reference mismatch")
    if source.get("replay_visible") is not True:
        raise FailClosedRuntimeError("change normalization failed closed: source artifact is not replay-visible")
    return source


def _normalize_source_entries(source: dict[str, Any]) -> list[dict[str, Any]]:
    if source["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        return _normalize_implementation_manifest(source)
    if source["artifact_type"] == GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1:
        return _normalize_mutation_proposal(source)
    raise FailClosedRuntimeError("change normalization failed closed: unsupported source artifact type")


def _normalize_implementation_manifest(source: dict[str, Any]) -> list[dict[str, Any]]:
    if source.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("change normalization failed closed: implementation manifest is not created")
    raw_entries = source.get("file_entries")
    raw_tests = source.get("test_entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise FailClosedRuntimeError("change normalization failed closed: implementation manifest files are required")
    if not isinstance(raw_tests, list):
        raise FailClosedRuntimeError("change normalization failed closed: implementation manifest tests must be a list")
    if source.get("file_count") != len(raw_entries) or source.get("test_count") != len(raw_tests):
        raise FailClosedRuntimeError("change normalization failed closed: implementation manifest counts mismatch")
    entries = []
    for item in [*raw_entries, *raw_tests]:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("change normalization failed closed: implementation entry must be an object")
        source_entry_hash_field = "test_entry_hash" if "test_entry_id" in item else "file_entry_hash"
        _verify_hash(item, source_entry_hash_field, "change normalization failed closed: implementation entry hash mismatch")
        content_hash = _require_hash(item.get("content_hash"), "content_hash")
        if replay_hash(item.get("content")) != content_hash:
            raise FailClosedRuntimeError("change normalization failed closed: implementation content hash mismatch")
        entries.append(
            _change_entry(
                source_entry_reference=_require_string(
                    item.get("test_entry_id") or item.get("file_entry_id"), "source_entry_reference"
                ),
                source_entry_hash=item[source_entry_hash_field],
                target_path=item.get("target_path"),
                source_operation=item.get("operation"),
                artifact_type=item.get("artifact_type"),
                before_hash=None,
                after_hash=content_hash,
                unresolved_fields=("before_hash",),
            )
        )
    return _sorted_unique_entries(entries)


def _normalize_mutation_proposal(source: dict[str, Any]) -> list[dict[str, Any]]:
    raw_entries = source.get("file_mutations")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise FailClosedRuntimeError("change normalization failed closed: mutation proposal entries are required")
    if source.get("file_mutation_count") != len(raw_entries):
        raise FailClosedRuntimeError("change normalization failed closed: mutation proposal count mismatch")
    entries = []
    for index, item in enumerate(raw_entries):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("change normalization failed closed: mutation entry must be an object")
        new_content_hash = _require_hash(item.get("new_content_hash"), "new_content_hash")
        if replay_hash(item.get("new_content")) != new_content_hash:
            raise FailClosedRuntimeError("change normalization failed closed: mutation content hash mismatch")
        if item.get("approved") is not True:
            raise FailClosedRuntimeError("change normalization failed closed: mutation entry is not approved")
        source_entry = {
            "target_path": item.get("target_path"),
            "operation": item.get("operation"),
            "new_content_hash": new_content_hash,
            "approved": True,
        }
        entries.append(
            _change_entry(
                source_entry_reference=f"{source['proposal_id']}:MUTATION-{index + 1:06d}",
                source_entry_hash=replay_hash(source_entry),
                target_path=item.get("target_path"),
                source_operation=item.get("operation"),
                artifact_type="REPOSITORY_FILE",
                before_hash=None,
                after_hash=new_content_hash,
                unresolved_fields=("before_hash", "artifact_type_detail"),
            )
        )
    target_paths = [_normalize_path(value) for value in source.get("target_paths", [])]
    if target_paths != [entry["target_path"] for entry in entries]:
        raise FailClosedRuntimeError("change normalization failed closed: mutation target paths mismatch")
    return _sorted_unique_entries(entries)


def _change_entry(
    *,
    source_entry_reference: str,
    source_entry_hash: str,
    target_path: Any,
    source_operation: Any,
    artifact_type: Any,
    before_hash: str | None,
    after_hash: str | None,
    unresolved_fields: tuple[str, ...],
) -> dict[str, Any]:
    path = _normalize_path(target_path)
    source_operation_text = _require_string(source_operation, "source operation")
    operation_type = OPERATION_TYPES.get(source_operation_text)
    if operation_type is None:
        raise FailClosedRuntimeError("change normalization failed closed: unsupported operation type")
    normalized_artifact_type = _normalize_artifact_type(artifact_type)
    unresolved = [
        {"target_path": path, "field": field, "reason": _unresolved_reason(field)}
        for field in unresolved_fields
    ]
    entry = {
        "source_entry_reference": _require_string(source_entry_reference, "source_entry_reference"),
        "source_entry_hash": _require_hash(source_entry_hash, "source_entry_hash"),
        "target_path": path,
        "source_operation": source_operation_text,
        "operation_type": operation_type,
        "artifact_type": normalized_artifact_type,
        "before_hash": _optional_hash(before_hash, "before_hash"),
        "after_hash": _optional_hash(after_hash, "after_hash"),
        "unresolved_mappings": unresolved,
    }
    entry["change_entry_hash"] = replay_hash(entry)
    return entry


def _sorted_unique_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda item: (item["target_path"], item["operation_type"], item["source_entry_reference"]))
    seen: set[str] = set()
    for entry in ordered:
        if entry["target_path"] in seen:
            raise FailClosedRuntimeError("change normalization failed closed: conflicting duplicate target path")
        seen.add(entry["target_path"])
    return ordered


def _normalized_change_artifact(
    *,
    normalization_id: str,
    source_reference: str,
    source_hash: str,
    source_artifact_type: str,
    entries: list[dict[str, Any]],
    unresolved_mappings: list[dict[str, str]],
    normalization_status: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": NORMALIZED_CHANGE_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_RUNTIME_VERSION,
        "normalization_id": normalization_id,
        "normalization_status": normalization_status,
        "source_artifact_type": source_artifact_type,
        "source_reference": source_reference,
        "source_hash": source_hash,
        "allowlisted_source_artifact_types": list(ALLOWLISTED_SOURCE_ARTIFACT_TYPES),
        "change_entries": deepcopy(entries),
        "change_entry_count": len(entries),
        "unresolved_mappings": deepcopy(unresolved_mappings),
        "unresolved_mapping_count": len(unresolved_mappings),
        "normalization_policy": {
            "repository_relative_paths_required": True,
            "deterministic_sorting": True,
            "duplicate_target_paths_rejected": True,
            "unsupported_operations_rejected": True,
            "source_hash_verification_required": True,
        },
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "validation_planned": False,
        "validation_executed": False,
        "impact_analysis_performed": False,
        "certification_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["normalized_change_hash"] = _normalized_change_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *, normalization_id: Any, source_artifact: Any, source_reference: Any, source_hash: Any, created_at: Any, failure_reason: str
) -> dict[str, Any]:
    source_type = source_artifact.get("artifact_type") if isinstance(source_artifact, dict) else "UNKNOWN"
    safe_source_hash = source_hash if isinstance(source_hash, str) and source_hash.startswith("sha256:") else None
    return _normalized_change_artifact(
        normalization_id=normalization_id.strip() if isinstance(normalization_id, str) and normalization_id.strip() else "UNKNOWN",
        source_reference=source_reference.strip() if isinstance(source_reference, str) and source_reference.strip() else "UNKNOWN",
        source_hash=safe_source_hash or replay_hash({"unverified_source": True}),
        source_artifact_type=source_type if isinstance(source_type, str) and source_type.strip() else "UNKNOWN",
        entries=[],
        unresolved_mappings=[],
        normalization_status=FAILED_CLOSED,
        created_at=created_at.strip() if isinstance(created_at, str) and created_at.strip() else "UNKNOWN",
        failure_reason=failure_reason,
    )


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_RUNTIME_VERSION,
        "normalized_change_artifact": deepcopy(artifact),
        "normalization_id": artifact["normalization_id"],
        "normalization_status": artifact["normalization_status"],
        "normalized_change_hash": artifact["normalized_change_hash"],
        "normalized_change_replay_reference": str(replay_path),
        "change_entries": deepcopy(artifact["change_entries"]),
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "fail_closed": artifact["normalization_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "impact_analysis_performed": False,
        "validation_planned": False,
        "validation_executed": False,
        "certification_performed": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _verify_normalized_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != NORMALIZED_CHANGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("change normalization artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "change normalization artifact hash mismatch")
    if artifact.get("normalized_change_hash") != _normalized_change_hash(artifact):
        raise FailClosedRuntimeError("normalized change hash mismatch")
    if artifact.get("replay_visible") is not True or artifact.get("read_only") is not True:
        raise FailClosedRuntimeError("normalized change artifact must be replay-visible and read-only")
    if any(value is not False for value in artifact.get("authority_flags", {}).values()):
        raise FailClosedRuntimeError("normalized change artifact cannot grant authority")


def _normalized_change_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_artifact_type": artifact["source_artifact_type"],
            "source_reference": artifact["source_reference"],
            "source_hash": artifact["source_hash"],
            "change_entries": artifact["change_entries"],
            "unresolved_mappings": artifact["unresolved_mappings"],
            "normalization_status": artifact["normalization_status"],
            "normalization_policy": artifact["normalization_policy"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _normalize_path(value: Any) -> str:
    text = _require_string(value, "target_path")
    if "\\" in text:
        raise FailClosedRuntimeError("change normalization failed closed: invalid repository-relative path")
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("change normalization failed closed: invalid repository-relative path")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise FailClosedRuntimeError("change normalization failed closed: invalid repository-relative path")
    return normalized


def _normalize_artifact_type(value: Any) -> str:
    text = _require_string(value, "artifact_type").upper().replace("-", "_").replace(" ", "_")
    if not all(character.isalnum() or character == "_" for character in text):
        raise FailClosedRuntimeError("change normalization failed closed: invalid artifact type")
    return text


def _unresolved_reason(field: str) -> str:
    if field == "before_hash":
        return "source artifact does not provide authoritative before-state hash"
    return "source artifact provides only generic repository file classification"


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {"replay_index": 0, "replay_step": REPLAY_STEP, "artifact": deepcopy(artifact)}
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("change normalization failed closed: replay artifact already exists")


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _optional_hash(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_hash(value, field)


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"change normalization failed closed: {field} must be a sha256 hash")
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"change normalization failed closed: {field} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"change normalization failed closed: {exc}" if str(exc) else "change normalization failed closed"
