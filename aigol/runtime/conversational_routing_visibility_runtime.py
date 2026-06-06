"""Operator-visible routing explanation for the interactive conversation CLI."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME_V1"
FINAL_CLASSIFICATION = "CERTIFIED_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME"

CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1 = "CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1"

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"

ROUTING_SELECTED = "ROUTING_SELECTED"
ROUTING_FAILED_CLOSED = "ROUTING_FAILED_CLOSED"

NO_CERTIFIED_WORKFLOW_MATCHED = "NO_CERTIFIED_WORKFLOW_MATCHED"

REPLAY_STEP = "conversational_routing_visibility_recorded"


def record_conversational_routing_visibility(
    *,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    workflow_id: str,
    routing_status: str,
    routing_confidence: str,
    matched_signals: list[str],
    competing_signals: list[str],
    routing_reason: str,
    routing_timestamp: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Persist the operator-visible routing explanation for one turn."""

    replay_path = Path(replay_dir)
    artifact = {
        "artifact_type": CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "routing_visibility_id": f"{_require_string(prompt_id, 'prompt_id')}:ROUTING_VISIBILITY",
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "routing_status": _require_status(routing_status),
        "routing_confidence": _require_confidence(routing_confidence),
        "matched_signals": _signals(matched_signals, "matched_signals"),
        "competing_signals": _signals(competing_signals, "competing_signals"),
        "routing_reason": _require_string(routing_reason, "routing_reason"),
        "routing_timestamp": _require_string(routing_timestamp, "routing_timestamp"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "visibility_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "conversational_routing_visibility_artifact": deepcopy(artifact),
        "conversational_routing_visibility_replay_reference": str(replay_path),
        "operator_routing_summary": render_conversational_routing_visibility(artifact),
        "replay_visible": True,
        "visibility_only": True,
    }


def reconstruct_conversational_routing_visibility_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct routing visibility evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("conversational routing visibility replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("conversational routing visibility artifact must be a JSON object")
    _verify_artifact_hash(artifact, "conversational routing visibility artifact")
    if artifact.get("artifact_type") != CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversational routing visibility artifact type mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "turn_id": artifact["turn_id"],
        "prompt_id": artifact["prompt_id"],
        "workflow_id": artifact["workflow_id"],
        "routing_status": artifact["routing_status"],
        "routing_confidence": artifact["routing_confidence"],
        "matched_signals": deepcopy(artifact["matched_signals"]),
        "competing_signals": deepcopy(artifact["competing_signals"]),
        "routing_reason": artifact["routing_reason"],
        "routing_timestamp": artifact["routing_timestamp"],
        "human_prompt_hash": artifact["human_prompt_hash"],
        "replay_visible": True,
        "visibility_only": True,
        "replay_artifact_count": 1,
        "replay_hash": replay_hash(wrapper),
    }


def render_conversational_routing_visibility(artifact: dict[str, Any]) -> str:
    """Render the routing explanation for the operator."""

    if artifact.get("routing_status") == ROUTING_FAILED_CLOSED:
        heading = "ROUTING FAILED CLOSED"
        workflow_line = None
    else:
        heading = "ROUTING DECISION"
        workflow_line = f"workflow: {_require_string(artifact.get('workflow_id'), 'workflow_id')}"
    lines = ["================================", heading]
    if workflow_line is not None:
        lines.append(workflow_line)
    lines.append(f"confidence: {_require_confidence(artifact.get('routing_confidence'))}")
    lines.append("matched:")
    lines.extend(_render_signal_lines(artifact.get("matched_signals", [])))
    lines.append("competing:")
    lines.extend(_render_signal_lines(artifact.get("competing_signals", [])))
    lines.append("reason:")
    lines.append(_require_string(artifact.get("routing_reason"), "routing_reason"))
    lines.append("================================")
    return "\n".join(lines)


def _render_signal_lines(signals: Any) -> list[str]:
    if not isinstance(signals, list) or not signals:
        return ["[]"]
    return [f"- {signal}" for signal in signals]


def _signals(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list):
        raise FailClosedRuntimeError(f"conversational routing visibility {field_name} must be a list")
    normalized = [_require_string(value, field_name) for value in values]
    return list(dict.fromkeys(normalized))


def _require_confidence(value: Any) -> str:
    confidence = _require_string(value, "routing_confidence")
    if confidence not in {HIGH, MEDIUM, LOW}:
        raise FailClosedRuntimeError("conversational routing visibility confidence is not allowed")
    return confidence


def _require_status(value: Any) -> str:
    status = _require_string(value, "routing_status")
    if status not in {ROUTING_SELECTED, ROUTING_FAILED_CLOSED}:
        raise FailClosedRuntimeError("conversational routing visibility status is not allowed")
    return status


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"conversational routing visibility {field_name} is required")
    return value.strip()


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("conversational routing visibility replay hash mismatch")
