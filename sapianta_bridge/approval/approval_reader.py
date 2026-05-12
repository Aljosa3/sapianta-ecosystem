"""Read-only approval and decision history inspection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .approval_models import ApprovalError, validate_decision_artifact
from .approval_storage import approval_dirs, read_approval


def _paths(state: str, config: TransportConfig | None = None) -> list[Path]:
    directory = approval_dirs(config)[state]
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def pending_approvals(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return _ordered([read_approval(path) for path in _paths("pending", config)])


def approved_approvals(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return _ordered([read_approval(path) for path in _paths("approved", config)])


def rejected_approvals(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return _ordered([read_approval(path) for path in _paths("rejected", config)])


def approval_history(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return _ordered(pending_approvals(config) + approved_approvals(config) + rejected_approvals(config))


def approval_by_id(
    approval_id: str,
    config: TransportConfig | None = None,
) -> dict[str, Any] | None:
    for approval in approval_history(config):
        if approval["approval_id"] == approval_id:
            return approval
    return None


def approvals_for_task(task_id: str, config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [approval for approval in approval_history(config) if approval["source_task_id"] == task_id]


def approvals_for_reflection(
    reflection_id: str,
    config: TransportConfig | None = None,
) -> list[dict[str, Any]]:
    return [
        approval
        for approval in approval_history(config)
        if approval["source_reflection_id"] == reflection_id
    ]


def decision_history(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    decisions = []
    for path in _paths("decisions", config):
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ApprovalError(str(path), f"malformed decision JSON: {exc.msg}") from exc
        validate_decision_artifact(artifact)
        decisions.append(artifact)
    return sorted(decisions, key=lambda artifact: (artifact["timestamp"], artifact["decision_id"]))


def _ordered(approvals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(approvals, key=lambda artifact: (artifact["timestamp"], artifact["approval_id"]))
