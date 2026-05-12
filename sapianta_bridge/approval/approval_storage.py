"""Append-only approval storage helpers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .approval_models import ApprovalError, validate_approval_artifact


def approval_root(config: TransportConfig | None = None) -> Path:
    active_config = config or TransportConfig()
    return active_config.runtime_root / "approval"


def approval_dirs(config: TransportConfig | None = None) -> dict[str, Path]:
    root = approval_root(config)
    return {
        "pending": root / "pending",
        "approved": root / "approved",
        "rejected": root / "rejected",
        "decisions": root / "decisions",
    }


def ensure_approval_dirs(config: TransportConfig | None = None) -> None:
    for directory in approval_dirs(config).values():
        directory.mkdir(parents=True, exist_ok=True)


def approval_path(state: str, approval_id: str, config: TransportConfig | None = None) -> Path:
    directories = approval_dirs(config)
    if state not in directories:
        raise ApprovalError("approval_state", "unknown approval storage state")
    return directories[state] / f"{approval_id}.json"


def write_pending_approval(artifact: dict[str, Any], config: TransportConfig | None = None) -> Path:
    validate_approval_artifact(artifact)
    if artifact["decision"] != "PENDING":
        raise ApprovalError("decision", "only pending approvals can be enqueued")
    ensure_approval_dirs(config)
    destination = approval_path("pending", artifact["approval_id"], config)
    if destination.exists():
        raise ApprovalError("approval_id", "duplicate approval detected")
    destination.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return destination


def read_approval(path: Path) -> dict[str, Any]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovalError(str(path), f"malformed approval JSON: {exc.msg}") from exc
    validate_approval_artifact(artifact)
    return artifact


def move_pending_to_decided(
    approval_id: str,
    decision: str,
    *,
    approved_by: str,
    reason: str,
    config: TransportConfig | None = None,
) -> Path:
    if decision not in {"APPROVED", "REJECTED"}:
        raise ApprovalError("decision", "invalid terminal approval decision")
    ensure_approval_dirs(config)
    source = approval_path("pending", approval_id, config)
    if not source.exists():
        raise ApprovalError("approval_id", "pending approval not found")
    artifact = read_approval(source)
    artifact["decision"] = decision
    artifact["approved_by"] = approved_by
    artifact["decision_reason"] = reason
    validate_approval_artifact(artifact)
    destination_state = "approved" if decision == "APPROVED" else "rejected"
    destination = approval_path(destination_state, approval_id, config)
    if destination.exists():
        raise ApprovalError("approval_id", "decision already recorded")
    source.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    shutil.move(str(source), str(destination))
    return destination
