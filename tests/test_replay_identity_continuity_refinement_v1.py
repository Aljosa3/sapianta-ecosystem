"""Tests for REPLAY_IDENTITY_CONTINUITY_REFINEMENT_V1."""

from __future__ import annotations

import json

from aigol.runtime.operator.runtime_execution_cli import (
    latest_runtime_replay,
    list_runtime_replays,
    run_runtime_inspection,
    runtime_continuity_summary,
    show_runtime_session,
)


def _references(runtime_root) -> list[str]:
    listed = list_runtime_replays(runtime_root=runtime_root)
    assert listed["fail_closed"] is False
    return [replay["replay_reference"] for replay in reversed(listed["replays"])]


def test_default_runtime_inspection_allocates_unique_monotonic_replay_identities(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"

    results = [run_runtime_inspection(runtime_root=runtime_root) for _ in range(3)]

    assert [result["operation"]["replay_reference"] for result in results] == [
        "RUNTIME-INSPECTION-000001",
        "RUNTIME-INSPECTION-000002",
        "RUNTIME-INSPECTION-000003",
    ]
    assert all(result["fail_closed"] is False for result in results)
    assert _references(runtime_root) == [
        "RUNTIME-INSPECTION-000001",
        "RUNTIME-INSPECTION-000002",
        "RUNTIME-INSPECTION-000003",
    ]


def test_replay_observability_reflects_monotonic_identity_continuity(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    for _ in range(3):
        assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False

    latest = latest_runtime_replay(runtime_root=runtime_root)
    summary = runtime_continuity_summary(runtime_root=runtime_root)
    session = show_runtime_session(
        replay_reference="RUNTIME-INSPECTION-000003",
        runtime_root=runtime_root,
    )

    assert latest["replay_reference"] == "RUNTIME-INSPECTION-000003"
    assert summary["latest_replay"] == "RUNTIME-INSPECTION-000003"
    assert summary["replay_count"] == 3
    assert summary["continuity"] == "valid"
    assert session["continuity"] == "valid"
    assert session["replay_reference"] == "RUNTIME-INSPECTION-000003"


def test_identity_allocation_is_deterministic_for_equal_runtime_histories(tmp_path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"

    first = [run_runtime_inspection(runtime_root=first_root)["operation"]["replay_reference"] for _ in range(3)]
    second = [run_runtime_inspection(runtime_root=second_root)["operation"]["replay_reference"] for _ in range(3)]

    assert first == second == [
        "RUNTIME-INSPECTION-000001",
        "RUNTIME-INSPECTION-000002",
        "RUNTIME-INSPECTION-000003",
    ]


def test_duplicate_operational_identity_fails_closed_and_prevents_append(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    first_entry = ledger_path.read_text(encoding="utf-8")
    ledger_path.write_text(first_entry + first_entry, encoding="utf-8")
    before = ledger_path.read_text(encoding="utf-8")

    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["fail_closed"] is True
    assert result["persistence"]["status"] == "NOT_PERSISTED"
    assert list_runtime_replays(runtime_root=runtime_root)["fail_closed"] is True
    assert runtime_continuity_summary(runtime_root=runtime_root)["fail_closed"] is True
    assert ledger_path.read_text(encoding="utf-8") == before


def test_malformed_or_non_monotonic_operational_identity_fails_closed(tmp_path) -> None:
    malformed_root = tmp_path / "malformed"
    assert run_runtime_inspection(runtime_root=malformed_root)["fail_closed"] is False
    malformed_ledger = malformed_root / "ledger" / "governed_returns.jsonl"
    entry = json.loads(malformed_ledger.read_text(encoding="utf-8"))
    entry["replay_identity"] = "RUNTIME-INSPECTION-NOT-A-SEQUENCE"
    malformed_ledger.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert list_runtime_replays(runtime_root=malformed_root)["fail_closed"] is True


def test_existing_evidence_identity_collision_fails_closed_without_persistence(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    collision = runtime_root / "evidence" / "RUNTIME-INSPECTION-000001"
    collision.mkdir(parents=True)
    (collision / "governed_return.json").write_text("{}\n", encoding="utf-8")

    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["fail_closed"] is True
    assert result["persistence"]["status"] == "NOT_PERSISTED"
    assert (runtime_root / "ledger" / "governed_returns.jsonl").exists() is False


def test_invalid_existing_operational_metadata_prevents_successor_persistence(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    assert run_runtime_inspection(runtime_root=runtime_root)["fail_closed"] is False
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    evidence_path = runtime_root / "evidence" / "RUNTIME-INSPECTION-000001" / "governed_return.json"
    artifact = json.loads(evidence_path.read_text(encoding="utf-8"))
    artifact["diagnostic_evidence"]["runtime_operation"]["provider"] = "invalid_provider"
    evidence_path.write_text(json.dumps(artifact, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    before = ledger_path.read_text(encoding="utf-8")

    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["fail_closed"] is True
    assert result["persistence"]["status"] == "NOT_PERSISTED"
    assert ledger_path.read_text(encoding="utf-8") == before
