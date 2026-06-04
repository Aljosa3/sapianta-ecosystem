"""Replay-visible binding of one validated output to one real governance artifact."""

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


AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION = "AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1"
EXACT_OUTPUT_MUTATION_AUTHORIZATION = "EXACT_OUTPUT_MUTATION_AUTHORIZATION"
REAL_OUTPUT_BINDING_EVIDENCE_ARTIFACT_V1 = "REAL_OUTPUT_BINDING_EVIDENCE_ARTIFACT_V1"
REAL_OUTPUT_BINDING_ARTIFACT_V1 = "REAL_OUTPUT_BINDING_ARTIFACT_V1"
ARTIFACT_VERIFICATION_RESULT_V1 = "ARTIFACT_VERIFICATION_RESULT_V1"
OUTPUT_BOUND = "OUTPUT_BOUND"
ARTIFACT_CREATED = "ARTIFACT_CREATED"
ARTIFACT_VERIFIED = "ARTIFACT_VERIFIED"
FAILED_CLOSED = "FAILED_CLOSED"
CREATE_ONLY = "CREATE_ONLY"
GOVERNANCE_DOCUMENT_MARKDOWN = "GOVERNANCE_DOCUMENT_MARKDOWN"
TARGET_PATH = "governance/MARKETING_DOMAIN_FOUNDATION_V1.md"
TARGET_CONTENT = """# MARKETING_DOMAIN_FOUNDATION_V1

## Status

Deterministic placeholder governance document created by
`AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1`.

## Scope

This artifact proves one exact, create-only governance output binding.
"""

REPLAY_STEPS = (
    "mutation_authorization_recorded",
    "output_binding_evidence_recorded",
    "output_binding_artifact_recorded",
    "artifact_verification_result_recorded",
)


