"""Replay-visible Provider Proposal runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_classifier import CLASSIFIED, PROVIDER_PROPOSAL, classify_intent
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_PROPOSAL_RUNTIME_VERSION = "PROVIDER_PROPOSAL_RUNTIME_V1"
PROVIDER_PROPOSAL_ARTIFACT = "PROVIDER_PROPOSAL_V1"
CREATED = "PROVIDER_PROPOSAL_CREATED"
RETURNED = "PROVIDER_PROPOSAL_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("provider_proposal_created", "provider_proposal_returned")

FORBIDDEN_FIELDS = frozenset(
    {
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


def create_provider_proposal(
    *,
    proposal_id: str,
    prompt_id: str,
    human_prompt: str,
    provider_type: str,
    reason: str,
    created_at: str,
    replay_dir: str | Path,
    intent_classification_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an advisory provider proposal without invoking a provider."""

    replay_path = Path(replay_dir)
    try:
        _ensure_proposal_replay_available(replay_path)
        intent_artifact = intent_classification_artifact
        if intent_artifact is None:
            intent_artifact = classify_intent(
                artifact_id=f"{proposal_id}:INTENT",
                human_request_reference=prompt_id,
                human_prompt=human_prompt,
                classification_timestamp=created_at,
                replay_reference=f"{proposal_id}:INTENT_REPLAY",
                replay_dir=replay_path / "intent_classification",
            )["intent_classification_artifact"]
        intent_artifact = _validate_intent(intent_artifact)
        proposal = _proposal_artifact(
            proposal_id=proposal_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            intent_id=intent_artifact["artifact_id"],
            provider_type=provider_type,
            reason=reason,
            created_at=created_at,
            proposal_status=CREATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], proposal)
        returned = _proposal_returned(
            proposal=proposal,
            intent_artifact=intent_artifact,
            proposal_status=RETURNED,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(proposal, returned)
    except Exception as exc:
        proposal = _failed_proposal_artifact(
            proposal_id=proposal_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            provider_type=provider_type,
            reason=reason,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], proposal)
        returned = _proposal_returned(
            proposal=proposal,
            intent_artifact=None,
            proposal_status=FAILED_CLOSED,
            failure_reason=proposal["failure_reason"],
        )
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(proposal, returned)


def reconstruct_provider_proposal_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider proposal replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider proposal replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider proposal replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "provider proposal artifact")
        wrappers.append(wrapper)

    proposal = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("proposal_reference") != proposal["proposal_id"]:
        raise FailClosedRuntimeError("provider proposal replay proposal reference mismatch")
    if returned.get("proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal replay proposal hash mismatch")
    _validate_proposal(proposal)
    return {
        "proposal_id": proposal["proposal_id"],
        "prompt_id": proposal["prompt_id"],
        "prompt": proposal["prompt_text"],
        "intent_id": proposal["intent_id"],
        "provider_type": proposal["provider_type"],
        "reason": proposal["reason"],
        "proposal_status": proposal["proposal_status"],
        "authority": False,
        "execution_capable": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _ensure_proposal_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _validate_intent(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider proposal failed closed: intent missing")
    if artifact.get("artifact_type") != "INTENT_CLASSIFICATION_ARTIFACT":
        raise FailClosedRuntimeError("provider proposal failed closed: invalid intent")
    if FORBIDDEN_FIELDS.intersection(artifact):
        raise FailClosedRuntimeError("provider proposal failed closed: authority-bearing intent")
    _verify_artifact_hash(artifact, "intent classification artifact")
    if artifact.get("classification_status") != CLASSIFIED:
        raise FailClosedRuntimeError("provider proposal failed closed: intent classification failed")
    if artifact.get("classification_destination") != PROVIDER_PROPOSAL:
        raise FailClosedRuntimeError("provider proposal failed closed: intent is not provider proposal")
    return deepcopy(artifact)


def _proposal_artifact(
    *,
    proposal_id: str,
    prompt_id: str,
    human_prompt: str,
    intent_id: str,
    provider_type: str,
    reason: str,
    created_at: str,
    proposal_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    prompt = _normalize_text(human_prompt, "human_prompt")
    proposal = {
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "intent_id": _require_string(intent_id, "intent_id"),
        "artifact_type": PROVIDER_PROPOSAL_ARTIFACT,
        "provider_type": _normalize_token(provider_type, "provider_type"),
        "reason": _normalize_text(reason, "reason"),
        "authority": False,
        "execution_capable": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "proposal_status": proposal_status,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": failure_reason,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    _validate_proposal(proposal)
    return proposal


def _failed_proposal_artifact(
    *,
    proposal_id: Any,
    prompt_id: Any,
    human_prompt: Any,
    provider_type: Any,
    reason: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    proposal = {
        "proposal_id": proposal_id if isinstance(proposal_id, str) and proposal_id.strip() else "INVALID_PROPOSAL_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "intent_id": None,
        "artifact_type": PROVIDER_PROPOSAL_ARTIFACT,
        "provider_type": _best_effort_token(provider_type),
        "reason": reason if isinstance(reason, str) and reason.strip() else "INVALID_REASON",
        "authority": False,
        "execution_capable": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "proposal_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": failure_reason,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _proposal_returned(
    *,
    proposal: dict[str, Any],
    intent_artifact: dict[str, Any] | None,
    proposal_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(proposal, "provider proposal artifact")
    returned = {
        "replay_event": RETURNED if proposal_status != FAILED_CLOSED else FAILED_CLOSED,
        "proposal_reference": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "prompt_id": proposal["prompt_id"],
        "intent_id": proposal["intent_id"],
        "intent_artifact_hash": intent_artifact.get("artifact_hash") if isinstance(intent_artifact, dict) else None,
        "provider_type": proposal["provider_type"],
        "proposal_status": proposal_status,
        "replay_visible": True,
        "authority": False,
        "execution_capable": False,
        "reconstruction_metadata": {
            "prompt_reconstructable": True,
            "intent_reconstructable": intent_artifact is not None,
            "proposal_reconstructable": True,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "authority_introduced": False,
        },
        "failure_reason": failure_reason,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(proposal: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "provider_proposal": deepcopy(proposal),
        "provider_proposal_replay": deepcopy(returned),
    }
    capture["provider_proposal_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider proposal replay step ordering mismatch")
    _verify_artifact_hash(artifact, "provider proposal artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": CREATED if index == 0 else RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _validate_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("artifact_type") != PROVIDER_PROPOSAL_ARTIFACT:
        raise FailClosedRuntimeError("provider proposal failed closed: invalid artifact")
    if proposal.get("authority") is not False:
        raise FailClosedRuntimeError("provider proposal failed closed: authority introduced")
    if proposal.get("execution_capable") is not False:
        raise FailClosedRuntimeError("provider proposal failed closed: execution capability introduced")
    if proposal.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("provider proposal failed closed: provider invocation detected")
    if proposal.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("provider proposal failed closed: worker invocation detected")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("provider proposal failed closed: replay visibility missing")
    if FORBIDDEN_FIELDS.intersection(proposal):
        raise FailClosedRuntimeError("provider proposal failed closed: authority-bearing proposal")
    status = proposal.get("proposal_status")
    if status == CREATED:
        _require_string(proposal.get("intent_id"), "intent_id")
        _require_string(proposal.get("reason"), "reason")
    elif status != FAILED_CLOSED:
        raise FailClosedRuntimeError("provider proposal failed closed: invalid status")


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
        raise FailClosedRuntimeError("provider proposal replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider proposal replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider proposal failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _best_effort_token(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip().upper().replace("-", "_")
    return "INVALID_PROVIDER_TYPE"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
