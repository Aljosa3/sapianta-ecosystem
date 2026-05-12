"""Shared reflection model helpers and fail-closed errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


@dataclass(frozen=True)
class ReflectionError(Exception):
    field: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "reason": self.reason}


def validate_reflection_artifact(artifact: Any) -> None:
    if not isinstance(artifact, dict):
        raise ReflectionError("reflection", "reflection artifact must be an object")
    required = (
        "reflection_id",
        "timestamp",
        "source_task_id",
        "execution_outcome",
        "capability_delta",
        "governance_risk",
        "observations",
        "advisory_proposals",
        "advisory_only",
        "allowed_to_execute_automatically",
    )
    for field in required:
        if field not in artifact:
            raise ReflectionError(field, "missing reflection field")
    if not isinstance(artifact["reflection_id"], str) or not artifact["reflection_id"].strip():
        raise ReflectionError("reflection_id", "reflection_id must be non-empty")
    if not isinstance(artifact["source_task_id"], str) or not artifact["source_task_id"].strip():
        raise ReflectionError("source_task_id", "source_task_id must be non-empty")
    if artifact["advisory_only"] is not True:
        raise ReflectionError("advisory_only", "reflection must remain advisory-only")
    if artifact["allowed_to_execute_automatically"] is not False:
        raise ReflectionError(
            "allowed_to_execute_automatically",
            "reflection must not allow automatic execution",
        )
    risk = artifact["governance_risk"]
    if not isinstance(risk, dict) or risk.get("level") not in RISK_LEVELS:
        raise ReflectionError("governance_risk.level", "invalid governance risk level")
