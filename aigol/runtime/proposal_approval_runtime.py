"""Replay-visible Proposal Approval Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_runtime import CREATED, PROPOSAL_RUNTIME_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROPOSAL_APPROVAL_RUNTIME_VERSION = "PROPOSAL_APPROVAL_RUNTIME_V1"
PROPOSAL_APPROVAL_ARTIFACT_V1 = "PROPOSAL_APPROVAL_ARTIFACT_V1"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
EXPIRED = "EXPIRED"
PROPOSAL_APPROVED = "PROPOSAL_APPROVED"
PROPOSAL_REJECTED = "PROPOSAL_REJECTED"
PROPOSAL_APPROVAL_EXPIRED = "PROPOSAL_APPROVAL_EXPIRED"
PROPOSAL_APPROVAL_RETURNED = "PROPOSAL_APPROVAL_RETURNED"

REPLAY_STEPS = ("proposal_approval_decided", "proposal_approval_returned")
VALID_APPROVAL_STATUSES = frozenset({APPROVED, REJECTED, EXPIRED})
VALID_HUMAN_DECISIONS = {
    "APPROVE": APPROVED,
    "APPROVED": APPROVED,
    "REJECT": REJECTED,
    "REJECTED": REJECTED,
    "EXPIRE": EXPIRED,
    "EXPIRED": EXPIRED,
}
FORBIDDEN_FIELDS = frozenset(
    {
        "authorization_decision",
        "execution_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }
)


def decide_proposal_approval(
    *,
    approval_id: str,
    proposal_artifact: dict[str, Any],
    human_decision: str,
    decision_reason: str,
    operator_label: str,
    created_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a human-authorized proposal approval disposition."""

    replay_path = Path(replay_dir)
    _ensure_approval_replay_available(replay_path)
    proposal = _validate_proposal_artifact(proposal_artifact)
    approval_status = _approval_status(human_decision)
    approval = _approval_artifact(
        approval_id=approval_id,
        proposal=proposal,
        human_decision=human_decision,
        approval_status=approval_status,
        decision_reason=decision_reason,
        operator_label=operator_label,
        created_at=created_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], approval)
    returned = _approval_returned(approval)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(approval, returned)


