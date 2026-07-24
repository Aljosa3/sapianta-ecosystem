"""Bind one completed Filesystem Replace Worker Replay to canonical Result Capture."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime import execution_runtime
from aigol.runtime import worker_invocation_runtime
from aigol.runtime import worker_result_capture_runtime as result_capture
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
)
from aigol.workers import filesystem_replace_worker


RUNTIME_VERSION = (
    "G31_FILESYSTEM_REPLACE_WORKER_OUTPUT_TO_RESULT_CAPTURE_BINDING_V1"
)
FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1 = (
    "FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1"
)
CAPTURED_BY = "PLATFORM_CORE_G31_FILESYSTEM_REPLACE_RESULT_CAPTURE_BINDING"
SUCCESS = "G31_FILESYSTEM_REPLACE_WORKER_RESULT_CAPTURED"
FAILED_CLOSED = "G31_FILESYSTEM_REPLACE_WORKER_RESULT_CAPTURE_FAILED_CLOSED"

EXPECTED_WORKER_EVENTS = (
    "request",
    "consumption",
    "journal",
    "started",
    "atomic",
    "result",
    "completion",
)


def capture_completed_filesystem_replace_worker_result(
    *,
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
    captured_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture one authentic completed replacement without validating its result."""

    try:
        binding = _validate_completed_worker_binding(
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
            "Result Capture Replay destination",
        )
        _ensure_destination_available(destination)
        output = _worker_output(binding=binding, captured_at=captured_at)
        _reject_output_reuse(
            binding["session_root"],
            output_hash=output["artifact_hash"],
            payload_hash=replay_hash(output["payload"]),
        )
        capture = result_capture.capture_worker_result(
            worker_result_capture_id=(
                f"{binding['invocation']['worker_invocation_id']}:"
                f"{binding['completion_wrapper']['replay_hash']}:RESULT-CAPTURE"
            ),
            worker_invocation_artifact=binding["invocation"],
            worker_invocation_replay_reference=str(
                binding["invocation_replay_path"]
            ),
            worker_output=output,
            captured_by=CAPTURED_BY,
            captured_at=_required(captured_at, "captured_at"),
            replay_dir=destination,
            execution_artifact=binding["execution"],
            execution_replay=binding["execution_replay"],
            execution_replay_reference=str(binding["execution_replay_path"]),
        )
        if capture.get("result_capture_status") != result_capture.WORKER_RESULT_CAPTURED:
            raise FailClosedRuntimeError(
                "canonical Result Capture rejected Filesystem Replace Worker output: "
                f"{capture.get('failure_reason')}"
            )
        reconstructed = result_capture.reconstruct_worker_result_capture_replay(
            destination
        )
        _validate_result_capture_reconstruction(
            capture=capture,
            reconstruction=reconstructed,
            worker_output=output,
            binding=binding,
            replay_path=destination,
        )
        return {
            **deepcopy(capture),
            "runtime_version": RUNTIME_VERSION,
            "g31_filesystem_result_capture_status": SUCCESS,
            "filesystem_replace_worker_output_artifact": deepcopy(output),
            "filesystem_replace_worker_output_hash": output["artifact_hash"],
            "filesystem_replace_worker_output_payload_hash": replay_hash(
                output["payload"]
            ),
            "filesystem_replace_worker_capture_hash": binding[
                "filesystem_capture"
            ]["capture_hash"],
            "filesystem_replace_worker_replay_reference": binding[
                "worker_reconstruction"
            ]["request_replay_reference"],
            "filesystem_replace_worker_replay_hash": binding[
                "worker_reconstruction"
            ]["replay_hash"],
            "filesystem_replace_worker_completion_hash": binding[
                "completion_wrapper"
            ]["replay_hash"],
            **_success_truth(),
        }
    except Exception as exc:
        return _failed_capture(str(exc), filesystem_worker_capture)


