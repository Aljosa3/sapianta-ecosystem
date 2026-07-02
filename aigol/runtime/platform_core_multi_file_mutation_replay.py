"""Replay-owned evidence for governed multi-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MULTI_FILE_REPLAY_VERSION = "G9_11_GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTATION_V1"
MULTI_FILE_REPLAY_STEPS = (
    "transaction_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "pre_transaction_validation_recorded",
    "per_file_execution_recorded",
    "post_transaction_validation_recorded",
    "rollback_metadata_recorded",
    "completion_recorded",
)


def ensure_multi_file_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(MULTI_FILE_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("multi-file mutation failed closed: replay artifact already exists")


def persist_multi_file_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if MULTI_FILE_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("multi-file mutation replay step mismatch")
    verify_multi_file_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": MULTI_FILE_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_multi_file_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_multi_file_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def reconstruct_multi_file_mutation_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = _load_multi_file_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    pre_validation = wrappers[3]["artifact"]
    execution = wrappers[4]["artifact"]
    post_validation = wrappers[5]["artifact"]
    rollback = wrappers[6]["artifact"]
    completion = wrappers[7]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay approval mismatch")
    if authorization["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay authorization mismatch")
    if pre_validation["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay pre-validation mismatch")
    if execution["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay execution mismatch")
    if post_validation["execution_hash"] != execution["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay post-validation mismatch")
    if rollback["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay rollback mismatch")
    if completion["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("multi-file mutation replay completion mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "candidate_id": candidate["candidate_id"],
        "operation_count": candidate["operation_count"],
        "target_paths": deepcopy(candidate["target_paths"]),
        "worker_invoked_count": execution["worker_invoked_count"],
        "repository_mutated": completion["repository_mutated"],
        "mutated_file_count": completion["mutated_file_count"],
        "rollback_metadata_present": completion["rollback_metadata_present"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "provider_invoked": completion["provider_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_multi_file_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("multi-file mutation artifact hash field missing")


def _load_multi_file_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(MULTI_FILE_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("multi-file mutation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("multi-file mutation replay artifact must be an object")
        verify_multi_file_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("multi-file mutation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("multi-file mutation replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multi-file mutation requires {field}")
    return value
