"""Deterministic result package return for AGOL Bridge."""

from __future__ import annotations

from pathlib import Path

from .replay_logger import append_replay_event, canonical_json, sha256_digest
from .schema_validator import validate_result_package
from .task_dispatcher import ensure_runtime_dirs


def write_result_package(result_package: dict, *, bridge_root: Path) -> dict:
    ensure_runtime_dirs(bridge_root)
    validation = validate_result_package(result_package)
    result_id = f"RESULT-{sha256_digest(result_package)[:24]}"
    if not validation["valid"]:
        path = bridge_root / "quarantine" / f"{result_id}.json"
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(canonical_json(result_package) + "\n")
        except FileExistsError:
            return {
                "status": "BLOCKED",
                "errors": [{"field": str(path), "error": "silent overwrite blocked"}],
            }
        replay = append_replay_event(
            bridge_root=bridge_root,
            task_id=result_id,
            event_type="QUARANTINE",
            previous_state="RETURNED",
            next_state="QUARANTINED",
            package=result_package if isinstance(result_package, dict) else {"invalid_result": True},
            actor="agol_bridge",
            reason="invalid result schema",
        )
        return {"status": "QUARANTINED", "path": str(path), "validation": validation, "replay": replay}

    path = bridge_root / "results" / f"{result_id}.json"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(canonical_json(result_package) + "\n")
    replay = append_replay_event(
        bridge_root=bridge_root,
        task_id=result_id,
        event_type="RETURNED",
        previous_state="DISPATCHED",
        next_state="RETURNED",
        package=result_package,
        actor="codex",
        reason="result package returned",
    )
    return {"status": "RETURNED", "path": str(path), "validation": validation, "replay": replay}
