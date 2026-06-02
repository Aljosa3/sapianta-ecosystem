"""Replay-visible Result Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.completion_runtime import COMPLETED, COMPLETION_ARTIFACT_V1, COMPLETION_RETURNED
from aigol.runtime.execution_runtime import EXECUTING, EXECUTION_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RESULT_RUNTIME_VERSION = "RESULT_RUNTIME_V1"
RESULT_ARTIFACT_V1 = "RESULT_ARTIFACT_V1"
RESULT_CAPTURED = "RESULT_CAPTURED"
RESULT_RECORDED = "RESULT_RECORDED"
RESULT_RETURNED = "RESULT_RETURNED"

REPLAY_STEPS = ("result_captured", "result_returned")
FORBIDDEN_RESULT_FIELDS = frozenset(
    {
        "quality_score",
        "quality_evaluation",
        "result_approval",
        "result_certification",
        "failure_analysis",
        "reflection",
        "self_improvement",
        "governance_mutation",
        "replay_mutation",
        "execution_history_mutation",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
    }
)


def capture_result(
    *,
    result_id: str,
    completion_artifact: dict[str, Any],
    completion_replay: dict[str, Any],
    execution_artifact: dict[str, Any],
    worker_output: dict[str, Any],
    canonical_chain_id: str,
    captured_by: str,
    captured_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture worker output as a result without evaluating or certifying it."""

    replay_path = Path(replay_dir)
    _ensure_result_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    completion = _validate_completion_artifact(completion_artifact, chain_id)
    completion_returned = _validate_completion_replay(completion_replay, completion)
    execution = _validate_execution_artifact(execution_artifact, completion, chain_id)
    output = _validate_worker_output(worker_output, completion, chain_id)
    result = _result_artifact(
        result_id=result_id,
        completion=completion,
        completion_replay=completion_returned,
        execution=execution,
        worker_output=output,
        canonical_chain_id=chain_id,
        captured_by=captured_by,
        captured_at=captured_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], result)
    returned = _result_returned(result)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(result, returned)


