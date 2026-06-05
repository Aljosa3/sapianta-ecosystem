"""Replay-visible implementation manifest runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION = "AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_V1"
IMPLEMENTATION_MANIFEST_ARTIFACT_V1 = "IMPLEMENTATION_MANIFEST_ARTIFACT_V1"
IMPLEMENTATION_MANIFEST_CREATED = "IMPLEMENTATION_MANIFEST_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"
CREATE_ONLY = "CREATE_ONLY"

REPLAY_STEPS = (
    "implementation_manifest_recorded",
    "implementation_manifest_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_approval_creation": False,
    "authorizes_filesystem_mutation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_automatic_implementation": False,
}

FORBIDDEN_OPERATIONS = (
    "EXECUTION_AUTHORIZATION",
    "DISPATCH",
    "WORKER_INVOCATION",
    "PROVIDER_INVOCATION",
    "APPROVAL_CREATION",
    "FILESYSTEM_MUTATION",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
    "AUTOMATIC_IMPLEMENTATION",
    "DEPENDENCY_INSTALL",
    "DELETE",
    "RENAME",
    "MOVE",
    "RECURSIVE_CREATE",
)


def create_implementation_manifest(
    *,
    manifest_id: str,
    canonical_chain_id: str,
    implementation_bundle_id: str,
    source_candidate_reference: str,
    source_candidate_hash: str,
    implementation_handoff_reference: str,
    implementation_handoff_hash: str,
    provider_generation_authorization_reference: str,
    provider_generation_authorization_hash: str,
    provider_response_reference: str,
    provider_response_hash: str,
    target_domain: str,
    target_resource: str,
    target_worker: str | None,
    generated_files: list[dict[str, Any]],
    generated_tests: list[dict[str, Any]] | None,
    validation_requirements: list[str],
    known_gaps: list[str] | None,
    created_at: str,
    replay_dir: str | Path,
    operation_mode: str = CREATE_ONLY,
) -> dict[str, Any]:
    """Create a deterministic implementation manifest without mutating files."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        manifest = _manifest_artifact(
            manifest_id=manifest_id,
            canonical_chain_id=canonical_chain_id,
            implementation_bundle_id=implementation_bundle_id,
            source_candidate_reference=source_candidate_reference,
            source_candidate_hash=source_candidate_hash,
            implementation_handoff_reference=implementation_handoff_reference,
            implementation_handoff_hash=implementation_handoff_hash,
            provider_generation_authorization_reference=provider_generation_authorization_reference,
            provider_generation_authorization_hash=provider_generation_authorization_hash,
            provider_response_reference=provider_response_reference,
            provider_response_hash=provider_response_hash,
            target_domain=target_domain,
            target_resource=target_resource,
            target_worker=target_worker,
            generated_files=generated_files,
            generated_tests=generated_tests or [],
            validation_requirements=validation_requirements,
            known_gaps=known_gaps or [],
            created_at=created_at,
            operation_mode=operation_mode,
            manifest_status=IMPLEMENTATION_MANIFEST_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(manifest)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], manifest)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(manifest, returned, replay_path)
    except Exception as exc:
        manifest = _failed_manifest_artifact(
            manifest_id=manifest_id,
            canonical_chain_id=canonical_chain_id,
            implementation_bundle_id=implementation_bundle_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(manifest)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], manifest)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(manifest, returned, replay_path)


