"""Deterministic live runtime response."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LiveRuntimeResponse:
    live_runtime_session_id: str
    interaction_turn_id: str
    response_return_id: str
    runtime_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "live_runtime_session_id": self.live_runtime_session_id,
            "interaction_turn_id": self.interaction_turn_id,
            "response_return_id": self.response_return_id,
            "runtime_status": self.runtime_status,
            "provider_hidden_state_trusted": False,
            "autonomous_continuation_present": False,
            "replay_safe": True,
        }


def create_live_runtime_response(*, binding: dict[str, Any]) -> LiveRuntimeResponse:
    return LiveRuntimeResponse(binding["live_runtime_session_id"], binding["interaction_turn_id"], binding["response_return_id"], "LIVE_RESPONSE_EMITTED")