def reconstruct_filesystem_replace_worker_result_capture_binding(
    *,
    binding_capture: dict[str, Any],
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
    """Reconstruct Result Capture and rebind it to exact Worker completion evidence."""

    binding = _validate_completed_worker_binding(
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
    if binding_capture.get("g31_filesystem_result_capture_status") != SUCCESS:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Capture binding is not successful"
        )
    output = binding_capture.get("filesystem_replace_worker_output_artifact")
    _verify_artifact(output, "Filesystem Replace Worker output artifact")
    replay_path = _inside_session(
        binding_capture.get("worker_result_capture_replay_reference"),
        binding["session_root"],
        "Result Capture Replay reference",
    )
    reconstructed = result_capture.reconstruct_worker_result_capture_replay(
        replay_path
    )
    _validate_result_capture_reconstruction(
        capture=binding_capture,
        reconstruction=reconstructed,
        worker_output=output,
        binding=binding,
        replay_path=replay_path,
    )
    return {
        "g31_filesystem_result_capture_status": SUCCESS,
        "worker_result_capture_id": reconstructed["worker_result_capture_id"],
        "worker_output_hash": output["artifact_hash"],
        "worker_output_payload_hash": replay_hash(output["payload"]),
        "execution_reference": reconstructed["execution_reference"],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture"
        ]["capture_hash"],
        "filesystem_replace_worker_replay_hash": binding[
            "worker_reconstruction"
        ]["replay_hash"],
        "filesystem_replace_worker_completion_hash": binding[
            "completion_wrapper"
        ]["replay_hash"],
        "replay_artifact_count": reconstructed["replay_artifact_count"],
        "replay_hash": reconstructed["replay_hash"],
        **_success_truth(),
    }


