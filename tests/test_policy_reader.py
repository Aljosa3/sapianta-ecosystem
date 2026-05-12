from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import evaluate_policy_input
from sapianta_bridge.policy.policy_reader import (
    evaluations_by_admissibility,
    evaluations_by_risk,
    evaluations_by_source,
    latest_policy_evaluation,
    policy_history,
)
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    config = TransportConfig(runtime_root=tmp_path / "runtime", workspace=tmp_path / "workspace")
    config.ensure_directories()
    config.workspace.mkdir()
    return config


def _input(proposal_id: str, summary: str) -> dict:
    return {
        "input_type": "REFLECTION_PROPOSAL",
        "proposal_id": proposal_id,
        "summary": summary,
        "requires_human_approval": True,
        "allowed_to_execute_automatically": False,
        "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
    }


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_policy_reader_is_read_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    evaluate_policy_input(_input("PROP-001", "advisory improvement"), config, timestamp="2026-05-12T00:00:00+00:00")
    before = _snapshot(config.runtime_root / "policy")

    assert latest_policy_evaluation(config) is not None
    assert len(policy_history(config)) == 1
    assert len(evaluations_by_source("PROP-001", config)) == 1
    assert len(evaluations_by_risk("LOW", config)) == 1
    assert len(evaluations_by_admissibility("ALLOWED", config)) == 1
    after = _snapshot(config.runtime_root / "policy")

    assert after == before