def reconstruct_implementation_manifest_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct implementation manifest replay evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation manifest replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation manifest replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    manifest = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError("implementation manifest returned reference mismatch")
    if returned.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError("implementation manifest returned artifact hash mismatch")
    if returned.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError("implementation manifest returned manifest hash mismatch")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("implementation manifest hash mismatch")
    return {
        "manifest_id": manifest["manifest_id"],
        "manifest_status": manifest["manifest_status"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "file_entries": deepcopy(manifest["file_entries"]),
        "test_entries": deepcopy(manifest["test_entries"]),
        "file_count": manifest["file_count"],
        "test_count": manifest["test_count"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "source_candidate_reference": manifest["source_candidate_reference"],
        "implementation_handoff_reference": manifest["implementation_handoff_reference"],
        "provider_generation_authorization_reference": manifest["provider_generation_authorization_reference"],
        "provider_response_reference": manifest["provider_response_reference"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_authorized": False,
        "authority_flags": deepcopy(manifest["authority_flags"]),
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": manifest["failure_reason"],
    }


def _manifest_artifact(
    *,
    manifest_id: str,
    canonical_chain_id: str,
    implementation_bundle_id: str,
    source_candidate_reference: str,
    source_candidate_hash: str,
    implementation_handoff_reference: str,
    implementation_handoff_hash: str,
    provider_generation_authorization_reference: str,
    provider_generation_authorization_hash: str,
    provider_response_reference: str,
    provider_response_hash: str,
    target_domain: str,
    target_resource: str,
    target_worker: str | None,
    generated_files: list[dict[str, Any]],
    generated_tests: list[dict[str, Any]],
    validation_requirements: list[str],
    known_gaps: list[str],
    created_at: str,
    operation_mode: str,
    manifest_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    if operation_mode != CREATE_ONLY:
        raise FailClosedRuntimeError("implementation manifest failed closed: only CREATE_ONLY is supported")
    file_entries = _file_entries(generated_files)
    test_entries = _test_entries(generated_tests, file_entries)
    validation = _string_list(validation_requirements, "validation_requirements", allow_empty=False)
    gaps = _string_list(known_gaps, "known_gaps", allow_empty=True)
    artifact = {
        "artifact_type": IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION,
        "manifest_id": _require_string(manifest_id, "manifest_id"),
        "created_at": _require_string(created_at, "created_at"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "implementation_bundle_id": _require_string(implementation_bundle_id, "implementation_bundle_id"),
        "source_candidate_reference": _require_string(source_candidate_reference, "source_candidate_reference"),
        "source_candidate_hash": _require_hash(source_candidate_hash, "source_candidate_hash"),
        "implementation_handoff_reference": _require_string(
            implementation_handoff_reference, "implementation_handoff_reference"
        ),
        "implementation_handoff_hash": _require_hash(implementation_handoff_hash, "implementation_handoff_hash"),
        "provider_generation_authorization_reference": _require_string(
            provider_generation_authorization_reference, "provider_generation_authorization_reference"
        ),
        "provider_generation_authorization_hash": _require_hash(
            provider_generation_authorization_hash, "provider_generation_authorization_hash"
        ),
        "provider_response_reference": _require_string(provider_response_reference, "provider_response_reference"),
        "provider_response_hash": _require_hash(provider_response_hash, "provider_response_hash"),
        "target_domain": _require_string(target_domain, "target_domain"),
        "target_resource": _require_string(target_resource, "target_resource"),
        "target_worker": target_worker.strip() if isinstance(target_worker, str) and target_worker.strip() else None,
        "operation_mode": operation_mode,
        "file_entries": file_entries,
        "test_entries": test_entries,
        "file_count": len(file_entries),
        "test_count": len(test_entries),
        "validation_requirements": validation,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "known_gaps": gaps,
        "manifest_status": manifest_status,
        "read_only": True,
        "replay_visible": True,
        "content_bearing_manifest": True,
        "filesystem_mutated": False,
        "execution_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["implementation_manifest_hash"] = _compute_manifest_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_manifest_artifact(
    *,
    manifest_id: str,
    canonical_chain_id: str,
    implementation_bundle_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    fallback_hash = replay_hash({"failed": True, "reason": failure_reason})
    artifact = {
        "artifact_type": IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION,
        "manifest_id": manifest_id if isinstance(manifest_id, str) and manifest_id.strip() else "UNKNOWN",
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "UNKNOWN",
        "canonical_chain_id": canonical_chain_id
        if isinstance(canonical_chain_id, str) and canonical_chain_id.strip()
        else "UNKNOWN",
        "implementation_bundle_id": implementation_bundle_id
        if isinstance(implementation_bundle_id, str) and implementation_bundle_id.strip()
        else "UNKNOWN",
        "source_candidate_reference": "UNKNOWN",
        "source_candidate_hash": fallback_hash,
        "implementation_handoff_reference": "UNKNOWN",
        "implementation_handoff_hash": fallback_hash,
        "provider_generation_authorization_reference": "UNKNOWN",
        "provider_generation_authorization_hash": fallback_hash,
        "provider_response_reference": "UNKNOWN",
        "provider_response_hash": fallback_hash,
        "target_domain": "UNKNOWN",
        "target_resource": "UNKNOWN",
        "target_worker": None,
        "operation_mode": CREATE_ONLY,
        "file_entries": [],
        "test_entries": [],
        "file_count": 0,
        "test_count": 0,
        "validation_requirements": [],
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "known_gaps": [],
        "manifest_status": FAILED_CLOSED,
        "read_only": True,
        "replay_visible": True,
        "content_bearing_manifest": False,
        "filesystem_mutated": False,
        "execution_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["implementation_manifest_hash"] = _compute_manifest_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _file_entries(generated_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(generated_files, list) or not generated_files:
        raise FailClosedRuntimeError("implementation manifest failed closed: generated_files are required")
    entries: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for index, file_item in enumerate(sorted(generated_files, key=lambda item: str(item.get("target_path", "")))):
        if not isinstance(file_item, dict):
            raise FailClosedRuntimeError("implementation manifest failed closed: generated file must be a JSON object")
        path = _normalize_target_path(file_item.get("target_path"))
        if path in seen_paths:
            raise FailClosedRuntimeError("implementation manifest failed closed: duplicate target path")
        seen_paths.add(path)
        content = _require_content(file_item.get("content"), "generated file content")
        artifact_type = _require_string(file_item.get("artifact_type"), "artifact_type")
        operation = _require_string(file_item.get("operation", CREATE_ONLY), "operation")
        if operation != CREATE_ONLY:
            raise FailClosedRuntimeError("implementation manifest failed closed: file operation must be CREATE_ONLY")
        validation_requirements = _string_list(
            file_item.get("validation_requirements", []), "file validation_requirements", allow_empty=True
        )
        entry = {
            "file_entry_id": file_item.get("file_entry_id")
            if isinstance(file_item.get("file_entry_id"), str) and file_item["file_entry_id"].strip()
            else f"FILE-{index + 1:06d}",
            "target_path": path,
            "artifact_type": artifact_type,
            "operation": operation,
            "content_encoding": "utf-8",
            "content": content,
            "content_hash": replay_hash(content),
            "content_size_bytes": len(content.encode("utf-8")),
            "source_segment_reference": _optional_string(file_item.get("source_segment_reference")),
            "preflight_target_state": file_item.get("preflight_target_state", "MUST_NOT_EXIST"),
            "validation_requirements": validation_requirements,
            "authority_flags": deepcopy(AUTHORITY_FLAGS),
        }
        if entry["preflight_target_state"] != "MUST_NOT_EXIST":
            raise FailClosedRuntimeError("implementation manifest failed closed: CREATE_ONLY target must not exist")
        entry["file_entry_hash"] = replay_hash(entry)
        entries.append(entry)
    return entries


def _test_entries(generated_tests: list[dict[str, Any]], file_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(generated_tests, list):
        raise FailClosedRuntimeError("implementation manifest failed closed: generated_tests must be a list")
    file_ids = {entry["file_entry_id"] for entry in file_entries}
    entries: list[dict[str, Any]] = []
    seen_paths: set[str] = {entry["target_path"] for entry in file_entries}
    for index, test_item in enumerate(sorted(generated_tests, key=lambda item: str(item.get("target_path", "")))):
        if not isinstance(test_item, dict):
            raise FailClosedRuntimeError("implementation manifest failed closed: generated test must be a JSON object")
        path = _normalize_target_path(test_item.get("target_path"))
        if path in seen_paths:
            raise FailClosedRuntimeError("implementation manifest failed closed: duplicate target path")
        seen_paths.add(path)
        content = _require_content(test_item.get("content"), "generated test content")
        tested_entries = _string_list(test_item.get("tests_file_entries", []), "tests_file_entries", allow_empty=False)
        if any(entry_id not in file_ids for entry_id in tested_entries):
            raise FailClosedRuntimeError("implementation manifest failed closed: test references unknown file entry")
        operation = _require_string(test_item.get("operation", CREATE_ONLY), "test operation")
        if operation != CREATE_ONLY:
            raise FailClosedRuntimeError("implementation manifest failed closed: test operation must be CREATE_ONLY")
        entry = {
            "test_entry_id": test_item.get("test_entry_id")
            if isinstance(test_item.get("test_entry_id"), str) and test_item["test_entry_id"].strip()
            else f"TEST-{index + 1:06d}",
            "target_path": path,
            "artifact_type": _require_string(test_item.get("artifact_type", "PYTEST_TEST"), "test artifact_type"),
            "operation": operation,
            "content_encoding": "utf-8",
            "content": content,
            "content_hash": replay_hash(content),
            "content_size_bytes": len(content.encode("utf-8")),
            "tests_file_entries": tested_entries,
            "validation_command": _require_string(test_item.get("validation_command"), "validation_command"),
            "expected_coverage_target": _require_string(
                test_item.get("expected_coverage_target"), "expected_coverage_target"
            ),
            "negative_case_requirement": _require_string(
                test_item.get("negative_case_requirement"), "negative_case_requirement"
            ),
            "fixture_references": _string_list(
                test_item.get("fixture_references", []), "fixture_references", allow_empty=True
            ),
            "authority_flags": deepcopy(AUTHORITY_FLAGS),
        }
        entry["test_entry_hash"] = replay_hash(entry)
        entries.append(entry)
    return entries


def _returned_artifact(manifest: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(manifest)
    returned = {
        "artifact_type": "IMPLEMENTATION_MANIFEST_RETURNED_V1",
        "runtime_version": AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION,
        "event_type": "IMPLEMENTATION_MANIFEST_RETURNED",
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "manifest_status": manifest["manifest_status"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "file_count": manifest["file_count"],
        "test_count": manifest["test_count"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "execution_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(manifest: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "implementation_manifest_artifact": deepcopy(manifest),
        "implementation_manifest_returned": deepcopy(returned),
        "implementation_manifest_replay_reference": str(replay_path),
        "manifest_id": manifest["manifest_id"],
        "manifest_status": manifest["manifest_status"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "file_entries": deepcopy(manifest["file_entries"]),
        "test_entries": deepcopy(manifest["test_entries"]),
        "file_count": manifest["file_count"],
        "test_count": manifest["test_count"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "execution_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authority_flags": deepcopy(manifest["authority_flags"]),
        "failure_reason": manifest["failure_reason"],
        "fail_closed": manifest["manifest_status"] == FAILED_CLOSED,
    }
    capture["implementation_manifest_capture_hash"] = replay_hash(capture)
    return capture


def _compute_manifest_hash(manifest: dict[str, Any]) -> str:
    return replay_hash(
        {
            "manifest_id": manifest["manifest_id"],
            "canonical_chain_id": manifest["canonical_chain_id"],
            "implementation_bundle_id": manifest["implementation_bundle_id"],
            "source_candidate_reference": manifest["source_candidate_reference"],
            "source_candidate_hash": manifest["source_candidate_hash"],
            "implementation_handoff_reference": manifest["implementation_handoff_reference"],
            "implementation_handoff_hash": manifest["implementation_handoff_hash"],
            "provider_generation_authorization_reference": manifest[
                "provider_generation_authorization_reference"
            ],
            "provider_generation_authorization_hash": manifest["provider_generation_authorization_hash"],
            "provider_response_reference": manifest["provider_response_reference"],
            "provider_response_hash": manifest["provider_response_hash"],
            "target_domain": manifest["target_domain"],
            "target_resource": manifest["target_resource"],
            "target_worker": manifest["target_worker"],
            "operation_mode": manifest["operation_mode"],
            "file_entries": manifest["file_entries"],
            "test_entries": manifest["test_entries"],
            "validation_requirements": manifest["validation_requirements"],
            "forbidden_operations": manifest["forbidden_operations"],
            "known_gaps": manifest["known_gaps"],
            "manifest_status": manifest["manifest_status"],
            "read_only": manifest["read_only"],
            "content_bearing_manifest": manifest["content_bearing_manifest"],
            "filesystem_mutated": manifest["filesystem_mutated"],
            "execution_authorized": manifest["execution_authorized"],
            "provider_invoked": manifest["provider_invoked"],
            "worker_invoked": manifest["worker_invoked"],
            "approval_created": manifest["approval_created"],
            "authority_flags": manifest["authority_flags"],
            "failure_reason": manifest["failure_reason"],
        }
    )


def _normalize_target_path(value: Any) -> str:
    path_text = _require_string(value, "target_path")
    if path_text.startswith("/") or "\\" in path_text:
        raise FailClosedRuntimeError("implementation manifest failed closed: invalid target path")
    path = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise FailClosedRuntimeError("implementation manifest failed closed: invalid target path")
    return path.as_posix()


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"implementation manifest failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"implementation manifest failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return _require_string(value, "optional string")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation manifest failed closed: {label} missing")
    return value.strip()


def _require_content(value: Any, label: str) -> str:
    if not isinstance(value, str) or value == "":
        raise FailClosedRuntimeError(f"implementation manifest failed closed: {label} missing")
    return value


def _require_hash(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"implementation manifest failed closed: {label} must be a sha256 hash")
    return text


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("implementation manifest failed closed: replay artifact already exists")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual:
        raise FailClosedRuntimeError("implementation manifest artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation manifest artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("implementation manifest replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation manifest replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "implementation manifest failed closed"


__all__ = [
    "AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION",
    "CREATE_ONLY",
    "IMPLEMENTATION_MANIFEST_ARTIFACT_V1",
    "IMPLEMENTATION_MANIFEST_CREATED",
    "create_implementation_manifest",
    "reconstruct_implementation_manifest_replay",
]
