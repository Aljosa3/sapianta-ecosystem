"""Replay-visible execution readiness runtime for OCS handoff artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_CANDIDATE_ARTIFACT_V1,
    EXECUTION_PACKET_ARTIFACT_V1,
    EXECUTION_READY,
    EXECUTION_READY_STATUS_ARTIFACT_V1,
    EXECUTION_VALIDATION_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_to_execution_handoff_runtime import (
    EXECUTION_HANDOFF_CANDIDATE,
    OCS_EXECUTION_HANDOFF_ARTIFACT_V1,
    reconstruct_ocs_execution_handoff_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_EXECUTION_READINESS_RUNTIME_V1"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "execution_candidate_recorded",
    "execution_packet_recorded",
    "execution_validation_recorded",
    "execution_ready_status_recorded",
)

REQUIRED_HANDOFF_VALIDATIONS = (
    "OCS_COGNITION_LINEAGE",
    "NORMALIZED_COGNITION_PRESENT",
    "BOUNDED_EXECUTION_INTENT",
    "ALLOWED_OUTPUTS_EXPLICIT",
    "FORBIDDEN_OPERATIONS_EXPLICIT",
    "HUMAN_APPROVAL_BINDING",
    "WORKER_ROLE_CONSTRAINTS",
    "REPLAY_LINEAGE_CONTINUITY",
    "AUTHORITY_BOUNDARIES",
    "HASH_INTEGRITY",
)

AUTHORITY_FALSE_FIELDS = (
    "authorization_created",
    "worker_request_created",
    "worker_assigned",
    "worker_dispatched",
    "worker_invoked",
    "execution_started",
    "repair_started",
    "retry_started",
)


def evaluate_ocs_execution_readiness(
    *,
    readiness_id: str,
    ocs_handoff_replay_reference: str,
    approval_status: str,
    approval_reference: str,
    approval_hash: str,
    approving_actor: str,
    approved_at: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Convert an approved OCS handoff candidate into an execution-ready packet."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        handoff = _load_handoff(Path(_require_string(ocs_handoff_replay_reference, "ocs_handoff_replay_reference")))
        approval = _approval_lineage(
            approval_status=approval_status,
            approval_reference=approval_reference,
            approval_hash=approval_hash,
            approving_actor=approving_actor,
            approved_at=approved_at,
            handoff=handoff,
        )
        candidate = _candidate_artifact(
            readiness_id=readiness_id,
            handoff=handoff,
            approval=approval,
            ocs_handoff_replay_reference=ocs_handoff_replay_reference,
            created_at=created_at,
        )
        packet = _packet_artifact(readiness_id=readiness_id, candidate=candidate, handoff=handoff, created_at=created_at)
        validation = _validation_artifact(
            readiness_id=readiness_id,
            handoff=handoff,
            approval=approval,
            candidate=candidate,
            packet=packet,
            created_at=created_at,
        )
        ready = _ready_artifact(
            readiness_id=readiness_id,
            candidate=candidate,
            packet=packet,
            validation=validation,
            created_at=created_at,
            status=EXECUTION_READY,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], packet)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], validation)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], ready)
        return _capture(candidate, packet, validation, ready, replay_path)
    except Exception as exc:
        ready = _failed_ready_artifact(
            readiness_id=readiness_id,
            ocs_handoff_replay_reference=ocs_handoff_replay_reference,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], ready)
        return _capture(None, None, None, ready, replay_path)


def reconstruct_ocs_execution_readiness_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS execution readiness replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    expected = (
        (0, "execution_candidate_recorded", EXECUTION_CANDIDATE_ARTIFACT_V1),
        (1, "execution_packet_recorded", EXECUTION_PACKET_ARTIFACT_V1),
        (2, "execution_validation_recorded", EXECUTION_VALIDATION_ARTIFACT_V1),
        (3, "execution_ready_status_recorded", EXECUTION_READY_STATUS_ARTIFACT_V1),
    )
    for index, step, artifact_type in expected:
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS execution readiness replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS execution readiness replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "OCS execution readiness replay artifact")
        if artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError("OCS execution readiness replay artifact type mismatch")
        wrappers.append(wrapper)

    candidate = wrappers[0]["artifact"]
    packet = wrappers[1]["artifact"]
    validation = wrappers[2]["artifact"]
    ready = wrappers[3]["artifact"]
    checks = (
        packet.get("candidate_hash") == candidate["artifact_hash"],
        validation.get("candidate_hash") == candidate["artifact_hash"],
        validation.get("packet_hash") == packet["artifact_hash"],
        ready.get("candidate_hash") == candidate["artifact_hash"],
        ready.get("packet_hash") == packet["artifact_hash"],
        ready.get("validation_hash") == validation["artifact_hash"],
        candidate.get("candidate_hash") == _candidate_hash(candidate),
        packet.get("packet_hash") == _packet_hash(packet),
        candidate.get("chain_id") == packet.get("chain_id") == validation.get("chain_id") == ready.get("chain_id"),
        ready.get("execution_status") == EXECUTION_READY,
        ready.get("execution_started") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError("OCS execution readiness replay lineage mismatch")
    handoff = _load_handoff(Path(candidate["handoff_replay_reference"]))
    if handoff["handoff_id"] != candidate["handoff_reference"]:
        raise FailClosedRuntimeError("OCS execution readiness handoff continuity mismatch")
    _validate_authority_boundaries(candidate)
    _validate_authority_boundaries(packet)
    _validate_authority_boundaries(validation)
    _validate_authority_boundaries(ready)
    return {
        "readiness_id": ready["dry_run_id"],
        "execution_status": ready["execution_status"],
        "chain_id": candidate["chain_id"],
        "handoff_reference": candidate["handoff_reference"],
        "candidate_reference": candidate["candidate_id"],
        "packet_reference": packet["packet_id"],
        "validation_reference": validation["validation_id"],
        "approval_status": candidate["approval_status"],
        "approval_reference": candidate["approval_reference"],
        "approval_hash": candidate["approval_hash"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "failure_reason": ready["failure_reason"],
    }


def render_ocs_execution_readiness_summary(capture: dict[str, Any]) -> str:
    """Render a compact operator summary for readiness evaluation."""

    lines = [
        "",
        "Execution Readiness",
        "",
        f"Execution Status: {capture.get('execution_status')}",
        f"Candidate Reference: {capture.get('candidate_reference')}",
        f"Packet Reference: {capture.get('packet_reference')}",
        f"Validation Reference: {capture.get('validation_reference')}",
        f"Replay Reference: {capture.get('ocs_execution_readiness_replay_reference')}",
        "",
        "No authorization, Worker request, dispatch, invocation, execution, repair, or retry was created.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_handoff(replay_path: Path) -> dict[str, Any]:
    reconstructed = reconstruct_ocs_execution_handoff_replay(replay_path)
    if reconstructed.get("handoff_status") != EXECUTION_HANDOFF_CANDIDATE:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: handoff is not a candidate")
    wrapper = load_json(replay_path / "000_ocs_execution_handoff_recorded.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: handoff artifact missing")
    _verify_artifact_hash(artifact, "OCS execution handoff artifact")
    if artifact.get("artifact_type") != OCS_EXECUTION_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: invalid handoff artifact")
    _validate_handoff_contract(artifact)
    return artifact


def _approval_lineage(
    *,
    approval_status: str,
    approval_reference: str,
    approval_hash: str,
    approving_actor: str,
    approved_at: str,
    handoff: dict[str, Any],
) -> dict[str, str]:
    normalized_status = _require_string(approval_status, "approval_status")
    if handoff.get("approval_required") is not True:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: approval requirement missing")
    if normalized_status != "APPROVED":
        raise FailClosedRuntimeError("OCS execution readiness failed closed: approval missing")
    approval = {
        "approval_status": normalized_status,
        "approval_reference": _require_string(approval_reference, "approval_reference"),
        "approval_hash": _require_string(approval_hash, "approval_hash"),
        "approving_actor": _require_string(approving_actor, "approving_actor"),
        "approved_at": _require_string(approved_at, "approved_at"),
    }
    if approval["approving_actor"].lower() in {"openai", "provider", "ocs", "llm"}:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: approval actor invalid")
    return approval


def _candidate_artifact(
    *,
    readiness_id: str,
    handoff: dict[str, Any],
    approval: dict[str, str],
    ocs_handoff_replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "candidate_id": f"{_require_string(readiness_id, 'readiness_id')}:CANDIDATE",
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "handoff_contract_hash": handoff["handoff_hash"],
        "handoff_replay_reference": _require_string(ocs_handoff_replay_reference, "ocs_handoff_replay_reference"),
        "chain_id": handoff["chain_id"],
        "target_domain": handoff["execution_candidate_scope"].get("domain", "UNSPECIFIED"),
        "target_resource": handoff["execution_intake_id"],
        "target_worker": handoff["target_worker_family"],
        "planned_artifacts": deepcopy(handoff["allowed_outputs"]),
        "required_resource_roles": deepcopy(handoff["worker_role_requirements"]),
        "approval_status": approval["approval_status"],
        "approval_reference": approval["approval_reference"],
        "approval_hash": approval["approval_hash"],
        "approving_actor": approval["approving_actor"],
        "approved_at": approval["approved_at"],
        "upstream_lineage_reference": handoff["handoff_id"],
        "upstream_lineage_hash": handoff["artifact_hash"],
        "execution_scope": {
            "mode": "OCS_EXECUTION_READINESS_ONLY",
            "source_handoff_id": handoff["handoff_id"],
            "execution_candidate_scope": deepcopy(handoff["execution_candidate_scope"]),
            "allowed_outputs": deepcopy(handoff["allowed_outputs"]),
            "forbidden_operations": deepcopy(handoff["forbidden_operations"]),
            "execution_authorized": False,
        },
        "required_validation": deepcopy(handoff["required_validation"]),
        "worker_constraints": {
            "worker_selection_required": handoff["worker_selection_required"],
            "target_worker_family": handoff["target_worker_family"],
            "candidate_worker_constraints": deepcopy(handoff["candidate_worker_constraints"]),
            "worker_capability_requirements": deepcopy(handoff["worker_capability_requirements"]),
            "worker_exclusion_rules": deepcopy(handoff["worker_exclusion_rules"]),
            "worker_registry_requirements": deepcopy(handoff["worker_registry_requirements"]),
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["candidate_hash"] = _candidate_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _packet_artifact(
    *,
    readiness_id: str,
    candidate: dict[str, Any],
    handoff: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "packet_id": f"{_require_string(readiness_id, 'readiness_id')}:PACKET",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "chain_id": candidate["chain_id"],
        "execution_contract": {
            "contract_type": "OCS_EXECUTION_HANDOFF_READINESS",
            "execution_state": "NOT_STARTED",
            "execution_authorized": False,
            "authorization_required": True,
            "preparation_only": True,
        },
        "allowed_outputs": deepcopy(handoff["allowed_outputs"]),
        "forbidden_operations": deepcopy(handoff["forbidden_operations"]),
        "required_validations": deepcopy(handoff["required_validation"]),
        "worker_role_requirements": deepcopy(handoff["worker_role_requirements"]),
        "worker_constraints": deepcopy(candidate["worker_constraints"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["packet_hash"] = _packet_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    readiness_id: str,
    handoff: dict[str, Any],
    approval: dict[str, str],
    candidate: dict[str, Any],
    packet: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    checks = {
        "scope_completeness": _scope_complete(handoff),
        "approval_requirements": approval["approval_status"] == "APPROVED" and bool(approval["approval_hash"]),
        "allowed_outputs": _string_list(handoff.get("allowed_outputs")),
        "forbidden_operations": _string_list(handoff.get("forbidden_operations")),
        "validation_requirements": set(REQUIRED_HANDOFF_VALIDATIONS).issubset(set(handoff.get("required_validation", []))),
        "worker_constraints": _worker_constraints_complete(handoff),
        "replay_lineage_continuity": candidate["handoff_hash"] == handoff["artifact_hash"],
        "candidate_lineage": packet["candidate_hash"] == candidate["artifact_hash"],
        "packet_lineage": packet["packet_hash"] == _packet_hash(packet),
        "approval_lineage": candidate["approval_hash"] == approval["approval_hash"],
        "authority_boundaries": (
            _authority_boundaries_ok(handoff)
            and _authority_boundaries_ok(candidate)
            and _authority_boundaries_ok(packet)
        ),
        "hash_integrity": candidate["candidate_hash"] == _candidate_hash(candidate),
    }
    if set(handoff.get("allowed_outputs", [])).intersection(handoff.get("forbidden_operations", [])):
        checks["allowed_forbidden_separation"] = False
    else:
        checks["allowed_forbidden_separation"] = True
    if not all(checks.values()):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: readiness validation failed")
    artifact = {
        "artifact_type": EXECUTION_VALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "validation_id": f"{_require_string(readiness_id, 'readiness_id')}:VALIDATION",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "chain_id": candidate["chain_id"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "approval_reference": approval["approval_reference"],
        "approval_hash": approval["approval_hash"],
        "validation_checks": checks,
        "validation_status": "OCS_EXECUTION_READINESS_VALIDATED",
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ready_artifact(
    *,
    readiness_id: str,
    candidate: dict[str, Any],
    packet: dict[str, Any],
    validation: dict[str, Any],
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "dry_run_id": _require_string(readiness_id, "readiness_id"),
        "readiness_id": _require_string(readiness_id, "readiness_id"),
        "execution_status": status,
        "chain_id": candidate["chain_id"],
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "validation_reference": validation["validation_id"],
        "validation_hash": validation["artifact_hash"],
        "approval_status": candidate["approval_status"],
        "approval_reference": candidate["approval_reference"],
        "approval_hash": candidate["approval_hash"],
        "execution_started": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_ready_artifact(
    *,
    readiness_id: str,
    ocs_handoff_replay_reference: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "dry_run_id": readiness_id if isinstance(readiness_id, str) and readiness_id.strip() else "OCS-READINESS-INVALID",
        "readiness_id": readiness_id if isinstance(readiness_id, str) and readiness_id.strip() else "OCS-READINESS-INVALID",
        "execution_status": FAILED_CLOSED,
        "chain_id": None,
        "candidate_reference": None,
        "candidate_hash": None,
        "packet_reference": None,
        "packet_hash": None,
        "validation_reference": None,
        "validation_hash": None,
        "ocs_handoff_replay_reference": ocs_handoff_replay_reference,
        "execution_started": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    candidate: dict[str, Any] | None,
    packet: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    ready: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(ready)
    capture.update(
        {
            "milestone_id": MILESTONE_ID,
            "execution_candidate_artifact": deepcopy(candidate),
            "execution_packet_artifact": deepcopy(packet),
            "execution_validation_artifact": deepcopy(validation),
            "execution_ready_status_artifact": deepcopy(ready),
            "candidate_reference": candidate.get("candidate_id") if candidate else None,
            "packet_reference": packet.get("packet_id") if packet else None,
            "validation_reference": validation.get("validation_id") if validation else None,
            "ocs_execution_readiness_replay_reference": str(replay_path),
            "fail_closed": ready["execution_status"] == FAILED_CLOSED,
            "authorization_created": False,
            "worker_request_created": False,
            "worker_assigned": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_started": False,
            "repair_started": False,
            "retry_started": False,
        }
    )
    capture["ocs_execution_readiness_capture_hash"] = replay_hash(capture)
    return capture


def _validate_handoff_contract(handoff: dict[str, Any]) -> None:
    if handoff.get("handoff_status") != EXECUTION_HANDOFF_CANDIDATE:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: handoff is not a candidate")
    if handoff.get("execution_readiness_status") != "NOT_EXECUTION_READY":
        raise FailClosedRuntimeError("OCS execution readiness failed closed: handoff readiness boundary invalid")
    if handoff.get("human_review_required") is not True or handoff.get("approval_required") is not True:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: approval requirement missing")
    if handoff.get("approval_status") != "PENDING_HUMAN_REVIEW":
        raise FailClosedRuntimeError("OCS execution readiness failed closed: handoff approval boundary invalid")
    if handoff.get("approval_reference") is not None or handoff.get("approval_hash") is not None:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: approval must be downstream")
    if handoff.get("worker_selection_status") != "NOT_SELECTED":
        raise FailClosedRuntimeError("OCS execution readiness failed closed: worker selection boundary invalid")
    if handoff.get("worker_reference") is not None or handoff.get("worker_hash") is not None:
        raise FailClosedRuntimeError("OCS execution readiness failed closed: worker must not be assigned")
    if not _scope_complete(handoff):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: scope incomplete")
    if not _worker_constraints_complete(handoff):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: worker constraints incomplete")
    if not set(REQUIRED_HANDOFF_VALIDATIONS).issubset(set(handoff.get("required_validation", []))):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: validation requirements incomplete")
    if not _authority_boundaries_ok(handoff):
        raise FailClosedRuntimeError("OCS execution readiness failed closed: authority boundary violation")


def _scope_complete(handoff: dict[str, Any]) -> bool:
    scope = handoff.get("execution_candidate_scope")
    return (
        isinstance(scope, dict)
        and bool(scope)
        and _string_list(handoff.get("requested_outcomes"))
        and _string_list(handoff.get("allowed_outputs"))
        and _string_list(handoff.get("forbidden_operations"))
        and _string_list(handoff.get("required_validation"))
    )


def _worker_constraints_complete(handoff: dict[str, Any]) -> bool:
    return (
        handoff.get("worker_selection_required") is True
        and isinstance(handoff.get("candidate_worker_constraints"), dict)
        and bool(handoff["candidate_worker_constraints"])
        and _is_string(handoff.get("target_worker_family"))
        and _string_list(handoff.get("worker_role_requirements"))
        and _string_list(handoff.get("worker_capability_requirements"))
        and _string_list(handoff.get("worker_exclusion_rules"))
        and _string_list(handoff.get("worker_registry_requirements"))
    )


def _authority_boundaries_ok(artifact: dict[str, Any]) -> bool:
    return all(artifact.get(field) is False for field in AUTHORITY_FALSE_FIELDS)


def _validate_authority_boundaries(artifact: dict[str, Any]) -> None:
    if not _authority_boundaries_ok(artifact):
        raise FailClosedRuntimeError("OCS execution readiness replay authority boundary violation")


def _boundary_flags() -> dict[str, bool]:
    return {
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _candidate_hash(candidate: dict[str, Any]) -> str:
    return replay_hash(
        {
            "handoff_reference": candidate.get("handoff_reference"),
            "handoff_hash": candidate.get("handoff_hash"),
            "chain_id": candidate.get("chain_id"),
            "planned_artifacts": candidate.get("planned_artifacts", []),
            "required_resource_roles": candidate.get("required_resource_roles", []),
            "approval_hash": candidate.get("approval_hash"),
            "execution_scope": candidate.get("execution_scope", {}),
            "worker_constraints": candidate.get("worker_constraints", {}),
        }
    )


def _packet_hash(packet: dict[str, Any]) -> str:
    return replay_hash(
        {
            "candidate_reference": packet.get("candidate_reference"),
            "candidate_hash": packet.get("candidate_hash"),
            "execution_contract": packet.get("execution_contract", {}),
            "allowed_outputs": packet.get("allowed_outputs", []),
            "forbidden_operations": packet.get("forbidden_operations", []),
            "required_validations": packet.get("required_validations", []),
            "worker_role_requirements": packet.get("worker_role_requirements", []),
            "worker_constraints": packet.get("worker_constraints", {}),
        }
    )


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS execution readiness replay ordering mismatch")
    _verify_artifact_hash(artifact, "OCS execution readiness artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("OCS execution readiness replay hash mismatch")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_string(item) for item in value)


def _is_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_string(value: Any, label: str) -> str:
    if not _is_string(value):
        raise FailClosedRuntimeError(f"OCS execution readiness failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    reason = str(exc).strip()
    return reason or "OCS execution readiness failed closed"
