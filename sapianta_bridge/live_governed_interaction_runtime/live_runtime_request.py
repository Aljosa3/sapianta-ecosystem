"""Live runtime request."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LiveRuntimeRequest:
    live_runtime_session_id: str
    interaction_turn_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"live_runtime_session_id": self.live_runtime_session_id, "interaction_turn_id": self.interaction_turn_id, "autonomous_continuation_requested": False}


def create_live_runtime_request(*, session: dict[str, Any], loop_output: dict[str, Any]) -> LiveRuntimeRequest:
    return LiveRuntimeRequest(session["live_runtime_session_id"], loop_output["turn"]["turn_id"])
