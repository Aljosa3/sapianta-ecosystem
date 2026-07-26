"""Schema-aware Authorization lineage presentation for G31 Replay Review."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_runtime import (
    CANONICAL_AUTHORIZATION_ACTOR,
    reconstruct_existing_authorization_binding_replay,
)
from aigol.runtime import (
    filesystem_replace_worker_result_capture_to_result_validation_binding_runtime
    as validation_binding,
)
from aigol.runtime import post_execution_replay_review_runtime as replay_review
from aigol.runtime import worker_result_validation_runtime as result_validation
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
)
from aigol.runtime.worker_invocation_request_runtime import (
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_invocation_runtime import _resolve_replay_reference
from aigol.workers import filesystem_replace_worker


RUNTIME_VERSION = (
    "G31_FILESYSTEM_REPLACE_SCHEMA_AWARE_AUTHORIZATION_LINEAGE_RESOLVER_V1"
)
REVIEWED_BY = "PLATFORM_CORE_G31_FILESYSTEM_REPLACE_REPLAY_REVIEW_BINDING"
SUCCESS = "G31_FILESYSTEM_REPLACE_WORKER_POST_EXECUTION_REPLAY_REVIEW_COMPLETED"
INVALID = "G31_FILESYSTEM_REPLACE_WORKER_POST_EXECUTION_REPLAY_REVIEW_INVALID"
FAILED_CLOSED = (
    "G31_FILESYSTEM_REPLACE_WORKER_POST_EXECUTION_REPLAY_REVIEW_FAILED_CLOSED"
)
HISTORICAL_SCHEMA = "AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1"
AUTHENTICATED_REPLACEMENT_SCHEMA = (
    "G31_EXISTING_MUTATION_AUTHORIZATION_BINDING_REPLAY_V1"
)
ARTIFACT_HASH_COMMITMENT = "AUTHORIZATION_ARTIFACT_HASH"
RECORD_HASH_COMMITMENT = "AUTHORIZATION_RECORD_HASH"
COMPATIBILITY_LINEAGE_TYPE = "AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1"

_ORIGINAL_CHAIN_LOADER = replay_review._load_chain_artifacts


def review_validated_filesystem_replace_worker_result(
    *,
    validation_binding_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    authenticated_request: dict[str, Any],
    filesystem_worker_capture: dict[str, Any],
    filesystem_worker_reconstruction: dict[str, Any],
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    worker_assignment_artifact: dict[str, Any],
    execution_artifact: dict[str, Any],
    execution_replay: dict[str, Any],
    execution_reconstruction: dict[str, Any],
    execution_replay_reference: str,
    reviewed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Authenticate R18C and invoke the unchanged generic review exactly once."""

    canonical_called = False
    validated = (
        validation_binding_capture.get(
            "g31_filesystem_result_validation_status"
        )
        == validation_binding.SUCCESS
    )
    repository_mutated = (
        filesystem_worker_capture.get("repository_mutated") is True
    )
    try:
        binding = _authenticate_validation(
            validation_binding_capture=validation_binding_capture,
            result_capture_binding_capture=result_capture_binding_capture,
            authenticated_request=authenticated_request,
            filesystem_worker_capture=filesystem_worker_capture,
            filesystem_worker_reconstruction=filesystem_worker_reconstruction,
            worker_invocation_artifact=worker_invocation_artifact,
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            worker_assignment_artifact=worker_assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution_replay,
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=execution_replay_reference,
        )
        destination = _inside_session(
            replay_dir,
            binding["session_root"],
            "Post-Execution Replay Review destination",
        )
        _ensure_destination_available(destination)
        _reject_repeated_review(
            binding["session_root"],
            validation=binding["validation"],
        )
        review_id = (
            f"{binding['validation']['worker_result_validation_id']}:"
            f"{binding['validation']['artifact_hash']}:"
            "POST-EXECUTION-REPLAY-REVIEW"
        )
        request_binding = _review_request_binding(
            review_id=review_id,
            binding=binding,
            destination=destination,
        )
        canonical_called = True
        canonical = replay_review.review_validated_worker_result(
            post_execution_replay_review_id=review_id,
            worker_result_validation_artifact=binding["validation"],
            worker_result_validation_replay_reference=str(
                binding["validation_replay_path"]
            ),
            reviewed_by=REVIEWED_BY,
            reviewed_at=_required(reviewed_at, "reviewed_at"),
            replay_dir=destination,
            chain_artifact_loader=_load_schema_aware_chain_artifacts,
        )
        if canonical.get("review_status") == replay_review.REVIEW_COMPLETED:
            reconstructed = (
                reconstruct_schema_aware_post_execution_replay_review(
                    destination
                )
            )
        else:
            reconstructed = None
        if canonical.get("review_status") == replay_review.FAILED_CLOSED:
            return {
                **deepcopy(canonical),
                "runtime_version": RUNTIME_VERSION,
                "g31_filesystem_post_execution_replay_review_status": INVALID,
                "review_request_binding": request_binding,
                **_terminal_truth(
                    review_completed=False,
                    repository_mutated=True,
                    canonical_called=True,
                ),
            }
        if canonical.get("review_status") != replay_review.REVIEW_COMPLETED:
            raise FailClosedRuntimeError(
                "canonical Post-Execution Replay Review returned unknown status"
            )
        if not isinstance(reconstructed, dict):
            raise FailClosedRuntimeError(
                "canonical Post-Execution Replay Review reconstruction missing"
            )
        _validate_canonical_reconstruction(
            canonical=canonical,
            reconstruction=reconstructed,
            binding=binding,
            review_id=review_id,
            replay_path=destination,
        )
        return {
            **deepcopy(canonical),
            "runtime_version": RUNTIME_VERSION,
            "g31_filesystem_post_execution_replay_review_status": SUCCESS,
            "review_request_binding": request_binding,
            "authorization_lineage_schema": AUTHENTICATED_REPLACEMENT_SCHEMA,
            "authorization_commitment_kind": RECORD_HASH_COMMITMENT,
            "authorization_commitment": binding["authorization_hash"],
            "authorization_source_replay_hash": binding[
                "authorization_replay_hash"
            ],
            "filesystem_replace_worker_output_hash": binding[
                "worker_output_hash"
            ],
            "filesystem_replace_worker_output_payload_hash": binding[
                "worker_output_payload_hash"
            ],
            "filesystem_replace_worker_capture_hash": binding[
                "filesystem_capture_hash"
            ],
            "filesystem_replace_worker_replay_hash": binding[
                "worker_replay_hash"
            ],
            "filesystem_replace_worker_completion_hash": binding[
                "completion_wrapper_hash"
            ],
            "validation_replay_hash": binding["validation_replay_hash"],
            "post_execution_replay_review_replay_hash": reconstructed[
                "replay_hash"
            ],
            **_terminal_truth(
                review_completed=True,
                repository_mutated=True,
                canonical_called=True,
            ),
        }
    except Exception as exc:
        return _failed(
            str(exc),
            validated=validated,
            canonical_called=canonical_called,
            repository_mutated=repository_mutated,
        )


