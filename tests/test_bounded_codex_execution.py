from sapianta_bridge.provider_connectors.bounded_codex_execution import (
    bounded_prompt_from_task_artifact,
    bounded_codex_command,
    validate_bounded_codex_command,
)


def test_bounded_codex_command_is_fixed_shape():
    command = bounded_codex_command(codex_executable="codex", bounded_prompt="bounded prompt")

    assert command == ("codex", "exec", "bounded prompt")
    validation = validate_bounded_codex_command(codex_executable="codex", command=command)
    assert validation["valid"] is True
    assert validation["contract_used"] == "codex exec <bounded_prompt>"
    assert validation["shell_execution_present"] is False
    assert validation["arbitrary_command_execution_present"] is False


def test_bounded_codex_command_rejects_non_codex_executable():
    command = bounded_codex_command(codex_executable="bash", bounded_prompt="bounded prompt")

    validation = validate_bounded_codex_command(codex_executable="bash", command=command)

    assert validation["valid"] is False
    assert any(error["field"] == "codex_executable" for error in validation["errors"])


def test_bounded_codex_command_rejects_previous_run_contract():
    validation = validate_bounded_codex_command(
        codex_executable="codex",
        command=("codex", "run", "/tmp/task.json"),
    )

    assert validation["valid"] is False
    assert any("run" in error["reason"] for error in validation["errors"])


def test_bounded_prompt_is_deterministic_from_task_artifact():
    artifact = {
        "provider_id": "codex_cli",
        "envelope_id": "ENV-1",
        "invocation_id": "INV-1",
        "transport_id": "TRANSPORT-1",
        "replay_identity": "REPLAY-1",
    }

    prompt = bounded_prompt_from_task_artifact(artifact)

    assert prompt == bounded_prompt_from_task_artifact(artifact)
    assert "SAPIANTA_CODEX_VALIDATION_OK" in prompt
    assert "ENV-1" in prompt
