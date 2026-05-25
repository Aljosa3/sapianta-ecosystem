"""Immutable runtime policy contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class PolicyContract:
    policy_id: str
    runtime_id: str
    sandbox_id: str
    capability_request_id: str
    policy_scope: str
    requested_capability: str
    requested_target: str
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "policy_id": self.policy_id,
            "runtime_id": self.runtime_id,
            "sandbox_id": self.sandbox_id,
            "capability_request_id": self.capability_request_id,
            "policy_scope": self.policy_scope,
            "requested_capability": self.requested_capability,
            "requested_target": self.requested_target,
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_capability_request(cls, capability_request, sandbox_context) -> "PolicyContract":
        payload = capability_request.request_payload if isinstance(capability_request.request_payload, dict) else {}
        default_scopes = {
            "read_text": "READ_ONLY",
            "inspect_json": "ANALYSIS_ONLY",
            "analyze_text": "ANALYSIS_ONLY",
            "mock_write_preview": "PREVIEW_ONLY",
        }
        policy_scope = payload.get("policy_scope", default_scopes.get(capability_request.capability, "ANALYSIS_ONLY"))
        contract = cls(
            policy_id=f"{capability_request.runtime_id}:{capability_request.capability_request_id}:policy",
            runtime_id=capability_request.runtime_id,
            sandbox_id=capability_request.sandbox_id,
            capability_request_id=capability_request.capability_request_id,
            policy_scope=policy_scope,
            requested_capability=capability_request.capability,
            requested_target=capability_request.target,
            governance_state=capability_request.governance_state,
            lineage_refs=deepcopy(capability_request.lineage_refs),
            created_at=capability_request.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            policy_id=contract.policy_id,
            runtime_id=contract.runtime_id,
            sandbox_id=contract.sandbox_id,
            capability_request_id=contract.capability_request_id,
            policy_scope=contract.policy_scope,
            requested_capability=contract.requested_capability,
            requested_target=contract.requested_target,
            governance_state=contract.governance_state,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