def reconstruct_filesystem_replace_worker_post_execution_replay_review_binding(
    *,
    review_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    authenticated_request: dict[str, Any],
    filesystem_worker_capture: dict[str, Any],
    filesystem_worker_reconstruction: dict[str, Any],
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    worker_assignment_artifact: dict[str, Any],
    execution_artifact: dict[str, Any],
    execution_replay: dict[str, Any],
    execution_reconstruction: dict[str, Any],
    execution_replay_reference: str,
) -> dict[str, Any]:
    """Reconstruct generic review through the same immutable typed lineage."""

    binding = _authenticate_validation(
        validation_binding_capture=validation_binding_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        authenticated_request=authenticated_request,
        filesystem_worker_capture=filesystem_worker_capture,
        filesystem_worker_reconstruction=filesystem_worker_reconstruction,
        worker_invocation_artifact=worker_invocation_artifact,
        worker_invocation_replay_reference=worker_invocation_replay_reference,
        worker_assignment_artifact=worker_assignment_artifact,
        execution_artifact=execution_artifact,
        execution_replay=execution_replay,
        execution_reconstruction=execution_reconstruction,
        execution_replay_reference=execution_replay_reference,
    )
    if (
        review_binding_capture.get(
            "g31_filesystem_post_execution_replay_review_status"
        )
        != SUCCESS
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Replay Review binding is not successful"
        )
    replay_path = _inside_session(
        review_binding_capture.get(
            "post_execution_replay_review_replay_reference"
        ),
        binding["session_root"],
        "Post-Execution Replay Review reference",
    )
    request_binding = review_binding_capture.get("review_request_binding")
    if not isinstance(request_binding, dict):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker review request binding is invalid"
        )
    review_id = _required(
        request_binding.get("post_execution_replay_review_id"),
        "post_execution_replay_review_id",
    )
    reconstructed = reconstruct_schema_aware_post_execution_replay_review(
        replay_path
    )
    _validate_canonical_reconstruction(
        canonical=review_binding_capture,
        reconstruction=reconstructed,
        binding=binding,
        review_id=review_id,
        replay_path=replay_path,
    )
    expected_request = _review_request_binding(
        review_id=review_id,
        binding=binding,
        destination=replay_path,
    )
    if request_binding != expected_request:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker review request binding mismatch"
        )
    if not all(
        (
            review_binding_capture.get("authorization_lineage_schema")
            == AUTHENTICATED_REPLACEMENT_SCHEMA,
            review_binding_capture.get("authorization_commitment_kind")
            == RECORD_HASH_COMMITMENT,
            review_binding_capture.get("authorization_commitment")
            == binding["authorization_hash"],
            review_binding_capture.get("authorization_source_replay_hash")
            == binding["authorization_replay_hash"],
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Authorization lineage binding mismatch"
        )
    return {
        "g31_filesystem_post_execution_replay_review_status": SUCCESS,
        "review_status": reconstructed["review_status"],
        "post_execution_replay_review_id": reconstructed[
            "post_execution_replay_review_id"
        ],
        "worker_result_validation_reference": reconstructed[
            "worker_result_validation_reference"
        ],
        "worker_result_validation_hash": binding["validation"]["artifact_hash"],
        "worker_result_capture_reference": reconstructed[
            "worker_result_capture_reference"
        ],
        "authorization_lineage_schema": AUTHENTICATED_REPLACEMENT_SCHEMA,
        "authorization_commitment_kind": RECORD_HASH_COMMITMENT,
        "authorization_commitment": binding["authorization_hash"],
        "authorization_source_replay_hash": binding[
            "authorization_replay_hash"
        ],
        "worker_output_reference": binding["worker_output_reference"],
        "worker_output_hash": binding["worker_output_hash"],
        "worker_output_payload_hash": binding["worker_output_payload_hash"],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture_hash"
        ],
        "filesystem_replace_worker_replay_hash": binding["worker_replay_hash"],
        "filesystem_replace_worker_completion_hash": binding[
            "completion_wrapper_hash"
        ],
        "validation_replay_hash": binding["validation_replay_hash"],
        "replay_artifact_count": reconstructed["replay_artifact_count"],
        "replay_hash": reconstructed["replay_hash"],
        **_terminal_truth(
            review_completed=True,
            repository_mutated=True,
            canonical_called=True,
        ),
    }


