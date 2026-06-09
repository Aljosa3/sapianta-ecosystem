"""Replay-visible Worker dispatch runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    DOMAIN_EXECUTION_READY_BRIDGED,
    reconstruct_domain_execution_ready_bridge_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_invocation_request_runtime import reconstruct_worker_invocation_request_replay
from aigol.runtime.worker_runtime import ASSIGNED, WORKER_ASSIGNMENT_ARTIFACT_V1


AIGOL_WORKER_DISPATCH_RUNTIME_VERSION = "AIGOL_WORKER_DISPATCH_RUNTIME_V1"
WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1 = "WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1"
WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1 = "WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1"
WORKER_DISPATCH_ARTIFACT_V1 = "WORKER_DISPATCH_ARTIFACT_V1"
WORKER_DISPATCH_RESULT_ARTIFACT_V1 = "WORKER_DISPATCH_RESULT_ARTIFACT_V1"
WORKER_DISPATCHED = "WORKER_DISPATCHED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "dispatch_evidence_recorded",
    "dispatch_classification_recorded",
    "dispatch_artifact_recorded",
    "dispatch_result_recorded",
)


def detect_domain_worker_dispatch_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for domain worker dispatch."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^dispatch\s+worker\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+worker\s+dispatch$",
        r"^create\s+worker\s+dispatch\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_WORKER_DISPATCH"
            elif lowered.startswith("create"):
                action = "CREATE_WORKER_DISPATCH"
            else:
                action = "DISPATCH_WORKER"
            return {
                "worker_dispatch_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "worker_dispatch_action": action,
                "matched_prompt": normalized,
            }
    return {
        "worker_dispatch_entry_intent_detected": False,
        "domain_name": None,
        "worker_dispatch_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_worker_assignment(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest undispatched Worker assignment replay for a domain."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("worker dispatch failed closed: session root missing")
    bridge_index = _domain_execution_ready_bridge_index(root, domain)
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/worker_assignment")):
        try:
            reconstructed = reconstruct_worker_assignment_runtime_replay(path)
            wrapper = load_json(path / "002_assignment_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            assignment = wrapper.get("artifact")
            if not isinstance(assignment, dict):
                continue
            _verify_artifact_hash(assignment, "worker assignment artifact")
            _validate_assignment_artifact(assignment)
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("assignment_status") != WORKER_ASSIGNED:
            continue
        bridge = _matching_bridge_for_assignment(path, assignment, bridge_index)
        if bridge is None:
            continue
        if _worker_assignment_already_dispatched(
            root,
            worker_assignment_reference=str(assignment.get("worker_assignment_id") or ""),
            worker_assignment_hash=str(assignment.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "worker_assignment_replay_reference": str(path),
                "worker_assignment_artifact": deepcopy(assignment),
                "worker_assignment_reference": reconstructed["worker_assignment_id"],
                "assignment_hash": assignment["artifact_hash"],
                "domain_execution_ready_bridge_replay_reference": bridge[
                    "domain_execution_ready_bridge_replay_reference"
                ],
                "domain_name": bridge["approved_domain"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("worker dispatch failed closed: matching worker assignment not found")
    return candidates[-1]


def dispatch_assigned_worker(
    *,
    worker_dispatch_id: str,
    worker_assignment_artifact: dict[str, Any],
    worker_assignment_replay_reference: str,
    dispatched_by: str,
    dispatched_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Dispatch one assigned Worker without invoking, executing, or producing results."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_assignment_lineage(Path(worker_assignment_replay_reference), worker_assignment_artifact)
        assignment = lineage["assignment"]
        evidence = _evidence_artifact(
            worker_dispatch_id=worker_dispatch_id,
            assignment=assignment,
            lineage=lineage,
            worker_assignment_replay_reference=worker_assignment_replay_reference,
            dispatched_at=dispatched_at,
        )
        classification = _classification_artifact(
            worker_dispatch_id=worker_dispatch_id,
            evidence=evidence,
            assignment=assignment,
            dispatched_at=dispatched_at,
        )
        dispatch = _dispatch_artifact(
            worker_dispatch_id=worker_dispatch_id,
            evidence=evidence,
            classification=classification,
            assignment=assignment,
            dispatched_by=dispatched_by,
            dispatched_at=dispatched_at,
        )
        result = _result_artifact(
            worker_dispatch_id=worker_dispatch_id,
            evidence=evidence,
            classification=classification,
            dispatch=dispatch,
            dispatched_at=dispatched_at,
            status=WORKER_DISPATCHED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], dispatch)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, dispatch, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_dispatch_id=worker_dispatch_id,
            worker_assignment_reference=(
                worker_assignment_artifact.get("worker_assignment_id")
                if isinstance(worker_assignment_artifact, dict)
                else None
            ),
            worker_assignment_replay_reference=worker_assignment_replay_reference,
            dispatched_at=dispatched_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_worker_dispatch_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker dispatch replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker dispatch replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker dispatch replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker dispatch replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    dispatch = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("dispatch_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker dispatch replay evidence lineage mismatch")
    if dispatch.get("dispatch_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker dispatch replay classification lineage mismatch")
    if result.get("worker_dispatch_hash") != dispatch["artifact_hash"]:
        raise FailClosedRuntimeError("worker dispatch replay dispatch continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], dispatch["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker dispatch replay chain mismatch")
    if evidence["worker_assignment_hash"] != dispatch["worker_assignment_hash"]:
        raise FailClosedRuntimeError("worker dispatch replay assignment lineage mismatch")
    _validate_dispatch_artifact(dispatch)
    assignment_replay_path = _resolve_replay_reference(
        evidence["worker_assignment_replay_reference"],
        anchor=replay_path,
    )
    _load_assignment_lineage(assignment_replay_path, None, dispatch=dispatch)
    return {
        "worker_dispatch_id": dispatch["worker_dispatch_id"],
        "dispatch_status": result["dispatch_status"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_id": dispatch["worker_id"],
        "worker_family": dispatch["worker_family"],
        "worker_role": dispatch["worker_role"],
        "chain_id": dispatch["chain_id"],
        "worker_invocation_request_reference": dispatch["worker_invocation_request_reference"],
        "authorization_reference": dispatch["authorization_reference"],
        "execution_packet_reference": dispatch["execution_packet_reference"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_dispatch_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_worker_dispatch_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Dispatch",
        "",
        f"Dispatch Status: {capture.get('dispatch_status')}",
        f"Worker Dispatch Reference: {capture.get('worker_dispatch_reference')}",
        f"Worker Assignment Reference: {capture.get('worker_assignment_reference')}",
        f"Dispatched Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('worker_dispatch_replay_reference')}",
        "",
        "No Worker has been invoked, executed, or produced results.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_assignment_lineage(
    assignment_replay_path: Path,
    provided_assignment: dict[str, Any] | None,
    *,
    dispatch: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    reconstructed = reconstruct_worker_assignment_runtime_replay(assignment_replay_path)
    if reconstructed.get("assignment_status") != WORKER_ASSIGNED:
        raise FailClosedRuntimeError("worker dispatch failed closed: assignment invalid")
    wrappers = []
    expected = (
        (0, "assignment_evidence_recorded"),
        (1, "assignment_classification_recorded"),
        (2, "assignment_artifact_recorded"),
        (3, "assignment_result_recorded"),
    )
    for index, step in expected:
        wrapper = load_json(assignment_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker dispatch failed closed: assignment replay corruption")
        _verify_artifact_hash(artifact, "worker assignment lineage artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    assignment = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    _validate_assignment_artifact(assignment)
    if provided_assignment is not None:
        _verify_artifact_hash(provided_assignment, "provided worker assignment artifact")
        if provided_assignment.get("worker_assignment_id") != assignment["worker_assignment_id"]:
            raise FailClosedRuntimeError("worker dispatch failed closed: assignment mismatch")
        if provided_assignment.get("artifact_hash") != assignment["artifact_hash"]:
            raise FailClosedRuntimeError("worker dispatch failed closed: assignment mismatch")
    if dispatch is not None:
        if dispatch.get("worker_assignment_reference") != assignment["worker_assignment_id"]:
            raise FailClosedRuntimeError("worker dispatch failed closed: assignment mismatch")
        if dispatch.get("worker_assignment_hash") != assignment["artifact_hash"]:
            raise FailClosedRuntimeError("worker dispatch failed closed: assignment mismatch")
    if result.get("worker_assignment_hash") != assignment["artifact_hash"]:
        raise FailClosedRuntimeError("worker dispatch failed closed: assignment lineage invalid")
    request_replay = _resolve_replay_reference(
        evidence["worker_invocation_request_replay_reference"],
        anchor=assignment_replay_path,
    )
    request_reconstructed = reconstruct_worker_invocation_request_replay(request_replay)
    if request_reconstructed.get("worker_invocation_request_id") != assignment["worker_invocation_request_reference"]:
        raise FailClosedRuntimeError("worker dispatch failed closed: invocation request lineage mismatch")
    checks = {
        "assignment_lineage": result["worker_assignment_hash"] == assignment["artifact_hash"],
        "invocation_request_lineage": assignment["worker_invocation_request_hash"]
        == evidence["worker_invocation_request_hash"],
        "authorization_lineage": assignment["authorization_hash"] == evidence["authorization_hash"],
        "execution_packet_lineage": assignment["execution_packet_hash"] == evidence["execution_packet_hash"],
        "chain_continuity": assignment["canonical_chain_id"] == evidence["chain_id"],
        "replay_continuity": request_reconstructed["request_status"] == "WORKER_INVOCATION_REQUEST_CREATED",
        "authority_continuity": _assignment_authority_continuity(assignment),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker dispatch failed closed: lineage continuity invalid")
    return {
        "assignment_evidence": evidence,
        "assignment_classification": classification,
        "assignment": assignment,
        "assignment_result": result,
        "lineage_checks": checks,
    }


def _validate_assignment_artifact(assignment: dict[str, Any]) -> None:
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker dispatch failed closed: invalid assignment artifact")
    if assignment.get("assignment_status") != WORKER_ASSIGNED:
        raise FailClosedRuntimeError("worker dispatch failed closed: assignment invalid")
    if assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("worker dispatch failed closed: worker unavailable")
    if assignment.get("worker_assigned") is not True:
        raise FailClosedRuntimeError("worker dispatch failed closed: assignment invalid")
    if assignment.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: duplicate dispatch marker")
    if assignment.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: worker invocation detected")
    if assignment.get("execution_started") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: execution started")
    if assignment.get("result_created") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: result already created")
    if assignment.get("approval_created") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: approval authority introduced")
    if assignment.get("governance_mutated") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: governance mutation detected")
    if assignment.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("worker dispatch failed closed: replay mutation detected")
    for field in (
        "worker_assignment_id",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "worker_invocation_request_reference",
        "worker_invocation_request_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "canonical_chain_id",
    ):
        _require_string(assignment.get(field), field)


def _evidence_artifact(
    *,
    worker_dispatch_id: str,
    assignment: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    worker_assignment_replay_reference: str,
    dispatched_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_RUNTIME_VERSION,
        "dispatch_evidence_id": f"{_require_string(worker_dispatch_id, 'worker_dispatch_id')}:EVIDENCE",
        "chain_id": assignment["canonical_chain_id"],
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_assignment_replay_reference": _require_string(
            worker_assignment_replay_reference,
            "worker_assignment_replay_reference",
        ),
        "worker_invocation_request_reference": assignment["worker_invocation_request_reference"],
        "worker_invocation_request_hash": assignment["worker_invocation_request_hash"],
        "authorization_reference": assignment["authorization_reference"],
        "authorization_hash": assignment["authorization_hash"],
        "execution_packet_reference": assignment["execution_packet_reference"],
        "execution_packet_hash": assignment["execution_packet_hash"],
        "worker_id": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "worker_family": assignment["worker_family"],
        "worker_role": assignment["worker_role"],
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(dispatched_at, "dispatched_at"),
        "replay_visible": True,
        **_post_dispatch_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_dispatch_id: str,
    evidence: dict[str, Any],
    assignment: dict[str, Any],
    dispatched_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_RUNTIME_VERSION,
        "dispatch_classification_id": f"{_require_string(worker_dispatch_id, 'worker_dispatch_id')}:CLASSIFICATION",
        "dispatch_evidence_reference": evidence["dispatch_evidence_id"],
        "dispatch_evidence_hash": evidence["artifact_hash"],
        "chain_id": assignment["canonical_chain_id"],
        "assigned_worker_identity": assignment["worker_id"],
        "dispatch_eligible": assignment["assignment_status"] == WORKER_ASSIGNED
        and assignment["worker_state_after"] == ASSIGNED,
        "execution_packet_compatible": evidence["execution_packet_hash"] == assignment["execution_packet_hash"],
        "role_compatible": evidence["worker_role"] == assignment["worker_role"],
        "authority_continuous": _assignment_authority_continuity(assignment),
        "replay_continuous": True,
        "classification_status": "WORKER_DISPATCH_SCOPE_CLASSIFIED",
        "classified_at": _require_string(dispatched_at, "dispatched_at"),
        "replay_visible": True,
        **_post_dispatch_boundary_flags(),
    }
    checks = (
        artifact["dispatch_eligible"],
        artifact["execution_packet_compatible"],
        artifact["role_compatible"],
        artifact["authority_continuous"],
        artifact["replay_continuous"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker dispatch failed closed: dispatch eligibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _dispatch_artifact(
    *,
    worker_dispatch_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    assignment: dict[str, Any],
    dispatched_by: str,
    dispatched_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_RUNTIME_VERSION,
        "worker_dispatch_id": _require_string(worker_dispatch_id, "worker_dispatch_id"),
        "dispatch_status": WORKER_DISPATCHED,
        "dispatch_evidence_reference": evidence["dispatch_evidence_id"],
        "dispatch_evidence_hash": evidence["artifact_hash"],
        "dispatch_classification_reference": classification["dispatch_classification_id"],
        "dispatch_classification_hash": classification["artifact_hash"],
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_invocation_request_reference": assignment["worker_invocation_request_reference"],
        "worker_invocation_request_hash": assignment["worker_invocation_request_hash"],
        "authorization_reference": assignment["authorization_reference"],
        "authorization_hash": assignment["authorization_hash"],
        "execution_packet_reference": assignment["execution_packet_reference"],
        "execution_packet_hash": assignment["execution_packet_hash"],
        "worker_id": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "worker_family": assignment["worker_family"],
        "worker_role": assignment["worker_role"],
        "allowed_outputs": deepcopy(assignment["allowed_outputs"]),
        "forbidden_operations": deepcopy(assignment["forbidden_operations"]),
        "validation_requirements": deepcopy(assignment["validation_requirements"]),
        "dispatched_by": _require_string(dispatched_by, "dispatched_by"),
        "dispatched_at": _require_string(dispatched_at, "dispatched_at"),
        "assignment_status_before": assignment["assignment_status"],
        "worker_state_before_dispatch": assignment["worker_state_after"],
        "chain_id": assignment["canonical_chain_id"],
        "replay_reference": assignment["replay_reference"],
        "replay_visible": True,
        **_post_dispatch_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_dispatch_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_dispatch_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    dispatch: dict[str, Any],
    dispatched_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_RUNTIME_VERSION,
        "dispatch_result_id": f"{_require_string(worker_dispatch_id, 'worker_dispatch_id')}:RESULT",
        "dispatch_status": status,
        "dispatch_evidence_reference": evidence["dispatch_evidence_id"],
        "dispatch_evidence_hash": evidence["artifact_hash"],
        "dispatch_classification_reference": classification["dispatch_classification_id"],
        "dispatch_classification_hash": classification["artifact_hash"],
        "worker_dispatch_reference": dispatch["worker_dispatch_id"],
        "worker_dispatch_hash": dispatch["artifact_hash"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_reference": dispatch["worker_id"],
        "worker_hash": dispatch["worker_hash"],
        "chain_id": dispatch["chain_id"],
        "completed_at": _require_string(dispatched_at, "dispatched_at"),
        "replay_visible": True,
        **_post_dispatch_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_dispatch_id: str,
    worker_assignment_reference: str | None,
    worker_assignment_replay_reference: str,
    dispatched_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_DISPATCH_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_DISPATCH_RUNTIME_VERSION,
        "dispatch_result_id": f"{worker_dispatch_id}:RESULT",
        "dispatch_status": FAILED_CLOSED,
        "dispatch_evidence_reference": None,
        "dispatch_evidence_hash": None,
        "dispatch_classification_reference": None,
        "dispatch_classification_hash": None,
        "worker_dispatch_reference": None,
        "worker_dispatch_hash": None,
        "worker_assignment_reference": worker_assignment_reference,
        "worker_assignment_hash": None,
        "worker_assignment_replay_reference": worker_assignment_replay_reference,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": dispatched_at,
        "replay_visible": True,
        "worker_dispatched": False,
        "dispatch_requested": False,
        **_pre_dispatch_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    dispatch: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "dispatch_evidence_artifact": deepcopy(evidence),
            "dispatch_classification_artifact": deepcopy(classification),
            "worker_dispatch_artifact": deepcopy(dispatch),
            "dispatch_result_artifact": deepcopy(result),
            "worker_dispatch_reference": dispatch.get("worker_dispatch_id") if dispatch else None,
            "worker_assignment_reference": dispatch.get("worker_assignment_reference") if dispatch else None,
            "worker_id": dispatch.get("worker_id") if dispatch else None,
            "worker_family": dispatch.get("worker_family") if dispatch else None,
            "worker_role": dispatch.get("worker_role") if dispatch else None,
            "worker_dispatch_replay_reference": str(replay_path),
            "fail_closed": result["dispatch_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_dispatch_capture_hash"] = replay_hash(capture)
    return capture


def _validate_dispatch_artifact(dispatch: dict[str, Any]) -> None:
    if dispatch.get("artifact_type") != WORKER_DISPATCH_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker dispatch failed closed: invalid dispatch artifact")
    if dispatch.get("dispatch_status") != WORKER_DISPATCHED:
        raise FailClosedRuntimeError("worker dispatch failed closed: dispatch status invalid")
    if dispatch.get("assignment_status_before") != WORKER_ASSIGNED:
        raise FailClosedRuntimeError("worker dispatch failed closed: assignment invalid")
    if dispatch.get("worker_state_before_dispatch") != ASSIGNED:
        raise FailClosedRuntimeError("worker dispatch failed closed: worker unavailable")
    if dispatch.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker dispatch failed closed: replay visibility missing")
    for field, expected in _post_dispatch_boundary_flags().items():
        if dispatch.get(field) is not expected:
            raise FailClosedRuntimeError("worker dispatch failed closed: authority violation")
    for field in (
        "worker_dispatch_id",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "worker_invocation_request_reference",
        "authorization_reference",
        "execution_packet_reference",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
        "dispatched_by",
        "dispatched_at",
    ):
        _require_string(dispatch.get(field), field)


def _domain_execution_ready_bridge_index(root: Path, domain_name: str) -> list[dict[str, Any]]:
    bridges: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/domain_execution_ready_bridge")):
        try:
            reconstructed = reconstruct_domain_execution_ready_bridge_replay(path)
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("bridge_status") != DOMAIN_EXECUTION_READY_BRIDGED:
            continue
        if str(reconstructed.get("approved_domain") or "").lower() != domain_name.lower():
            continue
        bridges.append(
            {
                "domain_execution_ready_bridge_replay_reference": str(path),
                "approved_domain": reconstructed["approved_domain"],
                "execution_ready_replay_reference": reconstructed["execution_ready_replay_reference"],
                "execution_ready_replay_hash": reconstructed["execution_ready_replay_hash"],
            }
        )
    return bridges


def _matching_bridge_for_assignment(
    assignment_replay_path: Path,
    assignment: dict[str, Any],
    bridge_index: list[dict[str, Any]],
) -> dict[str, Any] | None:
    try:
        evidence_wrapper = load_json(assignment_replay_path / "000_assignment_evidence_recorded.json")
        _verify_wrapper_hash(evidence_wrapper)
        evidence = evidence_wrapper.get("artifact")
        if not isinstance(evidence, dict):
            return None
        _verify_artifact_hash(evidence, "worker assignment evidence artifact")
        request_replay_path = _resolve_replay_reference(
            evidence["worker_invocation_request_replay_reference"],
            anchor=assignment_replay_path,
        )
        request_wrapper = load_json(
            request_replay_path / "002_invocation_request_artifact_recorded.json"
        )
        _verify_wrapper_hash(request_wrapper)
        request = request_wrapper.get("artifact")
        if not isinstance(request, dict):
            return None
        _verify_artifact_hash(request, "worker invocation request artifact")
        if request.get("worker_invocation_request_id") != assignment["worker_invocation_request_reference"]:
            return None
        auth_reference = (request.get("replay_references") or {}).get("execution_authorization_replay_reference")
        if not auth_reference:
            return None
        auth_replay_path = _resolve_replay_reference(auth_reference, anchor=request_replay_path)
        auth_wrapper = load_json(auth_replay_path / "000_authorization_request_recorded.json")
        _verify_wrapper_hash(auth_wrapper)
        auth_request = auth_wrapper.get("artifact")
        if not isinstance(auth_request, dict):
            return None
        _verify_artifact_hash(auth_request, "execution authorization request artifact")
    except (FailClosedRuntimeError, KeyError):
        return None
    ready_reference = str(auth_request.get("execution_ready_replay_reference") or "")
    ready_hash = str(auth_request.get("execution_ready_hash") or "")
    for bridge in bridge_index:
        if bridge["execution_ready_replay_reference"] == ready_reference:
            return bridge
        if bridge["execution_ready_replay_hash"] == ready_hash:
            return bridge
    return None


def _worker_assignment_already_dispatched(
    session_root: Path,
    *,
    worker_assignment_reference: str,
    worker_assignment_hash: str,
) -> bool:
    for path in sorted(session_root.glob("TURN-*/worker_dispatch")):
        try:
            reconstructed = reconstruct_worker_dispatch_replay(path)
            wrapper = load_json(path / "002_dispatch_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            dispatch = wrapper.get("artifact")
            if not isinstance(dispatch, dict):
                continue
            _verify_artifact_hash(dispatch, "worker dispatch artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("dispatch_status") != WORKER_DISPATCHED:
            continue
        if dispatch.get("worker_assignment_reference") == worker_assignment_reference:
            return True
        if dispatch.get("worker_assignment_hash") == worker_assignment_hash:
            return True
    return False


def _resolve_replay_reference(reference: Any, *, anchor: Path) -> Path:
    replay_path = Path(_require_string(reference, "replay_reference"))
    if replay_path.is_absolute() or replay_path.exists():
        return replay_path
    for parent in (anchor, *anchor.parents):
        candidate = parent / replay_path
        if candidate.exists():
            return candidate
    return replay_path


def _assignment_authority_continuity(assignment: dict[str, Any]) -> bool:
    return (
        assignment.get("worker_assigned") is True
        and assignment.get("worker_dispatched") is False
        and assignment.get("worker_invoked") is False
        and assignment.get("execution_started") is False
        and assignment.get("result_created") is False
        and assignment.get("approval_created") is False
        and assignment.get("governance_mutated") is False
        and assignment.get("replay_mutated") is False
    )


def _pre_dispatch_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_dispatch_boundary_flags() -> dict[str, bool]:
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


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker dispatch replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker dispatch artifact")
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
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("worker dispatch replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker dispatch replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker dispatch failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker dispatch failed closed: {exc}"
