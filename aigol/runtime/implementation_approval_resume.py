"""Governed approval resume for implementation handoff creation."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_CREATED,
    create_conversation_to_implementation_handoff,
    reconstruct_conversation_to_implementation_handoff_replay,
)
from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPLEMENTATION_APPROVAL_RESUME_VERSION = "AIGOL_IMPLEMENTATION_APPROVAL_RESUME_V1"
HUMAN_IMPLEMENTATION_APPROVAL_ARTIFACT_V1 = "HUMAN_IMPLEMENTATION_APPROVAL_ARTIFACT_V1"
IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1 = "IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1"
IMPLEMENTATION_APPROVAL_RESUMED = "IMPLEMENTATION_APPROVAL_RESUMED"
APPROVED = "APPROVED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "approval_request_recorded",
    "approval_decision_recorded",
    "approval_resume_recorded",
    "resumed_handoff_recorded",
)


def create_human_implementation_approval(
    *,
    approval_id: str,
    approval_request_artifact: dict[str, Any],
    approving_actor: str,
    approval_timestamp: str,
    approval_expires_at: str = "NEVER",
) -> dict[str, Any]:
    """Create a human approval artifact for a specific approval request."""

    request = deepcopy(approval_request_artifact)
    _verify_artifact_hash(request, "approval request")
    if request.get("approval_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("implementation approval failed closed: approval request is not required")
    artifact = {
        "artifact_type": HUMAN_IMPLEMENTATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_APPROVAL_RESUME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "chain_id": _require_string(request.get("canonical_chain_id"), "chain_id"),
        "approval_scope": _require_string(request.get("approval_scope"), "approval_scope"),
        "approval_request_reference": _require_string(request.get("approval_id"), "approval_request_reference"),
        "approval_request_hash": request["artifact_hash"],
        "proposal_reference": _require_string(request.get("proposal_reference"), "proposal_reference"),
        "proposal_hash": _require_string(request.get("proposal_hash"), "proposal_hash"),
        "approval_status": APPROVED,
        "approval_timestamp": _require_string(approval_timestamp, "approval_timestamp"),
        "approval_expires_at": _require_string(approval_expires_at, "approval_expires_at"),
        "approving_actor": _require_string(approving_actor, "approving_actor"),
        "approval_expired": False,
        "implementation_authorized_for_chain": True,
        "unrelated_work_authorized": False,
        "approval_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }
    artifact["approval_hash"] = _approval_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def resume_implementation_after_approval(
    *,
    resume_id: str,
    approval_required_replay_reference: str,
    human_approval_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resume an approval-required conversation chain into implementation handoff creation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        approval_required = _load_approval_required_execution(Path(approval_required_replay_reference))
        packet = _validate_resume_packet(approval_required)
        approval_request = packet["approval_request_artifact"]
        human_approval = _validate_human_approval(
            human_approval_artifact,
            approval_request=approval_request,
            approval_required=approval_required,
            created_at=created_at,
        )
        handoff = create_conversation_to_implementation_handoff(
            handoff_id=f"{_require_string(resume_id, 'resume_id')}:IMPLEMENTATION-HANDOFF",
            proposal_artifact=packet["proposal_artifact"],
            proposal_contract_validation_artifact=packet["proposal_contract_validation_artifact"],
            context_assembly_artifact=packet["context_assembly_artifact"],
            registry_resolution_artifact=packet["registry_resolution_artifact"],
            provider_necessity_policy_artifact=packet["provider_necessity_policy_artifact"],
            created_at=created_at,
            replay_dir=replay_path / "resumed_handoff",
        )
        if handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
            raise FailClosedRuntimeError(handoff.get("failure_reason") or "implementation approval resume failed closed: handoff failed")
        resume = _resume_artifact(
            resume_id=resume_id,
            approval_required=approval_required,
            packet=packet,
            human_approval=human_approval,
            handoff=handoff,
            created_at=created_at,
            resume_status=IMPLEMENTATION_APPROVAL_RESUMED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], approval_request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], human_approval)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], resume)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], handoff["implementation_handoff_artifact"])
        return _capture(resume, handoff, replay_path)
    except Exception as exc:
        resume = _failed_resume_artifact(
            resume_id=resume_id,
            approval_required_replay_reference=approval_required_replay_reference,
            human_approval_artifact=human_approval_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], resume)
        return _capture(resume, None, replay_path)


def reconstruct_implementation_approval_resume_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct approval-resume replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation approval resume replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation approval resume replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "implementation approval resume replay artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    approval = wrappers[1]["artifact"]
    resume = wrappers[2]["artifact"]
    handoff = wrappers[3]["artifact"]
    if resume["approval_request_hash"] != request["artifact_hash"]:
        raise FailClosedRuntimeError("implementation approval resume replay approval request mismatch")
    if resume["approval_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("implementation approval resume replay approval decision mismatch")
    if resume["handoff_hash"] != handoff["artifact_hash"]:
        raise FailClosedRuntimeError("implementation approval resume replay handoff mismatch")
    if approval["chain_id"] != resume["chain_id"]:
        raise FailClosedRuntimeError("implementation approval resume replay chain mismatch")
    reconstructed_handoff = reconstruct_conversation_to_implementation_handoff_replay(resume["handoff_replay_reference"])
    if reconstructed_handoff["handoff_id"] != resume["handoff_reference"]:
        raise FailClosedRuntimeError("implementation approval resume replay handoff lineage mismatch")
    return {
        "resume_id": resume["resume_id"],
        "resume_status": resume["resume_status"],
        "chain_id": resume["chain_id"],
        "approval_id": resume["approval_id"],
        "approval_scope": resume["approval_scope"],
        "handoff_status": resume["handoff_status"],
        "handoff_reference": resume["handoff_reference"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "failure_reason": resume["failure_reason"],
    }


def render_implementation_approval_resume_summary(capture: dict[str, Any]) -> str:
    lines = [
        f"approval_resume_status: {capture.get('resume_status')}",
        f"chain_id: {capture.get('chain_id')}",
        f"approval_id: {capture.get('approval_id')}",
        f"approval_scope: {capture.get('approval_scope')}",
        f"handoff_status: {capture.get('handoff_status')}",
        f"handoff_reference: {capture.get('handoff_reference')}",
        f"replay_reference: {capture.get('implementation_approval_resume_replay_reference')}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_approval_required_execution(replay_path: Path) -> dict[str, Any]:
    wrapper = load_json(replay_path / "000_conversation_to_ppp_handoff_execution_recorded.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation approval resume failed closed: invalid approval-required replay")
    _verify_artifact_hash(artifact, "approval-required conversation handoff")
    if artifact.get("terminal_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval missing")
    return artifact


def _validate_resume_packet(approval_required: dict[str, Any]) -> dict[str, Any]:
    packet = approval_required.get("approval_resume_packet")
    if not isinstance(packet, dict):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval missing")
    expected = deepcopy(packet)
    actual = expected.pop("packet_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("implementation approval resume failed closed: replay corruption detected")
    checks = (
        ("context_assembly_artifact", "context_hash"),
        ("registry_resolution_artifact", "registry_hash"),
        ("provider_necessity_policy_artifact", "policy_hash"),
        ("provider_proposal_production_artifact", "proposal_production_hash"),
        ("proposal_artifact", "proposal_hash"),
        ("proposal_contract_validation_artifact", "proposal_validation_hash"),
        ("approval_request_artifact", "approval_request_hash"),
    )
    for artifact_key, hash_key in checks:
        artifact = packet.get(artifact_key)
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation approval resume failed closed: replay corruption detected")
        _verify_artifact_hash(artifact, artifact_key)
        if packet.get(hash_key) != artifact["artifact_hash"]:
            raise FailClosedRuntimeError("implementation approval resume failed closed: replay corruption detected")
    if packet["approval_request_artifact"].get("artifact_hash") != approval_required.get("approval_hash"):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval lineage invalid")
    return deepcopy(packet)


def _validate_human_approval(
    approval: dict[str, Any],
    *,
    approval_request: dict[str, Any],
    approval_required: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval missing")
    if approval.get("artifact_type") != HUMAN_IMPLEMENTATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval missing")
    _verify_artifact_hash(approval, "human implementation approval")
    if approval.get("approval_status") != APPROVED:
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval missing")
    if approval.get("chain_id") != approval_required.get("canonical_chain_id"):
        raise FailClosedRuntimeError("implementation approval resume failed closed: chain mismatch")
    if approval.get("approval_scope") != approval_required.get("approval_scope"):
        raise FailClosedRuntimeError("implementation approval resume failed closed: scope mismatch")
    if approval.get("approval_request_hash") != approval_request.get("artifact_hash"):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval lineage invalid")
    if approval.get("proposal_hash") != approval_required.get("approval_resume_packet", {}).get("proposal_hash"):
        raise FailClosedRuntimeError("implementation approval resume failed closed: proposal lineage invalid")
    if approval.get("approval_hash") != _approval_hash(approval):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval lineage invalid")
    if approval.get("approval_expired") is True or _is_expired(approval.get("approval_expires_at"), created_at):
        raise FailClosedRuntimeError("implementation approval resume failed closed: approval expired")
    return deepcopy(approval)


def _resume_artifact(
    *,
    resume_id: str,
    approval_required: dict[str, Any],
    packet: dict[str, Any],
    human_approval: dict[str, Any],
    handoff: dict[str, Any],
    created_at: str,
    resume_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    handoff_artifact = handoff["implementation_handoff_artifact"]
    artifact = {
        "artifact_type": IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_APPROVAL_RESUME_VERSION,
        "resume_id": _require_string(resume_id, "resume_id"),
        "resume_status": resume_status,
        "chain_id": approval_required["canonical_chain_id"],
        "approval_required_reference": approval_required["execution_id"],
        "approval_required_hash": approval_required["artifact_hash"],
        "approval_request_reference": packet["approval_request_artifact"]["approval_id"],
        "approval_request_hash": packet["approval_request_artifact"]["artifact_hash"],
        "approval_id": human_approval["approval_id"],
        "approval_hash": human_approval["artifact_hash"],
        "approval_scope": human_approval["approval_scope"],
        "approval_timestamp": human_approval["approval_timestamp"],
        "approving_actor": human_approval["approving_actor"],
        "proposal_reference": packet["proposal_artifact"]["proposal_id"],
        "proposal_hash": packet["proposal_artifact"]["artifact_hash"],
        "proposal_validation_hash": packet["proposal_contract_validation_artifact"]["artifact_hash"],
        "handoff_status": handoff["handoff_status"],
        "handoff_reference": handoff_artifact["handoff_id"],
        "handoff_hash": handoff_artifact["artifact_hash"],
        "handoff_replay_reference": handoff["implementation_handoff_replay_reference"],
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "approval_created": False,
        "approval_modified": False,
        "implementation_authorized_for_unrelated_work": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resume_artifact(
    *,
    resume_id: str,
    approval_required_replay_reference: str,
    human_approval_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPLEMENTATION_APPROVAL_RESUME_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_APPROVAL_RESUME_VERSION,
        "resume_id": resume_id,
        "resume_status": FAILED_CLOSED,
        "chain_id": human_approval_artifact.get("chain_id") if isinstance(human_approval_artifact, dict) else None,
        "approval_required_reference": approval_required_replay_reference,
        "approval_required_hash": None,
        "approval_request_reference": None,
        "approval_request_hash": None,
        "approval_id": human_approval_artifact.get("approval_id") if isinstance(human_approval_artifact, dict) else None,
        "approval_hash": None,
        "approval_scope": human_approval_artifact.get("approval_scope") if isinstance(human_approval_artifact, dict) else None,
        "approval_timestamp": human_approval_artifact.get("approval_timestamp") if isinstance(human_approval_artifact, dict) else None,
        "approving_actor": human_approval_artifact.get("approving_actor") if isinstance(human_approval_artifact, dict) else None,
        "proposal_reference": None,
        "proposal_hash": None,
        "proposal_validation_hash": None,
        "handoff_status": None,
        "handoff_reference": None,
        "handoff_hash": None,
        "handoff_replay_reference": None,
        "created_at": created_at,
        "replay_visible": True,
        "approval_created": False,
        "approval_modified": False,
        "implementation_authorized_for_unrelated_work": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(resume: dict[str, Any], handoff: dict[str, Any] | None, replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(resume)
    capture.update(
        {
            "implementation_approval_resume_artifact": deepcopy(resume),
            "implementation_handoff_artifact": deepcopy(handoff["implementation_handoff_artifact"]) if handoff else None,
            "implementation_handoff_replay_reference": handoff.get("implementation_handoff_replay_reference")
            if handoff
            else None,
            "implementation_approval_resume_replay_reference": str(replay_path),
            "fail_closed": resume["resume_status"] == FAILED_CLOSED,
        }
    )
    capture["implementation_approval_resume_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("implementation approval resume replay ordering mismatch")
    _verify_artifact_hash(artifact, "implementation approval resume replay artifact")
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


def _is_expired(expires_at: Any, created_at: str) -> bool:
    if expires_at == "NEVER":
        return False
    if not isinstance(expires_at, str) or not expires_at.strip():
        return True
    try:
        return _parse_time(expires_at) < _parse_time(created_at)
    except ValueError:
        return True


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _approval_hash(approval: dict[str, Any]) -> str:
    return replay_hash(
        {
            "approval_id": approval.get("approval_id"),
            "chain_id": approval.get("chain_id"),
            "approval_scope": approval.get("approval_scope"),
            "approval_request_reference": approval.get("approval_request_reference"),
            "approval_request_hash": approval.get("approval_request_hash"),
            "proposal_hash": approval.get("proposal_hash"),
            "approval_status": approval.get("approval_status"),
            "approval_timestamp": approval.get("approval_timestamp"),
            "approval_expires_at": approval.get("approval_expires_at"),
            "approving_actor": approval.get("approving_actor"),
        }
    )


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("implementation approval resume replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("implementation approval resume replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation approval resume failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    reason = str(exc).strip()
    return reason or "implementation approval resume failed closed"
