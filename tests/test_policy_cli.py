from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy import policy_cli
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    config = TransportConfig(runtime_root=tmp_path / "runtime", workspace=tmp_path / "workspace")
    config.ensure_directories()
    config.workspace.mkdir()
    return config


def _args(config: TransportConfig, *command: str) -> list[str]:
    return ["--runtime-root", str(config.runtime_root), *command]


def _write_input(path: Path, proposal_id: str = "PROP-001") -> None:
    path.write_text(
        json.dumps(
            {
                "input_type": "REFLECTION_PROPOSAL",
                "proposal_id": proposal_id,
                "summary": "advisory deterministic validation improvement",
                "requires_human_approval": True,
                "allowed_to_execute_automatically": False,
                "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_cli_evaluate_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    input_path = tmp_path / "input.json"
    _write_input(input_path)

    exit_code = policy_cli.main(
        _args(config, "evaluate", str(input_path), "--timestamp", "2026-05-12T00:00:00+00:00")
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["evaluation"]["classification"]["admissibility"] == "ALLOWED"
    assert output["evaluation"]["execution_authority_granted"] is False


def test_cli_latest_history_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    input_path = tmp_path / "input.json"
    _write_input(input_path)
    assert policy_cli.main(
        _args(config, "evaluate", str(input_path), "--timestamp", "2026-05-12T00:00:00+00:00")
    ) == 0
    capsys.readouterr()

    assert policy_cli.main(_args(config, "latest")) == 0
    latest = json.loads(capsys.readouterr().out)
    assert latest["source_id"] == "PROP-001"

    assert policy_cli.main(_args(config, "history")) == 0
    history = json.loads(capsys.readouterr().out)
    assert len(history) == 1


def test_allowed_to_execute_and_authority_always_false(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    input_path = tmp_path / "input.json"
    _write_input(input_path)

    assert policy_cli.main(
        _args(config, "evaluate", str(input_path), "--timestamp", "2026-05-12T00:00:00+00:00")
    ) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["evaluation"]["classification"]["allowed_to_execute_automatically"] is False
    assert output["evaluation"]["execution_authority_granted"] is False
