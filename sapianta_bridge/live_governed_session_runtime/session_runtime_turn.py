"""Persistent runtime turn attachment."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionRuntimeTurn:
    session_runtime_id: str
    interaction_turn_id: str
    prior_interaction_turn_id: str | None

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_session_runtime_turn(*, session_runtime: dict, attachment_output: dict, prior_output: dict | None = None) -> SessionRuntimeTurn:
    binding = attachment_output["runtime_attachment_binding"]
    prior = prior_output.get("turn", {}).get("interaction_turn_id") if prior_output else None
    return SessionRuntimeTurn(session_runtime["session_runtime_id"], binding["interaction_turn_id"], prior)
