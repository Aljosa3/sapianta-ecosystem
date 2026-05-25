"""Immutable runtime observability snapshot."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RuntimeSnapshot:
    snapshot_id: str
    runtime_id: str
    lifecycle_state: str
    provider_state: str
    capability_state: str
    policy_state: str
    continuity_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "snapshot_id": self.snapshot_id,
            "runtime_id": self.runtime_id,
            "lifecycle_state": self.lifecycle_state,
            "provider_state": self.provider_state,
            "capability_state": self.capability_state,
            "policy_state": self.policy_state,
            "continuity_state": self.continuity_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_artifacts(cls, runtime_id: str, dispatch: dict, result: dict, store) -> "RuntimeSnapshot":
        snapshot = cls(
            snapshot_id=f"{runtime_id}:snapshot",
            runtime_id=runtime_id,
            lifecycle_state=result.get("lifecycle_state", "UNKNOWN"),
            provider_state="PRESENT" if result.get("provider_response") else "ABSENT",
            capability_state=_artifact_state(store.capability_result_path(runtime_id)),
            policy_state=_artifact_state(store.policy_result_path(runtime_id)),
            continuity_state=_artifact_state(store.continuity_result_path(runtime_id)),
            lineage_refs=deepcopy(dispatch.get("lineage_refs", [])),
            created_at=result.get("closure_timestamp", dispatch.get("dispatch_timestamp", "")),
        )
        replay_input = snapshot.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            snapshot_id=snapshot.snapshot_id,
            runtime_id=snapshot.runtime_id,
            lifecycle_state=snapshot.lifecycle_state,
            provider_state=snapshot.provider_state,
            capability_state=snapshot.capability_state,
            policy_state=snapshot.policy_state,
            continuity_state=snapshot.continuity_state,
            lineage_refs=snapshot.lineage_refs,
            created_at=snapshot.created_at,
            replay_hash=replay_hash(replay_input),
        )


def _artifact_state(path) -> str:
    return "PRESENT" if path.exists() else "ABSENT"
