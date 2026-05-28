"""Tests for REPLAY_CHAIN_INTEGRITY_VALIDATION_V1."""

from __future__ import annotations

import json

from aigol.runtime.operator.runtime_execution_cli import (
    latest_runtime_replay,
    list_runtime_replays,
    render_replay_listing,
    run_runtime_inspection,
    runtime_continuity_summary,
)


def _append_entry(runtime_root, source_reference: str, replay_reference: str) -> None:
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    source_path = runtime_root / "evidence" / source_reference / "governed_return.json"
    entry = json.loads(source_path.read_text(encoding="utf-8"))
    entry["replay_identity"] = replay_reference
    entry["diagnostic_evidence"]["runtime_operation"]["operation_id"] = replay_reference
    entry["diagnostic_evidence"]["runtime_operation"]["replay_reference"] = replay_reference
    with ledger_path.open("a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")


def test_valid_replay_chain_integrity_is_deterministic_and_append_only(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    for _ in range(3):
        assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger_path.read_text(encoding="utf-8")

    listed = list_runtime_replays(runtime_root=runtime_root)
    summary = runtime_continuity_summary(runtime_root=runtime_root)
    latest = latest_runtime_replay(runtime_root=runtime_root)

    assert listed["fail_closed"] is False
    assert [replay["replay_reference"] for replay in listed["replays"]] == [
        "RUNTIME-INSPECTION-000003",
        "RUNTIME-INSPECTION-000002",
        "RUNTIME-INSPECTION-000001",
    ]
    assert summary["continuity"] == "valid"
    assert summary["verified"] == 3
    assert latest["replay_reference"] == "RUNTIME-INSPECTION-000003"
    assert ledger_path.read_text(encoding="utf-8") == before


def test_replay_gap_detection_fails_closed_and_prevents_append(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    _append_entry(runtime_root, "RUNTIME-INSPECTION-000001", "RUNTIME-INSPECTION-000003")
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger_path.read_text(encoding="utf-8")

    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["fail_closed"] is True
    assert result["persistence"]["status"] == "NOT_PERSISTED"
    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert runtime_continuity_summary(runtime_root=runtime_root)["fail_closed"] is True
    assert ledger_path.read_text(encoding="utf-8") == before


def test_duplicate_replay_identity_detection_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    _append_entry(runtime_root, "RUNTIME-INSPECTION-000001", "RUNTIME-INSPECTION-000001")

    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert latest_runtime_replay(runtime_root=runtime_root)["fail_closed"] is True


def test_replay_ordering_corruption_detection_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    for _ in range(3):
        assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    entries = ledger_path.read_text(encoding="utf-8").splitlines()
    ledger_path.write_text("\n".join([entries[2], entries[1], entries[0]]) + "\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert runtime_continuity_summary(runtime_root=runtime_root)["malformed_replay_count"] == 1


def test_replay_ancestry_corruption_detection_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    evidence_path = runtime_root / "evidence" / "RUNTIME-INSPECTION-000001" / "governed_return.json"
    artifact = json.loads(evidence_path.read_text(encoding="utf-8"))
    artifact["diagnostic_evidence"]["runtime_operation"]["replay_reference"] = "RUNTIME-INSPECTION-000002"
    evidence_path.write_text(json.dumps(artifact, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert runtime_continuity_summary(runtime_root=runtime_root)["fail_closed"] is True


def test_replay_chain_continuity_after_runtime_restart(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["operation"]["replay_reference"] == "RUNTIME-INSPECTION-000001"

    # A second call reconstructs the next identity from persisted replay history only.
    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["fail_closed"] is False
    assert result["operation"]["replay_reference"] == "RUNTIME-INSPECTION-000002"
    assert "replay_reference: RUNTIME-INSPECTION-000002" in render_replay_listing(
        list_runtime_replays(runtime_root=runtime_root)
    )


def test_manual_replay_counter_skip_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"

    result = run_runtime_inspection(operation_id="RUNTIME-INSPECTION-000002", runtime_root=runtime_root)

    assert result["fail_closed"] is True
    assert result["persistence"]["status"] == "NOT_PERSISTED"
    assert (runtime_root / "ledger" / "governed_returns.jsonl").exists() is False
