"""Canonical JSON serialization for runtime transport persistence."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError


def canonical_serialize(data: Any) -> str:
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("runtime transport data must be JSON serializable") from exc


def replay_hash(data: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_serialize(data).encode("utf-8")).hexdigest()


def with_replay_hash(data: dict[str, Any], hash_field: str = "replay_hash") -> dict[str, Any]:
    artifact = deepcopy(data)
    artifact.pop(hash_field, None)
    artifact[hash_field] = replay_hash(artifact)
    return artifact


def verify_replay_hash(data: dict[str, Any], hash_field: str = "replay_hash") -> None:
    if hash_field not in data:
        raise FailClosedRuntimeError(f"{hash_field} is required")
    expected_input = deepcopy(data)
    actual = expected_input.pop(hash_field)
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError("runtime replay hash mismatch")


def write_json_immutable(path: Path, data: dict[str, Any]) -> None:
    if path.exists():
        raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_serialize(data) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FailClosedRuntimeError(f"runtime artifact missing: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"runtime artifact is not valid JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"runtime artifact must be a JSON object: {path.name}")
    return value
