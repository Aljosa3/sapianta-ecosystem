from __future__ import annotations

from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.replay import operator_operation_report
from aigol.cli.commands.run_governed import run_governed_operation_command


def _run_operation(tmp_path: Path, *, name: str, content: str) -> tuple[dict, Path]:
    workspace = tmp_path / "workspace"
    runtime_root = tmp_path / "runtime"
    workspace.mkdir(exist_ok=True)
    result = run_governed_operation_command(
        worker="filesystem",
        operation="create-file",
        target=f"{name}.txt",
        content=content,
        runtime_root=runtime_root,
        workspace=workspace,
    )
    return result, runtime_root


def test_operator_operation_report_lists_operations_and_statistics(tmp_path):
    first, runtime_root = _run_operation(tmp_path, name="one", content="ONE")
    second, _runtime_root = _run_operation(tmp_path, name="two", content="TWO")

    report = operator_operation_report(runtime_root=runtime_root)

    assert first["status"] == "SUCCEEDED"
    assert second["status"] == "SUCCEEDED"
    assert report["command"] == "aigol replay report"
    assert report["status"] == "REPORT_READY"
    assert report["operation_count"] == 2
    assert report["statistics"]["total_operations"] == 2
    assert report["statistics"]["successful_operations"] == 2
    assert report["statistics"]["fail_closed_operations"] == 0
    assert report["statistics"]["verification_failures"] == 0
    assert report["statistics"]["success_rate"] == "100.00%"
    assert report["statistics"]["worker_usage"] == {"FILESYSTEM_CREATE_WORKER": 2}
    assert report["statistics"]["operation_type_usage"] == {"CREATE_FILE": 2}
    assert {entry["operation_id"] for entry in report["entries"]} == {first["operation_id"], second["operation_id"]}


def test_cli_replay_report_renders_weekly_summary(tmp_path):
    _first, runtime_root = _run_operation(tmp_path, name="one", content="ONE")
    parser = build_parser()
    args = parser.parse_args(["replay", "report", "--runtime-root", str(runtime_root)])

    report = run_command(args)
    rendered = render_command_result(report)

    assert report["status"] == "REPORT_READY"
    assert "AIGOL REPLAY REPORT" in rendered
    assert "successful_operations: 1" in rendered
    assert "weekly_usage_summary:" in rendered


def test_operator_operation_report_marks_broken_replay_verification_failure(tmp_path):
    result, runtime_root = _run_operation(tmp_path, name="one", content="ONE")
    broken = runtime_root / result["operation_id"] / "worker" / "001_filesystem_worker_execution.json"
    broken.unlink()

    report = operator_operation_report(runtime_root=runtime_root)

    assert report["status"] == "REPORT_READY"
    assert report["operation_count"] == 1
    assert report["statistics"]["successful_operations"] == 0
    assert report["statistics"]["fail_closed_operations"] == 1
    assert report["statistics"]["verification_failures"] == 1
    assert report["entries"][0]["replay_status"] == "VERIFY_FAILED"
    assert "worker/001_filesystem_worker_execution.json" in report["entries"][0]["missing_evidence"]


def test_operator_operation_report_missing_root_fails_closed(tmp_path):
    report = operator_operation_report(runtime_root=tmp_path / "missing")

    assert report["status"] == "REPORT_FAILED"
    assert report["fail_closed"] is True
    assert report["operation_count"] == 0
    assert "operator runtime root is missing" in report["failure_reason"]


def test_operator_operation_report_empty_root_fails_closed(tmp_path):
    root = tmp_path / "runtime"
    root.mkdir()

    report = operator_operation_report(runtime_root=root)

    assert report["status"] == "REPORT_FAILED"
    assert report["fail_closed"] is True
    assert "operator runtime contains no operation records" in report["failure_reason"]
