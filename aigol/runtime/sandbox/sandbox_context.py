"""Deterministic sandbox context model."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


ALLOWED_EXECUTION_MODES = frozenset({"READ_ONLY", "ANALYSIS_ONLY", "MOCK_EXECUTION"})


@dataclass(frozen=True)
class SandboxContext:
    sandbox_id: str
    runtime_id: str
    package_id: str
    worker_id: str
    execution_mode: str
    allowed_capabilities: list[str]
    denied_capabilities: list[str]
    resource_limits: dict[str, Any]
    execution_ttl_seconds: int
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "sandbox_id": self.sandbox_id,
            "runtime_id": self.runtime_id,
            "package_id": self.package_id,
            "worker_id": self.worker_id,
            "execution_mode": self.execution_mode,
            "allowed_capabilities": deepcopy(self.allowed_capabilities),
            "denied_capabilities": deepcopy(self.denied_capabilities),
            "resource_limits": deepcopy(self.resource_limits),
            "execution_ttl_seconds": self.execution_ttl_seconds,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package) -> "SandboxContext":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        sandbox = payload.get("sandbox", {}) if isinstance(payload.get("sandbox", {}), dict) else {}
        execution_mode = sandbox.get("execution_mode", payload.get("execution_mode", "MOCK_EXECUTION"))
        allowed_capabilities = sandbox.get("allowed_capabilities", payload.get("allowed_capabilities", ["mock_execute"]))
        denied_capabilities = sandbox.get("denied_capabilities", payload.get("denied_capabilities", []))
        resource_limits = sandbox.get(
            "resource_limits",
            payload.get("resource_limits", {"max_memory_mb": 64, "max_runtime_seconds": 1}),
        )
        ttl = sandbox.get("execution_ttl_seconds", payload.get("execution_ttl_seconds", 1))
        context = cls(
            sandbox_id=f"{runtime_package.runtime_id}:{runtime_package.package_id}:sandbox",
            runtime_id=runtime_package.runtime_id,
            package_id=runtime_package.package_id,
            worker_id=runtime_package.worker_id,
            execution_mode=execution_mode,
            allowed_capabilities=deepcopy(allowed_capabilities),
            denied_capabilities=deepcopy(denied_capabilities),
            resource_limits=deepcopy(resource_limits),
            execution_ttl_seconds=ttl,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = context.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            sandbox_id=context.sandbox_id,
            runtime_id=context.runtime_id,
            package_id=context.package_id,
            worker_id=context.worker_id,
            execution_mode=context.execution_mode,
            allowed_capabilities=context.allowed_capabilities,
            denied_capabilities=context.denied_capabilities,
            resource_limits=context.resource_limits,
            execution_ttl_seconds=context.execution_ttl_seconds,
            lineage_refs=context.lineage_refs,
            created_at=context.created_at,
            replay_hash=replay_hash(replay_input),
        )
