"""Replay-owned evidence for governed rollback execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ROLLBACK_REPLAY_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
ROLLBACK_REPLAY_STEPS = (
    "rollback_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "pre_rollback_validation_recorded",
    "worker_request_recorded",
    "worker_result_recorded",
    "post_rollback_validation_recorded",
    "completion_recorded",
)


def ensure_rollback_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(ROLLBACK_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("governed rollback failed closed: replay artifact already exists")


def persist_rollback_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if ROLLBACK_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed rollback replay step ordering mismatch")
    verify_rollback_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": ROLLBACK_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_rollback_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_rollback_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def reconstruct_governed_rollback_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = _load_rollback_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    pre_validation = wrappers[3]["artifact"]
    worker_request = wrappers[4]["artifact"]
    worker_result = wrappers[5]["artifact"]
    post_validation = wrappers[6]["artifact"]
    completion = wrappers[7]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback approval candidate mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("governed rollback authorization candidate mismatch")
    if pre_validation["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback pre-validation candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("governed rollback worker request authorization mismatch")
    if worker_result["request_hash"] != worker_request["request_hash"]:
        raise FailClosedRuntimeError("governed rollback Worker result request mismatch")
    if post_validation["post_rollback_hash"] != candidate["expected_rollback_result_hash"]:
        raise FailClosedRuntimeError("governed rollback post-validation hash mismatch")
    if completion["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback completion candidate mismatch")
    if completion["worker_result_hash"] != worker_result["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback completion Worker mismatch")
    if completion["validation_hash"] != post_validation["artifact_hash"]:
        raise FailClosedRuntimeError("governed rollback completion validation mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": candidate["operation"],
        "prior_mutation_type": candidate["prior_mutation_type"],
        "prior_execution_id": candidate["prior_execution_id"],
        "target_path": candidate["target_path"],
        "rollback_action": candidate["rollback_action"],
        "pre_rollback_hash": pre_validation["target_content_hash_before"],
        "post_rollback_hash": post_validation["post_rollback_hash"],
        "worker_invoked": worker_result["worker_invoked"],
        "rollback_executed": worker_result["rollback_executed"],
        "repository_mutated": completion["repository_mutated"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "provider_invoked": completion["provider_invoked"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_rollback_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("governed rollback artifact hash field missing")


def _load_rollback_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(ROLLBACK_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed rollback replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed rollback replay artifact must be an object")
        verify_rollback_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed rollback artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed rollback replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed rollback requires {field}")
    return value
