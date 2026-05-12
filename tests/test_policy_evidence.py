from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import build_policy_evaluation
from sapianta_bridge.policy.policy_evidence import write_policy_evaluation
from sapianta_bridge.transport.transport_config import TransportConfig


def test_policy_evidence_written_with_authority_false(tmp_path: Path) -> None:
    config = TransportConfig(runtime_root=tmp_path / "runtime", workspace=tmp_path / "workspace")
    config.ensure_directories()
    evaluation = build_policy_evaluation(
        {
            "input_type": "REFLECTION_PROPOSAL",
            "proposal_id": "PROP-001",
            "summary": "advisory replay consistency improvement",
            "requires_human_approval": True,
            "allowed_to_execute_automatically": False,
            "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
        },
        timestamp="2026-05-12T00:00:00+00:00",
    )

    path = write_policy_evaluation(evaluation, config)

    assert path.exists()
    assert evaluation["classification"]["allowed_to_execute_automatically"] is False
    assert evaluation["execution_authority_granted"] is False
