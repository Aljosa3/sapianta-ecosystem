"""Replay-visible Worker result capture runtime for the current AiGOL execution chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOKED,
    reconstruct_worker_invocation_replay,
)


AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION = "AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_V1"
WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1"
WORKER_RESULT_CAPTURED = "WORKER_RESULT_CAPTURED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "result_capture_evidence_recorded",
    "result_capture_classification_recorded",
    "result_capture_artifact_recorded",
    "result_capture_result_recorded",
)

FORBIDDEN_OUTPUT_FIELDS = frozenset(
    {
        "approval_created",
        "approval_decision",
        "authorization_decision",
        "governance_mutated",
        "replay_mutated",
        "result_validated",
        "semantic_validation",
        "post_execution_replay_reviewed",
        "terminated",
        "credentials",
        "api_key",
        "secret",
    }
)


def capture_worker_result(
    *,
    worker_result_capture_id: str,
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    worker_output: dict[str, Any],
    captured_by: str,
    captured_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture Worker output without semantic validation, replay review, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_invocation_lineage(Path(worker_invocation_replay_reference), worker_invocation_artifact)
        invocation = lineage["invocation"]
        output = _validate_worker_output(worker_output, invocation)
        evidence = _evidence_artifact(
            worker_result_capture_id=worker_result_capture_id,
            invocation=invocation,
            lineage=lineage,
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            worker_output=output,
            captured_at=captured_at,
        )
        classification = _classification_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            invocation=invocation,
            worker_output=output,
            captured_at=captured_at,
        )
        capture_artifact = _result_capture_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            classification=classification,
            invocation=invocation,
            worker_output=output,
            captured_by=captured_by,
            captured_at=captured_at,
        )
        result = _result_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            classification=classification,
            capture_artifact=capture_artifact,
            captured_at=captured_at,
            status=WORKER_RESULT_CAPTURED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], capture_artifact)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, capture_artifact, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_result_capture_id=worker_result_capture_id,
            worker_invocation_reference=(
                worker_invocation_artifact.get("worker_invocation_id")
                if isinstance(worker_invocation_artifact, dict)
                else None
            ),
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            captured_at=captured_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_worker_result_capture_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker result capture replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker result capture replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result capture replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker result capture replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    capture_artifact = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("result_capture_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay evidence lineage mismatch")
    if capture_artifact.get("result_capture_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay classification lineage mismatch")
    if result.get("worker_result_capture_hash") != capture_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], capture_artifact["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker result capture replay chain mismatch")
    if evidence["worker_invocation_hash"] != capture_artifact["worker_invocation_hash"]:
        raise FailClosedRuntimeError("worker result capture replay invocation lineage mismatch")
    _validate_result_capture_artifact(capture_artifact)
    _load_invocation_lineage(
        Path(evidence["worker_invocation_replay_reference"]),
        None,
        result_capture=capture_artifact,
    )
    return {
        "worker_result_capture_id": capture_artifact["worker_result_capture_id"],
        "result_capture_status": result["result_capture_status"],
        "worker_invocation_reference": capture_artifact["worker_invocation_reference"],
        "worker_dispatch_reference": capture_artifact["worker_dispatch_reference"],
        "worker_assignment_reference": capture_artifact["worker_assignment_reference"],
        "authorization_reference": capture_artifact["authorization_reference"],
        "execution_packet_reference": capture_artifact["execution_packet_reference"],
        "worker_id": capture_artifact["worker_id"],
        "worker_family": capture_artifact["worker_family"],
        "worker_role": capture_artifact["worker_role"],
        "chain_id": capture_artifact["chain_id"],
        "produced_outputs": deepcopy(capture_artifact["produced_outputs"]),
        "operations": deepcopy(capture_artifact["operations"]),
        "worker_output_hash": capture_artifact["worker_output_hash"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_capture_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_worker_result_capture_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Result Capture",
        "",
        f"Result Capture Status: {capture.get('result_capture_status')}",
        f"Worker Result Capture Reference: {capture.get('worker_result_capture_reference')}",
        f"Worker Invocation Reference: {capture.get('worker_invocation_reference')}",
        f"Captured Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('worker_result_capture_replay_reference')}",
        "",
        "No semantic validation yet.",
        "No replay review yet.",
        "No termination yet.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def default_worker_output_for_invocation(invocation: dict[str, Any], *, captured_at: str) -> dict[str, Any]:
    """Return deterministic in-memory Worker output for CLI continuity."""

    _validate_invocation_artifact(invocation)
    produced_outputs = deepcopy(invocation["allowed_outputs"])
    output = {
        "worker_output_id": f"{invocation['worker_invocation_id']}:WORKER-OUTPUT",
        "worker_id": invocation["worker_id"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "authorization_reference": invocation["authorization_reference"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "chain_id": invocation["chain_id"],
        "produced_outputs": produced_outputs,
        "operations": ["CAPTURE_WORKER_OUTPUT"],
        "payload": {
            "capture_summary": "Worker output captured for governed result capture only.",
            "produced_output_count": len(produced_outputs),
        },
        "created_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
    }
    output["artifact_hash"] = replay_hash(output)
    return output


def _load_invocation_lineage(
    invocation_replay_path: Path,
    provided_invocation: dict[str, Any] | None,
    *,
    result_capture: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    reconstructed = reconstruct_worker_invocation_replay(invocation_replay_path)
    if reconstructed.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation invalid")
    wrappers = []
    expected = (
        (0, "invocation_evidence_recorded"),
        (1, "invocation_classification_recorded"),
        (2, "invocation_artifact_recorded"),
        (3, "invocation_result_recorded"),
    )
    for index, step in expected:
        wrapper = load_json(invocation_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result capture failed closed: invocation replay corruption")
        _verify_artifact_hash(artifact, "worker invocation lineage artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    invocation = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    _validate_invocation_artifact(invocation)
    if provided_invocation is not None:
        _verify_artifact_hash(provided_invocation, "provided worker invocation artifact")
        if provided_invocation.get("worker_invocation_id") != invocation["worker_invocation_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
        if provided_invocation.get("artifact_hash") != invocation["artifact_hash"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    if result_capture is not None:
        if result_capture.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
        if result_capture.get("worker_invocation_hash") != invocation["artifact_hash"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    checks = {
        "invocation_lineage": result["worker_invocation_hash"] == invocation["artifact_hash"],
        "dispatch_lineage": invocation["worker_dispatch_hash"] == evidence["worker_dispatch_hash"],
        "assignment_lineage": invocation["worker_assignment_hash"] == evidence["worker_assignment_hash"],
        "authorization_lineage": invocation["authorization_hash"] == evidence["authorization_hash"],
        "execution_packet_lineage": invocation["execution_packet_hash"] == evidence["execution_packet_hash"],
        "worker_identity_continuity": invocation["worker_id"] == evidence["worker_id"]
        and invocation["worker_hash"] == evidence["worker_hash"],
        "chain_continuity": invocation["chain_id"] == evidence["chain_id"],
        "replay_continuity": reconstructed["invocation_status"] == WORKER_INVOKED,
        "authority_continuity": _invocation_authority_continuity(invocation),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker result capture failed closed: lineage continuity invalid")
    return {
        "invocation_evidence": evidence,
        "invocation_classification": classification,
        "invocation": invocation,
        "invocation_result": result,
        "lineage_checks": checks,
    }


def _validate_invocation_artifact(invocation: dict[str, Any]) -> None:
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid invocation artifact")
    if invocation.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation invalid")
    for field, expected in _pre_capture_boundary_flags().items():
        if invocation.get(field) is not expected:
            raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if not _string_list(invocation.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker result capture failed closed: allowed outputs missing")
    if not _string_list(invocation.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operations missing")
    for field in (
        "worker_invocation_id",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
    ):
        _require_string(invocation.get(field), field)


def _validate_worker_output(worker_output: dict[str, Any], invocation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(worker_output, dict):
        raise FailClosedRuntimeError("worker result capture failed closed: worker output is required")
    output = deepcopy(worker_output)
    _verify_artifact_hash(output, "worker output artifact")
    if FORBIDDEN_OUTPUT_FIELDS.intersection(output):
        raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if output.get("worker_id") != invocation["worker_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_family") != invocation["worker_family"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_role") != invocation["worker_role"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    if output.get("worker_dispatch_reference") != invocation["worker_dispatch_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: dispatch mismatch")
    if output.get("authorization_reference") != invocation["authorization_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: authorization mismatch")
    if output.get("execution_packet_reference") != invocation["execution_packet_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: packet mismatch")
    if output.get("chain_id") != invocation["chain_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: chain mismatch")
    produced_outputs = output.get("produced_outputs")
    if not _string_list(produced_outputs):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    allowed_outputs = set(invocation["allowed_outputs"])
    if not set(produced_outputs).issubset(allowed_outputs):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    operations = output.get("operations")
    if not _string_list(operations):
        raise FailClosedRuntimeError("worker result capture failed closed: operations are required")
    forbidden = set(invocation["forbidden_operations"])
    if forbidden.intersection(operations):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operation detected")
    if output.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker result capture failed closed: replay visibility missing")
    _require_string(output.get("worker_output_id"), "worker_output_id")
    return output


def _evidence_artifact(
    *,
    worker_result_capture_id: str,
    invocation: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    worker_invocation_replay_reference: str,
    worker_output: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_evidence_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:EVIDENCE",
        "chain_id": invocation["chain_id"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_invocation_replay_reference": _require_string(
            worker_invocation_replay_reference,
            "worker_invocation_replay_reference",
        ),
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_invocation_request_reference": invocation["worker_invocation_request_reference"],
        "worker_invocation_request_hash": invocation["worker_invocation_request_hash"],
        "authorization_reference": invocation["authorization_reference"],
        "authorization_hash": invocation["authorization_hash"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "worker_id": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "produced_outputs": deepcopy(worker_output["produced_outputs"]),
        "operations": deepcopy(worker_output["operations"]),
        "worker_output_reference": worker_output["worker_output_id"],
        "worker_output_hash": worker_output["artifact_hash"],
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    invocation: dict[str, Any],
    worker_output: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_classification_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:CLASSIFICATION",
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "chain_id": invocation["chain_id"],
        "worker_identity_continuous": evidence["lineage_checks"]["worker_identity_continuity"],
        "invocation_lineage_continuous": evidence["lineage_checks"]["invocation_lineage"],
        "dispatch_lineage_continuous": evidence["lineage_checks"]["dispatch_lineage"],
        "assignment_lineage_continuous": evidence["lineage_checks"]["assignment_lineage"],
        "authorization_lineage_continuous": evidence["lineage_checks"]["authorization_lineage"],
        "execution_packet_lineage_continuous": evidence["lineage_checks"]["execution_packet_lineage"],
        "replay_continuous": evidence["lineage_checks"]["replay_continuity"],
        "authority_continuous": evidence["lineage_checks"]["authority_continuity"],
        "chain_continuous": evidence["lineage_checks"]["chain_continuity"],
        "output_within_allowed_scope": set(worker_output["produced_outputs"]).issubset(set(invocation["allowed_outputs"])),
        "forbidden_operations_absent": not set(worker_output["operations"]).intersection(invocation["forbidden_operations"]),
        "worker_scope_bound": worker_output["worker_id"] == invocation["worker_id"],
        "packet_scope_bound": worker_output["execution_packet_reference"] == invocation["execution_packet_reference"],
        "classification_status": "WORKER_RESULT_CAPTURE_SCOPE_CLASSIFIED",
        "classified_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(),
    }
    checks = (
        artifact["worker_identity_continuous"],
        artifact["invocation_lineage_continuous"],
        artifact["dispatch_lineage_continuous"],
        artifact["assignment_lineage_continuous"],
        artifact["authorization_lineage_continuous"],
        artifact["execution_packet_lineage_continuous"],
        artifact["replay_continuous"],
        artifact["authority_continuous"],
        artifact["chain_continuous"],
        artifact["output_within_allowed_scope"],
        artifact["forbidden_operations_absent"],
        artifact["worker_scope_bound"],
        artifact["packet_scope_bound"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker result capture failed closed: capture eligibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result_capture_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    invocation: dict[str, Any],
    worker_output: dict[str, Any],
    captured_by: str,
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "worker_result_capture_id": _require_string(worker_result_capture_id, "worker_result_capture_id"),
        "result_capture_status": WORKER_RESULT_CAPTURED,
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "result_capture_classification_reference": classification["result_capture_classification_id"],
        "result_capture_classification_hash": classification["artifact_hash"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_invocation_request_reference": invocation["worker_invocation_request_reference"],
        "worker_invocation_request_hash": invocation["worker_invocation_request_hash"],
        "authorization_reference": invocation["authorization_reference"],
        "authorization_hash": invocation["authorization_hash"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "worker_id": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "produced_outputs": deepcopy(worker_output["produced_outputs"]),
        "operations": deepcopy(worker_output["operations"]),
        "worker_output_reference": worker_output["worker_output_id"],
        "worker_output_hash": worker_output["artifact_hash"],
        "worker_output_payload_hash": replay_hash(worker_output["payload"]),
        "captured_by": _require_string(captured_by, "captured_by"),
        "captured_at": _require_string(captured_at, "captured_at"),
        "chain_id": invocation["chain_id"],
        "replay_reference": invocation["replay_reference"],
        "replay_visible": True,
        **_post_capture_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_result_capture_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    capture_artifact: dict[str, Any],
    captured_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_result_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:RESULT",
        "result_capture_status": status,
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "result_capture_classification_reference": classification["result_capture_classification_id"],
        "result_capture_classification_hash": classification["artifact_hash"],
        "worker_result_capture_reference": capture_artifact["worker_result_capture_id"],
        "worker_result_capture_hash": capture_artifact["artifact_hash"],
        "worker_invocation_reference": capture_artifact["worker_invocation_reference"],
        "worker_invocation_hash": capture_artifact["worker_invocation_hash"],
        "worker_dispatch_reference": capture_artifact["worker_dispatch_reference"],
        "worker_reference": capture_artifact["worker_id"],
        "worker_hash": capture_artifact["worker_hash"],
        "chain_id": capture_artifact["chain_id"],
        "completed_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_result_capture_id: str,
    worker_invocation_reference: str | None,
    worker_invocation_replay_reference: str,
    captured_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_result_id": f"{worker_result_capture_id}:RESULT",
        "result_capture_status": FAILED_CLOSED,
        "result_capture_evidence_reference": None,
        "result_capture_evidence_hash": None,
        "result_capture_classification_reference": None,
        "result_capture_classification_hash": None,
        "worker_result_capture_reference": None,
        "worker_result_capture_hash": None,
        "worker_invocation_reference": worker_invocation_reference,
        "worker_invocation_hash": None,
        "worker_invocation_replay_reference": worker_invocation_replay_reference,
        "worker_dispatch_reference": None,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": captured_at,
        "replay_visible": True,
        **_pre_capture_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    capture_artifact: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "result_capture_evidence_artifact": deepcopy(evidence),
            "result_capture_classification_artifact": deepcopy(classification),
            "worker_result_capture_artifact": deepcopy(capture_artifact),
            "result_capture_result_artifact": deepcopy(result),
            "worker_result_capture_reference": capture_artifact.get("worker_result_capture_id")
            if capture_artifact
            else None,
            "worker_invocation_reference": capture_artifact.get("worker_invocation_reference")
            if capture_artifact
            else None,
            "worker_dispatch_reference": capture_artifact.get("worker_dispatch_reference")
            if capture_artifact
            else None,
            "worker_id": capture_artifact.get("worker_id") if capture_artifact else None,
            "worker_family": capture_artifact.get("worker_family") if capture_artifact else None,
            "worker_role": capture_artifact.get("worker_role") if capture_artifact else None,
            "worker_result_capture_replay_reference": str(replay_path),
            "fail_closed": result["result_capture_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_result_capture_capture_hash"] = replay_hash(capture)
    return capture


def _validate_result_capture_artifact(capture_artifact: dict[str, Any]) -> None:
    if capture_artifact.get("artifact_type") != WORKER_RESULT_CAPTURE_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid result capture artifact")
    if capture_artifact.get("result_capture_status") != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid result capture status")
    for field, expected in _post_capture_boundary_flags().items():
        if capture_artifact.get(field) is not expected:
            raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if not set(capture_artifact.get("produced_outputs", [])).issubset(set(capture_artifact.get("allowed_outputs", []))):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    if set(capture_artifact.get("operations", [])).intersection(capture_artifact.get("forbidden_operations", [])):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operation detected")
    if not _string_list(capture_artifact.get("validation_requirements")):
        raise FailClosedRuntimeError("worker result capture failed closed: validation requirements missing")
    for field in (
        "worker_result_capture_id",
        "worker_invocation_reference",
        "worker_invocation_hash",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "worker_output_reference",
        "worker_output_hash",
        "chain_id",
        "captured_by",
        "captured_at",
    ):
        _require_string(capture_artifact.get(field), field)


def _invocation_authority_continuity(invocation: dict[str, Any]) -> bool:
    return (
        invocation.get("approval_created") is False
        and invocation.get("worker_assigned") is True
        and invocation.get("worker_dispatched") is True
        and invocation.get("dispatch_requested") is True
        and invocation.get("worker_invoked") is True
        and invocation.get("execution_started") is False
        and invocation.get("result_created") is False
        and invocation.get("result_validated") is False
        and invocation.get("post_execution_replay_reviewed") is False
        and invocation.get("terminated") is False
        and invocation.get("governance_mutated") is False
        and invocation.get("replay_mutated") is False
    )


def _pre_capture_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": False,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_capture_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": True,
        "worker_result_captured": True,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker result capture replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker result capture artifact")
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
        raise FailClosedRuntimeError("worker result capture replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker result capture replay hash mismatch")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker result capture failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker result capture failed closed: {exc}"
