"""Bind one certified Filesystem Replace Result Capture to generic validation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime import (
    filesystem_replace_worker_output_to_result_capture_binding_runtime
    as result_capture_binding,
)
from aigol.runtime import worker_result_capture_runtime
from aigol.runtime import worker_result_validation_runtime as result_validation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
)
from aigol.workers import filesystem_replace_worker


RUNTIME_VERSION = (
    "G31_FILESYSTEM_REPLACE_RESULT_CAPTURE_TO_RESULT_VALIDATION_BINDING_V1"
)
VALIDATED_BY = "PLATFORM_CORE_G31_FILESYSTEM_REPLACE_RESULT_VALIDATION_BINDING"
SUCCESS = "G31_FILESYSTEM_REPLACE_WORKER_RESULT_VALIDATION_COMPLETED"
INVALID = "G31_FILESYSTEM_REPLACE_WORKER_RESULT_VALIDATION_INVALID"
FAILED_CLOSED = "G31_FILESYSTEM_REPLACE_WORKER_RESULT_VALIDATION_FAILED_CLOSED"


def validate_captured_filesystem_replace_worker_result(
    *,
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
    validated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate one exact captured replacement through the canonical owner."""

    canonical_called = False
    captured = (
        result_capture_binding_capture.get(
            "g31_filesystem_result_capture_status"
        )
        == result_capture_binding.SUCCESS
    )
    repository_mutated = (
        filesystem_worker_capture.get("repository_mutated") is True
    )
    try:
        binding = _authenticate_result_capture(
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
            "Result Validation Replay destination",
        )
        _ensure_destination_available(destination)
        _reject_repeated_validation(
            binding["session_root"],
            capture_artifact=binding["capture_artifact"],
            worker_output=binding["worker_output"],
        )
        validation_id = (
            f"{binding['capture_artifact']['worker_result_capture_id']}:"
            f"{binding['worker_output']['artifact_hash']}:RESULT-VALIDATION"
        )
        request_binding = _validation_request_binding(
            validation_id=validation_id,
            binding=binding,
            destination=destination,
        )
        canonical_called = True
        canonical = result_validation.validate_worker_result(
            worker_result_validation_id=validation_id,
            worker_result_capture_artifact=binding["capture_artifact"],
            worker_result_capture_replay_reference=str(
                binding["result_capture_replay_path"]
            ),
            validated_by=VALIDATED_BY,
            validated_at=_required(validated_at, "validated_at"),
            replay_dir=destination,
        )
        if canonical.get("validation_status") == result_validation.FAILED_CLOSED:
            return {
                **deepcopy(canonical),
                "runtime_version": RUNTIME_VERSION,
                "g31_filesystem_result_validation_status": INVALID,
                "validation_request_binding": request_binding,
                **_terminal_truth(
                    result_validated=False,
                    repository_mutated=True,
                    canonical_called=True,
                ),
            }
        if canonical.get("validation_status") != result_validation.RESULT_VALIDATED:
            raise FailClosedRuntimeError(
                "canonical Result Validation returned an unknown status"
            )
        reconstructed = (
            result_validation.reconstruct_worker_result_validation_replay(
                destination
            )
        )
        _validate_canonical_reconstruction(
            canonical=canonical,
            reconstruction=reconstructed,
            binding=binding,
            validation_id=validation_id,
            replay_path=destination,
        )
        return {
            **deepcopy(canonical),
            "runtime_version": RUNTIME_VERSION,
            "g31_filesystem_result_validation_status": SUCCESS,
            "validation_request_binding": request_binding,
            "filesystem_replace_worker_output_hash": binding["worker_output"][
                "artifact_hash"
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
            "validation_replay_hash": reconstructed["replay_hash"],
            **_terminal_truth(
                result_validated=True,
                repository_mutated=True,
                canonical_called=True,
            ),
        }
    except Exception as exc:
        return _failed(
            str(exc),
            captured=captured,
            canonical_called=canonical_called,
            repository_mutated=repository_mutated,
        )


def reconstruct_filesystem_replace_worker_result_validation_binding(
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
    """Reconstruct validation and rebind it to exact Filesystem evidence."""

    binding = _authenticate_result_capture(
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
        validation_binding_capture.get(
            "g31_filesystem_result_validation_status"
        )
        != SUCCESS
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Validation binding is not successful"
        )
    replay_path = _inside_session(
        validation_binding_capture.get(
            "worker_result_validation_replay_reference"
        ),
        binding["session_root"],
        "Result Validation Replay reference",
    )
    reconstructed = result_validation.reconstruct_worker_result_validation_replay(
        replay_path
    )
    request_binding = validation_binding_capture.get("validation_request_binding")
    if not isinstance(request_binding, dict):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker validation request binding is invalid"
        )
    validation_id = _required(
        request_binding.get("worker_result_validation_id"),
        "worker_result_validation_id",
    )
    _validate_canonical_reconstruction(
        canonical=validation_binding_capture,
        reconstruction=reconstructed,
        binding=binding,
        validation_id=validation_id,
        replay_path=replay_path,
    )
    expected_request = _validation_request_binding(
        validation_id=validation_id,
        binding=binding,
        destination=replay_path,
    )
    if request_binding != expected_request:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker validation request binding mismatch"
        )
    return {
        "g31_filesystem_result_validation_status": SUCCESS,
        "validation_status": reconstructed["validation_status"],
        "worker_result_validation_id": reconstructed[
            "worker_result_validation_id"
        ],
        "worker_result_capture_reference": reconstructed[
            "worker_result_capture_reference"
        ],
        "worker_result_capture_hash": binding["capture_artifact"][
            "artifact_hash"
        ],
        "worker_output_reference": binding["worker_output"]["worker_output_id"],
        "worker_output_hash": binding["worker_output"]["artifact_hash"],
        "worker_output_payload_hash": binding["worker_output_payload_hash"],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture_hash"
        ],
        "filesystem_replace_worker_replay_hash": binding["worker_replay_hash"],
        "filesystem_replace_worker_completion_hash": binding[
            "completion_wrapper_hash"
        ],
        "replay_artifact_count": reconstructed["replay_artifact_count"],
        "replay_hash": reconstructed["replay_hash"],
        **_terminal_truth(
            result_validated=True,
            repository_mutated=True,
            canonical_called=True,
        ),
    }


