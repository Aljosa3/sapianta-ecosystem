"""Non-executing governed implementation preparation dry run."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_CREATED,
    reconstruct_conversation_to_implementation_handoff_replay,
)
from aigol.runtime.implementation_approval_resume import (
    IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1,
    IMPLEMENTATION_APPROVAL_RESUMED,
)
from aigol.runtime.implementation_handoff_visibility import (
    IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_SUMMARY_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION = "AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_V1"
EXECUTION_CANDIDATE_ARTIFACT_V1 = "EXECUTION_CANDIDATE_ARTIFACT_V1"
EXECUTION_PACKET_ARTIFACT_V1 = "EXECUTION_PACKET_ARTIFACT_V1"
EXECUTION_VALIDATION_ARTIFACT_V1 = "EXECUTION_VALIDATION_ARTIFACT_V1"
EXECUTION_READY_STATUS_ARTIFACT_V1 = "EXECUTION_READY_STATUS_ARTIFACT_V1"
EXECUTION_READY = "EXECUTION_READY"
FAILED_CLOSED = "FAILED_CLOSED"

CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1 = "CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1"

FORBIDDEN_OPERATIONS = (
    "INVOKE_WORKER",
    "INVOKE_CODEX",
    "INVOKE_CLAUDE_CODE",
    "CREATE_FILE",
    "CREATE_CODE",
    "DISPATCH_EXECUTION",
    "AUTHORIZE_EXECUTION",
    "MUTATE_GOVERNANCE",
    "MUTATE_EXISTING_REPLAY",
)

REQUIRED_VALIDATIONS = (
    "CHAIN_CONTINUITY",
    "HANDOFF_LINEAGE",
    "APPROVAL_LINEAGE",
    "CANDIDATE_LINEAGE",
    "PACKET_LINEAGE",
    "AUTHORITY_BOUNDARIES",
    "REPLAY_CONTINUITY",
    "HASH_INTEGRITY",
)

REPLAY_STEPS = (
    "execution_candidate_recorded",
    "execution_packet_recorded",
    "execution_validation_recorded",
    "execution_ready_status_recorded",
)


def prepare_governed_implementation_dry_run(
    *,
    dry_run_id: str,
    handoff_replay_reference: str,
    handoff_visibility_artifact: dict[str, Any],
    upstream_lineage_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Convert a certified implementation handoff into a non-executing execution-ready packet."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        handoff = _load_handoff(Path(_require_string(handoff_replay_reference, "handoff_replay_reference")))
        visibility = _validate_visibility(handoff_visibility_artifact, handoff)
        lineage = _validate_upstream_lineage(upstream_lineage_artifact, handoff)
        candidate = _candidate_artifact(
            dry_run_id=dry_run_id,
            handoff=handoff,
            visibility=visibility,
            lineage=lineage,
            created_at=created_at,
        )
        packet = _packet_artifact(dry_run_id=dry_run_id, candidate=candidate, created_at=created_at)
        validation = _validation_artifact(
            dry_run_id=dry_run_id,
            handoff=handoff,
            visibility=visibility,
            lineage=lineage,
            candidate=candidate,
            packet=packet,
            created_at=created_at,
        )
        ready = _ready_artifact(
            dry_run_id=dry_run_id,
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
        ready = _failed_ready_artifact(dry_run_id=dry_run_id, created_at=created_at, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], ready)
        return _capture(None, None, None, ready, replay_path)


def reconstruct_governed_implementation_dry_run_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct governed implementation dry-run replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governed implementation dry run replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed implementation dry run replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "governed implementation dry run replay artifact")
        wrappers.append(wrapper)
    candidate = wrappers[0]["artifact"]
    packet = wrappers[1]["artifact"]
    validation = wrappers[2]["artifact"]
    ready = wrappers[3]["artifact"]
    if packet["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run replay candidate lineage mismatch")
    if validation["candidate_hash"] != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run replay validation candidate mismatch")
    if validation["packet_hash"] != packet["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run replay packet lineage mismatch")
    if ready["validation_hash"] != validation["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run replay validation lineage mismatch")
    if candidate["candidate_hash"] != _candidate_hash(candidate):
        raise FailClosedRuntimeError("governed implementation dry run candidate hash mismatch")
    if packet["packet_hash"] != _packet_hash(packet):
        raise FailClosedRuntimeError("governed implementation dry run packet hash mismatch")
    handoff = _load_handoff(_resolve_replay_reference(candidate["handoff_replay_reference"], anchor=replay_path))
    if handoff["handoff_id"] != candidate["handoff_reference"]:
        raise FailClosedRuntimeError("governed implementation dry run handoff continuity mismatch")
    return {
        "dry_run_id": ready["dry_run_id"],
        "execution_status": ready["execution_status"],
        "chain_id": candidate["chain_id"],
        "handoff_reference": candidate["handoff_reference"],
        "candidate_reference": candidate["candidate_id"],
        "packet_reference": packet["packet_id"],
        "validation_reference": validation["validation_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "failure_reason": ready["failure_reason"],
    }


def render_governed_implementation_dry_run_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Execution Preparation",
        "",
        f"Execution Status: {capture.get('execution_status')}",
        f"Candidate Reference: {capture.get('candidate_reference')}",
        f"Packet Reference: {capture.get('packet_reference')}",
        f"Validation Reference: {capture.get('validation_reference')}",
        f"Replay Reference: {capture.get('governed_implementation_dry_run_replay_reference')}",
        "",
        "Execution has not started.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _resolve_replay_reference(reference: Any, *, anchor: Path) -> Path:
    replay_path = Path(_require_string(reference, "replay_reference"))
    if replay_path.is_absolute() or replay_path.exists():
        return replay_path
    for parent in (anchor, *anchor.parents):
        candidate = parent / replay_path
        if candidate.exists():
            return candidate
    return replay_path


def _load_handoff(replay_path: Path) -> dict[str, Any]:
    wrapper = load_json(replay_path / "000_implementation_handoff_created.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: invalid handoff lineage")
    _verify_artifact_hash(artifact, "implementation handoff")
    if artifact.get("artifact_type") != IMPLEMENTATION_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: invalid handoff lineage")
    if artifact.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff not created")
    reconstructed = reconstruct_conversation_to_implementation_handoff_replay(replay_path)
    if reconstructed.get("handoff_id") != artifact["handoff_id"]:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
    return artifact


def _validate_visibility(visibility_artifact: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(visibility_artifact, dict):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff visibility missing")
    visibility = deepcopy(visibility_artifact)
    _verify_artifact_hash(visibility, "implementation handoff visibility")
    if visibility.get("artifact_type") != IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: invalid handoff visibility")
    if visibility.get("summary_status") != IMPLEMENTATION_HANDOFF_SUMMARY_CREATED:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: invalid handoff visibility")
    if visibility.get("handoff_reference") != handoff["handoff_id"]:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
    if visibility.get("handoff_artifact_hash") != handoff["artifact_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
    if visibility.get("handoff_hash") != handoff["handoff_hash"]:
        raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
    if not _string_list(visibility.get("planned_artifacts")):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: artifact plan invalid")
    if not _string_list(visibility.get("required_resource_roles")):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: resource roles invalid")
    return visibility


def _validate_upstream_lineage(upstream_artifact: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(upstream_artifact, dict):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: approval lineage missing")
    upstream = deepcopy(upstream_artifact)
    _verify_artifact_hash(upstream, "implementation upstream lineage")
    artifact_type = upstream.get("artifact_type")
    if artifact_type == CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1:
        if upstream.get("terminal_status") != IMPLEMENTATION_HANDOFF_CREATED:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
        if upstream.get("handoff_reference") != handoff["handoff_id"]:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
        if upstream.get("handoff_hash") != handoff["handoff_hash"]:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
        return {
            "chain_id": upstream["canonical_chain_id"],
            "approval_status": upstream["approval_status"],
            "approval_reference": None,
            "approval_hash": upstream["approval_hash"],
            "upstream_reference": upstream["execution_id"],
            "upstream_hash": upstream["artifact_hash"],
        }
    if artifact_type == IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1:
        if upstream.get("resume_status") != IMPLEMENTATION_APPROVAL_RESUMED:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: approval lineage invalid")
        if upstream.get("handoff_reference") != handoff["handoff_id"]:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
        if upstream.get("handoff_hash") != handoff["artifact_hash"]:
            raise FailClosedRuntimeError("governed implementation dry run failed closed: handoff lineage invalid")
        return {
            "chain_id": upstream["chain_id"],
            "approval_status": "APPROVED",
            "approval_reference": upstream["approval_id"],
            "approval_hash": upstream["approval_hash"],
            "upstream_reference": upstream["resume_id"],
            "upstream_hash": upstream["artifact_hash"],
        }
    raise FailClosedRuntimeError("governed implementation dry run failed closed: approval lineage invalid")


def _candidate_artifact(
    *,
    dry_run_id: str,
    handoff: dict[str, Any],
    visibility: dict[str, Any],
    lineage: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION,
        "candidate_id": f"{_require_string(dry_run_id, 'dry_run_id')}:CANDIDATE",
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "handoff_replay_reference": visibility["handoff_replay_reference"],
        "chain_id": lineage["chain_id"],
        "target_domain": visibility["target_domain"],
        "target_resource": visibility["target_resource"],
        "target_worker": visibility["target_worker"],
        "planned_artifacts": deepcopy(visibility["planned_artifacts"]),
        "required_resource_roles": deepcopy(visibility["required_resource_roles"]),
        "approval_status": lineage["approval_status"],
        "approval_reference": lineage["approval_reference"],
        "approval_hash": lineage["approval_hash"],
        "upstream_lineage_reference": lineage["upstream_reference"],
        "upstream_lineage_hash": lineage["upstream_hash"],
        "execution_scope": {
            "mode": "PREPARATION_ONLY",
            "allowed_outputs": deepcopy(visibility["planned_artifacts"]),
            "execution_authorized": False,
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
    }
    artifact["candidate_hash"] = _candidate_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _packet_artifact(*, dry_run_id: str, candidate: dict[str, Any], created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_PACKET_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION,
        "packet_id": f"{_require_string(dry_run_id, 'dry_run_id')}:PACKET",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "chain_id": candidate["chain_id"],
        "execution_contract": {
            "contract_type": "BOUNDED_IMPLEMENTATION_PREPARATION",
            "execution_state": "NOT_STARTED",
            "execution_authorized": False,
            "preparation_only": True,
        },
        "allowed_outputs": deepcopy(candidate["planned_artifacts"]),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "required_validations": list(REQUIRED_VALIDATIONS),
        "worker_role_requirements": deepcopy(candidate["required_resource_roles"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
    }
    artifact["packet_hash"] = _packet_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    dry_run_id: str,
    handoff: dict[str, Any],
    visibility: dict[str, Any],
    lineage: dict[str, Any],
    candidate: dict[str, Any],
    packet: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    checks = {
        "chain_continuity": candidate["chain_id"] == packet["chain_id"] == lineage["chain_id"],
        "handoff_lineage": candidate["handoff_reference"] == handoff["handoff_id"],
        "approval_lineage": candidate["approval_hash"] == lineage["approval_hash"],
        "candidate_lineage": packet["candidate_hash"] == candidate["artifact_hash"],
        "packet_lineage": packet["packet_hash"] == _packet_hash(packet),
        "authority_boundaries": all(
            candidate[field] is False and packet[field] is False
            for field in (
                "worker_invoked",
                "code_generated",
                "files_created",
                "execution_requested",
                "dispatch_requested",
                "authorization_created",
                "governance_mutated",
            )
        ),
        "replay_continuity": visibility["handoff_replay_reference"] == candidate["handoff_replay_reference"],
        "hash_integrity": candidate["candidate_hash"] == _candidate_hash(candidate),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("governed implementation dry run failed closed: execution validation failed")
    artifact = {
        "artifact_type": EXECUTION_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION,
        "validation_id": f"{_require_string(dry_run_id, 'dry_run_id')}:VALIDATION",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "approval_reference": lineage["approval_reference"],
        "approval_hash": lineage["approval_hash"],
        "validation_checks": checks,
        "validation_status": "EXECUTION_PREPARATION_VALIDATED",
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ready_artifact(
    *,
    dry_run_id: str,
    candidate: dict[str, Any],
    packet: dict[str, Any],
    validation: dict[str, Any],
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION,
        "dry_run_id": _require_string(dry_run_id, "dry_run_id"),
        "execution_status": status,
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "validation_reference": validation["validation_id"],
        "validation_hash": validation["artifact_hash"],
        "execution_started": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_ready_artifact(*, dry_run_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_VERSION,
        "dry_run_id": dry_run_id,
        "execution_status": FAILED_CLOSED,
        "candidate_reference": None,
        "candidate_hash": None,
        "packet_reference": None,
        "packet_hash": None,
        "validation_reference": None,
        "validation_hash": None,
        "execution_started": False,
        "created_at": created_at,
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
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
            "execution_candidate_artifact": deepcopy(candidate),
            "execution_packet_artifact": deepcopy(packet),
            "execution_validation_artifact": deepcopy(validation),
            "execution_ready_status_artifact": deepcopy(ready),
            "governed_implementation_dry_run_replay_reference": str(replay_path),
            "fail_closed": ready["execution_status"] == FAILED_CLOSED,
        }
    )
    capture["governed_implementation_dry_run_capture_hash"] = replay_hash(capture)
    return capture


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
        }
    )


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governed implementation dry run replay ordering mismatch")
    _verify_artifact_hash(artifact, "governed implementation dry run artifact")
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
        raise FailClosedRuntimeError("governed implementation dry run replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("governed implementation dry run replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed implementation dry run failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    reason = str(exc).strip()
    return reason or "governed implementation dry run failed closed"
