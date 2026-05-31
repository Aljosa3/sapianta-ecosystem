from __future__ import annotations

from copy import deepcopy
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.run_governed import generate_default_operation_id, run_governed_operation_command
from aigol.runtime.transport.serialization import replay_hash


ROOT = Path(__file__).resolve().parents[1]


def _run(tmp_path, **overrides):
    args = {
        "worker": "filesystem",
        "operation": "create-file",
        "target": "test.txt",
        "content": "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
        "operation_id": "AIGOL-OPERATOR-EXTENSION-000001",
        "created_at": "2026-05-31T12:00:00Z",
        "runtime_root": tmp_path / "runtime",
        "workspace": tmp_path / "workspace",
    }
    args.update(overrides)
    args["workspace"].mkdir(exist_ok=True)
    return run_governed_operation_command(**args)


def test_run_governed_filesystem_operation_succeeds(tmp_path):
    result = _run(tmp_path)

    assert result["command"] == "aigol run-governed"
    assert result["status"] == "SUCCEEDED"
    assert result["execution_status"] == "SUCCEEDED"
    assert result["proposal_id"] == "AIGOL-OPERATOR-EXTENSION-000001:PROPOSAL"
    assert result["authorization_id"] == "AIGOL-OPERATOR-EXTENSION-000001:AUTHORIZATION"
    assert result["worker_result"]["created"] is True
    assert result["replay_id"] == "AIGOL-OPERATOR-EXTENSION-000001"
    assert result["fail_closed"] is False
    assert (tmp_path / "workspace" / "test.txt").read_text(encoding="utf-8") == "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1"


def test_run_governed_parser_and_renderer(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    parser = build_parser()
    args = parser.parse_args(
        [
            "run-governed",
            "--worker",
            "filesystem",
            "--operation",
            "create-file",
            "--target",
            "test.txt",
            "--content",
            "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
            "--operation-id",
            "AIGOL-OPERATOR-EXTENSION-000001",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(workspace),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["status"] == "SUCCEEDED"
    assert "AIGOL RUN GOVERNED" in rendered
    assert "operator_status: READY" in rendered
    assert "proposal_id: AIGOL-OPERATOR-EXTENSION-000001:PROPOSAL" in rendered
    assert "authorization_id: AIGOL-OPERATOR-EXTENSION-000001:AUTHORIZATION" in rendered
    assert "execution_status: SUCCEEDED" in rendered
    assert "replay_summary:" in rendered


def test_run_governed_generates_default_operation_id(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = run_governed_operation_command(
        worker="filesystem",
        operation="create-file",
        target="default-id.txt",
        content="AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
    )

    expected = generate_default_operation_id(
        worker="filesystem",
        operation="create-file",
        target="default-id.txt",
        content="AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
    )

    assert result["status"] == "SUCCEEDED"
    assert result["operation_id"] == expected
    assert result["proposal_id"] == f"{expected}:PROPOSAL"
    assert result["replay_summary"]["event_count"] == 6


def test_default_operation_id_advances_when_replay_exists(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    args = {
        "worker": "filesystem",
        "operation": "create-file",
        "target": "default-id.txt",
        "content": "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
        "runtime_root": tmp_path / "runtime",
        "workspace": workspace,
    }

    first = run_governed_operation_command(**args)
    second = run_governed_operation_command(**args)

    assert first["status"] == "SUCCEEDED"
    assert second["status"] == "FAILED_CLOSED"
    assert second["operation_id"].endswith("-0002")
    assert "filesystem worker target already exists" in second["failure_reason"]


def test_replay_operation_summary_by_operation_id(tmp_path):
    result = _run(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "replay",
            "operation",
            "--operation-id",
            result["operation_id"],
            "--runtime-root",
            str(tmp_path / "runtime"),
        ]
    )

    summary = run_command(args)
    rendered = render_command_result(summary)

    assert summary["command"] == "aigol replay operation"
    assert summary["status"] == "SUCCEEDED"
    assert summary["execution_status"] == "SUCCEEDED"
    assert summary["proposal_id"] == result["proposal_id"]
    assert summary["authorization_id"] == result["authorization_id"]
    assert summary["replay_summary"]["event_count"] == 6
    assert "AIGOL REPLAY OPERATION" in rendered
    assert f"operation_id: {result['operation_id']}" in rendered


def test_replay_operation_missing_id_fails_closed(tmp_path):
    parser = build_parser()
    args = parser.parse_args(
        [
            "replay",
            "operation",
            "--operation-id",
            "MISSING-OPERATION",
            "--runtime-root",
            str(tmp_path / "runtime"),
        ]
    )

    summary = run_command(args)

    assert summary["status"] == "FAILED_CLOSED"
    assert summary["fail_closed"] is True
    assert summary["execution_status"] == "FAILED_CLOSED"


def test_run_governed_cli_entrypoint(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "run-governed",
            "--worker",
            "filesystem",
            "--operation",
            "create-file",
            "--target",
            "test.txt",
            "--content",
            "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
            "--operation-id",
            "AIGOL-OPERATOR-EXTENSION-000001",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(workspace),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    assert "AIGOL RUN GOVERNED" in result.stdout
    assert "execution_status: SUCCEEDED" in result.stdout


def test_unknown_worker_fails_closed(tmp_path):
    result = _run(tmp_path, worker="unknown")

    assert result["status"] == "FAILED_CLOSED"
    assert result["execution_status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "unknown worker" in result["failure_reason"]


def test_invalid_proposal_fails_closed(tmp_path, monkeypatch):
    import aigol.cli.commands.run_governed as command

    def failed_provider_attachment(**_kwargs):
        return {
            "provider_proposal_envelope": {
                "event_type": "FAILED_CLOSED",
                "failure_reason": "invalid proposal",
            }
        }

    monkeypatch.setattr(command, "run_provider_attachment", failed_provider_attachment)
    result = _run(tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "invalid proposal" in result["failure_reason"]


def test_missing_authorization_fails_closed(tmp_path, monkeypatch):
    import aigol.cli.commands.run_governed as command

    def missing_authorization(**_kwargs):
        return {"authorization_record": {}}

    monkeypatch.setattr(command, "authorize_worker_request", missing_authorization)
    result = _run(tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "authorization record type is invalid" in result["failure_reason"]


def test_worker_scope_mismatch_fails_closed(tmp_path, monkeypatch):
    import aigol.cli.commands.run_governed as command

    monkeypatch.setattr(command, "AUTHORIZED_SCOPE", "READ_ONLY")
    result = _run(tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "authorization record scope mismatch" in result["failure_reason"]


def test_append_only_replay_violation_fails_closed(tmp_path):
    first = _run(tmp_path)
    second = _run(tmp_path)

    assert first["status"] == "SUCCEEDED"
    assert second["status"] == "FAILED_CLOSED"
    assert "append-only runtime artifact already exists" in second["failure_reason"]


def test_result_hash_changes_if_evidence_changes(tmp_path):
    result = _run(tmp_path)
    changed = deepcopy(result)
    original_hash = changed.pop("result_hash")
    changed["execution_status"] = "TAMPERED"

    assert original_hash == replay_hash({key: value for key, value in result.items() if key != "result_hash"})
    assert original_hash != replay_hash(changed)
