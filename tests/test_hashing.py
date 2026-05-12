from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.protocol.hashing import compute_hash, verify_hash


def test_deterministic_hash_stable_across_runs() -> None:
    left = {"b": [2, 1], "a": {"z": True, "m": None}}
    right = {"a": {"m": None, "z": True}, "b": [2, 1]}

    assert compute_hash(left) == compute_hash(right)
    assert compute_hash(left) == compute_hash(left)


def test_verify_hash_rejects_invalid_hash() -> None:
    artifact = {"protocol_version": "0.1", "value": "stable"}
    assert verify_hash(artifact, "not-a-hash") is False
    assert verify_hash(artifact, "0" * 64) is False