def reconstruct_proposal_approval_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Proposal Approval Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("proposal approval replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("proposal approval replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "proposal approval artifact")
        wrappers.append(wrapper)

    approval = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("approval_reference") != approval["approval_id"]:
        raise FailClosedRuntimeError("proposal approval replay approval reference mismatch")
    if returned.get("approval_hash") != approval["artifact_hash"]:
        raise FailClosedRuntimeError("proposal approval replay approval hash mismatch")
    if returned.get("proposal_reference") != approval["proposal_id"]:
        raise FailClosedRuntimeError("proposal approval replay proposal reference mismatch")
    _validate_approval_artifact(approval)
    return {
        "approval_id": approval["approval_id"],
        "proposal_id": approval["proposal_id"],
        "proposal_hash": approval["proposal_hash"],
        "proposal_status_before": approval["proposal_status_before"],
        "approval_status": approval["approval_status"],
        "human_decision": approval["human_decision"],
        "operator_label": approval["operator_label"],
        "created_at": approval["created_at"],
        "replay_reference": approval["replay_reference"],
        "authority": False,
        "provider_approval": False,
        "worker_approval": False,
        "automatic_approval": False,
        "execution_requested": False,
        "execution_request_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _approval_artifact(
    *,
    approval_id: str,
    proposal: dict[str, Any],
    human_decision: str,
    approval_status: str,
    decision_reason: str,
    operator_label: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROPOSAL_APPROVAL_ARTIFACT_V1,
        "approval_runtime_version": PROPOSAL_APPROVAL_RUNTIME_VERSION,
        "approval_id": _require_string(approval_id, "approval_id"),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "proposal_status_before": proposal["status"],
        "human_decision": _normalize_token(human_decision, "human_decision"),
        "approval_status": approval_status,
        "decision_reason": _normalize_text(decision_reason, "decision_reason"),
        "operator_label": _normalize_text(operator_label, "operator_label"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "authority": False,
        "provider_approval": False,
        "worker_approval": False,
        "automatic_approval": False,
        "execution_requested": False,
        "execution_request_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_approval_artifact(artifact)
    return artifact


def _approval_returned(approval: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(approval, "proposal approval artifact")
    returned = {
        "event_type": PROPOSAL_APPROVAL_RETURNED,
        "approval_reference": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "proposal_reference": approval["proposal_id"],
        "proposal_hash": approval["proposal_hash"],
        "approval_status": approval["approval_status"],
        "replay_reference": approval["replay_reference"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "execution_request_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "reconstruction_metadata": {
            "proposal_reconstructable": True,
            "approval_reconstructable": True,
            "execution_requested": False,
            "execution_request_created": False,
            "provider_invoked": False,
            "worker_invoked": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(approval: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "proposal_approval_artifact": deepcopy(approval),
        "proposal_approval_replay": deepcopy(returned),
    }
    capture["proposal_approval_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_approval_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("proposal approval replay step ordering mismatch")
    _verify_artifact_hash(artifact, "proposal approval artifact")
    event_type = _event_type_for_status(artifact["approval_status"]) if index == 0 else PROPOSAL_APPROVAL_RETURNED
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": event_type,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_proposal_artifact(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("proposal approval failed closed: proposal is required")
    _verify_artifact_hash(proposal, "proposal runtime artifact")
    if proposal.get("artifact_type") != PROPOSAL_RUNTIME_ARTIFACT_V1:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid proposal artifact")
    if proposal.get("status") != CREATED:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid proposal status")
    if proposal.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("proposal approval failed closed: invalid proposal creator")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("proposal approval failed closed: replay visibility missing")
    if proposal.get("authority") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: proposal authority introduced")
    if proposal.get("approval_created") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: duplicate proposal approval marker")
    if proposal.get("execution_requested") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: execution requested")
    if proposal.get("provider_authority") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: provider authority introduced")
    if proposal.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: provider invocation detected")
    if proposal.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: worker invocation detected")
    _require_string(proposal.get("proposal_id"), "proposal_id")
    return deepcopy(proposal)


def _validate_approval_artifact(approval: dict[str, Any]) -> None:
    if approval.get("artifact_type") != PROPOSAL_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid approval artifact")
    if approval.get("proposal_status_before") != CREATED:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid proposal status change")
    if approval.get("approval_status") not in VALID_APPROVAL_STATUSES:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid approval status")
    if VALID_HUMAN_DECISIONS.get(approval.get("human_decision")) != approval.get("approval_status"):
        raise FailClosedRuntimeError("proposal approval failed closed: decision/status mismatch")
    if approval.get("replay_visible") is not True:
        raise FailClosedRuntimeError("proposal approval failed closed: replay visibility missing")
    if approval.get("authority") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: authority introduced")
    if approval.get("provider_approval") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: provider approval introduced")
    if approval.get("worker_approval") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: worker approval introduced")
    if approval.get("automatic_approval") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: automatic approval introduced")
    if approval.get("execution_requested") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: execution requested")
    if approval.get("execution_request_created") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: execution request created")
    if approval.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: provider invocation detected")
    if approval.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("proposal approval failed closed: worker invocation detected")
    if FORBIDDEN_FIELDS.intersection(approval):
        raise FailClosedRuntimeError("proposal approval failed closed: authority-bearing approval")
    _require_string(approval.get("approval_id"), "approval_id")
    _require_string(approval.get("proposal_id"), "proposal_id")
    _require_string(approval.get("proposal_hash"), "proposal_hash")
    _require_string(approval.get("decision_reason"), "decision_reason")
    _require_string(approval.get("operator_label"), "operator_label")
    _require_string(approval.get("created_at"), "created_at")
    _require_string(approval.get("replay_reference"), "replay_reference")


def _approval_status(human_decision: str) -> str:
    decision = _normalize_token(human_decision, "human_decision")
    status = VALID_HUMAN_DECISIONS.get(decision)
    if status is None:
        raise FailClosedRuntimeError("proposal approval failed closed: invalid human decision")
    return status


def _event_type_for_status(status: str) -> str:
    if status == APPROVED:
        return PROPOSAL_APPROVED
    if status == REJECTED:
        return PROPOSAL_REJECTED
    if status == EXPIRED:
        return PROPOSAL_APPROVAL_EXPIRED
    raise FailClosedRuntimeError("proposal approval failed closed: invalid approval status")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("proposal approval replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("proposal approval replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
