"""Replay-safe binding from ChatGPT ingress to NL envelope proposal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ingress_session import stable_hash


@dataclass(frozen=True)
class IngressBinding:
    session_id: str
    request_id: str
    semantic_request_id: str
    replay_identity: str
    envelope_id: str | None
    admissibility: str | None

    def to_dict(self) -> dict[str, Any]:
        value = {
            "session_id": self.session_id,
            "request_id": self.request_id,
            "semantic_request_id": self.semantic_request_id,
            "replay_identity": self.replay_identity,
            "envelope_id": self.envelope_id,
            "admissibility": self.admissibility,
        }
        value["ingress_binding_sha256"] = stable_hash(value)
        value["replay_safe"] = True
        return value


def create_ingress_binding(
    *,
    ingress_request: dict[str, Any],
    envelope_proposal: dict[str, Any],
) -> IngressBinding:
    session = ingress_request["session"]
    semantic_request = envelope_proposal.get("semantic_request", {})
    envelope = envelope_proposal.get("execution_envelope") or {}
    admissibility = envelope_proposal.get("admissibility", {})
    return IngressBinding(
        session_id=session["session_id"],
        request_id=session["request_id"],
        semantic_request_id=semantic_request.get("semantic_request_id", ""),
        replay_identity=semantic_request.get("replay_identity", session.get("replay_binding", "")),
        envelope_id=envelope.get("envelope_id"),
        admissibility=admissibility.get("admissibility"),
    )


def validate_ingress_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, IngressBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_binding", "reason": "binding must be an object"}]}
    for field in ("session_id", "request_id", "semantic_request_id", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "binding field must be non-empty"})
    expected = None
    if not errors:
        payload = {
            "session_id": value["session_id"],
            "request_id": value["request_id"],
            "semantic_request_id": value["semantic_request_id"],
            "replay_identity": value["replay_identity"],
            "envelope_id": value.get("envelope_id"),
            "admissibility": value.get("admissibility"),
        }
        expected = stable_hash(payload)
        if value.get("ingress_binding_sha256") != expected:
            errors.append({"field": "ingress_binding_sha256", "reason": "ingress binding hash mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "ingress binding must be replay-safe"})
    return {"valid": not errors, "errors": errors, "ingress_binding_sha256": expected}