def reconstruct_schema_aware_post_execution_replay_review(
    replay_reference: str | Path,
) -> dict[str, Any]:
    """Reconstruct one review through immutable invocation-scoped lineage."""

    return replay_review.reconstruct_post_execution_replay_review(
        replay_reference,
        chain_artifact_loader=_load_schema_aware_chain_artifacts,
    )


def _load_schema_aware_chain_artifacts(
    validation_evidence: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result_capture_path = _resolve_replay_reference(
        validation_evidence["worker_result_capture_replay_reference"],
        anchor=Path.cwd(),
    )
    result_capture_evidence = replay_review._load_artifact(
        result_capture_path,
        0,
        "result_capture_evidence_recorded",
    )
    result_capture = replay_review._load_artifact(
        result_capture_path,
        2,
        "result_capture_artifact_recorded",
    )
    invocation_path = _resolve_replay_reference(
        result_capture_evidence["worker_invocation_replay_reference"],
        anchor=result_capture_path,
    )
    invocation_evidence = replay_review._load_artifact(
        invocation_path,
        0,
        "invocation_evidence_recorded",
    )
    invocation = replay_review._load_artifact(
        invocation_path,
        2,
        "invocation_artifact_recorded",
    )
    dispatch_path = _resolve_replay_reference(
        invocation_evidence["worker_dispatch_replay_reference"],
        anchor=invocation_path,
    )
    dispatch_evidence = replay_review._load_artifact(
        dispatch_path,
        0,
        "dispatch_evidence_recorded",
    )
    dispatch = replay_review._load_artifact(
        dispatch_path,
        2,
        "dispatch_artifact_recorded",
    )
    assignment_path = _resolve_replay_reference(
        dispatch_evidence["worker_assignment_replay_reference"],
        anchor=dispatch_path,
    )
    assignment_evidence = replay_review._load_artifact(
        assignment_path,
        0,
        "assignment_evidence_recorded",
    )
    assignment = replay_review._load_artifact(
        assignment_path,
        2,
        "assignment_artifact_recorded",
    )
    request_path = _resolve_replay_reference(
        assignment_evidence["worker_invocation_request_replay_reference"],
        anchor=assignment_path,
    )
    request_evidence = replay_review._load_artifact(
        request_path,
        0,
        "invocation_request_evidence_recorded",
    )
    request = replay_review._load_artifact(
        request_path,
        2,
        "invocation_request_artifact_recorded",
    )
    authorization = resolve_authorization_lineage(
        request_replay_path=request_path,
        request_evidence=request_evidence,
        request_artifact=request,
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


def resolve_authorization_lineage(
    *,
    request_replay_path: str | Path,
    request_evidence: dict[str, Any],
    request_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Resolve one immutable Authorization lineage with typed hash semantics."""

    replay_path = Path(request_replay_path).resolve()
    reconstructed_request = reconstruct_worker_invocation_request_replay(
        replay_path
    )
    if reconstructed_request.get("request_status") != "WORKER_INVOCATION_REQUEST_CREATED":
        raise FailClosedRuntimeError(
            "schema-aware Authorization lineage requires valid Invocation Request"
        )
    compatibility = request_artifact.get("compatibility_lineage")
    if compatibility is None:
        authorization_path = _resolve_replay_reference(
            request_evidence["execution_authorization_replay_reference"],
            anchor=replay_path,
        )
        reconstructed = reconstruct_execution_authorization_replay(
            authorization_path
        )
        authorization = replay_review._load_artifact(
            authorization_path,
            2,
            "authorization_artifact_recorded",
        )
        if not all(
            (
                reconstructed.get("authorization_status")
                == EXECUTION_AUTHORIZED,
                request_artifact.get("authorization_reference")
                == authorization.get("authorization_id"),
                request_artifact.get("authorization_hash")
                == authorization.get("artifact_hash"),
                request_evidence.get("authorization_hash")
                == authorization.get("artifact_hash"),
                request_artifact.get("chain_id")
                == authorization.get("chain_id"),
            )
        ):
            raise FailClosedRuntimeError(
                "historical Authorization lineage mismatch"
            )
        return {
            **deepcopy(authorization),
            "authorization_lineage_schema": HISTORICAL_SCHEMA,
            "authorization_commitment_kind": ARTIFACT_HASH_COMMITMENT,
            "authorization_commitment": authorization["artifact_hash"],
            "authorization_source_replay_hash": reconstructed["replay_hash"],
        }
    if not isinstance(compatibility, dict) or compatibility.get(
        "lineage_type"
    ) != COMPATIBILITY_LINEAGE_TYPE:
        raise FailClosedRuntimeError(
            "authenticated replacement Authorization lineage schema invalid"
        )
    authenticated_request = (
        filesystem_replace_worker.validate_authenticated_replace_request_v2(
            compatibility.get("authenticated_request")
        )
    )
    session_root = Path(authenticated_request["session_root"]).resolve()
    if not replay_path.is_relative_to(session_root):
        raise FailClosedRuntimeError(
            "authenticated replacement Invocation Request is cross-session"
        )
    authorization_path = _resolve_replay_reference(
        request_evidence["execution_authorization_replay_reference"],
        anchor=replay_path,
    ).resolve()
    if not authorization_path.is_relative_to(session_root):
        raise FailClosedRuntimeError(
            "authenticated replacement Authorization Replay is cross-session"
        )
    if authorization_path != Path(
        authenticated_request["authorization_replay_reference"]
    ).resolve():
        raise FailClosedRuntimeError(
            "authenticated replacement Authorization Replay mismatch"
        )
    reconstructed = reconstruct_existing_authorization_binding_replay(
        authorization_path,
        session_root=session_root,
    )
    binding = reconstructed.get("authorization_binding_artifact")
    if not isinstance(binding, dict):
        raise FailClosedRuntimeError(
            "authenticated replacement Authorization binding missing"
        )
    selection_capture = compatibility.get("resource_selection_capture")
    if not isinstance(selection_capture, dict):
        raise FailClosedRuntimeError(
            "authenticated replacement selection lineage missing"
        )
    context_hash = selection_capture.get(
        "consumed_replacement_selection_context_hash"
    )
    checks = (
        reconstructed_request.get(
            "complete_worker_selection_lineage_reconstructed"
        )
        is True,
        request_evidence.get("execution_authorization_replay_reference")
        == authenticated_request["authorization_replay_reference"],
        request_evidence.get("authorization_reference")
        == authenticated_request["authorization_id"],
        request_evidence.get("authorization_hash")
        == authenticated_request["authorization_hash"],
        request_artifact.get("authorization_reference")
        == authenticated_request["authorization_id"],
        request_artifact.get("authorization_hash")
        == authenticated_request["authorization_hash"],
        request_artifact.get("chain_id") == context_hash,
        request_evidence.get("chain_id") == context_hash,
        reconstructed.get("canonical_authorization_actor")
        == CANONICAL_AUTHORIZATION_ACTOR,
        reconstructed.get("authorization_replay_reference")
        == str(authorization_path),
        reconstructed.get("authorization_replay_hash")
        == authenticated_request["authorization_replay_hash"],
        binding.get("authorization_id")
        == authenticated_request["authorization_id"],
        binding.get("authorization_hash")
        == authenticated_request["authorization_hash"],
        binding.get("authorization_status")
        == authenticated_request["authorization_status"]
        == "AUTHORIZED",
        binding.get("authorization_scope")
        == authenticated_request["authorization_scope"],
        binding.get("canonical_authorization_actor")
        == authenticated_request["canonical_authorization_actor"],
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "authenticated replacement Authorization lineage mismatch"
        )
    return {
        "artifact_hash": authenticated_request["authorization_hash"],
        "chain_id": request_artifact["chain_id"],
        "authorization_id": authenticated_request["authorization_id"],
        "authorization_status": authenticated_request["authorization_status"],
        "canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR,
        "authorization_lineage_schema": AUTHENTICATED_REPLACEMENT_SCHEMA,
        "authorization_commitment_kind": RECORD_HASH_COMMITMENT,
        "authorization_commitment": authenticated_request[
            "authorization_hash"
        ],
        "authorization_source_replay_hash": reconstructed[
            "authorization_replay_hash"
        ],
        "replay_visible": True,
        "authoritative": False,
    }


def _authenticate_validation(
    *,
    validation_binding_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    authenticated_request: dict[str, Any],
    filesystem_worker_capture: dict[str, Any],
    filesystem_worker_reconstruction: dict[str, Any],
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    worker_assignment_artifact: dict[str, Any],
    execution_artifact: dict[str, Any],
    execution_replay: dict[str, Any],
    execution_reconstruction: dict[str, Any],
    execution_replay_reference: str,
) -> dict[str, Any]:
    request = filesystem_replace_worker.validate_authenticated_replace_request_v2(
        authenticated_request
    )
    session_root = Path(request["session_root"]).resolve()
    validation_reconstruction = (
        validation_binding.reconstruct_filesystem_replace_worker_result_validation_binding(
            validation_binding_capture=validation_binding_capture,
            result_capture_binding_capture=result_capture_binding_capture,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_worker_capture,
            filesystem_worker_reconstruction=filesystem_worker_reconstruction,
            worker_invocation_artifact=worker_invocation_artifact,
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            worker_assignment_artifact=worker_assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution_replay,
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=execution_replay_reference,
        )
    )
    if (
        validation_reconstruction.get(
            "g31_filesystem_result_validation_status"
        )
        != validation_binding.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "schema-aware Replay Review requires certified R18C validation"
        )
    validation_replay_path = _inside_session(
        validation_binding_capture.get(
            "worker_result_validation_replay_reference"
        ),
        session_root,
        "Result Validation Replay reference",
    )
    wrappers = _load_replay_wrappers(
        validation_replay_path,
        result_validation.REPLAY_STEPS,
        "Result Validation Replay",
    )
    evidence, classification, validation, result = (
        wrapper["artifact"] for wrapper in wrappers
    )
    provided = (
        validation_binding_capture.get("validation_evidence_artifact"),
        validation_binding_capture.get("validation_classification_artifact"),
        validation_binding_capture.get("worker_result_validation_artifact"),
        validation_binding_capture.get("validation_result_artifact"),
    )
    if tuple(deepcopy(item) for item in provided) != (
        evidence,
        classification,
        validation,
        result,
    ):
        raise FailClosedRuntimeError(
            "schema-aware Replay Review validation evidence mismatch"
        )
    canonical_reconstruction = (
        result_validation.reconstruct_worker_result_validation_replay(
            validation_replay_path
        )
    )
    request_binding = validation_binding_capture.get(
        "validation_request_binding"
    )
    if not isinstance(request_binding, dict):
        raise FailClosedRuntimeError(
            "schema-aware Replay Review validation commitment invalid"
        )
    authorization_reconstruction = (
        reconstruct_existing_authorization_binding_replay(
            request["authorization_replay_reference"],
            session_root=session_root,
        )
    )
    checks = (
        validation.get("artifact_type")
        == result_validation.WORKER_RESULT_VALIDATION_ARTIFACT_V1,
        validation.get("validation_status")
        == result_validation.RESULT_VALIDATED,
        result.get("validation_status")
        == result_validation.RESULT_VALIDATED,
        validation_reconstruction.get("worker_result_validation_id")
        == validation["worker_result_validation_id"],
        validation_reconstruction.get("replay_hash")
        == canonical_reconstruction.get("replay_hash"),
        validation_reconstruction.get("replay_artifact_count") == 4,
        canonical_reconstruction.get("post_execution_replay_reviewed")
        is False,
        validation_reconstruction.get("worker_output_hash")
        == validation["worker_output_hash"],
        validation_reconstruction.get("worker_output_payload_hash")
        == request_binding.get("worker_output_payload_hash"),
        validation_reconstruction.get("filesystem_replace_worker_capture_hash")
        == request_binding.get("filesystem_replace_worker_capture_hash"),
        validation_reconstruction.get("filesystem_replace_worker_replay_hash")
        == request_binding.get("filesystem_replace_worker_replay_hash"),
        validation_reconstruction.get(
            "filesystem_replace_worker_completion_hash"
        )
        == request_binding.get("completion_wrapper_hash"),
        authorization_reconstruction.get("authorization_replay_hash")
        == request["authorization_replay_hash"],
        validation.get("authorization_reference")
        == request["authorization_id"],
        validation.get("authorization_hash") == request["authorization_hash"],
        filesystem_worker_capture.get("repository_mutated") is True,
        filesystem_worker_capture.get("restoration_performed") is False,
        filesystem_worker_capture.get("recovery_required") is False,
        filesystem_worker_capture.get("mutation_terminated") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "schema-aware Replay Review admission mismatch"
        )
    return {
        "session_root": session_root,
        "validation_replay_path": validation_replay_path,
        "validation_replay_hash": canonical_reconstruction["replay_hash"],
        "validation_evidence": evidence,
        "validation_classification": classification,
        "validation": validation,
        "validation_result": result,
        "authorization_hash": request["authorization_hash"],
        "authorization_replay_hash": request["authorization_replay_hash"],
        "worker_result_capture_reference": validation[
            "worker_result_capture_reference"
        ],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "worker_output_reference": validation["worker_output_reference"],
        "worker_output_hash": validation["worker_output_hash"],
        "worker_output_payload_hash": request_binding[
            "worker_output_payload_hash"
        ],
        "filesystem_capture_hash": request_binding[
            "filesystem_replace_worker_capture_hash"
        ],
        "worker_replay_hash": request_binding[
            "filesystem_replace_worker_replay_hash"
        ],
        "journal_wrapper_hash": request_binding["journal_wrapper_hash"],
        "result_wrapper_hash": request_binding["result_wrapper_hash"],
        "completion_wrapper_hash": request_binding[
            "completion_wrapper_hash"
        ],
    }


def _review_request_binding(
    *,
    review_id: str,
    binding: dict[str, Any],
    destination: Path,
) -> dict[str, Any]:
    return {
        "post_execution_replay_review_id": review_id,
        "worker_result_validation_reference": binding["validation"][
            "worker_result_validation_id"
        ],
        "worker_result_validation_hash": binding["validation"][
            "artifact_hash"
        ],
        "worker_result_validation_replay_reference": str(
            binding["validation_replay_path"]
        ),
        "worker_result_validation_replay_hash": binding[
            "validation_replay_hash"
        ],
        "validation_evidence_hash": binding["validation_evidence"][
            "artifact_hash"
        ],
        "validation_classification_hash": binding[
            "validation_classification"
        ]["artifact_hash"],
        "validation_result_hash": binding["validation_result"][
            "artifact_hash"
        ],
        "authorization_lineage_schema": AUTHENTICATED_REPLACEMENT_SCHEMA,
        "authorization_commitment_kind": RECORD_HASH_COMMITMENT,
        "authorization_commitment": binding["authorization_hash"],
        "authorization_source_replay_hash": binding[
            "authorization_replay_hash"
        ],
        "worker_result_capture_reference": binding[
            "worker_result_capture_reference"
        ],
        "worker_result_capture_hash": binding["worker_result_capture_hash"],
        "worker_output_reference": binding["worker_output_reference"],
        "worker_output_hash": binding["worker_output_hash"],
        "worker_output_payload_hash": binding["worker_output_payload_hash"],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture_hash"
        ],
        "filesystem_replace_worker_replay_hash": binding["worker_replay_hash"],
        "journal_wrapper_hash": binding["journal_wrapper_hash"],
        "result_wrapper_hash": binding["result_wrapper_hash"],
        "completion_wrapper_hash": binding["completion_wrapper_hash"],
        "review_destination": str(destination),
    }


def _validate_canonical_reconstruction(
    *,
    canonical: dict[str, Any],
    reconstruction: dict[str, Any],
    binding: dict[str, Any],
    review_id: str,
    replay_path: Path,
) -> None:
    wrappers = _load_replay_wrappers(
        replay_path,
        replay_review.REPLAY_STEPS,
        "Post-Execution Replay Review",
    )
    evidence, classification, review, result = (
        wrapper["artifact"] for wrapper in wrappers
    )
    provided = (
        canonical.get("review_evidence_artifact"),
        canonical.get("review_classification_artifact"),
        canonical.get("post_execution_replay_review_artifact"),
        canonical.get("review_result_artifact"),
    )
    checks = (
        tuple(deepcopy(item) for item in provided)
        == (evidence, classification, review, result),
        reconstruction.get("review_status") == replay_review.REVIEW_COMPLETED,
        reconstruction.get("post_execution_replay_review_id") == review_id,
        reconstruction.get("worker_result_validation_reference")
        == binding["validation"]["worker_result_validation_id"],
        reconstruction.get("worker_result_capture_reference")
        == binding["worker_result_capture_reference"],
        reconstruction.get("replay_artifact_count") == 4,
        reconstruction.get("result_validated") is True,
        reconstruction.get("post_execution_replay_reviewed") is True,
        reconstruction.get("terminated") is False,
        reconstruction.get("governance_mutated") is False,
        reconstruction.get("replay_mutated") is False,
        review.get("worker_result_validation_hash")
        == binding["validation"]["artifact_hash"],
        review.get("worker_result_capture_hash")
        == binding["worker_result_capture_hash"],
        review.get("authorization_hash") == binding["authorization_hash"],
        review.get("reviewed_by") == REVIEWED_BY,
        review.get("real_output_binding_reference") is None,
        review.get("domain_bundle_reference") is None,
        review.get("executable_bundle_reference") is None,
        all(
            review.get(field) == replay_review.INTEGRITY_VERIFIED
            for field in (
                "replay_integrity_assessment",
                "authority_integrity_assessment",
                "execution_integrity_assessment",
                "validation_integrity_assessment",
                "output_binding_integrity_assessment",
            )
        ),
        canonical.get("review_status") == replay_review.REVIEW_COMPLETED,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "schema-aware canonical Replay Review mismatch"
        )


def _reject_repeated_review(
    session_root: Path,
    *,
    validation: dict[str, Any],
) -> None:
    for path in session_root.rglob("002_review_artifact_recorded.json"):
        wrapper = _load_wrapper(path, "Post-Execution Replay Review")
        review = wrapper["artifact"]
        if (
            review.get("worker_result_validation_reference")
            == validation["worker_result_validation_id"]
            or review.get("worker_result_validation_hash")
            == validation["artifact_hash"]
            or review.get("worker_result_capture_reference")
            == validation["worker_result_capture_reference"]
            or review.get("worker_result_capture_hash")
            == validation["worker_result_capture_hash"]
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker validation was already reviewed"
            )
    for path in session_root.rglob("003_review_result_recorded.json"):
        wrapper = _load_wrapper(path, "Post-Execution Replay Review")
        result = wrapper["artifact"]
        if (
            result.get("worker_result_validation_reference")
            == validation["worker_result_validation_id"]
            or result.get("worker_result_validation_hash")
            == validation["artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker validation was already submitted "
                "for review"
            )


def _ensure_destination_available(destination: Path) -> None:
    for index, step in enumerate(replay_review.REPLAY_STEPS):
        if (destination / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker Replay Review already exists"
            )


def _load_replay_wrappers(
    path: Path,
    steps: tuple[str, ...],
    label: str,
) -> tuple[dict[str, Any], ...]:
    wrappers = []
    for index, step in enumerate(steps):
        wrapper = _load_wrapper(path / f"{index:03d}_{step}.json", label)
        if (
            wrapper.get("replay_index") != index
            or wrapper.get("replay_step") != step
        ):
            raise FailClosedRuntimeError(f"{label} ordering mismatch")
        wrappers.append(wrapper)
    return tuple(wrappers)


def _load_wrapper(path: Path, label: str) -> dict[str, Any]:
    wrapper = load_json(path)
    verify_replay_hash(wrapper)
    _verify_artifact(wrapper.get("artifact"), f"{label} artifact")
    return wrapper


def _verify_artifact(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict) or not isinstance(
        artifact.get("artifact_hash"), str
    ):
        raise FailClosedRuntimeError(f"{label} is invalid")
    value = deepcopy(artifact)
    actual = value.pop("artifact_hash")
    if actual != replay_hash(value):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _inside_session(
    path: str | Path | Any,
    session_root: Path,
    label: str,
) -> Path:
    if not isinstance(path, (str, Path)) or not str(path):
        raise FailClosedRuntimeError(f"{label} is required")
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(session_root):
        raise FailClosedRuntimeError(f"{label} is cross-session")
    return resolved


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(
            f"schema-aware Replay Review requires {field}"
        )
    return value.strip()


def _terminal_truth(
    *,
    review_completed: bool,
    repository_mutated: bool,
    canonical_called: bool,
) -> dict[str, Any]:
    return {
        "authentic_worker_output_present": True,
        "worker_result_captured": True,
        "result_created": True,
        "semantic_validation_performed": True,
        "result_validation_performed": True,
        "result_validated": True,
        "validation_replay_created": True,
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "result_accepted": False,
        "post_execution_replay_review_performed": canonical_called,
        "post_execution_replay_reviewed": review_completed,
        "post_execution_replay_review_count": 1 if canonical_called else 0,
        "execution_certified": False,
        "repository_mutated": repository_mutated,
        "main_repository_mutated": repository_mutated,
        "provider_invoked": False,
        "command_executed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _failed(
    reason: str,
    *,
    validated: bool,
    canonical_called: bool,
    repository_mutated: bool,
) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "g31_filesystem_post_execution_replay_review_status": FAILED_CLOSED,
        "review_status": replay_review.FAILED_CLOSED,
        "failure_reason": reason,
        "authentic_worker_output_present": validated,
        "worker_result_captured": validated,
        "result_created": validated,
        "semantic_validation_performed": validated,
        "result_validation_performed": validated,
        "result_validated": validated,
        "validation_replay_created": validated,
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "result_accepted": False,
        "post_execution_replay_review_performed": canonical_called,
        "post_execution_replay_reviewed": False,
        "post_execution_replay_review_count": 1 if canonical_called else 0,
        "execution_certified": False,
        "repository_mutated": repository_mutated,
        "main_repository_mutated": repository_mutated,
        "provider_invoked": False,
        "command_executed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
