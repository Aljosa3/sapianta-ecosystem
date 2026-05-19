"""Filesystem task transport with approval-gated dispatch."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from .lifecycle import transition_lifecycle, with_lifecycle_state
from .replay_logger import append_replay_event, canonical_json, sha256_digest
from .schema_validator import validate_task_package

RUNTIME_DIRS = ("incoming", "approved", "dispatched", "results", "replay_log", "quarantine")


def ensure_runtime_dirs(bridge_root: Path) -> None:
    for dirname in RUNTIME_DIRS:
        (bridge_root / dirname).mkdir(parents=True, exist_ok=True)


def _safe_name(identifier: str) -> str:
    allowed = [char if char.isalnum() or char in {"-", "_"} else "_" for char in identifier]
    value = "".join(allowed).strip("_")
    return value or "unnamed"


def _package_path(bridge_root: Path, state_dir: str, package: dict) -> Path:
    return bridge_root / state_dir / f"{_safe_name(str(package.get('task_id', 'invalid')))}.json"


def _write_json_exclusive(path: Path, package: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(canonical_json(package) + "\n")


def _write_json_replace(path: Path, package: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(package) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def quarantine_package(
    *,
    bridge_root: Path,
    package: dict,
    previous_state: str,
    reason: str,
    actor: str = "agol_bridge",
) -> dict:
    ensure_runtime_dirs(bridge_root)
    quarantined = with_lifecycle_state(deepcopy(package), "QUARANTINED")
    task_id = str(quarantined.get("task_id", f"invalid-{sha256_digest(quarantined)[:16]}"))
    path = bridge_root / "quarantine" / f"{_safe_name(task_id)}-{sha256_digest(quarantined)[:16]}.json"
    _write_json_exclusive(path, quarantined)
    replay = append_replay_event(
        bridge_root=bridge_root,
        task_id=task_id,
        event_type="QUARANTINE",
        previous_state=previous_state,
        next_state="QUARANTINED",
        package=quarantined,
        actor=actor,
        reason=reason,
    )
    return {"status": "QUARANTINED", "path": str(path), "package": quarantined, "replay": replay}


def _blocked_overwrite(path: Path) -> dict:
    return {
        "status": "BLOCKED",
        "errors": [{"field": str(path), "error": "silent overwrite blocked"}],
    }


def submit_task(package: dict, *, bridge_root: Path, source_path: Path | None = None) -> dict:
    ensure_runtime_dirs(bridge_root)
    validation = validate_task_package(package)
    if not validation["valid"]:
        return quarantine_package(
            bridge_root=bridge_root,
            package=package if isinstance(package, dict) else {"task_id": "invalid", "metadata": {}},
            previous_state="CREATED",
            reason="invalid schema",
        )

    normalized = with_lifecycle_state(package, "CREATED")
    approval_required = normalized["approval_required"]
    approved = normalized["metadata"].get("approved", False)
    if approval_required and not approved:
        transition = transition_lifecycle(normalized, "WAITING_FOR_APPROVAL")
        waiting = transition["package"]
        path = _package_path(bridge_root, "incoming", waiting)
        if path.exists() and path != source_path:
            return _blocked_overwrite(path)
        _write_json_replace(path, waiting)
        replay = append_replay_event(
            bridge_root=bridge_root,
            task_id=waiting["task_id"],
            event_type="WAITING_FOR_APPROVAL",
            previous_state=transition["previous_state"],
            next_state=transition["next_state"],
            package=waiting,
            actor="agol_bridge",
            reason="approval required",
        )
        return {"status": "WAITING_FOR_APPROVAL", "path": str(path), "package": waiting, "replay": replay}

    transition = transition_lifecycle(normalized, "APPROVED")
    approved_package = transition["package"]
    approved_package.setdefault("metadata", {})["approved"] = True
    path = _package_path(bridge_root, "approved", approved_package)
    if path.exists() and path != source_path:
        return _blocked_overwrite(path)
    _write_json_replace(path, approved_package)
    replay = append_replay_event(
        bridge_root=bridge_root,
        task_id=approved_package["task_id"],
        event_type="APPROVED",
        previous_state=transition["previous_state"],
        next_state=transition["next_state"],
        package=approved_package,
        actor="agol_bridge",
        reason="approval not required" if not approval_required else "approval present",
    )
    return {"status": "APPROVED", "path": str(path), "package": approved_package, "replay": replay}


def approve_task(task_id: str, *, bridge_root: Path, approved_by: str = "human") -> dict:
    ensure_runtime_dirs(bridge_root)
    path = bridge_root / "incoming" / f"{_safe_name(task_id)}.json"
    if not path.exists():
        return {"status": "BLOCKED", "errors": [{"field": "task_id", "error": "waiting task not found"}]}
    package = _read_json(path)
    validation = validate_task_package(package)
    if not validation["valid"]:
        return quarantine_package(
            bridge_root=bridge_root,
            package=package,
            previous_state=package.get("metadata", {}).get("lifecycle_state", "CREATED"),
            reason="invalid schema during approval",
        )
    transition = transition_lifecycle(package, "APPROVED")
    if transition["status"] != "TRANSITIONED":
        return quarantine_package(
            bridge_root=bridge_root,
            package=transition["package"],
            previous_state=transition["previous_state"],
            reason="unexpected approval transition",
        )
    approved_package = transition["package"]
    approved_package.setdefault("metadata", {})["approved"] = True
    approved_package["metadata"]["approved_by"] = approved_by
    approved_path = _package_path(bridge_root, "approved", approved_package)
    if approved_path.exists():
        return _blocked_overwrite(approved_path)
    _write_json_replace(approved_path, approved_package)
    path.unlink()
    replay = append_replay_event(
        bridge_root=bridge_root,
        task_id=approved_package["task_id"],
        event_type="APPROVED",
        previous_state=transition["previous_state"],
        next_state=transition["next_state"],
        package=approved_package,
        actor=approved_by,
        reason="explicit approval",
    )
    return {"status": "APPROVED", "path": str(approved_path), "package": approved_package, "replay": replay}


def dispatch_task(task_id: str, *, bridge_root: Path) -> dict:
    ensure_runtime_dirs(bridge_root)
    source = bridge_root / "approved" / f"{_safe_name(task_id)}.json"
    if not source.exists():
        waiting = bridge_root / "incoming" / f"{_safe_name(task_id)}.json"
        if waiting.exists():
            return {"status": "WAITING_FOR_APPROVAL", "errors": [{"field": "approval", "error": "approval missing"}]}
        return {"status": "BLOCKED", "errors": [{"field": "task_id", "error": "approved task not found"}]}
    package = _read_json(source)
    validation = validate_task_package(package)
    if not validation["valid"]:
        return quarantine_package(
            bridge_root=bridge_root,
            package=package,
            previous_state=package.get("metadata", {}).get("lifecycle_state", "CREATED"),
            reason="invalid schema during dispatch",
        )
    if package["approval_required"] and package["metadata"].get("approved") is not True:
        return {"status": "WAITING_FOR_APPROVAL", "errors": [{"field": "approval", "error": "approval missing"}]}
    transition = transition_lifecycle(package, "DISPATCHED")
    if transition["status"] != "TRANSITIONED":
        return quarantine_package(
            bridge_root=bridge_root,
            package=transition["package"],
            previous_state=transition["previous_state"],
            reason="unexpected dispatch transition",
        )
    dispatched = transition["package"]
    destination = _package_path(bridge_root, "dispatched", dispatched)
    try:
        _write_json_exclusive(destination, dispatched)
    except FileExistsError:
        return {
            "status": "BLOCKED",
            "errors": [{"field": "dispatched", "error": "immutable dispatched package already exists"}],
        }
    source.unlink()
    replay = append_replay_event(
        bridge_root=bridge_root,
        task_id=dispatched["task_id"],
        event_type="DISPATCHED",
        previous_state=transition["previous_state"],
        next_state=transition["next_state"],
        package=dispatched,
        actor="agol_bridge",
        reason="filesystem handoff only",
    )
    return {"status": "DISPATCHED", "path": str(destination), "package": dispatched, "replay": replay}
