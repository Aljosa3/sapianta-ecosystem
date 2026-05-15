"""Replay-visible live runtime binding."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class LiveRuntimeBinding:
    live_runtime_session_id: str
    interaction_loop_session_id: str
    interaction_turn_id: str
    transport_session_id: str
    governed_session_id: str
    execution_gate_id: str
    provider_invocation_id: str
    bounded_runtime_id: str
    result_capture_id: str
    response_return_id: str

    def to_dict(self) -> dict[str, Any]:
        value = self.__dict__.copy()
        value["binding_sha256"] = stable_hash(value)
        value["replay_safe"] = True
        return value


def create_live_runtime_binding(*, session: dict[str, Any], loop_output: dict[str, Any]) -> LiveRuntimeBinding:
    binding = loop_output["binding"]
    return LiveRuntimeBinding(
        session["live_runtime_session_id"], binding["interaction_session_id"], binding["turn_id"],
        binding["transport_session_id"], binding["governed_session_id"], binding["execution_gate_id"],
        binding["provider_invocation_id"], binding["bounded_runtime_id"], binding["result_capture_id"], binding["response_return_id"],
    )
