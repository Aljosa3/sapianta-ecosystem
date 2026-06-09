"""Replay-visible Worker assignment runtime for AiGOL V1."""

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
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_INVOCATION_REQUEST_ARTIFACT_V1,
    WORKER_INVOCATION_REQUEST_CREATED,
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_runtime import AVAILABLE, ASSIGNED, WORKER_ARTIFACT_V1, WORKER_ASSIGNMENT_ARTIFACT_V1


AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION = "AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1"
WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1 = "WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1"
WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1 = "WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1"
WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1 = "WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1"
WORKER_ASSIGNED = "WORKER_ASSIGNED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "assignment_evidence_recorded",
    "assignment_classification_recorded",
    "assignment_artifact_recorded",
    "assignment_result_recorded",
)


def detect_domain_worker_assignment_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for domain worker assignment."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^assign\s+worker\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+worker\s+assignment$",
        r"^create\s+worker\s+assignment\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_WORKER_ASSIGNMENT"
            elif lowered.startswith("create"):
                action = "CREATE_WORKER_ASSIGNMENT"
            else:
                action = "ASSIGN_WORKER"
            return {
                "worker_assignment_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "worker_assignment_action": action,
                "matched_prompt": normalized,
            }
    return {
        "worker_assignment_entry_intent_detected": False,
        "domain_name": None,
        "worker_assignment_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_worker_invocation_request(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest unassigned Worker invocation request replay for a domain."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("worker assignment failed closed: session root missing")
    bridge_index = _domain_execution_ready_bridge_index(root, domain)
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/worker_invocation_request")):
        try:
            reconstructed = reconstruct_worker_invocation_request_replay(path)
            wrapper = load_json(path / "002_invocation_request_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            request = wrapper.get("artifact")
            if not isinstance(request, dict):
                continue
            request = _validate_request_artifact(request)
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("request_status") != WORKER_INVOCATION_REQUEST_CREATED:
            continue
        bridge = _matching_bridge_for_request(request, bridge_index)
        if bridge is None:
            continue
        if _worker_invocation_request_already_assigned(
            root,
            worker_invocation_request_reference=str(request.get("worker_invocation_request_id") or ""),
            worker_invocation_request_hash=str(request.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "worker_invocation_request_replay_reference": str(path),
                "worker_invocation_request_artifact": deepcopy(request),
                "worker_invocation_request_reference": reconstructed["worker_invocation_request_id"],
                "request_hash": request["artifact_hash"],
                "domain_execution_ready_bridge_replay_reference": bridge[
                    "domain_execution_ready_bridge_replay_reference"
                ],
                "domain_name": bridge["approved_domain"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("worker assignment failed closed: matching invocation request not found")
    return candidates[-1]


def assign_worker_from_invocation_request(
    *,
    worker_assignment_id: str,
    worker_invocation_request_artifact: dict[str, Any],
    worker_invocation_request_replay_reference: str,
    worker_registry_artifacts: list[dict[str, Any]],
    assigned_by: str,
    assigned_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Assign one compatible Worker without dispatching, invoking, or executing it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = _validate_invocation_request(
            worker_invocation_request_artifact,
            Path(worker_invocation_request_replay_reference),
        )
        worker = _select_compatible_worker(worker_registry_artifacts, request)
        evidence = _evidence_artifact(
            worker_assignment_id=worker_assignment_id,
            request=request,
            worker=worker,
            worker_invocation_request_replay_reference=worker_invocation_request_replay_reference,
            assigned_at=assigned_at,
        )
        classification = _classification_artifact(
            worker_assignment_id=worker_assignment_id,
            evidence=evidence,
            request=request,
            worker=worker,
            assigned_at=assigned_at,
        )
        assignment = _assignment_artifact(
            worker_assignment_id=worker_assignment_id,
            evidence=evidence,
            classification=classification,
            request=request,
            worker=worker,
            assigned_by=assigned_by,
            assigned_at=assigned_at,
        )
        result = _result_artifact(
            worker_assignment_id=worker_assignment_id,
            evidence=evidence,
            classification=classification,
            assignment=assignment,
            assigned_at=assigned_at,
            status=WORKER_ASSIGNED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], assignment)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, assignment, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_assignment_id=worker_assignment_id,
            worker_invocation_request_reference=(
                worker_invocation_request_artifact.get("worker_invocation_request_id")
                if isinstance(worker_invocation_request_artifact, dict)
                else None
            ),
            worker_invocation_request_replay_reference=worker_invocation_request_replay_reference,
            assigned_at=assigned_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_worker_assignment_runtime_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker assignment replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker assignment replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker assignment replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker assignment replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    assignment = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("assignment_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker assignment replay evidence lineage mismatch")
    if assignment.get("assignment_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker assignment replay classification lineage mismatch")
    if result.get("worker_assignment_hash") != assignment["artifact_hash"]:
        raise FailClosedRuntimeError("worker assignment replay assignment continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], assignment["canonical_chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker assignment replay chain mismatch")
    if evidence["worker_invocation_request_hash"] != assignment["worker_invocation_request_hash"]:
        raise FailClosedRuntimeError("worker assignment replay request lineage mismatch")
    _validate_assignment_artifact(assignment)
    _validate_invocation_request_replay_reference(
        Path(evidence["worker_invocation_request_replay_reference"]),
        assignment["worker_invocation_request_reference"],
        assignment["worker_invocation_request_hash"],
    )
    return {
        "worker_assignment_id": assignment["worker_assignment_id"],
        "assignment_status": result["assignment_status"],
        "worker_id": assignment["worker_id"],
        "worker_family": assignment["worker_family"],
        "worker_role": assignment["worker_role"],
        "canonical_chain_id": assignment["canonical_chain_id"],
        "worker_invocation_request_reference": assignment["worker_invocation_request_reference"],
        "authorization_reference": assignment["authorization_reference"],
        "execution_packet_reference": assignment["execution_packet_reference"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_assignment_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def render_worker_assignment_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Assignment",
        "",
        f"Assignment Status: {capture.get('assignment_status')}",
        f"Worker Assignment Reference: {capture.get('worker_assignment_reference')}",
        f"Assigned Worker: {capture.get('worker_id')}",
        f"Worker Family: {capture.get('worker_family')}",
        f"Worker Role: {capture.get('worker_role')}",
        f"Replay Reference: {capture.get('worker_assignment_replay_reference')}",
        "",
        "No Worker has been dispatched, invoked, or executed.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def default_worker_registry_for_request(request: dict[str, Any], *, created_at: str) -> list[dict[str, Any]]:
    """Return a deterministic in-memory registered Worker candidate for CLI continuity."""

    _validate_request_artifact(request)
    worker = {
        "artifact_type": WORKER_ARTIFACT_V1,
        "worker_runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "worker_id": f"AIGOL-WORKER-{_worker_id_fragment(request['target_worker_family'])}",
        "worker_type": request["target_worker_family"],
        "worker_version": "1.0.0",
        "declared_capabilities": [request["worker_role"]],
        "supported_request_types": ["WORKER_INVOCATION_REQUEST"],
        "capability_id": request["worker_role"],
        "trust_boundary": "LOCAL_BOUNDED_WORKER",
        "state": AVAILABLE,
        "worker_family": request["target_worker_family"],
        "worker_roles": [request["worker_role"]],
        "compatible_execution_packets": [request["execution_packet_reference"]],
        "allowed_outputs": deepcopy(request["allowed_outputs"]),
        "forbidden_operations": deepcopy(request["forbidden_operations"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": "IN_MEMORY_REGISTERED_WORKER_CANDIDATE",
        "replay_visible": True,
        "governance_authority": False,
        "approval_authority": False,
        "proposal_authority": False,
        "provider_authority": False,
        "self_authorization": False,
        "replay_mutation_authority": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_recorded": False,
    }
    worker["artifact_hash"] = replay_hash(worker)
    return [worker]


def _validate_invocation_request(request_artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    request = _validate_request_artifact(request_artifact)
    replay = reconstruct_worker_invocation_request_replay(replay_path)
    if replay.get("request_status") != WORKER_INVOCATION_REQUEST_CREATED:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request invalid")
    if replay.get("worker_invocation_request_id") != request["worker_invocation_request_id"]:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request lineage mismatch")
    if replay.get("request_hash") != request["request_hash"]:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request hash mismatch")
    _validate_invocation_request_replay_reference(
        replay_path,
        request["worker_invocation_request_id"],
        request["artifact_hash"],
    )
    return request


def _validate_invocation_request_replay_reference(
    replay_path: Path,
    request_reference: str,
    request_hash: str,
) -> None:
    wrapper = load_json(replay_path / "002_invocation_request_artifact_recorded.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request replay corruption")
    _verify_artifact_hash(artifact, "worker invocation request artifact")
    if artifact.get("worker_invocation_request_id") != request_reference:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request lineage mismatch")
    if artifact.get("artifact_hash") != request_hash:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request hash mismatch")


def _validate_request_artifact(request_artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request_artifact, dict):
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request is required")
    request = deepcopy(request_artifact)
    _verify_artifact_hash(request, "worker invocation request artifact")
    if request.get("artifact_type") != WORKER_INVOCATION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker assignment failed closed: invalid invocation request artifact")
    if request.get("request_status") != WORKER_INVOCATION_REQUEST_CREATED:
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request invalid")
    if request.get("request_hash") != _request_hash(request):
        raise FailClosedRuntimeError("worker assignment failed closed: invocation request hash mismatch")
    if request.get("worker_assigned") is not False:
        raise FailClosedRuntimeError("worker assignment failed closed: duplicate assignment marker")
    if not _string_list(request.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker assignment failed closed: allowed outputs missing")
    if not _string_list(request.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker assignment failed closed: forbidden operations missing")
    for field, expected in _pre_assignment_boundary_flags().items():
        if request.get(field) is not expected:
            raise FailClosedRuntimeError("worker assignment failed closed: authority violation")
    for field in (
        "worker_invocation_request_id",
        "chain_id",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_role",
        "target_worker_family",
        "request_hash",
    ):
        _require_string(request.get(field), field)
    return request


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


def _matching_bridge_for_request(
    request: dict[str, Any],
    bridge_index: list[dict[str, Any]],
) -> dict[str, Any] | None:
    auth_reference = (request.get("replay_references") or {}).get("execution_authorization_replay_reference")
    if not auth_reference:
        return None
    try:
        wrapper = load_json(Path(auth_reference) / "000_authorization_request_recorded.json")
        _verify_wrapper_hash(wrapper)
        auth_request = wrapper.get("artifact")
        if not isinstance(auth_request, dict):
            return None
        _verify_artifact_hash(auth_request, "execution authorization request artifact")
    except FailClosedRuntimeError:
        return None
    ready_reference = str(auth_request.get("execution_ready_replay_reference") or "")
    ready_hash = str(auth_request.get("execution_ready_hash") or "")
    for bridge in bridge_index:
        if bridge["execution_ready_replay_reference"] == ready_reference:
            return bridge
        if bridge["execution_ready_replay_hash"] == ready_hash:
            return bridge
    return None


def _worker_invocation_request_already_assigned(
    session_root: Path,
    *,
    worker_invocation_request_reference: str,
    worker_invocation_request_hash: str,
) -> bool:
    for path in sorted(session_root.glob("TURN-*/worker_assignment")):
        try:
            reconstructed = reconstruct_worker_assignment_runtime_replay(path)
            wrapper = load_json(path / "002_assignment_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            assignment = wrapper.get("artifact")
            if not isinstance(assignment, dict):
                continue
            _verify_artifact_hash(assignment, "worker assignment artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("assignment_status") != WORKER_ASSIGNED:
            continue
        if assignment.get("worker_invocation_request_reference") == worker_invocation_request_reference:
            return True
        if assignment.get("worker_invocation_request_hash") == worker_invocation_request_hash:
            return True
    return False


def _select_compatible_worker(workers: list[dict[str, Any]], request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(workers, list) or not workers:
        raise FailClosedRuntimeError("worker assignment failed closed: no compatible worker exists")
    compatible: list[dict[str, Any]] = []
    failures: list[str] = []
    for candidate in workers:
        try:
            worker = _validate_worker_artifact(candidate)
            _validate_worker_compatibility(worker, request)
            compatible.append(worker)
        except FailClosedRuntimeError as exc:
            failures.append(str(exc))
    if not compatible:
        reason = failures[0] if failures else "worker assignment failed closed: no compatible worker exists"
        if any("family mismatch" in failure for failure in failures):
            raise FailClosedRuntimeError("worker assignment failed closed: worker family mismatch")
        if any("role mismatch" in failure for failure in failures):
            raise FailClosedRuntimeError("worker assignment failed closed: worker role mismatch")
        if any("packet mismatch" in failure for failure in failures):
            raise FailClosedRuntimeError("worker assignment failed closed: packet mismatch")
        raise FailClosedRuntimeError(reason)
    if len(compatible) > 1:
        raise FailClosedRuntimeError("worker assignment failed closed: worker assignment ambiguous")
    return compatible[0]


def _validate_worker_artifact(worker_artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(worker_artifact, dict):
        raise FailClosedRuntimeError("worker assignment failed closed: worker is required")
    worker = deepcopy(worker_artifact)
    _verify_artifact_hash(worker, "worker artifact")
    if worker.get("artifact_type") != WORKER_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker assignment failed closed: invalid worker artifact")
    if worker.get("state") != AVAILABLE:
        raise FailClosedRuntimeError("worker assignment failed closed: worker unavailable")
    for field in (
        "governance_authority",
        "approval_authority",
        "proposal_authority",
        "provider_authority",
        "self_authorization",
        "replay_mutation_authority",
        "worker_dispatched",
        "worker_invoked",
        "execution_performed",
        "completion_recorded",
    ):
        if worker.get(field) is not False:
            raise FailClosedRuntimeError("worker assignment failed closed: authority violation")
    if worker.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker assignment failed closed: worker replay visibility missing")
    for field in ("worker_id", "worker_type", "worker_version", "capability_id", "worker_family"):
        _require_string(worker.get(field), field)
    if not _string_list(worker.get("worker_roles")):
        raise FailClosedRuntimeError("worker assignment failed closed: worker role missing")
    if not _string_list(worker.get("compatible_execution_packets")):
        raise FailClosedRuntimeError("worker assignment failed closed: packet compatibility missing")
    if not _string_list(worker.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker assignment failed closed: allowed output compatibility missing")
    if not _string_list(worker.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker assignment failed closed: forbidden operation compatibility missing")
    return worker


def _validate_worker_compatibility(worker: dict[str, Any], request: dict[str, Any]) -> None:
    if worker["worker_family"] != request["target_worker_family"]:
        raise FailClosedRuntimeError("worker assignment failed closed: worker family mismatch")
    if request["worker_role"] not in worker["worker_roles"]:
        raise FailClosedRuntimeError("worker assignment failed closed: worker role mismatch")
    packets = set(worker["compatible_execution_packets"])
    if request["execution_packet_reference"] not in packets and "*" not in packets:
        raise FailClosedRuntimeError("worker assignment failed closed: packet mismatch")
    if not _covers(worker["allowed_outputs"], request["allowed_outputs"]):
        raise FailClosedRuntimeError("worker assignment failed closed: allowed outputs mismatch")
    if not _covers(worker["forbidden_operations"], request["forbidden_operations"]):
        raise FailClosedRuntimeError("worker assignment failed closed: forbidden operations mismatch")


def _evidence_artifact(
    *,
    worker_assignment_id: str,
    request: dict[str, Any],
    worker: dict[str, Any],
    worker_invocation_request_replay_reference: str,
    assigned_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "assignment_evidence_id": f"{_require_string(worker_assignment_id, 'worker_assignment_id')}:EVIDENCE",
        "chain_id": request["chain_id"],
        "worker_invocation_request_reference": request["worker_invocation_request_id"],
        "worker_invocation_request_hash": request["artifact_hash"],
        "worker_invocation_request_replay_reference": _require_string(
            worker_invocation_request_replay_reference,
            "worker_invocation_request_replay_reference",
        ),
        "authorization_reference": request["authorization_reference"],
        "authorization_hash": request["authorization_hash"],
        "execution_packet_reference": request["execution_packet_reference"],
        "execution_packet_hash": request["execution_packet_hash"],
        "candidate_reference": request["replay_references"]["execution_candidate_reference"],
        "handoff_reference": request["replay_references"]["handoff_reference"],
        "worker_reference": worker["worker_id"],
        "worker_hash": worker["artifact_hash"],
        "worker_family": worker["worker_family"],
        "worker_role": request["worker_role"],
        "lineage_checks": {
            "invocation_request_lineage": True,
            "authorization_lineage": True,
            "packet_lineage": True,
            "candidate_lineage": True,
            "handoff_lineage": True,
            "chain_continuity": True,
            "replay_continuity": True,
            "authority_continuity": True,
        },
        "recorded_at": _require_string(assigned_at, "assigned_at"),
        "replay_visible": True,
        **_post_assignment_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_assignment_id: str,
    evidence: dict[str, Any],
    request: dict[str, Any],
    worker: dict[str, Any],
    assigned_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "assignment_classification_id": f"{_require_string(worker_assignment_id, 'worker_assignment_id')}:CLASSIFICATION",
        "assignment_evidence_reference": evidence["assignment_evidence_id"],
        "assignment_evidence_hash": evidence["artifact_hash"],
        "chain_id": request["chain_id"],
        "assigned_worker_identity": worker["worker_id"],
        "worker_family_compatible": worker["worker_family"] == request["target_worker_family"],
        "worker_role_compatible": request["worker_role"] in worker["worker_roles"],
        "execution_packet_compatible": request["execution_packet_reference"] in worker["compatible_execution_packets"]
        or "*" in worker["compatible_execution_packets"],
        "allowed_outputs_compatible": _covers(worker["allowed_outputs"], request["allowed_outputs"]),
        "forbidden_operations_compatible": _covers(worker["forbidden_operations"], request["forbidden_operations"]),
        "classification_status": "WORKER_ASSIGNMENT_SCOPE_CLASSIFIED",
        "classified_at": _require_string(assigned_at, "assigned_at"),
        "replay_visible": True,
        **_post_assignment_boundary_flags(),
    }
    checks = (
        artifact["worker_family_compatible"],
        artifact["worker_role_compatible"],
        artifact["execution_packet_compatible"],
        artifact["allowed_outputs_compatible"],
        artifact["forbidden_operations_compatible"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker assignment failed closed: worker compatibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _assignment_artifact(
    *,
    worker_assignment_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    request: dict[str, Any],
    worker: dict[str, Any],
    assigned_by: str,
    assigned_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_ARTIFACT_V1,
        "worker_runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "worker_assignment_id": _require_string(worker_assignment_id, "worker_assignment_id"),
        "assignment_status": WORKER_ASSIGNED,
        "assignment_evidence_reference": evidence["assignment_evidence_id"],
        "assignment_evidence_hash": evidence["artifact_hash"],
        "assignment_classification_reference": classification["assignment_classification_id"],
        "assignment_classification_hash": classification["artifact_hash"],
        "worker_id": worker["worker_id"],
        "worker_hash": worker["artifact_hash"],
        "worker_type": worker["worker_type"],
        "worker_family": worker["worker_family"],
        "worker_role": request["worker_role"],
        "capability_id": worker["capability_id"],
        "worker_invocation_request_reference": request["worker_invocation_request_id"],
        "worker_invocation_request_hash": request["artifact_hash"],
        "request_hash": request["request_hash"],
        "authorization_reference": request["authorization_reference"],
        "authorization_hash": request["authorization_hash"],
        "execution_packet_reference": request["execution_packet_reference"],
        "execution_packet_hash": request["execution_packet_hash"],
        "allowed_outputs": deepcopy(request["allowed_outputs"]),
        "forbidden_operations": deepcopy(request["forbidden_operations"]),
        "validation_requirements": deepcopy(request["validation_requirements"]),
        "assigned_by": _require_string(assigned_by, "assigned_by"),
        "assigned_at": _require_string(assigned_at, "assigned_at"),
        "worker_state_before": AVAILABLE,
        "worker_state_after": ASSIGNED,
        "canonical_chain_id": request["chain_id"],
        "replay_reference": request["replay_references"]["execution_authorization_replay_reference"],
        "replay_visible": True,
        **_post_assignment_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_assignment_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_assignment_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    assignment: dict[str, Any],
    assigned_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "assignment_result_id": f"{_require_string(worker_assignment_id, 'worker_assignment_id')}:RESULT",
        "assignment_status": status,
        "assignment_evidence_reference": evidence["assignment_evidence_id"],
        "assignment_evidence_hash": evidence["artifact_hash"],
        "assignment_classification_reference": classification["assignment_classification_id"],
        "assignment_classification_hash": classification["artifact_hash"],
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_invocation_request_reference": assignment["worker_invocation_request_reference"],
        "worker_invocation_request_hash": assignment["worker_invocation_request_hash"],
        "worker_reference": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "chain_id": assignment["canonical_chain_id"],
        "completed_at": _require_string(assigned_at, "assigned_at"),
        "replay_visible": True,
        **_post_assignment_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_assignment_id: str,
    worker_invocation_request_reference: str | None,
    worker_invocation_request_replay_reference: str,
    assigned_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_ASSIGNMENT_RUNTIME_VERSION,
        "assignment_result_id": f"{worker_assignment_id}:RESULT",
        "assignment_status": FAILED_CLOSED,
        "assignment_evidence_reference": None,
        "assignment_evidence_hash": None,
        "assignment_classification_reference": None,
        "assignment_classification_hash": None,
        "worker_assignment_reference": None,
        "worker_assignment_hash": None,
        "worker_invocation_request_reference": worker_invocation_request_reference,
        "worker_invocation_request_hash": None,
        "worker_invocation_request_replay_reference": worker_invocation_request_replay_reference,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": assigned_at,
        "replay_visible": True,
        "worker_assigned": False,
        **_pre_assignment_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    assignment: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "assignment_evidence_artifact": deepcopy(evidence),
            "assignment_classification_artifact": deepcopy(classification),
            "worker_assignment_artifact": deepcopy(assignment),
            "assignment_result_artifact": deepcopy(result),
            "worker_assignment_reference": assignment.get("worker_assignment_id") if assignment else None,
            "worker_id": assignment.get("worker_id") if assignment else None,
            "worker_family": assignment.get("worker_family") if assignment else None,
            "worker_role": assignment.get("worker_role") if assignment else None,
            "worker_assignment_replay_reference": str(replay_path),
            "fail_closed": result["assignment_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_assignment_capture_hash"] = replay_hash(capture)
    return capture


def _validate_assignment_artifact(assignment: dict[str, Any]) -> None:
    if assignment.get("artifact_type") != WORKER_ASSIGNMENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker assignment failed closed: invalid assignment artifact")
    if assignment.get("assignment_status") != WORKER_ASSIGNED:
        raise FailClosedRuntimeError("worker assignment failed closed: assignment status invalid")
    if assignment.get("worker_state_before") != AVAILABLE or assignment.get("worker_state_after") != ASSIGNED:
        raise FailClosedRuntimeError("worker assignment failed closed: worker state invalid")
    if assignment.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker assignment failed closed: replay visibility missing")
    for field, expected in _post_assignment_boundary_flags().items():
        if assignment.get(field) is not expected:
            raise FailClosedRuntimeError("worker assignment failed closed: authority violation")
    for field in (
        "worker_assignment_id",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "worker_invocation_request_reference",
        "worker_invocation_request_hash",
        "authorization_reference",
        "execution_packet_reference",
        "canonical_chain_id",
        "assigned_by",
        "assigned_at",
    ):
        _require_string(assignment.get(field), field)


def _request_hash(request: dict[str, Any]) -> str:
    return replay_hash(
        {
            "worker_invocation_request_id": request.get("worker_invocation_request_id"),
            "chain_id": request.get("chain_id"),
            "authorization_reference": request.get("authorization_reference"),
            "authorization_hash": request.get("authorization_hash"),
            "execution_packet_reference": request.get("execution_packet_reference"),
            "execution_packet_hash": request.get("execution_packet_hash"),
            "worker_role": request.get("worker_role"),
            "target_worker_family": request.get("target_worker_family"),
            "allowed_outputs": request.get("allowed_outputs", []),
            "forbidden_operations": request.get("forbidden_operations", []),
            "validation_requirements": request.get("validation_requirements", []),
            "replay_references": request.get("replay_references", {}),
        }
    )


def _pre_assignment_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_assignment_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _covers(available: list[str], required: list[str]) -> bool:
    if "*" in available:
        return True
    return set(required).issubset(set(available))


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker assignment replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker assignment artifact")
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
        raise FailClosedRuntimeError("worker assignment replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker assignment replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker assignment failed closed: {field} is required")
    return value


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _worker_id_fragment(value: str) -> str:
    return "".join(char if char.isalnum() else "-" for char in value.upper()).strip("-") or "BOUNDARY"


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker assignment failed closed: {exc}"
