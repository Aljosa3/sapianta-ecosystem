"""Canonical normalized execution result semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .provider_identity import validate_provider_identity


EXECUTION_STATUSES = ("SUCCESS", "FAIL", "BLOCKED", "NOT_EXECUTED")


@dataclass(frozen=True)
class NormalizedExecutionResult:
    provider_id: str
    execution_status: str
    artifacts_created: tuple[str, ...] = field(default_factory=tuple)
    tests_executed: bool = False
    governance_modified: bool = False
    execution_time_ms: int = 0
    replay_safe: bool = True
    stdout_tail: str = ""
    stderr_tail: str = ""
    hidden_tasks_generated: bool = False
    validation_bypassed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "execution_status": self.execution_status,
            "artifacts_created": list(self.artifacts_created),
            "tests_executed": self.tests_executed,
            "governance_modified": self.governance_modified,
            "execution_time_ms": self.execution_time_ms,
            "replay_safe": self.replay_safe,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
            "hidden_tasks_generated": self.hidden_tasks_generated,
            "validation_bypassed": self.validation_bypassed,
        }


def validate_normalized_result(result: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    value = result.to_dict() if isinstance(result, NormalizedExecutionResult) else result
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "normalized_result", "reason": "result must be an object"}],
        }
    identity_result = validate_provider_identity(
        {"provider_id": value.get("provider_id"), "provider_type": "NORMALIZED_RESULT"}
    )
    errors.extend(error for error in identity_result["errors"] if error["field"] == "provider_id")
    if value.get("execution_status") not in EXECUTION_STATUSES:
        errors.append({"field": "execution_status", "reason": "unsupported execution status"})
    if not isinstance(value.get("artifacts_created"), list):
        errors.append({"field": "artifacts_created", "reason": "artifacts_created must be a list"})
    if value.get("governance_modified") is not False:
        errors.append({"field": "governance_modified", "reason": "providers cannot modify governance"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "normalized result must be replay-safe"})
    if value.get("hidden_tasks_generated") is not False:
        errors.append({"field": "hidden_tasks_generated", "reason": "providers cannot generate hidden tasks"})
    if value.get("validation_bypassed") is not False:
        errors.append({"field": "validation_bypassed", "reason": "providers cannot bypass validation"})
    if not isinstance(value.get("execution_time_ms"), int) or value.get("execution_time_ms") < 0:
        errors.append({"field": "execution_time_ms", "reason": "execution_time_ms must be non-negative integer"})
    return {"valid": not errors, "errors": errors, "normalized_result_valid": not errors}
