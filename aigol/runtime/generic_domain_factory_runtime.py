"""Registry-driven executable domain bundle factory runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.domain_bundle_registry_runtime import (
    DOMAIN_BUNDLE_RESOLVED,
    domain_bundle_contents,
    resolve_domain_bundle,
)
from aigol.runtime.executable_domain_bundle_runtime import (
    AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
    ARTIFACTS_CREATED,
    CREATE_ONLY,
    EXECUTABLE_BUNDLE_ARTIFACT_VERIFICATION_V1,
    EXECUTABLE_BUNDLE_AUTHORIZED,
    EXECUTABLE_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1,
    EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION,
    EXECUTABLE_BUNDLE_VERIFICATION_RESULT_V1,
    EXECUTABLE_BUNDLE_VERIFIED,
    EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1,
    FAILED_CLOSED,
    REPLAY_STEPS,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    WORKER_RESULT_VALIDATION_ARTIFACT_V1,
    reconstruct_worker_result_validation_replay,
)


AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION = "AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_V1"


def create_generic_executable_domain_bundle(
    *,
    generic_domain_factory_runtime_id: str,
    domain_id: str,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str,
    workspace_root: str | Path,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create and verify a registry-defined executable domain bundle."""

    replay_path = Path(replay_dir)
    created_paths: list[str] = []
    try:
        _ensure_replay_available(replay_path)
        resolution = resolve_domain_bundle(
            resolution_id=f"{generic_domain_factory_runtime_id}:DOMAIN-BUNDLE-RESOLUTION",
            domain_id=domain_id,
            require_executable=True,
            created_at=created_at,
            replay_dir=replay_path / "domain_bundle_registry_resolution",
        )
        if resolution.get("resolution_status") != DOMAIN_BUNDLE_RESOLVED:
            raise FailClosedRuntimeError(resolution.get("failure_reason") or "generic domain factory failed closed: domain resolution failed")
        entry = resolution["registry_entry"]
        contents = domain_bundle_contents(entry)
        validation = _load_validation_lineage(
            Path(worker_result_validation_replay_reference),
            worker_result_validation_artifact,
            expected_paths=entry["artifact_paths"],
        )
        authorization = _authorization_artifact(
            runtime_id=generic_domain_factory_runtime_id,
            validation=validation,
            resolution=resolution,
            entry=entry,
            contents=contents,
            authorized_by=created_by,
            authorized_at=created_at,
        )
        targets = _resolve_targets(Path(workspace_root), entry["artifact_paths"])
        existing = [path for path, target in targets.items() if target.exists()]
        if existing:
            raise FailClosedRuntimeError(f"generic domain factory failed closed: target already exists: {existing[0]}")
        evidence = _creation_evidence(
            runtime_id=generic_domain_factory_runtime_id,
            validation=validation,
            authorization=authorization,
            resolution=resolution,
            validation_replay_reference=worker_result_validation_replay_reference,
            workspace_root=Path(workspace_root),
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], authorization)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], evidence)
        for path in entry["artifact_paths"]:
            with targets[path].open("x", encoding="utf-8") as handle:
                handle.write(contents[path])
            created_paths.append(path)
        verifications = [_verify_target(path, targets[path], authorization) for path in entry["artifact_paths"]]
        verification = _verification_artifact(
            runtime_id=generic_domain_factory_runtime_id,
            authorization=authorization,
            evidence=evidence,
            verifications=verifications,
            verified_at=created_at,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], verification)
        bundle = _bundle_artifact(
            runtime_id=generic_domain_factory_runtime_id,
            validation=validation,
            authorization=authorization,
            evidence=evidence,
            verification=verification,
            resolution=resolution,
            entry=entry,
            created_by=created_by,
            created_at=created_at,
        )
        _persist_step(replay_path, 3, REPLAY_STEPS[3], bundle)
        return _capture(authorization, evidence, verification, bundle, resolution, replay_path)
    except Exception as exc:
        failure = _failed_bundle(
            runtime_id=generic_domain_factory_runtime_id,
            domain_id=domain_id,
            validation_reference=_safe_field(worker_result_validation_artifact, "worker_result_validation_id"),
            created_paths=created_paths,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], failure)
        return _capture(None, None, None, failure, None, replay_path)


