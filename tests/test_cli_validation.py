from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sapianta_bridge.protocol import cli

from protocol_fixtures import valid_task


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def test_cli_returns_exit_code_0_for_valid_artifact(tmp_path: Path, capsys) -> None:
    artifact_path = tmp_path / "task.json"
    _write_json(artifact_path, valid_task())

    exit_code = cli.main(["validate", str(artifact_path)])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output == {
        "artifact_type": "task",
        "protocol_version": "0.1",
        "state": "VALIDATED",
        "valid": True,
    }


def test_cli_returns_exit_code_1_for_invalid_artifact(tmp_path: Path, capsys) -> None:
    artifact = valid_task()
    del artifact["task_id"]
    artifact_path = tmp_path / "task.json"
    _write_json(artifact_path, artifact)

    exit_code = cli.main(["validate", str(artifact_path)])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert output["valid"] is False
    assert output["recommended_state"] == "QUARANTINED"


def test_cli_returns_exit_code_2_for_internal_failure(monkeypatch, capsys) -> None:
    def raise_failure(_path: Path):
        raise RuntimeError("forced")

    monkeypatch.setattr(cli, "enforce_artifact_path", raise_failure)
    exit_code = cli.main(["validate", "artifact.json"])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert output["valid"] is False
    assert output["errors"][0]["field"] == "internal_validator"
