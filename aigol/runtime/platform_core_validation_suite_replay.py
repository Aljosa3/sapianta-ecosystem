"""Replay-owned evidence helpers for governed validation suites."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.architectural_health_advisory import verify_architectural_health_advisory_report
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


VALIDATION_SUITE_REPLAY_VERSION = "G9_13_BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTATION_V1"
VALIDATION_SUITE_REPLAY_STEPS = (
    "validation_suite_candidate_recorded",
    "human_approval_recorded",
    "governance_authorization_recorded",
    "pre_suite_state_recorded",
    "command_execution_recorded",
    "validation_suite_summary_recorded",
    "architectural_health_advisory_recorded",
    "completion_recorded",
)


def ensure_validation_suite_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(VALIDATION_SUITE_REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("governed validation suite failed closed: replay artifact already exists")


def persist_validation_suite_replay_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if VALIDATION_SUITE_REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed validation suite replay step ordering mismatch")
    verify_validation_suite_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": VALIDATION_SUITE_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def persist_validation_suite_failure_if_possible(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    try:
        persist_validation_suite_replay_step(replay_path, index, step, artifact)
    except Exception:
        return


def reconstruct_governed_validation_suite_replay(replay_dir: str | Path) -> dict[str, Any]:
    wrappers = _load_validation_suite_replay(replay_dir)
    candidate = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    pre_suite = wrappers[3]["artifact"]
    command_execution = wrappers[4]["artifact"]
    summary = wrappers[5]["artifact"]
    advisory = wrappers[6]["artifact"]
    completion = wrappers[7]["artifact"]
    if approval["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite approval candidate mismatch")
    if authorization["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite authorization candidate mismatch")
    if authorization["approval_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite authorization approval mismatch")
    if pre_suite["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite pre-state candidate mismatch")
    if command_execution["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite command execution candidate mismatch")
    if summary["command_execution_hash"] != command_execution["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite summary execution mismatch")
    verify_architectural_health_advisory_report(advisory)
    if completion["suite_summary_hash"] != summary["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite completion summary mismatch")
    if completion["architectural_health_advisory_hash"] != advisory["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite completion advisory mismatch")
    return {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "candidate_id": candidate["candidate_id"],
        "command_count": candidate["command_count"],
        "executed_command_count": summary["executed_command_count"],
        "validation_suite_status": summary["validation_suite_status"],
        "validation_suite_passed": summary["validation_suite_passed"],
        "fail_closed": completion["fail_closed"],
        "worker_invoked_count": completion["worker_invoked_count"],
        "architectural_health_advisory_status": advisory["overall_advisory_status"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def verify_validation_suite_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_hash_field(artifact, "artifact_hash")
        return
    if "authorization_hash" in artifact:
        _verify_hash_field(artifact, "authorization_hash")
        return
    if "request_hash" in artifact:
        _verify_hash_field(artifact, "request_hash")
        return
    raise FailClosedRuntimeError("governed validation suite artifact hash field missing")


def _load_validation_suite_replay(replay_dir: str | Path) -> list[dict[str, Any]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(VALIDATION_SUITE_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed validation suite replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed validation suite replay artifact must be a JSON object")
        verify_validation_suite_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers


def _verify_hash_field(artifact: dict[str, Any], field: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed validation suite artifact must be a JSON object")
    actual = _require_string(artifact.get(field), field)
    expected_input = deepcopy(artifact)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation suite artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation suite replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation suite requires {field}")
    return value
