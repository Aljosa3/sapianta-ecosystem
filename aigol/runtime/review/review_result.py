"""Immutable provider harness review result."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ReviewResult:
    review_result_id: str
    runtime_id: str
    readiness_state: str
    findings: list[dict[str, Any]]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "review_result_id": self.review_result_id,
            "runtime_id": self.runtime_id,
            "readiness_state": self.readiness_state,
            "findings": deepcopy(self.findings),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