def create_exact_output_mutation_authorization(
    *,
    mutation_authorization_id: str,
    worker_result_validation_artifact: dict[str, Any],
    target_path: str,
    artifact_type: str,
    authorized_by: str,
    authorized_at: str,
) -> dict[str, Any]:
    """Create exact, create-only authority for the single supported governance output."""

    _validate_validation_artifact(worker_result_validation_artifact)
    _validate_target(target_path, artifact_type)
    if target_path not in worker_result_validation_artifact["allowed_outputs"]:
        raise FailClosedRuntimeError("real output binding failed closed: target outside allowed outputs")
    if target_path not in worker_result_validation_artifact["produced_outputs"]:
        raise FailClosedRuntimeError("real output binding failed closed: target outside validated outputs")
    artifact = {
        "artifact_type": EXACT_OUTPUT_MUTATION_AUTHORIZATION,
        "runtime_version": AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION,
        "mutation_authorization_id": _require_string(mutation_authorization_id, "mutation_authorization_id"),
        "worker_result_validation_reference": worker_result_validation_artifact["worker_result_validation_id"],
        "worker_result_validation_hash": worker_result_validation_artifact["artifact_hash"],
        "chain_id": worker_result_validation_artifact["chain_id"],
        "target_path": target_path,
        "target_artifact_type": artifact_type,
        "content_hash": replay_hash(TARGET_CONTENT),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
        "delete_permitted": False,
        "rename_permitted": False,
        "move_permitted": False,
        "directory_creation_permitted": False,
        "recursive_creation_permitted": False,
        "authorized_by": _require_string(authorized_by, "authorized_by"),
        "authorized_at": _require_string(authorized_at, "authorized_at"),
        "replay_visible": True,
        "authority_transferable": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def bind_validated_output(
    *,
    real_output_binding_id: str,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str,
    mutation_authorization_artifact: dict[str, Any],
    workspace_root: str | Path,
    bound_by: str,
    bound_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create and verify the one authorized governance artifact."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        validation = _load_validation_lineage(
            Path(worker_result_validation_replay_reference),
            worker_result_validation_artifact,
        )
        authorization = _validate_mutation_authorization(mutation_authorization_artifact, validation)
        target = _resolve_target(Path(workspace_root), authorization["target_path"])
        if target.exists():
            raise FailClosedRuntimeError("real output binding failed closed: target already exists")

        authorization_record = deepcopy(authorization)
        evidence = _evidence_artifact(
            binding_id=real_output_binding_id,
            validation=validation,
            authorization=authorization,
            validation_replay_reference=worker_result_validation_replay_reference,
            workspace_root=Path(workspace_root),
            bound_at=bound_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], authorization_record)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], evidence)

        with target.open("x", encoding="utf-8") as handle:
            handle.write(TARGET_CONTENT)

        binding = _binding_artifact(
            binding_id=real_output_binding_id,
            validation=validation,
            authorization=authorization,
            evidence=evidence,
            target=target,
            bound_by=bound_by,
            bound_at=bound_at,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], binding)
        verification = _verification_artifact(
            binding_id=real_output_binding_id,
            binding=binding,
            target=target,
            verified_at=bound_at,
        )
        _persist_step(replay_path, 3, REPLAY_STEPS[3], verification)
        return _capture(authorization_record, evidence, binding, verification, replay_path)
    except Exception as exc:
        result = _failed_verification(
            binding_id=real_output_binding_id,
            validation_reference=_safe_field(worker_result_validation_artifact, "worker_result_validation_id"),
            authorization_reference=_safe_field(mutation_authorization_artifact, "mutation_authorization_id"),
            target_path=_safe_field(mutation_authorization_artifact, "target_path"),
            verified_at=bound_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_real_output_binding_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify real output binding replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("real output binding replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("real output binding replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "real output binding replay artifact")
        wrappers.append(wrapper)

    authorization, evidence, binding, verification = (wrapper["artifact"] for wrapper in wrappers)
    _validate_mutation_authorization(authorization)
    _validate_binding_artifact(binding)
    if evidence.get("mutation_authorization_hash") != authorization["artifact_hash"]:
        raise FailClosedRuntimeError("real output binding replay authorization mismatch")
    if binding.get("output_binding_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("real output binding replay evidence mismatch")
    if verification.get("real_output_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("real output binding replay continuity mismatch")
    if len({authorization["chain_id"], evidence["chain_id"], binding["chain_id"], verification["chain_id"]}) != 1:
        raise FailClosedRuntimeError("real output binding replay chain mismatch")
    if verification.get("verification_status") != ARTIFACT_VERIFIED:
        raise FailClosedRuntimeError("real output binding replay verification invalid")
    if verification.get("content_hash") != binding["content_hash"]:
        raise FailClosedRuntimeError("real output binding replay content hash mismatch")
    target = Path(binding["resolved_target_path"])
    if not target.exists() or not target.is_file():
        raise FailClosedRuntimeError("real output binding replay artifact missing")
    if replay_hash(target.read_text(encoding="utf-8")) != binding["content_hash"]:
        raise FailClosedRuntimeError("real output binding replay artifact content mismatch")
    return {
        "real_output_binding_id": binding["real_output_binding_id"],
        "output_binding_status": binding["output_binding_status"],
        "artifact_creation_status": binding["artifact_creation_status"],
        "verification_status": verification["verification_status"],
        "target_path": binding["target_path"],
        "target_artifact_type": binding["target_artifact_type"],
        "content_hash": binding["content_hash"],
        "worker_result_validation_reference": binding["worker_result_validation_reference"],
        "mutation_authorization_reference": binding["mutation_authorization_reference"],
        "chain_id": binding["chain_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": verification["failure_reason"],
    }


def render_real_output_binding_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Real Output Binding",
        "",
        f"Output Binding Status: {capture.get('output_binding_status')}",
        f"Artifact Creation Status: {capture.get('artifact_creation_status')}",
        f"Artifact Verification Status: {capture.get('verification_status')}",
        f"Target Path: {capture.get('target_path')}",
        f"Replay Reference: {capture.get('real_output_binding_replay_reference')}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_validation_lineage(
    replay_path: Path,
    provided_validation: dict[str, Any],
) -> dict[str, Any]:
    reconstructed = reconstruct_worker_result_validation_replay(replay_path)
    if reconstructed.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("real output binding failed closed: validation invalid")
    wrapper = load_json(replay_path / "002_validation_artifact_recorded.json")
    _verify_wrapper_hash(wrapper)
    validation = wrapper.get("artifact")
    if not isinstance(validation, dict):
        raise FailClosedRuntimeError("real output binding failed closed: validation replay corruption")
    _verify_artifact_hash(validation, "worker result validation artifact")
    _validate_validation_artifact(validation)
    _verify_artifact_hash(provided_validation, "provided worker result validation artifact")
    if provided_validation.get("worker_result_validation_id") != validation["worker_result_validation_id"]:
        raise FailClosedRuntimeError("real output binding failed closed: validation mismatch")
    if provided_validation.get("artifact_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("real output binding failed closed: validation mismatch")
    return validation


def _validate_validation_artifact(validation: dict[str, Any]) -> None:
    if not isinstance(validation, dict) or validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("real output binding failed closed: invalid validation artifact")
    _verify_artifact_hash(validation, "worker result validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("real output binding failed closed: validation invalid")
    if not isinstance(validation.get("allowed_outputs"), list) or not isinstance(validation.get("produced_outputs"), list):
        raise FailClosedRuntimeError("real output binding failed closed: validated outputs missing")
    for field in ("worker_result_validation_id", "artifact_hash", "chain_id"):
        _require_string(validation.get(field), field)


def _validate_mutation_authorization(
    authorization: dict[str, Any],
    validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(authorization, dict) or authorization.get("artifact_type") != EXACT_OUTPUT_MUTATION_AUTHORIZATION:
        raise FailClosedRuntimeError("real output binding failed closed: exact output mutation authorization required")
    _verify_artifact_hash(authorization, "exact output mutation authorization")
    _validate_target(authorization.get("target_path"), authorization.get("target_artifact_type"))
    if authorization.get("permission") != CREATE_ONLY:
        raise FailClosedRuntimeError("real output binding failed closed: create-only permission required")
    for field in (
        "overwrite_permitted",
        "delete_permitted",
        "rename_permitted",
        "move_permitted",
        "directory_creation_permitted",
        "recursive_creation_permitted",
        "authority_transferable",
    ):
        if authorization.get(field) is not False:
            raise FailClosedRuntimeError(f"real output binding failed closed: {field} must be false")
    if authorization.get("content_hash") != replay_hash(TARGET_CONTENT):
        raise FailClosedRuntimeError("real output binding failed closed: authorized content hash mismatch")
    for field in (
        "mutation_authorization_id",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
        "chain_id",
        "authorized_by",
        "authorized_at",
    ):
        _require_string(authorization.get(field), field)
    if validation is not None:
        if authorization["worker_result_validation_reference"] != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("real output binding failed closed: validation authorization mismatch")
        if authorization["worker_result_validation_hash"] != validation["artifact_hash"]:
            raise FailClosedRuntimeError("real output binding failed closed: validation authorization mismatch")
        if authorization["chain_id"] != validation["chain_id"]:
            raise FailClosedRuntimeError("real output binding failed closed: chain mismatch")
        if authorization["target_path"] not in validation["allowed_outputs"]:
            raise FailClosedRuntimeError("real output binding failed closed: unauthorized path")
        if authorization["target_path"] not in validation["produced_outputs"]:
            raise FailClosedRuntimeError("real output binding failed closed: target outside validated outputs")
    return deepcopy(authorization)


def _validate_target(target_path: Any, artifact_type: Any) -> None:
    if target_path != TARGET_PATH:
        raise FailClosedRuntimeError("real output binding failed closed: unauthorized path")
    if artifact_type != GOVERNANCE_DOCUMENT_MARKDOWN:
        raise FailClosedRuntimeError("real output binding failed closed: invalid artifact type")
    path = Path(target_path)
    if path.is_absolute() or path.parts != ("governance", "MARKETING_DOMAIN_FOUNDATION_V1.md"):
        raise FailClosedRuntimeError("real output binding failed closed: target path invalid")


def _resolve_target(workspace_root: Path, target_path: str) -> Path:
    root = workspace_root.resolve()
    governance_dir = root / "governance"
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("real output binding failed closed: workspace root missing")
    if not governance_dir.exists() or not governance_dir.is_dir():
        raise FailClosedRuntimeError("real output binding failed closed: governance directory missing")
    target = (root / target_path).resolve()
    if target.parent != governance_dir.resolve():
        raise FailClosedRuntimeError("real output binding failed closed: unauthorized path")
    return target


def _evidence_artifact(
    *,
    binding_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    validation_replay_reference: str,
    workspace_root: Path,
    bound_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REAL_OUTPUT_BINDING_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION,
        "output_binding_evidence_id": f"{_require_string(binding_id, 'real_output_binding_id')}:EVIDENCE",
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_validation_replay_reference": _require_string(
            validation_replay_reference, "worker_result_validation_replay_reference"
        ),
        "mutation_authorization_reference": authorization["mutation_authorization_id"],
        "mutation_authorization_hash": authorization["artifact_hash"],
        "chain_id": validation["chain_id"],
        "target_path": authorization["target_path"],
        "target_artifact_type": authorization["target_artifact_type"],
        "content_hash": authorization["content_hash"],
        "workspace_root": str(workspace_root.resolve()),
        "path_authorized": True,
        "artifact_type_authorized": True,
        "create_only_authorized": True,
        "overwrite_forbidden": True,
        "recorded_at": _require_string(bound_at, "bound_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _binding_artifact(
    *,
    binding_id: str,
    validation: dict[str, Any],
    authorization: dict[str, Any],
    evidence: dict[str, Any],
    target: Path,
    bound_by: str,
    bound_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REAL_OUTPUT_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION,
        "real_output_binding_id": _require_string(binding_id, "real_output_binding_id"),
        "output_binding_status": OUTPUT_BOUND,
        "artifact_creation_status": ARTIFACT_CREATED,
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "mutation_authorization_reference": authorization["mutation_authorization_id"],
        "mutation_authorization_hash": authorization["artifact_hash"],
        "output_binding_evidence_reference": evidence["output_binding_evidence_id"],
        "output_binding_evidence_hash": evidence["artifact_hash"],
        "chain_id": validation["chain_id"],
        "target_path": authorization["target_path"],
        "resolved_target_path": str(target),
        "target_artifact_type": authorization["target_artifact_type"],
        "content_hash": authorization["content_hash"],
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
        "artifact_created": True,
        "governance_artifact_created": True,
        "bound_by": _require_string(bound_by, "bound_by"),
        "bound_at": _require_string(bound_at, "bound_at"),
        "replay_visible": True,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_binding_artifact(artifact)
    return artifact


def _verification_artifact(
    *,
    binding_id: str,
    binding: dict[str, Any],
    target: Path,
    verified_at: str,
) -> dict[str, Any]:
    exists = target.exists() and target.is_file()
    actual_content_hash = replay_hash(target.read_text(encoding="utf-8")) if exists else None
    path_matches = str(target) == binding["resolved_target_path"]
    content_hash_matches = actual_content_hash == binding["content_hash"]
    if not exists or not path_matches or not content_hash_matches:
        raise FailClosedRuntimeError("real output binding failed closed: artifact verification mismatch")
    artifact = {
        "artifact_type": ARTIFACT_VERIFICATION_RESULT_V1,
        "runtime_version": AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION,
        "artifact_verification_id": f"{_require_string(binding_id, 'real_output_binding_id')}:VERIFICATION",
        "verification_status": ARTIFACT_VERIFIED,
        "real_output_binding_reference": binding["real_output_binding_id"],
        "real_output_binding_hash": binding["artifact_hash"],
        "worker_result_validation_reference": binding["worker_result_validation_reference"],
        "worker_result_validation_hash": binding["worker_result_validation_hash"],
        "mutation_authorization_reference": binding["mutation_authorization_reference"],
        "mutation_authorization_hash": binding["mutation_authorization_hash"],
        "chain_id": binding["chain_id"],
        "target_path": binding["target_path"],
        "target_artifact_type": binding["target_artifact_type"],
        "content_hash": actual_content_hash,
        "file_exists": exists,
        "path_matches_authorization": path_matches,
        "content_hash_matches_authorization": content_hash_matches,
        "replay_references_match": True,
        "verified_at": _require_string(verified_at, "verified_at"),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_verification(
    *,
    binding_id: str,
    validation_reference: str | None,
    authorization_reference: str | None,
    target_path: str | None,
    verified_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ARTIFACT_VERIFICATION_RESULT_V1,
        "runtime_version": AIGOL_REAL_OUTPUT_BINDING_RUNTIME_VERSION,
        "artifact_verification_id": f"{binding_id}:VERIFICATION",
        "verification_status": FAILED_CLOSED,
        "real_output_binding_reference": None,
        "real_output_binding_hash": None,
        "worker_result_validation_reference": validation_reference,
        "worker_result_validation_hash": None,
        "mutation_authorization_reference": authorization_reference,
        "mutation_authorization_hash": None,
        "chain_id": None,
        "target_path": target_path,
        "target_artifact_type": None,
        "content_hash": None,
        "file_exists": False,
        "path_matches_authorization": False,
        "content_hash_matches_authorization": False,
        "replay_references_match": False,
        "verified_at": verified_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    authorization: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
    binding: dict[str, Any] | None,
    verification: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(verification)
    capture.update(
        {
            "mutation_authorization_artifact": deepcopy(authorization),
            "output_binding_evidence_artifact": deepcopy(evidence),
            "real_output_binding_artifact": deepcopy(binding),
            "artifact_verification_result": deepcopy(verification),
            "output_binding_status": binding.get("output_binding_status") if binding else FAILED_CLOSED,
            "artifact_creation_status": binding.get("artifact_creation_status") if binding else FAILED_CLOSED,
            "target_path": binding.get("target_path") if binding else verification.get("target_path"),
            "real_output_binding_reference": binding.get("real_output_binding_id") if binding else None,
            "real_output_binding_replay_reference": str(replay_path),
            "fail_closed": verification["verification_status"] == FAILED_CLOSED,
        }
    )
    capture["real_output_binding_capture_hash"] = replay_hash(capture)
    return capture


def _validate_binding_artifact(binding: dict[str, Any]) -> None:
    if binding.get("artifact_type") != REAL_OUTPUT_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("real output binding failed closed: invalid binding artifact")
    if binding.get("output_binding_status") != OUTPUT_BOUND or binding.get("artifact_creation_status") != ARTIFACT_CREATED:
        raise FailClosedRuntimeError("real output binding failed closed: invalid binding status")
    _validate_target(binding.get("target_path"), binding.get("target_artifact_type"))
    if binding.get("permission") != CREATE_ONLY or binding.get("overwrite_permitted") is not False:
        raise FailClosedRuntimeError("real output binding failed closed: invalid binding permission")
    for field in (
        "real_output_binding_id",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
        "mutation_authorization_reference",
        "mutation_authorization_hash",
        "output_binding_evidence_reference",
        "output_binding_evidence_hash",
        "chain_id",
        "resolved_target_path",
        "content_hash",
        "bound_by",
        "bound_at",
    ):
        _require_string(binding.get(field), field)


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("real output binding replay ordering mismatch")
    _verify_artifact_hash(artifact, "real output binding artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
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


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("real output binding replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("real output binding replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"real output binding failed closed: {field} is required")
    return value


def _safe_field(value: Any, field: str) -> str | None:
    if isinstance(value, dict) and isinstance(value.get(field), str):
        return value[field]
    return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"real output binding failed closed: {exc}"