def reconstruct_result_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Result Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("result replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("result replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "result artifact")
        wrappers.append(wrapper)

    result = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("result_reference") != result["result_id"]:
        raise FailClosedRuntimeError("result replay reference mismatch")
    if returned.get("result_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("result replay hash mismatch")
    if returned.get("canonical_chain_id") != result["canonical_chain_id"]:
        raise FailClosedRuntimeError("result replay chain mismatch")
    if returned.get("completion_reference") != result["completion_reference"]:
        raise FailClosedRuntimeError("result replay completion reference mismatch")
    if returned.get("execution_reference") != result["execution_reference"]:
        raise FailClosedRuntimeError("result replay execution reference mismatch")
    _validate_result_artifact(result)
    return {
        "result_id": result["result_id"],
        "canonical_chain_id": result["canonical_chain_id"],
        "result_status": result["result_status"],
        "worker_reference": result["worker_reference"],
        "execution_reference": result["execution_reference"],
        "completion_reference": result["completion_reference"],
        "worker_output_reference": result["worker_output_reference"],
        "worker_output_hash": result["worker_output_hash"],
        "result_payload_hash": result["result_payload_hash"],
        "captured_at": result["captured_at"],
        "result_quality_evaluated": False,
        "result_approved": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "reflection_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _result_artifact(
    *,
    result_id: str,
    completion: dict[str, Any],
    completion_replay: dict[str, Any],
    execution: dict[str, Any],
    worker_output: dict[str, Any],
    canonical_chain_id: str,
    captured_by: str,
    captured_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    result_payload = deepcopy(worker_output)
    artifact = {
        "artifact_type": RESULT_ARTIFACT_V1,
        "result_runtime_version": RESULT_RUNTIME_VERSION,
        "result_id": _require_string(result_id, "result_id"),
        "canonical_chain_id": canonical_chain_id,
        "execution_reference": completion["execution_reference"],
        "execution_hash": completion["execution_hash"],
        "completion_reference": completion["completion_id"],
        "completion_hash": completion["artifact_hash"],
        "completion_replay_hash": completion_replay["artifact_hash"],
        "worker_reference": completion["worker_reference"],
        "worker_hash": completion["worker_hash"],
        "worker_assignment_reference": completion["worker_assignment_reference"],
        "dispatch_reference": completion["dispatch_reference"],
        "worker_invocation_reference": completion["worker_invocation_reference"],
        "execution_request_reference": completion["execution_request_reference"],
        "worker_output_reference": _worker_output_reference(worker_output),
        "worker_output_hash": worker_output["artifact_hash"],
        "result_status": RESULT_CAPTURED,
        "result_payload": result_payload,
        "result_payload_hash": replay_hash(result_payload),
        "captured_by": _normalize_token(captured_by, "captured_by"),
        "captured_at": _require_string(captured_at, "captured_at"),
        "execution_status_before": execution["execution_status"],
        "completion_status_before": completion["completion_status"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "worker_self_certified": False,
        "result_quality_evaluated": False,
        "result_approved": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "reflection_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_result_artifact(artifact)
    return artifact


def _result_returned(result: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(result, "result artifact")
    returned = {
        "event_type": RESULT_RETURNED,
        "result_reference": result["result_id"],
        "result_hash": result["artifact_hash"],
        "canonical_chain_id": result["canonical_chain_id"],
        "completion_reference": result["completion_reference"],
        "completion_hash": result["completion_hash"],
        "execution_reference": result["execution_reference"],
        "execution_hash": result["execution_hash"],
        "worker_reference": result["worker_reference"],
        "worker_hash": result["worker_hash"],
        "worker_output_reference": result["worker_output_reference"],
        "worker_output_hash": result["worker_output_hash"],
        "result_status": result["result_status"],
        "captured_at": result["captured_at"],
        "replay_reference": result["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "worker_self_certified": False,
        "result_quality_evaluated": False,
        "result_approved": False,
        "result_certified": False,
        "failure_analysis_performed": False,
        "reflection_performed": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
        "reconstruction_metadata": {
            "result_reconstructable": True,
            "completion_reconstructable": True,
            "execution_reconstructable": True,
            "canonical_chain_continuous": True,
            "quality_evaluated": False,
            "result_certified": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(result: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "result_artifact": deepcopy(result),
        "result_replay": deepcopy(returned),
    }
    capture["result_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_result_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("result replay step ordering mismatch")
    _verify_artifact_hash(artifact, "result artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": RESULT_RECORDED if index == 0 else RESULT_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_completion_artifact(completion: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(completion, dict):
        raise FailClosedRuntimeError("result failed closed: completion artifact is required")
    _verify_artifact_hash(completion, "completion artifact")
    if completion.get("artifact_type") != COMPLETION_ARTIFACT_V1:
        raise FailClosedRuntimeError("result failed closed: invalid completion")
    if completion.get("completion_status") != COMPLETED:
        raise FailClosedRuntimeError("result failed closed: invalid completion")
    if completion.get("completed_by") != "AIGOL":
        raise FailClosedRuntimeError("result failed closed: completion must be AiGOL-created")
    if completion.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("result failed closed: chain mismatch")
    if completion.get("completion_recorded") is not True:
        raise FailClosedRuntimeError("result failed closed: invalid completion")
    if completion.get("result_certified") is not False:
        raise FailClosedRuntimeError("result failed closed: result certification introduced")
    if completion.get("result_quality_evaluated") is not False:
        raise FailClosedRuntimeError("result failed closed: quality evaluation introduced")
    if completion.get("failure_analysis_performed") is not False:
        raise FailClosedRuntimeError("result failed closed: failure analysis introduced")
    if completion.get("governance_mutated") is not False:
        raise FailClosedRuntimeError("result failed closed: governance mutation introduced")
    if completion.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("result failed closed: replay mutation introduced")
    _require_string(completion.get("completion_id"), "completion_id")
    _require_string(completion.get("execution_reference"), "execution_reference")
    _require_string(completion.get("execution_hash"), "execution_hash")
    _require_string(completion.get("worker_reference"), "worker_reference")
    _require_string(completion.get("worker_hash"), "worker_hash")
    _require_string(completion.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(completion.get("dispatch_reference"), "dispatch_reference")
    _require_string(completion.get("worker_invocation_reference"), "worker_invocation_reference")
    _require_string(completion.get("execution_request_reference"), "execution_request_reference")
    return deepcopy(completion)


def _validate_completion_replay(replay: dict[str, Any], completion: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("result failed closed: completion replay is required")
    _verify_artifact_hash(replay, "completion replay artifact")
    if replay.get("event_type") != COMPLETION_RETURNED:
        raise FailClosedRuntimeError("result failed closed: invalid completion replay")
    if replay.get("completion_reference") != completion["completion_id"]:
        raise FailClosedRuntimeError("result failed closed: completion replay reference mismatch")
    if replay.get("completion_hash") != completion["artifact_hash"]:
        raise FailClosedRuntimeError("result failed closed: completion replay hash mismatch")
    if replay.get("canonical_chain_id") != completion["canonical_chain_id"]:
        raise FailClosedRuntimeError("result failed closed: chain mismatch")
    if replay.get("execution_reference") != completion["execution_reference"]:
        raise FailClosedRuntimeError("result failed closed: execution reference mismatch")
    if replay.get("worker_reference") != completion["worker_reference"]:
        raise FailClosedRuntimeError("result failed closed: worker mismatch")
    if replay.get("result_certified") is not False:
        raise FailClosedRuntimeError("result failed closed: result certification introduced")
    return deepcopy(replay)


def _validate_execution_artifact(
    execution: dict[str, Any],
    completion: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(execution, dict):
        raise FailClosedRuntimeError("result failed closed: execution artifact is required")
    _verify_artifact_hash(execution, "execution artifact")
    if execution.get("artifact_type") != EXECUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("result failed closed: invalid execution")
    if execution.get("execution_status") != EXECUTING:
        raise FailClosedRuntimeError("result failed closed: invalid execution")
    if execution.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("result failed closed: chain mismatch")
    if execution.get("execution_id") != completion["execution_reference"]:
        raise FailClosedRuntimeError("result failed closed: execution reference mismatch")
    if execution.get("artifact_hash") != completion["execution_hash"]:
        raise FailClosedRuntimeError("result failed closed: execution hash mismatch")
    if execution.get("worker_reference") != completion["worker_reference"]:
        raise FailClosedRuntimeError("result failed closed: worker mismatch")
    if execution.get("worker_hash") != completion["worker_hash"]:
        raise FailClosedRuntimeError("result failed closed: worker mismatch")
    if execution.get("worker_assignment_reference") != completion["worker_assignment_reference"]:
        raise FailClosedRuntimeError("result failed closed: worker assignment mismatch")
    if execution.get("dispatch_reference") != completion["dispatch_reference"]:
        raise FailClosedRuntimeError("result failed closed: dispatch mismatch")
    if execution.get("worker_invocation_reference") != completion["worker_invocation_reference"]:
        raise FailClosedRuntimeError("result failed closed: invocation mismatch")
    if execution.get("execution_request_reference") != completion["execution_request_reference"]:
        raise FailClosedRuntimeError("result failed closed: execution request mismatch")
    if "result_certified" in execution and execution.get("result_certified") is not False:
        raise FailClosedRuntimeError("result failed closed: result certification introduced")
    if "result_quality_evaluated" in execution and execution.get("result_quality_evaluated") is not False:
        raise FailClosedRuntimeError("result failed closed: quality evaluation introduced")
    return deepcopy(execution)


def _validate_worker_output(
    worker_output: dict[str, Any],
    completion: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(worker_output, dict):
        raise FailClosedRuntimeError("result failed closed: worker output is required")
    _verify_artifact_hash(worker_output, "worker output artifact")
    if "canonical_chain_id" in worker_output and worker_output.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("result failed closed: chain mismatch")
    if "worker_id" in worker_output and worker_output.get("worker_id") != completion["worker_reference"]:
        raise FailClosedRuntimeError("result failed closed: worker mismatch")
    if FORBIDDEN_RESULT_FIELDS.intersection(worker_output):
        raise FailClosedRuntimeError("result failed closed: authority-bearing worker output")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "worker_self_certified",
        "result_quality_evaluated",
        "result_certified",
        "failure_analysis_performed",
        "governance_mutated",
        "replay_mutated",
        "execution_history_modified",
    ):
        if field in worker_output and worker_output.get(field) is not False:
            raise FailClosedRuntimeError("result failed closed: authority-bearing worker output")
    return deepcopy(worker_output)


def _worker_output_reference(worker_output: dict[str, Any]) -> str:
    for field in ("inspection_id", "result_output_id", "artifact_id", "worker_output_id"):
        value = worker_output.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return worker_output["artifact_hash"]


def _validate_result_artifact(result: dict[str, Any]) -> None:
    if result.get("artifact_type") != RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("result failed closed: invalid result artifact")
    if result.get("captured_by") != "AIGOL":
        raise FailClosedRuntimeError("result failed closed: captured_by must be AIGOL")
    if result.get("result_status") != RESULT_CAPTURED:
        raise FailClosedRuntimeError("result failed closed: invalid result status")
    if result.get("execution_status_before") != EXECUTING:
        raise FailClosedRuntimeError("result failed closed: invalid execution")
    if result.get("completion_status_before") != COMPLETED:
        raise FailClosedRuntimeError("result failed closed: invalid completion")
    if result.get("worker_output_hash") != result.get("result_payload", {}).get("artifact_hash"):
        raise FailClosedRuntimeError("result failed closed: worker output hash mismatch")
    if result.get("result_payload_hash") != replay_hash(result.get("result_payload")):
        raise FailClosedRuntimeError("result failed closed: result payload hash mismatch")
    if result.get("replay_visible") is not True:
        raise FailClosedRuntimeError("result failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "worker_self_certified",
        "result_quality_evaluated",
        "result_approved",
        "result_certified",
        "failure_analysis_performed",
        "reflection_performed",
        "self_improvement_performed",
        "governance_mutated",
        "replay_mutated",
        "execution_history_modified",
    ):
        if result.get(field) is not False:
            raise FailClosedRuntimeError("result failed closed: forbidden result authority introduced")
    _require_string(result.get("result_id"), "result_id")
    _require_string(result.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(result.get("execution_reference"), "execution_reference")
    _require_string(result.get("execution_hash"), "execution_hash")
    _require_string(result.get("completion_reference"), "completion_reference")
    _require_string(result.get("completion_hash"), "completion_hash")
    _require_string(result.get("worker_reference"), "worker_reference")
    _require_string(result.get("worker_hash"), "worker_hash")
    _require_string(result.get("worker_assignment_reference"), "worker_assignment_reference")
    _require_string(result.get("dispatch_reference"), "dispatch_reference")
    _require_string(result.get("worker_invocation_reference"), "worker_invocation_reference")
    _require_string(result.get("execution_request_reference"), "execution_request_reference")
    _require_string(result.get("worker_output_reference"), "worker_output_reference")
    _require_string(result.get("worker_output_hash"), "worker_output_hash")
    _require_string(result.get("captured_at"), "captured_at")
    _require_string(result.get("replay_reference"), "replay_reference")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("result replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("result replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
