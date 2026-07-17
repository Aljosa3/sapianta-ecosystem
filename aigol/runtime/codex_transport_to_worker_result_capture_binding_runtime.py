"""Bind one successful G31 Codex transport receipt to canonical result capture."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

from aigol.runtime import worker_result_capture_runtime as result_capture
from aigol.runtime.codex_worker_activation_binding_runtime import (
    ACTIVATION_TIMEOUT_SECONDS,
    CODEX_EXECUTABLE,
    reconstruct_codex_worker_activation_binding,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, verify_replay_hash
from sapianta_system.runtime.codex_execution_adapter.governed_codex_execution_dispatch import (
    MAX_CAPTURE_CHARS,
)


RUNTIME_VERSION = "G31_18_CODEX_TRANSPORT_TO_WORKER_RESULT_CAPTURE_BINDING_V1"
CAPTURED_BY = "PLATFORM_CORE_G31_CODEX_RESULT_CAPTURE_BINDING"
SUCCESS = "G31_CODEX_SEMANTIC_WORKER_RESULT_CAPTURED"
FAILED_CLOSED = "G31_CODEX_SEMANTIC_WORKER_RESULT_CAPTURE_FAILED_CLOSED"
RESULT_TRUTH_FIELDS = (
    "worker_process_started", "subprocess_invoked", "transport_receipt_successful",
    "authentic_worker_output_present", "semantic_worker_result_captured", "provider_invoked",
    "additional_worker_process_started", "result_validated", "result_accepted",
    "repository_mutated", "commit_created", "deployed", "released",
)


def capture_successful_codex_worker_result(
    *,
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
    captured_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture authentic successful stdout once; never validate or accept it."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    try:
        if not destination.is_relative_to(root):
            raise FailClosedRuntimeError("G31 result capture destination is cross-session")
        _ensure_destination_available(destination)
        binding = reconstruct_codex_worker_activation_binding(
            activation_capture=activation_capture,
            governed_execution_capture=governed_execution_capture,
            execution_candidate_capture=execution_candidate_capture,
            session_root=root,
            workspace=workspace,
        )
        output_text = _validate_successful_transport(binding, activation_capture)
        invocation = binding["lineage"]["invocation"]
        worker_output = _worker_output(
            invocation=invocation,
            binding=binding,
            output_text=output_text,
            captured_at=captured_at,
        )
        _reject_receipt_or_output_reuse(
            root, worker_output["payload"]["transport_receipt_id"],
            replay_hash(worker_output["payload"]),
        )
        capture = result_capture.capture_worker_result(
            worker_result_capture_id=(
                f"{invocation['worker_invocation_id']}:"
                f"{binding['transport_receipt']['receipt_id']}:RESULT-CAPTURE"
            ),
            worker_invocation_artifact=invocation,
            worker_invocation_replay_reference=binding["lineage"]["invocation_replay_reference"],
            worker_output=worker_output,
            captured_by=CAPTURED_BY,
            captured_at=_required(captured_at, "captured_at"),
            replay_dir=destination,
        )
        if capture.get("result_capture_status") != result_capture.WORKER_RESULT_CAPTURED:
            raise FailClosedRuntimeError(
                f"canonical Worker result capture rejected output: {capture.get('failure_reason')}"
            )
        reconstructed = result_capture.reconstruct_worker_result_capture_replay(destination)
        if reconstructed.get("worker_output_hash") != worker_output["artifact_hash"]:
            raise FailClosedRuntimeError("canonical result-capture output hash mismatch")
        return {
            **deepcopy(capture),
            "runtime_version": RUNTIME_VERSION,
            "g31_result_capture_status": SUCCESS,
            "semantic_worker_output_artifact": deepcopy(worker_output),
            "activation_replay_reference": binding["activation_replay_reference"],
            "activation_replay_hash": binding["activation_replay_hash"],
            "transport_receipt_id": binding["transport_receipt"]["receipt_id"],
            "transport_receipt_successful": True,
            "authentic_worker_output_present": True,
            "semantic_worker_result_captured": True,
            **_success_truth(),
        }
    except Exception as exc:
        return _failed_capture(str(exc), activation_capture)


def reconstruct_codex_worker_result_capture_binding(
    *,
    binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Reconstruct canonical capture and rebind it to supplied authentic transport bytes."""

    binding = reconstruct_codex_worker_activation_binding(
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    replay_path = Path(binding_capture.get("worker_result_capture_replay_reference", "")).resolve()
    root = Path(session_root).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("G31 result capture Replay is cross-session")
    reconstructed = result_capture.reconstruct_worker_result_capture_replay(replay_path)
    worker_output = binding_capture.get("semantic_worker_output_artifact")
    _verify_artifact(worker_output)
    capture_wrapper = load_json(replay_path / "002_result_capture_artifact_recorded.json")
    verify_replay_hash(capture_wrapper)
    capture_artifact = capture_wrapper.get("artifact") or {}
    checks = (
        binding_capture.get("g31_result_capture_status") == SUCCESS,
        reconstructed.get("result_capture_status") == result_capture.WORKER_RESULT_CAPTURED,
        reconstructed.get("worker_output_hash") == worker_output["artifact_hash"],
        capture_artifact.get("worker_output_payload_hash") == replay_hash(worker_output["payload"]),
        worker_output["payload"].get("activation_replay_hash") == binding["activation_replay_hash"],
        worker_output["payload"].get("transport_receipt_id")
        == binding["transport_receipt"]["receipt_id"],
        worker_output["payload"].get("semantic_output_sha256")
        == binding["transport_receipt"]["stdout_hash"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("G31 transport-to-result capture continuity mismatch")
    return {
        "g31_result_capture_status": SUCCESS,
        "worker_result_capture_id": reconstructed["worker_result_capture_id"],
        "worker_output_hash": worker_output["artifact_hash"],
        "worker_output_payload_hash": replay_hash(worker_output["payload"]),
        "activation_replay_hash": binding["activation_replay_hash"],
        "transport_receipt_id": binding["transport_receipt"]["receipt_id"],
        "replay_artifact_count": reconstructed["replay_artifact_count"],
        **_success_truth(),
    }


def render_codex_worker_result_capture(capture: dict[str, Any]) -> str:
    if capture.get("g31_result_capture_status") != SUCCESS:
        return "\n".join((
            "CODEX Semantic Worker Result Capture",
            "Capture Status: FAILED_CLOSED",
            f"Reason: {capture.get('failure_reason')}",
            "No semantic Worker result was captured, validated, or accepted.",
        ))
    return "\n".join((
        "CODEX Semantic Worker Result Capture",
        "Capture Status: WORKER_RESULT_CAPTURED",
        f"Transport Receipt: {capture.get('transport_receipt_id')}",
        f"Replay Reference: {capture.get('worker_result_capture_replay_reference')}",
        "Authentic bounded stdout was captured; validation and acceptance remain pending.",
    ))


def _validate_successful_transport(binding: dict[str, Any], activation: dict[str, Any]) -> str:
    receipt = binding["transport_receipt"]
    dispatch = binding["bounded_dispatch"]
    request = binding["codex_execution_request"]
    truth = binding["activation_truth"]
    metadata = dispatch.get("metadata") or {}
    prompt = request.get("handoff_package", {}).get("codex_prompt")
    checks = (
        activation.get("activation_status") == "EXECUTION_ACCEPTED",
        receipt.get("execution_status") == "EXECUTION_ACCEPTED",
        receipt.get("closure", {}).get("state") == "EXECUTION_ACCEPTED",
        dispatch.get("execution_status") == "EXECUTION_ACCEPTED",
        dispatch.get("returncode") == 0,
        dispatch.get("timed_out") is False,
        truth.get("process_start_count") == 1,
        truth.get("worker_process_started") is True,
        truth.get("subprocess_invoked") is True,
        truth.get("fixed_codex_exec_command_used") is True,
        truth.get("provider_invoked") is False,
        metadata.get("args") == [CODEX_EXECUTABLE, "exec", prompt],
        metadata.get("shell") is False,
        metadata.get("timeout_seconds") == ACTIVATION_TIMEOUT_SECONDS,
        metadata.get("capture_limit_chars") == MAX_CAPTURE_CHARS,
        receipt.get("validation_outcome", {}).get("valid") is True,
    )
    if not all(checks):
        raise FailClosedRuntimeError("Codex transport is not an authentic successful process receipt")
    output = dispatch.get("stdout")
    if not isinstance(output, str) or not output.strip():
        raise FailClosedRuntimeError("successful Codex transport output is empty")
    encoded = output.encode("utf-8")
    if len(output) >= MAX_CAPTURE_CHARS or len(encoded) >= MAX_CAPTURE_CHARS:
        raise FailClosedRuntimeError("Codex transport output is unusably truncated or outside bounds")
    if sha256(encoded).hexdigest() != receipt.get("stdout_hash"):
        raise FailClosedRuntimeError("Codex transport output hash mismatch")
    return output


def _worker_output(*, invocation: dict[str, Any], binding: dict[str, Any], output_text: str, captured_at: str) -> dict[str, Any]:
    receipt = binding["transport_receipt"]
    request = binding["codex_execution_request"]
    encoded = output_text.encode("utf-8")
    payload = {
        "semantic_output": output_text,
        "semantic_output_encoding": "utf-8",
        "semantic_output_byte_length": len(encoded),
        "semantic_output_sha256": sha256(encoded).hexdigest(),
        "transport_stdout_hash": receipt["stdout_hash"],
        "transport_stderr_hash": receipt["stderr_hash"],
        "transport_receipt_id": receipt["receipt_id"],
        "transport_receipt_replay_identity": receipt["replay_identity"],
        "activation_replay_reference": binding["activation_replay_reference"],
        "activation_replay_hash": binding["activation_replay_hash"],
        "codex_execution_request_id": request["codex_execution_request_id"],
        "codex_execution_request_replay_identity": request["replay_identity"],
        "stderr_is_transport_diagnostic_only": True,
    }
    output = {
        "worker_output_id": f"{invocation['worker_invocation_id']}:{receipt['receipt_id']}:WORKER-OUTPUT",
        "worker_id": invocation["worker_id"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "authorization_reference": invocation["authorization_reference"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "chain_id": invocation["chain_id"],
        "produced_outputs": deepcopy(invocation["allowed_outputs"]),
        "operations": ["CAPTURE_WORKER_OUTPUT"],
        "payload": payload,
        "created_at": _required(captured_at, "captured_at"),
        "replay_visible": True,
    }
    output["artifact_hash"] = replay_hash(output)
    return output


def _reject_receipt_or_output_reuse(root: Path, receipt_id: str, payload_hash: str) -> None:
    for path in root.rglob("002_result_capture_artifact_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        artifact = wrapper.get("artifact") or {}
        if artifact.get("worker_output_payload_hash") == payload_hash:
            raise FailClosedRuntimeError("Codex transport receipt or output was already captured")
        evidence_path = path.parent / "000_result_capture_evidence_recorded.json"
        if receipt_id in evidence_path.read_text(encoding="utf-8"):
            raise FailClosedRuntimeError("Codex transport receipt was already captured")


def _ensure_destination_available(root: Path) -> None:
    for index, step in enumerate(result_capture.REPLAY_STEPS):
        if (root / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("G31 result capture Replay destination already exists")


def _success_truth() -> dict[str, bool]:
    return {
        "worker_process_started": True,
        "subprocess_invoked": True,
        "provider_invoked": False,
        "additional_worker_process_started": False,
        "result_validated": False,
        "result_accepted": False,
        "repository_mutated": False,
        "commit_created": False,
        "deployed": False,
        "released": False,
    }


def _failed_capture(reason: str, activation: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "g31_result_capture_status": FAILED_CLOSED,
        "result_capture_status": result_capture.FAILED_CLOSED,
        "failure_reason": reason,
        "worker_process_started": activation.get("worker_process_started") is True,
        "subprocess_invoked": activation.get("subprocess_invoked") is True,
        "transport_receipt_successful": False,
        "authentic_worker_output_present": False,
        "semantic_worker_result_captured": False,
        "provider_invoked": False,
        "additional_worker_process_started": False,
        "result_validated": False,
        "result_accepted": False,
        "repository_mutated": False,
        "commit_created": False,
        "deployed": False,
        "released": False,
    }


def _verify_artifact(artifact: Any) -> None:
    if not isinstance(artifact, dict) or not isinstance(artifact.get("artifact_hash"), str):
        raise FailClosedRuntimeError("G31 semantic Worker output artifact is invalid")
    value = deepcopy(artifact)
    actual = value.pop("artifact_hash")
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("G31 semantic Worker output artifact hash mismatch")


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G31 result capture requires {field}")
    return value.strip()
