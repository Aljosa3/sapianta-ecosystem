from sapianta_bridge.provider_connectors.bounded_execution_workspace import validate_bounded_execution_workspace


def test_bounded_execution_workspace_accepts_artifact_inside_workspace(tmp_path):
    artifact = tmp_path / "task.json"
    artifact.write_text("{}", encoding="utf-8")

    validation = validate_bounded_execution_workspace(
        workspace_path=str(tmp_path),
        task_artifact_path=str(artifact),
    )

    assert validation["valid"] is True
    assert validation["workspace_bounded"] is True


def test_bounded_execution_workspace_rejects_artifact_escape(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    artifact = outside / "task.json"
    artifact.write_text("{}", encoding="utf-8")

    validation = validate_bounded_execution_workspace(
        workspace_path=str(workspace),
        task_artifact_path=str(artifact),
    )

    assert validation["valid"] is False
    assert validation["filesystem_escape_detected"] is True


def test_bounded_execution_workspace_rejects_parent_traversal(tmp_path):
    artifact = tmp_path / "task.json"
    artifact.write_text("{}", encoding="utf-8")

    validation = validate_bounded_execution_workspace(
        workspace_path=str(tmp_path / ".."),
        task_artifact_path=str(artifact),
    )

    assert validation["valid"] is False
    assert validation["filesystem_escape_detected"] is True
