from __future__ import annotations

from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.replay import verify_replay
from aigol.cli.commands.run_governed import run_governed_operation_command, summarize_governed_operation_replay


def _run_operator_operation(tmp_path: Path) -> tuple[dict, Path]:
    workspace = tmp_path / "workspace"
    runtime_root = tmp_path / "runtime"
    workspace.mkdir()
    result = run_governed_operation_command(
        worker="filesystem",
        operation="create-file",
        target="operator-verify.txt",
        content="REPLAY_VERIFY_OPERATOR_RUNTIME_COMPATIBILITY_V1",
        operation_id="AIGOL-RUN-GOVERNED-VERIFY-000001",
        runtime_root=runtime_root,
        workspace=workspace,
    )
    return result, runtime_root


def test_run_governed_operation_replay_operation_and_replay_verify_agree(tmp_path):
    result, runtime_root = _run_operator_operation(tmp_path)

    operation = summarize_governed_operation_replay(
        operation_id=result["operation_id"],
        runtime_root=runtime_root,
    )
    verification = verify_replay(
        replay_identity=result["operation_id"],
        runtime_root=runtime_root,
    )

    assert result["status"] == "SUCCEEDED"
    assert operation["status"] == "SUCCEEDED"
    assert verification["status"] == "VERIFY_PASSED"
    assert verification["replay_format"] == "operator_runtime"
    assert verification["ledger_entry_exists"] is True
    assert verification["evidence_files_exist"] is True
    assert verification["lineage_continuity_exists"] is True
    assert verification["proposal_id"] == operation["proposal_id"]
    assert verification["authorization_id"] == operation["authorization_id"]
    assert verification["replay_summary"]["event_count"] == operation["replay_summary"]["event_count"]


def test_cli_replay_verify_supports_operator_runtime_replay(tmp_path):
    result, runtime_root = _run_operator_operation(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "replay",
            "verify",
            "--replay-identity",
            result["operation_id"],
            "--runtime-root",
            str(runtime_root),
        ]
    )

    verification = run_command(args)
    rendered = render_command_result(verification)

    assert verification["status"] == "VERIFY_PASSED"
    assert "AIGOL REPLAY VERIFY" in rendered
    assert "VERIFY_PASSED" in rendered


def test_replay_verify_missing_operator_replay_fails_closed(tmp_path):
    verification = verify_replay(
        replay_identity="AIGOL-RUN-GOVERNED-MISSING",
        runtime_root=tmp_path / "runtime",
    )

    assert verification["status"] == "VERIFY_FAILED"
    assert verification["fail_closed"] is True
    assert verification["ledger_entry_exists"] is False


def test_replay_verify_missing_operator_evidence_fails_closed(tmp_path):
    result, runtime_root = _run_operator_operation(tmp_path)
    missing = runtime_root / result["operation_id"] / "worker" / "001_filesystem_worker_execution.json"
    missing.unlink()

    verification = verify_replay(
        replay_identity=result["operation_id"],
        runtime_root=runtime_root,
    )

    assert verification["status"] == "VERIFY_FAILED"
    assert verification["fail_closed"] is True
    assert verification["evidence_files_exist"] is False
    assert "worker/001_filesystem_worker_execution.json" in verification["missing_evidence"]


def test_replay_verify_broken_operator_structure_fails_closed(tmp_path):
    result, runtime_root = _run_operator_operation(tmp_path)
    broken = runtime_root / result["operation_id"] / "worker" / "000_authorized_worker_request.json"
    broken.write_text("{}", encoding="utf-8")

    verification = verify_replay(
        replay_identity=result["operation_id"],
        runtime_root=runtime_root,
    )

    assert verification["status"] == "VERIFY_FAILED"
    assert verification["fail_closed"] is True
    assert verification["lineage_continuity_exists"] is False
