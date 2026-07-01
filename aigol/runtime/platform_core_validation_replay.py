"""Replay-owned evidence helpers for governed validation execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


VALIDATION_REPLAY_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
VALIDATION_REPLAY_STEPS = (
    "validation_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "worker_request_recorded",
    "pre_execution_state_recorded",
    "worker_result_recorded",
    "validation_result_recorded",
    "completion_recorded",
)


def ensure_validation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(VALIDATION_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("governed validation failed closed: replay artifact already exists")


def persist_validation_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if VALIDATION_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed validation replay step ordering mismatch")
    verify_validation_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": VALIDATION_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_validation_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_validation_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def reconstruct_governed_validation_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = _load_validation_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    worker_request = wrappers[3]["artifact"]
    pre_execution = wrappers[4]["artifact"]
    worker_result = wrappers[5]["artifact"]
    validation_result = wrappers[6]["artifact"]
    completion = wrappers[7]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation approval candidate mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("governed validation authorization candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("governed validation worker request authorization mismatch")
    if pre_execution["command_spec_hash"] != candidate["command_spec_hash"]:
        raise FailClosedRuntimeError("governed validation pre-execution command mismatch")
    if worker_result["argv_hash"] != candidate["argv_hash"]:
        raise FailClosedRuntimeError("governed validation Worker argv mismatch")
    if validation_result["validation_status"] != worker_result["validation_status"]:
        raise FailClosedRuntimeError("governed validation result status mismatch")
    if completion["validation_result_hash"] != validation_result["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation completion result mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "command_id": candidate["command_id"],
        "validation_status": validation_result["validation_status"],
        "exit_code": validation_result["exit_code"],
        "timed_out": validation_result["timed_out"],
        "worker_invoked": worker_result["worker_invoked"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "provider_invoked": completion["provider_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_validation_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("governed validation artifact hash field missing")


def _load_validation_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(VALIDATION_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed validation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed validation replay artifact must be a JSON object")
        verify_validation_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed validation artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value
