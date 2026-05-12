from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sapianta_bridge.protocol.enforcement import enforce_artifact_path
from sapianta_bridge.protocol.quarantine import (
    classify_quarantine_category,
    create_quarantine_envelope,
    quarantine_artifact,
)

from protocol_fixtures import valid_task


def test_quarantine_preserves_original_artifact(tmp_path: Path) -> None:
    artifact_path = tmp_path / "task.json"
    raw = '{"protocol_version":"9.9"}'
    artifact_path.write_text(raw, encoding="utf-8")
    errors = [{"field": "protocol_version", "reason": "invalid protocol version"}]

    envelope = quarantine_artifact(
        artifact_path,
        reason="invalid protocol version",
        validation_errors=errors,
        quarantine_root=tmp_path / "quarantine",
        timestamp="2026-05-12T00:00:00+00:00",
    )

    stored = (
        tmp_path
        / "quarantine"
        / "malformed"
        / envelope["quarantine_id"]
        / "artifact.original"
    )
    assert stored.read_text(encoding="utf-8") == raw


def test_quarantine_envelope_contains_evidence(tmp_path: Path) -> None:
    artifact_path = tmp_path / "task.json"
    artifact_path.write_text(json.dumps(valid_task()), encoding="utf-8")
    errors = [{"field": "lineage.parent_task_id", "reason": "lineage id must be non-empty"}]

    envelope = create_quarantine_envelope(
        artifact_path,
        reason="invalid lineage",
        validation_errors=errors,
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert envelope["quarantine_id"].startswith("QUARANTINE-")
    assert envelope["timestamp"] == "2026-05-12T00:00:00+00:00"
    assert envelope["validation_errors"] == errors
    assert envelope["source_hash"].startswith("sha256:")


def test_invalid_json_quarantined(tmp_path: Path) -> None:
    artifact_path = tmp_path / "task.json"
    artifact_path.write_text("{", encoding="utf-8")
    result = enforce_artifact_path(artifact_path)

    assert result.allowed_to_continue is False
    assert result.required_state == "QUARANTINED"
    assert classify_quarantine_category(result.reasons) == "malformed"


def test_unknown_artifact_quarantine_category() -> None:
    errors = [{"field": "artifact_type", "reason": "unsupported or unknown artifact type"}]
    assert classify_quarantine_category(errors) == "unknown_artifact"
