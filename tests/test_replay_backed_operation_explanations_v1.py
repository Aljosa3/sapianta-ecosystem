from __future__ import annotations

from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.replay import explain_operator_operation
from aigol.cli.commands.run_governed import run_governed_operation_command


def _run_operation(tmp_path: Path) -> tuple[dict, Path]:
    workspace = tmp_path / "workspace"
    runtime_root = tmp_path / "runtime"
    workspace.mkdir()
    result = run_governed_operation_command(
        worker="filesystem",
        operation="create-file",
        target="explain.txt",
        content="REPLAY_BACKED_OPERATION_EXPLANATIONS_V1",
        operation_id="AIGOL-RUN-GOVERNED-EXPLAIN-000001",
        runtime_root=runtime_root,
        workspace=workspace,
    )
    return result, runtime_root


def test_replay_backed_explanation_for_successful_operation(tmp_path):
    result, runtime_root = _run_operation(tmp_path)

    explanation = explain_operator_operation(
        operation_id=result["operation_id"],
        runtime_root=runtime_root,
    )

    assert result["status"] == "SUCCEEDED"
    assert explanation["status"] == "EXPLANATION_READY"
    assert explanation["explanation_type"] == "SUCCESSFUL_OPERATION"
    assert explanation["replay_backed"] is True
    assert explanation["fail_closed"] is False
    assert result["proposal_id"] in explanation["why_it_happened"]
    assert result["authorization_id"] in explanation["why_authorized"]
    assert "FILESYSTEM_CREATE_WORKER" in explanation["what_happened"]
    assert "VERIFY_PASSED" in explanation["trust_explanation"]
    assert explanation["evidence"]["replay_verify_status"] == "VERIFY_PASSED"
    assert explanation["evidence"]["replay_summary"]["event_count"] == 6


def test_cli_replay_explain_renders_human_readable_answer(tmp_path):
    result, runtime_root = _run_operation(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "replay",
            "explain",
            "--operation-id",
            result["operation_id"],
            "--runtime-root",
            str(runtime_root),
        ]
    )

    explanation = run_command(args)
    rendered = render_command_result(explanation)

    assert explanation["status"] == "EXPLANATION_READY"
    assert "AIGOL REPLAY EXPLAIN" in rendered
    assert "what_happened:" in rendered
    assert "why_authorized:" in rendered
    assert "trust_explanation:" in rendered


def test_explanation_missing_replay_fails_closed(tmp_path):
    explanation = explain_operator_operation(
        operation_id="AIGOL-RUN-GOVERNED-MISSING",
        runtime_root=tmp_path / "runtime",
    )

    assert explanation["status"] == "EXPLANATION_UNAVAILABLE"
    assert explanation["fail_closed"] is True
    assert explanation["replay_backed"] is False
    assert "operator operation replay is missing" in explanation["failure_reason"]


def test_explanation_broken_replay_fails_closed(tmp_path):
    result, runtime_root = _run_operation(tmp_path)
    broken = runtime_root / result["operation_id"] / "worker" / "001_filesystem_worker_execution.json"
    broken.unlink()

    explanation = explain_operator_operation(
        operation_id=result["operation_id"],
        runtime_root=runtime_root,
    )

    assert explanation["status"] == "EXPLANATION_UNAVAILABLE"
    assert explanation["fail_closed"] is True
    assert explanation["replay_backed"] is False
    assert "worker/001_filesystem_worker_execution.json" in explanation["evidence"]["missing_evidence"]


def test_explanation_hash_changes_when_evidence_changes(tmp_path):
    result, runtime_root = _run_operation(tmp_path)
    explanation = explain_operator_operation(
        operation_id=result["operation_id"],
        runtime_root=runtime_root,
    )
    changed = dict(explanation)
    original_hash = changed.pop("explanation_hash")
    changed["what_happened"] = "tampered"

    from aigol.runtime.transport.serialization import replay_hash

    assert original_hash != replay_hash(changed)
