"""Replay-visible bounded execution authorization runtime."""

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
    reconstruct_governed_implementation_dry_run_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_execution_readiness_runtime import reconstruct_ocs_execution_readiness_replay
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION = "AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1"
EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1 = "EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1"
EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1 = "EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1"
EXECUTION_AUTHORIZATION_ARTIFACT_V1 = "EXECUTION_AUTHORIZATION_ARTIFACT_V1"
EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1 = "EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1"
EXECUTION_AUTHORIZED = "EXECUTION_AUTHORIZED"
AUTHORIZATION_APPROVED = "AUTHORIZATION_APPROVED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "authorization_request_recorded",
    "authorization_decision_recorded",
    "authorization_artifact_recorded",
    "authorization_result_recorded",
)


def authorize_execution_ready(
    *,
    authorization_id: str,
    execution_ready_replay_reference: str,
    authorizing_actor: str,
    authorized_at: str,
    replay_dir: str | Path,
    authorization_expires_at: str = "NEVER",
) -> dict[str, Any]:
    """Authorize one bounded execution-ready packet without invoking a Worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_execution_ready_lineage(Path(execution_ready_replay_reference))
        request = _authorization_request(
            authorization_id=authorization_id,
            execution_ready_replay_reference=execution_ready_replay_reference,
            lineage=lineage,
            authorizing_actor=authorizing_actor,
            authorized_at=authorized_at,
            authorization_expires_at=authorization_expires_at,
        )
        decision = _authorization_decision(
            authorization_id=authorization_id,
            request=request,
            lineage=lineage,
            authorized_at=authorized_at,
        )
        authorization = _authorization_artifact(
            authorization_id=authorization_id,
            request=request,
            decision=decision,
            lineage=lineage,
            authorizing_actor=authorizing_actor,
            authorized_at=authorized_at,
            authorization_expires_at=authorization_expires_at,
        )
        result = _authorization_result(
            authorization_id=authorization_id,
            request=request,
            decision=decision,
            authorization=authorization,
            authorized_at=authorized_at,
            status=EXECUTION_AUTHORIZED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], decision)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], authorization)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(request, decision, authorization, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            authorization_id=authorization_id,
            execution_ready_replay_reference=execution_ready_replay_reference,
            authorized_at=authorized_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_execution_authorization_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct execution authorization replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("execution authorization replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("execution authorization replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "execution authorization replay artifact")
        wrappers.append(wrapper)

    request = wrappers[0]["artifact"]
    decision = wrappers[1]["artifact"]
    authorization = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if decision.get("authorization_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("execution authorization replay request lineage mismatch")
    if authorization.get("authorization_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("execution authorization replay decision lineage mismatch")
    if result.get("execution_authorization_hash") != authorization["artifact_hash"]:
        raise FailClosedRuntimeError("execution authorization replay authorization lineage mismatch")
    if len({request["chain_id"], decision["chain_id"], authorization["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("execution authorization replay chain mismatch")
    if len(
        {
            request["execution_packet_hash"],
            decision["execution_packet_hash"],
            authorization["execution_packet_hash"],
            result["execution_packet_hash"],
        }
    ) != 1:
        raise FailClosedRuntimeError("execution authorization replay packet lineage mismatch")
    _load_execution_ready_lineage(Path(request["execution_ready_replay_reference"]))
    return {
        "authorization_id": authorization["authorization_id"],
        "authorization_status": result["authorization_status"],
        "chain_id": authorization["chain_id"],
        "execution_packet_reference": authorization["execution_packet_reference"],
        "execution_packet_hash": authorization["execution_packet_hash"],
        "approval_status": authorization["approval_status"],
        "approval_reference": authorization["approval_reference"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "approval_created": False,
        "governance_mutated": False,
        "failure_reason": result["failure_reason"],
    }


def render_execution_authorization_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Execution Authorization",
        "",
        f"Authorization Status: {capture.get('authorization_status')}",
        f"Authorization Reference: {capture.get('authorization_reference')}",
        f"Execution Packet Reference: {capture.get('execution_packet_reference')}",
        f"Replay Reference: {capture.get('execution_authorization_replay_reference')}",
        "",
        "No Worker has been assigned, dispatched, invoked, or executed.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_execution_ready_lineage(replay_path: Path) -> dict[str, dict[str, Any]]:
    try:
        reconstructed = reconstruct_governed_implementation_dry_run_replay(replay_path)
    except FailClosedRuntimeError:
        reconstructed = reconstruct_ocs_execution_readiness_replay(replay_path)
    if reconstructed.get("execution_status") != EXECUTION_READY:
        raise FailClosedRuntimeError("execution authorization failed closed: execution is not ready")
    artifacts: list[dict[str, Any]] = []
    expected = (
        (0, "execution_candidate_recorded", EXECUTION_CANDIDATE_ARTIFACT_V1),
        (1, "execution_packet_recorded", EXECUTION_PACKET_ARTIFACT_V1),
        (2, "execution_validation_recorded", EXECUTION_VALIDATION_ARTIFACT_V1),
        (3, "execution_ready_status_recorded", EXECUTION_READY_STATUS_ARTIFACT_V1),
    )
    for index, step, artifact_type in expected:
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("execution authorization failed closed: replay corruption")
        _verify_artifact_hash(artifact, "execution-ready lineage artifact")
        if artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError("execution authorization failed closed: replay corruption")
        artifacts.append(artifact)
    candidate, packet, validation, ready = artifacts
    checks = (
        candidate.get("artifact_hash") == packet.get("candidate_hash"),
        candidate.get("artifact_hash") == validation.get("candidate_hash"),
        packet.get("artifact_hash") == validation.get("packet_hash"),
        candidate.get("artifact_hash") == ready.get("candidate_hash"),
        packet.get("artifact_hash") == ready.get("packet_hash"),
        validation.get("artifact_hash") == ready.get("validation_hash"),
        candidate.get("chain_id") == packet.get("chain_id"),
        ready.get("execution_status") == EXECUTION_READY,
        ready.get("execution_started") is False,
        candidate.get("approval_hash") == validation.get("approval_hash"),
        candidate.get("approval_status") in {"APPROVED", "APPROVAL_NOT_REQUIRED_FOR_HANDOFF"},
        isinstance(candidate.get("approval_hash"), str) and bool(candidate["approval_hash"].strip()),
    )
    if not all(checks):
        raise FailClosedRuntimeError("execution authorization failed closed: lineage continuity invalid")
    if candidate["approval_status"] == "APPROVED" and not candidate.get("approval_reference"):
        raise FailClosedRuntimeError("execution authorization failed closed: approval missing")
    if packet.get("execution_contract", {}).get("execution_authorized") is not False:
        raise FailClosedRuntimeError("execution authorization failed closed: authority violation")
    if packet.get("execution_contract", {}).get("execution_state") != "NOT_STARTED":
        raise FailClosedRuntimeError("execution authorization failed closed: authority violation")
    return {
        "candidate": candidate,
        "packet": packet,
        "validation": validation,
        "ready": ready,
    }


def _authorization_request(
    *,
    authorization_id: str,
    execution_ready_replay_reference: str,
    lineage: dict[str, dict[str, Any]],
    authorizing_actor: str,
    authorized_at: str,
    authorization_expires_at: str,
) -> dict[str, Any]:
    candidate, packet, validation, ready = (
        lineage["candidate"],
        lineage["packet"],
        lineage["validation"],
        lineage["ready"],
    )
    artifact = {
        "artifact_type": EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_request_id": f"{_require_string(authorization_id, 'authorization_id')}:REQUEST",
        "chain_id": candidate["chain_id"],
        "execution_ready_replay_reference": _require_string(
            execution_ready_replay_reference, "execution_ready_replay_reference"
        ),
        "execution_ready_reference": ready["dry_run_id"],
        "execution_ready_hash": ready["artifact_hash"],
        "execution_validation_reference": validation["validation_id"],
        "execution_validation_hash": validation["artifact_hash"],
        "execution_candidate_reference": candidate["candidate_id"],
        "execution_candidate_hash": candidate["artifact_hash"],
        "execution_packet_reference": packet["packet_id"],
        "execution_packet_hash": packet["artifact_hash"],
        "approval_status": candidate["approval_status"],
        "approval_reference": candidate["approval_reference"],
        "approval_hash": candidate["approval_hash"],
        "requested_scope": {
            "allowed_outputs": deepcopy(packet["allowed_outputs"]),
            "forbidden_operations": deepcopy(packet["forbidden_operations"]),
            "worker_role_requirements": deepcopy(packet["worker_role_requirements"]),
        },
        "requested_authorizing_actor": _require_string(authorizing_actor, "authorizing_actor"),
        "requested_at": _require_string(authorized_at, "authorized_at"),
        "requested_expiry": _require_string(authorization_expires_at, "authorization_expires_at"),
        "request_authoritative": False,
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _authorization_decision(
    *,
    authorization_id: str,
    request: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    authorized_at: str,
) -> dict[str, Any]:
    packet = lineage["packet"]
    checks = {
        "execution_packet_lineage": request["execution_packet_hash"] == packet["artifact_hash"],
        "execution_candidate_lineage": request["execution_candidate_hash"] == lineage["candidate"]["artifact_hash"],
        "handoff_lineage": bool(lineage["candidate"].get("handoff_reference")),
        "approval_lineage": request["approval_hash"] == lineage["candidate"]["approval_hash"],
        "chain_continuity": request["chain_id"] == lineage["candidate"]["chain_id"] == packet["chain_id"],
        "replay_continuity": lineage["ready"]["execution_status"] == EXECUTION_READY,
        "authority_continuity": packet["execution_contract"]["execution_authorized"] is False,
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("execution authorization failed closed: authorization validation failed")
    artifact = {
        "artifact_type": EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_decision_id": f"{_require_string(authorization_id, 'authorization_id')}:DECISION",
        "authorization_request_reference": request["authorization_request_id"],
        "authorization_request_hash": request["artifact_hash"],
        "chain_id": request["chain_id"],
        "execution_packet_reference": request["execution_packet_reference"],
        "execution_packet_hash": request["execution_packet_hash"],
        "approval_status": request["approval_status"],
        "approval_reference": request["approval_reference"],
        "approval_hash": request["approval_hash"],
        "validation_checks": checks,
        "decision_status": AUTHORIZATION_APPROVED,
        "decided_at": _require_string(authorized_at, "authorized_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _authorization_artifact(
    *,
    authorization_id: str,
    request: dict[str, Any],
    decision: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    authorizing_actor: str,
    authorized_at: str,
    authorization_expires_at: str,
) -> dict[str, Any]:
    packet = lineage["packet"]
    artifact = {
        "artifact_type": EXECUTION_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_id": _require_string(authorization_id, "authorization_id"),
        "authorization_status": EXECUTION_AUTHORIZED,
        "authorization_request_reference": request["authorization_request_id"],
        "authorization_request_hash": request["artifact_hash"],
        "authorization_decision_reference": decision["authorization_decision_id"],
        "authorization_decision_hash": decision["artifact_hash"],
        "chain_id": request["chain_id"],
        "execution_ready_reference": request["execution_ready_reference"],
        "execution_ready_hash": request["execution_ready_hash"],
        "execution_candidate_reference": request["execution_candidate_reference"],
        "execution_candidate_hash": request["execution_candidate_hash"],
        "execution_packet_reference": request["execution_packet_reference"],
        "execution_packet_hash": request["execution_packet_hash"],
        "approval_status": request["approval_status"],
        "approval_reference": request["approval_reference"],
        "approval_hash": request["approval_hash"],
        "authorized_scope": {
            "allowed_outputs": deepcopy(packet["allowed_outputs"]),
            "forbidden_operations": deepcopy(packet["forbidden_operations"]),
            "worker_role_requirements": deepcopy(packet["worker_role_requirements"]),
        },
        "authorizing_actor": _require_string(authorizing_actor, "authorizing_actor"),
        "authorized_at": _require_string(authorized_at, "authorized_at"),
        "authorization_expires_at": _require_string(authorization_expires_at, "authorization_expires_at"),
        "authorization_revoked": False,
        "authorization_transferable": False,
        "authorization_recursive": False,
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["authorization_hash"] = _authorization_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _authorization_result(
    *,
    authorization_id: str,
    request: dict[str, Any],
    decision: dict[str, Any],
    authorization: dict[str, Any],
    authorized_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_result_id": f"{_require_string(authorization_id, 'authorization_id')}:RESULT",
        "authorization_status": status,
        "authorization_request_reference": request["authorization_request_id"],
        "authorization_request_hash": request["artifact_hash"],
        "authorization_decision_reference": decision["authorization_decision_id"],
        "authorization_decision_hash": decision["artifact_hash"],
        "execution_authorization_reference": authorization["authorization_id"],
        "execution_authorization_hash": authorization["artifact_hash"],
        "chain_id": authorization["chain_id"],
        "execution_packet_reference": authorization["execution_packet_reference"],
        "execution_packet_hash": authorization["execution_packet_hash"],
        "completed_at": _require_string(authorized_at, "authorized_at"),
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    authorization_id: str,
    execution_ready_replay_reference: str,
    authorized_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_VERSION,
        "authorization_result_id": f"{authorization_id}:RESULT",
        "authorization_status": FAILED_CLOSED,
        "authorization_request_reference": None,
        "authorization_request_hash": None,
        "authorization_decision_reference": None,
        "authorization_decision_hash": None,
        "execution_authorization_reference": None,
        "execution_authorization_hash": None,
        "execution_ready_replay_reference": execution_ready_replay_reference,
        "chain_id": None,
        "execution_packet_reference": None,
        "execution_packet_hash": None,
        "completed_at": authorized_at,
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    request: dict[str, Any] | None,
    decision: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "authorization_request_artifact": deepcopy(request),
            "authorization_decision_artifact": deepcopy(decision),
            "execution_authorization_artifact": deepcopy(authorization),
            "authorization_result_artifact": deepcopy(result),
            "authorization_reference": authorization.get("authorization_id") if authorization else None,
            "approval_status": authorization.get("approval_status") if authorization else None,
            "approval_reference": authorization.get("approval_reference") if authorization else None,
            "execution_authorization_replay_reference": str(replay_path),
            "fail_closed": result["authorization_status"] == FAILED_CLOSED,
        }
    )
    capture["execution_authorization_capture_hash"] = replay_hash(capture)
    return capture


def _boundary_flags() -> dict[str, bool]:
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


def _authorization_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "authorization_id": artifact.get("authorization_id"),
            "chain_id": artifact.get("chain_id"),
            "execution_packet_reference": artifact.get("execution_packet_reference"),
            "execution_packet_hash": artifact.get("execution_packet_hash"),
            "approval_hash": artifact.get("approval_hash"),
            "authorized_scope": artifact.get("authorized_scope", {}),
            "authorizing_actor": artifact.get("authorizing_actor"),
            "authorized_at": artifact.get("authorized_at"),
            "authorization_expires_at": artifact.get("authorization_expires_at"),
        }
    )


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("execution authorization replay ordering mismatch")
    _verify_artifact_hash(artifact, "execution authorization artifact")
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
        raise FailClosedRuntimeError("execution authorization replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("execution authorization replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"execution authorization failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"execution authorization failed closed: {exc}"
