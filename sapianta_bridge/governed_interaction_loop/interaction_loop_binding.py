"""Continuity binding for governed loop turns."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class InteractionLoopBinding:
    interaction_session_id: str
    turn_id: str
    prior_turn_id: str | None
    prior_response_id: str | None
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


def create_loop_binding(*, turn: dict[str, Any], transport_binding: dict[str, Any]) -> InteractionLoopBinding:
    return InteractionLoopBinding(
        interaction_session_id=turn["interaction_session_id"],
        turn_id=turn["turn_id"],
        prior_turn_id=turn["prior_turn_id"],
        prior_response_id=turn["prior_response_id"],
        transport_session_id=transport_binding["transport_session_id"],
        governed_session_id=transport_binding["governed_session_id"],
        execution_gate_id=transport_binding["execution_gate_id"],
        provider_invocation_id=transport_binding["provider_invocation_id"],
        bounded_runtime_id=transport_binding["bounded_runtime_id"],
        result_capture_id=transport_binding["result_capture_id"],
        response_return_id=transport_binding["response_return_id"],
    )
