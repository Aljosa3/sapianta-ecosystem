"""Tests for MINIMAL_RUNTIME_SESSION_VIEW_V1."""

from __future__ import annotations

import json

from aigol.runtime.operator.runtime_execution_cli import (
    main,
    render_runtime_session,
    run_runtime_inspection,
    show_runtime_session,
)


REPLAY_REFERENCE = "RUNTIME-INSPECTION-000001"


def _persist(tmp_path):
    runtime_root = tmp_path / "runtime"
    result = run_runtime_inspection(runtime_root=runtime_root)
    assert result["fail_closed"] is False
    return runtime_root


def test_successful_runtime_session_inspection_is_readonly(tmp_path) -> None:
    runtime_root = _persist(tmp_path)
    ledger_path = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger_path.read_text(encoding="utf-8")

    result = show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)

    assert result["status"] == "persisted"
    assert result["schema_version"] == "1.0"
    assert result["operation"]["operation_type"] == "inspect-runtime"
    assert result["operation"]["provider"] == "metadata_inspection_provider"
    assert result["operation"]["readonly"] is True
    assert result["continuity"] == "valid"
    assert result["verification"] == "verify_passed"
    assert result["governance"] == "active"
    assert result["governed_return_present"] is True
    assert result["evidence_present"] is True
    assert result["evidence_reference"] == REPLAY_REFERENCE
    assert ledger_path.read_text(encoding="utf-8") == before


def test_runtime_session_output_is_deterministic(tmp_path) -> None:
    first_root = _persist(tmp_path / "first")
    second_root = _persist(tmp_path / "second")

    first = render_runtime_session(show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=first_root))
    second = render_runtime_session(show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=second_root))

    assert first == second
    assert "[SESSION]\nreplay_reference: RUNTIME-INSPECTION-000001\nstatus: persisted" in first
    assert "verification: verify_passed" in first


def test_missing_replay_fails_closed(tmp_path) -> None:
    result = show_runtime_session(replay_reference="MISSING", runtime_root=tmp_path / "runtime")

    assert result["status"] == "failed_closed"
    assert result["governance"] == "blocked"
    assert result["fail_closed"] is True


def test_malformed_ledger_fails_closed(tmp_path) -> None:
    runtime_root = _persist(tmp_path)
    (runtime_root / "ledger" / "governed_returns.jsonl").write_text("not-json\n", encoding="utf-8")

    assert show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True


def test_corrupted_evidence_fails_closed(tmp_path) -> None:
    runtime_root = _persist(tmp_path)
    (runtime_root / "evidence" / REPLAY_REFERENCE / "provider_stdout.txt").write_text("corrupted", encoding="utf-8")

    assert show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True


def test_invalid_lineage_fails_closed(tmp_path) -> None:
    runtime_root = _persist(tmp_path)
    lineage_path = runtime_root / "evidence" / REPLAY_REFERENCE / "lineage.json"
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    lineage["governed_return_hash"] = "sha256:" + "0" * 64
    lineage_path.write_text(json.dumps(lineage, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True


def test_invalid_schema_or_provider_boundary_fails_closed(tmp_path) -> None:
    schema_root = _persist(tmp_path / "schema")
    schema_path = schema_root / "evidence" / REPLAY_REFERENCE / "governed_return.json"
    artifact = json.loads(schema_path.read_text(encoding="utf-8"))
    artifact["schema_version"] = "2.0"
    schema_path.write_text(json.dumps(artifact, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    provider_root = _persist(tmp_path / "provider")
    provider_path = provider_root / "evidence" / REPLAY_REFERENCE / "governed_return.json"
    artifact = json.loads(provider_path.read_text(encoding="utf-8"))
    artifact["diagnostic_evidence"]["runtime_operation"]["provider"] = "invalid_provider"
    provider_path.write_text(json.dumps(artifact, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=schema_root)["fail_closed"] is True
    assert show_runtime_session(replay_reference=REPLAY_REFERENCE, runtime_root=provider_root)["fail_closed"] is True


def test_cli_exposes_show_runtime_session(tmp_path, capsys) -> None:
    runtime_root = _persist(tmp_path)

    assert main(["--runtime-root", str(runtime_root), "show-runtime-session", REPLAY_REFERENCE]) == 0
    output = capsys.readouterr().out
    assert "[SESSION]" in output
    assert "[LINEAGE]" in output
    assert "governance: active" in output
