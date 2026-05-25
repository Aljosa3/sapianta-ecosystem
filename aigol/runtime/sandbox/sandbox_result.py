"""Deterministic sandbox execution result."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


def sandbox_boundary_guarantees() -> dict[str, bool]:
    return {
        "shell_execution": False,
        "subprocess_execution": False,
        "filesystem_write": False,
        "unrestricted_network": False,
        "worker_spawn": False,
        "orchestration": False,
        "autonomous_execution": False,
    }


@dataclass(frozen=True)
class SandboxResult:
    sandbox_id: str
    runtime_id: str
    execution_mode: str
    allowed_capabilities: list[str]
    execution_status: str
    execution_summary: dict[str, Any]
    boundary_guarantees: dict[str, bool]
    execution_timestamp: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "sandbox_id": self.sandbox_id,
            "runtime_id": self.runtime_id,
            "execution_mode": self.execution_mode,
            "allowed_capabilities": deepcopy(self.allowed_capabilities),
            "execution_status": self.execution_status,
            "execution_summary": deepcopy(self.execution_summary),
            "boundary_guarantees": deepcopy(self.boundary_guarantees),
            "execution_timestamp": self.execution_timestamp,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
