"""Runtime result wrapper for normalized provider results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.providers.normalized_result import (
    NormalizedExecutionResult,
    validate_normalized_result,
)


RUNTIME_STATUSES = ("SUCCESS", "FAILED", "BLOCKED", "NEEDS_REVIEW")


@dataclass(frozen=True)
class RuntimeResult:
    runtime_status: str
    provider_id: str
    envelope_id: str
    replay_identity: str
    artifacts: tuple[str, ...]
    runtime_guard_status: dict[str, Any]
    normalized_result: dict[str, Any]
    replay_safe: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_status": self.runtime_status,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "replay_identity": self.replay_identity,
            "artifacts": list(self.artifacts),
            "runtime_guard_status": self.runtime_guard_status,
            "normalized_result": self.normalized_result,
            "replay_safe": self.replay_safe,
        }


def runtime_status_from_normalized(status: str) -> str:
    if status == "SUCCESS":
        return "SUCCESS"
    if status == "BLOCKED":
        return "BLOCKED"
    if status == "FAIL":
        return "FAILED"
    return "NEEDS_REVIEW"


def create_runtime_result(
    *,
    envelope: dict[str, Any],
    normalized_result: NormalizedExecutionResult,
    guard_status: dict[str, Any],
) -> RuntimeResult:
    normalized = normalized_result.to_dict()
    runtime_status = (
        "BLOCKED"
        if not guard_status.get("runtime_allowed", False)
        else runtime_status_from_normalized(normalized["execution_status"])
    )
    return RuntimeResult(
        runtime_status=runtime_status,
        provider_id=normalized["provider_id"],
        envelope_id=envelope.get("envelope_id", ""),
        replay_identity=envelope.get("replay_identity", ""),
        artifacts=tuple(normalized["artifacts_created"]),
        runtime_guard_status=guard_status,
        normalized_result=normalized,
        replay_safe=normalized.get("replay_safe") is True,
    )


def validate_runtime_result(result: Any) -> dict[str, Any]:
    value = result.to_dict() if isinstance(result, RuntimeResult) else result
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_result", "reason": "must be an object"}]}
    if value.get("runtime_status") not in RUNTIME_STATUSES:
        errors.append({"field": "runtime_status", "reason": "unsupported runtime status"})
    for field in ("provider_id", "envelope_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "runtime result field must be non-empty"})
    if not isinstance(value.get("artifacts"), list):
        errors.append({"field": "artifacts", "reason": "artifacts must be a list"})
    normalized_result = validate_normalized_result(value.get("normalized_result"))
    errors.extend(normalized_result["errors"])
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "runtime result must be replay-safe"})
    return {"valid": not errors, "errors": errors, "normalized_result_valid": normalized_result["valid"]}
