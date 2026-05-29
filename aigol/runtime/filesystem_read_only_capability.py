"""Bounded filesystem read-only inspection capability."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.minimal_execution_runtime_prototype import (
    AUTHORIZED,
    FAILED,
    REQUESTED,
    TERMINATED,
    VALIDATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


FILESYSTEM_READ_ONLY_INSPECTION = "FILESYSTEM_READ_ONLY_INSPECTION"
FILESYSTEM_SURFACE = "FILESYSTEM"
READ_ONLY_INSPECTION_CLASSIFICATION = "READ_ONLY_INSPECTION"
LOW_RISK = "LOW"
EXECUTED = "EXECUTED"
REPLAY_STEPS = ("request", "validation", "authorization", "execution", "termination")


def execute_filesystem_read_only_capability(
    *,
    execution_id: str,
    request_id: str,
    created_at: str,
    replay_dir: str | Path,
    root_path: str | Path,
    requested_path: str | Path,
    allowed_paths: list[str | Path],
    capability_id: str = FILESYSTEM_READ_ONLY_INSPECTION,
    lineage_parent: str | None = None,
    authorize: bool = True,
) -> dict[str, Any]:
    """Execute one bounded filesystem read-only inspection."""

    replay_path = Path(replay_dir)
    request = create_filesystem_read_only_request(
        execution_id=execution_id,
        request_id=request_id,
        capability_id=capability_id,
        created_at=created_at,
        root_path=root_path,
        requested_path=requested_path,
        allowed_paths=allowed_paths,
        lineage_parent=lineage_parent,
    )
    _persist_step(replay_path, 0, "request", request)
    try:
        validation = validate_filesystem_read_only_request(request)
        _persist_step(replay_path, 1, "validation", validation)
        authorization = authorize_filesystem_read_only_capability(validation, authorized=authorize)
        _persist_step(replay_path, 2, "authorization", authorization)
        execution = execute_authorized_filesystem_read_only_capability(authorization)
        _persist_step(replay_path, 3, "execution", execution)
        termination = terminate_filesystem_read_only_capability(execution)
        _persist_step(replay_path, 4, "termination", termination)
        return _capture(request, validation, authorization, execution, termination)
    except Exception as exc:
        failure = _failure_artifact(request=request, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(request, None, None, None, failure)


def create_filesystem_read_only_request(
    *,
    execution_id: str,
    request_id: str,
    capability_id: str,
    created_at: str,
    root_path: str | Path,
    requested_path: str | Path,
    allowed_paths: list[str | Path],
    lineage_parent: str | None = None,
) -> dict[str, Any]:
    """Create bounded filesystem read-only request."""

    root = _resolve_existing_path(root_path, "root_path")
    requested = _resolve_path(requested_path, root)
    allowed = [_resolve_path(path, root) for path in allowed_paths]
    if lineage_parent is not None:
        _require_string(lineage_parent, "lineage_parent")
    request = {
        "execution_id": _require_string(execution_id, "execution_id"),
        "request_id": _require_string(request_id, "request_id"),
        "capability_id": _normalize_token(capability_id, "capability_id"),
        "state": REQUESTED,
        "surface": FILESYSTEM_SURFACE,
        "classification": READ_ONLY_INSPECTION_CLASSIFICATION,
        "risk_level": LOW_RISK,
        "created_at": _require_string(created_at, "created_at"),
        "lineage_parent": lineage_parent,
        "root_path": str(root),
        "requested_path": str(requested),
        "allowed_paths": sorted(str(path) for path in allowed),
        "read_only": True,
        "write": False,
        "delete": False,
        "move": False,
        "execute": False,
        "network": False,
        "shell": False,
        "api": False,
        "hidden_state_created": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def validate_filesystem_read_only_request(request: dict[str, Any]) -> dict[str, Any]:
    """Validate allowlisted path scope and read-only classification."""

    _verify_artifact_hash(request)
    if request.get("state") != REQUESTED:
        raise FailClosedRuntimeError("filesystem read-only request must be REQUESTED")
    if request.get("capability_id") != FILESYSTEM_READ_ONLY_INSPECTION:
        raise FailClosedRuntimeError("invalid filesystem capability classification")
    if request.get("classification") != READ_ONLY_INSPECTION_CLASSIFICATION:
        raise FailClosedRuntimeError("invalid filesystem capability classification")
    if request.get("risk_level") != LOW_RISK:
        raise FailClosedRuntimeError("filesystem capability must remain LOW risk")
    _ensure_no_mutation_flags(request)
    root = _resolve_existing_path(request["root_path"], "root_path")
    requested = _resolve_existing_path(request["requested_path"], "requested_path")
    allowed = [_resolve_existing_path(path, "allowed_path") for path in request["allowed_paths"]]
    if not _is_relative_to(requested, root):
        raise FailClosedRuntimeError("filesystem path ambiguity detected")
    if not allowed:
        raise FailClosedRuntimeError("filesystem allowed paths are required")
    if not any(requested == allowed_path or _is_relative_to(requested, allowed_path) for allowed_path in allowed):
        raise FailClosedRuntimeError("forbidden filesystem path access detected")
    validation = {
        "execution_id": request["execution_id"],
        "request_id": request["request_id"],
        "capability_id": request["capability_id"],
        "state": VALIDATED,
        "previous_state": REQUESTED,
        "request_hash": request["artifact_hash"],
        "validated_path": str(requested),
        "root_path": str(root),
        "capability_classification": READ_ONLY_INSPECTION_CLASSIFICATION,
        "risk_level": LOW_RISK,
        "authorization_required": True,
        "replay_centrality_preserved": True,
        "execution_boundary_preserved": True,
        "mutation_detected": False,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def authorize_filesystem_read_only_capability(validation: dict[str, Any], *, authorized: bool = True) -> dict[str, Any]:
    """Create explicit authorization evidence for filesystem read-only inspection."""

    _verify_artifact_hash(validation)
    if validation.get("state") != VALIDATED:
        raise FailClosedRuntimeError("filesystem read-only authorization requires VALIDATED state")
    if authorized is not True:
        raise FailClosedRuntimeError("filesystem read-only authorization missing")
    authorization = {
        "execution_id": validation["execution_id"],
        "request_id": validation["request_id"],
        "capability_id": validation["capability_id"],
        "state": AUTHORIZED,
        "previous_state": VALIDATED,
        "validation_hash": validation["artifact_hash"],
        "authorized_path": validation["validated_path"],
        "authorization_scope": "FILESYSTEM_READ_ONLY_INSPECTION",
        "read_authority": True,
        "write_authority": False,
        "delete_authority": False,
        "move_authority": False,
        "execute_authority": False,
        "network_authority": False,
        "shell_authority": False,
        "api_authority": False,
        "governance_authority": False,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def execute_authorized_filesystem_read_only_capability(authorization: dict[str, Any]) -> dict[str, Any]:
    """Inspect one authorized filesystem path without mutation."""

    _verify_artifact_hash(authorization)
    if authorization.get("state") != AUTHORIZED:
        raise FailClosedRuntimeError("filesystem read-only execution requires AUTHORIZED state")
    _ensure_authorization_has_no_mutation(authorization)
    path = _resolve_existing_path(authorization["authorized_path"], "authorized_path")
    evidence = _inspect_path(path)
    execution = {
        "execution_id": authorization["execution_id"],
        "request_id": authorization["request_id"],
        "capability_id": authorization["capability_id"],
        "state": EXECUTED,
        "previous_state": AUTHORIZED,
        "authorization_hash": authorization["artifact_hash"],
        "execution_evidence": evidence,
        "execution_evidence_hash": evidence["evidence_hash"],
        "final_status": EXECUTED,
        "read_only": True,
        "write_performed": False,
        "delete_performed": False,
        "move_performed": False,
        "execute_performed": False,
        "network_performed": False,
        "shell_performed": False,
        "api_performed": False,
        "hidden_state_created": False,
    }
    execution["artifact_hash"] = replay_hash(execution)
    return execution


def terminate_filesystem_read_only_capability(execution: dict[str, Any]) -> dict[str, Any]:
    """Terminate filesystem read-only capability lifecycle."""

    _verify_artifact_hash(execution)
    if execution.get("state") != EXECUTED:
        raise FailClosedRuntimeError("filesystem read-only termination requires EXECUTED state")
    termination = {
        "execution_id": execution["execution_id"],
        "request_id": execution["request_id"],
        "capability_id": execution["capability_id"],
        "state": TERMINATED,
        "previous_state": EXECUTED,
        "execution_hash": execution["artifact_hash"],
        "final_status": TERMINATED,
        "replay_visible": True,
        "bounded_capability": True,
        "read_only": True,
        "hidden_continuation": False,
    }
    termination["artifact_hash"] = replay_hash(termination)
    return termination


def reconstruct_filesystem_read_only_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate filesystem read-only capability replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("filesystem read-only replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("filesystem read-only replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    states = [wrapper["artifact"]["state"] for wrapper in wrappers]
    _validate_reconstructed_states(states)
    final_artifact = wrappers[-1]["artifact"]
    return {
        "execution_id": final_artifact["execution_id"],
        "capability_id": final_artifact["capability_id"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": states,
        "replay_artifact_count": len(wrappers),
        "append_only_valid": True,
        "replay_visible": True,
        "bounded_capability": True,
        "read_only": True,
        "replay_hash": replay_hash(wrappers),
    }


def _inspect_path(path: Path) -> dict[str, Any]:
    stat = path.stat()
    metadata: dict[str, Any] = {
        "path": str(path),
        "name": path.name,
        "exists": True,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "size_bytes": stat.st_size,
    }
    if path.is_file():
        metadata["text_preview"] = _read_text_preview(path)
    if path.is_dir():
        metadata["entries"] = sorted(child.name for child in path.iterdir())
    evidence = {
        "operation": "filesystem_read_only_inspection",
        "capability_id": FILESYSTEM_READ_ONLY_INSPECTION,
        "classification": READ_ONLY_INSPECTION_CLASSIFICATION,
        "risk_level": LOW_RISK,
        "metadata": metadata,
        "read_only": True,
        "write_performed": False,
        "delete_performed": False,
        "move_performed": False,
        "execute_performed": False,
        "network_performed": False,
        "shell_performed": False,
        "api_performed": False,
    }
    evidence["evidence_hash"] = replay_hash(evidence)
    return evidence


def _read_text_preview(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "UNAVAILABLE_NON_UTF8"
    return text[:512]


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("filesystem read-only replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS[1:], start=1):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _failure_artifact(*, request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "execution_id": request["execution_id"],
        "request_id": request["request_id"],
        "capability_id": request["capability_id"],
        "state": FAILED,
        "previous_state": request.get("state", REQUESTED),
        "request_hash": request["artifact_hash"],
        "final_status": FAILED,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "bounded_capability": True,
        "read_only": True,
        "continuity_validated": False,
        "boundary_violation_detected": "forbidden" in failure_reason.lower() or "mutation" in failure_reason.lower(),
        "hidden_continuation": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_step(failure: dict[str, Any], step: str) -> dict[str, Any]:
    artifact = deepcopy(failure)
    artifact["failed_step"] = step
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    request: dict[str, Any],
    validation: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    termination: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "request": deepcopy(request),
        "validation": deepcopy(validation),
        "authorization": deepcopy(authorization),
        "execution": deepcopy(execution),
        "termination": deepcopy(termination),
    }
    capture["filesystem_capability_hash"] = replay_hash(capture)
    return capture


def _validate_reconstructed_states(states: list[str]) -> None:
    if states == [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]:
        return
    if states[-1] == FAILED:
        try:
            first_failed_index = states.index(FAILED)
        except ValueError as exc:
            raise FailClosedRuntimeError("filesystem read-only replay final status is invalid") from exc
        success_prefix = [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED]
        if states[:first_failed_index] == success_prefix[:first_failed_index] and all(
            state == FAILED for state in states[first_failed_index:]
        ):
            return
    raise FailClosedRuntimeError("filesystem read-only lifecycle ordering mismatch")


def _ensure_authorization_has_no_mutation(authorization: dict[str, Any]) -> None:
    for field in (
        "write_authority",
        "delete_authority",
        "move_authority",
        "execute_authority",
        "network_authority",
        "shell_authority",
        "api_authority",
        "governance_authority",
    ):
        if authorization.get(field) is not False:
            raise FailClosedRuntimeError("filesystem read-only boundary violation detected")


def _ensure_no_mutation_flags(request: dict[str, Any]) -> None:
    for field in ("write", "delete", "move", "execute", "network", "shell", "api", "hidden_state_created"):
        if request.get(field) is not False:
            raise FailClosedRuntimeError("filesystem read-only boundary violation detected")
    if request.get("read_only") is not True:
        raise FailClosedRuntimeError("filesystem read-only classification is invalid")


def _resolve_existing_path(value: str | Path, field_name: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FailClosedRuntimeError(f"{field_name} does not exist")
    return path


def _resolve_path(value: str | Path, root: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.expanduser().resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("filesystem read-only artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("filesystem read-only artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("filesystem read-only artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("filesystem read-only replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("filesystem read-only replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "filesystem read-only capability failed closed"


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
