"""Non-authoritative Governed Termination to Replay Certification binding."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime import replay_certification_runtime as replay_certification
from aigol.runtime.governed_termination_runtime import (
    GOVERNED_TERMINATION_ARTIFACT_V1,
    GOVERNED_TERMINATION_CLASSIFICATION_ARTIFACT_V1,
    GOVERNED_TERMINATION_EVIDENCE_ARTIFACT_V1,
    GOVERNED_TERMINATION_RESULT_ARTIFACT_V1,
    REPLAY_STEPS as TERMINATION_REPLAY_STEPS,
    TERMINAL_OPERATION_STATE,
    TERMINATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import (
    REPLAY_STEPS as REVIEW_REPLAY_STEPS,
)
from aigol.runtime.result_validation_runtime import (
    AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
    RESULT_VALIDATION_ARTIFACT_V1,
    RESULT_VALIDATION_COMPLETED,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
)
from aigol.runtime.worker_result_capture_runtime import (
    REPLAY_STEPS as RESULT_CAPTURE_REPLAY_STEPS,
)
from aigol.runtime.worker_result_validation_runtime import (
    REPLAY_STEPS as WORKER_RESULT_VALIDATION_REPLAY_STEPS,
)


RUNTIME_VERSION = (
    "G31_GOVERNED_TERMINATION_TO_FINAL_EXECUTION_CERTIFICATION_BINDING_V1"
)
RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1 = (
    "RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1"
)
SUCCESS = "G31_FINAL_EXECUTION_CERTIFICATION_COMPLETED"
FAILED_CLOSED = "G31_FINAL_EXECUTION_CERTIFICATION_FAILED_CLOSED"

TerminationReconstructor = Callable[[str | Path], dict[str, Any]]

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "executes_workers": False,
    "invokes_providers": False,
    "validates_results": False,
    "reviews_replay": False,
    "terminates_operations": False,
    "certifies_execution": False,
    "mutates_repository": False,
    "mutates_governance": False,
    "mutates_replay": False,
}


def certify_governed_termination(
    *,
    binding_id: str,
    terminal_capture: dict[str, Any],
    termination_replay_reference: str | Path,
    termination_reconstructor: TerminationReconstructor,
    certified_by: str,
    certified_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Authenticate terminal evidence and invoke the unchanged owner once."""

    certification_called = False
    projection: dict[str, Any] | None = None
    try:
        identifier = _require_string(binding_id, "binding_id")
        actor = _require_string(certified_by, "certified_by")
        timestamp = _require_string(certified_at, "certified_at")
        lineage = _authenticate_terminal_lifecycle(
            terminal_capture=terminal_capture,
            termination_replay_reference=termination_replay_reference,
            termination_reconstructor=termination_reconstructor,
        )
        destination = _inside_session(
            replay_dir,
            lineage["session_root"],
            "Certification Replay destination",
        )
        projection = _compatibility_projection(
            binding_id=identifier,
            lineage=lineage,
            composed_by=actor,
            composed_at=timestamp,
        )
        _reject_duplicate_certification(
            session_root=lineage["session_root"],
            destination=destination,
            termination_replay_reference=lineage[
                "termination_replay_reference"
            ],
            termination_replay_hash=lineage["termination_replay_hash"],
        )
        certification_called = True
        certification = replay_certification.certify_validated_replay(
            certification_id=f"{identifier}:REPLAY-CERTIFICATION",
            result_validation_artifact=projection,
            certified_by=actor,
            certified_at=timestamp,
            replay_dir=destination,
        )
        if (
            certification.get("certification_status")
            != replay_certification.REPLAY_CERTIFICATION_COMPLETED
            or certification.get("replay_certification_completed") is not True
        ):
            raise FailClosedRuntimeError(
                certification.get("failure_reason")
                or "Certification owner failed closed"
            )
        reconstructed = (
            replay_certification.reconstruct_replay_certification_replay(
                destination
            )
        )
        _validate_certification(
            certification=certification,
            reconstructed=reconstructed,
            projection=projection,
            lineage=lineage,
            destination=destination,
        )
        return {
            "runtime_version": RUNTIME_VERSION,
            "binding_id": identifier,
            "binding_status": SUCCESS,
            "result_validation_compatibility_projection": deepcopy(
                projection
            ),
            "result_validation_compatibility_projection_hash": projection[
                "artifact_hash"
            ],
            "final_execution_certification": deepcopy(certification),
            "final_execution_certification_reconstruction": deepcopy(
                reconstructed
            ),
            "final_execution_certification_reference": certification[
                "replay_certification_artifact"
            ]["replay_certification_id"],
            "final_execution_certification_hash": certification[
                "replay_certification_artifact"
            ]["artifact_hash"],
            "final_execution_certification_replay_reference": str(
                destination
            ),
            "final_execution_certification_replay_hash": reconstructed[
                "replay_hash"
            ],
            "governed_termination_reference": lineage[
                "termination"
            ]["governed_termination_id"],
            "governed_termination_hash": lineage["termination"][
                "artifact_hash"
            ],
            "governed_termination_replay_reference": lineage[
                "termination_replay_reference"
            ],
            "governed_termination_replay_hash": lineage[
                "termination_replay_hash"
            ],
            "ordered_replay_references": deepcopy(
                lineage["ordered_replay_references"]
            ),
            "ordered_replay_hashes": deepcopy(
                lineage["ordered_replay_hashes"]
            ),
            "certification_called": True,
            "execution_certified": True,
            "replay_lineage_preserved": True,
            "authorization_ownership_preserved": True,
            "replay_ownership_preserved": True,
            "termination_ownership_preserved": True,
            "result_validation_ownership_preserved": True,
            "certification_ownership_preserved": True,
            "repository_mutated": False,
            "historical_repository_mutation_preserved": True,
            "governance_mutated": False,
            "replay_mutated": False,
            "authority_flags": deepcopy(AUTHORITY_FLAGS),
            "fail_closed": False,
            "failure_reason": None,
        }
    except Exception as exc:
        return {
            "runtime_version": RUNTIME_VERSION,
            "binding_id": (
                binding_id
                if isinstance(binding_id, str) and binding_id.strip()
                else "INVALID"
            ),
            "binding_status": FAILED_CLOSED,
            "result_validation_compatibility_projection": deepcopy(
                projection
            ),
            "result_validation_compatibility_projection_hash": (
                projection.get("artifact_hash")
                if isinstance(projection, dict)
                else None
            ),
            "final_execution_certification": None,
            "final_execution_certification_reconstruction": None,
            "final_execution_certification_reference": None,
            "final_execution_certification_hash": None,
            "final_execution_certification_replay_reference": None,
            "final_execution_certification_replay_hash": None,
            "certification_called": certification_called,
            "execution_certified": False,
            "replay_lineage_preserved": False,
            "authorization_ownership_preserved": True,
            "replay_ownership_preserved": True,
            "termination_ownership_preserved": True,
            "result_validation_ownership_preserved": True,
            "certification_ownership_preserved": True,
            "repository_mutated": (
                terminal_capture.get("repository_mutated") is True
                if isinstance(terminal_capture, dict)
                else False
            ),
            "governance_mutated": False,
            "replay_mutated": False,
            "authority_flags": deepcopy(AUTHORITY_FLAGS),
            "fail_closed": True,
            "failure_reason": _failure_reason(exc),
        }


