"""Replay-owned evidence for governed existing-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


EXISTING_FILE_REPLAY_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_REPLAY_STEPS = (
    "mutation_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "worker_request_recorded",
    "pre_mutation_state_recorded",
    "worker_result_recorded",
    "post_mutation_validation_recorded",
    "rollback_metadata_recorded",
    "completion_recorded",
)


def ensure_existing_file_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(EXISTING_FILE_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("existing-file mutation failed closed: replay artifact already exists")


def persist_existing_file_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if EXISTING_FILE_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("existing-file mutation replay step ordering mismatch")
    verify_existing_file_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": EXISTING_FILE_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_existing_file_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_existing_file_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def load_existing_file_mutation_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(EXISTING_FILE_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("existing-file mutation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("existing-file mutation replay artifact must be a JSON object")
        verify_existing_file_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def reconstruct_existing_file_mutation_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = load_existing_file_mutation_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    worker_request = wrappers[3]["artifact"]
    pre_mutation = wrappers[4]["artifact"]
    worker_result = wrappers[5]["artifact"]
    validation = wrappers[6]["artifact"]
    rollback = wrappers[7]["artifact"]
    completion = wrappers[8]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("existing-file mutation approval candidate hash mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("existing-file mutation authorization candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("existing-file mutation worker request authorization mismatch")
    if pre_mutation["target_content_hash_before"] != candidate["expected_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation pre-hash mismatch")
    if worker_result["old_content_hash"] != candidate["expected_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation Worker old hash mismatch")
    if worker_result["new_content_hash"] != candidate["replacement_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation Worker new hash mismatch")
    if validation["validation_status"] != "VALIDATED":
        raise FailClosedRuntimeError("existing-file mutation validation missing")
    if rollback["original_content_hash"] != candidate["expected_content_hash"]:
        raise FailClosedRuntimeError("existing-file mutation rollback original hash mismatch")
    if completion["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("existing-file mutation completion candidate mismatch")
    if completion["worker_result_hash"] != worker_result["artifact_hash"]:
        raise FailClosedRuntimeError("existing-file mutation completion Worker hash mismatch")
    if completion["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("existing-file mutation completion validation hash mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": candidate["operation"],
        "target_path": candidate["target_path"],
        "old_content_hash": candidate["expected_content_hash"],
        "new_content_hash": candidate["replacement_content_hash"],
        "worker_id": authorization["worker_id"],
        "worker_invoked": worker_result["worker_invoked"],
        "repository_mutated": completion["repository_mutated"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "rollback_metadata_present": rollback["rollback_metadata_present"],
        "validation_status": validation["validation_status"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_existing_file_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("existing-file mutation artifact hash field missing")


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("existing-file mutation artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("existing-file mutation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("existing-file mutation replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"existing-file mutation requires {field}")
    return value
