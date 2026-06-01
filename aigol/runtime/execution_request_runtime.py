"""Replay-visible Execution Request Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import APPROVED, PROPOSAL_APPROVAL_ARTIFACT_V1
from aigol.runtime.proposal_runtime import CREATED, PROPOSAL_RUNTIME_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


EXECUTION_REQUEST_RUNTIME_VERSION = "EXECUTION_REQUEST_RUNTIME_V1"
EXECUTION_REQUEST_ARTIFACT_V1 = "EXECUTION_REQUEST_ARTIFACT_V1"
EXECUTION_REQUEST_CREATED = "EXECUTION_REQUEST_CREATED"
EXECUTION_REQUEST_RETURNED = "EXECUTION_REQUEST_RETURNED"
CREATED_STATUS = "CREATED"

REPLAY_STEPS = ("execution_request_created", "execution_request_returned")
VALID_REQUEST_TYPES = frozenset({"CAPABILITY_EXECUTION_REQUEST"})
FORBIDDEN_PAYLOAD_FIELDS = frozenset(
    {
        "approval_decision",
        "authorization_decision",
        "provider_command",
        "worker_command",
        "worker_instruction",
        "dispatch_target",
        "execute_now",
        "credentials",
        "api_key",
    }
)


def create_execution_request(
    *,
    execution_request_id: str,
    proposal_artifact: dict[str, Any],
    approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    request_type: str,
    request_payload: dict[str, Any],
    replay_reference: str,
    replay_dir: str | Path,
    status: str = CREATED_STATUS,
) -> dict[str, Any]:
    """Create a replay-visible execution request in CREATED state."""

    replay_path = Path(replay_dir)
    _ensure_execution_request_replay_available(replay_path)
    proposal = _validate_proposal_artifact(proposal_artifact)
    approval = _validate_approval_artifact(approval_artifact, proposal)
    request = _execution_request_artifact(
        execution_request_id=execution_request_id,
        proposal=proposal,
        approval=approval,
        requested_by=requested_by,
        created_at=created_at,
        request_type=request_type,
        request_payload=request_payload,
        status=status,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
    returned = _execution_request_returned(request)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(request, returned)


def reconstruct_execution_request_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Execution Request Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("execution request replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("execution request replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "execution request artifact")
        wrappers.append(wrapper)

    request = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("execution_request_reference") != request["execution_request_id"]:
        raise FailClosedRuntimeError("execution request replay reference mismatch")
    if returned.get("execution_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("execution request replay hash mismatch")
    if returned.get("proposal_reference") != request["proposal_reference"]:
        raise FailClosedRuntimeError("execution request replay proposal reference mismatch")
    _validate_execution_request_artifact(request)
    return {
        "execution_request_id": request["execution_request_id"],
        "proposal_reference": request["proposal_reference"],
        "approval_reference": request["approval_reference"],
        "requested_by": request["requested_by"],
        "created_at": request["created_at"],
        "request_type": request["request_type"],
        "request_payload": deepcopy(request["request_payload"]),
        "status": request["status"],
        "replay_reference": request["replay_reference"],
        "provider_authority": False,
        "provider_invoked": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _execution_request_artifact(
    *,
    execution_request_id: str,
    proposal: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    request_type: str,
    request_payload: dict[str, Any],
    status: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_REQUEST_ARTIFACT_V1,
        "execution_request_runtime_version": EXECUTION_REQUEST_RUNTIME_VERSION,
        "execution_request_id": _require_string(execution_request_id, "execution_request_id"),
        "proposal_reference": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "approval_reference": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "requested_by": _normalize_token(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "request_type": _normalize_token(request_type, "request_type"),
        "request_payload": _validate_request_payload(request_payload),
        "status": _normalize_token(status, "status"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
    }
    artifact["request_payload_hash"] = replay_hash(artifact["request_payload"])
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_execution_request_artifact(artifact)
    return artifact


def _execution_request_returned(request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(request, "execution request artifact")
    returned = {
        "event_type": EXECUTION_REQUEST_RETURNED,
        "execution_request_reference": request["execution_request_id"],
        "execution_request_hash": request["artifact_hash"],
        "proposal_reference": request["proposal_reference"],
        "proposal_hash": request["proposal_hash"],
        "approval_reference": request["approval_reference"],
        "approval_hash": request["approval_hash"],
        "status": request["status"],
        "replay_reference": request["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
        "reconstruction_metadata": {
            "execution_request_reconstructable": True,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "provider_authority": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(request: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "execution_request_artifact": deepcopy(request),
        "execution_request_replay": deepcopy(returned),
    }
    capture["execution_request_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_execution_request_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("execution request replay step ordering mismatch")
    _verify_artifact_hash(artifact, "execution request artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": EXECUTION_REQUEST_CREATED if index == 0 else EXECUTION_REQUEST_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_proposal_artifact(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("execution request failed closed: proposal is required")
    _verify_artifact_hash(proposal, "proposal runtime artifact")
    if proposal.get("artifact_type") != PROPOSAL_RUNTIME_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution request failed closed: invalid proposal artifact")
    if proposal.get("status") != CREATED:
        raise FailClosedRuntimeError("execution request failed closed: invalid proposal state")
    if proposal.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("execution request failed closed: invalid proposal creator")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("execution request failed closed: proposal replay visibility missing")
    if proposal.get("authority") is not False:
        raise FailClosedRuntimeError("execution request failed closed: proposal authority introduced")
    if proposal.get("execution_requested") is not False:
        raise FailClosedRuntimeError("execution request failed closed: execution already requested")
    if proposal.get("provider_authority") is not False:
        raise FailClosedRuntimeError("execution request failed closed: provider authority introduced")
    if proposal.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("execution request failed closed: worker invocation detected")
    _require_string(proposal.get("proposal_id"), "proposal_id")
    return deepcopy(proposal)


def _validate_approval_artifact(approval: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("execution request failed closed: approval is required")
    _verify_artifact_hash(approval, "proposal approval artifact")
    if approval.get("artifact_type") != PROPOSAL_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution request failed closed: invalid approval artifact")
    if approval.get("approval_status") != APPROVED:
        raise FailClosedRuntimeError("execution request failed closed: invalid proposal state")
    if approval.get("proposal_id") != proposal["proposal_id"]:
        raise FailClosedRuntimeError("execution request failed closed: proposal reference mismatch")
    if approval.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("execution request failed closed: proposal hash mismatch")
    if approval.get("execution_requested") is not False:
        raise FailClosedRuntimeError("execution request failed closed: approval execution requested")
    if approval.get("execution_request_created") is not False:
        raise FailClosedRuntimeError("execution request failed closed: duplicate execution request marker")
    if approval.get("provider_approval") is not False:
        raise FailClosedRuntimeError("execution request failed closed: provider approval introduced")
    if approval.get("worker_approval") is not False:
        raise FailClosedRuntimeError("execution request failed closed: worker approval introduced")
    if approval.get("automatic_approval") is not False:
        raise FailClosedRuntimeError("execution request failed closed: automatic approval introduced")
    if approval.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("execution request failed closed: provider invocation detected")
    if approval.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("execution request failed closed: worker invocation detected")
    _require_string(approval.get("approval_id"), "approval_id")
    return deepcopy(approval)


def _validate_execution_request_artifact(request: dict[str, Any]) -> None:
    if request.get("artifact_type") != EXECUTION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution request failed closed: invalid artifact")
    if request.get("requested_by") != "AIGOL":
        raise FailClosedRuntimeError("execution request failed closed: requested_by must be AIGOL")
    if request.get("request_type") not in VALID_REQUEST_TYPES:
        raise FailClosedRuntimeError("execution request failed closed: invalid request_type")
    if request.get("status") != CREATED_STATUS:
        raise FailClosedRuntimeError("execution request failed closed: invalid status")
    if request.get("request_payload_hash") != replay_hash(request.get("request_payload")):
        raise FailClosedRuntimeError("execution request failed closed: request payload hash mismatch")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("execution request failed closed: replay visibility missing")
    if request.get("provider_authority") is not False:
        raise FailClosedRuntimeError("execution request failed closed: provider authority introduced")
    if request.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("execution request failed closed: provider invocation detected")
    if request.get("worker_dispatched") is not False:
        raise FailClosedRuntimeError("execution request failed closed: worker dispatch detected")
    if request.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("execution request failed closed: worker invocation detected")
    if request.get("execution_performed") is not False:
        raise FailClosedRuntimeError("execution request failed closed: execution performed")
    if request.get("approval_created") is not False:
        raise FailClosedRuntimeError("execution request failed closed: approval introduced")
    if request.get("automatic_authorization") is not False:
        raise FailClosedRuntimeError("execution request failed closed: automatic authorization introduced")
    _require_string(request.get("execution_request_id"), "execution_request_id")
    _require_string(request.get("proposal_reference"), "proposal_reference")
    _require_string(request.get("proposal_hash"), "proposal_hash")
    _require_string(request.get("approval_reference"), "approval_reference")
    _require_string(request.get("approval_hash"), "approval_hash")
    _require_string(request.get("created_at"), "created_at")
    _require_string(request.get("replay_reference"), "replay_reference")


def _validate_request_payload(request_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request_payload, dict) or not request_payload:
        raise FailClosedRuntimeError("execution request failed closed: request_payload is required")
    if FORBIDDEN_PAYLOAD_FIELDS.intersection(request_payload):
        raise FailClosedRuntimeError("execution request failed closed: authority-bearing request payload")
    return deepcopy(request_payload)


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
        raise FailClosedRuntimeError("execution request replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("execution request replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
