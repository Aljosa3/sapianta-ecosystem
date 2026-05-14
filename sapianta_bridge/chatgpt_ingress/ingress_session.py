"""Deterministic ChatGPT ingress session identity."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IngressSession:
    session_id: str
    request_id: str
    timestamp: str
    replay_binding: str
    semantic_lineage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "replay_binding": self.replay_binding,
            "semantic_lineage": self.semantic_lineage,
            "mutable_memory": False,
            "chatgpt_governance_authority": False,
        }


def create_ingress_session(
    *,
    raw_text: str,
    timestamp: str = DEFAULT_TIMESTAMP,
    conversation_id: str = "CHATGPT-SESSION",
) -> IngressSession:
    request_hash = stable_hash({"raw_text": raw_text})
    session_payload = {
        "conversation_id": conversation_id,
        "request_hash": request_hash,
        "timestamp": timestamp,
    }
    session_id = f"INGRESS-SESSION-{stable_hash(session_payload)[:16]}"
    request_id = f"INGRESS-REQUEST-{request_hash[:16]}"
    lineage = {
        "conversation_id": conversation_id,
        "request_hash": request_hash,
        "source": "CHATGPT_INTERACTION",
    }
    replay_binding = stable_hash(
        {
            "session_id": session_id,
            "request_id": request_id,
            "timestamp": timestamp,
            "semantic_lineage": lineage,
        }
    )
    return IngressSession(
        session_id=session_id,
        request_id=request_id,
        timestamp=timestamp,
        replay_binding=replay_binding,
        semantic_lineage=lineage,
    )


def validate_ingress_session(session: Any) -> dict[str, Any]:
    value = session.to_dict() if isinstance(session, IngressSession) else session
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "session", "reason": "session must be an object"}]}
    for field in ("session_id", "request_id", "timestamp", "replay_binding"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "session field must be non-empty"})
    if not isinstance(value.get("semantic_lineage"), dict) or not value.get("semantic_lineage"):
        errors.append({"field": "semantic_lineage", "reason": "semantic lineage must be present"})
    if value.get("mutable_memory") is not False:
        errors.append({"field": "mutable_memory", "reason": "ingress session must not mutate memory"})
    if value.get("chatgpt_governance_authority") is not False:
        errors.append({"field": "chatgpt_governance_authority", "reason": "ChatGPT is not governance"})
    if not errors:
        expected = stable_hash(
            {
                "session_id": value["session_id"],
                "request_id": value["request_id"],
                "timestamp": value["timestamp"],
                "semantic_lineage": value["semantic_lineage"],
            }
        )
        if value["replay_binding"] != expected:
            errors.append({"field": "replay_binding", "reason": "session replay binding mismatch"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}
