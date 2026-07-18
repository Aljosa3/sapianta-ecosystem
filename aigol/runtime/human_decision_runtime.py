"""Replay-visible human decision runtime for approval-required operations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_HUMAN_DECISION_RUNTIME_VERSION = "AIGOL_HUMAN_DECISION_RUNTIME_V1"
HUMAN_DECISION_ARTIFACT_V1 = "HUMAN_DECISION_ARTIFACT_V1"
HUMAN_DECISION_RETURNED_V1 = "HUMAN_DECISION_RETURNED_V1"
HUMAN_DECISION_RECORDED = "HUMAN_DECISION_RECORDED"
APPROVE = "APPROVE"
REJECT = "REJECT"
REQUEST_MODIFICATION = "REQUEST_MODIFICATION"
GOVERNED_REJECTION_RECORDED = "GOVERNED_REJECTION_RECORDED"
MODIFICATION_REQUEST_RECORDED = "MODIFICATION_REQUEST_RECORDED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

VALID_DECISIONS = frozenset({APPROVE, REJECT, REQUEST_MODIFICATION})
REPLAY_STEPS = ("human_decision_recorded", "human_decision_returned")


def record_human_decision(
    *,
    human_decision_id: str,
    approval_required_artifact: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a human decision for a HUMAN_APPROVAL_REQUIRED operation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        approval_required = _validate_approval_required(approval_required_artifact)
        artifact = _decision_artifact(
            human_decision_id=human_decision_id,
            approval_required=approval_required,
            decision=decision,
            decision_reason=decision_reason,
            decided_by=decided_by,
            decided_at=decided_at,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_decision_artifact(
            human_decision_id=human_decision_id,
            approval_required_artifact=approval_required_artifact,
            decision=decision,
            decision_reason=decision_reason,
            decided_by=decided_by,
            decided_at=decided_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_human_decision_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct human decision replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human decision replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human decision replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "human decision artifact")
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("human_decision_reference") != decision["human_decision_id"]:
        raise FailClosedRuntimeError("human decision replay reference mismatch")
    if returned.get("human_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("human decision replay hash mismatch")
    if returned.get("chain_id") != decision["chain_id"]:
        raise FailClosedRuntimeError("human decision replay chain mismatch")
    return {
        "human_decision_id": decision["human_decision_id"],
        "decision_status": decision["decision_status"],
        "decision": decision["decision"],
        "chain_id": decision["chain_id"],
        "approval_scope": decision["approval_scope"],
        "terminal_status": decision["terminal_status"],
        "clarification_required": decision["clarification_required"],
        "implementation_authorized": decision["implementation_authorized"],
        "implementation_authorization_allowed": decision.get(
            "implementation_authorization_allowed", True
        ),
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": decision["failure_reason"],
    }


def render_human_decision_summary(capture: dict[str, Any]) -> str:
    lines = [
        "Human Decision",
        "",
        f"Decision Status: {capture.get('decision_status')}",
        f"Decision: {capture.get('decision')}",
        f"Terminal Status: {capture.get('terminal_status')}",
        f"Approval Scope: {capture.get('approval_scope')}",
        f"Human Decision Reference: {capture.get('human_decision_id')}",
        f"Replay Reference: {capture.get('human_decision_replay_reference')}",
    ]
    if capture.get("clarification_required"):
        lines.append("Clarification State: REQUIRED")
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def normalize_human_decision(value: str) -> str:
    token = value.strip().upper().replace(" ", "_").replace("-", "_").rstrip(".")
    aliases = {
        "APPROVED": APPROVE,
        "APPROVE": APPROVE,
        "YES": APPROVE,
        "REJECTED": REJECT,
        "REJECT": REJECT,
        "NO": REJECT,
        "REQUEST_CHANGES": REQUEST_MODIFICATION,
        "REQUEST_CHANGE": REQUEST_MODIFICATION,
        "REQUEST_MODIFICATION": REQUEST_MODIFICATION,
        "MODIFY": REQUEST_MODIFICATION,
        "MODIFICATION": REQUEST_MODIFICATION,
    }
    return aliases.get(token, token)


def _validate_approval_required(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval-required artifact missing")
    _verify_artifact_hash(artifact, "approval-required artifact")
    if artifact.get("terminal_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("human decision failed closed: approval is not pending")
    packet = artifact.get("approval_resume_packet")
    if not isinstance(packet, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval packet missing")
    expected = deepcopy(packet)
    actual = expected.pop("packet_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human decision failed closed: approval packet hash mismatch")
    request = packet.get("approval_request_artifact")
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval request missing")
    _verify_artifact_hash(request, "approval request")
    if request.get("approval_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("human decision failed closed: approval request is not pending")
    if (
        "implementation_authorization_allowed" in request
        and not isinstance(request["implementation_authorization_allowed"], bool)
    ):
        raise FailClosedRuntimeError(
            "human decision failed closed: implementation authority boundary is malformed"
        )
    if request.get("artifact_hash") != artifact.get("approval_hash"):
        raise FailClosedRuntimeError("human decision failed closed: approval lineage mismatch")
    return deepcopy(artifact)


def _decision_artifact(
    *,
    human_decision_id: str,
    approval_required: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
) -> dict[str, Any]:
    normalized_decision = normalize_human_decision(_require_string(decision, "decision"))
    if normalized_decision not in VALID_DECISIONS:
        raise FailClosedRuntimeError("human decision failed closed: invalid decision")
    return _base_decision_artifact(
        human_decision_id=human_decision_id,
        approval_required=approval_required,
        decision=normalized_decision,
        decision_reason=decision_reason,
        decided_by=decided_by,
        decided_at=decided_at,
        failure_reason=None,
    )


def _failed_decision_artifact(
    *,
    human_decision_id: str,
    approval_required_artifact: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION,
        "human_decision_id": human_decision_id,
        "decision_status": FAILED_CLOSED,
        "decision": normalize_human_decision(decision) if isinstance(decision, str) else None,
        "decision_reason": decision_reason if isinstance(decision_reason, str) else "",
        "decision_reason_hash": replay_hash(decision_reason) if isinstance(decision_reason, str) else None,
        "chain_id": approval_required_artifact.get("canonical_chain_id") if isinstance(approval_required_artifact, dict) else None,
        "approval_required_reference": approval_required_artifact.get("execution_id") if isinstance(approval_required_artifact, dict) else None,
        "approval_required_hash": approval_required_artifact.get("artifact_hash") if isinstance(approval_required_artifact, dict) else None,
        "approval_request_reference": None,
        "approval_request_hash": None,
        "approval_scope": approval_required_artifact.get("approval_scope") if isinstance(approval_required_artifact, dict) else None,
        "proposal_reference": None,
        "proposal_hash": None,
        "terminal_status": FAILED_CLOSED,
        "clarification_required": False,
        "implementation_authorized": False,
        "implementation_rejected": False,
        "modification_requested": False,
        "decided_by": decided_by if isinstance(decided_by, str) else "",
        "decided_at": decided_at if isinstance(decided_at, str) else "",
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _base_decision_artifact(
    *,
    human_decision_id: str,
    approval_required: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    packet = approval_required["approval_resume_packet"]
    request = packet["approval_request_artifact"]
    implementation_authorization_allowed = request.get(
        "implementation_authorization_allowed", True
    )
    status_by_decision = {
        APPROVE: HUMAN_DECISION_RECORDED,
        REJECT: GOVERNED_REJECTION_RECORDED,
        REQUEST_MODIFICATION: MODIFICATION_REQUEST_RECORDED,
    }
    terminal_by_decision = {
        APPROVE: "APPROVAL_DECISION_RECORDED",
        REJECT: "GOVERNED_REJECTION_TERMINATED",
        REQUEST_MODIFICATION: CLARIFICATION_REQUIRED,
    }
    artifact = {
        "artifact_type": HUMAN_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION,
        "human_decision_id": _require_string(human_decision_id, "human_decision_id"),
        "decision_status": status_by_decision[decision],
        "decision": decision,
        "decision_reason": _require_string(decision_reason, "decision_reason"),
        "decision_reason_hash": replay_hash(decision_reason),
        "chain_id": approval_required["canonical_chain_id"],
        "approval_required_reference": approval_required["execution_id"],
        "approval_required_hash": approval_required["artifact_hash"],
        "approval_request_reference": request["approval_id"],
        "approval_request_hash": request["artifact_hash"],
        "approval_scope": request["approval_scope"],
        "proposal_reference": request["proposal_reference"],
        "proposal_hash": request["proposal_hash"],
        "terminal_status": terminal_by_decision[decision],
        "clarification_required": decision == REQUEST_MODIFICATION,
        "implementation_authorized": (
            decision == APPROVE and implementation_authorization_allowed
        ),
        "implementation_rejected": (
            decision == REJECT and implementation_authorization_allowed
        ),
        "modification_requested": decision == REQUEST_MODIFICATION,
        "decided_by": _require_string(decided_by, "decided_by"),
        "decided_at": _require_string(decided_at, "decided_at"),
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    if "implementation_authorization_allowed" in request:
        artifact["implementation_authorization_allowed"] = (
            implementation_authorization_allowed
        )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(decision: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(decision, "human decision artifact")
    artifact = {
        "artifact_type": HUMAN_DECISION_RETURNED_V1,
        "event_type": "HUMAN_DECISION_RETURNED",
        "human_decision_reference": decision["human_decision_id"],
        "human_decision_hash": decision["artifact_hash"],
        "decision_status": decision["decision_status"],
        "decision": decision["decision"],
        "chain_id": decision["chain_id"],
        "approval_scope": decision["approval_scope"],
        "terminal_status": decision["terminal_status"],
        "clarification_required": decision["clarification_required"],
        "implementation_authorized": decision["implementation_authorized"],
        "implementation_rejected": decision["implementation_rejected"],
        "modification_requested": decision["modification_requested"],
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": decision["failure_reason"],
    }
    if "implementation_authorization_allowed" in decision:
        artifact["implementation_authorization_allowed"] = decision[
            "implementation_authorization_allowed"
        ]
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(decision: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(decision)
    capture.update(
        {
            "human_decision_artifact": deepcopy(decision),
            "human_decision_replay": deepcopy(returned),
            "human_decision_replay_reference": str(replay_path),
            "fail_closed": decision["decision_status"] == FAILED_CLOSED,
        }
    )
    capture["human_decision_capture_hash"] = replay_hash(capture)
    return capture


def _authority_boundaries() -> dict[str, bool]:
    return {
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_modified": False,
        "automatic_approval": False,
        "provider_authority": False,
        "worker_authority": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human decision replay ordering mismatch")
    _verify_artifact_hash(artifact, "human decision artifact")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
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
        raise FailClosedRuntimeError("human decision replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("human decision replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"human decision failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return str(exc) or "human decision failed closed"
