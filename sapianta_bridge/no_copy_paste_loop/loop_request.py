"""Deterministic no-copy/paste loop request."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sapianta_bridge.active_chatgpt_bridge.bridge_binding import stable_hash
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


@dataclass(frozen=True)
class NoCopyPasteLoopRequest:
    chatgpt_input: str
    requested_provider_id: str
    replay_identity: str
    semantic_request_id: str
    conversation_id: str
    timestamp: str
    workspace_hint: dict[str, Any] = field(default_factory=dict)
    authority_hint: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = {
            "chatgpt_input": self.chatgpt_input,
            "requested_provider_id": self.requested_provider_id,
            "replay_identity": self.replay_identity,
            "semantic_request_id": self.semantic_request_id,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "workspace_hint": self.workspace_hint,
            "authority_hint": self.authority_hint,
            "chatgpt_is_governance": False,
            "natural_language_is_execution_authority": False,
            "proposal_is_execution": False,
            "provider_is_governance": False,
            "loop_is_orchestration": False,
            "hidden_prompt_rewriting_present": False,
            "memory_mutation_present": False,
            "retry_requested": False,
            "routing_requested": False,
            "autonomous_continuation_requested": False,
        }
        value["loop_request_id"] = f"LOOP-REQUEST-{stable_hash(value)[:16]}"
        value["replay_safe"] = True
        return value


def create_loop_request(
    chatgpt_input: str,
    *,
    requested_provider_id: str = "deterministic_mock",
    conversation_id: str = "CHATGPT-SESSION",
    timestamp: str = "1970-01-01T00:00:00Z",
    workspace_hint: dict[str, Any] | None = None,
    authority_hint: dict[str, Any] | None = None,
) -> NoCopyPasteLoopRequest:
    nl_request = create_nl_request(chatgpt_input).to_dict()
    return NoCopyPasteLoopRequest(
        chatgpt_input=chatgpt_input,
        requested_provider_id=requested_provider_id,
        replay_identity=nl_request["replay_identity"],
        semantic_request_id=nl_request["semantic_request_id"],
        conversation_id=conversation_id,
        timestamp=timestamp,
        workspace_hint=workspace_hint or {},
        authority_hint=authority_hint or {},
    )


def validate_loop_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, NoCopyPasteLoopRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "loop_request", "reason": "must be an object"}]}
    for field in (
        "loop_request_id",
        "chatgpt_input",
        "requested_provider_id",
        "replay_identity",
        "semantic_request_id",
        "conversation_id",
        "timestamp",
    ):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "loop request field must be non-empty"})
    for field in (
        "chatgpt_is_governance",
        "natural_language_is_execution_authority",
        "proposal_is_execution",
        "provider_is_governance",
        "loop_is_orchestration",
        "hidden_prompt_rewriting_present",
        "memory_mutation_present",
        "retry_requested",
        "routing_requested",
        "autonomous_continuation_requested",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "loop request contains forbidden authority"})
    expected = None
    if not errors:
        payload = dict(value)
        payload.pop("loop_request_id", None)
        payload.pop("replay_safe", None)
        expected = f"LOOP-REQUEST-{stable_hash(payload)[:16]}"
        if value["loop_request_id"] != expected:
            errors.append({"field": "loop_request_id", "reason": "loop request identity mismatch"})
    return {"valid": not errors, "errors": errors, "loop_request_id": expected, "replay_safe": not errors}
