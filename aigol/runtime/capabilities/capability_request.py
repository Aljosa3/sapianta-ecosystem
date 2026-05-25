"""Deterministic governed capability request."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


def capability_boundary_guarantees() -> dict[str, bool]:
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
class CapabilityRequest:
    capability_request_id: str
    runtime_id: str
    sandbox_id: str
    package_id: str
    worker_id: str
    provider: str
    capability: str
    target: str
    request_payload: Any
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    boundary_guarantees: dict[str, bool] | None = None
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "capability_request_id": self.capability_request_id,
            "runtime_id": self.runtime_id,
            "sandbox_id": self.sandbox_id,
            "package_id": self.package_id,
            "worker_id": self.worker_id,
            "provider": self.provider,
            "capability": self.capability,
            "target": self.target,
            "request_payload": deepcopy(self.request_payload),
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "boundary_guarantees": deepcopy(self.boundary_guarantees or capability_boundary_guarantees()),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package, sandbox_id: str) -> "CapabilityRequest":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        request = payload.get("capability_request", {})
        capability = request.get("capability", "")
        target = request.get("target", "")
        request_payload = request.get("request_payload", {})
        capability_request = cls(
            capability_request_id=f"{runtime_package.runtime_id}:{runtime_package.package_id}:{capability}",
            runtime_id=runtime_package.runtime_id,
            sandbox_id=sandbox_id,
            package_id=runtime_package.package_id,
            worker_id=runtime_package.worker_id,
            provider=runtime_package.provider,
            capability=capability,
            target=target,
            request_payload=deepcopy(request_payload),
            governance_state=runtime_package.governance_state,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
            boundary_guarantees=capability_boundary_guarantees(),
        )
        replay_input = capability_request.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            capability_request_id=capability_request.capability_request_id,
            runtime_id=capability_request.runtime_id,
            sandbox_id=capability_request.sandbox_id,
            package_id=capability_request.package_id,
            worker_id=capability_request.worker_id,
            provider=capability_request.provider,
            capability=capability_request.capability,
            target=capability_request.target,
            request_payload=capability_request.request_payload,
            governance_state=capability_request.governance_state,
            lineage_refs=capability_request.lineage_refs,
            created_at=capability_request.created_at,
            boundary_guarantees=capability_request.boundary_guarantees,
            replay_hash=replay_hash(replay_input),
        )
