"""Minimal replay-visible Proposal Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROPOSAL_RUNTIME_VERSION = "PROPOSAL_RUNTIME_V1"
PROPOSAL_RUNTIME_ARTIFACT_V1 = "PROPOSAL_RUNTIME_ARTIFACT_V1"
CREATED = "CREATED"
PROPOSAL_RUNTIME_CREATED = "PROPOSAL_RUNTIME_CREATED"
PROPOSAL_RUNTIME_RETURNED = "PROPOSAL_RUNTIME_RETURNED"

REPLAY_STEPS = ("proposal_runtime_created", "proposal_runtime_returned")

VALID_PROPOSAL_TYPES = frozenset({"CAPABILITY_PROPOSAL"})
VALID_PROPOSAL_SOURCES = frozenset(
    {
        "CONVERSATION",
        "RESOLUTION_STRATEGY",
        "PROVIDER_EVIDENCE",
        "REPLAY_EVIDENCE",
        "GOVERNANCE_EVIDENCE",
        "HUMAN_PROMPT",
        "COMBINED",
    }
)
FORBIDDEN_FIELDS = frozenset(
    {
        "approval_decision",
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }
)


def create_proposal(
    *,
    proposal_id: str,
    proposal_type: str,
    proposal_source: str,
    proposal_text: str,
    created_at: str,
    replay_reference: str,
    replay_dir: str | Path,
    created_by: str = "AIGOL",
    status: str = CREATED,
) -> dict[str, Any]:
    """Create a non-authoritative proposal artifact in CREATED state."""

    replay_path = Path(replay_dir)
    _ensure_proposal_replay_available(replay_path)
    proposal = _proposal_artifact(
        proposal_id=proposal_id,
        proposal_type=proposal_type,
        proposal_source=proposal_source,
        proposal_text=proposal_text,
        created_at=created_at,
        created_by=created_by,
        status=status,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], proposal)
    returned = _proposal_returned(proposal)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(proposal, returned)


def reconstruct_proposal_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Proposal Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("proposal runtime replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("proposal runtime replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "proposal runtime artifact")
        wrappers.append(wrapper)

    proposal = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("proposal_reference") != proposal["proposal_id"]:
        raise FailClosedRuntimeError("proposal runtime replay proposal reference mismatch")
    if returned.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("proposal runtime replay proposal hash mismatch")
    _validate_proposal(proposal)
    return {
        "proposal_id": proposal["proposal_id"],
        "proposal_type": proposal["proposal_type"],
        "proposal_source": proposal["proposal_source"],
        "proposal_text": proposal["proposal_text"],
        "created_at": proposal["created_at"],
        "created_by": proposal["created_by"],
        "status": proposal["status"],
        "replay_reference": proposal["replay_reference"],
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _proposal_artifact(
    *,
    proposal_id: str,
    proposal_type: str,
    proposal_source: str,
    proposal_text: str,
    created_at: str,
    created_by: str,
    status: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROPOSAL_RUNTIME_ARTIFACT_V1,
        "proposal_runtime_version": PROPOSAL_RUNTIME_VERSION,
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "proposal_type": _normalize_token(proposal_type, "proposal_type"),
        "proposal_source": _normalize_token(proposal_source, "proposal_source"),
        "proposal_text": _normalize_text(proposal_text, "proposal_text"),
        "created_at": _require_string(created_at, "created_at"),
        "created_by": _normalize_token(created_by, "created_by"),
        "status": _normalize_token(status, "status"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_proposal(artifact)
    return artifact


def _proposal_returned(proposal: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(proposal, "proposal runtime artifact")
    returned = {
        "event_type": PROPOSAL_RUNTIME_RETURNED,
        "proposal_reference": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "proposal_status": proposal["status"],
        "replay_reference": proposal["replay_reference"],
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "reconstruction_metadata": {
            "proposal_reconstructable": True,
            "approval_created": False,
            "execution_requested": False,
            "provider_authority": False,
            "provider_invoked": False,
            "worker_invoked": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(proposal: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "proposal_runtime_artifact": deepcopy(proposal),
        "proposal_runtime_replay": deepcopy(returned),
    }
    capture["proposal_runtime_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_proposal_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("proposal runtime replay step ordering mismatch")
    _verify_artifact_hash(artifact, "proposal runtime artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": PROPOSAL_RUNTIME_CREATED if index == 0 else PROPOSAL_RUNTIME_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("artifact_type") != PROPOSAL_RUNTIME_ARTIFACT_V1:
        raise FailClosedRuntimeError("proposal runtime failed closed: invalid artifact")
    if proposal.get("proposal_type") not in VALID_PROPOSAL_TYPES:
        raise FailClosedRuntimeError("proposal runtime failed closed: invalid proposal_type")
    if proposal.get("proposal_source") not in VALID_PROPOSAL_SOURCES:
        raise FailClosedRuntimeError("proposal runtime failed closed: invalid proposal_source")
    if proposal.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("proposal runtime failed closed: creator must be AIGOL")
    if proposal.get("status") != CREATED:
        raise FailClosedRuntimeError("proposal runtime failed closed: invalid status")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("proposal runtime failed closed: replay visibility missing")
    if proposal.get("authority") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: authority introduced")
    if proposal.get("approval_created") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: approval introduced")
    if proposal.get("execution_requested") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: execution requested")
    if proposal.get("provider_authority") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: provider authority introduced")
    if proposal.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: provider invocation detected")
    if proposal.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("proposal runtime failed closed: worker invocation detected")
    if FORBIDDEN_FIELDS.intersection(proposal):
        raise FailClosedRuntimeError("proposal runtime failed closed: authority-bearing proposal")
    _require_string(proposal.get("proposal_id"), "proposal_id")
    _require_string(proposal.get("proposal_text"), "proposal_text")
    _require_string(proposal.get("created_at"), "created_at")
    _require_string(proposal.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("proposal runtime replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("proposal runtime replay hash mismatch")


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
