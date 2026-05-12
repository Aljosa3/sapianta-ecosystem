"""Immutable governance decision evidence for approval outcomes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.transport.transport_config import TransportConfig

from .approval_models import ApprovalError, validate_approval_artifact, validate_decision_artifact
from .approval_storage import approval_dirs, ensure_approval_dirs


def build_decision_artifact(
    approval: dict[str, Any],
    *,
    decision: str,
    approved_by: str,
    reason: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    validate_approval_artifact(approval)
    if decision not in {"APPROVED", "REJECTED"}:
        raise ApprovalError("decision", "decision must be APPROVED or REJECTED")
    effective_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    seed = {
        "approval_id": approval["approval_id"],
        "decision": decision,
        "approved_by": approved_by,
        "reason": reason,
        "timestamp": effective_timestamp,
    }
    artifact = {
        "decision_id": f"DECISION-{compute_hash(seed)[:16].upper()}",
        "approval_id": approval["approval_id"],
        "decision": decision,
        "approved_by": approved_by,
        "timestamp": effective_timestamp,
        "reason": reason,
        "source_reflection_id": approval["source_reflection_id"],
        "execution_authority_granted": False,
    }
    validate_decision_artifact(artifact)
    return artifact


def write_decision_artifact(
    artifact: dict[str, Any],
    config: TransportConfig | None = None,
) -> Path:
    validate_decision_artifact(artifact)
    ensure_approval_dirs(config)
    destination = approval_dirs(config)["decisions"] / f"{artifact['decision_id']}.json"
    if destination.exists():
        raise ApprovalError("decision_id", "decision artifact already exists")
    destination.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return destination
