"""Persistent runtime binding."""

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


@dataclass(frozen=True)
class SessionRuntimeBinding:
    session_runtime_id: str
    interaction_loop_session_id: str
    interaction_turn_id: str
    live_runtime_session_id: str
    runtime_attachment_session_id: str
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
        return value


def create_session_runtime_binding(*, session_runtime: dict, attachment_output: dict) -> SessionRuntimeBinding:
    b = attachment_output["runtime_attachment_binding"]
    return SessionRuntimeBinding(session_runtime["session_runtime_id"], b["interaction_loop_session_id"], b["interaction_turn_id"], b["live_runtime_session_id"], b["runtime_attachment_session_id"], b["transport_session_id"], b["governed_session_id"], b["execution_gate_id"], b["provider_invocation_id"], b["bounded_runtime_id"], b["result_capture_id"], b["response_return_id"])