def _authenticate_result_capture(
    *,
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
    capture_reconstruction = (
        result_capture_binding.reconstruct_filesystem_replace_worker_result_capture_binding(
            binding_capture=result_capture_binding_capture,
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
        capture_reconstruction.get("g31_filesystem_result_capture_status")
        != result_capture_binding.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Validation requires certified capture"
        )

    worker_output = deepcopy(
        result_capture_binding_capture.get(
            "filesystem_replace_worker_output_artifact"
        )
    )
    capture_artifact = deepcopy(
        result_capture_binding_capture.get("worker_result_capture_artifact")
    )
    _verify_artifact(worker_output, "Filesystem Replace Worker output")
    _verify_artifact(capture_artifact, "Worker Result Capture")
    if (
        worker_output.get("artifact_type")
        != result_capture_binding.FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1
        or capture_artifact.get("artifact_type")
        != worker_result_capture_runtime.WORKER_RESULT_CAPTURE_ARTIFACT_V1
        or capture_artifact.get("result_capture_status")
        != worker_result_capture_runtime.WORKER_RESULT_CAPTURED
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker validation artifact type mismatch"
        )
    payload = worker_output.get("payload")
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output payload is invalid"
        )
    payload_hash = replay_hash(payload)

    result_capture_replay_path = _inside_session(
        result_capture_binding_capture.get(
            "worker_result_capture_replay_reference"
        ),
        session_root,
        "Result Capture Replay reference",
    )
    capture_wrapper = _load_wrapper(
        result_capture_replay_path / "002_result_capture_artifact_recorded.json",
        "Result Capture Replay",
    )
    if capture_wrapper.get("artifact") != capture_artifact:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Capture artifact mismatch"
        )
    exact_capture_reconstruction = (
        worker_result_capture_runtime.reconstruct_worker_result_capture_replay(
            result_capture_replay_path
        )
    )

    journal = _load_wrapper(
        Path(request["destinations"]["journal"]),
        "Filesystem Replace Worker journal",
    )
    result = _load_wrapper(
        Path(request["destinations"]["result"]),
        "Filesystem Replace Worker result",
    )
    completion = _load_wrapper(
        Path(request["destinations"]["completion"]),
        "Filesystem Replace Worker completion",
    )
    invocation = worker_invocation_artifact
    assignment = worker_assignment_artifact
    execution = execution_artifact
    expected_events = list(result_capture_binding.EXPECTED_WORKER_EVENTS)
    expected_output_fields = {
        "artifact_type",
        "runtime_version",
        "worker_output_id",
        "worker_id",
        "worker_family",
        "worker_role",
        "worker_invocation_reference",
        "worker_dispatch_reference",
        "authorization_reference",
        "execution_packet_reference",
        "chain_id",
        "produced_outputs",
        "operations",
        "payload",
        "created_at",
        "replay_visible",
        "artifact_hash",
    }
    expected_payload_fields = {
        "request_id",
        "request_hash",
        "authorization_id",
        "authorization_hash",
        "target_path",
        "operation",
        "postimage_sha256",
        "replacement_mode",
        "worker_invocation_id",
        "worker_invocation_hash",
        "worker_dispatch_id",
        "worker_dispatch_hash",
        "worker_assignment_id",
        "worker_assignment_hash",
        "assignment_derived_capability",
        "execution_packet_id",
        "execution_packet_hash",
        "canonical_chain_id",
        "execution_id",
        "execution_hash",
        "execution_replay_reference",
        "execution_replay_hash",
        "filesystem_replace_worker_capture_hash",
        "filesystem_replace_worker_replay_reference",
        "filesystem_replace_worker_replay_hash",
        "filesystem_replace_worker_replay_artifact_count",
        "filesystem_replace_worker_event_keys",
        "journal_artifact_hash",
        "journal_wrapper_hash",
        "result_artifact_hash",
        "result_wrapper_hash",
        "completion_artifact_hash",
        "completion_wrapper_hash",
        "execution_status",
        "repository_mutated",
        "provider_invoked",
        "command_executed",
        "result_validated",
        "execution_certified",
    }

    checks = (
        set(worker_output) == expected_output_fields,
        set(payload) == expected_payload_fields,
        result_capture_binding_capture.get(
            "g31_filesystem_result_capture_status"
        )
        == result_capture_binding.SUCCESS,
        result_capture_binding_capture.get(
            "filesystem_replace_worker_output_hash"
        )
        == worker_output["artifact_hash"],
        result_capture_binding_capture.get(
            "filesystem_replace_worker_output_payload_hash"
        )
        == payload_hash,
        result_capture_binding_capture.get(
            "filesystem_replace_worker_capture_hash"
        )
        == filesystem_worker_capture.get("capture_hash"),
        result_capture_binding_capture.get(
            "filesystem_replace_worker_replay_hash"
        )
        == filesystem_worker_reconstruction.get("replay_hash"),
        result_capture_binding_capture.get(
            "filesystem_replace_worker_completion_hash"
        )
        == completion.get("replay_hash"),
        capture_artifact.get("worker_output_reference")
        == worker_output.get("worker_output_id"),
        capture_artifact.get("worker_output_hash")
        == worker_output["artifact_hash"],
        capture_artifact.get("worker_output_payload_hash") == payload_hash,
        capture_reconstruction.get("worker_output_hash")
        == worker_output["artifact_hash"],
        capture_reconstruction.get("worker_output_payload_hash") == payload_hash,
        exact_capture_reconstruction.get("worker_output_hash")
        == worker_output["artifact_hash"],
        exact_capture_reconstruction.get("replay_artifact_count") == 4,
        worker_output.get("worker_id") == invocation.get("worker_id"),
        worker_output.get("worker_family") == invocation.get("worker_family"),
        worker_output.get("worker_role") == invocation.get("worker_role"),
        worker_output.get("worker_invocation_reference")
        == invocation.get("worker_invocation_id"),
        worker_output.get("worker_dispatch_reference")
        == invocation.get("worker_dispatch_reference"),
        worker_output.get("authorization_reference")
        == invocation.get("authorization_reference"),
        worker_output.get("execution_packet_reference")
        == invocation.get("execution_packet_reference"),
        worker_output.get("chain_id") == invocation.get("chain_id"),
        worker_output.get("produced_outputs") == [request["target_path"]],
        worker_output.get("operations")
        == [filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE],
        worker_output.get("replay_visible") is True,
        payload.get("request_id") == request["request_id"],
        payload.get("request_hash") == request["request_hash"],
        payload.get("authorization_id") == request["authorization_id"],
        payload.get("authorization_hash") == request["authorization_hash"],
        payload.get("target_path") == request["target_path"],
        payload.get("operation") == request["worker_operation"],
        payload.get("postimage_sha256") == request["postimage_sha256"],
        payload.get("replacement_mode") == request["replacement_mode"],
        payload.get("worker_invocation_id")
        == invocation.get("worker_invocation_id"),
        payload.get("worker_invocation_hash") == invocation.get("artifact_hash"),
        payload.get("worker_dispatch_id")
        == invocation.get("worker_dispatch_reference"),
        payload.get("worker_dispatch_hash")
        == invocation.get("worker_dispatch_hash"),
        payload.get("worker_assignment_id")
        == assignment.get("worker_assignment_id"),
        payload.get("worker_assignment_hash") == assignment.get("artifact_hash"),
        payload.get("assignment_derived_capability")
        == filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE,
        payload.get("execution_packet_id")
        == invocation.get("execution_packet_reference"),
        payload.get("execution_packet_hash")
        == invocation.get("execution_packet_hash"),
        payload.get("canonical_chain_id") == invocation.get("chain_id"),
        payload.get("execution_id") == execution.get("execution_id"),
        payload.get("execution_hash") == execution.get("artifact_hash"),
        payload.get("execution_replay_reference")
        == str(Path(execution_replay_reference).resolve()),
        payload.get("execution_replay_hash")
        == execution_reconstruction.get("replay_hash"),
        payload.get("filesystem_replace_worker_capture_hash")
        == filesystem_worker_capture.get("capture_hash"),
        payload.get("filesystem_replace_worker_replay_reference")
        == filesystem_worker_reconstruction.get("request_replay_reference"),
        payload.get("filesystem_replace_worker_replay_hash")
        == filesystem_worker_reconstruction.get("replay_hash"),
        payload.get("filesystem_replace_worker_replay_artifact_count") == 7,
        payload.get("filesystem_replace_worker_event_keys") == expected_events,
        payload.get("journal_artifact_hash")
        == journal.get("artifact", {}).get("artifact_hash"),
        payload.get("journal_wrapper_hash") == journal.get("replay_hash"),
        payload.get("result_artifact_hash")
        == result.get("artifact", {}).get("artifact_hash"),
        payload.get("result_wrapper_hash") == result.get("replay_hash"),
        payload.get("completion_artifact_hash")
        == completion.get("artifact", {}).get("artifact_hash"),
        payload.get("completion_wrapper_hash") == completion.get("replay_hash"),
        payload.get("execution_status") == "COMPLETED",
        payload.get("repository_mutated") is True,
        payload.get("provider_invoked") is False,
        payload.get("command_executed") is False,
        payload.get("result_validated") is False,
        payload.get("execution_certified") is False,
        filesystem_worker_capture.get("repository_mutated") is True,
        filesystem_worker_capture.get("restoration_performed") is False,
        filesystem_worker_capture.get("recovery_required") is False,
        filesystem_worker_capture.get("mutation_terminated") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Validation admission mismatch"
        )
    return {
        "session_root": session_root,
        "request": request,
        "worker_output": worker_output,
        "worker_output_payload_hash": payload_hash,
        "capture_artifact": capture_artifact,
        "result_capture_replay_path": result_capture_replay_path,
        "capture_reconstruction": capture_reconstruction,
        "filesystem_capture_hash": filesystem_worker_capture["capture_hash"],
        "worker_replay_hash": filesystem_worker_reconstruction["replay_hash"],
        "journal_wrapper_hash": journal["replay_hash"],
        "result_wrapper_hash": result["replay_hash"],
        "completion_wrapper_hash": completion["replay_hash"],
    }


