"""Deterministic governed capability result."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


def capability_result_boundary_guarantees() -> dict[str, bool]:
    return {
        "no_shell_execution": True,
        "no_subprocess_execution": True,
        "no_filesystem_mutation": True,
        "no_unrestricted_network": True,
        "no_worker_spawn": True,
        "no_recursive_dispatch": True,
        "no_orchestration": True,
    }


@dataclass(frozen=True)
class CapabilityResult:
    capability_request_id: str
    runtime_id: str
    sandbox_id: str
    capability: str
    execution_status: str
    execution_summary: dict[str, Any]
    boundary_guarantees: dict[str, bool]
    execution_timestamp: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "capability_request_id": self.capability_request_id,
            "runtime_id": self.runtime_id,
            "sandbox_id": self.sandbox_id,
            "capability": self.capability,
            "execution_status": self.execution_status,
            "execution_summary": deepcopy(self.execution_summary),
            "boundary_guarantees": deepcopy(self.boundary_guarantees),
            "execution_timestamp": self.execution_timestamp,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
