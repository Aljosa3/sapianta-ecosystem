"""Append-only semantic continuity memory persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.serialization import load_json, verify_replay_hash, write_json_immutable


class MemoryStore:
    """Append-only memory artifact store."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.memory_dir = self.root / "runtime_memory"
        self.summary_dir = self.root / "runtime_memory_summaries"

    def memory_contract_path(self, runtime_id: str) -> Path:
        return self.memory_dir / f"runtime_{runtime_id}_memory_contract.json"

    def memory_record_path(self, runtime_id: str) -> Path:
        return self.memory_dir / f"runtime_{runtime_id}_memory_record.json"

    def memory_validation_path(self, runtime_id: str) -> Path:
        return self.memory_dir / f"runtime_{runtime_id}_memory_validation.json"

    def semantic_summary_path(self, runtime_id: str) -> Path:
        return self.summary_dir / f"runtime_{runtime_id}_semantic_summary.json"

    def persist_contract(self, runtime_id: str, contract: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.memory_contract_path(runtime_id), contract)
        return contract

    def persist_record(self, runtime_id: str, record: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.memory_record_path(runtime_id), record)
        return record

    def persist_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.memory_validation_path(runtime_id), validation)
        return validation

    def persist_summary(self, runtime_id: str, summary: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.semantic_summary_path(runtime_id), summary)
        return summary

    def load_contract(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.memory_contract_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_record(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.memory_record_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.memory_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_summary(self, runtime_id: str) -> dict[str, Any]:
        return load_json(self.semantic_summary_path(runtime_id))
