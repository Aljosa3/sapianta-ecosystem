"""Explicit governed interaction loop turn."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class InteractionLoopTurn:
    interaction_session_id: str
    turn_index: int
    human_input: str
    prior_turn_id: str | None
    prior_response_id: str | None

    def to_dict(self) -> dict[str, Any]:
        value = {
            "interaction_session_id": self.interaction_session_id,
            "turn_index": self.turn_index,
            "human_input": self.human_input,
            "prior_turn_id": self.prior_turn_id,
            "prior_response_id": self.prior_response_id,
        }
        value["turn_id"] = f"LOOP-TURN-{stable_hash(value)[:24]}"
        value["hidden_context_reconstruction_present"] = False
        return value


def create_loop_turn(*, session: dict[str, Any], turn_index: int, human_input: str, prior_turn_id: str | None = None, prior_response_id: str | None = None) -> InteractionLoopTurn:
    return InteractionLoopTurn(session["interaction_session_id"], turn_index, human_input, prior_turn_id, prior_response_id)
