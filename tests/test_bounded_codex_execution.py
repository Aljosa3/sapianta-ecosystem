from sapianta_bridge.provider_connectors.bounded_codex_execution import (
    bounded_codex_command,
    validate_bounded_codex_command,
)


def test_bounded_codex_command_is_fixed_shape():
    command = bounded_codex_command(codex_executable="codex", task_artifact_path="/tmp/task.json")

    assert command == ("codex", "run", "/tmp/task.json")
    validation = validate_bounded_codex_command(codex_executable="codex", command=command)
    assert validation["valid"] is True
    assert validation["shell_execution_present"] is False
    assert validation["arbitrary_command_execution_present"] is False


def test_bounded_codex_command_rejects_non_codex_executable():
    command = bounded_codex_command(codex_executable="bash", task_artifact_path="/tmp/task.json")

    validation = validate_bounded_codex_command(codex_executable="bash", command=command)

    assert validation["valid"] is False
    assert any(error["field"] == "codex_executable" for error in validation["errors"])
