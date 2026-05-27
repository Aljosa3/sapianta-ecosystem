"""Tests for MINIMAL_REPLAY_INSPECTION_V1."""

from __future__ import annotations

import json

from aigol.runtime.operator.runtime_execution_cli import (
    main,
    render_replay_inspection,
    render_replay_verification,
    run_replay_inspection,
    run_replay_verification,
    run_runtime_inspection,
)


REPLAY_REFERENCE = "RUNTIME-INSPECTION-001"


def _persist_runtime_inspection(tmp_path):
    runtime_root = tmp_path / "runtime"
    execution = run_runtime_inspection(runtime_root=runtime_root)
    assert execution["fail_closed"] is False
    return runtime_root


def test_successful_replay_inspection_is_readonly_and_uses_persisted_operation(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)
    ledger = runtime_root / "ledger" / "governed_returns.jsonl"
    before = ledger.read_text(encoding="utf-8")

    result = run_replay_inspection(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)

    assert result["status"] == "persisted"
    assert result["schema_version"] == "1.0"
    assert result["operation"]["operation_type"] == "inspect-runtime"
    assert result["operation"]["provider"] == "metadata_inspection_provider"
    assert result["operation"]["readonly"] is True
    assert result["evidence_present"] is True
    assert result["fail_closed"] is False
    assert ledger.read_text(encoding="utf-8") == before


def test_successful_replay_verification_delegates_to_existing_integrity_contract(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)

    result = run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)

    assert result == {
        "replay_reference": REPLAY_REFERENCE,
        "schema_version": "1.0",
        "verification": "verify_passed",
        "continuity": "valid",
        "evidence": "present",
        "governed_return_present": True,
        "fail_closed": False,
    }


def test_missing_replay_fails_closed(tmp_path) -> None:
    inspection = run_replay_inspection(replay_reference="MISSING", runtime_root=tmp_path / "runtime")
    verification = run_replay_verification(replay_reference="MISSING", runtime_root=tmp_path / "runtime")

    assert inspection["status"] == "failed_closed"
    assert inspection["fail_closed"] is True
    assert verification["verification"] == "verify_failed"
    assert verification["fail_closed"] is True


def test_malformed_ledger_fails_closed(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)
    (runtime_root / "ledger" / "governed_returns.jsonl").write_text("not-json\n", encoding="utf-8")

    result = run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)

    assert result["verification"] == "verify_failed"
    assert result["continuity"] == "invalid"
    assert result["fail_closed"] is True


def test_corrupted_evidence_fails_closed(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)
    stdout_path = runtime_root / "evidence" / REPLAY_REFERENCE / "provider_stdout.txt"
    stdout_path.write_text("corrupted provider evidence", encoding="utf-8")

    inspection = run_replay_inspection(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)
    verification = run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)

    assert inspection["status"] == "failed_closed"
    assert verification["verification"] == "verify_failed"


def test_schema_mismatch_fails_closed(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)
    artifact_path = runtime_root / "evidence" / REPLAY_REFERENCE / "governed_return.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["schema_version"] = "2.0"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert run_replay_inspection(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True
    assert run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True


def test_invalid_replay_lineage_fails_closed(tmp_path) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)
    lineage_path = runtime_root / "evidence" / REPLAY_REFERENCE / "lineage.json"
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    lineage["governed_return_hash"] = "sha256:" + "0" * 64
    lineage_path.write_text(json.dumps(lineage, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    assert run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=runtime_root)["fail_closed"] is True


def test_operator_replay_output_is_deterministic(tmp_path) -> None:
    first_root = _persist_runtime_inspection(tmp_path / "first")
    second_root = _persist_runtime_inspection(tmp_path / "second")

    first_inspect = render_replay_inspection(run_replay_inspection(replay_reference=REPLAY_REFERENCE, runtime_root=first_root))
    second_inspect = render_replay_inspection(run_replay_inspection(replay_reference=REPLAY_REFERENCE, runtime_root=second_root))
    first_verify = render_replay_verification(run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=first_root))
    second_verify = render_replay_verification(run_replay_verification(replay_reference=REPLAY_REFERENCE, runtime_root=second_root))

    assert first_inspect == second_inspect
    assert first_verify == second_verify
    assert "status: persisted" in first_inspect
    assert "verification: verify_passed" in first_verify


def test_cli_exposes_readonly_replay_commands(tmp_path, capsys) -> None:
    runtime_root = _persist_runtime_inspection(tmp_path)

    assert main(["--runtime-root", str(runtime_root), "inspect-replay", REPLAY_REFERENCE]) == 0
    assert "governed_return_present: true" in capsys.readouterr().out
    assert main(["--runtime-root", str(runtime_root), "verify-replay", REPLAY_REFERENCE]) == 0
    assert "continuity: valid" in capsys.readouterr().out
