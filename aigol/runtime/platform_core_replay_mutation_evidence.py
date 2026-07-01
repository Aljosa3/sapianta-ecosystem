"""Replay-owned evidence persistence and reconstruction for governed mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REPLAY_MUTATION_EVIDENCE_SERVICE_VERSION = "G8_09B_PLATFORM_CORE_MUTATION_RUNTIME_REFACTORING_V1"
MUTATION_REPLAY_STEPS = (
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


def ensure_mutation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(MUTATION_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("first mutating Worker failed closed: replay artifact already exists")


def persist_mutation_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if MUTATION_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("first mutating Worker replay step ordering mismatch")
    verify_mutation_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": REPLAY_MUTATION_EVIDENCE_SERVICE_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_mutation_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_mutation_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def load_first_mutating_worker_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    """Load ordered replay wrappers and validate hash-bound artifacts."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(MUTATION_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("first mutating Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("first mutating Worker replay artifact must be a JSON object")
        verify_mutation_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def reconstruct_first_mutating_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate the first governed mutation replay."""

    wrappers = load_first_mutating_worker_replay(replay_dir)
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
        raise FailClosedRuntimeError("first mutating Worker approval candidate hash mismatch")
    if authorization["proposal_id"] != candidate["candidate_id"]:
        raise FailClosedRuntimeError("first mutating Worker authorization candidate mismatch")
    if worker_request["authorization_hash"] != authorization["authorization_hash"]:
        raise FailClosedRuntimeError("first mutating Worker worker request authorization mismatch")
    if pre_mutation["target_exists_before"] is not False:
        raise FailClosedRuntimeError("first mutating Worker pre-mutation state mismatch")
    if validation["validation_status"] != "VALIDATED":
        raise FailClosedRuntimeError("first mutating Worker validation missing")
    if rollback["content_hash"] != candidate["content_hash"]:
        raise FailClosedRuntimeError("first mutating Worker rollback hash mismatch")
    if completion["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion candidate mismatch")
    if completion["worker_result_hash"] != worker_result["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion Worker hash mismatch")
    if completion["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("first mutating Worker completion validation hash mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": candidate["operation"],
        "target_filename": candidate["target_filename"],
        "content_hash": candidate["content_hash"],
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


def verify_mutation_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    raise FailClosedRuntimeError("first mutating Worker artifact hash field missing")


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first mutating Worker artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("first mutating Worker replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first mutating Worker requires {field}")
    return value
