"""Replay-safe execution envelope binding."""

from __future__ import annotations

import hashlib
import json
from typing import Any


REPLAY_BINDING_FIELDS = (
    "replay_identity",
    "provider_id",
    "authority_scope",
    "workspace_scope",
    "validation_requirements",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_replay_binding(envelope: dict[str, Any]) -> str:
    binding = {field: envelope.get(field) for field in REPLAY_BINDING_FIELDS}
    return hashlib.sha256(canonical_json(binding).encode("utf-8")).hexdigest()


def validate_replay_binding(envelope: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(envelope, dict):
        return {
            "valid": False,
            "errors": [{"field": "envelope", "reason": "envelope must be an object"}],
        }
    for field in REPLAY_BINDING_FIELDS:
        if field not in envelope:
            errors.append({"field": field, "reason": "missing replay binding field"})
    replay_identity = envelope.get("replay_identity")
    if not isinstance(replay_identity, str) or not replay_identity.strip():
        errors.append({"field": "replay_identity", "reason": "replay identity must be non-empty"})
    expected = compute_replay_binding(envelope) if not errors else None
    provided = envelope.get("replay_binding_sha256")
    if provided is not None and provided != expected:
        errors.append({"field": "replay_binding_sha256", "reason": "replay binding mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "replay_binding_sha256": expected,
        "same_envelope_same_authority_semantics": not errors,
    }
