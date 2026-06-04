"""Replay-visible post-execution review runtime for the current AiGOL chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    WORKER_RESULT_VALIDATION_ARTIFACT_V1,
    reconstruct_worker_result_validation_replay,
)


AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION = "AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_V1"
POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1"
REVIEW_COMPLETED = "REVIEW_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"

REPLAY_STEPS = (
    "review_evidence_recorded",
    "review_classification_recorded",
    "review_artifact_recorded",
    "review_result_recorded",
)


def review_validated_worker_result(
    *,
    post_execution_replay_review_id: str,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str,
    reviewed_by: str,
    reviewed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Review a validated execution chain without retry, mutation, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_validation_lineage(
            Path(worker_result_validation_replay_reference),
            worker_result_validation_artifact,
        )
        validation = lineage["validation"]
        evidence = _evidence_artifact(
            review_id=post_execution_replay_review_id,
            validation=validation,
            lineage=lineage,
            validation_replay_reference=worker_result_validation_replay_reference,
            reviewed_at=reviewed_at,
        )
        classification = _classification_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            reviewed_at=reviewed_at,
        )
        review = _review_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            classification=classification,
            validation=validation,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
        )
        result = _result_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            classification=classification,
            review=review,
            reviewed_at=reviewed_at,
            status=REVIEW_COMPLETED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], review)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, review, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            review_id=post_execution_replay_review_id,
            validation_reference=(
                worker_result_validation_artifact.get("worker_result_validation_id")
                if isinstance(worker_result_validation_artifact, dict)
                else None
            ),
            validation_replay_reference=worker_result_validation_replay_reference,
            reviewed_at=reviewed_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_post_execution_replay_review(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct post-execution replay review deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("post-execution replay review ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("post-execution replay review artifact must be a JSON object")
        _verify_artifact_hash(artifact, "post-execution replay review artifact")
        wrappers.append(wrapper)

    evidence, classification, review, result = (wrapper["artifact"] for wrapper in wrappers)
    if classification.get("review_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review evidence lineage mismatch")
    if review.get("review_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review classification lineage mismatch")
    if result.get("post_execution_replay_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], review["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("post-execution replay review chain mismatch")
    _validate_review_artifact(review)
    _load_validation_lineage(Path(evidence["worker_result_validation_replay_reference"]), None, review=review)
    return {
        "post_execution_replay_review_id": review["post_execution_replay_review_id"],
        "review_status": result["review_status"],
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_capture_reference": review["worker_result_capture_reference"],
        "worker_invocation_reference": review["worker_invocation_reference"],
        "worker_dispatch_reference": review["worker_dispatch_reference"],
        "authorization_reference": review["authorization_reference"],
        "execution_packet_reference": review["execution_packet_reference"],
        "worker_id": review["worker_id"],
        "chain_id": review["chain_id"],
        "replay_integrity_assessment": review["replay_integrity_assessment"],
        "authority_integrity_assessment": review["authority_integrity_assessment"],
        "execution_integrity_assessment": review["execution_integrity_assessment"],
        "validation_integrity_assessment": review["validation_integrity_assessment"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_review_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_post_execution_replay_review_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Post-Execution Replay Review",
        "",
        f"Replay Review Status: {capture.get('review_status')}",
        f"Post-Execution Replay Review Reference: {capture.get('post_execution_replay_review_reference')}",
        f"Worker Result Validation Reference: {capture.get('worker_result_validation_reference')}",
        f"Reviewed Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('post_execution_replay_review_replay_reference')}",
        "",
        "Termination is a separate downstream stage.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_validation_lineage(
    validation_replay_path: Path,
    provided_validation: dict[str, Any] | None,
    *,
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reconstructed = reconstruct_worker_result_validation_replay(validation_replay_path)
    if reconstructed.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: validation invalid")
    wrappers = _load_wrappers(
        validation_replay_path,
        (
            "validation_evidence_recorded",
            "validation_classification_recorded",
            "validation_artifact_recorded",
            "validation_result_recorded",
        ),
        "worker result validation lineage artifact",
    )
    validation_evidence, validation_classification, validation, validation_result = (
        wrapper["artifact"] for wrapper in wrappers
    )
    if validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: validation inconsistency")
    if provided_validation is not None:
        _verify_artifact_hash(provided_validation, "provided worker result validation artifact")
        if provided_validation.get("worker_result_validation_id") != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
        if provided_validation.get("artifact_hash") != validation["artifact_hash"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
    if review is not None:
        if review.get("worker_result_validation_reference") != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
        if review.get("worker_result_validation_hash") != validation["artifact_hash"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")

    chain = _load_chain_artifacts(validation_evidence)
    checks = {
        "review_continuity": review is None or review.get("worker_result_validation_hash") == validation["artifact_hash"],
        "validation_continuity": validation_result["worker_result_validation_hash"] == validation["artifact_hash"],
        "result_capture_lineage": validation["worker_result_capture_hash"] == chain["result_capture"]["artifact_hash"],
        "invocation_lineage": validation["worker_invocation_hash"] == chain["invocation"]["artifact_hash"],
        "dispatch_lineage": validation["worker_dispatch_hash"] == chain["dispatch"]["artifact_hash"],
        "assignment_lineage": validation["worker_assignment_hash"] == chain["assignment"]["artifact_hash"],
        "authorization_lineage": validation["authorization_hash"] == chain["authorization"]["artifact_hash"],
        "handoff_lineage": bool(chain["request_evidence"].get("handoff_reference"))
        and bool(chain["request_evidence"].get("handoff_hash")),
        "packet_continuity": validation["execution_packet_reference"] == chain["request"]["execution_packet_reference"]
        and validation["execution_packet_hash"] == chain["request"]["execution_packet_hash"],
        "worker_continuity": validation["worker_id"] == chain["invocation"]["worker_id"]
        == chain["dispatch"]["worker_id"],
        "chain_continuity": len(
            {
                validation["chain_id"],
                chain["result_capture"]["chain_id"],
                chain["invocation"]["chain_id"],
                chain["dispatch"]["chain_id"],
                chain["assignment"]["canonical_chain_id"],
                chain["request"]["chain_id"],
                chain["authorization"]["chain_id"],
            }
        )
        == 1,
        "replay_continuity": reconstructed["validation_status"] == RESULT_VALIDATED,
        "authority_continuity": _validation_authority_continuity(validation),
        "hash_continuity": all(bool(artifact.get("artifact_hash")) for artifact in chain.values())
        and validation_classification["validation_evidence_hash"] == validation_evidence["artifact_hash"],
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("post-execution replay review failed closed: lineage continuity invalid")
    return {
        "validation_evidence": validation_evidence,
        "validation_classification": validation_classification,
        "validation": validation,
        "validation_result": validation_result,
        "chain": chain,
        "lineage_checks": checks,
    }


def _load_chain_artifacts(validation_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result_capture_evidence = _load_artifact(
        Path(validation_evidence["worker_result_capture_replay_reference"]),
        0,
        "result_capture_evidence_recorded",
    )
    result_capture = _load_artifact(
        Path(validation_evidence["worker_result_capture_replay_reference"]),
        2,
        "result_capture_artifact_recorded",
    )
    invocation_evidence = _load_artifact(
        Path(result_capture_evidence["worker_invocation_replay_reference"]),
        0,
        "invocation_evidence_recorded",
    )
    invocation = _load_artifact(
        Path(result_capture_evidence["worker_invocation_replay_reference"]),
        2,
        "invocation_artifact_recorded",
    )
    dispatch_evidence = _load_artifact(
        Path(invocation_evidence["worker_dispatch_replay_reference"]),
        0,
        "dispatch_evidence_recorded",
    )
    dispatch = _load_artifact(
        Path(invocation_evidence["worker_dispatch_replay_reference"]),
        2,
        "dispatch_artifact_recorded",
    )
    assignment_evidence = _load_artifact(
        Path(dispatch_evidence["worker_assignment_replay_reference"]),
        0,
        "assignment_evidence_recorded",
    )
    assignment = _load_artifact(
        Path(dispatch_evidence["worker_assignment_replay_reference"]),
        2,
        "assignment_artifact_recorded",
    )
    request_evidence = _load_artifact(
        Path(assignment_evidence["worker_invocation_request_replay_reference"]),
        0,
        "invocation_request_evidence_recorded",
    )
    request = _load_artifact(
        Path(assignment_evidence["worker_invocation_request_replay_reference"]),
        2,
        "invocation_request_artifact_recorded",
    )
    authorization = _load_artifact(
        Path(request_evidence["execution_authorization_replay_reference"]),
        2,
        "authorization_artifact_recorded",
    )
    return {
        "result_capture": result_capture,
        "invocation": invocation,
        "dispatch": dispatch,
        "assignment": assignment,
        "request": request,
        "request_evidence": request_evidence,
        "authorization": authorization,
    }


def _evidence_artifact(
    *,
    review_id: str,
    validation: dict[str, Any],
    lineage: dict[str, Any],
    validation_replay_reference: str,
    reviewed_at: str,
) -> dict[str, Any]:
    chain = lineage["chain"]
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_evidence_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:EVIDENCE",
        "chain_id": validation["chain_id"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_validation_replay_reference": _require_string(
            validation_replay_reference, "worker_result_validation_replay_reference"
        ),
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "worker_invocation_reference": validation["worker_invocation_reference"],
        "worker_invocation_hash": validation["worker_invocation_hash"],
        "worker_dispatch_reference": validation["worker_dispatch_reference"],
        "worker_dispatch_hash": validation["worker_dispatch_hash"],
        "worker_assignment_reference": validation["worker_assignment_reference"],
        "worker_assignment_hash": validation["worker_assignment_hash"],
        "authorization_reference": validation["authorization_reference"],
        "authorization_hash": validation["authorization_hash"],
        "execution_packet_reference": validation["execution_packet_reference"],
        "execution_packet_hash": validation["execution_packet_hash"],
        "handoff_reference": chain["request_evidence"]["handoff_reference"],
        "handoff_hash": chain["request_evidence"]["handoff_hash"],
        "worker_id": validation["worker_id"],
        "worker_hash": validation["worker_hash"],
        "worker_family": validation["worker_family"],
        "worker_role": validation["worker_role"],
        "validation_requirements": deepcopy(validation["validation_requirements"]),
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(*, review_id: str, evidence: dict[str, Any], reviewed_at: str) -> dict[str, Any]:
    checks = evidence["lineage_checks"]
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_classification_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:CLASSIFICATION",
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "chain_id": evidence["chain_id"],
        "review_classification": "EXECUTION_CHAIN_INTEGRITY_VERIFIED",
        "replay_integrity_assessment": INTEGRITY_VERIFIED if checks["replay_continuity"] and checks["hash_continuity"] else FAILED_CLOSED,
        "authority_integrity_assessment": INTEGRITY_VERIFIED if checks["authority_continuity"] else FAILED_CLOSED,
        "execution_integrity_assessment": INTEGRITY_VERIFIED if all(
            checks[key]
            for key in (
                "handoff_lineage",
                "authorization_lineage",
                "invocation_lineage",
                "dispatch_lineage",
                "assignment_lineage",
                "result_capture_lineage",
                "packet_continuity",
                "worker_continuity",
                "chain_continuity",
            )
        )
        else FAILED_CLOSED,
        "validation_integrity_assessment": INTEGRITY_VERIFIED if checks["validation_continuity"] else FAILED_CLOSED,
        "classified_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(),
    }
    if FAILED_CLOSED in (
        artifact["replay_integrity_assessment"],
        artifact["authority_integrity_assessment"],
        artifact["execution_integrity_assessment"],
        artifact["validation_integrity_assessment"],
    ):
        raise FailClosedRuntimeError("post-execution replay review failed closed: integrity assessment failed")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _review_artifact(
    *,
    review_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    validation: dict[str, Any],
    reviewed_by: str,
    reviewed_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "post_execution_replay_review_id": _require_string(review_id, "post_execution_replay_review_id"),
        "review_status": REVIEW_COMPLETED,
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "review_classification_reference": classification["review_classification_id"],
        "review_classification_hash": classification["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "worker_invocation_reference": validation["worker_invocation_reference"],
        "worker_invocation_hash": validation["worker_invocation_hash"],
        "worker_dispatch_reference": validation["worker_dispatch_reference"],
        "worker_dispatch_hash": validation["worker_dispatch_hash"],
        "authorization_reference": validation["authorization_reference"],
        "authorization_hash": validation["authorization_hash"],
        "execution_packet_reference": validation["execution_packet_reference"],
        "execution_packet_hash": validation["execution_packet_hash"],
        "handoff_reference": evidence["handoff_reference"],
        "handoff_hash": evidence["handoff_hash"],
        "worker_id": validation["worker_id"],
        "worker_hash": validation["worker_hash"],
        "worker_family": validation["worker_family"],
        "worker_role": validation["worker_role"],
        "chain_id": validation["chain_id"],
        "replay_integrity_assessment": classification["replay_integrity_assessment"],
        "authority_integrity_assessment": classification["authority_integrity_assessment"],
        "execution_integrity_assessment": classification["execution_integrity_assessment"],
        "validation_integrity_assessment": classification["validation_integrity_assessment"],
        "reviewed_by": _require_string(reviewed_by, "reviewed_by"),
        "reviewed_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_review_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    review_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    review: dict[str, Any],
    reviewed_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_result_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:RESULT",
        "review_status": status,
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "review_classification_reference": classification["review_classification_id"],
        "review_classification_hash": classification["artifact_hash"],
        "post_execution_replay_review_reference": review["post_execution_replay_review_id"],
        "post_execution_replay_review_hash": review["artifact_hash"],
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_validation_hash": review["worker_result_validation_hash"],
        "chain_id": review["chain_id"],
        "completed_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    review_id: str,
    validation_reference: str | None,
    validation_replay_reference: str,
    reviewed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_result_id": f"{review_id}:RESULT",
        "review_status": FAILED_CLOSED,
        "review_evidence_reference": None,
        "review_evidence_hash": None,
        "review_classification_reference": None,
        "review_classification_hash": None,
        "post_execution_replay_review_reference": None,
        "post_execution_replay_review_hash": None,
        "worker_result_validation_reference": validation_reference,
        "worker_result_validation_hash": None,
        "worker_result_validation_replay_reference": validation_replay_reference,
        "chain_id": None,
        "completed_at": reviewed_at,
        "replay_visible": True,
        **_pre_review_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    review: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "review_evidence_artifact": deepcopy(evidence),
            "review_classification_artifact": deepcopy(classification),
            "post_execution_replay_review_artifact": deepcopy(review),
            "review_result_artifact": deepcopy(result),
            "post_execution_replay_review_reference": review.get("post_execution_replay_review_id") if review else None,
            "worker_result_validation_reference": review.get("worker_result_validation_reference") if review else None,
            "worker_id": review.get("worker_id") if review else None,
            "post_execution_replay_review_replay_reference": str(replay_path),
            "fail_closed": result["review_status"] == FAILED_CLOSED,
        }
    )
    capture["post_execution_replay_review_capture_hash"] = replay_hash(capture)
    return capture


def _validate_review_artifact(review: dict[str, Any]) -> None:
    if review.get("artifact_type") != POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid review artifact")
    if review.get("review_status") != REVIEW_COMPLETED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid review status")
    for field, expected in _post_review_boundary_flags().items():
        if review.get(field) is not expected:
            raise FailClosedRuntimeError("post-execution replay review failed closed: authority drift")
    for field in (
        "post_execution_replay_review_id",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
        "worker_result_capture_reference",
        "worker_result_capture_hash",
        "worker_invocation_reference",
        "worker_invocation_hash",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "handoff_reference",
        "handoff_hash",
        "worker_id",
        "worker_hash",
        "chain_id",
        "reviewed_by",
        "reviewed_at",
    ):
        _require_string(review.get(field), field)
    for assessment in (
        "replay_integrity_assessment",
        "authority_integrity_assessment",
        "execution_integrity_assessment",
        "validation_integrity_assessment",
    ):
        if review.get(assessment) != INTEGRITY_VERIFIED:
            raise FailClosedRuntimeError("post-execution replay review failed closed: integrity assessment failed")


def _validation_authority_continuity(validation: dict[str, Any]) -> bool:
    return all(validation.get(field) is expected for field, expected in _pre_review_boundary_flags().items())


def _pre_review_boundary_flags() -> dict[str, bool]:
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
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_review_boundary_flags() -> dict[str, bool]:
    flags = _pre_review_boundary_flags()
    flags["post_execution_replay_reviewed"] = True
    return flags


def _load_wrappers(path: Path, steps: tuple[str, ...], label: str) -> list[dict[str, Any]]:
    wrappers = []
    for index, step in enumerate(steps):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(f"{label} must be a JSON object")
        _verify_artifact_hash(artifact, label)
        wrappers.append(wrapper)
    return wrappers


def _load_artifact(path: Path, index: int, step: str) -> dict[str, Any]:
    wrapper = load_json(path / f"{index:03d}_{step}.json")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("post-execution replay review failed closed: replay continuity mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("post-execution replay review failed closed: replay corruption")
    _verify_artifact_hash(artifact, "post-execution chain artifact")
    return artifact


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("post-execution replay review ordering mismatch")
    _verify_artifact_hash(artifact, "post-execution replay review artifact")
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
        raise FailClosedRuntimeError("post-execution replay review replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("post-execution replay review replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"post-execution replay review failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"post-execution replay review failed closed: {exc}"
