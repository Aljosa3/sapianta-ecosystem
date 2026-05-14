"""Deterministic active ChatGPT bridge request."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sapianta_bridge.chatgpt_ingress.ingress_session import create_ingress_session, stable_hash
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


@dataclass(frozen=True)
class ActiveChatGPTBridgeRequest:
    original_input: str
    ingress_session_identity: str
    ingress_request_identity: str
    semantic_request_identity: str
    requested_provider_id: str
    replay_identity: str
    timestamp: str
    conversation_id: str
    workspace_hint: dict[str, Any] = field(default_factory=dict)
    authority_hint: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = {
            "original_input": self.original_input,
            "ingress_session_identity": self.ingress_session_identity,
            "ingress_request_identity": self.ingress_request_identity,
            "semantic_request_identity": self.semantic_request_identity,
            "requested_provider_id": self.requested_provider_id,
            "replay_identity": self.replay_identity,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "workspace_hint": self.workspace_hint,
            "authority_hint": self.authority_hint,
            "execution_authority_granted": False,
            "unrestricted_provider_instructions_present": False,
            "hidden_plan_present": False,
            "hidden_memory_present": False,
            "retry_instructions_present": False,
            "routing_instructions_present": False,
        }
        value["bridge_request_id"] = f"BRIDGE-REQUEST-{stable_hash(value)[:16]}"
        value["replay_safe"] = True
        return value


def create_bridge_request(
    raw_text: str,
    *,
    requested_provider_id: str = "deterministic_mock",
    timestamp: str = "1970-01-01T00:00:00Z",
    conversation_id: str = "CHATGPT-SESSION",
    workspace_hint: dict[str, Any] | None = None,
    authority_hint: dict[str, Any] | None = None,
) -> ActiveChatGPTBridgeRequest:
    ingress_session = create_ingress_session(
        raw_text=raw_text,
        timestamp=timestamp,
        conversation_id=conversation_id,
    ).to_dict()
    nl_request = create_nl_request(raw_text).to_dict()
    return ActiveChatGPTBridgeRequest(
        original_input=raw_text,
        ingress_session_identity=ingress_session["session_id"],
        ingress_request_identity=ingress_session["request_id"],
        semantic_request_identity=nl_request["semantic_request_id"],
        requested_provider_id=requested_provider_id,
        replay_identity=nl_request["replay_identity"],
        timestamp=timestamp,
        conversation_id=conversation_id,
        workspace_hint=workspace_hint or {},
        authority_hint=authority_hint or {},
    )


def validate_bridge_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, ActiveChatGPTBridgeRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "bridge_request", "reason": "must be an object"}]}
    for field in (
        "bridge_request_id",
        "original_input",
        "ingress_session_identity",
        "ingress_request_identity",
        "semantic_request_identity",
        "requested_provider_id",
        "replay_identity",
    ):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "bridge request field must be non-empty"})
    for field in (
        "execution_authority_granted",
        "unrestricted_provider_instructions_present",
        "hidden_plan_present",
        "hidden_memory_present",
        "retry_instructions_present",
        "routing_instructions_present",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "bridge request contains forbidden authority"})
    expected = None
    if not errors:
        payload = dict(value)
        payload.pop("bridge_request_id", None)
        payload.pop("replay_safe", None)
        expected = f"BRIDGE-REQUEST-{stable_hash(payload)[:16]}"
        if value["bridge_request_id"] != expected:
            errors.append({"field": "bridge_request_id", "reason": "bridge request identity mismatch"})
    return {"valid": not errors, "errors": errors, "bridge_request_id": expected, "replay_safe": not errors}
