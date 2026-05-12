"""Append-only quarantine handling for malformed protocol artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .hashing import canonical_json


QUARANTINE_CATEGORIES = (
    "malformed",
    "invalid_hash",
    "invalid_lineage",
    "invalid_lifecycle",
    "unknown_artifact",
)

DEFAULT_QUARANTINE_ROOT = Path(__file__).resolve().parent / "quarantine"


def _source_hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _quarantine_id(source_hash: str, reason: str, timestamp: str) -> str:
    seed = canonical_json(
        {
            "source_hash": source_hash,
            "reason": reason,
            "timestamp": timestamp,
        }
    )
    return "QUARANTINE-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16].upper()


def classify_quarantine_category(errors: list[dict[str, str]] | tuple[dict[str, str], ...]) -> str:
    fields = " ".join(error.get("field", "") for error in errors)
    reasons = " ".join(error.get("reason", "") for error in errors)
    combined = f"{fields} {reasons}".lower()

    if "hash" in combined or "sha256" in combined:
        return "invalid_hash"
    if "lineage" in combined:
        return "invalid_lineage"
    if "state" in combined or "transition" in combined:
        return "invalid_lifecycle"
    if "artifact_type" in combined:
        return "unknown_artifact"
    return "malformed"


def create_quarantine_envelope(
    artifact_path: str | Path,
    *,
    reason: str,
    validation_errors: list[dict[str, str]] | tuple[dict[str, str], ...],
    timestamp: str | None = None,
) -> dict[str, Any]:
    path = Path(artifact_path)
    raw = path.read_bytes()
    recorded_at = timestamp or datetime.now(timezone.utc).isoformat()
    source_hash = _source_hash(raw)
    return {
        "quarantine_id": _quarantine_id(source_hash, reason, recorded_at),
        "timestamp": recorded_at,
        "artifact_path": str(path),
        "reason": reason,
        "validation_errors": list(validation_errors),
        "source_hash": source_hash,
    }


def quarantine_artifact(
    artifact_path: str | Path,
    *,
    reason: str,
    validation_errors: list[dict[str, str]] | tuple[dict[str, str], ...],
    category: str | None = None,
    quarantine_root: str | Path = DEFAULT_QUARANTINE_ROOT,
    timestamp: str | None = None,
) -> dict[str, Any]:
    if not reason:
        raise ValueError("quarantine reason is required")
    if not validation_errors:
        raise ValueError("validation_errors are required")

    source_path = Path(artifact_path)
    raw = source_path.read_bytes()
    envelope = create_quarantine_envelope(
        source_path,
        reason=reason,
        validation_errors=validation_errors,
        timestamp=timestamp,
    )
    target_category = category or classify_quarantine_category(envelope["validation_errors"])
    if target_category not in QUARANTINE_CATEGORIES:
        target_category = "malformed"

    target_dir = Path(quarantine_root) / target_category / envelope["quarantine_id"]
    target_dir.mkdir(parents=True, exist_ok=False)

    artifact_target = target_dir / "artifact.original"
    envelope_target = target_dir / "quarantine.json"
    artifact_target.write_bytes(raw)
    envelope_target.write_text(
        json.dumps(envelope, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return envelope

