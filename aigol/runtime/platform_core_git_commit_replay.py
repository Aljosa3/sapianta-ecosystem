"""Replay-owned evidence helpers for governed Git commits."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


GIT_COMMIT_REPLAY_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GIT_COMMIT_REPLAY_STEPS = (
    "commit_candidate_recorded",
    "human_approval_recorded",
    "validation_evidence_recorded",
    "governance_authorization_recorded",
    "worker_request_recorded",
    "pre_execution_state_recorded",
    "worker_result_recorded",
    "commit_result_recorded",
    "rollback_metadata_recorded",
    "completion_recorded",
)


def ensure_git_commit_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(GIT_COMMIT_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("governed Git commit failed closed: replay artifact already exists")


def persist_git_commit_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if GIT_COMMIT_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed Git commit replay step ordering mismatch")
    verify_git_commit_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": GIT_COMMIT_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_git_commit_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_git_commit_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def reconstruct_governed_git_commit_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = _load_git_commit_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    validation = wrappers[2]["artifact"]
    authorization = wrappers[3]["artifact"]
    worker_request = wrappers[4]["artifact"]
    pre_execution = wrappers[5]["artifact"]
    worker_result = wrappers[6]["artifact"]
    commit_result = wrappers[7]["artifact"]
    rollback = wrappers[8]["artifact"]
    completion = wrappers[9]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit approval candidate mismatch")
    if validation["artifact_hash"] != candidate["validation_artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit validation evidence mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("governed Git commit authorization candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("governed Git commit worker request authorization mismatch")
    if pre_execution["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit pre-execution candidate mismatch")
    if worker_result["parent_head"] != candidate["expected_head"]:
        raise FailClosedRuntimeError("governed Git commit parent head mismatch")
    if worker_result["commit_hash"] != worker_result["post_commit_head"]:
        raise FailClosedRuntimeError("governed Git commit post head mismatch")
    if commit_result["commit_hash"] != worker_result["commit_hash"]:
        raise FailClosedRuntimeError("governed Git commit result Worker mismatch")
    if rollback["created_commit_hash"] != commit_result["commit_hash"]:
        raise FailClosedRuntimeError("governed Git commit rollback commit mismatch")
    if completion["commit_result_hash"] != commit_result["artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit completion result mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": candidate["operation"],
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "parent_head": commit_result["parent_head"],
        "commit_hash": commit_result["commit_hash"],
        "post_commit_head": commit_result["post_commit_head"],
        "file_set_hash": candidate["file_set_hash"],
        "worker_invoked": worker_result["worker_invoked"],
        "git_performed": completion["git_performed"],
        "commit_created": completion["commit_created"],
        "push_performed": completion["push_performed"],
        "remote_interaction_performed": completion["remote_interaction_performed"],
        "deployment_performed": completion["deployment_performed"],
        "rollback_metadata_present": rollback["rollback_metadata_present"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_git_commit_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("governed Git commit artifact hash field missing")


def _load_git_commit_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(GIT_COMMIT_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed Git commit replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed Git commit replay artifact must be a JSON object")
        verify_git_commit_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed Git commit artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed Git commit artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed Git commit replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git commit requires {field}")
    return value
