"""Deterministic replay certification runtime for validated execution results."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_ARTIFACT_V1, RESULT_VALIDATION_COMPLETED
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_REPLAY_CERTIFICATION_RUNTIME_VERSION = "AIGOL_REPLAY_CERTIFICATION_RUNTIME_V1"
REPLAY_CERTIFICATION_ARTIFACT_V1 = "REPLAY_CERTIFICATION_ARTIFACT_V1"
REPLAY_CERTIFICATION_COMPLETED = "REPLAY_CERTIFICATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "replay_certification_artifact_recorded",
    "replay_certification_returned",
)


def certify_validated_replay(
    *,
    certification_id: str,
    result_validation_artifact: dict[str, Any],
    certified_by: str,
    certified_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Certify a validated result for closed improvement-loop eligibility without mutating it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        validation = deepcopy(result_validation_artifact)
        _validate_result_validation(validation)
        certification = _certification_artifact(
            certification_id=certification_id,
            validation=validation,
            certified_by=certified_by,
            certified_at=certified_at,
            certification_status=REPLAY_CERTIFICATION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(certification)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], certification)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(certification, returned, replay_path)
    except Exception as exc:
        certification = _failed_certification_artifact(
            certification_id=certification_id,
            result_validation_artifact=result_validation_artifact,
            certified_by=certified_by,
            certified_at=certified_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(certification)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], certification)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(certification, returned, replay_path)


def reconstruct_replay_certification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate replay certification replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay certification replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay certification artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    certification = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("replay_certification_reference") != certification["replay_certification_id"]:
        raise FailClosedRuntimeError("replay certification returned reference mismatch")
    if returned.get("replay_certification_hash") != certification["artifact_hash"]:
        raise FailClosedRuntimeError("replay certification returned hash mismatch")
    return {
        "replay_certification_id": certification["replay_certification_id"],
        "certification_status": certification["certification_status"],
        "source_result_validation": certification["source_result_validation"],
        "source_worker_execution": certification["source_worker_execution"],
        "replay_lineage_preserved": certification["replay_lineage_preserved"],
        "fail_closed_preserved": certification["fail_closed_preserved"],
        "deterministic_certification_preserved": certification["deterministic_certification_preserved"],
        "ready_for_closed_improvement_loop": certification["ready_for_closed_improvement_loop"],
        "validation_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_result_validation(validation: dict[str, Any]) -> None:
    _validate_artifact(validation)
    if validation.get("artifact_type") != RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("replay certification failed closed: invalid artifact type")
    if validation.get("validation_status") != RESULT_VALIDATION_COMPLETED:
        raise FailClosedRuntimeError("replay certification failed closed: completed validation required")
    if validation.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: replay lineage broken")
    if validation.get("fail_closed_preserved") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: fail closed evidence missing")
    if validation.get("deterministic_validation_preserved") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: deterministic validation missing")
    if validation.get("ready_for_replay_certification") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: certification readiness missing")
    readiness = validation.get("certification_readiness")
    if not isinstance(readiness, dict):
        raise FailClosedRuntimeError("replay certification failed closed: certification readiness invalid")
    if readiness.get("ready_for_replay_certification") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: certification readiness invalid")
    if readiness.get("requires_replay_certification") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: replay certification requirement missing")
    if readiness.get("improvement_loop_entry_allowed") is not False:
        raise FailClosedRuntimeError("replay certification failed closed: premature improvement loop entry detected")
    _require_string(validation.get("source_worker_execution"), "source_worker_execution")
    _require_hash(validation.get("source_worker_execution_hash"), "source_worker_execution_hash")
    if not _string_list(validation.get("replay_references")):
        raise FailClosedRuntimeError("replay certification failed closed: replay references required")
    if not _hash_list(validation.get("replay_hashes")):
        raise FailClosedRuntimeError("replay certification failed closed: replay hashes required")
    evidence = validation.get("validation_evidence")
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("replay certification failed closed: validation evidence invalid")
    if validation.get("validation_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("replay certification failed closed: validation evidence hash mismatch")
    _verify_artifact_hash(evidence)
    if evidence.get("lineage_integrity_validated") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: lineage integrity not validated")
    if evidence.get("governance_constraints_validated") is not True:
        raise FailClosedRuntimeError("replay certification failed closed: governance compliance not validated")
    for flag in (
        "execution_result_modified",
        "governance_modified",
        "worker_invoked",
        "provider_invoked",
    ):
        if validation.get(flag) is not False:
            raise FailClosedRuntimeError(f"replay certification failed closed: validation {flag} must be false")


def _certification_artifact(
    *,
    certification_id: str,
    validation: dict[str, Any],
    certified_by: str,
    certified_at: str,
    certification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    lineage_evidence = {
        "source_result_validation_hash": validation["artifact_hash"],
        "validation_evidence_hash": validation["validation_evidence_hash"],
        "source_worker_execution_hash": validation["source_worker_execution_hash"],
        "replay_hashes": deepcopy(validation["replay_hashes"]),
        "lineage_integrity_validated": True,
    }
    artifact = {
        "artifact_type": REPLAY_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_CERTIFICATION_RUNTIME_VERSION,
        "replay_certification_id": _require_string(certification_id, "certification_id"),
        "certification_status": certification_status,
        "certification_decision": "CERTIFIED_FOR_CLOSED_IMPROVEMENT_LOOP",
        "source_result_validation": validation["result_validation_id"],
        "source_result_validation_hash": validation["artifact_hash"],
        "source_worker_execution": validation["source_worker_execution"],
        "source_worker_execution_hash": validation["source_worker_execution_hash"],
        "validation_references": {
            "result_validation_reference": validation["result_validation_id"],
            "validation_evidence_hash": validation["validation_evidence_hash"],
            "validation_status": validation["validation_status"],
        },
        "replay_references": deepcopy(validation["replay_references"]),
        "replay_hashes": deepcopy(validation["replay_hashes"]),
        "certification_rationale": (
            "Validated result is replay-lineage-preserving, governance-compliant, "
            "fail-closed, and ready for closed replay-derived improvement loops."
        ),
        "lineage_evidence": lineage_evidence,
        "certified_by": _require_string(certified_by, "certified_by"),
        "certified_at": _require_string(certified_at, "certified_at"),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "deterministic_certification_preserved": True,
        "ready_for_closed_improvement_loop": True,
        "validation_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "improvement_intent_created": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_certification_artifact(
    *,
    certification_id: str,
    result_validation_artifact: dict[str, Any],
    certified_by: str,
    certified_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REPLAY_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_CERTIFICATION_RUNTIME_VERSION,
        "replay_certification_id": certification_id if isinstance(certification_id, str) else "INVALID",
        "certification_status": FAILED_CLOSED,
        "certification_decision": FAILED_CLOSED,
        "source_result_validation": result_validation_artifact.get("result_validation_id")
        if isinstance(result_validation_artifact, dict)
        else None,
        "source_result_validation_hash": result_validation_artifact.get("artifact_hash")
        if isinstance(result_validation_artifact, dict)
        else None,
        "source_worker_execution": result_validation_artifact.get("source_worker_execution")
        if isinstance(result_validation_artifact, dict)
        else None,
        "source_worker_execution_hash": result_validation_artifact.get("source_worker_execution_hash")
        if isinstance(result_validation_artifact, dict)
        else None,
        "validation_references": {},
        "replay_references": [],
        "replay_hashes": [],
        "certification_rationale": "Replay certification failed closed before closed improvement-loop readiness.",
        "lineage_evidence": {},
        "certified_by": certified_by if isinstance(certified_by, str) else None,
        "certified_at": certified_at if isinstance(certified_at, str) else None,
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "deterministic_certification_preserved": True,
        "ready_for_closed_improvement_loop": False,
        "validation_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "improvement_intent_created": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(certification: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(certification)
    artifact = {
        "event_type": "REPLAY_CERTIFICATION_RETURNED",
        "replay_certification_reference": certification["replay_certification_id"],
        "replay_certification_hash": certification["artifact_hash"],
        "certification_status": certification["certification_status"],
        "certification_decision": certification["certification_decision"],
        "source_result_validation": certification["source_result_validation"],
        "replay_lineage_preserved": certification["replay_lineage_preserved"],
        "fail_closed_preserved": certification["fail_closed_preserved"],
        "ready_for_closed_improvement_loop": certification["ready_for_closed_improvement_loop"],
        "validation_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": certification["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(certification: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_REPLAY_CERTIFICATION_RUNTIME_VERSION,
        "certification_status": certification["certification_status"],
        "replay_certification_artifact": deepcopy(certification),
        "replay_certification_returned_artifact": deepcopy(returned),
        "replay_certification_replay_reference": str(replay_path),
        "replay_certification_completed": certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED,
        "replay_certification_artifact_generated": certification["artifact_type"] == REPLAY_CERTIFICATION_ARTIFACT_V1,
        "replay_lineage_preserved": certification["replay_lineage_preserved"],
        "fail_closed_preserved": certification["fail_closed_preserved"],
        "ready_for_closed_improvement_loop": certification["ready_for_closed_improvement_loop"],
        "failure_reason": certification["failure_reason"],
    }
    capture["replay_certification_capture_hash"] = replay_hash(capture)
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
            raise FailClosedRuntimeError("replay certification failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("replay certification failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("replay certification artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("replay certification artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("replay certification replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("replay certification replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replay certification failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"replay certification failed closed: {field_name} must be a replay hash")
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
    return "replay certification failed closed"
