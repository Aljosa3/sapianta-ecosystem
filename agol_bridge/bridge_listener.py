"""Filesystem listener helpers for AGOL Bridge incoming packages."""

from __future__ import annotations

import json
from pathlib import Path

from .task_dispatcher import ensure_runtime_dirs, quarantine_package, submit_task


def process_incoming_tasks(*, bridge_root: Path) -> list[dict]:
    ensure_runtime_dirs(bridge_root)
    results = []
    for path in sorted((bridge_root / "incoming").glob("*.json")):
        try:
            package = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            package = {"task_id": path.stem, "metadata": {}}
            results.append(
                quarantine_package(
                    bridge_root=bridge_root,
                    package=package,
                    previous_state="CREATED",
                    reason="invalid json",
                )
            )
            path.unlink()
            continue
        state = package.get("metadata", {}).get("lifecycle_state", "CREATED")
        if state == "WAITING_FOR_APPROVAL":
            results.append({"status": "WAITING_FOR_APPROVAL", "path": str(path), "package": package})
            continue
        outcome = submit_task(package, bridge_root=bridge_root, source_path=path)
        results.append(outcome)
        if path.exists() and outcome.get("path") != str(path):
            path.unlink()
    return results
