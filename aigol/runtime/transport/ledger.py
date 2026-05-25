"""Append-only runtime ledger for dispatch continuity."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError

from .serialization import canonical_serialize, replay_hash


class RuntimeLedger:
    """Append-only JSONL ledger for runtime transport events."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.ledger_dir = self.root / "runtime_replay"

    def ledger_path(self, runtime_id: str) -> Path:
        return self.ledger_dir / f"runtime_{runtime_id}_ledger.jsonl"

    def append(self, runtime_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = self.ledger_path(runtime_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        sequence = len(self.read(runtime_id, allow_missing=True))
        entry = {
            "sequence": sequence,
            "runtime_id": runtime_id,
            "event_type": event_type,
            "payload": deepcopy(payload),
        }
        entry["entry_hash"] = replay_hash(entry)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_serialize(entry) + "\n")
        return entry

    def read(self, runtime_id: str, allow_missing: bool = False) -> list[dict[str, Any]]:
        path = self.ledger_path(runtime_id)
        if not path.exists():
            if allow_missing:
                return []
            raise FailClosedRuntimeError(f"runtime ledger missing: {path.name}")
        entries = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FailClosedRuntimeError("runtime ledger entry is not valid JSON") from exc
            expected = deepcopy(entry)
            actual = expected.pop("entry_hash", None)
            if actual != replay_hash(expected):
                raise FailClosedRuntimeError("runtime ledger entry hash mismatch")
            if entry.get("sequence") != line_number:
                raise FailClosedRuntimeError("runtime ledger sequence mismatch")
            entries.append(entry)
        return entries
