"""Deterministic validation runtime for governed worker execution results."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    WORKER_EXECUTION_RESULT_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_RESULT_VALIDATION_RUNTIME_VERSION = "AIGOL_RESULT_VALIDATION_RUNTIME_V1"
RESULT_VALIDATION_ARTIFACT_V1 = "RESULT_VALIDATION_ARTIFACT_V1"
RESULT_VALIDATION_COMPLETED = "RESULT_VALIDATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "result_validation_evidence_recorded",
    "result_validation_artifact_recorded",
    "result_validation_returned",
)


def validate_governed_execution_result(
    *,
    validation_id: str,
    worker_execution_result_artifact: dict[str, Any],
    validated_by: str,
    validated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate a governed worker execution result without mutating it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        result = deepcopy(worker_execution_result_artifact)
        _validate_worker_execution_result(result)
        evidence = _validation_evidence_artifact(
            validation_id=validation_id,
            result=result,
            validated_at=validated_at,
        )
        validation = _validation_artifact(
            validation_id=validation_id,
            result=result,
            evidence=evidence,
            validated_by=validated_by,
            validated_at=validated_at,
            validation_status=RESULT_VALIDATION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(validation)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], validation)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(evidence, validation, returned, replay_path)
    except Exception as exc:
        validation = _failed_validation_artifact(
            validation_id=validation_id,
            worker_execution_result_artifact=worker_execution_result_artifact,
            validated_by=validated_by,
            validated_at=validated_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(validation)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], validation)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(None, validation, returned, replay_path)


def reconstruct_result_validation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate result validation replay."""

    replay_path = Path(replay_dir)
    validation_wrapper = load_json(replay_path / "001_result_validation_artifact_recorded.json")
    returned_wrapper = load_json(replay_path / "002_result_validation_returned.json")
    _verify_wrapper_hash(validation_wrapper)
    _verify_wrapper_hash(returned_wrapper)
    validation = validation_wrapper.get("artifact")
    returned = returned_wrapper.get("artifact")
    if not isinstance(validation, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("result validation replay artifact must be a JSON object")
    _verify_artifact_hash(validation)
    _verify_artifact_hash(returned)
    if validation.get("validation_status") == RESULT_VALIDATION_COMPLETED:
        evidence_wrapper = load_json(replay_path / "000_result_validation_evidence_recorded.json")
        if evidence_wrapper.get("replay_index") != 0 or evidence_wrapper.get("replay_step") != REPLAY_STEPS[0]:
            raise FailClosedRuntimeError("result validation replay ordering mismatch")
        _verify_wrapper_hash(evidence_wrapper)
        evidence = evidence_wrapper.get("artifact")
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("result validation evidence must be a JSON object")
        _verify_artifact_hash(evidence)
        if validation.get("validation_evidence_hash") != evidence["artifact_hash"]:
            raise FailClosedRuntimeError("result validation evidence hash mismatch")
        replay_artifact_count = 3
    else:
        replay_artifact_count = 2
    if validation_wrapper.get("replay_index") != 1 or validation_wrapper.get("replay_step") != REPLAY_STEPS[1]:
        raise FailClosedRuntimeError("result validation replay ordering mismatch")
    if returned_wrapper.get("replay_index") != 2 or returned_wrapper.get("replay_step") != REPLAY_STEPS[2]:
        raise FailClosedRuntimeError("result validation replay ordering mismatch")
    if returned.get("result_validation_reference") != validation["result_validation_id"]:
        raise FailClosedRuntimeError("result validation returned reference mismatch")
    if returned.get("result_validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("result validation returned hash mismatch")
    return {
        "result_validation_id": validation["result_validation_id"],
        "validation_status": validation["validation_status"],
        "source_worker_execution": validation["source_worker_execution"],
        "source_execution_candidate": validation["source_execution_candidate"],
        "replay_lineage_preserved": validation["replay_lineage_preserved"],
        "fail_closed_preserved": validation["fail_closed_preserved"],
        "deterministic_validation_preserved": validation["deterministic_validation_preserved"],
        "ready_for_replay_certification": validation["ready_for_replay_certification"],
        "execution_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": replay_artifact_count,
        "replay_hash": replay_hash([validation_wrapper, returned_wrapper]),
    }


def _validate_worker_execution_result(result: dict[str, Any]) -> None:
    _validate_artifact(result)
    if result.get("artifact_type") != WORKER_EXECUTION_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("result validation failed closed: invalid artifact type")
    if result.get("execution_status") != WORKER_EXECUTION_COMPLETED:
        raise FailClosedRuntimeError("result validation failed closed: completed execution result required")
    if result.get("execution_outcome") != "COMPLETED":
        raise FailClosedRuntimeError("result validation failed closed: execution outcome invalid")
    if result.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("result validation failed closed: replay lineage broken")
    if result.get("fail_closed_preserved") is not True:
        raise FailClosedRuntimeError("result validation failed closed: fail closed evidence missing")
    if result.get("ready_for_result_validation_runtime") is not True:
        raise FailClosedRuntimeError("result validation failed closed: result is not validation-ready")
    _require_string(result.get("source_execution_candidate"), "source_execution_candidate")
    _require_hash(result.get("source_execution_candidate_hash"), "source_execution_candidate_hash")
    if not _string_list(result.get("replay_references")):
        raise FailClosedRuntimeError("result validation failed closed: replay references required")
    if not _hash_list(result.get("replay_hashes")):
        raise FailClosedRuntimeError("result validation failed closed: replay hashes required")
    evidence = result.get("worker_evidence")
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("result validation failed closed: worker evidence invalid")
    if evidence.get("governed_execution") is not True:
        raise FailClosedRuntimeError("result validation failed closed: governed execution evidence missing")
    if evidence.get("external_provider_invoked") is not False or evidence.get("subprocess_invoked") is not False:
        raise FailClosedRuntimeError("result validation failed closed: forbidden execution evidence detected")
    logs = result.get("execution_logs")
    if not isinstance(logs, list) or not all(isinstance(item, str) and item.strip() for item in logs):
        raise FailClosedRuntimeError("result validation failed closed: execution logs invalid")
    validation_inputs = result.get("validation_inputs")
    if not isinstance(validation_inputs, dict) or validation_inputs.get("validation_performed") is not True:
        raise FailClosedRuntimeError("result validation failed closed: validation inputs invalid")
    if result.get("validation_inputs_hash") != validation_inputs.get("artifact_hash"):
        raise FailClosedRuntimeError("result validation failed closed: validation input hash mismatch")
    _verify_artifact_hash(validation_inputs)
    for flag in (
        "implementation_result_created",
        "code_modified",
        "governance_modified",
        "provider_invoked",
    ):
        if result.get(flag) is not False:
            raise FailClosedRuntimeError(f"result validation failed closed: result {flag} must be false")


def _validation_evidence_artifact(
    *,
    validation_id: str,
    result: dict[str, Any],
    validated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1",
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "result_validation_id": _require_string(validation_id, "validation_id"),
        "source_worker_execution": result["worker_execution_id"],
        "source_worker_execution_hash": result["artifact_hash"],
        "source_execution_candidate": result["source_execution_candidate"],
        "source_execution_candidate_hash": result["source_execution_candidate_hash"],
        "execution_outcome": result["execution_outcome"],
        "worker_evidence_hash": replay_hash(result["worker_evidence"]),
        "execution_logs_hash": replay_hash(result["execution_logs"]),
        "validation_inputs_hash": result["validation_inputs_hash"],
        "replay_references": deepcopy(result["replay_references"]),
        "replay_hashes": deepcopy(result["replay_hashes"]),
        "governance_constraints_validated": True,
        "lineage_integrity_validated": True,
        "validated_at": _require_string(validated_at, "validated_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    validation_id: str,
    result: dict[str, Any],
    evidence: dict[str, Any],
    validated_by: str,
    validated_at: str,
    validation_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESULT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "result_validation_id": _require_string(validation_id, "validation_id"),
        "validation_status": validation_status,
        "source_worker_execution": result["worker_execution_id"],
        "source_worker_execution_hash": result["artifact_hash"],
        "source_execution_candidate": result["source_execution_candidate"],
        "source_execution_candidate_hash": result["source_execution_candidate_hash"],
        "validation_evidence": deepcopy(evidence),
        "validation_evidence_hash": evidence["artifact_hash"],
        "validation_rationale": (
            "Execution result passed deterministic outcome, evidence, replay lineage, "
            "and governance constraint validation."
        ),
        "replay_references": deepcopy(result["replay_references"]),
        "replay_hashes": deepcopy(result["replay_hashes"]),
        "certification_readiness": {
            "ready_for_replay_certification": True,
            "improvement_loop_entry_allowed": False,
            "requires_replay_certification": True,
        },
        "validated_by": _require_string(validated_by, "validated_by"),
        "validated_at": _require_string(validated_at, "validated_at"),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "deterministic_validation_preserved": True,
        "ready_for_replay_certification": True,
        "execution_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_validation_artifact(
    *,
    validation_id: str,
    worker_execution_result_artifact: dict[str, Any],
    validated_by: str,
    validated_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESULT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "result_validation_id": validation_id if isinstance(validation_id, str) else "INVALID",
        "validation_status": FAILED_CLOSED,
        "source_worker_execution": worker_execution_result_artifact.get("worker_execution_id")
        if isinstance(worker_execution_result_artifact, dict)
        else None,
        "source_worker_execution_hash": worker_execution_result_artifact.get("artifact_hash")
        if isinstance(worker_execution_result_artifact, dict)
        else None,
        "source_execution_candidate": worker_execution_result_artifact.get("source_execution_candidate")
        if isinstance(worker_execution_result_artifact, dict)
        else None,
        "source_execution_candidate_hash": worker_execution_result_artifact.get("source_execution_candidate_hash")
        if isinstance(worker_execution_result_artifact, dict)
        else None,
        "validation_evidence": {},
        "validation_evidence_hash": None,
        "validation_rationale": "Result validation failed closed before certification readiness.",
        "replay_references": [],
        "replay_hashes": [],
        "certification_readiness": {
            "ready_for_replay_certification": False,
            "improvement_loop_entry_allowed": False,
            "requires_replay_certification": True,
        },
        "validated_by": validated_by if isinstance(validated_by, str) else None,
        "validated_at": validated_at if isinstance(validated_at, str) else None,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "deterministic_validation_preserved": True,
        "ready_for_replay_certification": False,
        "execution_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(validation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(validation)
    artifact = {
        "event_type": "RESULT_VALIDATION_RETURNED",
        "result_validation_reference": validation["result_validation_id"],
        "result_validation_hash": validation["artifact_hash"],
        "validation_status": validation["validation_status"],
        "source_worker_execution": validation["source_worker_execution"],
        "replay_lineage_preserved": validation["replay_lineage_preserved"],
        "fail_closed_preserved": validation["fail_closed_preserved"],
        "ready_for_replay_certification": validation["ready_for_replay_certification"],
        "execution_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": validation["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    validation: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "validation_status": validation["validation_status"],
        "result_validation_evidence_artifact": deepcopy(evidence),
        "result_validation_artifact": deepcopy(validation),
        "result_validation_returned_artifact": deepcopy(returned),
        "result_validation_replay_reference": str(replay_path),
        "result_validation_completed": validation["validation_status"] == RESULT_VALIDATION_COMPLETED,
        "result_validation_artifact_generated": validation["artifact_type"] == RESULT_VALIDATION_ARTIFACT_V1,
        "replay_lineage_preserved": validation["replay_lineage_preserved"],
        "fail_closed_preserved": validation["fail_closed_preserved"],
        "ready_for_replay_certification": validation["ready_for_replay_certification"],
        "failure_reason": validation["failure_reason"],
    }
    capture["result_validation_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("result validation failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("result validation failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("result validation artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("result validation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("result validation replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("result validation replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"result validation failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"result validation failed closed: {field_name} must be a replay hash")
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _hash_list(value: Any) -> list[str]:
    return [item for item in _string_list(value) if item.startswith("sha256:")]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "result validation failed closed"
