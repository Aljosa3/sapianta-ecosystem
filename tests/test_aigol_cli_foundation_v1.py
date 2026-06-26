import subprocess
from pathlib import Path

from agol_bridge.chatgpt_ingress.chatgpt_ingress_validator import validate_chatgpt_ingress_artifact

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain, continuity_preview_summary
from aigol.cli.commands.dispatch import authorize_dispatch
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.governance import validate_governance_continuity
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cli.commands.status import status_summary


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "aigol" / "cli"


def _artifact():
    return generate_ingress_artifact(
        human_request="Echo hello from AiGOL CLI.",
        semantic_intent="Minimal deterministic governed CLI continuity test",
    )


def _accepted_native_response(message):
    return {
        "status": "NATIVE_BRIDGE_ACCEPTED",
        "result_artifact": {
            "artifact_hash": "sha256:" + "1" * 64,
            "codex_cli_result": {
                "bounded_execution_status": "COMPLETED",
                "provider_invoked": True,
                "summary": "mocked bounded provider continuity",
                "provider_result": {
                    "status": "COMPLETED",
                    "diagnostic_evidence": {
                        "provider_invoked": True,
                        "subprocess_invoked": True,
                    },
                },
            },
        },
        "governed_return": {"status": "ACCEPTED"},
    }


def test_cli_status_command_works():
    result = status_summary()
    rendered = render_command_result(result)

    assert result["command"] == "aigol status"
    assert "AIGOL STATUS" in rendered
    assert "Provider: NOT_INVOKED" in rendered


def test_cli_ingress_generation_works():
    artifact = _artifact()

    assert artifact["artifact_type"] == "CHATGPT_INGRESS_ARTIFACT_V1"
    assert artifact["validation_status"] == "STRUCTURAL_CANDIDATE_ONLY"
    assert artifact["replay_identity"].startswith("CHATGPT-INGRESS-REPLAY-")


def test_generated_ingress_artifact_valid():
    validation = validate_chatgpt_ingress_artifact(_artifact())

    assert validation["valid"] is True
    assert validation["status"] == "ACCEPTED_AS_SEMANTIC_INPUT"


def test_governance_validation_continuity_works():
    result = validate_governance_continuity(ingress_artifact=_artifact())

    assert result["governance_status"] == "PASS"
    assert result["task_package_preview"]["governance_status"] == "READY_FOR_HUMAN_APPROVAL"


def test_continuity_preview_renders_deterministically():
    first = render_command_result(continuity_preview_summary(ingress_artifact=_artifact()))
    second = render_command_result(continuity_preview_summary(ingress_artifact=_artifact()))

    assert first == second
    assert "AIGOL CONTINUITY PREVIEW" in first
    assert "READY_FOR_CONTROLLED_EXECUTION_HANDOFF" in first


def test_dispatch_authorization_continuity_works():
    result = authorize_dispatch(ingress_artifact=_artifact())

    assert result["dispatch_status"] == "DISPATCH_AUTHORIZED"
    assert result["dispatch_authorized"] is True
    assert result["dispatch_authorization_hash"].startswith("sha256:")


def test_controlled_execution_handoff_callable(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_accepted_native_response,
    )

    assert result["execution_status"] == "EXECUTION_COMPLETED"
    assert result["provider_invoked"] is True
    assert result["execution_governance_hash"].startswith("sha256:")


def test_replay_continuity_visible():
    chain = build_governed_chain(ingress_artifact=_artifact())

    assert chain["replay_identity"]
    assert chain["continuity_preview"]["replay_identity"] == chain["replay_identity"]
    assert chain["hash_continuity"]["continuity_preview_hash"].startswith("sha256:")


def test_hash_continuity_preserved():
    chain = build_governed_chain(ingress_artifact=_artifact())
    hashes = chain["hash_continuity"]

    assert hashes["ingress_artifact_hash"].startswith("sha256:")
    assert hashes["task_preview_hash"].startswith("sha256:")
    assert hashes["human_approval_hash"].startswith("sha256:")
    assert hashes["handoff_preview_hash"].startswith("sha256:")
    assert hashes["dispatch_authorization_hash"].startswith("sha256:")
    assert hashes["continuity_preview_hash"].startswith("sha256:")


def test_fail_closed_behavior_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact={},
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_accepted_native_response,
    )

    assert result["execution_status"] == "EXECUTION_BLOCKED"
    assert result["provider_invoked"] is False


def test_invalid_ingress_rejected():
    result = validate_governance_continuity(ingress_artifact={"artifact_type": "BROKEN"})

    assert result["governance_status"] == "FAIL_CLOSED"
    assert result["validation"]["valid"] is False


def test_execution_path_not_duplicated():
    source = (CLI / "commands" / "execution.py").read_text(encoding="utf-8")

    assert "create_controlled_execution_handoff" in source
    assert "handle_native_message" not in source
    assert "import subprocess" not in source
    assert "subprocess.run" not in source


def test_provider_continuity_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        native_message_handler=_accepted_native_response,
    )
    artifact = result["execution_artifact"]

    assert artifact["execution_boundary"]["single_provider"] is True
    assert artifact["codex_provider_used"] == "BOUNDED_CODEX_CLI_PROVIDER"


def test_no_orchestration_introduced():
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "for attempt" not in combined
    assert "while retry" not in combined
    assert "retry_count +=" not in combined
    assert "time.sleep(" not in combined
    assert "orchestrator" not in combined
    assert "orchestrationruntime" not in combined
    assert "threading" not in combined
    assert "asyncio" not in combined


def test_no_hidden_continuation_introduced():
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "autonomous_continuation" in combined
    assert "autonomous_continuation\": true" not in combined
    assert "background" not in combined


def test_cli_entrypoint_status_command_works():
    result = subprocess.run(
        ["python", "-m", "aigol.cli.aigol_cli", "status"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    assert "AIGOL STATUS" in result.stdout


def test_run_command_parser_ingress_generate():
    parser = build_parser()
    args = parser.parse_args([
        "ingress",
        "generate",
        "--human-request",
        "Echo hello.",
        "--semantic-intent",
        "CLI parser test",
    ])
    result = run_command(args)

    assert result["command"] == "aigol ingress generate"
    assert result["ingress_artifact"]["artifact_type"] == "CHATGPT_INGRESS_ARTIFACT_V1"
