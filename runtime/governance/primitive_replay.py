"""Shared replay and continuity helpers for governed primitives."""

from __future__ import annotations

import hashlib
import json
from typing import Any


CANONICAL_REPLAY_FIELDS = (
    "primitive_id",
    "request_hash",
    "command_hash",
    "scope_hash",
    "replay_lineage",
    "deterministic_hash",
)


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def build_replay_identity(
    *,
    primitive_id: str,
    request_payload: dict[str, Any],
    command: tuple[str, ...],
    scope_payload: dict[str, Any],
    replay_lineage: tuple[str, ...],
) -> dict[str, object]:
    return {
        "command_hash": stable_hash(list(command)),
        "primitive_id": primitive_id,
        "replay_lineage": replay_lineage,
        "request_hash": stable_hash(request_payload),
        "scope_hash": stable_hash(scope_payload),
    }


def build_deterministic_result_hash(result_payload: dict[str, Any]) -> str:
    return stable_hash(result_payload)

