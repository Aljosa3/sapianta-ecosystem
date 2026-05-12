"""Replay-safe deterministic hashing for protocol artifacts."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Iterable


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def canonical_json(value: Any) -> str:
    """Serialize JSON-compatible values in a deterministic form."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _without_hash_fields(value: Any, omitted_fields: set[str]) -> Any:
    cloned = copy.deepcopy(value)
    if not omitted_fields or not isinstance(cloned, dict):
        return cloned

    artifact_hashes = cloned.get("artifact_hashes")
    if isinstance(artifact_hashes, dict):
        for field in omitted_fields:
            artifact_hashes.pop(field, None)
    return cloned


def compute_hash(value: Any, omit_hash_fields: Iterable[str] | None = None) -> str:
    """Compute a SHA256 hash over canonical JSON.

    When an artifact stores its own hash, callers should omit that self-hash
    field so the replay hash is stable and non-recursive.
    """
    omitted = set(omit_hash_fields or ())
    canonical = canonical_json(_without_hash_fields(value, omitted))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def is_valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def verify_hash(
    value: Any,
    expected_hash: str,
    omit_hash_fields: Iterable[str] | None = None,
) -> bool:
    if not is_valid_sha256(expected_hash):
        return False
    return compute_hash(value, omit_hash_fields=omit_hash_fields) == expected_hash