def _validation_request_binding(
    *,
    validation_id: str,
    binding: dict[str, Any],
    destination: Path,
) -> dict[str, Any]:
    output = binding["worker_output"]
    capture = binding["capture_artifact"]
    return {
        "worker_result_validation_id": validation_id,
        "worker_result_capture_reference": capture["worker_result_capture_id"],
        "worker_result_capture_hash": capture["artifact_hash"],
        "worker_result_capture_replay_reference": str(
            binding["result_capture_replay_path"]
        ),
        "worker_output_reference": output["worker_output_id"],
        "worker_output_hash": output["artifact_hash"],
        "worker_output_payload_hash": binding["worker_output_payload_hash"],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture_hash"
        ],
        "filesystem_replace_worker_replay_hash": binding["worker_replay_hash"],
        "journal_wrapper_hash": binding["journal_wrapper_hash"],
        "result_wrapper_hash": binding["result_wrapper_hash"],
        "completion_wrapper_hash": binding["completion_wrapper_hash"],
        "validation_destination": str(destination),
    }


def _validate_canonical_reconstruction(
    *,
    canonical: dict[str, Any],
    reconstruction: dict[str, Any],
    binding: dict[str, Any],
    validation_id: str,
    replay_path: Path,
) -> None:
    validation_wrapper = _load_wrapper(
        replay_path / "002_validation_artifact_recorded.json",
        "Result Validation Replay",
    )
    validation = validation_wrapper.get("artifact") or {}
    capture = binding["capture_artifact"]
    output = binding["worker_output"]
    checks = (
        reconstruction.get("validation_status")
        == result_validation.RESULT_VALIDATED,
        reconstruction.get("worker_result_validation_id") == validation_id,
        reconstruction.get("worker_result_capture_reference")
        == capture["worker_result_capture_id"],
        reconstruction.get("execution_reference")
        == capture.get("execution_reference"),
        reconstruction.get("worker_invocation_reference")
        == capture["worker_invocation_reference"],
        reconstruction.get("worker_dispatch_reference")
        == capture["worker_dispatch_reference"],
        reconstruction.get("authorization_reference")
        == capture["authorization_reference"],
        reconstruction.get("execution_packet_reference")
        == capture["execution_packet_reference"],
        reconstruction.get("worker_id") == capture["worker_id"],
        reconstruction.get("chain_id") == capture["chain_id"],
        reconstruction.get("replay_artifact_count") == 4,
        reconstruction.get("result_validated") is True,
        reconstruction.get("post_execution_replay_reviewed") is False,
        reconstruction.get("terminated") is False,
        reconstruction.get("governance_mutated") is False,
        reconstruction.get("replay_mutated") is False,
        validation.get("worker_result_capture_reference")
        == capture["worker_result_capture_id"],
        validation.get("worker_result_capture_hash") == capture["artifact_hash"],
        validation.get("worker_output_reference")
        == output["worker_output_id"],
        validation.get("worker_output_hash") == output["artifact_hash"],
        validation.get("worker_invocation_reference")
        == capture["worker_invocation_reference"],
        validation.get("worker_invocation_hash")
        == capture["worker_invocation_hash"],
        validation.get("worker_dispatch_reference")
        == capture["worker_dispatch_reference"],
        validation.get("worker_dispatch_hash") == capture["worker_dispatch_hash"],
        validation.get("worker_assignment_reference")
        == capture["worker_assignment_reference"],
        validation.get("worker_assignment_hash")
        == capture["worker_assignment_hash"],
        validation.get("authorization_reference")
        == capture["authorization_reference"],
        validation.get("authorization_hash") == capture["authorization_hash"],
        validation.get("execution_packet_reference")
        == capture["execution_packet_reference"],
        validation.get("execution_packet_hash")
        == capture["execution_packet_hash"],
        validation.get("execution_reference") == capture["execution_reference"],
        validation.get("execution_hash") == capture["execution_hash"],
        validation.get("execution_replay_hash")
        == capture["execution_replay_hash"],
        validation.get("execution_status") == capture["execution_status"],
        validation.get("worker_id") == capture["worker_id"],
        validation.get("worker_hash") == capture["worker_hash"],
        validation.get("chain_id") == capture["chain_id"],
        validation.get("produced_outputs") == output["produced_outputs"],
        validation.get("operations") == output["operations"],
        validation.get("validated_by") == VALIDATED_BY,
        validation.get("canonical_validation_meaning")
        == result_validation.CANONICAL_RESULT_VALIDATION_MEANING,
        validation.get("task_outcome_satisfaction_evaluated") is False,
        validation.get("task_outcome_satisfied") is False,
        canonical.get("worker_result_validation_artifact") == validation,
        canonical.get("validation_status") == result_validation.RESULT_VALIDATED,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker canonical Result Validation mismatch"
        )


