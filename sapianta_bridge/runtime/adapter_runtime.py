"""Bounded adapter runtime delivery."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult

from .runtime_binding import create_runtime_binding
from .runtime_evidence import runtime_evidence
from .runtime_guard import guard_runtime
from .runtime_result import RuntimeResult, create_runtime_result


def blocked_normalized_result(provider_id: str) -> NormalizedExecutionResult:
    return NormalizedExecutionResult(provider_id=provider_id or "unknown", execution_status="BLOCKED")


def execute_adapter_runtime(
    *,
    envelope: dict[str, Any],
    provider: ExecutionProvider,
) -> dict[str, Any]:
    envelope_validation = validate_execution_envelope(envelope)
    binding = create_runtime_binding(envelope) if envelope_validation["valid"] else None
    guard_status = guard_runtime(
        envelope=envelope,
        provider=provider,
        binding=binding,
        envelope_validation=envelope_validation,
    )
    if guard_status["runtime_allowed"]:
        normalized = provider.execute({"bounded": True, "expected_artifacts": envelope.get("allowed_actions", [])})
    else:
        normalized = blocked_normalized_result(getattr(provider.contract, "provider_id", "unknown"))
    runtime_result = create_runtime_result(
        envelope=envelope,
        normalized_result=normalized,
        guard_status=guard_status,
    )
    evidence = runtime_evidence(
        runtime_result=runtime_result,
        envelope_validation=envelope_validation,
        guard_status=guard_status,
    )
    return {
        "runtime_result": runtime_result.to_dict(),
        "runtime_evidence": evidence,
        "envelope_validation": envelope_validation,
        "runtime_guard": guard_status,
        "routing_present": False,
        "orchestration_present": False,
    }