def _load_validation_lineage(
    replay_path: Path,
    provided_validation: dict[str, Any],
    *,
    expected_paths: list[str],
) -> dict[str, Any]:
    if reconstruct_worker_result_validation_replay(replay_path).get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("generic domain factory failed closed: validation invalid")
    wrapper = load_json(replay_path / "002_validation_artifact_recorded.json")
    _verify_wrapper_hash(wrapper)
    validation = wrapper.get("artifact")
    _validate_validation_artifact(validation, expected_paths=expected_paths)
    _verify_artifact_hash(provided_validation, "provided worker result validation artifact")
    if provided_validation.get("artifact_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("generic domain factory failed closed: validation mismatch")
    return validation


def _validate_validation_artifact(validation: Any, *, expected_paths: list[str]) -> None:
    if not isinstance(validation, dict) or validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("generic domain factory failed closed: invalid validation artifact")
    _verify_artifact_hash(validation, "worker result validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("generic domain factory failed closed: validation invalid")
    if set(validation.get("allowed_outputs", [])) != set(expected_paths):
        raise FailClosedRuntimeError("generic domain factory failed closed: exact artifact list mismatch")
    if set(validation.get("produced_outputs", [])) != set(expected_paths):
        raise FailClosedRuntimeError("generic domain factory failed closed: exact validated output list mismatch")


def _authorization_artifact(
    *,
    runtime_id: str,
    validation: dict[str, Any],
    resolution: dict[str, Any],
    entry: dict[str, Any],
    contents: dict[str, str],
    authorized_by: str,
    authorized_at: str,
) -> dict[str, Any]:
    manifests = _manifests(entry, contents)
    artifact = {
        "artifact_type": EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION,
        "runtime_version": AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "factory_runtime_version": AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION,
        "executable_bundle_authorization_id": f"{_require_string(runtime_id, 'generic_domain_factory_runtime_id')}:AUTHORIZATION",
        "domain_id": entry["domain_id"],
        "bundle_id": entry["bundle_id"],
        "registry_version": resolution["registry_version"],
        "registry_hash": resolution["registry_hash"],
        "registry_entry_hash": resolution["registry_entry_hash"],
        "authorization_status": EXECUTABLE_BUNDLE_AUTHORIZED,
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "domain_bundle_resolution_reference": resolution["resolution_id"],
        "domain_bundle_resolution_hash": resolution["artifact_hash"],
        "chain_id": validation["chain_id"],
        "artifacts": manifests,
        "artifact_count": len(manifests),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
        "delete_permitted": False,
        "rename_permitted": False,
        "move_permitted": False,
        "implicit_creation_permitted": False,
        "recursive_creation_permitted": False,
        "directory_creation_permitted": False,
        "authority_transferable": False,
        "ocs_functionality_enabled": False,
        "semantic_cognition_changed": False,
        "authorized_by": _require_string(authorized_by, "authorized_by"),
        "authorized_at": _require_string(authorized_at, "authorized_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _creation_evidence(
    *,
    runtime_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    resolution: dict[str, Any],
    validation_replay_reference: str,
    workspace_root: Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTABLE_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "factory_runtime_version": AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION,
        "executable_bundle_creation_evidence_id": f"{_require_string(runtime_id, 'generic_domain_factory_runtime_id')}:EVIDENCE",
        "domain_id": authorization["domain_id"],
        "bundle_id": authorization["bundle_id"],
        "registry_hash": authorization["registry_hash"],
        "registry_entry_hash": authorization["registry_entry_hash"],
        "executable_bundle_authorization_reference": authorization["executable_bundle_authorization_id"],
        "executable_bundle_authorization_hash": authorization["artifact_hash"],
        "domain_bundle_resolution_reference": resolution["resolution_id"],
        "domain_bundle_resolution_hash": resolution["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_validation_replay_reference": _require_string(
            validation_replay_reference, "worker_result_validation_replay_reference"
        ),
        "chain_id": validation["chain_id"],
        "workspace_root": str(workspace_root.resolve()),
        "artifact_manifests": deepcopy(authorization["artifacts"]),
        "preflight_all_targets_absent": True,
        "recorded_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verification_artifact(
    *,
    runtime_id: str,
    authorization: dict[str, Any],
    evidence: dict[str, Any],
    verifications: list[dict[str, Any]],
    verified_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTABLE_BUNDLE_ARTIFACT_VERIFICATION_V1,
        "runtime_version": AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "factory_runtime_version": AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION,
        "per_artifact_verification_id": f"{_require_string(runtime_id, 'generic_domain_factory_runtime_id')}:VERIFICATION",
        "domain_id": authorization["domain_id"],
        "bundle_id": authorization["bundle_id"],
        "registry_hash": authorization["registry_hash"],
        "registry_entry_hash": authorization["registry_entry_hash"],
        "executable_bundle_authorization_reference": authorization["executable_bundle_authorization_id"],
        "executable_bundle_authorization_hash": authorization["artifact_hash"],
        "executable_bundle_creation_evidence_reference": evidence["executable_bundle_creation_evidence_id"],
        "executable_bundle_creation_evidence_hash": evidence["artifact_hash"],
        "chain_id": authorization["chain_id"],
        "artifact_verifications": deepcopy(verifications),
        "verified_artifact_count": len(verifications),
        "all_artifacts_verified": len(verifications) == len(authorization["artifacts"]),
        "verified_at": _require_string(verified_at, "verified_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bundle_artifact(
    *,
    runtime_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    evidence: dict[str, Any],
    verification: dict[str, Any],
    resolution: dict[str, Any],
    entry: dict[str, Any],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "factory_runtime_version": AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION,
        "executable_bundle_runtime_id": _require_string(runtime_id, "generic_domain_factory_runtime_id"),
        "domain_id": entry["domain_id"],
        "bundle_id": entry["bundle_id"],
        "registry_hash": resolution["registry_hash"],
        "registry_entry_hash": resolution["registry_entry_hash"],
        "executable_bundle_authorization_status": EXECUTABLE_BUNDLE_AUTHORIZED,
        "artifact_creation_status": ARTIFACTS_CREATED,
        "executable_bundle_verification_status": EXECUTABLE_BUNDLE_VERIFIED,
        "executable_bundle_authorization_reference": authorization["executable_bundle_authorization_id"],
        "executable_bundle_authorization_hash": authorization["artifact_hash"],
        "executable_bundle_creation_evidence_reference": evidence["executable_bundle_creation_evidence_id"],
        "executable_bundle_creation_evidence_hash": evidence["artifact_hash"],
        "per_artifact_verification_reference": verification["per_artifact_verification_id"],
        "per_artifact_verification_hash": verification["artifact_hash"],
        "domain_bundle_resolution_reference": resolution["resolution_id"],
        "domain_bundle_resolution_hash": resolution["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "chain_id": validation["chain_id"],
        "artifact_paths": list(entry["artifact_paths"]),
        "artifact_count": len(entry["artifact_paths"]),
        "partial_completion": False,
        "ocs_functionality_enabled": False,
        "semantic_cognition_changed": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_bundle(
    *,
    runtime_id: str,
    domain_id: str,
    validation_reference: str | None,
    created_paths: list[str],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTABLE_BUNDLE_VERIFICATION_RESULT_V1,
        "runtime_version": AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "factory_runtime_version": AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_VERSION,
        "executable_bundle_runtime_id": runtime_id,
        "domain_id": domain_id,
        "bundle_id": None,
        "executable_bundle_authorization_status": FAILED_CLOSED,
        "artifact_creation_status": FAILED_CLOSED,
        "executable_bundle_verification_status": FAILED_CLOSED,
        "executable_bundle_authorization_reference": None,
        "worker_result_validation_reference": validation_reference,
        "created_paths_before_failure": deepcopy(created_paths),
        "partial_completion": bool(created_paths),
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _manifests(entry: dict[str, Any], contents: dict[str, str]) -> list[dict[str, Any]]:
    templates = [
        *entry["artifact_templates"],
        entry["runtime_template"],
        entry["test_template"],
    ]
    return [
        {
            "path": template["path"],
            "artifact_type": template["artifact_type"],
            "content_hash": replay_hash(contents[template["path"]]),
            "permission": CREATE_ONLY,
            "overwrite_permitted": False,
        }
        for template in templates
    ]


def _resolve_targets(workspace_root: Path, artifact_paths: list[str]) -> dict[str, Path]:
    root = workspace_root.resolve()
    allowed_parents = {
        (root / "governance").resolve(),
        (root / "aigol" / "runtime").resolve(),
        (root / "tests").resolve(),
    }
    if not root.is_dir() or any(not parent.is_dir() for parent in allowed_parents):
        raise FailClosedRuntimeError("generic domain factory failed closed: required directory missing")
    targets = {}
    for path in artifact_paths:
        target = (root / path).resolve()
        if target.parent not in allowed_parents:
            raise FailClosedRuntimeError("generic domain factory failed closed: unauthorized path")
        targets[path] = target
    return targets


def _verify_target(path: str, target: Path, authorization: dict[str, Any]) -> dict[str, Any]:
    manifest = next(item for item in authorization["artifacts"] if item["path"] == path)
    exists = target.exists() and target.is_file()
    content_hash = replay_hash(target.read_text(encoding="utf-8")) if exists else None
    if not exists or content_hash != manifest["content_hash"]:
        raise FailClosedRuntimeError(f"generic domain factory failed closed: artifact verification mismatch: {path}")
    return {
        "path": path,
        "resolved_target_path": str(target),
        "artifact_type": manifest["artifact_type"],
        "content_hash": content_hash,
        "file_exists": True,
        "path_matches_authorization": True,
        "content_hash_matches_authorization": True,
    }


def _capture(
    authorization: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
    verification: dict[str, Any] | None,
    bundle: dict[str, Any],
    resolution: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(bundle)
    capture.update(
        {
            "executable_bundle_mutation_authorization_artifact": deepcopy(authorization),
            "executable_bundle_creation_evidence_artifact": deepcopy(evidence),
            "per_artifact_verification_artifact": deepcopy(verification),
            "domain_bundle_resolution_artifact": deepcopy(resolution),
            "executable_domain_bundle_artifact": deepcopy(bundle)
            if bundle.get("executable_bundle_verification_status") == EXECUTABLE_BUNDLE_VERIFIED
            else None,
            "executable_bundle_replay_reference": str(replay_path),
            "fail_closed": bundle.get("executable_bundle_verification_status") == FAILED_CLOSED,
        }
    )
    capture["generic_domain_factory_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("generic domain factory replay ordering mismatch")
    _verify_artifact_hash(artifact, "generic domain factory artifact")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("generic domain factory replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"generic domain factory failed closed: {field} is required")
    return value


def _safe_field(value: Any, field: str) -> str | None:
    if isinstance(value, dict) and isinstance(value.get(field), str):
        return value[field]
    return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"generic domain factory failed closed: {exc}"
