"""First bounded read-only capability attachment for the execution runtime prototype."""

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
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


READ_ONLY_RUNTIME_INSPECTION = "READ_ONLY_RUNTIME_INSPECTION"
READ_ONLY_CAPABILITY_SURFACE = "RUNTIME_INSPECTION"
READ_ONLY_CAPABILITY_CLASSIFICATION = "READ_ONLY"
EXECUTED = "EXECUTED"
REPLAY_STEPS = ("request", "validation", "authorization", "execution", "termination")


def execute_read_only_capability(
    *,
    execution_id: str,
    request_id: str,
    created_at: str,
    replay_dir: str | Path,
    capability_id: str = READ_ONLY_RUNTIME_INSPECTION,
    provider: MetadataInspectionProvider | None = None,
    lineage_parent: str | None = None,
    authorize: bool = True,
) -> dict[str, Any]:
    """Execute one bounded read-only runtime inspection capability."""

    replay_path = Path(replay_dir)
    request = create_read_only_capability_request(
        execution_id=execution_id,
        request_id=request_id,
        capability_id=capability_id,
        created_at=created_at,
        lineage_parent=lineage_parent,
    )
    _persist_step(replay_path, 0, "request", request)
    try:
        validation = validate_read_only_capability_request(request)
        _persist_step(replay_path, 1, "validation", validation)
        authorization = authorize_read_only_capability(validation, authorized=authorize)
        _persist_step(replay_path, 2, "authorization", authorization)
        execution = execute_authorized_read_only_capability(
            authorization,
            provider=provider or MetadataInspectionProvider(timestamp_provider=lambda: created_at),
        )
        _persist_step(replay_path, 3, "execution", execution)
        termination = terminate_read_only_capability_execution(execution)
        _persist_step(replay_path, 4, "termination", termination)
        return _capture(request, validation, authorization, execution, termination)
    except Exception as exc:
        failure = _failure_artifact(request=request, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(request, None, None, None, failure)


def create_read_only_capability_request(
    *,
    execution_id: str,
    request_id: str,
    capability_id: str,
    created_at: str,
    lineage_parent: str | None = None,
) -> dict[str, Any]:
    """Create replay-visible read-only capability request."""

    if lineage_parent is not None:
        _require_string(lineage_parent, "lineage_parent")
    request = {
        "execution_id": _require_string(execution_id, "execution_id"),
        "request_id": _require_string(request_id, "request_id"),
        "capability_id": _normalize_token(capability_id, "capability_id"),
        "state": REQUESTED,
        "surface": READ_ONLY_CAPABILITY_SURFACE,
        "classification": READ_ONLY_CAPABILITY_CLASSIFICATION,
        "created_at": _require_string(created_at, "created_at"),
        "lineage_parent": lineage_parent,
        "read_only": True,
        "write": False,
        "delete": False,
        "move": False,
        "network": False,
        "shell": False,
        "api": False,
        "hidden_state_created": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def validate_read_only_capability_request(request: dict[str, Any]) -> dict[str, Any]:
    """Validate capability classification and boundary compatibility."""

    _verify_artifact_hash(request)
    if request.get("state") != REQUESTED:
        raise FailClosedRuntimeError("read-only capability request must be REQUESTED")
    if request.get("capability_id") != READ_ONLY_RUNTIME_INSPECTION:
        raise FailClosedRuntimeError("invalid capability classification")
    if request.get("surface") != READ_ONLY_CAPABILITY_SURFACE:
        raise FailClosedRuntimeError("invalid capability surface")
    if request.get("classification") != READ_ONLY_CAPABILITY_CLASSIFICATION:
        raise FailClosedRuntimeError("invalid capability classification")
    _ensure_no_mutation_flags(request)
    validation = {
        "execution_id": request["execution_id"],
        "request_id": request["request_id"],
        "capability_id": request["capability_id"],
        "state": VALIDATED,
        "previous_state": REQUESTED,
        "request_hash": request["artifact_hash"],
        "capability_classification": READ_ONLY_CAPABILITY_CLASSIFICATION,
        "replay_centrality_preserved": True,
        "authorization_required": True,
        "bounded_capability": True,
        "constitutional_freeze_preserved": True,
        "mutation_detected": False,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def authorize_read_only_capability(validation: dict[str, Any], *, authorized: bool = True) -> dict[str, Any]:
    """Create explicit authorization evidence for the read-only capability."""

    _verify_artifact_hash(validation)
    if validation.get("state") != VALIDATED:
        raise FailClosedRuntimeError("read-only capability authorization requires VALIDATED state")
    if authorized is not True:
        raise FailClosedRuntimeError("read-only capability authorization missing")
    authorization = {
        "execution_id": validation["execution_id"],
        "request_id": validation["request_id"],
        "capability_id": validation["capability_id"],
        "state": AUTHORIZED,
        "previous_state": VALIDATED,
        "validation_hash": validation["artifact_hash"],
        "authorization_scope": "READ_ONLY_CAPABILITY_EXECUTION",
        "write_authority": False,
        "delete_authority": False,
        "move_authority": False,
        "network_authority": False,
        "shell_authority": False,
        "api_authority": False,
        "governance_authority": False,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def execute_authorized_read_only_capability(
    authorization: dict[str, Any],
    *,
    provider: MetadataInspectionProvider,
) -> dict[str, Any]:
    """Execute bounded read-only metadata inspection after authorization."""

    _verify_artifact_hash(authorization)
    if authorization.get("state") != AUTHORIZED:
        raise FailClosedRuntimeError("read-only capability execution requires AUTHORIZED state")
    _ensure_authorization_has_no_mutation(authorization)
    evidence = provider.inspect_runtime()
    _verify_provider_evidence(evidence)
    execution = {
        "execution_id": authorization["execution_id"],
        "request_id": authorization["request_id"],
        "capability_id": authorization["capability_id"],
        "state": EXECUTED,
        "previous_state": AUTHORIZED,
        "authorization_hash": authorization["artifact_hash"],
        "execution_evidence": deepcopy(evidence),
        "execution_evidence_hash": evidence["evidence_hash"],
        "final_status": EXECUTED,
        "read_only": True,
        "write_performed": False,
        "delete_performed": False,
        "move_performed": False,
        "network_performed": False,
        "shell_performed": False,
        "api_performed": False,
        "hidden_state_created": False,
    }
    execution["artifact_hash"] = replay_hash(execution)
    return execution


def terminate_read_only_capability_execution(execution: dict[str, Any]) -> dict[str, Any]:
    """Create terminal read-only capability execution artifact."""

    _verify_artifact_hash(execution)
    if execution.get("state") != EXECUTED:
        raise FailClosedRuntimeError("read-only capability termination requires EXECUTED state")
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


def reconstruct_read_only_capability_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate read-only capability replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("read-only capability replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("read-only capability replay artifact must be a JSON object")
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


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("read-only capability replay step ordering mismatch")
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
        "boundary_violation_detected": "boundary" in failure_reason.lower(),
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
    capture["capability_runtime_hash"] = replay_hash(capture)
    return capture


def _validate_reconstructed_states(states: list[str]) -> None:
    if states == [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]:
        return
    if states[-1] == FAILED:
        try:
            first_failed_index = states.index(FAILED)
        except ValueError as exc:
            raise FailClosedRuntimeError("read-only capability replay final status is invalid") from exc
        success_prefix = [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED]
        if states[:first_failed_index] == success_prefix[:first_failed_index] and all(
            state == FAILED for state in states[first_failed_index:]
        ):
            return
    raise FailClosedRuntimeError("read-only capability lifecycle ordering mismatch")


def _verify_provider_evidence(evidence: dict[str, Any]) -> None:
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("read-only capability evidence must be a JSON object")
    if evidence.get("operation") != "inspect_runtime":
        raise FailClosedRuntimeError("invalid read-only capability operation")
    indicators = evidence.get("metadata", {}).get("replay_capability_indicators", {})
    if indicators.get("read_only") is not True:
        raise FailClosedRuntimeError("read-only capability evidence is not read-only")
    expected_input = deepcopy(evidence)
    actual = expected_input.pop("evidence_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("read-only capability evidence hash mismatch")


def _ensure_authorization_has_no_mutation(authorization: dict[str, Any]) -> None:
    for field in (
        "write_authority",
        "delete_authority",
        "move_authority",
        "network_authority",
        "shell_authority",
        "api_authority",
        "governance_authority",
    ):
        if authorization.get(field) is not False:
            raise FailClosedRuntimeError("read-only capability boundary violation detected")


def _ensure_no_mutation_flags(request: dict[str, Any]) -> None:
    for field in ("write", "delete", "move", "network", "shell", "api", "hidden_state_created"):
        if request.get(field) is not False:
            raise FailClosedRuntimeError("read-only capability boundary violation detected")
    if request.get("read_only") is not True:
        raise FailClosedRuntimeError("read-only capability classification is invalid")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("read-only capability artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("read-only capability artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("read-only capability artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("read-only capability replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("read-only capability replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "read-only capability failed closed"


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
