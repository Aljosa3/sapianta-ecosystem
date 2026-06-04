"""Replay-visible creation of one exact Marketing domain governance bundle."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    WORKER_RESULT_VALIDATION_ARTIFACT_V1,
    reconstruct_worker_result_validation_replay,
)


AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION = "AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_V1"
BUNDLE_MUTATION_AUTHORIZATION = "BUNDLE_MUTATION_AUTHORIZATION"
DOMAIN_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1 = "DOMAIN_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1"
DOMAIN_BUNDLE_ARTIFACT_VERIFICATION_V1 = "DOMAIN_BUNDLE_ARTIFACT_VERIFICATION_V1"
MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1 = "MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1"
DOMAIN_BUNDLE_VERIFICATION_RESULT_V1 = "DOMAIN_BUNDLE_VERIFICATION_RESULT_V1"
BUNDLE_AUTHORIZED = "BUNDLE_AUTHORIZED"
ARTIFACTS_CREATED = "ARTIFACTS_CREATED"
BUNDLE_VERIFIED = "BUNDLE_VERIFIED"
FAILED_CLOSED = "FAILED_CLOSED"
CREATE_ONLY = "CREATE_ONLY"
MARKETING_DOMAIN_BUNDLE_ID = "MARKETING_DOMAIN_BUNDLE_V1"

FOUNDATION_PATH = "governance/MARKETING_DOMAIN_FOUNDATION_V1.md"
MODEL_PATH = "governance/MARKETING_DOMAIN_MODEL_V1.md"
CERTIFICATION_PATH = "governance/MARKETING_DOMAIN_CERTIFICATION.json"

FOUNDATION_CONTENT = """# MARKETING_DOMAIN_FOUNDATION_V1

## Status

Deterministic placeholder governance document created by
`AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_V1`.

## Scope

This artifact is the foundation member of the first governed Marketing domain bundle.
"""
MODEL_CONTENT = """# MARKETING_DOMAIN_MODEL_V1

## Status

Deterministic placeholder Marketing domain model.

## Model

The Marketing domain is represented as a governed, replay-visible domain bundle.
"""
CERTIFICATION_CONTENT = """{
  "artifact_type": "MARKETING_DOMAIN_CERTIFICATION",
  "artifact_version": "V1",
  "domain": "MARKETING",
  "status": "PLACEHOLDER_CERTIFIED",
  "bundle_id": "MARKETING_DOMAIN_BUNDLE_V1"
}
"""

BUNDLE_CONTENTS = {
    FOUNDATION_PATH: FOUNDATION_CONTENT,
    MODEL_PATH: MODEL_CONTENT,
    CERTIFICATION_PATH: CERTIFICATION_CONTENT,
}
BUNDLE_ARTIFACT_TYPES = {
    FOUNDATION_PATH: "GOVERNANCE_DOCUMENT_MARKDOWN",
    MODEL_PATH: "GOVERNANCE_DOCUMENT_MARKDOWN",
    CERTIFICATION_PATH: "GOVERNANCE_CERTIFICATION_JSON",
}
BUNDLE_PATHS = tuple(BUNDLE_CONTENTS)
REPLAY_STEPS = (
    "bundle_authorization_recorded",
    "bundle_creation_evidence_recorded",
    "per_artifact_verification_recorded",
    "bundle_verification_result_recorded",
)


def create_bundle_mutation_authorization(
    *,
    bundle_authorization_id: str,
    bundle_id: str,
    worker_result_validation_artifact: dict[str, Any],
    authorized_by: str,
    authorized_at: str,
) -> dict[str, Any]:
    """Authorize only the exact deterministic Marketing domain bundle."""

    _validate_validation_artifact(worker_result_validation_artifact)
    _require_bundle_id(bundle_id)
    _require_validated_outputs(worker_result_validation_artifact)
    artifacts = [_artifact_manifest(path) for path in BUNDLE_PATHS]
    artifact = {
        "artifact_type": BUNDLE_MUTATION_AUTHORIZATION,
        "runtime_version": AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "bundle_authorization_id": _require_string(bundle_authorization_id, "bundle_authorization_id"),
        "bundle_id": bundle_id,
        "authorization_status": BUNDLE_AUTHORIZED,
        "worker_result_validation_reference": worker_result_validation_artifact["worker_result_validation_id"],
        "worker_result_validation_hash": worker_result_validation_artifact["artifact_hash"],
        "chain_id": worker_result_validation_artifact["chain_id"],
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
        "delete_permitted": False,
        "rename_permitted": False,
        "move_permitted": False,
        "recursive_creation_permitted": False,
        "directory_creation_permitted": False,
        "authority_transferable": False,
        "authorized_by": _require_string(authorized_by, "authorized_by"),
        "authorized_at": _require_string(authorized_at, "authorized_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_marketing_domain_bundle(
    *,
    domain_bundle_runtime_id: str,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str,
    bundle_mutation_authorization_artifact: dict[str, Any],
    workspace_root: str | Path,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create, verify, and record the exact Marketing domain bundle."""

    replay_path = Path(replay_dir)
    created_paths: list[str] = []
    try:
        _ensure_replay_available(replay_path)
        validation = _load_validation_lineage(
            Path(worker_result_validation_replay_reference),
            worker_result_validation_artifact,
        )
        authorization = _validate_bundle_authorization(bundle_mutation_authorization_artifact, validation)
        targets = _resolve_targets(Path(workspace_root))
        existing = [path for path, target in targets.items() if target.exists()]
        if existing:
            raise FailClosedRuntimeError(f"domain bundle failed closed: target already exists: {existing[0]}")

        evidence = _creation_evidence(
            runtime_id=domain_bundle_runtime_id,
            validation=validation,
            authorization=authorization,
            validation_replay_reference=worker_result_validation_replay_reference,
            workspace_root=Path(workspace_root),
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], authorization)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], evidence)

        for path in BUNDLE_PATHS:
            with targets[path].open("x", encoding="utf-8") as handle:
                handle.write(BUNDLE_CONTENTS[path])
            created_paths.append(path)

        verifications = [_verify_target(path, targets[path], authorization) for path in BUNDLE_PATHS]
        verification_artifact = _per_artifact_verification(
            runtime_id=domain_bundle_runtime_id,
            authorization=authorization,
            evidence=evidence,
            verifications=verifications,
            verified_at=created_at,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], verification_artifact)
        bundle = _bundle_result(
            runtime_id=domain_bundle_runtime_id,
            validation=validation,
            authorization=authorization,
            evidence=evidence,
            verification=verification_artifact,
            created_by=created_by,
            created_at=created_at,
        )
        _persist_step(replay_path, 3, REPLAY_STEPS[3], bundle)
        return _capture(authorization, evidence, verification_artifact, bundle, replay_path)
    except Exception as exc:
        failure = _failed_bundle_result(
            runtime_id=domain_bundle_runtime_id,
            authorization_reference=_safe_field(bundle_mutation_authorization_artifact, "bundle_authorization_id"),
            validation_reference=_safe_field(worker_result_validation_artifact, "worker_result_validation_id"),
            created_paths=created_paths,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], failure)
        return _capture(None, None, None, failure, replay_path)