def _reject_repeated_validation(
    session_root: Path,
    *,
    capture_artifact: dict[str, Any],
    worker_output: dict[str, Any],
) -> None:
    validated_captures: set[tuple[str, str]] = set()
    for path in session_root.rglob("002_validation_artifact_recorded.json"):
        wrapper = _load_wrapper(path, "Result Validation Replay")
        validation = wrapper.get("artifact") or {}
        reference = validation.get("worker_result_capture_reference")
        capture_hash = validation.get("worker_result_capture_hash")
        validated_captures.add((reference, capture_hash))
        if (
            reference == capture_artifact["worker_result_capture_id"]
            or capture_hash == capture_artifact["artifact_hash"]
            or validation.get("worker_output_reference")
            == worker_output["worker_output_id"]
            or validation.get("worker_output_hash")
            == worker_output["artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker result was already validated"
            )
    for path in session_root.rglob("003_validation_result_recorded.json"):
        wrapper = _load_wrapper(path, "Result Validation Replay")
        result = wrapper.get("artifact") or {}
        if (
            result.get("worker_result_capture_reference")
            == capture_artifact["worker_result_capture_id"]
            or result.get("worker_result_capture_hash")
            == capture_artifact["artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker result was already submitted for validation"
            )
    for path in session_root.rglob("002_result_capture_artifact_recorded.json"):
        wrapper = _load_wrapper(path, "Result Capture Replay")
        capture = wrapper.get("artifact") or {}
        if (
            (
                capture.get("worker_result_capture_id"),
                capture.get("artifact_hash"),
            )
            in validated_captures
            and capture.get("worker_output_payload_hash")
            == replay_hash(worker_output["payload"])
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker output payload was already validated"
            )


def _ensure_destination_available(destination: Path) -> None:
    for index, step in enumerate(result_validation.REPLAY_STEPS):
        if (destination / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker Result Validation Replay already exists"
            )


def _load_wrapper(path: Path, label: str) -> dict[str, Any]:
    wrapper = load_json(path)
    verify_replay_hash(wrapper)
    _verify_artifact(wrapper.get("artifact"), f"{label} artifact")
    return wrapper


def _verify_artifact(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict) or not isinstance(
        artifact.get("artifact_hash"), str
    ):
        raise FailClosedRuntimeError(f"{label} artifact is invalid")
    value = deepcopy(artifact)
    actual = value.pop("artifact_hash")
    if actual != replay_hash(value):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


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
            f"Filesystem Replace Worker Result Validation requires {field}"
        )
    return value.strip()


def _terminal_truth(
    *,
    result_validated: bool,
    repository_mutated: bool,
    canonical_called: bool,
) -> dict[str, Any]:
    return {
        "authentic_worker_output_present": True,
        "worker_result_captured": True,
        "result_created": True,
        "semantic_validation_performed": canonical_called,
        "result_validation_performed": canonical_called,
        "result_validated": result_validated,
        "validation_replay_created": canonical_called,
        "validation_count": 1 if canonical_called else 0,
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "result_accepted": False,
        "post_execution_replay_reviewed": False,
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
    captured: bool,
    canonical_called: bool,
    repository_mutated: bool,
) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "g31_filesystem_result_validation_status": FAILED_CLOSED,
        "validation_status": result_validation.FAILED_CLOSED,
        "canonical_validation_meaning": (
            result_validation.CANONICAL_RESULT_VALIDATION_MEANING
        ),
        "failure_reason": reason,
        "authentic_worker_output_present": captured,
        "worker_result_captured": captured,
        "result_created": captured,
        "semantic_validation_performed": canonical_called,
        "result_validation_performed": canonical_called,
        "result_validated": False,
        "validation_replay_created": canonical_called,
        "validation_count": 1 if canonical_called else 0,
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "result_accepted": False,
        "post_execution_replay_reviewed": False,
        "execution_certified": False,
        "repository_mutated": repository_mutated,
        "main_repository_mutated": repository_mutated,
        "provider_invoked": False,
        "command_executed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
