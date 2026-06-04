"""Replay-visible governed lifecycle termination for the current AiGOL chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import (
    INTEGRITY_VERIFIED,
    POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1,
    REVIEW_COMPLETED,
    reconstruct_post_execution_replay_review,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION = "AIGOL_GOVERNED_TERMINATION_RUNTIME_V1"
GOVERNED_TERMINATION_EVIDENCE_ARTIFACT_V1 = "GOVERNED_TERMINATION_EVIDENCE_ARTIFACT_V1"
GOVERNED_TERMINATION_CLASSIFICATION_ARTIFACT_V1 = "GOVERNED_TERMINATION_CLASSIFICATION_ARTIFACT_V1"
GOVERNED_TERMINATION_ARTIFACT_V1 = "GOVERNED_TERMINATION_ARTIFACT_V1"
GOVERNED_TERMINATION_RESULT_ARTIFACT_V1 = "GOVERNED_TERMINATION_RESULT_ARTIFACT_V1"
TERMINATED = "TERMINATED"
FAILED_CLOSED = "FAILED_CLOSED"
TERMINAL_OPERATION_STATE = "TERMINAL_OPERATION_STATE"
SEPARATE_GOVERNED_REQUEST_REQUIRED = "SEPARATE_GOVERNED_REQUEST_REQUIRED"

REPLAY_STEPS = (
    "termination_evidence_recorded",
    "termination_classification_recorded",
    "termination_artifact_recorded",
    "termination_result_recorded",
)


def terminate_reviewed_operation(
    *,
    governed_termination_id: str,
    post_execution_replay_review_artifact: dict[str, Any],
    post_execution_replay_review_replay_reference: str,
    terminated_by: str,
    terminated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Close a reviewed operation without continuation, mutation, or new work."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        review = _load_review_lineage(
            Path(post_execution_replay_review_replay_reference),
            post_execution_replay_review_artifact,
        )
        evidence = _evidence_artifact(
            termination_id=governed_termination_id,
            review=review,
            review_replay_reference=post_execution_replay_review_replay_reference,
            terminated_at=terminated_at,
        )
        classification = _classification_artifact(
            termination_id=governed_termination_id,
            evidence=evidence,
            terminated_at=terminated_at,
        )
        termination = _termination_artifact(
            termination_id=governed_termination_id,
            evidence=evidence,
            classification=classification,
            review=review,
            terminated_by=terminated_by,
            terminated_at=terminated_at,
        )
        result = _result_artifact(
            termination_id=governed_termination_id,
            evidence=evidence,
            classification=classification,
            termination=termination,
            terminated_at=terminated_at,
            status=TERMINATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], termination)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, termination, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            termination_id=governed_termination_id,
            review_reference=(
                post_execution_replay_review_artifact.get("post_execution_replay_review_id")
                if isinstance(post_execution_replay_review_artifact, dict)
                else None
            ),
            review_replay_reference=post_execution_replay_review_replay_reference,
            terminated_at=terminated_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_governed_termination_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct governed termination replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed termination replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed termination replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "governed termination replay artifact")
        wrappers.append(wrapper)

    evidence, classification, termination, result = (wrapper["artifact"] for wrapper in wrappers)
    if classification.get("termination_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("governed termination replay evidence lineage mismatch")
    if termination.get("termination_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("governed termination replay classification lineage mismatch")
    if result.get("governed_termination_hash") != termination["artifact_hash"]:
        raise FailClosedRuntimeError("governed termination replay continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], termination["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("governed termination replay chain mismatch")
    _validate_termination_artifact(termination)
    _load_review_lineage(Path(evidence["post_execution_replay_review_replay_reference"]), None, termination=termination)
    return {
        "governed_termination_id": termination["governed_termination_id"],
        "termination_status": result["termination_status"],
        "terminal_operation_state": termination["terminal_operation_state"],
        "post_execution_replay_review_reference": termination["post_execution_replay_review_reference"],
        "worker_result_validation_reference": termination["worker_result_validation_reference"],
        "worker_id": termination["worker_id"],
        "chain_id": termination["chain_id"],
        "future_improvement_intent_handoff_status": termination["future_improvement_intent_handoff_status"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_termination_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_governed_termination_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Governed Termination",
        "",
        f"Termination Status: {capture.get('termination_status')}",
        f"Terminal Operation State: {capture.get('terminal_operation_state')}",
        f"Governed Termination Reference: {capture.get('governed_termination_reference')}",
        f"Post-Execution Replay Review Reference: {capture.get('post_execution_replay_review_reference')}",
        f"Replay Reference: {capture.get('governed_termination_replay_reference')}",
        "",
        "Operation lifecycle closed.",
        "No improvement intent created.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_review_lineage(
    review_replay_path: Path,
    provided_review: dict[str, Any] | None,
    *,
    termination: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reconstructed = reconstruct_post_execution_replay_review(review_replay_path)
    if reconstructed.get("review_status") != REVIEW_COMPLETED:
        raise FailClosedRuntimeError("governed termination failed closed: replay review invalid")
    wrappers = []
    for index, step in enumerate(
        (
            "review_evidence_recorded",
            "review_classification_recorded",
            "review_artifact_recorded",
            "review_result_recorded",
        )
    ):
        wrapper = load_json(review_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed termination failed closed: replay review corruption")
        _verify_artifact_hash(artifact, "post-execution replay review lineage artifact")
        wrappers.append(wrapper)
    evidence, classification, review, result = (wrapper["artifact"] for wrapper in wrappers)
    _validate_review_artifact(review)
    if provided_review is not None:
        _verify_artifact_hash(provided_review, "provided post-execution replay review artifact")
        if provided_review.get("post_execution_replay_review_id") != review["post_execution_replay_review_id"]:
            raise FailClosedRuntimeError("governed termination failed closed: replay review mismatch")
        if provided_review.get("artifact_hash") != review["artifact_hash"]:
            raise FailClosedRuntimeError("governed termination failed closed: replay review mismatch")
    if termination is not None:
        if termination.get("post_execution_replay_review_reference") != review["post_execution_replay_review_id"]:
            raise FailClosedRuntimeError("governed termination failed closed: replay review mismatch")
        if termination.get("post_execution_replay_review_hash") != review["artifact_hash"]:
            raise FailClosedRuntimeError("governed termination failed closed: replay review mismatch")
    checks = {
        "review_continuity": result["post_execution_replay_review_hash"] == review["artifact_hash"],
        "review_evidence_continuity": classification["review_evidence_hash"] == evidence["artifact_hash"],
        "validation_continuity": review["worker_result_validation_reference"]
        == evidence["worker_result_validation_reference"]
        and review["worker_result_validation_hash"] == evidence["worker_result_validation_hash"],
        "authorization_continuity": review["authorization_reference"] == evidence["authorization_reference"]
        and review["authorization_hash"] == evidence["authorization_hash"],
        "packet_continuity": review["execution_packet_reference"] == evidence["execution_packet_reference"]
        and review["execution_packet_hash"] == evidence["execution_packet_hash"],
        "worker_continuity": review["worker_id"] == evidence["worker_id"]
        and review["worker_hash"] == evidence["worker_hash"],
        "chain_continuity": len({evidence["chain_id"], classification["chain_id"], review["chain_id"], result["chain_id"]}) == 1,
        "replay_continuity": reconstructed["review_status"] == REVIEW_COMPLETED,
        "authority_continuity": _review_authority_continuity(review),
        "hash_continuity": all(bool(wrapper["artifact"].get("artifact_hash")) for wrapper in wrappers),
        "terminal_precondition": review.get("terminated") is False,
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("governed termination failed closed: closure precondition invalid")
    return review


def _evidence_artifact(
    *,
    termination_id: str,
    review: dict[str, Any],
    review_replay_reference: str,
    terminated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_TERMINATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION,
        "termination_evidence_id": f"{_require_string(termination_id, 'governed_termination_id')}:EVIDENCE",
        "post_execution_replay_review_reference": review["post_execution_replay_review_id"],
        "post_execution_replay_review_hash": review["artifact_hash"],
        "post_execution_replay_review_replay_reference": _require_string(
            review_replay_reference, "post_execution_replay_review_replay_reference"
        ),
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_validation_hash": review["worker_result_validation_hash"],
        "authorization_reference": review["authorization_reference"],
        "authorization_hash": review["authorization_hash"],
        "execution_packet_reference": review["execution_packet_reference"],
        "execution_packet_hash": review["execution_packet_hash"],
        "worker_id": review["worker_id"],
        "worker_hash": review["worker_hash"],
        "chain_id": review["chain_id"],
        "closure_preconditions": {
            "review_completed": review["review_status"] == REVIEW_COMPLETED,
            "replay_integrity_verified": review["replay_integrity_assessment"] == INTEGRITY_VERIFIED,
            "authority_integrity_verified": review["authority_integrity_assessment"] == INTEGRITY_VERIFIED,
            "execution_integrity_verified": review["execution_integrity_assessment"] == INTEGRITY_VERIFIED,
            "validation_integrity_verified": review["validation_integrity_assessment"] == INTEGRITY_VERIFIED,
            "not_previously_terminated": review["terminated"] is False,
        },
        "recorded_at": _require_string(terminated_at, "terminated_at"),
        "replay_visible": True,
        **_post_termination_boundary_flags(),
    }
    if not all(artifact["closure_preconditions"].values()):
        raise FailClosedRuntimeError("governed termination failed closed: closure precondition invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *, termination_id: str, evidence: dict[str, Any], terminated_at: str
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_TERMINATION_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION,
        "termination_classification_id": f"{_require_string(termination_id, 'governed_termination_id')}:CLASSIFICATION",
        "termination_evidence_reference": evidence["termination_evidence_id"],
        "termination_evidence_hash": evidence["artifact_hash"],
        "chain_id": evidence["chain_id"],
        "closure_classification": "GOVERNED_OPERATION_LIFECYCLE_CLOSURE",
        "terminal_state_classification": TERMINAL_OPERATION_STATE,
        "continuation_prohibited": True,
        "retry_prohibited": True,
        "resurrection_prohibited": True,
        "new_work_prohibited": True,
        "improvement_intent_handoff_requires_separate_governed_request": True,
        "classified_at": _require_string(terminated_at, "terminated_at"),
        "replay_visible": True,
        **_post_termination_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _termination_artifact(
    *,
    termination_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    review: dict[str, Any],
    terminated_by: str,
    terminated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_TERMINATION_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION,
        "governed_termination_id": _require_string(termination_id, "governed_termination_id"),
        "termination_status": TERMINATED,
        "terminal_operation_state": TERMINAL_OPERATION_STATE,
        "termination_evidence_reference": evidence["termination_evidence_id"],
        "termination_evidence_hash": evidence["artifact_hash"],
        "termination_classification_reference": classification["termination_classification_id"],
        "termination_classification_hash": classification["artifact_hash"],
        "post_execution_replay_review_reference": review["post_execution_replay_review_id"],
        "post_execution_replay_review_hash": review["artifact_hash"],
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_validation_hash": review["worker_result_validation_hash"],
        "authorization_reference": review["authorization_reference"],
        "authorization_hash": review["authorization_hash"],
        "execution_packet_reference": review["execution_packet_reference"],
        "execution_packet_hash": review["execution_packet_hash"],
        "worker_id": review["worker_id"],
        "worker_hash": review["worker_hash"],
        "chain_id": review["chain_id"],
        "future_improvement_intent_handoff_status": SEPARATE_GOVERNED_REQUEST_REQUIRED,
        "future_improvement_intent_source_reference": _require_string(termination_id, "governed_termination_id"),
        "improvement_intent_created": False,
        "improvement_intent_handoff_executed": False,
        "continuation_created": False,
        "retry_created": False,
        "terminated_by": _require_string(terminated_by, "terminated_by"),
        "terminated_at": _require_string(terminated_at, "terminated_at"),
        "replay_visible": True,
        **_post_termination_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_termination_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    termination_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    termination: dict[str, Any],
    terminated_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_TERMINATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION,
        "termination_result_id": f"{_require_string(termination_id, 'governed_termination_id')}:RESULT",
        "termination_status": status,
        "termination_evidence_reference": evidence["termination_evidence_id"],
        "termination_evidence_hash": evidence["artifact_hash"],
        "termination_classification_reference": classification["termination_classification_id"],
        "termination_classification_hash": classification["artifact_hash"],
        "governed_termination_reference": termination["governed_termination_id"],
        "governed_termination_hash": termination["artifact_hash"],
        "post_execution_replay_review_reference": termination["post_execution_replay_review_reference"],
        "post_execution_replay_review_hash": termination["post_execution_replay_review_hash"],
        "chain_id": termination["chain_id"],
        "completed_at": _require_string(terminated_at, "terminated_at"),
        "replay_visible": True,
        **_post_termination_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    termination_id: str,
    review_reference: str | None,
    review_replay_reference: str,
    terminated_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_TERMINATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_TERMINATION_RUNTIME_VERSION,
        "termination_result_id": f"{termination_id}:RESULT",
        "termination_status": FAILED_CLOSED,
        "termination_evidence_reference": None,
        "termination_evidence_hash": None,
        "termination_classification_reference": None,
        "termination_classification_hash": None,
        "governed_termination_reference": None,
        "governed_termination_hash": None,
        "post_execution_replay_review_reference": review_reference,
        "post_execution_replay_review_hash": None,
        "post_execution_replay_review_replay_reference": review_replay_reference,
        "chain_id": None,
        "completed_at": terminated_at,
        "replay_visible": True,
        **_pre_termination_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    termination: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "termination_evidence_artifact": deepcopy(evidence),
            "termination_classification_artifact": deepcopy(classification),
            "governed_termination_artifact": deepcopy(termination),
            "termination_result_artifact": deepcopy(result),
            "governed_termination_reference": termination.get("governed_termination_id") if termination else None,
            "post_execution_replay_review_reference": (
                termination.get("post_execution_replay_review_reference") if termination else None
            ),
            "worker_id": termination.get("worker_id") if termination else None,
            "terminal_operation_state": termination.get("terminal_operation_state") if termination else None,
            "future_improvement_intent_handoff_status": (
                termination.get("future_improvement_intent_handoff_status") if termination else None
            ),
            "governed_termination_replay_reference": str(replay_path),
            "fail_closed": result["termination_status"] == FAILED_CLOSED,
        }
    )
    capture["governed_termination_capture_hash"] = replay_hash(capture)
    return capture


def _validate_review_artifact(review: dict[str, Any]) -> None:
    if review.get("artifact_type") != POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed termination failed closed: invalid replay review artifact")
    if review.get("review_status") != REVIEW_COMPLETED:
        raise FailClosedRuntimeError("governed termination failed closed: replay review incomplete")
    for assessment in (
        "replay_integrity_assessment",
        "authority_integrity_assessment",
        "execution_integrity_assessment",
        "validation_integrity_assessment",
    ):
        if review.get(assessment) != INTEGRITY_VERIFIED:
            raise FailClosedRuntimeError("governed termination failed closed: replay review integrity invalid")
    for field, expected in _pre_termination_boundary_flags().items():
        if review.get(field) is not expected:
            raise FailClosedRuntimeError("governed termination failed closed: authority boundary invalid")


def _validate_termination_artifact(termination: dict[str, Any]) -> None:
    if termination.get("artifact_type") != GOVERNED_TERMINATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed termination failed closed: invalid termination artifact")
    if termination.get("termination_status") != TERMINATED:
        raise FailClosedRuntimeError("governed termination failed closed: invalid termination status")
    if termination.get("terminal_operation_state") != TERMINAL_OPERATION_STATE:
        raise FailClosedRuntimeError("governed termination failed closed: invalid terminal operation state")
    for field, expected in _post_termination_boundary_flags().items():
        if termination.get(field) is not expected:
            raise FailClosedRuntimeError("governed termination failed closed: authority boundary invalid")
    for field in (
        "governed_termination_id",
        "post_execution_replay_review_reference",
        "post_execution_replay_review_hash",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "chain_id",
        "terminated_by",
        "terminated_at",
    ):
        _require_string(termination.get(field), field)
    if termination.get("future_improvement_intent_handoff_status") != SEPARATE_GOVERNED_REQUEST_REQUIRED:
        raise FailClosedRuntimeError("governed termination failed closed: invalid future handoff boundary")
    for field in (
        "improvement_intent_created",
        "improvement_intent_handoff_executed",
        "continuation_created",
        "retry_created",
    ):
        if termination.get(field) is not False:
            raise FailClosedRuntimeError("governed termination failed closed: hidden continuation detected")


def _review_authority_continuity(review: dict[str, Any]) -> bool:
    return all(review.get(field) is expected for field, expected in _pre_termination_boundary_flags().items())


def _pre_termination_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": True,
        "worker_result_captured": True,
        "result_validated": True,
        "post_execution_replay_reviewed": True,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_termination_boundary_flags() -> dict[str, bool]:
    flags = _pre_termination_boundary_flags()
    flags["terminated"] = True
    return flags


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed termination replay ordering mismatch")
    _verify_artifact_hash(artifact, "governed termination artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("governed termination replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("governed termination replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed termination failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"governed termination failed closed: {exc}"
