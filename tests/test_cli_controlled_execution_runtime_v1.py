from pathlib import Path

from aigol.cli.aigol_cli import render_command_result
from aigol.cli.commands.execution import create_governed_return_artifact, run_execution_handoff
from aigol.cli.commands.ingress import generate_ingress_artifact


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "aigol" / "cli"


def _artifact():
    return generate_ingress_artifact(
        human_request="Run CLI controlled execution runtime proof.",
        semantic_intent="Bounded CLI governed execution continuity",
    )


def _native_response(*, status="COMPLETED", returncode=0, stdout="ok", stderr="", provider_invoked=True):
    return {
        "status": "NATIVE_BRIDGE_ACCEPTED",
        "result_artifact": {
            "artifact_hash": "sha256:" + "2" * 64,
            "codex_cli_result": {
                "bounded_execution_status": status,
                "provider_invoked": provider_invoked,
                "summary": "CLI provider continuity",
                "provider_result": {
                    "status": status,
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": returncode,
                    "diagnostic_evidence": {
                        "provider_invoked": provider_invoked,
                        "subprocess_invoked": provider_invoked,
                        "subprocess_returncode": returncode,
                        "codex_executable_found": True,
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
    return _native_response(status="FAILED", returncode=1, stdout="", stderr="provider failed")


def test_cli_execution_handoff_callable(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["command"] == "aigol execution handoff"
    assert result["execution_status"] == "EXECUTION_COMPLETED"


def test_provider_continuity_reached(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["provider_invoked"] is True
    assert result["diagnostic_evidence"]["subprocess_invoked"] is True


def test_provider_invoked_true_on_valid_continuity(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["governed_return"]["provider_invoked"] is True


def test_governed_return_generated(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["governed_return"]["artifact_type"] == "CLI_GOVERNED_RETURN_CONTINUITY_V1"
    assert result["diagnostic_evidence"]["governed_return_generated"] is True


def test_governed_return_hash_generated(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["governed_return_hash"].startswith("sha256:")
    assert result["governed_return"]["governed_return_hash"] == result["governed_return_hash"]


def test_replay_continuity_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["replay_identity"] == result["governed_return"]["replay_identity"]
    assert result["execution_governance_hash"] == result["governed_return"]["execution_governance_hash"]


def test_execution_blocked_on_invalid_continuity(tmp_path):
    result = run_execution_handoff(
        ingress_artifact={},
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["execution_status"] == "EXECUTION_BLOCKED"
    assert result["provider_invoked"] is False
    assert result["fail_closed"] is True


def test_execution_failed_on_provider_failure(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_failure_handler,
    )

    assert result["execution_status"] == "EXECUTION_FAILED"
    assert result["provider_invoked"] is True
    assert result["provider_exit_code"] == 1
    assert result["fail_closed"] is True


def test_execution_completed_on_successful_provider_return(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["execution_status"] == "EXECUTION_COMPLETED"
    assert result["provider_exit_code"] == 0
    assert result["fail_closed"] is False


def test_continuity_verified_true_on_valid_path(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )

    assert result["continuity_verified"] is True
    assert result["governed_return"]["continuity_verified"] is True


def test_fail_closed_preserved():
    blocked = create_governed_return_artifact(
        execution_artifact={
            "execution_status": "EXECUTION_BLOCKED",
            "provider_invoked": False,
            "replay_identity": "UNKNOWN",
            "execution_governance_hash": "",
            "execution_result_summary": {"provider_status": "NOT_INVOKED"},
        }
    )

    assert blocked["fail_closed"] is True
    assert blocked["continuity_verified"] is False


def test_no_retries_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "for attempt" not in source
    assert "while retry" not in source
    assert "retry_count +=" not in source
    assert "time.sleep(" not in source


def test_no_orchestration_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "orchestrator" not in source
    assert "orchestrationruntime" not in source
    assert "asyncio" not in source


def test_no_alternate_provider_path_introduced():
    source = (CLI / "commands" / "execution.py").read_text(encoding="utf-8")

    assert "create_controlled_execution_handoff" in source
    assert "run_bounded_codex_cli_task" not in source
    assert "import subprocess" not in source
    assert "subprocess.run" not in source


def test_diagnostic_evidence_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_failure_handler,
    )

    diagnostics = result["diagnostic_evidence"]
    assert diagnostics["provider_invoked"] is True
    assert diagnostics["provider_executable_found"] is True
    assert diagnostics["provider_exit_code"] == 1
    assert diagnostics["provider_stderr"] == "provider failed"
    assert diagnostics["failure_stage"] == "bounded_codex_cli_subprocess"


def test_terminal_execution_result_rendering(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_success_handler,
    )
    rendered = render_command_result(result)

    assert "AIGOL EXECUTION RESULT" in rendered
    assert "Execution:" in rendered
    assert "EXECUTION_COMPLETED" in rendered
    assert "Provider:" in rendered
    assert "INVOKED" in rendered
    assert "Governed Return:" in rendered
    assert "GENERATED" in rendered
    assert "Continuity:" in rendered
    assert "VERIFIED" in rendered
