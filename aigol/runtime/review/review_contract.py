"""Immutable provider harness review contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ReviewContract:
    review_id: str
    runtime_id: str
    provider_name: str
    review_scope: dict[str, Any]
    governance_state: str
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "review_id": self.review_id,
            "runtime_id": self.runtime_id,
            "provider_name": self.provider_name,
            "review_scope": deepcopy(self.review_scope),
            "governance_state": self.governance_state,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def create(
        cls,
        runtime_id: str,
        provider_name: str,
        review_scope: dict[str, Any],
        governance_state: str = "AUTHORIZED",
        created_at: str = "1970-01-01T00:00:00Z",
    ) -> "ReviewContract":
        contract = cls(
            review_id=f"{runtime_id}:{provider_name}:provider_harness_review",
            runtime_id=runtime_id,
            provider_name=provider_name,
            review_scope=deepcopy(review_scope),
            governance_state=governance_state,
            created_at=created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            review_id=contract.review_id,
            runtime_id=contract.runtime_id,
            provider_name=contract.provider_name,
            review_scope=contract.review_scope,
            governance_state=contract.governance_state,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
