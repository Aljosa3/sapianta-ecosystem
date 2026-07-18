"""Bind one authentic captured CODEX result to canonical result validation."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

from aigol.runtime import worker_result_validation_runtime as result_validation
from aigol.runtime.codex_transport_to_worker_result_capture_binding_runtime import (
    SUCCESS as RESULT_CAPTURE_SUCCESS,
    reconstruct_codex_worker_result_capture_binding,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, verify_replay_hash


RUNTIME_VERSION = "G31_CODEX_CAPTURE_TO_SEMANTIC_VALIDATION_BINDING_V1"
VALIDATED_BY = "PLATFORM_CORE_G31_CODEX_SEMANTIC_VALIDATION_BINDING"
SUCCESS = "G31_CODEX_SEMANTIC_VALIDATION_COMPLETED"
INVALID = "G31_CODEX_SEMANTIC_VALIDATION_INVALID"
FAILED_CLOSED = "G31_CODEX_SEMANTIC_VALIDATION_FAILED_CLOSED"
VALIDATION_TRUTH_FIELDS = (
    "semantic_worker_result_captured", "semantic_validation_performed",
    "result_validated", "validation_replay_created", "validation_count",
    "result_accepted", "repository_mutated", "commit_created", "deployed",
    "released", "provider_invoked", "additional_worker_process_started",
)


def validate_captured_codex_worker_result(
    *,
    result_capture_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
    validated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate one exact in-memory CODEX stdout capture through the canonical owner."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    canonical_called = False
    captured = result_capture_binding_capture.get("semantic_worker_result_captured") is True
    try:
        if not destination.is_relative_to(root):
            raise FailClosedRuntimeError("G31 semantic validation destination is cross-session")
        _ensure_destination_available(destination)
        binding = reconstruct_codex_worker_result_capture_binding(
            binding_capture=result_capture_binding_capture,
            activation_capture=activation_capture,
            governed_execution_capture=governed_execution_capture,
            execution_candidate_capture=execution_candidate_capture,
            session_root=root,
            workspace=workspace,
        )
        if binding.get("g31_result_capture_status") != RESULT_CAPTURE_SUCCESS:
            raise FailClosedRuntimeError("G31 semantic validation requires WORKER_RESULT_CAPTURED")
        output, output_sha256, capture_artifact = _exact_semantic_output(
            result_capture_binding_capture
        )
        _reject_repeated_validation(
            root,
            capture_reference=capture_artifact["worker_result_capture_id"],
            capture_hash=capture_artifact["artifact_hash"],
        )
        validation_id = (
            f"{capture_artifact['worker_result_capture_id']}:"
            f"SEMANTIC-VALIDATION:{output_sha256[:24]}"
        )
        request_binding = {
            "worker_result_validation_id": validation_id,
            "worker_result_capture_reference": capture_artifact["worker_result_capture_id"],
            "worker_result_capture_hash": capture_artifact["artifact_hash"],
            "worker_output_hash": binding["worker_output_hash"],
            "semantic_output_encoding": "utf-8",
            "semantic_output_byte_length": len(output),
            "semantic_output_sha256": output_sha256,
            "validation_destination": str(destination),
        }
        canonical_called = True
        canonical = result_validation.validate_worker_result(
            worker_result_validation_id=validation_id,
            worker_result_capture_artifact=capture_artifact,
            worker_result_capture_replay_reference=(
                result_capture_binding_capture["worker_result_capture_replay_reference"]
            ),
            validated_by=VALIDATED_BY,
            validated_at=_required(validated_at, "validated_at"),
            replay_dir=destination,
        )
        status = canonical.get("validation_status")
        if status == result_validation.RESULT_VALIDATED:
            reconstructed = result_validation.reconstruct_worker_result_validation_replay(
                destination
            )
            validation_artifact = canonical.get("worker_result_validation_artifact") or {}
            checks = (
                reconstructed.get("replay_artifact_count") == 4,
                reconstructed.get("worker_result_validation_id") == validation_id,
                reconstructed.get("worker_result_capture_reference")
                == capture_artifact["worker_result_capture_id"],
                validation_artifact.get("worker_result_capture_hash")
                == capture_artifact["artifact_hash"],
                validation_artifact.get("worker_output_hash") == binding["worker_output_hash"],
            )
            if not all(checks):
                raise FailClosedRuntimeError("canonical semantic validation binding mismatch")
            return {
                **deepcopy(canonical),
                "runtime_version": RUNTIME_VERSION,
                "g31_semantic_validation_status": SUCCESS,
                "validation_request_binding": request_binding,
                "semantic_output_sha256": output_sha256,
                "semantic_output_byte_length": len(output),
                "validation_replay_hash": reconstructed["replay_hash"],
                "semantic_worker_result_captured": True,
                "semantic_validation_performed": True,
                "result_validated": True,
                "validation_replay_created": True,
                "validation_count": 1,
                **_stop_truth(),
            }
        if status == result_validation.FAILED_CLOSED:
            return {
                **deepcopy(canonical),
                "runtime_version": RUNTIME_VERSION,
                "g31_semantic_validation_status": INVALID,
                "validation_request_binding": request_binding,
                "semantic_output_sha256": output_sha256,
                "semantic_output_byte_length": len(output),
                "semantic_worker_result_captured": True,
                "semantic_validation_performed": True,
                "result_validated": False,
                "validation_replay_created": destination.exists(),
                "validation_count": 1,
                **_stop_truth(),
            }
        raise FailClosedRuntimeError("canonical Worker result validator returned an unknown status")
    except Exception as exc:
        return _failed(str(exc), captured=captured, canonical_called=canonical_called)


def reconstruct_codex_worker_semantic_validation_binding(
    *,
    validation_binding_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Reconstruct the canonical validation and its exact captured-byte binding."""

    binding = reconstruct_codex_worker_result_capture_binding(
        binding_capture=result_capture_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    output, output_sha256, capture_artifact = _exact_semantic_output(
        result_capture_binding_capture
    )
    replay_path = Path(
        validation_binding_capture.get("worker_result_validation_replay_reference", "")
    ).resolve()
    root = Path(session_root).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("G31 semantic validation Replay is cross-session")
    reconstructed = result_validation.reconstruct_worker_result_validation_replay(replay_path)
    validation_wrapper = load_json(replay_path / "002_validation_artifact_recorded.json")
    verify_replay_hash(validation_wrapper)
    validation_artifact = validation_wrapper.get("artifact") or {}
    request = validation_binding_capture.get("validation_request_binding") or {}
    checks = (
        validation_binding_capture.get("g31_semantic_validation_status") == SUCCESS,
        reconstructed.get("validation_status") == result_validation.RESULT_VALIDATED,
        request.get("worker_result_validation_id")
        == reconstructed.get("worker_result_validation_id"),
        request.get("worker_result_capture_reference")
        == capture_artifact["worker_result_capture_id"],
        request.get("worker_result_capture_hash") == capture_artifact["artifact_hash"],
        request.get("worker_output_hash") == binding["worker_output_hash"],
        request.get("semantic_output_byte_length") == len(output),
        request.get("semantic_output_sha256") == output_sha256,
        validation_artifact.get("worker_output_hash") == binding["worker_output_hash"],
        validation_artifact.get("worker_result_capture_hash")
        == capture_artifact["artifact_hash"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("G31 semantic validation reconstruction mismatch")
    return {
        "validation_status": reconstructed["validation_status"],
        "worker_result_validation_id": reconstructed["worker_result_validation_id"],
        "worker_result_capture_reference": reconstructed["worker_result_capture_reference"],
        "semantic_output_sha256": output_sha256,
        "semantic_output_byte_length": len(output),
        "worker_output_hash": binding["worker_output_hash"],
        "replay_artifact_count": reconstructed["replay_artifact_count"],
        "replay_hash": reconstructed["replay_hash"],
        "result_validated": True,
        **_stop_truth(),
    }


def render_codex_worker_semantic_validation(capture: dict[str, Any]) -> str:
    status = capture.get("validation_status")
    return "\n".join((
        "CODEX Semantic Worker Result Validation",
        f"Validation Status: {status}",
        f"Canonical Meaning: {capture.get('canonical_validation_meaning')}",
        "Task Outcome Satisfaction Evaluated: "
        f"{capture.get('task_outcome_satisfaction_evaluated')}",
        f"Task Outcome Satisfied: {capture.get('task_outcome_satisfied')}",
        f"Validation Reference: {capture.get('worker_result_validation_reference')}",
        f"Replay Reference: {capture.get('worker_result_validation_replay_reference')}",
        "Validation is deterministic evidence processing; AiCLI did not validate or accept the result.",
        "Repository mutation, commit, deployment, and release remain prohibited.",
    ))


def _exact_semantic_output(binding_capture: dict[str, Any]) -> tuple[bytes, str, dict[str, Any]]:
    worker_output = binding_capture.get("semantic_worker_output_artifact")
    _verify_artifact(worker_output, "semantic Worker output")
    payload = worker_output.get("payload") or {}
    text = payload.get("semantic_output")
    if not isinstance(text, str) or not text.strip():
        raise FailClosedRuntimeError("exact authentic semantic output bytes are unavailable")
    if payload.get("semantic_output_encoding") != "utf-8":
        raise FailClosedRuntimeError("semantic output encoding was substituted")
    encoded = text.encode("utf-8")
    digest = sha256(encoded).hexdigest()
    capture_path = Path(
        binding_capture.get("worker_result_capture_replay_reference", "")
    ).resolve()
    wrapper = load_json(capture_path / "002_result_capture_artifact_recorded.json")
    verify_replay_hash(wrapper)
    capture_artifact = wrapper.get("artifact") or {}
    _verify_artifact(capture_artifact, "Worker result capture")
    checks = (
        payload.get("semantic_output_byte_length") == len(encoded),
        payload.get("semantic_output_sha256") == digest,
        payload.get("transport_stdout_hash") == digest,
        capture_artifact == binding_capture.get("worker_result_capture_artifact"),
        capture_artifact.get("worker_output_hash") == worker_output["artifact_hash"],
        capture_artifact.get("worker_output_payload_hash") == replay_hash(payload),
    )
    if not all(checks):
        raise FailClosedRuntimeError("semantic output bytes, hashes, or capture were substituted")
    return encoded, digest, capture_artifact


def _reject_repeated_validation(root: Path, *, capture_reference: str, capture_hash: str) -> None:
    for path in root.rglob("003_validation_result_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        artifact = wrapper.get("artifact") or {}
        _verify_artifact(artifact, "Worker result validation result")
        if artifact.get("worker_result_capture_reference") == capture_reference:
            raise FailClosedRuntimeError("captured CODEX result was already submitted for validation")
    for path in root.rglob("002_validation_artifact_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        artifact = wrapper.get("artifact") or {}
        if artifact.get("worker_result_capture_hash") == capture_hash:
            raise FailClosedRuntimeError("captured CODEX result was already validated")


def _ensure_destination_available(destination: Path) -> None:
    for index, step in enumerate(result_validation.REPLAY_STEPS):
        if (destination / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("G31 semantic validation destination already exists")


def _stop_truth() -> dict[str, bool]:
    return {
        "result_accepted": False,
        "repository_mutated": False,
        "commit_created": False,
        "deployed": False,
        "released": False,
        "provider_invoked": False,
        "additional_worker_process_started": False,
    }


def _failed(reason: str, *, captured: bool, canonical_called: bool) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "g31_semantic_validation_status": FAILED_CLOSED,
        "validation_status": result_validation.FAILED_CLOSED,
        "canonical_validation_meaning": (
            result_validation.CANONICAL_RESULT_VALIDATION_MEANING
        ),
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "failure_reason": reason,
        "semantic_worker_result_captured": captured,
        "semantic_validation_performed": canonical_called,
        "result_validated": False,
        "validation_replay_created": False,
        "validation_count": 1 if canonical_called else 0,
        **_stop_truth(),
    }


def _verify_artifact(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict) or not isinstance(artifact.get("artifact_hash"), str):
        raise FailClosedRuntimeError(f"{label} artifact is invalid")
    value = deepcopy(artifact)
    actual = value.pop("artifact_hash")
    if actual != replay_hash(value):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G31 semantic validation requires {field}")
    return value.strip()
