"""Deterministic local JSON egress exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_egress_artifact(response: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.write_text(json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n", encoding="utf-8")
    return target


def load_egress_artifact(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
