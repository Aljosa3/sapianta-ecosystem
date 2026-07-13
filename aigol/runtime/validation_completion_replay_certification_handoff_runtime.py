"""Compose completed governed validation evidence for Replay Certification."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_validation_runtime import (
    GOVERNED_VALIDATION_COMPLETED,
    GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1,
)
from aigol.runtime.governed_validation_suite_runtime import (
    GOVERNED_VALIDATION_SUITE_COMPLETED,
    GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1,
    VALIDATION_SUITE_BLOCKED,
    VALIDATION_SUITE_FAILED,
    VALIDATION_SUITE_PASSED,
    VALIDATION_SUITE_SUMMARY_ARTIFACT_V1,
    VALIDATION_SUITE_TIMED_OUT,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_replay import reconstruct_governed_validation_replay
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.platform_core_validation_suite_replay import (
    reconstruct_governed_validation_suite_replay,
)
from aigol.runtime.result_validation_runtime import (
    AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
    RESULT_VALIDATION_ARTIFACT_V1,
    RESULT_VALIDATION_COMPLETED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.workers.validation_command_worker import (
    VALIDATION_BLOCKED,
    VALIDATION_FAILED,
    VALIDATION_PASSED,
    VALIDATION_TIMED_OUT,
)


VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION = (
    "G27_11_VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_V1"
)
VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1 = (
    "VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1"
)
VALIDATION_COMPLETION_HANDOFF_READY = "VALIDATION_COMPLETION_HANDOFF_READY"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "validation_completion_replay_certification_handoff_recorded"

AUTHORITY_FLAGS = {
    "executes_validation": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "authorizes_execution": False,
    "mutates_repository": False,
    "certifies_results": False,
    "creates_certification_runtime": False,
    "creates_replay_runtime": False,
}


def compose_validation_completion_replay_certification_handoff(
    *,
    handoff_id: str,
    validation_artifact: dict[str, Any],
    validation_replay_reference: str | Path,
    composed_by: str,
    composed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose one existing Result Validation contract without certifying it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(handoff_id, "handoff_id")
        source = _validate_source_artifact(validation_artifact)
        source_replay = Path(validation_replay_reference)
        lineage = _validated_lifecycle_lineage(source, source_replay)
        composer = _require_string(composed_by, "composed_by")
        timestamp = _require_string(composed_at, "composed_at")
        result_validation = _result_validation_artifact(
            handoff_id=identifier,
            source=source,
            lineage=lineage,
            composed_by=composer,
            composed_at=timestamp,
        )
        artifact = _handoff_artifact(
            handoff_id=identifier,
            handoff_status=VALIDATION_COMPLETION_HANDOFF_READY,
            source=source,
            source_replay_reference=str(source_replay),
            lineage=lineage,
            result_validation=result_validation,
            composed_by=composer,
            composed_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_handoff_artifact(
            handoff_id=handoff_id,
            validation_artifact=validation_artifact,
            validation_replay_reference=validation_replay_reference,
            composed_by=composed_by,
            composed_at=composed_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def validate_validation_completion_replay_certification_handoff_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one canonical validation-completion handoff artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("validation completion handoff artifact must be a JSON object")
    candidate = deepcopy(artifact)
    _verify_handoff_artifact(candidate)
    return candidate


def reconstruct_validation_completion_replay_certification_handoff(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and verify one handoff replay."""

    wrapper = load_json(Path(replay_dir) / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("validation completion handoff replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "validation completion handoff replay hash mismatch")
    artifact = validate_validation_completion_replay_certification_handoff_artifact(wrapper.get("artifact"))
    return {
        "handoff_id": artifact["handoff_id"],
        "handoff_status": artifact["handoff_status"],
        "source_validation_artifact_type": artifact["source_validation_artifact_type"],
        "source_validation_artifact_hash": artifact["source_validation_artifact_hash"],
        "source_completion_artifact_hash": artifact["source_completion_artifact_hash"],
        "result_validation_artifact": deepcopy(artifact["result_validation_artifact"]),
        "result_validation_artifact_hash": artifact["result_validation_artifact_hash"],
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "plan_lineage_preserved": artifact["plan_lineage_preserved"],
        "ready_for_replay_certification": artifact["ready_for_replay_certification"],
        "requires_replay_certification": artifact["requires_replay_certification"],
        "fail_closed": artifact["handoff_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": wrapper["replay_hash"],
    }


def _validate_source_artifact(source: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise FailClosedRuntimeError("validation completion handoff failed closed: validation artifact required")
    artifact = deepcopy(source)
    _verify_hash(artifact, "artifact_hash", "validation completion handoff source artifact hash mismatch")
    artifact_type = artifact.get("artifact_type")
    if artifact_type == VALIDATION_RESULT_ARTIFACT_V1:
        if artifact.get("validation_status") not in {
            VALIDATION_PASSED,
            VALIDATION_FAILED,
            VALIDATION_TIMED_OUT,
            VALIDATION_BLOCKED,
        }:
            raise FailClosedRuntimeError("validation completion handoff failed closed: validation result status invalid")
    elif artifact_type == VALIDATION_SUITE_SUMMARY_ARTIFACT_V1:
        if artifact.get("validation_suite_status") not in {
            VALIDATION_SUITE_PASSED,
            VALIDATION_SUITE_FAILED,
            VALIDATION_SUITE_TIMED_OUT,
            VALIDATION_SUITE_BLOCKED,
        }:
            raise FailClosedRuntimeError("validation completion handoff failed closed: validation suite status invalid")
    else:
        raise FailClosedRuntimeError("validation completion handoff failed closed: unsupported validation artifact type")
    return artifact


def _validated_lifecycle_lineage(source: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    if not replay_path.is_dir():
        raise FailClosedRuntimeError("validation completion handoff failed closed: validation replay required")
    if source["artifact_type"] == VALIDATION_RESULT_ARTIFACT_V1:
        return _single_lifecycle_lineage(source, replay_path)
    return _suite_lifecycle_lineage(source, replay_path)


def _single_lifecycle_lineage(source: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    reconstructed = reconstruct_governed_validation_replay(replay_path)
    candidate = _replay_artifact(replay_path, 0, "validation_candidate_recorded")
    worker_result = _replay_artifact(replay_path, 5, "worker_result_recorded")
    recorded_source = _replay_artifact(replay_path, 6, "validation_result_recorded")
    completion = _replay_artifact(replay_path, 7, "completion_recorded")
    _require_exact_source(source, recorded_source)
    if completion.get("artifact_type") != GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1:
        raise FailClosedRuntimeError("validation completion handoff failed closed: single completion artifact required")
    if completion.get("execution_status") != GOVERNED_VALIDATION_COMPLETED or completion.get("fail_closed") is not False:
        raise FailClosedRuntimeError("validation completion handoff failed closed: completed validation lifecycle required")
    if completion.get("validation_result_hash") != source["artifact_hash"]:
        raise FailClosedRuntimeError("validation completion handoff failed closed: completion result mismatch")
    if completion.get("candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: completion candidate mismatch")
    if source.get("candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: validation candidate mismatch")
    if source.get("validation_status") != reconstructed.get("validation_status"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: reconstructed status mismatch")
    return _lineage_record(
        replay_path=replay_path,
        replay_hash_value=reconstructed["replay_hash"],
        candidate=candidate,
        execution_artifact=worker_result,
        completion=completion,
        validation_status=source["validation_status"],
    )


def _suite_lifecycle_lineage(source: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    reconstructed = reconstruct_governed_validation_suite_replay(replay_path)
    candidate = _replay_artifact(replay_path, 0, "validation_suite_candidate_recorded")
    command_execution = _replay_artifact(replay_path, 4, "command_execution_recorded")
    recorded_source = _replay_artifact(replay_path, 5, "validation_suite_summary_recorded")
    completion = _replay_artifact(replay_path, 7, "completion_recorded")
    _require_exact_source(source, recorded_source)
    if completion.get("artifact_type") != GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1:
        raise FailClosedRuntimeError("validation completion handoff failed closed: suite completion artifact required")
    if completion.get("execution_status") != GOVERNED_VALIDATION_SUITE_COMPLETED or completion.get("fail_closed") is not False:
        raise FailClosedRuntimeError("validation completion handoff failed closed: completed validation suite required")
    if completion.get("suite_summary_hash") != source["artifact_hash"]:
        raise FailClosedRuntimeError("validation completion handoff failed closed: completion summary mismatch")
    if completion.get("candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: completion candidate mismatch")
    if source.get("candidate_hash") != candidate.get("artifact_hash"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: validation suite candidate mismatch")
    if source.get("validation_suite_status") != reconstructed.get("validation_suite_status"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: reconstructed suite status mismatch")
    return _lineage_record(
        replay_path=replay_path,
        replay_hash_value=reconstructed["replay_hash"],
        candidate=candidate,
        execution_artifact=command_execution,
        completion=completion,
        validation_status=source["validation_suite_status"],
    )


def _lineage_record(
    *,
    replay_path: Path,
    replay_hash_value: str,
    candidate: dict[str, Any],
    execution_artifact: dict[str, Any],
    completion: dict[str, Any],
    validation_status: str,
) -> dict[str, Any]:
    plan_lineage = _plan_lineage(candidate)
    return {
        "source_validation_replay_reference": str(replay_path),
        "source_validation_replay_hash": _require_hash(replay_hash_value, "source validation replay hash"),
        "source_execution_reference": _require_string(completion.get("execution_id"), "source execution reference"),
        "source_execution_artifact_hash": _require_hash(
            execution_artifact.get("artifact_hash"), "source execution artifact hash"
        ),
        "source_completion_artifact_type": _require_string(
            completion.get("artifact_type"), "source completion artifact type"
        ),
        "source_completion_artifact_hash": _require_hash(
            completion.get("artifact_hash"), "source completion artifact hash"
        ),
        "source_execution_candidate": _require_string(candidate.get("candidate_id"), "source execution candidate"),
        "source_execution_candidate_hash": _require_hash(
            candidate.get("artifact_hash"), "source execution candidate hash"
        ),
        "source_validation_status": validation_status,
        "plan_lineage": plan_lineage,
        "plan_lineage_preserved": bool(plan_lineage),
    }


def _plan_lineage(candidate: dict[str, Any]) -> dict[str, Any]:
    associated = candidate.get("associated_reference")
    if not isinstance(associated, dict) or not associated:
        return {}
    lineage = deepcopy(associated)
    if "validation_plan_id" not in lineage:
        return {}
    _require_string(lineage.get("validation_plan_id"), "validation plan id")
    _require_hash(lineage.get("validation_plan_artifact_hash"), "validation plan artifact hash")
    _require_hash(lineage.get("validation_plan_hash"), "validation plan hash")
    return lineage


def _result_validation_artifact(
    *,
    handoff_id: str,
    source: dict[str, Any],
    lineage: dict[str, Any],
    composed_by: str,
    composed_at: str,
) -> dict[str, Any]:
    validation_id = f"{handoff_id}:RESULT-VALIDATION"
    evidence = {
        "artifact_type": "RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1",
        "runtime_version": VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION,
        "result_validation_id": validation_id,
        "source_worker_execution": lineage["source_execution_reference"],
        "source_worker_execution_hash": lineage["source_execution_artifact_hash"],
        "source_execution_candidate": lineage["source_execution_candidate"],
        "source_execution_candidate_hash": lineage["source_execution_candidate_hash"],
        "source_validation_artifact_type": source["artifact_type"],
        "source_validation_artifact_hash": source["artifact_hash"],
        "source_validation_status": lineage["source_validation_status"],
        "source_completion_artifact_type": lineage["source_completion_artifact_type"],
        "source_completion_artifact_hash": lineage["source_completion_artifact_hash"],
        "replay_references": [lineage["source_validation_replay_reference"]],
        "replay_hashes": [lineage["source_validation_replay_hash"]],
        "plan_lineage": deepcopy(lineage["plan_lineage"]),
        "plan_lineage_preserved": lineage["plan_lineage_preserved"],
        "governance_constraints_validated": True,
        "lineage_integrity_validated": True,
        "validated_at": composed_at,
        "replay_visible": True,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    artifact = {
        "artifact_type": RESULT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "result_validation_id": validation_id,
        "validation_status": RESULT_VALIDATION_COMPLETED,
        "source_worker_execution": lineage["source_execution_reference"],
        "source_worker_execution_hash": lineage["source_execution_artifact_hash"],
        "source_execution_candidate": lineage["source_execution_candidate"],
        "source_execution_candidate_hash": lineage["source_execution_candidate_hash"],
        "source_validation_artifact_type": source["artifact_type"],
        "source_validation_artifact_hash": source["artifact_hash"],
        "source_validation_status": lineage["source_validation_status"],
        "source_completion_artifact_type": lineage["source_completion_artifact_type"],
        "source_completion_artifact_hash": lineage["source_completion_artifact_hash"],
        "validation_evidence": evidence,
        "validation_evidence_hash": evidence["artifact_hash"],
        "validation_rationale": (
            "Completed governed validation lifecycle and Replay lineage were deterministically "
            "verified for existing Replay Certification input."
        ),
        "replay_references": [lineage["source_validation_replay_reference"]],
        "replay_hashes": [lineage["source_validation_replay_hash"]],
        "plan_lineage": deepcopy(lineage["plan_lineage"]),
        "plan_lineage_preserved": lineage["plan_lineage_preserved"],
        "certification_readiness": {
            "ready_for_replay_certification": True,
            "improvement_loop_entry_allowed": False,
            "requires_replay_certification": True,
        },
        "validated_by": composed_by,
        "validated_at": composed_at,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "deterministic_validation_preserved": True,
        "ready_for_replay_certification": True,
        "execution_result_modified": False,
        "governance_modified": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _handoff_artifact(
    *,
    handoff_id: str,
    handoff_status: str,
    source: dict[str, Any],
    source_replay_reference: str,
    lineage: dict[str, Any],
    result_validation: dict[str, Any] | None,
    composed_by: str,
    composed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    ready = handoff_status == VALIDATION_COMPLETION_HANDOFF_READY
    artifact = {
        "artifact_type": VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1,
        "runtime_version": VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION,
        "handoff_id": handoff_id,
        "handoff_status": handoff_status,
        "source_validation_artifact_type": source.get("artifact_type"),
        "source_validation_artifact_hash": source.get("artifact_hash"),
        "source_validation_replay_reference": source_replay_reference,
        "source_validation_replay_hash": lineage.get("source_validation_replay_hash"),
        "source_completion_artifact_type": lineage.get("source_completion_artifact_type"),
        "source_completion_artifact_hash": lineage.get("source_completion_artifact_hash"),
        "source_execution_candidate": lineage.get("source_execution_candidate"),
        "source_execution_candidate_hash": lineage.get("source_execution_candidate_hash"),
        "source_validation_status": lineage.get("source_validation_status"),
        "plan_lineage": deepcopy(lineage.get("plan_lineage") or {}),
        "plan_lineage_preserved": lineage.get("plan_lineage_preserved", False),
        "result_validation_artifact": deepcopy(result_validation),
        "result_validation_artifact_hash": (
            result_validation.get("artifact_hash") if isinstance(result_validation, dict) else None
        ),
        "replay_lineage_preserved": ready,
        "deterministic_validation_preserved": True,
        "ready_for_replay_certification": ready,
        "requires_replay_certification": True,
        "replay_visible": True,
        "validation_executed": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "composed_by": composed_by,
        "composed_at": composed_at,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_handoff_artifact(
    *,
    handoff_id: Any,
    validation_artifact: Any,
    validation_replay_reference: Any,
    composed_by: Any,
    composed_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source = validation_artifact if isinstance(validation_artifact, dict) else {}
    return _handoff_artifact(
        handoff_id=_safe_string(handoff_id),
        handoff_status=FAILED_CLOSED,
        source=source,
        source_replay_reference=_safe_string(validation_replay_reference),
        lineage={},
        result_validation=None,
        composed_by=_safe_string(composed_by),
        composed_at=_safe_string(composed_at),
        failure_reason=failure_reason,
    )


def _verify_handoff_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("validation completion handoff artifact type mismatch")
    if artifact.get("runtime_version") != VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("validation completion handoff runtime version mismatch")
    _verify_hash(artifact, "artifact_hash", "validation completion handoff artifact hash mismatch")
    for field, expected in AUTHORITY_FLAGS.items():
        if artifact.get("authority_flags", {}).get(field) is not expected:
            raise FailClosedRuntimeError("validation completion handoff authority flags invalid")
    for field in (
        "validation_executed",
        "worker_invoked",
        "provider_invoked",
        "execution_authorized",
        "repository_mutated",
        "certification_performed",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"validation completion handoff {field} must be false")
    if artifact.get("handoff_status") == VALIDATION_COMPLETION_HANDOFF_READY:
        if artifact.get("source_validation_artifact_type") not in {
            VALIDATION_RESULT_ARTIFACT_V1,
            VALIDATION_SUITE_SUMMARY_ARTIFACT_V1,
        }:
            raise FailClosedRuntimeError("validation completion handoff source type invalid")
        for field in (
            "source_validation_artifact_hash",
            "source_validation_replay_hash",
            "source_completion_artifact_hash",
            "source_execution_candidate_hash",
        ):
            _require_hash(artifact.get(field), field)
        result_validation = artifact.get("result_validation_artifact")
        _validate_result_validation_contract(result_validation)
        if artifact.get("result_validation_artifact_hash") != result_validation["artifact_hash"]:
            raise FailClosedRuntimeError("validation completion handoff result validation hash mismatch")
        for field in (
            "replay_lineage_preserved",
            "deterministic_validation_preserved",
            "ready_for_replay_certification",
            "requires_replay_certification",
        ):
            if artifact.get(field) is not True:
                raise FailClosedRuntimeError(f"validation completion handoff {field} must be true")
        if artifact.get("failure_reason") is not None:
            raise FailClosedRuntimeError("validation completion handoff ready artifact has failure reason")
    elif artifact.get("handoff_status") == FAILED_CLOSED:
        if artifact.get("result_validation_artifact") is not None:
            raise FailClosedRuntimeError("failed validation completion handoff must not emit certification input")
        if artifact.get("ready_for_replay_certification") is not False:
            raise FailClosedRuntimeError("failed validation completion handoff cannot be certification ready")
        _require_string(artifact.get("failure_reason"), "failure_reason")
    else:
        raise FailClosedRuntimeError("validation completion handoff status invalid")


def _validate_result_validation_contract(artifact: Any) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("validation completion handoff result validation contract invalid")
    _verify_hash(artifact, "artifact_hash", "validation completion handoff result validation hash mismatch")
    if artifact.get("validation_status") != RESULT_VALIDATION_COMPLETED:
        raise FailClosedRuntimeError("validation completion handoff result validation is incomplete")
    readiness = artifact.get("certification_readiness")
    if not isinstance(readiness, dict):
        raise FailClosedRuntimeError("validation completion handoff certification readiness invalid")
    if readiness.get("ready_for_replay_certification") is not True:
        raise FailClosedRuntimeError("validation completion handoff certification readiness invalid")
    if readiness.get("requires_replay_certification") is not True:
        raise FailClosedRuntimeError("validation completion handoff certification requirement missing")
    if readiness.get("improvement_loop_entry_allowed") is not False:
        raise FailClosedRuntimeError("validation completion handoff premature improvement loop entry")
    evidence = artifact.get("validation_evidence")
    if not isinstance(evidence, dict) or artifact.get("validation_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("validation completion handoff validation evidence invalid")
    _verify_hash(evidence, "artifact_hash", "validation completion handoff validation evidence hash mismatch")
    if evidence.get("lineage_integrity_validated") is not True:
        raise FailClosedRuntimeError("validation completion handoff lineage evidence invalid")
    if evidence.get("governance_constraints_validated") is not True:
        raise FailClosedRuntimeError("validation completion handoff governance evidence invalid")
    for field in (
        "replay_lineage_preserved",
        "fail_closed_preserved",
        "deterministic_validation_preserved",
        "ready_for_replay_certification",
    ):
        if artifact.get(field) is not True:
            raise FailClosedRuntimeError(f"validation completion handoff result {field} must be true")
    for field in ("execution_result_modified", "governance_modified", "worker_invoked", "provider_invoked"):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"validation completion handoff result {field} must be false")


def _replay_artifact(replay_path: Path, index: int, step: str) -> dict[str, Any]:
    wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("validation completion handoff failed closed: replay artifact missing")
    return artifact


def _require_exact_source(provided: dict[str, Any], recorded: dict[str, Any]) -> None:
    if provided.get("artifact_type") != recorded.get("artifact_type"):
        raise FailClosedRuntimeError("validation completion handoff failed closed: replay source type mismatch")
    if provided.get("artifact_hash") != recorded.get("artifact_hash") or provided != recorded:
        raise FailClosedRuntimeError("validation completion handoff failed closed: replay source artifact mismatch")


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        path = replay_path / f"000_{REPLAY_STEP}.json"
        if path.exists():
            raise FailClosedRuntimeError("validation completion handoff replay already exists")
        wrapper = {
            "replay_index": 0,
            "replay_step": REPLAY_STEP,
            "artifact": deepcopy(artifact),
            "replay_service_version": VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION,
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(path, wrapper)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("validation completion handoff failed closed: replay already exists")


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_RUNTIME_VERSION,
        "handoff_id": artifact["handoff_id"],
        "handoff_status": artifact["handoff_status"],
        "handoff_artifact": deepcopy(artifact),
        "result_validation_artifact": deepcopy(artifact["result_validation_artifact"]),
        "replay_reference": str(replay_path),
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "plan_lineage_preserved": artifact["plan_lineage_preserved"],
        "ready_for_replay_certification": artifact["ready_for_replay_certification"],
        "requires_replay_certification": artifact["requires_replay_certification"],
        "certification_performed": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "fail_closed": artifact["handoff_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _verify_hash(artifact: dict[str, Any], field: str, message: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(message)
    actual = artifact.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(artifact)
    expected.pop(field)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"validation completion handoff requires {field}")
    return value.strip()


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"validation completion handoff requires {field}")
    return text


def _safe_string(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    return value.strip() if isinstance(value, str) and value.strip() else "INVALID"


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "validation completion handoff failed closed"