def _validate_completed_worker_binding(
    *,
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
    if not session_root.is_dir():
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Result Capture session is unavailable"
        )

    invocation = deepcopy(worker_invocation_artifact)
    assignment = deepcopy(worker_assignment_artifact)
    execution = deepcopy(execution_artifact)
    returned = deepcopy(execution_replay)
    filesystem_capture = deepcopy(filesystem_worker_capture)
    supplied_worker_reconstruction = deepcopy(filesystem_worker_reconstruction)
    supplied_execution_reconstruction = deepcopy(execution_reconstruction)

    _verify_artifact(invocation, "Worker Invocation artifact")
    _verify_artifact(assignment, "Worker Assignment artifact")
    _verify_artifact(execution, "Execution artifact")
    _verify_artifact(returned, "Execution returned artifact")
    _verify_named_hash(
        filesystem_capture,
        "capture_hash",
        "Filesystem Replace Worker terminal capture",
    )

    invocation_replay_path = _inside_session(
        worker_invocation_replay_reference,
        session_root,
        "Worker Invocation Replay reference",
    )
    invocation_reconstruction = (
        worker_invocation_runtime.reconstruct_worker_invocation_replay(
            invocation_replay_path
        )
    )
    invocation_wrapper = _load_runtime_wrapper(
        invocation_replay_path / "002_invocation_artifact_recorded.json",
        "Worker Invocation Replay",
    )
    if invocation_wrapper.get("artifact") != invocation:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output Invocation Replay mismatch"
        )

    execution_replay_path = _inside_session(
        execution_replay_reference,
        session_root,
        "Execution Replay reference",
    )
    exact_execution_reconstruction = execution_runtime.reconstruct_execution_replay(
        execution_replay_path
    )
    execution_wrapper = _load_runtime_wrapper(
        execution_replay_path / "000_execution_started.json",
        "Execution Replay",
    )
    returned_wrapper = _load_runtime_wrapper(
        execution_replay_path / "001_execution_returned.json",
        "Execution Replay",
    )
    if exact_execution_reconstruction != supplied_execution_reconstruction:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output Execution reconstruction mismatch"
        )
    if execution_wrapper.get("artifact", {}).get("artifact_hash") != execution.get(
        "artifact_hash"
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output Execution artifact mismatch"
        )
    if returned_wrapper.get("artifact", {}).get("artifact_hash") != returned.get(
        "artifact_hash"
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output Execution returned artifact mismatch"
        )

    exact_worker_reconstruction = (
        filesystem_replace_worker.reconstruct_authenticated_replace_replay_v2(
            request
        )
    )
    if exact_worker_reconstruction != supplied_worker_reconstruction:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output mutation Replay mismatch"
        )
    events = {
        key: _load_worker_wrapper(
            Path(request["destinations"][key]),
            expected_key=key,
        )
        for key in ("consumption", "journal", "result", "completion")
    }
    journal = events["journal"]
    result = events["result"]
    completion = events["completion"]
    journal_artifact = journal["artifact"]
    result_artifact = result["artifact"]
    completion_artifact = completion["artifact"]

    if not all(
        (
            tuple(exact_worker_reconstruction.get("event_keys", ()))
            == EXPECTED_WORKER_EVENTS,
            exact_worker_reconstruction.get("latest_event")
            == "MUTATION_COMPLETED",
            exact_worker_reconstruction.get("replay_artifact_count") == 7,
            exact_worker_reconstruction.get("last_wrapper_hash")
            == completion.get("replay_hash"),
            exact_worker_reconstruction.get("latest_artifact")
            == completion_artifact,
            journal.get("previous_replay_hash")
            == events["consumption"].get("replay_hash"),
            journal_artifact.get("event_type")
            == "PRE_WRITE_JOURNAL_PERSISTED",
            journal_artifact.get("payload", {}).get("preimage_sha256")
            == request["preimage_sha256"],
            journal_artifact.get("payload", {}).get("original_mode")
            == request["source_mode"],
            result_artifact.get("event_type")
            == "POST_WRITE_VALIDATION_SUCCEEDED",
            result_artifact.get("payload")
            == {
                "postimage_sha256": request["postimage_sha256"],
                "replacement_mode": request["replacement_mode"],
            },
            completion_artifact.get("event_type") == "MUTATION_COMPLETED",
            completion_artifact.get("payload", {}).get("execution_status")
            == "COMPLETED",
            completion_artifact.get("payload", {}).get("repository_mutated")
            is True,
            completion_artifact.get("payload", {}).get(
                "main_repository_mutated"
            )
            is True,
            completion_artifact.get("payload", {}).get(
                "restoration_performed"
            )
            is False,
            completion_artifact.get("payload", {}).get("recovery_required")
            is False,
            completion_artifact.get("payload", {}).get("mutation_terminated")
            is False,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output completion evidence mismatch"
        )

    if not all(
        (
            filesystem_capture.get("request_id") == request["request_id"],
            filesystem_capture.get("request_hash") == request["request_hash"],
            filesystem_capture.get("authorization_id")
            == request["authorization_id"],
            filesystem_capture.get("authorization_hash")
            == request["authorization_hash"],
            filesystem_capture.get("execution_status") == "COMPLETED",
            filesystem_capture.get("authorization_consumed") is True,
            filesystem_capture.get("worker_invoked") is True,
            filesystem_capture.get("provider_invoked") is False,
            filesystem_capture.get("command_executed") is False,
            filesystem_capture.get("git_performed") is False,
            filesystem_capture.get("repository_mutated") is True,
            filesystem_capture.get("main_repository_mutated") is True,
            filesystem_capture.get("restoration_performed") is False,
            filesystem_capture.get("recovery_required") is False,
            filesystem_capture.get("mutation_terminated") is False,
            filesystem_capture.get("replay_visible") is True,
            filesystem_capture.get("replay_hash")
            == exact_worker_reconstruction["replay_hash"],
            filesystem_capture.get("replay_artifact_count") == 7,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker terminal capture mismatch"
        )

    if not all(
        (
            invocation_reconstruction.get("invocation_status")
            == worker_invocation_runtime.WORKER_INVOKED,
            invocation_reconstruction.get("worker_invocation_id")
            == invocation.get("worker_invocation_id"),
            invocation.get("worker_id")
            == filesystem_replace_worker.FILESYSTEM_REPLACE_WORKER_ID,
            invocation.get("authorization_reference")
            == request["authorization_id"],
            invocation.get("authorization_hash")
            == request["authorization_hash"],
            invocation.get("execution_packet_reference")
            == request["request_id"],
            invocation.get("execution_packet_hash") == request["request_hash"],
            invocation.get("allowed_outputs") == [request["target_path"]],
            filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE
            not in invocation.get("forbidden_operations", []),
            assignment.get("assignment_status") == "WORKER_ASSIGNED",
            assignment.get("worker_assignment_id")
            == invocation.get("worker_assignment_reference"),
            assignment.get("artifact_hash")
            == invocation.get("worker_assignment_hash"),
            assignment.get("worker_id") == invocation.get("worker_id"),
            assignment.get("capability_id")
            == filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE,
            execution.get("execution_id")
            == exact_execution_reconstruction.get("execution_id"),
            execution.get("artifact_hash")
            == returned.get("execution_hash"),
            execution.get("worker_invocation_reference")
            == invocation.get("worker_invocation_id"),
            execution.get("worker_invocation_hash")
            == invocation.get("artifact_hash"),
            execution.get("dispatch_reference")
            == invocation.get("worker_dispatch_reference"),
            execution.get("dispatch_hash")
            == invocation.get("worker_dispatch_hash"),
            execution.get("worker_assignment_reference")
            == assignment.get("worker_assignment_id"),
            execution.get("worker_assignment_hash")
            == assignment.get("artifact_hash"),
            execution.get("readiness_reference") == request["request_id"],
            execution.get("canonical_chain_id") == invocation.get("chain_id"),
            execution.get("capability_id")
            == assignment.get("capability_id"),
            execution.get("execution_status") == execution_runtime.EXECUTING,
            execution.get("provider_authority") is False,
            execution.get("worker_self_started") is False,
            execution.get("completion_recorded") is False,
            execution.get("result_certified") is False,
            execution.get("governance_mutated") is False,
            execution.get("replay_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output execution lineage mismatch"
        )

    return {
        "request": request,
        "session_root": session_root,
        "filesystem_capture": filesystem_capture,
        "worker_reconstruction": exact_worker_reconstruction,
        "invocation": invocation,
        "invocation_reconstruction": invocation_reconstruction,
        "invocation_replay_path": invocation_replay_path,
        "assignment": assignment,
        "execution": execution,
        "execution_replay": returned,
        "execution_reconstruction": exact_execution_reconstruction,
        "execution_replay_path": execution_replay_path,
        "journal_wrapper": journal,
        "result_wrapper": result,
        "completion_wrapper": completion,
    }


def _worker_output(*, binding: dict[str, Any], captured_at: str) -> dict[str, Any]:
    request = binding["request"]
    invocation = binding["invocation"]
    execution = binding["execution"]
    reconstruction = binding["worker_reconstruction"]
    journal = binding["journal_wrapper"]
    result = binding["result_wrapper"]
    completion = binding["completion_wrapper"]
    payload = {
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "target_path": request["target_path"],
        "operation": request["worker_operation"],
        "postimage_sha256": request["postimage_sha256"],
        "replacement_mode": request["replacement_mode"],
        "worker_invocation_id": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_dispatch_id": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_id": binding["assignment"]["worker_assignment_id"],
        "worker_assignment_hash": binding["assignment"]["artifact_hash"],
        "assignment_derived_capability": binding["assignment"]["capability_id"],
        "execution_packet_id": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "canonical_chain_id": invocation["chain_id"],
        "execution_id": execution["execution_id"],
        "execution_hash": execution["artifact_hash"],
        "execution_replay_reference": str(binding["execution_replay_path"]),
        "execution_replay_hash": binding["execution_reconstruction"][
            "replay_hash"
        ],
        "filesystem_replace_worker_capture_hash": binding[
            "filesystem_capture"
        ]["capture_hash"],
        "filesystem_replace_worker_replay_reference": reconstruction[
            "request_replay_reference"
        ],
        "filesystem_replace_worker_replay_hash": reconstruction["replay_hash"],
        "filesystem_replace_worker_replay_artifact_count": reconstruction[
            "replay_artifact_count"
        ],
        "filesystem_replace_worker_event_keys": deepcopy(
            reconstruction["event_keys"]
        ),
        "journal_artifact_hash": journal["artifact"]["artifact_hash"],
        "journal_wrapper_hash": journal["replay_hash"],
        "result_artifact_hash": result["artifact"]["artifact_hash"],
        "result_wrapper_hash": result["replay_hash"],
        "completion_artifact_hash": completion["artifact"]["artifact_hash"],
        "completion_wrapper_hash": completion["replay_hash"],
        "execution_status": "COMPLETED",
        "repository_mutated": True,
        "provider_invoked": False,
        "command_executed": False,
        "result_validated": False,
        "execution_certified": False,
    }
    output = {
        "artifact_type": FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "worker_output_id": (
            f"{invocation['worker_invocation_id']}:"
            f"{completion['replay_hash']}:WORKER-OUTPUT"
        ),
        "worker_id": invocation["worker_id"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "authorization_reference": invocation["authorization_reference"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "chain_id": invocation["chain_id"],
        "produced_outputs": [request["target_path"]],
        "operations": [
            filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE
        ],
        "payload": payload,
        "created_at": _required(captured_at, "captured_at"),
        "replay_visible": True,
    }
    output["artifact_hash"] = replay_hash(output)
    return output


def _validate_result_capture_reconstruction(
    *,
    capture: dict[str, Any],
    reconstruction: dict[str, Any],
    worker_output: dict[str, Any],
    binding: dict[str, Any],
    replay_path: Path,
) -> None:
    capture_wrapper = _load_runtime_wrapper(
        replay_path / "002_result_capture_artifact_recorded.json",
        "Result Capture Replay",
    )
    capture_artifact = capture_wrapper.get("artifact") or {}
    payload = worker_output["payload"]
    if not all(
        (
            reconstruction.get("result_capture_status")
            == result_capture.WORKER_RESULT_CAPTURED,
            reconstruction.get("worker_output_hash")
            == worker_output["artifact_hash"],
            reconstruction.get("worker_invocation_reference")
            == binding["invocation"]["worker_invocation_id"],
            reconstruction.get("worker_dispatch_reference")
            == binding["invocation"]["worker_dispatch_reference"],
            reconstruction.get("worker_assignment_reference")
            == binding["assignment"]["worker_assignment_id"],
            reconstruction.get("execution_reference")
            == binding["execution"]["execution_id"],
            reconstruction.get("execution_hash")
            == binding["execution"]["artifact_hash"],
            reconstruction.get("authorization_reference")
            == binding["request"]["authorization_id"],
            reconstruction.get("execution_packet_reference")
            == binding["request"]["request_id"],
            reconstruction.get("worker_id")
            == filesystem_replace_worker.FILESYSTEM_REPLACE_WORKER_ID,
            reconstruction.get("chain_id")
            == binding["invocation"]["chain_id"],
            reconstruction.get("produced_outputs")
            == [binding["request"]["target_path"]],
            reconstruction.get("operations")
            == [
                filesystem_replace_worker.OPERATION_REPLACE_EXISTING_TEXT_FILE
            ],
            reconstruction.get("replay_artifact_count") == 4,
            reconstruction.get("result_created") is True,
            reconstruction.get("worker_result_captured") is True,
            reconstruction.get("result_validated") is False,
            reconstruction.get("post_execution_replay_reviewed") is False,
            reconstruction.get("terminated") is False,
            reconstruction.get("governance_mutated") is False,
            reconstruction.get("replay_mutated") is False,
            capture_artifact.get("worker_output_hash")
            == worker_output["artifact_hash"],
            capture_artifact.get("worker_output_payload_hash")
            == replay_hash(payload),
            payload.get("filesystem_replace_worker_capture_hash")
            == binding["filesystem_capture"]["capture_hash"],
            payload.get("filesystem_replace_worker_replay_hash")
            == binding["worker_reconstruction"]["replay_hash"],
            payload.get("journal_wrapper_hash")
            == binding["journal_wrapper"]["replay_hash"],
            payload.get("completion_wrapper_hash")
            == binding["completion_wrapper"]["replay_hash"],
            capture.get("result_capture_status")
            == result_capture.WORKER_RESULT_CAPTURED,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker output-to-Result-Capture continuity mismatch"
        )


def _reject_output_reuse(
    session_root: Path,
    *,
    output_hash: str,
    payload_hash: str,
) -> None:
    for path in session_root.rglob("002_result_capture_artifact_recorded.json"):
        wrapper = _load_runtime_wrapper(path, "Result Capture Replay")
        artifact = wrapper.get("artifact") or {}
        if (
            artifact.get("worker_output_hash") == output_hash
            or artifact.get("worker_output_payload_hash") == payload_hash
        ):
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker completion was already captured"
            )


def _ensure_destination_available(replay_dir: Path) -> None:
    for index, step in enumerate(result_capture.REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(
                "Filesystem Replace Worker Result Capture Replay already exists"
            )


def _load_worker_wrapper(path: Path, *, expected_key: str) -> dict[str, Any]:
    wrapper = load_json(path)
    verify_replay_hash(wrapper)
    if wrapper.get("event_key") != expected_key:
        raise FailClosedRuntimeError(
            "Filesystem Replace Worker Replay event mismatch"
        )
    _verify_artifact(
        wrapper.get("artifact"),
        "Filesystem Replace Worker Replay artifact",
    )
    return wrapper


def _load_runtime_wrapper(path: Path, label: str) -> dict[str, Any]:
    wrapper = load_json(path)
    verify_replay_hash(wrapper)
    _verify_artifact(wrapper.get("artifact"), f"{label} artifact")
    return wrapper


def _verify_artifact(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} is invalid")
    _verify_named_hash(artifact, "artifact_hash", label)


def _verify_named_hash(artifact: dict[str, Any], field: str, label: str) -> None:
    if not isinstance(artifact, dict) or not isinstance(artifact.get(field), str):
        raise FailClosedRuntimeError(f"{label} hash is required")
    value = deepcopy(artifact)
    actual = value.pop(field)
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
            f"Filesystem Replace Worker Result Capture requires {field}"
        )
    return value.strip()


def _success_truth() -> dict[str, bool]:
    return {
        "authentic_worker_output_present": True,
        "worker_result_captured": True,
        "result_created": True,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "execution_certified": False,
        "provider_invoked": False,
        "command_executed": False,
        "repository_mutated": True,
        "main_repository_mutated": True,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _failed_capture(
    reason: str,
    filesystem_worker_capture: dict[str, Any],
) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "g31_filesystem_result_capture_status": FAILED_CLOSED,
        "result_capture_status": result_capture.FAILED_CLOSED,
        "failure_reason": reason,
        "authentic_worker_output_present": False,
        "worker_result_captured": False,
        "result_created": False,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "execution_certified": False,
        "provider_invoked": False,
        "command_executed": False,
        "repository_mutated": (
            isinstance(filesystem_worker_capture, dict)
            and filesystem_worker_capture.get("repository_mutated") is True
        ),
        "main_repository_mutated": (
            isinstance(filesystem_worker_capture, dict)
            and filesystem_worker_capture.get("main_repository_mutated") is True
        ),
        "governance_mutated": False,
        "replay_mutated": False,
    }
