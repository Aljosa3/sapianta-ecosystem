"""Replay-visible Resolution Strategy Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RESOLUTION_STRATEGY_RUNTIME_VERSION = "RESOLUTION_STRATEGY_RUNTIME_V1"
RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1 = "RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1"
SELF_RESOLUTION = "SELF_RESOLUTION"
PROVIDER = "PROVIDER"
REPLAY = "REPLAY"
SELECTED = "SELECTED"
RESOLUTION_STRATEGY_SELECTED = "RESOLUTION_STRATEGY_SELECTED"
RESOLUTION_STRATEGY_RETURNED = "RESOLUTION_STRATEGY_RETURNED"

REPLAY_STEPS = ("resolution_strategy_selected", "resolution_strategy_returned")
SUPPORTED_STRATEGIES = frozenset({SELF_RESOLUTION, PROVIDER, REPLAY})
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


def select_resolution_strategy(
    *,
    strategy_id: str,
    selected_strategy: str,
    selection_reason: str,
    human_prompt_reference: str,
    created_at: str,
    replay_dir: str | Path,
    created_by: str = "AIGOL",
) -> dict[str, Any]:
    """Record deterministic resolution strategy selection."""

    replay_path = Path(replay_dir)
    _ensure_strategy_replay_available(replay_path)
    artifact = _strategy_artifact(
        strategy_id=strategy_id,
        selected_strategy=selected_strategy,
        selection_reason=selection_reason,
        human_prompt_reference=human_prompt_reference,
        created_at=created_at,
        created_by=created_by,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
    returned = _strategy_returned(artifact)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(artifact, returned)


def reconstruct_resolution_strategy_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Resolution Strategy Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("resolution strategy replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("resolution strategy replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "resolution strategy artifact")
        wrappers.append(wrapper)

    strategy = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("strategy_reference") != strategy["strategy_id"]:
        raise FailClosedRuntimeError("resolution strategy replay strategy reference mismatch")
    if returned.get("strategy_hash") != strategy["artifact_hash"]:
        raise FailClosedRuntimeError("resolution strategy replay strategy hash mismatch")
    _validate_strategy_artifact(strategy)
    return {
        "strategy_id": strategy["strategy_id"],
        "selected_strategy": strategy["selected_strategy"],
        "selection_reason": strategy["selection_reason"],
        "human_prompt_reference": strategy["human_prompt_reference"],
        "created_at": strategy["created_at"],
        "selection_status": strategy["selection_status"],
        "provider_required": strategy["provider_required"],
        "replay_required": strategy["replay_required"],
        "provider_used": False,
        "worker_required": False,
        "approval_created": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _strategy_artifact(
    *,
    strategy_id: str,
    selected_strategy: str,
    selection_reason: str,
    human_prompt_reference: str,
    created_at: str,
    created_by: str,
) -> dict[str, Any]:
    strategy = _normalize_token(selected_strategy, "selected_strategy")
    artifact = {
        "artifact_type": RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1,
        "strategy_runtime_version": RESOLUTION_STRATEGY_RUNTIME_VERSION,
        "strategy_id": _require_string(strategy_id, "strategy_id"),
        "selected_strategy": strategy,
        "selection_reason": _normalize_text(selection_reason, "selection_reason"),
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "created_by": _normalize_token(created_by, "created_by"),
        "candidate_strategies": [SELF_RESOLUTION, REPLAY, PROVIDER],
        "source_precedence": [SELF_RESOLUTION, REPLAY, PROVIDER],
        "provider_required": strategy == PROVIDER,
        "provider_used": False,
        "replay_required": strategy == REPLAY,
        "worker_required": False,
        "proposal_lifecycle_required": False,
        "selection_status": SELECTED,
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "provider_authority": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_strategy_artifact(artifact)
    return artifact


def _strategy_returned(strategy: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(strategy, "resolution strategy artifact")
    returned = {
        "event_type": RESOLUTION_STRATEGY_RETURNED,
        "strategy_reference": strategy["strategy_id"],
        "strategy_hash": strategy["artifact_hash"],
        "selected_strategy": strategy["selected_strategy"],
        "selection_status": strategy["selection_status"],
        "human_prompt_reference": strategy["human_prompt_reference"],
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "provider_used": False,
        "worker_invoked": False,
        "reconstruction_metadata": {
            "strategy_reconstructable": True,
            "provider_used": False,
            "worker_required": False,
            "approval_created": False,
            "execution_requested": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(strategy: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "resolution_strategy_artifact": deepcopy(strategy),
        "resolution_strategy_replay": deepcopy(returned),
    }
    capture["resolution_strategy_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_strategy_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("resolution strategy replay step ordering mismatch")
    _verify_artifact_hash(artifact, "resolution strategy artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": RESOLUTION_STRATEGY_SELECTED if index == 0 else RESOLUTION_STRATEGY_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_strategy_artifact(strategy: dict[str, Any]) -> None:
    if strategy.get("artifact_type") != RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("resolution strategy failed closed: invalid artifact")
    if strategy.get("selected_strategy") not in SUPPORTED_STRATEGIES:
        raise FailClosedRuntimeError("resolution strategy failed closed: invalid strategy")
    if strategy.get("selected_strategy") not in strategy.get("candidate_strategies", []):
        raise FailClosedRuntimeError("resolution strategy failed closed: strategy not in candidates")
    if strategy.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("resolution strategy failed closed: creator must be AIGOL")
    if strategy.get("selection_status") != SELECTED:
        raise FailClosedRuntimeError("resolution strategy failed closed: invalid selection status")
    if strategy.get("provider_required") is not (strategy.get("selected_strategy") == PROVIDER):
        raise FailClosedRuntimeError("resolution strategy failed closed: invalid provider requirement")
    if strategy.get("replay_required") is not (strategy.get("selected_strategy") == REPLAY):
        raise FailClosedRuntimeError("resolution strategy failed closed: invalid replay requirement")
    if strategy.get("provider_used") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: provider use introduced")
    if strategy.get("worker_required") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: worker requirement introduced")
    if strategy.get("proposal_lifecycle_required") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: proposal lifecycle introduced")
    if strategy.get("replay_visible") is not True:
        raise FailClosedRuntimeError("resolution strategy failed closed: replay visibility missing")
    if strategy.get("authority") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: authority introduced")
    if strategy.get("approval_created") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: approval introduced")
    if strategy.get("execution_requested") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: execution requested")
    if strategy.get("provider_authority") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: provider authority introduced")
    if strategy.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("resolution strategy failed closed: worker invocation detected")
    if FORBIDDEN_FIELDS.intersection(strategy):
        raise FailClosedRuntimeError("resolution strategy failed closed: authority-bearing strategy")
    _require_string(strategy.get("strategy_id"), "strategy_id")
    _require_string(strategy.get("selection_reason"), "selection_reason")
    _require_string(strategy.get("human_prompt_reference"), "human_prompt_reference")
    _require_string(strategy.get("created_at"), "created_at")


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
        raise FailClosedRuntimeError("resolution strategy replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("resolution strategy replay hash mismatch")


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
