"""Deterministic identity for the real bounded Codex E2E loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


def e2e_loop_id_for(*, chatgpt_request: str, provider_id: str, replay_identity: str) -> str:
    return f"REAL-E2E-CODEX-LOOP-{stable_hash({'chatgpt_request': chatgpt_request, 'provider_id': provider_id, 'replay_identity': replay_identity})[:24]}"


@dataclass(frozen=True)
class RealE2ELoopIdentity:
    loop_id: str
    provider_id: str
    replay_identity: str
    request_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "request_sha256": self.request_sha256,
            "immutable": True,
            "replay_safe": True,
        }


def create_e2e_loop_identity(*, chatgpt_request: str, provider_id: str, replay_identity: str) -> RealE2ELoopIdentity:
    return RealE2ELoopIdentity(
        loop_id=e2e_loop_id_for(
            chatgpt_request=chatgpt_request,
            provider_id=provider_id,
            replay_identity=replay_identity,
        ),
        provider_id=provider_id,
        replay_identity=replay_identity,
        request_sha256=stable_hash({"chatgpt_request": chatgpt_request}),
    )


def validate_e2e_loop_identity(identity: Any, *, chatgpt_request: str | None = None) -> dict[str, Any]:
    value = identity.to_dict() if hasattr(identity, "to_dict") else identity
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "loop_identity", "reason": "must be an object"}]}
    for field in ("loop_id", "provider_id", "replay_identity", "request_sha256"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "loop identity field must be non-empty"})
    if chatgpt_request is not None and value.get("request_sha256") != stable_hash({"chatgpt_request": chatgpt_request}):
        errors.append({"field": "request_sha256", "reason": "request hash mismatch"})
    if not errors and chatgpt_request is not None:
        expected = e2e_loop_id_for(
            chatgpt_request=chatgpt_request,
            provider_id=value["provider_id"],
            replay_identity=value["replay_identity"],
        )
        if value["loop_id"] != expected:
            errors.append({"field": "loop_id", "reason": "loop identity mismatch"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "loop identity must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "loop identity must be replay-safe"})
    return {"valid": not errors, "errors": errors}