def reconstruct_multi_artifact_domain_bundle_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify the domain bundle replay and current files."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain bundle replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        _verify_artifact_hash(artifact, "domain bundle replay artifact")
        wrappers.append(wrapper)
    authorization, evidence, verification, bundle = (wrapper["artifact"] for wrapper in wrappers)
    _validate_bundle_authorization(authorization)
    if evidence.get("bundle_authorization_hash") != authorization["artifact_hash"]:
        raise FailClosedRuntimeError("domain bundle replay authorization mismatch")
    if verification.get("bundle_creation_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("domain bundle replay evidence mismatch")
    if bundle.get("per_artifact_verification_hash") != verification["artifact_hash"]:
        raise FailClosedRuntimeError("domain bundle replay verification mismatch")
    if bundle.get("bundle_verification_status") != BUNDLE_VERIFIED:
        raise FailClosedRuntimeError("domain bundle replay verification invalid")
    for item in verification["artifact_verifications"]:
        target = Path(item["resolved_target_path"])
        if not target.exists() or replay_hash(target.read_text(encoding="utf-8")) != item["content_hash"]:
            raise FailClosedRuntimeError("domain bundle replay artifact mismatch")
    return {
        "domain_bundle_runtime_id": bundle["domain_bundle_runtime_id"],
        "bundle_id": bundle["bundle_id"],
        "bundle_authorization_status": bundle["bundle_authorization_status"],
        "artifact_creation_status": bundle["artifact_creation_status"],
        "bundle_verification_status": bundle["bundle_verification_status"],
        "artifact_paths": deepcopy(bundle["artifact_paths"]),
        "worker_result_validation_reference": bundle["worker_result_validation_reference"],
        "chain_id": bundle["chain_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": bundle["failure_reason"],
    }


def render_multi_artifact_domain_bundle_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Multi-Artifact Domain Bundle",
        "",
        f"Bundle Authorization Status: {capture.get('bundle_authorization_status')}",
        f"Artifact Creation Status: {capture.get('artifact_creation_status')}",
        f"Bundle Verification Status: {capture.get('bundle_verification_status')}",
        f"Bundle ID: {capture.get('bundle_id')}",
        f"Replay Reference: {capture.get('domain_bundle_replay_reference')}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _artifact_manifest(path: str) -> dict[str, Any]:
    return {
        "path": path,
        "artifact_type": BUNDLE_ARTIFACT_TYPES[path],
        "content_hash": replay_hash(BUNDLE_CONTENTS[path]),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
    }


def _load_validation_lineage(replay_path: Path, provided_validation: dict[str, Any]) -> dict[str, Any]:
    reconstructed = reconstruct_worker_result_validation_replay(replay_path)
    if reconstructed.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("domain bundle failed closed: validation invalid")
    wrapper = load_json(replay_path / "002_validation_artifact_recorded.json")
    _verify_wrapper_hash(wrapper)
    validation = wrapper.get("artifact")
    _validate_validation_artifact(validation)
    _verify_artifact_hash(provided_validation, "provided worker result validation artifact")
    if provided_validation.get("artifact_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("domain bundle failed closed: validation mismatch")
    return validation


def _validate_validation_artifact(validation: Any) -> None:
    if not isinstance(validation, dict) or validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain bundle failed closed: invalid validation artifact")
    _verify_artifact_hash(validation, "worker result validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("domain bundle failed closed: validation invalid")
    _require_validated_outputs(validation)


def _require_validated_outputs(validation: dict[str, Any]) -> None:
    if set(BUNDLE_PATHS) != set(validation.get("allowed_outputs", [])):
        raise FailClosedRuntimeError("domain bundle failed closed: exact artifact list mismatch")
    if set(BUNDLE_PATHS) != set(validation.get("produced_outputs", [])):
        raise FailClosedRuntimeError("domain bundle failed closed: exact validated output list mismatch")


def _validate_bundle_authorization(
    authorization: Any,
    validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(authorization, dict) or authorization.get("artifact_type") != BUNDLE_MUTATION_AUTHORIZATION:
        raise FailClosedRuntimeError("domain bundle failed closed: bundle mutation authorization required")
    _verify_artifact_hash(authorization, "bundle mutation authorization")
    _require_bundle_id(authorization.get("bundle_id"))
    if authorization.get("authorization_status") != BUNDLE_AUTHORIZED:
        raise FailClosedRuntimeError("domain bundle failed closed: bundle authorization invalid")
    if authorization.get("artifacts") != [_artifact_manifest(path) for path in BUNDLE_PATHS]:
        raise FailClosedRuntimeError("domain bundle failed closed: exact artifact list mismatch")
    if authorization.get("artifact_count") != len(BUNDLE_PATHS) or authorization.get("permission") != CREATE_ONLY:
        raise FailClosedRuntimeError("domain bundle failed closed: create-only bundle authorization required")
    for field in (
        "overwrite_permitted",
        "delete_permitted",
        "rename_permitted",
        "move_permitted",
        "recursive_creation_permitted",
        "directory_creation_permitted",
        "authority_transferable",
    ):
        if authorization.get(field) is not False:
            raise FailClosedRuntimeError(f"domain bundle failed closed: {field} must be false")
    if validation is not None:
        if authorization.get("worker_result_validation_reference") != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("domain bundle failed closed: validation authorization mismatch")
        if authorization.get("worker_result_validation_hash") != validation["artifact_hash"]:
            raise FailClosedRuntimeError("domain bundle failed closed: validation authorization mismatch")
        if authorization.get("chain_id") != validation["chain_id"]:
            raise FailClosedRuntimeError("domain bundle failed closed: chain mismatch")
        _require_validated_outputs(validation)
    return deepcopy(authorization)


def _resolve_targets(workspace_root: Path) -> dict[str, Path]:
    root = workspace_root.resolve()
    governance = root / "governance"
    if not root.is_dir() or not governance.is_dir():
        raise FailClosedRuntimeError("domain bundle failed closed: governance directory missing")
    targets = {}
    for path in BUNDLE_PATHS:
        target = (root / path).resolve()
        if target.parent != governance.resolve():
            raise FailClosedRuntimeError("domain bundle failed closed: unauthorized path")
        targets[path] = target
    return targets


def _creation_evidence(
    *,
    runtime_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    validation_replay_reference: str,
    workspace_root: Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "bundle_creation_evidence_id": f"{_require_string(runtime_id, 'domain_bundle_runtime_id')}:EVIDENCE",
        "bundle_id": authorization["bundle_id"],
        "bundle_authorization_reference": authorization["bundle_authorization_id"],
        "bundle_authorization_hash": authorization["artifact_hash"],
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


def _verify_target(path: str, target: Path, authorization: dict[str, Any]) -> dict[str, Any]:
    manifest = next(item for item in authorization["artifacts"] if item["path"] == path)
    exists = target.exists() and target.is_file()
    content_hash = replay_hash(target.read_text(encoding="utf-8")) if exists else None
    if not exists or content_hash != manifest["content_hash"]:
        raise FailClosedRuntimeError(f"domain bundle failed closed: artifact verification mismatch: {path}")
    return {
        "path": path,
        "resolved_target_path": str(target),
        "artifact_type": manifest["artifact_type"],
        "content_hash": content_hash,
        "file_exists": True,
        "path_matches_authorization": True,
        "content_hash_matches_authorization": True,
    }


def _per_artifact_verification(
    *,
    runtime_id: str,
    authorization: dict[str, Any],
    evidence: dict[str, Any],
    verifications: list[dict[str, Any]],
    verified_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_ARTIFACT_VERIFICATION_V1,
        "runtime_version": AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "per_artifact_verification_id": f"{_require_string(runtime_id, 'domain_bundle_runtime_id')}:VERIFICATION",
        "bundle_id": authorization["bundle_id"],
        "bundle_authorization_reference": authorization["bundle_authorization_id"],
        "bundle_authorization_hash": authorization["artifact_hash"],
        "bundle_creation_evidence_reference": evidence["bundle_creation_evidence_id"],
        "bundle_creation_evidence_hash": evidence["artifact_hash"],
        "chain_id": authorization["chain_id"],
        "artifact_verifications": deepcopy(verifications),
        "verified_artifact_count": len(verifications),
        "all_artifacts_verified": len(verifications) == len(BUNDLE_PATHS),
        "verified_at": _require_string(verified_at, "verified_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bundle_result(
    *,
    runtime_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    evidence: dict[str, Any],
    verification: dict[str, Any],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1,
        "runtime_version": AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "domain_bundle_runtime_id": _require_string(runtime_id, "domain_bundle_runtime_id"),
        "bundle_id": authorization["bundle_id"],
        "bundle_authorization_status": BUNDLE_AUTHORIZED,
        "artifact_creation_status": ARTIFACTS_CREATED,
        "bundle_verification_status": BUNDLE_VERIFIED,
        "bundle_authorization_reference": authorization["bundle_authorization_id"],
        "bundle_authorization_hash": authorization["artifact_hash"],
        "bundle_creation_evidence_reference": evidence["bundle_creation_evidence_id"],
        "bundle_creation_evidence_hash": evidence["artifact_hash"],
        "per_artifact_verification_reference": verification["per_artifact_verification_id"],
        "per_artifact_verification_hash": verification["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "chain_id": validation["chain_id"],
        "artifact_paths": list(BUNDLE_PATHS),
        "artifact_count": len(BUNDLE_PATHS),
        "partial_completion": False,
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_bundle_result(
    *,
    runtime_id: str,
    authorization_reference: str | None,
    validation_reference: str | None,
    created_paths: list[str],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_VERIFICATION_RESULT_V1,
        "runtime_version": AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_VERSION,
        "domain_bundle_runtime_id": runtime_id,
        "bundle_id": MARKETING_DOMAIN_BUNDLE_ID,
        "bundle_authorization_status": FAILED_CLOSED,
        "artifact_creation_status": FAILED_CLOSED,
        "bundle_verification_status": FAILED_CLOSED,
        "bundle_authorization_reference": authorization_reference,
        "worker_result_validation_reference": validation_reference,
        "created_paths_before_failure": deepcopy(created_paths),
        "partial_completion": bool(created_paths),
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    authorization: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
    verification: dict[str, Any] | None,
    bundle: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(bundle)
    capture.update(
        {
            "bundle_mutation_authorization_artifact": deepcopy(authorization),
            "bundle_creation_evidence_artifact": deepcopy(evidence),
            "per_artifact_verification_artifact": deepcopy(verification),
            "multi_artifact_domain_bundle_artifact": deepcopy(bundle) if bundle.get("bundle_verification_status") == BUNDLE_VERIFIED else None,
            "domain_bundle_replay_reference": str(replay_path),
            "fail_closed": bundle.get("bundle_verification_status") == FAILED_CLOSED,
        }
    )
    capture["domain_bundle_capture_hash"] = replay_hash(capture)
    return capture


def _require_bundle_id(value: Any) -> str:
    if value != MARKETING_DOMAIN_BUNDLE_ID:
        raise FailClosedRuntimeError("domain bundle failed closed: invalid bundle id")
    return value


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("domain bundle replay ordering mismatch")
    _verify_artifact_hash(artifact, "domain bundle artifact")
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
        raise FailClosedRuntimeError("domain bundle replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain bundle failed closed: {field} is required")
    return value


def _safe_field(value: Any, field: str) -> str | None:
    if isinstance(value, dict) and isinstance(value.get(field), str):
        return value[field]
    return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"domain bundle failed closed: {exc}"
