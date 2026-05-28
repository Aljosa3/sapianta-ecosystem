"""Tests for MINIMAL_RUNTIME_HISTORY_AND_LISTING_V1."""

from __future__ import annotations

import json

from aigol.runtime.operator.runtime_execution_cli import (
    latest_runtime_replay,
    list_runtime_replays,
    main,
    render_latest_replay,
    render_replay_listing,
    run_runtime_inspection,
)


def _record(runtime_root, operation_id: str, timestamp: str) -> None:
    result = run_runtime_inspection(
        operation_id=operation_id,
        created_at=timestamp,
        runtime_root=runtime_root,
    )
    assert result["fail_closed"] is False


def test_replay_listing_is_newest_first_and_readonly(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    _record(runtime_root, "RUNTIME-INSPECTION-000002", "2026-05-27T00:00:02Z")
    _record(runtime_root, "RUNTIME-INSPECTION-000003", "2026-05-27T00:00:03Z")
    ledger = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger.read_text(encoding="utf-8")

    result = list_runtime_replays(runtime_root=runtime_root)

    assert result["count"] == 3
    assert [replay["replay_reference"] for replay in result["replays"]] == [
        "RUNTIME-INSPECTION-000003",
        "RUNTIME-INSPECTION-000002",
        "RUNTIME-INSPECTION-000001",
    ]
    assert all(replay["operation"]["readonly"] is True for replay in result["replays"])
    assert ledger.read_text(encoding="utf-8") == before


def test_latest_replay_returns_most_recent_ledger_operation(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    _record(runtime_root, "RUNTIME-INSPECTION-000002", "2026-05-27T00:00:02Z")

    result = latest_runtime_replay(runtime_root=runtime_root)

    assert result["status"] == "persisted"
    assert result["replay_reference"] == "RUNTIME-INSPECTION-000002"
    assert result["operation"]["operation_type"] == "inspect-runtime"
    assert result["operation"]["provider"] == "metadata_inspection_provider"
    assert result["verification_available"] is True


def test_valid_legacy_governed_returns_are_not_operational_listing_entries(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    entry = json.loads(ledger_path.read_text(encoding="utf-8").splitlines()[0])
    entry["replay_identity"] = "LEGACY-RETURN-001"
    entry["diagnostic_evidence"].pop("runtime_operation")
    with ledger_path.open("a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    result = list_runtime_replays(runtime_root=runtime_root)

    assert result["count"] == 1
    assert result["replays"][0]["replay_reference"] == "RUNTIME-INSPECTION-000001"


def test_malformed_ledger_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    ledger = runtime_root / "ledger" / "governed_returns.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("not-json\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert latest_runtime_replay(runtime_root=runtime_root)["status"] == "failed_closed"


def test_invalid_operational_replay_structure_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    entry = json.loads(ledger_path.read_text(encoding="utf-8"))
    entry["schema_version"] = "2.0"
    ledger_path.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["status"] == "failed_closed"


def test_missing_replay_identity_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    entry = json.loads(ledger_path.read_text(encoding="utf-8"))
    entry["replay_identity"] = ""
    ledger_path.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["status"] == "failed_closed"


def test_corrupted_selected_replay_evidence_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
    stdout_path = runtime_root / "evidence" / "RUNTIME-INSPECTION-000001" / "provider_stdout.txt"
    stdout_path.write_text("corrupted evidence", encoding="utf-8")

    assert list_runtime_replays(runtime_root=runtime_root)["status"] == "failed_closed"
    assert latest_runtime_replay(runtime_root=runtime_root)["status"] == "failed_closed"


def test_empty_ledger_is_empty_without_creating_state(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"

    listed = list_runtime_replays(runtime_root=runtime_root)
    latest = latest_runtime_replay(runtime_root=runtime_root)

    assert listed == {"replays": [], "count": 0, "status": "empty", "fail_closed": False}
    assert latest["status"] == "empty"
    assert not runtime_root.exists()


def test_history_rendering_and_cli_output_are_deterministic(tmp_path, capsys) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    for root in (first_root, second_root):
        _record(root, "RUNTIME-INSPECTION-000001", "2026-05-27T00:00:01Z")
        _record(root, "RUNTIME-INSPECTION-000002", "2026-05-27T00:00:02Z")

    first_list = render_replay_listing(list_runtime_replays(runtime_root=first_root))
    second_list = render_replay_listing(list_runtime_replays(runtime_root=second_root))
    first_latest = render_latest_replay(latest_runtime_replay(runtime_root=first_root))
    second_latest = render_latest_replay(latest_runtime_replay(runtime_root=second_root))

    assert first_list == second_list
    assert first_latest == second_latest
    assert "replay_reference: RUNTIME-INSPECTION-000002" in first_list
    assert main(["--runtime-root", str(first_root), "list-replays"]) == 0
    assert "[REPLAYS]" in capsys.readouterr().out
    assert main(["--runtime-root", str(first_root), "latest-replay"]) == 0
    assert "[LATEST]" in capsys.readouterr().out
