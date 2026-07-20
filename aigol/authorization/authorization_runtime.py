"""Minimal governed worker authorization runtime."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import (
    create_authorization_record,
    validate_authorization_record,
)
from aigol.authorization.authorization_validator import validate_authorization_inputs
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


AUTHORIZATION_RUNTIME_VERSION = "MINIMAL_GOVERNED_WORKER_AUTHORIZATION_RUNTIME_V1"
AUTHORIZATION_CREATED = "AUTHORIZATION_CREATED"
AUTHORIZATION_RETURNED = "AUTHORIZATION_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("authorization_created", "authorization_returned")
CANONICAL_AUTHORIZATION_ACTOR, EXISTING_AUTHORIZATION_BINDING_VERSION = "governed_authorization_runtime", "G31_24G_R04_R04_R01_AUTHORIZATION_BINDING_V1"
EXISTING_AUTHORIZATION_BINDING_STEPS = ("authorization_owner_resolved", "authorization_binding_recorded", "authorization_returned")


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
        "who_authorized": CANONICAL_AUTHORIZATION_ACTOR,
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


def persist_existing_authorization_binding_replay(
    *, binding: dict[str, Any], replay_dir: str | Path, session_root: str | Path) -> dict[str, Any]:
    """Persist an actor-bound Replay around one already-created authorization."""

    root, path = Path(session_root).resolve(), Path(replay_dir).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("authorization binding Replay is cross-session")
    _verify_artifact_hash(binding); record = validate_authorization_record(binding.get("authorization_record"))
    if not all((binding.get("runtime_version") == EXISTING_AUTHORIZATION_BINDING_VERSION,
                binding.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR,
                binding.get("authorization_replay_reference") == str(path),
                binding.get("session_id") == root.name, binding.get("authorization_record") == record, binding.get("authorization_id") == record["authorization_id"], binding.get("authorization_hash") == record["authorization_hash"], binding.get("authorization_status") == record["authorization_status"], binding.get("authorization_scope") == record["authorization_scope"], binding.get("worker_id") == record["worker_id"], isinstance(binding.get("r02_authorization_binding_hash"), str), all(binding.get(field) is False for field in ("authorization_consumed", "replace_request_created", "worker_invoked", "provider_invoked", "command_executed", "repository_mutated", "main_repository_mutated")))):
        raise FailClosedRuntimeError("authorization binding identity is invalid")
    _ensure_existing_binding_available(root, path, binding["authorization_hash"])
    owner = {
        "artifact_type": "AUTHORIZATION_OWNER_RESOLVED_BINDING_V1",
        "runtime_version": EXISTING_AUTHORIZATION_BINDING_VERSION,
        "canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR,
        "session_id": binding["session_id"], "authorization_id": binding["authorization_id"],
        "authorization_hash": binding["authorization_hash"],
        "r02_authorization_binding_hash": binding["r02_authorization_binding_hash"],
        "authorization_consumed": False, "worker_invoked": False,
        "repository_mutated": False, "replay_visible": True,
    }
    owner["artifact_hash"] = replay_hash(owner)
    returned = {
        "artifact_type": "AUTHORIZATION_BINDING_RETURNED_V1",
        "runtime_version": EXISTING_AUTHORIZATION_BINDING_VERSION,
        "canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR,
        "authorization_id": binding["authorization_id"],
        "authorization_hash": binding["authorization_hash"],
        "authorization_binding_hash": binding["artifact_hash"],
        "owner_resolution_hash": owner["artifact_hash"],
        "authorization_status": binding["authorization_status"],
        "authorization_consumed": False, "replace_request_created": False,
        "worker_invoked": False, "repository_mutated": False,
        "main_repository_mutated": False, "replay_visible": True,
    }
    returned["artifact_hash"] = replay_hash(returned)
    for index, artifact in enumerate((owner, binding, returned)):
        _persist_existing_binding_step(path, index, artifact)
    return reconstruct_existing_authorization_binding_replay(path, session_root=root)


def reconstruct_existing_authorization_binding_replay(
    replay_dir: str | Path, *, session_root: str | Path) -> dict[str, Any]:
    """Reconstruct one existing-record actor and authorization Replay binding."""

    root, path = Path(session_root).resolve(), Path(replay_dir).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("authorization binding Replay is cross-session")
    expected_files = {f"{index:03d}_{step}.json" for index, step in enumerate(EXISTING_AUTHORIZATION_BINDING_STEPS)}
    if not path.is_dir() or {item.name for item in path.iterdir()} != expected_files:
        raise FailClosedRuntimeError("authorization binding Replay file set mismatch")
    wrappers = []
    for index, step in enumerate(EXISTING_AUTHORIZATION_BINDING_STEPS):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("authorization binding Replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        _verify_artifact_hash(wrapper.get("artifact") or {})
        wrappers.append(wrapper)
    owner, binding, returned = [wrapper["artifact"] for wrapper in wrappers]; record = validate_authorization_record(binding.get("authorization_record"))
    if not all((owner.get("artifact_type") == "AUTHORIZATION_OWNER_RESOLVED_BINDING_V1", owner.get("runtime_version") == EXISTING_AUTHORIZATION_BINDING_VERSION, binding.get("artifact_type") == "EXISTING_MUTATION_AUTHORIZATION_ACTOR_BINDING_V1", binding.get("runtime_version") == EXISTING_AUTHORIZATION_BINDING_VERSION, returned.get("artifact_type") == "AUTHORIZATION_BINDING_RETURNED_V1", returned.get("runtime_version") == EXISTING_AUTHORIZATION_BINDING_VERSION,
                owner.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR,
                binding.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR, returned.get("canonical_authorization_actor") == CANONICAL_AUTHORIZATION_ACTOR,
                owner.get("session_id") == root.name == binding.get("session_id"),
                binding.get("authorization_replay_reference") == str(path),
                owner.get("authorization_id") == binding.get("authorization_id"),
                returned.get("authorization_id") == binding.get("authorization_id"),
                owner.get("authorization_hash") == binding.get("authorization_hash"),
                returned.get("authorization_hash") == binding.get("authorization_hash"),
                returned.get("authorization_binding_hash") == binding.get("artifact_hash"),
                returned.get("owner_resolution_hash") == owner.get("artifact_hash"), owner.get("r02_authorization_binding_hash") == binding.get("r02_authorization_binding_hash"),
                binding.get("authorization_record") == record, binding.get("authorization_id") == record["authorization_id"], binding.get("authorization_hash") == record["authorization_hash"], binding.get("authorization_status") == record["authorization_status"], binding.get("authorization_scope") == record["authorization_scope"], binding.get("worker_id") == record["worker_id"], returned.get("authorization_status") == "AUTHORIZED", all(item.get(field) is False for item in (owner, binding, returned) for field in ("authorization_consumed", "worker_invoked", "repository_mutated")), all(binding.get(field) is False for field in ("replace_request_created", "provider_invoked", "command_executed", "main_repository_mutated")), returned.get("replace_request_created") is False, returned.get("main_repository_mutated") is False)):
        raise FailClosedRuntimeError("authorization binding Replay identity mismatch")
    return {"canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR, "authorization_replay_reference": str(path), "authorization_replay_hash": replay_hash(wrappers),
            "authorization_binding_artifact": deepcopy(binding),
            "authorization_consumed": False, "replace_request_created": False,
            "worker_invoked": False, "repository_mutated": False, "main_repository_mutated": False}


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


def _ensure_existing_binding_available(root: Path, path: Path, authorization_hash: str) -> None:
    if any((path / f"{index:03d}_{step}.json").exists()
           for index, step in enumerate(EXISTING_AUTHORIZATION_BINDING_STEPS)):
        raise FailClosedRuntimeError("authorization binding Replay destination already exists")
    for existing in root.rglob(f"001_{EXISTING_AUTHORIZATION_BINDING_STEPS[1]}.json"):
        wrapper = load_json(existing); _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact") or {}; _verify_artifact_hash(artifact)
        if artifact.get("authorization_hash") == authorization_hash:
            raise FailClosedRuntimeError("authorization already has an actor and Replay binding")


def _persist_existing_binding_step(path: Path, index: int, artifact: dict[str, Any]) -> None:
    step = EXISTING_AUTHORIZATION_BINDING_STEPS[index]
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact),
               "replay_service_version": EXISTING_AUTHORIZATION_BINDING_VERSION}
    wrapper["replay_hash"] = replay_hash(wrapper)
    destination = path / f"{index:03d}_{step}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise FailClosedRuntimeError("authorization binding Replay destination already exists") from exc
    try:
        payload = (canonical_serialize(wrapper) + "\n").encode("utf-8")
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
    except Exception:
        raise FailClosedRuntimeError("authorization binding Replay persistence failed closed")

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
