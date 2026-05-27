"""Tests for MINIMAL_RUNTIME_CONTINUITY_SUMMARY_V1."""

from __future__ import annotations

from aigol.runtime.operator.runtime_execution_cli import (
    main,
    render_runtime_continuity_summary,
    run_runtime_inspection,
    runtime_continuity_summary,
)


def _record(runtime_root, operation_id: str, timestamp: str) -> None:
    result = run_runtime_inspection(
        operation_id=operation_id,
        created_at=timestamp,
        runtime_root=runtime_root,
    )
    assert result["fail_closed"] is False


def test_successful_runtime_summary_reports_verified_continuity_and_is_readonly(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-001", "2026-05-27T00:00:01Z")
    _record(runtime_root, "RUNTIME-INSPECTION-002", "2026-05-27T00:00:02Z")
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger_path.read_text(encoding="utf-8")

    result = runtime_continuity_summary(runtime_root=runtime_root)

    assert result == {
        "governance": "active",
        "continuity": "valid",
        "replay_count": 2,
        "latest_replay": "RUNTIME-INSPECTION-002",
        "evidence_available": True,
        "verification_health": "healthy",
        "malformed_replay_count": 0,
        "verified": 2,
        "failed": 0,
        "missing_evidence": 0,
        "malformed": 0,
        "fail_closed": False,
    }
    assert ledger_path.read_text(encoding="utf-8") == before


def test_empty_runtime_summary_is_readonly(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"

    result = runtime_continuity_summary(runtime_root=runtime_root)

    assert result["governance"] == "inactive"
    assert result["continuity"] == "empty"
    assert result["replay_count"] == 0
    assert result["latest_replay"] == "none"
    assert result["verification_health"] == "empty"
    assert result["fail_closed"] is False
    assert not runtime_root.exists()


def test_malformed_ledger_reports_failed_closed_summary(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text("not-json\n", encoding="utf-8")

    result = runtime_continuity_summary(runtime_root=runtime_root)

    assert result["continuity"] == "invalid"
    assert result["verification_health"] == "failed"
    assert result["malformed_replay_count"] == 1
    assert result["failed"] == 1
    assert result["fail_closed"] is True


def test_corrupted_evidence_is_counted_and_reported(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-001", "2026-05-27T00:00:01Z")
    _record(runtime_root, "RUNTIME-INSPECTION-002", "2026-05-27T00:00:02Z")
    (runtime_root / "evidence" / "RUNTIME-INSPECTION-002" / "provider_stdout.txt").write_text("corrupted", encoding="utf-8")

    result = runtime_continuity_summary(runtime_root=runtime_root)

    assert result["replay_count"] == 2
    assert result["latest_replay"] == "RUNTIME-INSPECTION-002"
    assert result["verified"] == 1
    assert result["failed"] == 1
    assert result["malformed"] == 1
    assert result["governance"] == "blocked"
    assert result["fail_closed"] is True


def test_missing_evidence_is_reported_separately(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _record(runtime_root, "RUNTIME-INSPECTION-001", "2026-05-27T00:00:01Z")
    (runtime_root / "evidence" / "RUNTIME-INSPECTION-001" / "lineage.json").unlink()

    result = runtime_continuity_summary(runtime_root=runtime_root)

    assert result["failed"] == 1
    assert result["missing_evidence"] == 1
    assert result["malformed"] == 0
    assert result["fail_closed"] is True


def test_runtime_summary_rendering_is_deterministic(tmp_path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    for root in (first_root, second_root):
        _record(root, "RUNTIME-INSPECTION-001", "2026-05-27T00:00:01Z")
        _record(root, "RUNTIME-INSPECTION-002", "2026-05-27T00:00:02Z")

    first = render_runtime_continuity_summary(runtime_continuity_summary(runtime_root=first_root))
    second = render_runtime_continuity_summary(runtime_continuity_summary(runtime_root=second_root))

    assert first == second
    assert "[RUNTIME SUMMARY]\ngovernance: active\ncontinuity: valid" in first
    assert "verified: 2" in first


def test_cli_exposes_runtime_summary_and_returns_nonzero_on_failure(tmp_path, capsys) -> None:
    healthy_root = tmp_path / "healthy"
    _record(healthy_root, "RUNTIME-INSPECTION-001", "2026-05-27T00:00:01Z")

    assert main(["--runtime-root", str(healthy_root), "runtime-summary"]) == 0
    assert "verification_health: healthy" in capsys.readouterr().out

    failed_root = tmp_path / "failed"
    ledger_path = failed_root / "ledger" / "governed_returns.jsonl"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text("not-json\n", encoding="utf-8")

    assert main(["--runtime-root", str(failed_root), "runtime-summary"]) == 2
    assert "verification_health: failed" in capsys.readouterr().out
