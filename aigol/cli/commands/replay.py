"""Replay command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations


def replay_summary(*, chain: dict) -> dict:
    return {
        "command": "aigol replay",
        "replay_identity": chain.get("replay_identity", "UNKNOWN"),
        "hash_continuity": chain.get("hash_continuity", {}),
        "replay_visible": True,
    }


__all__ = ["replay_summary"]

