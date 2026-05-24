"""Replay command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path

from aigol.cli.commands.return_continuity import read_ledger_entries, verify_governed_return


def replay_summary(*, chain: dict) -> dict:
    return {
        "command": "aigol replay",
        "replay_identity": chain.get("replay_identity", "UNKNOWN"),
        "hash_continuity": chain.get("hash_continuity", {}),
        "replay_visible": True,
    }


def ledger_summary(*, runtime_root: str | Path | None = None, limit: int = 10) -> dict:
    entries = read_ledger_entries(runtime_root=runtime_root, limit=limit)
    return {
        "command": "aigol replay ledger",
        "entries": [
            {
                "replay_identity": entry.get("replay_identity", "UNKNOWN"),
                "execution_status": entry.get("execution_status", "UNKNOWN"),
                "governed_return_hash": entry.get("governed_return_hash", ""),
            }
            for entry in entries
        ],
    }


def verify_replay(*, replay_identity: str, runtime_root: str | Path | None = None) -> dict:
    return verify_governed_return(replay_identity=replay_identity, runtime_root=runtime_root)


__all__ = ["ledger_summary", "replay_summary", "verify_replay"]
