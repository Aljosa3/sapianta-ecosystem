import json
from pathlib import Path

from aigol.cli.aigol_cli import render_command_result
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cli.commands.replay import ledger_summary, verify_replay
from aigol.cli.commands.return_continuity import (
    generate_governed_return_artifact,
    inspect_governed_return,
    persist_governed_return_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "aigol" / "cli"


def _artifact():
    return generate_ingress_artifact(
        human_request="Persist governed return continuity.",
        semantic_intent="Governed return continuity hardening",
    )


def _native_response(status="COMPLETED", returncode=0):
    return {
        "status": "NATIVE_BRIDGE_ACCEPTED",
        "result_artifact": {
            "artifact_hash": "sha256:" + "3" * 64,
            "codex_cli_result": {
                "bounded_execution_status": status,
                "provider_invoked": True,
                "summary": "return continuity",
                "provider_result": {
                    "status": status,
                    "stdout": "stdout evidence",
                    "stderr": "stderr evidence",
                    "returncode": returncode,
                    "diagnostic_evidence": {
                        "provider_invoked": True,
                        "subprocess_invoked": True,
                        "subprocess_returncode": returncode,
                        "codex_executable_found": True,
                        "provider_command": ["codex", "--version"],
                        "failing_layer": "" if status == "COMPLETED" else "bounded_codex_cli_subprocess",
                    },
                },
            },
        },
        "governed_return": {"status": "ACCEPTED" if status == "COMPLETED" else "FAILED"},
    }


def _success_handler(message):
    return _native_response()


def _failure_handler(message):
    return _native_response(status="FAILED", returncode=1)


def test_governed_return_artifact_generated_on_execution_completed(tmp_path):
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=tmp_path / "rt")

    artifact = result["governed_return_artifact"]
    assert artifact["artifact_type"] == "GOVERNED_RETURN_ARTIFACT_V1"
    assert artifact["execution_status"] == "EXECUTION_COMPLETED"


def test_governed_return_artifact_generated_on_execution_failed(tmp_path):
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_failure_handler, runtime_root=tmp_path / "rt")

    assert result["governed_return_artifact"]["execution_status"] == "EXECUTION_FAILED"
    assert result["governed_return_artifact"]["fail_closed"] is True


def test_governed_return_artifact_generated_on_execution_blocked(tmp_path):
    result = run_execution_handoff(ingress_artifact={}, workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=tmp_path / "rt")

    assert result["governed_return_artifact"]["execution_status"] == "EXECUTION_BLOCKED"
    assert result["governed_return_artifact"]["fail_closed"] is True


def test_governed_return_hash_deterministic(tmp_path):
    first = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, persist_return=False)
    second = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, persist_return=False)

    assert first["governed_return_artifact"]["governed_return_hash"] == second["governed_return_artifact"]["governed_return_hash"]


def test_ledger_append_only_behavior(tmp_path):
    runtime_root = tmp_path / "rt"
    first = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    second = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    ledger = runtime_root / "ledger" / "governed_returns.jsonl"

    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["governed_return_hash"] == first["governed_return_hash"]
    assert json.loads(lines[1])["governed_return_hash"] == second["governed_return_hash"]


def test_ledger_entry_contains_replay_identity(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    entries = ledger_summary(runtime_root=runtime_root)["entries"]

    assert entries[-1]["replay_identity"] == result["replay_identity"]


def test_evidence_directory_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    assert (runtime_root / "evidence" / result["replay_identity"]).is_dir()


def test_governed_return_json_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    assert (runtime_root / "evidence" / result["replay_identity"] / "governed_return.json").is_file()


def test_provider_stdout_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    assert (runtime_root / "evidence" / result["replay_identity"] / "provider_stdout.txt").read_text(encoding="utf-8") == "stdout evidence"


def test_provider_stderr_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    assert (runtime_root / "evidence" / result["replay_identity"] / "provider_stderr.txt").read_text(encoding="utf-8") == "stderr evidence"


def test_diagnostic_evidence_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    assert (runtime_root / "evidence" / result["replay_identity"] / "diagnostic_evidence.json").is_file()


def test_lineage_created(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    lineage = json.loads((runtime_root / "evidence" / result["replay_identity"] / "lineage.json").read_text(encoding="utf-8"))

    assert lineage["dispatch_authorization_hash"].startswith("sha256:")
    assert lineage["governed_return_hash"] == result["governed_return_hash"]


def test_replay_verify_passes_for_valid_artifact(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)

    verification = verify_replay(replay_identity=result["replay_identity"], runtime_root=runtime_root)
    assert verification["status"] == "VERIFY_PASSED"
    assert verification["fail_closed"] is False


def test_replay_verify_fails_closed_on_missing_evidence(tmp_path):
    verification = verify_replay(replay_identity="MISSING", runtime_root=tmp_path / "rt")

    assert verification["status"] == "VERIFY_FAILED"
    assert verification["fail_closed"] is True


def test_invalid_execution_status_rejected():
    artifact = generate_governed_return_artifact(
        execution_artifact={"execution_status": "BROKEN", "replay_identity": "RID"},
        cli_governed_return={"governed_return_hash": "sha256:" + "1" * 64},
    )

    assert artifact["status"] == "PERSISTENCE_REJECTED"
    assert artifact["rejection_reason"] == "invalid execution status"


def test_missing_replay_identity_rejected():
    artifact = generate_governed_return_artifact(
        execution_artifact={"execution_status": "EXECUTION_COMPLETED", "replay_identity": ""},
        cli_governed_return={"governed_return_hash": "sha256:" + "1" * 64},
    )

    assert artifact["status"] == "PERSISTENCE_REJECTED"
    assert artifact["rejection_reason"] == "missing replay identity"


def test_cli_return_inspect_renders_deterministic_output(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    rendered = render_command_result(inspect_governed_return(replay_identity=result["replay_identity"], runtime_root=runtime_root))

    assert "AIGOL RETURN INSPECT" in rendered
    assert result["governed_return_hash"] in rendered


def test_cli_replay_ledger_renders_deterministic_output(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    rendered = render_command_result(ledger_summary(runtime_root=runtime_root))

    assert "AIGOL REPLAY LEDGER" in rendered
    assert result["replay_identity"] in rendered


def test_cli_replay_verify_renders_deterministic_output(tmp_path):
    runtime_root = tmp_path / "rt"
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), native_message_handler=_success_handler, runtime_root=runtime_root)
    rendered = render_command_result(verify_replay(replay_identity=result["replay_identity"], runtime_root=runtime_root))

    assert "AIGOL REPLAY VERIFY" in rendered
    assert "VERIFY_PASSED" in rendered


def test_no_orchestration_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "orchestrator" not in source
    assert "orchestrationruntime" not in source
    assert "asyncio" not in source


def test_no_retries_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "for attempt" not in source
    assert "retry_count\": 1" not in source


def test_no_autonomous_continuation_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "autonomous_continuation\": true" not in source
    assert "background" not in source


def test_persistence_failure_is_structured(tmp_path):
    persistence = persist_governed_return_artifact(
        artifact={"artifact_type": "BROKEN"},
        provider_result={},
        runtime_root=tmp_path / "rt",
    )

    assert persistence["status"] == "PERSISTENCE_FAILED"
    assert persistence["fail_closed"] is True
