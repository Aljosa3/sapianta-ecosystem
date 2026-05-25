"""Minimal bounded sandbox executor."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_context import SandboxContext
from .sandbox_result import SandboxResult, sandbox_boundary_guarantees
from .sandbox_validator import SandboxValidator
from aigol.runtime.transport.serialization import replay_hash


class SandboxExecutor:
    """Simulates bounded execution without shell, network, workers, or filesystem mutation."""

    def __init__(self, validator: SandboxValidator | None = None) -> None:
        self.validator = validator or SandboxValidator()

    def execute(self, context: SandboxContext, payload: Any) -> SandboxResult:
        self.validator.validate(context)
        summary = {
            "mode": context.execution_mode,
            "payload_type": type(payload).__name__,
            "payload_replay_hash": replay_hash(payload),
            "simulated": True,
            "capabilities_used": sorted(context.allowed_capabilities),
        }
        result = SandboxResult(
            sandbox_id=context.sandbox_id,
            runtime_id=context.runtime_id,
            execution_mode=context.execution_mode,
            allowed_capabilities=deepcopy(sorted(context.allowed_capabilities)),
            execution_status="SANDBOX_EXECUTION_SIMULATED",
            execution_summary=summary,
            boundary_guarantees=sandbox_boundary_guarantees(),
            execution_timestamp=context.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        return SandboxResult(
            sandbox_id=result.sandbox_id,
            runtime_id=result.runtime_id,
            execution_mode=result.execution_mode,
            allowed_capabilities=result.allowed_capabilities,
            execution_status=result.execution_status,
            execution_summary=result.execution_summary,
            boundary_guarantees=result.boundary_guarantees,
            execution_timestamp=result.execution_timestamp,
            replay_hash=replay_hash(replay_input),
        )
