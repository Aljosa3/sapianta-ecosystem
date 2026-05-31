"""Minimal governed worker authorization runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import (
    create_authorization_record,
    validate_authorization_record,
)
from aigol.authorization.authorization_validator import validate_authorization_inputs
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AUTHORIZATION_RUNTIME_VERSION = "MINIMAL_GOVERNED_WORKER_AUTHORIZATION_RUNTIME_V1"
AUTHORIZATION_CREATED = "AUTHORIZATION_CREATED"
AUTHORIZATION_RETURNED = "AUTHORIZATION_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorization_created", "authorization_returned")


def authorize_worker_request(
    *,
    authorization_id: str,
    proposal: dict[str, Any],
    worker_target: dict[str, Any],
    authorization_scope: str,
    authorization_timestamp: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create replay-visible governed authorization evidence without execution."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        validated = validate_authorization_inputs(
            proposal=proposal,
            worker_target=worker_target,
            authorization_scope=authorization_scope,
        )
        record = create_authorization_record(
            authorization_id=authorization_id,
            proposal_id=validated["proposal"]["proposal_id"],
            worker_id=validated["worker_target"]["worker_id"],
            authorization_scope=validated["authorization_scope"],
            authorization_timestamp=authorization_timestamp,
        )
        record_dict = validate_authorization_record(record)
        created = _created_artifact(
            record=record_dict,
            validated=validated,
            authorization_timestamp=authorization_timestamp,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], created)
        returned = _returned_artifact(record=record_dict, created=created, failure_reason=None)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(record_dict, created, returned)
    except Exception as exc:
        failure = _failure_artifact(
            authorization_id=authorization_id,
            proposal=proposal,
            worker_target=worker_target,
            authorization_scope=authorization_scope,
            authorization_timestamp=authorization_timestamp,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        returned = _failed_returned(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(failure, failure, returned)


def reconstruct_authorization_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct governed authorization replay without creating authority."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("authorization replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("authorization replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    created = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("authorization_hash") != created.get("authorization_hash"):
        raise FailClosedRuntimeError("authorization replay hash lineage mismatch")
    if returned.get("created_hash") != created.get("artifact_hash"):
        raise FailClosedRuntimeError("authorization replay created hash mismatch")
    return {
        "who_proposed": created["proposal_id"],
        "who_reviewed": created["governance_review"],
        "who_authorized": "governed_authorization_runtime",
        "worker_authorized": created["worker_id"],
        "scope_authorized": created["authorization_scope"],
        "authorization_timestamp": created["authorization_timestamp"],
        "authorization_status": created["authorization_status"],
        "authorization_hash": created["authorization_hash"],
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "replay_visible": True,
        "authority_origin": "governed_authorization_only",
        "replay_hash": replay_hash(wrappers),
    }


def _created_artifact(*, record: dict[str, Any], validated: dict[str, Any], authorization_timestamp: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": AUTHORIZATION_RUNTIME_VERSION,
        "event_type": AUTHORIZATION_CREATED,
        "authorization_record": deepcopy(record),
        "authorization_id": record["authorization_id"],
        "proposal_id": record["proposal_id"],
        "proposal_lineage": deepcopy(validated["proposal"]["proposal_lineage"]),
        "proposal_hash": validated["proposal"]["proposal_hash"],
        "governance_review": validated["proposal"]["governance_review"],
        "worker_id": record["worker_id"],
        "worker_target": deepcopy(validated["worker_target"]),
        "authorization_scope": record["authorization_scope"],
        "authorization_timestamp": authorization_timestamp,
        "authorization_status": record["authorization_status"],
        "authorization_hash": record["authorization_hash"],
        "input_evidence_hash": validated["evidence_hash"],
        "provider_can_authorize": False,
        "proposal_can_authorize": False,
        "cognition_can_authorize": False,
        "replay_can_authorize": False,
        "worker_can_self_authorize": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(*, record: dict[str, Any], created: dict[str, Any], failure_reason: str | None) -> dict[str, Any]:
    artifact = {
        "runtime_version": AUTHORIZATION_RUNTIME_VERSION,
        "event_type": AUTHORIZATION_RETURNED,
        "authorization_id": record["authorization_id"],
        "proposal_id": record["proposal_id"],
        "worker_id": record["worker_id"],
        "authorization_scope": record["authorization_scope"],
        "authorization_status": record["authorization_status"],
        "authorization_hash": record["authorization_hash"],
        "created_hash": created["artifact_hash"],
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(
    *,
    authorization_id: Any,
    proposal: Any,
    worker_target: Any,
    authorization_scope: Any,
    authorization_timestamp: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "runtime_version": AUTHORIZATION_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "authorization_id": authorization_id if isinstance(authorization_id, str) and authorization_id.strip() else "INVALID_AUTHORIZATION_ID",
        "proposal_id": _safe_field(proposal, "proposal_id", "INVALID_PROPOSAL"),
        "worker_id": _safe_field(worker_target, "worker_id", "INVALID_WORKER"),
        "authorization_scope": authorization_scope if isinstance(authorization_scope, str) and authorization_scope.strip() else "INVALID_SCOPE",
        "authorization_timestamp": authorization_timestamp if isinstance(authorization_timestamp, str) and authorization_timestamp.strip() else "INVALID_TIMESTAMP",
        "authorization_status": FAILED_CLOSED,
        "authorization_hash": FAILED_CLOSED,
        "provider_can_authorize": False,
        "proposal_can_authorize": False,
        "cognition_can_authorize": False,
        "replay_can_authorize": False,
        "worker_can_self_authorize": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_returned(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": AUTHORIZATION_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "authorization_id": failure["authorization_id"],
        "proposal_id": failure["proposal_id"],
        "worker_id": failure["worker_id"],
        "authorization_scope": failure["authorization_scope"],
        "authorization_status": FAILED_CLOSED,
        "authorization_hash": FAILED_CLOSED,
        "created_hash": failure["artifact_hash"],
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "replay_visible": True,
        "failure_reason": failure["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(record: dict[str, Any], created: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "authorization_record": deepcopy(record),
        "authorization_created": deepcopy(created),
        "authorization_returned": deepcopy(returned),
    }
    capture["authorization_runtime_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("authorization replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("authorization artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorization artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("authorization replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorization replay hash mismatch")


def _safe_field(value: Any, field_name: str, fallback: str) -> str:
    if isinstance(value, dict) and isinstance(value.get(field_name), str) and value[field_name].strip():
        return value[field_name]
    return fallback


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed worker authorization failed closed"
