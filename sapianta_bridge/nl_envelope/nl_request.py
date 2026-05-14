"""Replay-safe natural language request model."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def semantic_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class NaturalLanguageRequest:
    semantic_request_id: str
    raw_text: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_request_id": self.semantic_request_id,
            "raw_text": self.raw_text,
            "replay_identity": self.replay_identity,
            "raw_text_sha256": semantic_hash(self.raw_text),
            "execution_authority_granted": False,
            "prompt_is_authority": False,
        }


def create_nl_request(raw_text: str, *, semantic_request_id: str | None = None) -> NaturalLanguageRequest:
    normalized = raw_text.strip()
    request_hash = semantic_hash(normalized)
    return NaturalLanguageRequest(
        semantic_request_id=semantic_request_id or f"SEM-{request_hash[:12]}",
        raw_text=raw_text,
        replay_identity=f"REPLAY-{request_hash[:16]}",
    )


def validate_nl_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, NaturalLanguageRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "nl_request", "reason": "request must be an object"}]}
    for field in ("semantic_request_id", "raw_text", "replay_identity"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "field must be non-empty"})
    if value.get("execution_authority_granted") is not False:
        errors.append({"field": "execution_authority_granted", "reason": "natural language cannot grant authority"})
    if value.get("prompt_is_authority") is not False:
        errors.append({"field": "prompt_is_authority", "reason": "prompt is not authority"})
    expected_hash = semantic_hash(value.get("raw_text", "")) if isinstance(value.get("raw_text"), str) else None
    if value.get("raw_text_sha256") not in (None, expected_hash):
        errors.append({"field": "raw_text_sha256", "reason": "raw text hash mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "replay_safe": not errors,
        "serializable": not errors,
    }
