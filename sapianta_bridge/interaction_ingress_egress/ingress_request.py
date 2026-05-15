"""Deterministic local ingress request artifact."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LocalIngressRequest:
    human_input: str
    conversation_id: str
    execution_gate_id: str
    bounded_runtime_id: str
    result_capture_id: str
    requested_provider_id: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "human_input": self.human_input,
            "conversation_id": self.conversation_id,
            "execution_gate_id": self.execution_gate_id,
            "bounded_runtime_id": self.bounded_runtime_id,
            "result_capture_id": self.result_capture_id,
            "requested_provider_id": self.requested_provider_id,
            "orchestration_requested": False,
            "retry_requested": False,
            "routing_requested": False,
            "autonomous_continuation_requested": False,
        }
        value["ingress_artifact_id"] = f"LOCAL-INGRESS-{stable_hash(value)[:16]}"
        value["replay_safe"] = True
        return value


def create_local_ingress_request(
    human_input: str,
    *,
    conversation_id: str = "CHATGPT-SESSION",
    execution_gate_id: str,
    bounded_runtime_id: str,
    result_capture_id: str,
    requested_provider_id: str = "deterministic_mock",
) -> LocalIngressRequest:
    return LocalIngressRequest(human_input, conversation_id, execution_gate_id, bounded_runtime_id, result_capture_id, requested_provider_id)


def load_ingress_artifact(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
