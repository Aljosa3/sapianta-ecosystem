"""Replay-visible Worker invocation runtime for the current AiGOL execution chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_assignment_runtime import WORKER_ASSIGNED
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    WORKER_DISPATCH_ARTIFACT_V1,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_runtime import ASSIGNED


AIGOL_WORKER_INVOCATION_RUNTIME_VERSION = "AIGOL_WORKER_INVOCATION_RUNTIME_V1"
WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1 = "WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1"
WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1 = "WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1"
WORKER_INVOCATION_ARTIFACT_V1 = "WORKER_INVOCATION_ARTIFACT_V1"
WORKER_INVOCATION_RESULT_ARTIFACT_V1 = "WORKER_INVOCATION_RESULT_ARTIFACT_V1"
WORKER_INVOKED = "WORKER_INVOKED"
INVOKED = WORKER_INVOKED
WORKER_INVOCATION_VALIDATED = "WORKER_INVOCATION_VALIDATED"
WORKER_INVOCATION_RETURNED = "WORKER_INVOCATION_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "invocation_evidence_recorded",
    "invocation_classification_recorded",
    "invocation_artifact_recorded",
    "invocation_result_recorded",
)


def invoke_dispatched_worker(
    *,
    worker_invocation_id: str,
    worker_dispatch_artifact: dict[str, Any],
    worker_dispatch_replay_reference: str,
    invoked_by: str,
    invoked_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Invoke one dispatched Worker without result validation, replay review, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_dispatch_lineage(Path(worker_dispatch_replay_reference), worker_dispatch_artifact)
        dispatch = lineage["dispatch"]
        evidence = _evidence_artifact(
            worker_invocation_id=worker_invocation_id,
            dispatch=dispatch,
            lineage=lineage,
            worker_dispatch_replay_reference=worker_dispatch_replay_reference,
            invoked_at=invoked_at,
        )
        classification = _classification_artifact(
            worker_invocation_id=worker_invocation_id,
            evidence=evidence,
            dispatch=dispatch,
            invoked_at=invoked_at,
        )
        invocation = _invocation_artifact(
            worker_invocation_id=worker_invocation_id,
            evidence=evidence,
            classification=classification,
            dispatch=dispatch,
            invoked_by=invoked_by,
            invoked_at=invoked_at,
        )
        result = _result_artifact(
            worker_invocation_id=worker_invocation_id,
            evidence=evidence,
            classification=classification,
            invocation=invocation,
            invoked_at=invoked_at,
            status=WORKER_INVOKED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], invocation)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, invocation, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_invocation_id=worker_invocation_id,
            worker_dispatch_reference=(
                worker_dispatch_artifact.get("worker_dispatch_id")
                if isinstance(worker_dispatch_artifact, dict)
                else None
            ),
            worker_dispatch_replay_reference=worker_dispatch_replay_reference,
            invoked_at=invoked_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def invoke_worker(**kwargs: Any) -> dict[str, Any]:
    """Compatibility wrapper for current-chain and legacy invocation callers."""

    if "worker_dispatch_artifact" not in kwargs and "dispatch_artifact" in kwargs:
        return _invoke_worker_legacy(**kwargs)
    return invoke_dispatched_worker(**kwargs)


def _invoke_worker_legacy(
    *,
    worker_invocation_id: str,
    dispatch_artifact: dict[str, Any],
    dispatch_replay: dict[str, Any],
    worker_assignment_artifact: dict[str, Any],
    canonical_chain_id: str,
    invocation_parameters: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Preserve older DISPATCH_ARTIFACT_V1 callers without changing the new runtime contract."""

    from aigol.runtime.dispatch_runtime import DISPATCH_ARTIFACT_V1, DISPATCH_RETURNED, DISPATCHED
    from aigol.runtime.worker_runtime import AVAILABLE, WORKER_ASSIGNMENT_ARTIFACT_V1

    replay_path = Path(replay_dir)
    for index, step in enumerate(("worker_invocation_validated", "worker_invocation_returned")):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")

    dispatch = deepcopy(dispatch_artifact)
    dispatch_returned = deepcopy(dispatch_replay)
    assignment = deepcopy(worker_assignment_artifact)
    _verify_artifact_hash(dispatch, "dispatch artifact")
    _verify_artifact_hash(dispatch_returned, "dispatch replay artifact")
    _verify_artifact_hash(assignment, "worker assignment artifact")
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    if dispatch.get("artifact_type") != DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch artifact")
    if dispatch.get("dispatch_status") != DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch status")
    if dispatch.get("canonical_chain_id") != chain_id:
        raise FailClosedRuntimeError("worker invocation failed closed: chain mismatch")
    if dispatch_returned.get("event_type") != DISPATCH_RETURNED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch replay event")
    if dispatch_returned.get("dispatch_reference") != dispatch["dispatch_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay reference mismatch")
    if dispatch_returned.get("dispatch_hash") != dispatch["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay hash mismatch")
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid worker assignment artifact")
    if assignment.get("worker_assignment_id") != dispatch["worker_assignment_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment reference mismatch")
    if assignment.get("artifact_hash") != dispatch["worker_assignment_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment hash mismatch")
    if assignment.get("worker_state_before") != AVAILABLE or assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if assignment.get("worker_id") != dispatch["worker_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if assignment.get("worker_hash") != dispatch["worker_hash"]:
        raise FailClosedRuntimeError("worker invocation failed closed: worker mismatch")
    if assignment.get("canonical_chain_id") != chain_id:
        raise FailClosedRuntimeError("worker invocation failed closed: chain mismatch")
    if not isinstance(invocation_parameters, dict) or not invocation_parameters:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation_parameters are required")
    if invocation_parameters.get("execution_request_reference") != dispatch["execution_request_reference"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if invocation_parameters.get("request_type") != dispatch["request_type"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")
    if invocation_parameters.get("capability_id") != dispatch["capability_id"]:
        raise FailClosedRuntimeError("worker invocation failed closed: invocation parameter validation failure")

    invoked_by_token = _require_string(invoked_by, "invoked_by").strip().upper().replace("-", "_")
    invocation = {
        "artifact_type": WORKER_INVOCATION_ARTIFACT_V1,
        "worker_invocation_runtime_version": "WORKER_INVOCATION_RUNTIME_V1",
        "worker_invocation_id": _require_string(worker_invocation_id, "worker_invocation_id"),
        "canonical_chain_id": chain_id,
        "dispatch_reference": dispatch["dispatch_id"],
        "dispatch_hash": dispatch["artifact_hash"],
        "dispatch_replay_hash": dispatch_returned["artifact_hash"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_reference": dispatch["worker_reference"],
        "worker_hash": dispatch["worker_hash"],
        "readiness_reference": dispatch["readiness_reference"],
        "execution_request_reference": dispatch["execution_request_reference"],
        "execution_request_hash": dispatch["execution_request_hash"],
        "invoked_by": invoked_by_token,
        "invoked_at": _require_string(invoked_at, "invoked_at"),
        "invocation_status": INVOKED,
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_before_invocation": assignment["worker_state_after"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "invocation_parameters": deepcopy(invocation_parameters),
        "invocation_parameters_hash": replay_hash(invocation_parameters),
        "validation_results": (
            "dispatch_valid",
            "dispatch_replay_continuous",
            "worker_identity_verified",
            "worker_assignment_valid",
            "canonical_chain_continuous",
            "invocation_parameters_valid",
            "provider_authority_absent",
            "execution_absent",
            "completion_absent",
        ),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_invoked": False,
        "execution_started": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "scope_expansion": False,
    }
    invocation["artifact_hash"] = replay_hash(invocation)
    returned = {
        "event_type": WORKER_INVOCATION_RETURNED,
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "canonical_chain_id": invocation["canonical_chain_id"],
        "dispatch_reference": invocation["dispatch_reference"],
        "dispatch_hash": invocation["dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_reference": invocation["worker_reference"],
        "worker_hash": invocation["worker_hash"],
        "execution_request_reference": invocation["execution_request_reference"],
        "invocation_status": invocation["invocation_status"],
        "replay_reference": invocation["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_self_invoked": False,
        "execution_started": False,
        "execution_performed": False,
        "completion_recorded": False,
        "automatic_authorization": False,
        "scope_expansion": False,
        "reconstruction_metadata": {
            "worker_invocation_reconstructable": True,
            "dispatch_reconstructable": True,
            "worker_assignment_reconstructable": True,
            "canonical_chain_continuous": True,
            "execution_started": False,
            "execution_performed": False,
            "completion_recorded": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    _persist_legacy_step(replay_path, 0, "worker_invocation_validated", invocation)
    _persist_legacy_step(replay_path, 1, "worker_invocation_returned", returned)
    capture = {
        "worker_invocation_artifact": deepcopy(invocation),
        "worker_invocation_replay": deepcopy(returned),
    }
    capture["worker_invocation_capture_hash"] = replay_hash(capture)
    return capture


def reconstruct_worker_invocation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker invocation replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker invocation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker invocation replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    invocation = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("invocation_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation replay evidence lineage mismatch")
    if invocation.get("invocation_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation replay classification lineage mismatch")
    if result.get("worker_invocation_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation replay invocation continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], invocation["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker invocation replay chain mismatch")
    if evidence["worker_dispatch_hash"] != invocation["worker_dispatch_hash"]:
        raise FailClosedRuntimeError("worker invocation replay dispatch lineage mismatch")
    _validate_invocation_artifact(invocation)
    _load_dispatch_lineage(Path(evidence["worker_dispatch_replay_reference"]), None, invocation=invocation)
    return {
        "worker_invocation_id": invocation["worker_invocation_id"],
        "invocation_status": result["invocation_status"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_invocation_request_reference": invocation["worker_invocation_request_reference"],
        "authorization_reference": invocation["authorization_reference"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "worker_id": invocation["worker_id"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "chain_id": invocation["chain_id"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_invocation_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_worker_invocation_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Invocation",
        "",
        f"Invocation Status: {capture.get('invocation_status')}",
        f"Worker Invocation Reference: {capture.get('worker_invocation_reference')}",
        f"Worker Dispatch Reference: {capture.get('worker_dispatch_reference')}",
        f"Invoked Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('worker_invocation_replay_reference')}",
        "",
        "No result validation yet.",
        "No replay review yet.",
        "No termination yet.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_dispatch_lineage(
    dispatch_replay_path: Path,
    provided_dispatch: dict[str, Any] | None,
    *,
    invocation: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    reconstructed = reconstruct_worker_dispatch_replay(dispatch_replay_path)
    if reconstructed.get("dispatch_status") != WORKER_DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch invalid")
    wrappers = []
    expected = (
        (0, "dispatch_evidence_recorded"),
        (1, "dispatch_classification_recorded"),
        (2, "dispatch_artifact_recorded"),
        (3, "dispatch_result_recorded"),
    )
    for index, step in expected:
        wrapper = load_json(dispatch_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation failed closed: dispatch replay corruption")
        _verify_artifact_hash(artifact, "worker dispatch lineage artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    dispatch = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    _validate_dispatch_artifact(dispatch)
    if provided_dispatch is not None:
        _verify_artifact_hash(provided_dispatch, "provided worker dispatch artifact")
        if provided_dispatch.get("worker_dispatch_id") != dispatch["worker_dispatch_id"]:
            raise FailClosedRuntimeError("worker invocation failed closed: dispatch mismatch")
        if provided_dispatch.get("artifact_hash") != dispatch["artifact_hash"]:
            raise FailClosedRuntimeError("worker invocation failed closed: dispatch mismatch")
    if invocation is not None:
        if invocation.get("worker_dispatch_reference") != dispatch["worker_dispatch_id"]:
            raise FailClosedRuntimeError("worker invocation failed closed: dispatch mismatch")
        if invocation.get("worker_dispatch_hash") != dispatch["artifact_hash"]:
            raise FailClosedRuntimeError("worker invocation failed closed: dispatch mismatch")
    checks = {
        "dispatch_lineage": result["worker_dispatch_hash"] == dispatch["artifact_hash"],
        "assignment_lineage": dispatch["worker_assignment_hash"] == evidence["worker_assignment_hash"],
        "invocation_request_lineage": dispatch["worker_invocation_request_hash"]
        == evidence["worker_invocation_request_hash"],
        "authorization_lineage": dispatch["authorization_hash"] == evidence["authorization_hash"],
        "execution_packet_lineage": dispatch["execution_packet_hash"] == evidence["execution_packet_hash"],
        "worker_identity_continuity": dispatch["worker_id"] == evidence["worker_id"]
        and dispatch["worker_hash"] == evidence["worker_hash"],
        "chain_continuity": dispatch["chain_id"] == evidence["chain_id"],
        "replay_continuity": reconstructed["dispatch_status"] == WORKER_DISPATCHED,
        "authority_continuity": _dispatch_authority_continuity(dispatch),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker invocation failed closed: lineage continuity invalid")
    return {
        "dispatch_evidence": evidence,
        "dispatch_classification": classification,
        "dispatch": dispatch,
        "dispatch_result": result,
        "lineage_checks": checks,
    }


def _validate_dispatch_artifact(dispatch: dict[str, Any]) -> None:
    if dispatch.get("artifact_type") != WORKER_DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid dispatch artifact")
    if dispatch.get("dispatch_status") != WORKER_DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch invalid")
    if dispatch.get("assignment_status_before") != WORKER_ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: assignment mismatch")
    if dispatch.get("worker_state_before_dispatch") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if dispatch.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker invocation failed closed: replay visibility missing")
    for field, expected in _pre_invocation_boundary_flags().items():
        if dispatch.get(field) is not expected:
            raise FailClosedRuntimeError("worker invocation failed closed: authority violation")
    if not _string_list(dispatch.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker invocation failed closed: allowed outputs missing")
    if not _string_list(dispatch.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker invocation failed closed: forbidden operations missing")
    for field in (
        "worker_dispatch_id",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "worker_invocation_request_reference",
        "worker_invocation_request_hash",
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
        _require_string(dispatch.get(field), field)


def _evidence_artifact(
    *,
    worker_invocation_id: str,
    dispatch: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    worker_dispatch_replay_reference: str,
    invoked_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_RUNTIME_VERSION,
        "invocation_evidence_id": f"{_require_string(worker_invocation_id, 'worker_invocation_id')}:EVIDENCE",
        "chain_id": dispatch["chain_id"],
        "worker_dispatch_reference": dispatch["worker_dispatch_id"],
        "worker_dispatch_hash": dispatch["artifact_hash"],
        "worker_dispatch_replay_reference": _require_string(
            worker_dispatch_replay_reference,
            "worker_dispatch_replay_reference",
        ),
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_invocation_request_reference": dispatch["worker_invocation_request_reference"],
        "worker_invocation_request_hash": dispatch["worker_invocation_request_hash"],
        "authorization_reference": dispatch["authorization_reference"],
        "authorization_hash": dispatch["authorization_hash"],
        "execution_packet_reference": dispatch["execution_packet_reference"],
        "execution_packet_hash": dispatch["execution_packet_hash"],
        "worker_id": dispatch["worker_id"],
        "worker_hash": dispatch["worker_hash"],
        "worker_family": dispatch["worker_family"],
        "worker_role": dispatch["worker_role"],
        "allowed_outputs": deepcopy(dispatch["allowed_outputs"]),
        "forbidden_operations": deepcopy(dispatch["forbidden_operations"]),
        "validation_requirements": deepcopy(dispatch["validation_requirements"]),
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(invoked_at, "invoked_at"),
        "replay_visible": True,
        **_post_invocation_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_invocation_id: str,
    evidence: dict[str, Any],
    dispatch: dict[str, Any],
    invoked_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_RUNTIME_VERSION,
        "invocation_classification_id": f"{_require_string(worker_invocation_id, 'worker_invocation_id')}:CLASSIFICATION",
        "invocation_evidence_reference": evidence["invocation_evidence_id"],
        "invocation_evidence_hash": evidence["artifact_hash"],
        "chain_id": dispatch["chain_id"],
        "assigned_worker_identity": dispatch["worker_id"],
        "assigned_worker_family": dispatch["worker_family"],
        "execution_packet_scope": dispatch["execution_packet_reference"],
        "allowed_outputs_compatible": evidence["allowed_outputs"] == dispatch["allowed_outputs"],
        "forbidden_operations_compatible": evidence["forbidden_operations"] == dispatch["forbidden_operations"],
        "dispatch_lineage_continuous": evidence["lineage_checks"]["dispatch_lineage"],
        "assignment_lineage_continuous": evidence["lineage_checks"]["assignment_lineage"],
        "invocation_request_lineage_continuous": evidence["lineage_checks"]["invocation_request_lineage"],
        "authorization_lineage_continuous": evidence["lineage_checks"]["authorization_lineage"],
        "execution_packet_lineage_continuous": evidence["lineage_checks"]["execution_packet_lineage"],
        "worker_identity_continuous": evidence["lineage_checks"]["worker_identity_continuity"],
        "authority_continuous": evidence["lineage_checks"]["authority_continuity"],
        "replay_continuous": evidence["lineage_checks"]["replay_continuity"],
        "classification_status": "WORKER_INVOCATION_SCOPE_CLASSIFIED",
        "classified_at": _require_string(invoked_at, "invoked_at"),
        "replay_visible": True,
        **_post_invocation_boundary_flags(),
    }
    checks = (
        artifact["allowed_outputs_compatible"],
        artifact["forbidden_operations_compatible"],
        artifact["dispatch_lineage_continuous"],
        artifact["assignment_lineage_continuous"],
        artifact["invocation_request_lineage_continuous"],
        artifact["authorization_lineage_continuous"],
        artifact["execution_packet_lineage_continuous"],
        artifact["worker_identity_continuous"],
        artifact["authority_continuous"],
        artifact["replay_continuous"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker invocation failed closed: invocation eligibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invocation_artifact(
    *,
    worker_invocation_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    dispatch: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_RUNTIME_VERSION,
        "worker_invocation_id": _require_string(worker_invocation_id, "worker_invocation_id"),
        "invocation_status": WORKER_INVOKED,
        "invocation_evidence_reference": evidence["invocation_evidence_id"],
        "invocation_evidence_hash": evidence["artifact_hash"],
        "invocation_classification_reference": classification["invocation_classification_id"],
        "invocation_classification_hash": classification["artifact_hash"],
        "worker_dispatch_reference": dispatch["worker_dispatch_id"],
        "worker_dispatch_hash": dispatch["artifact_hash"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_invocation_request_reference": dispatch["worker_invocation_request_reference"],
        "worker_invocation_request_hash": dispatch["worker_invocation_request_hash"],
        "authorization_reference": dispatch["authorization_reference"],
        "authorization_hash": dispatch["authorization_hash"],
        "execution_packet_reference": dispatch["execution_packet_reference"],
        "execution_packet_hash": dispatch["execution_packet_hash"],
        "worker_id": dispatch["worker_id"],
        "worker_hash": dispatch["worker_hash"],
        "worker_family": dispatch["worker_family"],
        "worker_role": dispatch["worker_role"],
        "allowed_outputs": deepcopy(dispatch["allowed_outputs"]),
        "forbidden_operations": deepcopy(dispatch["forbidden_operations"]),
        "validation_requirements": deepcopy(dispatch["validation_requirements"]),
        "invoked_by": _require_string(invoked_by, "invoked_by"),
        "invoked_at": _require_string(invoked_at, "invoked_at"),
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_before_invocation": dispatch["worker_state_before_dispatch"],
        "chain_id": dispatch["chain_id"],
        "replay_reference": dispatch["replay_reference"],
        "replay_visible": True,
        **_post_invocation_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_invocation_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_invocation_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    invocation: dict[str, Any],
    invoked_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_RUNTIME_VERSION,
        "invocation_result_id": f"{_require_string(worker_invocation_id, 'worker_invocation_id')}:RESULT",
        "invocation_status": status,
        "invocation_evidence_reference": evidence["invocation_evidence_id"],
        "invocation_evidence_hash": evidence["artifact_hash"],
        "invocation_classification_reference": classification["invocation_classification_id"],
        "invocation_classification_hash": classification["artifact_hash"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_reference": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "chain_id": invocation["chain_id"],
        "completed_at": _require_string(invoked_at, "invoked_at"),
        "replay_visible": True,
        **_post_invocation_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_invocation_id: str,
    worker_dispatch_reference: str | None,
    worker_dispatch_replay_reference: str,
    invoked_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_RUNTIME_VERSION,
        "invocation_result_id": f"{worker_invocation_id}:RESULT",
        "invocation_status": FAILED_CLOSED,
        "invocation_evidence_reference": None,
        "invocation_evidence_hash": None,
        "invocation_classification_reference": None,
        "invocation_classification_hash": None,
        "worker_invocation_reference": None,
        "worker_invocation_hash": None,
        "worker_dispatch_reference": worker_dispatch_reference,
        "worker_dispatch_hash": None,
        "worker_dispatch_replay_reference": worker_dispatch_replay_reference,
        "worker_assignment_reference": None,
        "worker_assignment_hash": None,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": invoked_at,
        "replay_visible": True,
        **_pre_invocation_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    invocation: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "invocation_evidence_artifact": deepcopy(evidence),
            "invocation_classification_artifact": deepcopy(classification),
            "worker_invocation_artifact": deepcopy(invocation),
            "invocation_result_artifact": deepcopy(result),
            "worker_invocation_reference": invocation.get("worker_invocation_id") if invocation else None,
            "worker_dispatch_reference": invocation.get("worker_dispatch_reference") if invocation else None,
            "worker_assignment_reference": invocation.get("worker_assignment_reference") if invocation else None,
            "worker_id": invocation.get("worker_id") if invocation else None,
            "worker_family": invocation.get("worker_family") if invocation else None,
            "worker_role": invocation.get("worker_role") if invocation else None,
            "worker_invocation_replay_reference": str(replay_path),
            "fail_closed": result["invocation_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_invocation_capture_hash"] = replay_hash(capture)
    return capture


def _validate_invocation_artifact(invocation: dict[str, Any]) -> None:
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid invocation artifact")
    if invocation.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker invocation failed closed: invalid invocation status")
    if invocation.get("dispatch_status_before") != WORKER_DISPATCHED:
        raise FailClosedRuntimeError("worker invocation failed closed: dispatch mismatch")
    if invocation.get("worker_state_before_invocation") != ASSIGNED:
        raise FailClosedRuntimeError("worker invocation failed closed: worker unavailable")
    if invocation.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker invocation failed closed: replay visibility missing")
    for field, expected in _post_invocation_boundary_flags().items():
        if invocation.get(field) is not expected:
            raise FailClosedRuntimeError("worker invocation failed closed: authority violation")
    if not _string_list(invocation.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker invocation failed closed: allowed outputs missing")
    if not _string_list(invocation.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker invocation failed closed: forbidden operations missing")
    for field in (
        "worker_invocation_id",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "worker_invocation_request_reference",
        "worker_invocation_request_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
        "invoked_by",
        "invoked_at",
    ):
        _require_string(invocation.get(field), field)


def _dispatch_authority_continuity(dispatch: dict[str, Any]) -> bool:
    return (
        dispatch.get("approval_created") is False
        and dispatch.get("worker_assigned") is True
        and dispatch.get("worker_dispatched") is True
        and dispatch.get("dispatch_requested") is True
        and dispatch.get("worker_invoked") is False
        and dispatch.get("execution_started") is False
        and dispatch.get("result_created") is False
        and dispatch.get("governance_mutated") is False
        and dispatch.get("replay_mutated") is False
    )


def _pre_invocation_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_invocation_boundary_flags() -> dict[str, bool]:
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


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker invocation replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker invocation artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_legacy_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    expected = ("worker_invocation_validated", "worker_invocation_returned")
    if expected[index] != step:
        raise FailClosedRuntimeError("worker invocation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "worker invocation artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": WORKER_INVOCATION_VALIDATED if index == 0 else WORKER_INVOCATION_RETURNED,
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
        raise FailClosedRuntimeError("worker invocation replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker invocation replay hash mismatch")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker invocation failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker invocation failed closed: {exc}"