def _authenticate_terminal_lifecycle(
    *,
    terminal_capture: dict[str, Any],
    termination_replay_reference: str | Path,
    termination_reconstructor: TerminationReconstructor,
) -> dict[str, Any]:
    if not isinstance(terminal_capture, dict):
        raise FailClosedRuntimeError(
            "final execution certification binding requires terminal capture"
        )
    if not callable(termination_reconstructor):
        raise FailClosedRuntimeError(
            "final execution certification binding requires certified reconstruction"
        )
    termination_path = Path(
        _require_string(
            str(termination_replay_reference),
            "termination_replay_reference",
        )
    ).resolve()
    if not termination_path.is_dir():
        raise FailClosedRuntimeError(
            "final execution certification binding termination Replay missing"
        )
    session_root = termination_path.parent.resolve()
    reconstructed = termination_reconstructor(termination_path)
    if not isinstance(reconstructed, dict):
        raise FailClosedRuntimeError(
            "final execution certification binding reconstruction invalid"
        )
    wrappers = _load_replay(
        termination_path,
        TERMINATION_REPLAY_STEPS,
        "Governed Termination",
    )
    evidence, classification, termination, result = (
        wrapper["artifact"] for wrapper in wrappers
    )
    provided = (
        terminal_capture.get("termination_evidence_artifact"),
        terminal_capture.get("termination_classification_artifact"),
        terminal_capture.get("governed_termination_artifact"),
        terminal_capture.get("termination_result_artifact"),
    )
    if tuple(deepcopy(item) for item in provided) != (
        evidence,
        classification,
        termination,
        result,
    ):
        raise FailClosedRuntimeError(
            "final execution certification binding terminal evidence substituted"
        )
    _verify_capture_hash(terminal_capture)
    if (
        evidence.get("artifact_type")
        != GOVERNED_TERMINATION_EVIDENCE_ARTIFACT_V1
        or classification.get("artifact_type")
        != GOVERNED_TERMINATION_CLASSIFICATION_ARTIFACT_V1
        or termination.get("artifact_type")
        != GOVERNED_TERMINATION_ARTIFACT_V1
        or result.get("artifact_type")
        != GOVERNED_TERMINATION_RESULT_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError(
            "final execution certification binding terminal schema unsupported"
        )
    checks = (
        terminal_capture.get("termination_status") == TERMINATED,
        result.get("termination_status") == TERMINATED,
        termination.get("termination_status") == TERMINATED,
        termination.get("terminal_operation_state")
        == TERMINAL_OPERATION_STATE,
        reconstructed.get("termination_status") == TERMINATED,
        reconstructed.get("terminal_operation_state")
        == TERMINAL_OPERATION_STATE,
        reconstructed.get("replay_artifact_count") == 4,
        terminal_capture.get("governed_termination_reference")
        == termination.get("governed_termination_id"),
        _same_path(
            terminal_capture.get("governed_termination_replay_reference"),
            termination_path,
        ),
        classification.get("termination_evidence_hash")
        == evidence.get("artifact_hash"),
        termination.get("termination_evidence_hash")
        == evidence.get("artifact_hash"),
        termination.get("termination_classification_hash")
        == classification.get("artifact_hash"),
        result.get("governed_termination_hash")
        == termination.get("artifact_hash"),
        result.get("post_execution_replay_review_hash")
        == termination.get("post_execution_replay_review_hash"),
        len(
            {
                evidence.get("chain_id"),
                classification.get("chain_id"),
                termination.get("chain_id"),
                result.get("chain_id"),
                reconstructed.get("chain_id"),
            }
        )
        == 1,
        termination.get("terminated") is True,
        termination.get("post_execution_replay_reviewed") is True,
        termination.get("governance_mutated") is False,
        termination.get("replay_mutated") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "final execution certification binding terminal continuity invalid"
        )

    review_path = _inside_session(
        evidence.get("post_execution_replay_review_replay_reference"),
        session_root,
        "Replay Review reference",
    )
    review_wrappers = _load_replay(
        review_path,
        REVIEW_REPLAY_STEPS,
        "Post-Execution Replay Review",
    )
    review_evidence = review_wrappers[0]["artifact"]
    review = review_wrappers[2]["artifact"]
    validation_path = _inside_session(
        review_evidence.get("worker_result_validation_replay_reference"),
        session_root,
        "Result Validation reference",
    )
    validation_wrappers = _load_replay(
        validation_path,
        WORKER_RESULT_VALIDATION_REPLAY_STEPS,
        "Worker Result Validation",
    )
    validation_evidence = validation_wrappers[0]["artifact"]
    validation = validation_wrappers[2]["artifact"]
    result_capture_path = _inside_session(
        validation_evidence.get("worker_result_capture_replay_reference"),
        session_root,
        "Result Capture reference",
    )
    result_capture_wrappers = _load_replay(
        result_capture_path,
        RESULT_CAPTURE_REPLAY_STEPS,
        "Worker Result Capture",
    )
    result_capture = result_capture_wrappers[2]["artifact"]
    termination_replay_hash = replay_hash(wrappers)
    review_replay_hash = replay_hash(review_wrappers)
    validation_replay_hash = replay_hash(validation_wrappers)
    result_capture_replay_hash = replay_hash(result_capture_wrappers)
    execution_reference = _require_string(
        termination.get("execution_reference"),
        "execution_reference",
    )
    execution_hash = _require_hash(
        termination.get("execution_hash"),
        "execution_hash",
    )
    execution_replay_reference = _inside_session(
        termination.get("execution_replay_reference"),
        session_root,
        "Execution Replay reference",
    )
    execution_replay_hash = _require_hash(
        termination.get("execution_replay_hash"),
        "execution_replay_hash",
    )
    continuity = (
        review.get("artifact_hash")
        == termination.get("post_execution_replay_review_hash"),
        review.get("post_execution_replay_review_id")
        == termination.get("post_execution_replay_review_reference"),
        validation.get("artifact_hash")
        == termination.get("worker_result_validation_hash"),
        validation.get("worker_result_validation_id")
        == termination.get("worker_result_validation_reference"),
        result_capture.get("artifact_hash")
        == validation.get("worker_result_capture_hash"),
        result_capture.get("worker_result_capture_id")
        == validation.get("worker_result_capture_reference"),
        validation.get("authorization_reference")
        == termination.get("authorization_reference"),
        validation.get("authorization_hash")
        == termination.get("authorization_hash"),
        validation.get("execution_packet_reference")
        == termination.get("execution_packet_reference"),
        validation.get("execution_packet_hash")
        == termination.get("execution_packet_hash"),
        validation.get("execution_reference") == execution_reference,
        validation.get("execution_hash") == execution_hash,
        _same_path(
            validation.get("execution_replay_reference"),
            execution_replay_reference,
        ),
        validation.get("execution_replay_hash") == execution_replay_hash,
        validation.get("worker_id") == termination.get("worker_id"),
        validation.get("worker_hash") == termination.get("worker_hash"),
        validation.get("chain_id") == termination.get("chain_id"),
    )
    if not all(continuity):
        raise FailClosedRuntimeError(
            "final execution certification binding upstream continuity invalid"
        )
    ordered_replay_references = [
        str(execution_replay_reference),
        str(result_capture_path),
        str(validation_path),
        str(review_path),
        str(termination_path),
    ]
    ordered_replay_hashes = [
        execution_replay_hash,
        result_capture_replay_hash,
        validation_replay_hash,
        review_replay_hash,
        termination_replay_hash,
    ]
    return {
        "session_root": session_root,
        "evidence": evidence,
        "classification": classification,
        "termination": termination,
        "result": result,
        "terminal_capture_hash": terminal_capture[
            "governed_termination_capture_hash"
        ],
        "termination_replay_reference": str(termination_path),
        "termination_replay_hash": termination_replay_hash,
        "review": review,
        "review_replay_reference": str(review_path),
        "review_replay_hash": review_replay_hash,
        "validation": validation,
        "validation_replay_reference": str(validation_path),
        "validation_replay_hash": validation_replay_hash,
        "result_capture": result_capture,
        "result_capture_replay_reference": str(result_capture_path),
        "result_capture_replay_hash": result_capture_replay_hash,
        "execution_reference": execution_reference,
        "execution_hash": execution_hash,
        "execution_replay_reference": str(execution_replay_reference),
        "execution_replay_hash": execution_replay_hash,
        "ordered_replay_references": ordered_replay_references,
        "ordered_replay_hashes": ordered_replay_hashes,
    }


def _compatibility_projection(
    *,
    binding_id: str,
    lineage: dict[str, Any],
    composed_by: str,
    composed_at: str,
) -> dict[str, Any]:
    termination = lineage["termination"]
    evidence = {
        "artifact_type": RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "result_validation_id": f"{binding_id}:RESULT-VALIDATION",
        "source_worker_execution": lineage["execution_reference"],
        "source_worker_execution_hash": lineage["execution_hash"],
        "source_result_capture_reference": lineage["result_capture"][
            "worker_result_capture_id"
        ],
        "source_result_capture_hash": lineage["result_capture"][
            "artifact_hash"
        ],
        "source_worker_result_validation_reference": lineage["validation"][
            "worker_result_validation_id"
        ],
        "source_worker_result_validation_hash": lineage["validation"][
            "artifact_hash"
        ],
        "source_post_execution_replay_review_reference": lineage["review"][
            "post_execution_replay_review_id"
        ],
        "source_post_execution_replay_review_hash": lineage["review"][
            "artifact_hash"
        ],
        "source_termination_evidence_reference": lineage["evidence"][
            "termination_evidence_id"
        ],
        "source_termination_evidence_hash": lineage["evidence"][
            "artifact_hash"
        ],
        "source_termination_classification_reference": lineage[
            "classification"
        ]["termination_classification_id"],
        "source_termination_classification_hash": lineage[
            "classification"
        ]["artifact_hash"],
        "source_governed_termination_reference": termination[
            "governed_termination_id"
        ],
        "source_governed_termination_hash": termination["artifact_hash"],
        "source_termination_result_reference": lineage["result"][
            "termination_result_id"
        ],
        "source_termination_result_hash": lineage["result"]["artifact_hash"],
        "source_terminal_capture_hash": lineage["terminal_capture_hash"],
        "authorization_reference": termination["authorization_reference"],
        "authorization_hash": termination["authorization_hash"],
        "execution_packet_reference": termination[
            "execution_packet_reference"
        ],
        "execution_packet_hash": termination["execution_packet_hash"],
        "worker_id": termination["worker_id"],
        "worker_hash": termination["worker_hash"],
        "chain_id": termination["chain_id"],
        "terminal_operation_state": termination["terminal_operation_state"],
        "replay_references": deepcopy(
            lineage["ordered_replay_references"]
        ),
        "replay_hashes": deepcopy(lineage["ordered_replay_hashes"]),
        "terminal_lifecycle_authenticated": True,
        "governance_constraints_validated": True,
        "lineage_integrity_validated": True,
        "non_authoritative": True,
        "validated_at": composed_at,
        "replay_visible": True,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    projection = {
        "artifact_type": RESULT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_RESULT_VALIDATION_RUNTIME_VERSION,
        "result_validation_id": evidence["result_validation_id"],
        "validation_status": RESULT_VALIDATION_COMPLETED,
        "source_worker_execution": lineage["execution_reference"],
        "source_worker_execution_hash": lineage["execution_hash"],
        "source_worker_result_validation_reference": lineage["validation"][
            "worker_result_validation_id"
        ],
        "source_worker_result_validation_hash": lineage["validation"][
            "artifact_hash"
        ],
        "source_governed_termination_reference": termination[
            "governed_termination_id"
        ],
        "source_governed_termination_hash": termination["artifact_hash"],
        "source_termination_result_hash": lineage["result"]["artifact_hash"],
        "source_terminal_capture_hash": lineage["terminal_capture_hash"],
        "validation_evidence": evidence,
        "validation_evidence_hash": evidence["artifact_hash"],
        "validation_rationale": (
            "Authenticated Governed Termination and its complete immutable "
            "execution lineage were projected into the unchanged Replay "
            "Certification input contract without creating authority."
        ),
        "replay_references": deepcopy(
            lineage["ordered_replay_references"]
        ),
        "replay_hashes": deepcopy(lineage["ordered_replay_hashes"]),
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
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    projection["artifact_hash"] = replay_hash(projection)
    return projection


def _validate_certification(
    *,
    certification: dict[str, Any],
    reconstructed: dict[str, Any],
    projection: dict[str, Any],
    lineage: dict[str, Any],
    destination: Path,
) -> None:
    artifact = certification.get("replay_certification_artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "final execution certification binding artifact missing"
        )
    checks = (
        artifact.get("source_result_validation")
        == projection.get("result_validation_id"),
        artifact.get("source_result_validation_hash")
        == projection.get("artifact_hash"),
        artifact.get("source_worker_execution")
        == lineage.get("execution_reference"),
        artifact.get("source_worker_execution_hash")
        == lineage.get("execution_hash"),
        artifact.get("replay_references")
        == lineage.get("ordered_replay_references"),
        artifact.get("replay_hashes")
        == lineage.get("ordered_replay_hashes"),
        reconstructed.get("source_result_validation")
        == projection.get("result_validation_id"),
        reconstructed.get("source_worker_execution")
        == lineage.get("execution_reference"),
        reconstructed.get("replay_lineage_preserved") is True,
        reconstructed.get("deterministic_certification_preserved") is True,
        reconstructed.get("replay_artifact_count") == 2,
        certification.get("replay_certification_replay_reference")
        == str(destination),
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "final execution certification binding owner continuity invalid"
        )


def _reject_duplicate_certification(
    *,
    session_root: Path,
    destination: Path,
    termination_replay_reference: str,
    termination_replay_hash: str,
) -> None:
    for index, step in enumerate(replay_certification.REPLAY_STEPS):
        if (destination / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(
                "final execution certification binding duplicate certification"
            )
    for path in sorted(
        session_root.rglob("000_replay_certification_artifact_recorded.json")
    ):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(
                "final execution certification binding existing evidence invalid"
            )
        _verify_artifact_hash(artifact, "existing Certification artifact")
        references = artifact.get("replay_references")
        hashes = artifact.get("replay_hashes")
        if (
            not isinstance(references, list)
            or not isinstance(hashes, list)
            or len(references) != len(hashes)
        ):
            raise FailClosedRuntimeError(
                "final execution certification binding existing lineage invalid"
            )
        if any(
            reference == termination_replay_reference
            and replay_value == termination_replay_hash
            for reference, replay_value in zip(references, hashes)
        ):
            raise FailClosedRuntimeError(
                "final execution certification binding duplicate certification"
            )


def _load_replay(
    replay_path: Path,
    steps: tuple[str, ...],
    label: str,
) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(
            replay_path / f"{index:03d}_{step}.json"
        )
        if (
            wrapper.get("replay_index") != index
            or wrapper.get("replay_step") != step
        ):
            raise FailClosedRuntimeError(
                f"final execution certification binding {label} ordering invalid"
            )
        verify_replay_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(
                f"final execution certification binding {label} artifact invalid"
            )
        _verify_artifact_hash(artifact, f"{label} artifact")
        wrappers.append(wrapper)
    return wrappers


def _verify_capture_hash(capture: dict[str, Any]) -> None:
    actual = _require_hash(
        capture.get("governed_termination_capture_hash"),
        "governed_termination_capture_hash",
    )
    candidate = deepcopy(capture)
    candidate.pop("governed_termination_capture_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(
            "final execution certification binding terminal capture hash mismatch"
        )


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = _require_hash(artifact.get("artifact_hash"), f"{label} hash")
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(
            f"final execution certification binding {label} hash mismatch"
        )


def _inside_session(
    value: Any,
    session_root: Path,
    field_name: str,
) -> Path:
    path = Path(_require_string(str(value), field_name)).resolve()
    try:
        path.relative_to(session_root)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"final execution certification binding {field_name} crosses session"
        ) from exc
    return path


def _same_path(value: Any, expected: Path) -> bool:
    if not isinstance(value, (str, Path)):
        return False
    return Path(value).resolve() == expected.resolve()


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(
            f"final execution certification binding {field_name} is required"
        )
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"final execution certification binding {field_name} must be a hash"
        )
    return text


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "final execution certification binding failed closed"
