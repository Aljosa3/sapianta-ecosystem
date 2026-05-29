"""Operator-facing replay summary command."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_result_summary import create_governed_result_summary, render_governed_result_summary
from aigol.runtime.human_prompt_to_governed_readonly_result import reconstruct_human_prompt_governed_result_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash


REPLAY_SUMMARY_VERSION = "REPLAY_SUMMARY_COMMAND_V1"


def summarize_operator_replay(*, replay_dir: str | Path, replay_id: str | None = None) -> dict[str, Any]:
    """Return a deterministic read-only summary of an operator replay directory."""

    replay_path = Path(replay_dir)
    resolved_replay_id = replay_id or replay_path.name
    replay_summary = reconstruct_human_prompt_governed_result_replay(replay_path)
    prompt_artifact = _load_artifact(replay_path, "000_human_prompt.json")
    result_artifact = _load_artifact(replay_path, "003_governed_result.json")
    governed_summary = create_governed_result_summary(
        operator_flow_id=_require_string(replay_summary["operator_flow_id"], "operator_flow_id"),
        human_request=_require_string(prompt_artifact.get("human_prompt", "UNAVAILABLE"), "human_prompt"),
        capability_used=_require_string(replay_summary.get("target_capability", "UNAVAILABLE"), "target_capability"),
        replay_reference=replay_path,
        governed_result=result_artifact,
        replay_summary=replay_summary,
    )
    summary = {
        "summary_version": REPLAY_SUMMARY_VERSION,
        "replay_id": _require_string(resolved_replay_id, "replay_id"),
        "replay_reference": str(replay_path),
        "status": governed_summary["status"],
        "capability": governed_summary["capability_used"],
        "authorization_status": _authorization_status(replay_summary),
        "verification_status": governed_summary["replay_verification_status"],
        "result_summary": governed_summary["reason"],
        "timestamp_ordering": _timestamp_ordering(prompt_artifact, replay_summary),
        "governed_result_summary": deepcopy(governed_summary),
        "rendered_summary": render_governed_result_summary(governed_summary),
        "operator_flow_id": replay_summary["operator_flow_id"],
        "replay_hash": replay_summary["replay_hash"],
        "read_only_view": True,
        "new_capability_created": False,
        "execution_power_added": False,
        "orchestration_added": False,
        "memory_added": False,
        "agent_added": False,
    }
    summary["summary_hash"] = replay_hash(summary)
    return summary


def render_replay_summary(summary: dict[str, Any]) -> str:
    """Render replay summary as a stable operator-facing view."""

    _verify_summary(summary)
    lines = [
        f"Replay ID: {summary['replay_id']}",
        f"Status: {summary['status']}",
        f"Capability: {summary['capability']}",
        f"Authorization Status: {summary['authorization_status']}",
        f"Verification Status: {summary['verification_status']}",
        f"Result Summary: {summary['result_summary']}",
        f"Timestamp / Ordering Information: {summary['timestamp_ordering']['created_at']} / {summary['timestamp_ordering']['lifecycle']}",
    ]
    return "\n".join(lines)


def _load_artifact(replay_path: Path, filename: str) -> dict[str, Any]:
    wrapper = load_json(replay_path / filename)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("replay summary artifact must be a JSON object")
    return artifact


def _authorization_status(replay_summary: dict[str, Any]) -> str:
    bridge = replay_summary.get("bridge_replay")
    if not isinstance(bridge, dict):
        return "UNAVAILABLE"
    transitions = bridge.get("lifecycle_transitions")
    if not isinstance(transitions, list):
        return "UNAVAILABLE"
    if "AUTHORIZED" in transitions:
        return "AUTHORIZED"
    if "FAILED" in transitions:
        return "FAILED_CLOSED"
    return "UNAVAILABLE"


def _timestamp_ordering(prompt_artifact: dict[str, Any], replay_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "created_at": _require_string(prompt_artifact.get("created_at", "UNAVAILABLE"), "created_at"),
        "lifecycle": list(replay_summary.get("lifecycle_transitions", [])),
        "replay_artifact_count": replay_summary.get("replay_artifact_count"),
    }


def _verify_summary(summary: dict[str, Any]) -> None:
    if not isinstance(summary, dict):
        raise FailClosedRuntimeError("replay summary must be a JSON object")
    required = {
        "summary_version",
        "replay_id",
        "replay_reference",
        "status",
        "capability",
        "authorization_status",
        "verification_status",
        "result_summary",
        "timestamp_ordering",
        "governed_result_summary",
        "rendered_summary",
        "operator_flow_id",
        "replay_hash",
        "read_only_view",
        "new_capability_created",
        "execution_power_added",
        "orchestration_added",
        "memory_added",
        "agent_added",
        "summary_hash",
    }
    if set(summary) != required:
        raise FailClosedRuntimeError("replay summary has malformed structure")
    expected_input = deepcopy(summary)
    actual = expected_input.pop("summary_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay summary hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
