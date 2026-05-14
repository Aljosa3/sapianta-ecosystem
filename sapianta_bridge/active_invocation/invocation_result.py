"""Replay-safe active invocation result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.runtime.runtime_result import RUNTIME_STATUSES, validate_runtime_result


INVOCATION_STATUSES = ("SUCCESS", "FAILED", "BLOCKED", "NEEDS_REVIEW")


@dataclass(frozen=True)
class InvocationResult:
    invocation_status: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    replay_identity: str
    runtime_result: dict[str, Any]
    normalized_result: dict[str, Any]
    lifecycle: tuple[str, ...]
    replay_safe: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_status": self.invocation_status,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "replay_identity": self.replay_identity,
            "runtime_result": self.runtime_result,
            "normalized_result": self.normalized_result,
            "lifecycle": list(self.lifecycle),
            "adaptive_interpretation_present": False,
            "replay_safe": self.replay_safe,
        }


def create_invocation_result(
    *,
    request: dict[str, Any],
    runtime_output: dict[str, Any],
    lifecycle: list[str],
) -> InvocationResult:
    runtime_result = runtime_output.get("runtime_result", {})
    runtime_status = runtime_result.get("runtime_status", "BLOCKED")
    invocation_status = runtime_status if runtime_status in INVOCATION_STATUSES else "BLOCKED"
    normalized_result = runtime_result.get("normalized_result", {})
    return InvocationResult(
        invocation_status=invocation_status,
        invocation_id=request.get("invocation_id", ""),
        provider_id=request.get("provider_id", ""),
        envelope_id=request.get("envelope_id", ""),
        replay_identity=request.get("replay_identity", ""),
        runtime_result=runtime_result,
        normalized_result=normalized_result,
        lifecycle=tuple(lifecycle),
        replay_safe=runtime_result.get("replay_safe") is True,
    )


def blocked_invocation_result(request: dict[str, Any], lifecycle: list[str] | None = None) -> InvocationResult:
    return InvocationResult(
        invocation_status="BLOCKED",
        invocation_id=request.get("invocation_id", ""),
        provider_id=request.get("provider_id", ""),
        envelope_id=request.get("envelope_id", ""),
        replay_identity=request.get("replay_identity", ""),
        runtime_result={},
        normalized_result={},
        lifecycle=tuple(lifecycle or ["PROPOSED"]),
        replay_safe=False,
    )


def validate_invocation_result(result: Any) -> dict[str, Any]:
    value = result.to_dict() if isinstance(result, InvocationResult) else result
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "invocation_result", "reason": "must be an object"}]}
    if value.get("invocation_status") not in INVOCATION_STATUSES:
        errors.append({"field": "invocation_status", "reason": "unsupported invocation status"})
    for field in ("invocation_id", "provider_id", "envelope_id", "replay_identity"):
        if value.get("invocation_status") != "BLOCKED" and (
            not isinstance(value.get(field), str) or not value.get(field, "").strip()
        ):
            errors.append({"field": field, "reason": "invocation result field must be non-empty"})
    if value.get("runtime_result"):
        runtime_validation = validate_runtime_result(value.get("runtime_result"))
        errors.extend(runtime_validation["errors"])
    if value.get("adaptive_interpretation_present") is not False:
        errors.append({"field": "adaptive_interpretation_present", "reason": "adaptive interpretation is forbidden"})
    if value.get("invocation_status") != "BLOCKED" and value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "invocation result must be replay-safe"})
    if value.get("runtime_result", {}).get("runtime_status") not in (*RUNTIME_STATUSES, None):
        errors.append({"field": "runtime_status", "reason": "unsupported runtime status"})
    return {"valid": not errors, "errors": errors}
